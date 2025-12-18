"""
Vistas relacionadas a una empresa (Cotizaciones, Órdenes, Entregas, Facturas).
"""
import flet as ft
from loguru import logger
from typing import Callable, Any

from src.frontend.app_state import app_state
from src.frontend.layout_constants import LayoutConstants
from src.frontend.views.quotes.quote_form_view import QuoteFormDialog
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
                alignment=ft.alignment.center,
            )
            
        if self._error_message:
            return ft.Container(
                content=ErrorDisplay(
                    message=self._error_message,
                    on_retry=self.load_data,
                ),
                expand=True,
                alignment=ft.alignment.center,
            )

        # Header con botón de volver
        header = ft.Row(
            controls=[
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    tooltip="Volver al Dashboard",
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
                    ft.Text("En Construcción", size=20, color=ft.Colors.GREY_600),
                    ft.Text(f"Aquí se mostrarán las {t(self.title_key).lower()} de {self._company.get('name')}", color=ft.Colors.GREY_500),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            expand=True,
            alignment=ft.alignment.center
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
    def __init__(self, company_id: int, company_type: str, on_back: Callable[[], None]):
        super().__init__(
            company_id=company_id,
            company_type=company_type,
            title_key="quotes.title",
            icon=ft.Icons.DESCRIPTION_OUTLINED,
            color=ft.Colors.ORANGE,
            on_back=on_back
        )
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
                    title=t("quotes.title"),
                    message=f"No hay cotizaciones registradas para {self._company.get('name')}",
                    action_text="Crear Cotización",
                    on_action=self._on_create_quote
                ),
                expand=True,
                alignment=ft.alignment.center
            )

        # SearchBar
        self._search_bar = SearchBar(
            placeholder="Buscar cotizaciones...",
            on_search=self._on_search,
        )

        # DataTable
        self._data_table = DataTable(
            columns=[
                {"key": "quote_number", "label": "Número", "sortable": True},
                {"key": "subject", "label": "Asunto", "sortable": True},
                {"key": "date", "label": "Fecha", "sortable": True},
                {"key": "total", "label": "Total", "sortable": True},
                {"key": "status", "label": "Estado", "sortable": True},
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
                            text="Nueva Cotización",
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
                "total": f"${quote.get('total', 0):,.2f}", # Simple format for now
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
        # TODO: Implementar vista de detalle de cotización
        pass

    def _on_create_quote(self, e=None):
        if not self.page:
            return

        dialog = QuoteFormDialog(
            page=self.page,
            company_id=self.company_id,
            on_save=self.load_data
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _on_edit_quote(self, row_data: dict):
        if not self.page:
            return
            
        quote = row_data.get("_original")
        if not quote:
            return

        dialog = QuoteFormDialog(
            page=self.page,
            company_id=self.company_id,
            quote=quote,
            on_save=self.load_data
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _on_delete_quote(self, row_data: dict):
        if not self.page:
            return
            
        quote = row_data.get("_original")
        if not quote:
            return

        def confirm_delete():
            self.page.run_task(self._delete_quote_task, quote["id"])

        dialog = ConfirmDialog(
            title="Eliminar Cotización",
            message=f"¿Estás seguro de eliminar la cotización {quote.get('quote_number')}?",
            on_confirm=confirm_delete,
            variant="danger",
            confirm_text="Eliminar"
        )
        dialog.show(self.page)

    async def _delete_quote_task(self, quote_id: int):
        from src.frontend.services.api import quote_api
        try:
            await quote_api.delete(quote_id)
            self.page.show_snack_bar(ft.SnackBar(content=ft.Text("Cotización eliminada")))
            await self.load_data()
        except Exception as e:
            logger.error(f"Error deleting quote: {e}")
            if self.page:
                self.page.show_snack_bar(ft.SnackBar(content=ft.Text(f"Error al eliminar: {str(e)}"), bgcolor="error"))


class CompanyOrdersView(CompanyRelatedBaseView):
    def __init__(self, company_id: int, company_type: str, on_back: Callable[[], None]):
        super().__init__(
            company_id=company_id,
            company_type=company_type,
            title_key="orders.title",
            icon=ft.Icons.SHOPPING_CART_OUTLINED,
            color=ft.Colors.GREEN,
            on_back=on_back
        )

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
