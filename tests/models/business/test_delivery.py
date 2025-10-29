"""
Unit tests for Delivery models.

Tests for DeliveryOrder, Transport, and PaymentCondition models.
"""

import pytest
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.business.delivery import (
    DeliveryOrder,
    DeliveryDate,
    Transport,
    PaymentCondition,
)


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
        from models.business.delivery import Base

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


class TestDeliveryOrder:
    """Test suite for DeliveryOrder model."""

    def test_create_delivery_order(self, session):
        """Test creating a basic delivery order."""
        delivery = DeliveryOrder(
            delivery_number="GD-2025-001",
            order_id=1,
            company_id=1,
            address_id=1,
            staff_id=1,
            delivery_date=date.today() + timedelta(days=7),
            status="pending",
        )

        session.add(delivery)
        session.commit()

        assert delivery.id is not None
        assert delivery.delivery_number == "GD-2025-001"
        assert delivery.status == "pending"

    def test_delivery_number_validation(self, session):
        """Test delivery number validation."""
        delivery = DeliveryOrder(
            delivery_number="  gd-2025-002  ",  # Test trimming and uppercase
            order_id=1,
            company_id=1,
            address_id=1,
            staff_id=1,
            delivery_date=date.today(),
            status="pending",
        )

        assert delivery.delivery_number == "GD-2025-002"

    def test_status_validation(self, session):
        """Test status validation."""
        # Valid statuses
        for status in ["pending", "in_transit", "delivered", "cancelled"]:
            delivery = DeliveryOrder(
                delivery_number=f"GD-2025-{status}",
                order_id=1,
                company_id=1,
                address_id=1,
                staff_id=1,
                delivery_date=date.today(),
                status=status,
            )
            assert delivery.status == status

        # Invalid status
        with pytest.raises(ValueError, match="Status must be one of"):
            delivery = DeliveryOrder(
                delivery_number="GD-2025-INVALID",
                order_id=1,
                company_id=1,
                address_id=1,
                staff_id=1,
                delivery_date=date.today(),
                status="invalid",
            )
            session.add(delivery)
            session.flush()

    def test_is_delivered_property(self, session):
        """Test is_delivered property."""
        delivery = DeliveryOrder(
            delivery_number="GD-2025-003",
            order_id=1,
            company_id=1,
            address_id=1,
            staff_id=1,
            delivery_date=date.today(),
            status="pending",
        )
        assert delivery.is_delivered is False

        # Mark as delivered
        delivery.status = "delivered"
        delivery.actual_delivery_date = date.today()
        assert delivery.is_delivered is True

    def test_is_late_property(self, session):
        """Test is_late property."""
        # Not late (future delivery)
        delivery = DeliveryOrder(
            delivery_number="GD-2025-004",
            order_id=1,
            company_id=1,
            address_id=1,
            staff_id=1,
            delivery_date=date.today() + timedelta(days=5),
            status="pending",
        )
        assert delivery.is_late is False

        # Late (past delivery date)
        delivery.delivery_date = date.today() - timedelta(days=2)
        assert delivery.is_late is True

        # Delivered late
        delivery.actual_delivery_date = date.today()
        delivery.status = "delivered"
        assert delivery.is_late is True

        # Delivered on time
        delivery.delivery_date = date.today()
        assert delivery.is_late is False

    def test_days_late_property(self, session):
        """Test days_late calculation."""
        delivery = DeliveryOrder(
            delivery_number="GD-2025-005",
            order_id=1,
            company_id=1,
            address_id=1,
            staff_id=1,
            delivery_date=date.today() - timedelta(days=3),
            status="pending",
        )

        assert delivery.days_late == 3

        # Not late
        delivery.delivery_date = date.today() + timedelta(days=5)
        assert delivery.days_late is None

    def test_mark_delivered(self, session):
        """Test marking delivery as completed."""
        delivery = DeliveryOrder(
            delivery_number="GD-2025-006",
            order_id=1,
            company_id=1,
            address_id=1,
            staff_id=1,
            delivery_date=date.today(),
            status="in_transit",
        )

        delivery.mark_delivered(
            signature_name="Juan Pérez",
            signature_id="12345678-9",
            notes="Delivered in good condition",
        )

        assert delivery.status == "delivered"
        assert delivery.actual_delivery_date == date.today()
        assert delivery.signature_name == "Juan Pérez"
        assert delivery.signature_id == "12345678-9"
        assert delivery.signature_datetime is not None
        assert "good condition" in delivery.notes


class TestTransport:
    """Test suite for Transport model."""

    def test_create_transport(self, session):
        """Test creating a transport company."""
        transport = Transport(
            name="Chilexpress",
            transport_type="courier",
            contact_name="Carlos Lopez",
            contact_phone="+56912345678",
            contact_email="carlos@chilexpress.cl",
            website="https://www.chilexpress.cl",
        )

        session.add(transport)
        session.commit()

        assert transport.id is not None
        assert transport.name == "Chilexpress"
        assert transport.transport_type == "courier"

    def test_name_validation(self, session):
        """Test name validation."""
        # Valid name
        transport = Transport(
            name="  FedEx Chile  ",  # Test trimming
            transport_type="carrier",
        )
        assert transport.name == "FedEx Chile"

        # Empty name
        with pytest.raises(ValueError, match="Transport name cannot be empty"):
            transport = Transport(name="", transport_type="carrier")
            session.add(transport)
            session.flush()

    def test_transport_type_validation(self, session):
        """Test transport type validation."""
        # Valid types
        for transport_type in ["own", "carrier", "courier", "freight_forwarder"]:
            transport = Transport(
                name=f"Transport {transport_type}",
                transport_type=transport_type,
            )
            assert transport.transport_type == transport_type

        # Invalid type
        with pytest.raises(ValueError, match="Transport type must be one of"):
            transport = Transport(name="Invalid Transport", transport_type="invalid")
            session.add(transport)
            session.flush()


class TestPaymentCondition:
    """Test suite for PaymentCondition model."""

    def test_create_payment_condition(self, session):
        """Test creating a payment condition."""
        payment_cond = PaymentCondition(
            code="NET30",
            name="Net 30 days",
            description="Full payment due 30 days after invoice",
            days_to_pay=30,
            percentage_advance=Decimal("0.00"),
            percentage_on_delivery=Decimal("0.00"),
            percentage_after_delivery=Decimal("100.00"),
            days_after_delivery=30,
        )

        session.add(payment_cond)
        session.commit()

        assert payment_cond.id is not None
        assert payment_cond.code == "NET30"
        assert payment_cond.days_to_pay == 30

    def test_code_validation(self, session):
        """Test code validation."""
        # Valid code (trimmed and uppercase)
        payment_cond = PaymentCondition(
            code="  net30  ",
            name="Net 30",
            percentage_advance=Decimal("0.00"),
            percentage_on_delivery=Decimal("0.00"),
            percentage_after_delivery=Decimal("100.00"),
        )
        assert payment_cond.code == "NET30"

        # Empty code
        with pytest.raises(ValueError, match="Payment condition code cannot be empty"):
            payment_cond = PaymentCondition(
                code="",
                name="Invalid",
                percentage_advance=Decimal("0.00"),
                percentage_on_delivery=Decimal("0.00"),
                percentage_after_delivery=Decimal("100.00"),
            )
            session.add(payment_cond)
            session.flush()

    def test_validate_percentages(self, session):
        """Test percentage validation."""
        # Valid percentages (sum to 100)
        payment_cond = PaymentCondition(
            code="50-50",
            name="50/50",
            percentage_advance=Decimal("50.00"),
            percentage_on_delivery=Decimal("50.00"),
            percentage_after_delivery=Decimal("0.00"),
        )

        payment_cond.validate_percentages()  # Should not raise

        # Invalid percentages (don't sum to 100)
        payment_cond.percentage_advance = Decimal("40.00")

        with pytest.raises(ValueError, match="Payment percentages must sum to 100"):
            payment_cond.validate_percentages()

    def test_summary_property(self, session):
        """Test summary property."""
        # NET30 payment terms
        payment_cond = PaymentCondition(
            code="NET30",
            name="Net 30 days",
            days_to_pay=30,
            percentage_advance=Decimal("0.00"),
            percentage_on_delivery=Decimal("0.00"),
            percentage_after_delivery=Decimal("100.00"),
            days_after_delivery=30,
        )

        summary = payment_cond.summary
        assert "100.0% 30 days after delivery" in summary

        # 50% advance, 50% on delivery
        payment_cond2 = PaymentCondition(
            code="50-50",
            name="50/50",
            percentage_advance=Decimal("50.00"),
            percentage_on_delivery=Decimal("50.00"),
            percentage_after_delivery=Decimal("0.00"),
        )

        summary2 = payment_cond2.summary
        assert "50.0% advance" in summary2
        assert "50.0% on delivery" in summary2

        # Cash on delivery
        payment_cond3 = PaymentCondition(
            code="COD",
            name="Cash on Delivery",
            percentage_advance=Decimal("0.00"),
            percentage_on_delivery=Decimal("100.00"),
            percentage_after_delivery=Decimal("0.00"),
        )

        summary3 = payment_cond3.summary
        assert "100.0% on delivery" in summary3

    def test_is_default_flag(self, session):
        """Test is_default flag."""
        payment_cond1 = PaymentCondition(
            code="NET30",
            name="Net 30",
            percentage_advance=Decimal("0.00"),
            percentage_on_delivery=Decimal("0.00"),
            percentage_after_delivery=Decimal("100.00"),
            is_default=True,
        )
        assert payment_cond1.is_default is True

        payment_cond2 = PaymentCondition(
            code="COD",
            name="COD",
            percentage_advance=Decimal("0.00"),
            percentage_on_delivery=Decimal("100.00"),
            percentage_after_delivery=Decimal("0.00"),
            is_default=False,
        )
        assert payment_cond2.is_default is False


class TestDeliveryDate:
    """Test suite for DeliveryDate model."""

    def test_create_delivery_date(self, session):
        """Test creating a delivery date."""
        delivery_date = DeliveryDate(
            delivery_order_id=1,
            planned_date=date.today() + timedelta(days=7),
            quantity=Decimal("50.000"),
            status="pending",
        )

        session.add(delivery_date)
        session.commit()

        assert delivery_date.id is not None
        assert delivery_date.quantity == Decimal("50.000")
        assert delivery_date.status == "pending"

    def test_status_validation(self, session):
        """Test status validation."""
        # Valid statuses
        for status in ["pending", "completed", "cancelled"]:
            delivery_date = DeliveryDate(
                delivery_order_id=1,
                planned_date=date.today(),
                status=status,
            )
            assert delivery_date.status == status

        # Invalid status
        with pytest.raises(ValueError, match="Status must be one of"):
            delivery_date = DeliveryDate(
                delivery_order_id=1,
                planned_date=date.today(),
                status="invalid",
            )
            session.add(delivery_date)
            session.flush()

    def test_quantity_validation(self, session):
        """Test quantity validation."""
        # Valid quantity
        delivery_date = DeliveryDate(
            delivery_order_id=1,
            planned_date=date.today(),
            quantity=Decimal("100.000"),
            status="pending",
        )
        assert delivery_date.quantity == Decimal("100.000")

        # Invalid: zero
        with pytest.raises(ValueError, match="Quantity must be positive"):
            delivery_date.quantity = Decimal("0.000")

        # Invalid: negative
        with pytest.raises(ValueError, match="Quantity must be positive"):
            delivery_date.quantity = Decimal("-10.000")

        # None is valid
        delivery_date.quantity = None
        assert delivery_date.quantity is None
