"""
Base declarativa y naming conventions para SQLAlchemy.

Este módulo proporciona la clase base para todos los modelos ORM del sistema,
incluyendo naming conventions para constraints y métodos utilitarios comunes.
"""

from typing import Any

from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base


# Naming convention para constraints automáticos
# Facilita migraciones de Alembic al generar nombres predecibles
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

# MetaData compartido por todos los modelos
metadata = MetaData(naming_convention=NAMING_CONVENTION)


class BaseModel:
    """
    Clase base para todos los modelos ORM.

    Proporciona métodos utilitarios comunes que todos los modelos heredarán:
    - __repr__: Representación string del modelo
    - to_dict: Conversión a diccionario para serialización

    Attributes:
        id: Primary key (debe definirse en cada modelo hijo)
    """

    id: int  # Type hint para soporte de IDE

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
        return f"<{self.__class__.__name__}(id={self.id})>"

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


# Base declarativa con BaseModel y metadata
Base = declarative_base(cls=BaseModel, metadata=metadata)
