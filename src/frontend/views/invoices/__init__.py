"""
Vistas de facturas.
"""
from .invoice_list_view import InvoiceListView
from .invoice_detail_view import InvoiceDetailView

__all__ = [
    "InvoiceListView",
    "InvoiceDetailView",
]
