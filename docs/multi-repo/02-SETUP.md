# Setup e Implementación Multi-Repo

## Tabla de Contenidos

- [Requisitos Previos](#requisitos-previos)
- [Setup Inicial](#setup-inicial)
- [Configuración del Backend](#configuración-del-backend)
- [Configuración del Frontend](#configuración-del-frontend)
- [Configuración del Contrato API](#configuración-del-contrato-api)
- [Docker y Docker Compose](#docker-y-docker-compose)
- [CI/CD con GitHub Actions](#cicd-con-github-actions)
- [Desarrollo Local](#desarrollo-local)
- [Verificación del Setup](#verificación-del-setup)

---

## Requisitos Previos

### Herramientas Necesarias

#### Backend
- **Python 3.13+**
- **Poetry 2.1.3+** - Gestor de dependencias
- **Git 2.30+**
- **MySQL/PostgreSQL** (producción) o **SQLite** (desarrollo)

#### Frontend
- **Node.js 20+** (LTS)
- **npm 10+** o **pnpm 8+**
- **Git 2.30+**

#### DevOps/Deployment
- **Docker 24+**
- **Docker Compose 2.20+**
- **Make** (opcional, para scripts)

#### Servicios Externos
- **GitHub** (o GitLab/Bitbucket) - Control de versiones
- **GitHub Actions** - CI/CD (o alternativas)

### Verificar Instalación

```bash
# Python
python --version  # Python 3.13.x

# Poetry
poetry --version  # Poetry 2.1.3+

# Node.js
node --version    # v20.x.x

# npm
npm --version     # 10.x.x

# Docker
docker --version          # Docker version 24.x.x
docker-compose --version  # Docker Compose version 2.x.x

# Git
git --version     # git version 2.x.x
```

---

## Setup Inicial

### Paso 1: Crear Organización en GitHub

1. Ve a GitHub → Settings → Organizations
2. Crea una nueva organización: `akgroup`
3. Configura permisos y equipos:
   - **Backend Team**: Acceso a `akgroup-backend`
   - **Frontend Team**: Acceso a `akgroup-frontend`
   - **DevOps Team**: Acceso a todos los repos

### Paso 2: Crear Repositorios

#### Backend Repository

```bash
# Crear repo en GitHub UI
# Nombre: akgroup-backend
# Descripción: Sistema de gestión empresarial - Backend API (FastAPI/Python)
# Privacidad: Private

# Clonar localmente
git clone git@github.com:akgroup/akgroup-backend.git
cd akgroup-backend
```

#### Frontend Repository

```bash
# Crear repo en GitHub UI
# Nombre: akgroup-frontend
# Descripción: Sistema de gestión empresarial - Frontend (React/TypeScript)
# Privacidad: Private

# Clonar localmente
git clone git@github.com:akgroup/akgroup-frontend.git
cd akgroup-frontend
```

#### Infrastructure Repository (opcional)

```bash
# Crear repo para Docker Compose, K8s, scripts compartidos
git clone git@github.com:akgroup/akgroup-infra.git
cd akgroup-infra
```

### Paso 3: Estructura de Carpetas Local

```bash
# Crear workspace local
mkdir ~/Projects/akgroup-workspace
cd ~/Projects/akgroup-workspace

# Clonar todos los repos
git clone git@github.com:akgroup/akgroup-backend.git
git clone git@github.com:akgroup/akgroup-frontend.git
git clone git@github.com:akgroup/akgroup-infra.git

# Estructura resultante:
# akgroup-workspace/
# ├── akgroup-backend/
# ├── akgroup-frontend/
# └── akgroup-infra/
```

---

## Configuración del Backend

### Paso 1: Mover Proyecto Existente

Si ya tienes el proyecto `App-AKGroup`, mueve su contenido al nuevo repo:

```bash
cd ~/Projects/App-AKGroup

# Copiar archivos al nuevo repo
cp -r src/ ~/Projects/akgroup-workspace/akgroup-backend/
cp -r tests/ ~/Projects/akgroup-workspace/akgroup-backend/
cp -r migrations/ ~/Projects/akgroup-workspace/akgroup-backend/
cp -r seeds/ ~/Projects/akgroup-workspace/akgroup-backend/
cp -r docs/ ~/Projects/akgroup-workspace/akgroup-backend/
cp main.py ~/Projects/akgroup-workspace/akgroup-backend/
cp pyproject.toml ~/Projects/akgroup-workspace/akgroup-backend/
cp poetry.lock ~/Projects/akgroup-workspace/akgroup-backend/
cp alembic.ini ~/Projects/akgroup-workspace/akgroup-backend/
cp .env.example ~/Projects/akgroup-workspace/akgroup-backend/
cp .gitignore ~/Projects/akgroup-workspace/akgroup-backend/
cp README.md ~/Projects/akgroup-workspace/akgroup-backend/
```

### Paso 2: Actualizar Configuración

#### `.env.example`

```env
# Entorno
ENVIRONMENT=development

# Base de datos
DATABASE_TYPE=sqlite
DATABASE_URL=sqlite:///./akgroup.db

# Para MySQL en producción:
# DATABASE_TYPE=mysql
# DATABASE_URL=mysql+pymysql://user:password@localhost:3306/akgroup_db

# API
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# CORS - IMPORTANTE: Agregar frontend URL
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# Logging
LOG_LEVEL=INFO

# JWT (cuando se implemente)
# JWT_SECRET_KEY=your-secret-key-here
# JWT_ALGORITHM=HS256
# JWT_EXPIRATION_MINUTES=30
```

#### `README.md` del Backend

```markdown
# AK Group Backend

Sistema de gestión empresarial - Backend API

## Stack

- **Python 3.13+**
- **FastAPI 0.115.0+**
- **SQLAlchemy 2.0.44+**
- **Alembic 1.17.0+**

## Setup

```bash
# Instalar dependencias
poetry install

# Configurar variables de entorno
cp .env.example .env

# Aplicar migraciones
poetry run alembic upgrade head

# Ejecutar servidor
poetry run python main.py
```

## Documentación

- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Testing

```bash
poetry run pytest
poetry run pytest --cov
```

## Deployment

Ver [deployment docs](docs/DEPLOYMENT.md)
```

### Paso 3: Script para Exportar OpenAPI

Crear script para generar el schema OpenAPI:

```python
# scripts/export_openapi.py
"""
Script para exportar el schema OpenAPI a un archivo JSON.

Uso:
    poetry run python scripts/export_openapi.py
"""
import json
from pathlib import Path

from main import app


def export_openapi_schema():
    """Exporta el schema OpenAPI a openapi.json"""
    schema = app.openapi()

    output_file = Path("openapi.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)

    print(f"✅ OpenAPI schema exportado a {output_file}")
    print(f"📊 Versión: {schema.get('info', {}).get('version')}")
    print(f"📝 Endpoints: {len(schema.get('paths', {}))}")


if __name__ == "__main__":
    export_openapi_schema()
```

```bash
# Hacer ejecutable
chmod +x scripts/export_openapi.py

# Ejecutar
poetry run python scripts/export_openapi.py
```

### Paso 4: Actualizar CORS para Frontend

```python
# src/config/settings.py (ya existente, verificar)
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ...

    # CORS settings - Actualizar para incluir frontend
    cors_origins: list[str] = [
        "http://localhost:3000",      # Vite dev server
        "http://localhost:5173",      # Vite alternate port
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # Producción
    # cors_origins: list[str] = ["https://app.akgroup.com"]

    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]

    # ...
```

### Paso 5: Commit y Push

```bash
cd ~/Projects/akgroup-workspace/akgroup-backend

git add .
git commit -m "feat: initial backend setup

- Migrado desde App-AKGroup
- Configurado CORS para frontend
- Agregado script de exportación OpenAPI
- Actualizado README
"

git push origin main
```

---

## Configuración del Frontend

### Paso 1: Crear Proyecto React con Vite

```bash
cd ~/Projects/akgroup-workspace/akgroup-frontend

# Crear proyecto React + TypeScript + Vite
npm create vite@latest . -- --template react-ts

# O con Vue:
# npm create vite@latest . -- --template vue-ts
```

### Paso 2: Instalar Dependencias

```bash
# Dependencias principales
npm install axios @tanstack/react-query react-router-dom zustand

# Dependencias de desarrollo
npm install -D @types/node

# Herramientas de generación de código
npm install -D openapi-typescript openapi-typescript-codegen

# Opcional: UI Library
npm install @mui/material @emotion/react @emotion/styled
# O: npm install antd
# O: npm install @headlessui/react @tailwindcss/forms
```

### Paso 3: Estructura de Carpetas

```bash
mkdir -p src/{components/{common,companies,products,layout},pages,services,hooks,store,types,utils,styles}
mkdir -p api-schema
```

Resultado:
```
akgroup-frontend/
├── api-schema/             # OpenAPI schema del backend
├── public/
├── src/
│   ├── components/
│   │   ├── common/         # Button, Input, Modal, etc.
│   │   ├── companies/      # CompanyList, CompanyForm, etc.
│   │   ├── products/       # ProductList, ProductForm, etc.
│   │   └── layout/         # Header, Sidebar, Footer
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── Companies/
│   │   ├── Products/
│   │   └── NotFound.tsx
│   ├── services/
│   │   ├── api.ts          # Axios instance
│   │   ├── companies.ts
│   │   └── products.ts
│   ├── hooks/
│   │   ├── useCompanies.ts
│   │   └── useProducts.ts
│   ├── store/              # Zustand stores
│   │   ├── authStore.ts
│   │   └── appStore.ts
│   ├── types/
│   │   ├── api.ts          # Auto-generado desde OpenAPI
│   │   └── models.ts
│   ├── utils/
│   │   ├── format.ts
│   │   └── validation.ts
│   ├── styles/
│   │   └── globals.css
│   ├── App.tsx
│   ├── main.tsx
│   └── vite-env.d.ts
├── .env.example
├── .env.development
├── .env.production
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

### Paso 4: Configurar Variables de Entorno

#### `.env.example`

```env
# Backend API URL
VITE_API_BASE_URL=http://localhost:8000

# Environment
VITE_ENV=development

# App Settings
VITE_APP_NAME=AK Group
VITE_APP_VERSION=1.0.0
```

#### `.env.development`

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_ENV=development
```

#### `.env.production`

```env
VITE_API_BASE_URL=https://api.akgroup.com
VITE_ENV=production
```

### Paso 5: Configurar Vite

#### `vite.config.ts`

```typescript
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');

  return {
    plugins: [react()],

    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
        '@components': path.resolve(__dirname, './src/components'),
        '@pages': path.resolve(__dirname, './src/pages'),
        '@services': path.resolve(__dirname, './src/services'),
        '@hooks': path.resolve(__dirname, './src/hooks'),
        '@store': path.resolve(__dirname, './src/store'),
        '@types': path.resolve(__dirname, './src/types'),
        '@utils': path.resolve(__dirname, './src/utils'),
      },
    },

    server: {
      port: 3000,
      open: true,
      proxy: {
        // Proxy para desarrollo local
        '/api': {
          target: env.VITE_API_BASE_URL || 'http://localhost:8000',
          changeOrigin: true,
        },
      },
    },

    build: {
      outDir: 'dist',
      sourcemap: mode === 'development',
    },
  };
});
```

#### `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,

    /* Bundler mode */
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",

    /* Linting */
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,

    /* Path aliases */
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@components/*": ["./src/components/*"],
      "@pages/*": ["./src/pages/*"],
      "@services/*": ["./src/services/*"],
      "@hooks/*": ["./src/hooks/*"],
      "@store/*": ["./src/store/*"],
      "@types/*": ["./src/types/*"],
      "@utils/*": ["./src/utils/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

### Paso 6: Configurar Axios (API Client)

#### `src/services/api.ts`

```typescript
import axios, { AxiosInstance, AxiosRequestConfig, AxiosError } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Crear instancia de Axios
const api: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 segundos
  withCredentials: true, // Para cookies/sessions
});

// Request interceptor - Agregar token JWT
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Manejar errores globalmente
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Token expirado o inválido
      localStorage.removeItem('accessToken');
      window.location.href = '/login';
    }

    if (error.response?.status === 403) {
      // Sin permisos
      console.error('Acceso denegado');
    }

    if (error.response?.status >= 500) {
      // Error del servidor
      console.error('Error del servidor:', error.response.data);
    }

    return Promise.reject(error);
  }
);

export default api;
```

### Paso 7: Scripts para Sincronizar OpenAPI

#### `scripts/sync-api-schema.sh`

```bash
#!/bin/bash
set -e

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔄 Sincronizando API schema...${NC}"

# 1. Descargar OpenAPI schema desde backend
BACKEND_URL="${VITE_API_BASE_URL:-http://localhost:8000}"
echo -e "${BLUE}📥 Descargando schema desde ${BACKEND_URL}...${NC}"

curl -f "${BACKEND_URL}/openapi.json" > api-schema/openapi.json

if [ $? -ne 0 ]; then
    echo "❌ Error: No se pudo descargar el schema"
    echo "   Verifica que el backend esté corriendo en ${BACKEND_URL}"
    exit 1
fi

echo -e "${GREEN}✅ Schema descargado${NC}"

# 2. Generar tipos TypeScript
echo -e "${BLUE}🔧 Generando tipos TypeScript...${NC}"
npx openapi-typescript api-schema/openapi.json --output src/types/api.ts

echo -e "${GREEN}✅ Tipos generados en src/types/api.ts${NC}"

# 3. Opcional: Generar cliente API
# echo -e "${BLUE}🔧 Generando cliente API...${NC}"
# npx openapi-typescript-codegen \
#   --input api-schema/openapi.json \
#   --output src/services/generated \
#   --client axios

echo -e "${GREEN}✅ Sincronización completada${NC}"
```

```bash
chmod +x scripts/sync-api-schema.sh
```

#### Agregar a `package.json`

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "sync-api": "sh scripts/sync-api-schema.sh",
    "generate-types": "openapi-typescript api-schema/openapi.json --output src/types/api.ts"
  }
}
```

### Paso 8: Ejemplo de Servicio (Companies)

#### `src/services/companies.ts`

```typescript
import api from './api';
import type { components } from '@types/api';

// Tipos auto-generados desde OpenAPI
type Company = components['schemas']['CompanySchema'];
type CompanyCreate = components['schemas']['CompanyCreate'];
type CompanyUpdate = components['schemas']['CompanyUpdate'];

export const companiesService = {
  /**
   * Lista todas las empresas
   */
  async getAll(): Promise<Company[]> {
    const response = await api.get<Company[]>('/companies');
    return response.data;
  },

  /**
   * Obtiene una empresa por ID
   */
  async getById(id: number): Promise<Company> {
    const response = await api.get<Company>(`/companies/${id}`);
    return response.data;
  },

  /**
   * Crea una nueva empresa
   */
  async create(data: CompanyCreate): Promise<Company> {
    const response = await api.post<Company>('/companies', data);
    return response.data;
  },

  /**
   * Actualiza una empresa
   */
  async update(id: number, data: CompanyUpdate): Promise<Company> {
    const response = await api.put<Company>(`/companies/${id}`, data);
    return response.data;
  },

  /**
   * Elimina una empresa (soft delete)
   */
  async delete(id: number): Promise<void> {
    await api.delete(`/companies/${id}`);
  },

  /**
   * Busca empresas por nombre
   */
  async search(query: string): Promise<Company[]> {
    const response = await api.get<Company[]>('/companies/search', {
      params: { q: query },
    });
    return response.data;
  },
};
```

### Paso 9: README del Frontend

#### `README.md`

```markdown
# AK Group Frontend

Sistema de gestión empresarial - Frontend

## Stack

- **React 18+**
- **TypeScript 5+**
- **Vite 5+**
- **Axios** - HTTP client
- **TanStack Query** - Data fetching
- **Zustand** - State management
- **React Router** - Routing

## Setup

```bash
# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env

# Sincronizar API schema desde backend (backend debe estar corriendo)
npm run sync-api

# Iniciar dev server
npm run dev
```

## Scripts

```bash
npm run dev           # Dev server (http://localhost:3000)
npm run build         # Build para producción
npm run preview       # Preview de build
npm run lint          # Linting
npm run sync-api      # Sincronizar API schema desde backend
npm run generate-types # Solo generar tipos TypeScript
```

## Estructura

```
src/
├── components/    # Componentes reutilizables
├── pages/         # Páginas/Vistas
├── services/      # API clients
├── hooks/         # Custom hooks
├── store/         # State management (Zustand)
├── types/         # TypeScript types (auto-generados)
├── utils/         # Utilidades
└── App.tsx        # Componente raíz
```

## Testing

```bash
npm run test
npm run test:coverage
```
```

### Paso 10: Commit y Push

```bash
cd ~/Projects/akgroup-workspace/akgroup-frontend

git add .
git commit -m "feat: initial frontend setup

- Proyecto React + TypeScript + Vite
- Configurado Axios y API client
- Scripts de sincronización OpenAPI
- Estructura de carpetas completa
- Aliases de TypeScript
"

git push origin main
```

---

## Configuración del Contrato API

### Opción 1: Backend Como Fuente de Verdad (Recomendado)

El backend genera automáticamente el OpenAPI schema, no se necesita repo adicional.

**Ventajas**:
- Menos repos que mantener
- Schema siempre actualizado con el código
- Menos posibilidad de desincronización

### Opción 2: Repositorio Independiente

Si prefieres tener un contrato explícito y versionado independientemente:

```bash
cd ~/Projects/akgroup-workspace
git clone git@github.com:akgroup/akgroup-api-contract.git
cd akgroup-api-contract
```

#### Estructura

```
akgroup-api-contract/
├── schemas/
│   ├── v1/
│   │   └── openapi.yaml
│   └── v2/
│       └── openapi.yaml
├── generated/
│   ├── typescript/
│   └── python/
├── scripts/
│   ├── generate-typescript.sh
│   └── generate-python.sh
├── .github/
│   └── workflows/
│       └── generate-code.yml
└── README.md
```

#### `schemas/v1/openapi.yaml`

```yaml
openapi: 3.0.3
info:
  title: AK Group API
  description: Sistema de gestión empresarial
  version: 1.0.0
  contact:
    name: AK Group
    email: dev@akgroup.com

servers:
  - url: http://localhost:8000/api/v1
    description: Desarrollo
  - url: https://api.akgroup.com/api/v1
    description: Producción

paths:
  /companies:
    get:
      summary: Lista todas las empresas
      operationId: listCompanies
      tags:
        - companies
      responses:
        '200':
          description: Lista de empresas
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Company'

    post:
      summary: Crea una nueva empresa
      operationId: createCompany
      tags:
        - companies
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CompanyCreate'
      responses:
        '201':
          description: Empresa creada
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Company'

  /companies/{id}:
    get:
      summary: Obtiene una empresa por ID
      operationId: getCompany
      tags:
        - companies
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: Empresa encontrada
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Company'
        '404':
          description: Empresa no encontrada

components:
  schemas:
    Company:
      type: object
      required:
        - id
        - name
        - rut
      properties:
        id:
          type: integer
          example: 1
        name:
          type: string
          example: "Empresa ABC S.A."
        rut:
          type: string
          example: "12.345.678-9"
        email:
          type: string
          format: email
          nullable: true
          example: "contacto@empresa.com"
        created_at:
          type: string
          format: date-time
        updated_at:
          type: string
          format: date-time

    CompanyCreate:
      type: object
      required:
        - name
        - rut
      properties:
        name:
          type: string
          minLength: 1
          maxLength: 255
        rut:
          type: string
          pattern: '^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$'
        email:
          type: string
          format: email
          nullable: true
```

---

## Docker y Docker Compose

### Repositorio Infrastructure

```bash
cd ~/Projects/akgroup-workspace/akgroup-infra
```

#### Estructura

```
akgroup-infra/
├── docker/
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   └── nginx.conf
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
└── README.md
```

#### `docker/backend.Dockerfile`

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Instalar Poetry
RUN pip install --no-cache-dir poetry==2.1.3

# Copiar archivos de dependencias
COPY pyproject.toml poetry.lock ./

# Configurar Poetry y instalar dependencias
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Copiar código fuente
COPY . .

# Instalar proyecto
RUN poetry install --no-interaction --no-ansi

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Comando por defecto
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### `docker/frontend.Dockerfile`

```dockerfile
# Build stage
FROM node:20-alpine AS build

WORKDIR /app

# Copiar package files
COPY package*.json ./

# Instalar dependencias
RUN npm ci

# Copiar código fuente
COPY . .

# Build
RUN npm run build

# Production stage
FROM nginx:alpine

# Copiar build
COPY --from=build /app/dist /usr/share/nginx/html

# Copiar configuración nginx
COPY docker/nginx.conf /etc/nginx/nginx.conf

# Exponer puerto
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:80 || exit 1

CMD ["nginx", "-g", "daemon off;"]
```

#### `docker/nginx.conf`

```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    # Gzip
    gzip on;
    gzip_vary on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    upstream backend {
        server backend:8000;
    }

    server {
        listen 80;
        server_name _;

        # Frontend - SPA
        location / {
            root /usr/share/nginx/html;
            index index.html;
            try_files $uri $uri/ /index.html;
        }

        # Backend API
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Backend docs
        location /docs {
            proxy_pass http://backend;
            proxy_set_header Host $host;
        }

        location /redoc {
            proxy_pass http://backend;
            proxy_set_header Host $host;
        }

        location /openapi.json {
            proxy_pass http://backend;
            proxy_set_header Host $host;
        }

        # Health check
        location /health {
            proxy_pass http://backend;
            proxy_set_header Host $host;
        }
    }
}
```

#### `docker-compose.yml` (Desarrollo)

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ../akgroup-backend
      dockerfile: ../akgroup-infra/docker/backend.Dockerfile
    container_name: akgroup-backend-dev
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=development
      - DATABASE_TYPE=sqlite
      - DATABASE_URL=sqlite:///./akgroup.db
      - CORS_ORIGINS=["http://localhost:3000"]
      - LOG_LEVEL=DEBUG
      - API_HOST=0.0.0.0
      - API_PORT=8000
      - API_RELOAD=true
    volumes:
      - ../akgroup-backend:/app
      - /app/.venv  # No montar .venv
      - backend-data:/app/data
    command: poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    networks:
      - akgroup-net
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ../akgroup-frontend
      dockerfile: ../akgroup-infra/docker/frontend.Dockerfile
      target: build
    container_name: akgroup-frontend-dev
    ports:
      - "3000:3000"
    environment:
      - VITE_API_BASE_URL=http://localhost:8000
      - VITE_ENV=development
    volumes:
      - ../akgroup-frontend:/app
      - /app/node_modules
    command: npm run dev -- --host
    depends_on:
      backend:
        condition: service_healthy
    networks:
      - akgroup-net

volumes:
  backend-data:

networks:
  akgroup-net:
    driver: bridge
```

#### `docker-compose.prod.yml` (Producción)

```yaml
version: '3.8'

services:
  db:
    image: mysql:8.0
    container_name: akgroup-db
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: akgroup_db
      MYSQL_USER: akgroup_user
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
    volumes:
      - mysql-data:/var/lib/mysql
    networks:
      - akgroup-net
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ../akgroup-backend
      dockerfile: ../akgroup-infra/docker/backend.Dockerfile
    container_name: akgroup-backend
    restart: always
    environment:
      - ENVIRONMENT=production
      - DATABASE_TYPE=mysql
      - DATABASE_URL=mysql+pymysql://akgroup_user:${MYSQL_PASSWORD}@db:3306/akgroup_db
      - CORS_ORIGINS=["https://app.akgroup.com"]
      - LOG_LEVEL=INFO
    depends_on:
      db:
        condition: service_healthy
    networks:
      - akgroup-net
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ../akgroup-frontend
      dockerfile: ../akgroup-infra/docker/frontend.Dockerfile
    container_name: akgroup-frontend
    restart: always
    depends_on:
      - backend
    networks:
      - akgroup-net

  nginx:
    image: nginx:alpine
    container_name: akgroup-nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      backend:
        condition: service_healthy
      frontend:
        condition: service_started
    networks:
      - akgroup-net

volumes:
  mysql-data:

networks:
  akgroup-net:
    driver: bridge
```

---

## CI/CD con GitHub Actions

### Backend CI/CD

#### `.github/workflows/backend-ci.yml`

```yaml
name: Backend CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: root
          MYSQL_DATABASE: test_db
        ports:
          - 3306:3306
        options: --health-cmd="mysqladmin ping" --health-interval=10s --health-timeout=5s --health-retries=3

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'

      - name: Install Poetry
        run: |
          curl -sSL https://install.python-poetry.org | python3 -
          echo "$HOME/.local/bin" >> $GITHUB_PATH

      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pypoetry
          key: ${{ runner.os }}-poetry-${{ hashFiles('**/poetry.lock') }}

      - name: Install dependencies
        run: poetry install

      - name: Run tests
        run: poetry run pytest --cov --cov-report=xml

      - name: Type check
        run: poetry run mypy .

      - name: Lint
        run: poetry run ruff check .

      - name: Format check
        run: poetry run black --check .

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml

  export-openapi:
    runs-on: ubuntu-latest
    needs: test
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'

      - name: Install Poetry
        run: |
          curl -sSL https://install.python-poetry.org | python3 -
          echo "$HOME/.local/bin" >> $GITHUB_PATH

      - name: Install dependencies
        run: poetry install

      - name: Export OpenAPI schema
        run: poetry run python scripts/export_openapi.py

      - name: Upload OpenAPI artifact
        uses: actions/upload-artifact@v3
        with:
          name: openapi-schema
          path: openapi.json

      - name: Notify frontend
        uses: peter-evans/repository-dispatch@v2
        with:
          token: ${{ secrets.REPO_ACCESS_TOKEN }}
          repository: akgroup/akgroup-frontend
          event-type: api-updated
          client-payload: '{"version": "${{ github.sha }}"}'
```

### Frontend CI/CD

#### `.github/workflows/frontend-ci.yml`

```yaml
name: Frontend CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
  repository_dispatch:
    types: [api-updated]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Lint
        run: npm run lint

      - name: Type check
        run: npx tsc --noEmit

      - name: Run tests
        run: npm run test

      - name: Build
        run: npm run build

      - name: Upload build artifact
        uses: actions/upload-artifact@v3
        with:
          name: frontend-build
          path: dist/

  sync-api-schema:
    runs-on: ubuntu-latest
    if: github.event_name == 'repository_dispatch'

    steps:
      - uses: actions/checkout@v3

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Download OpenAPI schema
        run: curl -f https://api.akgroup.com/openapi.json > api-schema/openapi.json

      - name: Generate TypeScript types
        run: npm run generate-types

      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v5
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          commit-message: 'chore: update API types'
          title: 'chore: update API types from backend'
          body: |
            Auto-generated PR to sync API schema changes.

            Backend version: ${{ github.event.client_payload.version }}
          branch: api-schema-update
          delete-branch: true
```

---

## Desarrollo Local

### Script de Setup Completo

Crear script para setup inicial:

#### `setup-workspace.sh`

```bash
#!/bin/bash
set -e

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 Setup de Workspace AK Group${NC}"

# 1. Verificar herramientas
echo -e "\n${BLUE}🔍 Verificando herramientas...${NC}"
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 no instalado"; exit 1; }
command -v poetry >/dev/null 2>&1 || { echo "❌ Poetry no instalado"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js no instalado"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "⚠️  Docker no instalado (opcional)"; }

echo -e "${GREEN}✅ Herramientas verificadas${NC}"

# 2. Clonar repos
echo -e "\n${BLUE}📦 Clonando repositorios...${NC}"
mkdir -p akgroup-workspace
cd akgroup-workspace

if [ ! -d "akgroup-backend" ]; then
    git clone git@github.com:akgroup/akgroup-backend.git
fi

if [ ! -d "akgroup-frontend" ]; then
    git clone git@github.com:akgroup/akgroup-frontend.git
fi

if [ ! -d "akgroup-infra" ]; then
    git clone git@github.com:akgroup/akgroup-infra.git
fi

echo -e "${GREEN}✅ Repositorios clonados${NC}"

# 3. Setup backend
echo -e "\n${BLUE}🔧 Configurando backend...${NC}"
cd akgroup-backend
cp .env.example .env
poetry install
poetry run alembic upgrade head
echo -e "${GREEN}✅ Backend configurado${NC}"

# 4. Setup frontend
echo -e "\n${BLUE}🔧 Configurando frontend...${NC}"
cd ../akgroup-frontend
cp .env.example .env
npm install
echo -e "${GREEN}✅ Frontend configurado${NC}"

# 5. Verificar
echo -e "\n${BLUE}✨ Setup completado!${NC}"
echo -e "\n${YELLOW}Próximos pasos:${NC}"
echo -e "  1. Iniciar backend:  cd akgroup-backend && poetry run python main.py"
echo -e "  2. Sincronizar API:  cd akgroup-frontend && npm run sync-api"
echo -e "  3. Iniciar frontend: cd akgroup-frontend && npm run dev"
echo -e "\n${YELLOW}O usar Docker:${NC}"
echo -e "  cd akgroup-infra && docker-compose up"
```

### Desarrollo Día a Día

#### Opción 1: Manual

```bash
# Terminal 1: Backend
cd akgroup-backend
poetry run python main.py

# Terminal 2: Frontend
cd akgroup-frontend
npm run dev

# Terminal 3: Sincronizar API (cuando sea necesario)
cd akgroup-frontend
npm run sync-api
```

#### Opción 2: Docker Compose

```bash
cd akgroup-infra
docker-compose up
```

---

## Verificación del Setup

### Checklist

```bash
# ✅ Backend
cd akgroup-backend
poetry run python main.py  # Debe iniciar sin errores
curl http://localhost:8000/health  # Debe retornar {"status": "healthy"}
curl http://localhost:8000/docs  # Debe abrir Swagger UI

# ✅ Frontend
cd akgroup-frontend
npm run dev  # Debe iniciar sin errores
# Abrir http://localhost:3000 en navegador

# ✅ API Schema
cd akgroup-frontend
npm run sync-api  # Debe descargar openapi.json y generar tipos

# ✅ Docker
cd akgroup-infra
docker-compose up  # Ambos servicios deben iniciar
curl http://localhost:8000/health  # Backend funcional
curl http://localhost:3000  # Frontend funcional
```

### Verificar Conectividad

```typescript
// En el navegador (console):
fetch('http://localhost:8000/api/v1/companies')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error)
```

---

**Siguiente:** [03-WORKFLOW.md - Flujos de Trabajo](./03-WORKFLOW.md)
