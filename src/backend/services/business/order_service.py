"""
Service layer for Order business logic.

Handles order operations including validation, calculations,
conversions from quotes, and status management.
"""


from decimal import Decimal
from datetime import date
from sqlalchemy.orm import Session

from src.backend.models.business.orders import Order, OrderProduct
from src.backend.repositories.business.order_repository import OrderRepository, OrderProductRepository
from src.backend.repositories.business.quote_repository import QuoteRepository
from src.shared.schemas.business.order import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderListResponse,
    OrderProductCreate,
    OrderProductUpdate,
    OrderProductResponse,
)
from src.backend.services.base import BaseService
from src.backend.exceptions.service import ValidationException
from src.backend.exceptions.repository import NotFoundException
from src.backend.utils.logger import logger
from src.backend.services.core.sequence_service import SequenceService
from src.backend.config.settings import settings
from src.backend.models.business.quotes import Quote
from src.backend.models.core.companies import Company


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
        self.order_product_repo = OrderProductRepository(session)
        self.sequence_service = SequenceService(session)

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

    def get_with_products(self, order_id: int) -> OrderResponse:
        """
        Get order with all products loaded.

        Args:
            order_id: Order ID

        Returns:
            Order with products

        Raises:
            NotFoundException: If order not found
        """
        logger.info(f"Getting order id={order_id} with products")
        order = self.order_repo.get_with_products(order_id)
        if not order:
            raise NotFoundException(
                f"Order not found: id={order_id}",
                details={"id": order_id}
            )
        return self.response_schema.model_validate(order)

    def get_by_company(
        self,
        company_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> list[OrderListResponse]:
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
    ) -> list[OrderListResponse]:
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
    ) -> list[OrderListResponse]:
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
        Recalculate order totals from products.

        Calculates:
        - Subtotal (sum of all line items)
        - Tax amount (subtotal * tax_percentage)
        - Total (subtotal + tax + shipping + other costs)

        Args:
            order_id: Order ID
            user_id: User performing calculation

        Returns:
            Updated order

        Raises:
            NotFoundException: If order not found
        """
        logger.info(f"Calculating totals for order_id={order_id}")

        self.session.info["user_id"] = user_id

        order = self.order_repo.get_with_products(order_id)
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

    def add_product(
        self,
        order_id: int,
        product_data: OrderProductCreate,
        user_id: int
    ) -> OrderProductResponse:
        """
        Add product to order.

        Automatically calculates line item subtotal and recalculates order totals.

        Args:
            order_id: Order ID
            product_data: Product data
            user_id: User adding product

        Returns:
            Created order product
        """
        logger.info(f"Adding product to order_id={order_id}")

        self.session.info["user_id"] = user_id

        # Verify order exists
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise NotFoundException(
                f"Order not found: id={order_id}",
                details={"id": order_id}
            )

        # Create order product
        order_product = OrderProduct(
            order_id=order_id,
            **product_data.model_dump()
        )

        # Calculate subtotal
        order_product.calculate_subtotal()

        # Save product
        created = self.order_product_repo.create(order_product)

        # Recalculate order totals
        self.calculate_totals(order_id, user_id)

        logger.success(f"Product added to order_id={order_id}: product_id={created.product_id}")
        return OrderProductResponse.model_validate(created)

    def update_product(
        self,
        order_id: int,
        product_id: int,
        product_data: OrderProductUpdate,
        user_id: int
    ) -> OrderProductResponse:
        """
        Update order product.

        Args:
            order_id: Order ID
            product_id: Order product ID
            product_data: Update data
            user_id: User updating product

        Returns:
            Updated order product
        """
        logger.info(f"Updating product {product_id} in order_id={order_id}")

        self.session.info["user_id"] = user_id

        # Get existing product
        order_product = self.order_product_repo.get_by_id(product_id)
        if not order_product or order_product.order_id != order_id:
            raise NotFoundException(
                f"Order product not found: id={product_id}",
                details={"id": product_id, "order_id": order_id}
            )

        # Update fields
        update_data = product_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(order_product, field, value)

        # Recalculate subtotal
        order_product.calculate_subtotal()

        # Save
        updated = self.order_product_repo.update(order_product)

        # Recalculate order totals
        self.calculate_totals(order_id, user_id)

        logger.success(f"Product updated in order_id={order_id}: product_id={product_id}")
        return OrderProductResponse.model_validate(updated)

    def remove_product(
        self,
        order_id: int,
        product_id: int,
        user_id: int
    ) -> None:
        """
        Remove product from order.

        Args:
            order_id: Order ID
            product_id: Order product ID
            user_id: User removing product
        """
        logger.info(f"Removing product {product_id} from order_id={order_id}")

        self.session.info["user_id"] = user_id

        # Get existing product
        order_product = self.order_product_repo.get_by_id(product_id)
        if not order_product or order_product.order_id != order_id:
            raise NotFoundException(
                f"Order product not found: id={product_id}",
                details={"id": product_id, "order_id": order_id}
            )

        # Delete
        self.order_product_repo.delete(product_id)

        # Recalculate order totals
        self.calculate_totals(order_id, user_id)

        logger.success(f"Product removed from order_id={order_id}: product_id={product_id}")

    def create(self, schema: OrderCreate, user_id: int) -> OrderResponse:
        """
        Create a new order.
        """
        logger.info(f"Servicio: creando {self.model.__name__}")

        try:
            self.session.info["user_id"] = user_id

            entity_data = schema.model_dump(exclude={"products"})
            
            # Generate order number if not provided or empty
            if not entity_data.get("order_number") or entity_data.get("order_number") == "STRING":
                # Fetch company to get trigram
                company = self.session.query(Company).filter(Company.id == entity_data.get("company_id")).first()
                company_trigram = company.trigram if company else None

                entity_data["order_number"] = self.sequence_service.generate_document_number(
                    prefix="OC",
                    company_trigram=company_trigram,
                    padding=2
                )

            entity = self.model(**entity_data)

            # Validate
            self.validate_create(entity)

            # Save
            created = self.repository.create(entity)

            # Add products if provided
            if schema.products:
                for product_data in schema.products:
                    self.add_product(created.id, product_data, user_id)
                # Reload to get updated totals
                created = self.order_repo.get_with_products(created.id)

            logger.success(f"{self.model.__name__} creado exitosamente: id={created.id}")
            return self.response_schema.model_validate(created)

        except Exception as e:
            logger.error(f"Error al crear {self.model.__name__}: {str(e)}")
            raise

    def create_from_quote(
        self,
        quote_id: int,
        user_id: int,
        order_number: str | None = None,
        status_id: int | None = None,
        payment_status_id: int | None = None,
    ) -> OrderResponse:
        """
        Create order from an accepted quote.

        Copies quote data to new order including:
        - Company, contact, plant, staff
        - Currency and exchange rate
        - Tax percentage and financial amounts
        - Shipping information
        - Notes
        - All products from the quote

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
        """
        logger.info(f"Creating order from quote_id={quote_id}")

        self.session.info["user_id"] = user_id

        # Get quote with products
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
            company = self.session.query(Company).filter(Company.id == quote.company_id).first()
            company_trigram = company.trigram if company else None
            order_number = self.sequence_service.generate_document_number(
                prefix="OC",
                company_trigram=company_trigram,
                padding=2
            )

        # Create order from quote data
        order = Order(
            order_number=order_number,
            revision="A",
            order_type="sales",  # Default to sales order
            quote_id=quote_id,
            company_id=quote.company_id,
            company_rut_id=quote.company_rut_id,
            contact_id=quote.contact_id,
            plant_id=quote.plant_id,
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

        # Validate
        self.validate_create(order)

        # Save order
        created_order = self.repository.create(order)

        # Copy products from quote to order
        for quote_product in quote.products:
            order_product = OrderProduct(
                order_id=created_order.id,
                product_id=quote_product.product_id,
                sequence=quote_product.sequence,
                quantity=quote_product.quantity,
                unit_price=quote_product.unit_price,
                discount_percentage=quote_product.discount_percentage,
                discount_amount=quote_product.discount_amount,
                subtotal=quote_product.subtotal,
                notes=quote_product.notes,
            )
            self.order_product_repo.create(order_product)

        # Reload to get products
        created_order = self.order_repo.get_with_products(created_order.id)

        logger.success(f"Order created from quote_id={quote_id}: order_id={created_order.id} with {len(quote.products)} products")
        return self.response_schema.model_validate(created_order)

