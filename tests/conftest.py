"""
Shared pytest fixtures for all tests.

This module provides database fixtures and test data factories
that are shared across all test modules.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="function")
def engine():
    """
    Create in-memory SQLite database for testing.

    Scope is function-level to ensure isolation between tests.
    """
    return create_engine("sqlite:///:memory:")


@pytest.fixture(scope="function")
def session(engine):
    """
    Create database session with all tables and lookup data.

    This fixture:
    1. Creates all tables from Base.metadata
    2. Populates lookup tables with basic test data
    3. Yields a session for the test
    4. Closes the session after the test
    """
    from models.base import Base
    from models.lookups import (
        Country,
        City,
        CompanyType,
        Currency,
        FamilyType,
        Matter,
        SalesType,
        QuoteStatus,
        OrderStatus,
        PaymentStatus,
    )

    # Create all tables (drop first to avoid duplicate index issues)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()

    # Populate lookup tables with basic test data
    try:
        # Countries
        chile = Country(id=1, name="Chile", iso_code_alpha2="CL", iso_code_alpha3="CHL")
        france = Country(id=2, name="France", iso_code_alpha2="FR", iso_code_alpha3="FRA")
        usa = Country(id=3, name="United States", iso_code_alpha2="US", iso_code_alpha3="USA")
        session.add_all([chile, france, usa])
        session.flush()

        # Cities
        santiago = City(id=1, name="Santiago", country_id=1)
        valparaiso = City(id=2, name="Valparaíso", country_id=1)
        paris = City(id=3, name="Paris", country_id=2)
        new_york = City(id=4, name="New York", country_id=3)
        session.add_all([santiago, valparaiso, paris, new_york])
        session.flush()

        # Company Types
        client_type = CompanyType(
            id=1,
            name="CLIENT",
            description="Customer company",
        )
        supplier_type = CompanyType(
            id=2,
            name="SUPPLIER",
            description="Supplier company",
        )
        session.add_all([client_type, supplier_type])
        session.flush()

        # Currencies
        clp = Currency(id=1, code="CLP", name="Chilean Peso", symbol="$")
        eur = Currency(id=2, code="EUR", name="Euro", symbol="€")
        usd = Currency(id=3, code="USD", name="US Dollar", symbol="US$")
        session.add_all([clp, eur, usd])
        session.flush()

        # Family Types
        mechanical = FamilyType(
            id=1,
            name="Mechanical",
            description="Mechanical products",
        )
        electrical = FamilyType(
            id=2,
            name="Electrical",
            description="Electrical products",
        )
        session.add_all([mechanical, electrical])
        session.flush()

        # Matters
        steel = Matter(id=1, name="Steel", description="Steel material")
        aluminum = Matter(id=2, name="Aluminum", description="Aluminum material")
        plastic = Matter(id=3, name="Plastic", description="Plastic material")
        session.add_all([steel, aluminum, plastic])
        session.flush()

        # Sales Types
        retail = SalesType(id=1, name="Retail", description="Retail sales")
        wholesale = SalesType(id=2, name="Wholesale", description="Wholesale sales")
        export = SalesType(id=3, name="Export", description="Export sales")
        session.add_all([retail, wholesale, export])
        session.flush()

        # Quote Statuses
        quote_draft = QuoteStatus(
            id=1,
            code="draft",
            name="Draft",
            description="Draft quote",
        )
        quote_sent = QuoteStatus(
            id=2,
            code="sent",
            name="Sent",
            description="Quote sent to customer",
        )
        quote_accepted = QuoteStatus(
            id=3,
            code="accepted",
            name="Accepted",
            description="Quote accepted by customer",
        )
        session.add_all([quote_draft, quote_sent, quote_accepted])
        session.flush()

        # Order Statuses
        order_pending = OrderStatus(
            id=1,
            code="pending",
            name="Pending",
            description="Pending order",
        )
        order_confirmed = OrderStatus(
            id=2,
            code="confirmed",
            name="Confirmed",
            description="Confirmed order",
        )
        order_shipped = OrderStatus(
            id=3,
            code="shipped",
            name="Shipped",
            description="Order shipped",
        )
        session.add_all([order_pending, order_confirmed, order_shipped])
        session.flush()

        # Payment Statuses
        payment_pending = PaymentStatus(
            id=1,
            code="pending",
            name="Pending",
            description="Payment pending",
        )
        payment_partial = PaymentStatus(
            id=2,
            code="partial",
            name="Partial",
            description="Partial payment received",
        )
        payment_paid = PaymentStatus(
            id=3,
            code="paid",
            name="Paid",
            description="Fully paid",
        )
        session.add_all([payment_pending, payment_partial, payment_paid])
        session.flush()

        session.commit()

    except Exception as e:
        session.rollback()
        raise e

    # Yield session for test
    yield session

    # Cleanup
    session.close()


@pytest.fixture
def sample_country(session):
    """Get Chile from the database."""
    from models.lookups import Country
    return session.query(Country).filter_by(iso_code_alpha2="CL").first()


@pytest.fixture
def sample_city(session):
    """Get Santiago from the database."""
    from models.lookups import City
    return session.query(City).filter_by(name="Santiago").first()


@pytest.fixture
def sample_company_type(session):
    """Get CLIENT company type from the database."""
    from models.lookups import CompanyType
    return session.query(CompanyType).filter_by(name="CLIENT").first()


@pytest.fixture
def sample_currency(session):
    """Get CLP currency from the database."""
    from models.lookups import Currency
    return session.query(Currency).filter_by(code="CLP").first()


@pytest.fixture
def sample_family_type(session):
    """Get Mechanical family type from the database."""
    from models.lookups import FamilyType
    return session.query(FamilyType).filter_by(name="Mechanical").first()


@pytest.fixture
def sample_quote_status(session):
    """Get draft quote status from the database."""
    from models.lookups import QuoteStatus
    return session.query(QuoteStatus).filter_by(code="draft").first()


@pytest.fixture
def sample_order_status(session):
    """Get pending order status from the database."""
    from models.lookups import OrderStatus
    return session.query(OrderStatus).filter_by(code="pending").first()


@pytest.fixture
def sample_payment_status(session):
    """Get pending payment status from the database."""
    from models.lookups import PaymentStatus
    return session.query(PaymentStatus).filter_by(code="pending").first()
