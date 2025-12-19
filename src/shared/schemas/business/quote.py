"""
Pydantic schemas for Quote and QuoteProduct models.

Defines validation schemas for creating, updating, and returning
quote data through the API.
"""

from datetime import date
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict

from src.shared.schemas.base import BaseSchema


# ============================================================================
# QUOTE PRODUCT SCHEMAS
# ============================================================================

class QuoteProductBase(BaseModel):
    """Base schema for QuoteProduct with common fields."""

    product_id: int = Field(..., gt=0, description="Product ID")
    sequence: int = Field(default=1, ge=1, description="Display order")
    quantity: Decimal = Field(..., gt=0, description="Quantity ordered")
    unit_price: Decimal = Field(..., ge=0, description="Price per unit")
    discount_percentage: Optional[Decimal] = Field(
        default=Decimal("0.00"),
        ge=0,
        le=100,
        description="Discount percentage"
    )
    notes: Optional[str] = Field(None, max_length=1000, description="Line item notes")


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

    product_id: Optional[int] = Field(None, gt=0)
    sequence: Optional[int] = Field(None, ge=1)
    quantity: Optional[Decimal] = Field(None, gt=0)
    unit_price: Optional[Decimal] = Field(None, ge=0)
    discount_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    notes: Optional[str] = Field(None, max_length=1000)


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
            "subtotal": "6750.00"
        }
    """

    id: int
    quote_id: int
    discount_amount: Decimal
    subtotal: Decimal

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
    unit: Optional[str] = Field(None, max_length=20, description="Unit (Unidad)")
    company_id: int = Field(..., gt=0, description="Customer company ID")
    company_rut_id: Optional[int] = Field(None, gt=0, description="Company RUT ID")
    contact_id: Optional[int] = Field(None, gt=0, description="Contact person ID")
    plant_id: Optional[int] = Field(None, gt=0, description="Plant ID")
    staff_id: int = Field(..., gt=0, description="Sales person ID")
    status_id: int = Field(..., gt=0, description="Quote status ID")
    quote_date: date = Field(..., description="Quote creation date")
    valid_until: Optional[date] = Field(None, description="Quote expiration date")
    shipping_date: Optional[date] = Field(None, description="Estimated shipping date")
    incoterm_id: Optional[int] = Field(None, gt=0, description="Incoterm ID")
    currency_id: int = Field(..., gt=0, description="Currency ID")
    exchange_rate: Optional[Decimal] = Field(None, gt=0, description="Exchange rate")
    tax_percentage: Decimal = Field(
        default=Decimal("19.00"),
        ge=0,
        le=100,
        description="Tax percentage"
    )
    notes: Optional[str] = Field(None, description="Customer-visible notes")
    internal_notes: Optional[str] = Field(None, description="Internal notes only")

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

    products: Optional[List[QuoteProductCreate]] = Field(
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

    subject: Optional[str] = Field(None, min_length=1, max_length=200)
    revision: Optional[str] = Field(None, min_length=1, max_length=10)
    contact_id: Optional[int] = Field(None, gt=0)
    plant_id: Optional[int] = Field(None, gt=0)
    staff_id: Optional[int] = Field(None, gt=0)
    status_id: Optional[int] = Field(None, gt=0)
    valid_until: Optional[date] = None
    shipping_date: Optional[date] = None
    incoterm_id: Optional[int] = Field(None, gt=0)
    currency_id: Optional[int] = Field(None, gt=0)
    exchange_rate: Optional[Decimal] = Field(None, gt=0)
    tax_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    notes: Optional[str] = None
    internal_notes: Optional[str] = None

    @field_validator("revision")
    @classmethod
    def uppercase_revision(cls, v: Optional[str]) -> Optional[str]:
        """Convert revision to uppercase."""
        return v.strip().upper() if v else None

    @field_validator("subject")
    @classmethod
    def subject_not_empty(cls, v: Optional[str]) -> Optional[str]:
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
            "products": [...]
        }
    """

    id: int
    subtotal: Decimal
    tax_amount: Decimal
    total: Decimal
    products: List[QuoteProductResponse] = Field(default_factory=list)

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
    staff_id: int
    status_id: int
    quote_date: date
    valid_until: Optional[date] = None
    total: Decimal

    model_config = ConfigDict(from_attributes=True)
