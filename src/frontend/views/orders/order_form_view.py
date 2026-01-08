import flet as ft
import asyncio
from typing import Optional, Callable, Dict, Any
from loguru import logger

from src.frontend.app_state import app_state
from src.frontend.layout_constants import LayoutConstants
from src.frontend.components.common import BaseCard, LoadingSpinner, ErrorDisplay
from src.frontend.components.forms import ValidatedTextField
from src.frontend.i18n.translation_manager import t

class OrderFormView(ft.Column):
    """
    Vista de formulario para crear/editar una orden.
    
    Args:
        company_id: ID de la empresa asociada
        quote_id: ID de la cotización de origen (opcional)
        order_id: ID de la orden a editar (opcional)
        on_save: Callback al guardar exitosamente
        on_cancel: Callback al cancelar
    """
    def __init__(
        self,
        company_id: int,
        quote_id: Optional[int] = None,
        order_id: Optional[int] = None,
        on_save: Optional[Callable] = None,
        on_cancel: Optional[Callable] = None,
    ):
        super().__init__()
        self.company_id = company_id
        self.quote_id = quote_id
        self.order_id = order_id
        self.on_save_callback = on_save
        self.on_cancel_callback = on_cancel

        self.is_editing = order_id is not None
        self._is_loading = True
        self._is_saving = False
        self._error_message = ""

        # Layout setup
        self.expand = True
        self.scroll = ft.ScrollMode.AUTO
        self.spacing = LayoutConstants.SPACING_MD

        # Form Fields
        self._init_form_fields()

        # Build initial layout
        self.controls = [self._build_loading()]

    def _init_form_fields(self):
        self.revision = ValidatedTextField(
            label=t("orders.fields.revision"),
            required=True,
            validators=["required"],
            prefix_icon=ft.Icons.HISTORY,
        )
        
        self.order_number = ValidatedTextField(
            label=t("orders.fields.order_number"),
            required=True,
            validators=["required"],
            prefix_icon=ft.Icons.NUMBERS,
            hint_text="Ej: ORD-2024-001",
        )

        self.customer_po = ValidatedTextField(
            label=t("orders.fields.customer_po"),
            prefix_icon=ft.Icons.RECEIPT,
            hint_text="OC del cliente",
        )

        self.project_number = ValidatedTextField(
            label=t("orders.fields.project_number"),
            prefix_icon=ft.Icons.ASSIGNMENT,
            hint_text="ID del proyecto",
        )

    def did_mount(self):
        if self.page:
            self.page.run_task(self._load_data)

    async def _load_data(self):
        self._is_loading = True
        self.controls = [self._build_loading()]
        if self.page: self.update()

        try:
            # Set default values
            self.revision.set_value("A")

            # Aquí se cargarían los datos si es edición o si viene de una cotización
            if self.quote_id:
                logger.info(f"Loading data from quote {self.quote_id} for new order")
                # TODO: Cargar datos de la cotización para pre-llenar campos
                pass
            
            if self.is_editing:
                logger.info(f"Loading order {self.order_id} for editing")
                # TODO: Cargar datos de la orden
                pass

            self._is_loading = False
            self.controls = self._build_content()
            if self.page: self.update()

        except Exception as e:
            logger.error(f"Error loading order form data: {e}")
            self._error_message = str(e)
            self.controls = [self._build_error()]
            if self.page: self.update()

    def _build_loading(self) -> ft.Control:
        return ft.Container(
            content=LoadingSpinner(message=t("common.loading")),
            alignment=ft.Alignment(0, 0),
            expand=True
        )

    def _build_error(self) -> ft.Control:
        return ft.Container(
            content=ErrorDisplay(
                message=self._error_message,
                on_retry=self._load_data
            ),
            alignment=ft.Alignment(0, 0),
            expand=True
        )

    def _build_content(self) -> list[ft.Control]:
        title_text = "Editar Orden" if self.is_editing else "Nueva Orden"
        if self.quote_id:
            title_text = f"Nueva Orden desde Cotización"

        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.SHOPPING_BAG, size=32),
                    ft.Text(
                        title_text,
                        size=LayoutConstants.FONT_SIZE_DISPLAY_MD,
                        weight=ft.FontWeight.BOLD,
                    ),
                ],
                spacing=LayoutConstants.SPACING_SM,
            ),
            padding=LayoutConstants.PADDING_MD,
        )

        save_btn = ft.Button(
            content=ft.Text(t("common.save")),
            icon=ft.Icons.SAVE,
            on_click=self._save,
            disabled=self._is_saving
        )
        
        cancel_btn = ft.Button(
            content=ft.Text(t("common.cancel")),
            on_click=self._cancel,
            disabled=self._is_saving
        )

        form_card = BaseCard(
            title="Datos de la Orden",
            icon=ft.Icons.DESCRIPTION,
            content=ft.Column([
                ft.ResponsiveRow([
                    ft.Column([self.order_number], col={"sm": 6}),
                    ft.Column([self.revision], col={"sm": 6}),
                ]),
                ft.ResponsiveRow([
                    ft.Column([self.customer_po], col={"sm": 6}),
                    ft.Column([self.project_number], col={"sm": 6}),
                ]),
            ])
        )

        return [
            header,
            ft.Divider(height=1, opacity=0.2),
            ft.Container(
                content=ft.Column([
                    form_card,
                    ft.Row([save_btn, cancel_btn], alignment=ft.MainAxisAlignment.END)
                ], spacing=LayoutConstants.SPACING_LG),
                padding=LayoutConstants.PADDING_LG,
                expand=True
            )
        ]

    async def _save(self, e):
        if not self._validate():
            return

        self._is_saving = True
        if self.page: self.update()

        try:
            # TODO: Implementar guardado real via API
            logger.info("Saving order...")
            await asyncio.sleep(1) # Simulación
            
            if self.page:
                self.page.overlay.append(ft.SnackBar(content=ft.Text("Orden guardada exitosamente"), bgcolor=ft.Colors.GREEN))
                self.page.overlay[-1].open = True
                self.page.update()

            if self.on_save_callback:
                self.on_save_callback()

        except Exception as ex:
            logger.error(f"Error saving order: {ex}")
            if self.page:
                self.page.overlay.append(ft.SnackBar(content=ft.Text(f"Error al guardar: {str(ex)}"), bgcolor=ft.Colors.ERROR))
                self.page.overlay[-1].open = True
                self.page.update()
        finally:
            self._is_saving = False
            if self.page: self.update()

    def _validate(self) -> bool:
        is_valid = True
        if not self.order_number.validate(): is_valid = False
        if not self.revision.validate(): is_valid = False
        return is_valid

    async def _cancel(self, e):
        if self.on_cancel_callback:
            self.on_cancel_callback()
