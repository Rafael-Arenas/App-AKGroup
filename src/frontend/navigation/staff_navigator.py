"""
Navegador de Personal (Staff).

Maneja toda la navegación relacionada con usuarios del sistema.
"""
from typing import TYPE_CHECKING
from loguru import logger

from src.frontend.navigation.base_navigator import BaseNavigator

if TYPE_CHECKING:
    from src.frontend.views.main_view import MainView


class StaffNavigator(BaseNavigator):
    """
    Navegador especializado para personal del sistema.
    
    Maneja navegación a:
    - Lista de personal
    - Detalle de personal
    - Formulario de personal (crear/editar)
    """
    
    # Índice de Staff en la navegación (según navigation_config.py)
    NAV_INDEX = 8
    
    def __init__(self, main_view: "MainView"):
        super().__init__(main_view)
        
    def navigate_to_list(self) -> None:
        """
        Navega a la lista de personal.
        """
        from src.frontend.views.staff.staff_list_view import StaffListView
        
        logger.info("Navigating to staff list")
        
        # Crear vista de lista
        list_view = StaffListView(
            on_view_detail=lambda staff_id: self.navigate_to_detail(staff_id),
            on_create=lambda: self.navigate_to_form(),
            on_edit=lambda staff_id: self.navigate_to_form(staff_id),
        )
        
        # Actualizar contenido
        self._update_content(list_view)
        
        # Actualizar breadcrumb
        self._set_breadcrumb([
            {"label": "staff.title", "route": None},
        ])
        
    def navigate_to_detail(self, staff_id: int) -> None:
        """
        Navega a la vista de detalle de un miembro del personal.
        
        Args:
            staff_id: ID del personal
        """
        from src.frontend.views.staff.staff_detail_view import StaffDetailView
        
        logger.info(f"Navigating to staff detail: ID={staff_id}")
        
        # Crear vista de detalle
        detail_view = StaffDetailView(
            staff_id=staff_id,
            on_edit=lambda sid: self.navigate_to_form(sid),
            on_delete=lambda sid: self._on_deleted(sid),
            on_back=lambda: self.navigate_to_list(),
        )
        
        # Actualizar contenido
        self._update_content(detail_view)
        
        # Actualizar breadcrumb
        self._set_breadcrumb([
            {"label": "staff.title", "route": "/staff"},
            {"label": "staff.detail", "route": None},
        ])
        
    def navigate_to_form(self, staff_id: int | None = None) -> None:
        """
        Navega a la vista de formulario de personal (crear/editar).
        
        Args:
            staff_id: ID del personal a editar (None para crear)
        """
        from src.frontend.views.staff.staff_form_view import StaffFormView
        
        logger.info(
            f"Navigating to staff form: ID={staff_id}, "
            f"mode={'edit' if staff_id else 'create'}"
        )
        
        # Crear vista de formulario
        form_view = StaffFormView(
            staff_id=staff_id,
            on_save=lambda sid: self._on_saved(sid),
            on_cancel=lambda: self.navigate_to_list(),
        )
        
        # Actualizar contenido
        self._update_content(form_view)
        
        # Actualizar breadcrumb
        action_key = "staff.edit" if staff_id else "staff.create"
        self._set_breadcrumb([
            {"label": "staff.title", "route": "/staff"},
            {"label": action_key, "route": None},
        ])
        
    def _on_saved(self, staff_id: int) -> None:
        """
        Callback cuando se guarda un personal exitosamente.
        
        Args:
            staff_id: ID del personal guardado
        """
        logger.success(f"Staff saved: ID={staff_id}")
        self.navigate_to_list()
        
    def _on_deleted(self, staff_id: int) -> None:
        """
        Callback cuando se elimina un personal.
        
        Args:
            staff_id: ID del personal eliminado
        """
        logger.success(f"Staff deleted: ID={staff_id}")
        self.navigate_to_list()
