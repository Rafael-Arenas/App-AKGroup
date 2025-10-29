"""
Dependencias de FastAPI.

Proporciona funciones de dependency injection para la API,
incluyendo sesión de base de datos y autenticación.
"""

from typing import Generator

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.backend.database.session import get_db
from src.backend.utils.logger import logger


def get_database() -> Generator[Session, None, None]:
    """
    Dependency para obtener sesión de base de datos.

    Yields:
        Session: Sesión de SQLAlchemy

    Example:
        @router.get("/items")
        def get_items(db: Session = Depends(get_database)):
            return db.query(Item).all()
    """
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()


def get_current_user_id() -> int:
    """
    Dependency para obtener ID del usuario actual.

    Por ahora retorna un user_id fijo (1) para testing.
    TODO: Implementar autenticación con JWT.

    Returns:
        int: ID del usuario actual

    Example:
        @router.post("/items")
        def create_item(user_id: int = Depends(get_current_user_id)):
            # user_id se usa para auditoría
            pass
    """
    # TODO: Implementar autenticación real con JWT
    # Por ahora, retornamos user_id = 1 para testing
    return 1


def validate_pagination(
    skip: int = 0,
    limit: int = 100
) -> tuple[int, int]:
    """
    Valida y retorna parámetros de paginación.

    Args:
        skip: Registros a saltar (default: 0)
        limit: Número máximo de registros (default: 100)

    Returns:
        tuple: (skip, limit) validados

    Raises:
        HTTPException: Si los parámetros son inválidos

    Example:
        @router.get("/items")
        def get_items(
            pagination: tuple = Depends(validate_pagination),
            db: Session = Depends(get_database)
        ):
            skip, limit = pagination
            return db.query(Item).offset(skip).limit(limit).all()
    """
    if skip < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El parámetro 'skip' debe ser mayor o igual a 0"
        )

    if limit < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El parámetro 'limit' debe ser mayor a 0"
        )

    if limit > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El parámetro 'limit' no puede exceder 1000"
        )

    return skip, limit
