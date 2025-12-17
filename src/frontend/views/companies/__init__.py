"""
Company management views.

Vistas para gestión de empresas (listado, formularios, detalle).
"""
from src.frontend.views.companies.company_list_view import CompanyListView
from src.frontend.views.companies.company_form_view import CompanyFormView
from src.frontend.views.companies.company_detail_view import CompanyDetailView
from src.frontend.views.companies.company_dashboard_view import CompanyDashboardView
from src.frontend.views.companies.company_related_views import (
    CompanyQuotesView,
    CompanyOrdersView,
    CompanyDeliveriesView,
    CompanyInvoicesView,
)

__all__ = [
    "CompanyListView",
    "CompanyFormView",
    "CompanyDetailView",
    "CompanyDashboardView",
    "CompanyQuotesView",
    "CompanyOrdersView",
    "CompanyDeliveriesView",
    "CompanyInvoicesView",
]
