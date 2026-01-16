"""
Repositories for Invoice models.

Handles data access for InvoiceSII and InvoiceExport.
"""

from collections.abc import Sequence
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.backend.models.business.invoices import InvoiceSII, InvoiceExport
from src.backend.repositories.base import BaseRepository
from src.backend.utils.logger import logger


class InvoiceSIIRepository(BaseRepository[InvoiceSII]):
    """Repository for Chilean SII domestic invoices."""

    def __init__(self, session: Session):
        super().__init__(session, InvoiceSII)

    def get_by_invoice_number(self, invoice_number: str) -> InvoiceSII | None:
        """Get invoice by unique invoice number."""
        logger.debug(f"Searching SII invoice by number: {invoice_number}")
        stmt = select(InvoiceSII).filter(InvoiceSII.invoice_number == invoice_number)
        invoice = self.session.execute(stmt).scalar_one_or_none()
        return invoice

    def get_by_company(self, company_id: int, skip: int = 0, limit: int = 100) -> Sequence[InvoiceSII]:
        """Get invoices by company."""
        stmt = (
            select(InvoiceSII)
            .filter(InvoiceSII.company_id == company_id)
            .order_by(InvoiceSII.invoice_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return self.session.execute(stmt).scalars().all()

    def get_by_payment_status(self, payment_status_id: int, skip: int = 0, limit: int = 100) -> Sequence[InvoiceSII]:
        """Get invoices by payment status."""
        stmt = (
            select(InvoiceSII)
            .filter(InvoiceSII.payment_status_id == payment_status_id)
            .order_by(InvoiceSII.invoice_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return self.session.execute(stmt).scalars().all()


class InvoiceExportRepository(BaseRepository[InvoiceExport]):
    """Repository for export invoices."""

    def __init__(self, session: Session):
        super().__init__(session, InvoiceExport)

    def get_by_invoice_number(self, invoice_number: str) -> InvoiceExport | None:
        """Get invoice by unique invoice number."""
        logger.debug(f"Searching export invoice by number: {invoice_number}")
        stmt = select(InvoiceExport).filter(InvoiceExport.invoice_number == invoice_number)
        invoice = self.session.execute(stmt).scalar_one_or_none()
        return invoice

    def get_by_company(self, company_id: int, skip: int = 0, limit: int = 100) -> Sequence[InvoiceExport]:
        """Get invoices by company."""
        stmt = (
            select(InvoiceExport)
            .filter(InvoiceExport.company_id == company_id)
            .order_by(InvoiceExport.invoice_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return self.session.execute(stmt).scalars().all()

    def get_by_country(self, country_id: int, skip: int = 0, limit: int = 100) -> Sequence[InvoiceExport]:
        """Get export invoices by destination country."""
        stmt = (
            select(InvoiceExport)
            .filter(InvoiceExport.country_id == country_id)
            .order_by(InvoiceExport.invoice_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return self.session.execute(stmt).scalars().all()
