"""
Tests for delivery and logistics models from business.delivery.

This module contains comprehensive tests for delivery-related business models,
including CRUD operations, validators, relationships, and edge cases.

Test Coverage:
    DeliveryOrder:
        - Basic CRUD operations
        - Field validation (delivery_number, status)
        - Relationships (order, company, address, transport, staff)
        - Business properties (is_delivered, is_late, days_late)
        - Business methods (mark_delivered)
        - CheckConstraints (status validation)
        - Mixins (Timestamp, Audit, Active)

    DeliveryDate:
        - CRUD operations
        - Field validation (status, quantity)
        - Relationship with DeliveryOrder
        - CheckConstraints (positive quantity, status validation)
        - Cascade delete with DeliveryOrder

    Transport:
        - CRUD operations
        - Field validation (name, transport_type)
        - CheckConstraints (transport_type validation)
        - Unique name constraint
        - Mixins (Timestamp, Active)

    PaymentCondition:
        - CRUD operations
        - Field validation (payment_condition_number, name)
        - Percentage validations
        - Business methods (validate_percentages)
        - Business properties (summary)
        - CheckConstraints (percentage ranges, sum to 100)
"""

from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from src.backend.models.business.delivery import (
    DeliveryOrder,
    DeliveryDate,
    Transport,
    PaymentCondition,
)
from src.backend.models.core.companies import Company
from src.backend.models.lookups import Currency, PaymentType


# ============= DELIVERY ORDER MODEL TESTS =============


class TestDeliveryOrderCreation:
    """Tests for DeliveryOrder model instantiation and creation."""

    def test_create_delivery_order_with_all_fields(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """
        Test creating a DeliveryOrder with all fields populated.

        This test verifies that a DeliveryOrder can be created with complete data
        and all fields are properly stored in the database.
        """
        # Create required dependencies
        from src.backend.models.core.staff import Staff
        from src.backend.models.core.addresses import Address
        from src.backend.models.lookups import OrderStatus, PaymentStatus
        from src.backend.models.business.orders import Order

        staff = Staff(
            username="testuser_del1",
            email="del1@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="confirmed", name="Confirmed", description="Confirmed")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        # Create order
        order = Order(
            order_number="O-DEL-001",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order)
        session.commit()

        # Create address
        address = Address(
            address="Test Street 123",
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()

        # Create transport
        transport = Transport(
            name="Express Delivery Inc",
            transport_type="carrier",
        )
        session.add(transport)
        session.commit()

        # Arrange & Act
        delivery = DeliveryOrder(
            delivery_number="GD-2025-001",
            revision="A",
            order_id=order.id,
            company_id=sample_company.id,
            address_id=address.id,
            transport_id=transport.id,
            staff_id=staff.id,
            delivery_date=date(2025, 2, 1),
            actual_delivery_date=date(2025, 2, 1),
            status="delivered",
            tracking_number="TRACK123456",
            delivery_instructions="Leave at front door",
            signature_name="John Doe",
            signature_id="12345678-9",
            signature_datetime=datetime.now(),
            notes="Delivered successfully",
            is_active=True,
        )
        session.add(delivery)
        session.commit()
        session.refresh(delivery)

        # Assert
        assert delivery.id is not None
        assert delivery.delivery_number == "GD-2025-001"
        assert delivery.revision == "A"
        assert delivery.order_id == order.id
        assert delivery.company_id == sample_company.id
        assert delivery.address_id == address.id
        assert delivery.transport_id == transport.id
        assert delivery.staff_id == staff.id
        assert delivery.delivery_date == date(2025, 2, 1)
        assert delivery.actual_delivery_date == date(2025, 2, 1)
        assert delivery.status == "delivered"
        assert delivery.tracking_number == "TRACK123456"
        assert delivery.signature_name == "John Doe"
        assert delivery.is_active is True

    def test_create_delivery_order_with_minimal_fields(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test creating DeliveryOrder with only required fields."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.core.addresses import Address
        from src.backend.models.lookups import OrderStatus, PaymentStatus
        from src.backend.models.business.orders import Order

        staff = Staff(
            username="testuser_del2",
            email="del2@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="pending", name="Pending", description="Pending")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        order = Order(
            order_number="O-DEL-002",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order)
        session.commit()

        address = Address(
            address="Test Street 456",
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()

        # Arrange & Act
        delivery = DeliveryOrder(
            delivery_number="GD-2025-002",
            order_id=order.id,
            company_id=sample_company.id,
            address_id=address.id,
            staff_id=staff.id,
            delivery_date=date.today(),
        )
        session.add(delivery)
        session.commit()
        session.refresh(delivery)

        # Assert
        assert delivery.id is not None
        assert delivery.delivery_number == "GD-2025-002"
        assert delivery.revision == "A"  # Default
        assert delivery.status == "pending"  # Default
        assert delivery.is_active is True  # Default from ActiveMixin


class TestDeliveryOrderValidation:
    """Tests for DeliveryOrder field validators and constraints."""

    def test_delivery_number_validator_strips_and_uppercases(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test that delivery_number is stripped and converted to uppercase."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.core.addresses import Address
        from src.backend.models.lookups import OrderStatus, PaymentStatus
        from src.backend.models.business.orders import Order

        staff = Staff(
            username="testuser_del3",
            email="del3@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="pending", name="Pending", description="Pending")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        order = Order(
            order_number="O-DEL-003",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order)
        session.commit()

        address = Address(
            address="Test Street 789",
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()

        # Arrange & Act
        delivery = DeliveryOrder(
            delivery_number="  gd-2025-003  ",  # lowercase with whitespace
            order_id=order.id,
            company_id=sample_company.id,
            address_id=address.id,
            staff_id=staff.id,
            delivery_date=date.today(),
        )
        session.add(delivery)
        session.commit()
        session.refresh(delivery)

        # Assert
        assert delivery.delivery_number == "GD-2025-003"  # Uppercase and trimmed

    def test_delivery_number_cannot_be_empty(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test that delivery_number cannot be empty."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.core.addresses import Address
        from src.backend.models.lookups import OrderStatus, PaymentStatus
        from src.backend.models.business.orders import Order

        staff = Staff(
            username="testuser_del4",
            email="del4@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="pending", name="Pending", description="Pending")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        order = Order(
            order_number="O-DEL-004",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order)
        session.commit()

        address = Address(
            address="Test Street 100",
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()

        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Delivery number cannot be empty"):
            delivery = DeliveryOrder(
                delivery_number="   ",  # Empty after strip
                order_id=order.id,
                company_id=sample_company.id,
                address_id=address.id,
                staff_id=staff.id,
                delivery_date=date.today(),
            )

    def test_status_validation_valid_statuses(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test that valid status values are accepted."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.core.addresses import Address
        from src.backend.models.lookups import OrderStatus, PaymentStatus
        from src.backend.models.business.orders import Order

        staff = Staff(
            username="testuser_del5",
            email="del5@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="confirmed", name="Confirmed", description="Confirmed")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        valid_statuses = ["pending", "in_transit", "delivered", "cancelled"]

        for idx, status_val in enumerate(valid_statuses):
            order = Order(
                order_number=f"O-DEL-STATUS-{idx}",
                company_id=sample_company.id,
                staff_id=staff.id,
                status_id=order_status.id,
                payment_status_id=payment_status.id,
                order_date=date.today(),
                currency_id=sample_currency.id,
            )
            session.add(order)
            session.commit()

            address = Address(
                address=f"Test Street {idx}",
                company_id=sample_company.id,
            )
            session.add(address)
            session.commit()

            delivery = DeliveryOrder(
                delivery_number=f"GD-STATUS-{idx}",
                status=status_val,
                order_id=order.id,
                company_id=sample_company.id,
                address_id=address.id,
                staff_id=staff.id,
                delivery_date=date.today(),
            )
            session.add(delivery)
            session.commit()
            session.refresh(delivery)
            assert delivery.status == status_val
            session.rollback()

    def test_status_validation_invalid(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test that invalid status raises ValueError."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.core.addresses import Address
        from src.backend.models.lookups import OrderStatus, PaymentStatus
        from src.backend.models.business.orders import Order

        staff = Staff(
            username="testuser_del6",
            email="del6@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="pending", name="Pending", description="Pending")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        order = Order(
            order_number="O-DEL-006",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order)
        session.commit()

        address = Address(
            address="Test Street 200",
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()

        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Status must be one of"):
            delivery = DeliveryOrder(
                delivery_number="GD-INVALID",
                status="invalid_status",
                order_id=order.id,
                company_id=sample_company.id,
                address_id=address.id,
                staff_id=staff.id,
                delivery_date=date.today(),
            )


class TestDeliveryOrderBusinessMethods:
    """Tests for DeliveryOrder business methods and properties."""

    def test_is_delivered_property_true(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test is_delivered returns True when delivered with actual date."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.core.addresses import Address
        from src.backend.models.lookups import OrderStatus, PaymentStatus
        from src.backend.models.business.orders import Order

        staff = Staff(
            username="testuser_del7",
            email="del7@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="completed", name="Completed", description="Completed")
        session.add(order_status)

        payment_status = PaymentStatus(code="paid", name="Paid", description="Paid")
        session.add(payment_status)
        session.commit()

        order = Order(
            order_number="O-DEL-007",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order)
        session.commit()

        address = Address(
            address="Test Street 300",
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()

        delivery = DeliveryOrder(
            delivery_number="GD-2025-007",
            order_id=order.id,
            company_id=sample_company.id,
            address_id=address.id,
            staff_id=staff.id,
            delivery_date=date.today(),
            actual_delivery_date=date.today(),
            status="delivered",
        )
        session.add(delivery)
        session.commit()
        session.refresh(delivery)

        # Assert
        assert delivery.is_delivered is True

    def test_is_delivered_property_false_when_not_delivered(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test is_delivered returns False when not delivered."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.core.addresses import Address
        from src.backend.models.lookups import OrderStatus, PaymentStatus
        from src.backend.models.business.orders import Order

        staff = Staff(
            username="testuser_del8",
            email="del8@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="pending", name="Pending", description="Pending")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        order = Order(
            order_number="O-DEL-008",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order)
        session.commit()

        address = Address(
            address="Test Street 400",
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()

        delivery = DeliveryOrder(
            delivery_number="GD-2025-008",
            order_id=order.id,
            company_id=sample_company.id,
            address_id=address.id,
            staff_id=staff.id,
            delivery_date=date.today(),
            status="pending",
        )
        session.add(delivery)
        session.commit()
        session.refresh(delivery)

        # Assert
        assert delivery.is_delivered is False

    def test_is_late_property_true_when_delivered_late(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test is_late returns True when delivered after planned date."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.core.addresses import Address
        from src.backend.models.lookups import OrderStatus, PaymentStatus
        from src.backend.models.business.orders import Order

        staff = Staff(
            username="testuser_del9",
            email="del9@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="completed", name="Completed", description="Completed")
        session.add(order_status)

        payment_status = PaymentStatus(code="paid", name="Paid", description="Paid")
        session.add(payment_status)
        session.commit()

        order = Order(
            order_number="O-DEL-009",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order)
        session.commit()

        address = Address(
            address="Test Street 500",
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()

        delivery = DeliveryOrder(
            delivery_number="GD-2025-009",
            order_id=order.id,
            company_id=sample_company.id,
            address_id=address.id,
            staff_id=staff.id,
            delivery_date=date.today() - timedelta(days=5),
            actual_delivery_date=date.today(),
            status="delivered",
        )
        session.add(delivery)
        session.commit()
        session.refresh(delivery)

        # Assert
        assert delivery.is_late is True

    def test_days_late_property(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test days_late property calculates correctly."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.core.addresses import Address
        from src.backend.models.lookups import OrderStatus, PaymentStatus
        from src.backend.models.business.orders import Order

        staff = Staff(
            username="testuser_del10",
            email="del10@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="completed", name="Completed", description="Completed")
        session.add(order_status)

        payment_status = PaymentStatus(code="paid", name="Paid", description="Paid")
        session.add(payment_status)
        session.commit()

        order = Order(
            order_number="O-DEL-010",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order)
        session.commit()

        address = Address(
            address="Test Street 600",
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()

        planned_date = date(2025, 1, 1)
        actual_date = date(2025, 1, 8)

        delivery = DeliveryOrder(
            delivery_number="GD-2025-010",
            order_id=order.id,
            company_id=sample_company.id,
            address_id=address.id,
            staff_id=staff.id,
            delivery_date=planned_date,
            actual_delivery_date=actual_date,
            status="delivered",
        )
        session.add(delivery)
        session.commit()
        session.refresh(delivery)

        # Assert
        assert delivery.days_late == 7

    def test_mark_delivered_method(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test mark_delivered method updates delivery status and signature."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.core.addresses import Address
        from src.backend.models.lookups import OrderStatus, PaymentStatus
        from src.backend.models.business.orders import Order

        staff = Staff(
            username="testuser_del11",
            email="del11@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="pending", name="Pending", description="Pending")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        order = Order(
            order_number="O-DEL-011",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order)
        session.commit()

        address = Address(
            address="Test Street 700",
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()

        delivery = DeliveryOrder(
            delivery_number="GD-2025-011",
            order_id=order.id,
            company_id=sample_company.id,
            address_id=address.id,
            staff_id=staff.id,
            delivery_date=date.today(),
            status="in_transit",
        )
        session.add(delivery)
        session.commit()
        session.refresh(delivery)

        # Act
        delivery.mark_delivered(
            signature_name="Jane Smith",
            signature_id="98765432-1",
            notes="Left at reception",
        )
        session.commit()
        session.refresh(delivery)

        # Assert
        assert delivery.status == "delivered"
        assert delivery.actual_delivery_date == date.today()
        assert delivery.signature_name == "Jane Smith"
        assert delivery.signature_id == "98765432-1"
        assert delivery.signature_datetime is not None
        assert delivery.notes == "Left at reception"


class TestDeliveryOrderRepr:
    """Tests for DeliveryOrder __repr__ method."""

    def test_delivery_order_repr(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test DeliveryOrder string representation."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.core.addresses import Address
        from src.backend.models.lookups import OrderStatus, PaymentStatus
        from src.backend.models.business.orders import Order

        staff = Staff(
            username="testuser_del12",
            email="del12@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="pending", name="Pending", description="Pending")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        order = Order(
            order_number="O-DEL-012",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order)
        session.commit()

        address = Address(
            address="Test Street 800",
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()

        delivery = DeliveryOrder(
            delivery_number="GD-REPR",
            order_id=order.id,
            company_id=sample_company.id,
            address_id=address.id,
            staff_id=staff.id,
            delivery_date=date.today(),
            status="pending",
        )
        session.add(delivery)
        session.commit()
        session.refresh(delivery)

        # Act
        repr_str = repr(delivery)

        # Assert
        assert "DeliveryOrder" in repr_str
        assert "GD-REPR" in repr_str
        assert "pending" in repr_str


# ============= DELIVERY DATE MODEL TESTS =============


class TestDeliveryDateCreation:
    """Tests for DeliveryDate model instantiation and creation."""

    def test_create_delivery_date_with_all_fields(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test creating a DeliveryDate with all fields populated."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.core.addresses import Address
        from src.backend.models.lookups import OrderStatus, PaymentStatus
        from src.backend.models.business.orders import Order

        staff = Staff(
            username="testuser_dd1",
            email="dd1@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="pending", name="Pending", description="Pending")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        order = Order(
            order_number="O-DD-001",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order)
        session.commit()

        address = Address(
            address="Test Street 900",
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()

        delivery_order = DeliveryOrder(
            delivery_number="GD-DD-001",
            order_id=order.id,
            company_id=sample_company.id,
            address_id=address.id,
            staff_id=staff.id,
            delivery_date=date.today(),
        )
        session.add(delivery_order)
        session.commit()

        # Arrange & Act
        delivery_date = DeliveryDate(
            delivery_order_id=delivery_order.id,
            planned_date=date(2025, 2, 1),
            actual_date=date(2025, 2, 1),
            quantity=Decimal("100.500"),
            status="completed",
            notes="First shipment",
        )
        session.add(delivery_date)
        session.commit()
        session.refresh(delivery_date)

        # Assert
        assert delivery_date.id is not None
        assert delivery_date.delivery_order_id == delivery_order.id
        assert delivery_date.planned_date == date(2025, 2, 1)
        assert delivery_date.actual_date == date(2025, 2, 1)
        assert delivery_date.quantity == Decimal("100.500")
        assert delivery_date.status == "completed"
        assert delivery_date.notes == "First shipment"

    def test_create_delivery_date_with_minimal_fields(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test creating DeliveryDate with only required fields."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.core.addresses import Address
        from src.backend.models.lookups import OrderStatus, PaymentStatus
        from src.backend.models.business.orders import Order

        staff = Staff(
            username="testuser_dd2",
            email="dd2@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="pending", name="Pending", description="Pending")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        order = Order(
            order_number="O-DD-002",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order)
        session.commit()

        address = Address(
            address="Test Street 1000",
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()

        delivery_order = DeliveryOrder(
            delivery_number="GD-DD-002",
            order_id=order.id,
            company_id=sample_company.id,
            address_id=address.id,
            staff_id=staff.id,
            delivery_date=date.today(),
        )
        session.add(delivery_order)
        session.commit()

        # Arrange & Act
        delivery_date = DeliveryDate(
            delivery_order_id=delivery_order.id,
            planned_date=date.today(),
        )
        session.add(delivery_date)
        session.commit()
        session.refresh(delivery_date)

        # Assert
        assert delivery_date.id is not None
        assert delivery_date.status == "pending"  # Default


class TestDeliveryDateValidation:
    """Tests for DeliveryDate field validators and constraints."""

    def test_status_validation_valid_statuses(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test that valid status values are accepted."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.core.addresses import Address
        from src.backend.models.lookups import OrderStatus, PaymentStatus
        from src.backend.models.business.orders import Order

        staff = Staff(
            username="testuser_dd3",
            email="dd3@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="pending", name="Pending", description="Pending")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        order = Order(
            order_number="O-DD-003",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order)
        session.commit()

        address = Address(
            address="Test Street 1100",
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()

        delivery_order = DeliveryOrder(
            delivery_number="GD-DD-003",
            order_id=order.id,
            company_id=sample_company.id,
            address_id=address.id,
            staff_id=staff.id,
            delivery_date=date.today(),
        )
        session.add(delivery_order)
        session.commit()

        valid_statuses = ["pending", "completed", "cancelled"]

        for status_val in valid_statuses:
            delivery_date = DeliveryDate(
                delivery_order_id=delivery_order.id,
                planned_date=date.today(),
                status=status_val,
            )
            session.add(delivery_date)
            session.commit()
            session.refresh(delivery_date)
            assert delivery_date.status == status_val
            session.rollback()

    def test_status_validation_invalid(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test that invalid status raises ValueError."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.core.addresses import Address
        from src.backend.models.lookups import OrderStatus, PaymentStatus
        from src.backend.models.business.orders import Order

        staff = Staff(
            username="testuser_dd4",
            email="dd4@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="pending", name="Pending", description="Pending")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        order = Order(
            order_number="O-DD-004",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order)
        session.commit()

        address = Address(
            address="Test Street 1200",
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()

        delivery_order = DeliveryOrder(
            delivery_number="GD-DD-004",
            order_id=order.id,
            company_id=sample_company.id,
            address_id=address.id,
            staff_id=staff.id,
            delivery_date=date.today(),
        )
        session.add(delivery_order)
        session.commit()

        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Status must be one of"):
            delivery_date = DeliveryDate(
                delivery_order_id=delivery_order.id,
                planned_date=date.today(),
                status="invalid_status",
            )

    def test_quantity_validation_positive(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test that positive quantity is valid."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.core.addresses import Address
        from src.backend.models.lookups import OrderStatus, PaymentStatus
        from src.backend.models.business.orders import Order

        staff = Staff(
            username="testuser_dd5",
            email="dd5@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="pending", name="Pending", description="Pending")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        order = Order(
            order_number="O-DD-005",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order)
        session.commit()

        address = Address(
            address="Test Street 1300",
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()

        delivery_order = DeliveryOrder(
            delivery_number="GD-DD-005",
            order_id=order.id,
            company_id=sample_company.id,
            address_id=address.id,
            staff_id=staff.id,
            delivery_date=date.today(),
        )
        session.add(delivery_order)
        session.commit()

        # Arrange & Act
        delivery_date = DeliveryDate(
            delivery_order_id=delivery_order.id,
            planned_date=date.today(),
            quantity=Decimal("50.000"),
        )
        session.add(delivery_date)
        session.commit()
        session.refresh(delivery_date)

        # Assert
        assert delivery_date.quantity == Decimal("50.000")

    def test_quantity_validation_negative_or_zero(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test that negative or zero quantity raises ValueError."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.core.addresses import Address
        from src.backend.models.lookups import OrderStatus, PaymentStatus
        from src.backend.models.business.orders import Order

        staff = Staff(
            username="testuser_dd6",
            email="dd6@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="pending", name="Pending", description="Pending")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        order = Order(
            order_number="O-DD-006",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order)
        session.commit()

        address = Address(
            address="Test Street 1400",
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()

        delivery_order = DeliveryOrder(
            delivery_number="GD-DD-006",
            order_id=order.id,
            company_id=sample_company.id,
            address_id=address.id,
            staff_id=staff.id,
            delivery_date=date.today(),
        )
        session.add(delivery_order)
        session.commit()

        # Test zero
        with pytest.raises(ValueError, match="Quantity must be positive"):
            delivery_date = DeliveryDate(
                delivery_order_id=delivery_order.id,
                planned_date=date.today(),
                quantity=Decimal("0.000"),
            )

        # Test negative
        with pytest.raises(ValueError, match="Quantity must be positive"):
            delivery_date = DeliveryDate(
                delivery_order_id=delivery_order.id,
                planned_date=date.today(),
                quantity=Decimal("-10.000"),
            )


# ============= TRANSPORT MODEL TESTS =============


class TestTransportCreation:
    """Tests for Transport model instantiation and creation."""

    def test_create_transport_with_all_fields(self, session):
        """Test creating a Transport with all fields populated."""
        # Arrange & Act
        transport = Transport(
            name="Fast Logistics Co.",
            delivery_number="TRACK-001",
            transport_type="carrier",
            contact_name="John Transport",
            contact_phone="+56912345678",
            contact_email="contact@fastlogistics.com",
            website="https://fastlogistics.com",
            notes="Reliable carrier",
            is_active=True,
        )
        session.add(transport)
        session.commit()
        session.refresh(transport)

        # Assert
        assert transport.id is not None
        assert transport.name == "Fast Logistics Co."
        assert transport.delivery_number == "TRACK-001"
        assert transport.transport_type == "carrier"
        assert transport.contact_name == "John Transport"
        assert transport.contact_phone == "+56912345678"
        assert transport.contact_email == "contact@fastlogistics.com"
        assert transport.website == "https://fastlogistics.com"
        assert transport.is_active is True

    def test_create_transport_with_minimal_fields(self, session):
        """Test creating Transport with only required fields."""
        # Arrange & Act
        transport = Transport(
            name="Minimal Transport",
        )
        session.add(transport)
        session.commit()
        session.refresh(transport)

        # Assert
        assert transport.id is not None
        assert transport.name == "Minimal Transport"
        assert transport.transport_type == "carrier"  # Default
        assert transport.is_active is True  # Default from ActiveMixin


class TestTransportValidation:
    """Tests for Transport field validators and constraints."""

    def test_name_validator_strips(self, session):
        """Test that name is stripped."""
        # Arrange & Act
        transport = Transport(
            name="  Transport Name  ",
        )
        session.add(transport)
        session.commit()
        session.refresh(transport)

        # Assert
        assert transport.name == "Transport Name"

    def test_name_cannot_be_empty(self, session):
        """Test that name cannot be empty."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Transport name cannot be empty"):
            transport = Transport(
                name="   ",
            )

    def test_transport_type_validation_valid_types(self, session):
        """Test that valid transport_type values are accepted."""
        valid_types = ["own", "carrier", "courier", "freight_forwarder"]

        for t_type in valid_types:
            transport = Transport(
                name=f"Transport {t_type}",
                transport_type=t_type,
            )
            session.add(transport)
            session.commit()
            session.refresh(transport)
            assert transport.transport_type == t_type
            session.rollback()

    def test_transport_type_validation_invalid(self, session):
        """Test that invalid transport_type raises ValueError."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Transport type must be one of"):
            transport = Transport(
                name="Invalid Transport",
                transport_type="invalid_type",
            )

    def test_name_unique_constraint(self, session):
        """Test that transport name must be unique."""
        # Create first transport
        transport1 = Transport(
            name="Unique Transport",
        )
        session.add(transport1)
        session.commit()

        # Try to create duplicate
        transport2 = Transport(
            name="Unique Transport",
        )
        session.add(transport2)

        # Assert
        with pytest.raises(IntegrityError):
            session.commit()


class TestTransportRepr:
    """Tests for Transport __repr__ method."""

    def test_transport_repr(self, session):
        """Test Transport string representation."""
        # Arrange
        transport = Transport(
            name="Test Transport",
            transport_type="courier",
        )
        session.add(transport)
        session.commit()
        session.refresh(transport)

        # Act
        repr_str = repr(transport)

        # Assert
        assert "Transport" in repr_str
        assert "Test Transport" in repr_str
        assert "courier" in repr_str


# ============= PAYMENT CONDITION MODEL TESTS =============


class TestPaymentConditionCreation:
    """Tests for PaymentCondition model instantiation and creation."""

    def test_create_payment_condition_with_all_fields(self, session, sample_payment_type):
        """Test creating a PaymentCondition with all fields populated."""
        # Arrange & Act
        payment_cond = PaymentCondition(
            payment_condition_number="50-50",
            name="50% Advance, 50% On Delivery",
            revision="A",
            description="Half payment upfront, half on delivery",
            payment_type_id=sample_payment_type.id,
            days_to_pay=None,
            percentage_advance=Decimal("50.00"),
            percentage_on_delivery=Decimal("50.00"),
            percentage_after_delivery=Decimal("0.00"),
            days_after_delivery=None,
            is_default=False,
            notes="Standard payment terms",
            is_active=True,
        )
        session.add(payment_cond)
        session.commit()
        session.refresh(payment_cond)

        # Assert
        assert payment_cond.id is not None
        assert payment_cond.payment_condition_number == "50-50"
        assert payment_cond.name == "50% Advance, 50% On Delivery"
        assert payment_cond.revision == "A"
        assert payment_cond.percentage_advance == Decimal("50.00")
        assert payment_cond.percentage_on_delivery == Decimal("50.00")
        assert payment_cond.percentage_after_delivery == Decimal("0.00")
        assert payment_cond.is_default is False
        assert payment_cond.is_active is True

    def test_create_payment_condition_with_minimal_fields(self, session, sample_payment_type):
        """Test creating PaymentCondition with only required fields."""
        # Arrange & Act
        payment_cond = PaymentCondition(
            payment_condition_number="NET30",
            name="Net 30 Days",
            payment_type_id=sample_payment_type.id,
            percentage_advance=Decimal("0.00"),
            percentage_on_delivery=Decimal("0.00"),
            percentage_after_delivery=Decimal("100.00"),
            days_to_pay=30,
        )
        session.add(payment_cond)
        session.commit()
        session.refresh(payment_cond)

        # Assert
        assert payment_cond.id is not None
        assert payment_cond.payment_condition_number == "NET30"
        assert payment_cond.revision == "A"  # Default
        assert payment_cond.is_default is False  # Default
        assert payment_cond.is_active is True  # Default from ActiveMixin


class TestPaymentConditionValidation:
    """Tests for PaymentCondition field validators and constraints."""

    def test_payment_condition_number_validator_strips_and_uppercases(self, session, sample_payment_type):
        """Test that payment_condition_number is stripped and converted to uppercase."""
        # Arrange & Act
        payment_cond = PaymentCondition(
            payment_condition_number="  net60  ",
            name="Net 60 Days",
            payment_type_id=sample_payment_type.id,
            percentage_advance=Decimal("0.00"),
            percentage_on_delivery=Decimal("0.00"),
            percentage_after_delivery=Decimal("100.00"),
        )
        session.add(payment_cond)
        session.commit()
        session.refresh(payment_cond)

        # Assert
        assert payment_cond.payment_condition_number == "NET60"

    def test_payment_condition_number_cannot_be_empty(self, session):
        """Test that payment_condition_number cannot be empty."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Payment condition number cannot be empty"):
            payment_cond = PaymentCondition(
                payment_condition_number="   ",
                name="Empty Code",
                percentage_advance=Decimal("0.00"),
                percentage_on_delivery=Decimal("0.00"),
                percentage_after_delivery=Decimal("100.00"),
            )

    def test_name_validator_strips(self, session, sample_payment_type):
        """Test that name is stripped."""
        # Arrange & Act
        payment_cond = PaymentCondition(
            payment_condition_number="TEST",
            name="  Test Name  ",
            payment_type_id=sample_payment_type.id,
            percentage_advance=Decimal("0.00"),
            percentage_on_delivery=Decimal("0.00"),
            percentage_after_delivery=Decimal("100.00"),
        )
        session.add(payment_cond)
        session.commit()
        session.refresh(payment_cond)

        # Assert
        assert payment_cond.name == "Test Name"

    def test_name_cannot_be_empty(self, session):
        """Test that name cannot be empty."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Payment condition name cannot be empty"):
            payment_cond = PaymentCondition(
                payment_condition_number="TEST",
                name="   ",
                percentage_advance=Decimal("0.00"),
                percentage_on_delivery=Decimal("0.00"),
                percentage_after_delivery=Decimal("100.00"),
            )


class TestPaymentConditionConstraints:
    """Tests for PaymentCondition database constraints."""

    def test_payment_condition_number_unique_constraint(self, session, sample_payment_type):
        """Test that payment condition number must be unique."""
        # Create first payment condition
        payment_cond1 = PaymentCondition(
            payment_condition_number="UNIQUE",
            name="First",
            payment_type_id=sample_payment_type.id,
            percentage_advance=Decimal("0.00"),
            percentage_on_delivery=Decimal("0.00"),
            percentage_after_delivery=Decimal("100.00"),
        )
        session.add(payment_cond1)
        session.commit()

        # Try to create duplicate
        payment_cond2 = PaymentCondition(
            payment_condition_number="UNIQUE",
            name="Second",
            payment_type_id=sample_payment_type.id,
            percentage_advance=Decimal("0.00"),
            percentage_on_delivery=Decimal("0.00"),
            percentage_after_delivery=Decimal("100.00"),
        )
        session.add(payment_cond2)

        # Assert
        with pytest.raises(IntegrityError):
            session.commit()

    def test_check_constraint_percentages_sum_100(self, session, sample_payment_type):
        """Test that percentages must sum to exactly 100."""
        # Test valid sum (100)
        payment_cond = PaymentCondition(
            payment_condition_number="VALID",
            name="Valid",
            payment_type_id=sample_payment_type.id,
            percentage_advance=Decimal("30.00"),
            percentage_on_delivery=Decimal("40.00"),
            percentage_after_delivery=Decimal("30.00"),
        )
        session.add(payment_cond)
        session.commit()
        session.refresh(payment_cond)
        assert payment_cond.id is not None
        session.rollback()

        # Test invalid sum (not 100)
        payment_cond2 = PaymentCondition(
            payment_condition_number="INVALID",
            name="Invalid",
            payment_type_id=sample_payment_type.id,
            percentage_advance=Decimal("30.00"),
            percentage_on_delivery=Decimal("40.00"),
            percentage_after_delivery=Decimal("40.00"),  # Sums to 110
        )
        session.add(payment_cond2)

        with pytest.raises(IntegrityError):
            session.commit()


class TestPaymentConditionBusinessMethods:
    """Tests for PaymentCondition business methods and properties."""

    def test_validate_percentages_method(self, session):
        """Test validate_percentages method."""
        # Valid case
        payment_cond = PaymentCondition(
            payment_condition_number="VALID",
            name="Valid",
            percentage_advance=Decimal("25.00"),
            percentage_on_delivery=Decimal("25.00"),
            percentage_after_delivery=Decimal("50.00"),
        )
        # Should not raise
        payment_cond.validate_percentages()

        # Invalid case
        payment_cond_invalid = PaymentCondition(
            payment_condition_number="INVALID",
            name="Invalid",
            percentage_advance=Decimal("25.00"),
            percentage_on_delivery=Decimal("25.00"),
            percentage_after_delivery=Decimal("60.00"),  # Sums to 110
        )
        with pytest.raises(ValueError, match="Payment percentages must sum to 100"):
            payment_cond_invalid.validate_percentages()

    def test_summary_property(self, session, sample_payment_type):
        """Test summary property generates human-readable summary."""
        # Test 50-50 split
        payment_cond = PaymentCondition(
            payment_condition_number="50-50",
            name="50-50",
            payment_type_id=sample_payment_type.id,
            percentage_advance=Decimal("50.00"),
            percentage_on_delivery=Decimal("50.00"),
            percentage_after_delivery=Decimal("0.00"),
        )
        session.add(payment_cond)
        session.commit()
        session.refresh(payment_cond)

        summary = payment_cond.summary
        assert "50.00% advance" in summary
        assert "50.00% on delivery" in summary

        # Test Net 30
        payment_cond2 = PaymentCondition(
            payment_condition_number="NET30",
            name="Net 30",
            payment_type_id=sample_payment_type.id,
            percentage_advance=Decimal("0.00"),
            percentage_on_delivery=Decimal("0.00"),
            percentage_after_delivery=Decimal("100.00"),
            days_to_pay=30,
            days_after_delivery=30,
        )
        session.add(payment_cond2)
        session.commit()
        session.refresh(payment_cond2)

        summary2 = payment_cond2.summary
        assert "100.00%" in summary2
        assert "30 days after delivery" in summary2


class TestPaymentConditionRepr:
    """Tests for PaymentCondition __repr__ method."""

    def test_payment_condition_repr(self, session, sample_payment_type):
        """Test PaymentCondition string representation."""
        # Arrange
        payment_cond = PaymentCondition(
            payment_condition_number="REPR",
            name="Test Payment Condition",
            payment_type_id=sample_payment_type.id,
            percentage_advance=Decimal("0.00"),
            percentage_on_delivery=Decimal("0.00"),
            percentage_after_delivery=Decimal("100.00"),
        )
        session.add(payment_cond)
        session.commit()
        session.refresh(payment_cond)

        # Act
        repr_str = repr(payment_cond)

        # Assert
        assert "PaymentCondition" in repr_str
        assert "REPR" in repr_str
        assert "Test Payment Condition" in repr_str
