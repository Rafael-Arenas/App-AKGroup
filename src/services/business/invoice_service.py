"""
Service layer for Invoice business logic.

Handles InvoiceSII and InvoiceExport operations.
"""

from typing import List
from sqlalchemy.orm import Session

from src.models.business.invoices import InvoiceSII, InvoiceExport
from src.repositories.business.invoice_repository import InvoiceSIIRepository, InvoiceExportRepository
from src.schemas.business.invoice import (
    InvoiceSIICreate, InvoiceSIIUpdate, InvoiceSIIResponse, InvoiceSIIListResponse,
    InvoiceExportCreate, InvoiceExportUpdate, InvoiceExportResponse, InvoiceExportListResponse,
)
from src.services.base import BaseService
from src.exceptions.service import ValidationException
from src.exceptions.repository import NotFoundException
from src.utils.logger import logger


class InvoiceSIIService(BaseService[InvoiceSII, InvoiceSIICreate, InvoiceSIIUpdate, InvoiceSIIResponse]):
    """Service for Chilean SII domestic invoices."""

    def __init__(self, repository: InvoiceSIIRepository, session: Session):
        super().__init__(repository=repository, session=session, model=InvoiceSII, response_schema=InvoiceSIIResponse)
        self.invoice_repo: InvoiceSIIRepository = repository

    def validate_create(self, entity: InvoiceSII) -> None:
        """Validate invoice before creation."""
        logger.debug(f"Validating SII invoice creation: number={entity.invoice_number}")
        existing = self.invoice_repo.get_by_invoice_number(entity.invoice_number)
        if existing:
            raise ValidationException(f"Invoice number already exists: {entity.invoice_number}")
        logger.debug("SII invoice validation passed")

    def validate_update(self, entity: InvoiceSII) -> None:
        """Validate invoice before update."""
        logger.debug(f"Validating SII invoice update: id={entity.id}")
        existing = self.invoice_repo.get_by_invoice_number(entity.invoice_number)
        if existing and existing.id != entity.id:
            raise ValidationException(f"Invoice number already exists: {entity.invoice_number}")
        logger.debug("SII invoice validation passed")

    def get_by_invoice_number(self, invoice_number: str) -> InvoiceSIIResponse:
        """Get invoice by number."""
        logger.info(f"Getting SII invoice by number: {invoice_number}")
        invoice = self.invoice_repo.get_by_invoice_number(invoice_number)
        if not invoice:
            raise NotFoundException(f"Invoice not found: {invoice_number}")
        return self.response_schema.model_validate(invoice)

    def get_by_company(self, company_id: int, skip: int = 0, limit: int = 100) -> List[InvoiceSIIListResponse]:
        """Get invoices by company."""
        logger.info(f"Getting SII invoices for company_id={company_id}")
        invoices = self.invoice_repo.get_by_company(company_id, skip, limit)
        return [InvoiceSIIListResponse.model_validate(i) for i in invoices]


class InvoiceExportService(BaseService[InvoiceExport, InvoiceExportCreate, InvoiceExportUpdate, InvoiceExportResponse]):
    """Service for export invoices."""

    def __init__(self, repository: InvoiceExportRepository, session: Session):
        super().__init__(repository=repository, session=session, model=InvoiceExport, response_schema=InvoiceExportResponse)
        self.invoice_repo: InvoiceExportRepository = repository

    def validate_create(self, entity: InvoiceExport) -> None:
        """Validate invoice before creation."""
        logger.debug(f"Validating export invoice creation: number={entity.invoice_number}")
        existing = self.invoice_repo.get_by_invoice_number(entity.invoice_number)
        if existing:
            raise ValidationException(f"Invoice number already exists: {entity.invoice_number}")
        entity.calculate_clp_total()
        logger.debug("Export invoice validation passed")

    def validate_update(self, entity: InvoiceExport) -> None:
        """Validate invoice before update."""
        logger.debug(f"Validating export invoice update: id={entity.id}")
        existing = self.invoice_repo.get_by_invoice_number(entity.invoice_number)
        if existing and existing.id != entity.id:
            raise ValidationException(f"Invoice number already exists: {entity.invoice_number}")
        entity.calculate_clp_total()
        logger.debug("Export invoice validation passed")

    def get_by_invoice_number(self, invoice_number: str) -> InvoiceExportResponse:
        """Get invoice by number."""
        logger.info(f"Getting export invoice by number: {invoice_number}")
        invoice = self.invoice_repo.get_by_invoice_number(invoice_number)
        if not invoice:
            raise NotFoundException(f"Invoice not found: {invoice_number}")
        return self.response_schema.model_validate(invoice)

    def get_by_company(self, company_id: int, skip: int = 0, limit: int = 100) -> List[InvoiceExportListResponse]:
        """Get invoices by company."""
        logger.info(f"Getting export invoices for company_id={company_id}")
        invoices = self.invoice_repo.get_by_company(company_id, skip, limit)
        return [InvoiceExportListResponse.model_validate(i) for i in invoices]
