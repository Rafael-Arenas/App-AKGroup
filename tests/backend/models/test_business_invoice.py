"""
Tests for InvoiceSII and InvoiceExport models from business.invoices.

This module contains comprehensive tests for invoice business models,
including CRUD operations, validators, relationships, financial calculations, and edge cases.

Test Coverage:
    InvoiceSII (Chilean domestic invoices):
        - Basic CRUD operations
        - Field validation (invoice_number, invoice_type)
        - Relationships (order, company, plant, staff, payment_status, currency)
        - Business properties (is_overdue, days_overdue, is_paid)
        - CheckConstraints (positive amounts, invoice_type validation)
        - SII integration fields
        - Mixins (Timestamp, Audit, Active)

    InvoiceExport (export invoices):
        - Basic CRUD operations
        - Field validation (invoice_number, invoice_type, exchange_rate)
        - Export-specific fields (country, ports, customs documentation)
        - Business methods (calculate_clp_total)
        - Business properties (is_overdue, days_overdue, is_paid)
        - CheckConstraints (positive amounts, exchange rate)
        - Relationships
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from src.backend.models.business.invoices import InvoiceSII, InvoiceExport
from src.backend.models.core.companies import Company
from src.backend.models.lookups.lookups import Currency, Incoterm


# ============= INVOICE SII MODEL TESTS =============


class TestInvoiceSIICreation:
    """Tests for InvoiceSII model instantiation and creation."""

    def test_create_invoice_sii_with_all_fields(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """
        Test creating an InvoiceSII with all fields populated.

        This test verifies that an InvoiceSII can be created with complete data
        and all fields are properly stored in the database.
        """
        # Create required dependencies
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups.lookups import OrderStatus, PaymentStatus
        from src.backend.models.business.orders import Order

        staff = Staff(
            username="testuser_inv1",
            email="inv1@test.com",
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
            order_number="O-INV-001",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order)
        session.commit()

        # Arrange & Act
        invoice = InvoiceSII(
            invoice_number="12345678",
            revision="A",
            invoice_type="33",
            order_id=order.id,
            company_id=sample_company.id,
            staff_id=staff.id,
            payment_status_id=payment_status.id,
            invoice_date=date(2025, 1, 15),
            due_date=date(2025, 2, 15),
            currency_id=sample_currency.id,
            exchange_rate=Decimal("1.00"),
            subtotal=Decimal("1000.00"),
            tax_amount=Decimal("190.00"),
            total=Decimal("1190.00"),
            net_amount=Decimal("1000.00"),
            exempt_amount=Decimal("0.00"),
            payment_terms="Net 30 days",
            sii_status="accepted",
            sii_track_id="TRACK123",
            sii_xml="<XML>...</XML>",
            notes="Invoice notes",
            is_active=True,
        )
        session.add(invoice)
        session.commit()
        session.refresh(invoice)

        # Assert
        assert invoice.id is not None
        assert invoice.invoice_number == "12345678"
        assert invoice.revision == "A"
        assert invoice.invoice_type == "33"
        assert invoice.order_id == order.id
        assert invoice.company_id == sample_company.id
        assert invoice.staff_id == staff.id
        assert invoice.payment_status_id == payment_status.id
        assert invoice.invoice_date == date(2025, 1, 15)
        assert invoice.due_date == date(2025, 2, 15)
        assert invoice.currency_id == sample_currency.id
        assert invoice.subtotal == Decimal("1000.00")
        assert invoice.tax_amount == Decimal("190.00")
        assert invoice.total == Decimal("1190.00")
        assert invoice.sii_status == "accepted"
        assert invoice.is_active is True

    def test_create_invoice_sii_with_minimal_fields(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test creating InvoiceSII with only required fields."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups.lookups import OrderStatus, PaymentStatus
        from src.backend.models.business.orders import Order

        staff = Staff(
            username="testuser_inv2",
            email="inv2@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="confirmed", name="Confirmed", description="Confirmed")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        order = Order(
            order_number="O-INV-002",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order)
        session.commit()

        # Arrange & Act
        invoice = InvoiceSII(
            invoice_number="12345679",
            order_id=order.id,
            company_id=sample_company.id,
            staff_id=staff.id,
            payment_status_id=payment_status.id,
            invoice_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(invoice)
        session.commit()
        session.refresh(invoice)

        # Assert
        assert invoice.id is not None
        assert invoice.invoice_number == "12345679"
        assert invoice.revision == "A"  # Default
        assert invoice.invoice_type == "33"  # Default
        assert invoice.subtotal == Decimal("0.00")
        assert invoice.tax_amount == Decimal("0.00")
        assert invoice.total == Decimal("0.00")
        assert invoice.net_amount == Decimal("0.00")
        assert invoice.exempt_amount == Decimal("0.00")


class TestInvoiceSIIValidation:
    """Tests for InvoiceSII field validators and constraints."""

    def test_invoice_number_validator_strips(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test that invoice_number is stripped."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups.lookups import OrderStatus, PaymentStatus
        from src.backend.models.business.orders import Order

        staff = Staff(
            username="testuser_inv3",
            email="inv3@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="confirmed", name="Confirmed", description="Confirmed")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        order = Order(
            order_number="O-INV-003",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order)
        session.commit()

        # Arrange & Act
        invoice = InvoiceSII(
            invoice_number="  12345680  ",  # With whitespace
            order_id=order.id,
            company_id=sample_company.id,
            staff_id=staff.id,
            payment_status_id=payment_status.id,
            invoice_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(invoice)
        session.commit()
        session.refresh(invoice)

        # Assert
        assert invoice.invoice_number == "12345680"  # Trimmed

    def test_invoice_number_cannot_be_empty(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test that invoice_number cannot be empty."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups.lookups import OrderStatus, PaymentStatus
        from src.backend.models.business.orders import Order

        staff = Staff(
            username="testuser_inv4",
            email="inv4@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="confirmed", name="Confirmed", description="Confirmed")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        order = Order(
            order_number="O-INV-004",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order)
        session.commit()

        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Invoice number cannot be empty"):
            invoice = InvoiceSII(
                invoice_number="   ",  # Empty after strip
                order_id=order.id,
                company_id=sample_company.id,
                staff_id=staff.id,
                payment_status_id=payment_status.id,
                invoice_date=date.today(),
                currency_id=sample_currency.id,
            )

    def test_invoice_type_validation_valid_types(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test that valid invoice_type values are accepted."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups.lookups import OrderStatus, PaymentStatus
        from src.backend.models.business.orders import Order

        staff = Staff(
            username="testuser_inv5",
            email="inv5@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="confirmed", name="Confirmed", description="Confirmed")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        # Test all valid types
        valid_types = ["33", "34", "56", "61", "39", "41"]

        for idx, inv_type in enumerate(valid_types):
            order = Order(
                order_number=f"O-INV-TYPE-{idx}",
                company_id=sample_company.id,
                staff_id=staff.id,
                status_id=order_status.id,
                payment_status_id=payment_status.id,
                order_date=date.today(),
                currency_id=sample_currency.id,
            )
            session.add(order)
            session.commit()

            invoice = InvoiceSII(
                invoice_number=f"INV-TYPE-{idx}",
                invoice_type=inv_type,
                order_id=order.id,
                company_id=sample_company.id,
                staff_id=staff.id,
                payment_status_id=payment_status.id,
                invoice_date=date.today(),
                currency_id=sample_currency.id,
            )
            session.add(invoice)
            session.commit()
            session.refresh(invoice)
            assert invoice.invoice_type == inv_type
            session.rollback()  # Rollback for next iteration

    def test_invoice_type_validation_invalid(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test that invalid invoice_type raises ValueError."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups.lookups import OrderStatus, PaymentStatus
        from src.backend.models.business.orders import Order

        staff = Staff(
            username="testuser_inv6",
            email="inv6@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="confirmed", name="Confirmed", description="Confirmed")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        order = Order(
            order_number="O-INV-006",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order)
        session.commit()

        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Invoice type must be one of"):
            invoice = InvoiceSII(
                invoice_number="INV-INVALID",
                invoice_type="99",  # Invalid
                order_id=order.id,
                company_id=sample_company.id,
                staff_id=staff.id,
                payment_status_id=payment_status.id,
                invoice_date=date.today(),
                currency_id=sample_currency.id,
            )


class TestInvoiceSIIConstraints:
    """Tests for InvoiceSII database constraints."""

    def test_invoice_number_unique_constraint(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test that invoice_number must be unique."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups.lookups import OrderStatus, PaymentStatus
        from src.backend.models.business.orders import Order

        staff = Staff(
            username="testuser_inv7",
            email="inv7@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="confirmed", name="Confirmed", description="Confirmed")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        # Create two orders
        order1 = Order(
            order_number="O-INV-007-A",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order1)
        session.commit()

        order2 = Order(
            order_number="O-INV-007-B",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order2)
        session.commit()

        # Create first invoice
        invoice1 = InvoiceSII(
            invoice_number="INV-DUP",
            order_id=order1.id,
            company_id=sample_company.id,
            staff_id=staff.id,
            payment_status_id=payment_status.id,
            invoice_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(invoice1)
        session.commit()

        # Try to create duplicate
        invoice2 = InvoiceSII(
            invoice_number="INV-DUP",
            order_id=order2.id,
            company_id=sample_company.id,
            staff_id=staff.id,
            payment_status_id=payment_status.id,
            invoice_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(invoice2)

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
        from src.backend.models.lookups.lookups import OrderStatus, PaymentStatus
        from src.backend.models.business.orders import Order

        staff = Staff(
            username="testuser_inv8",
            email="inv8@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="confirmed", name="Confirmed", description="Confirmed")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        order = Order(
            order_number="O-INV-008",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order)
        session.commit()

        # Arrange & Act
        invoice = InvoiceSII(
            invoice_number="INV-NEG",
            subtotal=Decimal("-100.00"),  # Negative
            order_id=order.id,
            company_id=sample_company.id,
            staff_id=staff.id,
            payment_status_id=payment_status.id,
            invoice_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(invoice)

        # Assert
        with pytest.raises(IntegrityError):
            session.commit()


class TestInvoiceSIIBusinessProperties:
    """Tests for InvoiceSII business properties."""

    def test_is_overdue_property_false_when_no_due_date(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test is_overdue returns False when no due_date."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups.lookups import OrderStatus, PaymentStatus
        from src.backend.models.business.orders import Order

        staff = Staff(
            username="testuser_inv9",
            email="inv9@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="confirmed", name="Confirmed", description="Confirmed")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        order = Order(
            order_number="O-INV-009",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order)
        session.commit()

        invoice = InvoiceSII(
            invoice_number="INV-009",
            order_id=order.id,
            company_id=sample_company.id,
            staff_id=staff.id,
            payment_status_id=payment_status.id,
            invoice_date=date.today(),
            currency_id=sample_currency.id,
            due_date=None,
        )
        session.add(invoice)
        session.commit()
        session.refresh(invoice)

        # Assert
        assert invoice.is_overdue is False

    def test_is_overdue_property_false_when_paid(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test is_overdue returns False when invoice is paid."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups.lookups import OrderStatus, PaymentStatus
        from src.backend.models.business.orders import Order

        staff = Staff(
            username="testuser_inv10",
            email="inv10@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="confirmed", name="Confirmed", description="Confirmed")
        session.add(order_status)

        payment_status = PaymentStatus(code="paid", name="Paid", description="Paid")
        session.add(payment_status)
        session.commit()

        order = Order(
            order_number="O-INV-010",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order)
        session.commit()

        invoice = InvoiceSII(
            invoice_number="INV-010",
            order_id=order.id,
            company_id=sample_company.id,
            staff_id=staff.id,
            payment_status_id=payment_status.id,
            invoice_date=date.today() - timedelta(days=60),
            due_date=date.today() - timedelta(days=30),
            paid_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(invoice)
        session.commit()
        session.refresh(invoice)

        # Assert
        assert invoice.is_overdue is False

    def test_is_overdue_property_true_when_past_due(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test is_overdue returns True when past due_date and unpaid."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups.lookups import OrderStatus, PaymentStatus
        from src.backend.models.business.orders import Order

        staff = Staff(
            username="testuser_inv11",
            email="inv11@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="confirmed", name="Confirmed", description="Confirmed")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        order = Order(
            order_number="O-INV-011",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order)
        session.commit()

        invoice = InvoiceSII(
            invoice_number="INV-011",
            order_id=order.id,
            company_id=sample_company.id,
            staff_id=staff.id,
            payment_status_id=payment_status.id,
            invoice_date=date.today() - timedelta(days=45),
            due_date=date.today() - timedelta(days=15),
            paid_date=None,
            currency_id=sample_currency.id,
        )
        session.add(invoice)
        session.commit()
        session.refresh(invoice)

        # Assert
        assert invoice.is_overdue is True

    def test_days_overdue_property(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test days_overdue property calculates correctly."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups.lookups import OrderStatus, PaymentStatus
        from src.backend.models.business.orders import Order

        staff = Staff(
            username="testuser_inv12",
            email="inv12@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="confirmed", name="Confirmed", description="Confirmed")
        session.add(order_status)

        payment_status = PaymentStatus(code="overdue", name="Overdue", description="Overdue")
        session.add(payment_status)
        session.commit()

        order = Order(
            order_number="O-INV-012",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order)
        session.commit()

        invoice = InvoiceSII(
            invoice_number="INV-012",
            order_id=order.id,
            company_id=sample_company.id,
            staff_id=staff.id,
            payment_status_id=payment_status.id,
            invoice_date=date.today() - timedelta(days=45),
            due_date=date.today() - timedelta(days=15),
            paid_date=None,
            currency_id=sample_currency.id,
        )
        session.add(invoice)
        session.commit()
        session.refresh(invoice)

        # Assert
        assert invoice.days_overdue == 15

    def test_is_paid_property(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test is_paid property returns True when paid_date is set."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups.lookups import OrderStatus, PaymentStatus
        from src.backend.models.business.orders import Order

        staff = Staff(
            username="testuser_inv13",
            email="inv13@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="confirmed", name="Confirmed", description="Confirmed")
        session.add(order_status)

        payment_status = PaymentStatus(code="paid", name="Paid", description="Paid")
        session.add(payment_status)
        session.commit()

        order = Order(
            order_number="O-INV-013",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order)
        session.commit()

        invoice = InvoiceSII(
            invoice_number="INV-013",
            order_id=order.id,
            company_id=sample_company.id,
            staff_id=staff.id,
            payment_status_id=payment_status.id,
            invoice_date=date.today(),
            paid_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(invoice)
        session.commit()
        session.refresh(invoice)

        # Assert
        assert invoice.is_paid is True


class TestInvoiceSIIRepr:
    """Tests for InvoiceSII __repr__ method."""

    def test_invoice_sii_repr(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
    ):
        """Test InvoiceSII string representation."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups.lookups import OrderStatus, PaymentStatus
        from src.backend.models.business.orders import Order

        staff = Staff(
            username="testuser_inv14",
            email="inv14@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="confirmed", name="Confirmed", description="Confirmed")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        order = Order(
            order_number="O-INV-014",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(order)
        session.commit()

        invoice = InvoiceSII(
            invoice_number="INV-REPR",
            invoice_type="33",
            total=Decimal("1500.00"),
            order_id=order.id,
            company_id=sample_company.id,
            staff_id=staff.id,
            payment_status_id=payment_status.id,
            invoice_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(invoice)
        session.commit()
        session.refresh(invoice)

        # Act
        repr_str = repr(invoice)

        # Assert
        assert "InvoiceSII" in repr_str
        assert "INV-REPR" in repr_str
        assert "33" in repr_str
        assert "1500.00" in repr_str


# ============= INVOICE EXPORT MODEL TESTS =============


class TestInvoiceExportCreation:
    """Tests for InvoiceExport model instantiation and creation."""

    def test_create_invoice_export_with_all_fields(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
        sample_incoterm: Incoterm,
        sample_country: "Country",
    ):
        """
        Test creating an InvoiceExport with all fields populated.

        This test verifies that an InvoiceExport can be created with complete data
        and all fields are properly stored in the database.
        """
        # Create required dependencies
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups.lookups import OrderStatus, PaymentStatus
        from src.backend.models.business.orders import Order

        staff = Staff(
            username="testuser_exp1",
            email="exp1@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="confirmed", name="Confirmed", description="Confirmed")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        # Create export order
        order = Order(
            order_number="O-EXP-001",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
            is_export=True,
        )
        session.add(order)
        session.commit()

        # Arrange & Act
        invoice = InvoiceExport(
            invoice_number="EXP-12345",
            revision="A",
            invoice_type="110",
            order_id=order.id,
            company_id=sample_company.id,
            staff_id=staff.id,
            payment_status_id=payment_status.id,
            invoice_date=date(2025, 1, 15),
            due_date=date(2025, 2, 15),
            shipping_date=date(2025, 1, 20),
            currency_id=sample_currency.id,
            exchange_rate=Decimal("900.00"),
            incoterm_id=sample_incoterm.id,
            country_id=sample_country.id,
            port_of_loading="Valparaiso",
            port_of_discharge="Miami",
            subtotal=Decimal("10000.00"),
            total=Decimal("10000.00"),
            total_clp=Decimal("9000000.00"),
            freight_cost=Decimal("500.00"),
            insurance_cost=Decimal("100.00"),
            payment_terms="L/C 90 days",
            letter_of_credit="LC123456",
            customs_declaration="DIN-987654",
            bill_of_lading="BL-ABC123",
            notes="Export invoice notes",
            is_active=True,
        )
        session.add(invoice)
        session.commit()
        session.refresh(invoice)

        # Assert
        assert invoice.id is not None
        assert invoice.invoice_number == "EXP-12345"
        assert invoice.revision == "A"
        assert invoice.invoice_type == "110"
        assert invoice.order_id == order.id
        assert invoice.exchange_rate == Decimal("900.00")
        assert invoice.incoterm_id == sample_incoterm.id
        assert invoice.country_id == sample_country.id
        assert invoice.port_of_loading == "Valparaiso"
        assert invoice.port_of_discharge == "Miami"
        assert invoice.subtotal == Decimal("10000.00")
        assert invoice.total == Decimal("10000.00")
        assert invoice.total_clp == Decimal("9000000.00")
        assert invoice.freight_cost == Decimal("500.00")
        assert invoice.insurance_cost == Decimal("100.00")
        assert invoice.letter_of_credit == "LC123456"
        assert invoice.customs_declaration == "DIN-987654"
        assert invoice.bill_of_lading == "BL-ABC123"
        assert invoice.is_active is True

    def test_create_invoice_export_with_minimal_fields(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
        sample_incoterm: Incoterm,
        sample_country: "Country",
    ):
        """Test creating InvoiceExport with only required fields."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups.lookups import OrderStatus, PaymentStatus
        from src.backend.models.business.orders import Order

        staff = Staff(
            username="testuser_exp2",
            email="exp2@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="confirmed", name="Confirmed", description="Confirmed")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        order = Order(
            order_number="O-EXP-002",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
            is_export=True,
        )
        session.add(order)
        session.commit()

        # Arrange & Act
        invoice = InvoiceExport(
            invoice_number="EXP-12346",
            order_id=order.id,
            company_id=sample_company.id,
            staff_id=staff.id,
            payment_status_id=payment_status.id,
            invoice_date=date.today(),
            currency_id=sample_currency.id,
            exchange_rate=Decimal("900.00"),
            incoterm_id=sample_incoterm.id,
            country_id=sample_country.id,
        )
        session.add(invoice)
        session.commit()
        session.refresh(invoice)

        # Assert
        assert invoice.id is not None
        assert invoice.invoice_number == "EXP-12346"
        assert invoice.revision == "A"  # Default
        assert invoice.invoice_type == "110"  # Default
        assert invoice.subtotal == Decimal("0.00")
        assert invoice.total == Decimal("0.00")
        assert invoice.total_clp == Decimal("0.00")
        assert invoice.freight_cost == Decimal("0.00")
        assert invoice.insurance_cost == Decimal("0.00")


class TestInvoiceExportValidation:
    """Tests for InvoiceExport field validators and constraints."""

    def test_invoice_type_validation_valid_export_types(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
        sample_incoterm: Incoterm,
        sample_country: "Country",
    ):
        """Test that valid export invoice_type values are accepted."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups.lookups import OrderStatus, PaymentStatus
        from src.backend.models.business.orders import Order

        staff = Staff(
            username="testuser_exp3",
            email="exp3@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="confirmed", name="Confirmed", description="Confirmed")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        # Test all valid export types
        valid_types = ["110", "111", "112"]

        for idx, inv_type in enumerate(valid_types):
            order = Order(
                order_number=f"O-EXP-TYPE-{idx}",
                company_id=sample_company.id,
                staff_id=staff.id,
                status_id=order_status.id,
                payment_status_id=payment_status.id,
                order_date=date.today(),
                currency_id=sample_currency.id,
                is_export=True,
            )
            session.add(order)
            session.commit()

            invoice = InvoiceExport(
                invoice_number=f"EXP-TYPE-{idx}",
                invoice_type=inv_type,
                order_id=order.id,
                company_id=sample_company.id,
                staff_id=staff.id,
                payment_status_id=payment_status.id,
                invoice_date=date.today(),
                currency_id=sample_currency.id,
                exchange_rate=Decimal("900.00"),
                incoterm_id=sample_incoterm.id,
                country_id=sample_country.id,
            )
            session.add(invoice)
            session.commit()
            session.refresh(invoice)
            assert invoice.invoice_type == inv_type
            session.rollback()

    def test_invoice_type_validation_invalid_export(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
        sample_incoterm: Incoterm,
        sample_country: "Country",
    ):
        """Test that invalid export invoice_type raises ValueError."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups.lookups import OrderStatus, PaymentStatus
        from src.backend.models.business.orders import Order

        staff = Staff(
            username="testuser_exp4",
            email="exp4@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="confirmed", name="Confirmed", description="Confirmed")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        order = Order(
            order_number="O-EXP-004",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
            is_export=True,
        )
        session.add(order)
        session.commit()

        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Export invoice type must be one of"):
            invoice = InvoiceExport(
                invoice_number="EXP-INVALID",
                invoice_type="33",  # Domestic type, not export
                order_id=order.id,
                company_id=sample_company.id,
                staff_id=staff.id,
                payment_status_id=payment_status.id,
                invoice_date=date.today(),
                currency_id=sample_currency.id,
                exchange_rate=Decimal("900.00"),
                incoterm_id=sample_incoterm.id,
                country_id=sample_country.id,
            )

    def test_exchange_rate_validation_positive(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
        sample_incoterm: Incoterm,
        sample_country: "Country",
    ):
        """Test that positive exchange_rate is valid."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups.lookups import OrderStatus, PaymentStatus
        from src.backend.models.business.orders import Order

        staff = Staff(
            username="testuser_exp5",
            email="exp5@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="confirmed", name="Confirmed", description="Confirmed")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        order = Order(
            order_number="O-EXP-005",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
            is_export=True,
        )
        session.add(order)
        session.commit()

        # Arrange & Act
        invoice = InvoiceExport(
            invoice_number="EXP-POS",
            order_id=order.id,
            company_id=sample_company.id,
            staff_id=staff.id,
            payment_status_id=payment_status.id,
            invoice_date=date.today(),
            currency_id=sample_currency.id,
            exchange_rate=Decimal("950.50"),
            incoterm_id=sample_incoterm.id,
            country_id=sample_country.id,
        )
        session.add(invoice)
        session.commit()
        session.refresh(invoice)

        # Assert
        assert invoice.exchange_rate == Decimal("950.50")

    def test_exchange_rate_validation_zero_or_negative(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
        sample_incoterm: Incoterm,
        sample_country: "Country",
    ):
        """Test that zero or negative exchange_rate raises ValueError."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups.lookups import OrderStatus, PaymentStatus
        from src.backend.models.business.orders import Order

        staff = Staff(
            username="testuser_exp6",
            email="exp6@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="confirmed", name="Confirmed", description="Confirmed")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        order = Order(
            order_number="O-EXP-006",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
            is_export=True,
        )
        session.add(order)
        session.commit()

        # Test zero
        with pytest.raises(ValueError, match="Exchange rate must be positive"):
            invoice = InvoiceExport(
                invoice_number="EXP-ZERO",
                order_id=order.id,
                company_id=sample_company.id,
                staff_id=staff.id,
                payment_status_id=payment_status.id,
                invoice_date=date.today(),
                currency_id=sample_currency.id,
                exchange_rate=Decimal("0.00"),
                incoterm_id=sample_incoterm.id,
                country_id=sample_country.id,
            )

        # Test negative
        with pytest.raises(ValueError, match="Exchange rate must be positive"):
            invoice = InvoiceExport(
                invoice_number="EXP-NEG",
                order_id=order.id,
                company_id=sample_company.id,
                staff_id=staff.id,
                payment_status_id=payment_status.id,
                invoice_date=date.today(),
                currency_id=sample_currency.id,
                exchange_rate=Decimal("-100.00"),
                incoterm_id=sample_incoterm.id,
                country_id=sample_country.id,
            )


class TestInvoiceExportBusinessMethods:
    """Tests for InvoiceExport business methods."""

    def test_calculate_clp_total(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
        sample_incoterm: Incoterm,
        sample_country: "Country",
    ):
        """Test calculate_clp_total method calculates correctly."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups.lookups import OrderStatus, PaymentStatus
        from src.backend.models.business.orders import Order

        staff = Staff(
            username="testuser_exp7",
            email="exp7@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="confirmed", name="Confirmed", description="Confirmed")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        order = Order(
            order_number="O-EXP-007",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
            is_export=True,
        )
        session.add(order)
        session.commit()

        # Arrange
        invoice = InvoiceExport(
            invoice_number="EXP-CALC",
            order_id=order.id,
            company_id=sample_company.id,
            staff_id=staff.id,
            payment_status_id=payment_status.id,
            invoice_date=date.today(),
            currency_id=sample_currency.id,
            exchange_rate=Decimal("900.00"),
            total=Decimal("10000.00"),
            incoterm_id=sample_incoterm.id,
            country_id=sample_country.id,
        )

        # Act
        invoice.calculate_clp_total()

        # Assert
        # 10000 * 900 = 9,000,000.00
        assert invoice.total_clp == Decimal("9000000.00")


class TestInvoiceExportRepr:
    """Tests for InvoiceExport __repr__ method."""

    def test_invoice_export_repr(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
        sample_incoterm: Incoterm,
        sample_country: "Country",
    ):
        """Test InvoiceExport string representation."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups.lookups import OrderStatus, PaymentStatus
        from src.backend.models.business.orders import Order

        staff = Staff(
            username="testuser_exp8",
            email="exp8@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)

        order_status = OrderStatus(code="confirmed", name="Confirmed", description="Confirmed")
        session.add(order_status)

        payment_status = PaymentStatus(code="unpaid", name="Unpaid", description="Unpaid")
        session.add(payment_status)
        session.commit()

        order = Order(
            order_number="O-EXP-008",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=order_status.id,
            payment_status_id=payment_status.id,
            order_date=date.today(),
            currency_id=sample_currency.id,
            is_export=True,
        )
        session.add(order)
        session.commit()

        invoice = InvoiceExport(
            invoice_number="EXP-REPR",
            total=Decimal("15000.00"),
            total_clp=Decimal("13500000.00"),
            order_id=order.id,
            company_id=sample_company.id,
            staff_id=staff.id,
            payment_status_id=payment_status.id,
            invoice_date=date.today(),
            currency_id=sample_currency.id,
            exchange_rate=Decimal("900.00"),
            incoterm_id=sample_incoterm.id,
            country_id=sample_country.id,
        )
        session.add(invoice)
        session.commit()
        session.refresh(invoice)

        # Act
        repr_str = repr(invoice)

        # Assert
        assert "InvoiceExport" in repr_str
        assert "EXP-REPR" in repr_str
        assert "15000.00" in repr_str
        assert "13500000.00" in repr_str
