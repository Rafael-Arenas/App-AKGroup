"""
Schemas de Pydantic para Product y ProductComponent.

Define los schemas de validación para operaciones CRUD sobre productos
y sus componentes (BOM - Bill of Materials).
"""

from __future__ import annotations

from decimal import Decimal
from pydantic import Field, field_validator

from src.shared.schemas.base import BaseSchema, BaseResponse
from src.shared.schemas.core.company import CompanyResponse
from src.shared.schemas.lookups.lookup import SalesTypeResponse, FamilyTypeResponse, MatterResponse
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
    short_designation: str | None = Field(
        None,
        max_length=100,
        description="Descripción corta"
    )
    product_type: str = Field(
        ...,
        description="Tipo: ARTICLE (simple) o NOMENCLATURE (con BOM)"
    )
    cost_price: Decimal | None = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Precio de costo"
    )
    sale_price: Decimal | None = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Precio de venta"
    )
    stock_quantity: Decimal | None = Field(
        default=Decimal("0.000"),
        ge=0,
        decimal_places=3,
        description="Cantidad en stock"
    )
    minimum_stock: Decimal | None = Field(
        None,
        ge=0,
        decimal_places=3,
        description="Stock mínimo"
    )
    family_type_id: int | None = Field(
        None,
        gt=0,
        description="ID de la familia de producto"
    )
    matter_id: int | None = Field(
        None,
        gt=0,
        description="ID del material/materia"
    )
    image_url: str | None = Field(
        None,
        max_length=500,
        description="URL de la imagen del producto"
    )
    plan_url: str | None = Field(
        None,
        max_length=500,
        description="URL del plano/diseño del producto"
    )
    supplier_reference: str | None = Field(
        None,
        max_length=100,
        description="Referencia del proveedor"
    )
    customs_number: str | None = Field(
        None,
        max_length=50,
        description="Número de aduana"
    )
    purchase_price: Decimal | None = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Precio de compra"
    )
    sale_price_eur: Decimal | None = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Precio en euros"
    )
    stock_location: str | None = Field(
        None,
        max_length=100,
        description="Ubicación en almacén"
    )
    net_weight: Decimal | None = Field(
        None,
        ge=0,
        decimal_places=3,
        description="Peso neto (kg)"
    )
    gross_weight: Decimal | None = Field(
        None,
        ge=0,
        decimal_places=3,
        description="Peso bruto (kg)"
    )
    length: Decimal | None = Field(
        None,
        ge=0,
        decimal_places=3,
        description="Longitud (mm)"
    )
    width: Decimal | None = Field(
        None,
        ge=0,
        decimal_places=3,
        description="Ancho (mm)"
    )
    height: Decimal | None = Field(
        None,
        ge=0,
        decimal_places=3,
        description="Altura (mm)"
    )
    volume: Decimal | None = Field(
        None,
        ge=0,
        decimal_places=6,
        description="Volumen (m³)"
    )
    hs_code: str | None = Field(
        None,
        max_length=20,
        description="Código arancelario"
    )
    country_of_origin: str | None = Field(
        None,
        max_length=2,
        description="País de origen (ISO-2)"
    )
    notes: str | None = Field(
        None,
        max_length=2000,
        description="Notas adicionales"
    )
    sales_type_id: int | None = Field(
        None,
        gt=0,
        description="ID del tipo de venta"
    )
    company_id: int | None = Field(
        None,
        gt=0,
        description="ID de la empresa fabricante"
    )
    designation_fr: str | None = Field(
        None,
        max_length=200,
        description="Nombre del producto en francés"
    )
    designation_en: str | None = Field(
        None,
        max_length=200,
        description="Nombre del producto en inglés"
    )
    revision: str | None = Field(
        None,
        max_length=20,
        description="Revisión"
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

    reference: str | None = Field(None, min_length=1, max_length=50)
    designation_es: str | None = Field(None, min_length=2, max_length=200)
    short_designation: str | None = Field(None, max_length=100)
    product_type: str | None = None
    cost_price: Decimal | None = Field(None, ge=0, decimal_places=2)
    sale_price: Decimal | None = Field(None, ge=0, decimal_places=2)
    stock_quantity: Decimal | None = Field(None, ge=0, decimal_places=3)
    minimum_stock: Decimal | None = Field(None, ge=0, decimal_places=3)
    family_type_id: int | None = Field(None, gt=0)
    matter_id: int | None = Field(None, gt=0)
    image_url: str | None = Field(None, max_length=500)
    plan_url: str | None = Field(None, max_length=500)
    supplier_reference: str | None = Field(None, max_length=100)
    customs_number: str | None = Field(None, max_length=50)
    purchase_price: Decimal | None = Field(None, ge=0, decimal_places=2)
    sale_price_eur: Decimal | None = Field(None, ge=0, decimal_places=2)
    stock_location: str | None = Field(None, max_length=100)
    net_weight: Decimal | None = Field(None, ge=0, decimal_places=3)
    gross_weight: Decimal | None = Field(None, ge=0, decimal_places=3)
    length: Decimal | None = Field(None, ge=0, decimal_places=3)
    width: Decimal | None = Field(None, ge=0, decimal_places=3)
    height: Decimal | None = Field(None, ge=0, decimal_places=3)
    volume: Decimal | None = Field(None, ge=0, decimal_places=6)
    hs_code: str | None = Field(None, max_length=20)
    country_of_origin: str | None = Field(None, max_length=2)
    notes: str | None = Field(None, max_length=2000)
    sales_type_id: int | None = Field(None, gt=0)
    company_id: int | None = Field(None, gt=0)
    designation_fr: str | None = Field(None, max_length=200)
    designation_en: str | None = Field(None, max_length=200)
    revision: str | None = Field(None, max_length=20)
    is_active: bool | None = None

    @field_validator('reference')
    @classmethod
    def reference_uppercase(cls, v: str | None) -> str | None:
        if v:
            return v.upper().strip()
        return v

    @field_validator('designation_es')
    @classmethod
    def designation_not_empty(cls, v: str | None) -> str | None:
        if v and not v.strip():
            raise ValueError("El nombre del producto no puede estar vacío")
        return v.strip() if v else v

    @field_validator('product_type')
    @classmethod
    def validate_product_type(cls, v: str | None) -> str | None:
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
    designation_fr: str | None = None
    designation_es: str | None = None
    designation_en: str | None = None
    short_designation: str | None = None
    revision: str | None = None
    product_type: str
    purchase_price: Decimal | None = None
    cost_price: Decimal | None = None
    sale_price: Decimal | None = None
    sale_price_eur: Decimal | None = None
    price_calculation_mode: str | None = None
    margin_percentage: Decimal | None = None
    stock_quantity: Decimal | None = None
    minimum_stock: Decimal | None = None
    stock_location: str | None = None
    family_type_id: int | None = None
    matter_id: int | None = None
    sales_type_id: int | None = None
    company_id: int | None = None
    image_url: str | None = None
    plan_url: str | None = None
    supplier_reference: str | None = None
    customs_number: str | None = None
    country_of_origin: str | None = None
    is_active: bool

    # Dimensiones y peso
    net_weight: Decimal | None = None
    gross_weight: Decimal | None = None
    length: Decimal | None = None
    width: Decimal | None = None
    height: Decimal | None = None
    volume: Decimal | None = None
    
    # Otros
    hs_code: str | None = None
    notes: str | None = None

    # Relaciones opcionales
    company: CompanyResponse | None = None
    sales_type: SalesTypeResponse | None = None
    family_type: FamilyTypeResponse | None = None
    matter: MatterResponse | None = None
    components: list[ProductComponentResponse] | None = []
    parent_components: list[ProductComponentResponse] | None = []


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
    component_name: str | None = None
    component_code: str | None = None


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


# Rebuild ProductResponse to resolve forward references
ProductResponse.model_rebuild()
