"""
Product-related lookup models.

This module contains lookup tables for product classification:
Unit, FamilyType, Matter.
"""

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import ActiveLookupBase, LookupBase

if TYPE_CHECKING:
    from ..core.products import Product


class Unit(ActiveLookupBase):
    """
    Unidades de medida (pcs, kg, m, etc.).

    Attributes:
        id: Primary key (inherited)
        name: Unit name (inherited)
        description: Description (inherited)
        code: Unit code (e.g., pcs, kg, m, l)
        is_active: Whether this unit is active (inherited)
    """

    __tablename__ = "units"

    code: Mapped[str] = mapped_column(
        String(10), unique=True, index=True, comment="Unit code (e.g., pcs, kg, m, l)"
    )

    __table_args__ = (
        CheckConstraint("length(trim(code)) > 0", name="code_not_empty"),
        CheckConstraint("length(trim(name)) > 0", name="name_not_empty"),
    )


class FamilyType(LookupBase):
    """
    Familias de productos.

    Attributes:
        id: Primary key (inherited)
        name: Family type name (unique)
        description: Description (inherited)
    """

    __tablename__ = "family_types"

    name: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, comment="Family type name"
    )

    # Relationships
    products: Mapped[list["Product"]] = relationship(
        "Product", back_populates="family_type", lazy="select"
    )

    __table_args__ = (
        CheckConstraint("length(trim(name)) > 0", name="name_not_empty"),
        {"sqlite_autoincrement": True},
    )


class Matter(LookupBase):
    """
    Materiales/Materias.

    Attributes:
        id: Primary key (inherited)
        name: Matter/material name (unique)
        description: Description (inherited)
    """

    __tablename__ = "matters"

    name: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, comment="Matter/material name"
    )

    # Relationships
    products: Mapped[list["Product"]] = relationship(
        "Product", back_populates="matter", lazy="select"
    )

    __table_args__ = (CheckConstraint("length(trim(name)) > 0", name="name_not_empty"),)
