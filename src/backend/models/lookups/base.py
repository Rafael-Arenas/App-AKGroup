"""
Base lookup models for the application.

This module provides abstract base classes for lookup/catalog tables
that other lookup models inherit from.
"""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..base import ActiveMixin, Base, TimestampMixin


class LookupBase(Base, TimestampMixin):
    """
    Clase base abstracta para todos los modelos de tipo Lookup.

    Hereda de Base y TimestampMixin para incluir campos de auditoría.
    Proporciona campos comunes: id, name, description.
    """

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        String(100), index=True, comment="Display name"
    )
    description: Mapped[str | None] = mapped_column(
        Text, comment="Detailed description"
    )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id}, name='{self.name}')>"


class ActiveLookupBase(LookupBase, ActiveMixin):
    """
    Clase base abstracta para lookups que además requieren un estado activo/inactivo.
    """

    __abstract__ = True
