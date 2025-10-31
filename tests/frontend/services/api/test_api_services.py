"""
Tests para los servicios API del frontend.

NOTA: Estos tests requieren que el backend FastAPI esté ejecutándose en localhost:8000
"""

import pytest
from src.frontend.services.api import (
    company_api,
    product_api,
    lookup_api,
    APIException,
    NotFoundException,
    ValidationException,
)


class TestCompanyAPI:
    """Tests para el servicio de Companies."""

    @pytest.mark.asyncio
    async def test_get_all_companies(self):
        """Test obtener todas las empresas."""
        companies = await company_api.get_all(skip=0, limit=10)
        assert isinstance(companies, list)

    @pytest.mark.asyncio
    async def test_get_active_companies(self):
        """Test obtener empresas activas."""
        companies = await company_api.get_active()
        assert isinstance(companies, list)
        # Todas deben estar activas
        for company in companies:
            assert company.get("is_active") is True

    @pytest.mark.asyncio
    async def test_get_company_by_id_not_found(self):
        """Test obtener empresa que no existe."""
        with pytest.raises(NotFoundException):
            await company_api.get_by_id(999999)

    @pytest.mark.asyncio
    async def test_search_companies(self):
        """Test buscar empresas por nombre."""
        results = await company_api.search("test")
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_create_update_delete_company(self):
        """Test ciclo completo de crear, actualizar y eliminar empresa."""
        # Crear
        company_data = {
            "name": "Test Company",
            "company_type_id": 1,
            "country_id": 1,
            "nit": "900000000-0",
            "email": "test@example.com",
            "is_active": True,
        }
        created = await company_api.create(company_data)
        assert created["id"] is not None
        assert created["name"] == "Test Company"

        # Actualizar
        updated = await company_api.update(
            created["id"], {"name": "Test Company Updated"}
        )
        assert updated["name"] == "Test Company Updated"

        # Eliminar
        success = await company_api.delete(created["id"])
        assert success is True

        # Verificar que ya no existe
        with pytest.raises(NotFoundException):
            await company_api.get_by_id(created["id"])

    @pytest.mark.asyncio
    async def test_create_company_validation_error(self):
        """Test crear empresa con datos inválidos."""
        invalid_data = {
            "name": "",  # Nombre vacío
            "company_type_id": 999,  # Tipo no existe
            "country_id": 999,  # País no existe
        }
        with pytest.raises((ValidationException, APIException)):
            await company_api.create(invalid_data)


class TestProductAPI:
    """Tests para el servicio de Products."""

    @pytest.mark.asyncio
    async def test_get_all_products(self):
        """Test obtener todos los productos."""
        products = await product_api.get_all(skip=0, limit=10)
        assert isinstance(products, list)

    @pytest.mark.asyncio
    async def test_get_products_by_type(self):
        """Test obtener productos por tipo."""
        articles = await product_api.get_by_type("ARTICLE")
        assert isinstance(articles, list)

        nomenclatures = await product_api.get_by_type("NOMENCLATURE")
        assert isinstance(nomenclatures, list)

    @pytest.mark.asyncio
    async def test_get_product_by_id_not_found(self):
        """Test obtener producto que no existe."""
        with pytest.raises(NotFoundException):
            await product_api.get_by_id(999999)

    @pytest.mark.asyncio
    async def test_create_update_delete_product(self):
        """Test ciclo completo de crear, actualizar y eliminar producto."""
        # Crear artículo
        article_data = {
            "code": f"TEST-{pytest.__version__}",  # Código único
            "name": "Test Article",
            "product_type": "ARTICLE",
            "unit_id": 1,
            "description": "Test description",
            "is_active": True,
        }
        created = await product_api.create(article_data)
        assert created["id"] is not None
        assert created["code"] == article_data["code"]

        # Actualizar
        updated = await product_api.update(
            created["id"], {"name": "Test Article Updated"}
        )
        assert updated["name"] == "Test Article Updated"

        # Eliminar
        success = await product_api.delete(created["id"])
        assert success is True

    @pytest.mark.asyncio
    async def test_add_remove_component(self):
        """Test añadir y eliminar componente de BOM."""
        # Crear artículo componente
        article_data = {
            "code": f"COMP-{pytest.__version__}",
            "name": "Component Article",
            "product_type": "ARTICLE",
            "unit_id": 1,
        }
        article = await product_api.create(article_data)

        # Crear nomenclatura
        nomenclature_data = {
            "code": f"NOM-{pytest.__version__}",
            "name": "Test Nomenclature",
            "product_type": "NOMENCLATURE",
            "unit_id": 1,
        }
        nomenclature = await product_api.create(nomenclature_data)

        # Añadir componente
        component_data = {
            "component_product_id": article["id"],
            "quantity": 2.5,
            "unit_id": 1,
        }
        component = await product_api.add_component(nomenclature["id"], component_data)
        assert component["id"] is not None

        # Eliminar componente
        success = await product_api.remove_component(
            nomenclature["id"], component["id"]
        )
        assert success is True

        # Limpiar
        await product_api.delete(nomenclature["id"])
        await product_api.delete(article["id"])


class TestLookupAPI:
    """Tests para el servicio de Lookups."""

    @pytest.mark.asyncio
    async def test_get_company_types(self):
        """Test obtener tipos de empresa."""
        company_types = await lookup_api.get_company_types()
        assert isinstance(company_types, list)
        assert len(company_types) > 0
        # Verificar estructura
        for ct in company_types:
            assert "id" in ct
            assert "name" in ct

    @pytest.mark.asyncio
    async def test_get_countries(self):
        """Test obtener países."""
        countries = await lookup_api.get_countries()
        assert isinstance(countries, list)
        assert len(countries) > 0
        # Verificar estructura
        for country in countries:
            assert "id" in country
            assert "name" in country
            assert "code" in country

    @pytest.mark.asyncio
    async def test_get_units(self):
        """Test obtener unidades de medida."""
        units = await lookup_api.get_units()
        assert isinstance(units, list)
        assert len(units) > 0
        # Verificar estructura
        for unit in units:
            assert "id" in unit
            assert "name" in unit
            assert "symbol" in unit


class TestErrorHandling:
    """Tests para manejo de errores."""

    @pytest.mark.asyncio
    async def test_not_found_exception(self):
        """Test excepción NotFoundException."""
        with pytest.raises(NotFoundException) as exc_info:
            await company_api.get_by_id(999999)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_api_exception_attributes(self):
        """Test atributos de APIException."""
        try:
            await company_api.get_by_id(999999)
        except APIException as e:
            assert hasattr(e, "message")
            assert hasattr(e, "status_code")
            assert hasattr(e, "details")
            assert e.status_code == 404


@pytest.mark.asyncio
async def test_context_manager():
    """Test uso de servicios como context managers."""
    async with company_api as service:
        companies = await service.get_all(limit=5)
        assert isinstance(companies, list)
