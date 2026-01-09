"""
Componente de tabla de datos avanzada.

Proporciona una DataTable con ordenamiento, paginación y acciones.
"""
from typing import Callable, Any
from dataclasses import dataclass
import flet as ft
from loguru import logger

from src.frontend.layout_constants import LayoutConstants
from src.frontend.i18n.translation_manager import t
from src.frontend.app_state import app_state
from src.frontend.components.common.empty_state import EmptyState


@dataclass
class ColumnConfig:
    """
    Configuración de columna para DataTable.

    Attributes:
        key: Clave del dato en el diccionario de fila
        label: Etiqueta de la columna (i18n key)
        sortable: Si la columna es ordenable
        width: Ancho de la columna (None = auto)
        formatter: Función para formatear el valor (opcional)
    """
    key: str
    label: str
    sortable: bool = False
    width: int | None = None
    formatter: Callable[[Any], str] | None = None


class DataTable(ft.Container):
    """
    Tabla de datos avanzada con ordenamiento, paginación y acciones.

    Args:
        columns: Lista de configuraciones de columnas
        data: Lista de diccionarios con los datos
        on_edit: Callback para editar (recibe el dato completo)
        on_delete: Callback para eliminar (recibe el dato completo)
        selectable: Si permite selección de filas
        on_selection_changed: Callback cuando cambia la selección
        page_size: Tamaño de página para paginación (0 = sin paginación)
        empty_message: Mensaje cuando no hay datos

    Example:
        >>> columns = [
        ...     ColumnConfig("id", "ID", sortable=True),
        ...     ColumnConfig("name", "Nombre", sortable=True),
        ... ]
        >>> data = [{"id": 1, "name": "Item 1"}]
        >>> table = DataTable(
        ...     columns=columns,
        ...     data=data,
        ...     on_edit=handle_edit,
        ...     on_delete=handle_delete
        ... )
    """

    def __init__(
        self,
        columns: list[ColumnConfig] | list[dict],
        data: list[dict[str, Any]] | None = None,
        on_edit: Callable[[dict[str, Any]], None] | None = None,
        on_delete: Callable[[dict[str, Any]], None] | None = None,
        on_row_click: Callable[[dict[str, Any]], None] | None = None,
        on_page_change: Callable[[int], None] | None = None,
        selectable: bool = False,
        on_selection_changed: Callable[[list[dict[str, Any]]], None] | None = None,
        page_size: int = 10,
        empty_message: str | None = None,
    ):
        """Inicializa la tabla de datos."""
        super().__init__()

        # Convertir dicts a ColumnConfig si es necesario
        self.columns = []
        for col in columns:
            if isinstance(col, dict):
                self.columns.append(ColumnConfig(
                    key=col.get("key", ""),
                    label=col.get("label", ""),
                    sortable=col.get("sortable", False),
                    width=col.get("width"),
                    formatter=col.get("formatter"),
                ))
            else:
                self.columns.append(col)

        self.data = data or []
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_row_click = on_row_click
        self.on_page_change = on_page_change
        self.selectable = selectable
        self.on_selection_changed = on_selection_changed
        self.page_size = page_size
        self.empty_message = empty_message or t("common.no_data")

        self._sort_column: str | None = None
        self._sort_ascending: bool = True
        self._current_page: int = 0
        self._total_items: int = 0
        self._selected_rows: set[int] = set()

        logger.debug(f"DataTable initialized: {len(self.columns)} columns, {len(self.data)} rows")

        # Configurar propiedades del Container
        self.expand = True

        # Suscribirse a cambios de tema
        app_state.theme.add_observer(self._on_theme_changed)

        # Establecer contenido inicial
        self.content = self.build()

    def _on_theme_changed(self) -> None:
        """Callback cuando cambia el tema."""
        if self.page:
            self.update()

    def build(self) -> ft.Control:
        """
        Construye el componente de tabla.

        Returns:
            Control de Flet con la tabla
        """
        if not self.data:
            return EmptyState(
                icon=ft.Icons.TABLE_CHART,
                title=t("common.no_data"),
                message=self.empty_message,
            )

        # Construir tabla completa
        table_content = ft.Column(
            controls=[
                self._build_table_header(),
                *self._build_table_rows(),
            ],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
        )

        # Construir paginación si es necesaria
        pagination = None
        if self.page_size > 0 and len(self.data) > self.page_size:
            total_pages = (len(self._get_sorted_data()) + self.page_size - 1) // self.page_size
            pagination = ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.CHEVRON_LEFT,
                        disabled=self._current_page == 0,
                        on_click=self._previous_page,
                    ),
                    ft.Text(
                        f"{t('common.page')} {self._current_page + 1} {t('common.of')} {total_pages}",
                        size=LayoutConstants.FONT_SIZE_MD,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.CHEVRON_RIGHT,
                        disabled=self._current_page >= total_pages - 1,
                        on_click=self._next_page,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=LayoutConstants.SPACING_MD,
            )

        # Envolver tabla en contenedor con borde
        table_container = ft.Container(
            content=table_content,
            border=ft.border.all(1),
            border_radius=LayoutConstants.RADIUS_SM,
            expand=True,
        )

        controls = [table_container]

        if pagination:
            controls.append(pagination)

        return ft.Column(
            controls=controls,
            spacing=LayoutConstants.SPACING_MD,
            expand=True,
        )

    def _build_table_header(self) -> ft.Container:
        """Construye la fila de encabezados."""
        header_cells = []

        # Checkbox para seleccionar todo (si es seleccionable)
        if self.selectable:
            select_all_checkbox = ft.Checkbox(
                value=False,
                on_change=self._on_select_all,
            )
            header_cells.append(
                ft.Container(
                    content=select_all_checkbox,
                    width=50,
                    padding=LayoutConstants.PADDING_SM,
                )
            )

        # Celdas de encabezado para cada columna
        for col in self.columns:
            header_content = [
                ft.Text(
                    t(col.label),
                    weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                    size=LayoutConstants.FONT_SIZE_MD,
                )
            ]

            # Indicador de ordenamiento si la columna es sortable
            if col.sortable:
                sort_icon = ft.Icon(
                    ft.Icons.UNFOLD_MORE,
                    size=LayoutConstants.ICON_SIZE_SM,
                )

                # Actualizar icono si esta columna está ordenada
                if self._sort_column == col.key:
                    sort_icon.name = (
                        ft.Icons.ARROW_UPWARD
                        if self._sort_ascending
                        else ft.Icons.ARROW_DOWNWARD
                    )

                header_content.append(sort_icon)

            header_row = ft.Row(
                header_content,
                spacing=LayoutConstants.SPACING_XS,
            )

            container = ft.Container(
                content=header_row,
                padding=LayoutConstants.PADDING_SM,
                width=col.width,
                expand=col.width is None,
                on_click=lambda _, c=col: self._handle_sort(c.key) if c.sortable else None,
            )

            # Cursor pointer si es sortable
            if col.sortable:
                container.cursor = ft.MouseCursor.CLICK

            header_cells.append(container)

        # Columna de acciones (si existe on_edit o on_delete)
        if self.on_edit or self.on_delete:
            header_cells.append(
                ft.Container(
                    content=ft.Text(
                        t("common.actions"),
                        weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                        size=LayoutConstants.FONT_SIZE_MD,
                    ),
                    padding=LayoutConstants.PADDING_SM,
                    width=120,
                    alignment=ft.Alignment(0, 0),  # center
                )
            )

        return ft.Container(
            content=ft.Row(
                header_cells,
                spacing=0,
            ),
        )

    def _build_table_rows(self) -> list[ft.Container]:
        """Construye las filas de datos de la tabla."""
        rows = []

        # Obtener datos ordenados y paginados
        sorted_data = self._get_sorted_data()
        paginated_data = self._get_paginated_data(sorted_data)

        for idx, row_data in enumerate(paginated_data):
            global_idx = self._current_page * self.page_size + idx
            row = self._build_data_row(row_data, global_idx, idx)
            rows.append(row)

        return rows

    def _build_data_row(
        self, row_data: dict[str, Any], global_idx: int, local_idx: int
    ) -> ft.Container:
        """
        Construye una fila de datos.

        Args:
            row_data: Datos de la fila
            global_idx: Índice global de la fila
            local_idx: Índice local en la página actual

        Returns:
            Container con la fila
        """
        cells = []

        # Checkbox de selección
        if self.selectable:
            checkbox = ft.Checkbox(
                value=global_idx in self._selected_rows,
                on_change=lambda e: self._on_row_select(global_idx, e.control.value),
            )
            cells.append(
                ft.Container(
                    content=checkbox,
                    width=50,
                    padding=LayoutConstants.PADDING_SM,
                )
            )

        # Celdas de datos
        for col in self.columns:
            value = row_data.get(col.key, "")

            # Formatear valor si hay formatter
            if col.formatter:
                display_value = col.formatter(value)
            else:
                display_value = str(value) if value is not None else ""

            cell = ft.Container(
                content=ft.Text(
                    display_value,
                    size=LayoutConstants.FONT_SIZE_MD,
                ),
                padding=LayoutConstants.PADDING_SM,
                width=col.width,
                expand=col.width is None,
                alignment=ft.Alignment(-1, 0),  # left
            )
            cells.append(cell)

        # Celda de acciones (si existe on_edit o on_delete)
        if self.on_edit or self.on_delete:
            actions = []
            if self.on_edit:
                actions.append(
                    ft.IconButton(
                        icon=ft.Icons.EDIT,
                        icon_size=LayoutConstants.ICON_SIZE_SM,
                        tooltip=t("common.edit"),
                        on_click=lambda e, data=row_data: self._handle_edit(data),
                    )
                )
            if self.on_delete:
                actions.append(
                    ft.IconButton(
                        icon=ft.Icons.DELETE,
                        icon_size=LayoutConstants.ICON_SIZE_SM,
                        tooltip=t("common.delete"),
                        on_click=lambda e, data=row_data: self._handle_delete(data),
                    )
                )

            actions_cell = ft.Container(
                content=ft.Row(
                    actions,
                    spacing=LayoutConstants.SPACING_XS,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                padding=LayoutConstants.PADDING_SM,
                width=120,
                alignment=ft.Alignment(0, 0),  # center
            )
            cells.append(actions_cell)

        # Container de la fila
        row_container = ft.Row(
            cells,
            spacing=0,
        )

        # Wrapper con hover y click
        wrapper = ft.Container(
            content=row_container,
            on_click=lambda _, data=row_data: self._handle_row_click(data)
            if self.on_row_click
            else None,
        )

        # Efectos hover y cursor
        if self.on_row_click:
            wrapper.cursor = ft.MouseCursor.CLICK
            wrapper.ink = True

        return wrapper

    def _get_sorted_data(self) -> list[dict[str, Any]]:
        """
        Obtiene los datos ordenados.

        Returns:
            Lista de datos ordenados
        """
        if not self._sort_column:
            return self.data

        return sorted(
            self.data,
            key=lambda x: x.get(self._sort_column, ""),
            reverse=not self._sort_ascending,
        )

    def _get_paginated_data(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Obtiene los datos de la página actual.

        Args:
            data: Datos completos (ordenados)

        Returns:
            Datos de la página actual
        """
        if self.page_size <= 0:
            return data

        start = self._current_page * self.page_size
        end = start + self.page_size
        return data[start:end]

    def _handle_sort(self, column_key: str) -> None:
        """
        Maneja el ordenamiento por columna.

        Args:
            column_key: Clave de la columna a ordenar
        """
        if self._sort_column == column_key:
            self._sort_ascending = not self._sort_ascending
        else:
            self._sort_column = column_key
            self._sort_ascending = True

        logger.debug(f"Sorting by {column_key}, ascending={self._sort_ascending}")
        if self.page:
            # Reconstruir contenido al ordenar
            self.content = self.build()
            self.update()

    def _handle_edit(self, row_data: dict[str, Any]) -> None:
        """
        Maneja el click en editar.

        Args:
            row_data: Datos de la fila
        """
        logger.info(f"Edit clicked for row: {row_data}")
        if self.on_edit:
            try:
                self.on_edit(row_data)
            except Exception as ex:
                logger.error(f"Error in edit callback: {ex}")

    def _handle_delete(self, row_data: dict[str, Any]) -> None:
        """
        Maneja el click en eliminar.

        Args:
            row_data: Datos de la fila
        """
        logger.info(f"Delete clicked for row: {row_data}")
        if self.on_delete:
            try:
                self.on_delete(row_data)
            except Exception as ex:
                logger.error(f"Error in delete callback: {ex}")

    def _handle_row_click(self, row_data: dict[str, Any]) -> None:
        """
        Maneja el click en una fila.

        Args:
            row_data: Datos de la fila
        """
        logger.info(f"Row clicked: {row_data}")
        if self.on_row_click:
            try:
                self.on_row_click(row_data)
            except Exception as ex:
                logger.error(f"Error in row click callback: {ex}")

    def _handle_select(self, row_index: int, selected: bool) -> None:
        """
        Maneja la selección de filas.

        Args:
            row_index: Índice de la fila
            selected: Estado de selección
        """
        if selected:
            self._selected_rows.add(row_index)
        else:
            self._selected_rows.discard(row_index)

        logger.debug(f"Selected rows: {len(self._selected_rows)}")

        if self.on_selection_changed:
            selected_data = [
                self.data[i] for i in self._selected_rows if i < len(self.data)
            ]
            try:
                self.on_selection_changed(selected_data)
            except Exception as ex:
                logger.error(f"Error in selection changed callback: {ex}")

    def _on_select_all(self, e: ft.ControlEvent) -> None:
        """Handler para seleccionar/deseleccionar todo."""
        if e.control.value:
            # Seleccionar todos los registros visibles en la página actual
            sorted_data = self._get_sorted_data()
            paginated_data = self._get_paginated_data(sorted_data)

            for idx in range(len(paginated_data)):
                global_idx = self._current_page * self.page_size + idx
                self._selected_rows.add(global_idx)
        else:
            # Deseleccionar todos
            self._selected_rows.clear()

        # Reconstruir tabla
        self.content = self.build()
        if self.page:
            self.update()

        # Llamar callback si existe
        if self.on_selection_changed:
            selected_data = [
                self.data[idx] for idx in self._selected_rows if idx < len(self.data)
            ]
            try:
                self.on_selection_changed(selected_data)
            except Exception as ex:
                logger.error(f"Error in selection changed callback: {ex}")

    def _on_row_select(self, row_idx: int, selected: bool) -> None:
        """
        Handler para selección de fila individual.

        Args:
            row_idx: Índice de la fila
            selected: Si está seleccionada
        """
        if selected:
            self._selected_rows.add(row_idx)
        else:
            self._selected_rows.discard(row_idx)

        # Reconstruir tabla para actualizar checkboxes
        self.content = self.build()
        if self.page:
            self.update()

        # Llamar callback si existe
        if self.on_selection_changed:
            selected_data = [
                self.data[idx] for idx in self._selected_rows if idx < len(self.data)
            ]
            try:
                self.on_selection_changed(selected_data)
            except Exception as ex:
                logger.error(f"Error in selection changed callback: {ex}")

    def _previous_page(self, e: ft.ControlEvent) -> None:
        """Navega a la página anterior."""
        if self._current_page > 0:
            self._current_page -= 1
            logger.debug(f"Navigate to page {self._current_page}")
            if self.on_page_change:
                try:
                    self.on_page_change(self._current_page + 1)  # 1-indexed for user
                except Exception as ex:
                    logger.error(f"Error in page change callback: {ex}")
            if self.page:
                # Reconstruir contenido al cambiar de página
                self.content = self.build()
                self.update()

    def _next_page(self, e: ft.ControlEvent) -> None:
        """Navega a la página siguiente."""
        total_pages = (len(self.data) + self.page_size - 1) // self.page_size
        if self._current_page < total_pages - 1:
            self._current_page += 1
            logger.debug(f"Navigate to page {self._current_page}")
            if self.on_page_change:
                try:
                    self.on_page_change(self._current_page + 1)  # 1-indexed for user
                except Exception as ex:
                    logger.error(f"Error in page change callback: {ex}")
            if self.page:
                # Reconstruir contenido al cambiar de página
                self.content = self.build()
                self.update()

    def update_data(self, data: list[dict[str, Any]]) -> None:
        """
        Actualiza los datos de la tabla.

        Args:
            data: Nuevos datos

        Example:
            >>> table.update_data(new_data)
            >>> table.update()
        """
        self.data = data
        self._current_page = 0
        self._selected_rows.clear()
        logger.info(f"Table data updated: {len(data)} rows")
        if self.page:
            self.update()

    def set_data(
        self,
        data: list[dict[str, Any]],
        total: int | None = None,
        current_page: int | None = None,
    ) -> None:
        """
        Establece los datos de la tabla con información de paginación.

        Args:
            data: Datos a mostrar
            total: Total de items (para paginación externa)
            current_page: Página actual (1-indexed)

        Example:
            >>> table.set_data(items, total=100, current_page=2)
            >>> table.update()
        """
        self.data = data
        if total is not None:
            self._total_items = total
        if current_page is not None:
            self._current_page = current_page - 1  # Convert to 0-indexed
        
        logger.info(f"Table data set: {len(data)} rows, total={total}, page={current_page}")

        # Siempre reconstruir el contenido cuando cambian los datos
        self.content = self.build()

        # Solo actualizar si está montado en una página
        try:
            if self.page:
                self.update()
        except Exception:
            pass

    def get_selected_data(self) -> list[dict[str, Any]]:
        """
        Obtiene los datos de las filas seleccionadas.

        Returns:
            Lista de datos seleccionados

        Example:
            >>> selected = table.get_selected_data()
        """
        return [self.data[i] for i in self._selected_rows if i < len(self.data)]

    def clear_selection(self) -> None:
        """
        Limpia la selección.

        Example:
            >>> table.clear_selection()
        """
        self._selected_rows.clear()
        if self.page:
            self.update()

    def will_unmount(self) -> None:
        """Limpieza cuando el componente se desmonta."""
        app_state.theme.remove_observer(self._on_theme_changed)
