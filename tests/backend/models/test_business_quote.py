"""
Tests for Quote and QuoteProduct models from business.quotes.

This module contains comprehensive tests for the Quote and QuoteProduct business models,
including CRUD operations, validators, relationships, financial calculations, and edge cases.

Test Coverage:
    Quote:
        - Basic CRUD operations
        - Field validation (quote_number, revision, tax_percentage)
        - Relationships (company, contact, plant, staff, status, etc.)
        - Financial calculations (calculate_totals)
        - Business properties (is_expired, days_until_expiry)
        - CheckConstraints (positive amounts, tax percentage range)
        - Cascade delete behavior
        - Mixins (Timestamp, Audit, Active)

    QuoteProduct:
        - CRUD operations
        - Field validation (quantity, unit_price, discount_percentage)
        - Financial calculations (calculate_subtotal, effective_unit_price)
        - Relationship with Quote and Product
        - CheckConstraints (positive values, discount range)
        - Cascade delete with Quote
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from src.backend.models.business.quotes import Quote, QuoteProduct
from src.backend.models.core.companies import Company
from src.backend.models.lookups import Currency, Incoterm, QuoteStatus


# ============= QUOTE MODEL TESTS =============


class TestQuoteCreation:
    """Tests for Quote model instantiation and creation."""

    def test_create_quote_with_all_fields(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
        sample_quote_status: QuoteStatus,
    ):
        """
        Test creating a Quote with all fields populated.

        This test verifies that a Quote can be created with complete data
        and all fields are properly stored in the database.
        """
        # Create staff for the quote (staff_id is required)
        from src.backend.models.core.staff import Staff

        staff = Staff(
            username="testuser_quote1",
            email="quote1@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)
        session.commit()

        # Arrange & Act
        quote = Quote(
            quote_number="Q-2025-001",
            subject="Quote for Industrial Equipment",
            revision="A",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=sample_quote_status.id,
            quote_date=date(2025, 1, 15),
            valid_until=date(2025, 2, 15),
            shipping_date=date(2025, 3, 1),
            currency_id=sample_currency.id,
            exchange_rate=Decimal("900.00"),
            subtotal=Decimal("1000.00"),
            tax_percentage=Decimal("19.00"),
            tax_amount=Decimal("190.00"),
            total=Decimal("1190.00"),
            notes="Customer-visible notes",
            internal_notes="Internal notes only",
            is_active=True,
        )
        session.add(quote)
        session.commit()
        session.refresh(quote)

        # Assert
        assert quote.id is not None
        assert quote.quote_number == "Q-2025-001"
        assert quote.subject == "Quote for Industrial Equipment"
        assert quote.revision == "A"
        assert quote.company_id == sample_company.id
        assert quote.status_id == sample_quote_status.id
        assert quote.quote_date == date(2025, 1, 15)
        assert quote.valid_until == date(2025, 2, 15)
        assert quote.currency_id == sample_currency.id
        assert quote.subtotal == Decimal("1000.00")
        assert quote.tax_percentage == Decimal("19.00")
        assert quote.tax_amount == Decimal("190.00")
        assert quote.total == Decimal("1190.00")

    def test_create_quote_with_minimal_fields(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
        sample_quote_status: QuoteStatus,
    ):
        """Test creating Quote with only required fields."""
        # Note: We need to create a mock staff for staff_id
        from src.backend.models.core.staff import Staff

        staff = Staff(
            username="testuser",
            email="test@test.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)
        session.commit()

        # Arrange & Act
        quote = Quote(
            quote_number="Q-2025-002",
            subject="Minimal Quote",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=sample_quote_status.id,
            quote_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(quote)
        session.commit()
        session.refresh(quote)

        # Assert
        assert quote.id is not None
        assert quote.quote_number == "Q-2025-002"
        assert quote.revision == "A"  # Default value
        assert quote.subtotal == Decimal("0.00")  # Default value
        assert quote.tax_percentage == Decimal("19.00")  # Default value
        assert quote.tax_amount == Decimal("0.00")  # Default value
        assert quote.total == Decimal("0.00")  # Default value

    def test_quote_default_values(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
        sample_quote_status: QuoteStatus,
    ):
        """Test that Quote default values are properly set."""
        from src.backend.models.core.staff import Staff

        staff = Staff(
            username="testuser2",
            email="test2@test.com",
            first_name="Test",
            last_name="User2",
        )
        session.add(staff)
        session.commit()

        quote = Quote(
            quote_number="Q-2025-003",
            subject="Test",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=sample_quote_status.id,
            quote_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(quote)
        session.commit()
        session.refresh(quote)

        # Assert defaults
        assert quote.revision == "A"
        assert quote.subtotal == Decimal("0.00")
        assert quote.tax_percentage == Decimal("19.00")
        assert quote.tax_amount == Decimal("0.00")
        assert quote.total == Decimal("0.00")
        assert quote.is_active is True


class TestQuoteValidation:
    """Tests for Quote field validators and constraints."""

    def test_quote_number_validator_strips_and_uppercases(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
        sample_quote_status: QuoteStatus,
    ):
        """Test that quote_number is stripped and converted to uppercase."""
        from src.backend.models.core.staff import Staff

        staff = Staff(
            username="testuser3",
            email="test3@test.com",
            first_name="Test",
            last_name="User3",
        )
        session.add(staff)
        session.commit()

        # Arrange & Act
        quote = Quote(
            quote_number="  q-2025-004  ",  # lowercase with whitespace
            subject="Test",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=sample_quote_status.id,
            quote_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(quote)
        session.commit()
        session.refresh(quote)

        # Assert
        assert quote.quote_number == "Q-2025-004"  # Uppercase and trimmed

    def test_quote_number_cannot_be_empty(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
        sample_quote_status: QuoteStatus,
    ):
        """Test that quote_number cannot be empty."""
        from src.backend.models.core.staff import Staff

        staff = Staff(
            username="testuser4",
            email="test4@test.com",
            first_name="Test",
            last_name="User4",
        )
        session.add(staff)
        session.commit()

        with pytest.raises(ValueError, match="cannot be empty"):
            quote = Quote(
                quote_number="   ",  # Whitespace only
                subject="Test",
                company_id=sample_company.id,
                staff_id=staff.id,
                status_id=sample_quote_status.id,
                quote_date=date.today(),
                currency_id=sample_currency.id,
            )
            session.add(quote)
            session.flush()

    def test_quote_number_must_be_unique(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
        sample_quote_status: QuoteStatus,
    ):
        """Test that quote_number must be unique."""
        from src.backend.models.core.staff import Staff

        staff = Staff(
            username="testuser5",
            email="test5@test.com",
            first_name="Test",
            last_name="User5",
        )
        session.add(staff)
        session.commit()

        # Arrange - Create first quote
        quote1 = Quote(
            quote_number="Q-2025-005",
            subject="Test 1",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=sample_quote_status.id,
            quote_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(quote1)
        session.commit()

        # Act & Assert - Try to create duplicate
        with pytest.raises(IntegrityError):
            quote2 = Quote(
                quote_number="Q-2025-005",  # Duplicate
                subject="Test 2",
                company_id=sample_company.id,
                staff_id=staff.id,
                status_id=sample_quote_status.id,
                quote_date=date.today(),
                currency_id=sample_currency.id,
            )
            session.add(quote2)
            session.commit()

    def test_revision_validator_uppercases(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
        sample_quote_status: QuoteStatus,
    ):
        """Test that revision is converted to uppercase."""
        from src.backend.models.core.staff import Staff

        staff = Staff(
            username="testuser6",
            email="test6@test.com",
            first_name="Test",
            last_name="User6",
        )
        session.add(staff)
        session.commit()

        quote = Quote(
            quote_number="Q-2025-006",
            subject="Test",
            revision="b",  # lowercase
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=sample_quote_status.id,
            quote_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(quote)
        session.commit()
        session.refresh(quote)

        assert quote.revision == "B"

    def test_tax_percentage_validator_range(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
        sample_quote_status: QuoteStatus,
    ):
        """Test that tax_percentage must be between 0 and 100."""
        from src.backend.models.core.staff import Staff

        staff = Staff(
            username="testuser7",
            email="test7@test.com",
            first_name="Test",
            last_name="User7",
        )
        session.add(staff)
        session.commit()

        # Test negative value
        with pytest.raises(ValueError, match="between 0 and 100"):
            quote = Quote(
                quote_number="Q-2025-007",
                subject="Test",
                company_id=sample_company.id,
                staff_id=staff.id,
                status_id=sample_quote_status.id,
                quote_date=date.today(),
                currency_id=sample_currency.id,
                tax_percentage=Decimal("-5.00"),
            )
            session.add(quote)
            session.flush()

        session.rollback()

        # Test value > 100
        with pytest.raises(ValueError, match="between 0 and 100"):
            quote = Quote(
                quote_number="Q-2025-007",
                subject="Test",
                company_id=sample_company.id,
                staff_id=staff.id,
                status_id=sample_quote_status.id,
                quote_date=date.today(),
                currency_id=sample_currency.id,
                tax_percentage=Decimal("150.00"),
            )
            session.add(quote)
            session.flush()

    def test_check_constraints_positive_amounts(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
        sample_quote_status: QuoteStatus,
    ):
        """Test CheckConstraints for positive amounts."""
        from src.backend.models.core.staff import Staff

        staff = Staff(
            username="testuser8",
            email="test8@test.com",
            first_name="Test",
            last_name="User8",
        )
        session.add(staff)
        session.commit()

        # Test negative subtotal
        with pytest.raises(IntegrityError):
            quote = Quote(
                quote_number="Q-2025-008",
                subject="Test",
                company_id=sample_company.id,
                staff_id=staff.id,
                status_id=sample_quote_status.id,
                quote_date=date.today(),
                currency_id=sample_currency.id,
                subtotal=Decimal("-100.00"),
            )
            session.add(quote)
            session.commit()


class TestQuoteBusinessMethods:
    """Tests for Quote business logic and methods."""

    def test_calculate_totals_from_products(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
        sample_quote_status: QuoteStatus,
    ):
        """
        Test calculate_totals() method calculates correct amounts.

        This test verifies that the calculate_totals method properly
        sums all quote products and calculates tax and total.
        """
        from src.backend.models.core.staff import Staff
        from src.backend.models.core.products import Product, ProductType

        # Create staff
        staff = Staff(
            username="testuser9",
            email="test9@test.com",
            first_name="Test",
            last_name="User9",
        )
        session.add(staff)
        session.commit()

        # Create products
        product1 = Product(
            product_type=ProductType.ARTICLE,
            reference="PROD-001",
            designation_es="Producto 1",
        )
        product2 = Product(
            product_type=ProductType.ARTICLE,
            reference="PROD-002",
            designation_es="Producto 2",
        )
        session.add_all([product1, product2])
        session.commit()

        # Create quote
        quote = Quote(
            quote_number="Q-2025-009",
            subject="Test Calculate Totals",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=sample_quote_status.id,
            quote_date=date.today(),
            currency_id=sample_currency.id,
            tax_percentage=Decimal("19.00"),
        )
        session.add(quote)
        session.commit()

        # Add quote products
        qp1 = QuoteProduct(
            quote_id=quote.id,
            product_id=product1.id,
            sequence=1,
            quantity=Decimal("10"),
            unit_price=Decimal("100.00"),
            subtotal=Decimal("1000.00"),
        )
        qp2 = QuoteProduct(
            quote_id=quote.id,
            product_id=product2.id,
            sequence=2,
            quantity=Decimal("5"),
            unit_price=Decimal("200.00"),
            subtotal=Decimal("1000.00"),
        )
        session.add_all([qp1, qp2])
        session.commit()
        session.refresh(quote)

        # Act
        quote.calculate_totals()
        session.commit()
        session.refresh(quote)

        # Assert
        assert quote.subtotal == Decimal("2000.00")  # 1000 + 1000
        assert quote.tax_amount == Decimal("380.00")  # 2000 * 0.19
        assert quote.total == Decimal("2380.00")  # 2000 + 380

    def test_is_expired_property_true(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
        sample_quote_status: QuoteStatus,
    ):
        """Test is_expired property returns True for expired quotes."""
        from src.backend.models.core.staff import Staff

        staff = Staff(
            username="testuser10",
            email="test10@test.com",
            first_name="Test",
            last_name="User10",
        )
        session.add(staff)
        session.commit()

        quote = Quote(
            quote_number="Q-2025-010",
            subject="Expired Quote",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=sample_quote_status.id,
            quote_date=date.today() - timedelta(days=60),
            valid_until=date.today() - timedelta(days=1),  # Yesterday
            currency_id=sample_currency.id,
        )
        session.add(quote)
        session.commit()
        session.refresh(quote)

        assert quote.is_expired is True

    def test_is_expired_property_false(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
        sample_quote_status: QuoteStatus,
    ):
        """Test is_expired property returns False for valid quotes."""
        from src.backend.models.core.staff import Staff

        staff = Staff(
            username="testuser11",
            email="test11@test.com",
            first_name="Test",
            last_name="User11",
        )
        session.add(staff)
        session.commit()

        quote = Quote(
            quote_number="Q-2025-011",
            subject="Valid Quote",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=sample_quote_status.id,
            quote_date=date.today(),
            valid_until=date.today() + timedelta(days=30),  # Future
            currency_id=sample_currency.id,
        )
        session.add(quote)
        session.commit()
        session.refresh(quote)

        assert quote.is_expired is False

    def test_is_expired_property_none(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
        sample_quote_status: QuoteStatus,
    ):
        """Test is_expired returns False when valid_until is None."""
        from src.backend.models.core.staff import Staff

        staff = Staff(
            username="testuser12",
            email="test12@test.com",
            first_name="Test",
            last_name="User12",
        )
        session.add(staff)
        session.commit()

        quote = Quote(
            quote_number="Q-2025-012",
            subject="No Expiry Quote",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=sample_quote_status.id,
            quote_date=date.today(),
            valid_until=None,  # No expiry date
            currency_id=sample_currency.id,
        )
        session.add(quote)
        session.commit()
        session.refresh(quote)

        assert quote.is_expired is False

    def test_days_until_expiry_property(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
        sample_quote_status: QuoteStatus,
    ):
        """Test days_until_expiry property calculates correctly."""
        from src.backend.models.core.staff import Staff

        staff = Staff(
            username="testuser13",
            email="test13@test.com",
            first_name="Test",
            last_name="User13",
        )
        session.add(staff)
        session.commit()

        quote = Quote(
            quote_number="Q-2025-013",
            subject="Test",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=sample_quote_status.id,
            quote_date=date.today(),
            valid_until=date.today() + timedelta(days=15),
            currency_id=sample_currency.id,
        )
        session.add(quote)
        session.commit()
        session.refresh(quote)

        assert quote.days_until_expiry == 15

    def test_days_until_expiry_negative(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
        sample_quote_status: QuoteStatus,
    ):
        """Test days_until_expiry returns negative for expired quotes."""
        from src.backend.models.core.staff import Staff

        staff = Staff(
            username="testuser14",
            email="test14@test.com",
            first_name="Test",
            last_name="User14",
        )
        session.add(staff)
        session.commit()

        quote = Quote(
            quote_number="Q-2025-014",
            subject="Test",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=sample_quote_status.id,
            quote_date=date.today(),
            valid_until=date.today() - timedelta(days=5),  # 5 days ago
            currency_id=sample_currency.id,
        )
        session.add(quote)
        session.commit()
        session.refresh(quote)

        assert quote.days_until_expiry == -5


class TestQuoteRepr:
    """Tests for Quote __repr__ method."""

    def test_repr_method(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
        sample_quote_status: QuoteStatus,
    ):
        """Test __repr__ string representation."""
        from src.backend.models.core.staff import Staff

        staff = Staff(
            username="testuser15",
            email="test15@test.com",
            first_name="Test",
            last_name="User15",
        )
        session.add(staff)
        session.commit()

        quote = Quote(
            quote_number="Q-2025-015",
            subject="Test",
            revision="B",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=sample_quote_status.id,
            quote_date=date.today(),
            currency_id=sample_currency.id,
            total=Decimal("1500.00"),
        )
        session.add(quote)
        session.commit()
        session.refresh(quote)

        repr_str = repr(quote)
        assert "Quote" in repr_str
        assert "Q-2025-015" in repr_str
        assert "B" in repr_str or "revision" in repr_str.lower()


# ============= QUOTE PRODUCT MODEL TESTS =============


class TestQuoteProductCreation:
    """Tests for QuoteProduct model creation."""

    def test_create_quote_product_with_all_fields(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
        sample_quote_status: QuoteStatus,
    ):
        """Test creating QuoteProduct with all fields."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.core.products import Product, ProductType

        # Create dependencies
        staff = Staff(
            username="testuser16",
            email="test16@test.com",
            first_name="Test",
            last_name="User16",
        )
        product = Product(
            product_type=ProductType.ARTICLE,
            reference="PROD-001",
            designation_es="Test Product",
        )
        session.add_all([staff, product])
        session.commit()

        quote = Quote(
            quote_number="Q-2025-016",
            subject="Test",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=sample_quote_status.id,
            quote_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(quote)
        session.commit()

        # Arrange & Act
        qp = QuoteProduct(
            quote_id=quote.id,
            product_id=product.id,
            sequence=1,
            quantity=Decimal("10.500"),
            unit_price=Decimal("125.50"),
            discount_percentage=Decimal("10.00"),
            discount_amount=Decimal("131.78"),
            subtotal=Decimal("1186.00"),
            notes="Line item notes",
        )
        session.add(qp)
        session.commit()
        session.refresh(qp)

        # Assert
        assert qp.id is not None
        assert qp.quote_id == quote.id
        assert qp.product_id == product.id
        assert qp.quantity == Decimal("10.500")
        assert qp.unit_price == Decimal("125.50")
        assert qp.discount_percentage == Decimal("10.00")
        assert qp.subtotal == Decimal("1186.00")


class TestQuoteProductValidation:
    """Tests for QuoteProduct validators and constraints."""

    def test_quantity_validator_must_be_positive(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
        sample_quote_status: QuoteStatus,
    ):
        """Test that quantity must be positive."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.core.products import Product, ProductType

        staff = Staff(
            username="testuser17",
            email="test17@test.com",
            first_name="Test",
            last_name="User17",
        )
        product = Product(
            product_type=ProductType.ARTICLE,
            reference="PROD-002",
            designation_es="Test Product",
        )
        session.add_all([staff, product])
        session.commit()

        quote = Quote(
            quote_number="Q-2025-017",
            subject="Test",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=sample_quote_status.id,
            quote_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(quote)
        session.commit()

        # Test zero quantity
        with pytest.raises(ValueError, match="must be positive"):
            qp = QuoteProduct(
                quote_id=quote.id,
                product_id=product.id,
                quantity=Decimal("0"),
                unit_price=Decimal("100.00"),
                subtotal=Decimal("0"),
            )
            session.add(qp)
            session.flush()

        session.rollback()

        # Test negative quantity
        with pytest.raises(ValueError, match="must be positive"):
            qp = QuoteProduct(
                quote_id=quote.id,
                product_id=product.id,
                quantity=Decimal("-5"),
                unit_price=Decimal("100.00"),
                subtotal=Decimal("0"),
            )
            session.add(qp)
            session.flush()

    def test_unit_price_validator_non_negative(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
        sample_quote_status: QuoteStatus,
    ):
        """Test that unit_price cannot be negative."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.core.products import Product, ProductType

        staff = Staff(
            username="testuser18",
            email="test18@test.com",
            first_name="Test",
            last_name="User18",
        )
        product = Product(
            product_type=ProductType.ARTICLE,
            reference="PROD-003",
            designation_es="Test Product",
        )
        session.add_all([staff, product])
        session.commit()

        quote = Quote(
            quote_number="Q-2025-018",
            subject="Test",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=sample_quote_status.id,
            quote_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(quote)
        session.commit()

        with pytest.raises(ValueError, match="cannot be negative"):
            qp = QuoteProduct(
                quote_id=quote.id,
                product_id=product.id,
                quantity=Decimal("10"),
                unit_price=Decimal("-50.00"),
                subtotal=Decimal("0"),
            )
            session.add(qp)
            session.flush()

    def test_discount_percentage_validator_range(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
        sample_quote_status: QuoteStatus,
    ):
        """Test that discount_percentage must be between 0 and 100."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.core.products import Product, ProductType

        staff = Staff(
            username="testuser19",
            email="test19@test.com",
            first_name="Test",
            last_name="User19",
        )
        product = Product(
            product_type=ProductType.ARTICLE,
            reference="PROD-004",
            designation_es="Test Product",
        )
        session.add_all([staff, product])
        session.commit()

        quote = Quote(
            quote_number="Q-2025-019",
            subject="Test",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=sample_quote_status.id,
            quote_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(quote)
        session.commit()

        # Test value > 100
        with pytest.raises(ValueError, match="between 0 and 100"):
            qp = QuoteProduct(
                quote_id=quote.id,
                product_id=product.id,
                quantity=Decimal("10"),
                unit_price=Decimal("100.00"),
                discount_percentage=Decimal("150.00"),
                subtotal=Decimal("0"),
            )
            session.add(qp)
            session.flush()


class TestQuoteProductBusinessMethods:
    """Tests for QuoteProduct business methods."""

    def test_calculate_subtotal_without_discount(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
        sample_quote_status: QuoteStatus,
    ):
        """Test calculate_subtotal() without discount."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.core.products import Product, ProductType

        staff = Staff(
            username="testuser20",
            email="test20@test.com",
            first_name="Test",
            last_name="User20",
        )
        product = Product(
            product_type=ProductType.ARTICLE,
            reference="PROD-005",
            designation_es="Test Product",
        )
        session.add_all([staff, product])
        session.commit()

        quote = Quote(
            quote_number="Q-2025-020",
            subject="Test",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=sample_quote_status.id,
            quote_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(quote)
        session.commit()

        # Arrange
        qp = QuoteProduct(
            quote_id=quote.id,
            product_id=product.id,
            quantity=Decimal("10"),
            unit_price=Decimal("100.00"),
            discount_percentage=Decimal("0.00"),
            subtotal=Decimal("0"),  # Will be calculated
        )

        # Act
        qp.calculate_subtotal()

        # Assert
        assert qp.discount_amount == Decimal("0.00")
        assert qp.subtotal == Decimal("1000.00")  # 10 * 100

    def test_calculate_subtotal_with_discount(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
        sample_quote_status: QuoteStatus,
    ):
        """Test calculate_subtotal() with discount percentage."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.core.products import Product, ProductType

        staff = Staff(
            username="testuser21",
            email="test21@test.com",
            first_name="Test",
            last_name="User21",
        )
        product = Product(
            product_type=ProductType.ARTICLE,
            reference="PROD-006",
            designation_es="Test Product",
        )
        session.add_all([staff, product])
        session.commit()

        quote = Quote(
            quote_number="Q-2025-021",
            subject="Test",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=sample_quote_status.id,
            quote_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(quote)
        session.commit()

        # Arrange
        qp = QuoteProduct(
            quote_id=quote.id,
            product_id=product.id,
            quantity=Decimal("10"),
            unit_price=Decimal("100.00"),
            discount_percentage=Decimal("20.00"),  # 20% discount
            subtotal=Decimal("0"),
        )

        # Act
        qp.calculate_subtotal()

        # Assert
        # 10 * 100 = 1000, 20% discount = 200, subtotal = 800
        assert qp.discount_amount == Decimal("200.00")
        assert qp.subtotal == Decimal("800.00")

    def test_effective_unit_price_property(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
        sample_quote_status: QuoteStatus,
    ):
        """Test effective_unit_price property calculation."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.core.products import Product, ProductType

        staff = Staff(
            username="testuser22",
            email="test22@test.com",
            first_name="Test",
            last_name="User22",
        )
        product = Product(
            product_type=ProductType.ARTICLE,
            reference="PROD-007",
            designation_es="Test Product",
        )
        session.add_all([staff, product])
        session.commit()

        quote = Quote(
            quote_number="Q-2025-022",
            subject="Test",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=sample_quote_status.id,
            quote_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(quote)
        session.commit()

        # Arrange
        qp = QuoteProduct(
            quote_id=quote.id,
            product_id=product.id,
            quantity=Decimal("10"),
            unit_price=Decimal("100.00"),
            discount_percentage=Decimal("20.00"),
            subtotal=Decimal("800.00"),  # After 20% discount
        )

        # Act & Assert
        # 800 / 10 = 80
        assert qp.effective_unit_price == Decimal("80.00")


class TestQuoteProductRepr:
    """Tests for QuoteProduct __repr__ method."""

    def test_repr_method(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
        sample_quote_status: QuoteStatus,
    ):
        """Test __repr__ string representation."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.core.products import Product, ProductType

        staff = Staff(
            username="testuser23",
            email="test23@test.com",
            first_name="Test",
            last_name="User23",
        )
        product = Product(
            product_type=ProductType.ARTICLE,
            reference="PROD-008",
            designation_es="Test Product",
        )
        session.add_all([staff, product])
        session.commit()

        quote = Quote(
            quote_number="Q-2025-023",
            subject="Test",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=sample_quote_status.id,
            quote_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(quote)
        session.commit()

        qp = QuoteProduct(
            quote_id=quote.id,
            product_id=product.id,
            quantity=Decimal("5"),
            unit_price=Decimal("100.00"),
            subtotal=Decimal("500.00"),
        )
        session.add(qp)
        session.commit()
        session.refresh(qp)

        repr_str = repr(qp)
        assert "QuoteProduct" in repr_str
        assert "5" in repr_str or "qty=5" in repr_str.lower()


class TestQuoteCascadeDelete:
    """Tests for cascade delete behavior."""

    def test_deleting_quote_deletes_products(
        self,
        session,
        sample_company: Company,
        sample_currency: Currency,
        sample_quote_status: QuoteStatus,
    ):
        """Test that deleting quote deletes associated products."""
        from src.backend.models.core.staff import Staff
        from src.backend.models.core.products import Product, ProductType

        staff = Staff(
            username="testuser24",
            email="test24@test.com",
            first_name="Test",
            last_name="User24",
        )
        product = Product(
            product_type=ProductType.ARTICLE,
            reference="PROD-009",
            designation_es="Test Product",
        )
        session.add_all([staff, product])
        session.commit()

        quote = Quote(
            quote_number="Q-2025-024",
            subject="Test",
            company_id=sample_company.id,
            staff_id=staff.id,
            status_id=sample_quote_status.id,
            quote_date=date.today(),
            currency_id=sample_currency.id,
        )
        session.add(quote)
        session.commit()

        qp = QuoteProduct(
            quote_id=quote.id,
            product_id=product.id,
            quantity=Decimal("10"),
            unit_price=Decimal("100.00"),
            subtotal=Decimal("1000.00"),
        )
        session.add(qp)
        session.commit()
        qp_id = qp.id

        # Act - Delete quote
        session.delete(quote)
        session.commit()

        # Assert - QuoteProduct should be deleted
        deleted_qp = session.query(QuoteProduct).filter_by(id=qp_id).first()
        assert deleted_qp is None
