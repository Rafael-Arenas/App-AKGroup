# Frontend Flet - AK Group

Frontend de escritorio multiplataforma para el Sistema de Gestión AK Group, construido con Flet (Flutter + Python).

## Arquitectura

El frontend sigue la arquitectura probada de Planificador3 con los siguientes patrones:

- **Singleton Pattern**: Estado global único (`app_state`)
- **Observer Pattern**: Componentes se suscriben a cambios de estado
- **Repository Pattern**: APIs separadas por dominio
- **Component Pattern**: Componentes reutilizables y composables

## Estructura de Directorios

```
src/frontend/
├── main.py                      # Entry point de la aplicación
├── app_state.py                 # Estado global (Singleton + Observer)
├── layout_constants.py          # Dimensiones y espaciado
├── navigation_config.py         # Configuración de navegación
│
├── components/                  # Componentes reutilizables
│   ├── navigation/             # Navegación (AppBar, Rail, Breadcrumb)
│   ├── common/                 # Comunes (Spinner, Error, Card, Table)
│   ├── forms/                  # Formularios (TextField, Dropdown, DatePicker)
│   └── charts/                 # Visualización (KPICard)
│
├── views/                       # Vistas de la aplicación
│   ├── main_view.py            # Vista principal contenedora
│   ├── dashboard/              # Dashboard
│   ├── companies/              # Gestión de empresas
│   └── products/               # Gestión de productos
│
├── i18n/                        # Internacionalización
│   ├── translation_manager.py  # Gestor de traducciones
│   └── locales/                # Archivos JSON (es, en, fr)
│
└── services/                    # Servicios
    └── api/                    # Clientes API (Company, Product, Lookup)
```

## Ejecutar la Aplicación

### Requisitos

- Python 3.13+
- Poetry 2.1.3+
- Backend FastAPI corriendo en http://localhost:8000

### Comandos

```bash
# Solo frontend
poetry run python src/frontend/main.py
# o
poetry run python scripts/dev_frontend.py

# Backend + Frontend
poetry run python scripts/dev_all.py
```

## Características Principales

### Componentes de Navegación

- **CustomNavigationRail**: Sidebar expandible/colapsable (72px ↔ 256px)
- **CustomAppBar**: Header con logo, título, selector de idioma/tema, notificaciones, perfil
- **Breadcrumb**: Navegación contextual tipo migas de pan

### Componentes Comunes

- **LoadingSpinner**: Indicador de carga con mensaje
- **ErrorDisplay**: Display de errores con botón "Reintentar"
- **EmptyState**: Estado vacío con ícono y acción
- **BaseCard**: Tarjeta colapsable con header y acciones
- **DataTable**: Tabla con ordenamiento, paginación y acciones por fila
- **SearchBar**: Búsqueda con debouncing e historial
- **FilterPanel**: Panel de filtros colapsable

### Componentes de Formularios

- **ValidatedTextField**: TextField con validadores built-in (email, phone, url, etc.)
- **DropdownField**: Dropdown con validación
- **DatePickerField**: Selector de fechas

### Vistas Principales

- **Dashboard**: Métricas (KPIs) y actividad reciente
- **Companies**: CRUD completo de empresas con búsqueda y filtros
- **Products**: CRUD de productos con soporte BOM (Bill of Materials)

## Internacionalización (i18n)

La aplicación soporta 3 idiomas:

- 🇪🇸 Español (ES) - por defecto
- 🇬🇧 Inglés (EN)
- 🇫🇷 Francés (FR)

### Uso

```python
from src.frontend.i18n.translation_manager import t

# Obtener traducción
title = t("companies.title")  # "Empresas"

# Con parámetros
error_msg = t("common.error", {"error": "404"})  # "Error: 404"
```

## Sistema de Temas

- **Claro**: Tema claro (default)
- **Oscuro**: Tema oscuro
- **Sistema**: Sigue el tema del sistema operativo

Todos los componentes se adaptan automáticamente al tema activo.

## Estado Global (AppState)

### NavigationState

```python
from src.frontend.app_state import app_state

# Cambiar sección
app_state.navigation.set_section(1, "companies.title", "/companies")

# Actualizar breadcrumb
app_state.navigation.set_breadcrumb([
    {"label": "Inicio", "route": "/"},
    {"label": "Empresas", "route": "/companies"}
])

# Suscribirse a cambios
def on_nav_change():
    print("Navegación cambió")

app_state.navigation.add_observer(on_nav_change)
```

### I18nState

```python
# Cambiar idioma
app_state.i18n.set_language("en")

# Suscribirse a cambios
def on_lang_change():
    print("Idioma cambió")

app_state.i18n.add_observer(on_lang_change)
```

### ThemeState

```python
# Cambiar tema
app_state.theme.set_theme_mode("dark")  # "light" | "dark" | "system"

# Obtener si es modo oscuro
is_dark = app_state.theme.is_dark_mode

# Suscribirse a cambios
def on_theme_change():
    print("Tema cambió")

app_state.theme.add_observer(on_theme_change)
```

## Servicios API

### Company API

```python
from src.frontend.services.api import company_api

# Listar empresas
companies = await company_api.get_all(skip=0, limit=100)

# Buscar por nombre
results = await company_api.search("AK Group")

# Crear empresa
company = await company_api.create({
    "name": "Mi Empresa",
    "trigram": "MEP",
    "company_type_id": 1,
    "country_id": 152
})

# Actualizar
updated = await company_api.update(1, {"name": "Nuevo Nombre"})

# Eliminar
await company_api.delete(1)
```

### Product API

```python
from src.frontend.services.api import product_api

# Listar productos
products = await product_api.get_all()

# Por tipo
articles = await product_api.get_by_type("ARTICLE")
nomenclatures = await product_api.get_by_type("NOMENCLATURE")

# Crear producto
product = await product_api.create({
    "code": "PROD-001",
    "name": "Producto 1",
    "product_type": "ARTICLE",
    "unit_id": 1,
    "cost": 100.00
})

# Agregar componente (BOM)
await product_api.add_component(product_id, {
    "component_id": 2,
    "quantity": 5
})
```

### Lookup API

```python
from src.frontend.services.api import lookup_api

# Obtener tipos de empresa
company_types = await lookup_api.get_company_types()

# Obtener países
countries = await lookup_api.get_countries()

# Obtener unidades
units = await lookup_api.get_units()
```

## Ciclo de Vida de Componentes

```python
class MyView(ft.Container):
    def __init__(self):
        super().__init__()
        # 1. Configurar propiedades
        self.expand = True

        # 2. Inicializar estado
        self.data = []

        # 3. Crear componentes
        self._build_components()

        # 4. Suscribirse a observers
        app_state.i18n.add_observer(self._on_language_change)

        # 5. Construir layout
        self.content = self._build_layout()

    def did_mount(self):
        """Llamado después de agregar a page"""
        self.page.run_task(self.load_data)

    async def load_data(self):
        """Carga asíncrona de datos"""
        self.loading = True
        self._update_content()

        try:
            self.data = await api.get_all()
        except Exception as e:
            self.error = str(e)
        finally:
            self.loading = False
            self._update_content()

    def will_unmount(self):
        """Limpieza antes de desmontar"""
        app_state.i18n.remove_observer(self._on_language_change)
```

## Mejores Prácticas

1. **Type Hints**: Usar type hints completos en todas las funciones
2. **Docstrings**: Documentar con formato Google style
3. **Logging**: Usar loguru para logging estructurado
4. **Async/Await**: Todas las llamadas a API deben ser async
5. **Estados**: Manejar loading, error y empty states
6. **Observers**: Limpiar observers en `will_unmount()`
7. **Constantes**: Usar LayoutConstants para dimensiones y espaciado
8. **Theming**: Dejar que Flet maneje los colores con Material 3
9. **i18n**: Todos los textos deben ser traducibles con `t()`

## Contribuir

Ver `CLAUDE.md` y `PYTHON_BEST_PRACTICES.md` en la raíz del proyecto para guías detalladas.

## Licencia

© 2025 AK Group. Todos los derechos reservados.
