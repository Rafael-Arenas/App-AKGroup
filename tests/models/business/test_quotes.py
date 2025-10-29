"""
Unit tests for Quote and QuoteProduct models.

Tests validation, business logic, and relationships for quote models.
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.business.quotes import Quote, QuoteProduct


# Test fixtures
@pytest.fixture
def engine():
    """Create in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    return engine


@pytest.fixture
def session(engine):
    """Create database session."""
    # Import Base and create all tables
    try:
        from models.base import Base
    except ImportError:
        # Use fallback Base from quotes module
        from models.business.quotes import Base

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


class TestQuote:
    """Test suite for Quote model."""

    def test_create_quote(self, session):
        """Test creating a basic quote."""
        quote = Quote(
            quote_number="Q-2025-001",
            subject="Test Quote",
            revision="A",
            company_id=1,
            staff_id=1,
            status_id=1,
            quote_date=date.today(),
            currency_id=1,
            subtotal=Decimal("1000.00"),
            tax_percentage=Decimal("19.00"),
            tax_amount=Decimal("190.00"),
            total=Decimal("1190.00"),
        )

        session.add(quote)
        session.commit()

        assert quote.id is not None
        assert quote.quote_number == "Q-2025-001"
        assert quote.subject == "Test Quote"
        assert quote.total == Decimal("1190.00")

    def test_quote_number_validation(self, session):
        """Test quote number validation."""
        quote = Quote(
            quote_number="  q-2025-002  ",  # Test trimming and uppercase
            subject="Test",
            company_id=1,
            staff_id=1,
            status_id=1,
            quote_date=date.today(),
            currency_id=1,
        )

        assert quote.quote_number == "Q-2025-002"

    def test_quote_number_empty_validation(self, session):
        """Test that empty quote number raises error."""
        with pytest.raises(ValueError, match="Quote number cannot be empty"):
            quote = Quote(
                quote_number="",
                subject="Test",
                company_id=1,
                staff_id=1,
                status_id=1,
                quote_date=date.today(),
                currency_id=1,
            )
            session.add(quote)
            session.flush()

    def test_tax_percentage_validation(self, session):
        """Test tax percentage validation."""
        # Valid tax percentage
        quote = Quote(
            quote_number="Q-2025-003",
            subject="Test",
            company_id=1,
            staff_id=1,
            status_id=1,
            quote_date=date.today(),
            currency_id=1,
            tax_percentage=Decimal("19.00"),
        )
        assert quote.tax_percentage == Decimal("19.00")

        # Invalid: negative
        with pytest.raises(ValueError, match="Tax percentage must be between 0 and 100"):
            quote.tax_percentage = Decimal("-5.00")

        # Invalid: over 100
        with pytest.raises(ValueError, match="Tax percentage must be between 0 and 100"):
            quote.tax_percentage = Decimal("150.00")

    def test_calculate_totals(self, session):
        """Test automatic total calculation."""
        quote = Quote(
            quote_number="Q-2025-004",
            subject="Test",
            company_id=1,
            staff_id=1,
            status_id=1,
            quote_date=date.today(),
            currency_id=1,
            subtotal=Decimal("1000.00"),
            tax_percentage=Decimal("19.00"),
        )

        quote.calculate_totals()

        assert quote.tax_amount == Decimal("190.00")
        assert quote.total == Decimal("1190.00")

    def test_is_expired_property(self, session):
        """Test is_expired property."""
        # Not expired
        quote = Quote(
            quote_number="Q-2025-005",
            subject="Test",
            company_id=1,
            staff_id=1,
            status_id=1,
            quote_date=date.today(),
            valid_until=date.today() + timedelta(days=30),
            currency_id=1,
        )
        assert quote.is_expired is False

        # Expired
        quote.valid_until = date.today() - timedelta(days=1)
        assert quote.is_expired is True

        # No expiry date
        quote.valid_until = None
        assert quote.is_expired is False

    def test_days_until_expiry_property(self, session):
        """Test days_until_expiry calculation."""
        quote = Quote(
            quote_number="Q-2025-006",
            subject="Test",
            company_id=1,
            staff_id=1,
            status_id=1,
            quote_date=date.today(),
            valid_until=date.today() + timedelta(days=30),
            currency_id=1,
        )

        assert quote.days_until_expiry == 30

        # No expiry date
        quote.valid_until = None
        assert quote.days_until_expiry is None

    def test_repr(self, session):
        """Test string representation."""
        quote = Quote(
            id=1,
            quote_number="Q-2025-007",
            subject="Test",
            revision="A",
            company_id=1,
            staff_id=1,
            status_id=1,
            quote_date=date.today(),
            currency_id=1,
            total=Decimal("1190.00"),
        )

        repr_str = repr(quote)
        assert "Quote" in repr_str
        assert "Q-2025-007" in repr_str
        assert "1190.00" in repr_str


class TestQuoteProduct:
    """Test suite for QuoteProduct model."""

    def test_create_quote_product(self, session):
        """Test creating a quote product line item."""
        quote_product = QuoteProduct(
            quote_id=1,
            product_id=1,
            sequence=1,
            quantity=Decimal("5.000"),
            unit_price=Decimal("100.00"),
            discount_percentage=Decimal("10.00"),
            subtotal=Decimal("450.00"),
        )

        session.add(quote_product)
        session.commit()

        assert quote_product.id is not None
        assert quote_product.quantity == Decimal("5.000")
        assert quote_product.subtotal == Decimal("450.00")

    def test_quantity_validation(self, session):
        """Test quantity must be positive."""
        with pytest.raises(ValueError, match="Quantity must be positive"):
            quote_product = QuoteProduct(
                quote_id=1,
                product_id=1,
                quantity=Decimal("0.000"),
                unit_price=Decimal("100.00"),
                subtotal=Decimal("0.00"),
            )
            session.add(quote_product)
            session.flush()

        with pytest.raises(ValueError, match="Quantity must be positive"):
            quote_product = QuoteProduct(
                quote_id=1,
                product_id=1,
                quantity=Decimal("-5.000"),
                unit_price=Decimal("100.00"),
                subtotal=Decimal("0.00"),
            )
            session.add(quote_product)
            session.flush()

    def test_unit_price_validation(self, session):
        """Test unit price cannot be negative."""
        with pytest.raises(ValueError, match="Unit price cannot be negative"):
            quote_product = QuoteProduct(
                quote_id=1,
                product_id=1,
                quantity=Decimal("5.000"),
                unit_price=Decimal("-100.00"),
                subtotal=Decimal("0.00"),
            )
            session.add(quote_product)
            session.flush()

    def test_discount_percentage_validation(self, session):
        """Test discount percentage validation."""
        # Valid discount
        quote_product = QuoteProduct(
            quote_id=1,
            product_id=1,
            quantity=Decimal("5.000"),
            unit_price=Decimal("100.00"),
            discount_percentage=Decimal("15.00"),
            subtotal=Decimal("425.00"),
        )
        assert quote_product.discount_percentage == Decimal("15.00")

        # Invalid: negative
        with pytest.raises(ValueError, match="Discount percentage must be between 0 and 100"):
            quote_product.discount_percentage = Decimal("-5.00")

        # Invalid: over 100
        with pytest.raises(ValueError, match="Discount percentage must be between 0 and 100"):
            quote_product.discount_percentage = Decimal("150.00")

    def test_calculate_subtotal_no_discount(self, session):
        """Test subtotal calculation without discount."""
        quote_product = QuoteProduct(
            quote_id=1,
            product_id=1,
            quantity=Decimal("5.000"),
            unit_price=Decimal("100.00"),
            discount_percentage=Decimal("0.00"),
            subtotal=Decimal("0.00"),
        )

        quote_product.calculate_subtotal()

        assert quote_product.discount_amount == Decimal("0.00")
        assert quote_product.subtotal == Decimal("500.00")

    def test_calculate_subtotal_with_discount(self, session):
        """Test subtotal calculation with discount."""
        quote_product = QuoteProduct(
            quote_id=1,
            product_id=1,
            quantity=Decimal("5.000"),
            unit_price=Decimal("100.00"),
            discount_percentage=Decimal("10.00"),
            subtotal=Decimal("0.00"),
        )

        quote_product.calculate_subtotal()

        # 5 * 100 = 500
        # 10% discount = 50
        # Subtotal = 450
        assert quote_product.discount_amount == Decimal("50.00")
        assert quote_product.subtotal == Decimal("450.00")

    def test_effective_unit_price_property(self, session):
        """Test effective unit price calculation."""
        quote_product = QuoteProduct(
            quote_id=1,
            product_id=1,
            quantity=Decimal("5.000"),
            unit_price=Decimal("100.00"),
            discount_percentage=Decimal("10.00"),
            discount_amount=Decimal("50.00"),
            subtotal=Decimal("450.00"),
        )

        # 450 / 5 = 90
        assert quote_product.effective_unit_price == Decimal("90.00")

    def test_effective_unit_price_zero_quantity(self, session):
        """Test effective unit price with zero quantity."""
        quote_product = QuoteProduct(
            quote_id=1,
            product_id=1,
            quantity=Decimal("0.000"),
            unit_price=Decimal("100.00"),
            subtotal=Decimal("0.00"),
        )

        # Should handle division by zero
        assert quote_product.effective_unit_price == Decimal("0.00")

    def test_repr(self, session):
        """Test string representation."""
        quote_product = QuoteProduct(
            id=1,
            quote_id=1,
            product_id=5,
            quantity=Decimal("3.000"),
            unit_price=Decimal("100.00"),
            subtotal=Decimal("300.00"),
        )

        repr_str = repr(quote_product)
        assert "QuoteProduct" in repr_str
        assert "quote_id=1" in repr_str
        assert "product_id=5" in repr_str


class TestQuoteIntegration:
    """Integration tests for Quote with QuoteProducts."""

    def test_quote_with_products_total_calculation(self, session):
        """Test calculating quote total from products."""
        quote = Quote(
            quote_number="Q-2025-100",
            subject="Integration Test",
            company_id=1,
            staff_id=1,
            status_id=1,
            quote_date=date.today(),
            currency_id=1,
            tax_percentage=Decimal("19.00"),
        )
        session.add(quote)
        session.flush()

        # Add products
        product1 = QuoteProduct(
            quote_id=quote.id,
            product_id=1,
            sequence=1,
            quantity=Decimal("2.000"),
            unit_price=Decimal("100.00"),
            discount_percentage=Decimal("0.00"),
        )
        product1.calculate_subtotal()

        product2 = QuoteProduct(
            quote_id=quote.id,
            product_id=2,
            sequence=2,
            quantity=Decimal("3.000"),
            unit_price=Decimal("50.00"),
            discount_percentage=Decimal("10.00"),
        )
        product2.calculate_subtotal()

        quote.products = [product1, product2]
        quote.calculate_totals()

        # Product 1: 2 * 100 = 200
        # Product 2: 3 * 50 = 150, 10% off = 135
        # Subtotal: 200 + 135 = 335
        # Tax (19%): 63.65
        # Total: 398.65
        assert quote.subtotal == Decimal("335.00")
        assert quote.tax_amount == Decimal("63.65")
        assert quote.total == Decimal("398.65")
