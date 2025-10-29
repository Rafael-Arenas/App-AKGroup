"""
Unit tests for Company, CompanyRut, and Branch models.

Tests validation, business logic, and relationships for company models.
"""

import pytest

from models.core.companies import Branch, Company, CompanyRut, CompanyTypeEnum


class TestCompanyTypeEnum:
    """Test suite for CompanyTypeEnum."""

    def test_enum_values(self):
        """Test enum has correct values."""
        assert CompanyTypeEnum.CLIENT.value == "CLIENT"
        assert CompanyTypeEnum.SUPPLIER.value == "SUPPLIER"

    def test_display_name(self):
        """Test display_name property."""
        assert CompanyTypeEnum.CLIENT.display_name == "Cliente"
        assert CompanyTypeEnum.SUPPLIER.display_name == "Proveedor"

    def test_description(self):
        """Test description property."""
        assert "adquiere" in CompanyTypeEnum.CLIENT.description
        assert "provee" in CompanyTypeEnum.SUPPLIER.description


class TestCompany:
    """Test suite for Company model."""

    def test_create_company(self, session):
        """Test creating a basic company."""
        company = Company(
            name="AK Group SpA",
            trigram="AKG",
            phone="+56912345678",
            website="https://akgroup.cl",
            company_type_id=1,
            country_id=1,
        )

        session.add(company)
        session.commit()

        assert company.id is not None
        assert company.name == "AK Group SpA"
        assert company.trigram == "AKG"

    def test_name_validation(self, session):
        """Test company name validation."""
        # Valid name (trimmed)
        company = Company(
            name="  Test Company  ",
            trigram="TST",
            company_type_id=1,
        )
        assert company.name == "Test Company"

        # Invalid: too short
        with pytest.raises(ValueError, match="at least 2 characters"):
            company = Company(
                name="A",
                trigram="TST",
                company_type_id=1,
            )
            session.add(company)
            session.flush()

        # Invalid: empty
        with pytest.raises(ValueError, match="at least 2 characters"):
            company = Company(
                name="",
                trigram="TST",
                company_type_id=1,
            )
            session.add(company)
            session.flush()

    def test_trigram_validation(self, session):
        """Test trigram validation."""
        # Valid trigram (uppercase conversion)
        company = Company(
            name="Test Company",
            trigram="abc",
            company_type_id=1,
        )
        assert company.trigram == "ABC"

        # Invalid: wrong length
        with pytest.raises(ValueError, match="exactly 3 characters"):
            company = Company(
                name="Test",
                trigram="AB",
                company_type_id=1,
            )
            session.add(company)
            session.flush()

        with pytest.raises(ValueError, match="exactly 3 characters"):
            company = Company(
                name="Test",
                trigram="ABCD",
                company_type_id=1,
            )
            session.add(company)
            session.flush()

        # Invalid: contains non-letters
        with pytest.raises(ValueError, match="only letters"):
            company = Company(
                name="Test",
                trigram="AB1",
                company_type_id=1,
            )
            session.add(company)
            session.flush()

    def test_phone_validation(self, session):
        """Test phone validation."""
        # Valid phone
        company = Company(
            name="Test Company",
            trigram="TST",
            phone="+56912345678",
            company_type_id=1,
        )
        session.add(company)
        session.flush()
        assert company.phone == "+56912345678"

        # Phone with valid format
        company.phone = "+56987654321"
        session.flush()
        assert company.phone == "+56987654321"

        # None is valid
        company.phone = None
        session.flush()
        assert company.phone is None

    def test_website_validation(self, session):
        """Test website URL validation."""
        # Valid URLs
        valid_urls = [
            "https://example.com",
            "http://example.com",
            "https://www.example.com/path",
        ]

        for url in valid_urls:
            company = Company(
                name="Test Company",
                trigram="TST",
                website=url,
                company_type_id=1,
            )
            assert company.website is not None

        # None is valid
        company = Company(
            name="Test",
            trigram="TST",
            company_type_id=1,
        )
        company.website = None
        assert company.website is None

    def test_repr(self, session):
        """Test string representation."""
        company = Company(
            id=1,
            name="AK Group",
            trigram="AKG",
            company_type_id=1,
        )

        repr_str = repr(company)
        assert "Company" in repr_str
        assert "AK Group" in repr_str
        assert "AKG" in repr_str


class TestCompanyRut:
    """Test suite for CompanyRut model."""

    def test_create_company_rut(self, session):
        """Test creating a company RUT."""
        # Using a valid Chilean RUT: 76.123.456-0
        rut = CompanyRut(
            rut="76123456-0",
            is_main=True,
            company_id=1,
        )

        session.add(rut)
        session.commit()

        assert rut.id is not None
        assert rut.rut == "76123456-0"
        assert rut.is_main is True

    def test_rut_validation(self, session):
        """Test RUT validation and normalization."""
        # Valid RUT with dots (should normalize): 76.123.456-0
        rut = CompanyRut(
            rut="76.123.456-0",
            company_id=1,
        )
        # RUT validator should normalize to format without dots
        assert "-" in rut.rut
        assert "." not in rut.rut

        # Valid RUT without dots: 12.345.678-5
        rut2 = CompanyRut(
            rut="12345678-5",
            company_id=1,
        )
        assert rut2.rut == "12345678-5"

    def test_is_main_flag(self, session):
        """Test is_main flag."""
        rut1 = CompanyRut(
            rut="76123456-0",
            is_main=True,
            company_id=1,
        )
        assert rut1.is_main is True

        rut2 = CompanyRut(
            rut="12345678-5",
            is_main=False,
            company_id=1,
        )
        assert rut2.is_main is False

        # Default should be False (using valid RUT: 33.333.333-3)
        rut3 = CompanyRut(
            rut="33333333-3",
            company_id=1,
        )
        session.add(rut3)
        session.flush()
        assert rut3.is_main is False

    def test_repr(self, session):
        """Test string representation."""
        rut = CompanyRut(
            id=1,
            rut="76123456-0",
            is_main=True,
            company_id=1,
        )

        repr_str = repr(rut)
        assert "CompanyRut" in repr_str
        assert "76123456-0" in repr_str
        assert "main=True" in repr_str


class TestBranch:
    """Test suite for Branch model."""

    def test_create_branch(self, session):
        """Test creating a branch."""
        branch = Branch(
            name="Sucursal Santiago Centro",
            address="Av. Providencia 123, Santiago",
            phone="+56912345678",
            email="santiago@example.com",
            company_id=1,
            city_id=1,
        )

        session.add(branch)
        session.commit()

        assert branch.id is not None
        assert branch.name == "Sucursal Santiago Centro"
        assert branch.phone == "+56912345678"

    def test_name_validation(self, session):
        """Test branch name validation."""
        # Valid name (trimmed)
        branch = Branch(
            name="  Sucursal Norte  ",
            company_id=1,
        )
        assert branch.name == "Sucursal Norte"

        # Invalid: too short
        with pytest.raises(ValueError, match="at least 2 characters"):
            branch = Branch(
                name="A",
                company_id=1,
            )
            session.add(branch)
            session.flush()

        # Invalid: empty
        with pytest.raises(ValueError, match="at least 2 characters"):
            branch = Branch(
                name="",
                company_id=1,
            )
            session.add(branch)
            session.flush()

    def test_phone_validation(self, session):
        """Test phone validation."""
        # Valid phone
        branch = Branch(
            name="Test Branch",
            phone="+56912345678",
            company_id=1,
        )
        session.add(branch)
        session.flush()
        assert branch.phone == "+56912345678"

        # Change to another valid phone
        branch.phone = "+56987654321"
        session.flush()
        assert branch.phone == "+56987654321"

        # None is valid
        branch.phone = None
        session.flush()
        assert branch.phone is None

    def test_active_mixin(self, session):
        """Test ActiveMixin functionality."""
        branch = Branch(
            name="Test Branch",
            company_id=1,
        )
        session.add(branch)
        session.flush()

        # Default should be active
        assert branch.is_active is True

        # Can be deactivated
        branch.is_active = False
        session.flush()
        assert branch.is_active is False

    def test_repr(self, session):
        """Test string representation."""
        branch = Branch(
            id=1,
            name="Sucursal Norte",
            company_id=5,
        )

        repr_str = repr(branch)
        assert "Branch" in repr_str
        assert "Sucursal Norte" in repr_str
        assert "company_id=5" in repr_str


class TestCompanyRelationships:
    """Integration tests for Company relationships."""

    def test_company_with_ruts(self, session):
        """Test company with multiple RUTs."""
        company = Company(
            name="Multi RUT Company",
            trigram="MRC",
            company_type_id=1,
        )
        session.add(company)
        session.flush()

        # Add multiple RUTs (using valid Chilean RUTs)
        rut1 = CompanyRut(
            rut="76123456-0",
            is_main=True,
            company_id=company.id,
        )
        rut2 = CompanyRut(
            rut="12345678-5",
            is_main=False,
            company_id=company.id,
        )

        company.ruts = [rut1, rut2]
        session.commit()

        # Verify relationships
        assert len(company.ruts) == 2
        assert any(r.is_main for r in company.ruts)
        assert any(not r.is_main for r in company.ruts)

    def test_company_with_branches(self, session):
        """Test company with multiple branches."""
        company = Company(
            name="Multi Branch Company",
            trigram="MBC",
            company_type_id=1,
        )
        session.add(company)
        session.flush()

        # Add branches
        branch1 = Branch(
            name="Sucursal Santiago",
            company_id=company.id,
        )
        branch2 = Branch(
            name="Sucursal Valparaíso",
            company_id=company.id,
        )

        company.branches = [branch1, branch2]
        session.commit()

        # Verify relationships
        assert len(company.branches) == 2
        assert all(b.company_id == company.id for b in company.branches)
