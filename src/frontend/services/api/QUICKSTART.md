# Quickstart - Servicios API Frontend

Guía rápida para empezar a usar los servicios API en menos de 5 minutos.

## 1. Verificar Backend

Asegúrate de que el backend FastAPI esté corriendo:

```bash
# En una terminal
poetry run backend
# O manualmente:
poetry run uvicorn src.backend.main:app --reload --port 8000
```

Verifica en: http://localhost:8000/docs

---

## 2. Importar Servicios

```python
# Importar servicios singleton (recomendado)
from src.frontend.services.api import company_api, product_api, lookup_api

# Importar excepciones
from src.frontend.services.api import (
    APIException,
    NotFoundException,
    ValidationException,
)
```

---

## 3. Ejemplos Básicos

### Listar Empresas

```python
import asyncio

async def main():
    # Obtener empresas activas
    companies = await company_api.get_active()

    for company in companies:
        print(f"{company['id']}: {company['name']}")

asyncio.run(main())
```

### Crear Empresa

```python
async def create():
    try:
        company = await company_api.create({
            "name": "Mi Empresa",
            "company_type_id": 1,
            "country_id": 1,
            "nit": "900123456-7",
            "email": "info@empresa.com",
        })
        print(f"Creada con ID: {company['id']}")
    except ValidationException as e:
        print(f"Error de validación: {e.details}")

asyncio.run(create())
```

### Buscar Empresas

```python
async def search():
    results = await company_api.search("AK")
    print(f"Encontradas: {len(results)} empresas")

asyncio.run(search())
```

---

## 4. Productos

### Listar Productos por Tipo

```python
async def list_products():
    # Solo artículos
    articles = await product_api.get_by_type("ARTICLE")

    # Solo nomenclaturas
    nomenclatures = await product_api.get_by_type("NOMENCLATURE")

    print(f"Artículos: {len(articles)}")
    print(f"Nomenclaturas: {len(nomenclatures)}")

asyncio.run(list_products())
```

### Crear Producto con BOM

```python
async def create_with_bom():
    # Crear artículo
    article = await product_api.create({
        "code": "ART-001",
        "name": "Componente A",
        "product_type": "ARTICLE",
        "unit_id": 1,
    })

    # Crear nomenclatura
    nomenclature = await product_api.create({
        "code": "NOM-001",
        "name": "Ensamble X",
        "product_type": "NOMENCLATURE",
        "unit_id": 1,
    })

    # Añadir componente a BOM
    component = await product_api.add_component(
        nomenclature["id"],
        {
            "component_product_id": article["id"],
            "quantity": 2.5,
            "unit_id": 1,
        }
    )

    print(f"BOM creado: {component['id']}")

asyncio.run(create_with_bom())
```

---

## 5. Datos de Referencia (Lookups)

```python
async def get_lookups():
    # Tipos de empresa
    company_types = await lookup_api.get_company_types()
    print("Tipos de empresa:", [ct["name"] for ct in company_types])

    # Países
    countries = await lookup_api.get_countries()
    print("Países disponibles:", len(countries))

    # Unidades de medida
    units = await lookup_api.get_units()
    print("Unidades:", [u["symbol"] for u in units])

asyncio.run(get_lookups())
```

---

## 6. Manejo de Errores

```python
async def safe_get():
    try:
        company = await company_api.get_by_id(999)
    except NotFoundException:
        print("Empresa no encontrada")
    except ValidationException as e:
        print(f"Datos inválidos: {e.details}")
    except APIException as e:
        print(f"Error: {e.message} (Status: {e.status_code})")

asyncio.run(safe_get())
```

---

## 7. Integración con Flet

```python
import flet as ft
from src.frontend.services.api import company_api

async def main(page: ft.Page):
    # Cargar datos
    companies = await company_api.get_all()

    # Mostrar en lista
    for company in companies:
        page.add(ft.Text(company["name"]))

    page.update()

ft.app(target=main)
```

---

## 8. Ejecutar Ejemplos Completos

```bash
# Ejemplos de uso
poetry run python -m src.frontend.services.api.example_usage

# Ejemplo con Flet UI
poetry run python src/frontend/services/api/flet_integration_example.py
```

---

## 9. Tests

```bash
# Ejecutar todos los tests
poetry run pytest tests/frontend/services/api/ -v

# Con cobertura
poetry run pytest tests/frontend/services/api/ --cov=src/frontend/services/api
```

---

## 10. Configuración Avanzada

### Cambiar URL del Backend

Crear `.env` en la raíz:

```bash
API_BACKEND_BASE_URL=https://api.produccion.com
API_TIMEOUT=60.0
API_MAX_RETRIES=5
```

### Usar Instancia Custom

```python
from src.frontend.services.api import CompanyAPIService

# Cliente con configuración personalizada
custom_api = CompanyAPIService(
    base_url="https://api.produccion.com/api/v1",
    timeout=60.0
)

companies = await custom_api.get_all()
```

---

## Referencia Rápida

### Company API
```python
await company_api.get_all(skip=0, limit=100)
await company_api.get_by_id(id)
await company_api.search(name)
await company_api.get_active()
await company_api.create(data)
await company_api.update(id, data)
await company_api.delete(id)
```

### Product API
```python
await product_api.get_all(skip=0, limit=100)
await product_api.get_by_id(id)
await product_api.get_by_type("ARTICLE" | "NOMENCLATURE")
await product_api.create(data)
await product_api.update(id, data)
await product_api.delete(id)
await product_api.add_component(id, component_data)
await product_api.remove_component(id, component_id)
```

### Lookup API
```python
await lookup_api.get_company_types()
await lookup_api.get_countries()
await lookup_api.get_units()
```

---

## Troubleshooting

**Backend no responde:**
```python
NetworkException: Error de red después de 3 intentos
```
→ Verifica que el backend esté en http://localhost:8000

**Timeout:**
```python
httpx.TimeoutException
```
→ Aumenta el timeout: `CompanyAPIService(timeout=60.0)`

**Validación fallida:**
```python
ValidationException: Error de validación
```
→ Revisa los datos requeridos en `e.details`

---

## Documentación Completa

- **README completo**: `src/frontend/services/api/README.md`
- **Resumen técnico**: `SERVICIOS_API_RESUMEN.md`
- **Ejemplos de código**: `src/frontend/services/api/example_usage.py`
- **Integración Flet**: `src/frontend/services/api/flet_integration_example.py`

---

## ¡Listo!

Ya puedes empezar a usar los servicios API en tu aplicación Flet.

Para más detalles, consulta el README completo o los archivos de ejemplo.
