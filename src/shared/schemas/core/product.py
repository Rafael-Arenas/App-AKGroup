"""
Schemas de Pydantic para Product y ProductComponent.

Define los schemas de validación para operaciones CRUD sobre productos
y sus componentes (BOM - Bill of Materials).
"""

from typing import Optional, List
from decimal import Decimal
from pydantic import Field, field_validator

from src.shared.schemas.base import BaseSchema, BaseResponse
from src.backend.config.constants import PRODUCT_TYPE_ARTICLE, PRODUCT_TYPE_NOMENCLATURE


# ============================================================================
# PRODUCT SCHEMAS
# ============================================================================

class ProductCreate(BaseSchema):
    """
    Schema para crear un nuevo producto.

    Example:
        # Producto simple (ARTICLE)
        data = ProductCreate(
            code="PROD-001",
            name="Tornillo M6",
            product_type="ARTICLE",
            cost_price=Decimal("100.00"),
            sale_price=Decimal("150.00"),
            unit_id=1
        )

        # Producto con BOM (NOMENCLATURE)
        data = ProductCreate(
            code="ASSEM-001",
            name="Ensamble Completo",
            product_type="NOMENCLATURE",
            unit_id=1
        )
    """

    code: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Código único del producto"
    )
    name: str = Field(
        ...,
        min_length=2,
        max_length=200,
        description="Nombre del producto"
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Descripción detallada"
    )
    product_type: str = Field(
        ...,
        description="Tipo: ARTICLE (simple) o NOMENCLATURE (con BOM)"
    )
    cost_price: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Precio de costo"
    )
    sale_price: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Precio de venta"
    )
    stock_quantity: Optional[Decimal] = Field(
        default=Decimal("0.000"),
        ge=0,
        decimal_places=3,
        description="Cantidad en stock"
    )
    min_stock: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=3,
        description="Stock mínimo"
    )
    max_stock: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=3,
        description="Stock máximo"
    )
    unit_id: int = Field(
        ...,
        gt=0,
        description="ID de la unidad de medida"
    )
    family_type_id: Optional[int] = Field(
        None,
        gt=0,
        description="ID de la familia de producto"
    )
    matter_id: Optional[int] = Field(
        None,
        gt=0,
        description="ID del material/materia"
    )

    @field_validator('code')
    @classmethod
    def code_uppercase(cls, v: str) -> str:
        """Convierte el código a mayúsculas."""
        return v.upper().strip()

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        """Asegura que el nombre no sea solo espacios."""
        if not v.strip():
            raise ValueError("El nombre del producto no puede estar vacío")
        return v.strip()

    @field_validator('product_type')
    @classmethod
    def validate_product_type(cls, v: str) -> str:
        """Valida que el tipo de producto sea válido."""
        valid_types = {PRODUCT_TYPE_ARTICLE, PRODUCT_TYPE_NOMENCLATURE}
        if v not in valid_types:
            raise ValueError(
                f"Tipo de producto debe ser {PRODUCT_TYPE_ARTICLE} o {PRODUCT_TYPE_NOMENCLATURE}"
            )
        return v


class ProductUpdate(BaseSchema):
    """
    Schema para actualizar un producto.

    Todos los campos son opcionales.

    Example:
        data = ProductUpdate(
            name="Nuevo Nombre",
            sale_price=Decimal("200.00")
        )
    """

    code: Optional[str] = Field(None, min_length=1, max_length=50)
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    product_type: Optional[str] = None
    cost_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    sale_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    stock_quantity: Optional[Decimal] = Field(None, ge=0, decimal_places=3)
    min_stock: Optional[Decimal] = Field(None, ge=0, decimal_places=3)
    max_stock: Optional[Decimal] = Field(None, ge=0, decimal_places=3)
    unit_id: Optional[int] = Field(None, gt=0)
    family_type_id: Optional[int] = Field(None, gt=0)
    matter_id: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None

    @field_validator('code')
    @classmethod
    def code_uppercase(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return v.upper().strip()
        return v

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v and not v.strip():
            raise ValueError("El nombre del producto no puede estar vacío")
        return v.strip() if v else v

    @field_validator('product_type')
    @classmethod
    def validate_product_type(cls, v: Optional[str]) -> Optional[str]:
        if v:
            valid_types = {PRODUCT_TYPE_ARTICLE, PRODUCT_TYPE_NOMENCLATURE}
            if v not in valid_types:
                raise ValueError(
                    f"Tipo de producto debe ser {PRODUCT_TYPE_ARTICLE} o {PRODUCT_TYPE_NOMENCLATURE}"
                )
        return v


class ProductResponse(BaseResponse):
    """
    Schema para respuesta de producto.

    Example:
        product = ProductResponse.model_validate(product_orm)
        print(product.name)
        print(product.code)
    """

    code: str
    name: str
    description: Optional[str] = None
    product_type: str
    cost_price: Optional[Decimal] = None
    sale_price: Optional[Decimal] = None
    stock_quantity: Optional[Decimal] = None
    min_stock: Optional[Decimal] = None
    max_stock: Optional[Decimal] = None
    unit_id: int
    family_type_id: Optional[int] = None
    matter_id: Optional[int] = None
    is_active: bool

    # Relaciones opcionales
    components: Optional[List['ProductComponentResponse']] = []
    parent_components: Optional[List['ProductComponentResponse']] = []


# ============================================================================
# PRODUCT COMPONENT SCHEMAS (BOM)
# ============================================================================

class ProductComponentCreate(BaseSchema):
    """
    Schema para agregar un componente a un producto (BOM).

    Example:
        # Agregar tornillo como componente de ensamble
        data = ProductComponentCreate(
            parent_id=1,  # ID del ensamble
            component_id=5,  # ID del tornillo
            quantity=Decimal("4.000")  # Se necesitan 4 tornillos
        )
    """

    parent_id: int = Field(
        ...,
        gt=0,
        description="ID del producto padre (debe ser NOMENCLATURE)"
    )
    component_id: int = Field(
        ...,
        gt=0,
        description="ID del componente"
    )
    quantity: Decimal = Field(
        ...,
        gt=0,
        decimal_places=3,
        description="Cantidad del componente necesaria"
    )

    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v: Decimal) -> Decimal:
        """Valida que la cantidad sea positiva."""
        if v <= 0:
            raise ValueError("La cantidad debe ser mayor a cero")
        return v


class ProductComponentUpdate(BaseSchema):
    """
    Schema para actualizar un componente.

    Solo se puede actualizar la cantidad.

    Example:
        data = ProductComponentUpdate(quantity=Decimal("5.000"))
    """

    quantity: Decimal = Field(
        ...,
        gt=0,
        decimal_places=3,
        description="Nueva cantidad del componente"
    )

    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("La cantidad debe ser mayor a cero")
        return v


class ProductComponentResponse(BaseResponse):
    """
    Schema para respuesta de componente de producto.

    Example:
        component = ProductComponentResponse.model_validate(component_orm)
        print(f"Cantidad: {component.quantity}")
    """

    parent_id: int
    component_id: int
    quantity: Decimal

    # Información del componente (eager loading opcional)
    component_name: Optional[str] = None
    component_code: Optional[str] = None


# ============================================================================
# SCHEMAS ESPECIALES
# ============================================================================

class ProductWithBOMResponse(ProductResponse):
    """
    Schema extendido para producto con BOM completo.

    Incluye todos los componentes con sus detalles.

    Example:
        product = ProductWithBOMResponse.model_validate(product_orm)
        for component in product.components:
            print(f"{component.component_name}: {component.quantity}")
    """

    total_components: int = 0
    bom_levels: int = 0  # Niveles de profundidad del BOM


class ProductSearchResponse(BaseSchema):
    """
    Schema simplificado para búsquedas rápidas.

    Example:
        results = [ProductSearchResponse.model_validate(p) for p in products]
    """

    id: int
    code: str
    name: str
    product_type: str
    sale_price: Optional[Decimal] = None
    stock_quantity: Optional[Decimal] = None
    is_active: bool
