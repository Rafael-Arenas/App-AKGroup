from typing import Optional
from sqlalchemy import Column, Integer, String, Text, Boolean
from ..base import Base, TimestampMixin, ActiveMixin

class LookupBase(Base, TimestampMixin):
    """
    Clase base abstracta para todos los modelos de tipo Lookup.
    Hereda de Base y TimestampMixin para incluir campos de auditoría.
    """
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # La mayoría de los lookups tienen un nombre/name
    name = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Display name",
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Detailed description",
    )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id}, name='{self.name}')>"

class ActiveLookupBase(LookupBase, ActiveMixin):
    """
    Clase base abstracta para lookups que además requieren un estado activo/inactivo.
    """
    __abstract__ = True
