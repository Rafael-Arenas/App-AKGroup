"""
Script para poblar la tabla company_types con los valores del CompanyTypeEnum.

Este script inserta los tipos de empresa definidos en CompanyTypeEnum
en la tabla company_types de la base de datos.

Usage:
    python -m src.scripts.seed_company_types

Example:
    >>> from src.scripts.seed_company_types import seed_company_types
    >>> seed_company_types()
    Seeding company types...
    ✓ CLIENT: Cliente
    ✓ SUPPLIER: Proveedor
    Company types seeded successfully!
"""

from typing import Optional

from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ..models.core.companies import CompanyTypeEnum
from ..models.lookups.lookups import CompanyType


def seed_company_types(
    session: Optional[Session] = None,
    database_url: str = "sqlite:///app_akgroup.db",
) -> None:
    """
    Pobla la tabla company_types con los valores del CompanyTypeEnum.

    Args:
        session: Sesión de SQLAlchemy existente (opcional)
        database_url: URL de la base de datos (usado si no se provee session)

    Example:
        >>> # Con sesión existente
        >>> seed_company_types(session=my_session)

        >>> # Creando nueva sesión
        >>> seed_company_types(database_url="sqlite:///mydb.db")
    """
    # Crear sesión si no se proveyó una
    close_session = False
    if session is None:
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        close_session = True

    try:
        logger.info("Seeding company types...")

        # Iterar sobre todos los valores del enum
        for company_type_enum in CompanyTypeEnum:
            # Verificar si ya existe
            existing = (
                session.query(CompanyType)
                .filter(CompanyType.name == company_type_enum.value)
                .first()
            )

            if existing:
                logger.debug(
                    f"Company type {company_type_enum.value} already exists, skipping"
                )
                continue

            # Crear nuevo registro
            company_type = CompanyType(
                name=company_type_enum.value,
                description=company_type_enum.description,
            )

            session.add(company_type)
            logger.success(
                f"✓ {company_type_enum.value}: {company_type_enum.display_name}"
            )

        # Commit de los cambios
        session.commit()
        logger.success("Company types seeded successfully!")

    except Exception as e:
        logger.error(f"Error seeding company types: {e}")
        session.rollback()
        raise

    finally:
        if close_session:
            session.close()


def main() -> None:
    """Función principal para ejecutar el script."""
    import sys

    # Obtener database_url de argumentos o usar default
    database_url = sys.argv[1] if len(sys.argv) > 1 else "sqlite:///app_akgroup.db"

    logger.info(f"Using database: {database_url}")
    seed_company_types(database_url=database_url)


if __name__ == "__main__":
    main()
