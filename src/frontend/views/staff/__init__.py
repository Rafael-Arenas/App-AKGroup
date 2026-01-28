"""
Staff views.

Vistas para la gestión de personal del sistema.
"""
from src.frontend.views.staff.staff_list_view import StaffListView
from src.frontend.views.staff.staff_detail_view import StaffDetailView
from src.frontend.views.staff.staff_form_view import StaffFormView

__all__ = [
    "StaffListView",
    "StaffDetailView",
    "StaffFormView",
]
