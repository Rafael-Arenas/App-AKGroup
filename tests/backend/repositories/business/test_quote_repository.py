"""
Tests para QuoteRepository y QuoteProductRepository.

Valida funcionalidad CRUD base más métodos específicos de Quote.
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from sqlalchemy.orm import Session

from src.backend.models.business.quotes import Quote, QuoteProduct
from src.backend.models.core.staff import Staff
from src.backend.models.lookups import OrderStatus, PaymentStatus


# ===================== FIXTURES =====================


@pytest.fixture
def sample_staff(session: Session) -> Staff:
    """Create a sample Staff for testing."""
    staff = Staff(
        username="test_staff_quote",
        first_name="Test",
        last_name="Staff",
        email="staff@test.com",
        position="Sales",
        is_active=True,
    )
    session.add(staff)
    session.commit()
    session.refresh(staff)
    return staff


@pytest.fixture
def sample_order_status(session: Session) -> OrderStatus:
    """Create a sample OrderStatus for testing."""
    status = OrderStatus(
        code="pending",
        name="Pending",
        description="Order is pending",
    )
    session.add(status)
    session.commit()
    session.refresh(status)
    return status


@pytest.fixture
def sample_payment_status(session: Session) -> PaymentStatus:
    """Create a sample PaymentStatus for testing."""
    status = PaymentStatus(
        code="unpaid",
        name="Unpaid",
        description="Payment pending",
    )
    session.add(status)
    session.commit()
    session.refresh(status)
    return status


@pytest.fixture
def sample_quote(
    session: Session,
    sample_company,
    sample_staff,
    sample_currency,
    sample_quote_status,
) -> Quote:
    """Create a sample Quote for testing."""
    quote = Quote(
        quote_number="Q-2025-001",
        subject="Test Quote",
        company_id=sample_company.id,
        staff_id=sample_staff.id,
        currency_id=sample_currency.id,
        status_id=sample_quote_status.id,
        quote_date=date.today(),
        valid_until=date.today() + timedelta(days=30),
        subtotal=Decimal("1000.00"),
        tax_percentage=Decimal("19.00"),
        tax_amount=Decimal("190.00"),
        total=Decimal("1190.00"),
    )
    session.add(quote)
    session.commit()
    session.refresh(quote)
    return quote


@pytest.fixture
def sample_quote_product(
    session: Session,
    sample_quote,
    sample_product,
) -> QuoteProduct:
    """Create a sample QuoteProduct for testing."""
    quote_product = QuoteProduct(
        quote_id=sample_quote.id,
        product_id=sample_product.id,
        sequence=1,
        quantity=Decimal("10.000"),
        unit_price=Decimal("100.00"),
        subtotal=Decimal("1000.00"),
    )
    session.add(quote_product)
    session.commit()
    session.refresh(quote_product)
    return quote_product


def create_test_quotes(
    session: Session,
    quote_repository,
    sample_company,
    sample_staff,
    sample_currency,
    sample_quote_status,
    count: int = 5,
) -> list[Quote]:
    """Helper function to create multiple test quotes."""
    quotes = []
    for i in range(count):
        quote = Quote(
            quote_number=f"Q-2025-{i+100:03d}",
            subject=f"Test Quote {i+1}",
            company_id=sample_company.id,
            staff_id=sample_staff.id,
            currency_id=sample_currency.id,
            status_id=sample_quote_status.id,
            quote_date=date.today() - timedelta(days=i),
            valid_until=date.today() + timedelta(days=30 - i),
            subtotal=Decimal("1000.00") * (i + 1),
            tax_percentage=Decimal("19.00"),
            tax_amount=Decimal("190.00") * (i + 1),
            total=Decimal("1190.00") * (i + 1),
        )
        created = quote_repository.create(quote)
        quotes.append(created)
    session.commit()
    return quotes


# ===================== QUOTE REPOSITORY TESTS =====================


class TestQuoteRepositoryGetByQuoteNumber:
    """Tests para get_by_quote_number()."""

    def test_get_by_quote_number_existing(self, quote_repository, sample_quote, session):
        """Test que obtiene quote existente por quote_number."""
        # Act
        result = quote_repository.get_by_quote_number(sample_quote.quote_number)

        # Assert
        assert result is not None
        assert result.id == sample_quote.id
        assert result.quote_number == sample_quote.quote_number

    def test_get_by_quote_number_not_found(self, quote_repository):
        """Test que retorna None cuando quote_number no existe."""
        # Act
        result = quote_repository.get_by_quote_number("Q-NONEXISTENT")

        # Assert
        assert result is None

    def test_get_by_quote_number_case_insensitive(
        self, quote_repository, sample_quote, session
    ):
        """Test que búsqueda por quote_number normaliza a uppercase."""
        # Act - buscar en lowercase
        result = quote_repository.get_by_quote_number(sample_quote.quote_number.lower())

        # Assert
        assert result is not None
        assert result.id == sample_quote.id


class TestQuoteRepositoryGetWithProducts:
    """Tests para get_with_products()."""

    def test_get_with_products_loads_relationships(
        self, quote_repository, sample_quote, quote_product_repository, sample_product, session
    ):
        """Test que carga products con eager loading."""
        # Arrange - crear products para la quote
        for i in range(3):
            product = QuoteProduct(
                quote_id=sample_quote.id,
                product_id=sample_product.id,
                sequence=i + 1,
                quantity=Decimal("10.000"),
                unit_price=Decimal("100.00"),
                subtotal=Decimal("1000.00"),
            )
            quote_product_repository.create(product)
        session.commit()

        # Act
        result = quote_repository.get_with_products(sample_quote.id)

        # Assert
        assert result is not None
        assert len(result.products) >= 3
        assert all(p.quote_id == sample_quote.id for p in result.products)

    def test_get_with_products_empty_list(self, quote_repository, session):
        """Test que retorna quote con lista vacía si no hay products."""
        # Arrange - crear quote sin products
        from src.backend.models.lookups import Currency, QuoteStatus
        from src.backend.models.core.companies import Company
        from src.backend.models.core.staff import Staff
        from src.backend.models.lookups import CompanyType
        
        company_type = CompanyType(name="CLIENT_TEST_EMPTY")
        session.add(company_type)
        session.flush()
        
        company = Company(name="Test Empty", trigram="TEM", company_type_id=company_type.id)
        session.add(company)
        session.flush()
        
        staff = Staff(username="empty_staff", first_name="Staff", last_name="Empty", email="empty@test.com", position="Test")
        session.add(staff)
        session.flush()
        
        currency = Currency(code="TST", name="Test Currency", symbol="T")
        session.add(currency)
        session.flush()
        
        status = QuoteStatus(code="empty", name="Empty")
        session.add(status)
        session.flush()
        
        quote = Quote(
            quote_number="Q-EMPTY-001",
            subject="Empty Quote",
            company_id=company.id,
            staff_id=staff.id,
            currency_id=currency.id,
            status_id=status.id,
            quote_date=date.today(),
            subtotal=Decimal("0.00"),
            tax_amount=Decimal("0.00"),
            total=Decimal("0.00"),
        )
        session.add(quote)
        session.commit()

        # Act
        result = quote_repository.get_with_products(quote.id)

        # Assert
        assert result is not None
        assert result.products == []

    def test_get_with_products_not_found(self, quote_repository):
        """Test que retorna None si quote no existe."""
        # Act
        result = quote_repository.get_with_products(99999)

        # Assert
        assert result is None


class TestQuoteRepositoryGetByCompany:
    """Tests para get_by_company()."""

    def test_get_by_company_existing(
        self,
        quote_repository,
        sample_quote,
        sample_company,
        sample_staff,
        sample_currency,
        sample_quote_status,
        session,
    ):
        """Test que obtiene quotes de una company."""
        # Arrange - crear más quotes para la misma company
        quotes = create_test_quotes(
            session,
            quote_repository,
            sample_company,
            sample_staff,
            sample_currency,
            sample_quote_status,
            count=3,
        )

        # Act
        results = quote_repository.get_by_company(sample_company.id)

        # Assert
        assert len(results) >= 4  # sample_quote + 3 created
        assert all(q.company_id == sample_company.id for q in results)

    def test_get_by_company_empty(self, quote_repository):
        """Test que retorna lista vacía si no hay quotes."""
        # Act
        results = quote_repository.get_by_company(99999)

        # Assert
        assert results == []

    def test_get_by_company_with_pagination(
        self,
        quote_repository,
        sample_company,
        sample_staff,
        sample_currency,
        sample_quote_status,
        session,
    ):
        """Test que pagination funciona correctamente."""
        # Arrange - crear 10 quotes
        quotes = create_test_quotes(
            session,
            quote_repository,
            sample_company,
            sample_staff,
            sample_currency,
            sample_quote_status,
            count=10,
        )

        # Act - obtener con skip y limit
        results = quote_repository.get_by_company(sample_company.id, skip=3, limit=5)

        # Assert
        assert len(results) == 5


class TestQuoteRepositoryGetByStatus:
    """Tests para get_by_status()."""

    def test_get_by_status_existing(
        self,
        quote_repository,
        sample_quote,
        sample_quote_status,
        session,
    ):
        """Test que filtra quotes por status."""
        # Act
        results = quote_repository.get_by_status(sample_quote_status.id)

        # Assert
        assert len(results) >= 1
        assert all(q.status_id == sample_quote_status.id for q in results)

    def test_get_by_status_empty(self, quote_repository):
        """Test que retorna lista vacía si no hay quotes con ese status."""
        # Act
        results = quote_repository.get_by_status(99999)

        # Assert
        assert results == []


class TestQuoteRepositoryGetByStaff:
    """Tests para get_by_staff()."""

    def test_get_by_staff_existing(
        self,
        quote_repository,
        sample_quote,
        sample_staff,
        session,
    ):
        """Test que filtra quotes por staff."""
        # Act
        results = quote_repository.get_by_staff(sample_staff.id)

        # Assert
        assert len(results) >= 1
        assert all(q.staff_id == sample_staff.id for q in results)

    def test_get_by_staff_empty(self, quote_repository):
        """Test que retorna lista vacía si no hay quotes del staff."""
        # Act
        results = quote_repository.get_by_staff(99999)

        # Assert
        assert results == []


class TestQuoteRepositoryGetExpiredQuotes:
    """Tests para get_expired_quotes()."""

    def test_get_expired_quotes_finds_expired(
        self,
        quote_repository,
        sample_company,
        sample_staff,
        sample_currency,
        sample_quote_status,
        session,
    ):
        """Test que encuentra quotes expiradas."""
        # Arrange - crear quote expirada
        expired_quote = Quote(
            quote_number="Q-EXPIRED-001",
            subject="Expired Quote",
            company_id=sample_company.id,
            staff_id=sample_staff.id,
            currency_id=sample_currency.id,
            status_id=sample_quote_status.id,
            quote_date=date.today() - timedelta(days=60),
            valid_until=date.today() - timedelta(days=30),  # Expired
            subtotal=Decimal("1000.00"),
            tax_amount=Decimal("190.00"),
            total=Decimal("1190.00"),
        )
        session.add(expired_quote)
        session.commit()

        # Act
        results = quote_repository.get_expired_quotes()

        # Assert
        assert len(results) >= 1
        expired_ids = [q.id for q in results]
        assert expired_quote.id in expired_ids

    def test_get_expired_quotes_excludes_valid(
        self,
        quote_repository,
        sample_quote,
        session,
    ):
        """Test que no incluye quotes válidas."""
        # Act
        results = quote_repository.get_expired_quotes()

        # Assert - sample_quote has valid_until in the future
        result_ids = [q.id for q in results]
        assert sample_quote.id not in result_ids


class TestQuoteRepositorySearchBySubject:
    """Tests para search_by_subject()."""

    def test_search_by_subject_partial_match(
        self,
        quote_repository,
        sample_company,
        sample_staff,
        sample_currency,
        sample_quote_status,
        session,
    ):
        """Test que encuentra quotes con match parcial en subject."""
        # Arrange - crear quotes con subjects específicos
        for i, subject in enumerate(["Widget Project", "Gadget Project", "Other"]):
            quote = Quote(
                quote_number=f"Q-SEARCH-{i+1:03d}",
                subject=subject,
                company_id=sample_company.id,
                staff_id=sample_staff.id,
                currency_id=sample_currency.id,
                status_id=sample_quote_status.id,
                quote_date=date.today(),
                subtotal=Decimal("1000.00"),
                tax_amount=Decimal("190.00"),
                total=Decimal("1190.00"),
            )
            session.add(quote)
        session.commit()

        # Act
        results = quote_repository.search_by_subject("Project")

        # Assert
        assert len(results) >= 2
        assert all("Project" in q.subject for q in results)

    def test_search_by_subject_case_insensitive(
        self,
        quote_repository,
        sample_quote,
        session,
    ):
        """Test que búsqueda es case insensitive."""
        # Act
        results = quote_repository.search_by_subject(sample_quote.subject.lower())

        # Assert
        assert len(results) >= 1
        assert any(q.id == sample_quote.id for q in results)

    def test_search_by_subject_no_results(self, quote_repository):
        """Test que retorna lista vacía sin matches."""
        # Act
        results = quote_repository.search_by_subject("NonexistentSubject")

        # Assert
        assert results == []


# ===================== QUOTE PRODUCT REPOSITORY TESTS =====================


class TestQuoteProductRepositoryGetByQuote:
    """Tests para get_by_quote()."""

    def test_get_by_quote_existing(
        self, quote_product_repository, sample_quote, sample_product, session
    ):
        """Test que obtiene products de una quote."""
        # Arrange - crear 3 products
        for i in range(3):
            product = QuoteProduct(
                quote_id=sample_quote.id,
                product_id=sample_product.id,
                sequence=i + 1,
                quantity=Decimal("10.000"),
                unit_price=Decimal("100.00"),
                subtotal=Decimal("1000.00"),
            )
            quote_product_repository.create(product)
        session.commit()

        # Act
        results = quote_product_repository.get_by_quote(sample_quote.id)

        # Assert
        assert len(results) == 3
        assert all(p.quote_id == sample_quote.id for p in results)
        # Verify ordering by sequence
        sequences = [p.sequence for p in results]
        assert sequences == sorted(sequences)

    def test_get_by_quote_empty(self, quote_product_repository):
        """Test que retorna lista vacía si no hay products."""
        # Act
        results = quote_product_repository.get_by_quote(99999)

        # Assert
        assert results == []


class TestQuoteProductRepositoryGetByProduct:
    """Tests para get_by_product()."""

    def test_get_by_product_existing(
        self, quote_product_repository, sample_quote_product, sample_product, session
    ):
        """Test que obtiene quote products por product_id."""
        # Act
        results = quote_product_repository.get_by_product(sample_product.id)

        # Assert
        assert len(results) >= 1
        assert all(p.product_id == sample_product.id for p in results)

    def test_get_by_product_empty(self, quote_product_repository):
        """Test que retorna lista vacía si product no está en ninguna quote."""
        # Act
        results = quote_product_repository.get_by_product(99999)

        # Assert
        assert results == []


class TestQuoteProductRepositoryDeleteByQuote:
    """Tests para delete_by_quote()."""

    def test_delete_by_quote_removes_all(
        self, quote_product_repository, sample_quote, sample_product, session
    ):
        """Test que elimina todos los products de una quote."""
        # Arrange - crear products
        for i in range(5):
            product = QuoteProduct(
                quote_id=sample_quote.id,
                product_id=sample_product.id,
                sequence=i + 1,
                quantity=Decimal("10.000"),
                unit_price=Decimal("100.00"),
                subtotal=Decimal("1000.00"),
            )
            quote_product_repository.create(product)
        session.commit()

        # Verify products exist
        before = quote_product_repository.get_by_quote(sample_quote.id)
        assert len(before) == 5

        # Act
        deleted_count = quote_product_repository.delete_by_quote(sample_quote.id)
        session.commit()

        # Assert
        assert deleted_count == 5
        after = quote_product_repository.get_by_quote(sample_quote.id)
        assert len(after) == 0

    def test_delete_by_quote_nonexistent(self, quote_product_repository, session):
        """Test que delete_by_quote retorna 0 para quote inexistente."""
        # Act
        deleted_count = quote_product_repository.delete_by_quote(99999)

        # Assert
        assert deleted_count == 0
