# Documentación Multi-Repo - AK Group

Guía completa para trabajar con arquitectura Multi-Repo (repositorios separados para backend y frontend).

## 📚 Índice de Documentos

### [01 - Guía General](./01-GUIDE.md)
**Conceptos fundamentales y arquitectura**
- Introducción a Multi-Repo
- Conceptos clave (API Contract, Code Generation, etc.)
- Arquitectura general
- Comunicación entre servicios
- Ventajas y desventajas
- Cuándo usar esta arquitectura
- Comparación con monorepo y backend embebido

**Tiempo de lectura:** ~25 minutos

---

### [02 - Setup e Implementación](./02-SETUP.md)
**Guía paso a paso para implementar Multi-Repo**
- Requisitos previos
- Setup inicial de repositorios
- Configuración del backend (FastAPI)
- Configuración del frontend (React/Vue)
- Docker y Docker Compose
- CI/CD con GitHub Actions
- Desarrollo local
- Verificación del setup

**Tiempo de implementación:** ~4-6 horas

---

### [03 - Flujos de Trabajo](./03-WORKFLOW.md)
**Desarrollo día a día**
- Setup matutino
- Crear nuevas features
  - Solo frontend
  - Solo backend
  - Full-stack (backend + frontend)
- Sincronización de cambios en API
- Testing (unitario, integración, E2E)
- Manejo de breaking changes
- Proceso de release
- Hotfixes

**Referencia diaria**

---

### [04 - Contrato API (OpenAPI)](./04-API-CONTRACT.md)
**Gestión del contrato API**
- OpenAPI como fuente de verdad
- Generación automática de código
- Versionado de API
- Schema validation
- Deprecación de endpoints
- Ejemplos prácticos

**Referencia técnica**

---

### [05 - Deployment](./05-DEPLOYMENT.md)
**Estrategias de deployment**
- Deployment independiente vs coordinado
- CI/CD pipelines completos
- Ambientes (development, staging, production)
- Docker/Kubernetes
- Monitoreo y logging
- Health checks
- Rollback strategies

**Guía de DevOps**

---

### [06 - Troubleshooting](./06-TROUBLESHOOTING.md)
**Solución de problemas comunes**
- CORS errors
- Type mismatches
- Version incompatibility
- Database migrations
- Docker networking
- Debugging cross-service
- FAQ

**Referencia de problemas**

---

### [07 - Mejores Prácticas](./07-BEST-PRACTICES.md)
**Estándares y convenciones**
- Organización de código
- Git workflow
- API design (RESTful)
- Testing best practices
- Seguridad
- Performance
- Comunicación entre equipos
- Reglas de oro

**Guía de estándares**

---

## 🚀 Quick Start

### Para Comenzar

1. **Leer primero:** [01-GUIDE.md](./01-GUIDE.md) para entender conceptos
2. **Implementar:** [02-SETUP.md](./02-SETUP.md) para setup inicial
3. **Referencia diaria:** [03-WORKFLOW.md](./03-WORKFLOW.md) para flujos de trabajo

### Orden Recomendado de Lectura

**Primera vez (completo):**
```
01-GUIDE.md → 02-SETUP.md → 03-WORKFLOW.md
```

**Implementando:**
```
02-SETUP.md (paso a paso)
```

**Día a día:**
```
03-WORKFLOW.md (referencia)
04-API-CONTRACT.md (cuando cambias API)
06-TROUBLESHOOTING.md (cuando hay problemas)
```

**Deployment:**
```
05-DEPLOYMENT.md (configurar CI/CD)
```

**Mejorando código:**
```
07-BEST-PRACTICES.md (estándares)
```

---

## 📋 Resumen Ejecutivo

### ¿Qué es Multi-Repo?

Arquitectura donde **backend** y **frontend** viven en repositorios Git completamente separados, comunicándose a través de un **contrato API** (OpenAPI/Swagger).

### Estructura

```
GitHub Organization: akgroup
│
├── akgroup-backend/    # FastAPI (Python)
├── akgroup-frontend/   # React/Vue (TypeScript)
└── akgroup-infra/      # Docker, CI/CD
```

### Ventajas Principales

✅ Deploys independientes
✅ Equipos especializados
✅ Escalabilidad (múltiples frontends)
✅ Permisos granulares
✅ Backend reutilizable

### Cuándo Usar

- Equipos separados (backend/frontend)
- Múltiples clientes (web, mobile, admin)
- Backend como API pública
- Proyecto a largo plazo

### Flujo Típico

```
1. Backend desarrolla nuevo endpoint
2. Backend mergea y deploya
3. GitHub Action notifica frontend
4. Frontend sincroniza API types
5. Frontend desarrolla UI
6. Frontend mergea y deploya
```

---

## 🛠️ Herramientas Necesarias

### Backend
- Python 3.13+
- Poetry 2.1.3+
- FastAPI 0.115.0+
- SQLAlchemy 2.0.44+

### Frontend
- Node.js 20+
- TypeScript 5+
- React/Vue
- Axios

### DevOps
- Docker 24+
- Docker Compose 2.20+
- GitHub Actions

---

## 📊 Estructura de Archivos

### Backend Repository

```
akgroup-backend/
├── src/
│   ├── api/          # Endpoints
│   ├── models/       # ORM models
│   ├── schemas/      # Pydantic schemas
│   ├── services/     # Business logic
│   └── repositories/ # Data access
├── tests/
├── migrations/
├── main.py
├── pyproject.toml
└── openapi.json      # API contract (generado)
```

### Frontend Repository

```
akgroup-frontend/
├── src/
│   ├── components/   # UI components
│   ├── pages/        # Views
│   ├── services/     # API clients
│   ├── types/        # TypeScript types (generados)
│   └── hooks/        # Custom hooks
├── api-schema/
│   └── openapi.json  # Copiado desde backend
├── package.json
└── vite.config.ts
```

---

## 🔗 Enlaces Útiles

### Recursos Externos
- [OpenAPI Specification](https://swagger.io/specification/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [GitHub Actions](https://docs.github.com/en/actions)

### Repositorios de Ejemplo
- [Full-Stack FastAPI Template](https://github.com/tiangolo/full-stack-fastapi-template)
- [Awesome FastAPI](https://github.com/mjhea0/awesome-fastapi)

---

## 📞 Soporte

¿Preguntas o problemas?

1. Revisa [06-TROUBLESHOOTING.md](./06-TROUBLESHOOTING.md)
2. Busca en issues de GitHub
3. Pregunta en el canal `#api-changes` de Slack

---

## 📝 Mantenimiento de Docs

Estos documentos deben actualizarse cuando:
- Cambia la arquitectura
- Se agregan nuevas herramientas
- Se descubren nuevos problemas comunes
- Se establecen nuevas convenciones

**Última actualización:** Octubre 2025
**Versión:** 1.0.0
