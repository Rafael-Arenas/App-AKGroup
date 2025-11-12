"""
Componente de tabla de componentes BOM (Bill of Materials).

Muestra la lista de componentes de una nomenclatura con cantidades y costos.
"""
from typing import Callable
import flet as ft
from loguru import logger

from src.frontend.app_state import app_state
from src.frontend.layout_constants import LayoutConstants


class BOMTable(ft.Container):
    """
    Tabla de componentes de BOM (Bill of Materials).

    Args:
        components: Lista de componentes del BOM
        on_remove: Callback cuando se remueve un componente
        editable: Si True, permite eliminar componentes

    Example:
        >>> bom_table = BOMTable(
        ...     components=[
        ...         {
        ...             "component_code": "COMP001",
        ...             "component_name": "Componente 1",
        ...             "quantity": 2,
        ...             "unit_cost": 10.5
        ...         }
        ...     ],
        ...     on_remove=handle_remove,
        ...     editable=True,
        ... )
        >>> page.add(bom_table)
    """

    def __init__(
        self,
        components: list[dict],
        on_remove: Callable[[dict], None] | None = None,
        editable: bool = False,
    ):
        """Inicializa la tabla de BOM."""
        super().__init__()
        self.components = components
        self.on_remove = on_remove
        self.editable = editable

        logger.debug(f"BOMTable initialized with {len(components)} components")

    def build(self) -> ft.Control:
        """Construye el componente de tabla BOM."""
        if not self.components:
            return ft.Container(
                content=ft.Text(
                    "No hay componentes en la lista de materiales",
                    size=LayoutConstants.FONT_SIZE_MD,
                ),
                padding=LayoutConstants.PADDING_LG,
                alignment=ft.alignment.center,
            )

        # Crear columnas de la tabla
        columns = [
            ft.DataColumn(
                ft.Text(
                    "Código",
                    weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                )
            ),
            ft.DataColumn(
                ft.Text(
                    "Nombre",
                    weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                )
            ),
            ft.DataColumn(
                ft.Text(
                    "Cantidad",
                    weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                ),
                numeric=True,
            ),
            ft.DataColumn(
                ft.Text(
                    "Costo Unitario",
                    weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                ),
                numeric=True,
            ),
            ft.DataColumn(
                ft.Text(
                    "Costo Total",
                    weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                ),
                numeric=True,
            ),
        ]

        # Agregar columna de acciones si es editable
        if self.editable:
            columns.append(
                ft.DataColumn(
                    ft.Text(
                        "Acciones",
                        weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                    )
                )
            )

        # Crear filas de la tabla
        rows = []
        total_cost = 0.0

        for component in self.components:
            component_code = component.get("component_code", "")
            component_name = component.get("component_name", "")
            quantity = component.get("quantity", 0)
            unit_cost = component.get("unit_cost", 0)
            line_total = quantity * unit_cost
            total_cost += line_total

            cells = [
                ft.DataCell(ft.Text(component_code)),
                ft.DataCell(ft.Text(component_name)),
                ft.DataCell(ft.Text(str(quantity))),
                ft.DataCell(ft.Text(f"${unit_cost:.2f}")),
                ft.DataCell(
                    ft.Text(
                        f"${line_total:.2f}",
                        weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                    )
                ),
            ]

            # Agregar botón de eliminar si es editable
            if self.editable:
                remove_button = ft.IconButton(
                    icon=ft.Icons.DELETE,
                    tooltip="Eliminar componente",
                    on_click=lambda e, comp=component: self._on_remove_click(comp),
                )
                cells.append(ft.DataCell(remove_button))

            rows.append(ft.DataRow(cells=cells))

        # Tabla
        table = ft.DataTable(
            columns=columns,
            rows=rows,
            border_radius=LayoutConstants.RADIUS_SM,
        )

        # Fila de total
        total_row = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text(
                        "TOTAL:",
                        size=LayoutConstants.FONT_SIZE_LG,
                        weight=LayoutConstants.FONT_WEIGHT_BOLD,
                    ),
                    ft.Text(
                        f"${total_cost:.2f}",
                        size=LayoutConstants.FONT_SIZE_LG,
                        weight=LayoutConstants.FONT_WEIGHT_BOLD,
                    ),
                ],
                alignment=ft.MainAxisAlignment.END,
                spacing=LayoutConstants.SPACING_MD,
            ),
            padding=LayoutConstants.PADDING_MD,
            border_radius=LayoutConstants.RADIUS_SM,
        )

        # Contenedor completo
        return ft.Column(
            controls=[
                ft.Container(
                    content=table,
                    border_radius=LayoutConstants.RADIUS_SM,
                ),
                total_row,
            ],
            spacing=LayoutConstants.SPACING_MD,
        )

    def _on_remove_click(self, component: dict) -> None:
        """
        Callback cuando se hace click en eliminar un componente.

        Args:
            component: Componente a eliminar
        """
        logger.info(f"Remove component clicked: {component.get('component_code')}")

        if self.on_remove:
            self.on_remove(component)

    def set_components(self, components: list[dict]) -> None:
        """
        Actualiza la lista de componentes.

        Args:
            components: Nueva lista de componentes

        Example:
            >>> bom_table.set_components(new_components)
            >>> bom_table.update()
        """
        self.components = components
        logger.debug(f"BOM components updated: {len(components)} components")

        if self.page:
            self.update()

    def add_component(self, component: dict) -> None:
        """
        Agrega un componente a la lista.

        Args:
            component: Componente a agregar

        Example:
            >>> bom_table.add_component({
            ...     "component_code": "NEW001",
            ...     "component_name": "Nuevo Componente",
            ...     "quantity": 1,
            ...     "unit_cost": 5.0
            ... })
        """
        self.components.append(component)
        logger.debug(f"Component added: {component.get('component_code')}")

        if self.page:
            self.update()

    def remove_component(self, component_code: str) -> None:
        """
        Elimina un componente de la lista por código.

        Args:
            component_code: Código del componente a eliminar

        Example:
            >>> bom_table.remove_component("COMP001")
        """
        self.components = [
            c for c in self.components if c.get("component_code") != component_code
        ]
        logger.debug(f"Component removed: {component_code}")

        if self.page:
            self.update()

    def get_total_cost(self) -> float:
        """
        Calcula el costo total del BOM.

        Returns:
            Costo total de todos los componentes

        Example:
            >>> total = bom_table.get_total_cost()
            >>> print(f"Total: ${total:.2f}")
        """
        total = 0.0
        for component in self.components:
            quantity = component.get("quantity", 0)
            unit_cost = component.get("unit_cost", 0)
            total += quantity * unit_cost

        return total

    def get_components(self) -> list[dict]:
        """
        Obtiene la lista actual de componentes.

        Returns:
            Lista de componentes

        Example:
            >>> components = bom_table.get_components()
        """
        return self.components.copy()
