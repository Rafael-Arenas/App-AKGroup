import flet as ft
import asyncio
from datetime import date
from typing import Optional, Callable, Dict, Any
from loguru import logger

from src.frontend.app_state import app_state
from src.frontend.layout_constants import LayoutConstants
from src.frontend.components.common import BaseCard, LoadingSpinner, ErrorDisplay
from src.frontend.components.forms import ValidatedTextField
from src.frontend.i18n.translation_manager import t
from src.frontend.utils.fake_data_generator import FakeDataGenerator
from src.frontend.services.api import order_api, quote_api

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
        self._quote: Optional[Dict[str, Any]] = None
        self._is_loading = True
        self._is_saving = False
        self._error_message = ""

        # Layout setup
        self.expand = True
        self.scroll = ft.ScrollMode.AUTO
        self.spacing = LayoutConstants.SPACING_MD

        # Form Fields
        self._init_form_fields()

        # Fake data button (only for creation mode)
        self._fake_data_button = ft.IconButton(
            icon=ft.Icons.CASINO,
            tooltip=t("orders.form.generate_fake_data"),
            on_click=self._on_generate_fake_data,
            visible=not self.is_editing,
            disabled=True,
        )

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
            read_only=not self.is_editing, # Only editable in edit mode if needed, but usually auto-assigned
        )

        self.customer_po_number = ValidatedTextField(
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
            
            if not self.is_editing:
                self.order_number.set_value("[ ASIGNACIÓN AUTOMÁTICA ]")

            # Load Quote data if provided
            if self.quote_id:
                logger.info(f"Loading data from quote {self.quote_id} for new order")
                self._quote = await quote_api.get_by_id(self.quote_id)
                # Pre-fill project number if it exists in quote notes or something?
                # For now just having the _quote data is enough for the save method
            
            if self.is_editing:
                logger.info(f"Loading order {self.order_id} for editing")
                order_data = await order_api.get_by_id(self.order_id)
                self.order_number.set_value(order_data.get("order_number", ""))
                self.revision.set_value(order_data.get("revision", ""))
                self.customer_po_number.set_value(order_data.get("customer_po_number", ""))
                self.project_number.set_value(order_data.get("project_number", ""))

            self._is_loading = False
            self.controls = self._build_content()
            if self._fake_data_button and not self.is_editing:
                self._fake_data_button.disabled = False
            if self.page: self.update()

        except Exception as e:
            logger.error(f"Error loading order form data: {e}")
            self._error_message = str(e)
            self.controls = [self._build_error()]
            if self._fake_data_button:
                self._fake_data_button.disabled = True
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
                    ft.VerticalDivider(width=1, opacity=0.2),
                    self._fake_data_button,
                ],
                spacing=LayoutConstants.SPACING_SM,
            ),
            padding=LayoutConstants.PADDING_MD,
        )

        # Action Buttons
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
                    ft.Column([self.customer_po_number], col={"sm": 6}),
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
            # Prepare data
            on_value = self.order_number.get_value()
            if on_value == "[ ASIGNACIÓN AUTOMÁTICA ]":
                on_value = "STRING"
                
            # Default values from quote if available, else standard defaults
            staff_id = self._quote.get("staff_id", 1) if self._quote else 1
            currency_id = self._quote.get("currency_id", 1) if self._quote else 1
            
            data = {
                "order_number": on_value,
                "revision": self.revision.get_value(),
                "customer_po_number": self.customer_po_number.get_value(),
                "project_number": self.project_number.get_value(),
                "company_id": self.company_id,
                "quote_id": self.quote_id,
                "staff_id": staff_id,
                "currency_id": currency_id,
                "order_date": date.today().isoformat(),
                "status_id": 1, # Default status (e.g. Draft/Pending)
                "payment_status_id": 1, # Default payment status (e.g. Pending)
            }

            # Use current user ID from state (mocked as 1 if not available)
            user_id = 1 

            if self.is_editing:
                result = await order_api.update(self.order_id, data, user_id=user_id)
                success_msg = "Orden actualizada exitosamente"
            else:
                result = await order_api.create(data, user_id=user_id)
                assigned_number = result.get("order_number", "")
                success_msg = f"Orden {assigned_number} creada exitosamente"
            
            if self.page:
                self.page.overlay.append(ft.SnackBar(content=ft.Text(success_msg), bgcolor=ft.Colors.GREEN))
                self.page.overlay[-1].open = True
                self.page.update()

            if self.on_save_callback:
                self.on_save_callback()

        except Exception as ex:
            logger.error(f"Error saving order: {ex}")
            if self.page:
                error_msg = f"Error al guardar: {str(ex)}"
                self.page.overlay.append(ft.SnackBar(content=ft.Text(error_msg), bgcolor=ft.Colors.ERROR))
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

    def _on_generate_fake_data(self, e: ft.ControlEvent) -> None:
        """Llena el formulario con datos ficticios para agilizar pruebas."""
        if self._is_loading or self.is_editing:
            return

        try:
            FakeDataGenerator.populate_order_form(self)
            self._fake_data_button.disabled = True
            if self.page:
                snackbar = ft.SnackBar(
                    content=ft.Text(t("orders.form.fake_data_success")),
                    bgcolor=ft.Colors.GREEN,
                    duration=2000,
                )
                self.page.overlay.append(snackbar)
                snackbar.open = True
                self.page.update()
        except Exception as ex:
            logger.exception(f"Error generating fake order data: {ex}")
            if self.page:
                snackbar = ft.SnackBar(
                    content=ft.Text(t("orders.form.fake_data_error", {"error": str(ex)})),
                    bgcolor=ft.Colors.RED,
                    duration=3000,
                )
                self.page.overlay.append(snackbar)
                snackbar.open = True
                self.page.update()
