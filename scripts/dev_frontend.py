"""
Script para ejecutar solo el frontend Flet.

Ejecuta la aplicación de escritorio Flet.
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import flet as ft
from loguru import logger

from src.frontend.main import main as flet_main


def main() -> None:
    """
    Ejecuta la aplicación frontend Flet.
    """
    logger.info("Iniciando frontend Flet en desarrollo...")

    ft.app(target=flet_main)


if __name__ == "__main__":
    main()
