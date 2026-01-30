"""
Entry point para la aplicación frontend Flet.

Este archivo inicializa y ejecuta la aplicación de escritorio AK Group.
"""
import flet as ft
from loguru import logger

from src.frontend.views import MainView
from src.frontend.app_state import app_state


async def main(page: ft.Page) -> None:
    """
    Función principal que inicializa la aplicación Flet (asíncrona).

    Args:
        page: Instancia de la página Flet
    """
    logger.info("Iniciando aplicación AK Group Frontend (Async Mode)")
    
    # Inicializar persistencia de estado (AHORA ESPERANDO)
    await app_state.initialize_persistence(page)

    # Configuración de la página
    page.title = "AK Group - Sistema de Gestión"
    page.padding = 0
    page.spacing = 0
    
    # Configuración del tamaño de ventana inicial
    page.window.width = 1400
    page.window.height = 1000
    page.window.min_width = 1000
    page.window.min_height = 700
    
    page.theme_mode = app_state.theme.get_flet_theme_mode()

    # Configurar tema con Material 3
    page.theme = ft.Theme(use_material3=True)
    page.dark_theme = ft.Theme(use_material3=True)

    # Suscribirse a cambios de tema
    def on_theme_change():
        """Callback cuando cambia el tema."""
        page.theme_mode = app_state.theme.get_flet_theme_mode()
        logger.info(f"Theme changed to: {page.theme_mode}")
        page.update()

    app_state.theme.add_observer(on_theme_change)

    # Crear la vista principal
    logger.info("Creando MainView")
    main_view = MainView()

    # Agregar a la página
    page.add(main_view)

    # Forzar actualización inicial
    page.update()

    logger.success("Aplicación AK Group iniciada exitosamente")


if __name__ == "__main__":
    logger.info("Ejecutando aplicación Flet en modo desktop")
    ft.run(main)
