"""
Vistas relacionadas a una empresa (Cotizaciones, Órdenes, Entregas, Facturas).
"""
import flet as ft
from loguru import logger
from typing import Callable, Any

from src.frontend.app_state import app_state
from src.frontend.layout_constants import LayoutConstants
from src.frontend.components.common import (
    LoadingSpinner, 
    ErrorDisplay,
    DataTable,
    SearchBar,
    EmptyState,
    ConfirmDialog,
)
from src.frontend.i18n.translation_manager import t

class CompanyRelatedBaseView(ft.Container):
    """
    Clase base para vistas relacionadas a una empresa.
    Muestra el header de la empresa y un contenido específico.
    """
    def __init__(
        self,
        company_id: int,
        company_type: str,
        title_key: str,
        icon: str,
        color: str,
        on_back: Callable[[], None],
    ):
        super().__init__()
        self.company_id = company_id
        self.company_type = company_type
        self.title_key = title_key
        self.icon = icon
        self.color = color
        self.on_back = on_back
        
        # Estado
        self._is_loading: bool = True
        self._error_message: str = ""
        self._company: dict | None = None
        
        self.expand = True
        self.padding = LayoutConstants.PADDING_LG
        self.content = self.build()

    def build(self) -> ft.Control:
        if self._is_loading:
            return ft.Container(
                content=LoadingSpinner(message=t("companies.messages.loading")),
                expand=True,
                alignment=ft.Alignment(0, 0),  # center
            )
            
        if self._error_message:
            return ft.Container(
                content=ErrorDisplay(
                    message=self._error_message,
                    on_retry=self.load_data,
                ),
                expand=True,
                alignment=ft.Alignment(0, 0),  # center
            )

        # Header con botón de volver
        header = ft.Row(
            controls=[
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    tooltip=t("common.back"),
                    on_click=lambda e: self.on_back(),
                ),
                ft.Icon(self.icon, size=32, color=self.color),
                ft.Column(
                    controls=[
                        ft.Text(t(self.title_key), size=20, weight=ft.FontWeight.BOLD),
                        ft.Text(f"{self._company.get('name', '')}", size=14, color=ft.Colors.GREY),
                    ],
                    spacing=0
                )
            ],
            spacing=16
        )

        # Contenido específico (placeholder por ahora o lista si se implementa)
        content_area = self.build_content()

        return ft.Column(
            controls=[
                ft.Container(content=header, padding=ft.padding.only(bottom=20), border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_300))),
                ft.Container(content=content_area, expand=True, padding=ft.padding.only(top=20))
            ],
            expand=True
        )

    def build_content(self) -> ft.Control:
        """
        Método a sobreescribir por las subclases para mostrar el contenido específico (tabla, lista, etc.)
        """
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.CONSTRUCTION, size=64, color=ft.Colors.GREY_400),
                    ft.Text(t("common.under_construction"), size=20, color=ft.Colors.GREY_600),
                    ft.Text(t("common.under_construction_description", {"title": t(self.title_key).lower(), "company": self._company.get('name')}), color=ft.Colors.GREY_500),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            expand=True,
            alignment=ft.Alignment(0, 0)  # center
        )

    def did_mount(self):
        if self.page:
            self.page.run_task(self.load_data)

    async def load_data(self):
        self._is_loading = True
        self._error_message = ""
        self.content = self.build()
        if self.page:
            self.update()
            
        try:
            # Cargar datos de la empresa
            from src.frontend.services.api import CompanyAPI
            company_api = CompanyAPI()
            self._company = await company_api.get_by_id(self.company_id)

            company_name = (self._company or {}).get("name")
            if company_name:
                dashboard_route = f"/companies/dashboard/{self.company_id}/{self.company_type}"
                updated_path: list[dict[str, str | None]] = []
                for item in app_state.navigation.breadcrumb_path:
                    if item.get("route") == dashboard_route:
                        updated_path.append({"label": str(company_name), "route": dashboard_route})
                    else:
                        updated_path.append(item)
                app_state.navigation.set_breadcrumb(updated_path)
            
            # Cargar datos específicos de la vista hija
            await self._load_child_data()
            
            self._is_loading = False
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            self._error_message = str(e)
            self._is_loading = False
            
        self.content = self.build()
        if self.page:
            self.update()

    async def _load_child_data(self):
        """
        Método a sobreescribir por las subclases para cargar sus propios datos.
        """
        pass


class CompanyQuotesView(CompanyRelatedBaseView):
    def __init__(
        self, 
        company_id: int, 
        company_type: str, 
        on_back: Callable[[], None],
        on_create_quote: Callable[[], None] | None = None,
        on_edit_quote: Callable[[int], None] | None = None,
        on_view_quote: Callable[[int], None] | None = None,
    ):
        logger.debug(f"CompanyQuotesView init: view_quote_callback={'provided' if on_view_quote else 'none'}")
        super().__init__(
            company_id=company_id,
            company_type=company_type,
            title_key="quotes.title",
            icon=ft.Icons.DESCRIPTION_OUTLINED,
            color=ft.Colors.ORANGE,
            on_back=on_back
        )
        self.on_create_quote = on_create_quote
        self.on_edit_quote = on_edit_quote
        self.on_view_quote = on_view_quote
        
        # Estado de la lista
        self._quotes: list[dict] = []
        self._total_quotes: int = 0
        self._current_page: int = 1
        self._page_size: int = 10
        self._search_query: str = ""
        
        # Componentes
        self._data_table: DataTable | None = None
        self._search_bar: SearchBar | None = None

    async def _load_child_data(self):
        from src.frontend.services.api import quote_api
        
        params = {
            "page": self._current_page,
            "page_size": self._page_size,
            "company_id": self.company_id
        }
        if self._search_query:
            params["query"] = self._search_query
            
        response = await quote_api.get_by_company(**params)
        self._quotes = response.get("items", [])
        self._total_quotes = response.get("total", 0)

    def build_content(self) -> ft.Control:
        if not self._quotes and not self._search_query:
            return ft.Container(
                content=EmptyState(
                    icon=ft.Icons.DESCRIPTION_OUTLINED,
                    title=t("quotes.no_quotes"),
                    message=t("quotes.no_quotes_message", {"company_name": self._company.get('name')}),
                    action_text=t("quotes.create"),
                    on_action=self._on_create_quote
                ),
                expand=True,
                alignment=ft.Alignment(0, 0)  # center
            )

        # SearchBar
        self._search_bar = SearchBar(
            placeholder=t("quotes.search_placeholder"),
            on_search=self._on_search,
        )

        # DataTable
        self._data_table = DataTable(
            columns=[
                {"key": "quote_number", "label": "quotes.columns.quote_number", "sortable": True},
                {"key": "subject", "label": "quotes.columns.subject", "sortable": True},
                {"key": "date", "label": "quotes.columns.quote_date", "sortable": True},
                {"key": "total", "label": "quotes.columns.total_amount", "sortable": True},
                {"key": "status", "label": "quotes.columns.status", "sortable": True},
            ],
            on_row_click=self._on_row_click,
            on_edit=self._on_edit_quote,
            on_delete=self._on_delete_quote,
            page_size=self._page_size,
            on_page_change=self._on_page_change,
        )

        formatted_data = self._format_quotes_for_table(self._quotes)
        self._data_table.set_data(
            formatted_data,
            total=self._total_quotes,
            current_page=self._current_page,
        )

        return ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row([
                        ft.Container(content=self._search_bar, expand=True),
                        ft.FloatingActionButton(
                            icon=ft.Icons.ADD,
                            on_click=self._on_create_quote,
                        )
                    ]),
                    padding=ft.padding.symmetric(horizontal=LayoutConstants.PADDING_LG),
                ),
                ft.Container(
                    content=self._data_table,
                    padding=ft.padding.only(
                        left=LayoutConstants.PADDING_LG,
                        right=LayoutConstants.PADDING_LG,
                        bottom=LayoutConstants.PADDING_LG,
                    ),
                    expand=True,
                ),
            ],
            spacing=LayoutConstants.SPACING_MD,
            expand=True
        )

    def _format_quotes_for_table(self, quotes: list[dict]) -> list[dict]:
        formatted = []
        for quote in quotes:
            formatted.append({
                "id": quote.get("id"),
                "quote_number": quote.get("quote_number", "-"),
                "subject": quote.get("subject", "-"),
                "date": quote.get("quote_date", "")[:10] if quote.get("quote_date") else "-",
                "total": f"${float(quote.get('total', 0)):,.2f}", # Simple format for now
                "status": str(quote.get("status_id", "Pendiente")), # TODO: Map ID to name
                "_original": quote,
            })
        return formatted

    def _on_search(self, query: str):
        self._search_query = query
        self._current_page = 1
        if self.page:
            self.page.run_task(self.load_data)

    def _on_page_change(self, page: int):
        self._current_page = page
        if self.page:
            self.page.run_task(self.load_data)

    def _on_row_click(self, row_data: dict):
        quote = row_data.get("_original")
        if not quote:
            return
            
        if self.on_view_quote:
            self.on_view_quote(quote["id"])

    def _on_create_quote(self, e=None):
        if self.on_create_quote:
            self.on_create_quote()

    def _on_edit_quote(self, row_data: dict):
        quote = row_data.get("_original")
        if not quote:
            return
        
        if self.on_edit_quote:
            self.on_edit_quote(quote["id"])

    def _on_delete_quote(self, row_data: dict):
        if not self.page:
            return
            
        quote = row_data.get("_original")
        if not quote:
            return

        def confirm_delete():
            self.page.run_task(self._delete_quote_task, quote["id"])

        dialog = ConfirmDialog(
            title=t("common.confirm_delete"),
            message=t("quotes.messages.delete_confirm", {"number": quote.get('quote_number')}),
            on_confirm=confirm_delete,
            variant="danger",
            confirm_text=t("common.delete")
        )
        dialog.show(self.page)

    async def _delete_quote_task(self, quote_id: int):
        from src.frontend.services.api import quote_api
        try:
            await quote_api.delete(quote_id)
            self.page.show_snack_bar(ft.SnackBar(content=ft.Text(t("quotes.messages.deleted"))))
            await self.load_data()
        except Exception as e:
            logger.error(f"Error deleting quote: {e}")
            if self.page:
                self.page.show_snack_bar(ft.SnackBar(content=ft.Text(t("quotes.messages.error_deleting", {"error": str(e)})), bgcolor="error"))


class CompanyOrdersView(CompanyRelatedBaseView):
    def __init__(
        self, 
        company_id: int, 
        company_type: str, 
        on_back: Callable[[], None],
        on_view_order: Callable[[int], None] | None = None,
        on_create_order: Callable[[], None] | None = None,
        on_edit_order: Callable[[int], None] | None = None,
    ):
        self.on_view_order = on_view_order
        self.on_create_order = on_create_order
        self.on_edit_order = on_edit_order
        
        self._orders: list[dict] = []
        self._total_orders: int = 0
        self._current_page: int = 1
        self._page_size: int = 10
        self._search_query: str = ""
        self._data_table: DataTable | None = None
        self._search_bar: SearchBar | None = None
        
        super().__init__(
            company_id=company_id,
            company_type=company_type,
            title_key="orders.title",
            icon=ft.Icons.SHOPPING_CART_OUTLINED,
            color=ft.Colors.GREEN,
            on_back=on_back
        )

    async def did_mount_async(self):
        await self.load_data()

    async def load_data(self):
        self._is_loading = True
        self._error_message = ""
        if self.page:
            self.content = self.build()
            self.update()

        try:
            await self._load_company_data()
            await self._load_child_data()
            self._is_loading = False
            if self.page:
                self.content = self.build()
                self.update()
        except Exception as e:
            logger.error(f"Error loading orders: {e}")
            self._is_loading = False
            self._error_message = str(e)
            if self.page:
                self.content = self.build()
                self.update()

    async def _load_company_data(self):
        from src.frontend.services.api import company_api
        self._company = await company_api.get_by_id(self.company_id)

    async def _load_child_data(self):
        from src.frontend.services.api import order_api
        
        response = await order_api.get_by_company(
            company_id=self.company_id,
            page=self._current_page,
            page_size=self._page_size
        )
        self._orders = response.get("items", [])
        self._total_orders = response.get("total", 0)

    def build_content(self) -> ft.Control:
        if not self._orders and not self._search_query:
            return ft.Container(
                content=EmptyState(
                    icon=ft.Icons.SHOPPING_CART_OUTLINED,
                    title=t("orders.no_orders"),
                    message=t("orders.no_orders_message", {"company_name": self._company.get('name')}),
                    action_text=t("orders.create"),
                    on_action=self._on_create_order
                ),
                expand=True,
                alignment=ft.Alignment(0, 0)
            )

        # SearchBar
        self._search_bar = SearchBar(
            placeholder=t("orders.search_placeholder"),
            on_search=self._on_search,
        )

        # DataTable
        self._data_table = DataTable(
            columns=[
                {"key": "order_number", "label": "orders.columns.order_number", "sortable": True},
                {"key": "revision", "label": "orders.columns.revision", "sortable": True},
                {"key": "date", "label": "orders.columns.order_date", "sortable": True},
                {"key": "total", "label": "orders.columns.total_amount", "sortable": True},
                {"key": "status", "label": "orders.columns.status", "sortable": True},
            ],
            on_row_click=self._on_row_click,
            on_edit=self._on_edit_order,
            on_delete=self._on_delete_order,
            page_size=self._page_size,
            on_page_change=self._on_page_change,
        )

        formatted_data = self._format_orders_for_table(self._orders)
        self._data_table.set_data(
            formatted_data,
            total=self._total_orders,
            current_page=self._current_page,
        )

        return ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row([
                        ft.Container(content=self._search_bar, expand=True),
                        ft.FloatingActionButton(
                            icon=ft.Icons.ADD,
                            on_click=self._on_create_order,
                        )
                    ]),
                    padding=ft.padding.symmetric(horizontal=LayoutConstants.PADDING_LG),
                ),
                ft.Container(
                    content=self._data_table,
                    padding=ft.padding.only(
                        left=LayoutConstants.PADDING_LG,
                        right=LayoutConstants.PADDING_LG,
                        bottom=LayoutConstants.PADDING_LG,
                    ),
                    expand=True,
                ),
            ],
            spacing=LayoutConstants.SPACING_MD,
            expand=True
        )

    def _format_orders_for_table(self, orders: list[dict]) -> list[dict]:
        formatted = []
        for order in orders:
            formatted.append({
                "id": order.get("id"),
                "order_number": order.get("order_number", "-"),
                "revision": order.get("revision", "-"),
                "date": order.get("order_date", "")[:10] if order.get("order_date") else "-",
                "total": f"${float(order.get('total', 0)):,.2f}",
                "status": str(order.get("status_id", "Pendiente")),
                "_original": order,
            })
        return formatted

    def _on_search(self, query: str):
        self._search_query = query
        self._current_page = 1
        if self.page:
            self.page.run_task(self.load_data)

    def _on_page_change(self, page: int):
        self._current_page = page
        if self.page:
            self.page.run_task(self.load_data)

    def _on_row_click(self, row_data: dict):
        order = row_data.get("_original")
        if not order:
            return
            
        if self.on_view_order:
            self.on_view_order(order["id"])

    def _on_create_order(self, e=None):
        if self.on_create_order:
            self.on_create_order()

    def _on_edit_order(self, row_data: dict):
        order = row_data.get("_original")
        if not order:
            return
        
        if self.on_edit_order:
            self.on_edit_order(order["id"])

    def _on_delete_order(self, row_data: dict):
        if not self.page:
            return
            
        order = row_data.get("_original")
        if not order:
            return

        def confirm_delete():
            self.page.run_task(self._delete_order_task, order["id"])

        dialog = ConfirmDialog(
            title=t("common.confirm_delete"),
            message=t("orders.messages.delete_confirm", {"number": order.get('order_number')}),
            on_confirm=confirm_delete,
            variant="danger",
            confirm_text=t("common.delete")
        )
        dialog.show(self.page)

    async def _delete_order_task(self, order_id: int):
        from src.frontend.services.api import order_api
        try:
            await order_api.delete(order_id, user_id=1)
            self.page.show_snack_bar(ft.SnackBar(content=ft.Text(t("orders.messages.deleted"))))
            await self.load_data()
        except Exception as e:
            logger.error(f"Error deleting order: {e}")
            if self.page:
                self.page.show_snack_bar(ft.SnackBar(content=ft.Text(t("orders.messages.error_deleting", {"error": str(e)})), bgcolor="error"))

class CompanyDeliveriesView(CompanyRelatedBaseView):
    def __init__(self, company_id: int, company_type: str, on_back: Callable[[], None]):
        super().__init__(
            company_id=company_id,
            company_type=company_type,
            title_key="deliveries.title",
            icon=ft.Icons.LOCAL_SHIPPING_OUTLINED,
            color=ft.Colors.TEAL,
            on_back=on_back
        )

class CompanyInvoicesView(CompanyRelatedBaseView):
    def __init__(self, company_id: int, company_type: str, on_back: Callable[[], None]):
        super().__init__(
            company_id=company_id,
            company_type=company_type,
            title_key="invoices.title",
            icon=ft.Icons.RECEIPT_LONG_OUTLINED,
            color=ft.Colors.INDIGO,
            on_back=on_back
        )
