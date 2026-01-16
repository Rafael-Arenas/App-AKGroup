from __future__ import annotations

"""
Pydantic schemas for Delivery models.

Defines validation schemas for DeliveryOrder, Transport, and PaymentCondition.
"""

from datetime import date, datetime
from decimal import Decimal
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
    transport_id: int | None = Field(None, gt=0, description="Transport/carrier ID")
    staff_id: int = Field(..., gt=0, description="Staff responsible ID")
    delivery_date: date = Field(..., description="Planned delivery date")
    actual_delivery_date: date | None = Field(None, description="Actual delivery date")
    status: str = Field(
        default="pending",
        description="Delivery status (pending, in_transit, delivered, cancelled)"
    )
    tracking_number: str | None = Field(None, max_length=100, description="Carrier tracking number")
    delivery_instructions: str | None = Field(None, description="Special delivery instructions")
    signature_name: str | None = Field(None, max_length=200, description="Recipient name")
    signature_id: str | None = Field(None, max_length=50, description="Recipient ID")
    signature_datetime: datetime | None = Field(None, description="Receipt datetime")
    notes: str | None = Field(None, description="Additional notes")

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

    revision: str | None = Field(None, min_length=1, max_length=10)
    address_id: int | None = Field(None, gt=0)
    transport_id: int | None = Field(None, gt=0)
    staff_id: int | None = Field(None, gt=0)
    delivery_date: date | None = None
    actual_delivery_date: date | None = None
    status: str | None = None
    tracking_number: str | None = Field(None, max_length=100)
    delivery_instructions: str | None = None
    signature_name: str | None = Field(None, max_length=200)
    signature_id: str | None = Field(None, max_length=50)
    signature_datetime: datetime | None = None
    notes: str | None = None

    @field_validator("revision")
    @classmethod
    def uppercase_revision(cls, v: str | None) -> str | None:
        """Convert to uppercase."""
        return v.strip().upper() if v else None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
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
    actual_delivery_date: date | None = None
    status: str

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# TRANSPORT SCHEMAS
# ============================================================================

class TransportBase(BaseModel):
    """Base schema for Transport."""

    name: str = Field(..., min_length=1, max_length=200, description="Transport company name")
    delivery_number: str | None = Field(None, max_length=100, description="Delivery reference number")
    transport_type: str = Field(
        default="carrier",
        description="Type: own, carrier, courier, freight_forwarder"
    )
    contact_name: str | None = Field(None, max_length=200, description="Contact person")
    contact_phone: str | None = Field(None, max_length=50, description="Contact phone")
    contact_email: str | None = Field(None, max_length=100, description="Contact email")
    website: str | None = Field(None, max_length=200, description="Company website")
    notes: str | None = Field(None, description="Additional notes")

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

    name: str | None = Field(None, min_length=1, max_length=200)
    delivery_number: str | None = Field(None, max_length=100)
    transport_type: str | None = None
    contact_name: str | None = Field(None, max_length=200)
    contact_phone: str | None = Field(None, max_length=50)
    contact_email: str | None = Field(None, max_length=100)
    website: str | None = Field(None, max_length=200)
    notes: str | None = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str | None) -> str | None:
        """Ensure name is not empty if provided."""
        if v and not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip() if v else None

    @field_validator("transport_type")
    @classmethod
    def validate_transport_type(cls, v: str | None) -> str | None:
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
# PAYMENT TYPE SCHEMAS
# ============================================================================

class PaymentTypeBase(BaseModel):
    """Base schema for PaymentType."""

    code: str = Field(..., min_length=1, max_length=20, description="Payment type code (e.g., 30D, 60D, CASH)")
    name: str = Field(..., min_length=1, max_length=50, description="Display name")
    days: int = Field(default=0, ge=0, description="Number of days for this payment type")
    description: str | None = Field(None, description="Detailed description")

    @field_validator("code")
    @classmethod
    def uppercase_code(cls, v: str) -> str:
        """Convert code to uppercase."""
        return v.strip().upper()


class PaymentTypeCreate(PaymentTypeBase):
    """Schema for creating a payment type."""

    pass


class PaymentTypeUpdate(BaseModel):
    """Schema for updating a payment type."""

    code: str | None = Field(None, min_length=1, max_length=20)
    name: str | None = Field(None, min_length=1, max_length=50)
    days: int | None = Field(None, ge=0)
    description: str | None = None

    @field_validator("code")
    @classmethod
    def uppercase_code(cls, v: str | None) -> str | None:
        """Convert code to uppercase if provided."""
        return v.strip().upper() if v else None


class PaymentTypeResponse(PaymentTypeBase):
    """Schema for payment type response."""

    id: int

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# PAYMENT CONDITION SCHEMAS
# ============================================================================

class PaymentConditionBase(BaseModel):
    """Base schema for PaymentCondition."""

    payment_condition_number: str = Field(..., min_length=1, max_length=20, description="Short number/code (e.g., 001, NET30, COD)")
    name: str = Field(..., min_length=1, max_length=100, description="Payment condition name")
    revision: str = Field(default="A", min_length=1, max_length=10, description="Revision")
    description: str | None = Field(None, description="Detailed description")
    payment_type_id: int = Field(..., gt=0, description="Payment type ID")
    days_to_pay: int | None = Field(None, ge=0, description="Days for payment")
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
    days_after_delivery: int | None = Field(None, ge=0, description="Days after delivery")
    is_default: bool = Field(default=False, description="Is default condition")
    notes: str | None = Field(None, description="Additional notes")

    @field_validator("payment_condition_number", "revision")
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

    name: str | None = Field(None, min_length=1, max_length=100)
    revision: str | None = Field(None, min_length=1, max_length=10)
    description: str | None = None
    payment_type_id: int | None = Field(None, gt=0)
    days_to_pay: int | None = Field(None, ge=0)
    percentage_advance: Decimal | None = Field(None, ge=0, le=100)
    percentage_on_delivery: Decimal | None = Field(None, ge=0, le=100)
    percentage_after_delivery: Decimal | None = Field(None, ge=0, le=100)
    days_after_delivery: int | None = Field(None, ge=0)
    is_default: bool | None = None
    notes: str | None = None

    @field_validator("revision")
    @classmethod
    def uppercase_revision(cls, v: str | None) -> str | None:
        """Convert to uppercase."""
        return v.strip().upper() if v else None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str | None) -> str | None:
        """Ensure name is not empty if provided."""
        if v and not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip() if v else None


class PaymentConditionResponse(PaymentConditionBase):
    """Schema for payment condition response."""

    id: int
    payment_type: PaymentTypeResponse | None = None

    model_config = ConfigDict(from_attributes=True)
