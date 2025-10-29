"""
Service layer for Order business logic.

Handles order operations including validation, calculations,
conversions from quotes, and status management.
"""

from typing import List, Optional
from decimal import Decimal
from datetime import date
from sqlalchemy.orm import Session

from src.backend.models.business.orders import Order
from src.backend.repositories.business.order_repository import OrderRepository
from src.backend.repositories.business.quote_repository import QuoteRepository
from src.shared.schemas.business.order import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderListResponse,
)
from src.backend.services.base import BaseService
from src.backend.exceptions.service import ValidationException
from src.backend.exceptions.repository import NotFoundException
from src.backend.utils.logger import logger


class OrderService(BaseService[Order, OrderCreate, OrderUpdate, OrderResponse]):
    """
    Service for Order business logic.

    Handles order operations, validations, conversions from quotes,
    and total calculations.

    Example:
        service = OrderService(repository, session)
        order = service.create(order_data, user_id=1)
        order = service.create_from_quote(quote_id=5, user_id=1)
        service.calculate_totals(order_id=10)
    """

    def __init__(
        self,
        repository: OrderRepository,
        session: Session,
    ):
        """
        Initialize OrderService.

        Args:
            repository: OrderRepository instance
            session: SQLAlchemy session
        """
        super().__init__(
            repository=repository,
            session=session,
            model=Order,
            response_schema=OrderResponse,
        )
        self.order_repo: OrderRepository = repository
        self.quote_repo = QuoteRepository(session)

    def validate_create(self, entity: Order) -> None:
        """
        Validate order before creation.

        Checks:
        - Order number is unique
        - Valid date ranges
        - Promised date not before order date

        Args:
            entity: Order to validate

        Raises:
            ValidationException: If validation fails
        """
        logger.debug(f"Validating order creation: number={entity.order_number}")

        # Validate unique order number
        existing = self.order_repo.get_by_order_number(entity.order_number)
        if existing:
            raise ValidationException(
                f"Order number already exists: {entity.order_number}",
                details={"order_number": entity.order_number}
            )

        # Validate promised date not before order date
        if entity.promised_date and entity.promised_date < entity.order_date:
            raise ValidationException(
                "Promised date cannot be before order date",
                details={
                    "order_date": str(entity.order_date),
                    "promised_date": str(entity.promised_date)
                }
            )

        # Validate completed date not before order date
        if entity.completed_date and entity.completed_date < entity.order_date:
            raise ValidationException(
                "Completed date cannot be before order date",
                details={
                    "order_date": str(entity.order_date),
                    "completed_date": str(entity.completed_date)
                }
            )

        logger.debug("Order validation passed")

    def validate_update(self, entity: Order) -> None:
        """
        Validate order before update.

        Checks:
        - Order number unique (excluding self)
        - Valid date ranges

        Args:
            entity: Order to validate

        Raises:
            ValidationException: If validation fails
        """
        logger.debug(f"Validating order update: id={entity.id}")

        # Validate unique order number (excluding self)
        existing = self.order_repo.get_by_order_number(entity.order_number)
        if existing and existing.id != entity.id:
            raise ValidationException(
                f"Order number already exists: {entity.order_number}",
                details={"order_number": entity.order_number}
            )

        # Validate promised date not before order date
        if entity.promised_date and entity.promised_date < entity.order_date:
            raise ValidationException(
                "Promised date cannot be before order date",
                details={
                    "order_date": str(entity.order_date),
                    "promised_date": str(entity.promised_date)
                }
            )

        # Validate completed date not before order date
        if entity.completed_date and entity.completed_date < entity.order_date:
            raise ValidationException(
                "Completed date cannot be before order date",
                details={
                    "order_date": str(entity.order_date),
                    "completed_date": str(entity.completed_date)
                }
            )

        logger.debug("Order validation passed")

    def get_by_order_number(self, order_number: str) -> OrderResponse:
        """
        Get order by unique order number.

        Args:
            order_number: Order number (e.g., "O-2025-001")

        Returns:
            Order data

        Raises:
            NotFoundException: If order not found

        Example:
            order = service.get_by_order_number("O-2025-001")
        """
        logger.info(f"Getting order by number: {order_number}")
        order = self.order_repo.get_by_order_number(order_number)
        if not order:
            raise NotFoundException(
                f"Order not found: {order_number}",
                details={"order_number": order_number}
            )
        return self.response_schema.model_validate(order)

    def get_by_company(
        self,
        company_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[OrderListResponse]:
        """
        Get all orders for a company.

        Args:
            company_id: Company ID
            skip: Pagination offset
            limit: Maximum records

        Returns:
            List of orders

        Example:
            orders = service.get_by_company(company_id=5, skip=0, limit=10)
        """
        logger.info(f"Getting orders for company_id={company_id}")
        orders = self.order_repo.get_by_company(company_id, skip, limit)
        return [OrderListResponse.model_validate(o) for o in orders]

    def get_by_status(
        self,
        status_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[OrderListResponse]:
        """
        Get orders by status.

        Args:
            status_id: Order status ID
            skip: Pagination offset
            limit: Maximum records

        Returns:
            List of orders
        """
        logger.info(f"Getting orders with status_id={status_id}")
        orders = self.order_repo.get_by_status(status_id, skip, limit)
        return [OrderListResponse.model_validate(o) for o in orders]

    def get_by_staff(
        self,
        staff_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[OrderListResponse]:
        """
        Get orders assigned to staff member.

        Args:
            staff_id: Staff ID
            skip: Pagination offset
            limit: Maximum records

        Returns:
            List of orders
        """
        logger.info(f"Getting orders for staff_id={staff_id}")
        orders = self.order_repo.get_by_staff(staff_id, skip, limit)
        return [OrderListResponse.model_validate(o) for o in orders]

    def calculate_totals(self, order_id: int, user_id: int) -> OrderResponse:
        """
        Recalculate order totals.

        Calculates:
        - Subtotal (sum of all line items - would need OrderProduct model)
        - Tax amount (subtotal * tax_percentage)
        - Total (subtotal + tax)

        Note: Currently calculates from existing values.
        Full implementation requires OrderProduct model.

        Args:
            order_id: Order ID
            user_id: User performing calculation

        Returns:
            Updated order

        Raises:
            NotFoundException: If order not found

        Example:
            order = service.calculate_totals(order_id=123, user_id=1)
        """
        logger.info(f"Calculating totals for order_id={order_id}")

        self.session.info["user_id"] = user_id

        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise NotFoundException(
                f"Order not found: id={order_id}",
                details={"id": order_id}
            )

        # Calculate totals (using existing model method)
        order.calculate_totals()

        # Save
        self.order_repo.update(order)

        logger.success(f"Totals calculated for order_id={order_id}: total={order.total}")
        return self.response_schema.model_validate(order)

    def create_from_quote(
        self,
        quote_id: int,
        user_id: int,
        order_number: Optional[str] = None,
        status_id: Optional[int] = None,
        payment_status_id: Optional[int] = None,
    ) -> OrderResponse:
        """
        Create order from an accepted quote.

        Copies quote data to new order including:
        - Company, contact, branch, staff
        - Currency and exchange rate
        - Tax percentage and financial amounts
        - Shipping information
        - Notes

        Args:
            quote_id: Quote ID to convert
            user_id: User creating order
            order_number: Custom order number (auto-generated if not provided)
            status_id: Initial order status (required)
            payment_status_id: Initial payment status (required)

        Returns:
            Created order

        Raises:
            NotFoundException: If quote not found
            ValidationException: If quote cannot be converted

        Example:
            order = service.create_from_quote(
                quote_id=123,
                user_id=1,
                order_number="O-2025-001",
                status_id=1,
                payment_status_id=1
            )
        """
        logger.info(f"Creating order from quote_id={quote_id}")

        self.session.info["user_id"] = user_id

        # Get quote
        quote = self.quote_repo.get_with_products(quote_id)
        if not quote:
            raise NotFoundException(
                f"Quote not found: id={quote_id}",
                details={"id": quote_id}
            )

        # Validate required parameters
        if not status_id:
            raise ValidationException(
                "status_id is required when creating order from quote",
                details={"quote_id": quote_id}
            )

        if not payment_status_id:
            raise ValidationException(
                "payment_status_id is required when creating order from quote",
                details={"quote_id": quote_id}
            )

        # Generate order number if not provided
        if not order_number:
            # Simple auto-generation (could be enhanced with sequence)
            order_number = f"O-{date.today().year}-{quote_id:04d}"

        # Create order from quote data
        order = Order(
            order_number=order_number,
            revision="A",
            order_type="sales",  # Default to sales order
            quote_id=quote_id,
            company_id=quote.company_id,
            contact_id=quote.contact_id,
            branch_id=quote.branch_id,
            staff_id=quote.staff_id,
            status_id=status_id,
            payment_status_id=payment_status_id,
            order_date=date.today(),
            promised_date=quote.shipping_date,  # Use quote shipping date as promised date
            incoterm_id=quote.incoterm_id,
            currency_id=quote.currency_id,
            exchange_rate=quote.exchange_rate,
            subtotal=quote.subtotal,
            tax_percentage=quote.tax_percentage,
            tax_amount=quote.tax_amount,
            total=quote.total,
            notes=quote.notes,
            internal_notes=quote.internal_notes,
            is_active=True,
        )

        # Validate and create
        created = self.create(
            OrderCreate.model_validate(order.__dict__),
            user_id=user_id
        )

        logger.success(f"Order created from quote_id={quote_id}: order_id={created.id}")
        return created
