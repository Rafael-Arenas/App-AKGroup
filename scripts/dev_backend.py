"""
Script para ejecutar el backend FastAPI en modo desarrollo.

Inicia el servidor uvicorn con hot reload.
"""

import sys
from pathlib import Path

# Agregar raíz del proyecto al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import uvicorn
from loguru import logger

from src.backend.config.settings import settings


def main() -> None:
    """
    Inicia el servidor backend FastAPI.

    Configuración:
        - Host: De settings.api_host
        - Port: De settings.api_port
        - Reload: True en desarrollo
        - Log level: De settings.log_level
    """
    logger.info("=" * 60)
    logger.info("Starting Backend FastAPI Server")
    logger.info("=" * 60)
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Database: {settings.database_type}")
    logger.info(f"API URL: http://{settings.api_host}:{settings.api_port}")
    logger.info(f"Docs: http://{settings.api_host}:{settings.api_port}/docs")
    logger.info("=" * 60)

    uvicorn.run(
        "src.backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
