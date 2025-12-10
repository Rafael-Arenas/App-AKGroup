"""
Componente para una fila de componente en el BOM (Bill of Materials).

Permite mostrar y editar un componente individual de una nomenclatura.
"""
import flet as ft
from typing import Callable, Optional
from loguru import logger

from src.frontend.layout_constants import LayoutConstants
from src.frontend.i18n.translation_manager import t


class BOMComponentRow(ft.Container):
    """
    Fila para un componente en el BOM.
    
    Muestra el artículo seleccionado, cantidad y permite eliminarlo.
    
    Args:
        component_data: Datos del componente (id, name, quantity)
        on_quantity_change: Callback cuando cambia la cantidad
        on_remove: Callback cuando se elimina el componente
        index: Índice de la fila
    """
    
    def __init__(
        self,
        component_data: dict,
        on_quantity_change: Callable[[int, float], None] | None = None,
        on_remove: Callable[[int], None] | None = None,
        index: int = 0,
    ):
        """Inicializa la fila de componente."""
        super().__init__()
        
        self.component_data = component_data
        self.on_quantity_change_callback = on_quantity_change
        self.on_remove_callback = on_remove
        self.index = index
        
        # Construir componentes
        self._build_components()
        
        # Configurar contenedor
        self.padding = LayoutConstants.PADDING_SM
        self.border = ft.border.all(1, ft.Colors.OUTLINE)
        self.border_radius = LayoutConstants.BORDER_RADIUS_SM
        self.bgcolor = ft.Colors.SURFACE_VARIANT
        
        logger.debug(f"BOMComponentRow created: index={index}, component={component_data.get('name')}")
    
    def _build_components(self) -> None:
        """Construye los componentes de la fila."""
        # Nombre del artículo
        self._name_text = ft.Text(
            value=self.component_data.get("name", ""),
            size=LayoutConstants.FONT_SIZE_MD,
            weight=ft.FontWeight.W_500,
            expand=True,
        )
        
        # Código del artículo
        self._code_text = ft.Text(
            value=self.component_data.get("code", ""),
            size=LayoutConstants.FONT_SIZE_SM,
            color=ft.Colors.ON_SURFACE_VARIANT,
        )
        
        # Campo de cantidad
        self._quantity_field = ft.TextField(
            value=str(self.component_data.get("quantity", 1.0)),
            label=t("articles.form.quantity"),
            width=120,
            text_align=ft.TextAlign.RIGHT,
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=self._on_quantity_changed,
            dense=True,
        )
        
        # Botón de eliminar
        self._remove_button = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE,
            icon_color=ft.Colors.ERROR,
            tooltip=t("common.remove"),
            on_click=self._on_remove_clicked,
        )
        
        # Layout de la fila
        self.content = ft.Row(
            controls=[
                # Información del artículo
                ft.Container(
                    content=ft.Column(
                        controls=[
                            self._name_text,
                            self._code_text,
                        ],
                        spacing=2,
                    ),
                    expand=True,
                ),
                # Cantidad
                self._quantity_field,
                # Botón eliminar
                self._remove_button,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=LayoutConstants.SPACING_MD,
        )
    
    def _on_quantity_changed(self, e: ft.ControlEvent) -> None:
        """Callback cuando cambia la cantidad."""
        try:
            quantity = float(e.control.value)
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
            
            # Actualizar datos
            self.component_data["quantity"] = quantity
            
            # Llamar callback
            if self.on_quantity_change_callback:
                self.on_quantity_change_callback(self.index, quantity)
                
            logger.debug(f"Quantity changed: index={self.index}, quantity={quantity}")
            
        except ValueError as ex:
            logger.warning(f"Invalid quantity value: {e.control.value}")
            # Restaurar valor anterior
            e.control.value = str(self.component_data.get("quantity", 1.0))
            if self.page:
                e.control.update()
    
    def _on_remove_clicked(self, e: ft.ControlEvent) -> None:
        """Callback cuando se hace click en eliminar."""
        logger.info(f"Remove component clicked: index={self.index}")
        
        if self.on_remove_callback:
            self.on_remove_callback(self.index)
    
    def get_component_data(self) -> dict:
        """Retorna los datos del componente."""
        return self.component_data
    
    def update_quantity(self, quantity: float) -> None:
        """Actualiza la cantidad del componente."""
        self.component_data["quantity"] = quantity
        self._quantity_field.value = str(quantity)
        
        if self.page:
            self._quantity_field.update()
