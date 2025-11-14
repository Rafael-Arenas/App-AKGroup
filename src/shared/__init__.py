"""
Módulo compartido entre backend y frontend.

Este paquete contiene código compartido entre el backend (FastAPI)
y el frontend (Flet), principalmente schemas de Pydantic para
validación y serialización de datos, enums y constantes compartidas.
"""

__version__ = "0.1.0"

# Re-exportar enums para fácil acceso
from .enums import AddressType, NotePriority, ProductType

# Re-exportar constantes más utilizadas
from .constants import (
    PRODUCT_TYPE_ARTICLE,
    PRODUCT_TYPE_NOMENCLATURE,
    PRODUCT_TYPE_SERVICE,
    ADDRESS_TYPE_DELIVERY,
    ADDRESS_TYPE_BILLING,
    COMPANY_TYPE_CUSTOMER,
    COMPANY_TYPE_SUPPLIER,
    COMPANY_TYPE_BOTH,
)

__all__ = [
    # Enums
    "AddressType",
    "NotePriority",
    "ProductType",
    # Constantes de producto
    "PRODUCT_TYPE_ARTICLE",
    "PRODUCT_TYPE_NOMENCLATURE",
    "PRODUCT_TYPE_SERVICE",
    # Constantes de dirección
    "ADDRESS_TYPE_DELIVERY",
    "ADDRESS_TYPE_BILLING",
    # Constantes de empresa
    "COMPANY_TYPE_CUSTOMER",
    "COMPANY_TYPE_SUPPLIER",
    "COMPANY_TYPE_BOTH",
]
