---
trigger: always_on
---

# SQLite Configuration & Best Practices for Production (2025)

Esta guía define la configuración óptima de SQLite para aplicaciones modernas en Python (FastAPI/SQLAlchemy), priorizando rendimiento, concurrencia e integridad de datos.

---

## 🚀 Configuración Crítica (Pragmas)

Para sistemas en producción, **siempre** aplica estos PRAGMAs al iniciar cada conexión:

| Pragma | Valor Recomendado | Motivo |
|:-------|:------------------|:-------|
| `journal_mode` | `WAL` | **Concurrency**: Permite lectores y escritores simultáneos. Esencial para servidores web (FastAPI). Evita errores "database is locked". |
| `synchronous` | `NORMAL` | **Performance**: En modo WAL, `NORMAL` es seguro (fsync solo en checkpoints) y mucho más rápido que `FULL`. |
| `foreign_keys` | `ON` | **Integrity**: SQLite lo tiene apagado por defecto. Debe activarse en **cada conexión**. |
| `busy_timeout` | `5000` (ms) | **Robustness**: Espera hasta 5s si la DB está ocupada antes de lanzar error. Vital para concurrencia. |
| `cache_size` | `-64000` | **Performance**: Usa ~64MB de RAM para caché de páginas (valor negativo = kilobytes). Ajustar según memoria disponible. |
| `temp_store` | `MEMORY` | **Performance**: Tablas temporales e índices transitorios en RAM en vez de disco. |
| `mmap_size` | `268435456` | **Performance**: Memory-mapped I/O (~256MB). Acelera drásticamente lecturas en DBs grandes. |

---

## 🛠️ Implementación en SQLAlchemy 2.0

Configura el engine para aplicar estos parámetros automáticamente en cada conexión nueva.

### ✅ Async Engine (aiosqlite)

```python
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import event, Engine

# URL de conexión (¡Usa path absoluto en producción!)
DATABASE_URL = "sqlite+aiosqlite:///./production.db"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args={
        "timeout": 20,                # Timeout de conexión a nivel driver
        "check_same_thread": False,   # Necesario para aiosqlite
    }
)

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Aplica optimizaciones de SQLite al conectar."""
    cursor = dbapi_connection.cursor()
    
    # 1. Performance & Concurrency
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA busy_timeout=5000")
    
    # 2. Memory & Optimization
    cursor.execute("PRAGMA cache_size=-64000") # 64MB
    cursor.execute("PRAGMA temp_store=MEMORY")
    cursor.execute("PRAGMA mmap_size=268435456") # 256MB
    
    # 3. Data Integrity
    cursor.execute("PRAGMA foreign_keys=ON")
    
    cursor.close()
```

### ✅ Sync Engine (sqlite3)

La lógica del evento es idéntica. Para el engine síncrono:

```python
engine = create_engine(
    "sqlite:///./production.db",
    connect_args={"check_same_thread": False} # Solo si compartes conexión entre threads (no recomendado)
)
```

---

## 📦 Migraciones con Alembic y SQLite

SQLite **no soporta** la mayoría de operaciones `ALTER TABLE` estándar. Es obligatorio usar **Batch Mode**.

### `alembic/env.py`

```python
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
        literal_binds=True, # Importante para logs SQL limpios
        
        # ⚠️ CRÍTICO PARA SQLITE:
        render_as_batch=True 
    )

    with context.begin_transaction():
        context.run_migrations()
```

---

## 🛡️ Checklist de Mantenimiento

Para mantener la base de datos sana y rápida:

1.  **VACUUM periódico**: Recupera espacio en disco y desfragmenta. (Ej: Mensual o tras borrados masivos).
    *   Comando: `VACUUM;` (⚠️ Bloquea la DB, ejecutar en ventana de mantenimiento).
2.  **WAL Checkpoint**: Normalmente automático, pero si el archivo `-wal` crece gigabytes sin control:
    *   Comando: `PRAGMA wal_checkpoint(TRUNCATE);`
3.  **Optimize**:
    *   Comando: `PRAGMA optimize;` (Ejecutar antes de cerrar la app o periódicamente, ligero y rápido).

---

## ⚠️ Errores Comunes (Troubleshooting)

*   **"database is locked"**:
    *   Causa: Escritura larga bloqueando lecturas (o viceversa en modo no-WAL).
    *   Solución: Asegurar `journal_mode=WAL` y aumentar `busy_timeout`.
*   **Foreign Key Constraint Failed**:
    *   Causa: Intentar borrar/insertar registros violando relaciones.
    *   Validación: Al tener `foreign_keys=ON`, esto es *bueno*, significa que la DB protege tus datos.
*   **Lentitud en escrituras**:
    *   Verificar `synchronous=NORMAL` (vs FULL).
    *   Usar transacciones explícitas (`async with session.begin():`) para agrupar múltiples inserts.
