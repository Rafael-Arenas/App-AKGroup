# CompanyTypeEnum - Documentación

## Descripción

`CompanyTypeEnum` es un **enum híbrido** que proporciona type safety para los tipos de empresa en el sistema. Combina lo mejor de dos mundos:

- ✅ **Enum de Python**: Type safety, autocompletado, validación en tiempo de desarrollo
- ✅ **Tabla de base de datos**: Integridad referencial, constraints, metadata

## Arquitectura (Opción 2 - Híbrido)

```
┌─────────────────────┐
│  CompanyTypeEnum    │ ← Enum de Python (CLIENT, SUPPLIER)
│  (Python)           │
└──────────┬──────────┘
           │ sincroniza con
           ↓
┌─────────────────────┐
│  company_types      │ ← Tabla en base de datos
│  (Database)         │   - id: 1, name: "CLIENT", description: "..."
└──────────┬──────────┘   - id: 2, name: "SUPPLIER", description: "..."
           │
           │ FK
           ↓
┌─────────────────────┐
│  companies          │
│  - company_type_id  │ ← Foreign Key a company_types
└─────────────────────┘
```

## Valores Definidos

| Enum | Valor | Display Name | Descripción |
|------|-------|--------------|-------------|
| `CompanyTypeEnum.CLIENT` | `"CLIENT"` | Cliente | Empresa que adquiere productos o servicios |
| `CompanyTypeEnum.SUPPLIER` | `"SUPPLIER"` | Proveedor | Empresa que provee productos o servicios |

## Uso Básico

### 1. Acceder a valores del enum

```python
from src.models import CompanyTypeEnum

# Acceder a valores
client_type = CompanyTypeEnum.CLIENT
supplier_type = CompanyTypeEnum.SUPPLIER

print(client_type)                 # CompanyTypeEnum.CLIENT
print(client_type.value)           # "CLIENT"
print(client_type.display_name)    # "Cliente"
print(client_type.description)     # "Empresa que adquiere productos o servicios"
```

### 2. Usar con modelo Company

```python
from src.models import Company, CompanyTypeEnum

# Obtener una empresa (con company_type cargado via relationship)
company = session.query(Company).filter_by(id=1).first()

# Acceder al enum
company_type = company.company_type_enum

# Comparaciones type-safe
if company_type == CompanyTypeEnum.CLIENT:
    print("Es un cliente")
    # Lógica específica para clientes
elif company_type == CompanyTypeEnum.SUPPLIER:
    print("Es un proveedor")
    # Lógica específica para proveedores
```

### 3. Filtrar empresas por tipo

```python
from src.models import Company, CompanyType, CompanyTypeEnum

# Filtrar clientes
clients = session.query(Company).join(CompanyType).filter(
    CompanyType.name == CompanyTypeEnum.CLIENT.value
).all()

# Filtrar proveedores
suppliers = session.query(Company).join(CompanyType).filter(
    CompanyType.name == CompanyTypeEnum.SUPPLIER.value
).all()
```

### 4. Validación

```python
from src.models import CompanyTypeEnum

# Validar que un string es un tipo válido
user_input = "CLIENT"

try:
    company_type = CompanyTypeEnum[user_input]
    print(f"Válido: {company_type.display_name}")
except KeyError:
    print(f"'{user_input}' no es un tipo válido")
```

### 5. Iteración

```python
from src.models import CompanyTypeEnum

# Iterar sobre todos los tipos
for company_type in CompanyTypeEnum:
    print(f"{company_type.value}: {company_type.display_name}")
```

## Inicialización de la Base de Datos

Para poblar la tabla `company_types` con los valores del enum:

### Opción 1: Script directo

```bash
# Ejecutar el script de seed
python -m src.scripts.seed_company_types

# O especificar la URL de la base de datos
python -m src.scripts.seed_company_types "sqlite:///mydb.db"
```

### Opción 2: Desde código Python

```python
from src.scripts.seed_company_types import seed_company_types

# Con una sesión existente
seed_company_types(session=my_session)

# O especificando database URL
seed_company_types(database_url="sqlite:///app_akgroup.db")
```

### Opción 3: Como parte de una migración de Alembic

Cuando configures Alembic, puedes agregar el seed al script de migración:

```python
# En migrations/versions/xxxxx_create_company_types.py
from alembic import op
from src.models.core.companies import CompanyTypeEnum

def upgrade():
    # ... crear tablas ...

    # Insertar datos
    from sqlalchemy import table, column, String, Text, Integer
    company_types = table('company_types',
        column('id', Integer),
        column('name', String),
        column('description', Text)
    )

    op.bulk_insert(company_types, [
        {'name': CompanyTypeEnum.CLIENT.value, 'description': CompanyTypeEnum.CLIENT.description},
        {'name': CompanyTypeEnum.SUPPLIER.value, 'description': CompanyTypeEnum.SUPPLIER.description},
    ])
```

## Propiedades del Enum

### `value: str`
El valor del enum (ej: `"CLIENT"`, `"SUPPLIER"`)

```python
CompanyTypeEnum.CLIENT.value  # "CLIENT"
```

### `display_name: str`
Nombre para mostrar en español

```python
CompanyTypeEnum.CLIENT.display_name  # "Cliente"
```

### `description: str`
Descripción detallada del tipo

```python
CompanyTypeEnum.CLIENT.description  # "Empresa que adquiere productos o servicios"
```

## Propiedades del modelo Company

### `company_type_enum: Optional[CompanyTypeEnum]`
Property que retorna el tipo de empresa como enum

```python
company = session.query(Company).first()
enum_value = company.company_type_enum

if enum_value == CompanyTypeEnum.CLIENT:
    print("Es cliente")
```

**Nota**: Retorna `None` si:
- La empresa no tiene `company_type` asignado
- El valor en la DB no coincide con ningún valor del enum

## Agregar Nuevos Tipos

Para agregar un nuevo tipo de empresa (ej: `PARTNER`):

1. **Agregar al enum** (`src/models/core/companies.py`):

```python
class CompanyTypeEnum(str, enum.Enum):
    CLIENT = "CLIENT"
    SUPPLIER = "SUPPLIER"
    PARTNER = "PARTNER"  # ← Nuevo

    @property
    def display_name(self) -> str:
        names = {
            CompanyTypeEnum.CLIENT: "Cliente",
            CompanyTypeEnum.SUPPLIER: "Proveedor",
            CompanyTypeEnum.PARTNER: "Partner",  # ← Nuevo
        }
        return names[self]

    @property
    def description(self) -> str:
        descriptions = {
            CompanyTypeEnum.CLIENT: "Empresa que adquiere productos o servicios",
            CompanyTypeEnum.SUPPLIER: "Empresa que provee productos o servicios",
            CompanyTypeEnum.PARTNER: "Empresa asociada o colaboradora",  # ← Nuevo
        }
        return descriptions[self]
```

2. **Ejecutar el script de seed** para actualizar la DB:

```bash
python -m src.scripts.seed_company_types
```

El script detectará automáticamente el nuevo valor y lo insertará.

## Ventajas de esta Implementación

### ✅ Type Safety
```python
# El IDE sabe que solo puede ser CLIENT o SUPPLIER
if company.company_type_enum == CompanyTypeEnum.CLIENT:
    # Autocompletado funciona aquí
    pass
```

### ✅ Validación en tiempo de desarrollo
```python
# Esto dará error en tiempo de desarrollo (no en runtime)
if company.company_type_enum == "CLIENTE":  # ← Error: comparing to string
    pass
```

### ✅ Integridad referencial en DB
```sql
-- La FK en la tabla companies asegura que solo existan
-- tipos válidos en la base de datos
FOREIGN KEY (company_type_id) REFERENCES company_types(id)
```

### ✅ Fácil de extender
- Agregar nuevo tipo: solo editar el enum y correr seed
- La tabla se actualiza automáticamente

### ✅ Metadata en DB
- Descripciones, timestamps, etc. se almacenan en la DB
- Facilita reportes y queries

## Ejemplos de Uso Avanzado

Ver el archivo `examples/company_type_enum_usage.py` para más ejemplos.

## Archivos Relacionados

- **Enum**: `src/models/core/companies.py` (líneas 29-83)
- **Modelo Company**: `src/models/core/companies.py` (líneas 86-283)
- **Tabla CompanyType**: `src/models/lookups/lookups.py` (líneas 147-188)
- **Script de seed**: `src/scripts/seed_company_types.py`
- **Ejemplos**: `examples/company_type_enum_usage.py`

## Preguntas Frecuentes

### ¿Por qué no solo usar strings?
Strings no tienen type safety. Con el enum, el IDE puede ayudarte y detectar errores antes de ejecutar.

### ¿Por qué mantener la tabla company_types?
Para integridad referencial, metadata, y facilitar queries SQL directas.

### ¿Qué pasa si agrego un valor al enum pero no corro el seed?
La tabla no tendrá ese valor, y no podrás crear empresas con ese tipo hasta que lo insertes.

### ¿Puedo eliminar un tipo?
Técnicamente sí, pero primero debes:
1. Migrar todas las empresas que usen ese tipo
2. Eliminar el valor de la tabla
3. Eliminar del enum

---

**Autor**: Claude Code
**Fecha**: 2025-10-25
**Versión**: 1.0
