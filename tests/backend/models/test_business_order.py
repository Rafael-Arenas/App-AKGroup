"""
Tests for Order model from business.orders.

This module contains comprehensive tests for the Order business model,
including CRUD operations, validators, relationships, financial calculations, and edge cases.

Test Coverage:
    Order:
        - Basic CRUD operations
        - Field validation (order_number, order_type, tax_percentage)
        - Relationships (company, staff, quote, contact, plant, status, payment_status, etc.)
        - Financial calculations (calculate_totals)
        - Business properties (is_overdue, days_until_required, processing_days)
        - Business methods (create_from_quote)
        - CheckConstraints (positive amounts, tax percentage range, order_type validation)
        - Mixins (Timestamp, Audit, Active)
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from src.backend.models.business.orders import Order
from src.backend.models.core.companies import Company
from src.backend.models.lookups import Currency, Incoterm


# ============= ORDER MODEL TESTS =============


class TestOrderCreation:
    """Tests for Order model instantiation and creation."""

    def test_create_order_with_all_fields(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """
        Test creating an Order with all fields populated.

        This test verifies that an Order can be created with complete data
        and all fields are properly stored in the database.
        """
        # Create required dependencies
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups import OrderStatus, PaymentStatus

        staff = Staff(
            username="testuser_order1",
            email="order1@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(
            code="pending",
            name="Pending",
            description="Order pending processing",
        )
        session.add(order_status)

        payment_status = PaymentStatus(
            code="unpaid",
            name="Unpaid",
            description="Payment not received",
        )
        session.add(payment_status)
        session.commit()

        # Arrange & Act
        order = Order(
            order_number="O-2025-001",
            revision="A",
            order_type="sales",
            customer_quote_number="CQ-12345",
            project_number="PRJ-001",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date(2025, 1, 15),
            required_date=date(2025, 2, 15),
            promised_date=date(2025, 2, 10),
            currency_id=sample_currency.id,
            exchange_rate=Decimal("900.00"),
            subtotal=Decimal("1000.00"),
            tax_percentage=Decimal("19.00"),
            tax_amount=Decimal("190.00"),
            shipping_cost=Decimal("50.00"),
            other_costs=Decimal("25.00"),
            total=Decimal("1265.00"),
            payment_terms="Net 30 days",
            is_export=False,
            notes="Customer-visible notes",
            internal_notes="Internal notes only",
            is_active=True,
        )
        session.add(order)
        session.commit()
        session.refresh(order)

        # Assert
        assert order.id is not None
        assert order.order_number == "O-2025-001"
        assert order.revision == "A"
        assert order.order_type == "sales"
        assert order.customer_quote_number == "CQ-12345"
        assert order.project_number == "PRJ-001"
        assert order.company_id == sample_company.id
        assert order.staff_id == staff.id
        assert order.status_id == order_status.id
        assert order.payment_status_id == payment_status.id
        assert order.order_date == date(2025, 1, 15)
        assert order.required_date == date(2025, 2, 15)
        assert order.promised_date == date(2025, 2, 10)
        assert order.currency_id == sample_currency.id
        assert order.exchange_rate == Decimal("900.00")
        assert order.subtotal == Decimal("1000.00")
        assert order.tax_percentage == Decimal("19.00")
        assert order.tax_amount == Decimal("190.00")
        assert order.shipping_cost == Decimal("50.00")
        assert order.other_costs == Decimal("25.00")
        assert order.total == Decimal("1265.00")
        assert order.payment_terms == "Net 30 days"
        assert order.is_export is False
        assert order.is_active is True

    def test_create_order_with_minimal_fields(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test creating Order with only required fields."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups import OrderStatus, PaymentStatus

        staff = Staff(
            username="testuser_order2",
            email="order2@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(
            code="pending",
            name="Pending",
            description="Order pending",
        )
        session.add(order_status)

        payment_status = PaymentStatus(
            code="unpaid",
            name="Unpaid",
            description="Unpaid",
        )
        session.add(payment_status)
        session.commit()

        # Arrange & Act
        order = Order(
            order_number="O-2025-002",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order)
        session.commit()
        session.refresh(order)

        # Assert
        assert order.id is not None
        assert order.order_number == "O-2025-002"
        assert order.revision == "A"  # Default value
        assert order.order_type == "sales"  # Default value
        assert order.subtotal == Decimal("0.00")  # Default value
        assert order.tax_percentage == Decimal("19.00")  # Default value
        assert order.tax_amount == Decimal("0.00")  # Default value
        assert order.shipping_cost == Decimal("0.00")  # Default value
        assert order.other_costs == Decimal("0.00")  # Default value
        assert order.total == Decimal("0.00")  # Default value
        assert order.is_export is False  # Default value
        assert order.is_active is True  # Default from ActiveMixin

    def test_order_default_values(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test that Order default values are properly set."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups import OrderStatus, PaymentStatus

        staff = Staff(
            username="testuser_order3",
            email="order3@test.com",
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
            order_number="O-2025-003",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order)
        session.commit()
        session.refresh(order)

        # Assert defaults
        assert order.revision == "A"
        assert order.order_type == "sales"
        assert order.subtotal == Decimal("0.00")
        assert order.tax_percentage == Decimal("19.00")
        assert order.tax_amount == Decimal("0.00")
        assert order.shipping_cost == Decimal("0.00")
        assert order.other_costs == Decimal("0.00")
        assert order.total == Decimal("0.00")
        assert order.is_export is False
        assert order.is_active is True


class TestOrderValidation:
    """Tests for Order field validators and constraints."""

    def test_order_number_validator_strips_and_uppercases(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test that order_number is stripped and converted to uppercase."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups import OrderStatus, PaymentStatus

        staff = Staff(
            username="testuser_order4",
            email="order4@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="pending", name="Pending", description="Pending")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        # Arrange & Act
        order = Order(
            order_number="  o-2025-004  ",  # lowercase with whitespace
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order)
        session.commit()
        session.refresh(order)

        # Assert
        assert order.order_number == "O-2025-004"  # Uppercase and trimmed

    def test_order_number_cannot_be_empty(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test that order_number cannot be empty."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups import OrderStatus, PaymentStatus

        staff = Staff(
            username="testuser_order5",
            email="order5@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="pending", name="Pending", description="Pending")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Order number cannot be empty"):
            order = Order(
                order_number="   ",  # Empty after strip
                company_id=sample_company.id,
                staff_id=staff.id,
                status_id=order_status.id,
                payment_status_id=payment_status.id,
                order_date=date.today(),
                currency_id=sample_currency.id,
            )

    def test_order_type_validation_sales(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test that order_type 'sales' is valid."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups import OrderStatus, PaymentStatus

        staff = Staff(
            username="testuser_order6",
            email="order6@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="pending", name="Pending", description="Pending")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        # Arrange & Act
        order = Order(
            order_number="O-2025-006",
            order_type="sales",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order)
        session.commit()
        session.refresh(order)

        # Assert
        assert order.order_type == "sales"

    def test_order_type_validation_purchase(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test that order_type 'purchase' is valid."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups import OrderStatus, PaymentStatus

        staff = Staff(
            username="testuser_order7",
            email="order7@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="pending", name="Pending", description="Pending")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        # Arrange & Act
        order = Order(
            order_number="O-2025-007",
            order_type="purchase",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order)
        session.commit()
        session.refresh(order)

        # Assert
        assert order.order_type == "purchase"

    def test_order_type_validation_invalid(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test that invalid order_type raises ValueError."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups import OrderStatus, PaymentStatus

        staff = Staff(
            username="testuser_order8",
            email="order8@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="pending", name="Pending", description="Pending")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Order type must be one of"):
            order = Order(
                order_number="O-2025-008",
                order_type="invalid",
                company_id=sample_company.id,
                staff_id=staff.id,
                status_id=order_status.id,
                payment_status_id=payment_status.id,
                order_date=date.today(),
                currency_id=sample_currency.id,
            )

    def test_tax_percentage_validation_valid_range(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test that tax_percentage within 0-100 range is valid."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups import OrderStatus, PaymentStatus

        staff = Staff(
            username="testuser_order9",
            email="order9@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="pending", name="Pending", description="Pending")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        # Test various valid percentages
        for tax_pct in [Decimal("0.00"), Decimal("10.50"), Decimal("19.00"), Decimal("100.00")]:
            order = Order(
                order_number=f"O-2025-TAX-{tax_pct}",
                tax_percentage=tax_pct,
                company_id=sample_company.id,
                staff_id=staff.id,
                status_id=order_status.id,
                payment_status_id=payment_status.id,
                order_date=date.today(),
                currency_id=sample_currency.id,
            )
            session.add(order)
            session.commit()
            session.refresh(order)
            assert order.tax_percentage == tax_pct
            session.rollback()  # Rollback for next iteration

    def test_tax_percentage_validation_negative(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test that negative tax_percentage raises ValueError."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups import OrderStatus, PaymentStatus

        staff = Staff(
            username="testuser_order10",
            email="order10@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="pending", name="Pending", description="Pending")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Tax percentage must be between 0 and 100"):
            order = Order(
                order_number="O-2025-010",
                tax_percentage=Decimal("-1.00"),
                company_id=sample_company.id,
                staff_id=staff.id,
                status_id=order_status.id,
                payment_status_id=payment_status.id,
                order_date=date.today(),
                currency_id=sample_currency.id,
            )

    def test_tax_percentage_validation_over_100(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test that tax_percentage over 100 raises ValueError."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups import OrderStatus, PaymentStatus

        staff = Staff(
            username="testuser_order11",
            email="order11@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="pending", name="Pending", description="Pending")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Tax percentage must be between 0 and 100"):
            order = Order(
                order_number="O-2025-011",
                tax_percentage=Decimal("101.00"),
                company_id=sample_company.id,
                staff_id=staff.id,
                status_id=order_status.id,
                payment_status_id=payment_status.id,
                order_date=date.today(),
                currency_id=sample_currency.id,
            )


class TestOrderConstraints:
    """Tests for Order database constraints."""

    def test_order_number_unique_constraint(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test that order_number must be unique."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups import OrderStatus, PaymentStatus

        staff = Staff(
            username="testuser_order12",
            email="order12@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="pending", name="Pending", description="Pending")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        # Create first order
        order1 = Order(
            order_number="O-2025-DUP",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order1)
        session.commit()

        # Try to create duplicate
        order2 = Order(
            order_number="O-2025-DUP",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order2)

        # Assert
        with pytest.raises(IntegrityError):
            session.commit()

    def test_check_constraint_subtotal_positive(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test that subtotal must be >= 0."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups import OrderStatus, PaymentStatus

        staff = Staff(
            username="testuser_order13",
            email="order13@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="pending", name="Pending", description="Pending")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        # Arrange & Act
        order = Order(
            order_number="O-2025-013",
            subtotal=Decimal("-100.00"),  # Negative
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order)

        # Assert
        with pytest.raises(IntegrityError):
            session.commit()

    def test_check_constraint_tax_amount_positive(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test that tax_amount must be >= 0."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups import OrderStatus, PaymentStatus

        staff = Staff(
            username="testuser_order14",
            email="order14@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="pending", name="Pending", description="Pending")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        # Arrange & Act
        order = Order(
            order_number="O-2025-014",
            tax_amount=Decimal("-10.00"),  # Negative
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order)

        # Assert
        with pytest.raises(IntegrityError):
            session.commit()

    def test_check_constraint_shipping_cost_positive(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test that shipping_cost must be >= 0."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups import OrderStatus, PaymentStatus

        staff = Staff(
            username="testuser_order15",
            email="order15@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="pending", name="Pending", description="Pending")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        # Arrange & Act
        order = Order(
            order_number="O-2025-015",
            shipping_cost=Decimal("-50.00"),  # Negative
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order)

        # Assert
        with pytest.raises(IntegrityError):
            session.commit()


class TestOrderRelationships:
    """Tests for Order model relationships."""

    def test_order_company_relationship(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test that Order has relationship with Company."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups import OrderStatus, PaymentStatus

        staff = Staff(
            username="testuser_order16",
            email="order16@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="pending", name="Pending", description="Pending")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        # Arrange & Act
        order = Order(
            order_number="O-2025-016",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order)
        session.commit()
        session.refresh(order)

        # Assert
        assert order.company is not None
        assert order.company.id == sample_company.id
        assert order.company.name == sample_company.name

    def test_order_staff_relationship(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test that Order has relationship with Staff."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups import OrderStatus, PaymentStatus

        staff = Staff(
            username="testuser_order17",
            email="order17@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="pending", name="Pending", description="Pending")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        # Arrange & Act
        order = Order(
            order_number="O-2025-017",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order)
        session.commit()
        session.refresh(order)

        # Assert
        assert order.staff is not None
        assert order.staff.id == staff.id
        assert order.staff.username == "testuser_order17"

    def test_order_currency_relationship(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test that Order has relationship with Currency."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups import OrderStatus, PaymentStatus

        staff = Staff(
            username="testuser_order18",
            email="order18@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="pending", name="Pending", description="Pending")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        # Arrange & Act
        order = Order(
            order_number="O-2025-018",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order)
        session.commit()
        session.refresh(order)

        # Assert
        assert order.currency is not None
        assert order.currency.id == sample_currency.id
        assert order.currency.code == sample_currency.code


class TestOrderBusinessMethods:
    """Tests for Order business methods and properties."""

    def test_calculate_totals(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test calculate_totals method calculates tax and total correctly."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups import OrderStatus, PaymentStatus

        staff = Staff(
            username="testuser_order19",
            email="order19@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="pending", name="Pending", description="Pending")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        # Arrange
        order = Order(
            order_number="O-2025-019",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
            subtotal=Decimal("1000.00"),
            tax_percentage=Decimal("19.00"),
            shipping_cost=Decimal("50.00"),
            other_costs=Decimal("25.00"),
        )

        # Act
        order.calculate_totals()

        # Assert
        # Tax: 1000 * 0.19 = 190.00
        # Total: 1000 + 190 + 50 + 25 = 1265.00
        assert order.tax_amount == Decimal("190.00")
        assert order.total == Decimal("1265.00")

    def test_calculate_totals_zero_tax(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test calculate_totals with zero tax percentage."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups import OrderStatus, PaymentStatus

        staff = Staff(
            username="testuser_order20",
            email="order20@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="pending", name="Pending", description="Pending")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        # Arrange
        order = Order(
            order_number="O-2025-020",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
            subtotal=Decimal("1000.00"),
            tax_percentage=Decimal("0.00"),
            shipping_cost=Decimal("50.00"),
            other_costs=Decimal("0.00"),
        )

        # Act
        order.calculate_totals()

        # Assert
        assert order.tax_amount == Decimal("0.00")
        assert order.total == Decimal("1050.00")

    def test_is_overdue_property_false_when_no_promised_date(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test is_overdue returns False when no promised_date."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups import OrderStatus, PaymentStatus

        staff = Staff(
            username="testuser_order21",
            email="order21@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="pending", name="Pending", description="Pending")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        # Arrange
        order = Order(
            order_number="O-2025-021",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
            promised_date=None,
        )
        session.add(order)
        session.commit()
        session.refresh(order)

        # Assert
        assert order.is_overdue is False

    def test_is_overdue_property_false_when_completed(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test is_overdue returns False when order is completed."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups import OrderStatus, PaymentStatus

        staff = Staff(
            username="testuser_order22",
            email="order22@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="completed", name="Completed", description="Completed")
        session.add(order_status)

        payment_status = PaymentStatus(code="paid", name="Paid", description="Paid")
        session.add(payment_status)
        session.commit()

        # Arrange
        order = Order(
            order_number="O-2025-022",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today() - timedelta(days=30),
            currency_id=sample_currency.id,
            promised_date=date.today() - timedelta(days=5),
            completed_date=date.today(),
        )
        session.add(order)
        session.commit()
        session.refresh(order)

        # Assert
        assert order.is_overdue is False

    def test_is_overdue_property_true_when_past_promised_date(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test is_overdue returns True when past promised_date and not completed."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups import OrderStatus, PaymentStatus

        staff = Staff(
            username="testuser_order23",
            email="order23@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="pending", name="Pending", description="Pending")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        # Arrange
        order = Order(
            order_number="O-2025-023",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today() - timedelta(days=30),
            currency_id=sample_currency.id,
            promised_date=date.today() - timedelta(days=5),
            completed_date=None,
        )
        session.add(order)
        session.commit()
        session.refresh(order)

        # Assert
        assert order.is_overdue is True

    def test_days_until_required_property(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test days_until_required property calculates correctly."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups import OrderStatus, PaymentStatus

        staff = Staff(
            username="testuser_order24",
            email="order24@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="pending", name="Pending", description="Pending")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        # Arrange
        order = Order(
            order_number="O-2025-024",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
            required_date=date.today() + timedelta(days=15),
        )
        session.add(order)
        session.commit()
        session.refresh(order)

        # Assert
        assert order.days_until_required == 15

    def test_days_until_required_property_none_when_completed(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test days_until_required returns None when order completed."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups import OrderStatus, PaymentStatus

        staff = Staff(
            username="testuser_order25",
            email="order25@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="completed", name="Completed", description="Completed")
        session.add(order_status)

        payment_status = PaymentStatus(code="paid", name="Paid", description="Paid")
        session.add(payment_status)
        session.commit()

        # Arrange
        order = Order(
            order_number="O-2025-025",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
            required_date=date.today() + timedelta(days=15),
            completed_date=date.today(),
        )
        session.add(order)
        session.commit()
        session.refresh(order)

        # Assert
        assert order.days_until_required is None

    def test_processing_days_property(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test processing_days property calculates correctly."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups import OrderStatus, PaymentStatus

        staff = Staff(
            username="testuser_order26",
            email="order26@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="completed", name="Completed", description="Completed")
        session.add(order_status)

        payment_status = PaymentStatus(code="paid", name="Paid", description="Paid")
        session.add(payment_status)
        session.commit()

        # Arrange
        order_date = date(2025, 1, 1)
        completed_date = date(2025, 1, 16)

        order = Order(
            order_number="O-2025-026",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=order_date,
            currency_id=sample_currency.id,
            completed_date=completed_date,
        )
        session.add(order)
        session.commit()
        session.refresh(order)

        # Assert
        assert order.processing_days == 15

    def test_processing_days_property_none_when_not_completed(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test processing_days returns None when not completed."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups import OrderStatus, PaymentStatus

        staff = Staff(
            username="testuser_order27",
            email="order27@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="pending", name="Pending", description="Pending")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        # Arrange
        order = Order(
            order_number="O-2025-027",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
            completed_date=None,
        )
        session.add(order)
        session.commit()
        session.refresh(order)

        # Assert
        assert order.processing_days is None

    def test_create_from_quote_method(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test create_from_quote copies data from quote to order."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.business.quotes import Quote
        from src.backend.models.lookups import QuoteStatus, OrderStatus, PaymentStatus

        staff = Staff(
            username="testuser_order28",
            email="order28@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        quote_status = QuoteStatus(code="accepted", name="Accepted", description="Accepted")
        session.add(quote_status)

        order_status = OrderStatus(code="pending", name="Pending", description="Pending")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        # Create quote
        quote = Quote(
            quote_number="Q-2025-FOR-ORDER",
            subject="Test Quote",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=quote_status.id,
            quote_date=date.today(),
            currency_id=sample_currency.id,
            exchange_rate=Decimal("900.00"),
            subtotal=Decimal("1000.00"),
            tax_percentage=Decimal("19.00"),
            tax_amount=Decimal("190.00"),
            total=Decimal("1190.00"),
            notes="Quote notes",
        )
        session.add(quote)
        session.commit()
        session.refresh(quote)

        # Create order and populate from quote
        order = Order(
            order_number="O-FROM-QUOTE",
            company_id=sample_company.id,  # Will be overwritten
            staff_id=staff.id,  # Will be overwritten
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,  # Will be overwritten
        )
        order.create_from_quote(quote)
        session.add(order)
        session.commit()
        session.refresh(order)

        # Assert
        assert order.quote_id == quote.id
        assert order.company_id == quote.company_id
        assert order.staff_id == quote.staff_id
        assert order.currency_id == quote.currency_id
        assert order.exchange_rate == quote.exchange_rate
        assert order.subtotal == quote.subtotal
        assert order.tax_percentage == quote.tax_percentage
        assert order.tax_amount == quote.tax_amount
        assert order.total == quote.total
        assert order.notes == quote.notes


class TestOrderRepr:
    """Tests for Order __repr__ method."""

    def test_order_repr(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test Order string representation."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups import OrderStatus, PaymentStatus

        staff = Staff(
            username="testuser_order29",
            email="order29@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="pending", name="Pending", description="Pending")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        # Arrange
        order = Order(
            order_number="O-2025-REPR",
            order_type="sales",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
            total=Decimal("1500.00"),
        )
        session.add(order)
        session.commit()
        session.refresh(order)

        # Act
        repr_str = repr(order)

        # Assert
        assert "Order" in repr_str
        assert "O-2025-REPR" in repr_str
        assert "sales" in repr_str
        assert "1500.00" in repr_str
