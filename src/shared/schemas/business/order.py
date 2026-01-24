from __future__ import annotations

"""
Pydantic schemas for Order model.

Defines validation schemas for creating, updating, and returning
order data through the API.
"""

from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator, ConfigDict


# ============================================================================
# ORDER PRODUCT SCHEMAS
# ============================================================================

class OrderProductBase(BaseModel):
    """Base schema for OrderProduct with common fields."""

    product_id: int = Field(..., gt=0, description="Product ID")
    sequence: int = Field(default=1, ge=1, description="Display order")
    quantity: Decimal = Field(..., gt=0, description="Quantity ordered")
    unit_price: Decimal = Field(..., ge=0, description="Price per unit")
    discount_percentage: Decimal | None = Field(
        default=Decimal("0.00"),
        ge=0,
        le=100,
        description="Discount percentage"
    )
    notes: str | None = Field(None, max_length=1000, description="Line item notes")


class OrderProductCreate(OrderProductBase):
    """Schema for creating an order product (line item)."""
    pass


class OrderProductUpdate(BaseModel):
    """Schema for updating an order product."""

    product_id: int | None = Field(None, gt=0)
    sequence: int | None = Field(None, ge=1)
    quantity: Decimal | None = Field(None, gt=0)
    unit_price: Decimal | None = Field(None, ge=0)
    discount_percentage: Decimal | None = Field(None, ge=0, le=100)
    notes: str | None = Field(None, max_length=1000)


class ProductSummary(BaseModel):
    """Resumen de producto para incluir en respuestas de order product."""
    
    id: int
    reference: str
    designation_es: str | None = None
    designation_en: str | None = None
    designation_fr: str | None = None
    product_type: str = "article"
    
    model_config = ConfigDict(from_attributes=True)


class OrderProductResponse(OrderProductBase):
    """Schema for order product response."""

    id: int
    order_id: int
    discount_amount: Decimal
    subtotal: Decimal
    product: ProductSummary | None = None

    model_config = ConfigDict(from_attributes=True)


# === RELATED ENTITY SUMMARIES (FOR RESPONSES) ===

class ContactSummary(BaseModel):
    """Resumen de contacto para incluir en respuestas de orden."""
    id: int
    first_name: str
    last_name: str
    email: str | None = None
    phone: str | None = None
    mobile: str | None = None
    position: str | None = None
    model_config = ConfigDict(from_attributes=True)

class CompanyRutSummary(BaseModel):
    """Resumen de RUT de empresa para incluir en respuestas de orden."""
    id: int
    rut: str
    is_main: bool = False
    model_config = ConfigDict(from_attributes=True)

class PlantSummary(BaseModel):
    """Resumen de planta para incluir en respuestas de orden."""
    id: int
    name: str
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    model_config = ConfigDict(from_attributes=True)

class StaffSummary(BaseModel):
    """Resumen de personal para incluir en respuestas de orden."""
    id: int
    first_name: str
    last_name: str
    email: str | None = None
    phone: str | None = None
    position: str | None = None
    trigram: str | None = None
    model_config = ConfigDict(from_attributes=True)

class IncotermSummary(BaseModel):
    """Resumen de incoterm para incluir en respuestas de orden."""
    id: int
    code: str
    name: str | None = None
    model_config = ConfigDict(from_attributes=True)

class QuoteSummary(BaseModel):
    """Resumen de cotización para incluir en respuestas de orden."""
    id: int
    quote_number: str
    revision: str
    quote_date: date | None = None
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# ORDER SCHEMAS
# ============================================================================

class OrderBase(BaseModel):
    """Base schema for Order with common fields."""

    order_number: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Unique order number (e.g., O-2025-001)"
    )
    revision: str = Field(
        default="A",
        min_length=1,
        max_length=10,
        description="Order revision (A, B, C...)"
    )
    order_type: str = Field(
        default="sales",
        description="Order type: sales or purchase"
    )
    quote_id: int | None = Field(None, gt=0, description="Source quote ID")
    company_id: int = Field(..., gt=0, description="Company ID (customer/supplier)")
    company_rut_id: int | None = Field(None, gt=0, description="Company RUT ID")
    contact_id: int | None = Field(None, gt=0, description="Contact person ID")
    plant_id: int | None = Field(None, gt=0, description="Plant ID")
    staff_id: int = Field(..., gt=0, description="Staff member ID")
    status_id: int = Field(..., gt=0, description="Order status ID")
    payment_status_id: int = Field(..., gt=0, description="Payment status ID")
    order_date: date = Field(..., description="Order creation date")
    promised_date: date | None = Field(None, description="Promised delivery date")
    completed_date: date | None = Field(None, description="Completion date")
    project_number: str | None = Field(None, max_length=100, description="Project number")
    customer_po_number: str | None = Field(None, max_length=100, description="Customer's purchase order number")
    incoterm_id: int | None = Field(None, gt=0, description="Incoterm ID")
    currency_id: int = Field(..., gt=0, description="Currency ID")
    exchange_rate: Decimal | None = Field(None, gt=0, description="Exchange rate")
    tax_percentage: Decimal = Field(
        default=Decimal("19.00"),
        ge=0,
        le=100,
        description="Tax percentage"
    )
    payment_terms: str | None = Field(None, max_length=200, description="Payment terms")
    is_export: bool = Field(default=False, description="Is export order")
    notes: str | None = Field(None, description="Customer-visible notes")
    internal_notes: str | None = Field(None, description="Internal notes only")

    @field_validator("order_number", "revision")
    @classmethod
    def uppercase_fields(cls, v: str) -> str:
        """Convert order_number and revision to uppercase."""
        return v.strip().upper()

    @field_validator("order_type")
    @classmethod
    def validate_order_type(cls, v: str) -> str:
        """Validate order type is valid."""
        valid_types = {"sales", "purchase"}
        if v.lower() not in valid_types:
            raise ValueError(f"Order type must be one of {valid_types}")
        return v.lower()


class OrderCreate(OrderBase):
    """
    Schema for creating a new order.

    All required fields must be provided.

    Example:
        data = OrderCreate(
            order_number="O-2025-001",
            order_type="sales",
            company_id=5,
            staff_id=2,
            status_id=1,
            payment_status_id=1,
            order_date=date.today(),
            currency_id=1
        )
    """

    products: list[OrderProductCreate] | None = Field(
        default_factory=list,
        description="List of order products (line items)"
    )


class OrderUpdate(BaseModel):
    """
    Schema for updating an order.

    All fields are optional - only provided fields will be updated.

    Example:
        data = OrderUpdate(
            status_id=2,
            promised_date=date(2025, 12, 31),
            internal_notes="Updated notes"
        )
    """

    revision: str | None = Field(None, min_length=1, max_length=10)
    order_type: str | None = None
    company_rut_id: int | None = Field(None, gt=0)
    contact_id: int | None = Field(None, gt=0)
    plant_id: int | None = Field(None, gt=0)
    staff_id: int | None = Field(None, gt=0)
    status_id: int | None = Field(None, gt=0)
    payment_status_id: int | None = Field(None, gt=0)
    promised_date: date | None = None
    completed_date: date | None = None
    project_number: str | None = Field(None, max_length=100)
    customer_po_number: str | None = Field(None, max_length=100)
    incoterm_id: int | None = Field(None, gt=0)
    currency_id: int | None = Field(None, gt=0)
    exchange_rate: Decimal | None = Field(None, gt=0)
    tax_percentage: Decimal | None = Field(None, ge=0, le=100)
    payment_terms: str | None = Field(None, max_length=200)
    is_export: bool | None = None
    notes: str | None = None
    internal_notes: str | None = None

    @field_validator("revision")
    @classmethod
    def uppercase_revision(cls, v: str | None) -> str | None:
        """Convert revision to uppercase."""
        return v.strip().upper() if v else None

    @field_validator("order_type")
    @classmethod
    def validate_order_type(cls, v: str | None) -> str | None:
        """Validate order type is valid."""
        if v:
            valid_types = {"sales", "purchase"}
            if v.lower() not in valid_types:
                raise ValueError(f"Order type must be one of {valid_types}")
            return v.lower()
        return v


class OrderResponse(OrderBase):
    """
    Schema for order response.

    Includes all fields plus calculated values and products.
    """

    id: int
    subtotal: Decimal
    tax_amount: Decimal
    total: Decimal
    products: list[OrderProductResponse] = Field(default_factory=list)

    # Related entities (expanded)
    contact: ContactSummary | None = None
    company_rut: CompanyRutSummary | None = None
    plant: PlantSummary | None = None
    staff: StaffSummary | None = None
    incoterm: IncotermSummary | None = None
    quote: QuoteSummary | None = None  # Cotización de origen (si aplica)

    model_config = ConfigDict(from_attributes=True)


class OrderListResponse(BaseModel):
    """
    Schema for order list item (summary view).

    Lightweight response for list endpoints.
    """

    id: int
    order_number: str
    revision: str
    order_type: str
    company_id: int
    company_name: str | None = None  # Nombre de la empresa
    staff_id: int
    status_id: int
    payment_status_id: int
    order_date: date
    promised_date: date | None = None
    total: Decimal

    model_config = ConfigDict(from_attributes=True)

