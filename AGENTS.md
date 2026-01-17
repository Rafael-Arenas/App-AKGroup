# AGENTS.md

This file provides guidance to AI coding assistants when working with code in this repository.

## Project Overview

**App-AKGroup** is a business management system (Sistema de gestión empresarial) for AK Group, built as a cross-platform desktop application using Flet with a FastAPI backend.

## Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| **Language** | Python | ^3.13 |
| **Dependency Management** | Poetry | 2.1.3+ |
| **Backend API** | FastAPI | ^0.115.0 |
| **ASGI Server** | Uvicorn | ^0.34.0 |
| **UI Framework** | Flet | ^0.80.0 |
| **ORM** | SQLAlchemy | ^2.0.44 |
| **Async SQLite** | aiosqlite | ^0.21.0 |
| **MySQL Driver** | PyMySQL | ^1.1.0 |
| **Migrations** | Alembic | ^1.17.0 |
| **Validation** | Pydantic | ^2.12.3 |
| **Settings** | pydantic-settings | ^2.11.0 |
| **HTTP Client** | httpx | ^0.28.1 |
| **Logging** | Loguru | ^0.7.3 |
| **Date/Time** | Pendulum | ^3.1.0 |
| **Excel** | openpyxl | ^3.1.5 |
| **Crypto** | cryptography | ^44.0.0 |

### Dev Dependencies

| Tool | Version | Purpose |
|------|---------|---------|
| pytest | ^8.0.0 | Testing framework |
| pytest-cov | ^4.1.0 | Code coverage |
| pytest-asyncio | ^1.2.0 | Async test support |
| black | ^24.0.0 | Code formatter |
| ruff | ^0.1.0 | Linter |
| mypy | ^1.8.0 | Type checker |
| faker | ^37.12.0 | Test data generation |

## Project Structure

```
App-AKGroup/
├── src/
│   ├── backend/           # FastAPI backend
│   │   ├── api/           # API routes (endpoints)
│   │   ├── config/        # Configuration (settings.py)
│   │   ├── models/        # SQLAlchemy ORM models
│   │   │   ├── base/      # Base classes, mixins, types
│   │   │   ├── core/      # Core entities (Company, Contact, etc.)
│   │   │   └── business/  # Business entities (Quote, Order, Invoice)
│   │   ├── repositories/  # Data access layer (Repository Pattern)
│   │   ├── services/      # Business logic layer
│   │   ├── exceptions/    # Custom exceptions
│   │   └── utils/         # Utilities (logger, helpers)
│   ├── frontend/          # Flet desktop application
│   │   ├── components/    # Reusable UI components
│   │   ├── views/         # Application views/screens
│   │   ├── services/      # Frontend services (API clients)
│   │   └── utils/         # Frontend utilities
│   └── shared/            # Shared code between backend and frontend
│       ├── providers/     # Time providers (TimeProvider, FakeTimeProvider)
│       ├── services/      # Shared services (TimezoneService)
│       ├── schemas/       # Pydantic schemas
│       ├── enums/         # Shared enumerations
│       └── constants.py   # Shared constants
├── tests/                 # Test suite
├── docs/                  # Documentation
│   └── agents/            # Agent-specific rules
├── alembic/               # Database migrations
└── run_*.py               # Application entry points
```

## Development Commands

### Running the Application
```bash
# Run complete application (Backend + Frontend)
poetry run python run_app.py

# Run only the backend (FastAPI server on http://localhost:8000)
poetry run python run_backend.py

# Run only the frontend (Flet desktop app)
poetry run python run_frontend.py
```

### Testing
```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=. --cov-report=html

# Run backend tests only
poetry run pytest tests/backend -v --tb=short
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

### Code Quality
```bash
# Format + Lint + Type check
black . && ruff check --fix . && mypy .
```

## ⚠️ CRITICAL: Centralized Time Management

**NEVER use direct calls to `datetime.now()`, `date.today()`, `pendulum.now()`, or `pendulum.today()` in the codebase.**

### Always Use TimeProvider

```python
from src.shared.providers import TimeProvider

# Module-level singleton
_time_provider = TimeProvider()

# Get current UTC datetime
now = _time_provider.now()  # Returns pendulum.DateTime

# Get current UTC date
today = _time_provider.today()  # Returns pendulum.Date
```

### For Testing: Use FakeTimeProvider

```python
from src.shared.providers import FakeTimeProvider
import pendulum

# Create fake provider with fixed time
fake_time = FakeTimeProvider(pendulum.datetime(2026, 1, 15, 10, 0, 0, tz="UTC"))

# Advance time for testing
fake_time.advance(days=5)
```

### For Timezone Operations: Use TimezoneService

```python
from src.shared.services import TimezoneService

tz_service = TimezoneService()
now_chile = tz_service.now_in_timezone("America/Santiago")
is_open = tz_service.is_business_hours("America/Santiago")
```

### Exception: SQLAlchemy Mixins

The only exception is `models/base/mixins.py` where SQLAlchemy defaults require direct `pendulum.now("UTC")` calls.

## Design Patterns

1. **Repository Pattern**: All database access through repository classes
2. **Dependency Injection**: Services receive dependencies via constructors
3. **Factory Pattern**: RepositoryFactory for creating repository instances
4. **Provider Pattern**: TimeProvider for centralized time management
5. **Base Service Pattern**: Common CRUD operations in BaseService

## Important Rules

1. **Poetry Only**: Always use Poetry for dependency management
2. **TimeProvider**: Use `TimeProvider` for all time operations - **NEVER** `datetime.now()` or `date.today()`
3. **Type Hints**: All functions must have complete type hints
4. **Modern Python**: Use `list`, `dict`, `X | None` instead of `List`, `Dict`, `Optional[X]`
5. **Testing**: Write tests for business logic and data access layers

## Reference Documentation

| Document | Purpose |
|----------|---------|
| `docs/PYTHON_BEST_PRACTICES.md` | Coding standards and patterns |
| `docs/agents/pendulum_rules.md` | Pendulum/time handling rules |
| `docs/agents/alembic_rules.md` | Database migration rules |
| `src/shared/providers/time_provider.py` | Time management implementation |
| `src/shared/services/timezone_service.py` | Timezone operations |
