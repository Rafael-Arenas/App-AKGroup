"""
Componente de tarjeta base colapsable.

Proporciona una tarjeta reutilizable con header, contenido y acciones.
"""
from typing import Callable
import flet as ft
from loguru import logger

from src.frontend.color_constants import ColorConstants
from src.frontend.layout_constants import LayoutConstants
from src.frontend.app_state import app_state


class BaseCard(ft.Container):
    """
    Tarjeta base colapsable con header, contenido y acciones.

    Args:
        title: Título de la tarjeta
        icon: Ícono del header (opcional)
        content: Control de Flet con el contenido
        actions: Lista de controles para el footer (botones, etc.)
        collapsible: Si True, permite colapsar/expandir
        initially_collapsed: Estado inicial (True = colapsado)
        elevation: Elevación de la tarjeta

    Example:
        >>> card = BaseCard(
        ...     title="Mi Tarjeta",
        ...     icon=ft.Icons.INFO,
        ...     content=ft.Text("Contenido de la tarjeta"),
        ...     collapsible=True,
        ...     actions=[ft.ElevatedButton("Guardar")]
        ... )
        >>> page.add(card)
    """

    def __init__(
        self,
        title: str,
        icon: str | None = None,
        content: ft.Control | None = None,
        actions: list[ft.Control] | None = None,
        collapsible: bool = False,
        initially_collapsed: bool = False,
        elevation: int = LayoutConstants.ELEVATION_LOW,
    ):
        """Inicializa la tarjeta base."""
        super().__init__()
        self.title = title
        self.icon = icon
        self.content_control = content
        self.actions = actions or []
        self.collapsible = collapsible
        self.is_collapsed = initially_collapsed
        self.elevation = elevation
        logger.debug(f"BaseCard initialized: title={title}, collapsible={collapsible}")

        # Suscribirse a cambios de tema
        app_state.theme.add_observer(self._on_theme_changed)

    def _on_theme_changed(self) -> None:
        """Callback cuando cambia el tema."""
        if self.page:
            self.update()

    def build(self) -> ft.Control:
        """
        Construye el componente de tarjeta.

        Returns:
            Control de Flet con la tarjeta
        """
        is_dark = app_state.theme.is_dark_mode

        # Header de la tarjeta
        header_controls = []

        if self.icon:
            header_controls.append(
                ft.Icon(
                    name=self.icon,
                    color=ColorConstants.PRIMARY,
                    size=LayoutConstants.ICON_SIZE_MD,
                )
            )

        header_controls.append(
            ft.Text(
                self.title,
                size=LayoutConstants.FONT_SIZE_LG,
                weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                color=ColorConstants.get_color_for_theme("ON_SURFACE", is_dark),
                expand=True,
            )
        )

        if self.collapsible:
            header_controls.append(
                ft.IconButton(
                    icon=ft.Icons.EXPAND_MORE if not self.is_collapsed else ft.Icons.EXPAND_LESS,
                    icon_size=LayoutConstants.ICON_SIZE_MD,
                    on_click=self._toggle_collapse,
                    tooltip="Colapsar" if not self.is_collapsed else "Expandir",
                )
            )

        header = ft.Container(
            content=ft.Row(
                controls=header_controls,
                spacing=LayoutConstants.SPACING_SM,
                alignment=ft.MainAxisAlignment.START,
            ),
            padding=LayoutConstants.PADDING_MD,
            border=ft.border.only(
                bottom=ft.BorderSide(
                    1,
                    ColorConstants.get_color_for_theme("DIVIDER", is_dark),
                )
            ),
        )

        # Contenido de la tarjeta
        card_content = []
        card_content.append(header)

        if not self.is_collapsed and self.content_control:
            card_content.append(
                ft.Container(
                    content=self.content_control,
                    padding=LayoutConstants.PADDING_MD,
                )
            )

        # Footer con acciones
        if not self.is_collapsed and self.actions:
            card_content.append(
                ft.Container(
                    content=ft.Row(
                        controls=self.actions,
                        spacing=LayoutConstants.SPACING_SM,
                        alignment=ft.MainAxisAlignment.END,
                    ),
                    padding=LayoutConstants.PADDING_MD,
                    border=ft.border.only(
                        top=ft.BorderSide(
                            1,
                            ColorConstants.get_color_for_theme("DIVIDER", is_dark),
                        )
                    ),
                )
            )

        return ft.Card(
            content=ft.Column(
                controls=card_content,
                spacing=0,
            ),
            elevation=self.elevation,
            color=ColorConstants.get_color_for_theme("CARD_BACKGROUND", is_dark),
        )

    def _toggle_collapse(self, e: ft.ControlEvent) -> None:
        """
        Alterna el estado colapsado/expandido.

        Args:
            e: Evento de Flet
        """
        self.is_collapsed = not self.is_collapsed
        logger.debug(f"Card collapsed state: {self.is_collapsed}")
        if self.page:
            self.update()

    def set_content(self, content: ft.Control) -> None:
        """
        Establece nuevo contenido para la tarjeta.

        Args:
            content: Nuevo control de contenido

        Example:
            >>> card.set_content(ft.Text("Nuevo contenido"))
            >>> card.update()
        """
        self.content_control = content
        if self.page:
            self.update()

    def set_actions(self, actions: list[ft.Control]) -> None:
        """
        Establece nuevas acciones para el footer.

        Args:
            actions: Lista de controles para el footer

        Example:
            >>> card.set_actions([ft.ElevatedButton("Guardar")])
            >>> card.update()
        """
        self.actions = actions
        if self.page:
            self.update()

    def expand(self) -> None:
        """
        Expande la tarjeta si está colapsada.

        Example:
            >>> card.expand()
        """
        if self.is_collapsed:
            self.is_collapsed = False
            if self.page:
                self.update()

    def collapse(self) -> None:
        """
        Colapsa la tarjeta si está expandida.

        Example:
            >>> card.collapse()
        """
        if not self.is_collapsed:
            self.is_collapsed = True
            if self.page:
                self.update()

    def will_unmount(self) -> None:
        """Limpieza cuando el componente se desmonta."""
        app_state.theme.remove_observer(self._on_theme_changed)
