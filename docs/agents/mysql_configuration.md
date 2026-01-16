---
trigger: always_on
---

# MySQL/MariaDB Configuration & Best Practices for Production (2025)

Esta guía define la configuración óptima de MySQL para aplicaciones modernas en Python (FastAPI/SQLAlchemy), enfocada en estabilidad, unicode completo y manejo correcto de conexiones asíncronas.

---

## 🚀 Drivers & Conectores

### ✅ Async Driver: `asyncmy` (Recomendado)

Aunque `aiomysql` fue el estándar, **`asyncmy`** es más rápido, mantenido activamente y maneja mejor los tipos de datos modernos.

| Driver | Estado | Recomendación |
|:-------|:-------|:--------------|
| **asyncmy** | Activo, Alto Rendimiento | 🏆 **Primaria** |
| **aiomysql** | Mantenimiento bajo | Alternativa legacy |
| **PyMySQL** | Síncrono, Estable | Para scripts/tablas síncronas |

### ✅ Connection URL

Es **crítico** especificar el charset en la URL para soporte total de Emojis y caracteres unicode de 4 bytes.

```python
# Formato: mysql+asyncmy://user:pass@host:port/db?charset=utf8mb4
DATABASE_URL = "mysql+asyncmy://user:pass@localhost:3306/production_db?charset=utf8mb4"
```

---

## 🛠️ Configuración del Engine en SQLAlchemy 2.0

La gestión de conexiones en MySQL requiere atención especial al `pool_recycle` para evitar cierres inesperados por el servidor.

### ✅ Async Engine Configuration

```python
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    
    # ⚡ Optimización del Pool
    pool_size=10,             # Conexiones base mantenidas abiertas
    max_overflow=20,          # Conexiones extra permitidas en picos
    pool_timeout=30,          # Segundos de espera antes de error si pool lleno
    
    # 🛡️ Estabilidad MySQL (CRÍTICO)
    pool_recycle=3600,        # Reciclar conexión cada 1h (evita timeout de 8h de MySQL)
    pool_pre_ping=True,       # Verifica conexión antes de usarla (evita "MySQL server has gone away")
    
    # ⚙️ Driver Args
    connect_args={
        "echo": False,        # Logs internos del driver (no de SQLAlchemy)
    }
)
```

### ✅ Isolation Levels

MySQL usa `REPEATABLE READ` por defecto. Para altos volúmenes de concurrencia web, `READ COMMITTED` suele ser preferible para reducir bloqueos (deadlocks), aunque depende de la lógica de negocio.

```python
# Configurar nivel de aislamiento globalmente
engine = create_async_engine(
    DATABASE_URL,
    isolation_level="READ COMMITTED" # Soluciona muchos problemas de locking en altas cargas
)
```

---

## 📦 Migraciones con Alembic y MySQL

### ⚠️ DDL No-Transaccional

A diferencia de PostgreSQL, **MySQL NO soporta DDL (Data Definition Language) dentro de transacciones**.
*   Si una migración falla a mitad de camino, los cambios **no se revierten automáticante**.
*   La base de datos puede quedar en un estado inconsistente.

**Mejor Práctica**:
*   Dividir migraciones complejas en múltiples pasos pequeños.
*   Nunca mezclar DML (Data Manipulation) y DDL en la misma migración si es posible.

### `alembic/env.py`

Asegurar compatibilidad con `asyncmy` y UTF-8.

```python
config = context.config

# Sobrescribir URL si viene de env vars para asegurar driver correcto
# config.set_main_option("sqlalchemy.url", "mysql+asyncmy://...")

def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

async def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        
        # MySQL no necesita render_as_batch=True como SQLite,
        # pero compare_type=True es útil para detectar cambios en VARCHAR/TEXT
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()
```

---

## 🛡️ Checklist de Producción

1.  **Charset & Collation**:
    *   Siempre usar `utf8mb4`.
    *   Collation recomendada: `utf8mb4_0900_ai_ci` (MySQL 8.0+) o `utf8mb4_unicode_ci` (MySQL 5.7).
    *   Verificar al crear tablas: `__table_args__ = {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'}`.

2.  **Timeouts del Servidor**:
    *   Verificar variables `wait_timeout` y `interactive_timeout` en el servidor MySQL.
    *   `pool_recycle` en SQLAlchemy debe ser **menor** que estos valores.

3.  **Índices en Foreign Keys**:
    *   MySQL (InnoDB) requiere índices en las FK. SQLAlchemy suele crearlos, pero verificar para evitar deadlocks en borrados en cascada.

---

## ⚠️ Troubleshooting Común

*   **"MySQL server has gone away"**:
    *   Causa: Conexión cerrada por el servidor por inactividad o paquete muy grande.
    *   Solución: Activar `pool_pre_ping=True` y ajustar `pool_recycle`.
*   **"Lock wait timeout exceeded"**:
    *   Causa: Transacciones largas bloqueando filas.
    *   Solución: Mantener transacciones cortas (`async with session.begin():`), considerar `READ COMMITTED`.
*   **Incorrect string value (Emojis)**:
    *   Causa: Base de datos o conexión usando `utf8` (alias de `utf8mb3`).
    *   Solución: Forzar `charset=utf8mb4` en connection string y tablas.
