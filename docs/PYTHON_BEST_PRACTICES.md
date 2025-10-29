# Python Best Practices & Coding Standards

## Tabla de Contenidos
1. [PEP 8 - Guía de Estilo Oficial](#pep-8---guía-de-estilo-oficial)
2. [Principios de Clean Code](#principios-de-clean-code)
3. [Convenciones de Nombres](#convenciones-de-nombres)
4. [Estructura de Código](#estructura-de-código)
5. [Documentación](#documentación)
6. [Manejo de Errores](#manejo-de-errores)
7. [Type Hints](#type-hints)
8. [Herramientas Recomendadas](#herramientas-recomendadas)
9. [Principios SOLID](#principios-solid)
10. [Patrones de Diseño](#patrones-de-diseño)

---

## PEP 8 - Guía de Estilo Oficial

### Indentación y Formato
```python
# ✓ CORRECTO: 4 espacios por nivel de indentación
def my_function(param1, param2):
    if param1 > 0:
        return param1 + param2
    return 0

# ✗ INCORRECTO: tabs o 2 espacios
def my_function(param1, param2):
  if param1 > 0:
    return param1 + param2
```

### Longitud de Línea
- **Código**: Máximo 79 caracteres
- **Docstrings/Comentarios**: Máximo 72 caracteres
- Usa paréntesis para líneas largas

```python
# ✓ CORRECTO
result = some_function_name(
    argument1, argument2,
    argument3, argument4
)

# ✓ CORRECTO - continuación implícita
income = (gross_wages
          + taxable_interest
          + (dividends - qualified_dividends)
          - ira_deduction)
```

### Líneas en Blanco
```python
# 2 líneas en blanco antes de definiciones de clase o función top-level
import os
import sys


def function_one():
    pass


def function_two():
    pass


class MyClass:
    # 1 línea en blanco entre métodos
    def method_one(self):
        pass

    def method_two(self):
        pass
```

---

## Convenciones de Nombres

### Variables y Funciones: snake_case
```python
# ✓ CORRECTO
user_name = "Juan"
total_amount = 100
max_retry_count = 3

def calculate_total_price(items):
    pass

def get_user_data():
    pass
```

### Constantes: UPPER_SNAKE_CASE
```python
# ✓ CORRECTO
PI = 3.14159
MAX_CONNECTIONS = 100
DATABASE_URL = "sqlite:///app.db"
API_KEY = "your-api-key"
```

### Clases: PascalCase
```python
# ✓ CORRECTO
class UserProfile:
    pass

class DatabaseConnection:
    pass

class OrderProcessor:
    pass
```

### Módulos y Paquetes: lowercase
```python
# Nombres de archivo
# ✓ CORRECTO
# database.py
# user_manager.py
# order_processor.py

# ✗ INCORRECTO
# Database.py
# UserManager.py
```

### Variables Privadas: _prefijo
```python
class MyClass:
    def __init__(self):
        self.public_var = "visible"
        self._protected_var = "interno"
        self.__private_var = "muy privado"

    def _internal_method(self):
        """Método para uso interno"""
        pass
```

---

## Estructura de Código

### Organización de Imports
```python
# 1. Imports de biblioteca estándar
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional

# 2. Imports de terceros
import sqlalchemy
from pydantic import BaseModel
from loguru import logger

# 3. Imports locales de la aplicación
from models.user import User
from config.settings import settings
from utils.helpers import format_date
```

### Evitar Imports *
```python
# ✗ INCORRECTO
from module import *

# ✓ CORRECTO
from module import specific_function, SpecificClass
```

---

## Principios de Clean Code

### 1. Nombres Descriptivos
```python
# ✗ INCORRECTO
def calc(x, y):
    return x * y * 0.19

# ✓ CORRECTO
def calculate_tax_amount(price: float, quantity: int) -> float:
    TAX_RATE = 0.19
    subtotal = price * quantity
    return subtotal * TAX_RATE
```

### 2. Funciones Pequeñas y Específicas
```python
# ✗ INCORRECTO - Función que hace demasiado
def process_order(order_data):
    # Valida datos
    if not order_data.get('customer'):
        raise ValueError("Missing customer")

    # Calcula total
    total = sum(item['price'] for item in order_data['items'])

    # Aplica descuento
    if order_data.get('discount'):
        total *= (1 - order_data['discount'])

    # Guarda en base de datos
    save_to_db(order_data)

    # Envía email
    send_confirmation_email(order_data['customer'])

    return total

# ✓ CORRECTO - Funciones separadas y específicas
def validate_order_data(order_data: dict) -> None:
    if not order_data.get('customer'):
        raise ValueError("Missing customer")

def calculate_order_total(items: List[dict]) -> float:
    return sum(item['price'] for item in items)

def apply_discount(total: float, discount: float) -> float:
    return total * (1 - discount)

def process_order(order_data: dict) -> float:
    validate_order_data(order_data)
    total = calculate_order_total(order_data['items'])

    if discount := order_data.get('discount'):
        total = apply_discount(total, discount)

    save_order_to_database(order_data)
    send_confirmation_email(order_data['customer'])

    return total
```

### 3. DRY - Don't Repeat Yourself
```python
# ✗ INCORRECTO - Código repetido
def format_user_name(user):
    return f"{user.first_name} {user.last_name}".strip().title()

def format_employee_name(employee):
    return f"{employee.first_name} {employee.last_name}".strip().title()

# ✓ CORRECTO - Reutilización
def format_full_name(first_name: str, last_name: str) -> str:
    return f"{first_name} {last_name}".strip().title()

def format_user_name(user):
    return format_full_name(user.first_name, user.last_name)

def format_employee_name(employee):
    return format_full_name(employee.first_name, employee.last_name)
```

### 4. Comentarios Significativos
```python
# ✗ INCORRECTO - Comentario obvio
# Incrementa el contador en 1
counter += 1

# ✗ INCORRECTO - Código comentado
# old_function()
# legacy_code()

# ✓ CORRECTO - Explica el "por qué"
# Incrementamos antes de la validación para evitar condiciones de carrera
# cuando múltiples threads acceden al contador simultáneamente
counter += 1

# ✓ CORRECTO - Documenta decisiones de diseño
# Usamos SHA-256 en lugar de MD5 porque MD5 ya no es seguro
# para aplicaciones criptográficas (CVE-2008-1447)
hash_value = hashlib.sha256(data).hexdigest()
```

---

## Documentación

### Docstrings
```python
def calculate_discount(price: float, discount_percentage: float) -> float:
    """
    Calcula el precio final después de aplicar un descuento.

    Args:
        price: Precio original del producto
        discount_percentage: Porcentaje de descuento (0-100)

    Returns:
        Precio final después del descuento

    Raises:
        ValueError: Si el descuento es negativo o mayor a 100

    Example:
        >>> calculate_discount(100, 20)
        80.0
    """
    if discount_percentage < 0 or discount_percentage > 100:
        raise ValueError("Discount must be between 0 and 100")

    return price * (1 - discount_percentage / 100)


class User:
    """
    Representa un usuario del sistema.

    Attributes:
        username: Nombre de usuario único
        email: Correo electrónico del usuario
        created_at: Fecha de creación de la cuenta
    """

    def __init__(self, username: str, email: str):
        """
        Inicializa un nuevo usuario.

        Args:
            username: Nombre de usuario único
            email: Correo electrónico válido
        """
        self.username = username
        self.email = email
        self.created_at = datetime.now()
```

---

## Manejo de Errores

### Excepciones Específicas
```python
# ✗ INCORRECTO - Captura demasiado genérica
try:
    data = read_file(filename)
except:
    print("Error")

# ✓ CORRECTO - Excepciones específicas
try:
    data = read_file(filename)
except FileNotFoundError:
    logger.error(f"File not found: {filename}")
    raise
except PermissionError:
    logger.error(f"Permission denied: {filename}")
    raise
except Exception as e:
    logger.exception(f"Unexpected error reading {filename}")
    raise
```

### Uso de Context Managers
```python
# ✗ INCORRECTO
file = open('data.txt', 'r')
data = file.read()
file.close()

# ✓ CORRECTO
with open('data.txt', 'r') as file:
    data = file.read()
```

### Crear Excepciones Personalizadas
```python
class OrderError(Exception):
    """Excepción base para errores de orden"""
    pass

class InsufficientStockError(OrderError):
    """Se lanza cuando no hay suficiente stock"""
    pass

class InvalidOrderStateError(OrderError):
    """Se lanza cuando el estado de la orden es inválido"""
    pass

# Uso
def process_order(order):
    if order.quantity > available_stock:
        raise InsufficientStockError(
            f"Insufficient stock: requested {order.quantity}, "
            f"available {available_stock}"
        )
```

---

## Type Hints

### Tipos Básicos
```python
from typing import List, Dict, Optional, Union, Tuple, Set

def greet(name: str) -> str:
    return f"Hello, {name}"

def process_numbers(numbers: List[int]) -> int:
    return sum(numbers)

def get_user_data(user_id: int) -> Optional[Dict[str, str]]:
    """Retorna datos del usuario o None si no existe"""
    user = database.get_user(user_id)
    return user.to_dict() if user else None

def calculate(value: Union[int, float]) -> float:
    return float(value) * 1.5
```

### Tipos Complejos
```python
from typing import Callable, Any, TypeVar, Generic

# Callable
def apply_operation(value: int, operation: Callable[[int], int]) -> int:
    return operation(value)

# TypeVar para genéricos
T = TypeVar('T')

def get_first_element(items: List[T]) -> Optional[T]:
    return items[0] if items else None

# Generic class
class Repository(Generic[T]):
    def __init__(self):
        self._items: List[T] = []

    def add(self, item: T) -> None:
        self._items.append(item)

    def get_all(self) -> List[T]:
        return self._items.copy()
```

### Pydantic para Validación
```python
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime

class User(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    age: int = Field(..., ge=0, le=150)
    created_at: datetime = Field(default_factory=datetime.now)

    @validator('username')
    def username_alphanumeric(cls, v):
        assert v.isalnum(), 'must be alphanumeric'
        return v

# Uso
user = User(
    username="john123",
    email="john@example.com",
    age=30
)
```

---

## Principios SOLID

### S - Single Responsibility Principle
```python
# ✗ INCORRECTO - Múltiples responsabilidades
class User:
    def __init__(self, username, email):
        self.username = username
        self.email = email

    def save_to_database(self):
        # Guardar en BD
        pass

    def send_welcome_email(self):
        # Enviar email
        pass

    def generate_report(self):
        # Generar reporte
        pass

# ✓ CORRECTO - Una responsabilidad por clase
class User:
    def __init__(self, username: str, email: str):
        self.username = username
        self.email = email

class UserRepository:
    def save(self, user: User) -> None:
        # Guardar en BD
        pass

class EmailService:
    def send_welcome_email(self, user: User) -> None:
        # Enviar email
        pass

class UserReportGenerator:
    def generate(self, user: User) -> str:
        # Generar reporte
        pass
```

### O - Open/Closed Principle
```python
from abc import ABC, abstractmethod

# ✓ CORRECTO - Abierto para extensión, cerrado para modificación
class PaymentProcessor(ABC):
    @abstractmethod
    def process_payment(self, amount: float) -> bool:
        pass

class CreditCardProcessor(PaymentProcessor):
    def process_payment(self, amount: float) -> bool:
        # Lógica para tarjeta de crédito
        return True

class PayPalProcessor(PaymentProcessor):
    def process_payment(self, amount: float) -> bool:
        # Lógica para PayPal
        return True

class CryptoProcessor(PaymentProcessor):
    def process_payment(self, amount: float) -> bool:
        # Lógica para criptomonedas
        return True
```

### L - Liskov Substitution Principle
```python
# ✓ CORRECTO - Las subclases pueden sustituir a la clase base
class Bird:
    def move(self):
        return "Moving"

class FlyingBird(Bird):
    def fly(self):
        return "Flying"

class Penguin(Bird):
    def swim(self):
        return "Swimming"

# Uso
def make_bird_move(bird: Bird):
    return bird.move()  # Funciona con cualquier Bird
```

### I - Interface Segregation Principle
```python
from abc import ABC, abstractmethod

# ✓ CORRECTO - Interfaces específicas
class Readable(ABC):
    @abstractmethod
    def read(self) -> str:
        pass

class Writable(ABC):
    @abstractmethod
    def write(self, data: str) -> None:
        pass

class ReadOnlyFile(Readable):
    def read(self) -> str:
        return "data"

class ReadWriteFile(Readable, Writable):
    def read(self) -> str:
        return "data"

    def write(self, data: str) -> None:
        pass
```

### D - Dependency Inversion Principle
```python
from abc import ABC, abstractmethod

# ✓ CORRECTO - Depender de abstracciones
class IDatabase(ABC):
    @abstractmethod
    def save(self, data: dict) -> None:
        pass

class PostgresDatabase(IDatabase):
    def save(self, data: dict) -> None:
        # Lógica PostgreSQL
        pass

class MongoDatabase(IDatabase):
    def save(self, data: dict) -> None:
        # Lógica MongoDB
        pass

class UserService:
    def __init__(self, database: IDatabase):
        self.database = database

    def create_user(self, user_data: dict):
        self.database.save(user_data)

# Uso con inyección de dependencias
db = PostgresDatabase()
user_service = UserService(db)
```

---

## Patrones de Diseño

### Singleton
```python
class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

### Factory
```python
class ShapeFactory:
    @staticmethod
    def create_shape(shape_type: str):
        if shape_type == "circle":
            return Circle()
        elif shape_type == "square":
            return Square()
        raise ValueError(f"Unknown shape: {shape_type}")
```

### Repository Pattern
```python
from abc import ABC, abstractmethod
from typing import List, Optional

class IRepository(ABC, Generic[T]):
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:
        pass

    @abstractmethod
    def get_all(self) -> List[T]:
        pass

    @abstractmethod
    def add(self, entity: T) -> T:
        pass

    @abstractmethod
    def update(self, entity: T) -> T:
        pass

    @abstractmethod
    def delete(self, id: int) -> None:
        pass

class UserRepository(IRepository[User]):
    def __init__(self, session):
        self.session = session

    def get_by_id(self, id: int) -> Optional[User]:
        return self.session.query(User).filter_by(id=id).first()

    def get_all(self) -> List[User]:
        return self.session.query(User).all()

    def add(self, user: User) -> User:
        self.session.add(user)
        self.session.commit()
        return user

    def update(self, user: User) -> User:
        self.session.merge(user)
        self.session.commit()
        return user

    def delete(self, id: int) -> None:
        user = self.get_by_id(id)
        if user:
            self.session.delete(user)
            self.session.commit()
```

---

## Herramientas Recomendadas

### Linters y Formatters
```bash
# Instalar herramientas de desarrollo
poetry add --group dev black ruff mypy pytest pytest-cov

# Black - Formateador automático
black .

# Ruff - Linter rápido (reemplazo moderno de flake8, pylint)
ruff check .
ruff check --fix .

# MyPy - Type checker
mypy .

# Pytest - Testing
pytest
pytest --cov=. --cov-report=html
```

### Configuración pyproject.toml
```toml
[tool.black]
line-length = 88
target-version = ['py313']
include = '\.pyi?$'

[tool.ruff]
line-length = 88
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "B",  # flake8-bugbear
    "C4", # flake8-comprehensions
    "UP", # pyupgrade
]
ignore = []

[tool.mypy]
python_version = "3.13"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
```

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.10.0
    hooks:
      - id: black

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.4
    hooks:
      - id: ruff
        args: [--fix]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

---

## Testing Best Practices

### Estructura de Tests
```python
import pytest
from app.services import UserService

class TestUserService:
    @pytest.fixture
    def user_service(self):
        return UserService()

    def test_create_user_with_valid_data(self, user_service):
        # Arrange
        user_data = {
            "username": "testuser",
            "email": "test@example.com"
        }

        # Act
        result = user_service.create_user(user_data)

        # Assert
        assert result.username == "testuser"
        assert result.email == "test@example.com"

    def test_create_user_with_invalid_email_raises_error(self, user_service):
        user_data = {
            "username": "testuser",
            "email": "invalid-email"
        }

        with pytest.raises(ValueError, match="Invalid email"):
            user_service.create_user(user_data)
```

---

## Logging Best Practices

```python
from loguru import logger

# Configuración de logger
logger.add(
    "logs/app_{time}.log",
    rotation="1 day",
    retention="30 days",
    level="INFO"
)

# Uso correcto
def process_order(order_id: int):
    logger.info(f"Processing order {order_id}")

    try:
        order = get_order(order_id)
        logger.debug(f"Order data: {order}")

        result = validate_order(order)
        logger.success(f"Order {order_id} validated successfully")

        return result

    except OrderNotFoundError:
        logger.warning(f"Order {order_id} not found")
        raise

    except Exception as e:
        logger.exception(f"Error processing order {order_id}")
        raise
```

---

## Resumen - Checklist Rápido

- [ ] Usar 4 espacios para indentación
- [ ] Líneas <= 79 caracteres
- [ ] snake_case para funciones y variables
- [ ] PascalCase para clases
- [ ] UPPER_SNAKE_CASE para constantes
- [ ] Docstrings para todas las funciones públicas
- [ ] Type hints en todas las funciones
- [ ] Manejar excepciones específicas
- [ ] Una responsabilidad por función/clase
- [ ] Nombres descriptivos y significativos
- [ ] Evitar código repetido (DRY)
- [ ] Tests para código crítico
- [ ] Usar formatters automáticos (Black)
- [ ] Validar con linters (Ruff)
- [ ] Type checking (MyPy)
- [ ] Logging apropiado
- [ ] Imports organizados
- [ ] Código sin comentarios innecesarios

---

**Recursos Adicionales:**
- [PEP 8 Oficial](https://peps.python.org/pep-0008/)
- [Real Python - PEP 8](https://realpython.com/python-pep8/)
- [Clean Code Python](https://github.com/zedr/clean-code-python)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
