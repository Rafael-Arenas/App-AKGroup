"""
Vista de detalle de cotización.

Muestra información completa de una cotización, incluyendo productos y totales.
"""
from decimal import Decimal
from typing import Callable
import flet as ft
from loguru import logger

from src.frontend.app_state import app_state
from src.frontend.layout_constants import LayoutConstants
from src.frontend.i18n.translation_manager import t
from src.frontend.components.common import BaseCard, LoadingSpinner, ErrorDisplay, ConfirmDialog, DataTable, EmptyState


class QuoteDetailView(ft.Container):
    """
    Vista de detalle de cotización.

    Args:
        quote_id: ID de la cotización a mostrar
        company_id: ID de la empresa asociada (para navegación)
        company_type: Tipo de empresa (para navegación)
        on_edit: Callback cuando se edita la cotización
        on_delete: Callback cuando se elimina la cotización
        on_back: Callback para volver atrás

    Example:
        >>> detail = QuoteDetailView(quote_id=123, company_id=1, on_edit=handle_edit)
        >>> page.add(detail)
    """

    def __init__(
        self,
        quote_id: int,
        company_id: int,
        company_type: str,
        on_edit: Callable[[int], None] | None = None,
        on_delete: Callable[[int], None] | None = None,
        on_create_order: Callable[[int], None] | None = None,
        on_add_products: Callable[[int], None] | None = None,
        on_back: Callable[[], None] | None = None,
    ):
        """Inicializa la vista de detalle de cotización."""
        super().__init__()
        self.quote_id = quote_id
        self.company_id = company_id
        self.company_type = company_type
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_create_order = on_create_order
        self.on_add_products = on_add_products
        self.on_back = on_back

        self._is_loading: bool = True
        self._error_message: str = ""
        self._quote: dict | None = None

        # Configurar propiedades del contenedor
        self.expand = True
        self.padding = LayoutConstants.PADDING_LG

        # Construir contenido inicial (loading)
        self.content = self.build()

        logger.info(f"QuoteDetailView initialized: quote_id={quote_id}")

    def build(self) -> ft.Control:
        """Construye el componente de detalle de cotización."""
        # Contenedor para actualización dinámica
        self._main_container = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, spacing=LayoutConstants.SPACING_LG)

        if self._is_loading:
            self._main_container.controls = [
                ft.Container(
                    content=LoadingSpinner(message=t("common.loading")),
                    expand=True,
                    alignment=ft.Alignment(0, 0),
                )
            ]
            return self._main_container
        elif self._error_message:
            self._main_container.controls = [
                ft.Container(
                    content=ErrorDisplay(
                        message=self._error_message,
                        on_retry=self.load_quote,
                    ),
                    expand=True,
                    alignment=ft.Alignment(0, 0),
                )
            ]
            return self._main_container

        if not self._quote:
             self._main_container.controls = [
                ft.Container(
                    content=ErrorDisplay(
                        message=t("quotes.messages.not_found"),
                        on_retry=self.load_quote,
                    ),
                    expand=True,
                    alignment=ft.Alignment(0, 0),
                )
            ]
             return self._main_container

        # Badge de estado
        status_id = self._quote.get("status_id")
        status_text = t("quotes.status.draft")
        status_color = ft.Colors.GREY
        
        if status_id == 1:
             status_text = t("quotes.status.draft")
             status_color = ft.Colors.GREY
        elif status_id == 2:
             status_text = t("quotes.status.sent")
             status_color = ft.Colors.BLUE
        elif status_id == 3:
             status_text = t("quotes.status.accepted")
             status_color = ft.Colors.GREEN
        elif status_id == 4:
             status_text = t("quotes.status.rejected")
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
                        ft.Icon(ft.Icons.DESCRIPTION,
                            size=LayoutConstants.ICON_SIZE_XL,
                        ),
                        ft.Column(
                            controls=[
                                ft.Text(
                                    self._quote.get("quote_number", "Sin número"),
                                    size=LayoutConstants.FONT_SIZE_DISPLAY_MD,
                                    weight=LayoutConstants.FONT_WEIGHT_BOLD,
                                ),
                                ft.Row(
                                    controls=[
                                        ft.Text(
                                            self._quote.get("subject", ""),
                                            size=LayoutConstants.FONT_SIZE_MD,
                                            color=ft.Colors.GREY_700
                                        ),
                                        status_badge,
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
                        ft.Button(
                            content=ft.Text("Generar Orden"),
                            icon=ft.Icons.SHOPPING_BAG,
                            on_click=self._on_create_order_click,
                        ),
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

        # Información General
        general_info = ft.Column(
            controls=[
                self._create_info_row(t("quotes.fields.date"), self._quote.get("quote_date", "-")),
                self._create_info_row(t("quotes.fields.valid_until"), self._quote.get("valid_until", "-") or "-"),
                self._create_info_row(t("quotes.fields.shipping_date"), self._quote.get("shipping_date", "-") or "-"),
                self._create_info_row(t("quotes.fields.revision"), self._quote.get("revision", "-")),
                self._create_info_row(t("quotes.fields.staff"), str(self._quote.get("staff_id", "-"))),
            ],
            spacing=LayoutConstants.SPACING_SM,
        )

        general_card = BaseCard(
            title=t("quotes.sections.general_info"),
            icon=ft.Icons.INFO_OUTLINED,
            content=general_info,
        )

        # Información Financiera
        financial_info = ft.Column(
            controls=[
                 self._create_info_row(t("quotes.fields.currency"), str(self._quote.get("currency_id", "-"))),
                 self._create_info_row(t("quotes.fields.exchange_rate"), f"{float(self._quote.get('exchange_rate', 1) or 1):.2f}"),
                 self._create_info_row(t("quotes.fields.incoterm"), str(self._quote.get("incoterm_id", "-") or "-")),
            ],
            spacing=LayoutConstants.SPACING_SM,
        )
        
        financial_card = BaseCard(
            title=t("quotes.sections.financial_details"),
            icon=ft.Icons.ATTACH_MONEY,
            content=financial_info,
        )

        # Productos
        products = self._quote.get("products", [])
        
        if not products:
            products_content = EmptyState(
                icon=ft.Icons.SHOPPING_CART_OUTLINED,
                title="No hay productos",
                message="Esta cotización aún no tiene productos asociados. Agrega artículos o nomenclaturas para comenzar.",
                action_text="Agregar Productos",
                on_action=self._on_add_products_click,
            )
        else:
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
            
            # Obtener idioma actual para seleccionar la designación correcta
            current_lang = app_state.i18n.current_language
            
            formatted_products = []
            for p in products:
                product_info = p.get("product", {}) or {}
                
                # Seleccionar nombre según idioma
                if current_lang == "es":
                    product_name = product_info.get("designation_es") or product_info.get("designation_en") or product_info.get("reference", "")
                elif current_lang == "fr":
                    product_name = product_info.get("designation_fr") or product_info.get("designation_es") or product_info.get("reference", "")
                else:
                    product_name = product_info.get("designation_en") or product_info.get("designation_es") or product_info.get("reference", "")
                
                if not product_name:
                    product_name = f"Producto #{p.get('product_id')}"
                
                # Tipo de producto
                product_type_raw = product_info.get("product_type", "article")
                product_type = t(f"articles.types.{product_type_raw}") if product_type_raw else "-"
                
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
            products_content = products_table

        if products:
            products_card_content = ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(
                                f"{t('quotes.sections.products')} ({len(products)})",
                                size=LayoutConstants.FONT_SIZE_LG,
                                weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                                expand=True,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.ADD,
                                tooltip="Agregar más productos",
                                on_click=lambda e: self._on_add_products_click(),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    products_content,
                ],
                spacing=LayoutConstants.SPACING_SM,
            )
            products_card = ft.Card(
                content=ft.Container(
                    content=products_card_content,
                    padding=LayoutConstants.PADDING_LG,
                ),
                elevation=2,
            )
        else:
            products_card = BaseCard(
                title=f"{t('quotes.sections.products')} ({len(products)})",
                icon=ft.Icons.SHOPPING_CART_OUTLINED,
                content=products_content,
            )

        # Totales
        tax_percent = float(self._quote.get('tax_percentage', 19))
        totals_column = ft.Column(
            controls=[
                 self._create_total_row(t("quotes.fields.subtotal"), float(self._quote.get("subtotal", 0))),
                 self._create_total_row(t("quotes.fields.taxes").format(percent=tax_percent), float(self._quote.get("tax_amount", 0))),
                 ft.Divider(),
                 self._create_total_row(t("quotes.fields.total_amount"), float(self._quote.get("total", 0)), is_bold=True, size=20),
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
        if self._quote.get("notes"):
             notes_content.append(ft.Text(f"{t('quotes.sections.customer_notes')}:", weight=ft.FontWeight.BOLD))
             notes_content.append(ft.Text(self._quote.get("notes")))
             notes_content.append(ft.Divider())
        
        if self._quote.get("internal_notes"):
             notes_content.append(ft.Text(f"{t('quotes.sections.internal_notes')}:", weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_700))
             notes_content.append(ft.Text(self._quote.get("internal_notes"), italic=True, color=ft.Colors.GREY_700))

        if not notes_content:
            notes_content.append(ft.Text(t("quotes.sections.no_notes"), italic=True, color=ft.Colors.GREY))

        notes_card = BaseCard(
            title=t("quotes.sections.notes"),
            icon=ft.Icons.NOTE,
            content=ft.Column(notes_content),
        )

        # Layout Final
        left_col = ft.Column(
            controls=[general_card, financial_card, notes_card],
            spacing=LayoutConstants.SPACING_MD,
            expand=1,
        )
        
        right_col = ft.Column(
            controls=[products_card, totals_card],
            spacing=LayoutConstants.SPACING_MD,
            expand=2,
        )

        self._main_container.controls = [
            header,
            ft.Row(
                controls=[left_col, right_col],
                vertical_alignment=ft.CrossAxisAlignment.START,
                expand=True,
                spacing=LayoutConstants.SPACING_LG,
            )
        ]

        return self._main_container
    def _create_info_row(self, label: str, value: str) -> ft.Row:
        """Crea una fila de información."""
        return ft.Row(
            controls=[
                ft.Text(
                    f"{label}:",
                    size=LayoutConstants.FONT_SIZE_MD,
                    weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                    width=120,
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
        logger.info("QuoteDetailView mounted")
        app_state.theme.add_observer(self._on_state_changed)
        app_state.i18n.add_observer(self._on_state_changed)
        if self.page:
            self.page.run_task(self.load_quote)

    def will_unmount(self) -> None:
        """Lifecycle: Se ejecuta cuando el componente se desmonta."""
        app_state.theme.remove_observer(self._on_state_changed)
        app_state.i18n.remove_observer(self._on_state_changed)

    async def load_quote(self) -> None:
        """Carga los datos de la cotización desde la API."""
        logger.info(f"Loading quote ID={self.quote_id}")
        self._is_loading = True
        self._error_message = ""

        # Reconstruir contenido para mostrar loading
        self.content = self.build()
        if self.page:
            self.update()

        try:
            from src.frontend.services.api import quote_api
            from src.frontend.services.api import CompanyAPI
            
            # TODO: ensure quote_api is initialized or use the instance from api module
            # Based on previous file reads, it seems 'quote_api' is an instance in 'src.frontend.services.api'
            # Check import in CompanyQuotesView: "from src.frontend.services.api import quote_api"
            
            self._quote = await quote_api.get_by_id(self.quote_id)
            
            logger.success(f"Quote loaded: {self._quote.get('quote_number')}")

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
            logger.exception(f"Error loading quote: {e}")
            self._error_message = t("quotes.messages.error_loading", error=str(e))
            self._is_loading = False

        # Reconstruir contenido con los datos cargados
        self.content = self.build()
        if self.page:
            self.update()

    def _on_edit_click(self, e: ft.ControlEvent) -> None:
        """Callback para editar."""
        if self.on_edit:
            self.on_edit(self.quote_id)

    def _on_create_order_click(self, e: ft.ControlEvent) -> None:
        """Callback para crear orden desde la cotización."""
        if self.on_create_order:
            self.on_create_order(self.quote_id)

    def _on_delete_click(self, e: ft.ControlEvent) -> None:
        """Callback para eliminar."""
        if self.page:
            confirm_dialog = ConfirmDialog(
                title=t("common.confirm_delete"),
                message=t("quotes.messages.delete_confirm", number=self._quote.get('quote_number')),
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
            self.on_delete(self.quote_id)

    def _on_add_products_click(self, e=None) -> None:
        """Callback para agregar productos."""
        if self.on_add_products:
            self.on_add_products(self.quote_id)

    def _on_back_click(self, e: ft.ControlEvent) -> None:
        """Callback para volver atrás."""
        if self.on_back:
            self.on_back()

    def _on_state_changed(self) -> None:
        """Observer: Se ejecuta cuando cambia el estado."""
        logger.debug("QuoteDetailView state changed, rebuilding content")
        self.content = self.build()
        if self.page:
            self.update()
