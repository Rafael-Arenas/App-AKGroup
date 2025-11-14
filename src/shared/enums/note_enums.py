"""
Enumeraciones para notas (Note).

Define las prioridades de notas utilizadas en el sistema.
"""

import enum


class NotePriority(str, enum.Enum):
    """
    Prioridad de una nota.

    Values:
        LOW: Prioridad baja
        NORMAL: Prioridad normal (default)
        HIGH: Prioridad alta
        URGENT: Urgente

    Example:
        >>> priority = NotePriority.HIGH
        >>> print(priority.value)
        'high'
    """

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
