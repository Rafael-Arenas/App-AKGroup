"""
Repositories for Invoice models.

Handles data access for InvoiceSII and InvoiceExport.
"""

from typing import Optional, List
from datetime import date
from sqlalchemy.orm import Session

from src.backend.models.business.invoices import InvoiceSII, InvoiceExport
from src.backend.repositories.base import BaseRepository
from src.backend.utils.logger import logger


class InvoiceSIIRepository(BaseRepository[InvoiceSII]):
    """Repository for Chilean SII domestic invoices."""

    def __init__(self, session: Session):
        super().__init__(session, InvoiceSII)

    def get_by_invoice_number(self, invoice_number: str) -> Optional[InvoiceSII]:
        """Get invoice by unique invoice number."""
        logger.debug(f"Searching SII invoice by number: {invoice_number}")
        invoice = (
            self.session.query(InvoiceSII)
            .filter(InvoiceSII.invoice_number == invoice_number)
            .first()
        )
        return invoice

    def get_by_company(self, company_id: int, skip: int = 0, limit: int = 100) -> List[InvoiceSII]:
        """Get invoices by company."""
        return (
            self.session.query(InvoiceSII)
            .filter(InvoiceSII.company_id == company_id)
            .order_by(InvoiceSII.invoice_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_payment_status(self, payment_status_id: int, skip: int = 0, limit: int = 100) -> List[InvoiceSII]:
        """Get invoices by payment status."""
        return (
            self.session.query(InvoiceSII)
            .filter(InvoiceSII.payment_status_id == payment_status_id)
            .order_by(InvoiceSII.invoice_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )


class InvoiceExportRepository(BaseRepository[InvoiceExport]):
    """Repository for export invoices."""

    def __init__(self, session: Session):
        super().__init__(session, InvoiceExport)

    def get_by_invoice_number(self, invoice_number: str) -> Optional[InvoiceExport]:
        """Get invoice by unique invoice number."""
        logger.debug(f"Searching export invoice by number: {invoice_number}")
        invoice = (
            self.session.query(InvoiceExport)
            .filter(InvoiceExport.invoice_number == invoice_number)
            .first()
        )
        return invoice

    def get_by_company(self, company_id: int, skip: int = 0, limit: int = 100) -> List[InvoiceExport]:
        """Get invoices by company."""
        return (
            self.session.query(InvoiceExport)
            .filter(InvoiceExport.company_id == company_id)
            .order_by(InvoiceExport.invoice_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_country(self, country_id: int, skip: int = 0, limit: int = 100) -> List[InvoiceExport]:
        """Get export invoices by destination country."""
        return (
            self.session.query(InvoiceExport)
            .filter(InvoiceExport.country_id == country_id)
            .order_by(InvoiceExport.invoice_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
