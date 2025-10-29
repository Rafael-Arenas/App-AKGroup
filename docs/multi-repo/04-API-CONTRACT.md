# Gestión del Contrato API (OpenAPI)

## OpenAPI como Fuente de Verdad

El **contrato API** define la interfaz entre backend y frontend. Usamos OpenAPI 3.0+ como especificación estándar.

### Generación Automática (Backend → Frontend)

```python
# Backend genera OpenAPI automáticamente desde código
from fastapi import FastAPI
from pydantic import BaseModel

class Company(BaseModel):
    id: int
    name: str
    rut: str

app = FastAPI()

@app.get("/companies", response_model=List[Company])
def list_companies():
    """FastAPI genera automáticamente OpenAPI desde este código"""
    pass

# Disponible en:
# - /docs (Swagger UI)
# - /redoc (ReDoc)
# - /openapi.json (schema JSON)
```

### Script de Exportación

```python
# scripts/export_openapi.py
import json
from main import app

schema = app.openapi()
with open("openapi.json", "w") as f:
    json.dump(schema, f, indent=2)
```

### Generación de Tipos TypeScript

```bash
# Frontend genera tipos desde OpenAPI
npm run sync-api  # Ejecuta:
# 1. curl http://localhost:8000/openapi.json > api-schema/openapi.json
# 2. npx openapi-typescript api-schema/openapi.json --output src/types/api.ts
```

### Ejemplo de Tipos Generados

```typescript
// src/types/api.ts (auto-generado)
export interface paths {
  "/api/v1/companies": {
    get: {
      responses: {
        200: {
          content: {
            "application/json": components["schemas"]["Company"][];
          };
        };
      };
    };
    post: {
      requestBody: {
        content: {
          "application/json": components["schemas"]["CompanyCreate"];
        };
      };
      responses: {
        201: {
          content: {
            "application/json": components["schemas"]["Company"];
          };
        };
      };
    };
  };
}

export interface components {
  schemas: {
    Company: {
      id: number;
      name: string;
      rut: string;
      email?: string | null;
      created_at: string;
      updated_at: string;
    };
    CompanyCreate: {
      name: string;
      rut: string;
      email?: string | null;
    };
  };
}
```

## Versionado de API

### Estrategia de Versionado

```python
# Backend: Múltiples versiones
app = FastAPI()

# V1
app.include_router(v1.router, prefix="/api/v1", tags=["v1"])

# V2 (con breaking changes)
app.include_router(v2.router, prefix="/api/v2", tags=["v2"])
```

```typescript
// Frontend: Configurar versión
const API_VERSION = import.meta.env.VITE_API_VERSION || 'v1';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/${API_VERSION}`,
});
```

### Deprecación de Endpoints

```python
@router.get("/old-endpoint", deprecated=True)
def old_endpoint(response: Response):
    """DEPRECATED: Usar /new-endpoint"""
    response.headers["X-API-Warn"] = "Deprecated"
    response.headers["Sunset"] = "2024-12-31"
    return {"message": "old"}
```

## Schema Validation

### Backend (Pydantic)

```python
from pydantic import BaseModel, EmailStr, Field

class CompanyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    rut: str = Field(..., pattern=r'^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$')
    email: EmailStr | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Empresa ABC",
                "rut": "12.345.678-9",
                "email": "info@empresa.com"
            }
        }
```

### Frontend (Zod - opcional)

```typescript
import { z } from 'zod';

const CompanyCreateSchema = z.object({
  name: z.string().min(1).max(255),
  rut: z.string().regex(/^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$/),
  email: z.string().email().nullable().optional(),
});

type CompanyCreate = z.infer<typeof CompanyCreateSchema>;
```

---

**Siguiente:** [05-DEPLOYMENT.md](./05-DEPLOYMENT.md)
