"""
Configuración del engine de base de datos.

Provee el engine de SQLAlchemy configurado basado en los settings de la aplicación.
Soporta tanto SQLite (desarrollo) como MySQL (producción).
"""

from sqlalchemy import create_engine, event
from sqlalchemy.pool import QueuePool, StaticPool

from src.config.settings import get_settings

settings = get_settings()


def create_db_engine():
    """
    Crea el engine de base de datos basado en la configuración.

    Returns:
        Engine: Engine de SQLAlchemy configurado
    """
    database_url = settings.database_url

    if settings.database_type == "sqlite":
        # SQLite configuration
        engine = create_engine(
            database_url,
            echo=settings.database_echo,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,  # For SQLite, use static pool
        )

        # Enable foreign key constraints for SQLite
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    elif settings.database_type == "mysql":
        # MySQL configuration
        engine = create_engine(
            database_url,
            echo=settings.database_echo,
            poolclass=QueuePool,
            pool_size=settings.mysql_pool_size,
            max_overflow=settings.mysql_max_overflow,
            pool_recycle=settings.mysql_pool_recycle,
            pool_pre_ping=True,  # Verify connections before use
            connect_args={
                "connect_timeout": settings.mysql_connect_timeout,
                "charset": "utf8mb4",
            },
        )

        # Log successful MySQL connections
        @event.listens_for(engine, "connect")
        def receive_connect(dbapi_conn, connection_record):
            from src.utils.logger import logger

            logger.debug("MySQL connection established")

    else:
        raise ValueError(f"Unsupported database type: {settings.database_type}")

    return engine


# Create global engine instance
engine = create_db_engine()
