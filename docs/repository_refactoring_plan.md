# Plan de Refactorización de Repositorios

> **Fecha**: Enero 2026  
> **Objetivo**: Modernizar y optimizar la capa de repositorios siguiendo las mejores prácticas de SQLAlchemy 2.0 y Python 3.13+

---

## 📊 Estado Actual

### ✅ Lo que está bien implementado:
- Uso de `select()` moderno de SQLAlchemy 2.0
- Eager loading con `selectinload()` para evitar N+1
- Patrón Repository con interfaz abstracta `IRepository`
- Documentación detallada con docstrings
- Logging consistente en operaciones

---

## 🚀 Fases de Implementación

---

## Fase 1: Tipado Moderno (Prioridad Alta)

**Objetivo**: Actualizar todo el tipado a sintaxis moderna de Python 3.10+

**Archivos afectados**: Todos los repositorios

### Cambios requeridos:

#### 1.1 Reemplazar `Optional[T]` por `T | None`
```python
# ❌ Antes
from typing import Optional
def get_by_id(self, id: int) -> Optional[T]:

# ✅ Después
def get_by_id(self, id: int) -> T | None:
```

#### 1.2 Reemplazar `List[T]` por `list[T]`
```python
# ❌ Antes
from typing import List
def get_all(self) -> List[T]:

# ✅ Después
def get_all(self) -> list[T]:
```

#### 1.3 Usar `Sequence` para retornos inmutables
```python
# ✅ Más correcto semánticamente
from collections.abc import Sequence

def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[T]:
```

#### 1.4 Mejorar TypeVar con bound
```python
# ✅ TypeVar más preciso
from sqlalchemy.orm import DeclarativeBase

T = TypeVar("T", bound=DeclarativeBase)
```

### Checklist Fase 1:
- [x] `base.py` - Actualizar tipado base ✅
- [x] `core/*.py` - Actualizar tipado en core ✅
- [x] `business/*.py` - Actualizar tipado en business ✅
- [x] `lookups/*.py` - Actualizar tipado en lookups ✅

**Estado: ✅ COMPLETADA** (2026-01-15)

---

## Fase 2: Limpieza de Código (Prioridad Alta)

**Objetivo**: Eliminar redundancias y código innecesario

### 2.1 Eliminar `list()` redundante
```python
# ❌ Antes (conversión innecesaria)
entities = list(result.scalars().all())

# ✅ Después (.all() ya retorna lista)
entities = result.scalars().all()
```

### 2.2 Eliminar imports no usados
```python
# En company_repository.py
from sqlalchemy import or_, select  # 'or_' no se usa → eliminar
```

### 2.3 Optimizar método `update()` en BaseRepository
```python
# ❌ Antes: Doble query (get_by_id + merge)
existing = self.get_by_id(entity.id)
if not existing:
    raise NotFoundException(...)
self.session.merge(entity)

# ✅ Después: Una sola operación
merged = self.session.merge(entity)
self.session.flush()
return merged
```

### Checklist Fase 2:
- [x] Eliminar `list()` redundantes en todos los archivos ✅ (ya hecho en Fase 1)
- [x] Eliminar imports no usados (8 corregidos con ruff --fix) ✅
- [x] Optimizar `update()` en `base.py` - Ahora usa `exists()` + retorna merged ✅
- [x] Agregar método `exists()` eficiente a BaseRepository ✅

**Estado: ✅ COMPLETADA** (2026-01-15)

---

## Fase 3: Operaciones Bulk (Prioridad Media)

**Objetivo**: Añadir métodos para operaciones masivas

### 3.1 Crear múltiples entidades
```python
def create_many(self, entities: list[T]) -> list[T]:
    """Crear múltiples entidades en una operación."""
    self.session.add_all(entities)
    self.session.flush()
    return entities
```

### 3.2 Actualización masiva
```python
from sqlalchemy import update

def update_many(self, ids: list[int], values: dict) -> int:
    """Actualizar múltiples registros por IDs."""
    stmt = update(self.model).where(self.model.id.in_(ids)).values(**values)
    result = self.session.execute(stmt)
    self.session.flush()
    return result.rowcount
```

### 3.3 Eliminación masiva
```python
from sqlalchemy import delete

def delete_many(self, ids: list[int]) -> int:
    """Eliminar múltiples registros por IDs."""
    stmt = delete(self.model).where(self.model.id.in_(ids))
    result = self.session.execute(stmt)
    self.session.flush()
    return result.rowcount
```

### Checklist Fase 3:
- [x] Implementar `create_many()` en BaseRepository ✅
- [x] Implementar `update_many()` en BaseRepository ✅
- [x] Implementar `delete_many()` en BaseRepository ✅
- [x] Agregar tests para operaciones bulk (12 tests nuevos) ✅

**Estado: ✅ COMPLETADA** (2026-01-15)

---

## Fase 4: Query Builder Pattern (Prioridad Media)

**Objetivo**: Centralizar construcción de queries con filtros dinámicos

### 4.1 Método base para construir queries
```python
from sqlalchemy.sql import Select

def _build_query(
    self,
    filters: dict | None = None,
    order_by: str | None = None,
    descending: bool = False,
    skip: int = 0,
    limit: int = 100,
) -> Select:
    """Construye query con filtros dinámicos."""
    stmt = select(self.model)
    
    if filters:
        for key, value in filters.items():
            if value is not None:
                column = getattr(self.model, key, None)
                if column is not None:
                    stmt = stmt.filter(column == value)
    
    if order_by:
        column = getattr(self.model, order_by)
        order = column.desc() if descending else column.asc()
        stmt = stmt.order_by(order)
    
    return stmt.offset(skip).limit(limit)
```

### 4.2 Método flexible de ordenamiento
```python
def get_all(
    self,
    skip: int = 0,
    limit: int = 100,
    order_by: str = "id",
    descending: bool = False
) -> Sequence[T]:
    """Obtener todos con ordenamiento flexible."""
    stmt = self._build_query(
        order_by=order_by,
        descending=descending,
        skip=skip,
        limit=limit
    )
    return self.session.execute(stmt).scalars().all()
```

### Checklist Fase 4:
- [x] Implementar `_build_query()` en BaseRepository ✅
- [x] Refactorizar `get_all()` para usar query builder (añadió order_by, descending) ✅
- [x] Crear método `find_by()` genérico con filtros ✅
- [x] Agregar tests para query builder (12 tests nuevos) ✅

**Estado: ✅ COMPLETADA** (2026-01-15)

---

## Fase 5: Repositorio Genérico para Lookups (Prioridad Baja)

**Objetivo**: Reducir duplicación en repositorios de lookup

### 5.1 Crear GenericLookupRepository
```python
class GenericLookupRepository(BaseRepository[T]):
    """Repositorio genérico para modelos lookup."""
    
    def get_by_name(self, name: str) -> T | None:
        """Buscar por nombre exacto."""
        stmt = select(self.model).filter(self.model.name == name)
        return self.session.execute(stmt).scalar_one_or_none()
    
    def get_by_code(self, code: str, normalize: str = "upper") -> T | None:
        """Buscar por código con normalización."""
        value = code.upper() if normalize == "upper" else code.lower()
        stmt = select(self.model).filter(self.model.code == value)
        return self.session.execute(stmt).scalar_one_or_none()
    
    def get_active(self, skip: int = 0, limit: int = 100) -> Sequence[T]:
        """Obtener solo registros activos."""
        stmt = (
            select(self.model)
            .filter(self.model.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        return self.session.execute(stmt).scalars().all()
```

### 5.2 Simplificar repositorios lookup
```python
# ❌ Antes: Muchas clases casi idénticas
class CompanyTypeRepository(BaseRepository[CompanyType]):
    def get_by_name(self, name: str) -> Optional[CompanyType]:
        stmt = select(CompanyType).filter(CompanyType.name == name)
        return self.session.execute(stmt).scalar_one_or_none()

# ✅ Después: Heredar de GenericLookupRepository
class CompanyTypeRepository(GenericLookupRepository[CompanyType]):
    def __init__(self, session: Session):
        super().__init__(session, CompanyType)
```

### Checklist Fase 5:
- [ ] Crear `GenericLookupRepository` en `base.py`
- [ ] Refactorizar `lookup_repository.py` para usar genérico
- [ ] Estandarizar convención de normalización (upper/lower)
- [ ] Documentar convenciones

---

## Fase 6: Repository Factory (Prioridad Baja)

**Objetivo**: Centralizar creación de repositorios

### 6.1 Implementar RepositoryFactory
```python
from functools import cached_property

class RepositoryFactory:
    """Factory para obtener repositorios con sesión compartida."""
    
    def __init__(self, session: Session):
        self.session = session
    
    @cached_property
    def companies(self) -> CompanyRepository:
        return CompanyRepository(self.session)
    
    @cached_property
    def orders(self) -> OrderRepository:
        return OrderRepository(self.session)
    
    @cached_property
    def quotes(self) -> QuoteRepository:
        return QuoteRepository(self.session)
    
    # ... otros repositorios
```

### 6.2 Uso en servicios
```python
# ❌ Antes
class OrderService:
    def __init__(self, session: Session):
        self.order_repo = OrderRepository(session)
        self.quote_repo = QuoteRepository(session)
        self.company_repo = CompanyRepository(session)

# ✅ Después
class OrderService:
    def __init__(self, repos: RepositoryFactory):
        self.repos = repos
    
    def create_order(self, data: OrderCreate):
        company = self.repos.companies.get_by_id(data.company_id)
        # ...
```

### Checklist Fase 6:
- [ ] Crear `RepositoryFactory` en `__init__.py`
- [ ] Actualizar servicios para usar factory
- [ ] Actualizar inyección de dependencias

---

## 📝 Notas de Implementación

### Orden recomendado:
1. **Fase 1 + 2** pueden hacerse juntas (bajo riesgo)
2. **Fase 3** requiere tests adicionales
3. **Fase 4** puede introducirse gradualmente
4. **Fase 5 + 6** son opcionales, solo si hay tiempo

### Testing:
- Cada fase debe incluir tests unitarios
- Ejecutar suite completa después de cada fase
- Verificar que no hay regresiones

### Compatibilidad:
- Mantener backward compatibility donde sea posible
- Deprecar métodos viejos antes de eliminarlos

---

## 📅 Estimación de Tiempo

| Fase | Esfuerzo | Riesgo |
|:-----|:---------|:-------|
| Fase 1 | 2-3 horas | Bajo |
| Fase 2 | 1-2 horas | Bajo |
| Fase 3 | 2-3 horas | Medio |
| Fase 4 | 3-4 horas | Medio |
| Fase 5 | 2-3 horas | Bajo |
| Fase 6 | 2-3 horas | Medio |

**Total estimado**: 12-18 horas

---

## ✅ Criterios de Éxito

- [ ] Todos los tests pasan después de cada fase
- [ ] No hay regresiones en funcionalidad
- [ ] Código más limpio y mantenible
- [ ] Tipado completo sin errores de mypy
- [ ] Documentación actualizada
