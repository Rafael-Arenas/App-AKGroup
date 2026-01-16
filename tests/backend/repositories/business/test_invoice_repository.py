"""
Tests para InvoiceSIIRepository y InvoiceExportRepository.

Valida funcionalidad CRUD base más métodos específicos de facturas.
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from sqlalchemy.orm import Session

from src.backend.models.business.invoices import InvoiceSII, InvoiceExport
from src.backend.models.business.orders import Order
from src.backend.models.core.staff import Staff
from src.backend.models.lookups import OrderStatus, PaymentStatus


# ===================== FIXTURES =====================


@pytest.fixture
def sample_staff(session: Session) -> Staff:
    """Create a sample Staff for invoice testing."""
    staff = Staff(
        username="invoice_staff",
        first_name="Invoice",
        last_name="Staff",
        email="invoice.staff@test.com",
        position="Accounting",
        is_active=True,
    )
    session.add(staff)
    session.commit()
    session.refresh(staff)
    return staff


@pytest.fixture
def sample_order_status(session: Session) -> OrderStatus:
    """Create a sample OrderStatus for testing."""
    status = OrderStatus(
        code="completed_inv",
        name="Completed",
        description="Order completed",
    )
    session.add(status)
    session.commit()
    session.refresh(status)
    return status


@pytest.fixture
def sample_payment_status(session: Session) -> PaymentStatus:
    """Create a sample PaymentStatus for testing."""
    status = PaymentStatus(
        code="pending_inv",
        name="Pending",
        description="Payment pending",
    )
    session.add(status)
    session.commit()
    session.refresh(status)
    return status


@pytest.fixture
def sample_order_for_invoice(
    session: Session,
    sample_company,
    sample_staff,
    sample_currency,
    sample_order_status,
    sample_payment_status,
) -> Order:
    """Create a sample Order for invoice testing."""
    order = Order(
        order_number="O-INV-2025-001",
        order_type="sales",
        company_id=sample_company.id,
        staff_id=sample_staff.id,
        currency_id=sample_currency.id,
        status_id=sample_order_status.id,
        payment_status_id=sample_payment_status.id,
        order_date=date.today(),
        subtotal=Decimal("1000.00"),
        tax_percentage=Decimal("19.00"),
        tax_amount=Decimal("190.00"),
        total=Decimal("1190.00"),
    )
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


@pytest.fixture
def sample_invoice_sii(
    session: Session,
    sample_order_for_invoice,
    sample_company,
    sample_staff,
    sample_currency,
    sample_payment_status,
) -> InvoiceSII:
    """Create a sample InvoiceSII for testing."""
    invoice = InvoiceSII(
        invoice_number="F-2025-001",
        invoice_type="33",
        order_id=sample_order_for_invoice.id,
        company_id=sample_company.id,
        staff_id=sample_staff.id,
        currency_id=sample_currency.id,
        payment_status_id=sample_payment_status.id,
        invoice_date=date.today(),
        due_date=date.today() + timedelta(days=30),
        subtotal=Decimal("1000.00"),
        tax_amount=Decimal("190.00"),
        total=Decimal("1190.00"),
        net_amount=Decimal("1000.00"),
    )
    session.add(invoice)
    session.commit()
    session.refresh(invoice)
    return invoice


@pytest.fixture
def sample_invoice_export(
    session: Session,
    sample_order_for_invoice,
    sample_company,
    sample_staff,
    sample_currency,
    sample_payment_status,
    sample_incoterm,
    sample_country,
) -> InvoiceExport:
    """Create a sample InvoiceExport for testing."""
    invoice = InvoiceExport(
        invoice_number="FE-2025-001",
        invoice_type="110",
        order_id=sample_order_for_invoice.id,
        company_id=sample_company.id,
        staff_id=sample_staff.id,
        currency_id=sample_currency.id,
        payment_status_id=sample_payment_status.id,
        incoterm_id=sample_incoterm.id,
        country_id=sample_country.id,
        invoice_date=date.today(),
        due_date=date.today() + timedelta(days=60),
        exchange_rate=Decimal("900.50"),
        subtotal=Decimal("1000.00"),
        total=Decimal("1000.00"),  # Export invoices usually tax-exempt
        total_clp=Decimal("900500.00"),
    )
    session.add(invoice)
    session.commit()
    session.refresh(invoice)
    return invoice


# ===================== INVOICE SII REPOSITORY TESTS =====================


class TestInvoiceSIIRepositoryGetByInvoiceNumber:
    """Tests para get_by_invoice_number()."""

    def test_get_by_invoice_number_existing(
        self, invoice_sii_repository, sample_invoice_sii, session
    ):
        """Test que obtiene factura existente por número."""
        # Act
        result = invoice_sii_repository.get_by_invoice_number(
            sample_invoice_sii.invoice_number
        )

        # Assert
        assert result is not None
        assert result.id == sample_invoice_sii.id
        assert result.invoice_number == sample_invoice_sii.invoice_number

    def test_get_by_invoice_number_not_found(self, invoice_sii_repository):
        """Test que retorna None cuando invoice_number no existe."""
        # Act
        result = invoice_sii_repository.get_by_invoice_number("F-NONEXISTENT")

        # Assert
        assert result is None


class TestInvoiceSIIRepositoryGetByCompany:
    """Tests para get_by_company()."""

    def test_get_by_company_existing(
        self,
        invoice_sii_repository,
        sample_invoice_sii,
        sample_company,
        sample_order_for_invoice,
        sample_staff,
        sample_currency,
        sample_payment_status,
        session,
    ):
        """Test que obtiene facturas de una company."""
        # Arrange - crear más facturas
        for i in range(3):
            # Create unique order for each invoice
            order = Order(
                order_number=f"O-INV-MULTI-{i+100:03d}",
                order_type="sales",
                company_id=sample_company.id,
                staff_id=sample_staff.id,
                currency_id=sample_currency.id,
                status_id=sample_order_for_invoice.status_id,
                payment_status_id=sample_payment_status.id,
                order_date=date.today(),
                subtotal=Decimal("1000.00"),
                tax_amount=Decimal("190.00"),
                total=Decimal("1190.00"),
            )
            session.add(order)
            session.flush()
            
            invoice = InvoiceSII(
                invoice_number=f"F-2025-{i+100:03d}",
                invoice_type="33",
                order_id=order.id,
                company_id=sample_company.id,
                staff_id=sample_staff.id,
                currency_id=sample_currency.id,
                payment_status_id=sample_payment_status.id,
                invoice_date=date.today(),
                subtotal=Decimal("1000.00"),
                tax_amount=Decimal("190.00"),
                total=Decimal("1190.00"),
                net_amount=Decimal("1000.00"),
            )
            session.add(invoice)
        session.commit()

        # Act
        results = invoice_sii_repository.get_by_company(sample_company.id)

        # Assert
        assert len(results) >= 4  # sample + 3 created
        assert all(i.company_id == sample_company.id for i in results)

    def test_get_by_company_empty(self, invoice_sii_repository):
        """Test que retorna lista vacía si no hay facturas."""
        # Act
        results = invoice_sii_repository.get_by_company(99999)

        # Assert
        assert results == []


class TestInvoiceSIIRepositoryGetByPaymentStatus:
    """Tests para get_by_payment_status()."""

    def test_get_by_payment_status_existing(
        self,
        invoice_sii_repository,
        sample_invoice_sii,
        sample_payment_status,
        session,
    ):
        """Test que filtra facturas por payment status."""
        # Act
        results = invoice_sii_repository.get_by_payment_status(sample_payment_status.id)

        # Assert
        assert len(results) >= 1
        assert all(i.payment_status_id == sample_payment_status.id for i in results)

    def test_get_by_payment_status_empty(self, invoice_sii_repository):
        """Test que retorna lista vacía si no hay facturas con ese status."""
        # Act
        results = invoice_sii_repository.get_by_payment_status(99999)

        # Assert
        assert results == []


# ===================== INVOICE EXPORT REPOSITORY TESTS =====================


class TestInvoiceExportRepositoryGetByInvoiceNumber:
    """Tests para get_by_invoice_number()."""

    def test_get_by_invoice_number_existing(
        self, invoice_export_repository, sample_invoice_export, session
    ):
        """Test que obtiene factura de exportación existente por número."""
        # Act
        result = invoice_export_repository.get_by_invoice_number(
            sample_invoice_export.invoice_number
        )

        # Assert
        assert result is not None
        assert result.id == sample_invoice_export.id
        assert result.invoice_number == sample_invoice_export.invoice_number

    def test_get_by_invoice_number_not_found(self, invoice_export_repository):
        """Test que retorna None cuando invoice_number no existe."""
        # Act
        result = invoice_export_repository.get_by_invoice_number("FE-NONEXISTENT")

        # Assert
        assert result is None


class TestInvoiceExportRepositoryGetByCompany:
    """Tests para get_by_company()."""

    def test_get_by_company_existing(
        self,
        invoice_export_repository,
        sample_invoice_export,
        sample_company,
        session,
    ):
        """Test que obtiene facturas de exportación de una company."""
        # Act
        results = invoice_export_repository.get_by_company(sample_company.id)

        # Assert
        assert len(results) >= 1
        assert all(i.company_id == sample_company.id for i in results)

    def test_get_by_company_empty(self, invoice_export_repository):
        """Test que retorna lista vacía si no hay facturas."""
        # Act
        results = invoice_export_repository.get_by_company(99999)

        # Assert
        assert results == []


class TestInvoiceExportRepositoryGetByCountry:
    """Tests para get_by_country()."""

    def test_get_by_country_existing(
        self,
        invoice_export_repository,
        sample_invoice_export,
        sample_country,
        session,
    ):
        """Test que filtra facturas por país de destino."""
        # Act
        results = invoice_export_repository.get_by_country(sample_country.id)

        # Assert
        assert len(results) >= 1
        assert all(i.country_id == sample_country.id for i in results)

    def test_get_by_country_empty(self, invoice_export_repository):
        """Test que retorna lista vacía si no hay facturas para ese país."""
        # Act
        results = invoice_export_repository.get_by_country(99999)

        # Assert
        assert results == []
