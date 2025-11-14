"""
Enumeraciones para productos (Product).

Define los tipos de producto utilizados en el sistema.
"""

import enum


class ProductType(str, enum.Enum):
    """
    Tipos de producto.

    Values:
        ARTICLE: Producto simple sin componentes
        NOMENCLATURE: Producto con BOM (Bill of Materials)
        SERVICE: Servicio (no físico)

    Example:
        >>> product_type = ProductType.ARTICLE
        >>> print(product_type.value)
        'ARTICLE'
    """

    ARTICLE = "ARTICLE"
    NOMENCLATURE = "NOMENCLATURE"
    SERVICE = "SERVICE"
