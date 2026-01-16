"""
Tests para OrderRepository y OrderProductRepository.

Valida funcionalidad CRUD base más métodos específicos de Order.
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from sqlalchemy.orm import Session

from src.backend.models.business.orders import Order, OrderProduct
from src.backend.models.business.quotes import Quote
from src.backend.models.core.staff import Staff
from src.backend.models.lookups import OrderStatus, PaymentStatus


# ===================== FIXTURES =====================


@pytest.fixture
def sample_staff(session: Session) -> Staff:
    """Create a sample Staff for testing."""
    staff = Staff(
        username="test_staff_order",
        first_name="Test",
        last_name="Staff Order",
        email="staff.order@test.com",
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
        code="pending_order",
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
        code="unpaid_order",
        name="Unpaid",
        description="Payment pending",
    )
    session.add(status)
    session.commit()
    session.refresh(status)
    return status


@pytest.fixture
def sample_order(
    session: Session,
    sample_company,
    sample_staff,
    sample_currency,
    sample_order_status,
    sample_payment_status,
) -> Order:
    """Create a sample Order for testing."""
    order = Order(
        order_number="O-2025-001",
        order_type="sales",
        company_id=sample_company.id,
        staff_id=sample_staff.id,
        currency_id=sample_currency.id,
        status_id=sample_order_status.id,
        payment_status_id=sample_payment_status.id,
        order_date=date.today(),
        subtotal=Decimal("1000.00"),
        tax_percentage=Decimal("19.00"),
        tax_amount=Decimal("190.00"),
        total=Decimal("1190.00"),
    )
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


@pytest.fixture
def sample_order_product(
    session: Session,
    sample_order,
    sample_product,
) -> OrderProduct:
    """Create a sample OrderProduct for testing."""
    order_product = OrderProduct(
        order_id=sample_order.id,
        product_id=sample_product.id,
        sequence=1,
        quantity=Decimal("10.000"),
        unit_price=Decimal("100.00"),
        subtotal=Decimal("1000.00"),
    )
    session.add(order_product)
    session.commit()
    session.refresh(order_product)
    return order_product


def create_test_orders(
    session: Session,
    order_repository,
    sample_company,
    sample_staff,
    sample_currency,
    sample_order_status,
    sample_payment_status,
    count: int = 5,
) -> list[Order]:
    """Helper function to create multiple test orders."""
    orders = []
    for i in range(count):
        order = Order(
            order_number=f"O-2025-{i+100:03d}",
            order_type="sales",
            company_id=sample_company.id,
            staff_id=sample_staff.id,
            currency_id=sample_currency.id,
            status_id=sample_order_status.id,
            payment_status_id=sample_payment_status.id,
            order_date=date.today() - timedelta(days=i),
            subtotal=Decimal("1000.00") * (i + 1),
            tax_percentage=Decimal("19.00"),
            tax_amount=Decimal("190.00") * (i + 1),
            total=Decimal("1190.00") * (i + 1),
        )
        created = order_repository.create(order)
        orders.append(created)
    session.commit()
    return orders


# ===================== ORDER REPOSITORY TESTS =====================


class TestOrderRepositoryGetByOrderNumber:
    """Tests para get_by_order_number()."""

    def test_get_by_order_number_existing(self, order_repository, sample_order, session):
        """Test que obtiene order existente por order_number."""
        # Act
        result = order_repository.get_by_order_number(sample_order.order_number)

        # Assert
        assert result is not None
        assert result.id == sample_order.id
        assert result.order_number == sample_order.order_number

    def test_get_by_order_number_not_found(self, order_repository):
        """Test que retorna None cuando order_number no existe."""
        # Act
        result = order_repository.get_by_order_number("O-NONEXISTENT")

        # Assert
        assert result is None

    def test_get_by_order_number_case_insensitive(
        self, order_repository, sample_order, session
    ):
        """Test que búsqueda por order_number normaliza a uppercase."""
        # Act - buscar en lowercase
        result = order_repository.get_by_order_number(sample_order.order_number.lower())

        # Assert
        assert result is not None
        assert result.id == sample_order.id


class TestOrderRepositoryGetWithProducts:
    """Tests para get_with_products()."""

    def test_get_with_products_loads_relationships(
        self, order_repository, sample_order, sample_product, session
    ):
        """Test que carga products con eager loading."""
        # Arrange - crear products para la order
        from src.backend.repositories.business.order_repository import OrderProductRepository
        order_product_repo = OrderProductRepository(session)
        
        for i in range(3):
            product = OrderProduct(
                order_id=sample_order.id,
                product_id=sample_product.id,
                sequence=i + 1,
                quantity=Decimal("10.000"),
                unit_price=Decimal("100.00"),
                subtotal=Decimal("1000.00"),
            )
            order_product_repo.create(product)
        session.commit()

        # Act
        result = order_repository.get_with_products(sample_order.id)

        # Assert
        assert result is not None
        assert len(result.products) >= 3
        assert all(p.order_id == sample_order.id for p in result.products)

    def test_get_with_products_not_found(self, order_repository):
        """Test que retorna None si order no existe."""
        # Act
        result = order_repository.get_with_products(99999)

        # Assert
        assert result is None


class TestOrderRepositoryGetByCompany:
    """Tests para get_by_company()."""

    def test_get_by_company_existing(
        self,
        order_repository,
        sample_order,
        sample_company,
        sample_staff,
        sample_currency,
        sample_order_status,
        sample_payment_status,
        session,
    ):
        """Test que obtiene orders de una company."""
        # Arrange - crear más orders para la misma company
        orders = create_test_orders(
            session,
            order_repository,
            sample_company,
            sample_staff,
            sample_currency,
            sample_order_status,
            sample_payment_status,
            count=3,
        )

        # Act
        results = order_repository.get_by_company(sample_company.id)

        # Assert
        assert len(results) >= 4  # sample_order + 3 created
        assert all(o.company_id == sample_company.id for o in results)

    def test_get_by_company_empty(self, order_repository):
        """Test que retorna lista vacía si no hay orders."""
        # Act
        results = order_repository.get_by_company(99999)

        # Assert
        assert results == []

    def test_get_by_company_with_pagination(
        self,
        order_repository,
        sample_company,
        sample_staff,
        sample_currency,
        sample_order_status,
        sample_payment_status,
        session,
    ):
        """Test que pagination funciona correctamente."""
        # Arrange - crear 10 orders
        orders = create_test_orders(
            session,
            order_repository,
            sample_company,
            sample_staff,
            sample_currency,
            sample_order_status,
            sample_payment_status,
            count=10,
        )

        # Act - obtener con skip y limit
        results = order_repository.get_by_company(sample_company.id, skip=3, limit=5)

        # Assert
        assert len(results) == 5


class TestOrderRepositoryGetByStatus:
    """Tests para get_by_status()."""

    def test_get_by_status_existing(
        self,
        order_repository,
        sample_order,
        sample_order_status,
        session,
    ):
        """Test que filtra orders por status."""
        # Act
        results = order_repository.get_by_status(sample_order_status.id)

        # Assert
        assert len(results) >= 1
        assert all(o.status_id == sample_order_status.id for o in results)

    def test_get_by_status_empty(self, order_repository):
        """Test que retorna lista vacía si no hay orders con ese status."""
        # Act
        results = order_repository.get_by_status(99999)

        # Assert
        assert results == []


class TestOrderRepositoryGetByPaymentStatus:
    """Tests para get_by_payment_status()."""

    def test_get_by_payment_status_existing(
        self,
        order_repository,
        sample_order,
        sample_payment_status,
        session,
    ):
        """Test que filtra orders por payment status."""
        # Act
        results = order_repository.get_by_payment_status(sample_payment_status.id)

        # Assert
        assert len(results) >= 1
        assert all(o.payment_status_id == sample_payment_status.id for o in results)

    def test_get_by_payment_status_empty(self, order_repository):
        """Test que retorna lista vacía si no hay orders con ese payment status."""
        # Act
        results = order_repository.get_by_payment_status(99999)

        # Assert
        assert results == []


class TestOrderRepositoryGetByStaff:
    """Tests para get_by_staff()."""

    def test_get_by_staff_existing(
        self,
        order_repository,
        sample_order,
        sample_staff,
        session,
    ):
        """Test que filtra orders por staff."""
        # Act
        results = order_repository.get_by_staff(sample_staff.id)

        # Assert
        assert len(results) >= 1
        assert all(o.staff_id == sample_staff.id for o in results)

    def test_get_by_staff_empty(self, order_repository):
        """Test que retorna lista vacía si no hay orders del staff."""
        # Act
        results = order_repository.get_by_staff(99999)

        # Assert
        assert results == []


class TestOrderRepositoryGetByQuote:
    """Tests para get_by_quote()."""

    def test_get_by_quote_existing(
        self,
        order_repository,
        sample_company,
        sample_staff,
        sample_currency,
        sample_order_status,
        sample_payment_status,
        sample_quote_status,
        session,
    ):
        """Test que obtiene order creada desde una quote."""
        # Arrange - crear quote
        quote = Quote(
            quote_number="Q-ORDER-TEST-001",
            subject="Quote for Order",
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
        session.flush()

        # Crear order desde quote
        order = Order(
            order_number="O-FROM-QUOTE-001",
            order_type="sales",
            quote_id=quote.id,
            company_id=sample_company.id,
            staff_id=sample_staff.id,
            currency_id=sample_currency.id,
            status_id=sample_order_status.id,
            payment_status_id=sample_payment_status.id,
            order_date=date.today(),
            subtotal=Decimal("1000.00"),
            tax_amount=Decimal("190.00"),
            total=Decimal("1190.00"),
        )
        session.add(order)
        session.commit()

        # Act
        result = order_repository.get_by_quote(quote.id)

        # Assert
        assert result is not None
        assert result.quote_id == quote.id

    def test_get_by_quote_not_found(self, order_repository):
        """Test que retorna None si no hay order para la quote."""
        # Act
        result = order_repository.get_by_quote(99999)

        # Assert
        assert result is None


class TestOrderRepositoryGetOverdueOrders:
    """Tests para get_overdue_orders()."""

    def test_get_overdue_orders_finds_overdue(
        self,
        order_repository,
        sample_company,
        sample_staff,
        sample_currency,
        sample_order_status,
        sample_payment_status,
        session,
    ):
        """Test que encuentra orders atrasadas."""
        # Arrange - crear order atrasada
        overdue_order = Order(
            order_number="O-OVERDUE-001",
            order_type="sales",
            company_id=sample_company.id,
            staff_id=sample_staff.id,
            currency_id=sample_currency.id,
            status_id=sample_order_status.id,
            payment_status_id=sample_payment_status.id,
            order_date=date.today() - timedelta(days=60),
            promised_date=date.today() - timedelta(days=30),  # Overdue
            completed_date=None,  # Not completed
            subtotal=Decimal("1000.00"),
            tax_amount=Decimal("190.00"),
            total=Decimal("1190.00"),
        )
        session.add(overdue_order)
        session.commit()

        # Act
        results = order_repository.get_overdue_orders()

        # Assert
        assert len(results) >= 1
        overdue_ids = [o.id for o in results]
        assert overdue_order.id in overdue_ids

    def test_get_overdue_orders_excludes_completed(
        self,
        order_repository,
        sample_company,
        sample_staff,
        sample_currency,
        sample_order_status,
        sample_payment_status,
        session,
    ):
        """Test que no incluye orders completadas aunque tengan fecha pasada."""
        # Arrange - crear order con fecha pasada pero completada
        completed_order = Order(
            order_number="O-COMPLETED-001",
            order_type="sales",
            company_id=sample_company.id,
            staff_id=sample_staff.id,
            currency_id=sample_currency.id,
            status_id=sample_order_status.id,
            payment_status_id=sample_payment_status.id,
            order_date=date.today() - timedelta(days=60),
            promised_date=date.today() - timedelta(days=30),
            completed_date=date.today() - timedelta(days=25),  # Completed
            subtotal=Decimal("1000.00"),
            tax_amount=Decimal("190.00"),
            total=Decimal("1190.00"),
        )
        session.add(completed_order)
        session.commit()

        # Act
        results = order_repository.get_overdue_orders()

        # Assert
        result_ids = [o.id for o in results]
        assert completed_order.id not in result_ids


class TestOrderRepositoryGetByOrderType:
    """Tests para get_by_order_type()."""

    def test_get_by_order_type_sales(
        self,
        order_repository,
        sample_order,
        session,
    ):
        """Test que filtra orders por tipo 'sales'."""
        # Act
        results = order_repository.get_by_order_type("sales")

        # Assert
        assert len(results) >= 1
        assert all(o.order_type == "sales" for o in results)

    def test_get_by_order_type_purchase(
        self,
        order_repository,
        sample_company,
        sample_staff,
        sample_currency,
        sample_order_status,
        sample_payment_status,
        session,
    ):
        """Test que filtra orders por tipo 'purchase'."""
        # Arrange - crear orden de compra
        purchase_order = Order(
            order_number="O-PURCHASE-001",
            order_type="purchase",
            company_id=sample_company.id,
            staff_id=sample_staff.id,
            currency_id=sample_currency.id,
            status_id=sample_order_status.id,
            payment_status_id=sample_payment_status.id,
            order_date=date.today(),
            subtotal=Decimal("1000.00"),
            tax_amount=Decimal("190.00"),
            total=Decimal("1190.00"),
        )
        session.add(purchase_order)
        session.commit()

        # Act
        results = order_repository.get_by_order_type("purchase")

        # Assert
        assert len(results) >= 1
        assert all(o.order_type == "purchase" for o in results)


class TestOrderRepositoryGetExportOrders:
    """Tests para get_export_orders()."""

    def test_get_export_orders_finds_exports(
        self,
        order_repository,
        sample_company,
        sample_staff,
        sample_currency,
        sample_order_status,
        sample_payment_status,
        session,
    ):
        """Test que encuentra órdenes de exportación."""
        # Arrange - crear orden de exportación
        export_order = Order(
            order_number="O-EXPORT-001",
            order_type="sales",
            is_export=True,
            company_id=sample_company.id,
            staff_id=sample_staff.id,
            currency_id=sample_currency.id,
            status_id=sample_order_status.id,
            payment_status_id=sample_payment_status.id,
            order_date=date.today(),
            subtotal=Decimal("1000.00"),
            tax_amount=Decimal("190.00"),
            total=Decimal("1190.00"),
        )
        session.add(export_order)
        session.commit()

        # Act
        results = order_repository.get_export_orders()

        # Assert
        assert len(results) >= 1
        assert all(o.is_export for o in results)


class TestOrderRepositorySearchByProject:
    """Tests para search_by_project()."""

    def test_search_by_project_partial_match(
        self,
        order_repository,
        sample_company,
        sample_staff,
        sample_currency,
        sample_order_status,
        sample_payment_status,
        session,
    ):
        """Test que encuentra orders con match parcial en project_number."""
        # Arrange - crear orders con project numbers específicos
        for i, proj in enumerate(["PROJ-2025-001", "PROJ-2025-002", "OTHER-001"]):
            order = Order(
                order_number=f"O-PROJ-{i+1:03d}",
                order_type="sales",
                project_number=proj,
                company_id=sample_company.id,
                staff_id=sample_staff.id,
                currency_id=sample_currency.id,
                status_id=sample_order_status.id,
                payment_status_id=sample_payment_status.id,
                order_date=date.today(),
                subtotal=Decimal("1000.00"),
                tax_amount=Decimal("190.00"),
                total=Decimal("1190.00"),
            )
            session.add(order)
        session.commit()

        # Act
        results = order_repository.search_by_project("PROJ-2025")

        # Assert
        assert len(results) >= 2
        assert all("PROJ-2025" in o.project_number for o in results)

    def test_search_by_project_no_results(self, order_repository):
        """Test que retorna lista vacía sin matches."""
        # Act
        results = order_repository.search_by_project("NONEXISTENT-PROJECT")

        # Assert
        assert results == []


# ===================== ORDER PRODUCT REPOSITORY TESTS =====================


class TestOrderProductRepositoryGetByOrder:
    """Tests para get_by_order()."""

    def test_get_by_order_existing(
        self, sample_order, sample_product, session
    ):
        """Test que obtiene products de una order."""
        from src.backend.repositories.business.order_repository import OrderProductRepository
        order_product_repo = OrderProductRepository(session)
        
        # Arrange - crear 3 products
        for i in range(3):
            product = OrderProduct(
                order_id=sample_order.id,
                product_id=sample_product.id,
                sequence=i + 1,
                quantity=Decimal("10.000"),
                unit_price=Decimal("100.00"),
                subtotal=Decimal("1000.00"),
            )
            order_product_repo.create(product)
        session.commit()

        # Act
        results = order_product_repo.get_by_order(sample_order.id)

        # Assert
        assert len(results) == 3
        assert all(p.order_id == sample_order.id for p in results)
        # Verify ordering by sequence
        sequences = [p.sequence for p in results]
        assert sequences == sorted(sequences)

    def test_get_by_order_empty(self, session):
        """Test que retorna lista vacía si no hay products."""
        from src.backend.repositories.business.order_repository import OrderProductRepository
        order_product_repo = OrderProductRepository(session)
        
        # Act
        results = order_product_repo.get_by_order(99999)

        # Assert
        assert results == []


class TestOrderProductRepositoryDeleteByOrder:
    """Tests para delete_by_order()."""

    def test_delete_by_order_removes_all(
        self, sample_order, sample_product, session
    ):
        """Test que elimina todos los products de una order."""
        from src.backend.repositories.business.order_repository import OrderProductRepository
        order_product_repo = OrderProductRepository(session)
        
        # Arrange - crear products
        for i in range(5):
            product = OrderProduct(
                order_id=sample_order.id,
                product_id=sample_product.id,
                sequence=i + 1,
                quantity=Decimal("10.000"),
                unit_price=Decimal("100.00"),
                subtotal=Decimal("1000.00"),
            )
            order_product_repo.create(product)
        session.commit()

        # Verify products exist
        before = order_product_repo.get_by_order(sample_order.id)
        assert len(before) == 5

        # Act
        deleted_count = order_product_repo.delete_by_order(sample_order.id)
        session.commit()

        # Assert
        assert deleted_count == 5
        after = order_product_repo.get_by_order(sample_order.id)
        assert len(after) == 0
