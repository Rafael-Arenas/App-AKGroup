"""
Schemas de validación usando Pydantic.

Este paquete contiene todos los schemas de Pydantic para validación de datos,
serialización y documentación automática de la API.
"""

from src.schemas.base import BaseSchema, BaseResponse, TimestampResponse

__all__ = [
    "BaseSchema",
    "BaseResponse",
    "TimestampResponse",
]
