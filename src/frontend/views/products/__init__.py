"""
Product management views.

Vistas para gestión de productos (listado, formularios, detalle).
"""
from src.frontend.views.products.product_list_view import ProductListView
from src.frontend.views.products.product_form_view import ProductFormView
from src.frontend.views.products.product_detail_view import ProductDetailView

__all__ = ["ProductListView", "ProductFormView", "ProductDetailView"]
