"""
Breadcrumb - Navegación secundaria con migas de pan.

Muestra la ruta de navegación actual y permite navegar a niveles superiores.
"""

import flet as ft
from loguru import logger

from src.frontend.color_constants import ColorConstants
from src.frontend.layout_constants import LayoutConstants
from src.frontend.app_state import app_state


class Breadcrumb(ft.Row):
    """
    Componente de breadcrumb (migas de pan) para navegación secundaria.

    Características:
    - Muestra la ruta completa de navegación
    - Los niveles anteriores son clickeables
    - El último nivel (actual) no es clickeable
    - Separadores visuales entre niveles
    """

    def __init__(
        self,
        path: list[dict] | None = None,
        on_navigate: callable = None,
    ):
        """
        Inicializa el Breadcrumb.

        Args:
            path: Lista de diccionarios con format {"label": str, "route": str | None}
                  Ejemplo: [
                      {"label": "Inicio", "route": "/"},
                      {"label": "Empresas", "route": "/companies"},
                      {"label": "Editar", "route": None}
                  ]
            on_navigate: Callback al hacer click (recibe route)

        Example:
            >>> breadcrumb = Breadcrumb(
            ...     path=[
            ...         {"label": "Inicio", "route": "/"},
            ...         {"label": "Empresas", "route": None}
            ...     ],
            ...     on_navigate=handle_navigation
            ... )
        """
        super().__init__()

        self.path = path or []
        self.on_navigate_callback = on_navigate

        # Configurar row
        self.spacing = LayoutConstants.SPACING_SM
        self.height = 40  # Altura del breadcrumb
        self.vertical_alignment = ft.CrossAxisAlignment.CENTER

        # Construir controles
        self.controls = self._build_controls()

    def _build_controls(self) -> list[ft.Control]:
        """
        Construye los controles del breadcrumb.

        Returns:
            Lista de controles del breadcrumb
        """
        if not self.path:
            return []

        controls = []
        is_dark = app_state.theme.is_dark_mode

        for i, item in enumerate(self.path):
            is_last = (i == len(self.path) - 1)
            has_route = item.get("route") is not None

            # Item del breadcrumb
            if is_last or not has_route:
                # Último item o sin ruta: no clickeable, estilo diferente
                text_color = ColorConstants.get_color_for_theme("ON_SURFACE", is_dark)
                controls.append(
                    ft.Text(
                        item["label"],
                        size=LayoutConstants.FONT_SIZE_MD,
                        weight=ft.FontWeight.W_600,
                        color=text_color,
                    )
                )
                logger.debug(f"Breadcrumb item (current): {item['label']} - color: {text_color}")
            else:
                # Items anteriores con ruta: clickeables
                link_color = ColorConstants.PRIMARY
                hover_bg = ColorConstants.get_color_for_theme("OVERLAY", is_dark)

                controls.append(
                    ft.TextButton(
                        text=item["label"],
                        on_click=lambda e, route=item["route"]: self._handle_navigate(route),
                        style=ft.ButtonStyle(
                            color={
                                ft.ControlState.DEFAULT: link_color,
                                ft.ControlState.HOVERED: link_color,
                            },
                            overlay_color={
                                ft.ControlState.HOVERED: hover_bg,
                            },
                            padding=ft.padding.symmetric(
                                horizontal=LayoutConstants.PADDING_SM,
                                vertical=LayoutConstants.PADDING_XS,
                            ),
                        ),
                    )
                )

            # Separador (si no es el último)
            if not is_last:
                separator_color = ColorConstants.get_color_for_theme("ON_SURFACE_VARIANT", is_dark)
                controls.append(
                    ft.Icon(
                        ft.Icons.CHEVRON_RIGHT,
                        size=16,
                        color=separator_color,
                    )
                )

        return controls

    def _handle_navigate(self, route: str):
        """
        Maneja la navegación a un nivel del breadcrumb.

        Args:
            route: Ruta a navegar
        """
        logger.debug(f"Breadcrumb navigation to: {route}")
        if self.on_navigate_callback:
            self.on_navigate_callback(route)

    def update_path(self, path: list[dict]) -> None:
        """
        Actualiza el path del breadcrumb.

        Args:
            path: Nueva lista de niveles

        Example:
            >>> breadcrumb.update_path([
            ...     {"label": "Inicio", "route": "/"},
            ...     {"label": "Productos", "route": None}
            ... ])
        """
        self.path = path
        self.controls = self._build_controls()
        if self.page:
            self.update()
        logger.debug(f"Breadcrumb actualizado: {len(path)} niveles")


# Exportar
__all__ = ["Breadcrumb"]
