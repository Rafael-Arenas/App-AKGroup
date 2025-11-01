"""
Fixtures compartidos para tests de servicios.

Proporciona fixtures para instanciar servicios con repositorios mockeados,
schemas de prueba, y utilidades comunes para tests de la capa de lógica de negocio.
"""

import pytest
from decimal import Decimal
from unittest.mock import Mock, MagicMock
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.backend.services.base import BaseService
from src.backend.repositories.base import BaseRepository
from src.backend.models.core.companies import Company
from src.backend.models.core.products import Product, ProductType


# ===================== MOCK SCHEMAS =====================


class MockCreateSchema(BaseModel):
    """Schema mock para create operations."""

    name: str
    trigram: str
    company_type_id: int


class MockUpdateSchema(BaseModel):
    """Schema mock para update operations."""

    name: str | None = None
    trigram: str | None = None


class MockResponseSchema(BaseModel):
    """Schema mock para response."""

    id: int
    name: str
    trigram: str
    company_type_id: int

    class Config:
        from_attributes = True


class MockProductCreateSchema(BaseModel):
    """Schema mock para Product create operations."""

    product_type: str
    reference: str
    designation_es: str
    family_type_id: int
    cost_price: Decimal | None = None
    sale_price: Decimal | None = None


class MockProductUpdateSchema(BaseModel):
    """Schema mock para Product update operations."""

    reference: str | None = None
    designation_es: str | None = None
    cost_price: Decimal | None = None
    sale_price: Decimal | None = None


class MockProductResponseSchema(BaseModel):
    """Schema mock para Product response."""

    id: int
    product_type: str
    reference: str
    designation_es: str
    family_type_id: int
    cost_price: Decimal | None = None
    sale_price: Decimal | None = None

    class Config:
        from_attributes = True


# ===================== BASE SERVICE FIXTURES =====================


@pytest.fixture
def mock_company_repository():
    """
    Mock de CompanyRepository para tests de servicios.

    Returns:
        Mock configurado con métodos básicos
    """
    mock_repo = Mock(spec=BaseRepository)
    mock_repo.get_by_id = Mock(return_value=None)
    mock_repo.get_all = Mock(return_value=[])
    mock_repo.create = Mock()
    mock_repo.update = Mock()
    mock_repo.delete = Mock()
    mock_repo.soft_delete = Mock()
    mock_repo.count = Mock(return_value=0)
    mock_repo.exists = Mock(return_value=False)
    return mock_repo


@pytest.fixture
def mock_product_repository():
    """
    Mock de ProductRepository para tests de servicios.

    Returns:
        Mock configurado con métodos básicos
    """
    mock_repo = Mock(spec=BaseRepository)
    mock_repo.get_by_id = Mock(return_value=None)
    mock_repo.get_all = Mock(return_value=[])
    mock_repo.create = Mock()
    mock_repo.update = Mock()
    mock_repo.delete = Mock()
    mock_repo.soft_delete = Mock()
    mock_repo.count = Mock(return_value=0)
    mock_repo.exists = Mock(return_value=False)
    return mock_repo


@pytest.fixture
def base_company_service(mock_company_repository, session):
    """
    Fixture para BaseService configurado con Company.

    Args:
        mock_company_repository: Mock del repositorio
        session: Sesión de base de datos

    Returns:
        BaseService instance
    """
    service = BaseService(
        repository=mock_company_repository,
        session=session,
        model=Company,
        response_schema=MockResponseSchema,
    )
    return service


@pytest.fixture
def base_product_service(mock_product_repository, session):
    """
    Fixture para BaseService configurado con Product.

    Args:
        mock_product_repository: Mock del repositorio
        session: Sesión de base de datos

    Returns:
        BaseService instance
    """
    service = BaseService(
        repository=mock_product_repository,
        session=session,
        model=Product,
        response_schema=MockProductResponseSchema,
    )
    return service


# ===================== SAMPLE DATA FOR SERVICES =====================


@pytest.fixture
def sample_company_entity(sample_company_type):
    """
    Entidad Company de ejemplo para tests de servicios.

    Args:
        sample_company_type: CompanyType fixture

    Returns:
        Company instance
    """
    company = Company(
        id=1,
        name="Test Company",
        trigram="TST",
        company_type_id=sample_company_type.id,
        is_active=True,
    )
    return company


@pytest.fixture
def sample_product_entity(sample_family_type):
    """
    Entidad Product de ejemplo para tests de servicios.

    Args:
        sample_family_type: FamilyType fixture

    Returns:
        Product instance
    """
    product = Product(
        id=1,
        product_type=ProductType.ARTICLE,
        reference="PROD-001",
        designation_es="Producto de Prueba",
        family_type_id=sample_family_type.id,
        cost_price=Decimal("100.00"),
        sale_price=Decimal("150.00"),
        is_active=True,
    )
    return product


@pytest.fixture
def sample_create_schema():
    """
    Schema de creación de ejemplo.

    Returns:
        MockCreateSchema instance
    """
    return MockCreateSchema(name="Test Company", trigram="TST", company_type_id=1)


@pytest.fixture
def sample_update_schema():
    """
    Schema de actualización de ejemplo.

    Returns:
        MockUpdateSchema instance
    """
    return MockUpdateSchema(name="Updated Company")


@pytest.fixture
def sample_product_create_schema(sample_family_type):
    """
    Schema de creación de producto de ejemplo.

    Args:
        sample_family_type: FamilyType fixture

    Returns:
        MockProductCreateSchema instance
    """
    return MockProductCreateSchema(
        product_type="article",
        reference="PROD-001",
        designation_es="Producto Test",
        family_type_id=sample_family_type.id,
        cost_price=Decimal("100.00"),
        sale_price=Decimal("150.00"),
    )


# ===================== HELPER FUNCTIONS =====================


def create_mock_entities(count: int, model_class=Company) -> list:
    """
    Crea una lista de entidades mock para testing.

    Args:
        count: Número de entidades a crear
        model_class: Clase del modelo

    Returns:
        Lista de entidades mock
    """
    entities = []
    for i in range(count):
        entity = MagicMock(spec=model_class)
        entity.id = i + 1
        entity.name = f"Entity {i + 1}"
        entity.is_active = True
        entities.append(entity)
    return entities
