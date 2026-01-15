"""
Base infrastructure exports.

Este módulo exporta todas las clases base, mixins, validadores,
constantes y tipos anotados para crear modelos SQLAlchemy 2.0.

Usage:
    from models.base import Base, TimestampMixin, EmailValidator
    from models.base import intpk, str_200, decimal_price

    class MyModel(Base, TimestampMixin):
        __tablename__ = 'my_table'
        id: Mapped[intpk]
        name: Mapped[str_200]
        email: Mapped[str | None] = mapped_column(String(100))

        @validates("email")
        def validate_email(self, key, value):
            return EmailValidator.validate(value)
"""

# Base and metadata
from .base import Base, NAMING_CONVENTION, metadata

# Constants
from .constants import DecimalPrecision, FieldLengths

# Mixins
from .mixins import ActiveMixin, AuditMixin, SoftDeleteMixin, TimestampMixin

# Types (SQLAlchemy 2.0 annotated types)
from .types import (
    bool_false,
    bool_true,
    datetime_tz,
    decimal_dimension,
    decimal_exchange,
    decimal_percentage,
    decimal_price,
    decimal_quantity,
    decimal_volume,
    decimal_weight,
    intpk,
    str_3,
    str_10,
    str_12,
    str_20,
    str_50,
    str_100,
    str_200,
    str_500,
    text_field,
)

# Validators
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
    # Constants
    "FieldLengths",
    "DecimalPrecision",
    # Types (SQLAlchemy 2.0)
    "intpk",
    "str_3",
    "str_10",
    "str_12",
    "str_20",
    "str_50",
    "str_100",
    "str_200",
    "str_500",
    "text_field",
    "decimal_price",
    "decimal_quantity",
    "decimal_percentage",
    "decimal_weight",
    "decimal_dimension",
    "decimal_volume",
    "decimal_exchange",
    "datetime_tz",
    "bool_true",
    "bool_false",
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
