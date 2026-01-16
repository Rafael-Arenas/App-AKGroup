"""
Repositories for all 12 Lookup models.

Handles data access for Country, City, CompanyType, Incoterm, Currency, Unit,
FamilyType, Matter, SalesType, QuoteStatus, OrderStatus, PaymentStatus.
"""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.backend.models.lookups import (
    Country, City, CompanyType, Incoterm, Currency, Unit,
    FamilyType, Matter, SalesType, QuoteStatus, OrderStatus, PaymentStatus
)
from src.backend.repositories.base import BaseRepository


class CountryRepository(BaseRepository[Country]):
    """Repository for Country lookup."""

    def __init__(self, session: Session):
        super().__init__(session, Country)

    def get_by_name(self, name: str) -> Country | None:
        """Get country by name."""
        stmt = select(Country).filter(Country.name == name)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_iso_code(self, iso_code: str) -> Country | None:
        """Get country by ISO code (alpha-2 or alpha-3)."""
        stmt = select(Country).filter(
            (Country.iso_code_alpha2 == iso_code.upper()) |
            (Country.iso_code_alpha3 == iso_code.upper())
        )
        return self.session.execute(stmt).scalar_one_or_none()


class CityRepository(BaseRepository[City]):
    """Repository for City lookup."""

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


class CompanyTypeRepository(BaseRepository[CompanyType]):
    """Repository for CompanyType lookup."""

    def __init__(self, session: Session):
        super().__init__(session, CompanyType)

    def get_by_name(self, name: str) -> CompanyType | None:
        """Get company type by name."""
        stmt = select(CompanyType).filter(CompanyType.name == name)
        return self.session.execute(stmt).scalar_one_or_none()


class IncotermRepository(BaseRepository[Incoterm]):
    """Repository for Incoterm lookup."""

    def __init__(self, session: Session):
        super().__init__(session, Incoterm)

    def get_by_code(self, code: str) -> Incoterm | None:
        """Get incoterm by code."""
        stmt = select(Incoterm).filter(Incoterm.code == code.upper())
        return self.session.execute(stmt).scalar_one_or_none()

    def get_active(self, skip: int = 0, limit: int = 100) -> Sequence[Incoterm]:
        """Get active incoterms."""
        stmt = (
            select(Incoterm)
            .filter(Incoterm.is_active == True)
            .order_by(Incoterm.code)
            .offset(skip)
            .limit(limit)
        )
        return self.session.execute(stmt).scalars().all()


class CurrencyRepository(BaseRepository[Currency]):
    """Repository for Currency lookup."""

    def __init__(self, session: Session):
        super().__init__(session, Currency)

    def get_by_code(self, code: str) -> Currency | None:
        """Get currency by code."""
        stmt = select(Currency).filter(Currency.code == code.upper())
        return self.session.execute(stmt).scalar_one_or_none()

    def get_active(self, skip: int = 0, limit: int = 100) -> Sequence[Currency]:
        """Get active currencies."""
        stmt = (
            select(Currency)
            .filter(Currency.is_active == True)
            .order_by(Currency.code)
            .offset(skip)
            .limit(limit)
        )
        return self.session.execute(stmt).scalars().all()


class UnitRepository(BaseRepository[Unit]):
    """Repository for Unit lookup."""

    def __init__(self, session: Session):
        super().__init__(session, Unit)

    def get_by_code(self, code: str) -> Unit | None:
        """Get unit by code."""
        stmt = select(Unit).filter(Unit.code == code.lower())
        return self.session.execute(stmt).scalar_one_or_none()

    def get_active(self, skip: int = 0, limit: int = 100) -> Sequence[Unit]:
        """Get active units."""
        stmt = (
            select(Unit)
            .filter(Unit.is_active == True)
            .order_by(Unit.name)
            .offset(skip)
            .limit(limit)
        )
        return self.session.execute(stmt).scalars().all()


class FamilyTypeRepository(BaseRepository[FamilyType]):
    """Repository for FamilyType lookup."""

    def __init__(self, session: Session):
        super().__init__(session, FamilyType)

    def get_by_name(self, name: str) -> FamilyType | None:
        """Get family type by name."""
        stmt = select(FamilyType).filter(FamilyType.name == name)
        return self.session.execute(stmt).scalar_one_or_none()


class MatterRepository(BaseRepository[Matter]):
    """Repository for Matter lookup."""

    def __init__(self, session: Session):
        super().__init__(session, Matter)

    def get_by_name(self, name: str) -> Matter | None:
        """Get matter by name."""
        stmt = select(Matter).filter(Matter.name == name)
        return self.session.execute(stmt).scalar_one_or_none()


class SalesTypeRepository(BaseRepository[SalesType]):
    """Repository for SalesType lookup."""

    def __init__(self, session: Session):
        super().__init__(session, SalesType)

    def get_by_name(self, name: str) -> SalesType | None:
        """Get sales type by name."""
        stmt = select(SalesType).filter(SalesType.name == name)
        return self.session.execute(stmt).scalar_one_or_none()


class QuoteStatusRepository(BaseRepository[QuoteStatus]):
    """Repository for QuoteStatus lookup."""

    def __init__(self, session: Session):
        super().__init__(session, QuoteStatus)

    def get_by_code(self, code: str) -> QuoteStatus | None:
        """Get quote status by code."""
        stmt = select(QuoteStatus).filter(QuoteStatus.code == code.lower())
        return self.session.execute(stmt).scalar_one_or_none()


class OrderStatusRepository(BaseRepository[OrderStatus]):
    """Repository for OrderStatus lookup."""

    def __init__(self, session: Session):
        super().__init__(session, OrderStatus)

    def get_by_code(self, code: str) -> OrderStatus | None:
        """Get order status by code."""
        stmt = select(OrderStatus).filter(OrderStatus.code == code.lower())
        return self.session.execute(stmt).scalar_one_or_none()


class PaymentStatusRepository(BaseRepository[PaymentStatus]):
    """Repository for PaymentStatus lookup."""

    def __init__(self, session: Session):
        super().__init__(session, PaymentStatus)

    def get_by_code(self, code: str) -> PaymentStatus | None:
        """Get payment status by code."""
        stmt = select(PaymentStatus).filter(PaymentStatus.code == code.lower())
        return self.session.execute(stmt).scalar_one_or_none()
