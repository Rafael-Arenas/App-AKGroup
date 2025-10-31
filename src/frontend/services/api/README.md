# Servicios API - Frontend Flet

Servicios para comunicación HTTP asíncrona entre el frontend Flet y el backend FastAPI.

## Estructura

```
api/
├── __init__.py              # Exports y singletons
├── base_api_client.py       # Cliente HTTP base con retry logic
├── company_api.py           # Servicio de Companies
├── product_api.py           # Servicio de Products
├── lookup_api.py            # Servicio de Lookups (datos de referencia)
├── example_usage.py         # Ejemplos de uso
└── README.md                # Este archivo
```

## Características

### Cliente HTTP Base (`base_api_client.py`)

- **Cliente asíncrono**: Basado en `httpx.AsyncClient`
- **Timeout configurable**: Default 30 segundos
- **Retry logic**: Hasta 3 reintentos con backoff exponencial para errores de red
- **Manejo de errores**: Excepciones específicas por tipo de error
- **Logging automático**: Todas las peticiones y respuestas se registran con loguru
- **Context manager**: Soporte para `async with` para manejo de recursos

### Excepciones Personalizadas

```python
APIException           # Base para todos los errores de API
├── NetworkException   # Errores de red/conexión
├── ValidationException # Errores de validación (422)
├── NotFoundException   # Recurso no encontrado (404)
└── UnauthorizedException # No autorizado (401)
```

## Uso Básico

### Importar Servicios Singleton

```python
from src.frontend.services.api import company_api, product_api, lookup_api
```

### Ejemplo: Obtener Empresas

```python
import asyncio
from loguru import logger
from src.frontend.services.api import company_api, NotFoundException, APIException

async def get_companies():
    try:
        # Obtener empresas activas
        companies = await company_api.get_active()
        logger.info(f"Empresas activas: {len(companies)}")

        for company in companies:
            print(f"{company['id']}: {company['name']}")

    except NotFoundException as e:
        logger.error(f"No encontrado: {e.message}")
    except APIException as e:
        logger.error(f"Error de API: {e.message}")

# Ejecutar
asyncio.run(get_companies())
```

### Ejemplo: Crear Empresa

```python
async def create_company():
    try:
        company_data = {
            "name": "AK Group",
            "company_type_id": 1,
            "country_id": 1,
            "nit": "900123456-7",
            "email": "info@akgroup.com",
            "phone": "+57 300 1234567",
            "address": "Calle 123 #45-67",
            "is_active": True
        }

        new_company = await company_api.create(company_data)
        logger.success(f"Empresa creada con ID: {new_company['id']}")

    except ValidationException as e:
        logger.error(f"Error de validación: {e.message}")
        logger.error(f"Detalles: {e.details}")
```

### Ejemplo: Usar Context Manager

```python
async def get_products_with_context():
    # El cliente se cierra automáticamente al salir del contexto
    async with product_api as service:
        products = await service.get_all(limit=10)
        logger.info(f"Productos: {len(products)}")
```

## Servicios Disponibles

### CompanyAPIService

**Endpoints:**
- `get_all(skip, limit)` - Lista empresas con paginación
- `get_by_id(company_id)` - Obtiene empresa por ID
- `search(name)` - Busca empresas por nombre
- `get_active()` - Obtiene empresas activas
- `create(data)` - Crea nueva empresa
- `update(company_id, data)` - Actualiza empresa
- `delete(company_id)` - Elimina empresa

**Ejemplo:**
```python
# Buscar empresas
results = await company_api.search("AK")

# Actualizar empresa
updated = await company_api.update(1, {
    "name": "Nuevo Nombre",
    "phone": "+57 300 9876543"
})
```

### ProductAPIService

**Endpoints:**
- `get_all(skip, limit)` - Lista productos con paginación
- `get_by_id(product_id)` - Obtiene producto por ID
- `get_by_type(product_type)` - Filtra por tipo ("ARTICLE" o "NOMENCLATURE")
- `create(data)` - Crea nuevo producto
- `update(product_id, data)` - Actualiza producto
- `delete(product_id)` - Elimina producto
- `add_component(product_id, component_data)` - Añade componente a BOM
- `remove_component(product_id, component_id)` - Elimina componente de BOM

**Ejemplo:**
```python
# Crear nomenclatura
nomenclature = await product_api.create({
    "code": "NOM-001",
    "name": "Conjunto A",
    "product_type": "NOMENCLATURE",
    "unit_id": 1
})

# Añadir componente
component = await product_api.add_component(
    nomenclature["id"],
    {
        "component_product_id": 5,
        "quantity": 2.5,
        "unit_id": 1
    }
)
```

### LookupAPIService

**Endpoints:**
- `get_company_types()` - Tipos de empresa
- `get_countries()` - Países
- `get_units()` - Unidades de medida

**Ejemplo:**
```python
# Obtener datos de referencia
company_types = await lookup_api.get_company_types()
countries = await lookup_api.get_countries()
units = await lookup_api.get_units()
```

## Manejo de Errores

### Jerarquía de Excepciones

```python
try:
    company = await company_api.get_by_id(999)
except NotFoundException:
    print("Empresa no encontrada")
except ValidationException as e:
    print(f"Datos inválidos: {e.details}")
except NetworkException:
    print("Error de conexión, reintentar más tarde")
except UnauthorizedException:
    print("No autorizado, iniciar sesión")
except APIException as e:
    print(f"Error general: {e.message} (Status: {e.status_code})")
```

### Atributos de las Excepciones

```python
try:
    await company_api.create(invalid_data)
except APIException as e:
    print(f"Mensaje: {e.message}")
    print(f"Status Code: {e.status_code}")
    print(f"Detalles: {e.details}")
```

## Configuración

### URL del Backend

Por defecto, los servicios se conectan a `http://localhost:8000/api/v1`.

Para cambiar la URL:

```python
from src.frontend.services.api import CompanyAPIService

# Crear instancia con URL personalizada
custom_api = CompanyAPIService(
    base_url="https://api.akgroup.com/api/v1",
    timeout=60.0  # 60 segundos
)

companies = await custom_api.get_all()
```

### Timeout y Reintentos

```python
from src.frontend.services.api.base_api_client import BaseAPIClient

# Cliente con configuración personalizada
client = BaseAPIClient(
    base_url="http://localhost:8000/api/v1",
    timeout=45.0,      # 45 segundos de timeout
    max_retries=5      # 5 reintentos máximo
)
```

## Logging

Los servicios usan `loguru` para logging automático:

```python
# Logs generados automáticamente:
# INFO  - GET request | endpoint=/companies params={'skip': 0, 'limit': 10}
# DEBUG - Petición HTTP | method=GET url=/companies attempt=1/3
# DEBUG - Respuesta recibida | status=200 url=http://localhost:8000/api/v1/companies
# SUCCESS - Empresas obtenidas exitosamente | total=5
```

### Configurar Nivel de Log

```python
from loguru import logger

# Mostrar solo WARNING y superiores
logger.remove()
logger.add(lambda msg: print(msg), level="WARNING")
```

## Integración con Flet

### Uso en Componentes Flet

```python
import flet as ft
from src.frontend.services.api import company_api, APIException

class CompanyListView(ft.UserControl):
    async def load_companies(self):
        try:
            self.companies = await company_api.get_active()
            self.update()
        except APIException as e:
            await self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text(f"Error: {e.message}"))
            )
```

### Manejo de Estado Async

```python
async def main(page: ft.Page):
    async def handle_load():
        page.add(ft.ProgressRing())
        page.update()

        try:
            companies = await company_api.get_all()
            # Actualizar UI con datos
            page.clean()
            for company in companies:
                page.add(ft.Text(company['name']))
        except APIException as e:
            page.add(ft.Text(f"Error: {e.message}", color="red"))
        finally:
            page.update()

    page.add(ft.ElevatedButton("Cargar", on_click=lambda _: handle_load()))

ft.app(target=main)
```

## Testing

### Ejemplo de Test

```python
import pytest
from src.frontend.services.api import company_api, NotFoundException

@pytest.mark.asyncio
async def test_get_company_by_id():
    company = await company_api.get_by_id(1)
    assert company['id'] == 1
    assert 'name' in company

@pytest.mark.asyncio
async def test_get_company_not_found():
    with pytest.raises(NotFoundException):
        await company_api.get_by_id(999999)
```

## Ejemplos Completos

Ver `example_usage.py` para ejemplos completos de todos los servicios.

Ejecutar ejemplos:
```bash
poetry run python -m src.frontend.services.api.example_usage
```

## Mejores Prácticas

1. **Usar servicios singleton**: Importa `company_api`, `product_api`, `lookup_api` directamente
2. **Manejo de errores específico**: Captura excepciones específicas antes que `APIException`
3. **Context managers**: Usa `async with` cuando crees instancias personalizadas
4. **Logging**: Los servicios ya logean automáticamente, no es necesario agregar logs adicionales
5. **Timeout apropiado**: Ajusta el timeout según la operación (operaciones pesadas = mayor timeout)
6. **Validación local**: Valida datos antes de enviar al backend para evitar errores 422

## Troubleshooting

### Backend no responde

```python
from src.frontend.services.api import NetworkException

try:
    companies = await company_api.get_all()
except NetworkException as e:
    # Backend offline o problemas de red
    print(f"No se puede conectar al backend: {e.message}")
    # Mostrar datos en caché o mensaje al usuario
```

### Timeout muy corto

```python
# Aumentar timeout para operaciones pesadas
from src.frontend.services.api import CompanyAPIService

slow_api = CompanyAPIService(timeout=60.0)  # 60 segundos
data = await slow_api.get_all()
```

### Errores de validación

```python
from src.frontend.services.api import ValidationException

try:
    await company_api.create(data)
except ValidationException as e:
    # e.details contiene los campos con error
    for field, errors in e.details.items():
        print(f"Campo '{field}': {errors}")
```

## Roadmap

- [ ] Autenticación con JWT tokens
- [ ] Cache de respuestas con TTL
- [ ] Websockets para notificaciones en tiempo real
- [ ] Batch requests
- [ ] GraphQL support (opcional)
