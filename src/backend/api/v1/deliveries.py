"""
FastAPI routes for Delivery endpoints.

Provides REST API for managing delivery orders, transports, and payment conditions.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from src.backend.database import get_db
from src.backend.repositories.business.delivery_repository import (
    DeliveryOrderRepository,
    TransportRepository,
    PaymentConditionRepository,
)
from src.backend.services.business.delivery_service import (
    DeliveryOrderService,
    TransportService,
    PaymentConditionService,
)
from src.shared.schemas.business.delivery import (
    DeliveryOrderCreate,
    DeliveryOrderUpdate,
    DeliveryOrderResponse,
    DeliveryOrderListResponse,
    TransportCreate,
    TransportUpdate,
    TransportResponse,
    PaymentConditionCreate,
    PaymentConditionUpdate,
    PaymentConditionResponse,
)
from src.backend.exceptions.service import ValidationException
from src.backend.exceptions.repository import NotFoundException
from src.backend.utils.logger import logger

# Create main router
deliveries_router = APIRouter(prefix="/deliveries", tags=["deliveries"])

# Create sub-routers
delivery_orders_router = APIRouter(prefix="/delivery-orders", tags=["delivery-orders"])
transports_router = APIRouter(prefix="/transports", tags=["transports"])
payment_conditions_router = APIRouter(prefix="/payment-conditions", tags=["payment-conditions"])


# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================

def get_delivery_service(db: Session = Depends(get_db)) -> DeliveryOrderService:
    """Get DeliveryOrderService instance."""
    repository = DeliveryOrderRepository(db)
    return DeliveryOrderService(repository, db)


def get_transport_service(db: Session = Depends(get_db)) -> TransportService:
    """Get TransportService instance."""
    repository = TransportRepository(db)
    return TransportService(repository, db)


def get_payment_condition_service(db: Session = Depends(get_db)) -> PaymentConditionService:
    """Get PaymentConditionService instance."""
    repository = PaymentConditionRepository(db)
    return PaymentConditionService(repository, db)


# ============================================================================
# DELIVERY ORDER ENDPOINTS
# ============================================================================

@delivery_orders_router.get("/", response_model=List[DeliveryOrderListResponse])
def get_delivery_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: DeliveryOrderService = Depends(get_delivery_service),
) -> List[DeliveryOrderListResponse]:
    """Get all delivery orders with pagination."""
    logger.info(f"GET /delivery-orders - skip={skip}, limit={limit}")
    try:
        deliveries = service.get_all(skip=skip, limit=limit)
        logger.success(f"Retrieved {len(deliveries)} delivery order(s)")
        return deliveries
    except Exception as e:
        logger.error(f"Error retrieving delivery orders: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving delivery orders: {str(e)}"
        )


@delivery_orders_router.get("/number/{delivery_number}", response_model=DeliveryOrderResponse)
def get_delivery_by_number(
    delivery_number: str,
    service: DeliveryOrderService = Depends(get_delivery_service),
) -> DeliveryOrderResponse:
    """Get delivery order by unique delivery number."""
    logger.info(f"GET /delivery-orders/number/{delivery_number}")
    try:
        delivery = service.get_by_delivery_number(delivery_number)
        logger.success(f"Delivery order found: {delivery_number}")
        return delivery
    except NotFoundException as e:
        logger.warning(f"Delivery order not found: {delivery_number}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving delivery order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving delivery order: {str(e)}"
        )


@delivery_orders_router.get("/company/{company_id}", response_model=List[DeliveryOrderListResponse])
def get_deliveries_by_company(
    company_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: DeliveryOrderService = Depends(get_delivery_service),
) -> List[DeliveryOrderListResponse]:
    """Get delivery orders by company."""
    logger.info(f"GET /delivery-orders/company/{company_id}")
    try:
        deliveries = service.get_by_company(company_id, skip, limit)
        logger.success(f"Retrieved {len(deliveries)} delivery order(s)")
        return deliveries
    except Exception as e:
        logger.error(f"Error retrieving delivery orders: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving delivery orders: {str(e)}"
        )


@delivery_orders_router.get("/status/{status}", response_model=List[DeliveryOrderListResponse])
def get_deliveries_by_status(
    status: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: DeliveryOrderService = Depends(get_delivery_service),
) -> List[DeliveryOrderListResponse]:
    """Get delivery orders by status."""
    logger.info(f"GET /delivery-orders/status/{status}")
    try:
        deliveries = service.get_by_status(status, skip, limit)
        logger.success(f"Retrieved {len(deliveries)} delivery order(s)")
        return deliveries
    except Exception as e:
        logger.error(f"Error retrieving delivery orders: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving delivery orders: {str(e)}"
        )


@delivery_orders_router.get("/{delivery_id}", response_model=DeliveryOrderResponse)
def get_delivery(
    delivery_id: int,
    service: DeliveryOrderService = Depends(get_delivery_service),
) -> DeliveryOrderResponse:
    """Get delivery order by ID."""
    logger.info(f"GET /delivery-orders/{delivery_id}")
    try:
        delivery = service.get_by_id(delivery_id)
        logger.success(f"Delivery order found: id={delivery_id}")
        return delivery
    except NotFoundException as e:
        logger.warning(f"Delivery order not found: id={delivery_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving delivery order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving delivery order: {str(e)}"
        )


@delivery_orders_router.post("/", response_model=DeliveryOrderResponse, status_code=status.HTTP_201_CREATED)
def create_delivery(
    delivery: DeliveryOrderCreate,
    user_id: int = Query(..., description="User creating the delivery"),
    service: DeliveryOrderService = Depends(get_delivery_service),
) -> DeliveryOrderResponse:
    """Create a new delivery order."""
    logger.info(f"POST /delivery-orders - Creating: {delivery.delivery_number}")
    try:
        created = service.create(delivery, user_id=user_id)
        logger.success(f"Delivery order created: id={created.id}")
        return created
    except ValidationException as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating delivery order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating delivery order: {str(e)}"
        )


@delivery_orders_router.put("/{delivery_id}", response_model=DeliveryOrderResponse)
def update_delivery(
    delivery_id: int,
    delivery: DeliveryOrderUpdate,
    user_id: int = Query(..., description="User updating the delivery"),
    service: DeliveryOrderService = Depends(get_delivery_service),
) -> DeliveryOrderResponse:
    """Update a delivery order."""
    logger.info(f"PUT /delivery-orders/{delivery_id}")
    try:
        updated = service.update(delivery_id, delivery, user_id=user_id)
        logger.success(f"Delivery order updated: id={delivery_id}")
        return updated
    except NotFoundException as e:
        logger.warning(f"Delivery order not found: id={delivery_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationException as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating delivery order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating delivery order: {str(e)}"
        )


@delivery_orders_router.post("/{delivery_id}/mark-delivered", response_model=DeliveryOrderResponse)
def mark_delivery_delivered(
    delivery_id: int,
    signature_name: str = Query(..., description="Name of recipient"),
    signature_id: str = Query(..., description="ID of recipient"),
    notes: str = Query(None, description="Delivery notes"),
    user_id: int = Query(..., description="User marking delivery"),
    service: DeliveryOrderService = Depends(get_delivery_service),
) -> DeliveryOrderResponse:
    """Mark delivery as completed with signature."""
    logger.info(f"POST /delivery-orders/{delivery_id}/mark-delivered")
    try:
        delivery = service.mark_delivered(
            delivery_id=delivery_id,
            signature_name=signature_name,
            signature_id=signature_id,
            notes=notes,
            user_id=user_id,
        )
        logger.success(f"Delivery marked as delivered: id={delivery_id}")
        return delivery
    except NotFoundException as e:
        logger.warning(f"Delivery order not found: id={delivery_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error marking delivery: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error marking delivery: {str(e)}"
        )


@delivery_orders_router.delete("/{delivery_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_delivery(
    delivery_id: int,
    user_id: int = Query(..., description="User deleting the delivery"),
    service: DeliveryOrderService = Depends(get_delivery_service),
) -> None:
    """Delete a delivery order (soft delete)."""
    logger.info(f"DELETE /delivery-orders/{delivery_id}")
    try:
        service.delete(delivery_id, user_id=user_id)
        logger.success(f"Delivery order deleted: id={delivery_id}")
    except NotFoundException as e:
        logger.warning(f"Delivery order not found: id={delivery_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting delivery order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting delivery order: {str(e)}"
        )


# ============================================================================
# TRANSPORT ENDPOINTS
# ============================================================================

@transports_router.get("/", response_model=List[TransportResponse])
def get_transports(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: TransportService = Depends(get_transport_service),
) -> List[TransportResponse]:
    """Get all transports with pagination."""
    logger.info(f"GET /transports - skip={skip}, limit={limit}")
    try:
        transports = service.get_all(skip=skip, limit=limit)
        logger.success(f"Retrieved {len(transports)} transport(s)")
        return transports
    except Exception as e:
        logger.error(f"Error retrieving transports: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving transports: {str(e)}"
        )


@transports_router.get("/type/{transport_type}", response_model=List[TransportResponse])
def get_transports_by_type(
    transport_type: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: TransportService = Depends(get_transport_service),
) -> List[TransportResponse]:
    """Get transports by type."""
    logger.info(f"GET /transports/type/{transport_type}")
    try:
        transports = service.get_by_type(transport_type, skip, limit)
        logger.success(f"Retrieved {len(transports)} transport(s)")
        return transports
    except Exception as e:
        logger.error(f"Error retrieving transports: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving transports: {str(e)}"
        )


@transports_router.get("/{transport_id}", response_model=TransportResponse)
def get_transport(
    transport_id: int,
    service: TransportService = Depends(get_transport_service),
) -> TransportResponse:
    """Get transport by ID."""
    logger.info(f"GET /transports/{transport_id}")
    try:
        transport = service.get_by_id(transport_id)
        logger.success(f"Transport found: id={transport_id}")
        return transport
    except NotFoundException as e:
        logger.warning(f"Transport not found: id={transport_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving transport: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving transport: {str(e)}"
        )


@transports_router.post("/", response_model=TransportResponse, status_code=status.HTTP_201_CREATED)
def create_transport(
    transport: TransportCreate,
    user_id: int = Query(..., description="User creating the transport"),
    service: TransportService = Depends(get_transport_service),
) -> TransportResponse:
    """Create a new transport."""
    logger.info(f"POST /transports - Creating: {transport.name}")
    try:
        created = service.create(transport, user_id=user_id)
        logger.success(f"Transport created: id={created.id}")
        return created
    except ValidationException as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating transport: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating transport: {str(e)}"
        )


@transports_router.put("/{transport_id}", response_model=TransportResponse)
def update_transport(
    transport_id: int,
    transport: TransportUpdate,
    user_id: int = Query(..., description="User updating the transport"),
    service: TransportService = Depends(get_transport_service),
) -> TransportResponse:
    """Update a transport."""
    logger.info(f"PUT /transports/{transport_id}")
    try:
        updated = service.update(transport_id, transport, user_id=user_id)
        logger.success(f"Transport updated: id={transport_id}")
        return updated
    except NotFoundException as e:
        logger.warning(f"Transport not found: id={transport_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationException as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating transport: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating transport: {str(e)}"
        )


@transports_router.delete("/{transport_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transport(
    transport_id: int,
    user_id: int = Query(..., description="User deleting the transport"),
    service: TransportService = Depends(get_transport_service),
) -> None:
    """Delete a transport (soft delete)."""
    logger.info(f"DELETE /transports/{transport_id}")
    try:
        service.delete(transport_id, user_id=user_id)
        logger.success(f"Transport deleted: id={transport_id}")
    except NotFoundException as e:
        logger.warning(f"Transport not found: id={transport_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting transport: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting transport: {str(e)}"
        )


# ============================================================================
# PAYMENT CONDITION ENDPOINTS
# ============================================================================

@payment_conditions_router.get("/", response_model=List[PaymentConditionResponse])
def get_payment_conditions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: PaymentConditionService = Depends(get_payment_condition_service),
) -> List[PaymentConditionResponse]:
    """Get all payment conditions with pagination."""
    logger.info(f"GET /payment-conditions - skip={skip}, limit={limit}")
    try:
        conditions = service.get_all(skip=skip, limit=limit)
        logger.success(f"Retrieved {len(conditions)} payment condition(s)")
        return conditions
    except Exception as e:
        logger.error(f"Error retrieving payment conditions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving payment conditions: {str(e)}"
        )


@payment_conditions_router.get("/default", response_model=PaymentConditionResponse)
def get_default_payment_condition(
    service: PaymentConditionService = Depends(get_payment_condition_service),
) -> PaymentConditionResponse:
    """Get default payment condition."""
    logger.info("GET /payment-conditions/default")
    try:
        condition = service.get_default()
        logger.success("Default payment condition retrieved")
        return condition
    except NotFoundException as e:
        logger.warning("No default payment condition found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving default payment condition: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving payment condition: {str(e)}"
        )


@payment_conditions_router.get("/number/{number}", response_model=PaymentConditionResponse)
def get_payment_condition_by_number(
    number: str,
    service: PaymentConditionService = Depends(get_payment_condition_service),
) -> PaymentConditionResponse:
    """Get payment condition by number."""
    logger.info(f"GET /payment-conditions/number/{number}")
    try:
        condition = service.get_by_number(number)
        logger.success(f"Payment condition found: {number}")
        return condition
    except NotFoundException as e:
        logger.warning(f"Payment condition not found: {number}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving payment condition: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving payment condition: {str(e)}"
        )


@payment_conditions_router.get("/{condition_id}", response_model=PaymentConditionResponse)
def get_payment_condition(
    condition_id: int,
    service: PaymentConditionService = Depends(get_payment_condition_service),
) -> PaymentConditionResponse:
    """Get payment condition by ID."""
    logger.info(f"GET /payment-conditions/{condition_id}")
    try:
        condition = service.get_by_id(condition_id)
        logger.success(f"Payment condition found: id={condition_id}")
        return condition
    except NotFoundException as e:
        logger.warning(f"Payment condition not found: id={condition_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving payment condition: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving payment condition: {str(e)}"
        )


@payment_conditions_router.post("/", response_model=PaymentConditionResponse, status_code=status.HTTP_201_CREATED)
def create_payment_condition(
    condition: PaymentConditionCreate,
    user_id: int = Query(..., description="User creating the payment condition"),
    service: PaymentConditionService = Depends(get_payment_condition_service),
) -> PaymentConditionResponse:
    """Create a new payment condition."""
    logger.info(f"POST /payment-conditions - Creating: {condition.payment_condition_number}")
    try:
        created = service.create(condition, user_id=user_id)
        logger.success(f"Payment condition created: id={created.id}")
        return created
    except ValidationException as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating payment condition: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating payment condition: {str(e)}"
        )


@payment_conditions_router.put("/{condition_id}", response_model=PaymentConditionResponse)
def update_payment_condition(
    condition_id: int,
    condition: PaymentConditionUpdate,
    user_id: int = Query(..., description="User updating the payment condition"),
    service: PaymentConditionService = Depends(get_payment_condition_service),
) -> PaymentConditionResponse:
    """Update a payment condition."""
    logger.info(f"PUT /payment-conditions/{condition_id}")
    try:
        updated = service.update(condition_id, condition, user_id=user_id)
        logger.success(f"Payment condition updated: id={condition_id}")
        return updated
    except NotFoundException as e:
        logger.warning(f"Payment condition not found: id={condition_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationException as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating payment condition: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating payment condition: {str(e)}"
        )


@payment_conditions_router.delete("/{condition_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment_condition(
    condition_id: int,
    user_id: int = Query(..., description="User deleting the payment condition"),
    service: PaymentConditionService = Depends(get_payment_condition_service),
) -> None:
    """Delete a payment condition (soft delete)."""
    logger.info(f"DELETE /payment-conditions/{condition_id}")
    try:
        service.delete(condition_id, user_id=user_id)
        logger.success(f"Payment condition deleted: id={condition_id}")
    except NotFoundException as e:
        logger.warning(f"Payment condition not found: id={condition_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting payment condition: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting payment condition: {str(e)}"
        )


# Include all sub-routers in main router
deliveries_router.include_router(delivery_orders_router)
deliveries_router.include_router(transports_router)
deliveries_router.include_router(payment_conditions_router)
