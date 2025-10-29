"""
Database session management.

Provides session factory and dependency injection utilities
for database access throughout the application.
"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import Session, sessionmaker

from src.database.engine import engine

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,  # Don't expire objects after commit
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency injection function for database sessions.

    Yields:
        Session: SQLAlchemy session

    Example:
        # FastAPI dependency
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()

        # Manual usage
        db = next(get_db())
        try:
            items = db.query(Item).all()
        finally:
            db.close()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def session_scope():
    """
    Context manager for database sessions with automatic commit/rollback.

    Yields:
        Session: SQLAlchemy session

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
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_session() -> Session:
    """
    Get a new database session.

    Returns:
        Session: SQLAlchemy session

    Note:
        Caller is responsible for closing the session.

    Example:
        session = get_session()
        try:
            users = session.query(User).all()
        finally:
            session.close()
    """
    return SessionLocal()
