"""
Componente de panel de filtros.

Proporciona un panel colapsable con filtros configurables.
"""
from typing import Callable, Any, Literal
from dataclasses import dataclass
from datetime import datetime
import flet as ft
from loguru import logger

from src.frontend.color_constants import ColorConstants
from src.frontend.layout_constants import LayoutConstants
from src.frontend.i18n.translation_manager import t
from src.frontend.app_state import app_state


@dataclass
class FilterConfig:
    """
    Configuración de un filtro.

    Attributes:
        key: Clave del filtro
        label: Etiqueta del filtro (i18n key)
        filter_type: Tipo de filtro ("dropdown", "text", "checkbox", "date_range")
        options: Opciones para dropdown (lista de {"value": ..., "text": ...})
        default_value: Valor por defecto
    """
    key: str
    label: str
    filter_type: Literal["dropdown", "text", "checkbox", "date_range"]
    options: list[dict[str, str]] | None = None
    default_value: Any = None


class FilterPanel(ft.Container):
    """
    Panel de filtros colapsable con diferentes tipos de filtros.

    Args:
        filters: Lista de configuraciones de filtros
        on_apply: Callback cuando se aplican filtros (recibe dict con valores)
        on_clear: Callback cuando se limpian filtros
        initially_collapsed: Si True, inicia colapsado

    Example:
        >>> filters = [
        ...     FilterConfig("category", "Categoría", "dropdown", [
        ...         {"value": "1", "text": "Cat 1"}
        ...     ]),
        ...     FilterConfig("search", "Buscar", "text"),
        ... ]
        >>> def handle_apply(filter_values):
        ...     print(filter_values)
        >>> panel = FilterPanel(
        ...     filters=filters,
        ...     on_apply=handle_apply
        ... )
    """

    def __init__(
        self,
        filters: list[FilterConfig] | list[dict],
        on_apply: Callable[[dict[str, Any]], None] | None = None,
        on_clear: Callable[[], None] | None = None,
        on_filter_change: Callable[[dict[str, Any]], None] | None = None,
        initially_collapsed: bool = False,
    ):
        """Inicializa el panel de filtros."""
        super().__init__()

        # Convertir dicts a FilterConfig si es necesario
        self.filters = []
        for f in filters:
            if isinstance(f, dict):
                # Convertir options: {"label": ..., "value": ...} -> {"text": ..., "value": ...}
                options = f.get("options", [])
                converted_options = []
                for opt in options:
                    if isinstance(opt, dict):
                        converted_options.append({
                            "value": opt.get("value", ""),
                            "text": opt.get("label", opt.get("text", "")),
                        })
                    else:
                        converted_options.append(opt)

                # Convertir dict a FilterConfig
                self.filters.append(FilterConfig(
                    key=f.get("key", ""),
                    label=f.get("label", ""),
                    filter_type=f.get("type", "dropdown"),
                    options=converted_options if converted_options else None,
                    default_value=f.get("default", None),
                ))
            else:
                self.filters.append(f)

        # on_filter_change es un alias para on_apply
        self.on_apply = on_filter_change or on_apply
        self.on_clear = on_clear
        self.is_collapsed = initially_collapsed
        self._filter_controls: dict[str, ft.Control] = {}
        self._active_filters_count: int = 0
        logger.debug(f"FilterPanel initialized with {len(self.filters)} filters")

        # Suscribirse a cambios de tema
        app_state.theme.add_observer(self._on_theme_changed)

    def _on_theme_changed(self) -> None:
        """Callback cuando cambia el tema."""
        if self.page:
            self.update()

    def build(self) -> ft.Control:
        """
        Construye el componente de panel de filtros.

        Returns:
            Control de Flet con el panel de filtros
        """
        is_dark = app_state.theme.is_dark_mode

        # Header del panel
        badge = None
        if self._active_filters_count > 0:
            badge = ft.Container(
                content=ft.Text(
                    str(self._active_filters_count),
                    size=LayoutConstants.FONT_SIZE_XS,
                    color=ColorConstants.BADGE_TEXT,
                    weight=LayoutConstants.FONT_WEIGHT_BOLD,
                ),
                bgcolor=ColorConstants.BADGE_BACKGROUND,
                width=LayoutConstants.BADGE_SIZE,
                height=LayoutConstants.BADGE_SIZE,
                border_radius=LayoutConstants.RADIUS_FULL,
                alignment=ft.alignment.center,
            )

        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.FILTER_LIST,
                        color=ColorConstants.PRIMARY,
                        size=LayoutConstants.ICON_SIZE_MD,
                    ),
                    ft.Text(
                        t("common.filters"),
                        size=LayoutConstants.FONT_SIZE_LG,
                        weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                        expand=True,
                    ),
                    badge if badge else ft.Container(),
                    ft.IconButton(
                        icon=ft.Icons.EXPAND_MORE if not self.is_collapsed else ft.Icons.EXPAND_LESS,
                        on_click=self._toggle_collapse,
                        tooltip=t("common.collapse") if not self.is_collapsed else t("common.expand"),
                    ),
                ],
                spacing=LayoutConstants.SPACING_SM,
            ),
            padding=LayoutConstants.PADDING_MD,
            border=ft.border.only(
                bottom=ft.BorderSide(1, ColorConstants.get_color_for_theme("DIVIDER", is_dark))
            ),
        )

        # Contenido del panel (filtros)
        content = []
        if not self.is_collapsed:
            filter_controls = []

            for filter_config in self.filters:
                control = self._create_filter_control(filter_config)
                self._filter_controls[filter_config.key] = control
                filter_controls.append(
                    ft.Container(
                        content=control,
                        padding=ft.padding.only(bottom=LayoutConstants.PADDING_MD),
                    )
                )

            # Botones
            buttons = ft.Row(
                controls=[
                    ft.TextButton(
                        text=t("common.clear_filters"),
                        icon=ft.Icons.CLEAR,
                        on_click=self._handle_clear,
                    ),
                    ft.ElevatedButton(
                        text=t("common.apply_filters"),
                        icon=ft.Icons.CHECK,
                        bgcolor=ColorConstants.PRIMARY,
                        color=ft.Colors.WHITE,
                        on_click=self._handle_apply,
                    ),
                ],
                alignment=ft.MainAxisAlignment.END,
                spacing=LayoutConstants.SPACING_SM,
            )

            content.append(
                ft.Container(
                    content=ft.Column(
                        controls=filter_controls + [buttons],
                        spacing=LayoutConstants.SPACING_SM,
                    ),
                    padding=LayoutConstants.PADDING_MD,
                )
            )

        return ft.Container(
            content=ft.Column(
                controls=[header] + content,
                spacing=0,
            ),
            border=ft.border.all(1, ColorConstants.get_color_for_theme("DIVIDER", is_dark)),
            border_radius=LayoutConstants.RADIUS_SM,
            bgcolor=ColorConstants.get_color_for_theme("SURFACE", is_dark),
        )

    def _create_filter_control(self, config: FilterConfig) -> ft.Control:
        """
        Crea el control según el tipo de filtro.

        Args:
            config: Configuración del filtro

        Returns:
            Control de Flet
        """
        if config.filter_type == "dropdown":
            options = [
                ft.dropdown.Option(key=opt["value"], text=opt["text"])
                for opt in (config.options or [])
            ]
            return ft.Dropdown(
                label=t(config.label),
                options=options,
                value=config.default_value,
                border_color=ColorConstants.BORDER_LIGHT,
            )

        elif config.filter_type == "text":
            return ft.TextField(
                label=t(config.label),
                value=config.default_value or "",
                border_color=ColorConstants.BORDER_LIGHT,
            )

        elif config.filter_type == "checkbox":
            return ft.Checkbox(
                label=t(config.label),
                value=config.default_value or False,
            )

        elif config.filter_type == "date_range":
            return ft.Column(
                controls=[
                    ft.Text(t(config.label), weight=LayoutConstants.FONT_WEIGHT_MEDIUM),
                    ft.Row(
                        controls=[
                            ft.TextField(
                                label=t("common.from"),
                                hint_text="YYYY-MM-DD",
                                width=150,
                                border_color=ColorConstants.BORDER_LIGHT,
                            ),
                            ft.TextField(
                                label=t("common.to"),
                                hint_text="YYYY-MM-DD",
                                width=150,
                                border_color=ColorConstants.BORDER_LIGHT,
                            ),
                        ],
                        spacing=LayoutConstants.SPACING_SM,
                    ),
                ],
                spacing=LayoutConstants.SPACING_XS,
            )

        # Default: TextField
        return ft.TextField(
            label=t(config.label),
            border_color=ColorConstants.BORDER_LIGHT,
        )

    def _toggle_collapse(self, e: ft.ControlEvent) -> None:
        """
        Alterna el estado colapsado/expandido.

        Args:
            e: Evento de Flet
        """
        self.is_collapsed = not self.is_collapsed
        logger.debug(f"Filter panel collapsed: {self.is_collapsed}")
        if self.page:
            self.update()

    def _handle_apply(self, e: ft.ControlEvent) -> None:
        """
        Maneja el click en aplicar filtros.

        Args:
            e: Evento de Flet
        """
        filter_values = self.get_filter_values()
        logger.info(f"Applying filters: {filter_values}")

        # Contar filtros activos (no vacíos)
        self._active_filters_count = sum(
            1 for v in filter_values.values() if v is not None and v != "" and v != False
        )

        if self.on_apply:
            try:
                self.on_apply(filter_values)
            except Exception as ex:
                logger.error(f"Error in apply callback: {ex}")

        if self.page:
            self.update()

    def _handle_clear(self, e: ft.ControlEvent) -> None:
        """
        Maneja el click en limpiar filtros.

        Args:
            e: Evento de Flet
        """
        logger.info("Clearing filters")
        self.clear_filters()
        self._active_filters_count = 0

        if self.on_clear:
            try:
                self.on_clear()
            except Exception as ex:
                logger.error(f"Error in clear callback: {ex}")

        if self.page:
            self.update()

    def get_filter_values(self) -> dict[str, Any]:
        """
        Obtiene los valores actuales de todos los filtros.

        Returns:
            Diccionario con los valores de los filtros

        Example:
            >>> values = panel.get_filter_values()
        """
        values = {}

        for config in self.filters:
            control = self._filter_controls.get(config.key)

            if config.filter_type == "dropdown":
                if isinstance(control, ft.Dropdown):
                    values[config.key] = control.value

            elif config.filter_type == "text":
                if isinstance(control, ft.TextField):
                    values[config.key] = control.value or ""

            elif config.filter_type == "checkbox":
                if isinstance(control, ft.Checkbox):
                    values[config.key] = control.value or False

            elif config.filter_type == "date_range":
                if isinstance(control, ft.Column):
                    row = control.controls[1]
                    if isinstance(row, ft.Row) and len(row.controls) == 2:
                        from_field = row.controls[0]
                        to_field = row.controls[1]
                        values[config.key] = {
                            "from": from_field.value if isinstance(from_field, ft.TextField) else None,
                            "to": to_field.value if isinstance(to_field, ft.TextField) else None,
                        }

        return values

    def set_filter_value(self, key: str, value: Any) -> None:
        """
        Establece el valor de un filtro específico.

        Args:
            key: Clave del filtro
            value: Valor a establecer

        Example:
            >>> panel.set_filter_value("category", "1")
            >>> panel.update()
        """
        control = self._filter_controls.get(key)

        if isinstance(control, (ft.Dropdown, ft.TextField)):
            control.value = value
        elif isinstance(control, ft.Checkbox):
            control.value = bool(value)

        if self.page:
            self.update()

    def clear_filters(self) -> None:
        """
        Limpia todos los filtros.

        Example:
            >>> panel.clear_filters()
        """
        for config in self.filters:
            control = self._filter_controls.get(config.key)

            if isinstance(control, ft.Dropdown):
                control.value = None
            elif isinstance(control, ft.TextField):
                control.value = ""
            elif isinstance(control, ft.Checkbox):
                control.value = False
            elif isinstance(control, ft.Column):
                # Date range
                row = control.controls[1]
                if isinstance(row, ft.Row) and len(row.controls) == 2:
                    for field in row.controls:
                        if isinstance(field, ft.TextField):
                            field.value = ""

        if self.page:
            self.update()

    def expand(self) -> None:
        """
        Expande el panel.

        Example:
            >>> panel.expand()
        """
        if self.is_collapsed:
            self.is_collapsed = False
            if self.page:
                self.update()

    def collapse(self) -> None:
        """
        Colapsa el panel.

        Example:
            >>> panel.collapse()
        """
        if not self.is_collapsed:
            self.is_collapsed = True
            if self.page:
                self.update()

    def get_active_filters_count(self) -> int:
        """
        Obtiene el número de filtros activos.

        Returns:
            Cantidad de filtros activos

        Example:
            >>> count = panel.get_active_filters_count()
        """
        return self._active_filters_count

    def update_filter_options(self, key: str, options: list[dict[str, str]]) -> None:
        """
        Actualiza las opciones de un filtro dropdown.

        Args:
            key: Clave del filtro
            options: Nueva lista de opciones [{"value": ..., "label": ...}, ...]

        Example:
            >>> panel.update_filter_options("country", [{"value": "1", "label": "USA"}])
            >>> panel.update()
        """
        # Encontrar la configuración del filtro
        filter_config = None
        for config in self.filters:
            if config.key == key:
                filter_config = config
                break

        if not filter_config:
            logger.warning(f"Filter key '{key}' not found")
            return

        # Convertir options si es necesario
        converted_options = []
        for opt in options:
            if isinstance(opt, dict):
                converted_options.append({
                    "value": opt.get("value", ""),
                    "text": opt.get("label", opt.get("text", "")),
                })
            else:
                converted_options.append(opt)

        # Actualizar la configuración
        filter_config.options = converted_options

        # Actualizar el control si ya existe
        control = self._filter_controls.get(key)
        if control and isinstance(control, ft.Dropdown):
            control.options = [
                ft.dropdown.Option(key=opt["value"], text=opt["text"])
                for opt in converted_options
            ]
            if self.page:
                self.update()

        logger.debug(f"Updated filter options for '{key}': {len(converted_options)} options")

    def will_unmount(self) -> None:
        """Limpieza cuando el componente se desmonta."""
        app_state.theme.remove_observer(self._on_theme_changed)
