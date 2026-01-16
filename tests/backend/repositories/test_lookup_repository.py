"""
Tests para GenericLookupRepository.

Valida la funcionalidad de repositorios genéricos para tablas lookup.
"""

import pytest
from sqlalchemy.orm import Session

from src.backend.repositories.base import GenericLookupRepository
from src.backend.models.lookups import CompanyType, Currency


class TestGenericLookupRepository:
    """Tests para GenericLookupRepository."""

    @pytest.fixture
    def company_type_repo(self, session: Session):
        """Fixture para CompanyTypeRepository usando GenericLookupRepository."""
        return GenericLookupRepository(session, CompanyType)

    @pytest.fixture
    def currency_repo(self, session: Session):
        """Fixture para CurrencyRepository usando GenericLookupRepository."""
        repo = GenericLookupRepository(session, Currency)
        repo.code_normalize = "upper"  # Configurar normalización
        return repo

    @pytest.fixture
    def sample_company_types(self, session: Session):
        """Crea algunos CompanyType de prueba."""
        types = [
            CompanyType(name="Customer"),
            CompanyType(name="Supplier"),
            CompanyType(name="Partner"),
        ]
        session.add_all(types)
        session.commit()
        return types

    @pytest.fixture
    def sample_currencies(self, session: Session):
        """Crea algunas Currency de prueba."""
        currencies = [
            Currency(name="US Dollar", code="USD", symbol="$", is_active=True),
            Currency(name="Euro", code="EUR", symbol="€", is_active=True),
            Currency(name="Chilean Peso", code="CLP", symbol="$", is_active=False),
        ]
        session.add_all(currencies)
        session.commit()
        return currencies

    def test_get_by_name_finds_existing(
        self, company_type_repo, sample_company_types
    ):
        """Test que get_by_name encuentra entidad existente."""
        result = company_type_repo.get_by_name("Customer")
        assert result is not None
        assert result.name == "Customer"

    def test_get_by_name_returns_none_for_nonexistent(
        self, company_type_repo, sample_company_types
    ):
        """Test que get_by_name retorna None para nombre inexistente."""
        result = company_type_repo.get_by_name("NonExistent")
        assert result is None

    def test_get_by_name_strips_whitespace(
        self, company_type_repo, sample_company_types
    ):
        """Test que get_by_name elimina espacios."""
        result = company_type_repo.get_by_name("  Customer  ")
        assert result is not None
        assert result.name == "Customer"

    def test_get_by_code_with_uppercase_normalization(
        self, currency_repo, sample_currencies
    ):
        """Test que get_by_code normaliza a mayúsculas."""
        # Buscar con minúsculas
        result = currency_repo.get_by_code("usd")
        assert result is not None
        assert result.code == "USD"

    def test_get_by_code_returns_none_for_nonexistent(
        self, currency_repo, sample_currencies
    ):
        """Test que get_by_code retorna None para código inexistente."""
        result = currency_repo.get_by_code("XXX")
        assert result is None

    def test_get_active_returns_only_active(
        self, currency_repo, sample_currencies
    ):
        """Test que get_active retorna solo registros activos."""
        result = currency_repo.get_active()
        assert len(result) == 2
        assert all(c.is_active for c in result)

    def test_get_all_ordered_returns_ordered(
        self, company_type_repo, sample_company_types
    ):
        """Test que get_all_ordered retorna ordenados por nombre."""
        result = company_type_repo.get_all_ordered()
        names = [t.name for t in result]
        assert names == sorted(names)

    def test_search_by_name_finds_partial_matches(
        self, company_type_repo, sample_company_types
    ):
        """Test que search_by_name encuentra coincidencias parciales."""
        result = company_type_repo.search_by_name("er")
        # Debería encontrar "Customer", "Supplier", "Partner"
        assert len(result) == 3

    def test_search_by_name_is_case_insensitive(
        self, company_type_repo, sample_company_types
    ):
        """Test que search_by_name es case-insensitive."""
        result = company_type_repo.search_by_name("CUSTOMER")
        assert len(result) == 1
        assert result[0].name == "Customer"

    def test_search_by_name_with_limit(
        self, company_type_repo, sample_company_types
    ):
        """Test que search_by_name respeta el límite."""
        result = company_type_repo.search_by_name("er", limit=2)
        assert len(result) == 2
