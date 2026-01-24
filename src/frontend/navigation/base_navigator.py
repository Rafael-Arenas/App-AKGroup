"""
Navegador Base.

Proporciona funcionalidad común para todos los navegadores especializados.
"""
from typing import TYPE_CHECKING
import flet as ft
from loguru import logger

from src.frontend.app_state import app_state

if TYPE_CHECKING:
    from src.frontend.views.main_view import MainView


class BaseNavigator:
    """
    Clase base para navegadores especializados.
    
    Proporciona métodos comunes para actualizar contenido y breadcrumbs.
    
    Args:
        main_view: Referencia a la vista principal
        
    Example:
        >>> navigator = CompanyNavigator(main_view)
        >>> navigator.navigate_to_detail(123, "CLIENT")
    """
    
    def __init__(self, main_view: "MainView"):
        """
        Inicializa el navegador base.
        
        Args:
            main_view: Referencia a la vista principal
        """
        self.main_view = main_view
        
    def _update_content(self, view: ft.Control) -> None:
        """
        Actualiza el contenido del área principal.
        
        Args:
            view: Control de Flet a mostrar
        """
        if self.main_view._content_area:
            self.main_view._content_area.content = view
            if self.main_view.page:
                self.main_view.update()
                
    def _set_breadcrumb(self, items: list[dict[str, str | None]]) -> None:
        """
        Actualiza el breadcrumb con nuevos items.
        
        Args:
            items: Lista de items del breadcrumb con formato {"label": str, "route": str | None}
        """
        app_state.navigation.set_breadcrumb(items)
        logger.debug(f"Breadcrumb updated: {[item['label'] for item in items]}")
        
    def _navigate_to_index(self, index: int) -> None:
        """
        Navega a un índice de sección específico.
        
        Args:
            index: Índice de la sección
        """
        if self.main_view._navigation_rail:
            self.main_view._navigation_rail.set_selected_index(index)
        self.main_view._on_destination_change(index)
