"""
Script para ejecutar el frontend Flet en modo desarrollo.

Inicia la aplicación Flet desktop.
"""

import sys
from pathlib import Path

# Agregar raíz del proyecto al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import flet as ft
from loguru import logger

from src.frontend.main import main as flet_main
from src.frontend.config.settings import settings


def main() -> None:
    """
    Inicia la aplicación frontend Flet.

    Configuración:
        - Título: De settings.app_title
        - Tamaño: De settings.app_width y app_height
        - Tema: De settings.ui_theme
    """
    logger.info("=" * 60)
    logger.info("Starting Frontend Flet Application")
    logger.info("=" * 60)
    logger.info(f"App Title: {settings.app_title}")
    logger.info(f"API URL: {settings.api_url}")
    logger.info(f"Window Size: {settings.app_width}x{settings.app_height}")
    logger.info(f"Theme: {settings.ui_theme}")
    logger.info("=" * 60)

    ft.app(target=flet_main)


if __name__ == "__main__":
    main()
