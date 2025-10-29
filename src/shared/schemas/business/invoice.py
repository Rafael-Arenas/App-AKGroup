"""
Pydantic schemas for Invoice models.

Defines validation schemas for InvoiceSII and InvoiceExport.
"""

from datetime import date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict


# ============================================================================
# INVOICE SII SCHEMAS (Chilean domestic invoices)
# ============================================================================

class InvoiceSIIBase(BaseModel):
    """Base schema for InvoiceSII."""

    invoice_number: str = Field(..., min_length=1, max_length=50, description="SII invoice number (folio)")
    revision: str = Field(default="A", min_length=1, max_length=10, description="Invoice revision")
    invoice_type: str = Field(default="33", description="SII document type (33, 34, 56, 61, etc.)")
    order_id: int = Field(..., gt=0, description="Source order ID")
    company_id: int = Field(..., gt=0, description="Customer company ID")
    branch_id: Optional[int] = Field(None, gt=0, description="Customer branch ID")
    staff_id: int = Field(..., gt=0, description="Staff ID")
    payment_status_id: int = Field(..., gt=0, description="Payment status ID")
    invoice_date: date = Field(..., description="Invoice issue date")
    due_date: Optional[date] = Field(None, description="Payment due date")
    paid_date: Optional[date] = Field(None, description="Payment completion date")
    currency_id: int = Field(..., gt=0, description="Currency ID")
    exchange_rate: Optional[Decimal] = Field(None, gt=0, description="Exchange rate")
    subtotal: Decimal = Field(default=Decimal("0.00"), ge=0, description="Subtotal")
    tax_amount: Decimal = Field(default=Decimal("0.00"), ge=0, description="Tax amount")
    total: Decimal = Field(default=Decimal("0.00"), ge=0, description="Total")
    net_amount: Decimal = Field(default=Decimal("0.00"), ge=0, description="Net amount")
    exempt_amount: Decimal = Field(default=Decimal("0.00"), ge=0, description="Exempt amount")
    payment_terms: Optional[str] = Field(None, max_length=200, description="Payment terms")
    sii_status: Optional[str] = Field(None, max_length=50, description="SII status")
    sii_track_id: Optional[str] = Field(None, max_length=100, description="SII track ID")
    sii_xml: Optional[str] = Field(None, description="SII XML")
    notes: Optional[str] = Field(None, description="Notes")

    @field_validator("invoice_type")
    @classmethod
    def validate_invoice_type(cls, v: str) -> str:
        valid_types = {"33", "34", "56", "61", "39", "41"}
        if v not in valid_types:
            raise ValueError(f"Invoice type must be one of {valid_types}")
        return v


class InvoiceSIICreate(InvoiceSIIBase):
    """Schema for creating an SII invoice."""
    pass


class InvoiceSIIUpdate(BaseModel):
    """Schema for updating an SII invoice."""
    revision: Optional[str] = Field(None, min_length=1, max_length=10)
    payment_status_id: Optional[int] = Field(None, gt=0)
    due_date: Optional[date] = None
    paid_date: Optional[date] = None
    payment_terms: Optional[str] = Field(None, max_length=200)
    sii_status: Optional[str] = Field(None, max_length=50)
    sii_track_id: Optional[str] = Field(None, max_length=100)
    sii_xml: Optional[str] = None
    notes: Optional[str] = None


class InvoiceSIIResponse(InvoiceSIIBase):
    """Schema for SII invoice response."""
    id: int
    model_config = ConfigDict(from_attributes=True)


class InvoiceSIIListResponse(BaseModel):
    """Schema for SII invoice list item."""
    id: int
    invoice_number: str
    invoice_type: str
    company_id: int
    invoice_date: date
    total: Decimal
    payment_status_id: int
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# INVOICE EXPORT SCHEMAS
# ============================================================================

class InvoiceExportBase(BaseModel):
    """Base schema for InvoiceExport."""

    invoice_number: str = Field(..., min_length=1, max_length=50, description="Export invoice number")
    revision: str = Field(default="A", min_length=1, max_length=10, description="Invoice revision")
    invoice_type: str = Field(default="110", description="Export document type (110, 111, 112)")
    order_id: int = Field(..., gt=0, description="Source order ID")
    company_id: int = Field(..., gt=0, description="Foreign customer company ID")
    branch_id: Optional[int] = Field(None, gt=0, description="Customer branch ID")
    staff_id: int = Field(..., gt=0, description="Staff ID")
    payment_status_id: int = Field(..., gt=0, description="Payment status ID")
    invoice_date: date = Field(..., description="Invoice issue date")
    due_date: Optional[date] = Field(None, description="Payment due date")
    paid_date: Optional[date] = Field(None, description="Payment completion date")
    shipping_date: Optional[date] = Field(None, description="Goods shipping date")
    currency_id: int = Field(..., gt=0, description="Currency ID (USD, EUR)")
    exchange_rate: Decimal = Field(..., gt=0, description="Exchange rate to CLP")
    incoterm_id: int = Field(..., gt=0, description="Incoterm ID")
    country_id: int = Field(..., gt=0, description="Destination country ID")
    port_of_loading: Optional[str] = Field(None, max_length=100, description="Loading port")
    port_of_discharge: Optional[str] = Field(None, max_length=100, description="Discharge port")
    subtotal: Decimal = Field(default=Decimal("0.00"), ge=0, description="Subtotal")
    total: Decimal = Field(default=Decimal("0.00"), ge=0, description="Total")
    total_clp: Decimal = Field(default=Decimal("0.00"), ge=0, description="Total in CLP")
    freight_cost: Decimal = Field(default=Decimal("0.00"), ge=0, description="Freight cost")
    insurance_cost: Decimal = Field(default=Decimal("0.00"), ge=0, description="Insurance cost")
    payment_terms: Optional[str] = Field(None, max_length=200, description="Payment terms")
    letter_of_credit: Optional[str] = Field(None, max_length=100, description="Letter of credit")
    customs_declaration: Optional[str] = Field(None, max_length=100, description="Customs declaration")
    bill_of_lading: Optional[str] = Field(None, max_length=100, description="Bill of lading")
    notes: Optional[str] = Field(None, description="Notes")

    @field_validator("invoice_type")
    @classmethod
    def validate_invoice_type(cls, v: str) -> str:
        valid_types = {"110", "111", "112"}
        if v not in valid_types:
            raise ValueError(f"Export invoice type must be one of {valid_types}")
        return v


class InvoiceExportCreate(InvoiceExportBase):
    """Schema for creating an export invoice."""
    pass


class InvoiceExportUpdate(BaseModel):
    """Schema for updating an export invoice."""
    revision: Optional[str] = Field(None, min_length=1, max_length=10)
    payment_status_id: Optional[int] = Field(None, gt=0)
    due_date: Optional[date] = None
    paid_date: Optional[date] = None
    shipping_date: Optional[date] = None
    payment_terms: Optional[str] = Field(None, max_length=200)
    letter_of_credit: Optional[str] = Field(None, max_length=100)
    customs_declaration: Optional[str] = Field(None, max_length=100)
    bill_of_lading: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class InvoiceExportResponse(InvoiceExportBase):
    """Schema for export invoice response."""
    id: int
    model_config = ConfigDict(from_attributes=True)


class InvoiceExportListResponse(BaseModel):
    """Schema for export invoice list item."""
    id: int
    invoice_number: str
    invoice_type: str
    company_id: int
    country_id: int
    invoice_date: date
    total: Decimal
    total_clp: Decimal
    payment_status_id: int
    model_config = ConfigDict(from_attributes=True)
