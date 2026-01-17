"""
Tipos anotados para SQLAlchemy 2.0.

Este módulo proporciona tipos reutilizables con Annotated para definir
columnas de forma concisa y consistente en los modelos.

Usage:
    from src.backend.models.base.types import intpk, str_200, decimal_price
    
    class MyModel(Base):
        id: Mapped[intpk]
        name: Mapped[str_200]
        price: Mapped[decimal_price | None]
"""

import pendulum
from datetime import datetime
from decimal import Decimal
from typing import Annotated

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, Text
from sqlalchemy.orm import mapped_column

from .constants import DecimalPrecision, FieldLengths

# ============ PRIMARY KEY TYPES ============

intpk = Annotated[int, mapped_column(Integer, primary_key=True, autoincrement=True)]
"""Integer primary key with autoincrement."""

# ============ STRING TYPES ============

str_3 = Annotated[str, mapped_column(String(FieldLengths.TRIGRAM))]
"""String(3) for trigrams and short codes."""

str_10 = Annotated[str, mapped_column(String(FieldLengths.REVISION))]
"""String(10) for revisions."""

str_12 = Annotated[str, mapped_column(String(FieldLengths.RUT))]
"""String(12) for Chilean RUT."""

str_20 = Annotated[str, mapped_column(String(FieldLengths.CODE))]
"""String(20) for codes and short identifiers."""

str_50 = Annotated[str, mapped_column(String(FieldLengths.REFERENCE))]
"""String(50) for references and document numbers."""

str_100 = Annotated[str, mapped_column(String(FieldLengths.SHORT_NAME))]
"""String(100) for short names."""

str_200 = Annotated[str, mapped_column(String(FieldLengths.NAME))]
"""String(200) for full names."""

str_500 = Annotated[str, mapped_column(String(FieldLengths.URL))]
"""String(500) for URLs and long descriptions."""

text_field = Annotated[str, mapped_column(Text)]
"""Text field for unlimited length content."""

# ============ DECIMAL TYPES ============

decimal_price = Annotated[Decimal, mapped_column(Numeric(*DecimalPrecision.PRICE))]
"""Decimal(15,2) for monetary amounts."""

decimal_quantity = Annotated[Decimal, mapped_column(Numeric(*DecimalPrecision.QUANTITY))]
"""Decimal(15,3) for quantities with 3 decimal places."""

decimal_percentage = Annotated[Decimal, mapped_column(Numeric(*DecimalPrecision.PERCENTAGE))]
"""Decimal(5,2) for percentages (0.00 - 100.00)."""

decimal_weight = Annotated[Decimal, mapped_column(Numeric(*DecimalPrecision.WEIGHT))]
"""Decimal(10,3) for weights in kg."""

decimal_dimension = Annotated[Decimal, mapped_column(Numeric(*DecimalPrecision.DIMENSION))]
"""Decimal(10,2) for dimensions (length, width, height)."""

decimal_volume = Annotated[Decimal, mapped_column(Numeric(*DecimalPrecision.VOLUME))]
"""Decimal(10,4) for volume in cubic meters."""

decimal_exchange = Annotated[Decimal, mapped_column(Numeric(*DecimalPrecision.EXCHANGE_RATE))]
"""Decimal(12,6) for exchange rates."""

# ============ DATETIME TYPES ============

datetime_tz = Annotated[pendulum.DateTime, mapped_column(DateTime(timezone=True))]
"""DateTime with timezone support."""

# ============ BOOLEAN TYPES ============

bool_true = Annotated[bool, mapped_column(Boolean, default=True)]
"""Boolean defaulting to True."""

bool_false = Annotated[bool, mapped_column(Boolean, default=False)]
"""Boolean defaulting to False."""
