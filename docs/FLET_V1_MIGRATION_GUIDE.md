# Guía de Migración: Flet v0.28.x → Flet v1 (v0.80.0)

Esta guía documenta todos los cambios necesarios para migrar aplicaciones Flet desde la versión 0.28.x a la versión 1 (v0.80.0).

---

## 📋 Checklist de Migración

- [ ] Actualizar dependencias en `pyproject.toml` o `requirements.txt`
- [ ] Reemplazar `ft.ElevatedButton` por `ft.Button`
- [ ] Actualizar métodos con sufijo `_async`
- [ ] Cambiar `ft.alignment.center` a `ft.Alignment(0, 0)`
- [ ] Actualizar `PopupMenuItem(text=...)` a `PopupMenuItem(content=ft.Text(...))`
- [ ] Cambiar `ft.Icon(name=...)` a `ft.Icon(...)`
- [ ] Mover operaciones de `_build()` a `did_mount()` si acceden a `self.page`
- [ ] Eliminar parámetro `text` de `FloatingActionButton`
- [ ] Cambiar `text` a `content` en `TextButton` y `Button`
- [ ] Eliminar `prefix_icon` de `TextField` y `Dropdown`
- [ ] Cambiar `on_change` de parámetro a propiedad
- [ ] Agregar manejo de `RuntimeError` en componentes personalizados
- [ ] Corregir uso de `datetime.min.time()` en Windows
- [ ] Ejecutar pruebas visuales y funcionales

---

## 🔧 Cambios Obligatorios

### 1. ⚠️ Swap de Button y ElevatedButton (CRÍTICO)

**El cambio más importante:** `Button` y `ElevatedButton` intercambiaron roles.

**Antes (v0.28):**
```python
ft.ElevatedButton(text="Guardar", on_click=handler)
```

**Ahora (v1):**
```python
ft.Button(text="Guardar", on_click=handler)
```

**Acción:** Buscar y reemplazar todas las instancias de `ft.ElevatedButton` por `ft.Button`.

```bash
# Buscar todas las instancias
grep -r "ft.ElevatedButton" .
```

---

### 2. Eliminación de sufijo `_async`

Todos los métodos con sufijo `_async` fueron removidos.

**Antes:**
```python
async def did_mount_async(self):
    await self.load_data()

await page.update_async()
await page.open_async(dialog)
```

**Ahora:**
```python
async def did_mount(self):
    await self.load_data()

await page.update()
await page.open(dialog)
```

**Métodos afectados:**
- `did_mount_async()` → `did_mount()`
- `update_async()` → `update()`
- `page.open_async()` → `page.open()`
- `page.close_async()` → `page.close()`

---

### 3. Cambios en Alignment API

La API de `alignment` cambió completamente.

**Antes:**
```python
ft.Container(
    alignment=ft.alignment.center,
    content=ft.Text("Centrado")
)
```

**Ahora:**
```python
ft.Container(
    alignment=ft.Alignment(0, 0),  # x, y donde (0,0) es el centro
    content=ft.Text("Centrado")
)
```

**Valores comunes:**
- `ft.alignment.center` → `ft.Alignment(0, 0)`
- `ft.alignment.top_left` → `ft.Alignment(-1, -1)`
- `ft.alignment.top_right` → `ft.Alignment(1, -1)`
- `ft.alignment.bottom_left` → `ft.Alignment(-1, 1)`
- `ft.alignment.bottom_right` → `ft.Alignment(1, 1)`

```bash
# Buscar todas las instancias
grep -r "ft.alignment\." .
```

---

### 4. Cambios en PopupMenuItem

El parámetro `text` cambió a `content` y ahora requiere un widget.

**Antes:**
```python
ft.PopupMenuItem(
    text="Mi opción",
    icon=ft.Icons.PERSON,
    on_click=handler
)
```

**Ahora:**
```python
ft.PopupMenuItem(
    content=ft.Text("Mi opción"),
    icon=ft.Icons.PERSON,
    on_click=handler
)
```

---

### 5. Cambios en Icon

El parámetro `name` cambió a ser el primer argumento posicional.

**Antes:**
```python
ft.Icon(name=ft.Icons.PERSON, size=24, color="blue")
```

**Ahora:**
```python
ft.Icon(ft.Icons.PERSON, size=24, color="blue")
```

```bash
# Buscar todas las instancias
grep -r "ft.Icon(name=" .
```

---

### 6. Cambios en Lifecycle (did_mount)

El acceso a `self.page` es más estricto y requiere que el control esté montado.

**Problema:** Operaciones en `_build()` que acceden a `self.page` fallarán.

**Solución:** Mover operaciones que requieren `self.page` de `_build()` a `did_mount()`.

**Antes:**
```python
def _build(self):
    self._load_data()  # Accede a self.page
    return ft.Column([...])
```

**Ahora:**
```python
def _build(self):
    return ft.Column([...])

async def did_mount(self):
    await self._load_data()  # Ahora aquí
```

---

### 7. Cambios en FloatingActionButton

El parámetro `text` fue removido.

**Antes:**
```python
ft.FloatingActionButton(
    icon=ft.Icons.ADD,
    text="Crear",
    on_click=handler
)
```

**Ahora:**
```python
ft.FloatingActionButton(
    icon=ft.Icons.ADD,
    on_click=handler
)
```

---

### 8. Cambios en TextButton y Button

Los parámetros `text` cambiaron a `content` que requiere un widget.

**Antes:**
```python
ft.TextButton(text="Cancelar", on_click=handler)
ft.Button(text="Guardar", on_click=handler)
```

**Ahora:**
```python
ft.TextButton(content=ft.Text("Cancelar"), on_click=handler)
ft.Button(content=ft.Text("Guardar"), on_click=handler)
```

**Nota:** Este cambio permite mayor flexibilidad (iconos, estilos personalizados, etc.).

```bash
# Buscar instancias de TextButton
grep -r "ft.TextButton(text=" .

# Buscar instancias de Button
grep -r "ft.Button(text=" .
```

---

### 9. Eliminación de prefix_icon

Los parámetros `prefix_icon` fueron removidos de `TextField` y `Dropdown`.

**Antes:**
```python
ft.TextField(
    label="Nombre",
    prefix_icon=ft.Icons.PERSON,
    on_change=handler
)
```

**Ahora:**
```python
# Opción 1: Sin icono
ft.TextField(
    label="Nombre"
)

# Opción 2: Usar suffix o prefix con Row
ft.Row([
    ft.Icon(ft.Icons.PERSON),
    ft.TextField(label="Nombre", expand=True)
])
```

---

### 10. Cambio en on_change

`on_change` ya no se pasa como parámetro del constructor, sino que se asigna como propiedad.

**Antes:**
```python
ft.TextField(
    label="Nombre",
    on_change=handler
)
```

**Ahora:**
```python
field = ft.TextField(label="Nombre")
field.on_change = handler
```

**Aplica a:**
- `TextField`
- `Dropdown`
- `Checkbox`
- `Switch`
- `Slider`

---

### 11. Manejo de RuntimeError en componentes personalizados

Los componentes que acceden a `self.page` antes de estar montados lanzan `RuntimeError`.

**Solución:** Agregar try/except en todos los métodos que acceden a `self.page`.

**Antes:**
```python
def set_value(self, value):
    self.control.value = value
    self.page.update()
```

**Ahora:**
```python
def set_value(self, value):
    self.control.value = value
    try:
        self.page.update()
    except RuntimeError:
        pass  # Control no montado aún
```

**Métodos comunes que requieren protección:**
- `set_value()`
- `set_error()`
- `clear_error()`
- `set_enabled()`
- `set_options()`
- `clear()`

---

### 12. Error de timezone en datetime (Windows)

Usar `datetime.min.time()` con `datetime.combine()` causa error en Windows al serializar con msgpack.

**Problema:**
```python
from datetime import datetime, date

# Causa OSError en Windows
date_value = datetime.combine(date.today(), datetime.min.time())
```

**Solución:**
```python
from datetime import datetime, date, time

# Usar mediodía en lugar de medianoche
date_value = datetime.combine(date.today(), time(12, 0))
```

---

## 🔄 Cambios Opcionales (Deprecados pero funcionales)

### 13. Colors con shades

**Antes:**
```python
Colors.BLACK12
Colors.WHITE10
```

**Ahora:**
```python
BLACK_12
WHITE_10
```

---

### 14. ConstrainedControl → LayoutControl

**Antes:**
```python
from flet import ConstrainedControl

class MyControl(ConstrainedControl):
    pass
```

**Ahora:**
```python
from flet import LayoutControl

class MyControl(LayoutControl):
    pass
```

---

### 15. copy_with → copy

**Antes:**
```python
new_style = old_style.copy_with(color="blue")
```

**Ahora:**
```python
new_style = old_style.copy(color="blue")
```

---

## 📦 Actualización de Dependencias

### Poetry

```toml
# pyproject.toml
[tool.poetry.dependencies]
python = ">=3.8"
flet = "^0.80.0"
httpx = "^0.28.1"  # Requerido por Flet v1
msgpack = "^1.1.2"  # Nueva dependencia
```

```bash
poetry update flet httpx
poetry add msgpack
```

### pip

```txt
# requirements.txt
flet>=0.80.0
httpx>=0.28.1
msgpack>=1.1.2
```

```bash
pip install --upgrade flet httpx msgpack
```

---

## 🔍 Comandos de Búsqueda

```bash
# 1. Buscar ElevatedButton
grep -r "ft.ElevatedButton" . --include="*.py"

# 2. Buscar métodos _async
grep -r "did_mount_async\|update_async\|open_async\|close_async" . --include="*.py"

# 3. Buscar alignment
grep -r "ft.alignment\." . --include="*.py"

# 4. Buscar PopupMenuItem con text
grep -r "PopupMenuItem.*text=" . --include="*.py"

# 5. Buscar Icon con name
grep -r "ft.Icon(name=" . --include="*.py"

# 6. Buscar FloatingActionButton con text
grep -r "FloatingActionButton.*text=" . --include="*.py"

# 7. Buscar TextButton con text
grep -r "ft.TextButton(text=" . --include="*.py"

# 8. Buscar Button con text
grep -r "ft.Button(text=" . --include="*.py"

# 9. Buscar prefix_icon
grep -r "prefix_icon=" . --include="*.py"

# 10. Buscar datetime.min.time()
grep -r "datetime.min.time()" . --include="*.py"
```

---

## ✅ Verificación Post-Migración

### 1. Verificar instalación
```bash
# Poetry
poetry show flet
poetry show httpx

# pip
pip show flet
pip show httpx
```

### 2. Ejecutar la aplicación
```bash
python main.py  # o tu punto de entrada
```

### 3. Pruebas visuales
- [ ] Verificar que los botones se vean correctamente
- [ ] Confirmar que los eventos `on_click` funcionen
- [ ] Validar que los formularios se comporten igual
- [ ] Revisar alineaciones y layouts
- [ ] Probar menús contextuales y popups

### 4. Pruebas funcionales
- [ ] Ejecutar suite de tests (si existe)
- [ ] Probar flujos críticos de usuario
- [ ] Validar operaciones CRUD
- [ ] Verificar navegación entre vistas

---

## 🆕 Nuevas Características en Flet v1

Aprovecha estas nuevas funcionalidades:

1. **Testing Framework:** Framework de pruebas integrado
2. **Canvas.capture():** Captura de canvas
3. **DataTable.on_select_change:** Evento de selección en DataTable
4. **DateRangePicker:** Selector de rango de fechas
5. **ContextMenu:** Menú contextual nativo
6. **RadioGroup nativo:** Migrado al widget nativo de Flutter
7. **page.get_device_info():** Información del dispositivo
8. **RadarChart:** Nuevo tipo de gráfico

---

## 🐛 Problemas Comunes

### Error: "RuntimeError: Control must be added to the page first"

**Causa:** Acceso a `self.page` antes de que el control esté montado.

**Solución:** Mover código a `did_mount()` o agregar try/except.

### Error: "OSError: [Errno 22] Invalid argument"

**Causa:** Uso de `datetime.min.time()` en Windows.

**Solución:** Usar `time(12, 0)` en lugar de `datetime.min.time()`.

### Error: "TypeError: 'text' is an invalid keyword argument"

**Causa:** Uso de `text` en lugar de `content` en botones.

**Solución:** Cambiar `text="..."` a `content=ft.Text("...")`.

### Botones no se ven (invisibles)

**Causa:** Uso de `ft.ElevatedButton` sin actualizar a `ft.Button`.

**Solución:** Reemplazar todas las instancias de `ft.ElevatedButton`.

---

## 📚 Recursos

- [Flet v0.80.0 Release Notes](https://github.com/flet-dev/flet/releases/tag/v0.80.0)
- [Flet Documentation](https://docs.flet.dev/)
- [Flet GitHub Repository](https://github.com/flet-dev/flet)
- [Flet Discord Community](https://discord.gg/dzWXP8SHG8)

---

## 📝 Notas Finales

- La migración es **no destructiva** - solo actualiza nombres de componentes
- No se requieren cambios en la lógica de negocio
- La estructura del proyecto permanece igual
- Todos los cambios son **backward compatible** en términos de funcionalidad
- **Tiempo estimado:** 2-4 horas para proyectos medianos (dependiendo del tamaño)

---

**Última actualización:** Enero 2026  
**Versión de esta guía:** 1.0
