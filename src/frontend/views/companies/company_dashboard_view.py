"""
Vista de Dashboard de Empresa.

Muestra un menú de navegación para acceder a las diferentes secciones
de una empresa específica (Detalles, Cotizaciones, Órdenes, etc.).
"""
from typing import Callable
import flet as ft
from loguru import logger

from src.frontend.app_state import app_state
from src.frontend.layout_constants import LayoutConstants
from src.frontend.components.common import LoadingSpinner, ErrorDisplay
from src.frontend.i18n.translation_manager import t


class CompanyDashboardView(ft.Container):
    """
    Vista dashboard para una empresa específica.
    """

    def __init__(
        self,
        company_id: int,
        company_type: str = "CLIENT",
        on_view_details: Callable[[int, str], None] | None = None,
        on_back: Callable[[], None] | None = None,
        on_view_quotes: Callable[[int, str], None] | None = None,
        on_view_orders: Callable[[int, str], None] | None = None,
        on_view_deliveries: Callable[[int, str], None] | None = None,
        on_view_invoices: Callable[[int, str], None] | None = None,
    ):
        super().__init__()
        self.company_id = company_id
        self.company_type = company_type
        self.on_view_details = on_view_details
        self.on_back = on_back
        self.on_view_quotes = on_view_quotes
        self.on_view_orders = on_view_orders
        self.on_view_deliveries = on_view_deliveries
        self.on_view_invoices = on_view_invoices

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
                    on_retry=self.load_company,
                ),
                expand=True,
                alignment=ft.alignment.center,
            )

        # Header
        header = ft.Row(
            controls=[
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    tooltip="Volver",
                    on_click=lambda e: self.on_back() if self.on_back else None,
                ),
                ft.Icon(ft.Icons.BUSINESS, size=32, color=ft.Colors.BLUE_700),
                ft.Column(
                    controls=[
                        ft.Text(self._company.get("name", ""), size=20, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            ft.Text(self._company.get("trigram", ""), size=14, color=ft.Colors.GREY),
                            self._create_type_badge(),
                            self._create_status_badge(),
                        ], spacing=8)
                    ],
                    spacing=0
                )
            ],
            spacing=16
        )

        # Actions
        actions_grid = ft.GridView(
            max_extent=300,
            child_aspect_ratio=1.5,
            spacing=20,
            run_spacing=20,
        )

        # Cards
        # Cotizaciones
        actions_grid.controls.append(self._create_action_card(
            t("quotes.title"),
            ft.Icons.DESCRIPTION_OUTLINED,
            ft.Colors.ORANGE,
            lambda: self.on_view_quotes(self.company_id, self.company_type) if self.on_view_quotes else None
        ))
        
        # Ordenes
        actions_grid.controls.append(self._create_action_card(
            t("orders.title"),
            ft.Icons.SHOPPING_CART_OUTLINED,
            ft.Colors.GREEN,
            lambda: self.on_view_orders(self.company_id, self.company_type) if self.on_view_orders else None
        ))

        # Entregas
        actions_grid.controls.append(self._create_action_card(
            t("deliveries.title"),
            ft.Icons.LOCAL_SHIPPING_OUTLINED,
            ft.Colors.TEAL,
            lambda: self.on_view_deliveries(self.company_id, self.company_type) if self.on_view_deliveries else None
        ))

        # Facturas
        actions_grid.controls.append(self._create_action_card(
            t("invoices.title"),
            ft.Icons.RECEIPT_LONG_OUTLINED,
            ft.Colors.INDIGO,
            lambda: self.on_view_invoices(self.company_id, self.company_type) if self.on_view_invoices else None
        ))

        # Detalles
        actions_grid.controls.append(self._create_action_card(
            "Ver Detalles",
            ft.Icons.INFO_OUTLINE,
            ft.Colors.BLUE,
            lambda: self.on_view_details(self.company_id, self.company_type) if self.on_view_details else None
        ))

        return ft.Column(
            controls=[
                ft.Container(content=header, padding=ft.padding.only(bottom=20), border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_300))),
                ft.Container(content=actions_grid, expand=True, padding=ft.padding.only(top=20))
            ],
            expand=True
        )

    def _create_action_card(self, title, icon, color, on_click):
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Icon(icon, size=40, color=color),
                    ft.Text(title, size=16, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=20,
                on_click=lambda e: on_click(),
                ink=True,
                border_radius=10
            ),
            elevation=2
        )

    def _create_status_badge(self):
        is_active = self._company.get("is_active", True)
        return ft.Container(
            content=ft.Text(
                t("companies.status.active") if is_active else t("companies.status.inactive"),
                size=10, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD
            ),
            padding=ft.padding.symmetric(horizontal=8, vertical=2),
            bgcolor=ft.Colors.GREEN if is_active else ft.Colors.RED,
            border_radius=20
        )

    def _create_type_badge(self):
        type_code = self._company.get("company_type", "")
        type_map = {
            "CLIENT": t("clients.title"),
            "SUPPLIER": t("suppliers.title"),
            "BOTH": t("companies.title"),
        }
        return ft.Container(
            content=ft.Text(
                type_map.get(type_code, type_code),
                size=10, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD
            ),
            padding=ft.padding.symmetric(horizontal=8, vertical=2),
            bgcolor=ft.Colors.BLUE,
            border_radius=20
        )

    def did_mount(self):
        app_state.theme.add_observer(self._on_state_changed)
        app_state.i18n.add_observer(self._on_state_changed)
        if self.page:
            self.page.run_task(self.load_company)

    def will_unmount(self):
        app_state.theme.remove_observer(self._on_state_changed)
        app_state.i18n.remove_observer(self._on_state_changed)

    def _on_state_changed(self):
        if self.page:
            self.update()

    async def load_company(self):
        self._is_loading = True
        self._error_message = ""
        self.content = self.build()
        if self.page:
            self.update()
            
        try:
            from src.frontend.services.api import CompanyAPI
            company_api = CompanyAPI()
            self._company = await company_api.get_by_id(self.company_id)
            self._is_loading = False
        except Exception as e:
            logger.error(f"Error loading company: {e}")
            self._error_message = str(e)
            self._is_loading = False
            
        self.content = self.build()
        if self.page:
            self.update()
