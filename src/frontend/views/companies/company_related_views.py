"""
Vistas relacionadas a una empresa (Cotizaciones, Órdenes, Entregas, Facturas).
"""
import flet as ft
from loguru import logger
from typing import Callable

from src.frontend.app_state import app_state
from src.frontend.layout_constants import LayoutConstants
from src.frontend.components.common import LoadingSpinner, ErrorDisplay
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
            
            # Aquí se podrían cargar los datos específicos (cotizaciones, ordenes, etc.)
            # self._items = await service.get_by_company(self.company_id)
            
            self._is_loading = False
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            self._error_message = str(e)
            self._is_loading = False
            
        self.content = self.build()
        if self.page:
            self.update()


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
