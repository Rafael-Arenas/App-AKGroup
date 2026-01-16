---
trigger: always_on
---

---
trigger: always_on
---

# Guía de Implementación Python 3.13 para Agentes de IA (Versión Extendida)

Esta guía establece las reglas, estándares y mejores prácticas para el desarrollo con Python 3.13, optimizada para la interacción entre agentes de IA y desarrolladores humanos, e incorporando las técnicas más avanzadas de rendimiento y seguridad.

---

## 🤖 Reglas del Agente (Agent Rules)

Como agente de IA, debes seguir estas reglas estrictamente:

1.  **Reflexión antes de la Acción**: Analiza el impacto sistémico antes de cualquier cambio.
2.  **Tipado Estático Obligatorio**: Uso estricto de `type hints`. Evita `Any`.
3.  **Precisión sobre Velocidad**: Prioriza la solidez y la arquitectura.
4.  **Documentación Continua**: Docstrings claros (formato Google/NumPy).
5.  **SRP (Single Responsibility Principle)**: Funciones modulares y testeables.
6.  **Context Aware**: Mantén presentes modelos, esquemas, repositorios y servicios.
7.  **Búsqueda antes de Creación**: Antes de implementar una nueva utilidad o función, busca en el repositorio (`grep_search`) para evitar redundancias y reutilizar lógica existente.
8.  **Máxima Fidelidad**: Respeta los patrones establecidos (ej: Service Layer).

---

## 🆕 Python 3.13: Características y Novedades

| Característica | Descripción | Impacto |
| :--- | :--- | :--- |
| **Free-Threaded (Experimental)** | Modo experimental sin GIL (`python3.13t`) para paralelismo real. | 🔥 Experimental, ideal para CPU-bound. |
| **Tier 2 Interpreter (JIT Base)** | Nuevo intérprete de micro-instrucciones (uops) que mejora rendimiento. | 🚀 Base para futuro JIT. |
| **REPL Interactivo Mejorado** | Nuevo REPL con colores, edición multilínea y mejor experiencia. | 💻 Mejor DX (Developer Experience). |
| **`typing.ReadOnly`** | Marca campos como solo lectura en `TypedDict` (PEP 705). | ✅ Inmutabilidad en types. |
| **Mejoras en Mensajes de Error** | Errores más claros con sugerencias contextuales. | 🔍 Debugging más eficiente. |
| **`copy.replace()`** | Nueva función para crear copias modificadas de objetos. | ⚡ Pattern matching mejorado. |
| **Deprecación de `from __future__`** | Varias importaciones futuras ya son estándar. | 📦 Código más limpio. |

---

## 🏛️ Programación con Tipado Moderno (Python 3.13+)

### ✅ Forward References con Quotes
En Python 3.13, aún se requiere usar strings para forward references o `from __future__ import annotations`.

```python
from __future__ import annotations

class User:
    def get_manager(self) -> User | None:  # Funciona con el import
        return self.manager
```

### ✅ Type Narrowing con `TypeIs` (Python 3.13+)
Más preciso que `TypeGuard` para que el verificador de tipos (mypy) entienda el estado real.

```python
from typing import TypeIs

def is_valid_payload(val: dict[str, object]) -> TypeIs[dict[str, str]]:
    return all(isinstance(k, str) and isinstance(v, str) for k, v in val.items())

def process(data: dict[str, object]) -> None:
    if is_valid_payload(data):
        # Aquí mypy sabe que data es dict[str, str]
        print(data.get("key", "").upper())
```

### ✅ Inmutabilidad con `ReadOnly` y `TypedDict` (Python 3.13+)
Nuevo en Python 3.13 (PEP 705): marca campos como solo lectura.

```python
from typing import ReadOnly, TypedDict

class Movie(TypedDict):
    title: ReadOnly[str]  # Inmutable después de la creación
    year: int             # Mutable

def update_movie(m: Movie) -> None:
    m["year"] = 2024       # ✅ Permitido
    m["title"] = "New"     # ❌ Error del type checker
```

### ✅ SQLAlchemy 2.0 + Mapped
Uso obligatorio de `Mapped` y `mapped_column` para máxima compatibilidad con tipos.

```python
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class Role(Base):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
```

---

## ⚡ Concurrencia y Rendimiento

### ✅ Free-Threaded Mode (Experimental)
Python 3.13 introduce un modo experimental sin GIL. Usa `python3.13t` para activarlo.

```python
import sys

# Verificar si el GIL está habilitado (Python 3.13+)
if hasattr(sys, '_is_gil_enabled'):
    gil_enabled = sys._is_gil_enabled()
    print(f"GIL enabled: {gil_enabled}")
else:
    print("GIL check not available (pre-3.13)")
```

### ✅ Tier 2 Interpreter (Micro-ops)
Python 3.13 introduce el intérprete Tier 2 con micro-instrucciones (uops), que forma la base para el futuro JIT. Esto mejora el rendimiento en código hot.

### ✅ Estructura con `asyncio.TaskGroup`
Sustituye a `asyncio.gather` para una gestión de errores más limpia (Exception Groups).

```python
import asyncio

async def main():
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(fetch_api())
        task2 = tg.create_task(query_db())
    # Si falla una, las demás se cancelan automáticamente.
```

### ✅ Manejo de Errores con Exception Groups (`except*`)
Los `TaskGroups` lanzan `ExceptionGroup` si una o más tareas fallan. Utiliza `except*` para capturar tipos específicos.

```python
import asyncio
from loguru import logger

async def main():
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(risky_operation())
    except* ValueError as eg:
        for exc in eg.exceptions:
            logger.error(f"Error de valor: {exc}")
    except* ConnectionError as eg:
        logger.error("Error de conexión en una o más tareas")
```

### ✅ ThreadPoolExecutor para CPU-bound
En modo free-threaded (`python3.13t`), puedes lograr paralelismo real.

```python
from concurrent.futures import ThreadPoolExecutor

def heavy_computation(n: int) -> int:
    return sum(i * i for i in range(n))

with ThreadPoolExecutor(max_workers=4) as executor:
    # En modo free-threaded: paralelismo real
    results = list(executor.map(heavy_computation, [10000] * 10))
```

---

## 🚀 FastAPI + SQLAlchemy 2.0 (Patrón de Servicio)

Integración completa con **Pydantic v2** y **SQLAlchemy Async**.

### Esquema (Pydantic v2)
```python
from pydantic import BaseModel, ConfigDict, EmailStr

class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # Reemplaza a orm_mode
    email: EmailStr
    full_name: str
```

### Capa de Servicio
```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_active_user(self, user_id: int) -> User | None:
        # Uso de eager loading con selectinload
        result = await self.db.execute(
            select(User).options(selectinload(User.roles)).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
```

---

## 🔐 Seguridad y Calidad de Código

### 1. Interpolación Segura
Usa f-strings con cuidado. Evita insertar datos de usuario directamente en queries o comandos.

```python
# ✅ Correcto: Queries parametrizadas
stmt = select(User).where(User.email == user_email)

# ❌ Incorrecto: Vulnerable a inyección
# f"SELECT * FROM users WHERE email = '{user_email}'"
```

### 2. Hashing y JWT
- **Hashing**: `passlib` con `bcrypt`. No guardes nunca texto plano.
- **JWT**: `python-jose` o `PyJWT`. Siempre incluye fecha de expiración (`exp`) y usa `HS256` o superior.

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

### 3. Ruff y Mypy (Calidad)
Configuración recomendada en `pyproject.toml`:
```toml
[tool.ruff]
target-version = "py313"
select = ["E", "F", "I", "B", "UP", "ASYNC"]

[tool.mypy]
python_version = "3.13"
strict = true
```

---

## 🧪 Testing y Logging

### Pruebas Asíncronas
Usa `pytest-asyncio` con fixtures de base de datos en memoria (SQLite+aiosqlite).

```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_user_creation(db_session: AsyncSession):
    service = UserService(db_session)
    user = await service.create_user(UserCreate(email="test@test.com"))
    assert user.id is not None
```

### Fixture de Base de Datos en Memoria
```python
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

@pytest.fixture
async def db_session():
    """Sesión de prueba con base de datos en memoria."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as session:
        yield session
    
    await engine.dispose()
```

### Logging Estructurado con Loguru
```python
from loguru import logger

logger.info("Operación completada", extra={"user_id": 1})
logger.error("Fallo crítico en DB", error=str(e))
```

---

## 💡 Novedades Específicas de Python 3.13

### ✅ REPL Interactivo Mejorado
El nuevo REPL incluye:
- **Colores y resaltado de sintaxis**
- **Edición multilínea** mejorada
- **Historial de comandos** persistente
- **Sugerencias** de autocompletado

```bash
# Ejecutar el nuevo REPL
python3.13
```

### ✅ `copy.replace()` para Objetos Inmutables
Nueva función que crea copias modificadas de objetos que soportan el protocolo.

```python
import copy
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    x: int
    y: int

p1 = Point(1, 2)
p2 = copy.replace(p1, x=10)  # Point(x=10, y=2)
```

### ✅ Mensajes de Error Mejorados
Python 3.13 continúa mejorando los mensajes de error con sugerencias contextuales.

```python
# Antes (genérico):
# NameError: name 'prnt' is not defined

# Python 3.13 (con sugerencia):
# NameError: name 'prnt' is not defined. Did you mean: 'print'?
```

### ✅ `@typing.override` Decorator
Marca métodos que sobrescriben métodos de la clase base (ya disponible en 3.12, consolidado en 3.13).

```python
from typing import override

class Base:
    def process(self) -> None:
        pass

class Child(Base):
    @override
    def process(self) -> None:  # ✅ Verificado por type checkers
        print("Overridden!")
```

## 📚 Referencias

- [What's New in Python 3.13](https://docs.python.org/3.13/whatsnew/3.13.html)
- [PEP 705 – TypedDict: ReadOnly](https://peps.python.org/pep-0705/)
- [PEP 703 – Making the GIL Optional](https://peps.python.org/pep-0703/)
- [Python 3.13 Release Schedule](https://peps.python.org/pep-0719/)
