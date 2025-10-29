"""
Jerarquía de excepciones personalizadas para AK Group.

Este paquete define todas las excepciones personalizadas utilizadas
en la aplicación, organizadas por capa (base, repository, service, auth).
"""

from src.backend.exceptions.base import AppException, DatabaseException
from src.backend.exceptions.repository import (
    NotFoundException,
    DuplicateException,
    InvalidStateException,
)
from src.backend.exceptions.service import (
    ValidationException,
    BusinessRuleException,
    UnauthorizedException,
)

__all__ = [
    # Base
    "AppException",
    "DatabaseException",
    # Repository
    "NotFoundException",
    "DuplicateException",
    "InvalidStateException",
    # Service
    "ValidationException",
    "BusinessRuleException",
    "UnauthorizedException",
]
