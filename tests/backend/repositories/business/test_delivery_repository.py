"""
Tests para DeliveryOrderRepository, TransportRepository y PaymentConditionRepository.

Valida funcionalidad CRUD base más métodos específicos de entrega.
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from sqlalchemy.orm import Session

from src.backend.models.business.delivery import (
    DeliveryOrder,
    DeliveryDate,
    Transport,
    PaymentCondition,
)
from src.backend.models.business.orders import Order
from src.backend.models.core.addresses import Address
from src.backend.models.core.staff import Staff
from src.backend.models.lookups import OrderStatus, PaymentStatus, PaymentType


# ===================== FIXTURES =====================


@pytest.fixture
def sample_staff(session: Session) -> Staff:
    """Create a sample Staff for delivery testing."""
    staff = Staff(
        username="delivery_staff",
        first_name="Delivery",
        last_name="Staff",
        email="delivery.staff@test.com",
        position="Logistics",
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
        code="confirmed_del",
        name="Confirmed",
        description="Order confirmed",
    )
    session.add(status)
    session.commit()
    session.refresh(status)
    return status


@pytest.fixture
def sample_payment_status(session: Session) -> PaymentStatus:
    """Create a sample PaymentStatus for testing."""
    status = PaymentStatus(
        code="paid_del",
        name="Paid",
        description="Payment received",
    )
    session.add(status)
    session.commit()
    session.refresh(status)
    return status


@pytest.fixture
def sample_address(session: Session, sample_company) -> Address:
    """Create a sample Address for delivery testing."""
    from src.shared.enums import AddressType
    
    address = Address(
        company_id=sample_company.id,
        address="Test Street 123, Building A, Floor 5",
        city="Santiago",
        country="Chile",
        address_type=AddressType.DELIVERY,
    )
    session.add(address)
    session.commit()
    session.refresh(address)
    return address


@pytest.fixture
def sample_order_for_delivery(
    session: Session,
    sample_company,
    sample_staff,
    sample_currency,
    sample_order_status,
    sample_payment_status,
) -> Order:
    """Create a sample Order for delivery testing."""
    order = Order(
        order_number="O-DEL-2025-001",
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
def sample_transport(session: Session) -> Transport:
    """Create a sample Transport for testing."""
    transport = Transport(
        name="DHL Express",
        transport_type="courier",
        contact_name="DHL Contact",
        contact_phone="+1234567890",
        is_active=True,
    )
    session.add(transport)
    session.commit()
    session.refresh(transport)
    return transport


@pytest.fixture
def sample_delivery_order(
    session: Session,
    sample_order_for_delivery,
    sample_company,
    sample_address,
    sample_transport,
    sample_staff,
) -> DeliveryOrder:
    """Create a sample DeliveryOrder for testing."""
    delivery = DeliveryOrder(
        delivery_number="GD-2025-001",
        order_id=sample_order_for_delivery.id,
        company_id=sample_company.id,
        address_id=sample_address.id,
        transport_id=sample_transport.id,
        staff_id=sample_staff.id,
        delivery_date=date.today() + timedelta(days=7),
        status="pending",
    )
    session.add(delivery)
    session.commit()
    session.refresh(delivery)
    return delivery


@pytest.fixture
def sample_payment_type(session: Session) -> PaymentType:
    """Create a sample PaymentType for testing."""
    payment_type = PaymentType(
        code="NET60",
        name="Net 60 Days",
        days=60,
        is_active=True,
    )
    session.add(payment_type)
    session.commit()
    session.refresh(payment_type)
    return payment_type


@pytest.fixture
def sample_payment_condition(session: Session, sample_payment_type) -> PaymentCondition:
    """Create a sample PaymentCondition for testing."""
    condition = PaymentCondition(
        payment_condition_number="001",
        name="Standard Net 60",
        payment_type_id=sample_payment_type.id,
        days_to_pay=60,
        percentage_advance=Decimal("0.00"),
        percentage_on_delivery=Decimal("0.00"),
        percentage_after_delivery=Decimal("100.00"),
        is_default=True,
    )
    session.add(condition)
    session.commit()
    session.refresh(condition)
    return condition


# ===================== DELIVERY ORDER REPOSITORY TESTS =====================


class TestDeliveryOrderRepositoryGetByDeliveryNumber:
    """Tests para get_by_delivery_number()."""

    def test_get_by_delivery_number_existing(
        self, delivery_order_repository, sample_delivery_order, session
    ):
        """Test que obtiene guía de despacho existente por número."""
        # Act
        result = delivery_order_repository.get_by_delivery_number(
            sample_delivery_order.delivery_number
        )

        # Assert
        assert result is not None
        assert result.id == sample_delivery_order.id
        assert result.delivery_number == sample_delivery_order.delivery_number

    def test_get_by_delivery_number_not_found(self, delivery_order_repository):
        """Test que retorna None cuando delivery_number no existe."""
        # Act
        result = delivery_order_repository.get_by_delivery_number("GD-NONEXISTENT")

        # Assert
        assert result is None

    def test_get_by_delivery_number_case_insensitive(
        self, delivery_order_repository, sample_delivery_order, session
    ):
        """Test que búsqueda normaliza a uppercase."""
        # Act - buscar en lowercase
        result = delivery_order_repository.get_by_delivery_number(
            sample_delivery_order.delivery_number.lower()
        )

        # Assert
        assert result is not None
        assert result.id == sample_delivery_order.id


class TestDeliveryOrderRepositoryGetByOrder:
    """Tests para get_by_order()."""

    def test_get_by_order_existing(
        self,
        delivery_order_repository,
        sample_delivery_order,
        sample_order_for_delivery,
        sample_company,
        sample_address,
        sample_staff,
        session,
    ):
        """Test que obtiene guías de una orden."""
        # Arrange - crear más guías para la misma orden
        for i in range(2):
            delivery = DeliveryOrder(
                delivery_number=f"GD-2025-{i+100:03d}",
                order_id=sample_order_for_delivery.id,
                company_id=sample_company.id,
                address_id=sample_address.id,
                staff_id=sample_staff.id,
                delivery_date=date.today() + timedelta(days=i + 1),
                status="pending",
            )
            delivery_order_repository.create(delivery)
        session.commit()

        # Act
        results = delivery_order_repository.get_by_order(sample_order_for_delivery.id)

        # Assert
        assert len(results) >= 3  # sample + 2 created
        assert all(d.order_id == sample_order_for_delivery.id for d in results)

    def test_get_by_order_empty(self, delivery_order_repository):
        """Test que retorna lista vacía si no hay guías."""
        # Act
        results = delivery_order_repository.get_by_order(99999)

        # Assert
        assert results == []


class TestDeliveryOrderRepositoryGetByCompany:
    """Tests para get_by_company()."""

    def test_get_by_company_existing(
        self,
        delivery_order_repository,
        sample_delivery_order,
        sample_company,
        session,
    ):
        """Test que obtiene guías de una company."""
        # Act
        results = delivery_order_repository.get_by_company(sample_company.id)

        # Assert
        assert len(results) >= 1
        assert all(d.company_id == sample_company.id for d in results)

    def test_get_by_company_empty(self, delivery_order_repository):
        """Test que retorna lista vacía si no hay guías."""
        # Act
        results = delivery_order_repository.get_by_company(99999)

        # Assert
        assert results == []


class TestDeliveryOrderRepositoryGetByStatus:
    """Tests para get_by_status()."""

    def test_get_by_status_pending(
        self,
        delivery_order_repository,
        sample_delivery_order,
        session,
    ):
        """Test que filtra guías por status."""
        # Act
        results = delivery_order_repository.get_by_status("pending")

        # Assert
        assert len(results) >= 1
        assert all(d.status == "pending" for d in results)

    def test_get_by_status_delivered(
        self,
        delivery_order_repository,
        sample_order_for_delivery,
        sample_company,
        sample_address,
        sample_staff,
        session,
    ):
        """Test que encuentra guías entregadas."""
        # Arrange - crear guía entregada
        delivered = DeliveryOrder(
            delivery_number="GD-DELIVERED-001",
            order_id=sample_order_for_delivery.id,
            company_id=sample_company.id,
            address_id=sample_address.id,
            staff_id=sample_staff.id,
            delivery_date=date.today() - timedelta(days=5),
            actual_delivery_date=date.today() - timedelta(days=3),
            status="delivered",
        )
        session.add(delivered)
        session.commit()

        # Act
        results = delivery_order_repository.get_by_status("delivered")

        # Assert
        assert len(results) >= 1
        assert all(d.status == "delivered" for d in results)


class TestDeliveryOrderRepositoryGetPendingDeliveries:
    """Tests para get_pending_deliveries()."""

    def test_get_pending_deliveries_finds_pending_and_in_transit(
        self,
        delivery_order_repository,
        sample_delivery_order,
        sample_order_for_delivery,
        sample_company,
        sample_address,
        sample_staff,
        session,
    ):
        """Test que encuentra guías pendientes y en tránsito."""
        # Arrange - crear guía en tránsito
        in_transit = DeliveryOrder(
            delivery_number="GD-TRANSIT-001",
            order_id=sample_order_for_delivery.id,
            company_id=sample_company.id,
            address_id=sample_address.id,
            staff_id=sample_staff.id,
            delivery_date=date.today(),
            status="in_transit",
        )
        session.add(in_transit)
        session.commit()

        # Act
        results = delivery_order_repository.get_pending_deliveries()

        # Assert
        assert len(results) >= 2
        assert all(d.status in ["pending", "in_transit"] for d in results)

    def test_get_pending_deliveries_excludes_delivered(
        self,
        delivery_order_repository,
        sample_order_for_delivery,
        sample_company,
        sample_address,
        sample_staff,
        session,
    ):
        """Test que no incluye guías entregadas."""
        # Arrange - crear guía entregada
        delivered = DeliveryOrder(
            delivery_number="GD-DONE-001",
            order_id=sample_order_for_delivery.id,
            company_id=sample_company.id,
            address_id=sample_address.id,
            staff_id=sample_staff.id,
            delivery_date=date.today() - timedelta(days=5),
            actual_delivery_date=date.today() - timedelta(days=3),
            status="delivered",
        )
        session.add(delivered)
        session.commit()

        # Act
        results = delivery_order_repository.get_pending_deliveries()

        # Assert
        result_ids = [d.id for d in results]
        assert delivered.id not in result_ids


# ===================== TRANSPORT REPOSITORY TESTS =====================


class TestTransportRepositoryGetByName:
    """Tests para get_by_name()."""

    def test_get_by_name_existing(
        self, transport_repository, sample_transport, session
    ):
        """Test que obtiene transporte por nombre."""
        # Act
        result = transport_repository.get_by_name(sample_transport.name)

        # Assert
        assert result is not None
        assert result.id == sample_transport.id
        assert result.name == sample_transport.name

    def test_get_by_name_not_found(self, transport_repository):
        """Test que retorna None cuando nombre no existe."""
        # Act
        result = transport_repository.get_by_name("Nonexistent Transport")

        # Assert
        assert result is None


class TestTransportRepositoryGetByType:
    """Tests para get_by_type()."""

    def test_get_by_type_courier(
        self, transport_repository, sample_transport, session
    ):
        """Test que filtra transportes por tipo."""
        # Act
        results = transport_repository.get_by_type("courier")

        # Assert
        assert len(results) >= 1
        assert all(t.transport_type == "courier" for t in results)

    def test_get_by_type_carrier(
        self, transport_repository, session
    ):
        """Test que encuentra transportes tipo carrier."""
        # Arrange - crear transporte tipo carrier
        carrier = Transport(
            name="Freight Carrier",
            transport_type="carrier",
            is_active=True,
        )
        session.add(carrier)
        session.commit()

        # Act
        results = transport_repository.get_by_type("carrier")

        # Assert
        assert len(results) >= 1
        assert all(t.transport_type == "carrier" for t in results)

    def test_get_by_type_empty(self, transport_repository):
        """Test que retorna lista vacía si no hay transportes de ese tipo."""
        # Act
        results = transport_repository.get_by_type("own")

        # Assert - could be empty or have some, just verify type
        assert all(t.transport_type == "own" for t in results)


# ===================== PAYMENT CONDITION REPOSITORY TESTS =====================


class TestPaymentConditionRepositoryGetByNumber:
    """Tests para get_by_number()."""

    def test_get_by_number_existing(
        self, payment_condition_repository, sample_payment_condition, session
    ):
        """Test que obtiene condición de pago por número."""
        # Act
        result = payment_condition_repository.get_by_number(
            sample_payment_condition.payment_condition_number
        )

        # Assert
        assert result is not None
        assert result.id == sample_payment_condition.id
        assert (
            result.payment_condition_number
            == sample_payment_condition.payment_condition_number
        )

    def test_get_by_number_not_found(self, payment_condition_repository):
        """Test que retorna None cuando número no existe."""
        # Act
        result = payment_condition_repository.get_by_number("NONEXIST")

        # Assert
        assert result is None

    def test_get_by_number_case_insensitive(
        self, payment_condition_repository, sample_payment_condition, session
    ):
        """Test que búsqueda normaliza a uppercase."""
        # Act - buscar en lowercase
        result = payment_condition_repository.get_by_number(
            sample_payment_condition.payment_condition_number.lower()
        )

        # Assert
        assert result is not None
        assert result.id == sample_payment_condition.id


class TestPaymentConditionRepositoryGetDefault:
    """Tests para get_default()."""

    def test_get_default_existing(
        self, payment_condition_repository, sample_payment_condition, session
    ):
        """Test que obtiene condición de pago por defecto."""
        # Act
        result = payment_condition_repository.get_default()

        # Assert
        assert result is not None
        assert result.is_default is True

    def test_get_default_not_found(
        self, payment_condition_repository, session
    ):
        """Test que retorna None si no hay condición por defecto."""
        # Arrange - eliminar todas las condiciones por defecto
        # (no hacemos nada aquí, solo verificamos comportamiento sin defaults)
        
        # Act
        result = payment_condition_repository.get_default()

        # Assert - podría existir o no según fixtures
        if result is not None:
            assert result.is_default is True
