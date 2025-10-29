"""
REST API endpoints for Quote and QuoteProduct.

Provides CRUD operations and custom endpoints for quote management.
"""

from typing import List
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from src.api.dependencies import get_database, get_current_user_id
from src.services.business.quote_service import QuoteService
from src.repositories.business.quote_repository import QuoteRepository
from src.schemas.business.quote import (
    QuoteCreate,
    QuoteUpdate,
    QuoteResponse,
    QuoteListResponse,
    QuoteProductCreate,
    QuoteProductUpdate,
    QuoteProductResponse,
)
from src.schemas.base import MessageResponse
from src.utils.logger import logger

router = APIRouter(prefix="/quotes", tags=["quotes"])


def get_quote_service(db: Session = Depends(get_database)) -> QuoteService:
    """
    Dependency to get QuoteService instance.

    Args:
        db: Database session

    Returns:
        Configured QuoteService instance
    """
    repository = QuoteRepository(db)
    return QuoteService(repository=repository, session=db)


# ============================================================================
# QUOTE ENDPOINTS
# ============================================================================

@router.get("/", response_model=List[QuoteListResponse])
def get_quotes(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    service: QuoteService = Depends(get_quote_service),
):
    """
    Get all quotes with pagination.

    Args:
        skip: Number of records to skip (pagination offset)
        limit: Maximum number of records to return

    Returns:
        List of quotes (summary view without products)

    Example:
        GET /api/v1/quotes?skip=0&limit=50
    """
    logger.info(f"GET /quotes - skip={skip}, limit={limit}")
    quotes = service.get_all(skip=skip, limit=limit)
    logger.info(f"Returning {len(quotes)} quote(s)")
    return quotes


@router.get("/company/{company_id}", response_model=List[QuoteListResponse])
def get_quotes_by_company(
    company_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: QuoteService = Depends(get_quote_service),
):
    """
    Get all quotes for a specific company.

    Args:
        company_id: Company ID
        skip: Pagination offset
        limit: Maximum records

    Returns:
        List of quotes for the company

    Example:
        GET /api/v1/quotes/company/5?skip=0&limit=10
    """
    logger.info(f"GET /quotes/company/{company_id}")
    quotes = service.get_by_company(company_id, skip, limit)
    logger.info(f"Returning {len(quotes)} quote(s) for company_id={company_id}")
    return quotes


@router.get("/status/{status_id}", response_model=List[QuoteListResponse])
def get_quotes_by_status(
    status_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: QuoteService = Depends(get_quote_service),
):
    """
    Get quotes by status.

    Args:
        status_id: Quote status ID
        skip: Pagination offset
        limit: Maximum records

    Returns:
        List of quotes with the specified status
    """
    logger.info(f"GET /quotes/status/{status_id}")
    quotes = service.get_by_status(status_id, skip, limit)
    logger.info(f"Returning {len(quotes)} quote(s) with status_id={status_id}")
    return quotes


@router.get("/staff/{staff_id}", response_model=List[QuoteListResponse])
def get_quotes_by_staff(
    staff_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: QuoteService = Depends(get_quote_service),
):
    """
    Get quotes assigned to a staff member.

    Args:
        staff_id: Staff member ID
        skip: Pagination offset
        limit: Maximum records

    Returns:
        List of quotes assigned to the staff member
    """
    logger.info(f"GET /quotes/staff/{staff_id}")
    quotes = service.get_by_staff(staff_id, skip, limit)
    logger.info(f"Returning {len(quotes)} quote(s) for staff_id={staff_id}")
    return quotes


@router.get("/search", response_model=List[QuoteListResponse])
def search_quotes(
    subject: str = Query(..., min_length=1, description="Text to search in subject"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: QuoteService = Depends(get_quote_service),
):
    """
    Search quotes by subject (partial match, case-insensitive).

    Args:
        subject: Text to search in subject field
        skip: Pagination offset
        limit: Maximum records

    Returns:
        List of matching quotes

    Example:
        GET /api/v1/quotes/search?subject=equipment&skip=0&limit=10
    """
    logger.info(f"GET /quotes/search?subject={subject}")
    quotes = service.search_by_subject(subject, skip, limit)
    logger.info(f"Search returned {len(quotes)} quote(s)")
    return quotes


@router.get("/number/{quote_number}", response_model=QuoteResponse)
def get_quote_by_number(
    quote_number: str,
    service: QuoteService = Depends(get_quote_service),
):
    """
    Get quote by unique quote number.

    Args:
        quote_number: Quote number (e.g., "Q-2025-001")

    Returns:
        Quote with all details and products

    Raises:
        404: If quote not found

    Example:
        GET /api/v1/quotes/number/Q-2025-001
    """
    logger.info(f"GET /quotes/number/{quote_number}")
    quote = service.get_by_quote_number(quote_number)
    logger.info(f"Quote found: {quote.subject}")
    return quote


@router.get("/{quote_id}", response_model=QuoteResponse)
def get_quote(
    quote_id: int,
    service: QuoteService = Depends(get_quote_service),
):
    """
    Get quote by ID with all products.

    Args:
        quote_id: Quote ID

    Returns:
        Quote with all details and products

    Raises:
        404: If quote not found

    Example:
        GET /api/v1/quotes/123
    """
    logger.info(f"GET /quotes/{quote_id}")
    quote = service.get_with_products(quote_id)
    logger.info(f"Quote found: {quote.quote_number}")
    return quote


@router.post("/", response_model=QuoteResponse, status_code=status.HTTP_201_CREATED)
def create_quote(
    quote_data: QuoteCreate,
    service: QuoteService = Depends(get_quote_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Create new quote.

    Can optionally include products (line items) in the request.
    Products will be automatically added and totals calculated.

    Args:
        quote_data: Quote data including optional products
        service: Quote service
        user_id: Current user ID

    Returns:
        Created quote with calculated totals

    Example:
        POST /api/v1/quotes
        {
            "quote_number": "Q-2025-001",
            "subject": "New equipment",
            "company_id": 5,
            "staff_id": 2,
            "status_id": 1,
            "quote_date": "2025-01-15",
            "currency_id": 1,
            "products": [
                {
                    "product_id": 10,
                    "quantity": 5,
                    "unit_price": 1500
                }
            ]
        }
    """
    logger.info(f"POST /quotes - number={quote_data.quote_number}")
    quote = service.create(quote_data, user_id)

    # Add products if provided
    if quote_data.products:
        for product_data in quote_data.products:
            service.add_product(quote.id, product_data, user_id)

        # Recalculate totals with products
        quote = service.calculate_totals(quote.id, user_id)

    logger.success(f"Quote created: id={quote.id}, number={quote.quote_number}")
    return quote


@router.put("/{quote_id}", response_model=QuoteResponse)
def update_quote(
    quote_id: int,
    quote_data: QuoteUpdate,
    service: QuoteService = Depends(get_quote_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Update existing quote.

    Only updates quote header fields. To modify products,
    use the product endpoints.

    Args:
        quote_id: Quote ID
        quote_data: Update data (only provided fields will be updated)
        service: Quote service
        user_id: Current user ID

    Returns:
        Updated quote

    Raises:
        404: If quote not found

    Example:
        PUT /api/v1/quotes/123
        {
            "subject": "Updated subject",
            "status_id": 2
        }
    """
    logger.info(f"PUT /quotes/{quote_id}")
    quote = service.update(quote_id, quote_data, user_id)
    logger.success(f"Quote updated: id={quote_id}")
    return quote


@router.delete("/{quote_id}", response_model=MessageResponse)
def delete_quote(
    quote_id: int,
    soft: bool = Query(True, description="Use soft delete (mark as deleted)"),
    service: QuoteService = Depends(get_quote_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Delete quote.

    By default uses soft delete (marks as deleted). Can permanently
    delete using soft=false parameter.

    Args:
        quote_id: Quote ID
        soft: If True, soft delete; if False, hard delete
        service: Quote service
        user_id: Current user ID

    Returns:
        Success message

    Raises:
        404: If quote not found

    Example:
        DELETE /api/v1/quotes/123?soft=true
    """
    logger.info(f"DELETE /quotes/{quote_id} (soft={soft})")
    service.delete(quote_id, user_id, soft=soft)
    delete_type = "marked as deleted" if soft else "permanently deleted"
    logger.success(f"Quote {delete_type}: id={quote_id}")
    return MessageResponse(
        message=f"Quote {delete_type} successfully",
        details={"quote_id": quote_id, "soft_delete": soft}
    )


@router.post("/{quote_id}/calculate", response_model=QuoteResponse)
def calculate_quote_totals(
    quote_id: int,
    service: QuoteService = Depends(get_quote_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Recalculate quote totals from line items.

    Useful when products have been modified externally or to refresh calculations.

    Args:
        quote_id: Quote ID
        service: Quote service
        user_id: Current user ID

    Returns:
        Quote with recalculated totals

    Raises:
        404: If quote not found

    Example:
        POST /api/v1/quotes/123/calculate
    """
    logger.info(f"POST /quotes/{quote_id}/calculate")
    quote = service.calculate_totals(quote_id, user_id)
    logger.success(f"Totals calculated for quote_id={quote_id}")
    return quote


# ============================================================================
# QUOTE PRODUCT ENDPOINTS
# ============================================================================

@router.post("/{quote_id}/products", response_model=QuoteProductResponse, status_code=status.HTTP_201_CREATED)
def add_product_to_quote(
    quote_id: int,
    product_data: QuoteProductCreate,
    service: QuoteService = Depends(get_quote_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Add product to quote.

    Automatically calculates line item subtotal and updates quote totals.

    Args:
        quote_id: Quote ID
        product_data: Product data
        service: Quote service
        user_id: Current user ID

    Returns:
        Created quote product

    Raises:
        404: If quote not found

    Example:
        POST /api/v1/quotes/123/products
        {
            "product_id": 10,
            "sequence": 1,
            "quantity": 5,
            "unit_price": 1500,
            "discount_percentage": 10
        }
    """
    logger.info(f"POST /quotes/{quote_id}/products")
    product = service.add_product(quote_id, product_data, user_id)
    logger.success(f"Product added to quote_id={quote_id}: product_id={product.id}")
    return product


@router.put("/products/{product_id}", response_model=QuoteProductResponse)
def update_quote_product(
    product_id: int,
    product_data: QuoteProductUpdate,
    service: QuoteService = Depends(get_quote_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Update quote product.

    Automatically recalculates line item subtotal and quote totals.

    Args:
        product_id: Quote product ID
        product_data: Update data
        service: Quote service
        user_id: Current user ID

    Returns:
        Updated quote product

    Raises:
        404: If product not found

    Example:
        PUT /api/v1/quotes/products/456
        {
            "quantity": 10,
            "discount_percentage": 15
        }
    """
    logger.info(f"PUT /quotes/products/{product_id}")
    product = service.update_product(product_id, product_data, user_id)
    logger.success(f"Quote product updated: id={product_id}")
    return product


@router.delete("/products/{product_id}", response_model=MessageResponse)
def remove_product_from_quote(
    product_id: int,
    service: QuoteService = Depends(get_quote_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Remove product from quote.

    Automatically updates quote totals after removal.

    Args:
        product_id: Quote product ID
        service: Quote service
        user_id: Current user ID

    Returns:
        Success message

    Raises:
        404: If product not found

    Example:
        DELETE /api/v1/quotes/products/456
    """
    logger.info(f"DELETE /quotes/products/{product_id}")
    service.remove_product(product_id, user_id)
    logger.success(f"Product removed from quote: product_id={product_id}")
    return MessageResponse(
        message="Product removed from quote successfully",
        details={"product_id": product_id}
    )
