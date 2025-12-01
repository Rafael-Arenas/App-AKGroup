"""
Product view components.

Componentes específicos para las vistas de productos.
"""
from src.frontend.views.products.components.product_card import ProductCard
from src.frontend.views.products.components.bom_table import BOMTable
from src.frontend.views.products.components.bom_component_row import BOMComponentRow
from src.frontend.views.products.components.article_selector_dialog import ArticleSelectorDialog

__all__ = ["ProductCard", "BOMTable", "BOMComponentRow", "ArticleSelectorDialog"]
