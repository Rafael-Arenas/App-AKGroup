from __future__ import annotations

"""
Pydantic schemas for Quote and QuoteProduct models.

Defines validation schemas for creating, updating, and returning
quote data through the API.
"""

from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator, ConfigDict

from src.shared.schemas.base import BaseSchema


# ============================================================================
# RELATED ENTITY SUMMARY SCHEMAS
# ============================================================================

class ContactSummary(BaseModel):
    """Resumen de contacto para incluir en respuestas de quote."""
    
    id: int
    first_name: str
    last_name: str
    email: str | None = None
    phone: str | None = None
    mobile: str | None = None
    position: str | None = None
    
    model_config = ConfigDict(from_attributes=True)


class CompanyRutSummary(BaseModel):
    """Resumen de RUT de empresa para incluir en respuestas de quote."""
    
    id: int
    rut: str
    is_main: bool = False
    
    model_config = ConfigDict(from_attributes=True)


class PlantSummary(BaseModel):
    """Resumen de planta para incluir en respuestas de quote."""
    
    id: int
    name: str
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    
    model_config = ConfigDict(from_attributes=True)


class StaffSummary(BaseModel):
    """Resumen de personal para incluir en respuestas de quote."""
    
    id: int
    first_name: str
    last_name: str
    email: str | None = None
    phone: str | None = None
    position: str | None = None
    trigram: str | None = None
    
    model_config = ConfigDict(from_attributes=True)


class IncotermSummary(BaseModel):
    """Resumen de incoterm para incluir en respuestas de quote."""
    
    id: int
    code: str
    name: str | None = None
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# QUOTE PRODUCT SCHEMAS
# ============================================================================

class QuoteProductBase(BaseModel):
    """Base schema for QuoteProduct with common fields."""

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


class QuoteProductCreate(QuoteProductBase):
    """
    Schema for creating a quote product (line item).

    All required fields must be provided.

    Example:
        data = QuoteProductCreate(
            product_id=10,
            sequence=1,
            quantity=Decimal("5.000"),
            unit_price=Decimal("1500.00"),
            discount_percentage=Decimal("10.00")
        )
    """

    pass


class QuoteProductUpdate(BaseModel):
    """
    Schema for updating a quote product.

    All fields are optional - only provided fields will be updated.

    Example:
        data = QuoteProductUpdate(
            quantity=Decimal("10.000"),
            discount_percentage=Decimal("15.00")
        )
    """

    product_id: int | None = Field(None, gt=0)
    sequence: int | None = Field(None, ge=1)
    quantity: Decimal | None = Field(None, gt=0)
    unit_price: Decimal | None = Field(None, ge=0)
    discount_percentage: Decimal | None = Field(None, ge=0, le=100)
    notes: str | None = Field(None, max_length=1000)



class ProductSummary(BaseModel):
    """Resumen de producto para incluir en respuestas de quote product."""
    
    id: int
    reference: str
    designation_es: str | None = None
    designation_en: str | None = None
    designation_fr: str | None = None
    product_type: str = "article"
    
    model_config = ConfigDict(from_attributes=True)


class QuoteProductResponse(QuoteProductBase):
    """
    Schema for quote product response.

    Includes all fields plus calculated values.

    Example:
        {
            "id": 1,
            "quote_id": 5,
            "product_id": 10,
            "sequence": 1,
            "quantity": "5.000",
            "unit_price": "1500.00",
            "discount_percentage": "10.00",
            "discount_amount": "750.00",
            "subtotal": "6750.00",
            "product": {
                "id": 10,
                "reference": "PROD-001",
                "designation_es": "Tornillo M6",
                "product_type": "article"
            }
        }
    """

    id: int
    quote_id: int
    discount_amount: Decimal
    subtotal: Decimal
    product: ProductSummary | None = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# QUOTE SCHEMAS
# ============================================================================

class QuoteBase(BaseModel):
    """Base schema for Quote with common fields."""

    quote_number: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Unique quote number (e.g., Q-2025-001)"
    )
    subject: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Quote subject or description"
    )
    revision: str = Field(
        default="A",
        min_length=1,
        max_length=10,
        description="Quote revision (A, B, C...)"
    )
    unit: str | None = Field(None, max_length=20, description="Unit (Unidad)")
    company_id: int = Field(..., gt=0, description="Customer company ID")
    company_rut_id: int | None = Field(None, gt=0, description="Company RUT ID")
    contact_id: int | None = Field(None, gt=0, description="Contact person ID")
    plant_id: int | None = Field(None, gt=0, description="Plant ID")
    staff_id: int = Field(..., gt=0, description="Sales person ID")
    status_id: int = Field(..., gt=0, description="Quote status ID")
    quote_date: date = Field(..., description="Quote creation date")
    valid_until: date | None = Field(None, description="Quote expiration date")
    shipping_date: date | None = Field(None, description="Estimated shipping date")
    incoterm_id: int | None = Field(None, gt=0, description="Incoterm ID")
    currency_id: int = Field(..., gt=0, description="Currency ID")
    exchange_rate: Decimal | None = Field(None, gt=0, description="Exchange rate")
    tax_percentage: Decimal = Field(
        default=Decimal("19.00"),
        ge=0,
        le=100,
        description="Tax percentage"
    )
    notes: str | None = Field(None, description="Customer-visible notes")
    internal_notes: str | None = Field(None, description="Internal notes only")

    @field_validator("quote_number", "revision")
    @classmethod
    def uppercase_fields(cls, v: str) -> str:
        """Convert quote_number and revision to uppercase."""
        return v.strip().upper()

    @field_validator("subject")
    @classmethod
    def subject_not_empty(cls, v: str) -> str:
        """Ensure subject is not just whitespace."""
        if not v.strip():
            raise ValueError("Subject cannot be empty")
        return v.strip()


class QuoteCreate(QuoteBase):
    """
    Schema for creating a new quote.

    Can optionally include line items (products).

    Example:
        data = QuoteCreate(
            quote_number="Q-2025-001",
            subject="New equipment quote",
            company_id=5,
            staff_id=2,
            status_id=1,
            quote_date=date.today(),
            currency_id=1,
            products=[
                QuoteProductCreate(product_id=10, quantity=5, unit_price=1500)
            ]
        )
    """

    products: list[QuoteProductCreate] | None = Field(
        default_factory=list,
        description="List of quote products (line items)"
    )


class QuoteUpdate(BaseModel):
    """
    Schema for updating a quote.

    All fields are optional - only provided fields will be updated.

    Note:
        To update products, use separate QuoteProduct endpoints.
        This schema only updates quote header fields.

    Example:
        data = QuoteUpdate(
            subject="Updated subject",
            valid_until=date(2025, 12, 31),
            status_id=2
        )
    """

    subject: str | None = Field(None, min_length=1, max_length=200)
    revision: str | None = Field(None, min_length=1, max_length=10)
    company_rut_id: int | None = Field(None, gt=0)
    contact_id: int | None = Field(None, gt=0)
    plant_id: int | None = Field(None, gt=0)
    staff_id: int | None = Field(None, gt=0)
    status_id: int | None = Field(None, gt=0)
    valid_until: date | None = None
    shipping_date: date | None = None
    incoterm_id: int | None = Field(None, gt=0)
    currency_id: int | None = Field(None, gt=0)
    exchange_rate: Decimal | None = Field(None, gt=0)
    tax_percentage: Decimal | None = Field(None, ge=0, le=100)
    notes: str | None = None
    internal_notes: str | None = None

    @field_validator("revision")
    @classmethod
    def uppercase_revision(cls, v: str | None) -> str | None:
        """Convert revision to uppercase."""
        return v.strip().upper() if v else None

    @field_validator("subject")
    @classmethod
    def subject_not_empty(cls, v: str | None) -> str | None:
        """Ensure subject is not just whitespace if provided."""
        if v and not v.strip():
            raise ValueError("Subject cannot be empty")
        return v.strip() if v else None


class QuoteResponse(QuoteBase):
    """
    Schema for quote response.

    Includes all fields plus calculated values and relationships.

    Example:
        {
            "id": 1,
            "quote_number": "Q-2025-001",
            "subject": "Equipment quote",
            "revision": "A",
            "company_id": 5,
            "staff_id": 2,
            "status_id": 1,
            "quote_date": "2025-01-15",
            "valid_until": "2025-02-15",
            "currency_id": 1,
            "subtotal": "10000.00",
            "tax_percentage": "19.00",
            "tax_amount": "1900.00",
            "total": "11900.00",
            "products": [...],
            "contact": {...},
            "company_rut": {...},
            "plant": {...},
            "staff": {...},
            "incoterm": {...},
            "created_at": "2025-01-15T10:30:00",
            "updated_at": "2025-01-15T10:30:00"
        }
    """

    id: int
    subtotal: Decimal
    tax_amount: Decimal
    total: Decimal
    products: list[QuoteProductResponse] = Field(default_factory=list)
    
    # Timestamps
    created_at: datetime | None = None
    updated_at: datetime | None = None
    
    # Related entities (expanded)
    contact: ContactSummary | None = None
    company_rut: CompanyRutSummary | None = None
    plant: PlantSummary | None = None
    staff: StaffSummary | None = None
    incoterm: IncotermSummary | None = None

    model_config = ConfigDict(from_attributes=True)


class QuoteListResponse(BaseModel):
    """
    Schema for quote list item (summary view).

    Lightweight response for list endpoints without products.

    Example:
        {
            "id": 1,
            "quote_number": "Q-2025-001",
            "subject": "Equipment quote",
            "company_id": 5,
            "quote_date": "2025-01-15",
            "total": "11900.00",
            "status_id": 1
        }
    """

    id: int
    quote_number: str
    subject: str
    revision: str
    company_id: int
    company_name: str | None = None
    staff_id: int
    status_id: int
    quote_date: date
    valid_until: date | None = None
    total: Decimal

    model_config = ConfigDict(from_attributes=True)
