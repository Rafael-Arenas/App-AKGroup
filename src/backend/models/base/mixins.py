"""
Mixins reutilizables para modelos SQLAlchemy 2.0.

Este módulo proporciona mixins que añaden funcionalidad común a los modelos:
- TimestampMixin: Campos created_at y updated_at automáticos
- AuditMixin: Campos de auditoría (created_by, updated_by)
- SoftDeleteMixin: Soft delete (marcado lógico, no físico)
- ActiveMixin: Flag is_active para habilitar/deshabilitar registros

Todos los mixins usan el patrón moderno de SQLAlchemy 2.0 con Mapped[] types
y @declared_attr para compatibilidad con herencia múltiple.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, event
from sqlalchemy.orm import Mapped, Session, declared_attr, mapped_column

if TYPE_CHECKING:
    pass


class TimestampMixin:
    """
    Añade timestamps automáticos a los modelos.

    Campos:
        created_at: Timestamp UTC de creación (auto)
        updated_at: Timestamp UTC de última actualización (auto)

    El campo updated_at se actualiza automáticamente en cada UPDATE
    gracias al event listener configurado más abajo.

    Usage:
        class MyModel(Base, TimestampMixin):
            __tablename__ = 'my_table'
            id: Mapped[int] = mapped_column(primary_key=True)
    """

    @declared_attr
    def created_at(cls) -> Mapped[datetime]:
        """Timestamp UTC cuando el registro fue creado."""
        return mapped_column(
            DateTime(timezone=True),
            default=lambda: datetime.now(timezone.utc),
            comment="UTC timestamp of record creation",
        )

    @declared_attr
    def updated_at(cls) -> Mapped[datetime]:
        """Timestamp UTC de la última actualización del registro."""
        return mapped_column(
            DateTime(timezone=True),
            default=lambda: datetime.now(timezone.utc),
            onupdate=lambda: datetime.now(timezone.utc),
            comment="UTC timestamp of last update",
        )


class AuditMixin:
    """
    Añade campos de auditoría para rastrear quién creó/modificó registros.

    Campos:
        created_by_id: ID del usuario que creó el registro
        updated_by_id: ID del usuario que modificó el registro

    Para que funcione automáticamente, establece el user_id en session.info:
        session.info["user_id"] = current_user.id

    El event listener (más abajo) se encarga de setear estos campos automáticamente.

    Usage:
        class MyModel(Base, AuditMixin):
            __tablename__ = 'my_table'
            id: Mapped[int] = mapped_column(primary_key=True)

        # En tu repository/service:
        session.info["user_id"] = 123
        session.add(my_model)  # created_by_id = 123 automáticamente
    """

    @declared_attr
    def created_by_id(cls) -> Mapped[int | None]:
        """ID del usuario que creó este registro."""
        return mapped_column(comment="User ID who created this record", default=None)

    @declared_attr
    def updated_by_id(cls) -> Mapped[int | None]:
        """ID del usuario que actualizó este registro por última vez."""
        return mapped_column(
            comment="User ID who last updated this record", default=None
        )


class SoftDeleteMixin:
    """
    Añade funcionalidad de soft delete (eliminación lógica, no física).

    En lugar de eliminar registros de la base de datos, se marcan como
    eliminados estableciendo is_deleted=True y deleted_at=timestamp.

    Campos:
        is_deleted: Flag booleano (True = eliminado)
        deleted_at: Timestamp UTC de eliminación
        deleted_by_id: ID del usuario que eliminó el registro

    Usage:
        class MyModel(Base, SoftDeleteMixin):
            __tablename__ = 'my_table'
            id: Mapped[int] = mapped_column(primary_key=True)

        # En tu repository:
        def soft_delete(self, model_id: int, user_id: int):
            obj = session.get(MyModel, model_id)
            obj.is_deleted = True
            obj.deleted_at = datetime.now(timezone.utc)
            obj.deleted_by_id = user_id
            session.commit()

        # Para queries, filtrar por is_deleted=False
        stmt = select(MyModel).where(MyModel.is_deleted == False)
    """

    @declared_attr
    def is_deleted(cls) -> Mapped[bool]:
        """Flag de eliminación lógica (False = activo, True = eliminado)."""
        return mapped_column(
            default=False,
            index=True,
            comment="Soft delete flag (False=active, True=deleted)",
        )

    @declared_attr
    def deleted_at(cls) -> Mapped[datetime | None]:
        """Timestamp UTC de cuando fue eliminado (NULL si activo)."""
        return mapped_column(
            DateTime(timezone=True),
            default=None,
            comment="UTC timestamp of deletion (NULL if active)",
        )

    @declared_attr
    def deleted_by_id(cls) -> Mapped[int | None]:
        """ID del usuario que eliminó este registro."""
        return mapped_column(
            comment="User ID who deleted this record", default=None
        )


class ActiveMixin:
    """
    Añade flag is_active para habilitar/deshabilitar registros.

    Diferente de soft delete: is_active es para estados temporales
    (ej: producto activo/inactivo), mientras que soft delete es permanente.

    Campo:
        is_active: Flag booleano (True = activo, False = inactivo)

    Usage:
        class Currency(Base, ActiveMixin):
            __tablename__ = 'currencies'
            id: Mapped[int] = mapped_column(primary_key=True)
            code: Mapped[str] = mapped_column(String(3))

        # Queries solo de activos
        stmt = select(Currency).where(Currency.is_active == True)
    """

    @declared_attr
    def is_active(cls) -> Mapped[bool]:
        """Flag de estado activo/inactivo."""
        return mapped_column(
            default=True,
            index=True,
            comment="Active status flag (True=active, False=inactive)",
        )


# ========== EVENT LISTENERS ==========
# Automatizan el seteo de campos de auditoría


@event.listens_for(Session, "before_flush")
def receive_before_flush(
    session: Session, flush_context: object, instances: object
) -> None:
    """
    Event listener que se ejecuta antes de flush.

    Automáticamente establece:
    - created_by_id en registros nuevos
    - updated_by_id en registros modificados
    - updated_at en registros modificados

    Requiere que el user_id esté en session.info:
        session.info["user_id"] = current_user_id

    Args:
        session: Sesión de SQLAlchemy
        flush_context: Contexto del flush
        instances: Instancias afectadas
    """
    user_id = session.info.get("user_id")

    if user_id is None:
        return  # No hay contexto de usuario, skip

    # Registros nuevos (INSERT)
    for instance in session.new:
        if hasattr(instance, "created_by_id") and instance.created_by_id is None:
            instance.created_by_id = user_id
        if hasattr(instance, "updated_by_id") and instance.updated_by_id is None:
            instance.updated_by_id = user_id

    # Registros modificados (UPDATE)
    for instance in session.dirty:
        if hasattr(instance, "updated_by_id"):
            instance.updated_by_id = user_id
        # updated_at se maneja con onupdate en la columna


@event.listens_for(Session, "before_update", propagate=True)
def receive_before_update(mapper: object, connection: object, target: object) -> None:
    """
    Event listener alternativo para actualizar updated_at.

    Se ejecuta antes de cada UPDATE para garantizar que updated_at
    se actualice incluso si onupdate falla.

    Args:
        mapper: Mapper de SQLAlchemy
        connection: Conexión a la base de datos
        target: Instancia del modelo siendo actualizada
    """
    if hasattr(target, "updated_at"):
        target.updated_at = datetime.now(timezone.utc)
