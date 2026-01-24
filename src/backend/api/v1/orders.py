"""
FastAPI routes for Order endpoints.

Provides REST API for managing orders including CRUD operations,
filtering by company/status, and creating orders from quotes.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from src.backend.api.dependencies import get_database as get_db
from src.backend.repositories.business.order_repository import OrderRepository
from src.backend.services.business.order_service import OrderService
from src.shared.schemas.business.order import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderListResponse,
    OrderProductCreate,
    OrderProductUpdate,
    OrderProductResponse,
)
from src.backend.exceptions.service import ValidationException
from src.backend.exceptions.repository import NotFoundException
from src.backend.utils.logger import logger

router = APIRouter(prefix="/orders", tags=["orders"])


def get_order_service(db: Session = Depends(get_db)) -> OrderService:
    """
    Dependency to get OrderService instance.

    Args:
        db: Database session

    Returns:
        OrderService instance
    """
    repository = OrderRepository(db)
    return OrderService(repository, db)


@router.get("/", response_model=list[OrderListResponse])
def get_orders(
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    service: OrderService = Depends(get_order_service),
) -> list[OrderListResponse]:
    """
    Get all orders with pagination.

    Returns a list of orders ordered by order date (newest first).

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        service: Order service instance

    Returns:
        List of orders
    """
    logger.info(f"GET /orders - skip={skip}, limit={limit}")
    try:
        orders = service.get_all(skip=skip, limit=limit)
        logger.success(f"Retrieved {len(orders)} order(s)")
        return orders
    except Exception as e:
        logger.error(f"Error retrieving orders: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving orders: {str(e)}"
        )


@router.get("/number/{order_number}", response_model=OrderResponse)
def get_order_by_number(
    order_number: str,
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    """
    Get order by unique order number.

    Args:
        order_number: Order number (e.g., "O-2025-001")
        service: Order service instance

    Returns:
        Order data

    Raises:
        404: If order not found
    """
    logger.info(f"GET /orders/number/{order_number}")
    try:
        order = service.get_by_order_number(order_number)
        logger.success(f"Order found: {order_number}")
        return order
    except NotFoundException as e:
        logger.warning(f"Order not found: {order_number}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error retrieving order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving order: {str(e)}"
        )


@router.get("/company/{company_id}", response_model=list[OrderListResponse])
def get_orders_by_company(
    company_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: OrderService = Depends(get_order_service),
) -> list[OrderListResponse]:
    """
    Get all orders for a specific company.

    Args:
        company_id: Company ID
        skip: Pagination offset
        limit: Maximum records
        service: Order service instance

    Returns:
        List of orders for the company
    """
    logger.info(f"GET /orders/company/{company_id}")
    try:
        orders = service.get_by_company(company_id, skip, limit)
        logger.success(f"Retrieved {len(orders)} order(s) for company_id={company_id}")
        return orders
    except Exception as e:
        logger.error(f"Error retrieving orders for company: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving orders: {str(e)}"
        )


@router.get("/status/{status_id}", response_model=list[OrderListResponse])
def get_orders_by_status(
    status_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: OrderService = Depends(get_order_service),
) -> list[OrderListResponse]:
    """
    Get orders by status.

    Args:
        status_id: Order status ID
        skip: Pagination offset
        limit: Maximum records
        service: Order service instance

    Returns:
        List of orders with the specified status
    """
    logger.info(f"GET /orders/status/{status_id}")
    try:
        orders = service.get_by_status(status_id, skip, limit)
        logger.success(f"Retrieved {len(orders)} order(s) with status_id={status_id}")
        return orders
    except Exception as e:
        logger.error(f"Error retrieving orders by status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving orders: {str(e)}"
        )


@router.get("/staff/{staff_id}", response_model=list[OrderListResponse])
def get_orders_by_staff(
    staff_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: OrderService = Depends(get_order_service),
) -> list[OrderListResponse]:
    """
    Get orders assigned to staff member.

    Args:
        staff_id: Staff ID
        skip: Pagination offset
        limit: Maximum records
        service: Order service instance

    Returns:
        List of orders for the staff member
    """
    logger.info(f"GET /orders/staff/{staff_id}")
    try:
        orders = service.get_by_staff(staff_id, skip, limit)
        logger.success(f"Retrieved {len(orders)} order(s) for staff_id={staff_id}")
        return orders
    except Exception as e:
        logger.error(f"Error retrieving orders by staff: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving orders: {str(e)}"
        )


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    """
    Get order by ID with all products.

    Args:
        order_id: Order ID
        service: Order service instance

    Returns:
        Order data with products
    """
    logger.info(f"GET /orders/{order_id}")
    try:
        order = service.get_with_products(order_id)
        logger.success(f"Order found: id={order_id}")
        return order
    except NotFoundException as e:
        logger.warning(f"Order not found: id={order_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error retrieving order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving order: {str(e)}"
        )


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order: OrderCreate,
    user_id: int = Query(..., description="User creating the order"),
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    """
    Create a new order.

    Args:
        order: Order data
        user_id: User creating the order
        service: Order service instance

    Returns:
        Created order
    """
    logger.info(f"POST /orders - Creating order: {order.order_number}")
    try:
        created = service.create(order, user_id=user_id)
        logger.success(f"Order created: id={created.id}, number={order.order_number}")
        return created
    except ValidationException as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating order: {str(e)}"
        )


@router.post("/from-quote/{quote_id}", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order_from_quote(
    quote_id: int,
    user_id: int = Query(..., description="User creating the order"),
    order_number: str = Query(None, description="Custom order number (auto-generated if not provided)"),
    status_id: int = Query(..., description="Initial order status ID"),
    payment_status_id: int = Query(..., description="Initial payment status ID"),
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    """
    Create order from an accepted quote.

    Copies quote data to new order including company, products, and financial data.

    Args:
        quote_id: Quote ID to convert
        user_id: User creating the order
        order_number: Custom order number (optional)
        status_id: Initial order status
        payment_status_id: Initial payment status
        service: Order service instance

    Returns:
        Created order
    """
    logger.info(f"POST /orders/from-quote/{quote_id}")
    try:
        order = service.create_from_quote(
            quote_id=quote_id,
            user_id=user_id,
            order_number=order_number,
            status_id=status_id,
            payment_status_id=payment_status_id,
        )
        logger.success(f"Order created from quote_id={quote_id}: order_id={order.id}")
        return order
    except NotFoundException as e:
        logger.warning(f"Quote not found: id={quote_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationException as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating order from quote: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating order: {str(e)}"
        )


@router.put("/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: int,
    order: OrderUpdate,
    user_id: int = Query(..., description="User updating the order"),
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    """
    Update an existing order.

    Args:
        order_id: Order ID
        order: Order update data
        user_id: User updating the order
        service: Order service instance

    Returns:
        Updated order
    """
    logger.info(f"PUT /orders/{order_id}")
    try:
        updated = service.update(order_id, order, user_id=user_id)
        logger.success(f"Order updated: id={order_id}")
        return updated
    except NotFoundException as e:
        logger.warning(f"Order not found: id={order_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationException as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating order: {str(e)}"
        )


@router.post("/{order_id}/calculate", response_model=OrderResponse)
def calculate_order_totals(
    order_id: int,
    user_id: int = Query(..., description="User performing calculation"),
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    """
    Recalculate order totals.

    Calculates subtotal, tax, and total based on line items.

    Args:
        order_id: Order ID
        user_id: User performing calculation
        service: Order service instance

    Returns:
        Order with updated totals
    """
    logger.info(f"POST /orders/{order_id}/calculate")
    try:
        order = service.calculate_totals(order_id, user_id)
        logger.success(f"Order totals calculated: id={order_id}")
        return order
    except NotFoundException as e:
        logger.warning(f"Order not found: id={order_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error calculating order totals: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating totals: {str(e)}"
        )


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(
    order_id: int,
    user_id: int = Query(..., description="User deleting the order"),
    service: OrderService = Depends(get_order_service),
) -> None:
    """
    Delete an order (soft delete - sets is_active=False).

    Args:
        order_id: Order ID
        user_id: User deleting the order
        service: Order service instance
    """
    logger.info(f"DELETE /orders/{order_id}")
    try:
        service.delete(order_id, user_id=user_id)
        logger.success(f"Order deleted: id={order_id}")
    except NotFoundException as e:
        logger.warning(f"Order not found: id={order_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error deleting order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting order: {str(e)}"
        )


# ============================================================================
# ORDER PRODUCT ENDPOINTS
# ============================================================================

@router.post("/{order_id}/products", response_model=OrderProductResponse, status_code=status.HTTP_201_CREATED)
def add_order_product(
    order_id: int,
    product: OrderProductCreate,
    user_id: int = Query(..., description="User adding the product"),
    service: OrderService = Depends(get_order_service),
) -> OrderProductResponse:
    """
    Add product to order.

    Args:
        order_id: Order ID
        product: Product data
        user_id: User adding the product
        service: Order service instance

    Returns:
        Created order product
    """
    logger.info(f"POST /orders/{order_id}/products")
    try:
        created = service.add_product(order_id, product, user_id)
        logger.success(f"Product added to order_id={order_id}")
        return created
    except NotFoundException as e:
        logger.warning(f"Order not found: id={order_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationException as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error adding product to order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding product: {str(e)}"
        )


@router.put("/{order_id}/products/{product_id}", response_model=OrderProductResponse)
def update_order_product(
    order_id: int,
    product_id: int,
    product: OrderProductUpdate,
    user_id: int = Query(..., description="User updating the product"),
    service: OrderService = Depends(get_order_service),
) -> OrderProductResponse:
    """
    Update order product.

    Args:
        order_id: Order ID
        product_id: Order product ID
        product: Update data
        user_id: User updating the product
        service: Order service instance

    Returns:
        Updated order product
    """
    logger.info(f"PUT /orders/{order_id}/products/{product_id}")
    try:
        updated = service.update_product(order_id, product_id, product, user_id)
        logger.success(f"Product updated in order_id={order_id}")
        return updated
    except NotFoundException as e:
        logger.warning(f"Order or product not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationException as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating order product: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating product: {str(e)}"
		)


@router.delete("/{order_id}/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_order_product(
    order_id: int,
    product_id: int,
    user_id: int = Query(..., description="User removing the product"),
    service: OrderService = Depends(get_order_service),
) -> None:
    """
    Remove product from order.

    Args:
        order_id: Order ID
        product_id: Order product ID
        user_id: User removing the product
        service: Order service instance
    """
    logger.info(f"DELETE /orders/{order_id}/products/{product_id}")
    try:
        service.remove_product(order_id, product_id, user_id)
        logger.success(f"Product removed from order_id={order_id}")
    except NotFoundException as e:
        logger.warning(f"Order or product not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error removing order product: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error removing product: {str(e)}"
        )
