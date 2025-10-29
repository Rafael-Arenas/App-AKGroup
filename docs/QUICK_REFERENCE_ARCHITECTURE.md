# Quick Reference: Architecture Patterns

## How to Implement a New Model

This guide shows you how to implement the complete architecture for any new model in the AKGroup project.

---

## Step 1: Create the Repository

**Location:** `src/repositories/core/{model_name}_repository.py`

```python
"""
Repositorio para {ModelName}.

Maneja el acceso a datos para {description}.
"""

from typing import Optional, List
from sqlalchemy.orm import Session

from src.models.core.{model_file} import {ModelName}
from src.repositories.base import BaseRepository
from src.utils.logger import logger


class {ModelName}Repository(BaseRepository[{ModelName}]):
    """
    Repositorio para {ModelName} con métodos específicos.

    Example:
        repo = {ModelName}Repository(session)
        entity = repo.get_by_something(value)
    """

    def __init__(self, session: Session):
        """
        Inicializa el repositorio de {ModelName}.

        Args:
            session: Sesión de SQLAlchemy
        """
        super().__init__(session, {ModelName})

    # Add custom query methods here
    def get_by_custom_field(self, value: str) -> Optional[{ModelName}]:
        """
        Custom search method.

        Args:
            value: Value to search for

        Returns:
            {ModelName} if exists, None otherwise

        Example:
            entity = repo.get_by_custom_field("value")
        """
        logger.debug(f"Buscando {ModelName} por custom_field: {value}")

        entity = (
            self.session.query({ModelName})
            .filter({ModelName}.custom_field == value)
            .first()
        )

        if entity:
            logger.debug(f"{ModelName} encontrado: id={entity.id}")
        else:
            logger.debug(f"No se encontró {ModelName}")

        return entity
```

---

## Step 2: Create the Service

**Location:** `src/services/core/{model_name}_service.py`

```python
"""
Servicio de lógica de negocio para {ModelName}.

Implementa validaciones y reglas de negocio.
"""

from sqlalchemy.orm import Session

from src.models.core.{model_file} import {ModelName}
from src.repositories.core.{model_name}_repository import {ModelName}Repository
from src.schemas.core.{model_name} import (
    {ModelName}Create,
    {ModelName}Update,
    {ModelName}Response
)
from src.services.base import BaseService
from src.exceptions.service import ValidationException
from src.exceptions.repository import NotFoundException
from src.utils.logger import logger


class {ModelName}Service(
    BaseService[{ModelName}, {ModelName}Create, {ModelName}Update, {ModelName}Response]
):
    """
    Servicio para {ModelName} con validaciones de negocio.

    Example:
        service = {ModelName}Service(repository, session)
        entity = service.create({ModelName}Create(...), user_id=1)
    """

    def __init__(
        self,
        repository: {ModelName}Repository,
        session: Session,
    ):
        """
        Inicializa el servicio de {ModelName}.

        Args:
            repository: Repositorio de {ModelName}
            session: Sesión de SQLAlchemy
        """
        super().__init__(
            repository=repository,
            session=session,
            model={ModelName},
            response_schema={ModelName}Response,
        )
        self.{model_name}_repo: {ModelName}Repository = repository

    def validate_create(self, entity: {ModelName}) -> None:
        """
        Valida reglas de negocio antes de crear.

        Args:
            entity: Entidad a validar

        Raises:
            ValidationException: Si la validación falla
        """
        logger.debug(f"Validando creación de {ModelName}")

        # Add your validation logic here
        # Example: Check uniqueness
        existing = self.{model_name}_repo.get_by_custom_field(entity.custom_field)
        if existing:
            raise ValidationException(
                f"Ya existe {ModelName} con ese valor",
                details={"custom_field": entity.custom_field}
            )

        logger.debug("Validación de creación exitosa")

    def validate_update(self, entity: {ModelName}) -> None:
        """
        Valida reglas de negocio antes de actualizar.

        Args:
            entity: Entidad a validar

        Raises:
            ValidationException: Si la validación falla
        """
        logger.debug(f"Validando actualización de {ModelName} id={entity.id}")

        # Add your validation logic here
        # Example: Check uniqueness excluding self
        existing = self.{model_name}_repo.get_by_custom_field(entity.custom_field)
        if existing and existing.id != entity.id:
            raise ValidationException(
                f"Ya existe otro {ModelName} con ese valor",
                details={
                    "custom_field": entity.custom_field,
                    "existing_id": existing.id
                }
            )

        logger.debug("Validación de actualización exitosa")

    # Add custom business logic methods here
    def custom_business_method(self, param: str) -> {ModelName}Response:
        """
        Custom business logic.

        Args:
            param: Parameter

        Returns:
            Entity response

        Example:
            result = service.custom_business_method("value")
        """
        logger.info(f"Servicio: ejecutando lógica personalizada")

        entity = self.{model_name}_repo.get_by_custom_field(param)
        if not entity:
            raise NotFoundException(
                f"{ModelName} no encontrado",
                details={"param": param}
            )

        return self.response_schema.model_validate(entity)
```

---

## Step 3: Create the Schemas

**Location:** `src/schemas/core/{model_name}.py`

```python
"""
Schemas de Pydantic para {ModelName}.

Define los schemas de validación para operaciones CRUD.
"""

from typing import Optional
from pydantic import Field, field_validator

from src.schemas.base import BaseSchema, BaseResponse


# ============================================================================
# {MODEL_NAME} SCHEMAS
# ============================================================================

class {ModelName}Create(BaseSchema):
    """
    Schema para crear un nuevo {ModelName}.

    Example:
        data = {ModelName}Create(
            field1="value1",
            field2="value2"
        )
    """

    field1: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Field description"
    )
    field2: Optional[str] = Field(
        None,
        max_length=200,
        description="Optional field"
    )
    foreign_key_id: int = Field(
        ...,
        gt=0,
        description="Foreign key reference"
    )

    @field_validator('field1')
    @classmethod
    def field1_not_empty(cls, v: str) -> str:
        """Validates field1."""
        if not v.strip():
            raise ValueError("Field1 cannot be empty")
        return v.strip()

    @field_validator('field2')
    @classmethod
    def normalize_field2(cls, v: Optional[str]) -> Optional[str]:
        """Normalizes field2."""
        if v:
            return v.strip().upper()
        return v


class {ModelName}Update(BaseSchema):
    """
    Schema para actualizar un {ModelName}.

    All fields are optional - only provided fields will be updated.

    Example:
        data = {ModelName}Update(field1="new_value")
    """

    field1: Optional[str] = Field(None, min_length=1, max_length=100)
    field2: Optional[str] = Field(None, max_length=200)
    foreign_key_id: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None

    @field_validator('field1')
    @classmethod
    def field1_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v.strip():
                raise ValueError("Field1 cannot be empty")
            return v.strip()
        return v

    @field_validator('field2')
    @classmethod
    def normalize_field2(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return v.strip().upper()
        return v


class {ModelName}Response(BaseResponse):
    """
    Schema para respuesta de {ModelName}.

    Includes all fields.

    Example:
        entity = {ModelName}Response.model_validate(entity_orm)
        print(entity.field1)
    """

    field1: str
    field2: Optional[str] = None
    foreign_key_id: int
    is_active: bool

    # Optional: computed properties
    @property
    def custom_property(self) -> str:
        """Computed property."""
        return f"{self.field1} - {self.field2}"
```

---

## Step 4: Update __init__.py Files

### `src/repositories/core/__init__.py`
```python
from src.repositories.core.{model_name}_repository import {ModelName}Repository

__all__ = [
    ...,
    "{ModelName}Repository",
]
```

### `src/services/core/__init__.py`
```python
from src.services.core.{model_name}_service import {ModelName}Service

__all__ = [
    ...,
    "{ModelName}Service",
]
```

### `src/schemas/core/__init__.py`
```python
from src.schemas.core.{model_name} import (
    {ModelName}Create,
    {ModelName}Update,
    {ModelName}Response,
)

__all__ = [
    ...,
    "{ModelName}Create",
    "{ModelName}Update",
    "{ModelName}Response",
]
```

---

## Step 5: Usage Example

```python
from sqlalchemy.orm import Session
from src.repositories.core.{model_name}_repository import {ModelName}Repository
from src.services.core.{model_name}_service import {ModelName}Service
from src.schemas.core.{model_name} import {ModelName}Create

# Initialize
session = Session(...)
repository = {ModelName}Repository(session)
service = {ModelName}Service(repository, session)

# Create
data = {ModelName}Create(
    field1="value1",
    field2="value2",
    foreign_key_id=1
)
entity = service.create(data, user_id=1)
session.commit()

# Read
entity = service.get_by_id(1)
entities = service.get_all(skip=0, limit=100)

# Update
update_data = {ModelName}Update(field1="new_value")
updated = service.update(1, update_data, user_id=1)
session.commit()

# Delete (soft delete by default)
service.delete(1, user_id=1, soft=True)
session.commit()

# Custom methods
result = service.custom_business_method("param")
```

---

## Common Patterns

### Pattern 1: Unique Field Validation
```python
def validate_create(self, entity: Model) -> None:
    existing = self.repo.get_by_field(entity.field)
    if existing:
        raise ValidationException(
            f"Field already exists",
            details={"field": entity.field}
        )
```

### Pattern 2: Relationship Validation
```python
def validate_create(self, entity: Model) -> None:
    # Check foreign key exists
    if not self.other_repo.exists(entity.foreign_key_id):
        raise ValidationException(
            "Related entity not found",
            details={"foreign_key_id": entity.foreign_key_id}
        )
```

### Pattern 3: Business Rule Validation
```python
def validate_create(self, entity: Model) -> None:
    if entity.start_date > entity.end_date:
        raise BusinessRuleException(
            "Start date must be before end date",
            details={
                "start_date": entity.start_date,
                "end_date": entity.end_date
            }
        )
```

### Pattern 4: Cascade Deletion Check
```python
def delete(self, id: int, user_id: int, soft: bool = True) -> None:
    entity = self.repository.get_by_id(id)
    if not entity:
        raise NotFoundException("Entity not found")

    # Check for related entities
    related_count = self.repository.count_related(id)
    if related_count > 0:
        raise BusinessRuleException(
            f"Cannot delete: has {related_count} related entities"
        )

    super().delete(id, user_id, soft)
```

### Pattern 5: Default Value Management
```python
def validate_create(self, entity: Model) -> None:
    if entity.is_default:
        # Remove default flag from others
        existing_default = self.repo.get_default()
        if existing_default:
            existing_default.is_default = False
```

---

## Validation Rules Checklist

When implementing a new model, consider these validation rules:

- [ ] Required fields are not empty/null
- [ ] Unique fields don't already exist
- [ ] Email format is valid (if applicable)
- [ ] Phone format is valid (if applicable)
- [ ] Foreign keys reference existing entities
- [ ] Dates are in valid ranges
- [ ] Numeric values are within acceptable ranges
- [ ] Text fields meet length requirements
- [ ] Business rules are enforced
- [ ] Cascade deletion is handled correctly

---

## Testing Checklist

- [ ] Repository tests (CRUD operations)
- [ ] Service tests (business logic)
- [ ] Schema validation tests
- [ ] Integration tests
- [ ] Edge case tests
- [ ] Error handling tests

---

## Code Quality Checklist

- [ ] All functions have type hints
- [ ] All public functions have docstrings
- [ ] Logging statements added (debug, info, success, error)
- [ ] Exceptions are specific and documented
- [ ] Code follows PEP 8 and Black formatting
- [ ] Imports are organized (stdlib → third-party → local)
- [ ] No unused imports or variables
- [ ] MyPy type checking passes
- [ ] Ruff linting passes

---

## Quick Commands

```bash
# Format code
black .

# Lint
ruff check --fix .

# Type check
mypy .

# Create migration
alembic revision --autogenerate -m "Add {ModelName} architecture"

# Apply migration
alembic upgrade head

# Run tests
pytest tests/test_{model_name}.py

# Run with coverage
pytest --cov=src.repositories.core.{model_name}_repository
```

---

## Reference Examples

See these files for complete implementation examples:
- **Simple Model:** `src/services/core/service_service.py` (Service/Department)
- **With Relationships:** `src/services/core/contact_service.py` (Contact)
- **With Complex Logic:** `src/services/core/address_service.py` (Address)
- **Polymorphic:** `src/services/core/note_service.py` (Note)
- **With Unique Fields:** `src/services/core/staff_service.py` (Staff)

---

**Need Help?** Review `IMPLEMENTATION_SUMMARY.md` for detailed examples and patterns.
