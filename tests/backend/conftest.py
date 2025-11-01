"""
Pytest configuration and fixtures for backend tests.

This module provides common fixtures for database setup, test data factories,
and other test utilities for SQLAlchemy models testing.

Fixtures:
    engine: SQLAlchemy engine with in-memory SQLite
    session: Database session for each test (auto-rollback)
    sample_country: Sample Country instance
    sample_city: Sample City instance
    sample_company_type: Sample CompanyType instance
    sample_currency: Sample Currency instance
    sample_incoterm: Sample Incoterm instance
    sample_quote_status: Sample QuoteStatus instance
    sample_unit: Sample Unit instance
    sample_family_type: Sample FamilyType instance
    sample_matter: Sample Matter instance
    sample_sales_type: Sample SalesType instance
"""

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Generator

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

# Import Base and all models
from src.backend.models.base import Base
from src.backend.models.lookups.lookups import (
    City,
    CompanyType,
    Country,
    Currency,
    FamilyType,
    Incoterm,
    Matter,
    QuoteStatus,
    SalesType,
    Unit,
)
from src.backend.models.core.companies import Branch, Company, CompanyRut
from src.backend.models.business.quotes import Quote, QuoteProduct


# Enable foreign keys in SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Enable foreign key constraints in SQLite."""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@pytest.fixture(scope="function")
def engine() -> Generator[Engine, None, None]:
    """
    Create an in-memory SQLite engine for testing.

    This fixture creates a new in-memory database for each test function,
    ensuring complete isolation between tests.

    Yields:
        SQLAlchemy Engine instance

    Example:
        >>> def test_something(engine):
        ...     # Engine is already created and configured
        ...     assert engine is not None
    """
    # Create in-memory SQLite database
    test_engine = create_engine(
        "sqlite:///:memory:",
        echo=False,  # Set to True for SQL debugging
        connect_args={"check_same_thread": False},
    )

    # Create all tables
    Base.metadata.create_all(test_engine)

    yield test_engine

    # Cleanup
    Base.metadata.drop_all(test_engine)
    test_engine.dispose()


@pytest.fixture(scope="function")
def session(engine: Engine) -> Generator[Session, None, None]:
    """
    Create a database session for testing.

    This fixture creates a new session for each test and automatically
    rolls back all changes after the test completes, ensuring test isolation.

    Args:
        engine: SQLAlchemy engine fixture

    Yields:
        SQLAlchemy Session instance

    Example:
        >>> def test_create_currency(session):
        ...     currency = Currency(code="USD", name="US Dollar")
        ...     session.add(currency)
        ...     session.commit()
        ...     assert currency.id is not None
    """
    # Create session factory
    SessionLocal = sessionmaker(bind=engine)
    test_session = SessionLocal()

    # Set user context for audit mixins (optional)
    test_session.info["user_id"] = 1  # Test user ID

    yield test_session

    # Rollback any changes and close session
    test_session.rollback()
    test_session.close()


# ============= LOOKUP TABLE FIXTURES =============


@pytest.fixture
def sample_country(session: Session) -> Country:
    """
    Create a sample Country for testing.

    Args:
        session: Database session

    Returns:
        Country instance with Chile data

    Example:
        >>> def test_with_country(sample_country):
        ...     assert sample_country.name == "Chile"
        ...     assert sample_country.iso_code_alpha2 == "CL"
    """
    country = Country(
        name="Chile",
        iso_code_alpha2="CL",
        iso_code_alpha3="CHL",
    )
    session.add(country)
    session.commit()
    session.refresh(country)
    return country


@pytest.fixture
def sample_city(session: Session, sample_country: Country) -> City:
    """
    Create a sample City for testing.

    Args:
        session: Database session
        sample_country: Country fixture

    Returns:
        City instance (Santiago, Chile)

    Example:
        >>> def test_with_city(sample_city):
        ...     assert sample_city.name == "Santiago"
        ...     assert sample_city.country.name == "Chile"
    """
    city = City(
        name="Santiago",
        country_id=sample_country.id,
    )
    session.add(city)
    session.commit()
    session.refresh(city)
    return city


@pytest.fixture
def sample_company_type(session: Session) -> CompanyType:
    """
    Create a sample CompanyType for testing.

    Args:
        session: Database session

    Returns:
        CompanyType instance (CLIENT type)

    Example:
        >>> def test_with_company_type(sample_company_type):
        ...     assert sample_company_type.name == "CLIENT"
    """
    company_type = CompanyType(
        name="CLIENT",
        description="Empresa que adquiere productos o servicios",
    )
    session.add(company_type)
    session.commit()
    session.refresh(company_type)
    return company_type


@pytest.fixture
def sample_currency(session: Session) -> Currency:
    """
    Create a sample Currency for testing.

    Args:
        session: Database session

    Returns:
        Currency instance (CLP)

    Example:
        >>> def test_with_currency(sample_currency):
        ...     assert sample_currency.code == "CLP"
        ...     assert sample_currency.is_active is True
    """
    currency = Currency(
        code="CLP",
        name="Chilean Peso",
        symbol="$",
        is_active=True,
    )
    session.add(currency)
    session.commit()
    session.refresh(currency)
    return currency


@pytest.fixture
def sample_incoterm(session: Session) -> Incoterm:
    """
    Create a sample Incoterm for testing.

    Args:
        session: Database session

    Returns:
        Incoterm instance (FOB)

    Example:
        >>> def test_with_incoterm(sample_incoterm):
        ...     assert sample_incoterm.code == "FOB"
    """
    incoterm = Incoterm(
        code="FOB",
        name="Free On Board",
        description="Seller delivers goods on board vessel",
        is_active=True,
    )
    session.add(incoterm)
    session.commit()
    session.refresh(incoterm)
    return incoterm


@pytest.fixture
def sample_quote_status(session: Session) -> QuoteStatus:
    """
    Create a sample QuoteStatus for testing.

    Args:
        session: Database session

    Returns:
        QuoteStatus instance (draft status)

    Example:
        >>> def test_with_quote_status(sample_quote_status):
        ...     assert sample_quote_status.code == "draft"
    """
    status = QuoteStatus(
        code="draft",
        name="Draft",
        description="Quote in draft state",
    )
    session.add(status)
    session.commit()
    session.refresh(status)
    return status


@pytest.fixture
def sample_unit(session: Session) -> Unit:
    """
    Create a sample Unit for testing.

    Args:
        session: Database session

    Returns:
        Unit instance (pcs)

    Example:
        >>> def test_with_unit(sample_unit):
        ...     assert sample_unit.code == "pcs"
    """
    unit = Unit(
        code="pcs",
        name="Pieces",
        description="Unit pieces",
        is_active=True,
    )
    session.add(unit)
    session.commit()
    session.refresh(unit)
    return unit


@pytest.fixture
def sample_family_type(session: Session) -> FamilyType:
    """
    Create a sample FamilyType for testing.

    Args:
        session: Database session

    Returns:
        FamilyType instance

    Example:
        >>> def test_with_family_type(sample_family_type):
        ...     assert sample_family_type.name == "Mecánico"
    """
    family = FamilyType(
        name="Mecánico",
        description="Productos mecánicos",
    )
    session.add(family)
    session.commit()
    session.refresh(family)
    return family


@pytest.fixture
def sample_matter(session: Session) -> Matter:
    """
    Create a sample Matter for testing.

    Args:
        session: Database session

    Returns:
        Matter instance

    Example:
        >>> def test_with_matter(sample_matter):
        ...     assert sample_matter.name == "Acero inoxidable"
    """
    matter = Matter(
        name="Acero inoxidable",
        description="Material resistente a la corrosión",
    )
    session.add(matter)
    session.commit()
    session.refresh(matter)
    return matter


@pytest.fixture
def sample_sales_type(session: Session) -> SalesType:
    """
    Create a sample SalesType for testing.

    Args:
        session: Database session

    Returns:
        SalesType instance

    Example:
        >>> def test_with_sales_type(sample_sales_type):
        ...     assert sample_sales_type.name == "Export"
    """
    sales_type = SalesType(
        name="Export",
        description="International sales",
    )
    session.add(sales_type)
    session.commit()
    session.refresh(sales_type)
    return sales_type


# ============= CORE MODEL FIXTURES =============


@pytest.fixture
def sample_company(
    session: Session,
    sample_company_type: CompanyType,
    sample_country: Country,
    sample_city: City,
) -> Company:
    """
    Create a sample Company for testing.

    Args:
        session: Database session
        sample_company_type: CompanyType fixture
        sample_country: Country fixture
        sample_city: City fixture

    Returns:
        Company instance

    Example:
        >>> def test_with_company(sample_company):
        ...     assert sample_company.name == "AK Group SpA"
        ...     assert sample_company.trigram == "AKG"
    """
    company = Company(
        name="AK Group SpA",
        trigram="AKG",
        main_address="Av. Providencia 123, Santiago",
        phone="+56912345678",
        website="https://akgroup.cl",
        company_type_id=sample_company_type.id,
        country_id=sample_country.id,
        city_id=sample_city.id,
        is_active=True,
    )
    session.add(company)
    session.commit()
    session.refresh(company)
    return company


@pytest.fixture
def sample_product(
    session: Session,
    sample_family_type: FamilyType,
) -> "Product":
    """
    Create a sample Product for testing.

    Args:
        session: Database session
        sample_family_type: FamilyType fixture

    Returns:
        Product instance

    Example:
        >>> def test_with_product(sample_product):
        ...     assert sample_product.reference == "PROD-TEST"
    """
    from src.backend.models.core.products import Product, ProductType

    product = Product(
        product_type=ProductType.ARTICLE,
        reference="PROD-TEST",
        designation_es="Producto de Prueba",
        designation_en="Test Product",
        family_type_id=sample_family_type.id,
        cost_price=Decimal("100.00"),
        sale_price=Decimal("150.00"),
        stock_quantity=Decimal("50.0"),
        is_active=True,
    )
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


# ============= UTILITY FUNCTIONS =============


def create_currency(
    session: Session,
    code: str = "USD",
    name: str = "US Dollar",
    symbol: str = "$",
    is_active: bool = True,
) -> Currency:
    """
    Factory function to create Currency instances.

    Args:
        session: Database session
        code: Currency code (ISO 4217)
        name: Currency name
        symbol: Currency symbol
        is_active: Active status

    Returns:
        Currency instance

    Example:
        >>> currency = create_currency(session, code="EUR", name="Euro", symbol="€")
        >>> assert currency.code == "EUR"
    """
    currency = Currency(code=code, name=name, symbol=symbol, is_active=is_active)
    session.add(currency)
    session.commit()
    session.refresh(currency)
    return currency


def create_company(
    session: Session,
    name: str,
    trigram: str,
    company_type_id: int,
    country_id: int | None = None,
    city_id: int | None = None,
    **kwargs,
) -> Company:
    """
    Factory function to create Company instances.

    Args:
        session: Database session
        name: Company name
        trigram: 3-letter code
        company_type_id: FK to company_types
        country_id: FK to countries
        city_id: FK to cities
        **kwargs: Additional fields

    Returns:
        Company instance

    Example:
        >>> company = create_company(
        ...     session,
        ...     name="Test Corp",
        ...     trigram="TST",
        ...     company_type_id=1
        ... )
    """
    company = Company(
        name=name,
        trigram=trigram,
        company_type_id=company_type_id,
        country_id=country_id,
        city_id=city_id,
        **kwargs,
    )
    session.add(company)
    session.commit()
    session.refresh(company)
    return company
