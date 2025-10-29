"""
Script para ejecutar solo el backend FastAPI.

Ejecuta el servidor de desarrollo del backend en el puerto 8000.
"""

import uvicorn
from loguru import logger


def main() -> None:
    """
    Ejecuta el servidor de desarrollo del backend.
    """
    logger.info("Iniciando backend FastAPI en desarrollo...")
    logger.info("URL: http://localhost:8000")
    logger.info("Docs: http://localhost:8000/docs")

    uvicorn.run(
        "src.backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    main()
