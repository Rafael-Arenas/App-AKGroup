"""
Fixtures compartidos para tests de repositorios.

Proporciona fixtures para instanciar repositorios con sesiones de prueba,
datos de ejemplo, y utilidades comunes para tests de la capa de acceso a datos.
"""

import pytest
from sqlalchemy.orm import Session

from src.backend.repositories.base import BaseRepository
from src.backend.repositories.core.company_repository import (
    CompanyRepository,
    CompanyRutRepository,
    BranchRepository,
)
from src.backend.repositories.core.product_repository import (
    ProductRepository,
    ProductComponentRepository,
)
from src.backend.repositories.core.address_repository import AddressRepository
from src.backend.repositories.core.contact_repository import ContactRepository
from src.backend.repositories.core.service_repository import ServiceRepository
from src.backend.repositories.core.staff_repository import StaffRepository
from src.backend.repositories.core.note_repository import NoteRepository

from src.backend.repositories.business.quote_repository import (
    QuoteRepository,
    QuoteProductRepository,
)
from src.backend.repositories.business.order_repository import OrderRepository
from src.backend.repositories.business.invoice_repository import (
    InvoiceSIIRepository,
    InvoiceExportRepository,
)
from src.backend.repositories.business.delivery_repository import (
    DeliveryOrderRepository,
    TransportRepository,
    PaymentConditionRepository,
)

from src.backend.repositories.lookups.lookup_repository import (
    CountryRepository,
    CityRepository,
    CompanyTypeRepository,
    IncotermRepository,
    CurrencyRepository,
    UnitRepository,
    FamilyTypeRepository,
    MatterRepository,
    SalesTypeRepository,
    QuoteStatusRepository,
    OrderStatusRepository,
    PaymentStatusRepository,
)

from src.backend.models.core.companies import Company, CompanyRut, Branch
from src.backend.models.core.products import Product, ProductComponent
from src.backend.models.core.addresses import Address
from src.backend.models.core.contacts import Contact, Service
from src.backend.models.core.staff import Staff
from src.backend.models.core.notes import Note

from src.backend.models.business.quotes import Quote, QuoteProduct
from src.backend.models.business.orders import Order
from src.backend.models.business.invoices import InvoiceSII, InvoiceExport
from src.backend.models.business.delivery import (
    DeliveryOrder,
    Transport,
    PaymentCondition,
)

from src.backend.models.lookups.lookups import (
    Country,
    City,
    Currency,
    CompanyType,
)


# ===================== BASE REPOSITORY FIXTURES =====================


@pytest.fixture
def base_repository(session: Session) -> BaseRepository:
    """
    Fixture para BaseRepository con modelo Company.

    Usado para testear funcionalidad genérica del BaseRepository.
    """
    return BaseRepository(session, Company)


# ===================== CORE REPOSITORY FIXTURES =====================


@pytest.fixture
def company_repository(session: Session) -> CompanyRepository:
    """Fixture para CompanyRepository."""
    return CompanyRepository(session)


@pytest.fixture
def company_rut_repository(session: Session) -> CompanyRutRepository:
    """Fixture para CompanyRutRepository."""
    return CompanyRutRepository(session)


@pytest.fixture
def branch_repository(session: Session) -> BranchRepository:
    """Fixture para BranchRepository."""
    return BranchRepository(session)


@pytest.fixture
def product_repository(session: Session) -> ProductRepository:
    """Fixture para ProductRepository."""
    return ProductRepository(session)


@pytest.fixture
def product_component_repository(session: Session) -> ProductComponentRepository:
    """Fixture para ProductComponentRepository."""
    return ProductComponentRepository(session)


@pytest.fixture
def address_repository(session: Session) -> AddressRepository:
    """Fixture para AddressRepository."""
    return AddressRepository(session)


@pytest.fixture
def contact_repository(session: Session) -> ContactRepository:
    """Fixture para ContactRepository."""
    return ContactRepository(session)


@pytest.fixture
def service_repository(session: Session) -> ServiceRepository:
    """Fixture para ServiceRepository."""
    return ServiceRepository(session)


@pytest.fixture
def staff_repository(session: Session) -> StaffRepository:
    """Fixture para StaffRepository."""
    return StaffRepository(session)


@pytest.fixture
def note_repository(session: Session) -> NoteRepository:
    """Fixture para NoteRepository."""
    return NoteRepository(session)


# ===================== BUSINESS REPOSITORY FIXTURES =====================


@pytest.fixture
def quote_repository(session: Session) -> QuoteRepository:
    """Fixture para QuoteRepository."""
    return QuoteRepository(session)


@pytest.fixture
def quote_product_repository(session: Session) -> QuoteProductRepository:
    """Fixture para QuoteProductRepository."""
    return QuoteProductRepository(session)


@pytest.fixture
def order_repository(session: Session) -> OrderRepository:
    """Fixture para OrderRepository."""
    return OrderRepository(session)


@pytest.fixture
def invoice_sii_repository(session: Session) -> InvoiceSIIRepository:
    """Fixture para InvoiceSIIRepository."""
    return InvoiceSIIRepository(session)


@pytest.fixture
def invoice_export_repository(session: Session) -> InvoiceExportRepository:
    """Fixture para InvoiceExportRepository."""
    return InvoiceExportRepository(session)


@pytest.fixture
def delivery_order_repository(session: Session) -> DeliveryOrderRepository:
    """Fixture para DeliveryOrderRepository."""
    return DeliveryOrderRepository(session)


@pytest.fixture
def transport_repository(session: Session) -> TransportRepository:
    """Fixture para TransportRepository."""
    return TransportRepository(session)


@pytest.fixture
def payment_condition_repository(session: Session) -> PaymentConditionRepository:
    """Fixture para PaymentConditionRepository."""
    return PaymentConditionRepository(session)


# ===================== LOOKUP REPOSITORY FIXTURES =====================


@pytest.fixture
def country_repository(session: Session) -> CountryRepository:
    """Fixture para CountryRepository."""
    return CountryRepository(session)


@pytest.fixture
def city_repository(session: Session) -> CityRepository:
    """Fixture para CityRepository."""
    return CityRepository(session)


@pytest.fixture
def company_type_repository(session: Session) -> CompanyTypeRepository:
    """Fixture para CompanyTypeRepository."""
    return CompanyTypeRepository(session)


@pytest.fixture
def incoterm_repository(session: Session) -> IncotermRepository:
    """Fixture para IncotermRepository."""
    return IncotermRepository(session)


@pytest.fixture
def currency_repository(session: Session) -> CurrencyRepository:
    """Fixture para CurrencyRepository."""
    return CurrencyRepository(session)


@pytest.fixture
def unit_repository(session: Session) -> UnitRepository:
    """Fixture para UnitRepository."""
    return UnitRepository(session)


@pytest.fixture
def family_type_repository(session: Session) -> FamilyTypeRepository:
    """Fixture para FamilyTypeRepository."""
    return FamilyTypeRepository(session)


@pytest.fixture
def matter_repository(session: Session) -> MatterRepository:
    """Fixture para MatterRepository."""
    return MatterRepository(session)


@pytest.fixture
def sales_type_repository(session: Session) -> SalesTypeRepository:
    """Fixture para SalesTypeRepository."""
    return SalesTypeRepository(session)


@pytest.fixture
def quote_status_repository(session: Session) -> QuoteStatusRepository:
    """Fixture para QuoteStatusRepository."""
    return QuoteStatusRepository(session)


@pytest.fixture
def order_status_repository(session: Session) -> OrderStatusRepository:
    """Fixture para OrderStatusRepository."""
    return OrderStatusRepository(session)


@pytest.fixture
def payment_status_repository(session: Session) -> PaymentStatusRepository:
    """Fixture para PaymentStatusRepository."""
    return PaymentStatusRepository(session)


# ===================== SAMPLE DATA FIXTURES =====================


@pytest.fixture
def sample_company_data(sample_company_type, sample_country, sample_city) -> dict:
    """
    Datos de ejemplo para crear una Company.

    Returns:
        Diccionario con datos válidos para Company.
    """
    return {
        "name": "Test Company",
        "trigram": "TST",
        "company_type_id": sample_company_type.id,
        "country_id": sample_country.id,
        "city_id": sample_city.id,
        "phone": "+56912345678",
        "email": "test@example.com",
        "website": "https://test.com",
    }


@pytest.fixture
def sample_product_data(sample_family_type, sample_unit) -> dict:
    """
    Datos de ejemplo para crear un Product.

    Returns:
        Diccionario con datos válidos para Product.
    """
    return {
        "product_type": "article",
        "reference": "PROD-001",
        "designation_es": "Producto de Prueba",
        "designation_en": "Test Product",
        "family_type_id": sample_family_type.id,
        "unit_id": sample_unit.id,
        "cost_price": 100.00,
        "sale_price": 150.00,
        "stock_quantity": 50.0,
    }


@pytest.fixture
def sample_address_data(sample_company, sample_city) -> dict:
    """
    Datos de ejemplo para crear una Address.

    Returns:
        Diccionario con datos válidos para Address.
    """
    return {
        "company_id": sample_company.id,
        "address": "Av. Test 123, Piso 4",
        "city_id": sample_city.id,
        "postal_code": "12345",
        "address_type": "delivery",
        "is_default": False,
    }


@pytest.fixture
def sample_note_data(sample_company) -> dict:
    """
    Datos de ejemplo para crear una Note.

    Returns:
        Diccionario con datos válidos para Note.
    """
    return {
        "entity_type": "company",
        "entity_id": sample_company.id,
        "title": "Test Note",
        "content": "This is a test note content",
        "priority": "normal",
        "category": "General",
    }


# ===================== HELPER FUNCTIONS =====================


@pytest.fixture
def create_test_companies(session: Session, company_repository: CompanyRepository, sample_company_type):
    """
    Helper function para crear múltiples companies de prueba.

    Returns:
        Función que crea N companies y retorna la lista.
    """
    def _create(count: int = 5) -> list[Company]:
        companies = []
        # Usar letras para trigrams (AAA, AAB, AAC, etc.)
        for i in range(count):
            trigram_suffix = chr(65 + (i % 26))  # A-Z
            trigram_prefix = chr(65 + (i // 26))  # A-Z
            company = Company(
                name=f"Test Company {i+1}",
                trigram=f"T{trigram_prefix}{trigram_suffix}",
                company_type_id=sample_company_type.id,
            )
            created = company_repository.create(company)
            companies.append(created)
        session.commit()
        return companies

    return _create


@pytest.fixture
def create_test_products(session: Session, product_repository: ProductRepository, sample_family_type):
    """
    Helper function para crear múltiples products de prueba.

    Returns:
        Función que crea N products y retorna la lista.
    """
    def _create(count: int = 5) -> list[Product]:
        products = []
        for i in range(count):
            product = Product(
                product_type="article",
                reference=f"PROD-{i+1:03d}",
                designation_es=f"Producto {i+1}",
                family_type_id=sample_family_type.id,
                cost_price=100.00 * (i + 1),
                sale_price=150.00 * (i + 1),
            )
            created = product_repository.create(product)
            products.append(created)
        session.commit()
        return products

    return _create
