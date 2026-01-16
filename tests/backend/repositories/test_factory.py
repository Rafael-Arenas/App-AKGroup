"""
Tests para RepositoryFactory.

Valida que el factory crea repositorios correctamente y comparte la sesión.
"""

import pytest
from sqlalchemy.orm import Session

from src.backend.repositories import RepositoryFactory, Repos
from src.backend.repositories.core.company_repository import CompanyRepository
from src.backend.repositories.business.order_repository import OrderRepository
from src.backend.repositories.lookups.lookup_repository import CountryRepository


class TestRepositoryFactory:
    """Tests para RepositoryFactory."""

    def test_factory_initialization(self, session: Session):
        """Test que el factory se inicializa correctamente."""
        factory = RepositoryFactory(session)
        assert factory.session is session

    def test_repos_alias_works(self, session: Session):
        """Test que el alias Repos funciona."""
        factory = Repos(session)
        assert isinstance(factory, RepositoryFactory)

    def test_companies_repository_type(self, session: Session):
        """Test que companies retorna CompanyRepository."""
        factory = RepositoryFactory(session)
        assert isinstance(factory.companies, CompanyRepository)

    def test_orders_repository_type(self, session: Session):
        """Test que orders retorna OrderRepository."""
        factory = RepositoryFactory(session)
        assert isinstance(factory.orders, OrderRepository)

    def test_countries_repository_type(self, session: Session):
        """Test que countries retorna CountryRepository."""
        factory = RepositoryFactory(session)
        assert isinstance(factory.countries, CountryRepository)

    def test_repositories_share_session(self, session: Session):
        """Test que todos los repositorios comparten la misma sesión."""
        factory = RepositoryFactory(session)

        # Acceder a varios repositorios
        companies = factory.companies
        orders = factory.orders
        quotes = factory.quotes

        # Todos deben tener la misma sesión
        assert companies.session is session
        assert orders.session is session
        assert quotes.session is session

    def test_cached_property_returns_same_instance(self, session: Session):
        """Test que cached_property retorna la misma instancia."""
        factory = RepositoryFactory(session)

        # Acceder dos veces al mismo repositorio
        companies1 = factory.companies
        companies2 = factory.companies

        # Debe ser la misma instancia (no crear nueva)
        assert companies1 is companies2

    def test_all_core_repositories_accessible(self, session: Session):
        """Test que todos los repositorios core son accesibles."""
        factory = RepositoryFactory(session)

        # Verificar que no lanzan errores
        assert factory.companies is not None
        assert factory.company_ruts is not None
        assert factory.plants is not None
        assert factory.contacts is not None
        assert factory.addresses is not None
        assert factory.products is not None
        assert factory.product_components is not None
        assert factory.staff is not None
        assert factory.notes is not None
        assert factory.services is not None

    def test_all_business_repositories_accessible(self, session: Session):
        """Test que todos los repositorios business son accesibles."""
        factory = RepositoryFactory(session)

        assert factory.orders is not None
        assert factory.order_products is not None
        assert factory.quotes is not None
        assert factory.quote_products is not None
        assert factory.delivery_orders is not None
        assert factory.delivery_dates is not None
        assert factory.transports is not None
        assert factory.payment_conditions is not None
        assert factory.invoices_sii is not None
        assert factory.invoices_export is not None

    def test_all_lookup_repositories_accessible(self, session: Session):
        """Test que todos los repositorios lookup son accesibles."""
        factory = RepositoryFactory(session)

        assert factory.countries is not None
        assert factory.cities is not None
        assert factory.company_types is not None
        assert factory.incoterms is not None
        assert factory.currencies is not None
        assert factory.units is not None
        assert factory.family_types is not None
        assert factory.matters is not None
        assert factory.sales_types is not None
        assert factory.quote_statuses is not None
        assert factory.order_statuses is not None
        assert factory.payment_statuses is not None

    def test_factory_can_perform_operations(self, session: Session, sample_company_type):
        """Test que el factory permite realizar operaciones reales."""
        from src.backend.models.core.companies import Company

        factory = RepositoryFactory(session)

        # Crear una empresa usando el factory
        company = Company(
            name="Factory Test Company",
            trigram="FTC",
            company_type_id=sample_company_type.id,
        )
        created = factory.companies.create(company)
        session.commit()

        # Verificar que se creó
        assert created.id is not None

        # Buscar usando el factory
        found = factory.companies.get_by_id(created.id)
        assert found is not None
        assert found.name == "Factory Test Company"

    def test_factory_transaction_across_repositories(
        self, session: Session, sample_company_type
    ):
        """Test que operaciones en múltiples repos comparten transacción."""
        from src.backend.models.core.companies import Company
        from src.backend.models.lookups import Country

        factory = RepositoryFactory(session)

        # Crear país
        country = Country(name="Factory Test Country")
        factory.countries.create(country)

        # Crear empresa
        company = Company(
            name="Multi Repo Test",
            trigram="MRT",
            company_type_id=sample_company_type.id,
        )
        factory.companies.create(company)

        # Ambos deben tener IDs (flush hizo su trabajo)
        assert country.id is not None
        assert company.id is not None

        # Rollback
        session.rollback()

        # Ninguno debe existir después del rollback
        assert factory.countries.get_by_id(country.id) is None
        assert factory.companies.get_by_id(company.id) is None
