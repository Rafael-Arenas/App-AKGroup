"""
Tests para ProductRepository y ProductComponentRepository.

Valida funcionalidad CRUD base más métodos específicos de Product y BOM.
"""

import pytest
from decimal import Decimal
from sqlalchemy.exc import IntegrityError

from src.backend.models.core.products import Product, ProductComponent, ProductType
from src.backend.exceptions.repository import NotFoundException


# ===================== PRODUCT REPOSITORY TESTS =====================


class TestProductRepositoryGetByReference:
    """Tests para get_by_reference()."""

    def test_get_by_reference_existing(
        self, product_repository, sample_product, session
    ):
        """Test que obtiene producto existente por referencia."""
        # Act
        result = product_repository.get_by_reference(sample_product.reference)

        # Assert
        assert result is not None
        assert result.id == sample_product.id
        assert result.reference == sample_product.reference

    def test_get_by_reference_not_found(self, product_repository):
        """Test que retorna None cuando referencia no existe."""
        # Act
        result = product_repository.get_by_reference("NONEXIST")

        # Assert
        assert result is None

    def test_get_by_reference_case_insensitive(
        self, product_repository, sample_product, session
    ):
        """Test que búsqueda por referencia es case insensitive."""
        # Act - buscar en lowercase
        result = product_repository.get_by_reference(sample_product.reference.lower())

        # Assert
        assert result is not None
        assert result.id == sample_product.id


class TestProductRepositorySearch:
    """Tests para search()."""

    def test_search_by_reference(self, product_repository, sample_product, session):
        """Test que busca por referencia."""
        # Act - buscar parte de la referencia
        results = product_repository.search(sample_product.reference[:4])

        # Assert
        assert len(results) >= 1
        assert any(p.id == sample_product.id for p in results)

    def test_search_by_designation_es(
        self, product_repository, sample_product, session
    ):
        """Test que busca por designación en español."""
        # Act - buscar parte de la designación
        results = product_repository.search("Producto")

        # Assert
        assert len(results) >= 1
        assert any(p.id == sample_product.id for p in results)

    def test_search_by_designation_en(
        self, product_repository, sample_family_type, session
    ):
        """Test que busca por designación en inglés."""
        # Arrange - crear producto con designación en inglés
        product = Product(
            product_type=ProductType.ARTICLE,
            reference="SEARCH-EN",
            designation_en="English Product",
            family_type_id=sample_family_type.id,
        )
        product_repository.create(product)
        session.commit()

        # Act
        results = product_repository.search("English")

        # Assert
        assert len(results) >= 1
        assert any(p.reference == "SEARCH-EN" for p in results)

    def test_search_no_results(self, product_repository):
        """Test que retorna lista vacía sin matches."""
        # Act
        results = product_repository.search("NONEXISTENTKEYWORD12345")

        # Assert
        assert results == []

    def test_search_case_insensitive(self, product_repository, sample_product, session):
        """Test que búsqueda es case insensitive."""
        # Act - buscar en lowercase
        results = product_repository.search(sample_product.reference.lower())

        # Assert
        assert len(results) >= 1
        assert any(p.id == sample_product.id for p in results)

    def test_search_multiple_results(
        self, product_repository, create_test_products, session
    ):
        """Test que encuentra múltiples productos."""
        # Arrange - crear 5 productos
        create_test_products(5)

        # Act - buscar "Producto" debe encontrar todos
        results = product_repository.search("Producto")

        # Assert
        assert len(results) >= 5


class TestProductRepositoryGetWithComponents:
    """Tests para get_with_components()."""

    def test_get_with_components_loads_bom(
        self,
        product_repository,
        product_component_repository,
        sample_family_type,
        session,
    ):
        """Test que carga componentes con eager loading."""
        # Arrange - crear producto nomenclatura con componentes
        parent = Product(
            product_type=ProductType.NOMENCLATURE,
            reference="PARENT",
            designation_es="Producto Padre",
            family_type_id=sample_family_type.id,
        )
        product_repository.create(parent)

        # Crear componentes
        comp1 = Product(
            product_type=ProductType.ARTICLE,
            reference="COMP1",
            designation_es="Componente 1",
            family_type_id=sample_family_type.id,
        )
        comp2 = Product(
            product_type=ProductType.ARTICLE,
            reference="COMP2",
            designation_es="Componente 2",
            family_type_id=sample_family_type.id,
        )
        product_repository.create(comp1)
        product_repository.create(comp2)

        # Agregar a BOM
        bom1 = ProductComponent(
            parent_id=parent.id,
            component_id=comp1.id,
            quantity=Decimal("2.0"),
        )
        bom2 = ProductComponent(
            parent_id=parent.id,
            component_id=comp2.id,
            quantity=Decimal("3.5"),
        )
        product_component_repository.create(bom1)
        product_component_repository.create(bom2)
        session.commit()

        # Act
        result = product_repository.get_with_components(parent.id)

        # Assert
        assert result is not None
        assert len(result.components) == 2
        assert result.components[0].component is not None
        assert result.components[1].component is not None

    def test_get_with_components_empty_bom(
        self, product_repository, sample_product, session
    ):
        """Test que retorna producto con BOM vacío."""
        # Act
        result = product_repository.get_with_components(sample_product.id)

        # Assert
        assert result is not None
        assert result.components == []

    def test_get_with_components_not_found(self, product_repository):
        """Test que retorna None si producto no existe."""
        # Act
        result = product_repository.get_with_components(99999)

        # Assert
        assert result is None


class TestProductRepositoryGetActiveProducts:
    """Tests para get_active_products()."""

    def test_get_active_products_only(
        self, product_repository, create_test_products, session
    ):
        """Test que retorna solo productos activos."""
        # Arrange - crear 5 productos
        products = create_test_products(5)

        # Marcar 2 como inactivos
        products[1].is_active = False
        products[3].is_active = False
        session.commit()

        # Act
        results = product_repository.get_active_products()

        # Assert - verificar que los activos están
        active_count = len([p for p in results if p.id in [prod.id for prod in products]])
        assert active_count == 3
        assert all(p.is_active for p in results)

    def test_get_active_products_with_limit(
        self, product_repository, create_test_products, session
    ):
        """Test que limit funciona correctamente."""
        # Arrange - crear 10 productos activos
        create_test_products(10)

        # Act - limitar a 5
        results = product_repository.get_active_products(limit=5)

        # Assert
        assert len(results) == 5
        assert all(p.is_active for p in results)

    def test_get_active_products_pagination(
        self, product_repository, create_test_products, session
    ):
        """Test que pagination funciona."""
        # Arrange - crear 10 productos
        products = create_test_products(10)
        product_ids = [p.id for p in products]

        # Act - skip 5, obtener el resto
        results = product_repository.get_active_products(skip=5, limit=10)

        # Assert
        results_from_created = [p for p in results if p.id in product_ids]
        assert len(results_from_created) == 5
        assert all(p.is_active for p in results)


class TestProductRepositoryGetByType:
    """Tests para get_by_type()."""

    def test_get_by_type_article(
        self, product_repository, sample_product, session
    ):
        """Test que filtra productos tipo ARTICLE."""
        # Act
        results = product_repository.get_by_type(ProductType.ARTICLE)

        # Assert
        assert len(results) >= 1
        assert all(p.product_type == ProductType.ARTICLE for p in results)
        assert any(p.id == sample_product.id for p in results)

    def test_get_by_type_nomenclature(
        self, product_repository, sample_family_type, session
    ):
        """Test que filtra productos tipo NOMENCLATURE."""
        # Arrange - crear nomenclatura
        nomenclature = Product(
            product_type=ProductType.NOMENCLATURE,
            reference="NOMENC",
            designation_es="Nomenclatura",
            family_type_id=sample_family_type.id,
        )
        product_repository.create(nomenclature)
        session.commit()

        # Act
        results = product_repository.get_by_type(ProductType.NOMENCLATURE)

        # Assert
        assert len(results) >= 1
        assert all(p.product_type == ProductType.NOMENCLATURE for p in results)
        assert any(p.id == nomenclature.id for p in results)

    def test_get_by_type_with_pagination(
        self, product_repository, create_test_products, session
    ):
        """Test que pagination funciona con filtro de tipo."""
        # Arrange - crear 10 productos tipo ARTICLE
        products = create_test_products(10)
        product_ids = [p.id for p in products]

        # Act
        results = product_repository.get_by_type(ProductType.ARTICLE, skip=3, limit=10)

        # Assert
        results_from_created = [p for p in results if p.id in product_ids]
        assert len(results_from_created) == 7


class TestProductRepositoryGetLowStock:
    """Tests para get_low_stock()."""

    def test_get_low_stock_filters_correctly(
        self, product_repository, sample_family_type, session
    ):
        """Test que encuentra productos con stock bajo."""
        # Arrange - crear productos con stock bajo
        low_stock_products = []
        for i in range(3):
            product = Product(
                product_type=ProductType.ARTICLE,
                reference=f"LOW-{i}",
                designation_es=f"Low Stock {i}",
                family_type_id=sample_family_type.id,
                stock_quantity=Decimal("5.0"),
                minimum_stock=Decimal("10.0"),
                is_active=True,
            )
            created = product_repository.create(product)
            low_stock_products.append(created)

        # Crear producto con stock OK
        ok_product = Product(
            product_type=ProductType.ARTICLE,
            reference="OK",
            designation_es="Stock OK",
            family_type_id=sample_family_type.id,
            stock_quantity=Decimal("15.0"),
            minimum_stock=Decimal("10.0"),
            is_active=True,
        )
        product_repository.create(ok_product)
        session.commit()

        # Act
        results = product_repository.get_low_stock()

        # Assert - verificar que los productos con stock bajo están
        low_stock_ids = [p.id for p in low_stock_products]
        found_low_stock = [p for p in results if p.id in low_stock_ids]
        assert len(found_low_stock) == 3
        assert ok_product.id not in [p.id for p in results]

    def test_get_low_stock_empty(self, product_repository, sample_family_type, session):
        """Test cuando no hay productos con stock bajo."""
        # Arrange - crear productos con stock OK
        product = Product(
            product_type=ProductType.ARTICLE,
            reference="OKSTOCK",
            designation_es="Stock OK",
            family_type_id=sample_family_type.id,
            stock_quantity=Decimal("100.0"),
            minimum_stock=Decimal("10.0"),
        )
        product_repository.create(product)
        session.commit()

        # Act
        results = product_repository.get_low_stock()

        # Assert - el producto creado NO debe estar
        assert product.id not in [p.id for p in results]

    def test_get_low_stock_ignores_inactive(
        self, product_repository, sample_family_type, session
    ):
        """Test que ignora productos inactivos."""
        # Arrange - crear producto inactivo con stock bajo
        inactive = Product(
            product_type=ProductType.ARTICLE,
            reference="INACTIVE",
            designation_es="Inactive",
            family_type_id=sample_family_type.id,
            stock_quantity=Decimal("1.0"),
            minimum_stock=Decimal("10.0"),
            is_active=False,
        )
        product_repository.create(inactive)
        session.commit()

        # Act
        results = product_repository.get_low_stock()

        # Assert - el producto inactivo NO debe estar
        assert inactive.id not in [p.id for p in results]


class TestProductRepositoryGetByFamily:
    """Tests para get_by_family()."""

    def test_get_by_family_filters_correctly(
        self, product_repository, sample_product, sample_family_type, session
    ):
        """Test que filtra productos por familia."""
        # Act
        results = product_repository.get_by_family(sample_family_type.id)

        # Assert
        assert len(results) >= 1
        assert all(p.family_type_id == sample_family_type.id for p in results)
        assert any(p.id == sample_product.id for p in results)

    def test_get_by_family_empty(self, product_repository):
        """Test que retorna lista vacía si no hay productos de esa familia."""
        # Act
        results = product_repository.get_by_family(99999)

        # Assert
        assert results == []

    def test_get_by_family_with_pagination(
        self, product_repository, create_test_products, sample_family_type, session
    ):
        """Test que pagination funciona con filtro de familia."""
        # Arrange - crear 10 productos de la misma familia
        products = create_test_products(10)
        product_ids = [p.id for p in products]

        # Act
        results = product_repository.get_by_family(
            sample_family_type.id, skip=3, limit=10
        )

        # Assert
        results_from_created = [p for p in results if p.id in product_ids]
        assert len(results_from_created) == 7


# ===================== PRODUCT COMPONENT REPOSITORY TESTS =====================


class TestProductComponentRepositoryGetByParent:
    """Tests para get_by_parent()."""

    def test_get_by_parent_existing(
        self,
        product_repository,
        product_component_repository,
        sample_family_type,
        session,
    ):
        """Test que obtiene componentes de un producto padre."""
        # Arrange - crear producto con componentes
        parent = Product(
            product_type=ProductType.NOMENCLATURE,
            reference="PARENT",
            designation_es="Padre",
            family_type_id=sample_family_type.id,
        )
        product_repository.create(parent)

        comp1 = Product(
            product_type=ProductType.ARTICLE,
            reference="COMP1",
            designation_es="Componente 1",
            family_type_id=sample_family_type.id,
        )
        product_repository.create(comp1)

        bom = ProductComponent(
            parent_id=parent.id,
            component_id=comp1.id,
            quantity=Decimal("2.5"),
        )
        product_component_repository.create(bom)
        session.commit()

        # Act
        results = product_component_repository.get_by_parent(parent.id)

        # Assert
        assert len(results) == 1
        assert results[0].parent_id == parent.id
        assert results[0].component_id == comp1.id
        assert results[0].quantity == Decimal("2.5")

    def test_get_by_parent_empty(self, product_component_repository, sample_product):
        """Test que retorna lista vacía si no hay componentes."""
        # Act
        results = product_component_repository.get_by_parent(sample_product.id)

        # Assert
        assert results == []


class TestProductComponentRepositoryGetByComponent:
    """Tests para get_by_component()."""

    def test_get_by_component_existing(
        self,
        product_repository,
        product_component_repository,
        sample_family_type,
        session,
    ):
        """Test que obtiene dónde se usa un componente."""
        # Arrange - crear componente usado en 2 productos
        component = Product(
            product_type=ProductType.ARTICLE,
            reference="COMP",
            designation_es="Componente",
            family_type_id=sample_family_type.id,
        )
        product_repository.create(component)

        parent1 = Product(
            product_type=ProductType.NOMENCLATURE,
            reference="PARENT1",
            designation_es="Padre 1",
            family_type_id=sample_family_type.id,
        )
        parent2 = Product(
            product_type=ProductType.NOMENCLATURE,
            reference="PARENT2",
            designation_es="Padre 2",
            family_type_id=sample_family_type.id,
        )
        product_repository.create(parent1)
        product_repository.create(parent2)

        bom1 = ProductComponent(
            parent_id=parent1.id,
            component_id=component.id,
            quantity=Decimal("1.0"),
        )
        bom2 = ProductComponent(
            parent_id=parent2.id,
            component_id=component.id,
            quantity=Decimal("3.0"),
        )
        product_component_repository.create(bom1)
        product_component_repository.create(bom2)
        session.commit()

        # Act
        results = product_component_repository.get_by_component(component.id)

        # Assert
        assert len(results) == 2
        assert all(r.component_id == component.id for r in results)
        parent_ids = [r.parent_id for r in results]
        assert parent1.id in parent_ids
        assert parent2.id in parent_ids

    def test_get_by_component_empty(self, product_component_repository, sample_product):
        """Test que retorna lista vacía si componente no se usa."""
        # Act
        results = product_component_repository.get_by_component(sample_product.id)

        # Assert
        assert results == []


class TestProductComponentRepositoryGetComponent:
    """Tests para get_component()."""

    def test_get_component_existing(
        self,
        product_repository,
        product_component_repository,
        sample_family_type,
        session,
    ):
        """Test que obtiene un componente específico."""
        # Arrange
        parent = Product(
            product_type=ProductType.NOMENCLATURE,
            reference="PARENT",
            designation_es="Padre",
            family_type_id=sample_family_type.id,
        )
        component = Product(
            product_type=ProductType.ARTICLE,
            reference="COMP",
            designation_es="Componente",
            family_type_id=sample_family_type.id,
        )
        product_repository.create(parent)
        product_repository.create(component)

        bom = ProductComponent(
            parent_id=parent.id,
            component_id=component.id,
            quantity=Decimal("5.0"),
        )
        product_component_repository.create(bom)
        session.commit()

        # Act
        result = product_component_repository.get_component(parent.id, component.id)

        # Assert
        assert result is not None
        assert result.parent_id == parent.id
        assert result.component_id == component.id
        assert result.quantity == Decimal("5.0")

    def test_get_component_not_found(self, product_component_repository):
        """Test que retorna None si componente no existe."""
        # Act
        result = product_component_repository.get_component(99999, 88888)

        # Assert
        assert result is None


class TestProductComponentRepositoryDeleteComponent:
    """Tests para delete_component()."""

    def test_delete_component_existing(
        self,
        product_repository,
        product_component_repository,
        sample_family_type,
        session,
    ):
        """Test que elimina un componente específico."""
        # Arrange
        parent = Product(
            product_type=ProductType.NOMENCLATURE,
            reference="PARENT",
            designation_es="Padre",
            family_type_id=sample_family_type.id,
        )
        component = Product(
            product_type=ProductType.ARTICLE,
            reference="COMP",
            designation_es="Componente",
            family_type_id=sample_family_type.id,
        )
        product_repository.create(parent)
        product_repository.create(component)

        bom = ProductComponent(
            parent_id=parent.id,
            component_id=component.id,
            quantity=Decimal("1.0"),
        )
        product_component_repository.create(bom)
        session.commit()

        # Act
        product_component_repository.delete_component(parent.id, component.id)
        session.commit()

        # Assert - verificar que fue eliminado
        result = product_component_repository.get_component(parent.id, component.id)
        assert result is None

    def test_delete_component_not_found_raises_error(
        self, product_component_repository
    ):
        """Test que eliminar componente inexistente lanza error."""
        # Act & Assert
        with pytest.raises(NotFoundException):
            product_component_repository.delete_component(99999, 88888)

    def test_delete_component_only_removes_specific(
        self,
        product_repository,
        product_component_repository,
        sample_family_type,
        session,
    ):
        """Test que solo elimina el componente específico."""
        # Arrange - crear producto con 2 componentes
        parent = Product(
            product_type=ProductType.NOMENCLATURE,
            reference="PARENT",
            designation_es="Padre",
            family_type_id=sample_family_type.id,
        )
        comp1 = Product(
            product_type=ProductType.ARTICLE,
            reference="COMP1",
            designation_es="Componente 1",
            family_type_id=sample_family_type.id,
        )
        comp2 = Product(
            product_type=ProductType.ARTICLE,
            reference="COMP2",
            designation_es="Componente 2",
            family_type_id=sample_family_type.id,
        )
        product_repository.create(parent)
        product_repository.create(comp1)
        product_repository.create(comp2)

        bom1 = ProductComponent(
            parent_id=parent.id, component_id=comp1.id, quantity=Decimal("1.0")
        )
        bom2 = ProductComponent(
            parent_id=parent.id, component_id=comp2.id, quantity=Decimal("2.0")
        )
        product_component_repository.create(bom1)
        product_component_repository.create(bom2)
        session.commit()

        # Act - eliminar solo comp1
        product_component_repository.delete_component(parent.id, comp1.id)
        session.commit()

        # Assert
        assert (
            product_component_repository.get_component(parent.id, comp1.id) is None
        )
        assert (
            product_component_repository.get_component(parent.id, comp2.id) is not None
        )
