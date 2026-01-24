"""
Navegador de Órdenes (Orders).

Maneja toda la navegación relacionada con órdenes.
"""
from typing import TYPE_CHECKING
from loguru import logger

from src.frontend.navigation.base_navigator import BaseNavigator

if TYPE_CHECKING:
    from src.frontend.views.main_view import MainView


class OrderNavigator(BaseNavigator):
    """
    Navegador especializado para órdenes.
    
    Maneja navegación a:
    - Lista de órdenes
    - Detalle de orden
    - Formulario de orden (crear/editar)
    """
    
    def __init__(self, main_view: "MainView"):
        super().__init__(main_view)
        
    def navigate_to_list(self) -> None:
        """Navega a la lista de órdenes."""
        logger.info("Navigating to order list")
        self._navigate_to_index(6)
        
    def navigate_to_detail(
        self,
        company_id: int,
        company_type: str,
        order_id: int,
        from_order_list: bool = False,
    ) -> None:
        """
        Navega a la vista de detalle de orden.
        
        Args:
            company_id: ID de la empresa asociada
            company_type: Tipo de empresa ("CLIENT" o "SUPPLIER")
            order_id: ID de la orden
            from_order_list: Si viene desde la lista de órdenes del menú principal
        """
        from src.frontend.views.orders.order_detail_view import OrderDetailView
        
        logger.info(f"Navigating to order detail: company_id={company_id}, order_id={order_id}, from_order_list={from_order_list}")
        
        # Determinar la acción de "volver" según el contexto
        if from_order_list:
            on_back = lambda: self.navigate_to_list()
        else:
            on_back = lambda: self.main_view.company_navigator.navigate_to_orders(company_id, company_type)
        
        detail_view = OrderDetailView(
            order_id=order_id,
            company_id=company_id,
            company_type=company_type,
            on_edit=lambda oid: self.navigate_to_form(company_id, company_type, order_id=oid, from_order_list=from_order_list),
            on_delete=lambda oid: self._on_deleted(oid, company_id, company_type, from_order_list=from_order_list),
            on_back=on_back,
        )
        
        self._update_content(detail_view)
        
        # Configurar breadcrumb según el contexto
        if from_order_list:
            # Viene desde el menú de órdenes
            self._set_breadcrumb([
                {"label": "orders.title", "route": "/orders"},
                {"label": "orders.detail", "route": None},
            ])
        else:
            # Viene desde el dashboard/órdenes de un cliente
            section_key = "clients" if company_type == "CLIENT" else "suppliers"
            dashboard_route = f"/companies/dashboard/{company_id}/{company_type}"
            orders_route = f"{dashboard_route}/orders"
            
            self._set_breadcrumb([
                {"label": f"{section_key}.title", "route": f"/companies/{company_type.lower()}s"},
                {"label": "dashboard.title", "route": dashboard_route},
                {"label": "orders.title", "route": orders_route},
                {"label": "orders.detail", "route": None},
            ])
            
    def navigate_to_form(
        self,
        company_id: int,
        company_type: str,
        quote_id: int | None = None,
        order_id: int | None = None,
        from_order_list: bool = False,
    ) -> None:
        """
        Navega a la vista de formulario de orden.
        
        Args:
            company_id: ID de la empresa
            company_type: Tipo de empresa
            quote_id: ID de la cotización (si se crea desde cotización)
            order_id: ID de la orden (None para crear nueva)
            from_order_list: Si viene desde la lista de órdenes del menú principal
        """
        from src.frontend.views.orders.order_form_view import OrderFormView
        
        logger.info(
            f"Navigating to order form: company_id={company_id}, quote_id={quote_id}, "
            f"order_id={order_id}, from_order_list={from_order_list}, mode={'edit' if order_id else 'create'}"
        )
        
        # Determinar acciones de guardar/cancelar según el contexto
        if from_order_list:
            on_save = lambda: self.navigate_to_list()
            on_cancel = lambda: self.navigate_to_list()
        else:
            on_save = lambda: self.main_view.company_navigator.navigate_to_orders(company_id, company_type)
            on_cancel = lambda: self.main_view.company_navigator.navigate_to_orders(company_id, company_type)
        
        form_view = OrderFormView(
            company_id=company_id,
            quote_id=quote_id,
            order_id=order_id,
            on_save=on_save,
            on_cancel=on_cancel,
        )
        
        self._update_content(form_view)
        
        # Configurar breadcrumb según el contexto
        action_key = "orders.edit" if order_id else "orders.create"
        
        if from_order_list:
            # Viene desde el menú de órdenes
            self._set_breadcrumb([
                {"label": "orders.title", "route": "/orders"},
                {"label": action_key, "route": None},
            ])
        else:
            # Viene desde el dashboard/órdenes de un cliente
            section_key = "clients" if company_type == "CLIENT" else "suppliers"
            dashboard_route = f"/companies/dashboard/{company_id}/{company_type}"
            
            self._set_breadcrumb([
                {"label": f"{section_key}.title", "route": f"/companies/{company_type.lower()}s"},
                {"label": "dashboard.title", "route": dashboard_route},
                {"label": "orders.title", "route": f"{dashboard_route}/orders"},
                {"label": action_key, "route": None},
            ])
            
    def _on_deleted(
        self,
        order_id: int,
        company_id: int,
        company_type: str,
        from_order_list: bool = False,
    ) -> None:
        """Callback cuando se elimina una orden desde el detalle."""
        logger.success(f"Order deleted: {order_id}")
        if from_order_list:
            self.navigate_to_list()
        else:
            self.main_view.company_navigator.navigate_to_orders(company_id, company_type)
