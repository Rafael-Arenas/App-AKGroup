"""
Base infrastructure exports.

Este módulo exporta todas las clases base, mixins y validadores
necesarios para crear modelos SQLAlchemy en el sistema.

Usage:
    from models.base import Base, TimestampMixin, EmailValidator

    class MyModel(Base, TimestampMixin):
        __tablename__ = 'my_table'
        id = Column(Integer, primary_key=True)
        email = Column(String(100))

        @validates("email")
        def validate_email(self, key, value):
            return EmailValidator.validate(value)
"""

from .base import NAMING_CONVENTION, Base, BaseModel, metadata
from .mixins import (
    ActiveMixin,
    AuditMixin,
    SoftDeleteMixin,
    TimestampMixin,
)
from .validators import (
    DecimalValidator,
    EmailValidator,
    PhoneValidator,
    RutValidator,
    UrlValidator,
)

__all__ = [
    # Base
    "Base",
    "metadata",
    "NAMING_CONVENTION",
    "BaseModel",
    # Mixins
    "TimestampMixin",
    "AuditMixin",
    "SoftDeleteMixin",
    "ActiveMixin",
    # Validators
    "EmailValidator",
    "PhoneValidator",
    "RutValidator",
    "UrlValidator",
    "DecimalValidator",
]
