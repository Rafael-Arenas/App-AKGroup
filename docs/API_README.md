# AK Group - API REST

API REST para el sistema de gestión empresarial de AK Group, implementada con FastAPI.

## Inicio Rápido

### 1. Configurar el entorno

```bash
# Copiar el archivo de configuración
cp .env.example .env

# Instalar dependencias con Poetry
poetry install

# Activar el entorno virtual
poetry shell
```

### 2. Ejecutar la aplicación

```bash
# Opción 1: Usando Poetry
poetry run python main.py

# Opción 2: Dentro del shell de Poetry
python main.py

# Opción 3: Con uvicorn directamente
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en: http://localhost:8000

## Documentación

Una vez que la API esté ejecutándose, puedes acceder a:

- **Swagger UI (Interactiva)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Endpoints Principales

### Root & Health

- `GET /` - Información básica de la API
- `GET /health` - Health check (estado de la aplicación y BD)

### Companies (Empresas)

- `GET /api/v1/companies` - Listar todas las empresas (con paginación)
- `GET /api/v1/companies/active` - Listar empresas activas
- `GET /api/v1/companies/search/{name}` - Buscar por nombre
- `GET /api/v1/companies/trigram/{trigram}` - Obtener por trigram
- `GET /api/v1/companies/{id}` - Obtener por ID
- `GET /api/v1/companies/{id}/with-branches` - Obtener con sucursales
- `POST /api/v1/companies` - Crear empresa
- `PUT /api/v1/companies/{id}` - Actualizar empresa
- `DELETE /api/v1/companies/{id}?soft=true` - Eliminar empresa

### Products (Productos)

- `GET /api/v1/products` - Listar todos los productos
- `GET /api/v1/products/search?q={query}` - Buscar por código o nombre
- `GET /api/v1/products/type/{type}` - Filtrar por tipo (ARTICLE/NOMENCLATURE)
- `GET /api/v1/products/code/{code}` - Obtener por código
- `GET /api/v1/products/{id}` - Obtener por ID
- `GET /api/v1/products/{id}/with-components` - Obtener con componentes (BOM)
- `POST /api/v1/products` - Crear producto
- `PUT /api/v1/products/{id}` - Actualizar producto
- `DELETE /api/v1/products/{id}?soft=true` - Eliminar producto

### BOM (Bill of Materials)

- `POST /api/v1/products/{id}/components` - Agregar componente
- `PUT /api/v1/products/{id}/components/{component_id}` - Actualizar cantidad
- `DELETE /api/v1/products/{id}/components/{component_id}` - Eliminar componente
- `GET /api/v1/products/{id}/bom-cost` - Calcular costo total del BOM

## Ejemplos de Uso

### Crear una empresa

```bash
curl -X POST "http://localhost:8000/api/v1/companies" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "AK Group",
    "trigram": "AKG",
    "company_type_id": 1,
    "email": "contact@akgroup.com",
    "phone": "+56912345678"
  }'
```

### Crear un producto (ARTICLE)

```bash
curl -X POST "http://localhost:8000/api/v1/products" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "PROD-001",
    "name": "Tornillo M6",
    "product_type": "ARTICLE",
    "cost_price": 100.00,
    "sale_price": 150.00,
    "unit_id": 1
  }'
```

### Crear un producto (NOMENCLATURE)

```bash
curl -X POST "http://localhost:8000/api/v1/products" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "ASSEM-001",
    "name": "Ensamble Completo",
    "product_type": "NOMENCLATURE",
    "unit_id": 1
  }'
```

### Agregar componente a un BOM

```bash
curl -X POST "http://localhost:8000/api/v1/products/1/components" \
  -H "Content-Type: application/json" \
  -d '{
    "parent_id": 1,
    "component_id": 2,
    "quantity": 4.000
  }'
```

### Buscar productos

```bash
curl "http://localhost:8000/api/v1/products/search?q=tornillo"
```

## Configuración

### Base de Datos

#### Desarrollo (SQLite)
Por defecto, la aplicación usa SQLite. No requiere configuración adicional.

```env
DATABASE_TYPE=sqlite
SQLITE_PATH=akgroup.db
```

#### Producción (MySQL)
Para usar MySQL, actualiza el archivo `.env`:

```env
DATABASE_TYPE=mysql
MYSQL_HOST=tu-servidor.com
MYSQL_PORT=3306
MYSQL_USER=tu_usuario
MYSQL_PASSWORD=tu_password
MYSQL_DATABASE=akgroup_db
```

### CORS

Por defecto, CORS permite todas las origins (`["*"]`). Para producción, especifica los origins permitidos:

```env
CORS_ORIGINS=["https://tu-dominio.com","https://app.tu-dominio.com"]
```

### Autenticación

**NOTA**: Actualmente, la API usa un `user_id` fijo (1) para testing.

**TODO**: Implementar autenticación real con JWT en el futuro.

## Arquitectura

La aplicación sigue Clean Architecture con las siguientes capas:

```
main.py (FastAPI App)
    ↓
API Layer (src/api/v1/)
    ↓
Facade Layer (src/facades/)
    ↓
Service Layer (src/services/)
    ↓
Repository Layer (src/repositories/)
    ↓
Database (SQLAlchemy Models)
```

### Patrones Implementados

- **Repository Pattern**: Acceso a datos abstraído
- **Service Pattern**: Lógica de negocio centralizada
- **Facade Pattern**: API simplificada con manejo de transacciones
- **Dependency Injection**: FastAPI Depends()

### Características

- ✅ CRUD completo para Companies y Products
- ✅ Gestión de BOM (Bill of Materials) con detección de ciclos
- ✅ Cálculo recursivo de costos de BOM
- ✅ Soft delete (eliminación lógica)
- ✅ Auditoría automática (created_by, updated_by, timestamps)
- ✅ Validación con Pydantic
- ✅ Manejo de errores estructurado
- ✅ Logging con Loguru
- ✅ Documentación automática (Swagger/ReDoc)
- ✅ Health check endpoint
- ✅ CORS configurables
- ✅ Soporte SQLite y MySQL

## Migraciones de Base de Datos

Para crear migraciones (cuando se actualicen los modelos):

```bash
# Crear migración automática
alembic revision --autogenerate -m "descripción del cambio"

# Aplicar migraciones
alembic upgrade head

# Revertir migración
alembic downgrade -1

# Ver historial
alembic history
```

## Logs

Los logs se guardan en:
- **Consola**: Output colorizado con niveles INFO, DEBUG, WARNING, ERROR
- **Archivo**: `logs/akgroup.log` (rotación automática cada 500 MB)

Niveles de log disponibles:
- `DEBUG`: Información detallada para debugging
- `INFO`: Eventos normales de la aplicación
- `SUCCESS`: Operaciones exitosas
- `WARNING`: Advertencias recuperables
- `ERROR`: Errores no recuperables

Configurar nivel de log en `.env`:
```env
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

## Testing (Próximamente)

```bash
# Ejecutar tests
poetry run pytest

# Con coverage
poetry run pytest --cov=src --cov-report=html

# Test específico
poetry run pytest tests/test_companies.py
```

## Próximos Pasos

1. **Autenticación**: Implementar JWT o session-based auth
2. **Tests**: Escribir tests unitarios e integración
3. **Quote CRUD**: Implementar gestión de cotizaciones
4. **Más entidades**: Implementar resto de modelos (Orders, Invoices, etc.)
5. **Permisos**: Sistema de roles y permisos
6. **Cache**: Implementar Redis para cache
7. **Background Tasks**: Celery para tareas asíncronas
8. **Docker**: Dockerfile y docker-compose

## Soporte

Para más información, consulta:
- `CLAUDE.md` - Guía completa del proyecto
- `PYTHON_BEST_PRACTICES.md` - Estándares de código
- Swagger UI en `/docs` - Documentación interactiva
