"""
Nomenclature management views.

Vistas para gestión de nomenclaturas (listado, formularios, detalle).
"""
from src.frontend.views.nomenclatures.nomenclature_list_view import NomenclatureListView
from src.frontend.views.nomenclatures.nomenclature_form_view import NomenclatureFormView
from src.frontend.views.nomenclatures.nomenclature_detail_view import NomenclatureDetailView

__all__ = ["NomenclatureListView", "NomenclatureFormView", "NomenclatureDetailView"]
