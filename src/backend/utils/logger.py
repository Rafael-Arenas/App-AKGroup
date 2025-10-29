"""
Configuración de logging usando Loguru.

Proporciona un logger configurado para la aplicación con rotación de archivos,
niveles de log, y formato personalizado.
"""

import sys
from pathlib import Path

from loguru import logger as loguru_logger

from src.backend.config.settings import get_settings

settings = get_settings()

# Remover handlers por defecto de loguru
loguru_logger.remove()

# Formato personalizado
LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)


def setup_logger():
    """
    Configura el logger con los settings de la aplicación.

    Configura dos handlers:
    1. Console output (stdout) con nivel INFO o superior
    2. File output con rotación y retención configurables

    Example:
        setup_logger()
        logger.info("Aplicación iniciada")
        logger.error("Error crítico", error_details={"code": 500})
    """
    # Crear directorio de logs si no existe
    log_file_path = Path(settings.log_file)
    log_file_path.parent.mkdir(parents=True, exist_ok=True)

    # Handler para console (stdout)
    loguru_logger.add(
        sys.stdout,
        format=LOG_FORMAT,
        level=settings.log_level,
        colorize=True,
    )

    # Handler para archivo con rotación
    loguru_logger.add(
        settings.log_file,
        format=LOG_FORMAT,
        level=settings.log_level,
        rotation=settings.log_rotation,  # Rotar cuando alcanza el tamaño
        retention=settings.log_retention,  # Mantener logs por X días
        compression="zip",  # Comprimir logs antiguos
        encoding="utf-8",
    )

    loguru_logger.info(f"Logger configurado - Nivel: {settings.log_level}")
    loguru_logger.info(f"Archivo de log: {settings.log_file}")


# Alias para usar en toda la aplicación
logger = loguru_logger

# Configurar automáticamente al importar
setup_logger()
