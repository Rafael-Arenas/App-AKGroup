"""
Services for lookup/reference tables.

Provides business logic for all 12 lookup tables:
- Country
- City
- CompanyType
- Incoterm
- Currency
- Unit
- FamilyType
- Matter
- SalesType
- QuoteStatus
- OrderStatus
- PaymentStatus
"""

from sqlalchemy.orm import Session


from src.backend.models.lookups import (
    Country,
    City,
    CompanyType,
    Incoterm,
    Currency,
    Unit,
    FamilyType,
    Matter,
    SalesType,
    QuoteStatus,
    OrderStatus,
    PaymentStatus,
)
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
from src.shared.schemas.lookups.lookup import (
    CountryCreate,
    CountryUpdate,
    CountryResponse,
    CityCreate,
    CityUpdate,
    CityResponse,
    CompanyTypeCreate,
    CompanyTypeUpdate,
    CompanyTypeResponse,
    IncotermCreate,
    IncotermUpdate,
    IncotermResponse,
    CurrencyCreate,
    CurrencyUpdate,
    CurrencyResponse,
    UnitCreate,
    UnitUpdate,
    UnitResponse,
    FamilyTypeCreate,
    FamilyTypeUpdate,
    FamilyTypeResponse,
    MatterCreate,
    MatterUpdate,
    MatterResponse,
    SalesTypeCreate,
    SalesTypeUpdate,
    SalesTypeResponse,
    QuoteStatusCreate,
    QuoteStatusUpdate,
    QuoteStatusResponse,
    OrderStatusCreate,
    OrderStatusUpdate,
    OrderStatusResponse,
    PaymentStatusCreate,
    PaymentStatusUpdate,
    PaymentStatusResponse,
)
from src.backend.services.base import BaseService
from src.backend.exceptions.service import ValidationException
from src.backend.exceptions.repository import NotFoundException
from src.backend.utils.logger import logger


# ========== COUNTRY SERVICE ==========
class CountryService(BaseService[Country, CountryCreate, CountryUpdate, CountryResponse]):
    """
    Service for Country lookup operations.

    Provides business logic for managing countries including validation
    of unique country names and ISO codes.
    """

    def __init__(self, repository: CountryRepository, session: Session):
        """
        Initialize CountryService.

        Args:
            repository: CountryRepository instance
            session: Database session
        """
        super().__init__(repository, session, Country, CountryResponse)
        self.country_repo: CountryRepository = repository

    def validate_create(self, entity: Country) -> None:
        """
        Validate country creation.

        Args:
            entity: Country entity to validate

        Raises:
            ValidationException: If country name already exists
        """
        existing = self.country_repo.get_by_name(entity.name)
        if existing:
            logger.warning(f"Country already exists: {entity.name}")
            raise ValidationException(
                f"Country already exists: {entity.name}",
                details={"name": entity.name, "existing_id": existing.id},
            )

    def validate_update(self, entity: Country) -> None:
        """
        Validate country update.

        Args:
            entity: Country entity to validate

        Raises:
            ValidationException: If country name already exists for different country
        """
        existing = self.country_repo.get_by_name(entity.name)
        if existing and existing.id != entity.id:
            logger.warning(f"Country name already exists: {entity.name}")
            raise ValidationException(
                f"Country name already exists: {entity.name}",
                details={"name": entity.name, "existing_id": existing.id},
            )

    def get_by_name(self, name: str) -> CountryResponse:
        """
        Get country by name.

        Args:
            name: Country name

        Returns:
            CountryResponse with country data

        Raises:
            NotFoundException: If country not found
        """
        logger.info(f"Getting country by name: {name}")
        country = self.country_repo.get_by_name(name)
        if not country:
            logger.warning(f"Country not found: {name}")
            raise NotFoundException(f"Country not found: {name}")
        return self.response_schema.model_validate(country)


# ========== CITY SERVICE ==========
class CityService(BaseService[City, CityCreate, CityUpdate, CityResponse]):
    """
    Service for City lookup operations.

    Provides business logic for managing cities including filtering by country.
    """

    def __init__(self, repository: CityRepository, session: Session):
        """
        Initialize CityService.

        Args:
            repository: CityRepository instance
            session: Database session
        """
        super().__init__(repository, session, City, CityResponse)
        self.city_repo: CityRepository = repository

    def validate_create(self, entity: City) -> None:
        """
        Validate city creation.

        Args:
            entity: City entity to validate

        Note:
            Cities can have duplicate names in different countries, so no unique validation.
        """
        pass

    def validate_update(self, entity: City) -> None:
        """
        Validate city update.

        Args:
            entity: City entity to validate
        """
        pass

    def get_by_country(self, country_id: int) -> list[CityResponse]:
        """
        Get all cities in a country.

        Args:
            country_id: ID of the country

        Returns:
            List of CityResponse objects
        """
        logger.info(f"Getting cities for country: {country_id}")
        cities = self.city_repo.get_by_country(country_id)
        logger.info(f"Found {len(cities)} cities for country {country_id}")
        return [self.response_schema.model_validate(c) for c in cities]


# ========== COMPANY TYPE SERVICE ==========
class CompanyTypeService(
    BaseService[CompanyType, CompanyTypeCreate, CompanyTypeUpdate, CompanyTypeResponse]
):
    """
    Service for CompanyType lookup operations.

    Provides business logic for managing company types.
    """

    def __init__(self, repository: CompanyTypeRepository, session: Session):
        """
        Initialize CompanyTypeService.

        Args:
            repository: CompanyTypeRepository instance
            session: Database session
        """
        super().__init__(repository, session, CompanyType, CompanyTypeResponse)
        self.company_type_repo: CompanyTypeRepository = repository

    def validate_create(self, entity: CompanyType) -> None:
        """
        Validate company type creation.

        Args:
            entity: CompanyType entity to validate

        Raises:
            ValidationException: If company type name already exists
        """
        existing = self.company_type_repo.get_by_name(entity.name)
        if existing:
            logger.warning(f"Company type already exists: {entity.name}")
            raise ValidationException(
                f"Company type already exists: {entity.name}",
                details={"name": entity.name, "existing_id": existing.id},
            )

    def validate_update(self, entity: CompanyType) -> None:
        """
        Validate company type update.

        Args:
            entity: CompanyType entity to validate

        Raises:
            ValidationException: If company type name already exists for different entity
        """
        existing = self.company_type_repo.get_by_name(entity.name)
        if existing and existing.id != entity.id:
            logger.warning(f"Company type name already exists: {entity.name}")
            raise ValidationException(
                f"Company type name already exists: {entity.name}",
                details={"name": entity.name, "existing_id": existing.id},
            )

    def get_by_name(self, name: str) -> CompanyTypeResponse:
        """
        Get company type by name.

        Args:
            name: Company type name

        Returns:
            CompanyTypeResponse with company type data

        Raises:
            NotFoundException: If company type not found
        """
        logger.info(f"Getting company type by name: {name}")
        company_type = self.company_type_repo.get_by_name(name)
        if not company_type:
            logger.warning(f"Company type not found: {name}")
            raise NotFoundException(f"Company type not found: {name}")
        return self.response_schema.model_validate(company_type)


# ========== INCOTERMS SERVICE ==========
class IncotermService(
    BaseService[Incoterm, IncotermCreate, IncotermUpdate, IncotermResponse]
):
    """
    Service for Incoterm lookup operations.

    Provides business logic for managing Incoterm including validation
    of unique codes.
    """

    def __init__(self, repository: IncotermRepository, session: Session):
        """
        Initialize IncotermService.

        Args:
            repository: IncotermRepository instance
            session: Database session
        """
        super().__init__(repository, session, Incoterm, IncotermResponse)
        self.incoterms_repo: IncotermRepository = repository

    def validate_create(self, entity: Incoterm) -> None:
        """
        Validate Incoterm creation.

        Args:
            entity: Incoterm entity to validate

        Raises:
            ValidationException: If Incoterm code already exists
        """
        existing = self.incoterms_repo.get_by_code(entity.code)
        if existing:
            logger.warning(f"Incoterm code already exists: {entity.code}")
            raise ValidationException(
                f"Incoterm code already exists: {entity.code}",
                details={"code": entity.code, "existing_id": existing.id},
            )

    def validate_update(self, entity: Incoterm) -> None:
        """
        Validate Incoterm update.

        Args:
            entity: Incoterm entity to validate

        Raises:
            ValidationException: If Incoterm code already exists for different entity
        """
        existing = self.incoterms_repo.get_by_code(entity.code)
        if existing and existing.id != entity.id:
            logger.warning(f"Incoterm code already exists: {entity.code}")
            raise ValidationException(
                f"Incoterm code already exists: {entity.code}",
                details={"code": entity.code, "existing_id": existing.id},
            )

    def get_by_code(self, code: str) -> IncotermResponse:
        """
        Get Incoterm by code.

        Args:
            code: Incoterm code (e.g., 'FOB', 'CIF')

        Returns:
            IncotermResponse with Incoterm data

        Raises:
            NotFoundException: If Incoterm not found
        """
        logger.info(f"Getting Incoterm by code: {code}")
        incoterm = self.incoterms_repo.get_by_code(code)
        if not incoterm:
            logger.warning(f"Incoterm not found: {code}")
            raise NotFoundException(f"Incoterm not found: {code}")
        return self.response_schema.model_validate(incoterm)


# ========== CURRENCY SERVICE ==========
class CurrencyService(BaseService[Currency, CurrencyCreate, CurrencyUpdate, CurrencyResponse]):
    """
    Service for Currency lookup operations.

    Provides business logic for managing currencies including validation
    of unique ISO codes.
    """

    def __init__(self, repository: CurrencyRepository, session: Session):
        """
        Initialize CurrencyService.

        Args:
            repository: CurrencyRepository instance
            session: Database session
        """
        super().__init__(repository, session, Currency, CurrencyResponse)
        self.currency_repo: CurrencyRepository = repository

    def validate_create(self, entity: Currency) -> None:
        """
        Validate currency creation.

        Args:
            entity: Currency entity to validate

        Raises:
            ValidationException: If currency code already exists
        """
        existing = self.currency_repo.get_by_code(entity.code)
        if existing:
            logger.warning(f"Currency code already exists: {entity.code}")
            raise ValidationException(
                f"Currency code already exists: {entity.code}",
                details={"code": entity.code, "existing_id": existing.id},
            )

    def validate_update(self, entity: Currency) -> None:
        """
        Validate currency update.

        Args:
            entity: Currency entity to validate

        Raises:
            ValidationException: If currency code already exists for different entity
        """
        existing = self.currency_repo.get_by_code(entity.code)
        if existing and existing.id != entity.id:
            logger.warning(f"Currency code already exists: {entity.code}")
            raise ValidationException(
                f"Currency code already exists: {entity.code}",
                details={"code": entity.code, "existing_id": existing.id},
            )

    def get_by_code(self, code: str) -> CurrencyResponse:
        """
        Get currency by ISO code.

        Args:
            code: ISO 4217 currency code (e.g., 'USD', 'EUR')

        Returns:
            CurrencyResponse with currency data

        Raises:
            NotFoundException: If currency not found
        """
        logger.info(f"Getting currency by code: {code}")
        currency = self.currency_repo.get_by_code(code)
        if not currency:
            logger.warning(f"Currency not found: {code}")
            raise NotFoundException(f"Currency not found: {code}")
        return self.response_schema.model_validate(currency)


# ========== UNIT SERVICE ==========
class UnitService(BaseService[Unit, UnitCreate, UnitUpdate, UnitResponse]):
    """
    Service for Unit lookup operations.

    Provides business logic for managing measurement units.
    """

    def __init__(self, repository: UnitRepository, session: Session):
        """
        Initialize UnitService.

        Args:
            repository: UnitRepository instance
            session: Database session
        """
        super().__init__(repository, session, Unit, UnitResponse)
        self.unit_repo: UnitRepository = repository

    def validate_create(self, entity: Unit) -> None:
        """
        Validate unit creation.

        Args:
            entity: Unit entity to validate

        Raises:
            ValidationException: If unit code already exists
        """
        existing = self.unit_repo.get_by_code(entity.code)
        if existing:
            logger.warning(f"Unit code already exists: {entity.code}")
            raise ValidationException(
                f"Unit code already exists: {entity.code}",
                details={"code": entity.code, "existing_id": existing.id},
            )

    def validate_update(self, entity: Unit) -> None:
        """
        Validate unit update.

        Args:
            entity: Unit entity to validate

        Raises:
            ValidationException: If unit code already exists for different entity
        """
        existing = self.unit_repo.get_by_code(entity.code)
        if existing and existing.id != entity.id:
            logger.warning(f"Unit code already exists: {entity.code}")
            raise ValidationException(
                f"Unit code already exists: {entity.code}",
                details={"code": entity.code, "existing_id": existing.id},
            )

    def get_by_code(self, code: str) -> UnitResponse:
        """
        Get unit by code.

        Args:
            code: Unit code (e.g., 'kg', 'm', 'pcs')

        Returns:
            UnitResponse with unit data

        Raises:
            NotFoundException: If unit not found
        """
        logger.info(f"Getting unit by code: {code}")
        unit = self.unit_repo.get_by_code(code)
        if not unit:
            logger.warning(f"Unit not found: {code}")
            raise NotFoundException(f"Unit not found: {code}")
        return self.response_schema.model_validate(unit)


# ========== FAMILY TYPE SERVICE ==========
class FamilyTypeService(
    BaseService[FamilyType, FamilyTypeCreate, FamilyTypeUpdate, FamilyTypeResponse]
):
    """
    Service for FamilyType lookup operations.

    Provides business logic for managing product family types.
    """

    def __init__(self, repository: FamilyTypeRepository, session: Session):
        """
        Initialize FamilyTypeService.

        Args:
            repository: FamilyTypeRepository instance
            session: Database session
        """
        super().__init__(repository, session, FamilyType, FamilyTypeResponse)
        self.family_type_repo: FamilyTypeRepository = repository

    def validate_create(self, entity: FamilyType) -> None:
        """
        Validate family type creation.

        Args:
            entity: FamilyType entity to validate

        Raises:
            ValidationException: If family type name already exists
        """
        existing = self.family_type_repo.get_by_name(entity.name)
        if existing:
            logger.warning(f"Family type already exists: {entity.name}")
            raise ValidationException(
                f"Family type already exists: {entity.name}",
                details={"name": entity.name, "existing_id": existing.id},
            )

    def validate_update(self, entity: FamilyType) -> None:
        """
        Validate family type update.

        Args:
            entity: FamilyType entity to validate

        Raises:
            ValidationException: If family type name already exists for different entity
        """
        existing = self.family_type_repo.get_by_name(entity.name)
        if existing and existing.id != entity.id:
            logger.warning(f"Family type name already exists: {entity.name}")
            raise ValidationException(
                f"Family type name already exists: {entity.name}",
                details={"name": entity.name, "existing_id": existing.id},
            )

    def get_by_name(self, name: str) -> FamilyTypeResponse:
        """
        Get family type by name.

        Args:
            name: Family type name

        Returns:
            FamilyTypeResponse with family type data

        Raises:
            NotFoundException: If family type not found
        """
        logger.info(f"Getting family type by name: {name}")
        family_type = self.family_type_repo.get_by_name(name)
        if not family_type:
            logger.warning(f"Family type not found: {name}")
            raise NotFoundException(f"Family type not found: {name}")
        return self.response_schema.model_validate(family_type)


# ========== MATTER SERVICE ==========
class MatterService(BaseService[Matter, MatterCreate, MatterUpdate, MatterResponse]):
    """
    Service for Matter lookup operations.

    Provides business logic for managing materials/matters.
    """

    def __init__(self, repository: MatterRepository, session: Session):
        """
        Initialize MatterService.

        Args:
            repository: MatterRepository instance
            session: Database session
        """
        super().__init__(repository, session, Matter, MatterResponse)
        self.matter_repo: MatterRepository = repository

    def validate_create(self, entity: Matter) -> None:
        """
        Validate matter creation.

        Args:
            entity: Matter entity to validate

        Raises:
            ValidationException: If matter name already exists
        """
        existing = self.matter_repo.get_by_name(entity.name)
        if existing:
            logger.warning(f"Matter already exists: {entity.name}")
            raise ValidationException(
                f"Matter already exists: {entity.name}",
                details={"name": entity.name, "existing_id": existing.id},
            )

    def validate_update(self, entity: Matter) -> None:
        """
        Validate matter update.

        Args:
            entity: Matter entity to validate

        Raises:
            ValidationException: If matter name already exists for different entity
        """
        existing = self.matter_repo.get_by_name(entity.name)
        if existing and existing.id != entity.id:
            logger.warning(f"Matter name already exists: {entity.name}")
            raise ValidationException(
                f"Matter name already exists: {entity.name}",
                details={"name": entity.name, "existing_id": existing.id},
            )

    def get_by_name(self, name: str) -> MatterResponse:
        """
        Get matter by name.

        Args:
            name: Matter name

        Returns:
            MatterResponse with matter data

        Raises:
            NotFoundException: If matter not found
        """
        logger.info(f"Getting matter by name: {name}")
        matter = self.matter_repo.get_by_name(name)
        if not matter:
            logger.warning(f"Matter not found: {name}")
            raise NotFoundException(f"Matter not found: {name}")
        return self.response_schema.model_validate(matter)


# ========== SALES TYPE SERVICE ==========
class SalesTypeService(
    BaseService[SalesType, SalesTypeCreate, SalesTypeUpdate, SalesTypeResponse]
):
    """
    Service for SalesType lookup operations.

    Provides business logic for managing sales types.
    """

    def __init__(self, repository: SalesTypeRepository, session: Session):
        """
        Initialize SalesTypeService.

        Args:
            repository: SalesTypeRepository instance
            session: Database session
        """
        super().__init__(repository, session, SalesType, SalesTypeResponse)
        self.sales_type_repo: SalesTypeRepository = repository

    def validate_create(self, entity: SalesType) -> None:
        """
        Validate sales type creation.

        Args:
            entity: SalesType entity to validate

        Raises:
            ValidationException: If sales type name already exists
        """
        existing = self.sales_type_repo.get_by_name(entity.name)
        if existing:
            logger.warning(f"Sales type already exists: {entity.name}")
            raise ValidationException(
                f"Sales type already exists: {entity.name}",
                details={"name": entity.name, "existing_id": existing.id},
            )

    def validate_update(self, entity: SalesType) -> None:
        """
        Validate sales type update.

        Args:
            entity: SalesType entity to validate

        Raises:
            ValidationException: If sales type name already exists for different entity
        """
        existing = self.sales_type_repo.get_by_name(entity.name)
        if existing and existing.id != entity.id:
            logger.warning(f"Sales type name already exists: {entity.name}")
            raise ValidationException(
                f"Sales type name already exists: {entity.name}",
                details={"name": entity.name, "existing_id": existing.id},
            )

    def get_by_name(self, name: str) -> SalesTypeResponse:
        """
        Get sales type by name.

        Args:
            name: Sales type name

        Returns:
            SalesTypeResponse with sales type data

        Raises:
            NotFoundException: If sales type not found
        """
        logger.info(f"Getting sales type by name: {name}")
        sales_type = self.sales_type_repo.get_by_name(name)
        if not sales_type:
            logger.warning(f"Sales type not found: {name}")
            raise NotFoundException(f"Sales type not found: {name}")
        return self.response_schema.model_validate(sales_type)


# ========== QUOTE STATUS SERVICE ==========
class QuoteStatusService(
    BaseService[QuoteStatus, QuoteStatusCreate, QuoteStatusUpdate, QuoteStatusResponse]
):
    """
    Service for QuoteStatus lookup operations.

    Provides business logic for managing quote statuses.
    """

    def __init__(self, repository: QuoteStatusRepository, session: Session):
        """
        Initialize QuoteStatusService.

        Args:
            repository: QuoteStatusRepository instance
            session: Database session
        """
        super().__init__(repository, session, QuoteStatus, QuoteStatusResponse)
        self.quote_status_repo: QuoteStatusRepository = repository

    def validate_create(self, entity: QuoteStatus) -> None:
        """
        Validate quote status creation.

        Args:
            entity: QuoteStatus entity to validate

        Raises:
            ValidationException: If quote status name already exists
        """
        existing = self.quote_status_repo.get_by_name(entity.name)
        if existing:
            logger.warning(f"Quote status already exists: {entity.name}")
            raise ValidationException(
                f"Quote status already exists: {entity.name}",
                details={"name": entity.name, "existing_id": existing.id},
            )

    def validate_update(self, entity: QuoteStatus) -> None:
        """
        Validate quote status update.

        Args:
            entity: QuoteStatus entity to validate

        Raises:
            ValidationException: If quote status name already exists for different entity
        """
        existing = self.quote_status_repo.get_by_name(entity.name)
        if existing and existing.id != entity.id:
            logger.warning(f"Quote status name already exists: {entity.name}")
            raise ValidationException(
                f"Quote status name already exists: {entity.name}",
                details={"name": entity.name, "existing_id": existing.id},
            )

    def get_by_name(self, name: str) -> QuoteStatusResponse:
        """
        Get quote status by name.

        Args:
            name: Quote status name

        Returns:
            QuoteStatusResponse with quote status data

        Raises:
            NotFoundException: If quote status not found
        """
        logger.info(f"Getting quote status by name: {name}")
        quote_status = self.quote_status_repo.get_by_name(name)
        if not quote_status:
            logger.warning(f"Quote status not found: {name}")
            raise NotFoundException(f"Quote status not found: {name}")
        return self.response_schema.model_validate(quote_status)


# ========== ORDER STATUS SERVICE ==========
class OrderStatusService(
    BaseService[OrderStatus, OrderStatusCreate, OrderStatusUpdate, OrderStatusResponse]
):
    """
    Service for OrderStatus lookup operations.

    Provides business logic for managing order statuses.
    """

    def __init__(self, repository: OrderStatusRepository, session: Session):
        """
        Initialize OrderStatusService.

        Args:
            repository: OrderStatusRepository instance
            session: Database session
        """
        super().__init__(repository, session, OrderStatus, OrderStatusResponse)
        self.order_status_repo: OrderStatusRepository = repository

    def validate_create(self, entity: OrderStatus) -> None:
        """
        Validate order status creation.

        Args:
            entity: OrderStatus entity to validate

        Raises:
            ValidationException: If order status name already exists
        """
        existing = self.order_status_repo.get_by_name(entity.name)
        if existing:
            logger.warning(f"Order status already exists: {entity.name}")
            raise ValidationException(
                f"Order status already exists: {entity.name}",
                details={"name": entity.name, "existing_id": existing.id},
            )

    def validate_update(self, entity: OrderStatus) -> None:
        """
        Validate order status update.

        Args:
            entity: OrderStatus entity to validate

        Raises:
            ValidationException: If order status name already exists for different entity
        """
        existing = self.order_status_repo.get_by_name(entity.name)
        if existing and existing.id != entity.id:
            logger.warning(f"Order status name already exists: {entity.name}")
            raise ValidationException(
                f"Order status name already exists: {entity.name}",
                details={"name": entity.name, "existing_id": existing.id},
            )

    def get_by_name(self, name: str) -> OrderStatusResponse:
        """
        Get order status by name.

        Args:
            name: Order status name

        Returns:
            OrderStatusResponse with order status data

        Raises:
            NotFoundException: If order status not found
        """
        logger.info(f"Getting order status by name: {name}")
        order_status = self.order_status_repo.get_by_name(name)
        if not order_status:
            logger.warning(f"Order status not found: {name}")
            raise NotFoundException(f"Order status not found: {name}")
        return self.response_schema.model_validate(order_status)


# ========== PAYMENT STATUS SERVICE ==========
class PaymentStatusService(
    BaseService[PaymentStatus, PaymentStatusCreate, PaymentStatusUpdate, PaymentStatusResponse]
):
    """
    Service for PaymentStatus lookup operations.

    Provides business logic for managing payment statuses.
    """

    def __init__(self, repository: PaymentStatusRepository, session: Session):
        """
        Initialize PaymentStatusService.

        Args:
            repository: PaymentStatusRepository instance
            session: Database session
        """
        super().__init__(repository, session, PaymentStatus, PaymentStatusResponse)
        self.payment_status_repo: PaymentStatusRepository = repository

    def validate_create(self, entity: PaymentStatus) -> None:
        """
        Validate payment status creation.

        Args:
            entity: PaymentStatus entity to validate

        Raises:
            ValidationException: If payment status name already exists
        """
        existing = self.payment_status_repo.get_by_name(entity.name)
        if existing:
            logger.warning(f"Payment status already exists: {entity.name}")
            raise ValidationException(
                f"Payment status already exists: {entity.name}",
                details={"name": entity.name, "existing_id": existing.id},
            )

    def validate_update(self, entity: PaymentStatus) -> None:
        """
        Validate payment status update.

        Args:
            entity: PaymentStatus entity to validate

        Raises:
            ValidationException: If payment status name already exists for different entity
        """
        existing = self.payment_status_repo.get_by_name(entity.name)
        if existing and existing.id != entity.id:
            logger.warning(f"Payment status name already exists: {entity.name}")
            raise ValidationException(
                f"Payment status name already exists: {entity.name}",
                details={"name": entity.name, "existing_id": existing.id},
            )

    def get_by_name(self, name: str) -> PaymentStatusResponse:
        """
        Get payment status by name.

        Args:
            name: Payment status name

        Returns:
            PaymentStatusResponse with payment status data

        Raises:
            NotFoundException: If payment status not found
        """
        logger.info(f"Getting payment status by name: {name}")
        payment_status = self.payment_status_repo.get_by_name(name)
        if not payment_status:
            logger.warning(f"Payment status not found: {name}")
            raise NotFoundException(f"Payment status not found: {name}")
        return self.response_schema.model_validate(payment_status)
