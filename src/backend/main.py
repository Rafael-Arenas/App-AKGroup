"""
FastAPI Application - Sistema de Gestión Empresarial AK Group.

Punto de entrada principal de la API REST del backend.
"""

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.backend.api import error_handlers
from src.backend.api.v1 import (  # noqa: F401
    companies,
    products,
    addresses,
    contacts,
    company_ruts,
    services,
    staff,
    notes,
    quotes,
    orders,
    deliveries,
    invoices,
    lookups,
)
from src.backend.config.settings import settings
from src.backend.database.engine import engine
from src.backend.models.base.base import Base
from src.backend.exceptions.base import AppException, DatabaseException
from src.backend.exceptions.repository import NotFoundException, DuplicateException
from src.backend.exceptions.service import ValidationException, BusinessRuleException
from src.backend.utils.logger import logger

# Import all models for table creation
from src.backend.models.core import (  # noqa: F401
    Company,
    CompanyRut,
    Branch,
    Product,
    ProductComponent,
)
from src.backend.models.lookups.lookups import CompanyType, Unit  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestión del ciclo de vida de la aplicación.

    Ejecuta tareas de inicialización y limpieza.

    Args:
        app: Instancia de FastAPI

    Yields:
        None durante la ejecución de la aplicación
    """
    # Startup
    logger.info("🚀 Iniciando aplicación FastAPI")
    logger.info(f"📊 Base de datos: {settings.database_type}")
    logger.info(f"🔧 Entorno: {settings.environment}")

    # Crear tablas si no existen (solo para desarrollo)
    if settings.environment == "development":
        logger.info("🔨 Creando tablas de base de datos...")
        Base.metadata.create_all(bind=engine)
        logger.success("✅ Tablas creadas exitosamente")

    yield

    # Shutdown
    logger.info("🛑 Cerrando aplicación FastAPI")
    engine.dispose()
    logger.success("✅ Conexiones de base de datos cerradas")


# Crear instancia de FastAPI
app = FastAPI(
    title="AK Group - Sistema de Gestión Empresarial",
    description="""
    API REST para el sistema de gestión empresarial de AK Group.

    ## Características principales:

    * **Gestión de Empresas**: CRUD completo de empresas, sucursales y RUTs
    * **Gestión de Productos**: CRUD de productos (ARTICLE y NOMENCLATURE)
    * **BOM (Bill of Materials)**: Gestión de componentes y cálculo de costos
    * **Búsqueda**: Endpoints de búsqueda por diferentes criterios
    * **Auditoría**: Tracking de creación y actualización de registros
    * **Soft Delete**: Eliminación lógica de registros

    ## Autenticación

    Por ahora, la API usa un user_id fijo (1) para testing.
    TODO: Implementar autenticación real.
    """,
    version="1.0.0",
    contact={
        "name": "AK Group",
        "email": "dev@akgroup.com",
    },
    license_info={
        "name": "Proprietary",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# ============================================================================
# MIDDLEWARE
# ============================================================================

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

app.add_exception_handler(NotFoundException, error_handlers.not_found_exception_handler)
app.add_exception_handler(DuplicateException, error_handlers.duplicate_exception_handler)
app.add_exception_handler(ValidationException, error_handlers.validation_exception_handler)
app.add_exception_handler(BusinessRuleException, error_handlers.business_rule_exception_handler)
app.add_exception_handler(DatabaseException, error_handlers.database_exception_handler)
app.add_exception_handler(AppException, error_handlers.app_exception_handler)


# ============================================================================
# ROUTERS
# ============================================================================

# Incluir routers de API v1
app.include_router(
    companies.router,
    prefix="/api/v1",
    tags=["companies"]
)

app.include_router(
    products.router,
    prefix="/api/v1",
    tags=["products"]
)

app.include_router(
    addresses.router,
    prefix="/api/v1",
    tags=["addresses"]
)

app.include_router(
    contacts.router,
    prefix="/api/v1",
    tags=["contacts"]
)

app.include_router(
    company_ruts.router,
    prefix="/api/v1",
    tags=["company-ruts"]
)

app.include_router(
    services.router,
    prefix="/api/v1",
    tags=["services"]
)

app.include_router(
    staff.router,
    prefix="/api/v1",
    tags=["staff"]
)

app.include_router(
    notes.router,
    prefix="/api/v1",
    tags=["notes"]
)

app.include_router(
    quotes.router,
    prefix="/api/v1",
    tags=["quotes"]
)

app.include_router(
    orders.router,
    prefix="/api/v1",
    tags=["orders"]
)

app.include_router(
    deliveries.deliveries_router,
    prefix="/api/v1",
    tags=["deliveries"]
)

app.include_router(
    invoices.invoices_router,
    prefix="/api/v1",
    tags=["invoices"]
)

app.include_router(
    lookups.lookups_router,
    prefix="/api/v1",
    tags=["lookups"]
)


# ============================================================================
# ENDPOINTS RAÍZ
# ============================================================================

@app.get("/", tags=["root"])
def root() -> dict[str, Any]:
    """
    Endpoint raíz - Información básica de la API.

    Returns:
        Información sobre la API y enlaces a documentación

    Example:
        GET /
        Response:
        {
            "message": "AK Group - Sistema de Gestión Empresarial API",
            "version": "1.0.0",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    """
    return {
        "message": "AK Group - Sistema de Gestión Empresarial API",
        "version": "1.0.0",
        "environment": settings.environment,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }


@app.get("/health", tags=["health"], status_code=status.HTTP_200_OK)
def health_check() -> dict[str, Any]:
    """
    Health check endpoint - Verifica el estado de la aplicación.

    Returns:
        Estado de la aplicación y base de datos

    Example:
        GET /health
        Response:
        {
            "status": "healthy",
            "database": "connected",
            "version": "1.0.0"
        }
    """
    # Verificar conexión a base de datos
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        logger.error(f"Health check falló: {e}")
        db_status = "disconnected"

    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "database": db_status,
        "database_type": settings.database_type,
        "environment": settings.environment,
        "version": "1.0.0",
    }


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Any) -> JSONResponse:
    """
    Manejador para rutas no encontradas.

    Args:
        request: Request de FastAPI
        exc: Excepción de ruta no encontrada

    Returns:
        JSONResponse con error 404
    """
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": "Not Found",
            "message": f"Ruta no encontrada: {request.url.path}",
            "details": {
                "method": request.method,
                "path": request.url.path,
            }
        }
    )


if __name__ == "__main__":
    import uvicorn

    logger.info("🚀 Iniciando servidor de desarrollo...")
    uvicorn.run(
        "src.backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level=settings.log_level.lower(),
    )
