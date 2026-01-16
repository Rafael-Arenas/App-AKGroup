---
trigger: always_on
---

---
trigger: always_on
---

---
trigger: always_on
---

# Guía de Mejores Prácticas SQLAlchemy 2.0 para Agentes de IA (2025)

Esta guía establece los estándares, patrones y mejores prácticas para el desarrollo con SQLAlchemy 2.0, optimizada para la interacción entre agentes de IA y desarrolladores.

---

## 🎯 Filosofía Core de SQLAlchemy 2.0

| Principio | Descripción |
|:----------|:------------|
| **Declaraciones Explícitas** | Preferir `select()` explícito sobre patrones implícitos |
| **Tipado Estático** | Uso obligatorio de `Mapped[]` y `mapped_column()` |
| **Transacciones Explícitas** | Demarcación clara de inicio/fin de transacciones |
| **Unificación Core/ORM** | API consistente entre Core y ORM |

---

## 🏗️ Definición de Modelos

### ✅ DeclarativeBase y Tipado Moderno

Uso obligatorio de `DeclarativeBase`, `Mapped[]` y `mapped_column()`:

```python
from datetime import datetime
from typing import Optional
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    """Base declarativa para todos los modelos."""
    pass

class User(Base):
    __tablename__ = "users"
    
    # Primary key con tipo explícito
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Campos obligatorios
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(100))
    
    # Campos opcionales (nullable)
    bio: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Timestamps con defaults
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(onupdate=datetime.utcnow)
    
    # Relaciones tipadas
    posts: Mapped[list["Post"]] = relationship(back_populates="author")
```

### ✅ Convenciones de Nomenclatura

Configura convenciones consistentes para constraints:

```python
from sqlalchemy import MetaData

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

### ✅ Integración con Dataclasses

SQLAlchemy 2.0 soporta mapping directo de dataclasses:

```python
from sqlalchemy.orm import MappedAsDataclass

class Product(MappedAsDataclass, Base):
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String(100))
    price: Mapped[float]
    stock: Mapped[int] = mapped_column(default=0)
```

---

## ⚡ Operaciones Asíncronas

### ✅ Configuración del Engine Async

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Motor asíncrono único por servicio
async_engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/db",
    echo=False,  # True solo para debug
    pool_size=5,
    max_overflow=10,
)

# Factory de sesiones
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Evita re-queries tras commit
    autoflush=False,
)
```

### ✅ Gestión de Sesiones (Per-Request)

**Regla crítica**: Sesiones de vida corta, una por request/operación.

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_db_session() -> AsyncSession:
    """Context manager para sesiones de vida corta."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Uso en FastAPI como dependencia
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
```

### ✅ Transacciones Explícitas

```python
async def transfer_funds(session: AsyncSession, from_id: int, to_id: int, amount: float):
    """Transacción explícita con context manager."""
    async with session.begin():
        from_account = await session.get(Account, from_id)
        to_account = await session.get(Account, to_id)
        
        from_account.balance -= amount
        to_account.balance += amount
        # Commit automático al salir del bloque
```

---

## 🔍 Consultas y Select

### ✅ `select()` como Interfaz Principal

**Obligatorio**: Usar `select()` en lugar de `session.query()`:

```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload

# ✅ Correcto: select() moderno
async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

# ❌ Incorrecto: Query legacy (deprecated)
# session.query(User).filter(User.email == email).first()
```

### ✅ session.get() para Primary Keys

Usa `session.get()` para búsquedas por PK (verifica identity map primero):

```python
async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    return await session.get(User, user_id)
```

### ✅ Selección de Columnas Específicas

Evita over-fetching:

```python
# Solo columnas necesarias
stmt = select(User.id, User.email, User.full_name).where(User.is_active == True)
result = await session.execute(stmt)
rows = result.all()  # Lista de tuplas (id, email, full_name)
```

---

## 📦 Eager Loading (Carga Anticipada)

### Estrategias Disponibles

| Estrategia | Uso Recomendado | Query |
|:-----------|:----------------|:------|
| `selectinload()` | **Colecciones (1:N, M:N)** | Segunda query con `IN` |
| `joinedload()` | Relaciones 1:1 o M:1 | JOIN en misma query |
| `subqueryload()` | Colecciones grandes | Subconsulta separada |
| `lazyload()` | Default, evitar en loops | Query por acceso |

### ✅ selectinload() para Colecciones

**Recomendado** para prevenir N+1:

```python
from sqlalchemy.orm import selectinload

async def get_user_with_posts(session: AsyncSession, user_id: int) -> User | None:
    stmt = (
        select(User)
        .options(selectinload(User.posts))
        .where(User.id == user_id)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
```

### ✅ Carga Anidada

```python
stmt = (
    select(User)
    .options(
        selectinload(User.posts).selectinload(Post.comments),
        selectinload(User.roles),
    )
    .where(User.id == user_id)
)
```

### ✅ joinedload() para Relaciones Simples

```python
from sqlalchemy.orm import joinedload

async def get_post_with_author(session: AsyncSession, post_id: int) -> Post | None:
    stmt = (
        select(Post)
        .options(joinedload(Post.author))
        .where(Post.id == post_id)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
```

---

## 🔄 Operaciones CRUD

### ✅ Creación

```python
async def create_user(session: AsyncSession, data: UserCreate) -> User:
    user = User(
        email=data.email,
        full_name=data.full_name,
        hashed_password=hash_password(data.password),
    )
    session.add(user)
    await session.flush()  # Genera ID sin commit
    await session.refresh(user)  # Carga valores generados
    return user
```

### ✅ Actualización

```python
from sqlalchemy import update

# Actualización en masa (eficiente)
async def deactivate_old_users(session: AsyncSession, days: int):
    cutoff = datetime.utcnow() - timedelta(days=days)
    stmt = (
        update(User)
        .where(User.last_login < cutoff)
        .values(is_active=False)
    )
    await session.execute(stmt)

# Actualización de instancia
async def update_user(session: AsyncSession, user_id: int, data: UserUpdate) -> User:
    user = await session.get(User, user_id)
    if not user:
        raise NotFoundError("User not found")
    
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    
    await session.flush()
    return user
```

### ✅ Eliminación

```python
from sqlalchemy import delete

# Eliminación en masa
async def delete_expired_tokens(session: AsyncSession):
    stmt = delete(Token).where(Token.expires_at < datetime.utcnow())
    await session.execute(stmt)

# Eliminación de instancia
async def delete_user(session: AsyncSession, user_id: int):
    user = await session.get(User, user_id)
    if user:
        await session.delete(user)
```

---

## 🏛️ Patrón Repository/Service

### ✅ Capa de Servicio

```python
from typing import Sequence

class UserService:
    """Servicio de dominio para operaciones de usuario."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, user_id: int) -> User | None:
        return await self.session.get(User, user_id)
    
    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def list_active(self, limit: int = 100, offset: int = 0) -> Sequence[User]:
        stmt = (
            select(User)
            .where(User.is_active == True)
            .order_by(User.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def create(self, data: UserCreate) -> User:
        user = User(**data.model_dump())
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user
```

### ✅ Integración con FastAPI

```python
from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)

@router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
):
    user = await service.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

---

## ⚠️ Anti-Patrones a Evitar

| ❌ Anti-Patrón | ✅ Solución |
|:---------------|:-----------|
| `session.query()` | Usar `select()` |
| Sesiones globales | Sesiones per-request |
| Lazy loading en loops | Eager loading con `selectinload()` |
| `expire_on_commit=True` sin refresh | Usar `expire_on_commit=False` o `refresh()` |
| Concatenación de SQL | Parámetros con `bindparam()` |
| Modelos en migraciones | Tablas definidas en migración |
| `async_scoped_session` | Pasar sesión explícitamente |