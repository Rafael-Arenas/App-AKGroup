"""
Infraestructura de base de datos para la aplicación AK Group.

Este paquete provee conexión a base de datos, gestión de sesiones,
y configuración del engine.
"""

from src.backend.database.engine import engine
from src.backend.database.session import SessionLocal, get_db, session_scope

__all__ = [
    "engine",
    "SessionLocal",
    "get_db",
    "session_scope",
]
