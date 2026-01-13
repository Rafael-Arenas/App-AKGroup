"""
Vista de detalle de orden.

Muestra información completa de una orden, incluyendo productos y totales.
"""
from decimal import Decimal
from typing import Callable
import flet as ft
from loguru import logger

from src.frontend.app_state import app_state
from src.frontend.layout_constants import LayoutConstants
from src.frontend.i18n.translation_manager import t
from src.frontend.components.common import BaseCard, LoadingSpinner, ErrorDisplay, ConfirmDialog, DataTable


class OrderDetailView(ft.Container):
    """
    Vista de detalle de orden.

    Args:
        order_id: ID de la orden a mostrar
        company_id: ID de la empresa asociada (para navegación)
        company_type: Tipo de empresa (para navegación)
        on_edit: Callback cuando se edita la orden
        on_delete: Callback cuando se elimina la orden
        on_back: Callback para volver atrás

    Example:
        >>> detail = OrderDetailView(order_id=123, company_id=1, on_edit=handle_edit)
        >>> page.add(detail)
    """

    def __init__(
        self,
        order_id: int,
        company_id: int,
        company_type: str,
        on_edit: Callable[[int], None] | None = None,
        on_delete: Callable[[int], None] | None = None,
        on_back: Callable[[], None] | None = None,
    ):
        """Inicializa la vista de detalle de orden."""
        super().__init__()
        self.order_id = order_id
        self.company_id = company_id
        self.company_type = company_type
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_back = on_back

        self._is_loading: bool = True
        self._error_message: str = ""
        self._order: dict | None = None

        # Configurar propiedades del contenedor
        self.expand = True
        self.padding = LayoutConstants.PADDING_LG

        # Construir contenido inicial (loading)
        self.content = self.build()

        logger.info(f"OrderDetailView initialized: order_id={order_id}")

    def build(self) -> ft.Control:
        """Construye el componente de detalle de orden."""
        if self._is_loading:
            return ft.Container(
                content=LoadingSpinner(message=t("common.loading")),
                expand=True,
                alignment=ft.Alignment(0, 0),  # center
            )
        elif self._error_message:
            return ft.Container(
                content=ErrorDisplay(
                    message=self._error_message,
                    on_retry=self.load_order,
                ),
                expand=True,
                alignment=ft.Alignment(0, 0),  # center
            )

        if not self._order:
             return ft.Container(
                content=ErrorDisplay(
                    message=t("orders.messages.not_found"),
                    on_retry=self.load_order,
                ),
                expand=True,
                alignment=ft.Alignment(0, 0),  # center
            )

        # Badge de estado
        status_id = self._order.get("status_id")
        status_text = t("orders.status.pending")
        status_color = ft.Colors.GREY
        
        # Mapeo simple temporal
        if status_id == 1:
             status_text = t("orders.status.pending")
             status_color = ft.Colors.GREY
        elif status_id == 2:
             status_text = t("orders.status.confirmed")
             status_color = ft.Colors.BLUE
        elif status_id == 3:
             status_text = t("orders.status.in_progress")
             status_color = ft.Colors.ORANGE
        elif status_id == 4:
             status_text = t("orders.status.completed")
             status_color = ft.Colors.GREEN
        elif status_id == 5:
             status_text = t("orders.status.cancelled")
             status_color = ft.Colors.RED
        
        status_badge = ft.Container(
            content=ft.Text(
                status_text,
                size=LayoutConstants.FONT_SIZE_SM,
                weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                color=ft.Colors.WHITE,
            ),
            padding=ft.padding.symmetric(
                horizontal=LayoutConstants.PADDING_SM,
                vertical=LayoutConstants.PADDING_XS,
            ),
            border_radius=LayoutConstants.RADIUS_SM,
            bgcolor=status_color,
        )

        # Badge de estado de pago
        payment_status_id = self._order.get("payment_status_id")
        payment_status_text = t("orders.payment_status.pending")
        payment_status_color = ft.Colors.GREY
        
        if payment_status_id == 1:
             payment_status_text = t("orders.payment_status.pending")
             payment_status_color = ft.Colors.GREY
        elif payment_status_id == 2:
             payment_status_text = t("orders.payment_status.partial")
             payment_status_color = ft.Colors.ORANGE
        elif payment_status_id == 3:
             payment_status_text = t("orders.payment_status.paid")
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
                            tooltip="Volver",
                            on_click=self._on_back_click,
                        ),
                        ft.Icon(ft.Icons.SHOPPING_BAG,
                            size=LayoutConstants.ICON_SIZE_XL,
                        ),
                        ft.Column(
                            controls=[
                                ft.Text(
                                    self._order.get("order_number", "Sin número"),
                                    size=LayoutConstants.FONT_SIZE_DISPLAY_MD,
                                    weight=LayoutConstants.FONT_WEIGHT_BOLD,
                                ),
                                ft.Row(
                                    controls=[
                                        ft.Text(
                                            f"{t('orders.fields.revision')}: {self._order.get('revision', '')}",
                                            size=LayoutConstants.FONT_SIZE_MD,
                                            color=ft.Colors.GREY_700
                                        ),
                                        status_badge,
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

        # Información General de la Orden
        general_info_controls = [
            self._create_info_row(t("orders.fields.revision"), self._order.get("revision", "-")),
            self._create_info_row(t("orders.fields.order_number"), self._order.get("order_number", "-")),
            self._create_info_row(t("orders.fields.order_date"), self._order.get("order_date", "-")),
            self._create_info_row(t("orders.fields.promised_date"), self._order.get("promised_date", "-") or "-"),
            self._create_info_row(t("orders.fields.order_type"), self._order.get("order_type", "-")),
            self._create_info_row(t("orders.fields.staff"), str(self._order.get("staff_id", "-"))),
        ]
        
        if self._order.get("customer_po_number"):
            general_info_controls.append(
                self._create_info_row(t("orders.fields.customer_po_number"), self._order.get("customer_po_number", "-"))
            )
        
        if self._order.get("project_number"):
            general_info_controls.append(
                self._create_info_row(t("orders.fields.project_number"), self._order.get("project_number", "-"))
            )
        
        if self._order.get("completed_date"):
            general_info_controls.append(
                self._create_info_row(t("orders.fields.completed_date"), self._order.get("completed_date", "-"))
            )

        general_info = ft.Column(
            controls=general_info_controls,
            spacing=LayoutConstants.SPACING_SM,
        )

        general_card = BaseCard(
            title=t("orders.sections.general_info"),
            icon=ft.Icons.INFO_OUTLINED,
            content=general_info,
        )

        # Información Financiera
        financial_info_controls = [
             self._create_info_row(t("orders.fields.currency"), str(self._order.get("currency_id", "-"))),
             self._create_info_row(t("orders.fields.exchange_rate"), f"{float(self._order.get('exchange_rate', 1) or 1):.2f}"),
        ]
        
        if self._order.get("incoterm_id"):
            financial_info_controls.append(
                self._create_info_row(t("orders.fields.incoterm"), str(self._order.get("incoterm_id", "-")))
            )
        
        if self._order.get("payment_terms"):
            financial_info_controls.append(
                self._create_info_row(t("orders.fields.payment_terms"), self._order.get("payment_terms", "-"))
            )
        
        if self._order.get("is_export"):
            financial_info_controls.append(
                self._create_info_row(t("orders.fields.is_export"), "Sí" if self._order.get("is_export") else "No")
            )

        financial_info = ft.Column(
            controls=financial_info_controls,
            spacing=LayoutConstants.SPACING_SM,
        )
        
        financial_card = BaseCard(
            title=t("orders.sections.financial_details"),
            icon=ft.Icons.ATTACH_MONEY,
            content=financial_info,
        )

        # Productos
        products = self._order.get("products", [])
        products_table = DataTable(
            columns=[
                {"key": "product_name", "label": "quotes.products_table.product", "sortable": True},
                {"key": "product_type", "label": "articles.form.type", "sortable": True},
                {"key": "quantity", "label": "quotes.products_table.quantity", "numeric": True},
                {"key": "unit_price", "label": "quotes.products_table.unit_price", "numeric": True},
                {"key": "total", "label": "quotes.products_table.total", "numeric": True},
            ],
            page_size=100,
        )
        
        # Formatear productos para la tabla
        formatted_products = []
        for p in products:
            # Obtener nombre del producto según el idioma actual
            product_data = p.get("product", {}) or {}
            current_lang = app_state.i18n.current_language
            
            if current_lang == "es":
                product_name = product_data.get("designation_es") or product_data.get("reference", f"Producto #{p.get('product_id')}")
            elif current_lang == "fr":
                product_name = product_data.get("designation_fr") or product_data.get("designation_es") or product_data.get("reference", f"Producto #{p.get('product_id')}")
            else:
                product_name = product_data.get("designation_en") or product_data.get("designation_es") or product_data.get("reference", f"Producto #{p.get('product_id')}")
            
            # Obtener tipo de producto
            product_type_raw = product_data.get("product_type", "article")
            product_type = t(f"articles.types.{product_type_raw}") if product_type_raw else ""
            
            qty = float(p.get("quantity", 0))
            price = float(p.get("unit_price", 0))
            subtotal = float(p.get("subtotal", 0))

            formatted_products.append({
                "id": p.get("id"),
                "product_name": product_name,
                "product_type": product_type,
                "quantity": f"{qty:.2f}",
                "unit_price": f"${price:,.2f}",
                "total": f"${subtotal:,.2f}",
            })
            
        products_table.set_data(formatted_products, total=len(products))

        products_card = BaseCard(
            title=f"{t('orders.sections.products')} ({len(products)})",
            icon=ft.Icons.SHOPPING_CART_OUTLINED,
            content=products_table,
        )

        # Totales
        tax_percent = float(self._order.get('tax_percentage', 19))
        totals_column = ft.Column(
            controls=[
                 self._create_total_row(t("orders.fields.subtotal"), float(self._order.get("subtotal", 0))),
                 self._create_total_row(t("orders.fields.taxes").format(percent=tax_percent), float(self._order.get("tax_amount", 0))),
                 ft.Divider(),
                 self._create_total_row(t("orders.fields.total_amount"), float(self._order.get("total", 0)), is_bold=True, size=20),
            ],
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
        if self._order.get("notes"):
             notes_content.append(ft.Text(f"{t('orders.sections.customer_notes')}:", weight=ft.FontWeight.BOLD))
             notes_content.append(ft.Text(self._order.get("notes")))
             notes_content.append(ft.Divider())
        
        if self._order.get("internal_notes"):
             notes_content.append(ft.Text(f"{t('orders.sections.internal_notes')}:", weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_700))
             notes_content.append(ft.Text(self._order.get("internal_notes"), italic=True, color=ft.Colors.GREY_700))

        if not notes_content:
            notes_content.append(ft.Text(t("orders.sections.no_notes"), italic=True, color=ft.Colors.GREY))

        notes_card = BaseCard(
            title=t("orders.sections.notes"),
            icon=ft.Icons.NOTE,
            content=ft.Column(notes_content),
        )

        # Información de Entregas (Delivery Orders)
        deliveries = self._order.get("delivery_orders", [])
        delivery_controls = []
        
        if deliveries:
            for delivery in deliveries:
                delivery_controls.append(
                    self._create_info_row(
                        t("orders.delivery.number"),
                        f"{delivery.get('delivery_number', '-')} (Rev. {delivery.get('revision', '-')})"
                    )
                )
        else:
            delivery_controls.append(
                ft.Text(t("orders.delivery.no_deliveries"), italic=True, color=ft.Colors.GREY)
            )
        
        delivery_card = BaseCard(
            title=t("orders.sections.deliveries"),
            icon=ft.Icons.LOCAL_SHIPPING,
            content=ft.Column(delivery_controls, spacing=LayoutConstants.SPACING_SM),
        )

        # Direcciones Asociadas
        addresses_controls = []
        
        shipping_addr = self._order.get("shipping_address")
        if shipping_addr:
            addr_text = f"{shipping_addr.get('street', '')}, {shipping_addr.get('city', '')}"
            addresses_controls.append(
                self._create_info_row(t("orders.address.shipping"), addr_text)
            )
        
        billing_addr = self._order.get("billing_address")
        if billing_addr:
            addr_text = f"{billing_addr.get('street', '')}, {billing_addr.get('city', '')}"
            addresses_controls.append(
                self._create_info_row(t("orders.address.billing"), addr_text)
            )
        
        if not addresses_controls:
            addresses_controls.append(
                ft.Text(t("orders.address.no_addresses"), italic=True, color=ft.Colors.GREY)
            )
        
        addresses_card = BaseCard(
            title=t("orders.sections.addresses"),
            icon=ft.Icons.LOCATION_ON,
            content=ft.Column(addresses_controls, spacing=LayoutConstants.SPACING_SM),
        )

        # Transporte Asociado
        transport = self._order.get("transport")
        transport_controls = []
        
        if transport:
            transport_controls.append(
                self._create_info_row(t("orders.transport.name"), transport.get("name", "-"))
            )
            if transport.get("delivery_number"):
                transport_controls.append(
                    self._create_info_row(t("orders.transport.delivery_number"), transport.get("delivery_number", "-"))
                )
        else:
            transport_controls.append(
                ft.Text(t("orders.transport.no_transport"), italic=True, color=ft.Colors.GREY)
            )
        
        transport_card = BaseCard(
            title=t("orders.sections.transport"),
            icon=ft.Icons.LOCAL_SHIPPING_OUTLINED,
            content=ft.Column(transport_controls, spacing=LayoutConstants.SPACING_SM),
        )

        # Condición de Pago
        payment_condition = self._order.get("payment_condition")
        payment_controls = []
        
        if payment_condition:
            payment_controls.append(
                self._create_info_row(
                    t("orders.payment.condition_number"),
                    f"{payment_condition.get('payment_condition_number', '-')} (Rev. {payment_condition.get('revision', '-')})"
                )
            )
            payment_controls.append(
                self._create_info_row(t("orders.payment.name"), payment_condition.get("name", "-"))
            )
            
            payment_type = payment_condition.get("payment_type")
            if payment_type:
                payment_controls.append(
                    self._create_info_row(
                        t("orders.payment.type"),
                        f"{payment_type.get('name', '-')} ({payment_type.get('days', 0)} días)"
                    )
                )
        else:
            payment_controls.append(
                ft.Text(t("orders.payment.no_payment_condition"), italic=True, color=ft.Colors.GREY)
            )
        
        payment_card = BaseCard(
            title=t("orders.sections.payment_condition"),
            icon=ft.Icons.PAYMENT,
            content=ft.Column(payment_controls, spacing=LayoutConstants.SPACING_SM),
        )

        # Layout Final
        
        # Columna izquierda (Info General, Entregas, Direcciones)
        left_col = ft.Column(
            controls=[general_card, delivery_card, addresses_card],
            spacing=LayoutConstants.SPACING_MD,
            expand=1,
        )
        
        # Columna central (Transporte, Pago, Financiera)
        center_col = ft.Column(
            controls=[transport_card, payment_card, financial_card],
            spacing=LayoutConstants.SPACING_MD,
            expand=1,
        )
        
        # Columna derecha (Productos, Totales, Notas)
        right_col = ft.Column(
            controls=[products_card, totals_card, notes_card],
            spacing=LayoutConstants.SPACING_MD,
            expand=2,
        )

        content = ft.Column(
            controls=[
                header,
                ft.Row(
                    controls=[left_col, center_col, right_col],
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    expand=True,
                    spacing=LayoutConstants.SPACING_LG,
                )
            ],
            spacing=LayoutConstants.SPACING_LG,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        return content

    def _create_info_row(self, label: str, value: str) -> ft.Row:
        """Crea una fila de información."""
        return ft.Row(
            controls=[
                ft.Text(
                    f"{label}:",
                    size=LayoutConstants.FONT_SIZE_MD,
                    weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                    width=150,
                    color=ft.Colors.GREY_700
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
        logger.info("OrderDetailView mounted")
        app_state.theme.add_observer(self._on_state_changed)
        app_state.i18n.add_observer(self._on_state_changed)
        if self.page:
            self.page.run_task(self.load_order)

    def will_unmount(self) -> None:
        """Lifecycle: Se ejecuta cuando el componente se desmonta."""
        app_state.theme.remove_observer(self._on_state_changed)
        app_state.i18n.remove_observer(self._on_state_changed)

    async def load_order(self) -> None:
        """Carga los datos de la orden desde la API."""
        logger.info(f"Loading order ID={self.order_id}")
        self._is_loading = True
        self._error_message = ""

        # Reconstruir contenido para mostrar loading
        self.content = self.build()
        if self.page:
            self.update()

        try:
            from src.frontend.services.api import order_api
            from src.frontend.services.api import CompanyAPI
            
            self._order = await order_api.get_by_id(self.order_id)
            
            logger.success(f"Order loaded: {self._order.get('order_number')}")

            try:
                company_api = CompanyAPI()
                company = await company_api.get_by_id(self.company_id)
                company_name = (company or {}).get("name")
                if company_name:
                    dashboard_route = f"/companies/dashboard/{self.company_id}/{self.company_type}"
                    updated_path: list[dict[str, str | None]] = []
                    for item in app_state.navigation.breadcrumb_path:
                        if item.get("route") == dashboard_route:
                            updated_path.append({"label": str(company_name), "route": dashboard_route})
                        else:
                            updated_path.append(item)
                    app_state.navigation.set_breadcrumb(updated_path)
            except Exception as e:
                logger.warning(f"Could not update breadcrumb company name: {e}")

            self._is_loading = False

        except Exception as e:
            logger.exception(f"Error loading order: {e}")
            self._error_message = t("orders.messages.error_loading", error=str(e))
            self._is_loading = False

        # Reconstruir contenido con los datos cargados
        self.content = self.build()
        if self.page:
            self.update()

    def _on_edit_click(self, e: ft.ControlEvent) -> None:
        """Callback para editar."""
        if self.on_edit:
            self.on_edit(self.order_id)

    def _on_delete_click(self, e: ft.ControlEvent) -> None:
        """Callback para eliminar."""
        if self.page:
            confirm_dialog = ConfirmDialog(
                title=t("common.confirm_delete"),
                message=t("orders.messages.delete_confirm", number=self._order.get('order_number')),
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
            self.on_delete(self.order_id)

    def _on_back_click(self, e: ft.ControlEvent) -> None:
        """Callback para volver atrás."""
        if self.on_back:
            self.on_back()

    def _on_state_changed(self) -> None:
        """Observer: Se ejecuta cuando cambia el estado."""
        logger.debug("OrderDetailView state changed, rebuilding content")
        self.content = self.build()
        if self.page:
            self.update()
