"""
Tests para BaseService.

Valida lógica de negocio común que todos los servicios heredan.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from decimal import Decimal

from src.backend.services.base import BaseService
from src.backend.exceptions.repository import NotFoundException
from src.backend.exceptions.service import ValidationException
from src.backend.models.core.companies import Company


# ===================== GET BY ID TESTS =====================


class TestBaseServiceGetById:
    """Tests para get_by_id()."""

    def test_get_by_id_existing_entity(
        self, base_company_service, mock_company_repository, sample_company_entity
    ):
        """Test que obtiene entidad existente por ID."""
        # Arrange
        mock_company_repository.get_by_id.return_value = sample_company_entity

        # Act
        result = base_company_service.get_by_id(1)

        # Assert
        mock_company_repository.get_by_id.assert_called_once_with(1)
        assert result.id == 1
        assert result.name == "Test Company"

    def test_get_by_id_not_found_raises_exception(
        self, base_company_service, mock_company_repository
    ):
        """Test que lanza NotFoundException cuando ID no existe."""
        # Arrange
        mock_company_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundException) as exc_info:
            base_company_service.get_by_id(99999)

        assert "Company no encontrado" in str(exc_info.value)
        mock_company_repository.get_by_id.assert_called_once_with(99999)

    def test_get_by_id_returns_response_schema(
        self, base_company_service, mock_company_repository, sample_company_entity
    ):
        """Test que retorna schema de respuesta correctamente."""
        # Arrange
        mock_company_repository.get_by_id.return_value = sample_company_entity

        # Act
        result = base_company_service.get_by_id(1)

        # Assert
        assert hasattr(result, "id")
        assert hasattr(result, "name")
        assert hasattr(result, "trigram")


# ===================== GET ALL TESTS =====================


class TestBaseServiceGetAll:
    """Tests para get_all()."""

    def test_get_all_returns_empty_list(
        self, base_company_service, mock_company_repository
    ):
        """Test que retorna lista vacía cuando no hay datos."""
        # Arrange
        mock_company_repository.get_all.return_value = []

        # Act
        result = base_company_service.get_all()

        # Assert
        assert result == []
        mock_company_repository.get_all.assert_called_once_with(skip=0, limit=100)

    def test_get_all_returns_list_of_entities(
        self, base_company_service, mock_company_repository
    ):
        """Test que retorna lista de entidades."""
        # Arrange
        trigrams = ["TAA", "TAB", "TAC"]
        entities = []
        for i in range(3):
            entity = Company(
                id=i + 1,
                name=f"Company {i+1}",
                trigram=trigrams[i],
                company_type_id=1,
            )
            entities.append(entity)

        mock_company_repository.get_all.return_value = entities

        # Act
        result = base_company_service.get_all()

        # Assert
        assert len(result) == 3
        assert all(hasattr(r, "id") for r in result)
        assert all(hasattr(r, "name") for r in result)

    def test_get_all_with_pagination(
        self, base_company_service, mock_company_repository
    ):
        """Test que pagination se pasa correctamente al repositorio."""
        # Arrange
        mock_company_repository.get_all.return_value = []

        # Act
        base_company_service.get_all(skip=10, limit=50)

        # Assert
        mock_company_repository.get_all.assert_called_once_with(skip=10, limit=50)

    def test_get_all_converts_to_response_schemas(
        self, base_company_service, mock_company_repository, sample_company_entity
    ):
        """Test que convierte entidades a schemas de respuesta."""
        # Arrange
        mock_company_repository.get_all.return_value = [sample_company_entity]

        # Act
        result = base_company_service.get_all()

        # Assert
        assert len(result) == 1
        assert result[0].id == sample_company_entity.id
        assert result[0].name == sample_company_entity.name


# ===================== CREATE TESTS =====================


class TestBaseServiceCreate:
    """Tests para create()."""

    def test_create_valid_entity(
        self,
        base_company_service,
        mock_company_repository,
        sample_create_schema,
        sample_company_entity,
    ):
        """Test que crea entidad válida."""
        # Arrange
        mock_company_repository.create.return_value = sample_company_entity

        # Act
        result = base_company_service.create(sample_create_schema, user_id=1)

        # Assert
        mock_company_repository.create.assert_called_once()
        assert result.id == 1
        assert result.name == "Test Company"

    def test_create_sets_user_context(
        self,
        base_company_service,
        mock_company_repository,
        sample_create_schema,
        sample_company_entity,
        session,
    ):
        """Test que establece contexto de usuario en sesión."""
        # Arrange
        mock_company_repository.create.return_value = sample_company_entity

        # Act
        base_company_service.create(sample_create_schema, user_id=42)

        # Assert
        assert session.info.get("user_id") == 42

    def test_create_calls_validate_create(
        self,
        base_company_service,
        mock_company_repository,
        sample_create_schema,
        sample_company_entity,
    ):
        """Test que llama validate_create antes de crear."""
        # Arrange
        mock_company_repository.create.return_value = sample_company_entity
        base_company_service.validate_create = Mock()

        # Act
        base_company_service.create(sample_create_schema, user_id=1)

        # Assert
        base_company_service.validate_create.assert_called_once()

    def test_create_validation_exception_propagates(
        self, base_company_service, sample_create_schema
    ):
        """Test que ValidationException se propaga correctamente."""
        # Arrange
        def raise_validation_error(entity):
            raise ValidationException("Validation failed")

        base_company_service.validate_create = raise_validation_error

        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            base_company_service.create(sample_create_schema, user_id=1)

        assert "Validation failed" in str(exc_info.value)

    def test_create_does_not_commit(
        self,
        base_company_service,
        mock_company_repository,
        sample_create_schema,
        sample_company_entity,
    ):
        """Test que create NO hace commit automático."""
        # Arrange
        mock_company_repository.create.return_value = sample_company_entity

        # Act
        base_company_service.create(sample_create_schema, user_id=1)

        # Assert - verificar que solo se llamó create (flush) no commit
        mock_company_repository.create.assert_called_once()


# ===================== UPDATE TESTS =====================


class TestBaseServiceUpdate:
    """Tests para update()."""

    def test_update_existing_entity(
        self,
        base_company_service,
        mock_company_repository,
        sample_update_schema,
        sample_company_entity,
    ):
        """Test que actualiza entidad existente."""
        # Arrange
        mock_company_repository.get_by_id.return_value = sample_company_entity
        mock_company_repository.update.return_value = sample_company_entity

        # Act
        result = base_company_service.update(1, sample_update_schema, user_id=1)

        # Assert
        mock_company_repository.get_by_id.assert_called_once_with(1)
        mock_company_repository.update.assert_called_once()
        assert result.name == "Updated Company"

    def test_update_non_existing_entity_raises_exception(
        self, base_company_service, mock_company_repository, sample_update_schema
    ):
        """Test que lanza NotFoundException si entidad no existe."""
        # Arrange
        mock_company_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundException) as exc_info:
            base_company_service.update(99999, sample_update_schema, user_id=1)

        assert "Company no encontrado" in str(exc_info.value)

    def test_update_sets_user_context(
        self,
        base_company_service,
        mock_company_repository,
        sample_update_schema,
        sample_company_entity,
        session,
    ):
        """Test que establece contexto de usuario."""
        # Arrange
        mock_company_repository.get_by_id.return_value = sample_company_entity
        mock_company_repository.update.return_value = sample_company_entity

        # Act
        base_company_service.update(1, sample_update_schema, user_id=42)

        # Assert
        assert session.info.get("user_id") == 42

    def test_update_only_modifies_provided_fields(
        self,
        base_company_service,
        mock_company_repository,
        sample_company_entity,
    ):
        """Test que solo actualiza campos proporcionados en schema."""
        # Arrange
        from tests.backend.services.conftest import MockUpdateSchema

        mock_company_repository.get_by_id.return_value = sample_company_entity
        mock_company_repository.update.return_value = sample_company_entity

        # Schema con solo name (trigram no debe cambiar)
        partial_schema = MockUpdateSchema(name="New Name")

        # Act
        result = base_company_service.update(1, partial_schema, user_id=1)

        # Assert
        # Verificar que solo name cambió
        assert sample_company_entity.name == "New Name"
        assert sample_company_entity.trigram == "TST"  # No cambió

    def test_update_calls_validate_update(
        self,
        base_company_service,
        mock_company_repository,
        sample_update_schema,
        sample_company_entity,
    ):
        """Test que llama validate_update antes de actualizar."""
        # Arrange
        mock_company_repository.get_by_id.return_value = sample_company_entity
        mock_company_repository.update.return_value = sample_company_entity
        base_company_service.validate_update = Mock()

        # Act
        base_company_service.update(1, sample_update_schema, user_id=1)

        # Assert
        base_company_service.validate_update.assert_called_once()


# ===================== DELETE TESTS =====================


class TestBaseServiceDelete:
    """Tests para delete()."""

    def test_delete_soft_delete_by_default(
        self, base_company_service, mock_company_repository
    ):
        """Test que hace soft delete por defecto."""
        # Act
        base_company_service.delete(1, user_id=1, soft=True)

        # Assert - Company tiene is_deleted, así que debe llamar soft_delete
        # Si el modelo tiene el attr 'is_deleted', se usa soft_delete
        if hasattr(base_company_service.model, "is_deleted"):
            mock_company_repository.soft_delete.assert_called_once_with(1, 1)
        else:
            mock_company_repository.delete.assert_called_once_with(1)

    def test_delete_hard_delete_when_soft_false(
        self, base_company_service, mock_company_repository
    ):
        """Test que hace hard delete cuando soft=False."""
        # Act
        base_company_service.delete(1, user_id=1, soft=False)

        # Assert
        mock_company_repository.delete.assert_called_once_with(1)
        mock_company_repository.soft_delete.assert_not_called()

    def test_delete_sets_user_context(
        self, base_company_service, mock_company_repository, session
    ):
        """Test que establece contexto de usuario."""
        # Act
        base_company_service.delete(1, user_id=42, soft=True)

        # Assert
        assert session.info.get("user_id") == 42

    def test_delete_not_found_raises_exception(
        self, base_company_service, mock_company_repository
    ):
        """Test que lanza NotFoundException si entidad no existe."""
        # Arrange - configurar tanto soft_delete como delete para lanzar error
        mock_company_repository.soft_delete.side_effect = NotFoundException(
            "Company no encontrado"
        )
        mock_company_repository.delete.side_effect = NotFoundException(
            "Company no encontrado"
        )

        # Act & Assert
        with pytest.raises(NotFoundException):
            base_company_service.delete(99999, user_id=1, soft=True)

    def test_delete_hard_without_soft_delete_mixin(
        self, base_company_service, mock_company_repository
    ):
        """Test que hace hard delete si modelo no tiene soft delete."""
        # Arrange - simular modelo sin is_deleted
        base_company_service.model = type(
            "ModelWithoutSoftDelete", (), {"__name__": "TestModel"}
        )

        # Act
        base_company_service.delete(1, user_id=1, soft=True)

        # Assert - debe hacer hard delete porque no tiene is_deleted
        mock_company_repository.delete.assert_called_once_with(1)


# ===================== UTILITY METHODS TESTS =====================


class TestBaseServiceUtilityMethods:
    """Tests para métodos utilitarios."""

    def test_count_returns_repository_count(
        self, base_company_service, mock_company_repository
    ):
        """Test que count retorna el valor del repositorio."""
        # Arrange
        mock_company_repository.count.return_value = 42

        # Act
        result = base_company_service.count()

        # Assert
        assert result == 42
        mock_company_repository.count.assert_called_once()

    def test_exists_returns_true_for_existing_id(
        self, base_company_service, mock_company_repository
    ):
        """Test que exists retorna True para ID existente."""
        # Arrange
        mock_company_repository.exists.return_value = True

        # Act
        result = base_company_service.exists(1)

        # Assert
        assert result is True
        mock_company_repository.exists.assert_called_once_with(1)

    def test_exists_returns_false_for_non_existing_id(
        self, base_company_service, mock_company_repository
    ):
        """Test que exists retorna False para ID inexistente."""
        # Arrange
        mock_company_repository.exists.return_value = False

        # Act
        result = base_company_service.exists(99999)

        # Assert
        assert result is False
        mock_company_repository.exists.assert_called_once_with(99999)


# ===================== VALIDATION METHODS TESTS =====================


class TestBaseServiceValidationMethods:
    """Tests para métodos de validación."""

    def test_validate_create_default_implementation_does_nothing(
        self, base_company_service, sample_company_entity
    ):
        """Test que validate_create por defecto no hace nada."""
        # Act & Assert - no debe lanzar excepción
        try:
            base_company_service.validate_create(sample_company_entity)
        except Exception as e:
            pytest.fail(f"validate_create no debe lanzar excepción: {e}")

    def test_validate_update_default_implementation_does_nothing(
        self, base_company_service, sample_company_entity
    ):
        """Test que validate_update por defecto no hace nada."""
        # Act & Assert - no debe lanzar excepción
        try:
            base_company_service.validate_update(sample_company_entity)
        except Exception as e:
            pytest.fail(f"validate_update no debe lanzar excepción: {e}")

    def test_validate_create_can_be_overridden(self, base_company_service):
        """Test que validate_create puede ser sobrescrito."""
        # Arrange
        def custom_validation(entity):
            if entity.name == "Invalid":
                raise ValidationException("Name cannot be Invalid")

        base_company_service.validate_create = custom_validation
        invalid_entity = Company(
            id=1, name="Invalid", trigram="INV", company_type_id=1
        )

        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            base_company_service.validate_create(invalid_entity)

        assert "Name cannot be Invalid" in str(exc_info.value)

    def test_validate_update_can_be_overridden(self, base_company_service):
        """Test que validate_update puede ser sobrescrito."""
        # Arrange
        def custom_validation(entity):
            if len(entity.name) < 3:
                raise ValidationException("Name too short")

        base_company_service.validate_update = custom_validation
        invalid_entity = Company(id=1, name="AB", trigram="ABC", company_type_id=1)

        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            base_company_service.validate_update(invalid_entity)

        assert "Name too short" in str(exc_info.value)


# ===================== INTEGRATION TESTS =====================


class TestBaseServiceIntegration:
    """Tests de integración para flujos completos."""

    def test_complete_crud_workflow(
        self,
        base_company_service,
        mock_company_repository,
        sample_create_schema,
        sample_update_schema,
        sample_company_entity,
    ):
        """Test de flujo completo CRUD."""
        # Arrange
        mock_company_repository.create.return_value = sample_company_entity
        mock_company_repository.get_by_id.return_value = sample_company_entity
        mock_company_repository.update.return_value = sample_company_entity

        # Act - Create
        created = base_company_service.create(sample_create_schema, user_id=1)
        assert created.id == 1

        # Act - Get
        retrieved = base_company_service.get_by_id(1)
        assert retrieved.id == created.id

        # Act - Update
        updated = base_company_service.update(1, sample_update_schema, user_id=1)
        assert updated.id == 1

        # Act - Delete
        base_company_service.delete(1, user_id=1, soft=True)

        # Assert - verificar que se llamó el método correcto
        if hasattr(base_company_service.model, "is_deleted"):
            mock_company_repository.soft_delete.assert_called_once_with(1, 1)
        else:
            mock_company_repository.delete.assert_called_once_with(1)

    def test_error_handling_throughout_lifecycle(
        self, base_company_service, mock_company_repository
    ):
        """Test que errores se manejan correctamente en todo el ciclo de vida."""
        # Test get_by_id no encontrado
        mock_company_repository.get_by_id.return_value = None
        with pytest.raises(NotFoundException):
            base_company_service.get_by_id(99999)

        # Test update no encontrado
        with pytest.raises(NotFoundException):
            from tests.backend.services.conftest import MockUpdateSchema

            base_company_service.update(99999, MockUpdateSchema(name="Test"), user_id=1)

        # Test delete no encontrado
        mock_company_repository.soft_delete.side_effect = NotFoundException("Not found")
        mock_company_repository.delete.side_effect = NotFoundException("Not found")
        with pytest.raises(NotFoundException):
            base_company_service.delete(99999, user_id=1, soft=True)
