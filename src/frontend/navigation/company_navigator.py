"""
Navegador de Empresas (Companies).

Maneja toda la navegación relacionada con clientes y proveedores.
"""
from typing import TYPE_CHECKING
from loguru import logger

from src.frontend.navigation.base_navigator import BaseNavigator

if TYPE_CHECKING:
    from src.frontend.views.main_view import MainView


class CompanyNavigator(BaseNavigator):
    """
    Navegador especializado para empresas (clientes y proveedores).
    
    Maneja navegación a:
    - Lista de empresas
    - Detalle de empresa
    - Formulario de empresa
    - Dashboard de empresa
    - Cotizaciones de empresa
    - Órdenes de empresa
    - Entregas de empresa
    - Facturas de empresa
    """
    
    def __init__(self, main_view: "MainView"):
        super().__init__(main_view)
        
    def navigate_to_list(self, company_type: str = "CLIENT") -> None:
        """
        Navega a la lista de empresas.
        
        Args:
            company_type: Tipo de empresa ("CLIENT" o "SUPPLIER")
        """
        logger.info(f"Navigating to company list: type={company_type}")
        index = 1 if company_type == "CLIENT" else 2
        self._navigate_to_index(index)
        
    def navigate_to_detail(
        self,
        company_id: int,
        company_type: str = "CLIENT",
        from_dashboard: bool = False,
    ) -> None:
        """
        Navega a la vista de detalle de una empresa.
        
        Args:
            company_id: ID de la empresa
            company_type: Tipo de empresa ("CLIENT" o "SUPPLIER")
            from_dashboard: Si viene del dashboard
        """
        from src.frontend.views.companies.company_detail_view import CompanyDetailView
        
        logger.info(f"Navigating to company detail: ID={company_id}, type={company_type}")
        
        # Determine back action
        if from_dashboard:
            on_back = lambda: self.navigate_to_dashboard(company_id, company_type)
        else:
            on_back = lambda: self.navigate_to_list(company_type)
        
        # Crear vista de detalle
        detail_view = CompanyDetailView(
            company_id=company_id,
            on_edit=lambda cid: self.navigate_to_form(cid, company_type),
            on_delete=lambda cid: self._on_deleted(cid, company_type),
            on_back=on_back,
        )
        
        # Actualizar contenido
        self._update_content(detail_view)
        
        # Actualizar breadcrumb
        section_key = "clients" if company_type == "CLIENT" else "suppliers"
        breadcrumb = [
            {"label": f"{section_key}.title", "route": f"/companies/{company_type.lower()}s"},
        ]
        
        if from_dashboard:
            dashboard_route = f"/companies/dashboard/{company_id}/{company_type}"
            breadcrumb.append({"label": "dashboard.title", "route": dashboard_route})
            
        breadcrumb.append({"label": f"{section_key}.detail", "route": None})
        
        self._set_breadcrumb(breadcrumb)
        
    def navigate_to_form(
        self,
        company_id: int | None = None,
        company_type: str = "CLIENT",
    ) -> None:
        """
        Navega a la vista de formulario de empresa (crear/editar).
        
        Args:
            company_id: ID de la empresa a editar (None para crear)
            company_type: Tipo de empresa ("CLIENT" o "SUPPLIER")
        """
        from src.frontend.views.companies.company_form_view import CompanyFormView
        
        logger.info(
            f"Navigating to company form: ID={company_id}, type={company_type}, "
            f"mode={'edit' if company_id else 'create'}"
        )
        
        # Crear vista de formulario
        form_view = CompanyFormView(
            company_id=company_id,
            default_type=company_type,
            on_save=lambda company: self._on_saved(company, company_type),
            on_cancel=lambda: self.navigate_to_list(company_type),
        )
        
        # Actualizar contenido
        self._update_content(form_view)
        
        # Actualizar breadcrumb
        section_key = "clients" if company_type == "CLIENT" else "suppliers"
        action_key = f"{section_key}.edit" if company_id else f"{section_key}.create"
        self._set_breadcrumb([
            {"label": f"{section_key}.title", "route": f"/companies/{company_type.lower()}s"},
            {"label": action_key, "route": None},
        ])
        
    def navigate_to_dashboard(
        self,
        company_id: int,
        company_type: str = "CLIENT",
    ) -> None:
        """
        Navega al dashboard de una empresa.
        
        Args:
            company_id: ID de la empresa
            company_type: Tipo de empresa ("CLIENT" o "SUPPLIER")
        """
        from src.frontend.views.companies.company_dashboard_view import CompanyDashboardView
        
        logger.info(f"Navigating to company dashboard: ID={company_id}")
        
        dashboard_view = CompanyDashboardView(
            company_id=company_id,
            company_type=company_type,
            on_view_details=lambda cid, ctype: self.navigate_to_detail(cid, ctype, from_dashboard=True),
            on_back=lambda: self.navigate_to_list(company_type),
            on_view_quotes=self.navigate_to_quotes,
            on_view_orders=self.navigate_to_orders,
            on_view_deliveries=self.navigate_to_deliveries,
            on_view_invoices=self.navigate_to_invoices,
        )
        
        self._update_content(dashboard_view)
        
        section_key = "clients" if company_type == "CLIENT" else "suppliers"
        dashboard_route = f"/companies/dashboard/{company_id}/{company_type}"
        self._set_breadcrumb([
            {"label": f"{section_key}.title", "route": f"/companies/{company_type.lower()}s"},
            {"label": "dashboard.title", "route": dashboard_route},
        ])
        
    def navigate_to_quotes(self, company_id: int, company_type: str) -> None:
        """Navega a la vista de cotizaciones de una empresa."""
        from src.frontend.views.companies.company_related_views import CompanyQuotesView
        
        logger.info(f"Navigating to quotes for company {company_id}")
        
        view = CompanyQuotesView(
            company_id=company_id,
            company_type=company_type,
            on_back=lambda: self.navigate_to_dashboard(company_id, company_type),
            on_create_quote=lambda: self.main_view.quote_navigator.navigate_to_form(company_id, company_type),
            on_edit_quote=lambda quote_id: self.main_view.quote_navigator.navigate_to_form(company_id, company_type, quote_id),
            on_view_quote=lambda quote_id: self.main_view.quote_navigator.navigate_to_detail(company_id, company_type, quote_id),
        )
        
        self._update_content(view)
        
        section_key = "clients" if company_type == "CLIENT" else "suppliers"
        dashboard_route = f"/companies/dashboard/{company_id}/{company_type}"
        quotes_route = f"{dashboard_route}/quotes"
        
        self._set_breadcrumb([
            {"label": f"{section_key}.title", "route": f"/companies/{company_type.lower()}s"},
            {"label": "dashboard.title", "route": dashboard_route},
            {"label": "quotes.title", "route": quotes_route},
        ])
        
    def navigate_to_orders(self, company_id: int, company_type: str) -> None:
        """Navega a la vista de órdenes de una empresa."""
        from src.frontend.views.companies.company_related_views import CompanyOrdersView
        
        logger.info(f"Navigating to orders for company {company_id}")
        
        view = CompanyOrdersView(
            company_id=company_id,
            company_type=company_type,
            on_back=lambda: self.navigate_to_dashboard(company_id, company_type),
            on_view_order=lambda order_id: self.main_view.order_navigator.navigate_to_detail(company_id, company_type, order_id),
            on_create_order=lambda: self.main_view.order_navigator.navigate_to_form(company_id=company_id, company_type=company_type),
            on_edit_order=lambda order_id: self.main_view.order_navigator.navigate_to_form(company_id=company_id, company_type=company_type, order_id=order_id),
        )
        
        self._update_content(view)
        
        section_key = "clients" if company_type == "CLIENT" else "suppliers"
        dashboard_route = f"/companies/dashboard/{company_id}/{company_type}"
        
        self._set_breadcrumb([
            {"label": f"{section_key}.title", "route": f"/companies/{company_type.lower()}s"},
            {"label": "dashboard.title", "route": dashboard_route},
            {"label": "orders.title", "route": None},
        ])
        
    def navigate_to_deliveries(self, company_id: int, company_type: str) -> None:
        """Navega a la vista de entregas de una empresa."""
        from src.frontend.views.companies.company_related_views import CompanyDeliveriesView
        
        logger.info(f"Navigating to deliveries for company {company_id}")
        
        view = CompanyDeliveriesView(
            company_id=company_id,
            company_type=company_type,
            on_back=lambda: self.navigate_to_dashboard(company_id, company_type)
        )
        
        self._update_content(view)
        
        section_key = "clients" if company_type == "CLIENT" else "suppliers"
        dashboard_route = f"/companies/dashboard/{company_id}/{company_type}"
        
        self._set_breadcrumb([
            {"label": f"{section_key}.title", "route": f"/companies/{company_type.lower()}s"},
            {"label": "dashboard.title", "route": dashboard_route},
            {"label": "deliveries.title", "route": None},
        ])
        
    def navigate_to_invoices(self, company_id: int, company_type: str) -> None:
        """Navega a la vista de facturas de una empresa."""
        from src.frontend.views.companies.company_related_views import CompanyInvoicesView
        
        logger.info(f"Navigating to invoices for company {company_id}")
        
        view = CompanyInvoicesView(
            company_id=company_id,
            company_type=company_type,
            on_back=lambda: self.navigate_to_dashboard(company_id, company_type)
        )
        
        self._update_content(view)
        
        section_key = "clients" if company_type == "CLIENT" else "suppliers"
        dashboard_route = f"/companies/dashboard/{company_id}/{company_type}"
        
        self._set_breadcrumb([
            {"label": f"{section_key}.title", "route": f"/companies/{company_type.lower()}s"},
            {"label": "dashboard.title", "route": dashboard_route},
            {"label": "invoices.title", "route": None},
        ])
        
    def _on_saved(self, company: dict, company_type: str) -> None:
        """
        Callback cuando se guarda una empresa exitosamente.
        
        Args:
            company: Datos de la empresa guardada
            company_type: Tipo de empresa
        """
        logger.success(f"Company saved: {company.get('name')}")
        self.navigate_to_list(company_type)
        
    def _on_deleted(self, company_id: int, company_type: str) -> None:
        """
        Callback cuando se elimina una empresa.
        
        Args:
            company_id: ID de la empresa eliminada
            company_type: Tipo de empresa
        """
        logger.success(f"Company deleted: ID={company_id}")
        self.navigate_to_list(company_type)
