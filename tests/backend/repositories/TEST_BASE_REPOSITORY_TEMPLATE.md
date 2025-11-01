# 🎯 TEMPLATE MAESTRO - Tests de Repositories

Este documento contiene el template completo para crear tests de repositories.
Úsalo como base para generar tests rápidamente.

## 📁 Estructura de Archivos

```
tests/backend/repositories/
├── conftest.py ✅ (Ya creado)
├── test_base_repository.py ⭐ (Template maestro - crear primero)
├── core/
│   ├── test_company_repository.py (Copiar y adaptar template)
│   ├── test_product_repository.py (Copiar y adaptar template)
│   └── ... (resto de repositories core)
├── business/
│   └── ... (repositories business)
└── lookups/
    └── ... (repositories lookups)
```

## 🔧 PATRÓN DE TESTS - BaseRepository

### Cobertura Completa (~30 tests)

**1. CRUD Básico (10 tests)**
- test_get_by_id_existing
- test_get_by_id_not_found
- test_get_all_empty
- test_get_all_with_data
- test_get_all_with_pagination
- test_create_valid_entity
- test_update_existing_entity
- test_update_non_existing_entity_raises_error
- test_delete_existing_entity
- test_delete_non_existing_entity_raises_error

**2. Soft Delete (3 tests)**
- test_soft_delete_marks_as_deleted
- test_soft_delete_not_found_raises_error
- test_soft_delete_without_mixin_raises_error

**3. Utility Methods (4 tests)**
- test_count_empty
- test_count_with_data
- test_exists_true
- test_exists_false

**4. Transaction Behavior (5 tests)**
- test_create_flushes_without_commit
- test_update_flushes_without_commit
- test_delete_flushes_without_commit
- test_multiple_operations_in_transaction
- test_rollback_after_error

**5. Edge Cases (8 tests)**
- test_get_all_limit_zero
- test_get_all_skip_beyond_total
- test_create_with_duplicate_unique_field
- test_update_with_invalid_id
- test_pagination_last_page_partial
- test_concurrent_create_operations
- test_large_batch_operations
- test_null_session_handling

## 📝 EJEMPLO COMPLETO - CompanyRepository

### Métodos Custom a Testear

Además del CRUD base, cada repository tiene métodos específicos:

**CompanyRepository:**
- get_by_trigram()
- search_by_name()
- get_with_branches()
- get_with_ruts()
- get_with_relations()
- get_active_companies()
- get_by_type()

### Tests Adicionales (~20 tests)

**Búsquedas Específicas:**
- test_get_by_trigram_existing
- test_get_by_trigram_not_found
- test_get_by_trigram_case_insensitive
- test_search_by_name_partial_match
- test_search_by_name_no_results
- test_search_by_name_multiple_results
- test_search_by_name_case_insensitive

**Eager Loading:**
- test_get_with_branches_loads_relationships
- test_get_with_branches_empty_list
- test_get_with_ruts_loads_relationships
- test_get_with_relations_loads_all

**Filtros:**
- test_get_active_companies_only
- test_get_active_companies_pagination
- test_get_by_type_customer
- test_get_by_type_supplier
- test_get_by_type_empty

**Performance:**
- test_search_performance_with_large_dataset
- test_eager_loading_n_plus_1_prevention

## 🚀 CÓDIGO EJEMPLO COMPLETO

```python
\"\"\"
Tests para BaseRepository.

Valida funcionalidad CRUD básica que todos los repositories heredan.
\"\"\"

import pytest
from sqlalchemy.exc import IntegrityError

from src.backend.repositories.base import BaseRepository
from src.backend.models.core.companies import Company
from src.backend.exceptions.repository import NotFoundException


class TestBaseRepositoryGetById:
    \"\"\"Tests para get_by_id().\"\"\"

    def test_get_by_id_existing(self, base_repository, sample_company, session):
        \"\"\"Test que obtiene entidad existente por ID.\"\"\"
        # Arrange - sample_company ya está en DB

        # Act
        result = base_repository.get_by_id(sample_company.id)

        # Assert
        assert result is not None
        assert result.id == sample_company.id
        assert result.name == sample_company.name

    def test_get_by_id_not_found(self, base_repository):
        \"\"\"Test que retorna None cuando ID no existe.\"\"\"
        # Act
        result = base_repository.get_by_id(99999)

        # Assert
        assert result is None


class TestBaseRepositoryGetAll:
    \"\"\"Tests para get_all().\"\"\"

    def test_get_all_empty(self, base_repository):
        \"\"\"Test que retorna lista vacía cuando no hay datos.\"\"\"
        # Act
        result = base_repository.get_all()

        # Assert
        assert result == []
        assert isinstance(result, list)

    def test_get_all_with_data(self, base_repository, create_test_companies, session):
        \"\"\"Test que retorna todas las entidades.\"\"\"
        # Arrange - crear 5 companies
        companies = create_test_companies(5)

        # Act
        result = base_repository.get_all()

        # Assert
        assert len(result) == 5

    def test_get_all_with_pagination(self, base_repository, create_test_companies, session):
        \"\"\"Test que pagination funciona correctamente.\"\"\"
        # Arrange - crear 10 companies
        create_test_companies(10)

        # Act - obtener segunda página (skip=5, limit=3)
        result = base_repository.get_all(skip=5, limit=3)

        # Assert
        assert len(result) == 3


class TestBaseRepositoryCreate:
    \"\"\"Tests para create().\"\"\"

    def test_create_valid_entity(self, base_repository, sample_company_type, session):
        \"\"\"Test que crea entidad válida.\"\"\"
        # Arrange
        company = Company(
            name="New Company",
            trigram="NEW",
            company_type_id=sample_company_type.id
        )

        # Act
        result = base_repository.create(company)
        session.commit()  # Commit manual

        # Assert
        assert result.id is not None
        assert result.name == "New Company"

    def test_create_flushes_without_commit(self, base_repository, sample_company_type, session):
        \"\"\"Test que create hace flush pero NO commit.\"\"\"
        # Arrange
        company = Company(
            name="Test Company",
            trigram="TST",
            company_type_id=sample_company_type.id
        )

        # Act
        result = base_repository.create(company)
        # NO hacemos commit

        # Assert - tiene ID pero no está committed
        assert result.id is not None

        # Rollback para verificar
        session.rollback()

        # Verify - después de rollback, no existe
        retrieved = base_repository.get_by_id(result.id)
        assert retrieved is None


class TestBaseRepositoryUpdate:
    \"\"\"Tests para update().\"\"\"

    def test_update_existing_entity(self, base_repository, sample_company, session):
        \"\"\"Test que actualiza entidad existente.\"\"\"
        # Arrange
        original_name = sample_company.name
        sample_company.name = "Updated Name"

        # Act
        result = base_repository.update(sample_company)
        session.commit()

        # Assert
        assert result.name == "Updated Name"
        assert result.name != original_name

    def test_update_non_existing_entity_raises_error(self, base_repository, sample_company_type, session):
        \"\"\"Test que actualizar entidad inexistente lanza error.\"\"\"
        # Arrange - crear company SIN guardar en DB
        company = Company(
            name="Non Existing",
            trigram="NEX",
            company_type_id=sample_company_type.id
        )
        company.id = 99999  # ID que no existe

        # Act & Assert
        with pytest.raises(NotFoundException):
            base_repository.update(company)


class TestBaseRepositoryDelete:
    \"\"\"Tests para delete() y soft_delete().\"\"\"

    def test_delete_existing_entity(self, base_repository, sample_company, session):
        \"\"\"Test que elimina entidad existente (hard delete).\"\"\"
        # Arrange
        company_id = sample_company.id

        # Act
        base_repository.delete(company_id)
        session.commit()

        # Assert
        result = base_repository.get_by_id(company_id)
        assert result is None

    def test_delete_non_existing_entity_raises_error(self, base_repository):
        \"\"\"Test que eliminar entidad inexistente lanza error.\"\"\"
        # Act & Assert
        with pytest.raises(NotFoundException):
            base_repository.delete(99999)


class TestBaseRepositoryUtility:
    \"\"\"Tests para métodos utilitarios.\"\"\"

    def test_count_empty(self, base_repository):
        \"\"\"Test count cuando no hay datos.\"\"\"
        # Act
        count = base_repository.count()

        # Assert
        assert count == 0

    def test_count_with_data(self, base_repository, create_test_companies, session):
        \"\"\"Test count con datos.\"\"\"
        # Arrange
        create_test_companies(7)

        # Act
        count = base_repository.count()

        # Assert
        assert count == 7

    def test_exists_true(self, base_repository, sample_company):
        \"\"\"Test exists retorna True para ID existente.\"\"\"
        # Act
        result = base_repository.exists(sample_company.id)

        # Assert
        assert result is True

    def test_exists_false(self, base_repository):
        \"\"\"Test exists retorna False para ID inexistente.\"\"\"
        # Act
        result = base_repository.exists(99999)

        # Assert
        assert result is False
```

## 📚 CÓMO USAR ESTE TEMPLATE

### Paso 1: Copiar Template Base
```bash
cp test_base_repository_TEMPLATE.py test_base_repository.py
```

### Paso 2: Para Repositories Específicos

1. Copiar tests básicos del template
2. Reemplazar `Company` con tu modelo
3. Agregar tests para métodos custom

**Ejemplo para ProductRepository:**

```python
class TestProductRepositoryGetByReference:
    \"\"\"Tests para get_by_reference() - método específico.\"\"\"

    def test_get_by_reference_existing(self, product_repository, sample_product):
        # Act
        result = product_repository.get_by_reference(sample_product.reference)

        # Assert
        assert result is not None
        assert result.id == sample_product.id

    def test_get_by_reference_case_insensitive(self, product_repository, sample_product):
        # Act - buscar en lowercase
        result = product_repository.get_by_reference(sample_product.reference.lower())

        # Assert - debe encontrar (reference se convierte a uppercase)
        assert result is not None

    def test_get_by_reference_not_found(self, product_repository):
        # Act
        result = product_repository.get_by_reference("NONEXISTENT")

        # Assert
        assert result is None
```

## 🎯 SIGUIENTE PASO

**¿Quieres que implemente el archivo completo `test_base_repository.py`?**

O prefieres que:
1. 📝 Continue con templates para Services
2. 🎨 Cree un generador automático de tests
3. 🚀 Implemente un repository específico completo (ej: CompanyRepository)

**¡Dime cómo prefieres continuar y lo implemento!**
