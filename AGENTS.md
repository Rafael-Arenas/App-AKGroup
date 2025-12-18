# AGENTS.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**App-AKGroup** is a business management system (Sistema de gestión empresarial) for AK Group, built as a cross-platform desktop application using Flet (Flutter-based framework).

## Technology Stack

- **Python**: >=3.13.0,<4.0
- **Dependency Management**: Poetry 2.1.3+
- **UI Framework**: Flet 0.28.3 (cross-platform desktop UI)
- **Database**: SQLAlchemy 2.0.44 (ORM) + aiosqlite (async operations)
- **Data Validation**: Pydantic 2.12.3 + pydantic-settings
- **Migrations**: Alembic 1.17.0
- **Logging**: Loguru 0.7.3
- **Date/Time**: Pendulum 3.1.0
- **Excel**: openpyxl 3.1.5

## Development Commands

### Environment Setup
```bash
# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Check Python version
poetry env info

# Add new dependency
poetry add <package-name>

# Add dev dependency
poetry add --group dev <package-name>
```

### Code Quality Tools
```bash
# Format code with Black (88 char line length)
black .

# Lint with Ruff (modern replacement for flake8/pylint)
ruff check .
ruff check --fix .

# Type checking with MyPy
mypy .

# Run all quality checks
black . && ruff check --fix . && mypy .
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

### Running the Application

The application has 3 convenient entry points in the root directory:

```bash
# Run complete application (Backend + Frontend)
python run_app.py

# Run only the backend (FastAPI server on http://localhost:8000)
python run_backend.py

# Run only the frontend (Flet desktop app)
python run_frontend.py
```

Alternative commands with Poetry:
```bash
poetry run python run_app.py      # Complete application
poetry run python run_backend.py  # Backend only
poetry run python run_frontend.py # Frontend only
```

**Note:** When running frontend separately, ensure the backend is running first on http://localhost:8000

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_specific.py

# Run specific test function
pytest tests/test_specific.py::test_function_name
```

## Architecture & Patterns

### Code Organization

The codebase follows clean architecture principles with separation of concerns:

- **models/**: SQLAlchemy ORM models (database schema)
- **repositories/**: Data access layer implementing Repository Pattern
- **services/**: Business logic layer
- **ui/**: Flet UI components and views
- **config/**: Configuration management using pydantic-settings
- **utils/**: Shared utility functions
- **migrations/**: Alembic database migrations

### Design Patterns in Use

1. **Repository Pattern**: All database access through repository classes
2. **Dependency Injection**: Services receive dependencies via constructors
3. **Factory Pattern**: Object creation abstracted through factories
4. **Singleton Pattern**: Shared resources (DB connections, configs)

### SOLID Principles

The codebase strictly adheres to SOLID principles:
- **Single Responsibility**: One class/function = one responsibility
- **Open/Closed**: Extend via abstractions, not modifications
- **Liskov Substitution**: Subtypes must be substitutable for base types
- **Interface Segregation**: Multiple specific interfaces over one general
- **Dependency Inversion**: Depend on abstractions, not concrete implementations

## Code Standards

### Naming Conventions
- **Functions/Variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Modules**: `lowercase.py`
- **Private members**: `_prefix`

### Type Hints & Documentation
- **Required**: Type hints on all function signatures
- **Required**: Docstrings on all public functions/classes
- **Format**: Google/NumPy docstring style with Args, Returns, Raises, Example

Example:
```python
def calculate_total(items: List[dict], tax_rate: float = 0.19) -> float:
    """
    Calcula el total incluyendo impuestos.

    Args:
        items: Lista de items con precios
        tax_rate: Tasa de impuesto (default: 0.19)

    Returns:
        Total con impuestos aplicados

    Raises:
        ValueError: Si items está vacío

    Example:
        >>> calculate_total([{"price": 100}], 0.19)
        119.0
    """
```

### Import Organization
1. Standard library imports
2. Third-party imports
3. Local application imports

Each group separated by blank line.

### Error Handling
- Use specific exception types (never bare `except`)
- Create custom exceptions inheriting from base application exceptions
- Use context managers (`with` statements) for resource management
- Always log exceptions with appropriate level (warning/error/exception)

### Logging Strategy
```python
from loguru import logger

# Info: Normal flow
logger.info("Processing order {order_id}", order_id=123)

# Debug: Detailed information
logger.debug("Order data: {data}", data=order_dict)

# Success: Successful operations
logger.success("Order {order_id} processed", order_id=123)

# Warning: Recoverable issues
logger.warning("Item {item_id} low stock", item_id=456)

# Error: Unrecoverable errors
logger.error("Failed to process {order_id}", order_id=123)

# Exception: Log with full traceback
logger.exception("Unexpected error processing order")
```

## Flet UI Architecture

### Component Structure
- Break UI into reusable components
- Each view should be a separate class
- Use `ft.UserControl` for custom components
- Maintain separation between UI and business logic

### State Management
- Services should handle business state
- UI components handle presentation state only
- Use `update()` to refresh UI after state changes

## Database Conventions

### Model Definitions
- Use SQLAlchemy declarative base
- Include `__tablename__` explicitly
- Add `__repr__` for debugging
- Use Pydantic models for validation/serialization

### Repository Pattern
```python
class IRepository(ABC, Generic[T]):
    """Base repository interface"""

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:
        pass

    @abstractmethod
    def get_all(self) -> List[T]:
        pass

    @abstractmethod
    def add(self, entity: T) -> T:
        pass

    @abstractmethod
    def update(self, entity: T) -> T:
        pass

    @abstractmethod
    def delete(self, id: int) -> None:
        pass
```

## Configuration Management

Use `pydantic-settings` for configuration:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

## File References

- **Best Practices Guide**: `PYTHON_BEST_PRACTICES.md` - Comprehensive coding standards
- **Dependencies**: `pyproject.toml` - All project dependencies and metadata
- **Gitignore**: `.gitignore` - Comprehensive ignore patterns

## Important Notes

1. **Python Version**: This project requires Python 3.13+ due to latest features
2. **Poetry Only**: Always use Poetry for dependency management, never pip directly
3. **No Bare Exceptions**: Always catch specific exception types
4. **Type Safety**: All functions must have complete type hints
5. **Testing**: Write tests for business logic and data access layers
6. **Async Operations**: Use aiosqlite for async database operations where needed
7. **Excel Integration**: Use openpyxl for import/export functionality
8. **Date/Time**: Use Pendulum for all date/time operations (timezone aware)

## Development Workflow

1. Create feature branch from main
2. Implement changes following code standards
3. Run formatters and linters (`black . && ruff check --fix .`)
4. Run type checker (`mypy .`)
5. Write/update tests
6. Run test suite (`pytest --cov`)
7. Create migration if models changed (`alembic revision --autogenerate`)
8. Commit with descriptive message
9. Create pull request

## Reference Documentation

For detailed examples and patterns, always refer to:
- `PYTHON_BEST_PRACTICES.md` for coding standards and patterns
- Project README for high-level overview
- Inline docstrings for specific function/class usage
