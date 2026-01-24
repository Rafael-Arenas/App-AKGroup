"""
Navegador de Nomenclaturas (Nomenclatures).

Maneja toda la navegación relacionada con nomenclaturas.
"""
from typing import TYPE_CHECKING
from loguru import logger

from src.frontend.navigation.base_navigator import BaseNavigator

if TYPE_CHECKING:
    from src.frontend.views.main_view import MainView


class NomenclatureNavigator(BaseNavigator):
    """
    Navegador especializado para nomenclaturas.
    
    Maneja navegación a:
    - Lista de nomenclaturas
    - Detalle de nomenclatura
    - Formulario de nomenclatura (crear/editar)
    - Artículos de nomenclatura
    """
    
    def __init__(self, main_view: "MainView"):
        super().__init__(main_view)
        
    def navigate_to_list(self) -> None:
        """Navega a la lista de nomenclaturas."""
        logger.info("Navigating to nomenclature list")
        self._navigate_to_index(4)
        
    def navigate_to_detail(self, nomenclature_id: int) -> None:
        """
        Navega a la vista de detalle de una nomenclatura.
        
        Args:
            nomenclature_id: ID de la nomenclatura a mostrar
        """
        from src.frontend.views.nomenclatures.nomenclature_detail_view import NomenclatureDetailView
        
        logger.info(f"Navigating to nomenclature detail: ID={nomenclature_id}")
        
        # Crear vista de detalle
        detail_view = NomenclatureDetailView(
            nomenclature_id=nomenclature_id,
            on_edit=self.navigate_to_form,
            on_delete=self._on_deleted,
            on_back=self.navigate_to_list,
        )
        
        # Actualizar contenido
        self._update_content(detail_view)
        
        # Actualizar breadcrumb
        self._set_breadcrumb([
            {"label": "nomenclatures.title", "route": "/nomenclatures"},
            {"label": "nomenclatures.detail", "route": None},
        ])
        
    def navigate_to_form(self, nomenclature_id: int | None = None) -> None:
        """
        Navega a la vista de formulario de nomenclatura.
        
        Args:
            nomenclature_id: ID de la nomenclatura a editar (None para crear nueva)
        """
        from src.frontend.views.nomenclatures.nomenclature_form_view import NomenclatureFormView
        
        logger.info(
            f"Navigating to nomenclature form: ID={nomenclature_id}, "
            f"mode={'edit' if nomenclature_id else 'create'}"
        )
        
        # Crear vista de formulario
        form_view = NomenclatureFormView(
            nomenclature_id=nomenclature_id,
            on_save=self._on_saved,
            on_cancel=self.navigate_to_list,
            on_add_articles=self.navigate_to_articles,
        )
        
        # Actualizar contenido
        self._update_content(form_view)
        
        # Actualizar breadcrumb
        action_key = "nomenclatures.edit" if nomenclature_id else "nomenclatures.create"
        self._set_breadcrumb([
            {"label": "nomenclatures.title", "route": "/nomenclatures"},
            {"label": action_key, "route": None},
        ])
        
    def navigate_to_articles(self, nomenclature_id: int) -> None:
        """
        Navega a la vista de agregar artículos a una nomenclatura.
        
        Args:
            nomenclature_id: ID de la nomenclatura
        """
        from src.frontend.views.nomenclatures.nomenclature_articles_view import NomenclatureArticlesView
        
        logger.info(f"Navigating to nomenclature articles: nomenclature_id={nomenclature_id}")
        
        articles_view = NomenclatureArticlesView(
            nomenclature_id=nomenclature_id,
            on_back=lambda: self.navigate_to_detail(nomenclature_id),
            on_article_added=lambda: self.navigate_to_detail(nomenclature_id),
        )
        
        self._update_content(articles_view)
        
        self._set_breadcrumb([
            {"label": "nomenclatures.title", "route": "/nomenclatures"},
            {"label": "nomenclatures.detail", "route": f"/nomenclatures/{nomenclature_id}"},
            {"label": "nomenclatures.add_articles", "route": None},
        ])
        
    def _on_saved(self, nomenclature: dict) -> None:
        """
        Callback cuando se guarda una nomenclatura exitosamente.
        
        Args:
            nomenclature: Datos de la nomenclatura guardada
        """
        logger.success(f"Nomenclature saved: {nomenclature.get('reference', nomenclature.get('code'))}")
        self.navigate_to_list()
        
    def _on_deleted(self, nomenclature_id: int) -> None:
        """
        Callback cuando se elimina una nomenclatura.
        
        Args:
            nomenclature_id: ID de la nomenclatura eliminada
        """
        logger.success(f"Nomenclature deleted: ID={nomenclature_id}")
        self.navigate_to_list()
