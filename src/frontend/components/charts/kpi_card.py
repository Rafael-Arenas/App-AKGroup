"""
Componente de tarjeta KPI.

Muestra métricas clave con valores, cambios y tendencias.
"""
from typing import Literal
import flet as ft
from loguru import logger

from src.frontend.layout_constants import LayoutConstants
from src.frontend.app_state import app_state


class KPICard(ft.Container):
    """
    Tarjeta de KPI con valor principal, cambio y tendencia.

    Args:
        icon: Ícono del KPI
        label: Etiqueta del KPI
        value: Valor principal a mostrar
        change_value: Valor del cambio (opcional)
        change_percentage: Porcentaje de cambio (opcional)
        trend: Tendencia ("up", "down", "neutral")
        format_as_currency: Si True, formatea como moneda
        currency_symbol: Símbolo de moneda (default: "$")
        elevation: Elevación de la tarjeta

    Example:
        >>> kpi = KPICard(
        ...     icon=ft.Icons.ATTACH_MONEY,
        ...     label="Ventas Totales",
        ...     value=125000,
        ...     change_percentage=15.5,
        ...     trend="up",
        ...     format_as_currency=True
        ... )
        >>> page.add(kpi)
    """

    def __init__(
        self,
        icon: str,
        label: str,
        value: float | int,
        change_value: float | int | None = None,
        change_percentage: float | None = None,
        trend: Literal["up", "down", "neutral"] = "neutral",
        format_as_currency: bool = False,
        currency_symbol: str = "$",
        elevation: int = LayoutConstants.ELEVATION_LOW,
    ):
        """Inicializa la tarjeta KPI."""
        super().__init__()
        self.icon = icon
        self.label = label
        self.value = value
        self.change_value = change_value
        self.change_percentage = change_percentage
        self.trend = trend
        self.format_as_currency = format_as_currency
        self.currency_symbol = currency_symbol
        self.elevation = elevation
        logger.debug(f"KPICard initialized: label={label}, value={value}, trend={trend}")

        # Suscribirse a cambios de tema
        app_state.theme.add_observer(self._on_theme_changed)
        
        # Construir contenido
        self.content = self.build()

    def _on_theme_changed(self) -> None:
        """Callback cuando cambia el tema."""
        if self.page:
            self.update()

    def _format_value(self, val: float | int) -> str:
        """
        Formatea el valor según la configuración.

        Args:
            val: Valor a formatear

        Returns:
            Valor formateado como string
        """
        if self.format_as_currency:
            # Formatear como moneda con separadores de miles
            formatted = f"{val:,.2f}" if isinstance(val, float) else f"{val:,}"
            return f"{self.currency_symbol}{formatted}"
        else:
            return f"{val:,.2f}" if isinstance(val, float) else f"{val:,}"

    def _get_trend_color(self) -> str | None:
        """
        Obtiene el color según la tendencia.

        Returns:
            Color hexadecimal o None para usar el color por defecto
        """
        # Dejamos que Flet maneje los colores con su tema Material 3
        return None

    def _get_trend_icon(self) -> str:
        """
        Obtiene el ícono según la tendencia.

        Returns:
            Nombre del ícono
        """
        if self.trend == "up":
            return ft.Icons.TRENDING_UP
        elif self.trend == "down":
            return ft.Icons.TRENDING_DOWN
        else:
            return ft.Icons.TRENDING_FLAT

    def build(self) -> ft.Control:
        """
        Construye el componente de tarjeta KPI.

        Returns:
            Control de Flet con la tarjeta KPI
        """
        trend_color = self._get_trend_color()
        trend_icon = self._get_trend_icon()

        # Header con ícono y label
        header = ft.Row(
            controls=[
                ft.Icon(
                    name=self.icon,
                    size=LayoutConstants.ICON_SIZE_LG,
                ),
                ft.Text(
                    self.label,
                    size=LayoutConstants.FONT_SIZE_MD,
                    weight=LayoutConstants.FONT_WEIGHT_MEDIUM,
                    expand=True,
                ),
            ],
            spacing=LayoutConstants.SPACING_SM,
        )

        # Valor principal
        value_text = ft.Text(
            self._format_value(self.value),
            size=LayoutConstants.FONT_SIZE_DISPLAY_SM,
            weight=LayoutConstants.FONT_WEIGHT_BOLD,
        )

        # Cambio y tendencia
        change_controls = []
        if self.change_percentage is not None:
            sign = "+" if self.change_percentage >= 0 else ""
            change_controls.append(
                ft.Row(
                    controls=[
                        ft.Icon(
                            name=trend_icon,
                            size=LayoutConstants.ICON_SIZE_SM,
                        ),
                        ft.Text(
                            f"{sign}{self.change_percentage:.1f}%",
                            size=LayoutConstants.FONT_SIZE_MD,
                            weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                        ),
                    ],
                    spacing=LayoutConstants.SPACING_XS,
                )
            )

        if self.change_value is not None:
            sign = "+" if self.change_value >= 0 else ""
            change_text = f"{sign}{self._format_value(abs(self.change_value))}"
            change_controls.append(
                ft.Text(
                    change_text,
                    size=LayoutConstants.FONT_SIZE_SM,
                )
            )

        content_controls = [header, value_text]
        if change_controls:
            content_controls.append(
                ft.Row(
                    controls=change_controls,
                    spacing=LayoutConstants.SPACING_SM,
                    wrap=True,
                )
            )

        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=content_controls,
                    spacing=LayoutConstants.SPACING_SM,
                ),
                padding=LayoutConstants.PADDING_LG,
            ),
            elevation=self.elevation,
        )

    def update_value(
        self,
        value: float | int,
        change_value: float | int | None = None,
        change_percentage: float | None = None,
        trend: Literal["up", "down", "neutral"] | None = None,
    ) -> None:
        """
        Actualiza el valor del KPI.

        Args:
            value: Nuevo valor principal
            change_value: Nuevo valor de cambio (opcional)
            change_percentage: Nuevo porcentaje de cambio (opcional)
            trend: Nueva tendencia (opcional)

        Example:
            >>> kpi.update_value(150000, change_percentage=20.5, trend="up")
            >>> kpi.update()
        """
        self.value = value
        if change_value is not None:
            self.change_value = change_value
        if change_percentage is not None:
            self.change_percentage = change_percentage
        if trend is not None:
            self.trend = trend

        logger.debug(f"KPI value updated: {self.label}={value}")
        if self.page:
            self.update()

    def set_trend(self, trend: Literal["up", "down", "neutral"]) -> None:
        """
        Establece la tendencia del KPI.

        Args:
            trend: Nueva tendencia

        Example:
            >>> kpi.set_trend("up")
            >>> kpi.update()
        """
        self.trend = trend
        if self.page:
            self.update()

    def set_label(self, label: str) -> None:
        """
        Actualiza la etiqueta del KPI.

        Args:
            label: Nueva etiqueta

        Example:
            >>> kpi.set_label("Ventas del Mes")
            >>> kpi.update()
        """
        self.label = label
        if self.page:
            self.update()

    def set_icon(self, icon: str) -> None:
        """
        Actualiza el ícono del KPI.

        Args:
            icon: Nuevo ícono

        Example:
            >>> kpi.set_icon(ft.Icons.TRENDING_UP)
            >>> kpi.update()
        """
        self.icon = icon
        if self.page:
            self.update()

    def will_unmount(self) -> None:
        """Limpieza cuando el componente se desmonta."""
        app_state.theme.remove_observer(self._on_theme_changed)
