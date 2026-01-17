"""
Constantes compartidas entre frontend y backend.

Este módulo define constantes de negocio que son utilizadas tanto por el frontend
como por el backend, garantizando consistencia en toda la aplicación.
"""

# ============================================================================
# TIPOS DE PRODUCTO
# ============================================================================

PRODUCT_TYPE_ARTICLE = "article"
PRODUCT_TYPE_NOMENCLATURE = "nomenclature"
PRODUCT_TYPE_SERVICE = "service"

# ============================================================================
# TIPOS DE DIRECCIÓN
# ============================================================================

ADDRESS_TYPE_DELIVERY = "delivery"
ADDRESS_TYPE_BILLING = "billing"
ADDRESS_TYPE_HEADQUARTERS = "headquarters"
ADDRESS_TYPE_PLANT = "plant"

# ============================================================================
# TIPOS DE EMPRESA
# ============================================================================

COMPANY_TYPE_CUSTOMER = "customer"
COMPANY_TYPE_SUPPLIER = "supplier"
COMPANY_TYPE_BOTH = "both"

# ============================================================================
# PRIORIDADES DE NOTAS
# ============================================================================

NOTE_PRIORITY_LOW = "low"
NOTE_PRIORITY_NORMAL = "normal"
NOTE_PRIORITY_HIGH = "high"
NOTE_PRIORITY_URGENT = "urgent"

# ============================================================================
# ESTADOS DE COTIZACIÓN
# ============================================================================

QUOTE_STATUS_DRAFT = "draft"
QUOTE_STATUS_SENT = "sent"
QUOTE_STATUS_ACCEPTED = "accepted"
QUOTE_STATUS_REJECTED = "rejected"
QUOTE_STATUS_EXPIRED = "expired"

# ============================================================================
# ESTADOS DE ORDEN
# ============================================================================

ORDER_STATUS_PENDING = "pending"
ORDER_STATUS_CONFIRMED = "confirmed"
ORDER_STATUS_IN_PRODUCTION = "in_production"
ORDER_STATUS_READY = "ready"
ORDER_STATUS_SHIPPED = "shipped"
ORDER_STATUS_DELIVERED = "delivered"
ORDER_STATUS_CANCELLED = "cancelled"

# ============================================================================
# ESTADOS DE PAGO
# ============================================================================

PAYMENT_STATUS_PENDING = "pending"
PAYMENT_STATUS_PARTIAL = "partial"
PAYMENT_STATUS_PAID = "paid"
PAYMENT_STATUS_OVERDUE = "overdue"

# ============================================================================
# ESTADOS DE ENTREGA
# ============================================================================

DELIVERY_STATUS_PENDING = "pending"
DELIVERY_STATUS_IN_TRANSIT = "in_transit"
DELIVERY_STATUS_DELIVERED = "delivered"
DELIVERY_STATUS_CANCELLED = "cancelled"

# ============================================================================
# TIPOS DE TRANSPORTE
# ============================================================================

TRANSPORT_TYPE_OWN = "own"
TRANSPORT_TYPE_CARRIER = "carrier"
TRANSPORT_TYPE_COURIER = "courier"
TRANSPORT_TYPE_FREIGHT_FORWARDER = "freight_forwarder"

# ============================================================================
# MONEDAS Y FORMATOS
# ============================================================================

DEFAULT_CURRENCY = "CLP"
SUPPORTED_CURRENCIES = ["CLP", "USD", "EUR"]
DEFAULT_TAX_RATE = 19.0  # IVA Chile

# ============================================================================
# PAGINACIÓN
# ============================================================================

DEFAULT_PAGINATION_LIMIT = 100
MAX_PAGINATION_LIMIT = 1000

# ============================================================================
# LÍMITES Y VALIDACIONES
# ============================================================================

MIN_PASSWORD_LENGTH = 8
MAX_DISCOUNT_PERCENTAGE = 50.0
MIN_PRODUCT_QUANTITY = 0.001
MAX_PRODUCT_QUANTITY = 999999.999

# ============================================================================
# FORMATOS
# ============================================================================

DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
RUT_REGEX = r'^\d{1,8}-[\dkK]$'
PHONE_REGEX = r'^\+?[1-9]\d{1,14}$'
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

# ============================================================================
# TIEMPO Y ZONAS HORARIAS
# ============================================================================

# Zona horaria por defecto del negocio
DEFAULT_TIMEZONE = "America/Santiago"
UTC_TIMEZONE = "UTC"

# Zonas horarias comunes para la app (timezone_id, display_name, country_code)
COMMON_TIMEZONES: list[tuple[str, str, str]] = [
    ("America/Santiago", "Chile (Santiago)", "CL"),
    ("America/Argentina/Buenos_Aires", "Argentina (Buenos Aires)", "AR"),
    ("America/Lima", "Perú (Lima)", "PE"),
    ("America/Bogota", "Colombia (Bogotá)", "CO"),
    ("America/Mexico_City", "México (CDMX)", "MX"),
    ("America/New_York", "USA (Nueva York)", "US"),
    ("America/Los_Angeles", "USA (Los Angeles)", "US"),
    ("Europe/Madrid", "España (Madrid)", "ES"),
    ("Europe/London", "Reino Unido (Londres)", "GB"),
    ("Asia/Shanghai", "China (Shanghai)", "CN"),
    ("Asia/Tokyo", "Japón (Tokio)", "JP"),
]

# Formatos de fecha (sintaxis Pendulum)
PENDULUM_DATE_FORMAT = "DD/MM/YYYY"
PENDULUM_DATETIME_FORMAT = "DD/MM/YYYY HH:mm"
PENDULUM_DATETIME_SECONDS_FORMAT = "DD/MM/YYYY HH:mm:ss"
PENDULUM_TIME_FORMAT = "HH:mm"
PENDULUM_DATETIME_FULL_FORMAT = "dddd, D [de] MMMM [de] YYYY HH:mm"

# Días de la semana laborales (0=lunes, 6=domingo)
BUSINESS_DAYS = [0, 1, 2, 3, 4]  # Lunes a Viernes
BUSINESS_HOUR_START = 9
BUSINESS_HOUR_END = 18
