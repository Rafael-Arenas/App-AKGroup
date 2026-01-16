"""
FastAPI routes for Invoice endpoints.

Provides REST API for managing InvoiceSII and InvoiceExport.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from src.backend.database import get_db
from src.backend.repositories.business.invoice_repository import InvoiceSIIRepository, InvoiceExportRepository
from src.backend.services.business.invoice_service import InvoiceSIIService, InvoiceExportService
from src.shared.schemas.business.invoice import (
    InvoiceSIICreate, InvoiceSIIUpdate, InvoiceSIIResponse, InvoiceSIIListResponse,
    InvoiceExportCreate, InvoiceExportUpdate, InvoiceExportResponse, InvoiceExportListResponse,
)
from src.backend.exceptions.service import ValidationException
from src.backend.exceptions.repository import NotFoundException
from src.backend.utils.logger import logger

# Create routers
invoices_router = APIRouter(prefix="/invoices", tags=["invoices"])
invoices_sii_router = APIRouter(prefix="/invoices-sii", tags=["invoices-sii"])
invoices_export_router = APIRouter(prefix="/invoices-export", tags=["invoices-export"])


# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================

def get_invoice_sii_service(db: Session = Depends(get_db)) -> InvoiceSIIService:
    """Get InvoiceSIIService instance."""
    repository = InvoiceSIIRepository(db)
    return InvoiceSIIService(repository, db)


def get_invoice_export_service(db: Session = Depends(get_db)) -> InvoiceExportService:
    """Get InvoiceExportService instance."""
    repository = InvoiceExportRepository(db)
    return InvoiceExportService(repository, db)


# ============================================================================
# INVOICE SII ENDPOINTS
# ============================================================================

@invoices_sii_router.get("/", response_model=list[InvoiceSIIListResponse])
def get_invoices_sii(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: InvoiceSIIService = Depends(get_invoice_sii_service),
) -> list[InvoiceSIIListResponse]:
    """Get all SII invoices with pagination."""
    logger.info(f"GET /invoices-sii - skip={skip}, limit={limit}")
    try:
        invoices = service.get_all(skip=skip, limit=limit)
        logger.success(f"Retrieved {len(invoices)} SII invoice(s)")
        return invoices
    except Exception as e:
        logger.error(f"Error retrieving SII invoices: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@invoices_sii_router.get("/number/{invoice_number}", response_model=InvoiceSIIResponse)
def get_invoice_sii_by_number(
    invoice_number: str,
    service: InvoiceSIIService = Depends(get_invoice_sii_service),
) -> InvoiceSIIResponse:
    """Get SII invoice by number."""
    logger.info(f"GET /invoices-sii/number/{invoice_number}")
    try:
        invoice = service.get_by_invoice_number(invoice_number)
        return invoice
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@invoices_sii_router.get("/company/{company_id}", response_model=list[InvoiceSIIListResponse])
def get_invoices_sii_by_company(
    company_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: InvoiceSIIService = Depends(get_invoice_sii_service),
) -> list[InvoiceSIIListResponse]:
    """Get SII invoices by company."""
    logger.info(f"GET /invoices-sii/company/{company_id}")
    try:
        invoices = service.get_by_company(company_id, skip, limit)
        return invoices
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@invoices_sii_router.get("/{invoice_id}", response_model=InvoiceSIIResponse)
def get_invoice_sii(
    invoice_id: int,
    service: InvoiceSIIService = Depends(get_invoice_sii_service),
) -> InvoiceSIIResponse:
    """Get SII invoice by ID."""
    logger.info(f"GET /invoices-sii/{invoice_id}")
    try:
        invoice = service.get_by_id(invoice_id)
        return invoice
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@invoices_sii_router.post("/", response_model=InvoiceSIIResponse, status_code=status.HTTP_201_CREATED)
def create_invoice_sii(
    invoice: InvoiceSIICreate,
    user_id: int = Query(..., description="User creating the invoice"),
    service: InvoiceSIIService = Depends(get_invoice_sii_service),
) -> InvoiceSIIResponse:
    """Create a new SII invoice."""
    logger.info(f"POST /invoices-sii - Creating: {invoice.invoice_number}")
    try:
        created = service.create(invoice, user_id=user_id)
        logger.success(f"SII invoice created: id={created.id}")
        return created
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@invoices_sii_router.put("/{invoice_id}", response_model=InvoiceSIIResponse)
def update_invoice_sii(
    invoice_id: int,
    invoice: InvoiceSIIUpdate,
    user_id: int = Query(..., description="User updating the invoice"),
    service: InvoiceSIIService = Depends(get_invoice_sii_service),
) -> InvoiceSIIResponse:
    """Update an SII invoice."""
    logger.info(f"PUT /invoices-sii/{invoice_id}")
    try:
        updated = service.update(invoice_id, invoice, user_id=user_id)
        return updated
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@invoices_sii_router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invoice_sii(
    invoice_id: int,
    user_id: int = Query(..., description="User deleting the invoice"),
    service: InvoiceSIIService = Depends(get_invoice_sii_service),
) -> None:
    """Delete an SII invoice (soft delete)."""
    logger.info(f"DELETE /invoices-sii/{invoice_id}")
    try:
        service.delete(invoice_id, user_id=user_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================================================
# INVOICE EXPORT ENDPOINTS
# ============================================================================

@invoices_export_router.get("/", response_model=list[InvoiceExportListResponse])
def get_invoices_export(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: InvoiceExportService = Depends(get_invoice_export_service),
) -> list[InvoiceExportListResponse]:
    """Get all export invoices with pagination."""
    logger.info(f"GET /invoices-export - skip={skip}, limit={limit}")
    try:
        invoices = service.get_all(skip=skip, limit=limit)
        logger.success(f"Retrieved {len(invoices)} export invoice(s)")
        return invoices
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@invoices_export_router.get("/number/{invoice_number}", response_model=InvoiceExportResponse)
def get_invoice_export_by_number(
    invoice_number: str,
    service: InvoiceExportService = Depends(get_invoice_export_service),
) -> InvoiceExportResponse:
    """Get export invoice by number."""
    logger.info(f"GET /invoices-export/number/{invoice_number}")
    try:
        invoice = service.get_by_invoice_number(invoice_number)
        return invoice
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@invoices_export_router.get("/company/{company_id}", response_model=list[InvoiceExportListResponse])
def get_invoices_export_by_company(
    company_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: InvoiceExportService = Depends(get_invoice_export_service),
) -> list[InvoiceExportListResponse]:
    """Get export invoices by company."""
    logger.info(f"GET /invoices-export/company/{company_id}")
    try:
        invoices = service.get_by_company(company_id, skip, limit)
        return invoices
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@invoices_export_router.get("/{invoice_id}", response_model=InvoiceExportResponse)
def get_invoice_export(
    invoice_id: int,
    service: InvoiceExportService = Depends(get_invoice_export_service),
) -> InvoiceExportResponse:
    """Get export invoice by ID."""
    logger.info(f"GET /invoices-export/{invoice_id}")
    try:
        invoice = service.get_by_id(invoice_id)
        return invoice
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@invoices_export_router.post("/", response_model=InvoiceExportResponse, status_code=status.HTTP_201_CREATED)
def create_invoice_export(
    invoice: InvoiceExportCreate,
    user_id: int = Query(..., description="User creating the invoice"),
    service: InvoiceExportService = Depends(get_invoice_export_service),
) -> InvoiceExportResponse:
    """Create a new export invoice."""
    logger.info(f"POST /invoices-export - Creating: {invoice.invoice_number}")
    try:
        created = service.create(invoice, user_id=user_id)
        logger.success(f"Export invoice created: id={created.id}")
        return created
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@invoices_export_router.put("/{invoice_id}", response_model=InvoiceExportResponse)
def update_invoice_export(
    invoice_id: int,
    invoice: InvoiceExportUpdate,
    user_id: int = Query(..., description="User updating the invoice"),
    service: InvoiceExportService = Depends(get_invoice_export_service),
) -> InvoiceExportResponse:
    """Update an export invoice."""
    logger.info(f"PUT /invoices-export/{invoice_id}")
    try:
        updated = service.update(invoice_id, invoice, user_id=user_id)
        return updated
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@invoices_export_router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invoice_export(
    invoice_id: int,
    user_id: int = Query(..., description="User deleting the invoice"),
    service: InvoiceExportService = Depends(get_invoice_export_service),
) -> None:
    """Delete an export invoice (soft delete)."""
    logger.info(f"DELETE /invoices-export/{invoice_id}")
    try:
        service.delete(invoice_id, user_id=user_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Include all sub-routers
invoices_router.include_router(invoices_sii_router)
invoices_router.include_router(invoices_export_router)
