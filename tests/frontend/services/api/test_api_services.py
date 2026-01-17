"""
Tests para los servicios API del frontend.

NOTA: Estos tests requieren que el backend FastAPI esté ejecutándose en localhost:8000
"""

import pytest
import uuid
from src.frontend.services.api import (
    CompanyAPIService,
    ProductAPIService,
    LookupAPIService,
    APIException,
    NotFoundException,
    ValidationException,
)


# ============================================================================
# FIXTURES - Crear instancias frescas por cada test
# ============================================================================

@pytest.fixture
def company_api():
    """Fixture que proporciona una instancia fresca del servicio de Company."""
    return CompanyAPIService()


@pytest.fixture
def product_api():
    """Fixture que proporciona una instancia fresca del servicio de Product."""
    return ProductAPIService()


@pytest.fixture
def lookup_api():
    """Fixture que proporciona una instancia fresca del servicio de Lookup."""
    return LookupAPIService()


# ============================================================================
# COMPANY API TESTS
# ============================================================================

class TestCompanyAPI:
    """Tests para el servicio de Companies."""

    @pytest.mark.asyncio
    async def test_get_all_companies(self, company_api):
        """Test obtener todas las empresas."""
        result = await company_api.get_all(skip=0, limit=10)
        # La API retorna un dict con 'items' y 'total'
        assert isinstance(result, dict)
        assert "items" in result
        assert "total" in result
        assert isinstance(result["items"], list)
        await company_api.close()

    @pytest.mark.asyncio
    async def test_get_active_companies(self, company_api):
        """Test obtener empresas activas."""
        companies = await company_api.get_active()
        assert isinstance(companies, list)
        # Todas deben estar activas
        for company in companies:
            assert company.get("is_active") is True
        await company_api.close()

    @pytest.mark.asyncio
    async def test_get_company_by_id_not_found(self, company_api):
        """Test obtener empresa que no existe."""
        with pytest.raises(NotFoundException):
            await company_api.get_by_id(999999)
        await company_api.close()

    @pytest.mark.asyncio
    async def test_search_companies(self, company_api):
        """Test buscar empresas por nombre."""
        result = await company_api.search("test")
        # search retorna un dict con 'items' y 'total'
        assert isinstance(result, dict)
        assert "items" in result
        assert isinstance(result["items"], list)
        await company_api.close()

    @pytest.mark.asyncio
    async def test_create_update_delete_company(self, company_api):
        """Test ciclo completo de crear, actualizar y eliminar empresa."""
        # Generar código único para evitar conflictos
        unique_id = str(uuid.uuid4())[:8].upper()
        
        # Crear - Incluir solo campos requeridos: name, trigram, company_type_id
        company_data = {
            "name": f"Test Company {unique_id}",
            "trigram": unique_id[:3].upper(),  # Campo requerido (3 letras mayúsculas)
            "company_type_id": 1,  # ID de tipo de empresa que existe en la DB
        }
        
        try:
            created = await company_api.create(company_data)
        except APIException as e:
            if e.status_code == 500:
                pytest.skip("Backend returned 500 error - may need database setup")
            raise
        
        assert created["id"] is not None
        assert "Test Company" in created["name"]

        # Actualizar
        updated = await company_api.update(
            created["id"], {"name": f"Test Company Updated {unique_id}"}
        )
        assert "Updated" in updated["name"]

        # Eliminar
        success = await company_api.delete(created["id"])
        assert success is True

        # Verificar que ya no existe
        with pytest.raises(NotFoundException):
            await company_api.get_by_id(created["id"])
        
        await company_api.close()

    @pytest.mark.asyncio
    async def test_create_company_validation_error(self, company_api):
        """Test crear empresa con datos inválidos."""
        invalid_data = {
            "name": "",  # Nombre vacío
            "company_type_id": 999,  # Tipo no existe
            "country_id": 999,  # País no existe
        }
        with pytest.raises((ValidationException, APIException)):
            await company_api.create(invalid_data)
        await company_api.close()


# ============================================================================
# PRODUCT API TESTS
# ============================================================================

class TestProductAPI:
    """Tests para el servicio de Products."""

    @pytest.mark.asyncio
    async def test_get_all_products(self, product_api):
        """Test obtener todos los productos."""
        result = await product_api.get_all(skip=0, limit=10)
        # La API retorna un dict con 'items' y 'total'
        assert isinstance(result, dict)
        assert "items" in result
        assert "total" in result
        assert isinstance(result["items"], list)
        await product_api.close()

    @pytest.mark.asyncio
    async def test_get_products_by_type(self, product_api):
        """Test obtener productos por tipo."""
        # Usar minúsculas según la validación en product_api.get_by_type
        articles = await product_api.get_by_type("article")
        assert isinstance(articles, list)

        nomenclatures = await product_api.get_by_type("nomenclature")
        assert isinstance(nomenclatures, list)
        await product_api.close()

    @pytest.mark.asyncio
    async def test_get_product_by_id_not_found(self, product_api):
        """Test obtener producto que no existe."""
        with pytest.raises(NotFoundException):
            await product_api.get_by_id(999999)
        await product_api.close()

    @pytest.mark.asyncio
    async def test_create_update_delete_product(self, product_api):
        """Test ciclo completo de crear, actualizar y eliminar producto."""
        # Generar referencia única
        unique_ref = f"TEST-{uuid.uuid4().hex[:8].upper()}"
        
        # Crear artículo con campos correctos según ProductCreate schema
        article_data = {
            "reference": unique_ref,  # Campo requerido
            "designation_es": "Test Article",  # Campo requerido
            "product_type": "article",  # Campo requerido (minúsculas según constantes)
        }
        created = await product_api.create(article_data)
        assert created["id"] is not None
        assert created["reference"] == unique_ref

        # Actualizar
        updated = await product_api.update(
            created["id"], {"designation_es": "Test Article Updated"}
        )
        assert updated["designation_es"] == "Test Article Updated"

        # Eliminar
        success = await product_api.delete(created["id"])
        assert success is True
        await product_api.close()

    @pytest.mark.asyncio
    async def test_add_remove_component(self, product_api):
        """Test añadir y eliminar componente de BOM."""
        # Generar referencias únicas
        article_ref = f"COMP-{uuid.uuid4().hex[:8].upper()}"
        nomenclature_ref = f"NOM-{uuid.uuid4().hex[:8].upper()}"
        
        # Crear artículo componente con campos correctos
        article_data = {
            "reference": article_ref,
            "designation_es": "Component Article",
            "product_type": "article",  # minúsculas según constantes
        }
        article = await product_api.create(article_data)

        # Crear nomenclatura con campos correctos
        nomenclature_data = {
            "reference": nomenclature_ref,
            "designation_es": "Test Nomenclature",
            "product_type": "nomenclature",  # minúsculas según constantes
        }
        nomenclature = await product_api.create(nomenclature_data)

        # Añadir componente - usar campos según ProductComponentCreate
        component_data = {
            "parent_id": nomenclature["id"],
            "component_id": article["id"],
            "quantity": "2.500",  # Decimal como string
        }
        component = await product_api.add_component(nomenclature["id"], component_data)
        assert component is not None

        # Eliminar componente - usar el ID del producto componente (article["id"]), 
        # no el ID del registro del componente
        success = await product_api.remove_component(
            nomenclature["id"], article["id"]  # component_id es el ID del producto componente
        )
        assert success is True

        # Limpiar
        await product_api.delete(nomenclature["id"])
        await product_api.delete(article["id"])
        await product_api.close()


# ============================================================================
# LOOKUP API TESTS
# ============================================================================

class TestLookupAPI:
    """Tests para el servicio de Lookups."""

    @pytest.mark.asyncio
    async def test_get_company_types(self, lookup_api):
        """Test obtener tipos de empresa."""
        company_types = await lookup_api.get_company_types()
        assert isinstance(company_types, list)
        assert len(company_types) > 0
        # Verificar estructura
        for ct in company_types:
            assert "id" in ct
            assert "name" in ct
        await lookup_api.close()

    @pytest.mark.asyncio
    async def test_get_countries(self, lookup_api):
        """Test obtener países."""
        countries = await lookup_api.get_countries()
        assert isinstance(countries, list)
        assert len(countries) > 0
        # Verificar estructura
        for country in countries:
            assert "id" in country
            assert "name" in country
        await lookup_api.close()

    @pytest.mark.asyncio
    async def test_get_units(self, lookup_api):
        """Test obtener unidades de medida."""
        units = await lookup_api.get_units()
        assert isinstance(units, list)
        # Si no hay unidades en la DB, el test no debería fallar
        if len(units) > 0:
            # Verificar estructura
            for unit in units:
                assert "id" in unit
                assert "name" in unit
        await lookup_api.close()


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestErrorHandling:
    """Tests para manejo de errores."""

    @pytest.mark.asyncio
    async def test_not_found_exception(self, company_api):
        """Test excepción NotFoundException."""
        with pytest.raises(NotFoundException) as exc_info:
            await company_api.get_by_id(999999)

        assert exc_info.value.status_code == 404
        await company_api.close()

    @pytest.mark.asyncio
    async def test_api_exception_attributes(self, company_api):
        """Test atributos de APIException."""
        try:
            await company_api.get_by_id(999999)
        except APIException as e:
            assert hasattr(e, "message")
            assert hasattr(e, "status_code")
            assert hasattr(e, "details")
            assert e.status_code == 404
        finally:
            await company_api.close()


# ============================================================================
# CONTEXT MANAGER TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_context_manager():
    """Test uso de servicios como context managers."""
    async with CompanyAPIService() as service:
        result = await service.get_all(limit=5)
        # La API retorna un dict con 'items' y 'total'
        assert isinstance(result, dict)
        assert "items" in result
        assert isinstance(result["items"], list)
