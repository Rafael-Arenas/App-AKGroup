"""
Repositories for all 12 Lookup models.

Handles data access for Country, City, CompanyType, Incoterm, Currency, Unit,
FamilyType, Matter, SalesType, QuoteStatus, OrderStatus, PaymentStatus.
"""

from typing import Optional, List
from sqlalchemy.orm import Session

from src.models.lookups.lookups import (
    Country, City, CompanyType, Incoterm, Currency, Unit,
    FamilyType, Matter, SalesType, QuoteStatus, OrderStatus, PaymentStatus
)
from src.repositories.base import BaseRepository
from src.utils.logger import logger


class CountryRepository(BaseRepository[Country]):
    """Repository for Country lookup."""

    def __init__(self, session: Session):
        super().__init__(session, Country)

    def get_by_name(self, name: str) -> Optional[Country]:
        """Get country by name."""
        return self.session.query(Country).filter(Country.name == name).first()

    def get_by_iso_code(self, iso_code: str) -> Optional[Country]:
        """Get country by ISO code (alpha-2 or alpha-3)."""
        return self.session.query(Country).filter(
            (Country.iso_code_alpha2 == iso_code.upper()) |
            (Country.iso_code_alpha3 == iso_code.upper())
        ).first()


class CityRepository(BaseRepository[City]):
    """Repository for City lookup."""

    def __init__(self, session: Session):
        super().__init__(session, City)

    def get_by_country(self, country_id: int) -> List[City]:
        """Get all cities for a country."""
        return (
            self.session.query(City)
            .filter(City.country_id == country_id)
            .order_by(City.name)
            .all()
        )

    def get_by_name_and_country(self, name: str, country_id: int) -> Optional[City]:
        """Get city by name and country."""
        return (
            self.session.query(City)
            .filter(City.name == name, City.country_id == country_id)
            .first()
        )


class CompanyTypeRepository(BaseRepository[CompanyType]):
    """Repository for CompanyType lookup."""

    def __init__(self, session: Session):
        super().__init__(session, CompanyType)

    def get_by_name(self, name: str) -> Optional[CompanyType]:
        """Get company type by name."""
        return self.session.query(CompanyType).filter(CompanyType.name == name).first()


class IncotermRepository(BaseRepository[Incoterm]):
    """Repository for Incoterm lookup."""

    def __init__(self, session: Session):
        super().__init__(session, Incoterm)

    def get_by_code(self, code: str) -> Optional[Incoterm]:
        """Get incoterm by code."""
        return self.session.query(Incoterm).filter(Incoterm.code == code.upper()).first()

    def get_active(self, skip: int = 0, limit: int = 100) -> List[Incoterm]:
        """Get active incoterms."""
        return (
            self.session.query(Incoterm)
            .filter(Incoterm.is_active == True)
            .order_by(Incoterm.code)
            .offset(skip)
            .limit(limit)
            .all()
        )


class CurrencyRepository(BaseRepository[Currency]):
    """Repository for Currency lookup."""

    def __init__(self, session: Session):
        super().__init__(session, Currency)

    def get_by_code(self, code: str) -> Optional[Currency]:
        """Get currency by code."""
        return self.session.query(Currency).filter(Currency.code == code.upper()).first()

    def get_active(self, skip: int = 0, limit: int = 100) -> List[Currency]:
        """Get active currencies."""
        return (
            self.session.query(Currency)
            .filter(Currency.is_active == True)
            .order_by(Currency.code)
            .offset(skip)
            .limit(limit)
            .all()
        )


class UnitRepository(BaseRepository[Unit]):
    """Repository for Unit lookup."""

    def __init__(self, session: Session):
        super().__init__(session, Unit)

    def get_by_code(self, code: str) -> Optional[Unit]:
        """Get unit by code."""
        return self.session.query(Unit).filter(Unit.code == code.lower()).first()

    def get_active(self, skip: int = 0, limit: int = 100) -> List[Unit]:
        """Get active units."""
        return (
            self.session.query(Unit)
            .filter(Unit.is_active == True)
            .order_by(Unit.name)
            .offset(skip)
            .limit(limit)
            .all()
        )


class FamilyTypeRepository(BaseRepository[FamilyType]):
    """Repository for FamilyType lookup."""

    def __init__(self, session: Session):
        super().__init__(session, FamilyType)

    def get_by_name(self, name: str) -> Optional[FamilyType]:
        """Get family type by name."""
        return self.session.query(FamilyType).filter(FamilyType.name == name).first()


class MatterRepository(BaseRepository[Matter]):
    """Repository for Matter lookup."""

    def __init__(self, session: Session):
        super().__init__(session, Matter)

    def get_by_name(self, name: str) -> Optional[Matter]:
        """Get matter by name."""
        return self.session.query(Matter).filter(Matter.name == name).first()


class SalesTypeRepository(BaseRepository[SalesType]):
    """Repository for SalesType lookup."""

    def __init__(self, session: Session):
        super().__init__(session, SalesType)

    def get_by_name(self, name: str) -> Optional[SalesType]:
        """Get sales type by name."""
        return self.session.query(SalesType).filter(SalesType.name == name).first()


class QuoteStatusRepository(BaseRepository[QuoteStatus]):
    """Repository for QuoteStatus lookup."""

    def __init__(self, session: Session):
        super().__init__(session, QuoteStatus)

    def get_by_code(self, code: str) -> Optional[QuoteStatus]:
        """Get quote status by code."""
        return self.session.query(QuoteStatus).filter(QuoteStatus.code == code.lower()).first()


class OrderStatusRepository(BaseRepository[OrderStatus]):
    """Repository for OrderStatus lookup."""

    def __init__(self, session: Session):
        super().__init__(session, OrderStatus)

    def get_by_code(self, code: str) -> Optional[OrderStatus]:
        """Get order status by code."""
        return self.session.query(OrderStatus).filter(OrderStatus.code == code.lower()).first()


class PaymentStatusRepository(BaseRepository[PaymentStatus]):
    """Repository for PaymentStatus lookup."""

    def __init__(self, session: Session):
        super().__init__(session, PaymentStatus)

    def get_by_code(self, code: str) -> Optional[PaymentStatus]:
        """Get payment status by code."""
        return self.session.query(PaymentStatus).filter(PaymentStatus.code == code.lower()).first()
