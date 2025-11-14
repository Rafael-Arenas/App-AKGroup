"""
Enumeraciones para direcciones (Address).

Define los tipos de dirección utilizados en el sistema.
"""

import enum


class AddressType(str, enum.Enum):
    """
    Tipos de dirección.

    Values:
        DELIVERY: Dirección de entrega
        BILLING: Dirección de facturación
        HEADQUARTERS: Sede central/matriz
        BRANCH: Sucursal

    Example:
        >>> address_type = AddressType.DELIVERY
        >>> print(address_type.value)
        'delivery'
    """

    DELIVERY = "delivery"
    BILLING = "billing"
    HEADQUARTERS = "headquarters"
    BRANCH = "branch"
