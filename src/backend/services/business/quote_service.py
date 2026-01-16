"""
Service layer for Quote and QuoteProduct business logic.

Handles quote operations including validation, calculations,
and complex business rules.
"""


from decimal import Decimal
from sqlalchemy.orm import Session

from src.backend.models.business.quotes import Quote, QuoteProduct
from src.backend.repositories.business.quote_repository import QuoteRepository, QuoteProductRepository
from src.shared.schemas.business.quote import (
    QuoteCreate,
    QuoteUpdate,
    QuoteResponse,
    QuoteListResponse,
    QuoteProductCreate,
    QuoteProductUpdate,
    QuoteProductResponse,
)
from src.backend.services.base import BaseService
from src.backend.exceptions.service import ValidationException
from src.backend.exceptions.repository import NotFoundException
from src.backend.utils.logger import logger
from src.backend.services.core.sequence_service import SequenceService
from src.backend.models.core.companies import Company


class QuoteService(BaseService[Quote, QuoteCreate, QuoteUpdate, QuoteResponse]):
    """
    Service for Quote business logic.

    Handles quote operations, validations, line item management,
    and conversions to orders.

    Example:
        service = QuoteService(repository, session)
        quote = service.create(quote_data, user_id=1)
        service.add_product(quote.id, product_data, user_id=1)
        service.calculate_totals(quote.id)
    """

    def __init__(
        self,
        repository: QuoteRepository,
        session: Session,
    ):
        """
        Initialize QuoteService.

        Args:
            repository: QuoteRepository instance
            session: SQLAlchemy session
        """
        super().__init__(
            repository=repository,
            session=session,
            model=Quote,
            response_schema=QuoteResponse,
        )
        self.quote_repo: QuoteRepository = repository
        self.product_repo = QuoteProductRepository(session)
        self.sequence_service = SequenceService(session)

    def create(self, schema: QuoteCreate, user_id: int) -> QuoteResponse:
        """
        Create a new quote.
        
        Overridden to exclude 'products' from the entity creation, as they are
        handled separately and cannot be passed as dicts to the SQLAlchemy relationship.
        """
        logger.info(f"Servicio: creando {self.model.__name__}")

        try:
            self.session.info["user_id"] = user_id

            # Create entity from schema, excluding products
            # products must be handled separately (e.g. via add_product)
            # Generate quote number if not provided or empty
            entity_data = schema.model_dump(exclude={"products"})
            # Automatic numbering if not provided
            if not entity_data.get("quote_number") or entity_data.get("quote_number") == "STRING":
                # Fetch company to get trigram
                company = self.session.query(Company).filter(Company.id == schema.company_id).first()
                company_trigram = company.trigram if company else None
                
                quote_number = self.sequence_service.generate_document_number(
                    prefix="C",
                    company_trigram=company_trigram
                )
                entity_data["quote_number"] = quote_number

            entity = self.model(**entity_data)

            # Validate
            self.validate_create(entity)

            # Save
            created = self.repository.create(entity)

            logger.success(f"{self.model.__name__} creado exitosamente: id={created.id}")
            return self.response_schema.model_validate(created)

        except ValidationException:
            raise
        except Exception as e:
            logger.error(f"Error al crear {self.model.__name__}: {str(e)}")
            raise

    def validate_create(self, entity: Quote) -> None:
        """
        Validate quote before creation.

        Checks:
        - Quote number is unique
        - Valid date ranges

        Args:
            entity: Quote to validate

        Raises:
            ValidationException: If validation fails
        """
        logger.debug(f"Validating quote creation: number={entity.quote_number}")

        # Validate unique quote number
        existing = self.quote_repo.get_by_quote_number(entity.quote_number)
        if existing:
            raise ValidationException(
                f"Quote number already exists: {entity.quote_number}",
                details={"quote_number": entity.quote_number}
            )

        # Validate dates
        if entity.valid_until and entity.valid_until < entity.quote_date:
            raise ValidationException(
                "Valid until date cannot be before quote date",
                details={
                    "quote_date": str(entity.quote_date),
                    "valid_until": str(entity.valid_until)
                }
            )

        logger.debug("Quote validation passed")

    def validate_update(self, entity: Quote) -> None:
        """
        Validate quote before update.

        Checks:
        - Quote number unique (excluding self)
        - Valid date ranges

        Args:
            entity: Quote to validate

        Raises:
            ValidationException: If validation fails
        """
        logger.debug(f"Validating quote update: id={entity.id}")

        # Validate unique quote number (excluding self)
        existing = self.quote_repo.get_by_quote_number(entity.quote_number)
        if existing and existing.id != entity.id:
            raise ValidationException(
                f"Quote number already exists: {entity.quote_number}",
                details={"quote_number": entity.quote_number}
            )

        # Validate dates
        if entity.valid_until and entity.valid_until < entity.quote_date:
            raise ValidationException(
                "Valid until date cannot be before quote date",
                details={
                    "quote_date": str(entity.quote_date),
                    "valid_until": str(entity.valid_until)
                }
            )

        logger.debug("Quote validation passed")

    def get_by_quote_number(self, quote_number: str) -> QuoteResponse:
        """
        Get quote by unique quote number.

        Args:
            quote_number: Quote number (e.g., "Q-2025-001")

        Returns:
            Quote data

        Raises:
            NotFoundException: If quote not found

        Example:
            quote = service.get_by_quote_number("Q-2025-001")
        """
        logger.info(f"Getting quote by number: {quote_number}")
        quote = self.quote_repo.get_by_quote_number(quote_number)
        if not quote:
            raise NotFoundException(
                f"Quote not found: {quote_number}",
                details={"quote_number": quote_number}
            )
        return self.response_schema.model_validate(quote)

    def get_with_products(self, quote_id: int) -> QuoteResponse:
        """
        Get quote with all products loaded.

        Args:
            quote_id: Quote ID

        Returns:
            Quote with products

        Raises:
            NotFoundException: If quote not found

        Example:
            quote = service.get_with_products(123)
            print(f"Quote has {len(quote.products)} products")
        """
        logger.info(f"Getting quote id={quote_id} with products")
        quote = self.quote_repo.get_with_products(quote_id)
        if not quote:
            raise NotFoundException(
                f"Quote not found: id={quote_id}",
                details={"id": quote_id}
            )
        return self.response_schema.model_validate(quote)

    def get_by_company(
        self,
        company_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> list[QuoteListResponse]:
        """
        Get all quotes for a company.

        Args:
            company_id: Company ID
            skip: Pagination offset
            limit: Maximum records

        Returns:
            List of quotes

        Example:
            quotes = service.get_by_company(company_id=5, skip=0, limit=10)
        """
        logger.info(f"Getting quotes for company_id={company_id}")
        quotes = self.quote_repo.get_by_company(company_id, skip, limit)
        return [QuoteListResponse.model_validate(q) for q in quotes]

    def get_by_status(
        self,
        status_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> list[QuoteListResponse]:
        """
        Get quotes by status.

        Args:
            status_id: Quote status ID
            skip: Pagination offset
            limit: Maximum records

        Returns:
            List of quotes
        """
        logger.info(f"Getting quotes with status_id={status_id}")
        quotes = self.quote_repo.get_by_status(status_id, skip, limit)
        return [QuoteListResponse.model_validate(q) for q in quotes]

    def get_by_staff(
        self,
        staff_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> list[QuoteListResponse]:
        """
        Get quotes assigned to staff member.

        Args:
            staff_id: Staff ID
            skip: Pagination offset
            limit: Maximum records

        Returns:
            List of quotes
        """
        logger.info(f"Getting quotes for staff_id={staff_id}")
        quotes = self.quote_repo.get_by_staff(staff_id, skip, limit)
        return [QuoteListResponse.model_validate(q) for q in quotes]

    def search_by_subject(
        self,
        subject: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[QuoteListResponse]:
        """
        Search quotes by subject.

        Args:
            subject: Text to search
            skip: Pagination offset
            limit: Maximum records

        Returns:
            List of matching quotes
        """
        logger.info(f"Searching quotes by subject: '{subject}'")
        quotes = self.quote_repo.search_by_subject(subject, skip, limit)
        return [QuoteListResponse.model_validate(q) for q in quotes]

    def calculate_totals(self, quote_id: int, user_id: int) -> QuoteResponse:
        """
        Recalculate quote totals from line items.

        Calculates:
        - Subtotal (sum of all line items)
        - Tax amount (subtotal * tax_percentage)
        - Total (subtotal + tax)

        Args:
            quote_id: Quote ID
            user_id: User performing calculation

        Returns:
            Updated quote

        Raises:
            NotFoundException: If quote not found

        Example:
            quote = service.calculate_totals(quote_id=123, user_id=1)
        """
        logger.info(f"Calculating totals for quote_id={quote_id}")

        self.session.info["user_id"] = user_id

        quote = self.quote_repo.get_with_products(quote_id)
        if not quote:
            raise NotFoundException(
                f"Quote not found: id={quote_id}",
                details={"id": quote_id}
            )

        # Calculate line item subtotals first
        for product in quote.products:
            product.calculate_subtotal()

        # Calculate quote totals
        quote.calculate_totals()

        # Save
        self.quote_repo.update(quote)

        logger.success(f"Totals calculated for quote_id={quote_id}: total={quote.total}")
        return self.response_schema.model_validate(quote)

    def add_product(
        self,
        quote_id: int,
        product_data: QuoteProductCreate,
        user_id: int
    ) -> QuoteProductResponse:
        """
        Add product to quote.

        Automatically calculates line item subtotal and recalculates quote totals.

        Args:
            quote_id: Quote ID
            product_data: Product data
            user_id: User adding product

        Returns:
            Created quote product

        Raises:
            NotFoundException: If quote not found

        Example:
            product_data = QuoteProductCreate(
                product_id=10,
                quantity=Decimal("5.000"),
                unit_price=Decimal("1500.00")
            )
            product = service.add_product(quote_id=123, product_data, user_id=1)
        """
        logger.info(f"Adding product to quote_id={quote_id}")

        self.session.info["user_id"] = user_id

        # Verify quote exists
        quote = self.quote_repo.get_by_id(quote_id)
        if not quote:
            raise NotFoundException(
                f"Quote not found: id={quote_id}",
                details={"id": quote_id}
            )

        # Create product
        product_dict = product_data.model_dump()
        product = QuoteProduct(quote_id=quote_id, **product_dict)

        # Calculate line item subtotal
        product.calculate_subtotal()

        # Save
        created = self.product_repo.create(product)

        # Recalculate quote totals
        quote.calculate_totals()
        self.quote_repo.update(quote)

        logger.success(f"Product added to quote_id={quote_id}: product_id={created.id}")
        return QuoteProductResponse.model_validate(created)

    def update_product(
        self,
        product_id: int,
        product_data: QuoteProductUpdate,
        user_id: int
    ) -> QuoteProductResponse:
        """
        Update quote product.

        Automatically recalculates line item subtotal and quote totals.

        Args:
            product_id: Quote product ID
            product_data: Update data
            user_id: User updating product

        Returns:
            Updated quote product

        Raises:
            NotFoundException: If product not found
        """
        logger.info(f"Updating quote product id={product_id}")

        self.session.info["user_id"] = user_id

        # Get existing product
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise NotFoundException(
                f"Quote product not found: id={product_id}",
                details={"id": product_id}
            )

        # Update fields
        update_data = product_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)

        # Recalculate line subtotal
        product.calculate_subtotal()

        # Save
        updated = self.product_repo.update(product)

        # Recalculate quote totals
        quote = self.quote_repo.get_by_id(product.quote_id)
        if quote:
            quote.calculate_totals()
            self.quote_repo.update(quote)

        logger.success(f"Quote product updated: id={product_id}")
        return QuoteProductResponse.model_validate(updated)

    def remove_product(self, product_id: int, user_id: int) -> None:
        """
        Remove product from quote.

        Automatically recalculates quote totals after removal.

        Args:
            product_id: Quote product ID
            user_id: User removing product

        Raises:
            NotFoundException: If product not found
        """
        logger.info(f"Removing quote product id={product_id}")

        self.session.info["user_id"] = user_id

        # Get product to know which quote to update
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise NotFoundException(
                f"Quote product not found: id={product_id}",
                details={"id": product_id}
            )

        quote_id = product.quote_id

        # Delete product
        self.product_repo.delete(product_id)

        # Recalculate quote totals
        quote = self.quote_repo.get_by_id(quote_id)
        if quote:
            quote.calculate_totals()
            self.quote_repo.update(quote)

        logger.success(f"Quote product removed: id={product_id}")
