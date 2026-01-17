---
trigger: always_on
---

# Reglas Maestras: Pendulum (Python Date/Time)

Esta guía establece el estándar para el manejo de fechas y horas utilizando la librería `pendulum`. Estas reglas son universales y deben aplicarse en cualquier contexto de Python.

---

## 📅 Reglas de Oro

1.  **Pendulum First**: Uso obligatorio de `pendulum` para toda lógica de fechas.
2.  **UTC en el Core**: El backend "piensa", almacena y procesa SOLO en **UTC**.
    *   ✅ `pendulum.now("UTC")`
    *   ❌ `pendulum.now()` (Peligro: usa zona local del servidor)
3.  **Conversión Tardía**: La conversión a zona horaria local (Chile, Japón, etc.) se hace **solo en el último momento** (Interfaz de Usuario o Reporte).
4.  **Inyección de Tiempo**: El "Ahora" se inyecta via `TimeProvider`, nunca se llama globalmente en lógica de negocio.

---

## 🛠️ Guía de Uso (Best Practices)

### 1. Inyección de Tiempo (TimeProvider)

Para poder "cambiar la hora de la aplicación" (testing, simulación, o overriding), usamos un proveedor.

```python
# Contrato
class ITimeProvider(Protocol):
    def now(self) -> pendulum.DateTime: ...

# Lógica de Negocio
class DashboardService:
    def __init__(self, time_provider: ITimeProvider):
        self.time = time_provider

    def get_stats(self):
        # El servicio no sabe qué hora es realmente, confía en el provider
        current_time = self.time.now() 
```

### 2. Soporte Multi-País (Timezones)

Pendulum maneja zonas horarias de forma trivial.

```python
utc_now = pendulum.now("UTC")

# 🇨🇱 Chile
chile_time = utc_now.in_timezone("America/Santiago")

# 🇯🇵 Tokyo
tokyo_time = utc_now.in_timezone("Asia/Tokyo")

# 🇺🇸 New York
ny_time = utc_now.in_timezone("America/New_York")

print(f"En Chile son las: {chile_time.format('HH:mm')}")
```

### 3. Configuración Dinámica (Zona Horaria y Formato)

Si la aplicación debe soportar configuración por usuario/tenant:

**A. Zona Horaria**
El sistema guarda la preferencia del usuario (ej: `user.timezone = "Europe/Madrid"`).

**B. Formato de Fecha**
El sistema permite formatos personalizables (ej: `DD/MM/YYYY` vs `MM-DD-YYYY`).

```python
def format_for_display(
    dt_utc: pendulum.DateTime, 
    user_timezone: str,
    date_format: str = "DD/MM/YYYY HH:mm"
) -> str:
    """Convierte UTC a la zona horaria del usuario y aplica formato."""
    return dt_utc.in_timezone(user_timezone).format(date_format)
```

### 4. Aritmética "Timezone-Safe"

Pendulum maneja los cambios de horario (DST) automáticamente.

```python
# Pendulum sabe que en cierta fecha cambió la hora en Chile
dt = pendulum.datetime(2025, 4, 5, 23, 0, 0, tz="America/Santiago")
next_hour = dt.add(hours=2) # Ajusta correctamente si hubo cambio de hora
```

---

## 🧪 Testing (Configurando el Tiempo)

Gracias al patrón `TimeProvider`, podemos "configurar" la hora de la aplicación en los tests a voluntad:

```python
def test_new_year_greeting():
    # Configuramos la app para que crea que es Año Nuevo en Kiribati
    fake_time = pendulum.datetime(2026, 1, 1, 0, 0, 0, tz="Pacific/Kiritimati")
    provider = FakeTimeProvider(fake_time)
    
    service = GreetingService(provider)
    msg = service.get_greeting()
    
    assert msg == "¡Feliz Año Nuevo!"
```

---

## 🚫 Taller de Errores Comunes

| ❌ Error | ✅ Solución | Por qué |
|:---|:---|:---|
| `datetime.now()` | `time_provider.now()` | `datetime` es no-testeable y naive. |
| Guardar `2025-01-01 15:00` (sin tz) | Guardar UTC ISO8601 | Sin TZ, 15:00 no significa nada globalmente. |
| Asumir GMT-4 para Chile | Usar `America/Santiago` | Las reglas de horario de verano cambian políticamente. |
| `dt + timedelta(days=1)` | `dt.add(days=1)` | `timedelta` ignora reglas complejas de calendario. |
