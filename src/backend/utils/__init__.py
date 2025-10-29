"""
Utilidades compartidas para la aplicación AK Group.

Este paquete contiene utilidades y helpers reutilizables en toda la aplicación.
"""

from src.backend.utils.logger import logger, setup_logger

__all__ = [
    "logger",
    "setup_logger",
]
