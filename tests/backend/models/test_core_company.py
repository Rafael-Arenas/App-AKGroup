"""
Tests for Company, CompanyRut, and Plant models from core.companies.

This module contains comprehensive tests for the core company models,
including CRUD operations, validators, relationships, business logic, and edge cases.

Test Coverage:
    Company:
        - Basic CRUD operations
        - Field validation (name, trigram, phone, website)
        - Relationships (company_type, country, city, ruts, plants)
        - CompanyTypeEnum property
        - Validators (trigram uppercase, phone format, URL format)
        - Mixins (Timestamp, Audit, Active)

    CompanyRut:
        - CRUD operations
        - RUT validation (Chilean RUT with check digit)
        - Unique constraint
        - is_main flag
        - Relationship with Company
        - Cascade delete behavior

    Plant:
        - CRUD operations
        - Field validation
        - Relationships with Company and City
        - ActiveMixin behavior
        - Cascade delete behavior
"""

from typing import Optional

import pytest
from sqlalchemy.exc import IntegrityError

from src.backend.models.core.companies import Plant, Company, CompanyRut, CompanyTypeEnum
from src.backend.models.lookups import City, CompanyType, Country


# ============= COMPANY MODEL TESTS =============


class TestCompanyCreation:
    """Tests for Company model instantiation and creation."""

    def test_create_company_with_valid_data(
        self,
        session,
        sample_company_type: CompanyType,
        sample_country: Country,
        sample_city: City,
    ):
        """
        Test creating a Company with all valid fields.

        Verifies that a Company can be created with complete data and
        all fields are properly stored.
        """
        # Arrange & Act
        company = Company(
            name="AK Group SpA",
            trigram="AKG",
            main_address="Av. Providencia 123, Santiago",
            phone="+56912345678",
            website="https://akgroup.cl",
            intracommunity_number="CL123456789",
            company_type_id=sample_company_type.id,
            country_id=sample_country.id,
            city_id=sample_city.id,
            is_active=True,
        )
        session.add(company)
        session.commit()
        session.refresh(company)

        # Assert
        assert company.id is not None
        assert company.name == "AK Group SpA"
        assert company.trigram == "AKG"
        assert company.main_address == "Av. Providencia 123, Santiago"
        assert company.phone == "+56912345678"
        assert company.website == "https://akgroup.cl"
        assert company.company_type_id == sample_company_type.id
        assert company.country_id == sample_country.id
        assert company.city_id == sample_city.id
        assert company.is_active is True

    def test_create_company_minimal_fields(self, session, sample_company_type: CompanyType):
        """Test creating Company with only required fields."""
        # Arrange & Act
        company = Company(
            name="Test Company",
            trigram="TST",
            company_type_id=sample_company_type.id,
        )
        session.add(company)
        session.commit()
        session.refresh(company)

        # Assert
        assert company.id is not None
        assert company.name == "Test Company"
        assert company.trigram == "TST"
        assert company.country_id is None
        assert company.city_id is None
        assert company.phone is None
        assert company.website is None

    def test_create_company_without_optional_fields(self, session, sample_company_type: CompanyType):
        """Test that optional fields (country, city, phone, etc.) can be None."""
        # Arrange & Act
        company = Company(
            name="Minimal Corp",
            trigram="MIN",
            company_type_id=sample_company_type.id,
            country_id=None,
            city_id=None,
            phone=None,
            website=None,
        )
        session.add(company)
        session.commit()

        # Assert
        assert company.id is not None


class TestCompanyValidation:
    """Tests for Company field validators."""

    def test_name_validator_strips_whitespace(self, session, sample_company_type: CompanyType):
        """Test that name validator strips leading/trailing whitespace."""
        # Arrange & Act
        company = Company(
            name="  Test Company  ",
            trigram="TST",
            company_type_id=sample_company_type.id,
        )
        session.add(company)
        session.commit()
        session.refresh(company)

        # Assert
        assert company.name == "Test Company"  # Whitespace stripped

    def test_name_validator_minimum_length(self, session, sample_company_type: CompanyType):
        """Test that name must be at least 2 characters."""
        # Test 1 character name
        with pytest.raises(ValueError, match="at least 2 characters"):
            company = Company(
                name="A",
                trigram="TST",
                company_type_id=sample_company_type.id,
            )
            session.add(company)
            session.flush()

    def test_name_validator_rejects_empty_string(self, session, sample_company_type: CompanyType):
        """Test that name cannot be empty or whitespace only."""
        # Empty string
        with pytest.raises(ValueError, match="at least 2 characters"):
            company = Company(
                name="",
                trigram="TST",
                company_type_id=sample_company_type.id,
            )
            session.add(company)
            session.flush()

        session.rollback()

        # Whitespace only
        with pytest.raises(ValueError, match="at least 2 characters"):
            company = Company(
                name="   ",
                trigram="TST",
                company_type_id=sample_company_type.id,
            )
            session.add(company)
            session.flush()

    def test_trigram_validator_converts_to_uppercase(self, session, sample_company_type: CompanyType):
        """Test that trigram is automatically converted to uppercase."""
        # Arrange & Act
        company = Company(
            name="Test Company",
            trigram="abc",  # lowercase
            company_type_id=sample_company_type.id,
        )
        session.add(company)
        session.commit()
        session.refresh(company)

        # Assert
        assert company.trigram == "ABC"  # Converted to uppercase

    def test_trigram_validator_exactly_3_chars(self, session, sample_company_type: CompanyType):
        """Test that trigram must be exactly 3 characters."""
        # Too short
        with pytest.raises(ValueError, match="exactly 3 characters"):
            company = Company(
                name="Test",
                trigram="AB",
                company_type_id=sample_company_type.id,
            )
            session.add(company)
            session.flush()

        session.rollback()

        # Too long
        with pytest.raises(ValueError, match="exactly 3 characters"):
            company = Company(
                name="Test",
                trigram="ABCD",
                company_type_id=sample_company_type.id,
            )
            session.add(company)
            session.flush()

    def test_trigram_validator_only_letters(self, session, sample_company_type: CompanyType):
        """Test that trigram must contain only letters."""
        # Numbers
        with pytest.raises(ValueError, match="only letters"):
            company = Company(
                name="Test",
                trigram="A12",
                company_type_id=sample_company_type.id,
            )
            session.add(company)
            session.flush()

        session.rollback()

        # Special characters
        with pytest.raises(ValueError, match="only letters"):
            company = Company(
                name="Test",
                trigram="A-B",
                company_type_id=sample_company_type.id,
            )
            session.add(company)
            session.flush()

    def test_trigram_must_be_unique(self, session, sample_company_type: CompanyType):
        """Test that trigram must be unique across companies."""
        # Arrange - Create first company
        company1 = Company(
            name="Company One",
            trigram="ABC",
            company_type_id=sample_company_type.id,
        )
        session.add(company1)
        session.commit()

        # Act & Assert - Try to create duplicate
        with pytest.raises(IntegrityError):
            company2 = Company(
                name="Company Two",
                trigram="ABC",  # Duplicate
                company_type_id=sample_company_type.id,
            )
            session.add(company2)
            session.commit()

    def test_phone_validator_accepts_valid_formats(self, session, sample_company_type: CompanyType):
        """Test that phone validator accepts valid E.164 format."""
        valid_phones = [
            ("+56912345678", "CLA"),
            ("+33123456789", "CLB"),
            ("+1234567890", "CLC"),
            ("912345678", "CLD"),  # Without +
        ]

        for phone, trigram in valid_phones:
            company = Company(
                name=f"Company {phone}",
                trigram=trigram,
                company_type_id=sample_company_type.id,
                phone=phone,
            )
            session.add(company)
            session.commit()
            session.refresh(company)
            assert company.phone == phone
            session.rollback()  # Reset for next iteration

    def test_phone_validator_rejects_invalid_formats(self, session, sample_company_type: CompanyType):
        """Test that phone validator rejects invalid formats."""
        invalid_phones = [
            "123",  # Too short
            "12345678901234567",  # Too long
            "abc",  # Not numbers
        ]

        for phone in invalid_phones:
            with pytest.raises(ValueError, match="Phone must be"):
                company = Company(
                    name="Test",
                    trigram="TST",
                    company_type_id=sample_company_type.id,
                    phone=phone,
                )
                session.add(company)
                session.flush()
            session.rollback()

    def test_phone_validator_accepts_none(self, session, sample_company_type: CompanyType):
        """Test that phone can be None (nullable field)."""
        company = Company(
            name="Test",
            trigram="TST",
            company_type_id=sample_company_type.id,
            phone=None,
        )
        session.add(company)
        session.commit()
        assert company.phone is None

    def test_website_validator_accepts_valid_urls(self, session, sample_company_type: CompanyType):
        """Test that website validator accepts valid HTTP/HTTPS URLs."""
        valid_urls = [
            ("https://example.com", "WBA"),
            ("http://example.com", "WBB"),
            ("https://www.example.com/path?query=1", "WBC"),
        ]

        for url, trigram in valid_urls:
            company = Company(
                name=f"Company {trigram}",
                trigram=trigram,
                company_type_id=sample_company_type.id,
                website=url,
            )
            session.add(company)
            session.commit()
            session.refresh(company)
            assert company.website == url
            session.rollback()

    def test_website_validator_rejects_invalid_urls(self, session, sample_company_type: CompanyType):
        """Test that website validator rejects URLs without http:// or https://."""
        invalid_urls = [
            "example.com",
            "www.example.com",
            "ftp://example.com",
        ]

        for url in invalid_urls:
            with pytest.raises(ValueError, match="URL must start with http"):
                company = Company(
                    name="Test",
                    trigram="TST",
                    company_type_id=sample_company_type.id,
                    website=url,
                )
                session.add(company)
                session.flush()
            session.rollback()

    def test_website_validator_accepts_none(self, session, sample_company_type: CompanyType):
        """Test that website can be None (nullable field)."""
        company = Company(
            name="Test",
            trigram="TST",
            company_type_id=sample_company_type.id,
            website=None,
        )
        session.add(company)
        session.commit()
        assert company.website is None


class TestCompanyRelationships:
    """Tests for Company relationships."""

    def test_company_type_relationship(self, session, sample_company: Company):
        """Test relationship with CompanyType."""
        # Assert
        assert sample_company.company_type is not None
        assert sample_company.company_type.name == "CLIENT"

    def test_country_relationship(self, session, sample_company: Company):
        """Test relationship with Country."""
        # Assert
        assert sample_company.country is not None
        assert sample_company.country.name == "Chile"
        assert sample_company.country.iso_code_alpha2 == "CL"

    def test_city_relationship(self, session, sample_company: Company):
        """Test relationship with City."""
        # Assert
        assert sample_company.city is not None
        assert sample_company.city.name == "Santiago"

    def test_company_ruts_relationship(self, session, sample_company: Company):
        """Test one-to-many relationship with CompanyRut."""
        # Arrange - Add RUTs to company
        rut1 = CompanyRut(
            rut="76123456-0",
            is_main=True,
            company_id=sample_company.id,
        )
        rut2 = CompanyRut(
            rut="12345678-5",
            is_main=False,
            company_id=sample_company.id,
        )
        session.add_all([rut1, rut2])
        session.commit()
        session.refresh(sample_company)

        # Assert
        assert len(sample_company.ruts) == 2
        assert any(r.is_main for r in sample_company.ruts)

    def test_company_plants_relationship(
        self,
        session,
        sample_company: Company,
        sample_city: City,
    ):
        """Test one-to-many relationship with Plant."""
        # Arrange - Add plants to company
        plant1 = Plant(
            name="Planta Santiago Centro",
            company_id=sample_company.id,
            city_id=sample_city.id,
        )
        plant2 = Plant(
            name="Planta Las Condes",
            company_id=sample_company.id,
            city_id=sample_city.id,
        )
        session.add_all([plant1, plant2])
        session.commit()
        session.refresh(sample_company)

        # Assert
        assert len(sample_company.plants) == 2
        plant_names = [p.name for p in sample_company.plants]
        assert "Planta Santiago Centro" in plant_names

    def test_cascade_delete_orphan_ruts(self, session, sample_company: Company):
        """Test that deleting company deletes associated RUTs (cascade)."""
        # Arrange - Add RUT
        rut = CompanyRut(
            rut="76123456-0",
            is_main=True,
            company_id=sample_company.id,
        )
        session.add(rut)
        session.commit()
        rut_id = rut.id

        # Act - Delete company
        session.delete(sample_company)
        session.commit()

        # Assert - RUT should also be deleted
        deleted_rut = session.query(CompanyRut).filter_by(id=rut_id).first()
        assert deleted_rut is None


class TestCompanyBusinessLogic:
    """Tests for Company business logic and properties."""

    def test_company_type_enum_property(self, session, sample_company: Company):
        """Test company_type_enum property returns correct enum."""
        # Assert
        assert sample_company.company_type_enum == CompanyTypeEnum.CLIENT

    def test_company_type_enum_returns_none_if_no_type(self, session, sample_company_type: CompanyType):
        """Test company_type_enum returns None if company_type is not set."""
        # Create a company first, then test what happens when relationship is None
        company = Company(
            name="Test Company",
            trigram="TST",
            company_type_id=sample_company_type.id,
        )
        session.add(company)
        session.commit()
        session.refresh(company)

        # Temporarily set the relationship to None to test the property
        # (In real usage, this shouldn't happen due to FK constraint)
        company.company_type = None

        # Assert
        assert company.company_type_enum is None

    def test_repr_method(self, session, sample_company: Company):
        """Test __repr__ string representation."""
        repr_str = repr(sample_company)
        assert "Company" in repr_str
        assert "AK Group SpA" in repr_str
        assert "AKG" in repr_str


class TestCompanyMixins:
    """Tests for Company mixins (Timestamp, Audit, Active)."""

    def test_timestamp_mixin(self, session, sample_company: Company):
        """Test TimestampMixin creates timestamps."""
        assert sample_company.created_at is not None
        assert sample_company.updated_at is not None

    def test_audit_mixin_sets_created_by(self, session, sample_company_type: CompanyType):
        """Test AuditMixin sets created_by_id from session context."""
        # Session has user_id = 1 set in conftest
        company = Company(
            name="Test",
            trigram="TST",
            company_type_id=sample_company_type.id,
        )
        session.add(company)
        session.commit()
        session.refresh(company)

        assert company.created_by_id == 1

    def test_active_mixin_default_true(self, session, sample_company: Company):
        """Test ActiveMixin defaults is_active to True."""
        assert sample_company.is_active is True

    def test_active_mixin_can_be_false(self, session, sample_company_type: CompanyType):
        """Test is_active can be set to False."""
        company = Company(
            name="Inactive Company",
            trigram="INC",
            company_type_id=sample_company_type.id,
            is_active=False,
        )
        session.add(company)
        session.commit()

        assert company.is_active is False


# ============= COMPANY RUT MODEL TESTS =============


class TestCompanyRutCreation:
    """Tests for CompanyRut model creation."""

    def test_create_company_rut_with_valid_data(self, session, sample_company: Company):
        """Test creating CompanyRut with valid Chilean RUT."""
        # Arrange & Act
        rut = CompanyRut(
            rut="76123456-0",
            is_main=True,
            company_id=sample_company.id,
        )
        session.add(rut)
        session.commit()
        session.refresh(rut)

        # Assert
        assert rut.id is not None
        assert rut.rut == "76123456-0"
        assert rut.is_main is True
        assert rut.company_id == sample_company.id

    def test_create_company_rut_with_dots(self, session, sample_company: Company):
        """Test that RUT validator normalizes format (removes dots)."""
        # Arrange & Act
        rut = CompanyRut(
            rut="76.123.456-0",  # With dots
            is_main=True,
            company_id=sample_company.id,
        )
        session.add(rut)
        session.commit()
        session.refresh(rut)

        # Assert - Dots removed
        assert rut.rut == "76123456-0"


class TestCompanyRutValidation:
    """Tests for CompanyRut RUT validation."""

    def test_rut_validator_valid_ruts(self, session, sample_company: Company):
        """Test RUT validator with various valid RUTs."""
        valid_ruts = [
            "11111111-1",
            "22222222-2",
            "12345678-5",
        ]

        for i, rut_str in enumerate(valid_ruts):
            rut = CompanyRut(
                rut=rut_str,
                is_main=(i == 0),
                company_id=sample_company.id,
            )
            session.add(rut)
            session.commit()
            session.refresh(rut)
            assert rut.rut == rut_str
            session.rollback()

    def test_rut_validator_invalid_check_digit(self, session, sample_company: Company):
        """Test that RUT validator rejects invalid check digit."""
        with pytest.raises(ValueError, match="Invalid RUT check digit"):
            rut = CompanyRut(
                rut="12345678-0",  # Invalid check digit
                is_main=True,
                company_id=sample_company.id,
            )
            session.add(rut)
            session.flush()

    def test_rut_validator_too_short(self, session, sample_company: Company):
        """Test that RUT validator rejects too short RUTs."""
        with pytest.raises(ValueError, match="RUT too short"):
            rut = CompanyRut(
                rut="1",
                is_main=True,
                company_id=sample_company.id,
            )
            session.add(rut)
            session.flush()

    def test_rut_must_be_unique(self, session, sample_company: Company):
        """Test that RUT must be unique across all companies."""
        # Arrange - Create first RUT
        rut1 = CompanyRut(
            rut="76123456-0",
            is_main=True,
            company_id=sample_company.id,
        )
        session.add(rut1)
        session.commit()

        # Act & Assert - Try to create duplicate
        with pytest.raises(IntegrityError):
            rut2 = CompanyRut(
                rut="76123456-0",  # Duplicate
                is_main=False,
                company_id=sample_company.id,
            )
            session.add(rut2)
            session.commit()


class TestCompanyRutRelationships:
    """Tests for CompanyRut relationships."""

    def test_company_relationship(self, session, sample_company: Company):
        """Test relationship with parent Company."""
        # Arrange
        rut = CompanyRut(
            rut="76123456-0",
            is_main=True,
            company_id=sample_company.id,
        )
        session.add(rut)
        session.commit()
        session.refresh(rut)

        # Assert
        assert rut.company is not None
        assert rut.company.id == sample_company.id
        assert rut.company.name == "AK Group SpA"

    def test_multiple_ruts_per_company(self, session, sample_company: Company):
        """Test that a company can have multiple RUTs."""
        # Arrange & Act
        rut1 = CompanyRut(rut="76123456-0", is_main=True, company_id=sample_company.id)
        rut2 = CompanyRut(rut="12345678-5", is_main=False, company_id=sample_company.id)
        session.add_all([rut1, rut2])
        session.commit()
        session.refresh(sample_company)

        # Assert
        assert len(sample_company.ruts) == 2


class TestCompanyRutRepr:
    """Tests for CompanyRut __repr__ method."""

    def test_repr_method(self, session, sample_company: Company):
        """Test __repr__ string representation."""
        rut = CompanyRut(
            rut="76123456-0",
            is_main=True,
            company_id=sample_company.id,
        )
        session.add(rut)
        session.commit()
        session.refresh(rut)

        repr_str = repr(rut)
        assert "CompanyRut" in repr_str
        assert "76123456-0" in repr_str
        assert "True" in repr_str or "main=True" in repr_str.lower()


# ============= PLANT MODEL TESTS =============


class TestPlantCreation:
    """Tests for Plant model creation."""

    def test_create_plant_with_valid_data(
        self,
        session,
        sample_company: Company,
        sample_city: City,
    ):
        """Test creating Plant with all valid fields."""
        # Arrange & Act
        plant = Plant(
            name="Planta Santiago Centro",
            address="Av. Providencia 456",
            phone="+56922334455",
            email="santiago@company.cl",
            company_id=sample_company.id,
            city_id=sample_city.id,
            is_active=True,
        )
        session.add(plant)
        session.commit()
        session.refresh(plant)

        # Assert
        assert plant.id is not None
        assert plant.name == "Planta Santiago Centro"
        assert plant.address == "Av. Providencia 456"
        assert plant.phone == "+56922334455"
        assert plant.email == "santiago@company.cl"
        assert plant.company_id == sample_company.id
        assert plant.city_id == sample_city.id
        assert plant.is_active is True

    def test_create_plant_minimal_fields(self, session, sample_company: Company):
        """Test creating Plant with only required fields."""
        # Arrange & Act
        plant = Plant(
            name="Minimal Plant",
            company_id=sample_company.id,
        )
        session.add(plant)
        session.commit()
        session.refresh(plant)

        # Assert
        assert plant.id is not None
        assert plant.name == "Minimal Plant"
        assert plant.address is None
        assert plant.phone is None
        assert plant.email is None
        assert plant.city_id is None


class TestPlantValidation:
    """Tests for Plant field validators."""

    def test_name_validator_strips_whitespace(self, session, sample_company: Company):
        """Test that name validator strips whitespace."""
        # Arrange & Act
        plant = Plant(
            name="  Test Plant  ",
            company_id=sample_company.id,
        )
        session.add(plant)
        session.commit()
        session.refresh(plant)

        # Assert
        assert plant.name == "Test Plant"

    def test_name_validator_minimum_length(self, session, sample_company: Company):
        """Test that name must be at least 2 characters."""
        with pytest.raises(ValueError, match="at least 2 characters"):
            plant = Plant(
                name="A",
                company_id=sample_company.id,
            )
            session.add(plant)
            session.flush()

    def test_phone_validator(self, session, sample_company: Company):
        """Test phone validator accepts valid formats."""
        plant = Plant(
            name="Test Plant",
            phone="+56912345678",
            company_id=sample_company.id,
        )
        session.add(plant)
        session.commit()
        assert plant.phone == "+56912345678"


class TestPlantRelationships:
    """Tests for Plant relationships."""

    def test_company_relationship(
        self,
        session,
        sample_company: Company,
    ):
        """Test relationship with parent Company."""
        # Arrange
        plant = Plant(
            name="Test Plant",
            company_id=sample_company.id,
        )
        session.add(plant)
        session.commit()
        session.refresh(plant)

        # Assert
        assert plant.company is not None
        assert plant.company.id == sample_company.id

    def test_city_relationship(
        self,
        session,
        sample_company: Company,
        sample_city: City,
    ):
        """Test relationship with City."""
        # Arrange
        plant = Plant(
            name="Test Plant",
            company_id=sample_company.id,
            city_id=sample_city.id,
        )
        session.add(plant)
        session.commit()
        session.refresh(plant)

        # Assert
        assert plant.city is not None
        assert plant.city.id == sample_city.id
        assert plant.city.name == "Santiago"

    def test_cascade_delete_with_company(
        self,
        session,
        sample_company: Company,
    ):
        """Test that deleting company deletes plants (cascade)."""
        # Arrange - Add plant
        plant = Plant(
            name="Test Plant",
            company_id=sample_company.id,
        )
        session.add(plant)
        session.commit()
        plant_id = plant.id

        # Act - Delete company
        session.delete(sample_company)
        session.commit()

        # Assert - Plant should also be deleted
        deleted_plant = session.query(Plant).filter_by(id=plant_id).first()
        assert deleted_plant is None


class TestPlantActiveStatus:
    """Tests for Plant ActiveMixin behavior."""

    def test_is_active_default_true(self, session, sample_company: Company):
        """Test that is_active defaults to True."""
        plant = Plant(
            name="Active Plant",
            company_id=sample_company.id,
        )
        session.add(plant)
        session.commit()
        session.refresh(plant)

        assert plant.is_active is True

    def test_filter_active_plants(self, session, sample_company: Company):
        """Test filtering plants by is_active."""
        # Arrange
        active = Plant(
            name="Active Plant",
            company_id=sample_company.id,
            is_active=True,
        )
        inactive = Plant(
            name="Inactive Plant",
            company_id=sample_company.id,
            is_active=False,
        )
        session.add_all([active, inactive])
        session.commit()

        # Act
        active_plants = session.query(Plant).filter_by(is_active=True).all()

        # Assert
        assert len(active_plants) == 1
        assert active_plants[0].name == "Active Plant"


class TestPlantRepr:
    """Tests for Plant __repr__ method."""

    def test_repr_method(self, session, sample_company: Company):
        """Test __repr__ string representation."""
        plant = Plant(
            name="Test Plant",
            company_id=sample_company.id,
        )
        session.add(plant)
        session.commit()
        session.refresh(plant)

        repr_str = repr(plant)
        assert "Plant" in repr_str
        assert "Test Plant" in repr_str
