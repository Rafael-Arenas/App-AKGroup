# Flujos de Trabajo Multi-Repo

## Tabla de Contenidos

- [Desarrollo Día a Día](#desarrollo-día-a-día)
- [Sincronización de Cambios en API](#sincronización-de-cambios-en-api)
- [Testing](#testing)
- [Manejo de Breaking Changes](#manejo-de-breaking-changes)
- [Proceso de Release](#proceso-de-release)
- [Hotfixes](#hotfixes)

---

## Desarrollo Día a Día

### Setup Matutino

```bash
# 1. Actualizar todos los repos
cd ~/Projects/akgroup-workspace

# Backend
cd akgroup-backend
git pull origin main
poetry install  # Si hay nuevas dependencias

# Frontend
cd ../akgroup-frontend
git pull origin main
npm install  # Si hay nuevas dependencias

# 2. Iniciar servicios
# Opción A: Docker
cd ../akgroup-infra
docker-compose up

# Opción B: Manual (dos terminales)
# Terminal 1: Backend
cd akgroup-backend && poetry run python main.py

# Terminal 2: Frontend
cd akgroup-frontend && npm run dev
```

### Crear Nueva Feature

#### Escenario 1: Solo Frontend (sin cambios en API)

```bash
cd akgroup-frontend

# 1. Crear branch
git checkout -b feature/ui-mejoras-dashboard

# 2. Desarrollar
# ... hacer cambios en src/pages/Dashboard.tsx

# 3. Commit
git add .
git commit -m "feat: mejoras visuales en dashboard"

# 4. Push y PR
git push origin feature/ui-mejoras-dashboard
# Crear PR en GitHub
```

#### Escenario 2: Solo Backend (sin breaking changes)

```bash
cd akgroup-backend

# 1. Crear branch
git checkout -b feature/agregar-filtros-empresas

# 2. Desarrollar
# ... agregar query params en src/api/v1/companies.py

# 3. Exportar OpenAPI actualizado
poetry run python scripts/export_openapi.py

# 4. Commit
git add .
git commit -m "feat: agregar filtros de búsqueda en empresas"

# 5. Push y PR
git push origin feature/agregar-filtros-empresas

# 6. Después del merge, notificar frontend
# (GitHub Action automática notifica al frontend)
```

#### Escenario 3: Full-Stack (Backend + Frontend)

Este es el flujo más común cuando agregas nueva funcionalidad:

```bash
# BACKEND PRIMERO
cd akgroup-backend

# 1. Crear branch backend
git checkout -b feature/gestion-proveedores

# 2. Crear modelos, schemas, endpoints
# src/models/core/suppliers.py
# src/schemas/core/supplier.py
# src/api/v1/suppliers.py

# 3. Tests
poetry run pytest tests/test_suppliers.py

# 4. Exportar OpenAPI
poetry run python scripts/export_openapi.py

# 5. Commit backend
git add .
git commit -m "feat(backend): agregar módulo de proveedores"
git push origin feature/gestion-proveedores

# 6. Crear PR backend
# Esperar review y merge

# FRONTEND DESPUÉS
cd ../akgroup-frontend

# 7. Crear branch frontend
git checkout -b feature/gestion-proveedores

# 8. Sincronizar API schema
npm run sync-api

# 9. Desarrollar frontend
# src/services/suppliers.ts (generado automáticamente o manual)
# src/pages/Suppliers/
# src/components/suppliers/

# 10. Commit frontend
git add .
git commit -m "feat(frontend): agregar UI de proveedores"
git push origin feature/gestion-proveedores

# 11. Crear PR frontend
```

**Timeline típica:**
```
Día 1: Backend development + tests
Día 2: Backend PR review + merge
Día 3: Frontend development (con API ya en main)
Día 4: Frontend PR review + merge
```

---

## Sincronización de Cambios en API

### Flujo Automático (Recomendado)

```
┌──────────────┐                    ┌──────────────┐
│   Backend    │                    │   Frontend   │
│              │                    │              │
│ 1. Merge PR  │                    │              │
│     ↓        │                    │              │
│ 2. GitHub    │                    │              │
│    Action    │                    │              │
│     ↓        │                    │              │
│ 3. Export    │                    │              │
│    OpenAPI   │                    │              │
│     ↓        │                    │              │
│ 4. Trigger   │─── Webhook ───────▶│ 5. GitHub    │
│    Frontend  │                    │    Action    │
│              │                    │     ↓        │
│              │                    │ 6. Download  │
│              │                    │    OpenAPI   │
│              │                    │     ↓        │
│              │                    │ 7. Generate  │
│              │                    │    Types     │
│              │                    │     ↓        │
│              │                    │ 8. Create PR │
└──────────────┘                    └──────────────┘
```

### Flujo Manual

```bash
# 1. Backend hace cambios y mergea a main
cd akgroup-backend
# ... cambios mergeados

# 2. Frontend developer sincroniza manualmente
cd akgroup-frontend

# Crear branch para actualización
git checkout -b chore/update-api-schema

# Descargar nuevo schema
npm run sync-api

# O manualmente:
curl http://localhost:8000/openapi.json > api-schema/openapi.json
npm run generate-types

# Verificar cambios
git diff src/types/api.ts

# Commit
git add api-schema/openapi.json src/types/api.ts
git commit -m "chore: update API schema to match backend v1.2.3"

# Push y PR
git push origin chore/update-api-schema
```

### Verificar Compatibilidad

```bash
# Después de sincronizar types, ejecutar tests
npm run test

# Si hay errores de tipos:
# - Actualizar código frontend para usar nuevos tipos
# - O reportar breaking change al backend team
```

---

## Testing

### Tests de Backend

```bash
cd akgroup-backend

# Ejecutar todos los tests
poetry run pytest

# Con cobertura
poetry run pytest --cov=src --cov-report=html

# Solo un módulo
poetry run pytest tests/test_companies.py

# Tests de integración (con DB)
poetry run pytest tests/integration/

# Type checking
poetry run mypy .

# Linting
poetry run ruff check .
poetry run black --check .
```

### Tests de Frontend

```bash
cd akgroup-frontend

# Unit tests
npm run test

# Con cobertura
npm run test:coverage

# Tests de componente específico
npm run test src/components/companies/CompanyList.test.tsx

# Type checking
npx tsc --noEmit

# Linting
npm run lint
```

### Tests de Integración E2E

Requiere ambos servicios corriendo:

```bash
# 1. Iniciar servicios
cd akgroup-infra
docker-compose up -d

# 2. Ejecutar tests E2E (con Playwright o Cypress)
cd akgroup-frontend
npm run test:e2e

# O:
npx playwright test
```

#### Ejemplo: `tests/e2e/companies.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test.describe('Companies Module', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000/companies');
  });

  test('should list companies', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Empresas');
    await expect(page.locator('.company-card')).toHaveCount(10);
  });

  test('should create new company', async ({ page }) => {
    await page.click('button:text("Nueva Empresa")');

    await page.fill('input[name="name"]', 'Test Company');
    await page.fill('input[name="rut"]', '12.345.678-9');
    await page.fill('input[name="email"]', 'test@company.com');

    await page.click('button:text("Guardar")');

    await expect(page.locator('.success-message')).toBeVisible();
    await expect(page.locator('.company-card')).toContainText('Test Company');
  });
});
```

---

## Manejo de Breaking Changes

### Definición

Un **breaking change** es cualquier cambio en la API que rompe compatibilidad con clientes existentes:

- Eliminar endpoint
- Cambiar estructura de response
- Cambiar tipo de campo
- Hacer obligatorio un campo opcional
- Cambiar validaciones

### Estrategia 1: Versionado de API

```python
# Backend: Mantener dos versiones simultáneamente
# src/api/v1/companies.py (versión antigua)
@router.get("/companies")
def list_companies_v1():
    # Implementación antigua
    pass

# src/api/v2/companies.py (versión nueva con breaking change)
@router.get("/companies")
def list_companies_v2():
    # Nueva implementación
    pass
```

```typescript
// Frontend: Usar versión específica
const API_VERSION = 'v1';  // o 'v2'

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/${API_VERSION}`,
});
```

### Estrategia 2: Feature Flags

```python
# Backend: Feature flag para nuevos comportamientos
from src.config.settings import settings

@router.get("/companies")
def list_companies():
    if settings.use_new_company_format:
        return new_implementation()
    else:
        return old_implementation()
```

### Estrategia 3: Proceso de Migración

```
Semana 1:
  - Backend: Implementar v2 endpoint
  - Backend: Deprecar v1 (agregar header de deprecación)
  - Docs: Documentar migración

Semana 2-3:
  - Frontend: Migrar a v2 en branch
  - Tests: Verificar todo funciona

Semana 4:
  - Deploy frontend con v2
  - Monitorear errores

Semana 5+:
  - Backend: Eliminar v1 endpoint
```

### Ejemplo de Deprecación

```python
# Backend
from fastapi import Header

@router.get("/companies", deprecated=True)
def list_companies_v1(
    response: Response
):
    """
    **DEPRECATED**: Este endpoint será removido en v2.0.0.
    Usar /api/v2/companies en su lugar.
    """
    response.headers["X-API-Warn"] = "Deprecated. Use /api/v2/companies"
    response.headers["Sunset"] = "2024-12-31"  # RFC 8594

    return old_implementation()
```

```typescript
// Frontend: Detectar deprecación
api.interceptors.response.use((response) => {
  if (response.headers['x-api-warn']) {
    console.warn('⚠️ API Deprecated:', response.headers['x-api-warn']);
  }
  return response;
});
```

---

## Proceso de Release

### Semantic Versioning

Ambos repos usan semver independientemente:

```
v1.2.3
│ │ └─ PATCH: Bug fixes, no breaking changes
│ └─── MINOR: New features, backwards compatible
└───── MAJOR: Breaking changes
```

### Release Backend

```bash
cd akgroup-backend

# 1. Crear release branch
git checkout -b release/v1.3.0

# 2. Actualizar versión
# pyproject.toml
[tool.poetry]
version = "1.3.0"

# 3. Actualizar CHANGELOG
# CHANGELOG.md
## [1.3.0] - 2024-01-15
### Added
- Módulo de proveedores
- Filtros avanzados en empresas

### Fixed
- Bug en cálculo de totales

# 4. Commit
git add .
git commit -m "chore: release v1.3.0"

# 5. Merge a main
git checkout main
git merge release/v1.3.0

# 6. Tag
git tag -a v1.3.0 -m "Release v1.3.0"
git push origin main --tags

# 7. GitHub Actions automático hace:
# - Tests
# - Build Docker image
# - Deploy a staging
# - (Manual) Deploy a production
```

### Release Frontend

```bash
cd akgroup-frontend

# Similar al backend
git checkout -b release/v2.1.0

# package.json
{
  "version": "2.1.0"
}

# CHANGELOG.md
## [2.1.0] - 2024-01-15
### Added
- UI de proveedores
- Mejoras en dashboard

git add .
git commit -m "chore: release v2.1.0"

git checkout main
git merge release/v2.1.0
git tag -a v2.1.0 -m "Release v2.1.0"
git push origin main --tags
```

### Coordinar Releases

Para features que requieren ambos servicios:

```
Backend v1.3.0 + Frontend v2.1.0
│
├─ Backend v1.3.0 release
│  ├─ Tag: v1.3.0
│  ├─ Deploy to staging
│  └─ Verif

icar API funciona
│
└─ Frontend v2.1.0 release
   ├─ Tag: v2.1.0
   ├─ Build con VITE_API_BASE_URL=staging
   ├─ Deploy to staging
   ├─ Tests E2E en staging
   └─ Deploy to production (ambos)
```

---

## Hotfixes

### Proceso de Hotfix

```bash
# 1. Identificar bug en producción
# Production: v1.2.3 tiene bug crítico

cd akgroup-backend

# 2. Crear hotfix branch desde tag de producción
git checkout v1.2.3
git checkout -b hotfix/v1.2.4

# 3. Fix rápido
# ... fix el bug

# 4. Tests
poetry run pytest tests/test_bug.py

# 5. Commit
git add .
git commit -m "fix: corregir cálculo de precios (closes #123)"

# 6. Merge a main Y develop
git checkout main
git merge hotfix/v1.2.4

git checkout develop
git merge hotfix/v1.2.4

# 7. Tag
git tag -a v1.2.4 -m "Hotfix v1.2.4"
git push origin main develop --tags

# 8. Deploy urgente
# CI/CD automático o manual
```

### Hotfix que Afecta Frontend

```bash
# Backend hotfix deployed: v1.2.4

cd akgroup-frontend

# 1. Verificar si frontend necesita cambios
npm run sync-api

# Si hay cambios en tipos:
git checkout -b hotfix/v2.0.1
# ... actualizar código frontend
git commit -m "fix: ajustar a backend v1.2.4"

# 2. Release frontend
git tag -a v2.0.1 -m "Hotfix v2.0.1"
git push origin main --tags
```

---

**Siguiente:** [04-API-CONTRACT.md - Gestión del Contrato API](./04-API-CONTRACT.md)
