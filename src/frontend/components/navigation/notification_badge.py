"""
NotificationBadge - Badge de notificaciones con contador.

Muestra un icono de campana con un badge numérico que indica
el número de notificaciones no leídas.
"""

import flet as ft
from loguru import logger

from src.frontend.layout_constants import LayoutConstants


class NotificationBadge(ft.Stack):
    """
    Badge de notificaciones con contador y estados visuales.

    Características:
    - Contador numérico de notificaciones
    - Estado urgente (color rojo + animación)
    - Estado normal (color azul)
    - Click handler para abrir panel de notificaciones
    """

    def __init__(
        self,
        count: int = 0,
        has_urgent: bool = False,
        on_click: callable = None,
    ):
        """
        Inicializa el NotificationBadge.

        Args:
            count: Número de notificaciones (0 para ocultar badge)
            has_urgent: Si hay notificaciones urgentes
            on_click: Callback al hacer click

        Example:
            >>> badge = NotificationBadge(count=5, has_urgent=False)
        """
        super().__init__()

        self.count = count
        self.has_urgent = has_urgent
        self.on_click_callback = on_click

        # El Stack contiene el botón y el badge posicionado
        self.controls = self._build_controls()

    def _build_controls(self) -> list[ft.Control]:
        """
        Construye los controles del Stack.

        Returns:
            Lista de controles para el Stack
        """
        controls = []

        # Botón base (icono de campana)
        self.icon_button = ft.IconButton(
            icon=ft.Icons.NOTIFICATIONS_OUTLINED,
            selected_icon=ft.Icons.NOTIFICATIONS,
            selected=self.count > 0,
            tooltip="Notificaciones",
            on_click=self._handle_click,
        )

        controls.append(self.icon_button)

        # Badge (solo si count > 0)
        if self.count > 0:
            badge = ft.Container(
                content=ft.Text(
                    str(min(self.count, 99)) if self.count < 100 else "99+",
                    size=LayoutConstants.FONT_SIZE_XS,
                    weight=ft.FontWeight.BOLD,
                ),
                border_radius=LayoutConstants.BADGE_SIZE // 2,
                width=LayoutConstants.BADGE_SIZE,
                height=LayoutConstants.BADGE_SIZE,
                alignment=ft.alignment.center,
                right=0,
                top=0,
            )

            controls.append(badge)

        return controls

    def _handle_click(self, e):
        """
        Maneja el click en el botón.

        Args:
            e: Evento de Flet
        """
        logger.debug(f"NotificationBadge clicked (count: {self.count})")
        if self.on_click_callback:
            self.on_click_callback(e)

    def update_count(self, count: int, has_urgent: bool = False) -> None:
        """
        Actualiza el contador de notificaciones.

        Args:
            count: Nuevo número de notificaciones
            has_urgent: Si hay notificaciones urgentes

        Example:
            >>> badge.update_count(10, has_urgent=True)
        """
        if self.count != count or self.has_urgent != has_urgent:
            self.count = count
            self.has_urgent = has_urgent
            self.controls = self._build_controls()
            if self.page:
                self.update()
            logger.debug(
                f"NotificationBadge actualizado: {count} "
                f"({'urgentes' if has_urgent else 'normales'})"
            )


# Exportar
__all__ = ["NotificationBadge"]
