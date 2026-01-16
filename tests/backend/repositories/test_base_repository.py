"""
Tests para BaseRepository.

Valida la funcionalidad CRUD genérica que todos los repositories heredan.
Estos tests aseguran que las operaciones básicas de acceso a datos funcionan
correctamente antes de probar repositories específicos.

Test Coverage:
    - CRUD operations (get_by_id, get_all, create, update, delete)
    - Soft delete functionality
    - Pagination (skip, limit)
    - Utility methods (count, exists)
    - Transaction behavior (flush without commit)
    - Error handling (NotFoundException)
    - Edge cases
"""

import pytest
from sqlalchemy.exc import IntegrityError

from src.backend.repositories.base import BaseRepository
from src.backend.models.core.companies import Company
from src.backend.exceptions.repository import NotFoundException


# ============= GET BY ID TESTS =============


class TestBaseRepositoryGetById:
    """Tests para BaseRepository.get_by_id()."""

    def test_get_by_id_existing_entity(self, base_repository, sample_company):
        """Test que obtiene entidad existente por ID."""
        # Act
        result = base_repository.get_by_id(sample_company.id)

        # Assert
        assert result is not None
        assert result.id == sample_company.id
        assert result.name == sample_company.name
        assert result.trigram == sample_company.trigram

    def test_get_by_id_not_found_returns_none(self, base_repository):
        """Test que retorna None cuando el ID no existe."""
        # Act
        result = base_repository.get_by_id(99999)

        # Assert
        assert result is None

    def test_get_by_id_with_negative_id(self, base_repository):
        """Test que maneja IDs negativos correctamente."""
        # Act
        result = base_repository.get_by_id(-1)

        # Assert
        assert result is None

    def test_get_by_id_with_zero(self, base_repository):
        """Test que maneja ID cero correctamente."""
        # Act
        result = base_repository.get_by_id(0)

        # Assert
        assert result is None


# ============= GET ALL TESTS =============


class TestBaseRepositoryGetAll:
    """Tests para BaseRepository.get_all()."""

    def test_get_all_returns_empty_list_when_no_data(self, base_repository):
        """Test que retorna lista vacía cuando no hay datos."""
        # Act
        result = base_repository.get_all()

        # Assert
        assert result == []
        assert isinstance(result, list)

    def test_get_all_returns_all_entities(self, base_repository, create_test_companies, session):
        """Test que retorna todas las entidades sin paginación."""
        # Arrange - crear 5 companies
        companies = create_test_companies(5)

        # Act
        result = base_repository.get_all()

        # Assert
        assert len(result) == 5
        assert all(isinstance(c, Company) for c in result)

    def test_get_all_with_skip_parameter(self, base_repository, create_test_companies, session):
        """Test que skip funciona correctamente (offset)."""
        # Arrange - crear 10 companies
        create_test_companies(10)

        # Act - saltar las primeras 3
        result = base_repository.get_all(skip=3)

        # Assert
        assert len(result) == 7  # 10 - 3 = 7

    def test_get_all_with_limit_parameter(self, base_repository, create_test_companies, session):
        """Test que limit funciona correctamente."""
        # Arrange - crear 10 companies
        create_test_companies(10)

        # Act - limitar a 5 resultados
        result = base_repository.get_all(limit=5)

        # Assert
        assert len(result) == 5

    def test_get_all_with_skip_and_limit(self, base_repository, create_test_companies, session):
        """Test que paginación completa (skip + limit) funciona."""
        # Arrange - crear 10 companies
        create_test_companies(10)

        # Act - segunda página: saltar 5, obtener 3
        result = base_repository.get_all(skip=5, limit=3)

        # Assert
        assert len(result) == 3

    def test_get_all_skip_beyond_total_returns_empty(self, base_repository, create_test_companies, session):
        """Test que skip más allá del total retorna lista vacía."""
        # Arrange - crear 5 companies
        create_test_companies(5)

        # Act - saltar 100 (más que el total)
        result = base_repository.get_all(skip=100)

        # Assert
        assert result == []

    def test_get_all_limit_zero_returns_empty(self, base_repository, create_test_companies, session):
        """Test que limit=0 retorna lista vacía."""
        # Arrange
        create_test_companies(5)

        # Act
        result = base_repository.get_all(limit=0)

        # Assert
        assert result == []

    def test_get_all_last_page_partial_results(self, base_repository, create_test_companies, session):
        """Test que última página con resultados parciales funciona."""
        # Arrange - crear 7 companies
        create_test_companies(7)

        # Act - última página: skip 5, limit 5 (solo 2 disponibles)
        result = base_repository.get_all(skip=5, limit=5)

        # Assert
        assert len(result) == 2


# ============= CREATE TESTS =============


class TestBaseRepositoryCreate:
    """Tests para BaseRepository.create()."""

    def test_create_valid_entity(self, base_repository, sample_company_type, session):
        """Test que crea entidad válida y asigna ID."""
        # Arrange
        company = Company(
            name="New Test Company",
            trigram="NTC",
            company_type_id=sample_company_type.id,
        )

        # Act
        result = base_repository.create(company)
        session.commit()

        # Assert
        assert result.id is not None
        assert result.name == "New Test Company"
        assert result.trigram == "NTC"

    def test_create_flushes_without_commit(self, base_repository, sample_company_type, session):
        """Test que create hace flush (asigna ID) pero NO commit."""
        # Arrange
        company = Company(
            name="Test Flush",
            trigram="TFL",
            company_type_id=sample_company_type.id,
        )

        # Act
        result = base_repository.create(company)
        # NO hacemos commit

        # Assert - tiene ID asignado por flush
        assert result.id is not None

        # Rollback y verificar que no se guardó
        session.rollback()
        retrieved = base_repository.get_by_id(result.id)
        assert retrieved is None

    def test_create_sets_timestamp_fields(self, base_repository, sample_company_type, session):
        """Test que create establece campos de timestamp."""
        # Arrange
        company = Company(
            name="Timestamp Test",
            trigram="TST",
            company_type_id=sample_company_type.id,
        )

        # Act
        result = base_repository.create(company)
        session.commit()

        # Assert
        assert result.created_at is not None
        assert result.updated_at is not None

    def test_create_sets_audit_fields(self, base_repository, sample_company_type, session):
        """Test que create establece campos de auditoría desde contexto."""
        # Arrange
        company = Company(
            name="Audit Test",
            trigram="AUD",
            company_type_id=sample_company_type.id,
        )

        # Act - session tiene user_id=1 desde conftest
        result = base_repository.create(company)
        session.commit()

        # Assert
        assert result.created_by_id == 1

    def test_create_with_duplicate_unique_field_raises_error(
        self, base_repository, sample_company, sample_company_type, session
    ):
        """Test que crear con campo único duplicado lanza IntegrityError."""
        # Arrange - intentar crear con trigram duplicado
        duplicate_company = Company(
            name="Duplicate",
            trigram=sample_company.trigram,  # Trigram duplicado
            company_type_id=sample_company_type.id,
        )

        # Act & Assert
        with pytest.raises(IntegrityError):
            base_repository.create(duplicate_company)
            session.commit()


# ============= UPDATE TESTS =============


class TestBaseRepositoryUpdate:
    """Tests para BaseRepository.update()."""

    def test_update_existing_entity(self, base_repository, sample_company, session):
        """Test que actualiza entidad existente correctamente."""
        # Arrange
        original_name = sample_company.name
        sample_company.name = "Updated Company Name"

        # Act
        result = base_repository.update(sample_company)
        session.commit()

        # Assert
        assert result.name == "Updated Company Name"
        assert result.name != original_name
        assert result.id == sample_company.id

    def test_update_updates_timestamp(self, base_repository, sample_company, session):
        """Test que update actualiza el campo updated_at."""
        # Arrange
        original_updated_at = sample_company.updated_at
        sample_company.name = "Changed Name"

        # Act
        result = base_repository.update(sample_company)
        session.commit()
        session.refresh(result)

        # Assert
        assert result.updated_at > original_updated_at

    def test_update_non_existing_entity_raises_not_found(
        self, base_repository, sample_company_type, session
    ):
        """Test que actualizar entidad inexistente lanza NotFoundException."""
        # Arrange - crear company sin guardar
        company = Company(
            name="Non Existing",
            trigram="NEX",
            company_type_id=sample_company_type.id,
        )
        company.id = 99999  # ID que no existe

        # Act & Assert
        with pytest.raises(NotFoundException, match="Company no encontrado"):
            base_repository.update(company)

    def test_update_flushes_without_commit(self, base_repository, sample_company, session):
        """Test que update hace flush pero NO commit."""
        # Arrange
        original_name = sample_company.name
        sample_company.name = "New Name"

        # Act
        base_repository.update(sample_company)
        # NO commit

        # Rollback
        session.rollback()

        # Assert - cambios no guardados
        session.refresh(sample_company)
        assert sample_company.name == original_name


# ============= DELETE TESTS =============


class TestBaseRepositoryDelete:
    """Tests para BaseRepository.delete() (hard delete)."""

    def test_delete_existing_entity(self, base_repository, sample_company, session):
        """Test que elimina entidad existente permanentemente."""
        # Arrange
        company_id = sample_company.id

        # Act
        base_repository.delete(company_id)
        session.commit()

        # Assert
        result = base_repository.get_by_id(company_id)
        assert result is None

    def test_delete_non_existing_entity_raises_not_found(self, base_repository):
        """Test que eliminar entidad inexistente lanza NotFoundException."""
        # Act & Assert
        with pytest.raises(NotFoundException, match="Company no encontrado"):
            base_repository.delete(99999)

    def test_delete_flushes_without_commit(self, base_repository, sample_company, session):
        """Test que delete hace flush pero NO commit."""
        # Arrange
        company_id = sample_company.id

        # Act
        base_repository.delete(company_id)
        # NO commit

        # Rollback
        session.rollback()

        # Assert - entidad sigue existiendo
        result = base_repository.get_by_id(company_id)
        assert result is not None


# ============= SOFT DELETE TESTS =============


class TestBaseRepositorySoftDelete:
    """Tests para BaseRepository.soft_delete()."""

    def test_soft_delete_marks_entity_as_deleted(
        self, base_repository, sample_company, session
    ):
        """Test que soft delete marca entidad como eliminada."""
        # Arrange
        company_id = sample_company.id
        user_id = 1

        # Act
        base_repository.soft_delete(company_id, user_id)
        session.commit()

        # Assert
        result = base_repository.get_by_id(company_id)
        assert result is not None  # Entidad sigue en DB
        assert result.is_deleted is True
        # Note: deleted_by_id no está en Company (solo ejemplo conceptual)

    def test_soft_delete_non_existing_entity_raises_not_found(self, base_repository):
        """Test que soft delete de entidad inexistente lanza error."""
        # Act & Assert
        with pytest.raises(NotFoundException):
            base_repository.soft_delete(99999, user_id=1)

    def test_soft_delete_without_mixin_raises_not_implemented(self, session):
        """Test que soft delete sin SoftDeleteMixin lanza NotImplementedError."""
        # Arrange - usar un modelo sin SoftDeleteMixin
        from src.backend.models.lookups import Country

        repo = BaseRepository(session, Country)
        country = Country(name="Test Country")
        repo.create(country)
        session.commit()

        # Act & Assert
        with pytest.raises(NotImplementedError, match="no soporta soft delete"):
            repo.soft_delete(country.id, user_id=1)


# ============= UTILITY METHODS TESTS =============


class TestBaseRepositoryUtilityMethods:
    """Tests para métodos utilitarios (count, exists)."""

    def test_count_returns_zero_when_empty(self, base_repository):
        """Test que count retorna 0 cuando no hay datos."""
        # Act
        count = base_repository.count()

        # Assert
        assert count == 0

    def test_count_returns_correct_number(self, base_repository, create_test_companies, session):
        """Test que count retorna número correcto de entidades."""
        # Arrange
        create_test_companies(7)

        # Act
        count = base_repository.count()

        # Assert
        assert count == 7

    def test_exists_returns_true_for_existing_id(self, base_repository, sample_company):
        """Test que exists retorna True para ID existente."""
        # Act
        result = base_repository.exists(sample_company.id)

        # Assert
        assert result is True

    def test_exists_returns_false_for_non_existing_id(self, base_repository):
        """Test que exists retorna False para ID inexistente."""
        # Act
        result = base_repository.exists(99999)

        # Assert
        assert result is False


# ============= TRANSACTION BEHAVIOR TESTS =============


class TestBaseRepositoryTransactionBehavior:
    """Tests para comportamiento transaccional."""

    def test_multiple_operations_in_same_transaction(
        self, base_repository, sample_company_type, session
    ):
        """Test que múltiples operaciones en misma transacción funcionan."""
        # Arrange & Act - crear 3 companies en misma transacción
        companies = []
        for i in range(3):
            company = Company(
                name=f"Company {i}",
                trigram=f"CA{chr(65+i)}",
                company_type_id=sample_company_type.id,
            )
            created = base_repository.create(company)
            companies.append(created)

        # NO commit aún
        assert all(c.id is not None for c in companies)

        # Commit todo junto
        session.commit()

        # Assert - todas guardadas
        count = base_repository.count()
        assert count == 3

    def test_rollback_after_error_reverts_changes(
        self, base_repository, sample_company, sample_company_type, session
    ):
        """Test que rollback después de error revierte cambios."""
        # Arrange
        original_count = base_repository.count()

        try:
            # Act - intentar crear company con trigram duplicado
            duplicate = Company(
                name="Duplicate",
                trigram=sample_company.trigram,
                company_type_id=sample_company_type.id,
            )
            base_repository.create(duplicate)
            session.commit()  # Esto fallará
        except IntegrityError:
            session.rollback()

        # Assert - count no cambió
        assert base_repository.count() == original_count

    def test_concurrent_create_operations(
        self, base_repository, sample_company_type, session
    ):
        """Test que operaciones de creación concurrentes funcionan."""
        # Arrange & Act - crear múltiples en rápida sucesión
        companies = []
        for i in range(10):
            company = Company(
                name=f"Concurrent {i}",
                trigram=f"CB{chr(65+i)}",
                company_type_id=sample_company_type.id,
            )
            created = base_repository.create(company)
            companies.append(created)

        session.commit()

        # Assert - todas tienen IDs únicos
        ids = [c.id for c in companies]
        assert len(ids) == len(set(ids))  # Sin duplicados
        assert all(id is not None for id in ids)


# ============= EDGE CASES TESTS =============


class TestBaseRepositoryEdgeCases:
    """Tests para casos extremos y edge cases."""

    def test_get_all_with_very_large_limit(self, base_repository, create_test_companies, session):
        """Test que limit muy grande no causa problemas."""
        # Arrange
        create_test_companies(5)

        # Act - limit mucho mayor que total
        result = base_repository.get_all(limit=10000)

        # Assert - retorna solo los 5 disponibles
        assert len(result) == 5

    def test_create_and_immediately_retrieve(
        self, base_repository, sample_company_type, session
    ):
        """Test que entidad creada se puede recuperar inmediatamente."""
        # Arrange
        company = Company(
            name="Immediate Test",
            trigram="IMM",
            company_type_id=sample_company_type.id,
        )

        # Act
        created = base_repository.create(company)
        session.commit()
        retrieved = base_repository.get_by_id(created.id)

        # Assert
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == created.name

    def test_update_same_entity_multiple_times(
        self, base_repository, sample_company, session
    ):
        """Test que actualizar misma entidad múltiples veces funciona."""
        # Act - actualizar 3 veces
        for i in range(3):
            sample_company.name = f"Updated {i}"
            base_repository.update(sample_company)

        session.commit()

        # Assert
        result = base_repository.get_by_id(sample_company.id)
        assert result.name == "Updated 2"

    def test_get_all_maintains_order_across_pages(
        self, base_repository, create_test_companies, session
    ):
        """Test que paginación mantiene orden consistente."""
        # Arrange
        create_test_companies(10)

        # Act - obtener en páginas
        page1 = base_repository.get_all(skip=0, limit=5)
        page2 = base_repository.get_all(skip=5, limit=5)

        # Assert - sin overlap
        page1_ids = {c.id for c in page1}
        page2_ids = {c.id for c in page2}
        assert len(page1_ids & page2_ids) == 0  # Sin intersección


# ============= BULK OPERATIONS TESTS =============


class TestBaseRepositoryBulkOperations:
    """Tests para operaciones bulk (create_many, update_many, delete_many)."""

    def test_create_many_creates_multiple_entities(
        self, base_repository, sample_company_type, session
    ):
        """Test que create_many crea múltiples entidades."""
        # Arrange
        companies = [
            Company(name=f"Bulk Company {i}", trigram=f"BK{chr(65+i)}", company_type_id=sample_company_type.id)
            for i in range(5)
        ]

        # Act
        result = base_repository.create_many(companies)
        session.commit()

        # Assert
        assert len(result) == 5
        assert all(c.id is not None for c in result)
        assert base_repository.count() == 5

    def test_create_many_with_empty_list_returns_empty(self, base_repository):
        """Test que create_many con lista vacía retorna lista vacía."""
        # Act
        result = base_repository.create_many([])

        # Assert
        assert result == []

    def test_create_many_flushes_without_commit(
        self, base_repository, sample_company_type, session
    ):
        """Test que create_many hace flush pero NO commit."""
        # Arrange
        companies = [
            Company(name=f"NoCommit {i}", trigram=f"NC{chr(65+i)}", company_type_id=sample_company_type.id)
            for i in range(3)
        ]

        # Act
        result = base_repository.create_many(companies)
        # NO commit

        # Assert - tienen IDs (flush hizo su trabajo)
        assert all(c.id is not None for c in result)

        # Rollback
        session.rollback()

        # Assert - no se guardaron
        assert base_repository.count() == 0

    def test_update_many_updates_multiple_entities(
        self, base_repository, create_test_companies, session
    ):
        """Test que update_many actualiza múltiples entidades."""
        # Arrange
        companies = create_test_companies(5)
        ids = [c.id for c in companies]

        # Act
        rowcount = base_repository.update_many(ids[:3], {"is_active": False})
        session.commit()

        # Assert
        assert rowcount == 3
        for company_id in ids[:3]:
            company = base_repository.get_by_id(company_id)
            assert company.is_active is False
        # Los otros 2 deben seguir activos
        for company_id in ids[3:]:
            company = base_repository.get_by_id(company_id)
            assert company.is_active is True

    def test_update_many_with_empty_ids_returns_zero(self, base_repository):
        """Test que update_many con IDs vacíos retorna 0."""
        # Act
        rowcount = base_repository.update_many([], {"is_active": False})

        # Assert
        assert rowcount == 0

    def test_update_many_with_empty_values_returns_zero(
        self, base_repository, create_test_companies, session
    ):
        """Test que update_many con valores vacíos retorna 0."""
        # Arrange
        companies = create_test_companies(3)
        ids = [c.id for c in companies]

        # Act
        rowcount = base_repository.update_many(ids, {})

        # Assert
        assert rowcount == 0

    def test_update_many_with_non_existing_ids_returns_zero(self, base_repository):
        """Test que update_many con IDs inexistentes retorna 0."""
        # Act
        rowcount = base_repository.update_many([99998, 99999], {"is_active": False})

        # Assert
        assert rowcount == 0

    def test_delete_many_deletes_multiple_entities(
        self, base_repository, create_test_companies, session
    ):
        """Test que delete_many elimina múltiples entidades."""
        # Arrange
        companies = create_test_companies(5)
        ids_to_delete = [companies[0].id, companies[2].id, companies[4].id]

        # Act
        rowcount = base_repository.delete_many(ids_to_delete)
        session.commit()

        # Assert
        assert rowcount == 3
        assert base_repository.count() == 2
        # Verificar que los eliminados ya no existen
        for deleted_id in ids_to_delete:
            assert base_repository.get_by_id(deleted_id) is None

    def test_delete_many_with_empty_ids_returns_zero(self, base_repository):
        """Test que delete_many con IDs vacíos retorna 0."""
        # Act
        rowcount = base_repository.delete_many([])

        # Assert
        assert rowcount == 0

    def test_delete_many_with_non_existing_ids_returns_zero(self, base_repository):
        """Test que delete_many con IDs inexistentes retorna 0."""
        # Act
        rowcount = base_repository.delete_many([99998, 99999])

        # Assert
        assert rowcount == 0

    def test_delete_many_flushes_without_commit(
        self, base_repository, create_test_companies, session
    ):
        """Test que delete_many hace flush pero NO commit."""
        # Arrange
        companies = create_test_companies(3)
        ids = [c.id for c in companies]

        # Act
        rowcount = base_repository.delete_many(ids)
        # NO commit

        # Assert
        assert rowcount == 3

        # Rollback
        session.rollback()

        # Assert - entidades siguen existiendo
        assert base_repository.count() == 3

    def test_bulk_operations_combined(
        self, base_repository, sample_company_type, session
    ):
        """Test combinando múltiples operaciones bulk."""
        # Create many
        companies = [
            Company(name=f"Combined {i}", trigram=f"C{chr(65+i//26)}{chr(65+i%26)}", company_type_id=sample_company_type.id)
            for i in range(10)
        ]
        created = base_repository.create_many(companies)
        session.commit()
        assert base_repository.count() == 10

        # Update many (desactivar 5)
        ids_to_update = [c.id for c in created[:5]]
        base_repository.update_many(ids_to_update, {"is_active": False})
        session.commit()

        # Delete many (eliminar 3)
        ids_to_delete = [c.id for c in created[7:]]
        base_repository.delete_many(ids_to_delete)
        session.commit()

        # Assert final state
        assert base_repository.count() == 7
        inactive_count = sum(
            1 for c in base_repository.get_all()
            if not c.is_active
        )
        assert inactive_count == 5


# ============= QUERY BUILDER TESTS =============


class TestBaseRepositoryQueryBuilder:
    """Tests para Query Builder Pattern (get_all con order, find_by)."""

    def test_get_all_with_order_by_ascending(
        self, base_repository, create_test_companies, session
    ):
        """Test que get_all ordena ascendentemente por columna."""
        # Arrange
        create_test_companies(5)

        # Act
        result = base_repository.get_all(order_by="name", descending=False)

        # Assert
        names = [c.name for c in result]
        assert names == sorted(names)

    def test_get_all_with_order_by_descending(
        self, base_repository, create_test_companies, session
    ):
        """Test que get_all ordena descendentemente."""
        # Arrange
        create_test_companies(5)

        # Act
        result = base_repository.get_all(order_by="name", descending=True)

        # Assert
        names = [c.name for c in result]
        assert names == sorted(names, reverse=True)

    def test_get_all_with_invalid_order_by_column(
        self, base_repository, create_test_companies, session
    ):
        """Test que order_by inválido es ignorado silenciosamente."""
        # Arrange
        create_test_companies(3)

        # Act - columna inexistente
        result = base_repository.get_all(order_by="nonexistent_column")

        # Assert - no falla, retorna resultados
        assert len(result) == 3

    def test_find_by_with_single_filter(
        self, base_repository, create_test_companies, session
    ):
        """Test que find_by filtra por una columna."""
        # Arrange
        companies = create_test_companies(5)
        # Desactivar algunas
        for c in companies[:2]:
            c.is_active = False
        session.commit()

        # Act
        active = base_repository.find_by(filters={"is_active": True})

        # Assert
        assert len(active) == 3
        assert all(c.is_active for c in active)

    def test_find_by_with_multiple_filters(
        self, base_repository, create_test_companies, session
    ):
        """Test que find_by filtra por múltiples columnas."""
        # Arrange
        companies = create_test_companies(5)
        target_type_id = companies[0].company_type_id
        companies[0].is_active = False
        companies[1].is_active = False
        session.commit()

        # Act - buscar activas del mismo tipo
        result = base_repository.find_by(
            filters={"company_type_id": target_type_id, "is_active": True}
        )

        # Assert
        assert len(result) == 3
        assert all(c.is_active and c.company_type_id == target_type_id for c in result)

    def test_find_by_with_none_filter_value_is_ignored(
        self, base_repository, create_test_companies, session
    ):
        """Test que valores None en filtros son ignorados."""
        # Arrange
        create_test_companies(5)

        # Act - filtro con None (debe buscar todos)
        result = base_repository.find_by(filters={"is_active": None})

        # Assert - retorna todos (filtro ignorado)
        assert len(result) == 5

    def test_find_by_with_invalid_filter_column_is_ignored(
        self, base_repository, create_test_companies, session
    ):
        """Test que columnas inválidas en filtros son ignoradas."""
        # Arrange
        create_test_companies(3)

        # Act - columna inexistente
        result = base_repository.find_by(filters={"nonexistent": "value"})

        # Assert - no falla, retorna todos
        assert len(result) == 3

    def test_find_by_with_no_matches_returns_empty(
        self, base_repository, create_test_companies, session
    ):
        """Test que find_by sin coincidencias retorna lista vacía."""
        # Arrange
        create_test_companies(5)

        # Act - buscar con ID inexistente
        result = base_repository.find_by(filters={"company_type_id": 99999})

        # Assert
        assert result == []

    def test_find_by_with_ordering(
        self, base_repository, create_test_companies, session
    ):
        """Test que find_by soporta ordenamiento."""
        # Arrange
        create_test_companies(5)

        # Act
        result = base_repository.find_by(
            filters={"is_active": True},
            order_by="name",
            descending=True
        )

        # Assert
        names = [c.name for c in result]
        assert names == sorted(names, reverse=True)

    def test_find_by_with_pagination(
        self, base_repository, create_test_companies, session
    ):
        """Test que find_by soporta paginación."""
        # Arrange
        create_test_companies(10)

        # Act - segunda página
        page1 = base_repository.find_by(filters={}, skip=0, limit=5)
        page2 = base_repository.find_by(filters={}, skip=5, limit=5)

        # Assert
        assert len(page1) == 5
        assert len(page2) == 5
        # Sin overlap
        page1_ids = {c.id for c in page1}
        page2_ids = {c.id for c in page2}
        assert len(page1_ids & page2_ids) == 0

    def test_find_by_empty_filters_returns_all(
        self, base_repository, create_test_companies, session
    ):
        """Test que find_by con filtros vacíos retorna todos."""
        # Arrange
        create_test_companies(5)

        # Act
        result = base_repository.find_by(filters={})

        # Assert
        assert len(result) == 5

    def test_find_by_none_filters_returns_all(
        self, base_repository, create_test_companies, session
    ):
        """Test que find_by con filters=None retorna todos."""
        # Arrange
        create_test_companies(5)

        # Act
        result = base_repository.find_by(filters=None)

        # Assert
        assert len(result) == 5
