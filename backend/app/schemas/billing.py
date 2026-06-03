from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, EmailStr


EmitMode = Literal["draft", "ready", "stub", "matias_sandbox"]
BillingCustomerKind = Literal["natural", "juridica"]
BillingDocumentType = Literal["CC", "NIT", "CE", "PASAPORTE", "OTRO"]
BillingCalculationMode = Literal["fixed", "manual", "by_document_amount"]


class GariBillingCustomer(BaseModel):
    customer_kind: BillingCustomerKind
    document_type: BillingDocumentType
    document_number: str = Field(min_length=3, max_length=40)
    legal_name: str = Field(min_length=2, max_length=200)
    trade_name: str | None = Field(default=None, max_length=200)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=40)
    address: str | None = Field(default=None, max_length=255)
    payment_percentage: float | None = Field(default=None, ge=0, le=100)
    payment_amount: float | None = Field(default=None, ge=0)


class GariBillingLine(BaseModel):
    code: str = Field(min_length=3, max_length=80)
    description: str = Field(min_length=2, max_length=255)
    quantity: float = Field(gt=0)
    unit_price: float = Field(ge=0)
    discount_amount: float = Field(default=0, ge=0)
    tax_rate: float = Field(default=0, ge=0)
    unit_measure: str = Field(default="NIU", min_length=1, max_length=20)
    editable: bool = True
    calculation_mode: BillingCalculationMode = "fixed"


class GariBillingInvoiceResult(BaseModel):
    model_config = ConfigDict(extra="allow")

    source_system: str | None = None
    external_reference: str | None = None
    idempotency_key: str | None = None
    emit_mode: EmitMode | None = None
    invoice_id: str | int | None = None
    status: str | None = None
    full_number: str | None = None
    total: float | int | None = None
    error_message: str | None = None
    gari_response: dict[str, Any] = Field(default_factory=dict)


class GariBillingFromCaseRequest(BaseModel):
    emit_mode: EmitMode | None = None
    billing_customer: GariBillingCustomer | None = None
    billing_lines: list[GariBillingLine] | None = None
    document_id: int | None = None
    version_id: int | None = None
    document_type: str | None = None
