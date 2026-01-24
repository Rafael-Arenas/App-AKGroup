"""
Navegador de Artículos (Articles).

Maneja toda la navegación relacionada con artículos.
"""
from typing import TYPE_CHECKING
from loguru import logger

from src.frontend.navigation.base_navigator import BaseNavigator

if TYPE_CHECKING:
    from src.frontend.views.main_view import MainView


class ArticleNavigator(BaseNavigator):
    """
    Navegador especializado para artículos.
    
    Maneja navegación a:
    - Lista de artículos
    - Detalle de artículo
    - Formulario de artículo (crear/editar)
    """
    
    def __init__(self, main_view: "MainView"):
        super().__init__(main_view)
        
    def navigate_to_list(self) -> None:
        """Navega a la lista de artículos."""
        logger.info("Navigating to article list")
        self._navigate_to_index(3)
        
    def navigate_to_detail(self, article_id: int) -> None:
        """
        Navega a la vista de detalle de un artículo.
        
        Args:
            article_id: ID del artículo a mostrar
        """
        from src.frontend.views.articles.article_detail_view import ArticleDetailView
        
        logger.info(f"Navigating to article detail: ID={article_id}")
        
        # Crear vista de detalle
        detail_view = ArticleDetailView(
            article_id=article_id,
            on_edit=self.navigate_to_form,
            on_delete=self._on_deleted,
            on_back=self.navigate_to_list,
        )
        
        # Actualizar contenido
        self._update_content(detail_view)
        
        # Actualizar breadcrumb
        self._set_breadcrumb([
            {"label": "articles.title", "route": "/articles"},
            {"label": "articles.detail", "route": None},
        ])
        
    def navigate_to_form(self, article_id: int | None = None) -> None:
        """
        Navega a la vista de formulario de artículo.
        
        Args:
            article_id: ID del artículo a editar (None para crear nuevo)
        """
        from src.frontend.views.articles.article_form_view import ArticleFormView
        
        logger.info(
            f"Navigating to article form: ID={article_id}, "
            f"mode={'edit' if article_id else 'create'}"
        )
        
        # Crear vista de formulario
        form_view = ArticleFormView(
            article_id=article_id,
            on_save=self._on_saved,
            on_cancel=self.navigate_to_list,
        )
        
        # Actualizar contenido
        self._update_content(form_view)
        
        # Actualizar breadcrumb
        action_key = "articles.edit" if article_id else "articles.create"
        self._set_breadcrumb([
            {"label": "articles.title", "route": "/articles"},
            {"label": action_key, "route": None},
        ])
        
    def _on_saved(self, article: dict) -> None:
        """
        Callback cuando se guarda un artículo exitosamente.
        
        Args:
            article: Datos del artículo guardado
        """
        logger.success(f"Article saved: {article.get('reference', article.get('code'))}")
        self.navigate_to_list()
        
    def _on_deleted(self, article_id: int) -> None:
        """
        Callback cuando se elimina un artículo.
        
        Args:
            article_id: ID del artículo eliminado
        """
        logger.success(f"Article deleted: ID={article_id}")
        self.navigate_to_list()
