"""
Repositories for all 12 Lookup models.

Handles data access for Country, City, CompanyType, Incoterm, Currency, Unit,
FamilyType, Matter, SalesType, QuoteStatus, OrderStatus, PaymentStatus.

Uses GenericLookupRepository for common lookup patterns, reducing code duplication.
"""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.backend.models.lookups import (
    Country, City, CompanyType, Incoterm, Currency, Unit,
    FamilyType, Matter, SalesType, QuoteStatus, OrderStatus, PaymentStatus
)
from src.backend.repositories.base import BaseRepository, GenericLookupRepository


# =============================================================================
# Repositories using GenericLookupRepository (simplified)
# =============================================================================


class CompanyTypeRepository(GenericLookupRepository[CompanyType]):
    """
    Repository for CompanyType lookup.

    Inherits: get_by_name(), get_active(), get_all_ordered(), search_by_name()
    """

    def __init__(self, session: Session):
        super().__init__(session, CompanyType)


class FamilyTypeRepository(GenericLookupRepository[FamilyType]):
    """
    Repository for FamilyType lookup.

    Inherits: get_by_name(), get_active(), get_all_ordered(), search_by_name()
    """

    def __init__(self, session: Session):
        super().__init__(session, FamilyType)


class MatterRepository(GenericLookupRepository[Matter]):
    """
    Repository for Matter lookup.

    Inherits: get_by_name(), get_active(), get_all_ordered(), search_by_name()
    """

    def __init__(self, session: Session):
        super().__init__(session, Matter)


class SalesTypeRepository(GenericLookupRepository[SalesType]):
    """
    Repository for SalesType lookup.

    Inherits: get_by_name(), get_active(), get_all_ordered(), search_by_name()
    """

    def __init__(self, session: Session):
        super().__init__(session, SalesType)


class IncotermRepository(GenericLookupRepository[Incoterm]):
    """
    Repository for Incoterm lookup.

    Uses uppercase normalization for codes (EXW, FOB, CIF, etc.).
    Inherits: get_by_code(), get_active(), get_all_ordered()
    """
    code_normalize = "upper"

    def __init__(self, session: Session):
        super().__init__(session, Incoterm)


class CurrencyRepository(GenericLookupRepository[Currency]):
    """
    Repository for Currency lookup.

    Uses uppercase normalization for codes (USD, EUR, CLP, etc.).
    Inherits: get_by_code(), get_active(), get_all_ordered()
    """
    code_normalize = "upper"

    def __init__(self, session: Session):
        super().__init__(session, Currency)


class UnitRepository(GenericLookupRepository[Unit]):
    """
    Repository for Unit lookup.

    Uses lowercase normalization for codes (kg, m, pcs, etc.).
    Inherits: get_by_code(), get_active(), get_all_ordered()
    """
    code_normalize = "lower"

    def __init__(self, session: Session):
        super().__init__(session, Unit)


class QuoteStatusRepository(GenericLookupRepository[QuoteStatus]):
    """
    Repository for QuoteStatus lookup.

    Uses lowercase normalization for codes.
    Inherits: get_by_code(), get_active(), get_all_ordered()
    """
    code_normalize = "lower"

    def __init__(self, session: Session):
        super().__init__(session, QuoteStatus)


class OrderStatusRepository(GenericLookupRepository[OrderStatus]):
    """
    Repository for OrderStatus lookup.

    Uses lowercase normalization for codes.
    Inherits: get_by_code(), get_active(), get_all_ordered()
    """
    code_normalize = "lower"

    def __init__(self, session: Session):
        super().__init__(session, OrderStatus)


class PaymentStatusRepository(GenericLookupRepository[PaymentStatus]):
    """
    Repository for PaymentStatus lookup.

    Uses lowercase normalization for codes.
    Inherits: get_by_code(), get_active(), get_all_ordered()
    """
    code_normalize = "lower"

    def __init__(self, session: Session):
        super().__init__(session, PaymentStatus)


# =============================================================================
# Repositories with custom methods (cannot be fully generalized)
# =============================================================================


class CountryRepository(GenericLookupRepository[Country]):
    """
    Repository for Country lookup.

    Has custom method for ISO code search (alpha-2 or alpha-3).
    Inherits: get_by_name(), get_active(), get_all_ordered(), search_by_name()
    """

    def __init__(self, session: Session):
        super().__init__(session, Country)

    def get_by_iso_code(self, iso_code: str) -> Country | None:
        """
        Get country by ISO code (alpha-2 or alpha-3).

        Args:
            iso_code: ISO code (CL, CHL, US, USA, etc.)

        Returns:
            Country if found, None otherwise
        """
        stmt = select(Country).filter(
            (Country.iso_code_alpha2 == iso_code.upper()) |
            (Country.iso_code_alpha3 == iso_code.upper())
        )
        return self.session.execute(stmt).scalar_one_or_none()


class CityRepository(BaseRepository[City]):
    """
    Repository for City lookup.

    Has custom methods for country-based queries.
    Does not extend GenericLookupRepository since cities need country context.
    """

    def __init__(self, session: Session):
        super().__init__(session, City)

    def get_by_country(self, country_id: int) -> Sequence[City]:
        """Get all cities for a country."""
        stmt = select(City).filter(City.country_id == country_id).order_by(City.name)
        return self.session.execute(stmt).scalars().all()

    def get_by_name_and_country(self, name: str, country_id: int) -> City | None:
        """Get city by name and country."""
        stmt = select(City).filter(City.name == name, City.country_id == country_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def search_by_name(self, name: str, country_id: int | None = None, limit: int = 50) -> Sequence[City]:
        """
        Search cities by name, optionally filtered by country.

        Args:
            name: Text to search
            country_id: Optional country filter
            limit: Max results

        Returns:
            List of matching cities
        """
        search_pattern = f"%{name}%"
        stmt = select(City).filter(City.name.ilike(search_pattern))

        if country_id is not None:
            stmt = stmt.filter(City.country_id == country_id)

        stmt = stmt.order_by(City.name).limit(limit)
        return self.session.execute(stmt).scalars().all()
