"""
Tests for lookup models from lookups.lookups.

This module contains comprehensive tests for all lookup/catalog tables used as
reference data throughout the system.

Test Coverage:
    Country:
        - CRUD operations
        - ISO code validation (alpha-2, alpha-3)
        - Name constraints
        - Relationships (cities, companies)

    City:
        - CRUD operations
        - Country relationship
        - Unique constraint (name + country)
        - Name validation

    CompanyType:
        - CRUD operations
        - Name validation
        - Company relationship

    Incoterm:
        - CRUD operations
        - Code validation (3 characters)
        - ActiveMixin behavior

    Unit:
        - CRUD operations
        - Code and name validation
        - ActiveMixin behavior

    FamilyType, Matter, SalesType:
        - CRUD operations
        - Name validation
        - Product relationships

    QuoteStatus, OrderStatus, PaymentStatus:
        - CRUD operations
        - Code and name validation
        - Business entity relationships

Note: Currency has its own dedicated test file (test_lookups_currency.py)
"""

import pytest
from sqlalchemy.exc import IntegrityError

from src.backend.models.lookups.lookups import (
    City,
    CompanyType,
    Country,
    FamilyType,
    Incoterm,
    Matter,
    OrderStatus,
    PaymentStatus,
    QuoteStatus,
    SalesType,
    Unit,
)


# ============= COUNTRY MODEL TESTS =============


class TestCountryCreation:
    """Tests for Country model creation."""

    def test_create_country_with_valid_data(self, session):
        """Test creating a Country with complete data."""
        # Arrange & Act
        country = Country(
            name="Chile",
            iso_code_alpha2="CL",
            iso_code_alpha3="CHL",
        )
        session.add(country)
        session.commit()
        session.refresh(country)

        # Assert
        assert country.id is not None
        assert country.name == "Chile"
        assert country.iso_code_alpha2 == "CL"
        assert country.iso_code_alpha3 == "CHL"

    def test_create_country_minimal_fields(self, session):
        """Test creating Country with only name (ISO codes optional)."""
        # Arrange & Act
        country = Country(name="France")
        session.add(country)
        session.commit()
        session.refresh(country)

        # Assert
        assert country.id is not None
        assert country.name == "France"
        assert country.iso_code_alpha2 is None
        assert country.iso_code_alpha3 is None

    @pytest.mark.parametrize(
        "name,alpha2,alpha3",
        [
            ("United States", "US", "USA"),
            ("Germany", "DE", "DEU"),
            ("Japan", "JP", "JPN"),
            ("Brazil", "BR", "BRA"),
        ],
    )
    def test_create_multiple_countries(self, session, name, alpha2, alpha3):
        """Test creating multiple countries with different data."""
        country = Country(
            name=name,
            iso_code_alpha2=alpha2,
            iso_code_alpha3=alpha3,
        )
        session.add(country)
        session.commit()

        assert country.name == name
        assert country.iso_code_alpha2 == alpha2


class TestCountryValidation:
    """Tests for Country field validation."""

    def test_name_must_be_unique(self, session):
        """Test that country name must be unique."""
        # Arrange
        country1 = Country(name="Chile")
        session.add(country1)
        session.commit()

        # Act & Assert
        with pytest.raises(IntegrityError):
            country2 = Country(name="Chile")  # Duplicate
            session.add(country2)
            session.commit()

    def test_name_minimum_length(self, session):
        """Test that name must be at least 2 characters."""
        with pytest.raises(IntegrityError, match="name_min_length|check constraint"):
            country = Country(name="A")  # Too short
            session.add(country)
            session.commit()

    def test_iso_alpha2_must_be_2_chars(self, session):
        """Test that ISO alpha-2 code must be exactly 2 characters."""
        # Too short
        with pytest.raises(IntegrityError, match="alpha2_length|check constraint"):
            country = Country(name="Test", iso_code_alpha2="C")
            session.add(country)
            session.commit()

        session.rollback()

        # Too long
        with pytest.raises(IntegrityError, match="alpha2_length|check constraint"):
            country = Country(name="Test2", iso_code_alpha2="CHL")
            session.add(country)
            session.commit()

    def test_iso_alpha3_must_be_3_chars(self, session):
        """Test that ISO alpha-3 code must be exactly 3 characters."""
        with pytest.raises(IntegrityError, match="alpha3_length|check constraint"):
            country = Country(name="Test", iso_code_alpha3="CH")  # Too short
            session.add(country)
            session.commit()

    def test_iso_codes_must_be_unique(self, session):
        """Test that ISO codes must be unique."""
        # Create first country
        country1 = Country(name="Chile", iso_code_alpha2="CL")
        session.add(country1)
        session.commit()

        # Try duplicate alpha-2
        with pytest.raises(IntegrityError):
            country2 = Country(name="Colombia", iso_code_alpha2="CL")  # Duplicate
            session.add(country2)
            session.commit()


class TestCountryRelationships:
    """Tests for Country relationships."""

    def test_cities_relationship(self, session):
        """Test one-to-many relationship with cities."""
        # Arrange
        country = Country(name="Chile", iso_code_alpha2="CL")
        session.add(country)
        session.commit()

        city1 = City(name="Santiago", country_id=country.id)
        city2 = City(name="Valparaíso", country_id=country.id)
        session.add_all([city1, city2])
        session.commit()
        session.refresh(country)

        # Assert
        assert len(country.cities) == 2
        city_names = [c.name for c in country.cities]
        assert "Santiago" in city_names
        assert "Valparaíso" in city_names


# ============= CITY MODEL TESTS =============


class TestCityCreation:
    """Tests for City model creation."""

    def test_create_city_with_valid_data(self, session, sample_country):
        """Test creating a City with valid data."""
        # Arrange & Act
        city = City(
            name="Santiago",
            country_id=sample_country.id,
        )
        session.add(city)
        session.commit()
        session.refresh(city)

        # Assert
        assert city.id is not None
        assert city.name == "Santiago"
        assert city.country_id == sample_country.id

    def test_same_city_name_different_countries(self, session):
        """Test that same city name can exist in different countries."""
        # Arrange - Create two countries
        chile = Country(name="Chile", iso_code_alpha2="CL")
        spain = Country(name="Spain", iso_code_alpha2="ES")
        session.add_all([chile, spain])
        session.commit()

        # Act - Create "Santiago" in both countries
        santiago_cl = City(name="Santiago", country_id=chile.id)
        santiago_es = City(name="Santiago", country_id=spain.id)
        session.add_all([santiago_cl, santiago_es])
        session.commit()

        # Assert - Both should exist
        all_santiagos = session.query(City).filter_by(name="Santiago").all()
        assert len(all_santiagos) == 2


class TestCityValidation:
    """Tests for City field validation."""

    def test_name_minimum_length(self, session, sample_country):
        """Test that city name must be at least 2 characters."""
        with pytest.raises(IntegrityError, match="name_min_length|check constraint"):
            city = City(name="A", country_id=sample_country.id)
            session.add(city)
            session.commit()

    def test_unique_constraint_name_country(self, session, sample_country):
        """Test that city name must be unique within a country."""
        # Arrange - Create first city
        city1 = City(name="Santiago", country_id=sample_country.id)
        session.add(city1)
        session.commit()

        # Act & Assert - Try duplicate in same country
        with pytest.raises(IntegrityError):
            city2 = City(name="Santiago", country_id=sample_country.id)
            session.add(city2)
            session.commit()


class TestCityRelationships:
    """Tests for City relationships."""

    def test_country_relationship(self, session):
        """Test many-to-one relationship with Country."""
        # Arrange
        country = Country(name="Chile")
        session.add(country)
        session.commit()

        city = City(name="Santiago", country_id=country.id)
        session.add(city)
        session.commit()
        session.refresh(city)

        # Assert
        assert city.country is not None
        assert city.country.name == "Chile"


# ============= COMPANY TYPE MODEL TESTS =============


class TestCompanyTypeCreation:
    """Tests for CompanyType model creation."""

    def test_create_company_type_with_valid_data(self, session):
        """Test creating CompanyType with valid data."""
        # Arrange & Act
        company_type = CompanyType(
            name="CLIENT",
            description="Customer/client company",
        )
        session.add(company_type)
        session.commit()
        session.refresh(company_type)

        # Assert
        assert company_type.id is not None
        assert company_type.name == "CLIENT"
        assert company_type.description == "Customer/client company"

    def test_create_company_type_minimal_fields(self, session):
        """Test creating CompanyType with only name."""
        company_type = CompanyType(name="SUPPLIER")
        session.add(company_type)
        session.commit()

        assert company_type.description is None

    @pytest.mark.parametrize(
        "name,description",
        [
            ("CLIENT", "Customer company"),
            ("SUPPLIER", "Supplier/vendor"),
            ("PARTNER", "Business partner"),
            ("INTERNAL", "Internal company"),
        ],
    )
    def test_create_multiple_company_types(self, session, name, description):
        """Test creating multiple company types."""
        company_type = CompanyType(name=name, description=description)
        session.add(company_type)
        session.commit()

        assert company_type.name == name


class TestCompanyTypeValidation:
    """Tests for CompanyType validation."""

    def test_name_must_be_unique(self, session):
        """Test that company type name must be unique."""
        # Arrange
        ct1 = CompanyType(name="CLIENT")
        session.add(ct1)
        session.commit()

        # Act & Assert
        with pytest.raises(IntegrityError):
            ct2 = CompanyType(name="CLIENT")  # Duplicate
            session.add(ct2)
            session.commit()

    def test_name_cannot_be_empty(self, session):
        """Test that name cannot be empty."""
        with pytest.raises(IntegrityError, match="name_not_empty|check constraint"):
            ct = CompanyType(name="")
            session.add(ct)
            session.commit()


# ============= INCOTERM MODEL TESTS =============


class TestIncotermCreation:
    """Tests for Incoterm model creation."""

    def test_create_incoterm_with_valid_data(self, session):
        """Test creating Incoterm with valid data."""
        # Arrange & Act
        incoterm = Incoterm(
            code="FOB",
            name="Free On Board",
            description="Seller delivers goods on board the vessel",
            is_active=True,
        )
        session.add(incoterm)
        session.commit()
        session.refresh(incoterm)

        # Assert
        assert incoterm.id is not None
        assert incoterm.code == "FOB"
        assert incoterm.name == "Free On Board"
        assert incoterm.is_active is True

    @pytest.mark.parametrize(
        "code,name",
        [
            ("EXW", "Ex Works"),
            ("FCA", "Free Carrier"),
            ("FOB", "Free On Board"),
            ("CIF", "Cost Insurance and Freight"),
            ("DAP", "Delivered At Place"),
        ],
    )
    def test_create_multiple_incoterms(self, session, code, name):
        """Test creating multiple incoterms."""
        incoterm = Incoterm(code=code, name=name)
        session.add(incoterm)
        session.commit()

        assert incoterm.code == code
        assert incoterm.name == name


class TestIncotermValidation:
    """Tests for Incoterm validation."""

    def test_code_must_be_exactly_3_chars(self, session):
        """Test that incoterm code must be exactly 3 characters."""
        # Too short
        with pytest.raises(IntegrityError, match="code_exact_length|check constraint"):
            incoterm = Incoterm(code="FO", name="Test")
            session.add(incoterm)
            session.commit()

        session.rollback()

        # Too long
        with pytest.raises(IntegrityError, match="code_exact_length|check constraint"):
            incoterm = Incoterm(code="FOOB", name="Test")
            session.add(incoterm)
            session.commit()

    def test_code_must_be_unique(self, session):
        """Test that incoterm code must be unique."""
        incoterm1 = Incoterm(code="FOB", name="Free On Board")
        session.add(incoterm1)
        session.commit()

        with pytest.raises(IntegrityError):
            incoterm2 = Incoterm(code="FOB", name="Duplicate")
            session.add(incoterm2)
            session.commit()


class TestIncotermActiveMixin:
    """Tests for Incoterm ActiveMixin behavior."""

    def test_is_active_default_true(self, session):
        """Test that is_active defaults to True."""
        incoterm = Incoterm(code="FOB", name="Free On Board")
        session.add(incoterm)
        session.commit()

        assert incoterm.is_active is True

    def test_filter_active_incoterms(self, session):
        """Test filtering incoterms by is_active."""
        active = Incoterm(code="FOB", name="Active", is_active=True)
        inactive = Incoterm(code="CIF", name="Inactive", is_active=False)
        session.add_all([active, inactive])
        session.commit()

        active_incoterms = session.query(Incoterm).filter_by(is_active=True).all()
        assert len(active_incoterms) == 1
        assert active_incoterms[0].code == "FOB"


# ============= UNIT MODEL TESTS =============


class TestUnitCreation:
    """Tests for Unit model creation."""

    def test_create_unit_with_valid_data(self, session):
        """Test creating Unit with valid data."""
        # Arrange & Act
        unit = Unit(
            code="pcs",
            name="Pieces",
            description="Individual pieces or units",
            is_active=True,
        )
        session.add(unit)
        session.commit()
        session.refresh(unit)

        # Assert
        assert unit.id is not None
        assert unit.code == "pcs"
        assert unit.name == "Pieces"
        assert unit.description == "Individual pieces or units"

    @pytest.mark.parametrize(
        "code,name",
        [
            ("pcs", "Pieces"),
            ("kg", "Kilogram"),
            ("m", "Meter"),
            ("l", "Liter"),
            ("box", "Box"),
        ],
    )
    def test_create_multiple_units(self, session, code, name):
        """Test creating multiple units."""
        unit = Unit(code=code, name=name)
        session.add(unit)
        session.commit()

        assert unit.code == code


class TestUnitValidation:
    """Tests for Unit validation."""

    def test_code_must_be_unique(self, session):
        """Test that unit code must be unique."""
        unit1 = Unit(code="kg", name="Kilogram")
        session.add(unit1)
        session.commit()

        with pytest.raises(IntegrityError):
            unit2 = Unit(code="kg", name="Duplicate")
            session.add(unit2)
            session.commit()

    def test_code_cannot_be_empty(self, session):
        """Test that code cannot be empty."""
        with pytest.raises(IntegrityError, match="code_not_empty|check constraint"):
            unit = Unit(code="", name="Test")
            session.add(unit)
            session.commit()

    def test_name_cannot_be_empty(self, session):
        """Test that name cannot be empty."""
        with pytest.raises(IntegrityError, match="name_not_empty|check constraint"):
            unit = Unit(code="test", name="")
            session.add(unit)
            session.commit()


# ============= FAMILY TYPE MODEL TESTS =============


class TestFamilyTypeCreation:
    """Tests for FamilyType model creation."""

    def test_create_family_type_with_valid_data(self, session):
        """Test creating FamilyType with valid data."""
        # Arrange & Act
        family = FamilyType(
            name="Mechanical",
            description="Mechanical components and parts",
        )
        session.add(family)
        session.commit()
        session.refresh(family)

        # Assert
        assert family.id is not None
        assert family.name == "Mechanical"
        assert family.description == "Mechanical components and parts"

    @pytest.mark.parametrize(
        "name",
        ["Mechanical", "Electrical", "Consumables", "Tools", "Raw Materials"],
    )
    def test_create_multiple_family_types(self, session, name):
        """Test creating multiple family types."""
        family = FamilyType(name=name)
        session.add(family)
        session.commit()

        assert family.name == name


class TestFamilyTypeValidation:
    """Tests for FamilyType validation."""

    def test_name_must_be_unique(self, session):
        """Test that family type name must be unique."""
        family1 = FamilyType(name="Mechanical")
        session.add(family1)
        session.commit()

        with pytest.raises(IntegrityError):
            family2 = FamilyType(name="Mechanical")  # Duplicate
            session.add(family2)
            session.commit()


# ============= MATTER MODEL TESTS =============


class TestMatterCreation:
    """Tests for Matter model creation."""

    def test_create_matter_with_valid_data(self, session):
        """Test creating Matter with valid data."""
        # Arrange & Act
        matter = Matter(
            name="Stainless Steel",
            description="Corrosion-resistant steel alloy",
        )
        session.add(matter)
        session.commit()
        session.refresh(matter)

        # Assert
        assert matter.id is not None
        assert matter.name == "Stainless Steel"

    @pytest.mark.parametrize(
        "name",
        ["Stainless Steel", "Aluminum", "Plastic ABS", "Wood", "Copper"],
    )
    def test_create_multiple_matters(self, session, name):
        """Test creating multiple materials."""
        matter = Matter(name=name)
        session.add(matter)
        session.commit()

        assert matter.name == name


class TestMatterValidation:
    """Tests for Matter validation."""

    def test_name_must_be_unique(self, session):
        """Test that matter name must be unique."""
        matter1 = Matter(name="Aluminum")
        session.add(matter1)
        session.commit()

        with pytest.raises(IntegrityError):
            matter2 = Matter(name="Aluminum")  # Duplicate
            session.add(matter2)
            session.commit()


# ============= SALES TYPE MODEL TESTS =============


class TestSalesTypeCreation:
    """Tests for SalesType model creation."""

    def test_create_sales_type_with_valid_data(self, session):
        """Test creating SalesType with valid data."""
        # Arrange & Act
        sales_type = SalesType(
            name="Retail",
            description="Retail sales to end consumers",
        )
        session.add(sales_type)
        session.commit()
        session.refresh(sales_type)

        # Assert
        assert sales_type.id is not None
        assert sales_type.name == "Retail"

    @pytest.mark.parametrize(
        "name",
        ["Retail", "Wholesale", "Export", "Domestic", "Online"],
    )
    def test_create_multiple_sales_types(self, session, name):
        """Test creating multiple sales types."""
        sales_type = SalesType(name=name)
        session.add(sales_type)
        session.commit()

        assert sales_type.name == name


class TestSalesTypeValidation:
    """Tests for SalesType validation."""

    def test_name_must_be_unique(self, session):
        """Test that sales type name must be unique."""
        st1 = SalesType(name="Retail")
        session.add(st1)
        session.commit()

        with pytest.raises(IntegrityError):
            st2 = SalesType(name="Retail")  # Duplicate
            session.add(st2)
            session.commit()


# ============= QUOTE STATUS MODEL TESTS =============


class TestQuoteStatusCreation:
    """Tests for QuoteStatus model creation."""

    def test_create_quote_status_with_valid_data(self, session):
        """Test creating QuoteStatus with valid data."""
        # Arrange & Act
        status = QuoteStatus(
            code="draft",
            name="Draft",
            description="Quote in draft state",
        )
        session.add(status)
        session.commit()
        session.refresh(status)

        # Assert
        assert status.id is not None
        assert status.code == "draft"
        assert status.name == "Draft"

    @pytest.mark.parametrize(
        "code,name",
        [
            ("draft", "Draft"),
            ("sent", "Sent"),
            ("accepted", "Accepted"),
            ("rejected", "Rejected"),
            ("expired", "Expired"),
        ],
    )
    def test_create_multiple_quote_statuses(self, session, code, name):
        """Test creating multiple quote statuses."""
        status = QuoteStatus(code=code, name=name)
        session.add(status)
        session.commit()

        assert status.code == code


class TestQuoteStatusValidation:
    """Tests for QuoteStatus validation."""

    def test_code_must_be_unique(self, session):
        """Test that quote status code must be unique."""
        status1 = QuoteStatus(code="draft", name="Draft")
        session.add(status1)
        session.commit()

        with pytest.raises(IntegrityError):
            status2 = QuoteStatus(code="draft", name="Duplicate")
            session.add(status2)
            session.commit()

    def test_code_cannot_be_empty(self, session):
        """Test that code cannot be empty."""
        with pytest.raises(IntegrityError, match="code_not_empty|check constraint"):
            status = QuoteStatus(code="", name="Test")
            session.add(status)
            session.commit()

    def test_name_cannot_be_empty(self, session):
        """Test that name cannot be empty."""
        with pytest.raises(IntegrityError, match="name_not_empty|check constraint"):
            status = QuoteStatus(code="test", name="")
            session.add(status)
            session.commit()


# ============= ORDER STATUS MODEL TESTS =============


class TestOrderStatusCreation:
    """Tests for OrderStatus model creation."""

    def test_create_order_status_with_valid_data(self, session):
        """Test creating OrderStatus with valid data."""
        # Arrange & Act
        status = OrderStatus(
            code="pending",
            name="Pending",
            description="Order is pending confirmation",
        )
        session.add(status)
        session.commit()
        session.refresh(status)

        # Assert
        assert status.id is not None
        assert status.code == "pending"
        assert status.name == "Pending"

    @pytest.mark.parametrize(
        "code,name",
        [
            ("pending", "Pending"),
            ("confirmed", "Confirmed"),
            ("in_production", "In Production"),
            ("shipped", "Shipped"),
            ("delivered", "Delivered"),
            ("cancelled", "Cancelled"),
        ],
    )
    def test_create_multiple_order_statuses(self, session, code, name):
        """Test creating multiple order statuses."""
        status = OrderStatus(code=code, name=name)
        session.add(status)
        session.commit()

        assert status.code == code


class TestOrderStatusValidation:
    """Tests for OrderStatus validation."""

    def test_code_must_be_unique(self, session):
        """Test that order status code must be unique."""
        status1 = OrderStatus(code="pending", name="Pending")
        session.add(status1)
        session.commit()

        with pytest.raises(IntegrityError):
            status2 = OrderStatus(code="pending", name="Duplicate")
            session.add(status2)
            session.commit()


# ============= PAYMENT STATUS MODEL TESTS =============


class TestPaymentStatusCreation:
    """Tests for PaymentStatus model creation."""

    def test_create_payment_status_with_valid_data(self, session):
        """Test creating PaymentStatus with valid data."""
        # Arrange & Act
        status = PaymentStatus(
            code="pending",
            name="Pending",
            description="Payment is pending",
        )
        session.add(status)
        session.commit()
        session.refresh(status)

        # Assert
        assert status.id is not None
        assert status.code == "pending"
        assert status.name == "Pending"

    @pytest.mark.parametrize(
        "code,name",
        [
            ("pending", "Pending"),
            ("partial", "Partial Payment"),
            ("paid", "Paid"),
            ("overdue", "Overdue"),
            ("cancelled", "Cancelled"),
        ],
    )
    def test_create_multiple_payment_statuses(self, session, code, name):
        """Test creating multiple payment statuses."""
        status = PaymentStatus(code=code, name=name)
        session.add(status)
        session.commit()

        assert status.code == code


class TestPaymentStatusValidation:
    """Tests for PaymentStatus validation."""

    def test_code_must_be_unique(self, session):
        """Test that payment status code must be unique."""
        status1 = PaymentStatus(code="pending", name="Pending")
        session.add(status1)
        session.commit()

        with pytest.raises(IntegrityError):
            status2 = PaymentStatus(code="pending", name="Duplicate")
            session.add(status2)
            session.commit()

    def test_code_cannot_be_empty(self, session):
        """Test that code cannot be empty."""
        with pytest.raises(IntegrityError, match="code_not_empty|check constraint"):
            status = PaymentStatus(code="", name="Test")
            session.add(status)
            session.commit()


# ============= GENERAL LOOKUP TESTS =============


class TestLookupTimestamps:
    """Tests for TimestampMixin on lookup models."""

    @pytest.mark.parametrize(
        "model_class,kwargs",
        [
            (Country, {"name": "Test Country"}),
            (CompanyType, {"name": "Test Type"}),
            (Incoterm, {"code": "TST", "name": "Test"}),
            (Unit, {"code": "tst", "name": "Test"}),
            (FamilyType, {"name": "Test Family"}),
            (Matter, {"name": "Test Matter"}),
            (SalesType, {"name": "Test Sales"}),
            (QuoteStatus, {"code": "test", "name": "Test"}),
            (OrderStatus, {"code": "test", "name": "Test"}),
            (PaymentStatus, {"code": "test", "name": "Test"}),
        ],
    )
    def test_timestamp_mixin_creates_timestamps(self, session, model_class, kwargs):
        """Test that all lookup models have TimestampMixin creating timestamps."""
        # Arrange & Act
        instance = model_class(**kwargs)
        session.add(instance)
        session.commit()
        session.refresh(instance)

        # Assert
        assert instance.created_at is not None
        assert instance.updated_at is not None


class TestLookupCRUD:
    """Tests for basic CRUD operations on lookup models."""

    def test_read_lookup_by_id(self, session):
        """Test reading lookup records by ID."""
        # Arrange
        country = Country(name="Test Country")
        session.add(country)
        session.commit()
        country_id = country.id

        # Act
        retrieved = session.query(Country).filter_by(id=country_id).first()

        # Assert
        assert retrieved is not None
        assert retrieved.name == "Test Country"

    def test_update_lookup(self, session):
        """Test updating lookup records."""
        # Arrange
        country = Country(name="Original Name")
        session.add(country)
        session.commit()
        original_created_at = country.created_at

        # Act
        country.name = "Updated Name"
        session.commit()
        session.refresh(country)

        # Assert
        assert country.name == "Updated Name"
        assert country.created_at == original_created_at
        assert country.updated_at > original_created_at

    def test_delete_lookup(self, session):
        """Test deleting lookup records."""
        # Arrange
        country = Country(name="To Delete")
        session.add(country)
        session.commit()
        country_id = country.id

        # Act
        session.delete(country)
        session.commit()

        # Assert
        deleted = session.query(Country).filter_by(id=country_id).first()
        assert deleted is None


class TestLookupEdgeCases:
    """Tests for edge cases in lookup models."""

    def test_special_characters_in_names(self, session):
        """Test that names accept special characters and unicode."""
        country = Country(name="Côte d'Ivoire")
        session.add(country)
        session.commit()

        assert "ô" in country.name
        assert "'" in country.name

    def test_very_long_descriptions(self, session):
        """Test lookup models with very long description fields."""
        long_desc = "A" * 5000
        company_type = CompanyType(
            name="Test",
            description=long_desc,
        )
        session.add(company_type)
        session.commit()

        assert len(company_type.description) == 5000

    def test_concurrent_lookup_creation(self, session):
        """Test creating multiple lookup records in same transaction."""
        countries = [
            Country(name=f"Country {i}")
            for i in range(10)
        ]
        session.add_all(countries)
        session.commit()

        count = session.query(Country).count()
        assert count == 10
