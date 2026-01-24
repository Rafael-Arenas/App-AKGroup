"""
Vista de detalle de factura.

Muestra información completa de una factura (SII o Export).
"""
from typing import Callable
import flet as ft
from loguru import logger

from src.frontend.app_state import app_state
from src.frontend.layout_constants import LayoutConstants
from src.frontend.i18n.translation_manager import t
from src.frontend.components.common import BaseCard, LoadingSpinner, ErrorDisplay, ConfirmDialog


class InvoiceDetailView(ft.Container):
    """
    Vista de detalle de factura (SII o Export).

    Args:
        invoice_id: ID de la factura a mostrar
        invoice_type_class: Clase de factura ("SII" o "EXPORT")
        on_edit: Callback cuando se edita la factura
        on_delete: Callback cuando se elimina la factura
        on_back: Callback para volver atrás
    """

    def __init__(
        self,
        invoice_id: int,
        invoice_type_class: str,  # "SII" or "EXPORT"
        on_edit: Callable[[int], None] | None = None,
        on_delete: Callable[[int], None] | None = None,
        on_back: Callable[[], None] | None = None,
    ):
        """Inicializa la vista de detalle de factura."""
        super().__init__()
        self.invoice_id = invoice_id
        self.invoice_type_class = invoice_type_class
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_back = on_back

        self._is_loading: bool = True
        self._error_message: str = ""
        self._invoice: dict | None = None

        # Configurar propiedades del contenedor
        self.expand = True
        self.padding = LayoutConstants.PADDING_LG

        # Construir contenido inicial (loading)
        self.content = self.build()

        logger.info(f"InvoiceDetailView initialized: invoice_id={invoice_id}, type={invoice_type_class}")

    def build(self) -> ft.Control:
        """Construye el componente de detalle de factura."""
        if self._is_loading:
            return ft.Container(
                content=LoadingSpinner(message=t("common.loading")),
                expand=True,
                alignment=ft.Alignment(0, 0),
            )
        elif self._error_message:
            return ft.Container(
                content=ErrorDisplay(
                    message=self._error_message,
                    on_retry=self.load_invoice,
                ),
                expand=True,
                alignment=ft.Alignment(0, 0),
            )

        if not self._invoice:
            return ft.Container(
                content=ErrorDisplay(
                    message=t("invoices.messages.not_found"),
                    on_retry=self.load_invoice,
                ),
                expand=True,
                alignment=ft.Alignment(0, 0),
            )

        # Badge de tipo de factura
        type_badge = ft.Container(
            content=ft.Text(
                self.invoice_type_class,
                size=LayoutConstants.FONT_SIZE_SM,
                weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                color=ft.Colors.WHITE,
            ),
            padding=ft.padding.symmetric(
                horizontal=LayoutConstants.PADDING_SM,
                vertical=LayoutConstants.PADDING_XS,
            ),
            border_radius=LayoutConstants.RADIUS_SM,
            bgcolor=ft.Colors.BLUE if self.invoice_type_class == "SII" else ft.Colors.PURPLE,
        )

        # Badge de estado de pago
        payment_status_id = self._invoice.get("payment_status_id")
        payment_status_text = "Pendiente"
        payment_status_color = ft.Colors.GREY

        if payment_status_id == 1:
            payment_status_text = "Pendiente"
            payment_status_color = ft.Colors.GREY
        elif payment_status_id == 2:
            payment_status_text = "Parcial"
            payment_status_color = ft.Colors.ORANGE
        elif payment_status_id == 3:
            payment_status_text = "Pagado"
            payment_status_color = ft.Colors.GREEN

        payment_status_badge = ft.Container(
            content=ft.Text(
                payment_status_text,
                size=LayoutConstants.FONT_SIZE_SM,
                weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                color=ft.Colors.WHITE,
            ),
            padding=ft.padding.symmetric(
                horizontal=LayoutConstants.PADDING_SM,
                vertical=LayoutConstants.PADDING_XS,
            ),
            border_radius=LayoutConstants.RADIUS_SM,
            bgcolor=payment_status_color,
        )

        # Header
        header = ft.Row(
            controls=[
                ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            tooltip=t("common.back"),
                            on_click=self._on_back_click,
                        ),
                        ft.Icon(
                            ft.Icons.RECEIPT_LONG,
                            size=LayoutConstants.ICON_SIZE_XL,
                        ),
                        ft.Column(
                            controls=[
                                ft.Text(
                                    self._invoice.get("invoice_number", "Sin número"),
                                    size=LayoutConstants.FONT_SIZE_DISPLAY_MD,
                                    weight=LayoutConstants.FONT_WEIGHT_BOLD,
                                ),
                                ft.Row(
                                    controls=[
                                        ft.Text(
                                            f"Rev. {self._invoice.get('revision', 'A')}",
                                            size=LayoutConstants.FONT_SIZE_MD,
                                            color=ft.Colors.GREY_700,
                                        ),
                                        type_badge,
                                        payment_status_badge,
                                    ],
                                    spacing=LayoutConstants.SPACING_SM,
                                ),
                            ],
                            expand=True,
                            spacing=LayoutConstants.SPACING_XS,
                        ),
                    ],
                    expand=True,
                ),
                ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.EDIT,
                            tooltip=t("common.edit"),
                            on_click=self._on_edit_click,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            tooltip=t("common.delete"),
                            on_click=self._on_delete_click,
                        ),
                    ],
                    spacing=LayoutConstants.SPACING_SM,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # Información General de la Factura
        invoice_type = self._invoice.get("invoice_type", "-")
        type_mapping = {
            "33": "Factura Electrónica",
            "34": "Factura Exenta",
            "56": "Nota de Débito",
            "61": "Nota de Crédito",
            "110": "Factura Export",
            "111": "Nota de Débito Export",
            "112": "Nota de Crédito Export",
        }
        type_text = type_mapping.get(invoice_type, invoice_type)

        general_info_controls = [
            self._create_info_row(t("invoices.fields.revision"), self._invoice.get("revision", "-")),
            self._create_info_row(t("invoices.fields.invoice_number"), self._invoice.get("invoice_number", "-")),
            self._create_info_row(t("invoices.fields.invoice_type"), type_text),
            self._create_info_row(t("invoices.fields.invoice_date"), str(self._invoice.get("invoice_date", "-"))),
            self._create_info_row(t("invoices.fields.order_id"), f"ID: {self._invoice.get('order_id', '-')}"),
            self._create_info_row(t("invoices.fields.company_id"), f"ID: {self._invoice.get('company_id', '-')}"),
            self._create_info_row(t("invoices.fields.staff_id"), f"ID: {self._invoice.get('staff_id', '-')}"),
        ]

        if self._invoice.get("due_date"):
            general_info_controls.append(
                self._create_info_row(t("invoices.fields.due_date"), str(self._invoice.get("due_date")))
            )

        if self._invoice.get("paid_date"):
            general_info_controls.append(
                self._create_info_row(t("invoices.fields.paid_date"), str(self._invoice.get("paid_date")))
            )

        if self._invoice.get("payment_terms"):
            general_info_controls.append(
                self._create_info_row(t("invoices.fields.payment_terms"), self._invoice.get("payment_terms", "-"))
            )

        general_info = ft.Column(
            controls=general_info_controls,
            spacing=LayoutConstants.SPACING_SM,
        )

        general_card = BaseCard(
            title=t("invoices.sections.general_info"),
            icon=ft.Icons.INFO_OUTLINED,
            content=general_info,
        )

        # Información específica SII
        sii_specific_card = None
        if self.invoice_type_class == "SII":
            sii_controls = []
            
            if self._invoice.get("sii_status"):
                sii_controls.append(
                    self._create_info_row("Estado SII", self._invoice.get("sii_status", "-"))
                )
            
            if self._invoice.get("sii_track_id"):
                sii_controls.append(
                    self._create_info_row("Track ID SII", self._invoice.get("sii_track_id", "-"))
                )
            
            if self._invoice.get("net_amount"):
                sii_controls.append(
                    self._create_info_row("Monto Neto", f"${float(self._invoice.get('net_amount', 0)):,.2f}")
                )
            
            if self._invoice.get("exempt_amount"):
                sii_controls.append(
                    self._create_info_row("Monto Exento", f"${float(self._invoice.get('exempt_amount', 0)):,.2f}")
                )

            if sii_controls:
                sii_specific_card = BaseCard(
                    title="Información SII",
                    icon=ft.Icons.DESCRIPTION_OUTLINED,
                    content=ft.Column(sii_controls, spacing=LayoutConstants.SPACING_SM),
                )

        # Información específica Export
        export_specific_card = None
        if self.invoice_type_class == "EXPORT":
            export_controls = []

            if self._invoice.get("shipping_date"):
                export_controls.append(
                    self._create_info_row(t("invoices.fields.shipping_date"), str(self._invoice.get("shipping_date")))
                )

            if self._invoice.get("incoterm_id"):
                export_controls.append(
                    self._create_info_row(t("invoices.fields.incoterm_id"), f"ID: {self._invoice.get('incoterm_id')}")
                )

            if self._invoice.get("country_id"):
                export_controls.append(
                    self._create_info_row(t("invoices.fields.country_id"), f"ID: {self._invoice.get('country_id')}")
                )

            if self._invoice.get("port_of_loading"):
                export_controls.append(
                    self._create_info_row("Puerto de Carga", self._invoice.get("port_of_loading", "-"))
                )

            if self._invoice.get("port_of_discharge"):
                export_controls.append(
                    self._create_info_row("Puerto de Descarga", self._invoice.get("port_of_discharge", "-"))
                )

            if self._invoice.get("freight_cost"):
                export_controls.append(
                    self._create_info_row("Costo de Flete", f"${float(self._invoice.get('freight_cost', 0)):,.2f}")
                )

            if self._invoice.get("insurance_cost"):
                export_controls.append(
                    self._create_info_row("Costo de Seguro", f"${float(self._invoice.get('insurance_cost', 0)):,.2f}")
                )

            if self._invoice.get("letter_of_credit"):
                export_controls.append(
                    self._create_info_row("Carta de Crédito", self._invoice.get("letter_of_credit", "-"))
                )

            if self._invoice.get("customs_declaration"):
                export_controls.append(
                    self._create_info_row("Declaración Aduanera", self._invoice.get("customs_declaration", "-"))
                )

            if self._invoice.get("bill_of_lading"):
                export_controls.append(
                    self._create_info_row("Bill of Lading", self._invoice.get("bill_of_lading", "-"))
                )

            if export_controls:
                export_specific_card = BaseCard(
                    title="Información de Exportación",
                    icon=ft.Icons.PUBLIC_OUTLINED,
                    content=ft.Column(export_controls, spacing=LayoutConstants.SPACING_SM),
                )

        # Totales
        totals_controls = [
            self._create_total_row(t("invoices.fields.subtotal"), float(self._invoice.get("subtotal", 0))),
        ]

        if self.invoice_type_class == "SII" and self._invoice.get("tax_amount"):
            totals_controls.append(
                self._create_total_row(t("invoices.fields.tax_amount"), float(self._invoice.get("tax_amount", 0)))
            )

        totals_controls.append(ft.Divider())
        totals_controls.append(
            self._create_total_row(t("invoices.fields.total"), float(self._invoice.get("total", 0)), is_bold=True, size=20)
        )

        if self.invoice_type_class == "EXPORT" and self._invoice.get("total_clp"):
            totals_controls.append(
                self._create_total_row("Total (CLP)", float(self._invoice.get("total_clp", 0)))
            )

        totals_column = ft.Column(
            controls=totals_controls,
            alignment=ft.MainAxisAlignment.END,
            horizontal_alignment=ft.CrossAxisAlignment.END,
        )

        totals_card = ft.Card(
            content=ft.Container(
                content=totals_column,
                padding=LayoutConstants.PADDING_LG,
            ),
            elevation=2,
        )

        # Notas
        notes_content = []
        if self._invoice.get("notes"):
            notes_content.append(ft.Text(self._invoice.get("notes")))
        else:
            notes_content.append(ft.Text(t("invoices.sections.no_notes"), italic=True, color=ft.Colors.GREY))

        notes_card = BaseCard(
            title=t("invoices.sections.notes"),
            icon=ft.Icons.NOTE,
            content=ft.Column(notes_content),
        )

        # Fechas
        created_at = self._invoice.get("created_at", "-")
        updated_at = self._invoice.get("updated_at", "-")
        dates_info = ft.Column(
            controls=[
                self._create_info_row(t("invoices.fields.invoice_date"), str(self._invoice.get("invoice_date", "-"))),
                self._create_info_row(t("invoices.fields.due_date"), str(self._invoice.get("due_date", "-")) if self._invoice.get("due_date") else "-"),
                self._create_info_row(t("invoices.fields.paid_date"), str(self._invoice.get("paid_date", "-")) if self._invoice.get("paid_date") else "-"),
                ft.Divider(height=LayoutConstants.SPACING_XS),
                self._create_info_row("Creado", str(created_at)[:19] if created_at != "-" else "-"),
                self._create_info_row("Actualizado", str(updated_at)[:19] if updated_at != "-" else "-"),
            ],
            spacing=LayoutConstants.SPACING_SM,
        )
        dates_card = BaseCard(title="Cronología", icon=ft.Icons.ACCESS_TIME, content=dates_info)

        # Layout: Split Layout (Barra Lateral)
        # Columna Principal (Izquierda - 70%)
        main_column_controls = [
            general_card,
            ft.Container(
                content=totals_card,
                alignment=ft.Alignment(1, 0),
            ),
            notes_card,
        ]

        if sii_specific_card:
            main_column_controls.insert(1, sii_specific_card)
        
        if export_specific_card:
            main_column_controls.insert(1, export_specific_card)

        main_column = ft.Column(
            controls=main_column_controls,
            spacing=LayoutConstants.SPACING_LG,
            expand=7,
        )

        # Columna Lateral (Derecha - 30%)
        sidebar_column = ft.Column(
            controls=[
                dates_card,
            ],
            spacing=LayoutConstants.SPACING_MD,
            expand=3,
        )

        # Layout Final
        content_layout = ft.Column(
            controls=[
                header,
                ft.Divider(height=LayoutConstants.SPACING_MD, color=ft.Colors.TRANSPARENT),
                ft.Row(
                    controls=[main_column, sidebar_column],
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    spacing=LayoutConstants.SPACING_LG,
                ),
            ],
            spacing=LayoutConstants.SPACING_LG,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        return content_layout

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

    def _create_total_row(self, label: str, value: float, is_bold: bool = False, size: int = 16) -> ft.Row:
        return ft.Row(
            controls=[
                ft.Text(
                    f"{label}:",
                    size=size,
                    weight=ft.FontWeight.BOLD if is_bold else ft.FontWeight.NORMAL,
                ),
                ft.Text(
                    f"${value:,.2f}",
                    size=size,
                    weight=ft.FontWeight.BOLD if is_bold else ft.FontWeight.NORMAL,
                ),
            ],
            alignment=ft.MainAxisAlignment.END,
            spacing=20,
        )

    def did_mount(self) -> None:
        """Lifecycle: Se ejecuta cuando el componente se monta."""
        logger.info("InvoiceDetailView mounted")
        app_state.theme.add_observer(self._on_state_changed)
        app_state.i18n.add_observer(self._on_state_changed)
        if self.page:
            self.page.run_task(self.load_invoice)

    def will_unmount(self) -> None:
        """Lifecycle: Se ejecuta cuando el componente se desmonta."""
        app_state.theme.remove_observer(self._on_state_changed)
        app_state.i18n.remove_observer(self._on_state_changed)

    async def load_invoice(self) -> None:
        """Carga los datos de la factura desde la API."""
        logger.info(f"Loading invoice ID={self.invoice_id}, type={self.invoice_type_class}")
        self._is_loading = True
        self._error_message = ""

        # Reconstruir contenido para mostrar loading
        self.content = self.build()
        if self.page:
            self.update()

        try:
            from src.frontend.services.api import invoice_api

            if self.invoice_type_class == "SII":
                self._invoice = await invoice_api.get_sii_by_id(self.invoice_id)
            else:
                self._invoice = await invoice_api.get_export_by_id(self.invoice_id)

            logger.success(f"Invoice loaded: {self._invoice.get('invoice_number')}")

            self._is_loading = False

        except Exception as e:
            logger.exception(f"Error loading invoice: {e}")
            self._error_message = t("invoices.messages.error_loading", {"error": str(e)})
            self._is_loading = False

        # Reconstruir contenido con los datos cargados
        self.content = self.build()
        if self.page:
            self.update()

    def _on_edit_click(self, e: ft.ControlEvent) -> None:
        """Callback para editar."""
        if self.on_edit:
            self.on_edit(self.invoice_id)

    def _on_delete_click(self, e: ft.ControlEvent) -> None:
        """Callback para eliminar."""
        if self.page:
            confirm_dialog = ConfirmDialog(
                title=t("common.confirm_delete"),
                message=t("invoices.messages.delete_confirm", {"number": self._invoice.get('invoice_number')}),
                confirm_text=t("common.delete"),
                cancel_text=t("common.cancel"),
                on_confirm=self._on_confirm_delete,
                on_cancel=lambda: None,
                variant="danger",
            )
            confirm_dialog.show(self.page)

    def _on_confirm_delete(self) -> None:
        """Callback cuando se confirma la eliminación."""
        if self.on_delete:
            self.on_delete(self.invoice_id)

    def _on_back_click(self, e: ft.ControlEvent) -> None:
        """Callback para volver atrás."""
        if self.on_back:
            self.on_back()

    def _on_state_changed(self) -> None:
        """Observer: Se ejecuta cuando cambia el estado."""
        logger.debug("InvoiceDetailView state changed, rebuilding content")
        self.content = self.build()
        if self.page:
            self.update()
