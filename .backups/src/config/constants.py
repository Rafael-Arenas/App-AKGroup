"""
Constantes de negocio para la aplicación AK Group.

Define constantes utilizadas en toda la aplicación para valores de negocio,
estados, tipos, y configuraciones que no deben cambiar frecuentemente.
"""

# Monedas
DEFAULT_CURRENCY = "CLP"
SUPPORTED_CURRENCIES = ["CLP", "USD", "EUR"]

# Impuestos
DEFAULT_TAX_RATE = 19.0  # IVA Chile

# Paginación
DEFAULT_PAGINATION_LIMIT = 100
MAX_PAGINATION_LIMIT = 1000

# Estados de cotización
QUOTE_STATUS_DRAFT = "draft"
QUOTE_STATUS_SENT = "sent"
QUOTE_STATUS_ACCEPTED = "accepted"
QUOTE_STATUS_REJECTED = "rejected"
QUOTE_STATUS_EXPIRED = "expired"

# Estados de orden
ORDER_STATUS_PENDING = "pending"
ORDER_STATUS_CONFIRMED = "confirmed"
ORDER_STATUS_IN_PRODUCTION = "in_production"
ORDER_STATUS_READY = "ready"
ORDER_STATUS_SHIPPED = "shipped"
ORDER_STATUS_DELIVERED = "delivered"
ORDER_STATUS_CANCELLED = "cancelled"

# Estados de pago
PAYMENT_STATUS_PENDING = "pending"
PAYMENT_STATUS_PARTIAL = "partial"
PAYMENT_STATUS_PAID = "paid"
PAYMENT_STATUS_OVERDUE = "overdue"

# Estados de entrega
DELIVERY_STATUS_PENDING = "pending"
DELIVERY_STATUS_IN_TRANSIT = "in_transit"
DELIVERY_STATUS_DELIVERED = "delivered"
DELIVERY_STATUS_CANCELLED = "cancelled"

# Tipos de empresa
COMPANY_TYPE_CUSTOMER = "customer"
COMPANY_TYPE_SUPPLIER = "supplier"
COMPANY_TYPE_BOTH = "both"

# Tipos de producto
PRODUCT_TYPE_ARTICLE = "ARTICLE"
PRODUCT_TYPE_NOMENCLATURE = "NOMENCLATURE"
PRODUCT_TYPE_SERVICE = "SERVICE"

# Tipos de dirección
ADDRESS_TYPE_DELIVERY = "delivery"
ADDRESS_TYPE_BILLING = "billing"
ADDRESS_TYPE_HEADQUARTERS = "headquarters"
ADDRESS_TYPE_BRANCH = "branch"

# Tipos de transporte
TRANSPORT_TYPE_OWN = "own"
TRANSPORT_TYPE_CARRIER = "carrier"
TRANSPORT_TYPE_COURIER = "courier"
TRANSPORT_TYPE_FREIGHT_FORWARDER = "freight_forwarder"

# Límites y validaciones
MIN_PASSWORD_LENGTH = 8
MAX_DISCOUNT_PERCENTAGE = 50.0
MIN_PRODUCT_QUANTITY = 0.001
MAX_PRODUCT_QUANTITY = 999999.999

# Formatos
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
RUT_REGEX = r'^\d{1,8}-[\dkK]$'
PHONE_REGEX = r'^\+?[1-9]\d{1,14}$'
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
