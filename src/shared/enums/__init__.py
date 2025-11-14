"""
Enumeraciones compartidas entre frontend y backend.

Este módulo exporta todos los enums que son utilizados tanto por el frontend
como por el backend, garantizando la independencia entre ambas capas.
"""

from .address_enums import AddressType
from .note_enums import NotePriority
from .product_enums import ProductType

__all__ = [
    "AddressType",
    "NotePriority",
    "ProductType",
]
