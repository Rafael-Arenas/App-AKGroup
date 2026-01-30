"""
LanguageSelector - Selector de idioma para la barra de navegación.

Permite cambiar entre idiomas disponibles (ES, EN, FR).
"""

from typing import ClassVar

import flet as ft
from loguru import logger

from src.frontend.app_state import app_state
from src.frontend.i18n.translation_manager import translation_manager


class LanguageSelector(ft.PopupMenuButton):
    """
    Selector de idioma con menú desplegable.

    Muestra el idioma actual y permite cambiar entre los idiomas disponibles.
    """

    # Nombres de idiomas en su propio idioma
    _LANGUAGE_NAMES: ClassVar[dict[str, str]] = {
        "es": "Español",
        "en": "English",
        "fr": "Français",
    }

    # Banderas emoji para cada idioma
    _LANGUAGE_FLAGS: ClassVar[dict[str, str]] = {
        "es": "🇪🇸",
        "en": "🇬🇧",
        "fr": "🇫🇷",
    }

    def __init__(self):
        """
        Inicializa el selector de idioma.

        Example:
            >>> selector = LanguageSelector()
        """
        super().__init__()

        # Configuración
        self.icon = ft.Icons.LANGUAGE
        self.tooltip = "Cambiar idioma"

        # Construir items del menú
        self.items = self._build_menu_items()

        # Suscribirse a cambios de idioma para actualizar el menú
        app_state.i18n.add_observer(self._on_language_change)

    def _build_menu_items(self) -> list[ft.PopupMenuItem]:
        """
        Construye los items del menú de idiomas.

        Returns:
            Lista de items del menú
        """
        items = []
        current_language = app_state.i18n.current_language

        for lang_code in app_state.i18n.available_languages:
            lang_name = self._LANGUAGE_NAMES.get(lang_code, lang_code)
            lang_flag = self._LANGUAGE_FLAGS.get(lang_code, "🌐")
            is_current = lang_code == current_language

            # Crear contenido personalizado para mejor alineación
            if is_current:
                content = ft.Row(
                    [
                        ft.Text(lang_flag, size=16),
                        ft.Container(width=8),
                        ft.Text(lang_name, size=14),
                        ft.Container(expand=True),
                        ft.Icon(ft.Icons.CHECK, size=18),
                    ],
                    spacing=0,
                    alignment=ft.MainAxisAlignment.START,
                )
                items.append(
                    ft.PopupMenuItem(
                        content=content,
                        on_click=lambda e, code=lang_code: self._on_language_select(
                            code
                        ),
                    )
                )
            else:
                content = ft.Row(
                    [
                        ft.Text(lang_flag, size=16),
                        ft.Container(width=8),
                        ft.Text(lang_name, size=14),
                    ],
                    spacing=0,
                    alignment=ft.MainAxisAlignment.START,
                )
                items.append(
                    ft.PopupMenuItem(
                        content=content,
                        on_click=lambda e, code=lang_code: self._on_language_select(
                            code
                        ),
                    )
                )

        return items

    async def _on_language_select(self, lang_code: str):
        """
        Maneja la selección de un idioma.

        Args:
            lang_code: Código del idioma seleccionado
        """
        current = app_state.i18n.current_language
        if lang_code == current:
            return

        logger.info(f"Cambiando idioma: {current} -> {lang_code}")

        # Actualizar idioma en translation_manager y app_state
        translation_manager.set_language(lang_code)
        await app_state.i18n.set_language(lang_code)

    def _on_language_change(self):
        """Callback cuando cambia el idioma."""
        # Reconstruir items del menú con el nuevo idioma seleccionado
        self.items = self._build_menu_items()

        # Actualizar UI
        if self.page:
            self.update()
            logger.debug("LanguageSelector actualizado")


# Exportar
__all__ = ["LanguageSelector"]
