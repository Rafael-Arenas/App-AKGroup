"""
Tests para CompanyRepository, CompanyRutRepository y PlantRepository.

Valida funcionalidad CRUD base más métodos específicos de Company.
"""

import pytest
from sqlalchemy.exc import IntegrityError

from src.backend.models.core.companies import Company, CompanyRut, Plant
from src.backend.exceptions.repository import NotFoundException


# ===================== COMPANY REPOSITORY TESTS =====================


class TestCompanyRepositoryGetByTrigram:
    """Tests para get_by_trigram()."""

    def test_get_by_trigram_existing(self, company_repository, sample_company, session):
        """Test que obtiene company existente por trigram."""
        # Act
        result = company_repository.get_by_trigram(sample_company.trigram)

        # Assert
        assert result is not None
        assert result.id == sample_company.id
        assert result.trigram == sample_company.trigram

    def test_get_by_trigram_not_found(self, company_repository):
        """Test que retorna None cuando trigram no existe."""
        # Act
        result = company_repository.get_by_trigram("NONEXIST")

        # Assert
        assert result is None

    def test_get_by_trigram_case_insensitive(
        self, company_repository, sample_company, session
    ):
        """Test que búsqueda por trigram es case insensitive."""
        # Act - buscar en lowercase
        result = company_repository.get_by_trigram(sample_company.trigram.lower())

        # Assert
        assert result is not None
        assert result.id == sample_company.id


class TestCompanyRepositorySearchByName:
    """Tests para search_by_name()."""

    def test_search_by_name_exact_match(
        self, company_repository, sample_company, session
    ):
        """Test que encuentra company con match exacto."""
        # Act
        results = company_repository.search_by_name(sample_company.name)

        # Assert
        assert len(results) == 1
        assert results[0].id == sample_company.id

    def test_search_by_name_partial_match(
        self, company_repository, create_test_companies, session
    ):
        """Test que encuentra companies con match parcial."""
        # Arrange - crear companies con nombres similares
        create_test_companies(5)  # "Test Company 1", "Test Company 2", etc.

        # Act - buscar "Test Company" debe encontrar todas
        results = company_repository.search_by_name("Test Company")

        # Assert
        assert len(results) >= 5
        assert all("Test Company" in c.name for c in results)

    def test_search_by_name_no_results(self, company_repository, session):
        """Test que retorna lista vacía cuando no hay matches."""
        # Act
        results = company_repository.search_by_name("NonexistentCompany")

        # Assert
        assert results == []
        assert isinstance(results, list)

    def test_search_by_name_case_insensitive(
        self, company_repository, sample_company, session
    ):
        """Test que búsqueda es case insensitive."""
        # Act - buscar en lowercase
        results = company_repository.search_by_name(sample_company.name.lower())

        # Assert
        assert len(results) >= 1
        assert any(c.id == sample_company.id for c in results)

    def test_search_by_name_multiple_results(
        self, company_repository, create_test_companies, session
    ):
        """Test que encuentra múltiples companies."""
        # Arrange - crear 10 companies
        create_test_companies(10)

        # Act - buscar "Test Company" debe encontrar todas
        results = company_repository.search_by_name("Test Company")

        # Assert
        assert len(results) >= 10


class TestCompanyRepositoryGetWithPlants:
    """Tests para get_with_plants()."""

    def test_get_with_plants_loads_relationships(
        self, company_repository, sample_company, plant_repository, session
    ):
        """Test que carga plants con eager loading."""
        # Arrange - crear plants para la company
        for i in range(3):
            plant = Plant(
                company_id=sample_company.id,
                name=f"Plant {i+1}",
                address=f"Address {i+1}",
            )
            plant_repository.create(plant)
        session.commit()

        # Act
        result = company_repository.get_with_plants(sample_company.id)

        # Assert
        assert result is not None
        assert len(result.plants) == 3
        assert all(b.company_id == sample_company.id for b in result.plants)

    def test_get_with_plants_empty_list(
        self, company_repository, sample_company, session
    ):
        """Test que retorna company con lista vacía si no hay plants."""
        # Act
        result = company_repository.get_with_plants(sample_company.id)

        # Assert
        assert result is not None
        assert result.plants == []

    def test_get_with_plants_not_found(self, company_repository):
        """Test que retorna None si company no existe."""
        # Act
        result = company_repository.get_with_plants(99999)

        # Assert
        assert result is None


class TestCompanyRepositoryGetWithRuts:
    """Tests para get_with_ruts()."""

    def test_get_with_ruts_loads_relationships(
        self, company_repository, sample_company, company_rut_repository, session
    ):
        """Test que carga RUTs con eager loading."""
        # Arrange - crear RUTs para la company (usar RUTs válidos)
        ruts = ["12345678-5", "98765432-5"]
        for i, rut_value in enumerate(ruts):
            rut = CompanyRut(
                company_id=sample_company.id,
                rut=rut_value,
                is_main=i == 0,
            )
            company_rut_repository.create(rut)
        session.commit()

        # Act
        result = company_repository.get_with_ruts(sample_company.id)

        # Assert
        assert result is not None
        assert len(result.ruts) == 2
        assert any(r.is_main for r in result.ruts)

    def test_get_with_ruts_empty_list(
        self, company_repository, sample_company, session
    ):
        """Test que retorna company con lista vacía si no hay RUTs."""
        # Act
        result = company_repository.get_with_ruts(sample_company.id)

        # Assert
        assert result is not None
        assert result.ruts == []


class TestCompanyRepositoryGetWithRelations:
    """Tests para get_with_relations()."""

    def test_get_with_relations_loads_all(
        self,
        company_repository,
        sample_company,
        plant_repository,
        company_rut_repository,
        address_repository,
        contact_repository,
        session,
    ):
        """Test que carga todas las relaciones con eager loading."""
        # Arrange - crear datos relacionados
        plant = Plant(
            company_id=sample_company.id,
            name="Main Plant",
            address="Main Address",
        )
        plant_repository.create(plant)

        rut = CompanyRut(
            company_id=sample_company.id,
            rut="12345678-5",
            is_main=True,
        )
        company_rut_repository.create(rut)

        session.commit()

        # Act
        result = company_repository.get_with_relations(sample_company.id)

        # Assert
        assert result is not None
        assert len(result.plants) == 1
        assert len(result.ruts) == 1

    def test_get_with_relations_not_found(self, company_repository):
        """Test que retorna None si company no existe."""
        # Act
        result = company_repository.get_with_relations(99999)

        # Assert
        assert result is None


class TestCompanyRepositoryGetActiveCompanies:
    """Tests para get_active_companies()."""

    def test_get_active_companies_only(
        self, company_repository, create_test_companies, session
    ):
        """Test que retorna solo companies activas."""
        # Arrange - crear 5 companies (todas activas por defecto)
        companies = create_test_companies(5)

        # Marcar 2 como inactivas
        companies[1].is_active = False
        companies[3].is_active = False
        session.commit()

        # Act
        results = company_repository.get_active_companies()

        # Assert - debe haber al menos 3 activas (las que creamos menos las 2 inactivas)
        active_count = len([c for c in results if c.id in [comp.id for comp in companies]])
        assert active_count == 3
        assert all(c.is_active for c in results)

    def test_get_active_companies_with_limit(
        self, company_repository, create_test_companies, session
    ):
        """Test que limit funciona correctamente."""
        # Arrange - crear 10 companies activas
        create_test_companies(10)

        # Act - limitar a 5
        results = company_repository.get_active_companies(limit=5)

        # Assert
        assert len(results) == 5
        assert all(c.is_active for c in results)

    def test_get_active_companies_pagination(
        self, company_repository, create_test_companies, session
    ):
        """Test que pagination funciona con filtro active."""
        # Arrange - crear 10 companies activas
        companies = create_test_companies(10)
        company_ids = [c.id for c in companies]

        # Act - obtener con skip
        results = company_repository.get_active_companies(skip=5, limit=10)

        # Assert - verificar que skip funciona
        results_from_created = [c for c in results if c.id in company_ids]
        assert len(results_from_created) == 5  # Las últimas 5 de las 10 creadas
        assert all(c.is_active for c in results)


class TestCompanyRepositoryGetByType:
    """Tests para get_by_type()."""

    def test_get_by_type_customer(
        self, company_repository, sample_company_type, session
    ):
        """Test que filtra companies por tipo."""
        # Arrange - crear company con tipo específico
        company = Company(
            name="Customer Company",
            trigram="CUS",
            company_type_id=sample_company_type.id,
        )
        company_repository.create(company)
        session.commit()

        # Act
        results = company_repository.get_by_type(sample_company_type.id)

        # Assert
        assert len(results) >= 1
        assert all(c.company_type_id == sample_company_type.id for c in results)

    def test_get_by_type_empty(self, company_repository):
        """Test que retorna lista vacía si no hay companies de ese tipo."""
        # Act
        results = company_repository.get_by_type(99999)

        # Assert
        assert results == []

    def test_get_by_type_with_pagination(
        self, company_repository, create_test_companies, sample_company_type, session
    ):
        """Test que pagination funciona con filtro de tipo."""
        # Arrange - crear 10 companies del mismo tipo
        companies = create_test_companies(10)
        company_ids = [c.id for c in companies]

        # Act
        results = company_repository.get_by_type(
            sample_company_type.id, skip=3, limit=10
        )

        # Assert - verificar que skip funciona
        results_from_created = [c for c in results if c.id in company_ids]
        assert len(results_from_created) == 7  # 10 creadas - 3 skip


# ===================== COMPANY RUT REPOSITORY TESTS =====================


class TestCompanyRutRepositoryGetByCompany:
    """Tests para get_by_company()."""

    def test_get_by_company_existing(
        self, company_rut_repository, sample_company, session
    ):
        """Test que obtiene RUTs de una company."""
        # Arrange - crear 2 RUTs (usar RUTs válidos)
        ruts = ["12345678-5", "98765432-5"]
        for i, rut_value in enumerate(ruts):
            rut = CompanyRut(
                company_id=sample_company.id,
                rut=rut_value,
                is_main=i == 0,
            )
            company_rut_repository.create(rut)
        session.commit()

        # Act
        results = company_rut_repository.get_by_company(sample_company.id)

        # Assert
        assert len(results) == 2
        assert all(r.company_id == sample_company.id for r in results)

    def test_get_by_company_empty(self, company_rut_repository, sample_company):
        """Test que retorna lista vacía si no hay RUTs."""
        # Act
        results = company_rut_repository.get_by_company(sample_company.id)

        # Assert
        assert results == []


class TestCompanyRutRepositoryGetPrimary:
    """Tests para get_primary_rut()."""

    def test_get_primary_rut_existing(
        self, company_rut_repository, sample_company, session
    ):
        """Test que obtiene RUT primario."""
        # Arrange - crear RUT primario (usar RUT válido)
        primary_rut = CompanyRut(
            company_id=sample_company.id,
            rut="12345678-5",
            is_main=True,
        )
        company_rut_repository.create(primary_rut)

        # Crear RUT secundario
        secondary_rut = CompanyRut(
            company_id=sample_company.id,
            rut="98765432-5",
            is_main=False,
        )
        company_rut_repository.create(secondary_rut)
        session.commit()

        # Act
        result = company_rut_repository.get_primary_rut(sample_company.id)

        # Assert
        assert result is not None
        assert result.is_main is True
        assert result.rut == "12345678-5"

    def test_get_primary_rut_not_found(self, company_rut_repository, sample_company):
        """Test que retorna None si no hay RUT primario."""
        # Act
        result = company_rut_repository.get_primary_rut(sample_company.id)

        # Assert
        assert result is None


class TestCompanyRutRepositoryGetByRut:
    """Tests para get_by_rut()."""

    def test_get_by_rut_existing(
        self, company_rut_repository, sample_company, session
    ):
        """Test que busca RUT por número."""
        # Arrange (usar RUT válido)
        rut = CompanyRut(
            company_id=sample_company.id,
            rut="12345678-5",
            is_main=True,
        )
        company_rut_repository.create(rut)
        session.commit()

        # Act
        result = company_rut_repository.get_by_rut("12345678-5")

        # Assert
        assert result is not None
        assert result.rut == "12345678-5"

    def test_get_by_rut_not_found(self, company_rut_repository):
        """Test que retorna None si RUT no existe."""
        # Act
        result = company_rut_repository.get_by_rut("99999999-9")

        # Assert
        assert result is None


# ===================== PLANT REPOSITORY TESTS =====================


class TestPlantRepositoryGetByCompany:
    """Tests para get_by_company()."""

    def test_get_by_company_existing(
        self, plant_repository, sample_company, session
    ):
        """Test que obtiene plants de una company."""
        # Arrange - crear 3 plants
        for i in range(3):
            plant = Plant(
                company_id=sample_company.id,
                name=f"Plant {i+1}",
                address=f"Address {i+1}",
            )
            plant_repository.create(plant)
        session.commit()

        # Act
        results = plant_repository.get_by_company(sample_company.id)

        # Assert
        assert len(results) == 3
        assert all(b.company_id == sample_company.id for b in results)

    def test_get_by_company_empty(self, plant_repository, sample_company):
        """Test que retorna lista vacía si no hay plants."""
        # Act
        results = plant_repository.get_by_company(sample_company.id)

        # Assert
        assert results == []

    def test_get_by_company_multiple_plants(
        self, plant_repository, sample_company, session
    ):
        """Test que obtiene múltiples plants."""
        # Arrange - crear 10 plants
        for i in range(10):
            plant = Plant(
                company_id=sample_company.id,
                name=f"Plant {i+1}",
                address=f"Address {i+1}",
            )
            plant_repository.create(plant)
        session.commit()

        # Act
        results = plant_repository.get_by_company(sample_company.id)

        # Assert
        assert len(results) == 10


class TestPlantRepositoryGetActivePlants:
    """Tests para get_active_plants()."""

    def test_get_active_plants_only(
        self, plant_repository, sample_company, session
    ):
        """Test que obtiene solo plants activas."""
        # Arrange - crear 5 plants
        for i in range(5):
            plant = Plant(
                company_id=sample_company.id,
                name=f"Plant {i+1}",
                address=f"Address {i+1}",
            )
            created = plant_repository.create(plant)

            # Marcar 2 como inactivas
            if i in [1, 3]:
                created.is_active = False

        session.commit()

        # Act
        results = plant_repository.get_active_plants(sample_company.id)

        # Assert
        assert len(results) == 3
        assert all(b.is_active for b in results)

    def test_get_active_plants_empty(self, plant_repository, sample_company):
        """Test que retorna lista vacía si no hay plants activas."""
        # Act
        results = plant_repository.get_active_plants(sample_company.id)

        # Assert
        assert results == []


class TestPlantRepositorySearchByName:
    """Tests para search_by_name()."""

    def test_search_by_name_partial_match(
        self, plant_repository, sample_company, session
    ):
        """Test que busca plants por nombre parcial."""
        # Arrange - crear plants con nombres similares
        for i in range(5):
            plant = Plant(
                company_id=sample_company.id,
                name=f"Santiago Plant {i+1}",
                address=f"Address {i+1}",
            )
            plant_repository.create(plant)
        session.commit()

        # Act
        results = plant_repository.search_by_name(sample_company.id, "Santiago")

        # Assert
        assert len(results) == 5
        assert all("Santiago" in b.name for b in results)

    def test_search_by_name_case_insensitive(
        self, plant_repository, sample_company, session
    ):
        """Test que búsqueda es case insensitive."""
        # Arrange
        plant = Plant(
            company_id=sample_company.id,
            name="Valparaiso Plant",
            address="Main Street",
        )
        plant_repository.create(plant)
        session.commit()

        # Act - buscar en lowercase
        results = plant_repository.search_by_name(sample_company.id, "valparaiso")

        # Assert
        assert len(results) >= 1
        assert any("Valparaiso" in b.name for b in results)

    def test_search_by_name_no_results(self, plant_repository, sample_company):
        """Test que retorna lista vacía sin matches."""
        # Act
        results = plant_repository.search_by_name(sample_company.id, "NonExistent")

        # Assert
        assert results == []
