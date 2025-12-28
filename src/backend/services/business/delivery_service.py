"""
Service layer for Delivery business logic.

Handles delivery orders, transport, and payment conditions.
"""

from typing import List
from sqlalchemy.orm import Session
from datetime import date, datetime

from src.backend.models.business.delivery import DeliveryOrder, Transport, PaymentCondition
from src.backend.repositories.business.delivery_repository import (
    DeliveryOrderRepository,
    TransportRepository,
    PaymentConditionRepository,
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
from src.backend.services.base import BaseService
from src.backend.exceptions.service import ValidationException
from src.backend.exceptions.repository import NotFoundException
from src.backend.utils.logger import logger


class DeliveryOrderService(BaseService[DeliveryOrder, DeliveryOrderCreate, DeliveryOrderUpdate, DeliveryOrderResponse]):
    """
    Service for DeliveryOrder business logic.

    Example:
        service = DeliveryOrderService(repository, session)
        delivery = service.create(delivery_data, user_id=1)
        service.mark_delivered(delivery_id=123, signature_name="John", signature_id="12345678")
    """

    def __init__(
        self,
        repository: DeliveryOrderRepository,
        session: Session,
    ):
        """Initialize DeliveryOrderService."""
        super().__init__(
            repository=repository,
            session=session,
            model=DeliveryOrder,
            response_schema=DeliveryOrderResponse,
        )
        self.delivery_repo: DeliveryOrderRepository = repository

    def validate_create(self, entity: DeliveryOrder) -> None:
        """
        Validate delivery order before creation.

        Checks:
        - Delivery number is unique
        - Valid dates

        Args:
            entity: DeliveryOrder to validate

        Raises:
            ValidationException: If validation fails
        """
        logger.debug(f"Validating delivery order creation: number={entity.delivery_number}")

        # Validate unique delivery number
        existing = self.delivery_repo.get_by_delivery_number(entity.delivery_number)
        if existing:
            raise ValidationException(
                f"Delivery number already exists: {entity.delivery_number}",
                details={"delivery_number": entity.delivery_number}
            )

        # Validate actual delivery date not before planned date
        if entity.actual_delivery_date and entity.actual_delivery_date < entity.delivery_date:
            raise ValidationException(
                "Actual delivery date cannot be before planned delivery date",
                details={
                    "delivery_date": str(entity.delivery_date),
                    "actual_delivery_date": str(entity.actual_delivery_date)
                }
            )

        logger.debug("Delivery order validation passed")

    def validate_update(self, entity: DeliveryOrder) -> None:
        """
        Validate delivery order before update.

        Args:
            entity: DeliveryOrder to validate

        Raises:
            ValidationException: If validation fails
        """
        logger.debug(f"Validating delivery order update: id={entity.id}")

        # Validate unique delivery number (excluding self)
        existing = self.delivery_repo.get_by_delivery_number(entity.delivery_number)
        if existing and existing.id != entity.id:
            raise ValidationException(
                f"Delivery number already exists: {entity.delivery_number}",
                details={"delivery_number": entity.delivery_number}
            )

        # Validate dates
        if entity.actual_delivery_date and entity.actual_delivery_date < entity.delivery_date:
            raise ValidationException(
                "Actual delivery date cannot be before planned delivery date",
                details={
                    "delivery_date": str(entity.delivery_date),
                    "actual_delivery_date": str(entity.actual_delivery_date)
                }
            )

        logger.debug("Delivery order validation passed")

    def get_by_delivery_number(self, delivery_number: str) -> DeliveryOrderResponse:
        """Get delivery order by number."""
        logger.info(f"Getting delivery order by number: {delivery_number}")
        delivery = self.delivery_repo.get_by_delivery_number(delivery_number)
        if not delivery:
            raise NotFoundException(
                f"Delivery order not found: {delivery_number}",
                details={"delivery_number": delivery_number}
            )
        return self.response_schema.model_validate(delivery)

    def get_by_company(
        self,
        company_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[DeliveryOrderListResponse]:
        """Get delivery orders by company."""
        logger.info(f"Getting delivery orders for company_id={company_id}")
        deliveries = self.delivery_repo.get_by_company(company_id, skip, limit)
        return [DeliveryOrderListResponse.model_validate(d) for d in deliveries]

    def get_by_status(
        self,
        status: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[DeliveryOrderListResponse]:
        """Get delivery orders by status."""
        logger.info(f"Getting delivery orders with status={status}")
        deliveries = self.delivery_repo.get_by_status(status, skip, limit)
        return [DeliveryOrderListResponse.model_validate(d) for d in deliveries]

    def mark_delivered(
        self,
        delivery_id: int,
        signature_name: str,
        signature_id: str,
        notes: str = None,
        user_id: int = None,
    ) -> DeliveryOrderResponse:
        """
        Mark delivery as completed with signature.

        Args:
            delivery_id: Delivery order ID
            signature_name: Name of person receiving delivery
            signature_id: ID of person receiving delivery
            notes: Optional delivery notes
            user_id: User marking delivery

        Returns:
            Updated delivery order

        Raises:
            NotFoundException: If delivery not found
        """
        logger.info(f"Marking delivery id={delivery_id} as delivered")

        if user_id:
            self.session.info["user_id"] = user_id

        delivery = self.delivery_repo.get_by_id(delivery_id)
        if not delivery:
            raise NotFoundException(
                f"Delivery order not found: id={delivery_id}",
                details={"id": delivery_id}
            )

        # Use model method to mark delivered
        delivery.mark_delivered(signature_name, signature_id, notes)

        # Save
        updated = self.delivery_repo.update(delivery)

        logger.success(f"Delivery marked as delivered: id={delivery_id}")
        return self.response_schema.model_validate(updated)


class TransportService(BaseService[Transport, TransportCreate, TransportUpdate, TransportResponse]):
    """
    Service for Transport business logic.

    Example:
        service = TransportService(repository, session)
        transport = service.create(transport_data, user_id=1)
    """

    def __init__(
        self,
        repository: TransportRepository,
        session: Session,
    ):
        """Initialize TransportService."""
        super().__init__(
            repository=repository,
            session=session,
            model=Transport,
            response_schema=TransportResponse,
        )
        self.transport_repo: TransportRepository = repository

    def validate_create(self, entity: Transport) -> None:
        """Validate transport before creation."""
        logger.debug(f"Validating transport creation: name={entity.name}")

        # Validate unique name
        existing = self.transport_repo.get_by_name(entity.name)
        if existing:
            raise ValidationException(
                f"Transport name already exists: {entity.name}",
                details={"name": entity.name}
            )

        logger.debug("Transport validation passed")

    def validate_update(self, entity: Transport) -> None:
        """Validate transport before update."""
        logger.debug(f"Validating transport update: id={entity.id}")

        # Validate unique name (excluding self)
        existing = self.transport_repo.get_by_name(entity.name)
        if existing and existing.id != entity.id:
            raise ValidationException(
                f"Transport name already exists: {entity.name}",
                details={"name": entity.name}
            )

        logger.debug("Transport validation passed")

    def get_by_type(
        self,
        transport_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[TransportResponse]:
        """Get transports by type."""
        logger.info(f"Getting transports with type={transport_type}")
        transports = self.transport_repo.get_by_type(transport_type, skip, limit)
        return [TransportResponse.model_validate(t) for t in transports]


class PaymentConditionService(BaseService[PaymentCondition, PaymentConditionCreate, PaymentConditionUpdate, PaymentConditionResponse]):
    """
    Service for PaymentCondition business logic.

    Example:
        service = PaymentConditionService(repository, session)
        condition = service.create(condition_data, user_id=1)
    """

    def __init__(
        self,
        repository: PaymentConditionRepository,
        session: Session,
    ):
        """Initialize PaymentConditionService."""
        super().__init__(
            repository=repository,
            session=session,
            model=PaymentCondition,
            response_schema=PaymentConditionResponse,
        )
        self.payment_repo: PaymentConditionRepository = repository

    def validate_create(self, entity: PaymentCondition) -> None:
        """Validate payment condition before creation."""
        logger.debug(f"Validating payment condition creation: number={entity.payment_condition_number}")

        # Validate unique number
        existing = self.payment_repo.get_by_number(entity.payment_condition_number)
        if existing:
            raise ValidationException(
                f"Payment condition number already exists: {entity.payment_condition_number}",
                details={"payment_condition_number": entity.payment_condition_number}
            )

        # Validate percentages sum to 100
        entity.validate_percentages()

        logger.debug("Payment condition validation passed")

    def validate_update(self, entity: PaymentCondition) -> None:
        """Validate payment condition before update."""
        logger.debug(f"Validating payment condition update: id={entity.id}")

        # Validate unique number (excluding self)
        existing = self.payment_repo.get_by_number(entity.payment_condition_number)
        if existing and existing.id != entity.id:
            raise ValidationException(
                f"Payment condition number already exists: {entity.payment_condition_number}",
                details={"payment_condition_number": entity.payment_condition_number}
            )

        # Validate percentages sum to 100
        entity.validate_percentages()

        logger.debug("Payment condition validation passed")

    def get_by_number(self, number: str) -> PaymentConditionResponse:
        """Get payment condition by number."""
        logger.info(f"Getting payment condition by number: {number}")
        condition = self.payment_repo.get_by_number(number)
        if not condition:
            raise NotFoundException(
                f"Payment condition not found: {number}",
                details={"payment_condition_number": number}
            )
        return self.response_schema.model_validate(condition)

    def get_default(self) -> PaymentConditionResponse:
        """Get default payment condition."""
        logger.info("Getting default payment condition")
        condition = self.payment_repo.get_default()
        if not condition:
            raise NotFoundException(
                "No default payment condition configured",
                details={}
            )
        return self.response_schema.model_validate(condition)
