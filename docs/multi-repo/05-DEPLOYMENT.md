# Deployment Multi-Repo

## Estrategias de Deployment

### 1. Deployment Independiente

Backend y frontend se deployan por separado:

```
Backend v1.2.3  →  Deploy independiente  →  Production
Frontend v2.1.0 →  Deploy independiente  →  Production
```

**Ventaja**: Flexibilidad total
**Desventaja**: Requiere coordinar releases

### 2. Deployment Coordinado

Deployar ambos servicios juntos para features grandes:

```
Backend v1.3.0 + Frontend v2.2.0  →  Deploy simultáneo  →  Production
```

### 3. Rolling Deployment

Backend mantiene compatibilidad mientras frontend se actualiza:

```
t0: Backend v1.2.3 + Frontend v2.0.0
t1: Backend v1.3.0 (backwards compatible) deployed
t2: Frontend v2.1.0 deployed (usa nuevas features)
t3: Backend v1.4.0 (elimina deprecated features)
```

## CI/CD con GitHub Actions

### Backend Pipeline

```yaml
# .github/workflows/backend-deploy.yml
name: Backend Deploy

on:
  push:
    branches: [main]
    tags:
      - 'v*'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      - name: Install Poetry
        run: pip install poetry
      - name: Install dependencies
        run: poetry install
      - name: Run tests
        run: poetry run pytest --cov

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: docker build -t akgroup/backend:${{ github.sha }} .
      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push akgroup/backend:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          ssh user@server "cd /app && docker pull akgroup/backend:${{ github.sha }} && docker-compose up -d backend"
```

### Frontend Pipeline

```yaml
# .github/workflows/frontend-deploy.yml
name: Frontend Deploy

on:
  push:
    branches: [main]
    tags:
      - 'v*'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '20'
      - name: Install dependencies
        run: npm ci
      - name: Run tests
        run: npm run test
      - name: Build
        run: npm run build

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build
        run: npm run build
      - name: Deploy to S3/CDN
        run: aws s3 sync dist/ s3://akgroup-frontend-prod
```

## Ambientes

### Development

```yaml
# docker-compose.yml
services:
  backend:
    environment:
      - ENVIRONMENT=development
      - DATABASE_TYPE=sqlite
      - LOG_LEVEL=DEBUG
  frontend:
    environment:
      - VITE_API_BASE_URL=http://localhost:8000
```

### Staging

```yaml
# docker-compose.staging.yml
services:
  backend:
    environment:
      - ENVIRONMENT=staging
      - DATABASE_URL=mysql://user:pass@db-staging:3306/akgroup
      - CORS_ORIGINS=["https://staging.akgroup.com"]
  frontend:
    environment:
      - VITE_API_BASE_URL=https://api-staging.akgroup.com
```

### Production

```yaml
# docker-compose.prod.yml
services:
  backend:
    replicas: 3
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=mysql://user:pass@db-prod:3306/akgroup
      - CORS_ORIGINS=["https://app.akgroup.com"]
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
  frontend:
    environment:
      - VITE_API_BASE_URL=https://api.akgroup.com
```

## Monitoreo y Logging

### Backend Logs

```python
# src/utils/logger.py
from loguru import logger

logger.add(
    "logs/app.log",
    rotation="500 MB",
    retention="10 days",
    level="INFO"
)

# Usar en código
logger.info("Company created", company_id=123, user_id=456)
```

### Metrics

```python
# Prometheus metrics
from prometheus_client import Counter, Histogram

request_count = Counter('http_requests_total', 'Total HTTP requests')
request_latency = Histogram('http_request_duration_seconds', 'HTTP request latency')

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    request_latency.observe(time.time() - start)
    request_count.inc()
    return response
```

### Health Checks

```python
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "version": "1.2.3",
        "database": check_db(),
        "timestamp": datetime.now().isoformat()
    }
```

---

**Siguiente:** [06-TROUBLESHOOTING.md](./06-TROUBLESHOOTING.md)
