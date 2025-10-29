# Arquitectura Multi-Repo con API Contract

## Tabla de Contenidos

- [Introducción](#introducción)
- [Conceptos Clave](#conceptos-clave)
- [Arquitectura General](#arquitectura-general)
- [Componentes del Sistema](#componentes-del-sistema)
- [Comunicación entre Servicios](#comunicación-entre-servicios)
- [Ventajas y Desventajas](#ventajas-y-desventajas)
- [Cuándo Usar Esta Arquitectura](#cuándo-usar-esta-arquitectura)
- [Comparación con Otras Arquitecturas](#comparación-con-otras-arquitecturas)

---

## Introducción

La **arquitectura Multi-Repo con API Contract** es un patrón de organización de código donde el backend y el frontend se mantienen en repositorios completamente separados, pero se comunican a través de un **contrato de API** bien definido (OpenAPI/Swagger) que actúa como única fuente de verdad.

### ¿Por qué Multi-Repo?

En lugar de tener todo el código en un solo repositorio (monorepo) o embeber un servicio dentro de otro, esta arquitectura separa completamente:

- **Backend** (FastAPI/Python) → Repositorio independiente
- **Frontend** (React/Vue/Angular) → Repositorio independiente
- **API Contract** (OpenAPI Schema) → Fuente de verdad compartida

Esta separación permite:
- Desarrollo independiente de cada servicio
- Equipos especializados trabajando sin interferencias
- Deploys independientes
- Escalabilidad para agregar más clientes (mobile, admin, etc.)

---

## Conceptos Clave

### 1. **API Contract (Contrato de API)**

El **contrato de API** es una especificación formal de cómo el backend y frontend se comunican. Se define usando:

- **OpenAPI 3.0+** (anteriormente Swagger)
- **JSON Schema** para validación de datos
- **Documentación interactiva** auto-generada

**Analogía**: Es como un contrato legal entre dos empresas. Define:
- Qué endpoints existen
- Qué datos aceptan (request)
- Qué datos retornan (response)
- Qué errores pueden ocurrir

### 2. **Repositorios Independientes**

Cada servicio vive en su propio repositorio Git:

```
GitHub Organization: AKGroup
│
├── akgroup-backend/         # Repo 1: FastAPI Backend
├── akgroup-frontend/        # Repo 2: React/Vue Frontend
└── akgroup-api-contract/    # Repo 3: OpenAPI Schema (opcional)
```

**Beneficios**:
- Historiales Git separados
- Permisos de acceso granulares
- CI/CD independiente
- Versionado independiente

### 3. **Code Generation (Generación de Código)**

A partir del **contrato OpenAPI**, se generan automáticamente:

- **Backend**: Modelos Pydantic, validadores, documentación
- **Frontend**: Tipos TypeScript, cliente API, hooks

**Flujo**:
```
OpenAPI Schema → Code Generator → TypeScript Types
                              → Pydantic Models
                              → API Client
```

### 4. **Semantic Versioning**

Cada repositorio sigue versionado semántico:

```
v1.2.3
│ │ └─ PATCH: Bug fixes (compatible)
│ └─── MINOR: Nuevas features (compatible)
└───── MAJOR: Breaking changes (incompatible)
```

---

## Arquitectura General

### Diagrama de Alto Nivel

```
┌─────────────────────────────────────────────────────────────────┐
│                         ORGANIZACIÓN AKGROUP                     │
└─────────────────────────────────────────────────────────────────┘
                                  │
                ┌─────────────────┼─────────────────┐
                │                 │                 │
                ▼                 ▼                 ▼
    ┌───────────────────┐ ┌──────────────┐ ┌──────────────────┐
    │  akgroup-backend  │ │  akgroup-    │ │  akgroup-        │
    │  (FastAPI/Python) │ │  frontend    │ │  api-contract    │
    │                   │ │ (React/Vue)  │ │  (OpenAPI)       │
    │  - API REST       │ │ - UI/UX      │ │  - Schemas       │
    │  - Business Logic │ │ - Components │ │  - Validations   │
    │  - Database       │ │ - State Mgmt │ │  - Types         │
    └───────────────────┘ └──────────────┘ └──────────────────┘
             │                    │                    │
             │                    │                    │
             └────────────────────┼────────────────────┘
                                  │
                                  ▼
                        ┌──────────────────┐
                        │   COMUNICACIÓN   │
                        │                  │
                        │  • HTTP/REST     │
                        │  • JSON          │
                        │  • OpenAPI 3.0   │
                        │  • CORS          │
                        └──────────────────┘
```

### Flujo de Datos

```
┌──────────────┐                    ┌──────────────┐
│   FRONTEND   │                    │   BACKEND    │
│              │                    │              │
│  1. Usuario  │                    │              │
│     Acción   │                    │              │
│              │                    │              │
│  2. API Call │──── HTTP/REST ────▶│ 3. Procesar  │
│     (JSON)   │    (OpenAPI)       │    Request   │
│              │                    │              │
│              │                    │ 4. Business  │
│              │                    │    Logic     │
│              │                    │              │
│              │                    │ 5. Database  │
│              │                    │    Query     │
│              │◀──── Response ─────│              │
│  6. Renderizar│    (JSON)         │ 6. Response  │
│     UI       │                    │    (JSON)    │
└──────────────┘                    └──────────────┘
```

---

## Componentes del Sistema

### Backend Repository (`akgroup-backend`)

**Responsabilidades**:
- API REST endpoints
- Lógica de negocio
- Acceso a base de datos
- Autenticación y autorización
- Validación de datos
- Generación del OpenAPI schema

**Stack Tecnológico**:
- **Python 3.13+**
- **FastAPI** - Framework web
- **SQLAlchemy** - ORM
- **Alembic** - Migraciones
- **Pydantic** - Validación de datos
- **Pytest** - Testing

**Estructura**:
```
akgroup-backend/
├── src/
│   ├── api/
│   │   └── v1/          # Endpoints versión 1
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   ├── repositories/    # Data access
│   └── config/          # Configuración
├── tests/
├── migrations/          # Alembic migrations
├── main.py              # Entry point
├── pyproject.toml       # Poetry dependencies
└── openapi.json         # OpenAPI schema (generado)
```

**Endpoints Principales**:
```
GET    /api/v1/companies           # Listar empresas
POST   /api/v1/companies           # Crear empresa
GET    /api/v1/companies/{id}      # Obtener empresa
PUT    /api/v1/companies/{id}      # Actualizar empresa
DELETE /api/v1/companies/{id}      # Eliminar empresa

GET    /api/v1/products            # Listar productos
POST   /api/v1/products            # Crear producto
...

GET    /docs                       # Documentación Swagger
GET    /redoc                      # Documentación ReDoc
GET    /openapi.json               # OpenAPI schema
GET    /health                     # Health check
```

### Frontend Repository (`akgroup-frontend`)

**Responsabilidades**:
- Interfaz de usuario
- Interacción con usuario
- Llamadas a API backend
- Estado de la aplicación
- Validación del lado del cliente
- Enrutamiento

**Stack Tecnológico**:
- **TypeScript** - Type safety
- **React 18+** (o Vue 3, Angular)
- **Vite** - Build tool
- **Axios** - HTTP client
- **React Router** - Routing
- **Zustand/Redux** - State management
- **TanStack Query** - Data fetching
- **Vitest** - Testing

**Estructura**:
```
akgroup-frontend/
├── src/
│   ├── components/        # Componentes reutilizables
│   │   ├── common/        # Botones, Inputs, etc.
│   │   ├── companies/     # Componentes de empresas
│   │   └── products/      # Componentes de productos
│   ├── pages/             # Páginas/Vistas
│   │   ├── Dashboard.tsx
│   │   ├── Companies/
│   │   └── Products/
│   ├── services/          # API clients
│   │   ├── api.ts         # Axios instance
│   │   ├── companies.ts   # Companies API
│   │   └── products.ts    # Products API
│   ├── hooks/             # Custom hooks
│   ├── store/             # State management
│   ├── types/             # TypeScript types
│   │   ├── api.ts         # Auto-generados desde OpenAPI
│   │   └── models.ts
│   ├── utils/
│   └── App.tsx
├── public/
├── tests/
├── package.json
├── tsconfig.json
├── vite.config.ts
└── api-schema/            # OpenAPI schema del backend
    └── openapi.json
```

### API Contract Repository (`akgroup-api-contract`) [Opcional]

**Responsabilidades**:
- Definir el contrato OpenAPI
- Versionado de API
- Generación de código compartido
- Documentación de la API

**Estructura**:
```
akgroup-api-contract/
├── schemas/
│   ├── v1/
│   │   └── openapi.yaml       # Definición OpenAPI v1
│   └── v2/
│       └── openapi.yaml       # Definición OpenAPI v2
├── generated/
│   ├── typescript/            # Tipos TS generados
│   └── python/                # Modelos Pydantic generados
├── scripts/
│   ├── generate-types.sh      # Generar tipos TS
│   └── generate-models.sh     # Generar modelos Python
└── README.md
```

**Nota**: Este repositorio es **opcional**. Muchas organizaciones prefieren que el backend sea la fuente de verdad y genere el OpenAPI automáticamente desde el código.

---

## Comunicación entre Servicios

### 1. Backend Genera OpenAPI

El backend genera automáticamente el esquema OpenAPI a partir de sus modelos Pydantic:

```python
# backend/main.py
from fastapi import FastAPI

app = FastAPI(
    title="AK Group API",
    version="1.0.0",
    description="Sistema de gestión empresarial"
)

# FastAPI genera automáticamente:
# - /docs (Swagger UI)
# - /redoc (ReDoc)
# - /openapi.json (OpenAPI schema)

@app.get("/api/v1/companies", response_model=List[CompanySchema])
def list_companies():
    """
    Lista todas las empresas.

    Este endpoint automáticamente genera documentación OpenAPI
    incluyendo el schema del CompanySchema.
    """
    ...
```

### 2. Frontend Consume OpenAPI

El frontend descarga el esquema OpenAPI y genera tipos TypeScript:

```bash
# frontend/scripts/sync-api-schema.sh

# 1. Descargar OpenAPI schema desde backend
curl http://localhost:8000/openapi.json > api-schema/openapi.json

# 2. Generar tipos TypeScript
npx openapi-typescript api-schema/openapi.json --output src/types/api.ts

# 3. Generar cliente API (opcional)
npx openapi-typescript-codegen \
  --input api-schema/openapi.json \
  --output src/services/generated \
  --client axios
```

### 3. Ejemplo de Uso en Frontend

```typescript
// src/types/api.ts (auto-generado)
export interface Company {
  id: number;
  name: string;
  rut: string;
  email: string | null;
  created_at: string;
  updated_at: string;
}

export interface CompanyCreate {
  name: string;
  rut: string;
  email?: string | null;
}

// src/services/companies.ts
import api from './api';
import type { Company, CompanyCreate } from '../types/api';

export const companiesService = {
  async getAll(): Promise<Company[]> {
    const response = await api.get<Company[]>('/companies');
    return response.data;
  },

  async create(data: CompanyCreate): Promise<Company> {
    const response = await api.post<Company>('/companies', data);
    return response.data;
  },

  async getById(id: number): Promise<Company> {
    const response = await api.get<Company>(`/companies/${id}`);
    return response.data;
  },
};

// src/pages/Companies/CompanyList.tsx
import { useQuery } from '@tanstack/react-query';
import { companiesService } from '../../services/companies';

export function CompanyList() {
  const { data: companies, isLoading } = useQuery({
    queryKey: ['companies'],
    queryFn: companiesService.getAll,
  });

  if (isLoading) return <div>Cargando...</div>;

  return (
    <div>
      {companies?.map((company) => (
        <div key={company.id}>
          {company.name} - {company.rut}
        </div>
      ))}
    </div>
  );
}
```

### 4. Sincronización Automática con GitHub Actions

Cuando el backend cambia la API, se notifica automáticamente al frontend:

```yaml
# backend/.github/workflows/notify-frontend.yml
name: Notify Frontend on API Changes

on:
  push:
    branches: [main]
    paths:
      - 'src/api/**'
      - 'src/schemas/**'

jobs:
  notify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Generate OpenAPI
        run: |
          poetry install
          poetry run python -c "from main import app; import json; print(json.dumps(app.openapi()))" > openapi.json

      - name: Trigger Frontend Update
        uses: peter-evans/repository-dispatch@v2
        with:
          token: ${{ secrets.REPO_ACCESS_TOKEN }}
          repository: akgroup/akgroup-frontend
          event-type: api-updated
          client-payload: '{"version": "${{ github.sha }}"}'
```

```yaml
# frontend/.github/workflows/update-api-schema.yml
name: Update API Schema

on:
  repository_dispatch:
    types: [api-updated]

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Download OpenAPI schema
        run: curl https://api.akgroup.com/openapi.json > api-schema/openapi.json

      - name: Regenerate TypeScript types
        run: npm run generate-api-types

      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v5
        with:
          title: "chore: update API types from backend"
          body: "Auto-generated PR to sync API schema"
          branch: api-schema-update
```

---

## Ventajas y Desventajas

### ✅ Ventajas

#### 1. **Independencia Total**
- Backend y frontend se desarrollan de forma completamente independiente
- No hay acoplamiento en el código
- Cada equipo puede elegir sus propias herramientas y prácticas

#### 2. **Escalabilidad**
- Fácil agregar más clientes (mobile app, admin panel, API pública)
- Backend puede servir a múltiples frontends
- Cada servicio escala independientemente

#### 3. **Deploys Independientes**
- Actualizar frontend sin tocar backend
- Actualizar backend sin afectar frontend (si no hay breaking changes)
- Rollback independiente de cada servicio

#### 4. **Permisos Granulares**
- Control de acceso por repositorio
- Equipos especializados (backend team, frontend team)
- Facilita onboarding de desarrolladores especializados

#### 5. **CI/CD Simple**
- Pipelines independientes por servicio
- Tests más rápidos (solo del servicio modificado)
- Deploy más rápido

#### 6. **Claridad de Responsabilidades**
- Backend: API y lógica de negocio
- Frontend: UI/UX
- Contrato API: Interfaz entre ambos

#### 7. **Reutilización de Backend**
- El backend es un producto en sí mismo
- Puede ser usado por múltiples clientes
- Fácil crear API pública

#### 8. **Tecnologías Independientes**
- Backend puede usar Python/FastAPI
- Frontend puede cambiar de React a Vue sin afectar backend
- Actualizaciones de dependencias independientes

### ❌ Desventajas

#### 1. **Sincronización Manual**
- Cambios en API requieren coordinar dos repositorios
- Breaking changes son más complejos de gestionar
- Requiere buena comunicación entre equipos

#### 2. **Complejidad Inicial**
- Setup más complejo que monorepo
- Requiere configurar CI/CD en múltiples repos
- Más herramientas y automatizaciones necesarias

#### 3. **Testing de Integración Complejo**
- Tests E2E requieren ambos servicios corriendo
- Setup de entorno de testing más elaborado
- Más difícil debuggear problemas cross-service

#### 4. **Documentación Fragmentada**
- README en dos repositorios
- Documentación de arquitectura puede estar dispersa
- Requiere disciplina para mantener docs sincronizadas

#### 5. **Overhead para Equipos Pequeños**
- Si eres solo 1-3 personas, puede ser demasiado overhead
- Más contexto switching entre repos
- Más tiempo en coordinación

#### 6. **Versionado Complejo**
- Compatibilidad entre versiones de backend y frontend
- Gestión de breaking changes requiere estrategia
- Requiere semantic versioning estricto

#### 7. **Desarrollo Local Más Complejo**
- Requiere clonar múltiples repos
- Configurar múltiples servicios localmente
- Docker Compose o scripts para orquestar

---

## Cuándo Usar Esta Arquitectura

### ✅ USA Multi-Repo SI:

1. **Múltiples Clientes**
   - Planeas tener web app, mobile app, admin panel, etc.
   - Backend será consumido por varios frontends

2. **Equipos Separados**
   - Tienes equipos especializados (backend, frontend)
   - Más de 5-10 desarrolladores
   - Equipos en diferentes ubicaciones/zonas horarias

3. **Backend como Producto**
   - El backend es un API pública o producto en sí mismo
   - Otros desarrolladores/empresas consumirán tu API
   - Requieres documentación de API profesional

4. **Deploys Independientes**
   - Necesitas actualizar frontend sin tocar backend frecuentemente
   - Releases independientes por servicio
   - Diferentes ciclos de release

5. **Escalabilidad a Largo Plazo**
   - Proyecto a largo plazo (años)
   - Esperás crecimiento significativo
   - Planeas microservicios en el futuro

6. **Reutilización de Backend**
   - Backend será usado por múltiples proyectos
   - API será consumida por terceros
   - Integración con sistemas externos

### ❌ NO USES Multi-Repo SI:

1. **Equipo Pequeño**
   - Solo 1-3 desarrolladores full-stack
   - Todos trabajan en todo
   - No hay especialización backend/frontend

2. **Proyecto Simple/MVP**
   - Proyecto inicial o MVP
   - No planeas múltiples clientes
   - Tiempo al mercado es crítico

3. **Backend No Se Reutilizará**
   - Backend solo para este frontend
   - No hay planes de API pública
   - No habrá mobile app

4. **Cambios Frecuentes en API**
   - API aún no está estable
   - Muchos cambios en contratos
   - Iteración rápida requerida

5. **Recursos Limitados**
   - Poco tiempo para setup complejo
   - Sin experiencia en multi-repo
   - Sin CI/CD configurado

---

## Comparación con Otras Arquitecturas

### Multi-Repo vs Monorepo

| Aspecto | Multi-Repo | Monorepo |
|---------|-----------|----------|
| **Setup Inicial** | Complejo | Simple |
| **Desarrollo Local** | Múltiples repos | Un solo repo |
| **Sincronización** | Manual | Automática |
| **CI/CD** | Independiente | Compartido |
| **Deploys** | Independientes | Generalmente juntos |
| **Escalabilidad** | Muy escalable | Limitada |
| **Permisos** | Granular | Todo o nada |
| **Equipos Grandes** | Ideal | Puede ser caótico |
| **Equipos Pequeños** | Overhead | Perfecto |

### Multi-Repo vs Backend Embebido

| Aspecto | Multi-Repo | Backend Embebido |
|---------|-----------|------------------|
| **Independencia** | Total | Ninguna |
| **Reutilización Backend** | Fácil | Difícil |
| **Múltiples Clientes** | Ideal | No recomendado |
| **Simplicidad** | Complejo | Muy simple |
| **Permisos** | Granular | No granular |

---

## Arquitectura de Ejemplo: AK Group

### Repos en la Organización

```
github.com/akgroup/
│
├── akgroup-backend          # Backend FastAPI
│   ├── ⭐ 15 stars
│   ├── 🍴 3 forks
│   ├── main, develop, feature/* branches
│   └── v1.2.3 (última release)
│
├── akgroup-frontend         # Frontend React
│   ├── ⭐ 8 stars
│   ├── 🍴 2 forks
│   ├── main, develop, feature/* branches
│   └── v2.1.0 (última release)
│
├── akgroup-mobile           # Mobile App React Native (futuro)
│   └── v1.0.0
│
└── akgroup-infra            # Docker Compose, K8s configs
    └── v1.0.0
```

### Flujo de Comunicación

```
┌──────────────┐                      ┌──────────────┐
│   Frontend   │                      │   Backend    │
│  (v2.1.0)    │◀────HTTP/REST────────│  (v1.2.3)    │
│              │      /api/v1         │              │
└──────────────┘                      └──────────────┘
       │                                     │
       │                                     │
       │    ┌─────────────────────┐         │
       └───▶│   OpenAPI v1.2.3    │◀────────┘
            │                     │
            │  • Schemas          │
            │  • Validators       │
            │  • Documentation    │
            └─────────────────────┘
```

---

## Recursos Adicionales

### Documentos Relacionados

- [02-SETUP.md](./02-SETUP.md) - Guía de implementación paso a paso
- [03-WORKFLOW.md](./03-WORKFLOW.md) - Flujos de trabajo día a día
- [04-API-CONTRACT.md](./04-API-CONTRACT.md) - Gestión del contrato API
- [05-DEPLOYMENT.md](./05-DEPLOYMENT.md) - Estrategias de deployment
- [06-TROUBLESHOOTING.md](./06-TROUBLESHOOTING.md) - Solución de problemas
- [07-BEST-PRACTICES.md](./07-BEST-PRACTICES.md) - Mejores prácticas

### Referencias Externas

- [OpenAPI Specification](https://swagger.io/specification/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Microservices Patterns](https://microservices.io/patterns/index.html)
- [API Design Best Practices](https://github.com/microsoft/api-guidelines)

---

**Siguiente:** [02-SETUP.md - Setup e Implementación](./02-SETUP.md)
