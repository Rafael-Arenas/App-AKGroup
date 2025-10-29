"""
Manejadores de errores para FastAPI.

Convierte excepciones de la aplicación en respuestas HTTP apropiadas.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse

from src.exceptions.base import AppException, DatabaseException
from src.exceptions.repository import NotFoundException, DuplicateException
from src.exceptions.service import ValidationException, BusinessRuleException
from src.utils.logger import logger


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """
    Manejador general para AppException.

    Args:
        request: Request de FastAPI
        exc: Excepción de aplicación

    Returns:
        JSONResponse con error formateado
    """
    logger.error(f"AppException: {exc.message}", extra={"details": exc.details})

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": exc.message,
            "details": exc.details
        }
    )


async def not_found_exception_handler(request: Request, exc: NotFoundException) -> JSONResponse:
    """
    Manejador para NotFoundException.

    Args:
        request: Request de FastAPI
        exc: Excepción de entidad no encontrada

    Returns:
        JSONResponse con status 404
    """
    logger.warning(f"NotFoundException: {exc.message}", extra={"details": exc.details})

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": "Not Found",
            "message": exc.message,
            "details": exc.details
        }
    )


async def duplicate_exception_handler(request: Request, exc: DuplicateException) -> JSONResponse:
    """
    Manejador para DuplicateException.

    Args:
        request: Request de FastAPI
        exc: Excepción de entidad duplicada

    Returns:
        JSONResponse con status 409
    """
    logger.warning(f"DuplicateException: {exc.message}", extra={"details": exc.details})

    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "error": "Conflict",
            "message": exc.message,
            "details": exc.details
        }
    )


async def validation_exception_handler(request: Request, exc: ValidationException) -> JSONResponse:
    """
    Manejador para ValidationException.

    Args:
        request: Request de FastAPI
        exc: Excepción de validación

    Returns:
        JSONResponse con status 400
    """
    logger.warning(f"ValidationException: {exc.message}", extra={"details": exc.details})

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Validation Error",
            "message": exc.message,
            "details": exc.details
        }
    )


async def business_rule_exception_handler(request: Request, exc: BusinessRuleException) -> JSONResponse:
    """
    Manejador para BusinessRuleException.

    Args:
        request: Request de FastAPI
        exc: Excepción de regla de negocio

    Returns:
        JSONResponse con status 422
    """
    logger.warning(f"BusinessRuleException: {exc.message}", extra={"details": exc.details})

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Business Rule Violation",
            "message": exc.message,
            "details": exc.details
        }
    )


async def database_exception_handler(request: Request, exc: DatabaseException) -> JSONResponse:
    """
    Manejador para DatabaseException.

    Args:
        request: Request de FastAPI
        exc: Excepción de base de datos

    Returns:
        JSONResponse con status 500
    """
    logger.error(f"DatabaseException: {exc.message}", extra={"details": exc.details})

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Database Error",
            "message": "Error al acceder a la base de datos",
            "details": exc.details if logger.level == "DEBUG" else {}
        }
    )
