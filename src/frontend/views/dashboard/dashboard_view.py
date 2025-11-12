"""
Vista del Dashboard principal.

Muestra métricas clave, KPIs y actividad reciente del sistema.
"""
import flet as ft
from loguru import logger

from src.frontend.app_state import app_state
from src.frontend.layout_constants import LayoutConstants
from src.frontend.components.charts import KPICard
from src.frontend.components.common import LoadingSpinner, ErrorDisplay


class DashboardView(ft.Container):
    """
    Vista del Dashboard con métricas y KPIs.

    Muestra información resumida del sistema:
    - Total de empresas
    - Total de productos
    - Cotizaciones activas
    - Pedidos totales
    - Actividad reciente

    Example:
        >>> dashboard = DashboardView()
        >>> page.add(dashboard)
    """

    def __init__(self):
        """Inicializa la vista del dashboard."""
        super().__init__()

        # Estado
        self._is_loading: bool = True
        self._error_message: str = ""
        self._dashboard_data: dict | None = None

        # KPI Cards
        self._companies_kpi: KPICard | None = None
        self._products_kpi: KPICard | None = None
        self._quotes_kpi: KPICard | None = None
        self._orders_kpi: KPICard | None = None

        logger.info("DashboardView initialized")

    def build(self) -> ft.Control:
        """
        Construye el componente del dashboard.

        Returns:
            Control de Flet con el dashboard completo
        """
        # Header
        header = ft.Text(
            "Bienvenido a AK Group",
            size=LayoutConstants.FONT_SIZE_DISPLAY_MD,
            weight=LayoutConstants.FONT_WEIGHT_BOLD,
        )

        # Crear KPI Cards
        self._companies_kpi = KPICard(
            icon=ft.Icons.BUSINESS,
            label="Total Empresas",
            value=0,
            trend="neutral",
        )

        self._products_kpi = KPICard(
            icon=ft.Icons.INVENTORY_2,
            label="Total Productos",
            value=0,
            trend="neutral",
        )

        self._quotes_kpi = KPICard(
            icon=ft.Icons.DESCRIPTION,
            label="Cotizaciones Activas",
            value=0,
            trend="neutral",
        )

        self._orders_kpi = KPICard(
            icon=ft.Icons.SHOPPING_CART,
            label="Pedidos Totales",
            value=0,
            trend="neutral",
        )

        # Fila de KPIs
        kpi_row = ft.Row(
            controls=[
                ft.Container(
                    content=self._companies_kpi,
                    expand=1,
                ),
                ft.Container(
                    content=self._products_kpi,
                    expand=1,
                ),
                ft.Container(
                    content=self._quotes_kpi,
                    expand=1,
                ),
                ft.Container(
                    content=self._orders_kpi,
                    expand=1,
                ),
            ],
            spacing=LayoutConstants.SPACING_MD,
            wrap=True,
        )

        # Sección de actividad reciente (placeholder)
        activity_section = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Actividad Reciente",
                        size=LayoutConstants.FONT_SIZE_XL,
                        weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                    ),
                    ft.Container(
                        content=ft.Text(
                            "No hay actividad reciente para mostrar",
                            size=LayoutConstants.FONT_SIZE_MD,
                        ),
                        padding=LayoutConstants.PADDING_XL,
                        alignment=ft.alignment.center,
                        border_radius=LayoutConstants.RADIUS_MD,
                    ),
                ],
                spacing=LayoutConstants.SPACING_MD,
            ),
            margin=ft.margin.only(top=LayoutConstants.SPACING_XL),
        )

        # Contenido principal
        content = ft.Column(
            controls=[
                header,
                kpi_row,
                activity_section,
            ],
            spacing=LayoutConstants.SPACING_LG,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        # Contenedor con estados
        if self._is_loading:
            return ft.Container(
                content=LoadingSpinner(
                    message="Cargando dashboard...",
                ),
                expand=True,
                alignment=ft.alignment.center,
            )
        elif self._error_message:
            return ft.Container(
                content=ErrorDisplay(
                    message=self._error_message,
                    on_retry=self.load_dashboard_data,
                ),
                expand=True,
                alignment=ft.alignment.center,
            )
        else:
            return content

    def did_mount(self) -> None:
        """
        Lifecycle: Se ejecuta cuando el componente se monta.

        Carga los datos del dashboard desde las APIs.
        """
        logger.info("DashboardView mounted, loading data")

        # Suscribirse a cambios de tema e idioma
        app_state.theme.add_observer(self._on_state_changed)
        app_state.i18n.add_observer(self._on_state_changed)

        # Cargar datos (async)
        if self.page:
            self.page.run_task(self.load_dashboard_data)

    def will_unmount(self) -> None:
        """
        Lifecycle: Se ejecuta cuando el componente se desmonta.

        Limpia los observers.
        """
        logger.info("DashboardView unmounting")
        app_state.theme.remove_observer(self._on_state_changed)
        app_state.i18n.remove_observer(self._on_state_changed)

    async def load_dashboard_data(self) -> None:
        """
        Carga los datos del dashboard desde las APIs.

        Obtiene contadores de empresas, productos, cotizaciones y pedidos.
        """
        logger.info("Loading dashboard data")
        self._is_loading = True
        self._error_message = ""

        if self.page:
            self.update()

        try:
            # Importar APIs
            from src.frontend.services.api import CompanyAPI, ProductAPI

            # Crear instancias de APIs
            company_api = CompanyAPI()
            product_api = ProductAPI()

            # Cargar datos en paralelo
            logger.debug("Fetching companies count")
            companies_response = await company_api.get_all(page=1, page_size=1)
            companies_count = companies_response.get("total", 0)

            logger.debug("Fetching products count")
            products_response = await product_api.get_all(page=1, page_size=1)
            products_count = products_response.get("total", 0)

            # TODO: Implementar APIs de cotizaciones y pedidos
            quotes_count = 0
            orders_count = 0

            # Actualizar KPIs
            if self._companies_kpi:
                self._companies_kpi.update_value(companies_count)

            if self._products_kpi:
                self._products_kpi.update_value(products_count)

            if self._quotes_kpi:
                self._quotes_kpi.update_value(quotes_count)

            if self._orders_kpi:
                self._orders_kpi.update_value(orders_count)

            logger.success(
                f"Dashboard data loaded: {companies_count} companies, "
                f"{products_count} products, {quotes_count} quotes, {orders_count} orders"
            )

            self._is_loading = False

        except Exception as e:
            logger.exception(f"Error loading dashboard data: {e}")
            self._error_message = f"Error al cargar datos del dashboard: {str(e)}"
            self._is_loading = False

        if self.page:
            self.update()

    def _on_state_changed(self) -> None:
        """
        Observer: Se ejecuta cuando cambia el estado de tema o idioma.

        Actualiza la interfaz.
        """
        logger.debug("State changed, updating DashboardView")
        if self.page:
            self.update()

    def refresh(self) -> None:
        """
        Refresca los datos del dashboard.

        Example:
            >>> dashboard.refresh()
        """
        logger.info("Refreshing dashboard data")
        if self.page:
            self.page.run_task(self.load_dashboard_data)
