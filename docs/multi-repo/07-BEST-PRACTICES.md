# Mejores Prácticas Multi-Repo

## Organización de Código

### Backend

**Estructura Clara:**
```python
# ✅ BIEN: Separación clara de responsabilidades
src/
├── api/          # Endpoints (controllers)
├── models/       # ORM models
├── schemas/      # Pydantic schemas (validation)
├── repositories/ # Data access layer
├── services/     # Business logic
└── config/       # Configuration

# ❌ MAL: Todo mezclado
src/
└── everything_here.py
```

**Type Hints Siempre:**
```python
# ✅ BIEN
def create_company(data: CompanyCreate, user_id: int) -> Company:
    """Crea una nueva empresa."""
    ...

# ❌ MAL
def create_company(data, user_id):
    ...
```

**Docstrings Completos:**
```python
# ✅ BIEN
def create_company(data: CompanyCreate) -> Company:
    """
    Crea una nueva empresa en el sistema.

    Args:
        data: Datos de la empresa a crear

    Returns:
        Company creada con ID asignado

    Raises:
        DuplicateException: Si el RUT ya existe
        ValidationException: Si los datos son inválidos

    Example:
        >>> create_company(CompanyCreate(name="Test", rut="12.345.678-9"))
        Company(id=1, name="Test", ...)
    """
    ...
```

### Frontend

**Componentes Pequeños:**
```tsx
// ✅ BIEN: Componente pequeño con una responsabilidad
export function CompanyCard({ company }: { company: Company }) {
  return (
    <div className="card">
      <h3>{company.name}</h3>
      <p>{company.rut}</p>
    </div>
  );
}

// ❌ MAL: Componente gigante que hace todo
export function CompanyPage() {
  // 500 líneas de código...
}
```

**Custom Hooks para Lógica:**
```typescript
// ✅ BIEN: Lógica encapsulada en hook
export function useCompanies() {
  return useQuery({
    queryKey: ['companies'],
    queryFn: companiesService.getAll,
  });
}

// Uso simple en componente
function CompanyList() {
  const { data: companies, isLoading } = useCompanies();
  // ...
}
```

**Tipos Desde API:**
```typescript
// ✅ BIEN: Usar tipos generados desde OpenAPI
import type { components } from '@types/api';
type Company = components['schemas']['Company'];

// ❌ MAL: Duplicar tipos manualmente
interface Company {
  id: number;
  name: string;
  // ... puede desincronizarse
}
```

## Git Workflow

### Naming Conventions

```bash
# Branches
feature/nombre-funcionalidad
bugfix/descripcion-bug
hotfix/v1.2.3
release/v1.3.0

# Commits (Conventional Commits)
feat: agregar módulo de proveedores
fix: corregir cálculo de totales
docs: actualizar README
chore: actualizar dependencias
refactor: simplificar lógica de productos
test: agregar tests de integración
```

### Commit Messages

```bash
# ✅ BIEN
feat(companies): add search filters

- Add name filter
- Add RUT filter
- Update OpenAPI schema

Closes #123

# ❌ MAL
update stuff
```

### Pull Requests

**Template de PR:**
```markdown
## Descripción
Breve descripción de los cambios

## Tipo de cambio
- [ ] Bug fix
- [ ] Nueva funcionalidad
- [ ] Breaking change
- [ ] Actualización de documentación

## Checklist
- [ ] Tests agregados/actualizados
- [ ] Documentación actualizada
- [ ] OpenAPI schema actualizado (backend)
- [ ] Types sincronizados (frontend)

## Screenshots (si aplica)

## Relacionado
Closes #123
Related to akgroup/akgroup-frontend#456
```

## API Design

### RESTful Conventions

```python
# ✅ BIEN: RESTful
GET    /api/v1/companies          # Lista
POST   /api/v1/companies          # Crear
GET    /api/v1/companies/{id}     # Obtener
PUT    /api/v1/companies/{id}     # Actualizar completo
PATCH  /api/v1/companies/{id}     # Actualizar parcial
DELETE /api/v1/companies/{id}     # Eliminar

# ❌ MAL: No RESTful
GET    /api/v1/getCompanies
POST   /api/v1/createCompany
GET    /api/v1/company?id=123
```

### Response Structure

```python
# ✅ BIEN: Consistente
{
  "id": 1,
  "name": "Company",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}

# ✅ BIEN: Error structure
{
  "error": "ValidationError",
  "message": "Invalid RUT format",
  "details": {
    "field": "rut",
    "value": "invalid"
  }
}

# ❌ MAL: Inconsistente
{
  "data": {...},
  "success": true,
  "timestamp": "..."
}
```

### Pagination

```python
# ✅ BIEN: Pagination estándar
GET /api/v1/companies?page=1&per_page=20

Response:
{
  "items": [...],
  "total": 100,
  "page": 1,
  "per_page": 20,
  "pages": 5
}

# O cursor-based
GET /api/v1/companies?cursor=abc123&limit=20

Response:
{
  "items": [...],
  "next_cursor": "def456",
  "has_more": true
}
```

## Testing

### Backend Tests

```python
# Test de endpoint (integración)
def test_create_company(client, auth_headers):
    """Test crear empresa"""
    data = {
        "name": "Test Company",
        "rut": "12.345.678-9"
    }

    response = client.post(
        "/api/v1/companies",
        json=data,
        headers=auth_headers
    )

    assert response.status_code == 201
    company = response.json()
    assert company["name"] == "Test Company"
    assert company["id"] > 0

# Test de servicio (unitario)
def test_company_service_create(mock_repo):
    """Test lógica de negocio"""
    service = CompanyService(mock_repo)

    data = CompanyCreate(name="Test", rut="12.345.678-9")
    company = service.create(data)

    assert company.name == "Test"
    mock_repo.add.assert_called_once()
```

### Frontend Tests

```typescript
// Test de componente
describe('CompanyCard', () => {
  it('renders company information', () => {
    const company: Company = {
      id: 1,
      name: 'Test Company',
      rut: '12.345.678-9',
    };

    render(<CompanyCard company={company} />);

    expect(screen.getByText('Test Company')).toBeInTheDocument();
    expect(screen.getByText('12.345.678-9')).toBeInTheDocument();
  });
});

// Test de hook
describe('useCompanies', () => {
  it('fetches companies', async () => {
    const { result } = renderHook(() => useCompanies(), {
      wrapper: QueryClientProvider,
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toHaveLength(10);
  });
});
```

## Seguridad

### Backend

```python
# ✅ Validar inputs
from pydantic import Field, EmailStr

class CompanyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr | None = None

# ✅ SQL Injection protection (ORM)
companies = session.execute(
    select(Company).where(Company.name == name)  # ✅ Safe
).scalars().all()

# ❌ NO hacer raw SQL sin parameters
query = f"SELECT * FROM companies WHERE name = '{name}'"  # ❌ Unsafe
```

### Frontend

```typescript
// ✅ Sanitize user input
import DOMPurify from 'dompurify';

const sanitized = DOMPurify.sanitize(userInput);

// ✅ Validar en cliente también
const schema = z.object({
  name: z.string().min(1).max(255),
  email: z.string().email().optional(),
});

// ❌ NO confiar en datos del cliente
// Siempre validar en backend también
```

## Performance

### Backend

```python
# ✅ Usar índices en DB
class Company(Base):
    __tablename__ = "companies"

    rut = Column(String, unique=True, index=True)  # ✅ Index
    email = Column(String, index=True)             # ✅ Index

# ✅ Pagination para listas grandes
@router.get("/companies")
def list_companies(page: int = 1, per_page: int = 20):
    offset = (page - 1) * per_page
    companies = session.query(Company).offset(offset).limit(per_page).all()
    return companies

# ✅ Select only needed fields
companies = session.execute(
    select(Company.id, Company.name, Company.rut)  # Solo campos necesarios
).all()
```

### Frontend

```typescript
// ✅ Memoization
const MemoizedCompanyCard = React.memo(CompanyCard);

// ✅ Lazy loading
const CompanyDetails = lazy(() => import('./CompanyDetails'));

// ✅ Data caching con TanStack Query
const { data } = useQuery({
  queryKey: ['companies'],
  queryFn: companiesService.getAll,
  staleTime: 5 * 60 * 1000,  // 5 minutos
});

// ✅ Debounce en búsquedas
const debouncedSearch = useDebouncedCallback(
  (value) => {
    search(value);
  },
  500
);
```

## Comunicación Entre Equipos

### Slack/Discord Channels

```
#backend          - Backend discussions
#frontend         - Frontend discussions
#api-changes      - Notificaciones de cambios en API
#releases         - Coordinación de releases
#incidents        - Problemas en producción
```

### Documentation

```markdown
# Mantener docs actualizados
- README.md en cada repo
- OpenAPI documentation
- Architecture Decision Records (ADRs)
- Changelog

# Ejemplo: ADR
## ADR-001: Usar Multi-Repo Architecture

### Context
Necesitamos decidir entre monorepo y multi-repo

### Decision
Usaremos multi-repo

### Consequences
+ Deploys independientes
+ Equipos separados
- Sincronización manual
```

---

## Resumen de Reglas de Oro

1. **Backend es fuente de verdad** para API contract
2. **Sincronizar types** después de cada cambio en backend
3. **Semantic versioning** estricto en ambos repos
4. **Tests siempre** antes de merge
5. **Documentar breaking changes** explícitamente
6. **Coordinar releases** grandes
7. **Monitorear** ambos servicios en producción
8. **Comunicar** cambios entre equipos
9. **Code review** obligatorio
10. **Automatizar** todo lo posible

---

**FIN DE LA GUÍA MULTI-REPO**

Documentos adicionales:
- [01-GUIDE.md](./01-GUIDE.md) - Guía general
- [02-SETUP.md](./02-SETUP.md) - Setup e implementación
- [03-WORKFLOW.md](./03-WORKFLOW.md) - Flujos de trabajo
- [04-API-CONTRACT.md](./04-API-CONTRACT.md) - Contrato API
- [05-DEPLOYMENT.md](./05-DEPLOYMENT.md) - Deployment
- [06-TROUBLESHOOTING.md](./06-TROUBLESHOOTING.md) - Solución de problemas
