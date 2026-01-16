"""
Repository Factory - Centraliza la creación de repositorios.

Proporciona acceso a todos los repositorios con una sesión compartida,
facilitando la inyección de dependencias y el manejo de transacciones.
"""

from functools import cached_property

from sqlalchemy.orm import Session

# Core repositories
from src.backend.repositories.core.company_repository import (
    CompanyRepository,
    CompanyRutRepository as CompanyRutRepoFromCompany,
    PlantRepository,
)
from src.backend.repositories.core.company_rut_repository import CompanyRutRepository
from src.backend.repositories.core.contact_repository import ContactRepository
from src.backend.repositories.core.address_repository import AddressRepository
from src.backend.repositories.core.product_repository import ProductRepository, ProductComponentRepository
from src.backend.repositories.core.staff_repository import StaffRepository
from src.backend.repositories.core.note_repository import NoteRepository
from src.backend.repositories.core.service_repository import ServiceRepository

# Business repositories
from src.backend.repositories.business.order_repository import OrderRepository, OrderProductRepository
from src.backend.repositories.business.quote_repository import QuoteRepository, QuoteProductRepository
from src.backend.repositories.business.delivery_repository import (
    DeliveryOrderRepository,
    DeliveryDateRepository,
    TransportRepository,
    PaymentConditionRepository,
)
from src.backend.repositories.business.invoice_repository import InvoiceSIIRepository, InvoiceExportRepository

# Lookup repositories
from src.backend.repositories.lookups.lookup_repository import (
    CountryRepository,
    CityRepository,
    CompanyTypeRepository,
    IncotermRepository,
    CurrencyRepository,
    UnitRepository,
    FamilyTypeRepository,
    MatterRepository,
    SalesTypeRepository,
    QuoteStatusRepository,
    OrderStatusRepository,
    PaymentStatusRepository,
)


class RepositoryFactory:
    """
    Factory para obtener repositorios con sesión compartida.

    Centraliza la creación de repositorios y garantiza que todos
    usen la misma sesión de base de datos.

    Los repositorios son creados de forma lazy usando cached_property,
    lo que significa que solo se instancian cuando se acceden por primera vez.

    Example:
        # En un endpoint de FastAPI
        def get_repos(db: Session = Depends(get_db)) -> RepositoryFactory:
            return RepositoryFactory(db)

        @router.post("/orders")
        def create_order(
            order_data: OrderCreate,
            repos: RepositoryFactory = Depends(get_repos)
        ):
            company = repos.companies.get_by_id(order_data.company_id)
            quote = repos.quotes.get_by_id(order_data.quote_id)
            order = repos.orders.create(Order(...))
            return order

        # En un servicio
        class OrderService:
            def __init__(self, repos: RepositoryFactory):
                self.repos = repos

            def create_from_quote(self, quote_id: int):
                quote = self.repos.quotes.get_with_products(quote_id)
                company = self.repos.companies.get_by_id(quote.company_id)
                # ...
    """

    def __init__(self, session: Session):
        """
        Inicializa el factory con una sesión de base de datos.

        Args:
            session: Sesión de SQLAlchemy a compartir entre repositorios
        """
        self._session = session

    @property
    def session(self) -> Session:
        """Acceso a la sesión compartida."""
        return self._session

    # =========================================================================
    # Core Repositories
    # =========================================================================

    @cached_property
    def companies(self) -> CompanyRepository:
        """Repositorio de empresas."""
        return CompanyRepository(self._session)

    @cached_property
    def company_ruts(self) -> CompanyRutRepository:
        """Repositorio de RUTs de empresas."""
        return CompanyRutRepository(self._session)

    @cached_property
    def plants(self) -> PlantRepository:
        """Repositorio de plantas/sucursales."""
        return PlantRepository(self._session)

    @cached_property
    def contacts(self) -> ContactRepository:
        """Repositorio de contactos."""
        return ContactRepository(self._session)

    @cached_property
    def addresses(self) -> AddressRepository:
        """Repositorio de direcciones."""
        return AddressRepository(self._session)

    @cached_property
    def products(self) -> ProductRepository:
        """Repositorio de productos."""
        return ProductRepository(self._session)

    @cached_property
    def product_components(self) -> ProductComponentRepository:
        """Repositorio de componentes de productos (BOM)."""
        return ProductComponentRepository(self._session)

    @cached_property
    def staff(self) -> StaffRepository:
        """Repositorio de usuarios del sistema."""
        return StaffRepository(self._session)

    @cached_property
    def notes(self) -> NoteRepository:
        """Repositorio de notas."""
        return NoteRepository(self._session)

    @cached_property
    def services(self) -> ServiceRepository:
        """Repositorio de servicios/departamentos."""
        return ServiceRepository(self._session)

    # =========================================================================
    # Business Repositories
    # =========================================================================

    @cached_property
    def orders(self) -> OrderRepository:
        """Repositorio de órdenes."""
        return OrderRepository(self._session)

    @cached_property
    def order_products(self) -> OrderProductRepository:
        """Repositorio de productos de órdenes."""
        return OrderProductRepository(self._session)

    @cached_property
    def quotes(self) -> QuoteRepository:
        """Repositorio de cotizaciones."""
        return QuoteRepository(self._session)

    @cached_property
    def quote_products(self) -> QuoteProductRepository:
        """Repositorio de productos de cotizaciones."""
        return QuoteProductRepository(self._session)

    @cached_property
    def delivery_orders(self) -> DeliveryOrderRepository:
        """Repositorio de órdenes de despacho."""
        return DeliveryOrderRepository(self._session)

    @cached_property
    def delivery_dates(self) -> DeliveryDateRepository:
        """Repositorio de fechas de entrega."""
        return DeliveryDateRepository(self._session)

    @cached_property
    def transports(self) -> TransportRepository:
        """Repositorio de transportes."""
        return TransportRepository(self._session)

    @cached_property
    def payment_conditions(self) -> PaymentConditionRepository:
        """Repositorio de condiciones de pago."""
        return PaymentConditionRepository(self._session)

    @cached_property
    def invoices_sii(self) -> InvoiceSIIRepository:
        """Repositorio de facturas SII (nacionales)."""
        return InvoiceSIIRepository(self._session)

    @cached_property
    def invoices_export(self) -> InvoiceExportRepository:
        """Repositorio de facturas de exportación."""
        return InvoiceExportRepository(self._session)

    # =========================================================================
    # Lookup Repositories
    # =========================================================================

    @cached_property
    def countries(self) -> CountryRepository:
        """Repositorio de países."""
        return CountryRepository(self._session)

    @cached_property
    def cities(self) -> CityRepository:
        """Repositorio de ciudades."""
        return CityRepository(self._session)

    @cached_property
    def company_types(self) -> CompanyTypeRepository:
        """Repositorio de tipos de empresa."""
        return CompanyTypeRepository(self._session)

    @cached_property
    def incoterms(self) -> IncotermRepository:
        """Repositorio de incoterms."""
        return IncotermRepository(self._session)

    @cached_property
    def currencies(self) -> CurrencyRepository:
        """Repositorio de monedas."""
        return CurrencyRepository(self._session)

    @cached_property
    def units(self) -> UnitRepository:
        """Repositorio de unidades de medida."""
        return UnitRepository(self._session)

    @cached_property
    def family_types(self) -> FamilyTypeRepository:
        """Repositorio de tipos de familia de productos."""
        return FamilyTypeRepository(self._session)

    @cached_property
    def matters(self) -> MatterRepository:
        """Repositorio de materiales."""
        return MatterRepository(self._session)

    @cached_property
    def sales_types(self) -> SalesTypeRepository:
        """Repositorio de tipos de venta."""
        return SalesTypeRepository(self._session)

    @cached_property
    def quote_statuses(self) -> QuoteStatusRepository:
        """Repositorio de estados de cotización."""
        return QuoteStatusRepository(self._session)

    @cached_property
    def order_statuses(self) -> OrderStatusRepository:
        """Repositorio de estados de orden."""
        return OrderStatusRepository(self._session)

    @cached_property
    def payment_statuses(self) -> PaymentStatusRepository:
        """Repositorio de estados de pago."""
        return PaymentStatusRepository(self._session)


# Alias para conveniencia
Repos = RepositoryFactory
