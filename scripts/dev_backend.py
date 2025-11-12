"""
Script para ejecutar solo el backend FastAPI.

Ejecuta el servidor de desarrollo del backend en el puerto 8000.
"""

import socket
import sys

import uvicorn
from loguru import logger


def is_port_in_use(port: int, host: str = "localhost") -> bool:
    """
    Verifica si un puerto está en uso.

    Args:
        port: Puerto a verificar
        host: Host a verificar (default: localhost)

    Returns:
        True si el puerto está en uso, False si está libre
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return False
        except OSError:
            return True


def main() -> None:
    """
    Ejecuta el servidor de desarrollo del backend.
    """
    # Verificar si el puerto 8000 está en uso
    if is_port_in_use(8000):
        logger.error("=" * 70)
        logger.error("ERROR: El puerto 8000 ya está en uso")
        logger.error("=" * 70)
        logger.error("")
        logger.error("Otro proceso está usando el puerto 8000.")
        logger.error("Por favor, cierra ese proceso antes de continuar.")
        logger.error("")
        logger.error("En Windows, puedes usar estos comandos:")
        logger.error("  1. Ver qué proceso usa el puerto:")
        logger.error("     netstat -ano | findstr :8000")
        logger.error("")
        logger.error("  2. Matar el proceso (reemplaza <PID> con el número):")
        logger.error("     taskkill /PID <PID> /F")
        logger.error("")
        logger.error("=" * 70)
        sys.exit(1)

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
