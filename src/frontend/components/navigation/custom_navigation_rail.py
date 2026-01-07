"""
CustomNavigationRail - Barra de navegación lateral personalizada.

Navegación principal con capacidad de expandir/colapsar y secciones agrupadas.
"""

import flet as ft
from loguru import logger

from src.frontend.app_state import app_state
from src.frontend.i18n.translation_manager import t
from src.frontend.layout_constants import LayoutConstants
from src.frontend.navigation_config import NAVIGATION_STRUCTURE
from src.frontend.components.navigation.navigation_section import NavigationSection


class CustomNavigationRail(ft.Container):
    """
    Barra de navegación lateral personalizada con expansión.

    Características:
    - Expandible/colapsable (72px <-> 256px)
    - Secciones agrupadas con dividers
    - Badges por sección
    - Animación suave de transición
    - Integración con AppState
    """

    def __init__(
        self,
        selected_index: int = 0,
        expanded: bool = False,
        on_destination_change: callable = None,
        on_expand_toggle: callable = None,
        section_badges: dict[int, int] = None,
    ):
        """
        Inicializa el CustomNavigationRail.

        Args:
            selected_index: Índice de la sección seleccionada
            expanded: Si está expandido inicialmente
            on_destination_change: Callback cuando cambia la sección (index)
            on_expand_toggle: Callback cuando se expande/colapsa (expanded)
            section_badges: Dict con badges por índice de sección

        Example:
            >>> rail = CustomNavigationRail(
            ...     selected_index=0,
            ...     expanded=True,
            ...     on_destination_change=handle_navigation
            ... )
        """
        super().__init__()

        self.selected_index = selected_index
        self.expanded = expanded
        self.on_destination_change_callback = on_destination_change
        self.on_expand_toggle_callback = on_expand_toggle
        self.section_badges = section_badges or {}

        # Configurar container con animación suave de ancho
        self.width = (
            LayoutConstants.RAIL_WIDTH_EXPANDED
            if expanded
            else LayoutConstants.RAIL_WIDTH_COLLAPSED
        )
        # CLAVE: Animar el ancho para evitar el salto visual
        self.animate = LayoutConstants.get_animation()

        # Suscribirse a cambios de idioma
        app_state.i18n.add_observer(self._on_language_change)

        # Suscribirse a cambios de tema
        app_state.theme.add_observer(self._on_theme_change)

        # Contenido
        self.content = self._build_content()

    def _build_content(self) -> ft.Control:
        """
        Construye el contenido del rail.

        Returns:
            Control con el contenido del rail
        """
        # Botón de expansión/colapso con tooltips traducidos
        expand_tooltip = (
            t("navigation.expand_menu")
            if not self.expanded
            else t("navigation.collapse_menu")
        )
        expand_button = ft.Container(
            content=ft.IconButton(
                icon=ft.Icons.MENU if not self.expanded else ft.Icons.MENU_OPEN,
                tooltip=expand_tooltip,
                on_click=self._handle_expand_toggle,
            ),
            padding=ft.padding.symmetric(
                vertical=LayoutConstants.PADDING_SM,
                horizontal=LayoutConstants.PADDING_MD,
            ),
            alignment=ft.Alignment(-1, 0),  # left - Siempre fijo a la izquierda
        )

        # Secciones de navegación con traducciones
        sections = []

        for i, group_data in enumerate(NAVIGATION_STRUCTURE):
            # Agregar divider antes de cada grupo (excepto el primero)
            if i > 0:
                sections.append(
                    ft.Divider(
                        height=1,
                        thickness=1,
                    )
                )
                sections.append(
                    ft.Container(height=LayoutConstants.SPACING_SM)
                )

            # Traducir label del grupo si existe
            group_label = None
            if group_data["group_label"]:
                group_label = t(group_data["group_label"])

            # Traducir labels de items
            translated_items = []
            for item in group_data["items"]:
                translated_item = item.copy()
                translated_item["label"] = t(item["label"])
                translated_items.append(translated_item)

            # Agregar sección
            section = NavigationSection(
                group_label=group_label,
                items=translated_items,
                selected_index=self.selected_index,
                is_expanded=self.expanded,
                on_item_click=self._handle_destination_change,
                section_badges=self.section_badges,
            )
            sections.append(section)

        # Columna principal con todas las secciones
        # Usar alignment=start para mantener los items arriba y evitar movimiento vertical
        sections_column = ft.Column(
            [expand_button] + sections,
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            alignment=ft.MainAxisAlignment.START,
        )

        return sections_column

    def _handle_expand_toggle(self, e):
        """
        Maneja el toggle de expansión/colapso.

        Args:
            e: Evento de Flet
        """
        self.expanded = not self.expanded
        logger.debug(
            f"NavigationRail {'expandido' if self.expanded else 'colapsado'}"
        )

        # Actualizar ancho con animación
        self.width = (
            LayoutConstants.RAIL_WIDTH_EXPANDED
            if self.expanded
            else LayoutConstants.RAIL_WIDTH_COLLAPSED
        )

        # Reconstruir contenido
        self.content = self._build_content()
        # Solo actualizar si está en la página
        if self.page:
            self.update()

        # Notificar callback
        if self.on_expand_toggle_callback:
            self.on_expand_toggle_callback(self.expanded)

    def _handle_destination_change(self, index: int):
        """
        Maneja el cambio de destino de navegación.

        Args:
            index: Índice del destino seleccionado
        """
        if self.selected_index != index:
            logger.info(f"Navegación: {self.selected_index} -> {index}")
            self.selected_index = index
            # Reconstruir para actualizar selección
            self.content = self._build_content()
            # Solo actualizar si está en la página
            if self.page:
                self.update()

            # Notificar callback
            if self.on_destination_change_callback:
                self.on_destination_change_callback(index)

    def set_selected_index(self, index: int) -> None:
        """
        Establece el índice seleccionado.

        Args:
            index: Nuevo índice

        Example:
            >>> rail.set_selected_index(1)
        """
        if self.selected_index != index:
            self.selected_index = index
            self.content = self._build_content()
            if self.page:
                self.update()

    def set_expanded(self, expanded: bool) -> None:
        """
        Establece el estado expandido.

        Args:
            expanded: True para expandir

        Example:
            >>> rail.set_expanded(True)
        """
        if self.expanded != expanded:
            self.expanded = expanded
            self.width = (
                LayoutConstants.RAIL_WIDTH_EXPANDED
                if expanded
                else LayoutConstants.RAIL_WIDTH_COLLAPSED
            )
            self.content = self._build_content()
            if self.page:
                self.update()

    def update_badges(self, section_badges: dict[int, int]) -> None:
        """
        Actualiza los badges de las secciones.

        Args:
            section_badges: Dict con badges por índice de sección

        Example:
            >>> rail.update_badges({0: 5, 2: 10})
        """
        self.section_badges = section_badges
        self.content = self._build_content()
        if self.page:
            self.update()

    def _on_language_change(self):
        """Actualiza el contenido cuando cambia el idioma."""
        self.content = self._build_content()
        if self.page:
            self.update()

    def _on_theme_change(self):
        """Actualiza el contenido cuando cambia el tema."""
        self.content = self._build_content()
        if self.page:
            self.update()


# Exportar
__all__ = ["CustomNavigationRail"]
