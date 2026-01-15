"""
Geographic lookup models (countries and cities).
"""

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import LookupBase

if TYPE_CHECKING:
    from ..core.companies import Company, Plant


class Country(LookupBase):
    """
    Países.

    Attributes:
        id: Primary key (inherited)
        name: Country name (inherited, overridden for unique)
        description: Description (inherited)
        iso_code_alpha2: ISO 3166-1 alpha-2 code (e.g., CL, FR, US)
        iso_code_alpha3: ISO 3166-1 alpha-3 code (e.g., CHL, FRA, USA)
    """

    __tablename__ = "countries"

    name: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, comment="Country name"
    )
    iso_code_alpha2: Mapped[str | None] = mapped_column(
        String(2), unique=True, comment="ISO 3166-1 alpha-2 code (e.g., CL, FR, US)"
    )
    iso_code_alpha3: Mapped[str | None] = mapped_column(
        String(3), unique=True, comment="ISO 3166-1 alpha-3 code (e.g., CHL, FRA, USA)"
    )

    # Relationships
    cities: Mapped[list["City"]] = relationship(
        "City", back_populates="country", lazy="select"
    )
    companies: Mapped[list["Company"]] = relationship(
        "Company", back_populates="country", lazy="select"
    )

    __table_args__ = (
        CheckConstraint("length(trim(name)) >= 2", name="name_min_length"),
        CheckConstraint(
            "iso_code_alpha2 IS NULL OR length(iso_code_alpha2) = 2",
            name="alpha2_length",
        ),
        CheckConstraint(
            "iso_code_alpha3 IS NULL OR length(iso_code_alpha3) = 3",
            name="alpha3_length",
        ),
    )


class City(LookupBase):
    """
    Ciudades asociadas a países.

    Attributes:
        id: Primary key (inherited)
        name: City name (inherited)
        description: Description (inherited)
        country_id: Foreign key to countries
    """

    __tablename__ = "cities"

    country_id: Mapped[int] = mapped_column(
        ForeignKey("countries.id", ondelete="RESTRICT"),
        index=True,
        comment="Country this city belongs to",
    )

    # Relationships
    country: Mapped["Country"] = relationship(
        "Country", back_populates="cities", lazy="joined"
    )
    companies: Mapped[list["Company"]] = relationship(
        "Company", back_populates="city", lazy="select"
    )
    plants: Mapped[list["Plant"]] = relationship(
        "Plant", back_populates="city", lazy="select"
    )

    __table_args__ = (
        Index("uq_city_name_country", "name", "country_id", unique=True),
        CheckConstraint("length(trim(name)) >= 2", name="name_min_length"),
    )
