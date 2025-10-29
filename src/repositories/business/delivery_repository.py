"""
Repositories for Delivery models.

Handles data access for DeliveryOrder, DeliveryDate, Transport, and PaymentCondition.
"""

from typing import Optional, List
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.models.business.delivery import DeliveryOrder, DeliveryDate, Transport, PaymentCondition
from src.repositories.base import BaseRepository
from src.utils.logger import logger


class DeliveryOrderRepository(BaseRepository[DeliveryOrder]):
    """
    Repository for DeliveryOrder.

    Manages delivery orders with status tracking and date management.

    Example:
        repository = DeliveryOrderRepository(session)
        delivery = repository.get_by_delivery_number("GD-2025-001")
        deliveries = repository.get_by_company(company_id=5)
    """

    def __init__(self, session: Session):
        """
        Initialize DeliveryOrderRepository.

        Args:
            session: SQLAlchemy session for database operations
        """
        super().__init__(session, DeliveryOrder)

    def get_by_delivery_number(self, delivery_number: str) -> Optional[DeliveryOrder]:
        """
        Get delivery order by unique delivery number.

        Args:
            delivery_number: Delivery number (e.g., "GD-2025-001")

        Returns:
            DeliveryOrder if found, None otherwise
        """
        logger.debug(f"Searching delivery order by number: {delivery_number}")
        delivery = (
            self.session.query(DeliveryOrder)
            .filter(DeliveryOrder.delivery_number == delivery_number.upper())
            .first()
        )
        if delivery:
            logger.debug(f"Delivery order found: {delivery_number}")
        else:
            logger.debug(f"Delivery order not found: {delivery_number}")
        return delivery

    def get_by_order(self, order_id: int) -> List[DeliveryOrder]:
        """Get all delivery orders for an order."""
        logger.debug(f"Getting delivery orders for order_id={order_id}")
        deliveries = (
            self.session.query(DeliveryOrder)
            .filter(DeliveryOrder.order_id == order_id)
            .order_by(DeliveryOrder.delivery_date.desc())
            .all()
        )
        logger.debug(f"Found {len(deliveries)} delivery order(s)")
        return deliveries

    def get_by_company(
        self,
        company_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[DeliveryOrder]:
        """Get delivery orders by company."""
        logger.debug(f"Getting delivery orders for company_id={company_id}")
        deliveries = (
            self.session.query(DeliveryOrder)
            .filter(DeliveryOrder.company_id == company_id)
            .order_by(DeliveryOrder.delivery_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        logger.debug(f"Found {len(deliveries)} delivery order(s)")
        return deliveries

    def get_by_status(
        self,
        status: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[DeliveryOrder]:
        """Get delivery orders by status."""
        logger.debug(f"Getting delivery orders with status={status}")
        deliveries = (
            self.session.query(DeliveryOrder)
            .filter(DeliveryOrder.status == status)
            .order_by(DeliveryOrder.delivery_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        logger.debug(f"Found {len(deliveries)} delivery order(s)")
        return deliveries

    def get_pending_deliveries(self, skip: int = 0, limit: int = 100) -> List[DeliveryOrder]:
        """Get pending deliveries."""
        logger.debug("Getting pending deliveries")
        deliveries = (
            self.session.query(DeliveryOrder)
            .filter(DeliveryOrder.status.in_(["pending", "in_transit"]))
            .order_by(DeliveryOrder.delivery_date)
            .offset(skip)
            .limit(limit)
            .all()
        )
        logger.debug(f"Found {len(deliveries)} pending delivery order(s)")
        return deliveries


class DeliveryDateRepository(BaseRepository[DeliveryDate]):
    """
    Repository for DeliveryDate.

    Manages delivery dates for multi-part deliveries.
    """

    def __init__(self, session: Session):
        """Initialize DeliveryDateRepository."""
        super().__init__(session, DeliveryDate)

    def get_by_delivery_order(self, delivery_order_id: int) -> List[DeliveryDate]:
        """Get all delivery dates for a delivery order."""
        logger.debug(f"Getting delivery dates for delivery_order_id={delivery_order_id}")
        dates = (
            self.session.query(DeliveryDate)
            .filter(DeliveryDate.delivery_order_id == delivery_order_id)
            .order_by(DeliveryDate.planned_date)
            .all()
        )
        logger.debug(f"Found {len(dates)} delivery date(s)")
        return dates


class TransportRepository(BaseRepository[Transport]):
    """
    Repository for Transport/carrier information.

    Example:
        repository = TransportRepository(session)
        transport = repository.get_by_name("DHL")
        transports = repository.get_by_type("courier")
    """

    def __init__(self, session: Session):
        """Initialize TransportRepository."""
        super().__init__(session, Transport)

    def get_by_name(self, name: str) -> Optional[Transport]:
        """Get transport by name."""
        logger.debug(f"Searching transport by name: {name}")
        transport = (
            self.session.query(Transport)
            .filter(Transport.name == name)
            .first()
        )
        if transport:
            logger.debug(f"Transport found: {name}")
        else:
            logger.debug(f"Transport not found: {name}")
        return transport

    def get_by_type(
        self,
        transport_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Transport]:
        """Get transports by type."""
        logger.debug(f"Getting transports with type={transport_type}")
        transports = (
            self.session.query(Transport)
            .filter(Transport.transport_type == transport_type)
            .order_by(Transport.name)
            .offset(skip)
            .limit(limit)
            .all()
        )
        logger.debug(f"Found {len(transports)} transport(s)")
        return transports


class PaymentConditionRepository(BaseRepository[PaymentCondition]):
    """
    Repository for PaymentCondition.

    Manages payment terms and conditions.

    Example:
        repository = PaymentConditionRepository(session)
        condition = repository.get_by_code("NET30")
        default = repository.get_default()
    """

    def __init__(self, session: Session):
        """Initialize PaymentConditionRepository."""
        super().__init__(session, PaymentCondition)

    def get_by_code(self, code: str) -> Optional[PaymentCondition]:
        """Get payment condition by code."""
        logger.debug(f"Searching payment condition by code: {code}")
        condition = (
            self.session.query(PaymentCondition)
            .filter(PaymentCondition.code == code.upper())
            .first()
        )
        if condition:
            logger.debug(f"Payment condition found: {code}")
        else:
            logger.debug(f"Payment condition not found: {code}")
        return condition

    def get_default(self) -> Optional[PaymentCondition]:
        """Get default payment condition."""
        logger.debug("Getting default payment condition")
        condition = (
            self.session.query(PaymentCondition)
            .filter(PaymentCondition.is_default == True)
            .first()
        )
        if condition:
            logger.debug(f"Default payment condition found: {condition.code}")
        else:
            logger.debug("No default payment condition found")
        return condition
