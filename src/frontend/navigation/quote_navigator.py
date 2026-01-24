"""
Navegador de Cotizaciones (Quotes).

Maneja toda la navegación relacionada con cotizaciones.
"""
from typing import TYPE_CHECKING
from loguru import logger

from src.frontend.navigation.base_navigator import BaseNavigator

if TYPE_CHECKING:
    from src.frontend.views.main_view import MainView


class QuoteNavigator(BaseNavigator):
    """
    Navegador especializado para cotizaciones.
    
    Maneja navegación a:
    - Lista de cotizaciones
    - Detalle de cotización
    - Formulario de cotización (crear/editar)
    - Productos de cotización
    """
    
    def __init__(self, main_view: "MainView"):
        super().__init__(main_view)
        
    def navigate_to_list(self) -> None:
        """Navega a la lista de cotizaciones."""
        logger.info("Navigating to quote list")
        self._navigate_to_index(5)
        
    def navigate_to_detail(
        self,
        company_id: int,
        company_type: str,
        quote_id: int,
        from_quote_list: bool = False,
    ) -> None:
        """
        Navega a la vista de detalle de cotización.
        
        Args:
            company_id: ID de la empresa asociada
            company_type: Tipo de empresa ("CLIENT" o "SUPPLIER")
            quote_id: ID de la cotización
            from_quote_list: Si viene desde la lista de cotizaciones del menú principal
        """
        from src.frontend.views.quotes.quote_detail_view import QuoteDetailView
        
        logger.info(f"Navigating to quote detail: company_id={company_id}, quote_id={quote_id}, from_quote_list={from_quote_list}")
        
        # Determinar la acción de "volver" según el contexto
        if from_quote_list:
            on_back = lambda: self.navigate_to_list()
        else:
            on_back = lambda: self.main_view.company_navigator.navigate_to_quotes(company_id, company_type)
        
        detail_view = QuoteDetailView(
            quote_id=quote_id,
            company_id=company_id,
            company_type=company_type,
            on_edit=lambda qid: self.navigate_to_form(company_id, company_type, qid, from_quote_list=from_quote_list),
            on_delete=lambda qid: self._on_deleted(qid, company_id, company_type, from_quote_list=from_quote_list),
            on_create_order=lambda qid: self.main_view.order_navigator.navigate_to_form(company_id, company_type, qid),
            on_add_products=lambda qid: self.navigate_to_products(company_id, company_type, qid, from_quote_list=from_quote_list),
            on_back=on_back,
        )
        
        self._update_content(detail_view)
        
        # Configurar breadcrumb según el contexto
        if from_quote_list:
            # Viene desde el menú de cotizaciones
            self._set_breadcrumb([
                {"label": "quotes.title", "route": "/quotes"},
                {"label": "quotes.detail", "route": None},
            ])
        else:
            # Viene desde el dashboard/cotizaciones de un cliente
            section_key = "clients" if company_type == "CLIENT" else "suppliers"
            dashboard_route = f"/companies/dashboard/{company_id}/{company_type}"
            quotes_route = f"{dashboard_route}/quotes"
            
            self._set_breadcrumb([
                {"label": f"{section_key}.title", "route": f"/companies/{company_type.lower()}s"},
                {"label": "dashboard.title", "route": dashboard_route},
                {"label": "quotes.title", "route": quotes_route},
                {"label": "quotes.detail", "route": None},
            ])
            
    def navigate_to_form(
        self,
        company_id: int,
        company_type: str,
        quote_id: int | None = None,
        from_quote_list: bool = False,
    ) -> None:
        """
        Navega a la vista de formulario de cotización.
        
        Args:
            company_id: ID de la empresa
            company_type: Tipo de empresa
            quote_id: ID de la cotización (None para crear nueva)
            from_quote_list: Si viene desde la lista de cotizaciones del menú principal
        """
        from src.frontend.views.quotes.quote_form_view import QuoteFormView
        
        logger.info(
            f"Navigating to quote form: company_id={company_id}, quote_id={quote_id}, "
            f"mode={'edit' if quote_id else 'create'}"
        )
        
        # Determinar acciones según el contexto
        if from_quote_list:
            on_save = lambda: self.navigate_to_list()
            on_cancel = lambda: self.navigate_to_list()
        else:
            on_save = lambda: self.main_view.company_navigator.navigate_to_quotes(company_id, company_type)
            on_cancel = lambda: self.main_view.company_navigator.navigate_to_quotes(company_id, company_type)
        
        form_view = QuoteFormView(
            company_id=company_id,
            quote_id=quote_id,
            on_save=on_save,
            on_cancel=on_cancel,
        )
        
        self._update_content(form_view)
        
        action_key = "quotes.edit" if quote_id else "quotes.create"
        
        # Configurar breadcrumb según el contexto
        if from_quote_list:
            # Viene desde el menú de cotizaciones
            self._set_breadcrumb([
                {"label": "quotes.title", "route": "/quotes"},
                {"label": action_key, "route": None},
            ])
        else:
            # Viene desde el dashboard/cotizaciones de un cliente
            section_key = "clients" if company_type == "CLIENT" else "suppliers"
            dashboard_route = f"/companies/dashboard/{company_id}/{company_type}"
            quotes_route = f"{dashboard_route}/quotes"
            
            self._set_breadcrumb([
                {"label": f"{section_key}.title", "route": f"/companies/{company_type.lower()}s"},
                {"label": "dashboard.title", "route": dashboard_route},
                {"label": "quotes.title", "route": quotes_route},
                {"label": action_key, "route": None},
            ])
            
    def navigate_to_products(
        self,
        company_id: int,
        company_type: str,
        quote_id: int,
        from_quote_list: bool = False,
    ) -> None:
        """
        Navega a la vista de agregar productos a una cotización.
        
        Args:
            company_id: ID de la empresa
            company_type: Tipo de empresa
            quote_id: ID de la cotización
            from_quote_list: Si viene desde la lista de cotizaciones del menú principal
        """
        from src.frontend.views.quotes.quote_products_view import QuoteProductsView
        
        logger.info(f"Navigating to quote products: company_id={company_id}, quote_id={quote_id}")
        
        products_view = QuoteProductsView(
            quote_id=quote_id,
            company_id=company_id,
            company_type=company_type,
            on_back=lambda: self.navigate_to_detail(company_id, company_type, quote_id, from_quote_list=from_quote_list),
            on_product_added=lambda: self.navigate_to_detail(company_id, company_type, quote_id, from_quote_list=from_quote_list),
        )
        
        self._update_content(products_view)
        
        # Configurar breadcrumb según el contexto
        if from_quote_list:
            # Viene desde el menú de cotizaciones
            self._set_breadcrumb([
                {"label": "quotes.title", "route": "/quotes"},
                {"label": "quotes.detail", "route": None},
                {"label": "quotes.add_products", "route": None},
            ])
        else:
            # Viene desde el dashboard/cotizaciones de un cliente
            section_key = "clients" if company_type == "CLIENT" else "suppliers"
            dashboard_route = f"/companies/dashboard/{company_id}/{company_type}"
            quotes_route = f"{dashboard_route}/quotes"
            
            self._set_breadcrumb([
                {"label": f"{section_key}.title", "route": f"/companies/{company_type.lower()}s"},
                {"label": "dashboard.title", "route": dashboard_route},
                {"label": "quotes.title", "route": quotes_route},
                {"label": "quotes.detail", "route": f"{quotes_route}/{quote_id}"},
                {"label": "quotes.add_products", "route": None},
            ])
            
    def _on_deleted(
        self,
        quote_id: int,
        company_id: int,
        company_type: str,
        from_quote_list: bool = False,
    ) -> None:
        """Callback cuando se elimina una cotización desde el detalle."""
        logger.success(f"Quote deleted: {quote_id}")
        if from_quote_list:
            self.navigate_to_list()
        else:
            self.main_view.company_navigator.navigate_to_quotes(company_id, company_type)
