"""
Base declarativa y naming conventions para SQLAlchemy 2.0.

Este módulo proporciona la clase base para todos los modelos ORM del sistema,
incluyendo naming conventions para constraints y métodos utilitarios comunes.
Usa el patrón moderno DeclarativeBase de SQLAlchemy 2.0.
"""

from typing import Any

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase


# Naming convention para constraints automáticos
# Facilita migraciones de Alembic al generar nombres predecibles
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """
    Clase base para todos los modelos ORM (SQLAlchemy 2.0).

    Usa el patrón moderno DeclarativeBase con metadata compartido
    y naming conventions para constraints.

    Proporciona métodos utilitarios comunes que todos los modelos heredarán:
    - __repr__: Representación string del modelo
    - to_dict: Conversión a diccionario para serialización

    Attributes:
        id: Primary key (debe definirse en cada modelo hijo)
        metadata: MetaData compartido con naming conventions

    Usage:
        from ..base import Base

        class Product(Base):
            __tablename__ = "products"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str] = mapped_column(String(200))
    """

    metadata = MetaData(naming_convention=NAMING_CONVENTION)

    def __repr__(self) -> str:
        """
        Representación string del modelo.

        Returns:
            String mostrando el nombre de la clase y su ID.

        Example:
            >>> product = Product(id=1)
            >>> repr(product)
            '<Product(id=1)>'
        """
        pk = getattr(self, "id", None)
        return f"<{self.__class__.__name__}(id={pk})>"

    def to_dict(self, exclude: set[str] | None = None) -> dict[str, Any]:
        """
        Convierte el modelo a diccionario.

        Útil para serialización JSON, APIs, logging, etc.

        Args:
            exclude: Set de nombres de campos a excluir del output.

        Returns:
            Diccionario con todos los campos del modelo (excepto excluidos).

        Example:
            >>> product.to_dict(exclude={'created_at', 'updated_at'})
            {'id': 1, 'name': 'Product A', 'price': 100.50}
        """
        exclude = exclude or set()
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
            if column.name not in exclude
        }


# Referencia al metadata para uso en Alembic
metadata = Base.metadata
