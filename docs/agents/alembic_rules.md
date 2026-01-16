
---
trigger: always_on
---

# Guía de Mejores Prácticas Alembic para Agentes (2025)

Esta guía define la configuración estándar, reglas de seguridad y flujos de trabajo recomendados para gestionar migraciones de base de datos con Alembic y SQLAlchemy 2.0.

---

## ⚙️ Configuración Crítica (`alembic.ini`)

### ✅ Plantilla de Archivos
Evita colisiones y mantén un orden cronológico claro.

```ini
[alembic]
# Formato: AÑO-MES-DIA_HORA_SLUG
file_template = %%(year)d-%%(month).2d-%%(day).2d_%%(hour).2d%%(minute).2d_%%(slug)s

# Zona horaria estándar
timezone = UTC
```

---

## 🏗️ Configuración del Entorno (`env.py`)

### ✅ Soporte Asíncrono (Asyncio)

Para proyectos modernos con `SQLAlchemy 2.0` y drivers asíncronos (e.g., `asyncpg`, `aiomysql`), el `env.py` debe configurarse para correr migraciones en un event loop.

```python
import asyncio
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy import pool
from alembic import context
from models import Base  # Importar tu Base declarativa

# CARGAR METADATA CON NAMING CONVENTION
target_metadata = Base.metadata

def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,             # Detectar cambios en tipos de columnas
        compare_server_default=True,   # Detectar cambios en defaults (cuidado en algunos DBs)
        include_schemas=False,         # True si usas múltiples esquemas
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations():
    """Correr migraciones en contexto asíncrono."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_online():
    asyncio.run(run_async_migrations())
```

---

## 🔒 Seguridad y Robustez

### ✅ Naming Conventions
**OBLIGATORIO**: Configurar `naming_convention` en `Base.metadata` para garantizar que constraints (FKs, PKs, Índices) tengan nombres predecibles y Alembic pueda detectarlos/eliminarlos correctamente.

```python
# En tu archivo de modelos (e.g., models/base.py)
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=convention)
```

### ✅ Filtros de Seguridad (`include_object`)
Usa `include_object` en `env.py` para prevenir que Alembic intente borrar tablas que no le pertenecen (e.g., tablas de sistema, `spatial_ref_sys` en PostGIS).

```python
def include_object(object, name, type_, reflected, compare_to):
    # Ignorar tablas de sistema o específicas
    if type_ == "table" and name in ["spatial_ref_sys", "alembic_version"]:
        return False
    return True

# En context.configure:
# include_object=include_object
```

---

## 🚫 Anti-Patrones en Migraciones

1.  **NO Importar Modelos en Versiones**:
    *   *Incorrecto*: `from myapp.models import User` dentro de un archivo `versions/xxx.py`.
    *   *Correcto*: Definir `sa.Table` o usar `sa.Column` explícitamente dentro de la migración. Los modelos cambian, las migraciones deben ser estáticas.

2.  **NO Renombrar Columnas sin Cuidado**:
    *   `op.alter_column` puede ser destructivo. Preferir `op.alter_column` con `existing_type` bien definido.

3.  **NO Mezclar DDL y DML (si es posible)**:
    *   Separa cambios de esquema (DDL) de migraciones de datos complejos (DML).

---

## 🧪 Estrategia de Testing

Antes de aplicar en producción, las migraciones deben probarse:

1.  **Upgrade/Downgrade Test**:
    *   En CI/CD, levantar una DB vacía.
    *   Ejecutar `alembic upgrade head`.
    *   Ejecutar `alembic downgrade base`.
    *   Ejecutar `alembic upgrade head` nuevamente.
    *   Esto verifica que las cadenas de migración son reversibles (idempotencia).

2.  **Verificar Autogenerate Vacío**:
    *   Después de correr migraciones, ejecutar `alembic check` o generar una nueva migración; si detecta cambios, la migración anterior estaba incompleta o los modelos no coinciden.
