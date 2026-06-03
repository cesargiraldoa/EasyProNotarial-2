from __future__ import annotations

import json
from typing import Any

from app.models.case import Case
from app.schemas.billing import GariBillingCustomer, GariBillingLine

DEFAULT_LINE_CODE = "SERV-NOTARIAL-001"
DEFAULT_LINE_DESCRIPTION = "Servicio notarial"
DEFAULT_LINE_UNIT_PRICE = 100000
DEFAULT_LINE_TAX_RATE = 19
DEFAULT_LINE_UNIT_MEASURE = "NIU"
SOURCE_SYSTEM = "easypro"
ALLOWED_DOCUMENT_TYPES = {"minuta", "escritura", "otro"}
ALLOWED_CUSTOMER_DOCUMENT_TYPES = {"CC", "NIT", "CE", "PASAPORTE", "OTRO"}


def _safe_json_loads(value: str | None) -> dict[str, Any]:
    if not value or not value.strip():
        return {}
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _first_non_empty(*values: Any) -> str:
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return ""


def _normalize_customer_kind(value: Any) -> str:
    normalized = _first_non_empty(value).strip().lower()
    return "juridica" if normalized in {"juridica", "juridical", "legal"} else "natural"


def _normalize_customer_document_type(value: Any) -> str:
    normalized = _first_non_empty(value).strip().upper()
    return normalized if normalized in ALLOWED_CUSTOMER_DOCUMENT_TYPES else "OTRO"


def _resolve_document_type(case: Case, document_type: str | None = None) -> str:
    candidate = _first_non_empty(document_type).strip().lower()
    if candidate in ALLOWED_DOCUMENT_TYPES:
        return candidate

    metadata = _safe_json_loads(case.metadata_json)
    metadata_document_type = _first_non_empty(metadata.get("billing_document_type")).strip().lower()
    if metadata_document_type in ALLOWED_DOCUMENT_TYPES:
        return metadata_document_type

    template_document_type = _first_non_empty(case.template.document_type if case.template else None).strip().lower()
    if template_document_type in ALLOWED_DOCUMENT_TYPES:
        return template_document_type

    if case.case_type.strip().lower() == "escritura":
        return "escritura"
    if case.act_type.strip():
        return "minuta"
    return "otro"


def _normalize_customer(customer: GariBillingCustomer | dict[str, Any] | None, case: Case) -> dict[str, Any]:
    if customer is None:
        metadata = _safe_json_loads(case.metadata_json)
        metadata_customer = metadata.get("billing_customer") if isinstance(metadata.get("billing_customer"), dict) else None
        if metadata_customer:
            customer = metadata_customer

    if customer is None:
        raise ValueError("Debes configurar billing_customer para este caso.")

    customer_payload = customer.model_dump() if isinstance(customer, GariBillingCustomer) else dict(customer)

    document_number = _first_non_empty(customer_payload.get("document_number"))
    legal_name = _first_non_empty(customer_payload.get("legal_name"))
    if not document_number:
        raise ValueError("El pagador debe incluir document_number.")
    if not legal_name:
        raise ValueError("El pagador debe incluir legal_name.")

    return {
        "customer_kind": _normalize_customer_kind(customer_payload.get("customer_kind")),
        "document_type": _normalize_customer_document_type(customer_payload.get("document_type")),
        "document_number": document_number,
        "legal_name": legal_name,
        "trade_name": _first_non_empty(customer_payload.get("trade_name")) or None,
        "email": _first_non_empty(customer_payload.get("email")) or None,
        "phone": _first_non_empty(customer_payload.get("phone")) or None,
        "address": _first_non_empty(customer_payload.get("address")) or None,
        "payment_percentage": customer_payload.get("payment_percentage"),
        "payment_amount": customer_payload.get("payment_amount"),
    }


def _normalize_lines(lines: list[GariBillingLine] | list[dict[str, Any]] | None, case: Case) -> list[dict[str, Any]]:
    metadata = _safe_json_loads(case.metadata_json)
    if lines is None:
        metadata_lines = metadata.get("billing_lines")
        if isinstance(metadata_lines, list) and metadata_lines:
            lines = metadata_lines

    if not lines:
        raise ValueError("Debes configurar billing_lines para este caso.")

    normalized_lines: list[dict[str, Any]] = []
    for item in lines:
        line_payload = item.model_dump() if isinstance(item, GariBillingLine) else dict(item or {})

        code = _first_non_empty(line_payload.get("code"), DEFAULT_LINE_CODE)
        description = _first_non_empty(line_payload.get("description"), DEFAULT_LINE_DESCRIPTION)
        quantity = float(line_payload.get("quantity") or 0)
        unit_price = float(line_payload.get("unit_price") or 0)
        discount_amount = float(line_payload.get("discount_amount") or 0)
        tax_rate = float(line_payload.get("tax_rate") or 0)
        unit_measure = _first_non_empty(line_payload.get("unit_measure"), DEFAULT_LINE_UNIT_MEASURE)

        if not code:
            raise ValueError("Cada servicio debe incluir code.")
        if not description:
            raise ValueError("Cada servicio debe incluir description.")
        if quantity <= 0:
            raise ValueError(f"El servicio {code} debe tener quantity mayor que cero.")
        if unit_price < 0:
            raise ValueError(f"El servicio {code} debe tener unit_price mayor o igual a cero.")
        if discount_amount < 0:
            raise ValueError(f"El servicio {code} debe tener discount_amount mayor o igual a cero.")
        if tax_rate < 0:
            raise ValueError(f"El servicio {code} debe tener tax_rate mayor o igual a cero.")

        normalized_lines.append(
            {
                "code": code,
                "description": description,
                "quantity": quantity,
                "unit_price": unit_price,
                "discount_amount": discount_amount,
                "tax_rate": tax_rate,
                "unit_measure": unit_measure,
            }
        )

    if not normalized_lines:
        raise ValueError("Debes configurar billing_lines para este caso.")
    return normalized_lines


def build_gari_billing_invoice_payload(
    case: Case,
    emit_mode: str = "draft",
    billing_customer: GariBillingCustomer | dict[str, Any] | None = None,
    billing_lines: list[GariBillingLine] | list[dict[str, Any]] | None = None,
    document_id: int | None = None,
    version_id: int | None = None,
    document_type: str | None = None,
) -> dict[str, Any]:
    metadata = _safe_json_loads(case.metadata_json)
    external_reference = f"case_{case.id}"
    customer_payload = _normalize_customer(billing_customer, case)
    lines_payload = _normalize_lines(billing_lines, case)
    resolved_document_type = _resolve_document_type(case, document_type)

    payload = {
        "source_system": SOURCE_SYSTEM,
        "external_reference": external_reference,
        "idempotency_key": f"easypro-{external_reference}",
        "emit_mode": emit_mode or "draft",
        "customer": customer_payload,
        "lines": lines_payload,
        "metadata": {
            "case_id": case.id,
            "document_type": resolved_document_type,
            "source_system": SOURCE_SYSTEM,
            "case_type": case.case_type,
            "act_type": case.act_type,
            "notary_id": case.notary_id,
            "notary_label": case.notary.notary_label if case.notary else None,
            "document_id": document_id,
            "version_id": version_id,
        },
    }
    if metadata:
        payload["metadata"]["case_metadata"] = metadata
    return payload
