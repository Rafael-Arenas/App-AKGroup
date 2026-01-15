"""
Constantes centralizadas para modelos SQLAlchemy.

Este módulo define constantes reutilizables para evitar números mágicos
y facilitar el mantenimiento de los modelos.

Usage:
    from src.backend.models.base.constants import FieldLengths, DecimalPrecision
    
    name: Mapped[str] = mapped_column(String(FieldLengths.NAME))
    price: Mapped[Decimal] = mapped_column(Numeric(*DecimalPrecision.PRICE))
"""


class FieldLengths:
    """Longitudes máximas de campos de texto."""

    # Identificadores
    NAME = 200
    SHORT_NAME = 100
    REFERENCE = 50
    CODE = 20
    TRIGRAM = 3
    REVISION = 10

    # Contacto
    EMAIL = 100
    PHONE = 20

    # URLs
    URL = 500
    URL_SHORT = 200

    # Descripciones
    DESCRIPTION = 500
    NOTES = 2000

    # Internacionales
    HS_CODE = 20
    INTRACOMMUNITY = 50
    CUSTOMS_NUMBER = 50
    COUNTRY_CODE = 5
    CURRENCY_CODE = 3
    CURRENCY_SYMBOL = 10

    # Números de documento
    DOCUMENT_NUMBER = 50
    RUT = 12

    # Direcciones
    ADDRESS = 500
    CITY_NAME = 100
    POSTAL_CODE = 20


class DecimalPrecision:
    """Precisión para campos decimales (precision, scale)."""

    # Precios y montos: hasta 999,999,999,999.99
    PRICE = (15, 2)

    # Cantidades: permite 3 decimales para stock
    QUANTITY = (15, 3)

    # Porcentajes: hasta 100.00
    PERCENTAGE = (5, 2)

    # Pesos y dimensiones
    WEIGHT = (10, 3)
    DIMENSION = (10, 2)
    VOLUME = (10, 4)

    # Exchange rates: 6 decimales para precisión
    EXCHANGE_RATE = (12, 6)
