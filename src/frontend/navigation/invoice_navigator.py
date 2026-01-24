"""
Navegador de Facturas (Invoices).

Maneja toda la navegación relacionada con facturas.
"""
from typing import TYPE_CHECKING
from loguru import logger

from src.frontend.navigation.base_navigator import BaseNavigator

if TYPE_CHECKING:
    from src.frontend.views.main_view import MainView


class InvoiceNavigator(BaseNavigator):
    """
    Navegador especializado para facturas.
    
    Maneja navegación a:
    - Lista de órdenes (punto de entrada desde menú)
    - Lista de facturas por orden
    - Detalle de factura
    """
    
    def __init__(self, main_view: "MainView"):
        super().__init__(main_view)
        
    def navigate_to_orders(self) -> None:
        """
        Navega a la lista de órdenes (vista principal de facturas).
        
        Según el requerimiento, la vista de facturas muestra primero
        las órdenes y al seleccionar una, se muestran las facturas de esa orden.
        """
        from src.frontend.views.orders.order_list_view import OrderListView
        
        logger.info("Navigating to orders (invoice entry point)")
        
        # Crear vista de órdenes con callback para ver facturas
        list_view = OrderListView(
            on_view_detail=lambda oid, cid, ctype: self.navigate_to_invoice_list_for_order(oid, cid, ctype),
            on_create=None,  # No se permite crear desde aquí
            on_edit=None,  # No se permite editar desde aquí
        )
        
        self._update_content(list_view)
        self._set_breadcrumb([
            {"label": "invoices.title", "route": "/invoices"},
        ])
        
    def navigate_to_invoice_list_for_order(
        self,
        order_id: int,
        company_id: int,
        company_type: str,
    ) -> None:
        """
        Navega a la lista de facturas de una orden específica.
        
        Args:
            order_id: ID de la orden
            company_id: ID de la empresa (para contexto)
            company_type: Tipo de empresa (para contexto)
        """
        from src.frontend.views.invoices.invoice_list_view import InvoiceListView
        from src.frontend.services.api import order_api
        
        logger.info(f"Navigating to invoice list for order_id={order_id}")
        
        # Necesitamos obtener el número de orden para mostrarlo
        # Esto se puede hacer de forma asíncrona en la vista, pero para el número usamos un placeholder
        order_number = f"# {order_id}"  # Placeholder, la vista cargará el real
        
        invoice_list_view = InvoiceListView(
            order_id=order_id,
            order_number=order_number,
            on_view_detail=lambda inv_id, inv_type_class: self.navigate_to_invoice_detail(
                inv_id, inv_type_class, order_id, company_id, company_type
            ),
            on_create=None,  # TODO: Implement when needed
            on_back=lambda: self.navigate_to_orders(),
        )
        
        self._update_content(invoice_list_view)
        self._set_breadcrumb([
            {"label": "invoices.title", "route": "/invoices"},
            {"label": f"invoices.for_order", "route": None},
        ])
        
    def navigate_to_invoice_detail(
        self,
        invoice_id: int,
        invoice_type_class: str,
        order_id: int,
        company_id: int,
        company_type: str,
    ) -> None:
        """
        Navega a la vista de detalle de factura.
        
        Args:
            invoice_id: ID de la factura
            invoice_type_class: Clase de factura ("SII" o "EXPORT")
            order_id: ID de la orden asociada
            company_id: ID de la empresa
            company_type: Tipo de empresa
        """
        from src.frontend.views.invoices.invoice_detail_view import InvoiceDetailView
        
        logger.info(
            f"Navigating to invoice detail: invoice_id={invoice_id}, "
            f"type={invoice_type_class}, order_id={order_id}"
        )
        
        detail_view = InvoiceDetailView(
            invoice_id=invoice_id,
            invoice_type_class=invoice_type_class,
            on_edit=None,  # TODO: Implement when needed
            on_delete=lambda inv_id: self._on_deleted(
                inv_id, invoice_type_class, order_id, company_id, company_type
            ),
            on_back=lambda: self.navigate_to_invoice_list_for_order(
                order_id, company_id, company_type
            ),
        )
        
        self._update_content(detail_view)
        self._set_breadcrumb([
            {"label": "invoices.title", "route": "/invoices"},
            {"label": "invoices.for_order", "route": None},  # TODO: Add route if needed
            {"label": "invoices.detail", "route": None},
        ])
    
    def _on_deleted(
        self,
        invoice_id: int,
        invoice_type_class: str,
        order_id: int,
        company_id: int,
        company_type: str,
    ) -> None:
        """Callback cuando se elimina una factura desde el detalle."""
        logger.success(f"Invoice deleted: {invoice_id} (type={invoice_type_class})")
        # Volver a la lista de facturas de la orden
        self.navigate_to_invoice_list_for_order(order_id, company_id, company_type)
