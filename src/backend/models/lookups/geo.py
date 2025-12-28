from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship
from .base import LookupBase

class Country(LookupBase):
    """
    Países.
    """
    __tablename__ = "countries"

    name = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
        comment="Country name",
    )

    iso_code_alpha2 = Column(
        String(2),
        unique=True,
        comment="ISO 3166-1 alpha-2 code (e.g., CL, FR, US)",
    )

    iso_code_alpha3 = Column(
        String(3),
        unique=True,
        comment="ISO 3166-1 alpha-3 code (e.g., CHL, FRA, USA)",
    )

    # Relationships
    cities = relationship("City", back_populates="country", lazy="select")
    companies = relationship("Company", back_populates="country", lazy="select")

    __table_args__ = (
        CheckConstraint(
            "length(trim(name)) >= 2",
            name="name_min_length",
        ),
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
    """
    __tablename__ = "cities"

    country_id = Column(
        Integer,
        ForeignKey("countries.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Country this city belongs to",
    )

    # Relationships
    country = relationship("Country", back_populates="cities", lazy="joined")
    companies = relationship("Company", back_populates="city", lazy="select")
    plants = relationship("Plant", back_populates="city", lazy="select")

    __table_args__ = (
        Index("uq_city_name_country", "name", "country_id", unique=True),
        CheckConstraint(
            "length(trim(name)) >= 2",
            name="name_min_length",
        ),
    )
