"""
Unit tests for Order model.

Tests validation, business logic, and quote conversion for orders.
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.business.orders import Order


# Test fixtures
@pytest.fixture
def engine():
    """Create in-memory SQLite database for testing."""
    return create_engine("sqlite:///:memory:")


@pytest.fixture
def session(engine):
    """Create database session."""
    try:
        from models.base import Base
    except ImportError:
        from models.business.orders import Base

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


class TestOrder:
    """Test suite for Order model."""

    def test_create_order(self, session):
        """Test creating a basic order."""
        order = Order(
            order_number="O-2025-001",
            order_type="sales",
            company_id=1,
            staff_id=1,
            status_id=1,
            payment_status_id=1,
            order_date=date.today(),
            currency_id=1,
            subtotal=Decimal("1000.00"),
            tax_percentage=Decimal("19.00"),
            total=Decimal("1190.00"),
        )

        session.add(order)
        session.commit()

        assert order.id is not None
        assert order.order_number == "O-2025-001"
        assert order.order_type == "sales"
        assert order.total == Decimal("1190.00")

    def test_order_number_validation(self, session):
        """Test order number validation."""
        order = Order(
            order_number="  o-2025-002  ",  # Test trimming and uppercase
            order_type="sales",
            company_id=1,
            staff_id=1,
            status_id=1,
            payment_status_id=1,
            order_date=date.today(),
            currency_id=1,
        )

        assert order.order_number == "O-2025-002"

    def test_order_type_validation(self, session):
        """Test order type validation."""
        # Valid types
        order_sales = Order(
            order_number="O-2025-003",
            order_type="sales",
            company_id=1,
            staff_id=1,
            status_id=1,
            payment_status_id=1,
            order_date=date.today(),
            currency_id=1,
        )
        assert order_sales.order_type == "sales"

        order_purchase = Order(
            order_number="O-2025-004",
            order_type="purchase",
            company_id=1,
            staff_id=1,
            status_id=1,
            payment_status_id=1,
            order_date=date.today(),
            currency_id=1,
        )
        assert order_purchase.order_type == "purchase"

        # Invalid type
        with pytest.raises(ValueError, match="Order type must be one of"):
            order_invalid = Order(
                order_number="O-2025-005",
                order_type="invalid",
                company_id=1,
                staff_id=1,
                status_id=1,
                payment_status_id=1,
                order_date=date.today(),
                currency_id=1,
            )
            session.add(order_invalid)
            session.flush()

    def test_tax_percentage_validation(self, session):
        """Test tax percentage validation."""
        order = Order(
            order_number="O-2025-006",
            order_type="sales",
            company_id=1,
            staff_id=1,
            status_id=1,
            payment_status_id=1,
            order_date=date.today(),
            currency_id=1,
            tax_percentage=Decimal("19.00"),
        )
        assert order.tax_percentage == Decimal("19.00")

        # Invalid: negative
        with pytest.raises(ValueError, match="Tax percentage must be between 0 and 100"):
            order.tax_percentage = Decimal("-5.00")

        # Invalid: over 100
        with pytest.raises(ValueError, match="Tax percentage must be between 0 and 100"):
            order.tax_percentage = Decimal("150.00")

    def test_calculate_totals(self, session):
        """Test automatic total calculation."""
        order = Order(
            order_number="O-2025-007",
            order_type="sales",
            company_id=1,
            staff_id=1,
            status_id=1,
            payment_status_id=1,
            order_date=date.today(),
            currency_id=1,
            subtotal=Decimal("1000.00"),
            tax_percentage=Decimal("19.00"),
            shipping_cost=Decimal("50.00"),
            other_costs=Decimal("25.00"),
        )

        order.calculate_totals()

        # Tax: 1000 * 0.19 = 190
        # Total: 1000 + 190 + 50 + 25 = 1265
        assert order.tax_amount == Decimal("190.00")
        assert order.total == Decimal("1265.00")

    def test_is_overdue_property(self, session):
        """Test is_overdue property."""
        # Not overdue (future promised date)
        order = Order(
            order_number="O-2025-008",
            order_type="sales",
            company_id=1,
            staff_id=1,
            status_id=1,
            payment_status_id=1,
            order_date=date.today(),
            promised_date=date.today() + timedelta(days=10),
            currency_id=1,
        )
        assert order.is_overdue is False

        # Overdue (past promised date)
        order.promised_date = date.today() - timedelta(days=1)
        assert order.is_overdue is True

        # Not overdue (completed)
        order.completed_date = date.today()
        assert order.is_overdue is False

        # No promised date
        order.promised_date = None
        order.completed_date = None
        assert order.is_overdue is False

    def test_days_until_required_property(self, session):
        """Test days_until_required calculation."""
        order = Order(
            order_number="O-2025-009",
            order_type="sales",
            company_id=1,
            staff_id=1,
            status_id=1,
            payment_status_id=1,
            order_date=date.today(),
            required_date=date.today() + timedelta(days=15),
            currency_id=1,
        )

        assert order.days_until_required == 15

        # Completed orders return None
        order.completed_date = date.today()
        assert order.days_until_required is None

        # No required date
        order.completed_date = None
        order.required_date = None
        assert order.days_until_required is None

    def test_processing_days_property(self, session):
        """Test processing_days calculation."""
        order = Order(
            order_number="O-2025-010",
            order_type="sales",
            company_id=1,
            staff_id=1,
            status_id=1,
            payment_status_id=1,
            order_date=date.today() - timedelta(days=5),
            completed_date=date.today(),
            currency_id=1,
        )

        assert order.processing_days == 5

        # Not completed
        order.completed_date = None
        assert order.processing_days is None

    def test_is_export_flag(self, session):
        """Test is_export flag."""
        order_domestic = Order(
            order_number="O-2025-011",
            order_type="sales",
            company_id=1,
            staff_id=1,
            status_id=1,
            payment_status_id=1,
            order_date=date.today(),
            currency_id=1,
            is_export=False,
        )
        assert order_domestic.is_export is False

        order_export = Order(
            order_number="O-2025-012",
            order_type="sales",
            company_id=1,
            staff_id=1,
            status_id=1,
            payment_status_id=1,
            order_date=date.today(),
            currency_id=1,
            is_export=True,
        )
        assert order_export.is_export is True

    def test_repr(self, session):
        """Test string representation."""
        order = Order(
            id=1,
            order_number="O-2025-013",
            order_type="sales",
            company_id=1,
            staff_id=1,
            status_id=1,
            payment_status_id=1,
            order_date=date.today(),
            currency_id=1,
            total=Decimal("1500.00"),
        )

        repr_str = repr(order)
        assert "Order" in repr_str
        assert "O-2025-013" in repr_str
        assert "sales" in repr_str
        assert "1500.00" in repr_str


class TestOrderQuoteConversion:
    """Tests for converting quotes to orders."""

    def test_create_from_quote(self, session):
        """Test creating order from quote data."""
        # Mock quote object (simplified)
        class MockQuote:
            id = 1
            company_id = 10
            contact_id = 20
            branch_id = 30
            staff_id = 40
            incoterm_id = 50
            currency_id = 60
            exchange_rate = Decimal("850.00")
            subtotal = Decimal("1000.00")
            tax_percentage = Decimal("19.00")
            tax_amount = Decimal("190.00")
            total = Decimal("1190.00")
            notes = "Original quote notes"

        quote = MockQuote()

        order = Order(
            order_number="O-2025-100",
            order_type="sales",
            status_id=1,
            payment_status_id=1,
            order_date=date.today(),
        )

        order.create_from_quote(quote)

        # Verify data was copied
        assert order.quote_id == 1
        assert order.company_id == 10
        assert order.contact_id == 20
        assert order.branch_id == 30
        assert order.staff_id == 40
        assert order.incoterm_id == 50
        assert order.currency_id == 60
        assert order.exchange_rate == Decimal("850.00")
        assert order.subtotal == Decimal("1000.00")
        assert order.tax_percentage == Decimal("19.00")
        assert order.tax_amount == Decimal("190.00")
        assert order.total == Decimal("1190.00")
        assert order.notes == "Original quote notes"
