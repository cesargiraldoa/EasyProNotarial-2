from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


EmitMode = Literal["draft", "ready", "stub", "matias_sandbox"]


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
