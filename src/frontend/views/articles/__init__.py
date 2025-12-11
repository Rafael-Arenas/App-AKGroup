"""
Article management views.

Vistas para gestión de artículos (listado, formularios, detalle).
"""
from src.frontend.views.articles.article_list_view import ArticleListView
from src.frontend.views.articles.article_form_view import ArticleFormView
from src.frontend.views.articles.article_detail_view import ArticleDetailView

__all__ = ["ArticleListView", "ArticleFormView", "ArticleDetailView"]
