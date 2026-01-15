from sqlalchemy import CheckConstraint, Column, String
from sqlalchemy.orm import relationship
from .base import LookupBase, ActiveLookupBase

class Unit(ActiveLookupBase):
    """
    Unidades de medida (pcs, kg, m, etc.).
    """
    __tablename__ = "units"

    code = Column(
        String(10),
        nullable=False,
        unique=True,
        index=True,
        comment="Unit code (e.g., pcs, kg, m, l)",
    )

    __table_args__ = (
        CheckConstraint(
            "length(trim(code)) > 0",
            name="code_not_empty",
        ),
        CheckConstraint(
            "length(trim(name)) > 0",
            name="name_not_empty",
        ),
    )

class FamilyType(LookupBase):
    """
    Familias de productos.
    """
    __tablename__ = "family_types"

    # Relationships
    products = relationship("Product", back_populates="family_type", lazy="select")

    __table_args__ = (
        CheckConstraint(
            "length(trim(name)) > 0",
            name="name_not_empty",
        ),
        # Unique name constraint
        {"sqlite_autoincrement": True},
    )

    # Override name to add unique constraint
    name = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
        comment="Family type name",
    )

class Matter(LookupBase):
    """
    Materiales/Materias.
    """
    __tablename__ = "matters"

    # Relationships
    products = relationship("Product", back_populates="matter", lazy="select")

    __table_args__ = (
        CheckConstraint(
            "length(trim(name)) > 0",
            name="name_not_empty",
        ),
    )

    # Override name to add unique constraint
    name = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
        comment="Matter/material name",
    )
