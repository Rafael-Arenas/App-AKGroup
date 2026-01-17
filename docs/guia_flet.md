# 📚 Guía Completa de Flet - AK Group Frontend

Esta guía documenta todos los elementos y patrones de Flet utilizados en el frontend de AK Group, sirviendo como referencia para desarrolladores.

---

## 📖 Tabla de Contenidos

1. [Introducción a Flet](#introducción-a-flet)
2. [Configuración Inicial](#configuración-inicial)
3. [Controles de Layout](#controles-de-layout)
4. [Controles de Entrada](#controles-de-entrada)
5. [Controles de Navegación](#controles-de-navegación)
6. [Controles de Visualización](#controles-de-visualización)
7. [Diálogos y Overlays](#diálogos-y-overlays)
8. [Animaciones](#animaciones)
9. [Ciclo de Vida de Componentes](#ciclo-de-vida-de-componentes)
10. [Patrones y Mejores Prácticas](#patrones-y-mejores-prácticas)
11. [Componentes Personalizados](#componentes-personalizados)

---

## Introducción a Flet

Flet es un framework que permite crear aplicaciones multiplataforma (web, desktop, mobile) usando Python. Utiliza Flutter como motor de renderizado.

### Características Principales:
- **Material Design 3**: Soporte nativo para el sistema de diseño de Google
- **Multiplataforma**: Una sola base de código para web, desktop y mobile
- **Hot Reload**: Desarrollo rápido con recarga en caliente
- **Componentes Reactivos**: UI se actualiza automáticamente con cambios de estado

---

## Configuración Inicial

### Estructura Básica de una Aplicación

```python
import flet as ft

def main(page: ft.Page) -> None:
    """Función principal que inicializa la aplicación Flet."""
    
    # Configuración de la página
    page.title = "Mi Aplicación"
    page.padding = 0
    page.spacing = 0
    page.theme_mode = ft.ThemeMode.LIGHT  # o DARK, SYSTEM
    
    # Configurar tema con Material 3
    page.theme = ft.Theme(
        use_material3=True,
    )
    
    # Configurar tema oscuro
    page.dark_theme = ft.Theme(
        use_material3=True,
    )
    
    # Agregar contenido
    page.add(ft.Text("¡Hola, Flet!"))
    
    # Actualizar la página
    page.update()

if __name__ == "__main__":
    ft.app(target=main)
```

### Propiedades Importantes de `ft.Page`

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `title` | `str` | Título de la ventana |
| `padding` | `int \| Padding` | Padding interno de la página |
| `spacing` | `int` | Espaciado entre controles |
| `theme_mode` | `ThemeMode` | Modo de tema (LIGHT, DARK, SYSTEM) |
| `theme` | `Theme` | Configuración del tema claro |
| `dark_theme` | `Theme` | Configuración del tema oscuro |
| `dialog` | `AlertDialog` | Diálogo activo de la página |

---

## Controles de Layout

### `ft.Container`

Contenedor principal que envuelve otros controles con propiedades de estilo.

```python
container = ft.Container(
    content=ft.Text("Contenido"),
    width=200,
    height=100,
    padding=16,                              # Padding interno
    margin=ft.margin.only(top=10),           # Margen externo
    bgcolor=ft.Colors.SURFACE,               # Color de fondo
    border=ft.border.all(1, ft.Colors.OUTLINE),  # Borde
    border_radius=ft.border_radius.all(12),  # Bordes redondeados
    alignment=ft.Alignment(0, 0),            # Alineación del contenido (centro)
    expand=True,                             # Expandir para llenar espacio
    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,  # Recorte con antialiasing
    animate=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),  # Animación
    on_click=lambda e: print("Click!"),      # Evento de click
    ink=True,                                # Efecto ripple
)
```

### Propiedades de Container

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `content` | `Control` | Control hijo |
| `width` / `height` | `int \| float` | Dimensiones |
| `padding` | `int \| Padding` | Padding interno |
| `margin` | `int \| Margin` | Margen externo |
| `bgcolor` | `str \| Colors` | Color de fondo |
| `border` | `Border` | Configuración de borde |
| `border_radius` | `BorderRadius` | Radio de esquinas |
| `alignment` | `Alignment` | Alineación del contenido |
| `expand` | `bool \| int` | Expandir para llenar espacio |
| `animate` | `Animation` | Animación de cambios |
| `ink` | `bool` | Efecto ripple al hacer click |

---

### `ft.Row`

Organiza controles horizontalmente.

```python
row = ft.Row(
    controls=[
        ft.Text("Item 1"),
        ft.Text("Item 2"),
        ft.Container(expand=True),  # Spacer
        ft.Text("Item 3"),
    ],
    alignment=ft.MainAxisAlignment.START,     # Alineación horizontal
    vertical_alignment=ft.CrossAxisAlignment.CENTER,  # Alineación vertical
    spacing=16,                               # Espacio entre controles
    wrap=True,                                # Permitir wrap
    scroll=ft.ScrollMode.AUTO,                # Scroll horizontal
    expand=True,                              # Expandir
)
```

### Propiedades de Row

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `controls` | `list[Control]` | Lista de controles hijos |
| `alignment` | `MainAxisAlignment` | Alineación en eje principal (horizontal) |
| `vertical_alignment` | `CrossAxisAlignment` | Alineación en eje cruzado (vertical) |
| `spacing` | `int` | Espacio entre controles |
| `wrap` | `bool` | Permitir que controles pasen a siguiente línea |
| `scroll` | `ScrollMode` | Tipo de scroll |

### Valores de `MainAxisAlignment`

- `START`: Al inicio
- `END`: Al final
- `CENTER`: Centrado
- `SPACE_BETWEEN`: Espacio entre elementos
- `SPACE_AROUND`: Espacio alrededor de elementos
- `SPACE_EVENLY`: Espacio uniforme

---

### `ft.Column`

Organiza controles verticalmente.

```python
column = ft.Column(
    controls=[
        ft.Text("Header"),
        ft.Divider(),
        ft.Text("Contenido"),
        ft.Container(height=20),  # Spacer
        ft.Text("Footer"),
    ],
    horizontal_alignment=ft.CrossAxisAlignment.CENTER,  # Alineación horizontal
    alignment=ft.MainAxisAlignment.START,               # Alineación vertical
    spacing=8,                                          # Espacio entre controles
    scroll=ft.ScrollMode.AUTO,                          # Scroll vertical
    expand=True,                                        # Expandir
    tight=True,                                         # Ajustar al contenido
)
```

---

### `ft.Card`

Tarjeta con elevación y bordes redondeados.

```python
card = ft.Card(
    content=ft.Container(
        content=ft.Column([
            ft.Text("Título", weight=ft.FontWeight.BOLD),
            ft.Text("Descripción del contenido"),
        ]),
        padding=16,
    ),
    elevation=4,                    # Sombra
)
```

---

### `ft.Divider`

Línea divisora horizontal.

```python
divider = ft.Divider(
    height=1,        # Altura total incluyendo espaciado
    thickness=1,     # Grosor de la línea
    color=ft.Colors.OUTLINE,
)
```

---

## Controles de Entrada

### `ft.TextField`

Campo de texto con múltiples opciones.

```python
text_field = ft.TextField(
    label="Email",                           # Etiqueta
    hint_text="Ingresa tu email",           # Placeholder
    value="",                               # Valor inicial
    password=False,                         # Modo password
    can_reveal_password=True,               # Botón para revelar password
    multiline=False,                        # Múltiples líneas
    min_lines=1,                            # Líneas mínimas
    max_lines=5,                            # Líneas máximas
    max_length=100,                         # Longitud máxima
    prefix_icon=ft.Icons.EMAIL,             # Ícono al inicio
    suffix_icon=ft.Icons.CLEAR,             # Ícono al final
    border=ft.InputBorder.OUTLINE,          # Tipo de borde
    read_only=False,                        # Solo lectura
    disabled=False,                         # Deshabilitado
    autofocus=True,                         # Auto enfoque
    on_change=lambda e: print(e.control.value),  # Evento cambio
    on_submit=lambda e: print("Enter pressed"),  # Evento submit
)
```

### Tipos de Borde (`InputBorder`)

- `OUTLINE`: Borde completo alrededor
- `UNDERLINE`: Solo línea inferior
- `NONE`: Sin borde

---

### `ft.Dropdown`

Selector desplegable.

```python
dropdown = ft.Dropdown(
    label="País",
    hint_text="Selecciona un país",
    value="chile",                          # Valor seleccionado
    options=[
        ft.dropdown.Option(key="chile", text="Chile"),
        ft.dropdown.Option(key="argentina", text="Argentina"),
        ft.dropdown.Option(key="peru", text="Perú"),
    ],
    expand=True,                           # Expandir ancho
    on_change=lambda e: print(e.control.value),
)
```

---

### `ft.Checkbox`

Casilla de verificación.

```python
checkbox = ft.Checkbox(
    label="Acepto los términos",
    value=False,                           # Estado inicial
    on_change=lambda e: print(e.control.value),
)
```

---

### `ft.DatePicker`

Selector de fecha.

```python
from datetime import datetime

date_picker = ft.DatePicker(
    value=datetime.now(),                  # Fecha inicial
    first_date=datetime(1970, 1, 1),       # Fecha mínima
    last_date=datetime(2100, 12, 31),      # Fecha máxima
    on_change=lambda e: print(e.control.value),
    on_dismiss=lambda e: print("Cerrado"),
)

# Para mostrar el picker:
# date_picker.pick_date()
```

---

## Controles de Navegación

### `ft.IconButton`

Botón con ícono.

```python
icon_button = ft.IconButton(
    icon=ft.Icons.MENU,
    icon_size=24,
    tooltip="Menú",
    on_click=lambda e: print("Click"),
    disabled=False,
)
```

---

### `ft.Button` (ElevatedButton)

Botón elevado estándar.

```python
button = ft.Button(
    content=ft.Text("Guardar"),
    icon=ft.Icons.SAVE,
    on_click=lambda e: print("Guardado"),
    disabled=False,
)
```

---

### `ft.TextButton`

Botón de texto sin elevación.

```python
text_button = ft.TextButton(
    content=ft.Text("Cancelar"),
    icon=ft.Icons.CANCEL,
    on_click=lambda e: print("Cancelado"),
    style=ft.ButtonStyle(
        padding=ft.padding.symmetric(horizontal=16, vertical=8),
    ),
)
```

---

### `ft.PopupMenuButton`

Menú desplegable popup.

```python
popup_menu = ft.PopupMenuButton(
    icon=ft.Icons.MORE_VERT,
    tooltip="Más opciones",
    items=[
        ft.PopupMenuItem(
            content=ft.Row([
                ft.Icon(ft.Icons.EDIT, size=18),
                ft.Container(width=8),
                ft.Text("Editar"),
            ]),
            on_click=lambda e: print("Editar"),
        ),
        ft.PopupMenuItem(),  # Separador
        ft.PopupMenuItem(
            content=ft.Row([
                ft.Icon(ft.Icons.DELETE, size=18),
                ft.Container(width=8),
                ft.Text("Eliminar"),
            ]),
            on_click=lambda e: print("Eliminar"),
        ),
    ],
)
```

---

## Controles de Visualización

### `ft.Text`

Control de texto con estilos.

```python
text = ft.Text(
    "Título Principal",
    size=24,                               # Tamaño de fuente
    weight=ft.FontWeight.BOLD,             # Peso de fuente
    color=ft.Colors.ON_SURFACE,            # Color
    text_align=ft.TextAlign.CENTER,        # Alineación
    selectable=True,                       # Permitir selección
    max_lines=2,                           # Líneas máximas
    overflow=ft.TextOverflow.ELLIPSIS,     # Manejo de overflow
)
```

### Valores de `FontWeight`

- `W_100` a `W_900`: Pesos numéricos
- `BOLD`: Negrita (W_700)
- `NORMAL`: Normal (W_400)

---

### `ft.Icon`

Ícono de Material Design.

```python
icon = ft.Icon(
    ft.Icons.HOME,
    size=24,
    color=ft.Colors.PRIMARY,
)
```

### Íconos Comunes Utilizados

| Ícono | Uso |
|-------|-----|
| `ft.Icons.HOME` | Inicio |
| `ft.Icons.PEOPLE` | Usuarios/Clientes |
| `ft.Icons.LOCAL_SHIPPING` | Envíos/Proveedores |
| `ft.Icons.INVENTORY_2` | Inventario/Productos |
| `ft.Icons.SHOPPING_CART` | Carrito/Pedidos |
| `ft.Icons.DESCRIPTION` | Documentos/Cotizaciones |
| `ft.Icons.EDIT` | Editar |
| `ft.Icons.DELETE` | Eliminar |
| `ft.Icons.ADD` | Agregar |
| `ft.Icons.SEARCH` | Buscar |
| `ft.Icons.FILTER_LIST` | Filtros |
| `ft.Icons.CHEVRON_LEFT` / `RIGHT` | Navegación |
| `ft.Icons.TRENDING_UP` / `DOWN` / `FLAT` | Tendencias |
| `ft.Icons.LIGHT_MODE` / `DARK_MODE` | Tema |
| `ft.Icons.MENU` / `MENU_OPEN` | Menú |
| `ft.Icons.CHECK` | Confirmación |
| `ft.Icons.CLEAR` | Limpiar |
| `ft.Icons.HISTORY` | Historial |

---

### `ft.ProgressRing`

Indicador de carga circular.

```python
progress = ft.ProgressRing(
    width=40,
    height=40,
    stroke_width=4,
    color=ft.Colors.PRIMARY,
)
```

---

### `ft.ListTile`

Elemento de lista con ícono, título y subtítulo.

```python
list_tile = ft.ListTile(
    leading=ft.Icon(ft.Icons.PERSON),
    title=ft.Text("Juan Pérez"),
    subtitle=ft.Text("juan@email.com"),
    trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT),
    on_click=lambda e: print("Click"),
)
```

---

## Diálogos y Overlays

### `ft.AlertDialog`

Diálogo modal con título, contenido y acciones.

```python
dialog = ft.AlertDialog(
    modal=True,                            # Modal (bloquear fondo)
    title=ft.Row([
        ft.Icon(ft.Icons.WARNING, size=32),
        ft.Text("Confirmar Acción", size=20, weight=ft.FontWeight.W_600),
    ]),
    content=ft.Text("¿Estás seguro de realizar esta acción?"),
    actions=[
        ft.TextButton(
            content=ft.Text("Cancelar"),
            on_click=lambda e: close_dialog(e),
        ),
        ft.Button(
            content=ft.Text("Confirmar"),
            on_click=lambda e: confirm_action(e),
        ),
    ],
    actions_alignment=ft.MainAxisAlignment.END,
)

# Para mostrar:
def show_dialog(page):
    page.dialog = dialog
    dialog.open = True
    page.update()

# Para cerrar:
def close_dialog(e):
    dialog.open = False
    e.page.update()
```

---

### `ft.SnackBar`

Notificación temporal en la parte inferior.

```python
snackbar = ft.SnackBar(
    content=ft.Text("Operación completada"),
    action="Deshacer",
    on_action=lambda e: print("Deshacer"),
)

# Para mostrar:
page.snack_bar = snackbar
snackbar.open = True
page.update()
```

---

## Animaciones

### `ft.Animation`

Configuración de animación para transiciones.

```python
from src.frontend.layout_constants import LayoutConstants

# Crear animación
animation = ft.Animation(
    duration=300,                          # Duración en ms
    curve=ft.AnimationCurve.EASE_IN_OUT,   # Curva de animación
)

# Usar en Container
container = ft.Container(
    content=ft.Text("Contenido"),
    width=100,
    animate=animation,  # Animar cambios de propiedades
)

# Helper method de LayoutConstants
animation = LayoutConstants.get_animation(
    duration=300,
    curve=ft.AnimationCurve.EASE_IN_OUT
)
```

### Curvas de Animación Disponibles

| Curva | Descripción |
|-------|-------------|
| `EASE_IN_OUT` | Suave al inicio y final |
| `EASE_IN` | Suave al inicio, rápido al final |
| `EASE_OUT` | Rápido al inicio, suave al final |
| `LINEAR` | Velocidad constante |
| `BOUNCE_IN` / `BOUNCE_OUT` | Efecto rebote |

---

## Ciclo de Vida de Componentes

### Métodos del Ciclo de Vida

Flet proporciona métodos de ciclo de vida para controles personalizados:

```python
class MiComponente(ft.Container):
    def __init__(self):
        super().__init__()
        self.content = self._build()
    
    def _build(self) -> ft.Control:
        """Construye el contenido del componente."""
        return ft.Text("Mi Componente")
    
    def did_mount(self) -> None:
        """
        Se ejecuta cuando el componente se monta en la página.
        Ideal para:
        - Suscribirse a observers
        - Cargar datos iniciales
        - Iniciar tareas asíncronas
        """
        app_state.theme.add_observer(self._on_theme_changed)
        if self.page:
            self.page.run_task(self._load_data)
    
    def will_unmount(self) -> None:
        """
        Se ejecuta cuando el componente se desmonta.
        Ideal para:
        - Remover observers para evitar memory leaks
        - Cancelar tareas pendientes
        - Limpiar recursos
        """
        app_state.theme.remove_observer(self._on_theme_changed)
    
    async def _load_data(self) -> None:
        """Carga datos de forma asíncrona."""
        # Cargar datos...
        self.content = self._build()
        if self.page:
            self.update()
    
    def _on_theme_changed(self) -> None:
        """Callback cuando cambia el tema."""
        if self.page:
            self.update()
```

---

## Patrones y Mejores Prácticas

### 1. Patrón Observer para Estado

```python
class AppState:
    """Estado global de la aplicación."""
    
    def __init__(self):
        self._observers: list[Callable] = []
        self._value = None
    
    def add_observer(self, callback: Callable) -> None:
        """Suscribe un observer."""
        if callback not in self._observers:
            self._observers.append(callback)
    
    def remove_observer(self, callback: Callable) -> None:
        """Remueve un observer."""
        if callback in self._observers:
            self._observers.remove(callback)
    
    def _notify_observers(self) -> None:
        """Notifica a todos los observers."""
        for observer in self._observers:
            try:
                observer()
            except Exception as e:
                logger.error(f"Error notifying observer: {e}")
    
    def set_value(self, value) -> None:
        """Actualiza el valor y notifica."""
        self._value = value
        self._notify_observers()
```

### 2. Componentes Reutilizables

```python
class ValidatedTextField(ft.Container):
    """Campo de texto con validación integrada."""
    
    def __init__(
        self,
        label: str,
        required: bool = False,
        validators: list[str] | None = None,
    ):
        super().__init__()
        self.label = label
        self.required = required
        self.validators = validators or []
        
        # Crear controles internos
        self._text_field = ft.TextField(label=label)
        self._error_text = ft.Text("", visible=False)
        
        self.content = ft.Column([
            self._text_field,
            self._error_text,
        ])
    
    def validate(self) -> bool:
        """Valida el campo."""
        value = self.get_value()
        if self.required and not value:
            self.set_error("Este campo es requerido")
            return False
        return True
    
    def get_value(self) -> str:
        return self._text_field.value or ""
    
    def set_error(self, message: str) -> None:
        self._error_text.value = message
        self._error_text.visible = True
        if self.page:
            self.update()
```

### 3. Manejo de Errores en Callbacks

```python
def _handle_click(self, e: ft.ControlEvent) -> None:
    """Maneja click con manejo de errores."""
    try:
        if self.on_click:
            self.on_click(e)
    except Exception as ex:
        logger.error(f"Error in click handler: {ex}")
```

### 4. Actualización Segura de UI

```python
def _update_ui(self) -> None:
    """Actualiza la UI de forma segura."""
    try:
        if self.page:
            self.update()
    except RuntimeError:
        # El control aún no está montado
        pass
```

### 5. Uso de Constantes

```python
from src.frontend.layout_constants import LayoutConstants

# Usar constantes en lugar de valores mágicos
container = ft.Container(
    padding=LayoutConstants.PADDING_MD,      # 16
    margin=LayoutConstants.SPACING_SM,       # 8
    border_radius=LayoutConstants.RADIUS_MD, # 12
)

text = ft.Text(
    "Título",
    size=LayoutConstants.FONT_SIZE_XL,       # 20
    weight=LayoutConstants.FONT_WEIGHT_BOLD, # W_700
)
```

---

## Componentes Personalizados

### Componentes Disponibles en el Proyecto

#### Componentes Comunes (`components/common/`)

| Componente | Descripción |
|------------|-------------|
| `DataTable` | Tabla de datos con ordenamiento, paginación y acciones |
| `EmptyState` | Estado vacío con ícono, mensaje y acción |
| `ErrorDisplay` | Visualización de errores con retry |
| `LoadingSpinner` | Indicador de carga con mensaje |
| `SearchBar` | Barra de búsqueda con debouncing e historial |
| `FilterPanel` | Panel colapsable con filtros configurables |
| `ConfirmDialog` | Diálogo de confirmación con variantes |
| `BaseCard` | Tarjeta base reutilizable |

#### Componentes de Formulario (`components/forms/`)

| Componente | Descripción |
|------------|-------------|
| `ValidatedTextField` | Campo de texto con validación |
| `DropdownField` | Dropdown con validación |
| `DatePickerField` | Selector de fecha con validación |
| `AddressFormDialog` | Formulario de dirección en diálogo |
| `ContactFormDialog` | Formulario de contacto en diálogo |

#### Componentes de Navegación (`components/navigation/`)

| Componente | Descripción |
|------------|-------------|
| `CustomAppBar` | Barra superior con logo, título, tema e idioma |
| `CustomNavigationRail` | Navegación lateral expandible |
| `Breadcrumb` | Navegación de migas de pan |
| `LanguageSelector` | Selector de idioma |
| `NotificationBadge` | Badge de notificaciones |
| `UserProfileMenu` | Menú de perfil de usuario |

#### Componentes de Gráficos (`components/charts/`)

| Componente | Descripción |
|------------|-------------|
| `KPICard` | Tarjeta de KPI con valor, cambio y tendencia |

---

### Ejemplo: Crear un Componente Personalizado

```python
from typing import Callable
import flet as ft
from loguru import logger

from src.frontend.layout_constants import LayoutConstants
from src.frontend.app_state import app_state


class MiCard(ft.Container):
    """
    Tarjeta personalizada con título, contenido y acciones.
    
    Args:
        title: Título de la tarjeta
        content: Contenido principal
        on_action: Callback para acción principal
    
    Example:
        >>> card = MiCard(
        ...     title="Mi Tarjeta",
        ...     content=ft.Text("Contenido"),
        ...     on_action=lambda: print("Acción!")
        ... )
    """
    
    def __init__(
        self,
        title: str,
        content: ft.Control,
        on_action: Callable[[], None] | None = None,
    ):
        super().__init__()
        
        self.title = title
        self._content = content
        self.on_action = on_action
        
        # Suscribirse a cambios de tema
        app_state.theme.add_observer(self._on_theme_changed)
        
        # Construir contenido
        self.content = self._build()
    
    def _build(self) -> ft.Control:
        """Construye el componente."""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    # Header
                    ft.Row([
                        ft.Text(
                            self.title,
                            size=LayoutConstants.FONT_SIZE_XL,
                            weight=LayoutConstants.FONT_WEIGHT_BOLD,
                        ),
                        ft.Container(expand=True),
                        ft.IconButton(
                            icon=ft.Icons.MORE_VERT,
                            on_click=self._handle_action,
                        ),
                    ]),
                    ft.Divider(),
                    # Content
                    self._content,
                ]),
                padding=LayoutConstants.PADDING_LG,
            ),
            elevation=LayoutConstants.ELEVATION_LOW,
        )
    
    def _handle_action(self, e: ft.ControlEvent) -> None:
        """Maneja la acción."""
        if self.on_action:
            try:
                self.on_action()
            except Exception as ex:
                logger.error(f"Error in action: {ex}")
    
    def _on_theme_changed(self) -> None:
        """Callback cuando cambia el tema."""
        self.content = self._build()
        if self.page:
            self.update()
    
    def will_unmount(self) -> None:
        """Limpieza al desmontar."""
        app_state.theme.remove_observer(self._on_theme_changed)
```

---

## Constantes de Layout

El proyecto utiliza constantes centralizadas en `LayoutConstants`:

### Espaciado

| Constante | Valor | Uso |
|-----------|-------|-----|
| `SPACING_NONE` | 0 | Sin espaciado |
| `SPACING_XXS` | 2 | Micro espaciado |
| `SPACING_XS` | 4 | Extra pequeño |
| `SPACING_SM` | 8 | Pequeño |
| `SPACING_MD` | 16 | Mediano (default) |
| `SPACING_LG` | 24 | Grande |
| `SPACING_XL` | 32 | Extra grande |
| `SPACING_XXL` | 48 | Máximo |

### Padding

| Constante | Valor |
|-----------|-------|
| `PADDING_XS` | 4 |
| `PADDING_SM` | 8 |
| `PADDING_MD` | 16 |
| `PADDING_LG` | 24 |
| `PADDING_XL` | 32 |

### Border Radius

| Constante | Valor |
|-----------|-------|
| `RADIUS_XS` | 4 |
| `RADIUS_SM` | 8 |
| `RADIUS_MD` | 12 |
| `RADIUS_LG` | 16 |
| `RADIUS_XL` | 24 |
| `RADIUS_FULL` | 9999 |

### Tamaños de Fuente

| Constante | Valor |
|-----------|-------|
| `FONT_SIZE_XS` | 10 |
| `FONT_SIZE_SM` | 12 |
| `FONT_SIZE_MD` | 14 |
| `FONT_SIZE_LG` | 16 |
| `FONT_SIZE_XL` | 20 |
| `FONT_SIZE_XXL` | 24 |
| `FONT_SIZE_DISPLAY_SM` | 32 |
| `FONT_SIZE_DISPLAY_MD` | 40 |

### Tamaños de Ícono

| Constante | Valor |
|-----------|-------|
| `ICON_SIZE_SM` | 16 |
| `ICON_SIZE_MD` | 24 |
| `ICON_SIZE_LG` | 32 |
| `ICON_SIZE_XL` | 48 |

---

## Recursos Adicionales

- [Documentación Oficial de Flet](https://flet.dev/docs/)
- [Galería de Controles](https://flet.dev/docs/controls)
- [Tutorial Oficial](https://flet.dev/docs/tutorials)
- [Ejemplos en GitHub](https://github.com/flet-dev/examples)

---

*Documento generado para AK Group Frontend - Enero 2026*
