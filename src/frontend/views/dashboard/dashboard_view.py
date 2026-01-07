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
    - Total de clientes
    - Total de proveedores
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
        self._clients_kpi: KPICard | None = None
        self._providers_kpi: KPICard | None = None
        self._products_kpi: KPICard | None = None
        self._quotes_kpi: KPICard | None = None
        self._orders_kpi: KPICard | None = None

        # Configurar propiedades del contenedor
        self.expand = True
        self.padding = 0

        # Construir contenido inicial
        self.content = self.build()

        logger.info("DashboardView initialized")

    def build(self) -> ft.Control:
        """
        Construye el componente del dashboard.

        Returns:
            Control de Flet con el dashboard completo
        """
        # Estados de carga/error
        if self._is_loading:
            return ft.Container(
                content=LoadingSpinner(message="Cargando dashboard..."),
                expand=True,
                alignment=ft.Alignment(0, 0),  # center
            )

        if self._error_message:
            return ft.Container(
                content=ErrorDisplay(
                    message=self._error_message,
                    on_retry=self.load_dashboard_data,
                ),
                expand=True,
                alignment=ft.Alignment(0, 0),  # center
            )

        # Contenido principal
        # Header
        header = ft.Text(
            "Bienvenido a AK Group",
            size=LayoutConstants.FONT_SIZE_DISPLAY_MD,
            weight=LayoutConstants.FONT_WEIGHT_BOLD,
        )

        # Crear KPI Cards con datos si están disponibles
        clients_count = self._dashboard_data.get("clients_count", 0) if self._dashboard_data else 0
        providers_count = self._dashboard_data.get("providers_count", 0) if self._dashboard_data else 0
        products_count = self._dashboard_data.get("products_count", 0) if self._dashboard_data else 0
        quotes_count = self._dashboard_data.get("quotes_count", 0) if self._dashboard_data else 0
        orders_count = self._dashboard_data.get("orders_count", 0) if self._dashboard_data else 0

        self._clients_kpi = KPICard(
            icon=ft.Icons.PEOPLE,
            label="Total Clientes",
            value=clients_count,
            trend="neutral",
        )

        self._providers_kpi = KPICard(
            icon=ft.Icons.LOCAL_SHIPPING,
            label="Total Proveedores",
            value=providers_count,
            trend="neutral",
        )

        self._products_kpi = KPICard(
            icon=ft.Icons.INVENTORY_2,
            label="Total Productos",
            value=products_count,
            trend="neutral",
        )

        self._quotes_kpi = KPICard(
            icon=ft.Icons.DESCRIPTION,
            label="Cotizaciones Activas",
            value=quotes_count,
            trend="neutral",
        )

        self._orders_kpi = KPICard(
            icon=ft.Icons.SHOPPING_CART,
            label="Pedidos Totales",
            value=orders_count,
            trend="neutral",
        )

        # Fila de KPIs principales (Clientes y Proveedores)
        main_kpi_row = ft.Row(
            controls=[
                ft.Container(
                    content=self._clients_kpi,
                    expand=1,
                ),
                ft.Container(
                    content=self._providers_kpi,
                    expand=1,
                ),
            ],
            spacing=LayoutConstants.SPACING_MD,
        )

        # Fila secundaria (Productos, Cotizaciones, Pedidos)
        secondary_kpi_row = ft.Row(
            controls=[
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
                        alignment=ft.Alignment(0, 0),  # center
                        border_radius=LayoutConstants.RADIUS_MD,
                    ),
                ],
                spacing=LayoutConstants.SPACING_MD,
            ),
            margin=ft.margin.only(top=LayoutConstants.SPACING_XL),
        )

        # Retornar contenido
        return ft.Container(
            content=ft.Column(
                controls=[
                    header,
                    ft.Container(height=10),  # Espacio pequeño
                    main_kpi_row,
                    ft.Container(height=10),  # Espacio pequeño
                    secondary_kpi_row,
                    activity_section,
                ],
                spacing=0,
                scroll=ft.ScrollMode.AUTO,
            ),
            expand=True,
            padding=LayoutConstants.PADDING_LG,
        )

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

        # Reconstruir contenido para mostrar loading
        self.content = self.build()
        if self.page:
            self.update()

        try:
            # Importar APIs
            from src.frontend.services.api import CompanyAPI, ProductAPI

            # Crear instancias de APIs
            company_api = CompanyAPI()
            product_api = ProductAPI()

            # Inicializar contadores
            clients_count = 0
            providers_count = 0
            products_count = 0

            # Cargar datos con manejo de errores
            try:
                logger.debug("Fetching clients count (company_type_id=1)")
                clients_response = await company_api.get_all(skip=0, limit=1000, company_type_id=1)
                clients_count = clients_response.get("total", 0)
            except Exception as e:
                logger.warning(f"Error fetching clients: {e}")
                clients_count = 0

            try:
                logger.debug("Fetching providers count (company_type_id=2)")
                providers_response = await company_api.get_all(skip=0, limit=1000, company_type_id=2)
                providers_count = providers_response.get("total", 0)
            except Exception as e:
                logger.warning(f"Error fetching providers: {e}")
                providers_count = 0

            try:
                logger.debug("Fetching products count")
                products_response = await product_api.get_all(skip=0, limit=1000)
                products_count = products_response.get("total", 0)
            except Exception as e:
                logger.warning(f"Error fetching products: {e}")
                products_count = 0

            # TODO: Implementar APIs de cotizaciones y pedidos
            quotes_count = 0
            orders_count = 0

            # Guardar datos en el estado
            self._dashboard_data = {
                "clients_count": clients_count,
                "providers_count": providers_count,
                "products_count": products_count,
                "quotes_count": quotes_count,
                "orders_count": orders_count,
            }

            logger.success(
                f"Dashboard data loaded: {clients_count} clients, "
                f"{providers_count} providers, {products_count} products, "
                f"{quotes_count} quotes, {orders_count} orders"
            )

            self._is_loading = False

        except Exception as e:
            logger.exception(f"Error loading dashboard data: {e}")
            self._error_message = f"Error al cargar datos del dashboard: {str(e)}"
            self._is_loading = False

        # Reconstruir contenido con los datos cargados o error
        self.content = self.build()
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
