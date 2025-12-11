"""
Application views.

Vistas principales de la aplicación.
"""
from src.frontend.views.main_view import MainView
from src.frontend.views.articles import ArticleListView, ArticleFormView, ArticleDetailView
from src.frontend.views.nomenclatures import NomenclatureListView, NomenclatureFormView, NomenclatureDetailView

__all__ = [
    "MainView",
    "ArticleListView",
    "ArticleFormView",
    "ArticleDetailView",
    "NomenclatureListView",
    "NomenclatureFormView",
    "NomenclatureDetailView",
]
