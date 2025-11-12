"""
NavigationSection - Sección agrupadora del NavigationRail.

Agrupa items de navegación relacionados con un label opcional.
"""

import flet as ft
from loguru import logger

from src.frontend.layout_constants import LayoutConstants
from src.frontend.app_state import app_state
from src.frontend.components.navigation.navigation_item import NavigationItem


class NavigationSection(ft.Column):
    """
    Sección del NavigationRail que agrupa items relacionados.

    Características:
    - Label de grupo (visible solo cuando expandido)
    - Lista de NavigationItems
    - Divider visual entre secciones
    """

    def __init__(
        self,
        group_label: str | None,
        items: list[dict],
        selected_index: int = 0,
        is_expanded: bool = False,
        on_item_click: callable = None,
        section_badges: dict[int, int] = None,
    ):
        """
        Inicializa la NavigationSection.

        Args:
            group_label: Label del grupo (None para no mostrar)
            items: Lista de diccionarios con info de items
            selected_index: Índice del item seleccionado
            is_expanded: Si el rail está expandido
            on_item_click: Callback al hacer click en un item
            section_badges: Dict con badges por índice de item

        Example:
            >>> section = NavigationSection(
            ...     group_label="Gestión",
            ...     items=[{"index": 0, "icon": ft.Icons.HOME, ...}],
            ...     selected_index=0
            ... )
        """
        super().__init__()

        self.group_label_text = group_label
        self.items_data = items
        self.selected_index = selected_index
        self.is_expanded = is_expanded
        self.on_item_click_callback = on_item_click
        self.section_badges = section_badges or {}

        # Configurar column
        self.spacing = LayoutConstants.SPACING_XS
        self.tight = True

        # Construir controles
        self.controls = self._build_controls()

    def _build_controls(self) -> list[ft.Control]:
        """
        Construye los controles de la sección.

        Returns:
            Lista de controles para la sección
        """
        controls = []

        # Label del grupo - SIEMPRE agregar el espacio para mantener posición fija
        # Usar opacidad animada para transición suave
        if self.group_label_text:
            controls.append(
                ft.Container(
                    content=ft.Text(
                        self.group_label_text,
                        size=LayoutConstants.FONT_SIZE_XS + 1,  # 11px
                        weight=ft.FontWeight.W_600,
                    ),
                    padding=ft.padding.only(
                        left=LayoutConstants.PADDING_MD,
                        top=LayoutConstants.PADDING_SM,
                        bottom=LayoutConstants.PADDING_XS,
                    ),
                    height=28,  # Altura fija para mantener espacio
                    opacity=1.0 if self.is_expanded else 0.0,
                    animate_opacity=LayoutConstants.get_animation(),
                )
            )

        # Items de navegación
        for item_data in self.items_data:
            index = item_data["index"]
            badge_count = self.section_badges.get(index, 0)

            nav_item = NavigationItem(
                icon=item_data["icon"],
                icon_selected=item_data["icon_selected"],
                label=item_data["label"],
                index=index,
                is_selected=(index == self.selected_index),
                is_expanded=self.is_expanded,
                badge_count=badge_count,
                on_click=self._handle_item_click,
            )

            controls.append(nav_item)

        return controls

    def _handle_item_click(self, index: int) -> None:
        """
        Maneja el click en un item de la sección.

        Args:
            index: Índice del item clickeado
        """
        logger.debug(f"NavigationSection item clicked: index {index}")
        if self.on_item_click_callback:
            self.on_item_click_callback(index)

    def set_selected_index(self, index: int) -> None:
        """
        Establece el índice seleccionado.

        Args:
            index: Nuevo índice seleccionado

        Example:
            >>> section.set_selected_index(1)
        """
        if self.selected_index != index:
            self.selected_index = index
            # Reconstruir para actualizar selección
            self.controls = self._build_controls()
            if self.page:
                self.update()

    def set_expanded(self, expanded: bool) -> None:
        """
        Establece el estado expandido.

        Args:
            expanded: True para expandir

        Example:
            >>> section.set_expanded(True)
        """
        if self.is_expanded != expanded:
            self.is_expanded = expanded
            # Reconstruir para mostrar/ocultar label y actualizar items
            self.controls = self._build_controls()
            if self.page:
                self.update()

    def update_badges(self, section_badges: dict[int, int]) -> None:
        """
        Actualiza los badges de los items.

        Args:
            section_badges: Dict con badges por índice

        Example:
            >>> section.update_badges({0: 5, 2: 10})
        """
        self.section_badges = section_badges
        # Reconstruir para actualizar badges
        self.controls = self._build_controls()
        if self.page:
            self.update()


# Exportar
__all__ = ["NavigationSection"]
