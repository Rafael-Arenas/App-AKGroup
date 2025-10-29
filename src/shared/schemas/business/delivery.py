"""
Pydantic schemas for Delivery models.

Defines validation schemas for DeliveryOrder, Transport, and PaymentCondition.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict


# ============================================================================
# DELIVERY ORDER SCHEMAS
# ============================================================================

class DeliveryOrderBase(BaseModel):
    """Base schema for DeliveryOrder with common fields."""

    delivery_number: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Unique delivery number (e.g., GD-2025-001)"
    )
    revision: str = Field(
        default="A",
        min_length=1,
        max_length=10,
        description="Delivery revision (A, B, C...)"
    )
    order_id: int = Field(..., gt=0, description="Source order ID")
    company_id: int = Field(..., gt=0, description="Customer company ID")
    address_id: int = Field(..., gt=0, description="Delivery address ID")
    transport_id: Optional[int] = Field(None, gt=0, description="Transport/carrier ID")
    staff_id: int = Field(..., gt=0, description="Staff responsible ID")
    delivery_date: date = Field(..., description="Planned delivery date")
    actual_delivery_date: Optional[date] = Field(None, description="Actual delivery date")
    status: str = Field(
        default="pending",
        description="Delivery status (pending, in_transit, delivered, cancelled)"
    )
    tracking_number: Optional[str] = Field(None, max_length=100, description="Carrier tracking number")
    delivery_instructions: Optional[str] = Field(None, description="Special delivery instructions")
    signature_name: Optional[str] = Field(None, max_length=200, description="Recipient name")
    signature_id: Optional[str] = Field(None, max_length=50, description="Recipient ID")
    signature_datetime: Optional[datetime] = Field(None, description="Receipt datetime")
    notes: Optional[str] = Field(None, description="Additional notes")

    @field_validator("delivery_number", "revision")
    @classmethod
    def uppercase_fields(cls, v: str) -> str:
        """Convert to uppercase."""
        return v.strip().upper()

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status is valid."""
        valid_statuses = {"pending", "in_transit", "delivered", "cancelled"}
        if v.lower() not in valid_statuses:
            raise ValueError(f"Status must be one of {valid_statuses}")
        return v.lower()


class DeliveryOrderCreate(DeliveryOrderBase):
    """
    Schema for creating a delivery order.

    Example:
        data = DeliveryOrderCreate(
            delivery_number="GD-2025-001",
            order_id=10,
            company_id=5,
            address_id=3,
            staff_id=2,
            delivery_date=date.today()
        )
    """

    pass


class DeliveryOrderUpdate(BaseModel):
    """
    Schema for updating a delivery order.

    All fields are optional.
    """

    revision: Optional[str] = Field(None, min_length=1, max_length=10)
    address_id: Optional[int] = Field(None, gt=0)
    transport_id: Optional[int] = Field(None, gt=0)
    staff_id: Optional[int] = Field(None, gt=0)
    delivery_date: Optional[date] = None
    actual_delivery_date: Optional[date] = None
    status: Optional[str] = None
    tracking_number: Optional[str] = Field(None, max_length=100)
    delivery_instructions: Optional[str] = None
    signature_name: Optional[str] = Field(None, max_length=200)
    signature_id: Optional[str] = Field(None, max_length=50)
    signature_datetime: Optional[datetime] = None
    notes: Optional[str] = None

    @field_validator("revision")
    @classmethod
    def uppercase_revision(cls, v: Optional[str]) -> Optional[str]:
        """Convert to uppercase."""
        return v.strip().upper() if v else None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate status is valid."""
        if v:
            valid_statuses = {"pending", "in_transit", "delivered", "cancelled"}
            if v.lower() not in valid_statuses:
                raise ValueError(f"Status must be one of {valid_statuses}")
            return v.lower()
        return v


class DeliveryOrderResponse(DeliveryOrderBase):
    """Schema for delivery order response."""

    id: int

    model_config = ConfigDict(from_attributes=True)


class DeliveryOrderListResponse(BaseModel):
    """Schema for delivery order list item (summary view)."""

    id: int
    delivery_number: str
    revision: str
    order_id: int
    company_id: int
    delivery_date: date
    actual_delivery_date: Optional[date] = None
    status: str

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# TRANSPORT SCHEMAS
# ============================================================================

class TransportBase(BaseModel):
    """Base schema for Transport."""

    name: str = Field(..., min_length=1, max_length=200, description="Transport company name")
    delivery_number: Optional[str] = Field(None, max_length=100, description="Delivery reference number")
    transport_type: str = Field(
        default="carrier",
        description="Type: own, carrier, courier, freight_forwarder"
    )
    contact_name: Optional[str] = Field(None, max_length=200, description="Contact person")
    contact_phone: Optional[str] = Field(None, max_length=50, description="Contact phone")
    contact_email: Optional[str] = Field(None, max_length=100, description="Contact email")
    website: Optional[str] = Field(None, max_length=200, description="Company website")
    notes: Optional[str] = Field(None, description="Additional notes")

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        """Ensure name is not empty."""
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()

    @field_validator("transport_type")
    @classmethod
    def validate_transport_type(cls, v: str) -> str:
        """Validate transport type."""
        valid_types = {"own", "carrier", "courier", "freight_forwarder"}
        if v.lower() not in valid_types:
            raise ValueError(f"Transport type must be one of {valid_types}")
        return v.lower()


class TransportCreate(TransportBase):
    """Schema for creating a transport."""

    pass


class TransportUpdate(BaseModel):
    """Schema for updating a transport."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    delivery_number: Optional[str] = Field(None, max_length=100)
    transport_type: Optional[str] = None
    contact_name: Optional[str] = Field(None, max_length=200)
    contact_phone: Optional[str] = Field(None, max_length=50)
    contact_email: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """Ensure name is not empty if provided."""
        if v and not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip() if v else None

    @field_validator("transport_type")
    @classmethod
    def validate_transport_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate transport type."""
        if v:
            valid_types = {"own", "carrier", "courier", "freight_forwarder"}
            if v.lower() not in valid_types:
                raise ValueError(f"Transport type must be one of {valid_types}")
            return v.lower()
        return v


class TransportResponse(TransportBase):
    """Schema for transport response."""

    id: int

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# PAYMENT CONDITION SCHEMAS
# ============================================================================

class PaymentConditionBase(BaseModel):
    """Base schema for PaymentCondition."""

    code: str = Field(..., min_length=1, max_length=20, description="Code (e.g., NET30, COD)")
    name: str = Field(..., min_length=1, max_length=100, description="Payment condition name")
    revision: str = Field(default="A", min_length=1, max_length=10, description="Revision")
    description: Optional[str] = Field(None, description="Detailed description")
    days_to_pay: Optional[int] = Field(None, ge=0, description="Days for payment")
    percentage_advance: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        le=100,
        description="Advance payment %"
    )
    percentage_on_delivery: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        le=100,
        description="On delivery %"
    )
    percentage_after_delivery: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        le=100,
        description="After delivery %"
    )
    days_after_delivery: Optional[int] = Field(None, ge=0, description="Days after delivery")
    is_default: bool = Field(default=False, description="Is default condition")
    notes: Optional[str] = Field(None, description="Additional notes")

    @field_validator("code", "revision")
    @classmethod
    def uppercase_fields(cls, v: str) -> str:
        """Convert to uppercase."""
        return v.strip().upper()

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        """Ensure name is not empty."""
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()


class PaymentConditionCreate(PaymentConditionBase):
    """Schema for creating a payment condition."""

    pass


class PaymentConditionUpdate(BaseModel):
    """Schema for updating a payment condition."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    revision: Optional[str] = Field(None, min_length=1, max_length=10)
    description: Optional[str] = None
    days_to_pay: Optional[int] = Field(None, ge=0)
    percentage_advance: Optional[Decimal] = Field(None, ge=0, le=100)
    percentage_on_delivery: Optional[Decimal] = Field(None, ge=0, le=100)
    percentage_after_delivery: Optional[Decimal] = Field(None, ge=0, le=100)
    days_after_delivery: Optional[int] = Field(None, ge=0)
    is_default: Optional[bool] = None
    notes: Optional[str] = None

    @field_validator("revision")
    @classmethod
    def uppercase_revision(cls, v: Optional[str]) -> Optional[str]:
        """Convert to uppercase."""
        return v.strip().upper() if v else None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """Ensure name is not empty if provided."""
        if v and not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip() if v else None


class PaymentConditionResponse(PaymentConditionBase):
    """Schema for payment condition response."""

    id: int

    model_config = ConfigDict(from_attributes=True)
