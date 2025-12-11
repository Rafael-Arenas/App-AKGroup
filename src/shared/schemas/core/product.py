"""
Schemas de Pydantic para Product y ProductComponent.

Define los schemas de validación para operaciones CRUD sobre productos
y sus componentes (BOM - Bill of Materials).
"""

from typing import Optional, List
from decimal import Decimal
from pydantic import Field, field_validator

from src.shared.schemas.base import BaseSchema, BaseResponse
from src.shared.constants import PRODUCT_TYPE_ARTICLE, PRODUCT_TYPE_NOMENCLATURE


# ============================================================================
# PRODUCT SCHEMAS
# ============================================================================

class ProductCreate(BaseSchema):
    """
    Schema para crear un nuevo producto.

    Example:
        # Producto simple (ARTICLE)
        data = ProductCreate(
            reference="PROD-001",
            designation_es="Tornillo M6",
            product_type="ARTICLE",
            cost_price=Decimal("100.00"),
            sale_price=Decimal("150.00")
        )

        # Producto con BOM (NOMENCLATURE)
        data = ProductCreate(
            reference="ASSEM-001",
            designation_es="Ensamble Completo",
            product_type="NOMENCLATURE"
        )
    """

    reference: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Código único del producto"
    )
    designation_es: str = Field(
        ...,
        min_length=2,
        max_length=200,
        description="Nombre del producto en español"
    )
    short_designation: Optional[str] = Field(
        None,
        max_length=100,
        description="Descripción corta"
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
    minimum_stock: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=3,
        description="Stock mínimo"
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
    image_url: Optional[str] = Field(
        None,
        max_length=500,
        description="URL de la imagen del producto"
    )
    plan_url: Optional[str] = Field(
        None,
        max_length=500,
        description="URL del plano/diseño del producto"
    )
    supplier_reference: Optional[str] = Field(
        None,
        max_length=100,
        description="Referencia del proveedor"
    )
    customs_number: Optional[str] = Field(
        None,
        max_length=50,
        description="Número de aduana"
    )

    @field_validator('reference')
    @classmethod
    def reference_uppercase(cls, v: str) -> str:
        """Convierte la referencia a mayúsculas."""
        return v.upper().strip()

    @field_validator('designation_es')
    @classmethod
    def designation_not_empty(cls, v: str) -> str:
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
            designation_es="Nuevo Nombre",
            sale_price=Decimal("200.00")
        )
    """

    reference: Optional[str] = Field(None, min_length=1, max_length=50)
    designation_es: Optional[str] = Field(None, min_length=2, max_length=200)
    short_designation: Optional[str] = Field(None, max_length=100)
    product_type: Optional[str] = None
    cost_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    sale_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    stock_quantity: Optional[Decimal] = Field(None, ge=0, decimal_places=3)
    minimum_stock: Optional[Decimal] = Field(None, ge=0, decimal_places=3)
    family_type_id: Optional[int] = Field(None, gt=0)
    matter_id: Optional[int] = Field(None, gt=0)
    image_url: Optional[str] = Field(None, max_length=500)
    plan_url: Optional[str] = Field(None, max_length=500)
    supplier_reference: Optional[str] = Field(None, max_length=100)
    customs_number: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None

    @field_validator('reference')
    @classmethod
    def reference_uppercase(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return v.upper().strip()
        return v

    @field_validator('designation_es')
    @classmethod
    def designation_not_empty(cls, v: Optional[str]) -> Optional[str]:
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
        print(product.reference)
        print(product.designation_es)
    """

    reference: str
    designation_fr: Optional[str] = None
    designation_es: Optional[str] = None
    designation_en: Optional[str] = None
    short_designation: Optional[str] = None
    revision: Optional[str] = None
    product_type: str
    purchase_price: Optional[Decimal] = None
    cost_price: Optional[Decimal] = None
    sale_price: Optional[Decimal] = None
    sale_price_eur: Optional[Decimal] = None
    price_calculation_mode: Optional[str] = None
    margin_percentage: Optional[Decimal] = None
    stock_quantity: Optional[Decimal] = None
    minimum_stock: Optional[Decimal] = None
    stock_location: Optional[str] = None
    family_type_id: Optional[int] = None
    matter_id: Optional[int] = None
    sales_type_id: Optional[int] = None
    company_id: Optional[int] = None
    image_url: Optional[str] = None
    plan_url: Optional[str] = None
    supplier_reference: Optional[str] = None
    customs_number: Optional[str] = None
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
