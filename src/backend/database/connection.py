"""
Database connection utilities.

Provee utilidades para crear y gestionar sesiones de base de datos
en el contexto de facades y API layer.
"""

from contextlib import contextmanager
from collections.abc import Generator

from sqlalchemy.orm import Session

from src.backend.database.session import SessionLocal, get_session
from src.backend.utils.logger import logger


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """
    Context manager para sesiones de base de datos con auto-commit/rollback.

    Esta es una referencia al session_scope de src.database.session
    para mantener compatibilidad con el código existente.

    Yields:
        Session: Sesión de SQLAlchemy

    Example:
        with session_scope() as session:
            user = User(name="John")
            session.add(user)
            # Automatic commit on success, rollback on exception
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
        logger.debug("Sesión comprometida exitosamente")
    except Exception as e:
        session.rollback()
        logger.error(f"Error en sesión, haciendo rollback: {str(e)}")
        raise
    finally:
        session.close()
        logger.debug("Sesión cerrada")


def get_db_session() -> Session:
    """
    Obtiene una nueva sesión de base de datos.

    Returns:
        Session: Nueva sesión de SQLAlchemy

    Note:
        El llamador es responsable de cerrar la sesión.

    Example:
        session = get_db_session()
        try:
            stmt = select(User)
            users = session.execute(stmt).scalars().all()
        finally:
            session.close()
    """
    return get_session()


# Re-export SessionLocal para compatibilidad
__all__ = [
    "session_scope",
    "get_db_session",
    "SessionLocal",
]
