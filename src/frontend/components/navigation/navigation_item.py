"""
NavigationItem - Item individual del NavigationRail.

Representa un elemento de navegación con icono, label opcional y badge.
"""

import flet as ft
from loguru import logger

from src.frontend.color_constants import ColorConstants
from src.frontend.layout_constants import LayoutConstants
from src.frontend.app_state import app_state


class NavigationItem(ft.Container):
    """
    Item individual de navegación con estados visuales.

    Características:
    - Icono (seleccionado/no seleccionado)
    - Label (visible solo cuando el rail está expandido)
    - Badge opcional con contador
    - Estados visuales: normal, hover, activo
    - Tooltip (visible cuando está colapsado)
    """

    def __init__(
        self,
        icon: str,
        icon_selected: str,
        label: str,
        index: int,
        is_selected: bool = False,
        is_expanded: bool = False,
        badge_count: int = 0,
        on_click: callable = None,
    ):
        """
        Inicializa el NavigationItem.

        Args:
            icon: Icono normal
            icon_selected: Icono cuando está seleccionado
            label: Texto del label
            index: Índice del item
            is_selected: Si está seleccionado
            is_expanded: Si el rail está expandido
            badge_count: Contador del badge (0 para ocultar)
            on_click: Callback al hacer click

        Example:
            >>> item = NavigationItem(
            ...     icon=ft.Icons.HOME_OUTLINED,
            ...     icon_selected=ft.Icons.HOME,
            ...     label="Inicio",
            ...     index=0
            ... )
        """
        super().__init__()

        self.icon_name = icon
        self.icon_selected_name = icon_selected
        self.label_text = label
        self.index = index
        self.is_selected = is_selected
        self.is_expanded = is_expanded
        self.badge_count = badge_count
        self.on_click_callback = on_click

        # Configurar container
        self.height = 56  # Altura estándar para items de navegación
        self.border_radius = LayoutConstants.RADIUS_MD
        self.padding = ft.padding.symmetric(
            horizontal=LayoutConstants.PADDING_MD,
            vertical=LayoutConstants.PADDING_SM,
        )
        # Agregar margen para que no esté pegado a los bordes
        self.margin = ft.margin.all(LayoutConstants.PADDING_SM)
        self.ink = True
        self.on_click = self._handle_click
        self.on_hover = self._handle_hover

        # Tooltip (solo cuando está colapsado)
        if not is_expanded:
            self.tooltip = label

        # Aplicar estilos según estado
        self._apply_styles()

        # Contenido
        self.content = self._build_content()

    def _build_content(self) -> ft.Control:
        """
        Construye el contenido del item.

        Returns:
            Control con el contenido del item
        """
        is_dark = app_state.theme.is_dark_mode

        # Icono - mantener color blanco cuando está seleccionado
        icon_color = (
            ColorConstants.APPBAR_ON_BACKGROUND
            if self.is_selected
            else ColorConstants.get_color_for_theme("ON_SURFACE", is_dark)
        )

        icon_widget = ft.Icon(
            self.icon_selected_name if self.is_selected else self.icon_name,
            size=LayoutConstants.ICON_SIZE_MD,
            color=icon_color,
        )

        # Badge en el icono (visible solo cuando colapsado Y hay badge)
        if self.badge_count > 0 and not self.is_expanded:
            icon_with_badge = ft.Stack(
                [
                    ft.Container(
                        content=icon_widget,
                        alignment=ft.alignment.center,
                    ),
                    ft.Container(
                        content=ft.Text(
                            str(min(self.badge_count, 99))
                            if self.badge_count < 100
                            else "99+",
                            size=LayoutConstants.FONT_SIZE_XS,
                            weight=ft.FontWeight.BOLD,
                            color=ColorConstants.BADGE_TEXT,
                        ),
                        bgcolor=ColorConstants.BADGE_BACKGROUND,
                        border_radius=LayoutConstants.BADGE_SIZE_SM // 2,
                        width=LayoutConstants.BADGE_SIZE_SM,
                        height=LayoutConstants.BADGE_SIZE_SM,
                        alignment=ft.alignment.center,
                        right=-4,
                        top=-4,
                    ),
                ],
                width=LayoutConstants.ICON_SIZE_MD,
                height=LayoutConstants.ICON_SIZE_MD,
            )
        else:
            icon_with_badge = icon_widget

        # SIEMPRE usar la misma estructura (Row) para evitar movimiento del icono
        # Los labels y badges simplemente cambian de opacidad
        label_color = (
            ColorConstants.APPBAR_ON_BACKGROUND
            if self.is_selected
            else ColorConstants.get_color_for_theme("ON_SURFACE", is_dark)
        )

        controls = [
            ft.Container(
                content=icon_with_badge,
                width=LayoutConstants.ICON_SIZE_MD + 8,
                alignment=ft.alignment.center_left,
            ),
            ft.Container(width=LayoutConstants.SPACING_MD),
            ft.Container(
                content=ft.Text(
                    self.label_text,
                    size=LayoutConstants.FONT_SIZE_MD,
                    weight=ft.FontWeight.W_500 if self.is_selected else ft.FontWeight.NORMAL,
                    color=label_color,
                ),
                expand=True,
                opacity=1.0 if self.is_expanded else 0.0,
                animate_opacity=LayoutConstants.get_animation(),
            ),
        ]

        # Badge al final (visible solo cuando expandido Y hay badge)
        if self.badge_count > 0:
            controls.append(
                ft.Container(
                    content=ft.Text(
                        str(min(self.badge_count, 99))
                        if self.badge_count < 100
                        else "99+",
                        size=LayoutConstants.FONT_SIZE_XS,
                        weight=ft.FontWeight.BOLD,
                        color=ColorConstants.BADGE_TEXT,
                    ),
                    bgcolor=ColorConstants.BADGE_BACKGROUND,
                    border_radius=LayoutConstants.BADGE_SIZE // 2,
                    padding=ft.padding.symmetric(
                        horizontal=6,
                        vertical=2,
                    ),
                    alignment=ft.alignment.center,
                    opacity=1.0 if self.is_expanded else 0.0,
                    animate_opacity=LayoutConstants.get_animation(),
                )
            )

        return ft.Row(
            controls,
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        )

    def _apply_styles(self) -> None:
        """Aplica los estilos según el estado."""
        is_dark = app_state.theme.is_dark_mode

        if self.is_selected:
            # Estado activo
            self.bgcolor = ColorConstants.RAIL_SELECTED_DARK if is_dark else ColorConstants.RAIL_SELECTED_LIGHT
            self.border = None  # Sin borde lateral
        else:
            # Estado normal
            self.bgcolor = None
            self.border = None

    def _handle_click(self, e):
        """
        Maneja el click en el item.

        Args:
            e: Evento de Flet
        """
        logger.debug(f"NavigationItem clicked: {self.label_text} (index {self.index})")
        if self.on_click_callback:
            self.on_click_callback(self.index)

    def _handle_hover(self, e):
        """
        Maneja el hover.

        Args:
            e: Evento de Flet
        """
        is_dark = app_state.theme.is_dark_mode

        if not self.is_selected:
            if e.data == "true":
                # Mouse enter
                hover_color = ColorConstants.get_color_for_theme("OVERLAY", is_dark)
                self.bgcolor = hover_color
            else:
                # Mouse leave
                self.bgcolor = None
            # Solo actualizar si está en la página
            if self.page:
                self.update()

    def set_selected(self, selected: bool) -> None:
        """
        Establece el estado de selección.

        Args:
            selected: True si está seleccionado

        Example:
            >>> item.set_selected(True)
        """
        if self.is_selected != selected:
            self.is_selected = selected
            self._apply_styles()
            self.content = self._build_content()
            if self.page:
                self.update()

    def set_expanded(self, expanded: bool) -> None:
        """
        Establece el estado expandido.

        Args:
            expanded: True si está expandido

        Example:
            >>> item.set_expanded(True)
        """
        if self.is_expanded != expanded:
            self.is_expanded = expanded
            self.tooltip = None if expanded else self.label_text
            self.content = self._build_content()
            if self.page:
                self.update()

    def set_badge(self, count: int) -> None:
        """
        Establece el contador del badge.

        Args:
            count: Número a mostrar (0 para ocultar)

        Example:
            >>> item.set_badge(5)
        """
        if self.badge_count != count:
            self.badge_count = count
            self.content = self._build_content()
            if self.page:
                self.update()


# Exportar
__all__ = ["NavigationItem"]
