"""
Componente de diálogo de confirmación.

Proporciona un AlertDialog reutilizable con variantes de estilo.
"""
from typing import Callable, Literal
import flet as ft
from loguru import logger

from src.frontend.color_constants import ColorConstants
from src.frontend.layout_constants import LayoutConstants
from src.frontend.i18n.translation_manager import t


class ConfirmDialog:
    """
    Diálogo de confirmación con diferentes variantes.

    Args:
        title: Título del diálogo
        message: Mensaje de confirmación
        on_confirm: Callback cuando se confirma
        on_cancel: Callback cuando se cancela (opcional)
        variant: Estilo del diálogo ("default", "warning", "danger")
        confirm_text: Texto del botón confirmar (opcional)
        cancel_text: Texto del botón cancelar (opcional)

    Example:
        >>> def handle_confirm():
        ...     print("Confirmed!")
        >>> dialog = ConfirmDialog(
        ...     title="Eliminar elemento",
        ...     message="¿Estás seguro de eliminar este elemento?",
        ...     on_confirm=handle_confirm,
        ...     variant="danger"
        ... )
        >>> dialog.show(page)
    """

    def __init__(
        self,
        title: str,
        message: str,
        on_confirm: Callable[[], None],
        on_cancel: Callable[[], None] | None = None,
        variant: Literal["default", "warning", "danger"] = "default",
        confirm_text: str | None = None,
        cancel_text: str | None = None,
    ):
        """Inicializa el diálogo de confirmación."""
        self.title = title
        self.message = message
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        self.variant = variant
        self.confirm_text = confirm_text or t("common.confirm")
        self.cancel_text = cancel_text or t("common.cancel")
        self._dialog: ft.AlertDialog | None = None
        logger.debug(f"ConfirmDialog initialized with variant={variant}")

    def _get_variant_color(self) -> str:
        """
        Obtiene el color según la variante.

        Returns:
            Color hexadecimal según la variante
        """
        color_map = {
            "default": ColorConstants.PRIMARY,
            "warning": ColorConstants.WARNING,
            "danger": ColorConstants.ERROR,
        }
        return color_map.get(self.variant, ColorConstants.PRIMARY)

    def _get_variant_icon(self) -> str:
        """
        Obtiene el ícono según la variante.

        Returns:
            Nombre del ícono según la variante
        """
        icon_map = {
            "default": ft.Icons.HELP_OUTLINE,
            "warning": ft.Icons.WARNING_AMBER,
            "danger": ft.Icons.DELETE_FOREVER,
        }
        return icon_map.get(self.variant, ft.Icons.HELP_OUTLINE)

    def _handle_confirm(self, e: ft.ControlEvent) -> None:
        """
        Maneja el click en confirmar.

        Args:
            e: Evento de Flet
        """
        logger.info(f"Confirm dialog accepted (variant={self.variant})")
        self._close_dialog(e)
        if self.on_confirm:
            try:
                self.on_confirm()
            except Exception as ex:
                logger.error(f"Error in confirm callback: {ex}")

    def _handle_cancel(self, e: ft.ControlEvent) -> None:
        """
        Maneja el click en cancelar.

        Args:
            e: Evento de Flet
        """
        logger.info("Confirm dialog cancelled")
        self._close_dialog(e)
        if self.on_cancel:
            try:
                self.on_cancel()
            except Exception as ex:
                logger.error(f"Error in cancel callback: {ex}")

    def _close_dialog(self, e: ft.ControlEvent) -> None:
        """
        Cierra el diálogo.

        Args:
            e: Evento de Flet
        """
        if self._dialog and e.page:
            self._dialog.open = False
            e.page.update()

    def show(self, page: ft.Page) -> None:
        """
        Muestra el diálogo en la página.

        Args:
            page: Página de Flet donde mostrar el diálogo

        Example:
            >>> dialog.show(page)
        """
        variant_color = self._get_variant_color()
        variant_icon = self._get_variant_icon()

        self._dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row(
                controls=[
                    ft.Icon(
                        name=variant_icon,
                        color=variant_color,
                        size=LayoutConstants.ICON_SIZE_LG,
                    ),
                    ft.Text(
                        self.title,
                        size=LayoutConstants.FONT_SIZE_XL,
                        weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                    ),
                ],
                spacing=LayoutConstants.SPACING_MD,
            ),
            content=ft.Text(
                self.message,
                size=LayoutConstants.FONT_SIZE_MD,
            ),
            actions=[
                ft.TextButton(
                    text=self.cancel_text,
                    on_click=self._handle_cancel,
                ),
                ft.ElevatedButton(
                    text=self.confirm_text,
                    bgcolor=variant_color,
                    color=ft.colors.WHITE,
                    on_click=self._handle_confirm,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        page.dialog = self._dialog
        self._dialog.open = True
        page.update()
        logger.debug("Confirm dialog shown")

    def close(self, page: ft.Page) -> None:
        """
        Cierra el diálogo manualmente.

        Args:
            page: Página de Flet

        Example:
            >>> dialog.close(page)
        """
        if self._dialog:
            self._dialog.open = False
            page.update()
            logger.debug("Confirm dialog closed manually")
