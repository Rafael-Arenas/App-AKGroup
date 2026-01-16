---
trigger: always_on
---

---
trigger: always_on
---

---
trigger: always_on
---

# SQLAlchemy 2.0 - Guía Extendida (Testing, Migraciones y Seguridad)

Complemento de la guía principal con secciones avanzadas.

---

## 🔗 Relaciones Many-to-Many

```python
from sqlalchemy import Table, Column, ForeignKey

# Tabla de asociación
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("role_id", ForeignKey("roles.id"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    roles: Mapped[list["Role"]] = relationship(secondary=user_roles, back_populates="users")

class Role(Base):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    users: Mapped[list["User"]] = relationship(secondary=user_roles, back_populates="roles")
```

---

## 🔒 Seguridad y Robustez

### ✅ Queries Parametrizadas

SQLAlchemy usa parámetros por defecto, **nunca concatenes strings**:

```python
# ✅ Correcto: Parametrizado automáticamente
stmt = select(User).where(User.email == user_input)

# ❌ Incorrecto: Vulnerable a SQL Injection
# f"SELECT * FROM users WHERE email = '{user_input}'"
```

### ✅ Validación con Pydantic

```python
from pydantic import BaseModel, EmailStr, ConfigDict

class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # Reemplaza orm_mode
    
    id: int
    email: EmailStr
    full_name: str

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
```

---

## 📊 Migraciones con Alembic

### ✅ Configuración Recomendada

```python
# alembic/env.py
from models import Base

target_metadata = Base.metadata

def run_migrations_offline():
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,  # Detecta cambios de tipo
    )

async def run_async_migrations():
    connectable = async_engine_from_config(config.get_section(config.config_ini_section))
    
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
```

### ✅ Reglas para Migraciones

1. **No uses modelos ORM en migraciones** - Define tablas directamente
2. **Siempre usa naming convention** - Constraints con nombres predecibles
3. **Revisa migraciones generadas** - Alembic puede generar operaciones incorrectas

---

## 🧪 Testing

### ✅ Fixtures con pytest-asyncio

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

@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    service = UserService(db_session)
    user = await service.create(UserCreate(email="test@example.com", full_name="Test"))
    
    assert user.id is not None
    assert user.email == "test@example.com"
```

---

## 📚 Referencias

- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/)
- [What's New in SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/changelog/whatsnew_20.html)
- [Async I/O Extension](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
