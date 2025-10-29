"""
Repository for Quote and QuoteProduct models.

Handles data access for quotes with custom query methods including
quote number lookups, company filtering, and status tracking.
"""

from typing import Optional, List
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import and_, or_

from src.models.business.quotes import Quote, QuoteProduct
from src.repositories.base import BaseRepository
from src.utils.logger import logger


class QuoteRepository(BaseRepository[Quote]):
    """
    Repository for Quote with custom query methods.

    Manages quotes with products, status tracking, and conversions to orders.
    Provides specialized queries for business operations.

    Example:
        repository = QuoteRepository(session)
        quote = repository.get_by_quote_number("Q-2025-001")
        quotes = repository.get_by_company(company_id=5, skip=0, limit=10)
    """

    def __init__(self, session: Session):
        """
        Initialize QuoteRepository.

        Args:
            session: SQLAlchemy session for database operations
        """
        super().__init__(session, Quote)

    def get_by_quote_number(self, quote_number: str) -> Optional[Quote]:
        """
        Get quote by unique quote number.

        Args:
            quote_number: Quote number (e.g., "Q-2025-001")

        Returns:
            Quote if found, None otherwise

        Example:
            quote = repository.get_by_quote_number("Q-2025-001")
            if quote:
                print(f"Found quote: {quote.subject}")
        """
        logger.debug(f"Searching quote by number: {quote_number}")
        quote = (
            self.session.query(Quote)
            .filter(Quote.quote_number == quote_number.upper())
            .first()
        )
        if quote:
            logger.debug(f"Quote found: {quote_number}")
        else:
            logger.debug(f"Quote not found: {quote_number}")
        return quote

    def get_with_products(self, quote_id: int) -> Optional[Quote]:
        """
        Get quote with products eagerly loaded.

        Uses eager loading to fetch quote and all related products
        in a single query, avoiding N+1 query problems.

        Args:
            quote_id: Quote ID

        Returns:
            Quote with products loaded, None if not found

        Example:
            quote = repository.get_with_products(123)
            for product in quote.products:
                print(f"Product: {product.product_id}, Qty: {product.quantity}")
        """
        logger.debug(f"Getting quote id={quote_id} with products (eager loading)")
        quote = (
            self.session.query(Quote)
            .options(selectinload(Quote.products))
            .filter(Quote.id == quote_id)
            .first()
        )
        if quote:
            logger.debug(f"Quote found with {len(quote.products)} product(s)")
        else:
            logger.debug(f"Quote not found: id={quote_id}")
        return quote

    def get_by_company(
        self,
        company_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Quote]:
        """
        Get all quotes for a specific company.

        Returns quotes ordered by quote date (most recent first).

        Args:
            company_id: Company ID
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return

        Returns:
            List of quotes for the company

        Example:
            quotes = repository.get_by_company(company_id=5, skip=0, limit=10)
            print(f"Found {len(quotes)} quotes for company")
        """
        logger.debug(f"Getting quotes for company_id={company_id} (skip={skip}, limit={limit})")
        quotes = (
            self.session.query(Quote)
            .filter(Quote.company_id == company_id)
            .order_by(Quote.quote_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        logger.debug(f"Found {len(quotes)} quote(s) for company_id={company_id}")
        return quotes

    def get_by_status(
        self,
        status_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Quote]:
        """
        Get quotes by status.

        Args:
            status_id: Quote status ID
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of quotes with the specified status

        Example:
            draft_quotes = repository.get_by_status(status_id=1, skip=0, limit=50)
        """
        logger.debug(f"Getting quotes with status_id={status_id}")
        quotes = (
            self.session.query(Quote)
            .filter(Quote.status_id == status_id)
            .order_by(Quote.quote_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        logger.debug(f"Found {len(quotes)} quote(s) with status_id={status_id}")
        return quotes

    def get_by_staff(
        self,
        staff_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Quote]:
        """
        Get quotes assigned to a specific staff member.

        Args:
            staff_id: Staff ID
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of quotes assigned to the staff member
        """
        logger.debug(f"Getting quotes for staff_id={staff_id}")
        quotes = (
            self.session.query(Quote)
            .filter(Quote.staff_id == staff_id)
            .order_by(Quote.quote_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        logger.debug(f"Found {len(quotes)} quote(s) for staff_id={staff_id}")
        return quotes

    def get_expired_quotes(self, skip: int = 0, limit: int = 100) -> List[Quote]:
        """
        Get quotes that have expired (valid_until date has passed).

        Args:
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of expired quotes
        """
        from datetime import date

        logger.debug("Getting expired quotes")
        quotes = (
            self.session.query(Quote)
            .filter(
                and_(
                    Quote.valid_until.isnot(None),
                    Quote.valid_until < date.today()
                )
            )
            .order_by(Quote.valid_until.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        logger.debug(f"Found {len(quotes)} expired quote(s)")
        return quotes

    def search_by_subject(
        self,
        subject: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Quote]:
        """
        Search quotes by subject (partial match, case-insensitive).

        Args:
            subject: Text to search in subject field
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of matching quotes
        """
        logger.debug(f"Searching quotes by subject: '{subject}'")
        search_pattern = f"%{subject}%"
        quotes = (
            self.session.query(Quote)
            .filter(Quote.subject.ilike(search_pattern))
            .order_by(Quote.quote_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        logger.debug(f"Found {len(quotes)} quote(s) matching subject")
        return quotes


class QuoteProductRepository(BaseRepository[QuoteProduct]):
    """
    Repository for QuoteProduct (quote line items).

    Manages individual line items within quotes including quantities,
    pricing, and discounts.

    Example:
        repository = QuoteProductRepository(session)
        products = repository.get_by_quote(quote_id=123)
    """

    def __init__(self, session: Session):
        """
        Initialize QuoteProductRepository.

        Args:
            session: SQLAlchemy session for database operations
        """
        super().__init__(session, QuoteProduct)

    def get_by_quote(self, quote_id: int) -> List[QuoteProduct]:
        """
        Get all products for a specific quote.

        Returns products ordered by sequence number.

        Args:
            quote_id: Quote ID

        Returns:
            List of quote products

        Example:
            products = repository.get_by_quote(quote_id=123)
            total = sum(p.subtotal for p in products)
        """
        logger.debug(f"Getting products for quote_id={quote_id}")
        products = (
            self.session.query(QuoteProduct)
            .filter(QuoteProduct.quote_id == quote_id)
            .order_by(QuoteProduct.sequence)
            .all()
        )
        logger.debug(f"Found {len(products)} product(s) for quote_id={quote_id}")
        return products

    def get_by_product(
        self,
        product_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[QuoteProduct]:
        """
        Get all quote line items containing a specific product.

        Useful for finding which quotes include a particular product.

        Args:
            product_id: Product ID
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of quote products
        """
        logger.debug(f"Getting quote products for product_id={product_id}")
        products = (
            self.session.query(QuoteProduct)
            .filter(QuoteProduct.product_id == product_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        logger.debug(f"Found {len(products)} quote product(s) for product_id={product_id}")
        return products

    def delete_by_quote(self, quote_id: int) -> int:
        """
        Delete all products for a specific quote.

        Args:
            quote_id: Quote ID

        Returns:
            Number of products deleted

        Note:
            This is a hard delete. Use with caution.
        """
        logger.debug(f"Deleting all products for quote_id={quote_id}")
        count = (
            self.session.query(QuoteProduct)
            .filter(QuoteProduct.quote_id == quote_id)
            .delete()
        )
        self.session.flush()
        logger.warning(f"Deleted {count} product(s) for quote_id={quote_id}")
        return count
