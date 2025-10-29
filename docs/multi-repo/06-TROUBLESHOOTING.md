# Solución de Problemas Multi-Repo

## Problemas Comunes

### 1. CORS Errors

**Síntoma:**
```
Access to fetch at 'http://localhost:8000/api/v1/companies'
from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Solución:**

```python
# Backend: Verificar CORS settings
# src/config/settings.py
cors_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
]
```

```python
# main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. Type Mismatch (Frontend)

**Síntoma:**
```typescript
// Error: Property 'email' does not exist on type 'Company'
company.email  // ❌
```

**Solución:**

```bash
# Sincronizar API schema
cd frontend
npm run sync-api

# Verificar que openapi.json está actualizado
cat api-schema/openapi.json | grep email
```

### 3. Version Incompatibility

**Síntoma:**
```
Backend: v1.3.0 (nueva estructura de response)
Frontend: v2.0.0 (espera estructura antigua)
→ Runtime errors
```

**Solución:**

```bash
# Verificar versiones
curl http://localhost:8000/health
# {"version": "1.3.0"}

# Frontend debe actualizar
cd frontend
npm run sync-api
# Actualizar código para nueva estructura
```

### 4. Database Migration Issues

**Síntoma:**
```
sqlalchemy.exc.OperationalError: no such table: companies
```

**Solución:**

```bash
cd backend

# Ver estado de migraciones
poetry run alembic current

# Aplicar migraciones pendientes
poetry run alembic upgrade head

# Si hay conflictos
poetry run alembic heads  # Ver heads
poetry run alembic merge  # Mergear branches
```

### 5. Docker Networking

**Síntoma:**
```
Frontend cannot connect to backend
curl: (7) Failed to connect to backend port 8000: Connection refused
```

**Solución:**

```yaml
# docker-compose.yml
services:
  frontend:
    environment:
      # ❌ NO usar localhost dentro de Docker
      - VITE_API_BASE_URL=http://localhost:8000

      # ✅ Usar nombre del servicio
      - VITE_API_BASE_URL=http://backend:8000

networks:
  akgroup-net:
    driver: bridge
```

## Debugging Cross-Service

### Backend Debugging

```python
# Agregar logs detallados
from src.utils.logger import logger

@router.post("/companies")
def create_company(data: CompanyCreate):
    logger.debug(f"Creating company with data: {data.model_dump()}")

    try:
        company = service.create(data)
        logger.success(f"Company created: {company.id}")
        return company
    except Exception as e:
        logger.exception(f"Error creating company: {e}")
        raise
```

### Frontend Debugging

```typescript
// src/services/api.ts
api.interceptors.request.use((config) => {
  console.log('🔵 Request:', config.method?.toUpperCase(), config.url, config.data);
  return config;
});

api.interceptors.response.use(
  (response) => {
    console.log('🟢 Response:', response.status, response.data);
    return response;
  },
  (error) => {
    console.error('🔴 Error:', error.response?.status, error.response?.data);
    return Promise.reject(error);
  }
);
```

### Network Debugging

```bash
# Ver requests/responses
# Usar Chrome DevTools → Network tab

# O con curl
curl -v http://localhost:8000/api/v1/companies

# Ver headers
curl -I http://localhost:8000/api/v1/companies
```

## FAQ

### ¿Cómo manejar cambios en ambos repos simultáneamente?

Crear branches con el mismo nombre en ambos:

```bash
# Backend
cd backend
git checkout -b feature/nueva-funcionalidad

# Frontend
cd frontend
git checkout -b feature/nueva-funcionalidad

# PRs vinculados en descripción
```

### ¿Qué hacer si backend y frontend están desincronizados?

```bash
# 1. Verificar versiones
curl http://localhost:8000/health
# {"version": "1.2.3"}

# 2. Frontend sincronizar
cd frontend
npm run sync-api

# 3. Si hay breaking changes, actualizar código frontend
```

### ¿Cómo testear cambios localmente antes de mergear?

```bash
# Backend en una rama
cd backend
git checkout feature/nueva-funcionalidad
poetry run python main.py

# Frontend apuntando a backend local
cd frontend
# .env.development
VITE_API_BASE_URL=http://localhost:8000

npm run dev
```

---

**Siguiente:** [07-BEST-PRACTICES.md](./07-BEST-PRACTICES.md)
