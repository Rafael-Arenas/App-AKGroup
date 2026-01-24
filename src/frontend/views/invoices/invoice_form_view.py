"""
Vista de formulario para crear facturas.

Permite crear facturas SII o Export asociadas a una orden.
"""
import flet as ft
from datetime import date
from typing import Optional, Callable
from loguru import logger

from src.shared.providers import TimeProvider

# Time provider para acceso centralizado al tiempo
time_provider = TimeProvider()

from src.frontend.app_state import app_state
from src.frontend.layout_constants import LayoutConstants
from src.frontend.components.common import LoadingSpinner, ErrorDisplay, BaseCard
from src.frontend.components.forms import ValidatedTextField
from src.frontend.i18n.translation_manager import t
from src.frontend.utils.fake_data_generator import FakeDataGenerator


class InvoiceFormView(ft.Container):
    """
    Vista de formulario para crear una factura (SII o Export).
    
    Args:
        order_id: ID de la orden asociada
        order_number: Número de la orden (para mostrar)
        invoice_id: ID de la factura (None para crear nueva)
        on_save: Callback cuando se guarda
        on_cancel: Callback cuando se cancela
    """
    
    def __init__(
        self,
        order_id: int,
        order_number: str,
        invoice_id: Optional[int] = None,
        on_save: Optional[Callable] = None,
        on_cancel: Optional[Callable] = None,
    ):
        super().__init__()
        self.order_id = order_id
        self.order_number = order_number
        self.invoice_id = invoice_id
        self.on_save = on_save
        self.on_cancel = on_cancel
        
        # Estado
        self._is_loading = True
        self._error_message = ""
        self._is_saving = False
        self._order_data = None
        
        # Configurar propiedades del contenedor
        self.padding = LayoutConstants.PADDING_LG
        
        # Fake data button
        self._fake_data_button = ft.IconButton(
            icon=ft.Icons.CASINO,
            tooltip=t("orders.form.generate_fake_data"),
            on_click=self._on_generate_fake_data,
            visible=not self.invoice_id,
            disabled=True,
        )
        
        # Campos del formulario
        self._init_form_fields()
        
        # Construir contenido inicial
        self.content = self._build_loading()
        
        logger.info(f"InvoiceFormView initialized: order_id={order_id}, invoice_id={invoice_id}")
        
    def _init_form_fields(self):
        """Inicializa los campos del formulario."""
        # Tipo de factura
        self.invoice_type_class = ft.Dropdown(
            label=t("invoices.fields.invoice_type_class"),
            options=[
                ft.dropdown.Option("SII", "SII (Nacional)"),
                ft.dropdown.Option("EXPORT", "Exportación"),
            ],
            value="SII",
        )

        
        # Campos comunes
        self.invoice_number = ValidatedTextField(
            label=t("invoices.fields.invoice_number"),
            hint_text="Ej: F-2026-001",
            required=True,
        )
        
        self.revision = ValidatedTextField(
            label=t("invoices.fields.revision"),
            hint_text="A",
            required=True,
        )
        # Set default value after creation
        self.revision.set_value("A")
        
        self.invoice_date = ft.TextField(
            label=t("invoices.fields.invoice_date"),
            value=str(time_provider.today()),
            hint_text="YYYY-MM-DD",
        )
        
        self.due_date = ft.TextField(
            label=t("invoices.fields.due_date"),
            hint_text="YYYY-MM-DD (opcional)",
        )
        
        self.payment_terms = ft.TextField(
            label=t("invoices.fields.payment_terms"),
            hint_text="Ej: 30 días",
            multiline=True,
            max_lines=2,
        )
        
        self.notes = ft.TextField(
            label=t("invoices.sections.notes"),
            hint_text="Notas adicionales...",
            multiline=True,
            max_lines=4,
        )
        
        # Campos SII específicos
        self.invoice_type_sii = ft.Dropdown(
            label="Tipo de Documento SII",
            options=[
                ft.dropdown.Option("33", "33 - Factura Electrónica"),
                ft.dropdown.Option("34", "34 - Factura Exenta"),
                ft.dropdown.Option("56", "56 - Nota de Débito"),
                ft.dropdown.Option("61", "61 - Nota de Crédito"),
            ],
            value="33",
        )
        
        # Campos Export específicos
        self.invoice_type_export = ft.Dropdown(
            label="Tipo de Documento Export",
            options=[
                ft.dropdown.Option("110", "110 - Factura de Exportación"),
                ft.dropdown.Option("111", "111 - Nota de Débito Export"),
                ft.dropdown.Option("112", "112 - Nota de Crédito Export"),
            ],
            value="110",
        )
        
        self.shipping_date = ft.TextField(
            label=t("invoices.fields.shipping_date"),
            hint_text="YYYY-MM-DD (opcional)",
        )
        
        self.port_of_loading = ft.TextField(
            label="Puerto de Carga",
            hint_text="Ej: Valparaíso",
        )
        
        self.port_of_discharge = ft.TextField(
            label="Puerto de Descarga",
            hint_text="Ej: Los Angeles",
        )
        
    def did_mount(self):
        """Lifecycle: Se ejecuta cuando el componente se monta."""
        if self.page:
            self.page.run_task(self._load_data)
    
    async def _load_data(self):
        """Carga los datos de la orden."""
        logger.info(f"Loading order data: order_id={self.order_id}")
        self._is_loading = True
        self._error_message = ""
        
        self.content = self._build_loading()
        if self.page:
            self.update()
        
        try:
            from src.frontend.services.api import order_api
            
            # Obtener datos de la orden
            self._order_data = await order_api.get_by_id(self.order_id)
            
            logger.success(f"Order data loaded: {self._order_data.get('order_number')}")
            self._is_loading = False
            self._fake_data_button.disabled = False
            
        except Exception as e:
            logger.exception(f"Error loading order: {e}")
            self._error_message = str(e)
            self._is_loading = False
            self._fake_data_button.disabled = True
        
        self.content = self._build_error() if self._error_message else self._build_content()
        if self.page:
            self.update()
    
    def _build_loading(self) -> ft.Control:
        """Construye vista de carga."""
        return ft.Container(
            content=LoadingSpinner(message=t("common.loading")),
            expand=True,
            alignment=ft.Alignment(0, 0),
        )
    
    def _build_error(self) -> ft.Control:
        """Construye vista de error."""
        return ft.Container(
            content=ErrorDisplay(
                message=self._error_message,
                on_retry=lambda: self.page.run_task(self._load_data) if self.page else None,
            ),
            expand=True,
            alignment=ft.Alignment(0, 0),
        )
    
    def _build_content(self) -> ft.Control:
        """Construye el contenido del formulario."""
        # Asignar event handler al dropdown
        self.invoice_type_class.on_change = self._on_invoice_type_change
        
        # Header
        header = ft.Row(
            controls=[
                ft.Icon(ft.Icons.RECEIPT_LONG, size=LayoutConstants.ICON_SIZE_XL),
                ft.Column(
                    controls=[
                        ft.Text(
                            "Crear Factura" if not self.invoice_id else "Editar Factura",
                            size=LayoutConstants.FONT_SIZE_DISPLAY_MD,
                            weight=LayoutConstants.FONT_WEIGHT_BOLD,
                        ),
                        ft.Text(
                            f"Orden: {self.order_number}",
                            size=LayoutConstants.FONT_SIZE_MD,
                            color=ft.Colors.GREY_700,
                        ),
                    ],
                    spacing=LayoutConstants.SPACING_XS,
                ),
                ft.VerticalDivider(width=1, opacity=0.2),
                self._fake_data_button,
            ],
            spacing=LayoutConstants.SPACING_MD,
        )
        
        # Información de la orden
        order_info = BaseCard(
            title="Información de la Orden",
            icon=ft.Icons.INFO_OUTLINED,
            content=ft.Column(
                controls=[
                    self._create_info_row("Número de Orden", self._order_data.get("order_number", "-")),
                    self._create_info_row("Cliente", self._order_data.get("company_name", "-")),
                    self._create_info_row("Total Orden", f"${float(self._order_data.get('total', 0)):,.2f}"),
                    self._create_info_row("Fecha Orden", str(self._order_data.get("order_date", "-"))),
                ],
                spacing=LayoutConstants.SPACING_SM,
            ),
        )
        
        # Campos comunes
        common_fields = BaseCard(
            title="Información General",
            icon=ft.Icons.EDIT_OUTLINED,
            content=ft.Column(
                controls=[
                    self.invoice_type_class,
                    self.invoice_number,
                    self.revision,
                    ft.Row(
                        controls=[
                            self.invoice_date,
                            self.due_date,
                        ],
                        spacing=LayoutConstants.SPACING_MD,
                    ),
                    self.payment_terms,
                    self.notes,
                ],
                spacing=LayoutConstants.SPACING_MD,
            ),
        )
        
        # Campos específicos (se mostrarán según el tipo)
        self.specific_fields_container = ft.Container(
            content=self._build_sii_fields(),  # Por defecto SII
        )
        
        # Botones de acción
        actions = ft.Row(
            controls=[
                ft.ElevatedButton(
                    content=ft.Text(t("common.cancel")),
                    on_click=self._cancel,
                    icon=ft.Icons.CANCEL_OUTLINED,
                ),
                ft.ElevatedButton(
                    content=ft.Text(t("common.save")),
                    on_click=self._save,
                    icon=ft.Icons.SAVE,
                    disabled=self._is_saving,
                ),
            ],
            alignment=ft.MainAxisAlignment.END,
            spacing=LayoutConstants.SPACING_MD,
        )
        
        # Layout principal
        return ft.Column(
            controls=[
                header,
                ft.Divider(height=LayoutConstants.SPACING_MD),
                order_info,
                common_fields,
                self.specific_fields_container,
                ft.Divider(height=LayoutConstants.SPACING_MD),
                actions,
            ],
            spacing=LayoutConstants.SPACING_LG,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
    
    def _build_sii_fields(self) -> ft.Control:
        """Construye campos específicos para factura SII."""
        return BaseCard(
            title="Campos SII",
            icon=ft.Icons.DESCRIPTION_OUTLINED,
            content=ft.Column(
                controls=[
                    self.invoice_type_sii,
                    ft.Text(
                        "La factura se creará con los valores de la orden (subtotal, impuestos, total)",
                        size=LayoutConstants.FONT_SIZE_SM,
                        color=ft.Colors.GREY_600,
                        italic=True,
                    ),
                ],
                spacing=LayoutConstants.SPACING_MD,
            ),
        )
    
    def _build_export_fields(self) -> ft.Control:
        """Construye campos específicos para factura Export."""
        return BaseCard(
            title="Campos de Exportación",
            icon=ft.Icons.PUBLIC_OUTLINED,
            content=ft.Column(
                controls=[
                    self.invoice_type_export,
                    self.shipping_date,
                    ft.Row(
                        controls=[
                            self.port_of_loading,
                            self.port_of_discharge,
                        ],
                        spacing=LayoutConstants.SPACING_MD,
                    ),
                    ft.Text(
                        "La factura se creará con los valores de la orden",
                        size=LayoutConstants.FONT_SIZE_SM,
                        color=ft.Colors.GREY_600,
                        italic=True,
                    ),
                ],
                spacing=LayoutConstants.SPACING_MD,
            ),
        )
    
    def _create_info_row(self, label: str, value: str) -> ft.Row:
        """Crea una fila de información."""
        return ft.Row(
            controls=[
                ft.Text(
                    f"{label}:",
                    size=LayoutConstants.FONT_SIZE_MD,
                    weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                    width=150,
                    color=ft.Colors.GREY_700,
                ),
                ft.Text(
                    value,
                    size=LayoutConstants.FONT_SIZE_MD,
                    expand=True,
                ),
            ],
        )
    
    def _on_invoice_type_change(self, e):
        """Callback cuando cambia el tipo de factura."""
        invoice_type = self.invoice_type_class.value
        logger.info(f"Invoice type changed to: {invoice_type}")
        
        if invoice_type == "SII":
            self.specific_fields_container.content = self._build_sii_fields()
        else:
            self.specific_fields_container.content = self._build_export_fields()
        
        if self.page:
            self.update()
    
    async def _save(self, e):
        """Guarda la factura."""
        if self._is_saving:
            return
        
        logger.info("Saving invoice...")
        
        # Validar
        if not self._validate():
            return
        
        self._is_saving = True
        if self.page:
            self.update()
        
        try:
            from src.frontend.services.api import invoice_api
            
            invoice_type_class = self.invoice_type_class.value
            
            # Preparar datos comunes
            invoice_data = {
                "invoice_number": self.invoice_number.get_value(),
                "revision": self.revision.get_value(),
                "order_id": self.order_id,
                "company_id": self._order_data.get("company_id"),
                "staff_id": self._order_data.get("staff_id", 1),  # TODO: Get from session
                "payment_status_id": 1,  # Pendiente por defecto
                "invoice_date": self.invoice_date.value,
                "currency_id": 1,  # TODO: Get from order
                "subtotal": str(self._order_data.get("subtotal", 0)),
                "total": str(self._order_data.get("total", 0)),
                "notes": self.notes.value if self.notes.value else None,
            }
            
            # Agregar fechas opcionales
            if self.due_date.value:
                invoice_data["due_date"] = self.due_date.value
            
            if self.payment_terms.value:
                invoice_data["payment_terms"] = self.payment_terms.value
            
            # Campos específicos según tipo
            if invoice_type_class == "SII":
                invoice_data["invoice_type"] = self.invoice_type_sii.value
                invoice_data["tax_amount"] = str(self._order_data.get("tax_amount", 0))
                invoice_data["net_amount"] = str(self._order_data.get("subtotal", 0))
                invoice_data["exempt_amount"] = "0"
                
                created = await invoice_api.create_sii(invoice_data, user_id=1)  # TODO: Get real user_id
            else:
                invoice_data["invoice_type"] = self.invoice_type_export.value
                invoice_data["exchange_rate"] = "1.0"  # TODO: Get from order or config
                invoice_data["incoterm_id"] = 1  # TODO: Get from order
                invoice_data["country_id"] = 1  # TODO: Get from order/company
                invoice_data["total_clp"] = str(self._order_data.get("total", 0))
                invoice_data["freight_cost"] = "0"
                invoice_data["insurance_cost"] = "0"
                
                if self.shipping_date.value:
                    invoice_data["shipping_date"] = self.shipping_date.value
                
                if self.port_of_loading.value:
                    invoice_data["port_of_loading"] = self.port_of_loading.value
                
                if self.port_of_discharge.value:
                    invoice_data["port_of_discharge"] = self.port_of_discharge.value
                
                created = await invoice_api.create_export(invoice_data, user_id=1)
            
            logger.success(f"Invoice created: {created.get('invoice_number')}")
            
            if self.page:
                snackbar = ft.SnackBar(
                    content=ft.Text("Factura guardada con éxito"),
                    bgcolor=ft.Colors.GREEN_700,
                )
                self.page.overlay.append(snackbar)
                snackbar.open = True
                # No actualizamos aquí porque vamos a navegar
            if self.on_save:
                self.on_save()
            
        except Exception as e:
            logger.exception(f"Error saving invoice: {e}")
            self._is_saving = False
            
            if self.page:
                snackbar = ft.SnackBar(
                    content=ft.Text(f"Error al guardar factura: {str(e)}"),
                    bgcolor=ft.Colors.RED_700,
                )
                self.page.overlay.append(snackbar)
                snackbar.open = True
                self.update()
    
    def _validate(self) -> bool:
        """Valida el formulario."""
        res_number = self.invoice_number.validate()
        res_revision = self.revision.validate()
        
        # Validar fechas si tienen valor
        # (Podríamos poner validadores más pro en el futuro)
        
        return res_number and res_revision
    
    def _cancel(self, e):
        """Cancela la edición."""
        logger.info("Form cancelled")
        if self.on_cancel:
            self.on_cancel()

    def _on_generate_fake_data(self, e: ft.ControlEvent) -> None:
        """Llena el formulario con datos ficticios."""
        if self._is_loading or self.invoice_id:
            return

        try:
            FakeDataGenerator.populate_invoice_form(self)
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
            logger.exception(f"Error generating fake invoice data: {ex}")
            if self.page:
                snackbar = ft.SnackBar(
                    content=ft.Text(t("orders.form.fake_data_error", {"error": str(ex)})),
                    bgcolor=ft.Colors.RED,
                    duration=3000,
                )
                self.page.overlay.append(snackbar)
                snackbar.open = True
                self.page.update()
