"""
Lookup/reference tables REST API endpoints.

Provides CRUD operations for all 12 lookup tables:
- Countries (GET, POST, PUT, DELETE)
- Cities (GET, POST, PUT, DELETE + filter by country)
- Company Types (GET, POST, PUT, DELETE)
- Incoterm (GET, POST, PUT, DELETE)
- Currencies (GET, POST, PUT, DELETE)
- Units (GET, POST, PUT, DELETE)
- Family Types (GET, POST, PUT, DELETE)
- Matters (GET, POST, PUT, DELETE)
- Sales Types (GET, POST, PUT, DELETE)
- Quote Statuses (GET, POST, PUT, DELETE)
- Order Statuses (GET, POST, PUT, DELETE)
- Payment Statuses (GET, POST, PUT, DELETE)

Total: 84+ endpoints for comprehensive lookup management.
"""

from typing import List
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from src.backend.api.dependencies import get_database, get_current_user_id
from src.backend.services.lookups.lookup_service import (
    CountryService,
    CityService,
    CompanyTypeService,
    IncotermService,
    CurrencyService,
    UnitService,
    FamilyTypeService,
    MatterService,
    SalesTypeService,
    QuoteStatusService,
    OrderStatusService,
    PaymentStatusService,
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
from src.shared.schemas.base import MessageResponse
from src.backend.utils.logger import logger


# ========== MAIN LOOKUPS ROUTER ==========
lookups_router = APIRouter(prefix="/lookups", tags=["lookups"])


# ========== COUNTRIES SUB-ROUTER ==========
countries_router = APIRouter(prefix="/countries", tags=["countries"])


def get_country_service(db: Session = Depends(get_database)) -> CountryService:
    """
    Dependency to get CountryService.

    Args:
        db: Database session

    Returns:
        CountryService instance
    """
    repository = CountryRepository(db)
    return CountryService(repository=repository, session=db)


@countries_router.get("/", response_model=List[CountryResponse])
def get_countries(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    service: CountryService = Depends(get_country_service),
):
    """
    Get all countries with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        service: CountryService instance

    Returns:
        List of CountryResponse objects
    """
    logger.info(f"GET /lookups/countries - skip={skip}, limit={limit}")
    countries = service.get_all(skip=skip, limit=limit)
    logger.info(f"Returning {len(countries)} country(ies)")
    return countries


@countries_router.get("/{country_id}", response_model=CountryResponse)
def get_country(
    country_id: int,
    service: CountryService = Depends(get_country_service),
):
    """
    Get country by ID.

    Args:
        country_id: Country ID
        service: CountryService instance

    Returns:
        CountryResponse object
    """
    logger.info(f"GET /lookups/countries/{country_id}")
    country = service.get_by_id(country_id)
    return country


@countries_router.post("/", response_model=CountryResponse, status_code=status.HTTP_201_CREATED)
def create_country(
    country_data: CountryCreate,
    service: CountryService = Depends(get_country_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Create new country.

    Args:
        country_data: Country creation data
        service: CountryService instance
        user_id: Current user ID

    Returns:
        CountryResponse object
    """
    logger.info(f"POST /lookups/countries - name={country_data.name}")
    country = service.create(country_data, user_id)
    logger.success(f"Country created: id={country.id}")
    return country


@countries_router.put("/{country_id}", response_model=CountryResponse)
def update_country(
    country_id: int,
    country_data: CountryUpdate,
    service: CountryService = Depends(get_country_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Update existing country.

    Args:
        country_id: Country ID
        country_data: Country update data
        service: CountryService instance
        user_id: Current user ID

    Returns:
        CountryResponse object
    """
    logger.info(f"PUT /lookups/countries/{country_id}")
    country = service.update(country_id, country_data, user_id)
    logger.success(f"Country updated: id={country_id}")
    return country


@countries_router.delete("/{country_id}", response_model=MessageResponse)
def delete_country(
    country_id: int,
    service: CountryService = Depends(get_country_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Delete country.

    Args:
        country_id: Country ID
        service: CountryService instance
        user_id: Current user ID

    Returns:
        MessageResponse with success message
    """
    logger.info(f"DELETE /lookups/countries/{country_id}")
    service.delete(country_id, user_id, soft=False)  # Hard delete for lookups
    logger.success(f"Country deleted: id={country_id}")
    return MessageResponse(
        message="Country deleted successfully", details={"country_id": country_id}
    )


# ========== CITIES SUB-ROUTER ==========
cities_router = APIRouter(prefix="/cities", tags=["cities"])


def get_city_service(db: Session = Depends(get_database)) -> CityService:
    """
    Dependency to get CityService.

    Args:
        db: Database session

    Returns:
        CityService instance
    """
    repository = CityRepository(db)
    return CityService(repository=repository, session=db)


@cities_router.get("/", response_model=List[CityResponse])
def get_cities(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    country_id: int = Query(None, description="Filter by country ID"),
    service: CityService = Depends(get_city_service),
):
    """
    Get all cities with pagination and optional country filter.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        country_id: Optional country ID filter
        service: CityService instance

    Returns:
        List of CityResponse objects
    """
    logger.info(f"GET /lookups/cities - skip={skip}, limit={limit}, country_id={country_id}")
    if country_id:
        cities = service.get_by_country(country_id)
        logger.info(f"Returning {len(cities)} city(ies) for country {country_id}")
        return cities[skip : skip + limit]
    cities = service.get_all(skip=skip, limit=limit)
    logger.info(f"Returning {len(cities)} city(ies)")
    return cities


@cities_router.get("/{city_id}", response_model=CityResponse)
def get_city(
    city_id: int,
    service: CityService = Depends(get_city_service),
):
    """
    Get city by ID.

    Args:
        city_id: City ID
        service: CityService instance

    Returns:
        CityResponse object
    """
    logger.info(f"GET /lookups/cities/{city_id}")
    city = service.get_by_id(city_id)
    return city


@cities_router.post("/", response_model=CityResponse, status_code=status.HTTP_201_CREATED)
def create_city(
    city_data: CityCreate,
    service: CityService = Depends(get_city_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Create new city.

    Args:
        city_data: City creation data
        service: CityService instance
        user_id: Current user ID

    Returns:
        CityResponse object
    """
    logger.info(f"POST /lookups/cities - name={city_data.name}, country_id={city_data.country_id}")
    city = service.create(city_data, user_id)
    logger.success(f"City created: id={city.id}")
    return city


@cities_router.put("/{city_id}", response_model=CityResponse)
def update_city(
    city_id: int,
    city_data: CityUpdate,
    service: CityService = Depends(get_city_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Update existing city.

    Args:
        city_id: City ID
        city_data: City update data
        service: CityService instance
        user_id: Current user ID

    Returns:
        CityResponse object
    """
    logger.info(f"PUT /lookups/cities/{city_id}")
    city = service.update(city_id, city_data, user_id)
    logger.success(f"City updated: id={city_id}")
    return city


@cities_router.delete("/{city_id}", response_model=MessageResponse)
def delete_city(
    city_id: int,
    service: CityService = Depends(get_city_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Delete city.

    Args:
        city_id: City ID
        service: CityService instance
        user_id: Current user ID

    Returns:
        MessageResponse with success message
    """
    logger.info(f"DELETE /lookups/cities/{city_id}")
    service.delete(city_id, user_id, soft=False)  # Hard delete for lookups
    logger.success(f"City deleted: id={city_id}")
    return MessageResponse(message="City deleted successfully", details={"city_id": city_id})


# ========== COMPANY TYPES SUB-ROUTER ==========
company_types_router = APIRouter(prefix="/company-types", tags=["company-types"])


def get_company_type_service(db: Session = Depends(get_database)) -> CompanyTypeService:
    """
    Dependency to get CompanyTypeService.

    Args:
        db: Database session

    Returns:
        CompanyTypeService instance
    """
    repository = CompanyTypeRepository(db)
    return CompanyTypeService(repository=repository, session=db)


@company_types_router.get("/", response_model=List[CompanyTypeResponse])
def get_company_types(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    service: CompanyTypeService = Depends(get_company_type_service),
):
    """
    Get all company types with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        service: CompanyTypeService instance

    Returns:
        List of CompanyTypeResponse objects
    """
    logger.info(f"GET /lookups/company-types - skip={skip}, limit={limit}")
    company_types = service.get_all(skip=skip, limit=limit)
    logger.info(f"Returning {len(company_types)} company type(s)")
    return company_types


@company_types_router.get("/{company_type_id}", response_model=CompanyTypeResponse)
def get_company_type(
    company_type_id: int,
    service: CompanyTypeService = Depends(get_company_type_service),
):
    """
    Get company type by ID.

    Args:
        company_type_id: Company type ID
        service: CompanyTypeService instance

    Returns:
        CompanyTypeResponse object
    """
    logger.info(f"GET /lookups/company-types/{company_type_id}")
    company_type = service.get_by_id(company_type_id)
    return company_type


@company_types_router.post(
    "/", response_model=CompanyTypeResponse, status_code=status.HTTP_201_CREATED
)
def create_company_type(
    company_type_data: CompanyTypeCreate,
    service: CompanyTypeService = Depends(get_company_type_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Create new company type.

    Args:
        company_type_data: Company type creation data
        service: CompanyTypeService instance
        user_id: Current user ID

    Returns:
        CompanyTypeResponse object
    """
    logger.info(f"POST /lookups/company-types - name={company_type_data.name}")
    company_type = service.create(company_type_data, user_id)
    logger.success(f"Company type created: id={company_type.id}")
    return company_type


@company_types_router.put("/{company_type_id}", response_model=CompanyTypeResponse)
def update_company_type(
    company_type_id: int,
    company_type_data: CompanyTypeUpdate,
    service: CompanyTypeService = Depends(get_company_type_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Update existing company type.

    Args:
        company_type_id: Company type ID
        company_type_data: Company type update data
        service: CompanyTypeService instance
        user_id: Current user ID

    Returns:
        CompanyTypeResponse object
    """
    logger.info(f"PUT /lookups/company-types/{company_type_id}")
    company_type = service.update(company_type_id, company_type_data, user_id)
    logger.success(f"Company type updated: id={company_type_id}")
    return company_type


@company_types_router.delete("/{company_type_id}", response_model=MessageResponse)
def delete_company_type(
    company_type_id: int,
    service: CompanyTypeService = Depends(get_company_type_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Delete company type.

    Args:
        company_type_id: Company type ID
        service: CompanyTypeService instance
        user_id: Current user ID

    Returns:
        MessageResponse with success message
    """
    logger.info(f"DELETE /lookups/company-types/{company_type_id}")
    service.delete(company_type_id, user_id, soft=False)  # Hard delete for lookups
    logger.success(f"Company type deleted: id={company_type_id}")
    return MessageResponse(
        message="Company type deleted successfully", details={"company_type_id": company_type_id}
    )


# ========== INCOTERMS SUB-ROUTER ==========
incoterms_router = APIRouter(prefix="/incoterms", tags=["incoterms"])


def get_incoterms_service(db: Session = Depends(get_database)) -> IncotermService:
    """
    Dependency to get IncotermService.

    Args:
        db: Database session

    Returns:
        IncotermService instance
    """
    repository = IncotermRepository(db)
    return IncotermService(repository=repository, session=db)


@incoterms_router.get("/", response_model=List[IncotermResponse])
def get_incoterms(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    service: IncotermService = Depends(get_incoterms_service),
):
    """
    Get all Incoterm with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        service: IncotermService instance

    Returns:
        List of IncotermResponse objects
    """
    logger.info(f"GET /lookups/incoterms - skip={skip}, limit={limit}")
    incoterms = service.get_all(skip=skip, limit=limit)
    logger.info(f"Returning {len(incoterms)} Incoterm(s)")
    return incoterms


@incoterms_router.get("/{incoterm_id}", response_model=IncotermResponse)
def get_incoterm(
    incoterm_id: int,
    service: IncotermService = Depends(get_incoterms_service),
):
    """
    Get Incoterm by ID.

    Args:
        incoterm_id: Incoterm ID
        service: IncotermService instance

    Returns:
        IncotermResponse object
    """
    logger.info(f"GET /lookups/incoterms/{incoterm_id}")
    incoterm = service.get_by_id(incoterm_id)
    return incoterm


@incoterms_router.post("/", response_model=IncotermResponse, status_code=status.HTTP_201_CREATED)
def create_incoterm(
    incoterm_data: IncotermCreate,
    service: IncotermService = Depends(get_incoterms_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Create new Incoterm.

    Args:
        incoterm_data: Incoterm creation data
        service: IncotermService instance
        user_id: Current user ID

    Returns:
        IncotermResponse object
    """
    logger.info(f"POST /lookups/incoterms - code={incoterm_data.code}")
    incoterm = service.create(incoterm_data, user_id)
    logger.success(f"Incoterm created: id={incoterm.id}")
    return incoterm


@incoterms_router.put("/{incoterm_id}", response_model=IncotermResponse)
def update_incoterm(
    incoterm_id: int,
    incoterm_data: IncotermUpdate,
    service: IncotermService = Depends(get_incoterms_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Update existing Incoterm.

    Args:
        incoterm_id: Incoterm ID
        incoterm_data: Incoterm update data
        service: IncotermService instance
        user_id: Current user ID

    Returns:
        IncotermResponse object
    """
    logger.info(f"PUT /lookups/incoterms/{incoterm_id}")
    incoterm = service.update(incoterm_id, incoterm_data, user_id)
    logger.success(f"Incoterm updated: id={incoterm_id}")
    return incoterm


@incoterms_router.delete("/{incoterm_id}", response_model=MessageResponse)
def delete_incoterm(
    incoterm_id: int,
    service: IncotermService = Depends(get_incoterms_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Delete Incoterm.

    Args:
        incoterm_id: Incoterm ID
        service: IncotermService instance
        user_id: Current user ID

    Returns:
        MessageResponse with success message
    """
    logger.info(f"DELETE /lookups/incoterms/{incoterm_id}")
    service.delete(incoterm_id, user_id, soft=False)  # Hard delete for lookups
    logger.success(f"Incoterm deleted: id={incoterm_id}")
    return MessageResponse(
        message="Incoterm deleted successfully", details={"incoterm_id": incoterm_id}
    )


# ========== CURRENCIES SUB-ROUTER ==========
currencies_router = APIRouter(prefix="/currencies", tags=["currencies"])


def get_currency_service(db: Session = Depends(get_database)) -> CurrencyService:
    """
    Dependency to get CurrencyService.

    Args:
        db: Database session

    Returns:
        CurrencyService instance
    """
    repository = CurrencyRepository(db)
    return CurrencyService(repository=repository, session=db)


@currencies_router.get("/", response_model=List[CurrencyResponse])
def get_currencies(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    service: CurrencyService = Depends(get_currency_service),
):
    """
    Get all currencies with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        service: CurrencyService instance

    Returns:
        List of CurrencyResponse objects
    """
    logger.info(f"GET /lookups/currencies - skip={skip}, limit={limit}")
    currencies = service.get_all(skip=skip, limit=limit)
    logger.info(f"Returning {len(currencies)} currency(ies)")
    return currencies


@currencies_router.get("/{currency_id}", response_model=CurrencyResponse)
def get_currency(
    currency_id: int,
    service: CurrencyService = Depends(get_currency_service),
):
    """
    Get currency by ID.

    Args:
        currency_id: Currency ID
        service: CurrencyService instance

    Returns:
        CurrencyResponse object
    """
    logger.info(f"GET /lookups/currencies/{currency_id}")
    currency = service.get_by_id(currency_id)
    return currency


@currencies_router.post("/", response_model=CurrencyResponse, status_code=status.HTTP_201_CREATED)
def create_currency(
    currency_data: CurrencyCreate,
    service: CurrencyService = Depends(get_currency_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Create new currency.

    Args:
        currency_data: Currency creation data
        service: CurrencyService instance
        user_id: Current user ID

    Returns:
        CurrencyResponse object
    """
    logger.info(f"POST /lookups/currencies - code={currency_data.code}")
    currency = service.create(currency_data, user_id)
    logger.success(f"Currency created: id={currency.id}")
    return currency


@currencies_router.put("/{currency_id}", response_model=CurrencyResponse)
def update_currency(
    currency_id: int,
    currency_data: CurrencyUpdate,
    service: CurrencyService = Depends(get_currency_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Update existing currency.

    Args:
        currency_id: Currency ID
        currency_data: Currency update data
        service: CurrencyService instance
        user_id: Current user ID

    Returns:
        CurrencyResponse object
    """
    logger.info(f"PUT /lookups/currencies/{currency_id}")
    currency = service.update(currency_id, currency_data, user_id)
    logger.success(f"Currency updated: id={currency_id}")
    return currency


@currencies_router.delete("/{currency_id}", response_model=MessageResponse)
def delete_currency(
    currency_id: int,
    service: CurrencyService = Depends(get_currency_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Delete currency.

    Args:
        currency_id: Currency ID
        service: CurrencyService instance
        user_id: Current user ID

    Returns:
        MessageResponse with success message
    """
    logger.info(f"DELETE /lookups/currencies/{currency_id}")
    service.delete(currency_id, user_id, soft=False)  # Hard delete for lookups
    logger.success(f"Currency deleted: id={currency_id}")
    return MessageResponse(
        message="Currency deleted successfully", details={"currency_id": currency_id}
    )


# ========== UNITS SUB-ROUTER ==========
units_router = APIRouter(prefix="/units", tags=["units"])


def get_unit_service(db: Session = Depends(get_database)) -> UnitService:
    """
    Dependency to get UnitService.

    Args:
        db: Database session

    Returns:
        UnitService instance
    """
    repository = UnitRepository(db)
    return UnitService(repository=repository, session=db)


@units_router.get("/", response_model=List[UnitResponse])
def get_units(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    service: UnitService = Depends(get_unit_service),
):
    """
    Get all units with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        service: UnitService instance

    Returns:
        List of UnitResponse objects
    """
    logger.info(f"GET /lookups/units - skip={skip}, limit={limit}")
    units = service.get_all(skip=skip, limit=limit)
    logger.info(f"Returning {len(units)} unit(s)")
    return units


@units_router.get("/{unit_id}", response_model=UnitResponse)
def get_unit(
    unit_id: int,
    service: UnitService = Depends(get_unit_service),
):
    """
    Get unit by ID.

    Args:
        unit_id: Unit ID
        service: UnitService instance

    Returns:
        UnitResponse object
    """
    logger.info(f"GET /lookups/units/{unit_id}")
    unit = service.get_by_id(unit_id)
    return unit


@units_router.post("/", response_model=UnitResponse, status_code=status.HTTP_201_CREATED)
def create_unit(
    unit_data: UnitCreate,
    service: UnitService = Depends(get_unit_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Create new unit.

    Args:
        unit_data: Unit creation data
        service: UnitService instance
        user_id: Current user ID

    Returns:
        UnitResponse object
    """
    logger.info(f"POST /lookups/units - code={unit_data.code}")
    unit = service.create(unit_data, user_id)
    logger.success(f"Unit created: id={unit.id}")
    return unit


@units_router.put("/{unit_id}", response_model=UnitResponse)
def update_unit(
    unit_id: int,
    unit_data: UnitUpdate,
    service: UnitService = Depends(get_unit_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Update existing unit.

    Args:
        unit_id: Unit ID
        unit_data: Unit update data
        service: UnitService instance
        user_id: Current user ID

    Returns:
        UnitResponse object
    """
    logger.info(f"PUT /lookups/units/{unit_id}")
    unit = service.update(unit_id, unit_data, user_id)
    logger.success(f"Unit updated: id={unit_id}")
    return unit


@units_router.delete("/{unit_id}", response_model=MessageResponse)
def delete_unit(
    unit_id: int,
    service: UnitService = Depends(get_unit_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Delete unit.

    Args:
        unit_id: Unit ID
        service: UnitService instance
        user_id: Current user ID

    Returns:
        MessageResponse with success message
    """
    logger.info(f"DELETE /lookups/units/{unit_id}")
    service.delete(unit_id, user_id, soft=False)  # Hard delete for lookups
    logger.success(f"Unit deleted: id={unit_id}")
    return MessageResponse(message="Unit deleted successfully", details={"unit_id": unit_id})


# ========== FAMILY TYPES SUB-ROUTER ==========
family_types_router = APIRouter(prefix="/family-types", tags=["family-types"])


def get_family_type_service(db: Session = Depends(get_database)) -> FamilyTypeService:
    """
    Dependency to get FamilyTypeService.

    Args:
        db: Database session

    Returns:
        FamilyTypeService instance
    """
    repository = FamilyTypeRepository(db)
    return FamilyTypeService(repository=repository, session=db)


@family_types_router.get("/", response_model=List[FamilyTypeResponse])
def get_family_types(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    service: FamilyTypeService = Depends(get_family_type_service),
):
    """
    Get all family types with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        service: FamilyTypeService instance

    Returns:
        List of FamilyTypeResponse objects
    """
    logger.info(f"GET /lookups/family-types - skip={skip}, limit={limit}")
    family_types = service.get_all(skip=skip, limit=limit)
    logger.info(f"Returning {len(family_types)} family type(s)")
    return family_types


@family_types_router.get("/{family_type_id}", response_model=FamilyTypeResponse)
def get_family_type(
    family_type_id: int,
    service: FamilyTypeService = Depends(get_family_type_service),
):
    """
    Get family type by ID.

    Args:
        family_type_id: Family type ID
        service: FamilyTypeService instance

    Returns:
        FamilyTypeResponse object
    """
    logger.info(f"GET /lookups/family-types/{family_type_id}")
    family_type = service.get_by_id(family_type_id)
    return family_type


@family_types_router.post(
    "/", response_model=FamilyTypeResponse, status_code=status.HTTP_201_CREATED
)
def create_family_type(
    family_type_data: FamilyTypeCreate,
    service: FamilyTypeService = Depends(get_family_type_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Create new family type.

    Args:
        family_type_data: Family type creation data
        service: FamilyTypeService instance
        user_id: Current user ID

    Returns:
        FamilyTypeResponse object
    """
    logger.info(f"POST /lookups/family-types - name={family_type_data.name}")
    family_type = service.create(family_type_data, user_id)
    logger.success(f"Family type created: id={family_type.id}")
    return family_type


@family_types_router.put("/{family_type_id}", response_model=FamilyTypeResponse)
def update_family_type(
    family_type_id: int,
    family_type_data: FamilyTypeUpdate,
    service: FamilyTypeService = Depends(get_family_type_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Update existing family type.

    Args:
        family_type_id: Family type ID
        family_type_data: Family type update data
        service: FamilyTypeService instance
        user_id: Current user ID

    Returns:
        FamilyTypeResponse object
    """
    logger.info(f"PUT /lookups/family-types/{family_type_id}")
    family_type = service.update(family_type_id, family_type_data, user_id)
    logger.success(f"Family type updated: id={family_type_id}")
    return family_type


@family_types_router.delete("/{family_type_id}", response_model=MessageResponse)
def delete_family_type(
    family_type_id: int,
    service: FamilyTypeService = Depends(get_family_type_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Delete family type.

    Args:
        family_type_id: Family type ID
        service: FamilyTypeService instance
        user_id: Current user ID

    Returns:
        MessageResponse with success message
    """
    logger.info(f"DELETE /lookups/family-types/{family_type_id}")
    service.delete(family_type_id, user_id, soft=False)  # Hard delete for lookups
    logger.success(f"Family type deleted: id={family_type_id}")
    return MessageResponse(
        message="Family type deleted successfully", details={"family_type_id": family_type_id}
    )


# ========== MATTERS SUB-ROUTER ==========
matters_router = APIRouter(prefix="/matters", tags=["matters"])


def get_matter_service(db: Session = Depends(get_database)) -> MatterService:
    """
    Dependency to get MatterService.

    Args:
        db: Database session

    Returns:
        MatterService instance
    """
    repository = MatterRepository(db)
    return MatterService(repository=repository, session=db)


@matters_router.get("/", response_model=List[MatterResponse])
def get_matters(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    service: MatterService = Depends(get_matter_service),
):
    """
    Get all matters with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        service: MatterService instance

    Returns:
        List of MatterResponse objects
    """
    logger.info(f"GET /lookups/matters - skip={skip}, limit={limit}")
    matters = service.get_all(skip=skip, limit=limit)
    logger.info(f"Returning {len(matters)} matter(s)")
    return matters


@matters_router.get("/{matter_id}", response_model=MatterResponse)
def get_matter(
    matter_id: int,
    service: MatterService = Depends(get_matter_service),
):
    """
    Get matter by ID.

    Args:
        matter_id: Matter ID
        service: MatterService instance

    Returns:
        MatterResponse object
    """
    logger.info(f"GET /lookups/matters/{matter_id}")
    matter = service.get_by_id(matter_id)
    return matter


@matters_router.post("/", response_model=MatterResponse, status_code=status.HTTP_201_CREATED)
def create_matter(
    matter_data: MatterCreate,
    service: MatterService = Depends(get_matter_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Create new matter.

    Args:
        matter_data: Matter creation data
        service: MatterService instance
        user_id: Current user ID

    Returns:
        MatterResponse object
    """
    logger.info(f"POST /lookups/matters - name={matter_data.name}")
    matter = service.create(matter_data, user_id)
    logger.success(f"Matter created: id={matter.id}")
    return matter


@matters_router.put("/{matter_id}", response_model=MatterResponse)
def update_matter(
    matter_id: int,
    matter_data: MatterUpdate,
    service: MatterService = Depends(get_matter_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Update existing matter.

    Args:
        matter_id: Matter ID
        matter_data: Matter update data
        service: MatterService instance
        user_id: Current user ID

    Returns:
        MatterResponse object
    """
    logger.info(f"PUT /lookups/matters/{matter_id}")
    matter = service.update(matter_id, matter_data, user_id)
    logger.success(f"Matter updated: id={matter_id}")
    return matter


@matters_router.delete("/{matter_id}", response_model=MessageResponse)
def delete_matter(
    matter_id: int,
    service: MatterService = Depends(get_matter_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Delete matter.

    Args:
        matter_id: Matter ID
        service: MatterService instance
        user_id: Current user ID

    Returns:
        MessageResponse with success message
    """
    logger.info(f"DELETE /lookups/matters/{matter_id}")
    service.delete(matter_id, user_id, soft=False)  # Hard delete for lookups
    logger.success(f"Matter deleted: id={matter_id}")
    return MessageResponse(message="Matter deleted successfully", details={"matter_id": matter_id})


# ========== SALES TYPES SUB-ROUTER ==========
sales_types_router = APIRouter(prefix="/sales-types", tags=["sales-types"])


def get_sales_type_service(db: Session = Depends(get_database)) -> SalesTypeService:
    """
    Dependency to get SalesTypeService.

    Args:
        db: Database session

    Returns:
        SalesTypeService instance
    """
    repository = SalesTypeRepository(db)
    return SalesTypeService(repository=repository, session=db)


@sales_types_router.get("/", response_model=List[SalesTypeResponse])
def get_sales_types(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    service: SalesTypeService = Depends(get_sales_type_service),
):
    """
    Get all sales types with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        service: SalesTypeService instance

    Returns:
        List of SalesTypeResponse objects
    """
    logger.info(f"GET /lookups/sales-types - skip={skip}, limit={limit}")
    sales_types = service.get_all(skip=skip, limit=limit)
    logger.info(f"Returning {len(sales_types)} sales type(s)")
    return sales_types


@sales_types_router.get("/{sales_type_id}", response_model=SalesTypeResponse)
def get_sales_type(
    sales_type_id: int,
    service: SalesTypeService = Depends(get_sales_type_service),
):
    """
    Get sales type by ID.

    Args:
        sales_type_id: Sales type ID
        service: SalesTypeService instance

    Returns:
        SalesTypeResponse object
    """
    logger.info(f"GET /lookups/sales-types/{sales_type_id}")
    sales_type = service.get_by_id(sales_type_id)
    return sales_type


@sales_types_router.post("/", response_model=SalesTypeResponse, status_code=status.HTTP_201_CREATED)
def create_sales_type(
    sales_type_data: SalesTypeCreate,
    service: SalesTypeService = Depends(get_sales_type_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Create new sales type.

    Args:
        sales_type_data: Sales type creation data
        service: SalesTypeService instance
        user_id: Current user ID

    Returns:
        SalesTypeResponse object
    """
    logger.info(f"POST /lookups/sales-types - name={sales_type_data.name}")
    sales_type = service.create(sales_type_data, user_id)
    logger.success(f"Sales type created: id={sales_type.id}")
    return sales_type


@sales_types_router.put("/{sales_type_id}", response_model=SalesTypeResponse)
def update_sales_type(
    sales_type_id: int,
    sales_type_data: SalesTypeUpdate,
    service: SalesTypeService = Depends(get_sales_type_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Update existing sales type.

    Args:
        sales_type_id: Sales type ID
        sales_type_data: Sales type update data
        service: SalesTypeService instance
        user_id: Current user ID

    Returns:
        SalesTypeResponse object
    """
    logger.info(f"PUT /lookups/sales-types/{sales_type_id}")
    sales_type = service.update(sales_type_id, sales_type_data, user_id)
    logger.success(f"Sales type updated: id={sales_type_id}")
    return sales_type


@sales_types_router.delete("/{sales_type_id}", response_model=MessageResponse)
def delete_sales_type(
    sales_type_id: int,
    service: SalesTypeService = Depends(get_sales_type_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Delete sales type.

    Args:
        sales_type_id: Sales type ID
        service: SalesTypeService instance
        user_id: Current user ID

    Returns:
        MessageResponse with success message
    """
    logger.info(f"DELETE /lookups/sales-types/{sales_type_id}")
    service.delete(sales_type_id, user_id, soft=False)  # Hard delete for lookups
    logger.success(f"Sales type deleted: id={sales_type_id}")
    return MessageResponse(
        message="Sales type deleted successfully", details={"sales_type_id": sales_type_id}
    )


# ========== QUOTE STATUSES SUB-ROUTER ==========
quote_statuses_router = APIRouter(prefix="/quote-statuses", tags=["quote-statuses"])


def get_quote_status_service(db: Session = Depends(get_database)) -> QuoteStatusService:
    """
    Dependency to get QuoteStatusService.

    Args:
        db: Database session

    Returns:
        QuoteStatusService instance
    """
    repository = QuoteStatusRepository(db)
    return QuoteStatusService(repository=repository, session=db)


@quote_statuses_router.get("/", response_model=List[QuoteStatusResponse])
def get_quote_statuses(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    service: QuoteStatusService = Depends(get_quote_status_service),
):
    """
    Get all quote statuses with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        service: QuoteStatusService instance

    Returns:
        List of QuoteStatusResponse objects
    """
    logger.info(f"GET /lookups/quote-statuses - skip={skip}, limit={limit}")
    quote_statuses = service.get_all(skip=skip, limit=limit)
    logger.info(f"Returning {len(quote_statuses)} quote status(es)")
    return quote_statuses


@quote_statuses_router.get("/{quote_status_id}", response_model=QuoteStatusResponse)
def get_quote_status(
    quote_status_id: int,
    service: QuoteStatusService = Depends(get_quote_status_service),
):
    """
    Get quote status by ID.

    Args:
        quote_status_id: Quote status ID
        service: QuoteStatusService instance

    Returns:
        QuoteStatusResponse object
    """
    logger.info(f"GET /lookups/quote-statuses/{quote_status_id}")
    quote_status = service.get_by_id(quote_status_id)
    return quote_status


@quote_statuses_router.post(
    "/", response_model=QuoteStatusResponse, status_code=status.HTTP_201_CREATED
)
def create_quote_status(
    quote_status_data: QuoteStatusCreate,
    service: QuoteStatusService = Depends(get_quote_status_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Create new quote status.

    Args:
        quote_status_data: Quote status creation data
        service: QuoteStatusService instance
        user_id: Current user ID

    Returns:
        QuoteStatusResponse object
    """
    logger.info(f"POST /lookups/quote-statuses - name={quote_status_data.name}")
    quote_status = service.create(quote_status_data, user_id)
    logger.success(f"Quote status created: id={quote_status.id}")
    return quote_status


@quote_statuses_router.put("/{quote_status_id}", response_model=QuoteStatusResponse)
def update_quote_status(
    quote_status_id: int,
    quote_status_data: QuoteStatusUpdate,
    service: QuoteStatusService = Depends(get_quote_status_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Update existing quote status.

    Args:
        quote_status_id: Quote status ID
        quote_status_data: Quote status update data
        service: QuoteStatusService instance
        user_id: Current user ID

    Returns:
        QuoteStatusResponse object
    """
    logger.info(f"PUT /lookups/quote-statuses/{quote_status_id}")
    quote_status = service.update(quote_status_id, quote_status_data, user_id)
    logger.success(f"Quote status updated: id={quote_status_id}")
    return quote_status


@quote_statuses_router.delete("/{quote_status_id}", response_model=MessageResponse)
def delete_quote_status(
    quote_status_id: int,
    service: QuoteStatusService = Depends(get_quote_status_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Delete quote status.

    Args:
        quote_status_id: Quote status ID
        service: QuoteStatusService instance
        user_id: Current user ID

    Returns:
        MessageResponse with success message
    """
    logger.info(f"DELETE /lookups/quote-statuses/{quote_status_id}")
    service.delete(quote_status_id, user_id, soft=False)  # Hard delete for lookups
    logger.success(f"Quote status deleted: id={quote_status_id}")
    return MessageResponse(
        message="Quote status deleted successfully", details={"quote_status_id": quote_status_id}
    )


# ========== ORDER STATUSES SUB-ROUTER ==========
order_statuses_router = APIRouter(prefix="/order-statuses", tags=["order-statuses"])


def get_order_status_service(db: Session = Depends(get_database)) -> OrderStatusService:
    """
    Dependency to get OrderStatusService.

    Args:
        db: Database session

    Returns:
        OrderStatusService instance
    """
    repository = OrderStatusRepository(db)
    return OrderStatusService(repository=repository, session=db)


@order_statuses_router.get("/", response_model=List[OrderStatusResponse])
def get_order_statuses(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    service: OrderStatusService = Depends(get_order_status_service),
):
    """
    Get all order statuses with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        service: OrderStatusService instance

    Returns:
        List of OrderStatusResponse objects
    """
    logger.info(f"GET /lookups/order-statuses - skip={skip}, limit={limit}")
    order_statuses = service.get_all(skip=skip, limit=limit)
    logger.info(f"Returning {len(order_statuses)} order status(es)")
    return order_statuses


@order_statuses_router.get("/{order_status_id}", response_model=OrderStatusResponse)
def get_order_status(
    order_status_id: int,
    service: OrderStatusService = Depends(get_order_status_service),
):
    """
    Get order status by ID.

    Args:
        order_status_id: Order status ID
        service: OrderStatusService instance

    Returns:
        OrderStatusResponse object
    """
    logger.info(f"GET /lookups/order-statuses/{order_status_id}")
    order_status = service.get_by_id(order_status_id)
    return order_status


@order_statuses_router.post(
    "/", response_model=OrderStatusResponse, status_code=status.HTTP_201_CREATED
)
def create_order_status(
    order_status_data: OrderStatusCreate,
    service: OrderStatusService = Depends(get_order_status_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Create new order status.

    Args:
        order_status_data: Order status creation data
        service: OrderStatusService instance
        user_id: Current user ID

    Returns:
        OrderStatusResponse object
    """
    logger.info(f"POST /lookups/order-statuses - name={order_status_data.name}")
    order_status = service.create(order_status_data, user_id)
    logger.success(f"Order status created: id={order_status.id}")
    return order_status


@order_statuses_router.put("/{order_status_id}", response_model=OrderStatusResponse)
def update_order_status(
    order_status_id: int,
    order_status_data: OrderStatusUpdate,
    service: OrderStatusService = Depends(get_order_status_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Update existing order status.

    Args:
        order_status_id: Order status ID
        order_status_data: Order status update data
        service: OrderStatusService instance
        user_id: Current user ID

    Returns:
        OrderStatusResponse object
    """
    logger.info(f"PUT /lookups/order-statuses/{order_status_id}")
    order_status = service.update(order_status_id, order_status_data, user_id)
    logger.success(f"Order status updated: id={order_status_id}")
    return order_status


@order_statuses_router.delete("/{order_status_id}", response_model=MessageResponse)
def delete_order_status(
    order_status_id: int,
    service: OrderStatusService = Depends(get_order_status_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Delete order status.

    Args:
        order_status_id: Order status ID
        service: OrderStatusService instance
        user_id: Current user ID

    Returns:
        MessageResponse with success message
    """
    logger.info(f"DELETE /lookups/order-statuses/{order_status_id}")
    service.delete(order_status_id, user_id, soft=False)  # Hard delete for lookups
    logger.success(f"Order status deleted: id={order_status_id}")
    return MessageResponse(
        message="Order status deleted successfully", details={"order_status_id": order_status_id}
    )


# ========== PAYMENT STATUSES SUB-ROUTER ==========
payment_statuses_router = APIRouter(prefix="/payment-statuses", tags=["payment-statuses"])


def get_payment_status_service(db: Session = Depends(get_database)) -> PaymentStatusService:
    """
    Dependency to get PaymentStatusService.

    Args:
        db: Database session

    Returns:
        PaymentStatusService instance
    """
    repository = PaymentStatusRepository(db)
    return PaymentStatusService(repository=repository, session=db)


@payment_statuses_router.get("/", response_model=List[PaymentStatusResponse])
def get_payment_statuses(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    service: PaymentStatusService = Depends(get_payment_status_service),
):
    """
    Get all payment statuses with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        service: PaymentStatusService instance

    Returns:
        List of PaymentStatusResponse objects
    """
    logger.info(f"GET /lookups/payment-statuses - skip={skip}, limit={limit}")
    payment_statuses = service.get_all(skip=skip, limit=limit)
    logger.info(f"Returning {len(payment_statuses)} payment status(es)")
    return payment_statuses


@payment_statuses_router.get("/{payment_status_id}", response_model=PaymentStatusResponse)
def get_payment_status(
    payment_status_id: int,
    service: PaymentStatusService = Depends(get_payment_status_service),
):
    """
    Get payment status by ID.

    Args:
        payment_status_id: Payment status ID
        service: PaymentStatusService instance

    Returns:
        PaymentStatusResponse object
    """
    logger.info(f"GET /lookups/payment-statuses/{payment_status_id}")
    payment_status = service.get_by_id(payment_status_id)
    return payment_status


@payment_statuses_router.post(
    "/", response_model=PaymentStatusResponse, status_code=status.HTTP_201_CREATED
)
def create_payment_status(
    payment_status_data: PaymentStatusCreate,
    service: PaymentStatusService = Depends(get_payment_status_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Create new payment status.

    Args:
        payment_status_data: Payment status creation data
        service: PaymentStatusService instance
        user_id: Current user ID

    Returns:
        PaymentStatusResponse object
    """
    logger.info(f"POST /lookups/payment-statuses - name={payment_status_data.name}")
    payment_status = service.create(payment_status_data, user_id)
    logger.success(f"Payment status created: id={payment_status.id}")
    return payment_status


@payment_statuses_router.put("/{payment_status_id}", response_model=PaymentStatusResponse)
def update_payment_status(
    payment_status_id: int,
    payment_status_data: PaymentStatusUpdate,
    service: PaymentStatusService = Depends(get_payment_status_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Update existing payment status.

    Args:
        payment_status_id: Payment status ID
        payment_status_data: Payment status update data
        service: PaymentStatusService instance
        user_id: Current user ID

    Returns:
        PaymentStatusResponse object
    """
    logger.info(f"PUT /lookups/payment-statuses/{payment_status_id}")
    payment_status = service.update(payment_status_id, payment_status_data, user_id)
    logger.success(f"Payment status updated: id={payment_status_id}")
    return payment_status


@payment_statuses_router.delete("/{payment_status_id}", response_model=MessageResponse)
def delete_payment_status(
    payment_status_id: int,
    service: PaymentStatusService = Depends(get_payment_status_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Delete payment status.

    Args:
        payment_status_id: Payment status ID
        service: PaymentStatusService instance
        user_id: Current user ID

    Returns:
        MessageResponse with success message
    """
    logger.info(f"DELETE /lookups/payment-statuses/{payment_status_id}")
    service.delete(payment_status_id, user_id, soft=False)  # Hard delete for lookups
    logger.success(f"Payment status deleted: id={payment_status_id}")
    return MessageResponse(
        message="Payment status deleted successfully",
        details={"payment_status_id": payment_status_id},
    )


# ========== INCLUDE ALL SUB-ROUTERS IN MAIN LOOKUPS ROUTER ==========
lookups_router.include_router(countries_router)
lookups_router.include_router(cities_router)
lookups_router.include_router(company_types_router)
lookups_router.include_router(incoterms_router)
lookups_router.include_router(currencies_router)
lookups_router.include_router(units_router)
lookups_router.include_router(family_types_router)
lookups_router.include_router(matters_router)
lookups_router.include_router(sales_types_router)
lookups_router.include_router(quote_statuses_router)
lookups_router.include_router(order_statuses_router)
lookups_router.include_router(payment_statuses_router)
