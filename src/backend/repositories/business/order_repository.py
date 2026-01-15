"""
Repository for Order model.

Handles data access for orders with custom query methods including
order number lookups, company filtering, and status tracking.
"""

from typing import Optional, List
from datetime import date
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import and_, or_

from src.backend.models.business.orders import Order, OrderProduct
from src.backend.repositories.base import BaseRepository
from src.backend.utils.logger import logger


class OrderRepository(BaseRepository[Order]):
    """
    Repository for Order with custom query methods.

    Manages purchase and sales orders with status tracking,
    payment tracking, and delivery management.

    Example:
        repository = OrderRepository(session)
        order = repository.get_by_order_number("O-2025-001")
        orders = repository.get_by_company(company_id=5)
    """

    def __init__(self, session: Session):
        """
        Initialize OrderRepository.

        Args:
            session: SQLAlchemy session for database operations
        """
        super().__init__(session, Order)

    def get_by_order_number(self, order_number: str) -> Optional[Order]:
        """
        Get order by unique order number.

        Args:
            order_number: Order number (e.g., "O-2025-001")

        Returns:
            Order if found, None otherwise
        """
        logger.debug(f"Searching order by number: {order_number}")
        order = (
            self.session.query(Order)
            .filter(Order.order_number == order_number.upper())
            .first()
        )
        if order:
            logger.debug(f"Order found: {order_number}")
        else:
            logger.debug(f"Order not found: {order_number}")
        return order

    def get_with_products(self, order_id: int) -> Optional[Order]:
        """
        Get order with products eagerly loaded.

        Uses eager loading to fetch order and all related products
        in a single query, avoiding N+1 query problems.

        Args:
            order_id: Order ID

        Returns:
            Order with products loaded, None if not found
        """
        logger.debug(f"Getting order id={order_id} with products (eager loading)")
        order = (
            self.session.query(Order)
            .options(
                selectinload(Order.products).selectinload(OrderProduct.product),
                selectinload(Order.contact),
                selectinload(Order.company_rut),
                selectinload(Order.plant),
                selectinload(Order.staff),
                selectinload(Order.incoterm),
                selectinload(Order.quote)  # Cargar cotización origen
            )
            .filter(Order.id == order_id)
            .first()
        )
        if order:
            logger.debug(f"Order found with {len(order.products)} product(s)")
        else:
            logger.debug(f"Order not found: id={order_id}")
        return order

    def get_by_company(
        self,
        company_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        """
        Get all orders for a specific company.

        Args:
            company_id: Company ID
            skip: Pagination offset
            limit: Maximum records

        Returns:
            List of orders for the company
        """
        logger.debug(f"Getting orders for company_id={company_id}")
        orders = (
            self.session.query(Order)
            .filter(Order.company_id == company_id)
            .order_by(Order.order_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        logger.debug(f"Found {len(orders)} order(s) for company_id={company_id}")
        return orders

    def get_by_status(
        self,
        status_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        """Get orders by status."""
        logger.debug(f"Getting orders with status_id={status_id}")
        orders = (
            self.session.query(Order)
            .filter(Order.status_id == status_id)
            .order_by(Order.order_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        logger.debug(f"Found {len(orders)} order(s) with status_id={status_id}")
        return orders

    def get_by_payment_status(
        self,
        payment_status_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        """Get orders by payment status."""
        logger.debug(f"Getting orders with payment_status_id={payment_status_id}")
        orders = (
            self.session.query(Order)
            .filter(Order.payment_status_id == payment_status_id)
            .order_by(Order.order_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        logger.debug(f"Found {len(orders)} order(s) with payment_status_id={payment_status_id}")
        return orders

    def get_by_staff(
        self,
        staff_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        """Get orders assigned to staff member."""
        logger.debug(f"Getting orders for staff_id={staff_id}")
        orders = (
            self.session.query(Order)
            .filter(Order.staff_id == staff_id)
            .order_by(Order.order_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        logger.debug(f"Found {len(orders)} order(s) for staff_id={staff_id}")
        return orders

    def get_by_quote(self, quote_id: int) -> Optional[Order]:
        """Get order created from a specific quote."""
        logger.debug(f"Getting order for quote_id={quote_id}")
        order = (
            self.session.query(Order)
            .filter(Order.quote_id == quote_id)
            .first()
        )
        if order:
            logger.debug(f"Order found for quote_id={quote_id}")
        else:
            logger.debug(f"No order found for quote_id={quote_id}")
        return order

    def get_overdue_orders(self, skip: int = 0, limit: int = 100) -> List[Order]:
        """Get orders that are overdue (promised date passed, not completed)."""
        logger.debug("Getting overdue orders")
        orders = (
            self.session.query(Order)
            .filter(
                and_(
                    Order.promised_date.isnot(None),
                    Order.promised_date < date.today(),
                    Order.completed_date.is_(None)
                )
            )
            .order_by(Order.promised_date)
            .offset(skip)
            .limit(limit)
            .all()
        )
        logger.debug(f"Found {len(orders)} overdue order(s)")
        return orders

    def get_by_order_type(
        self,
        order_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        """Get orders by type (sales or purchase)."""
        logger.debug(f"Getting orders with order_type={order_type}")
        orders = (
            self.session.query(Order)
            .filter(Order.order_type == order_type)
            .order_by(Order.order_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        logger.debug(f"Found {len(orders)} {order_type} order(s)")
        return orders

    def get_export_orders(self, skip: int = 0, limit: int = 100) -> List[Order]:
        """Get export orders only."""
        logger.debug("Getting export orders")
        orders = (
            self.session.query(Order)
            .filter(Order.is_export == True)
            .order_by(Order.order_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        logger.debug(f"Found {len(orders)} export order(s)")
        return orders

    def search_by_project(
        self,
        project_number: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        """Search orders by project number."""
        logger.debug(f"Searching orders by project_number: '{project_number}'")
        search_pattern = f"%{project_number}%"
        orders = (
            self.session.query(Order)
            .filter(Order.project_number.ilike(search_pattern))
            .order_by(Order.order_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        logger.debug(f"Found {len(orders)} order(s) matching project_number")
        return orders


class OrderProductRepository(BaseRepository[OrderProduct]):
    """
    Repository for OrderProduct (order line items).

    Manages individual line items within orders including quantities,
    pricing, and discounts.
    """

    def __init__(self, session: Session):
        """Initialize OrderProductRepository."""
        super().__init__(session, OrderProduct)

    def get_by_order(self, order_id: int) -> List[OrderProduct]:
        """
        Get all products for a specific order.

        Returns products ordered by sequence number.
        """
        logger.debug(f"Getting products for order_id={order_id}")
        products = (
            self.session.query(OrderProduct)
            .filter(OrderProduct.order_id == order_id)
            .order_by(OrderProduct.sequence)
            .all()
        )
        logger.debug(f"Found {len(products)} product(s) for order_id={order_id}")
        return products

    def get_by_product(
        self,
        product_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[OrderProduct]:
        """Get all order line items containing a specific product."""
        logger.debug(f"Getting order products for product_id={product_id}")
        products = (
            self.session.query(OrderProduct)
            .filter(OrderProduct.product_id == product_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        logger.debug(f"Found {len(products)} order product(s) for product_id={product_id}")
        return products

    def delete_by_order(self, order_id: int) -> int:
        """Delete all products for a specific order."""
        logger.debug(f"Deleting all products for order_id={order_id}")
        count = (
            self.session.query(OrderProduct)
            .filter(OrderProduct.order_id == order_id)
            .delete()
        )
        self.session.flush()
        logger.warning(f"Deleted {count} product(s) for order_id={order_id}")
        return count

