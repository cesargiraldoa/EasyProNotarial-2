from __future__ import annotations

import json
from typing import Any

from app.models.case import Case

DEFAULT_LINE_CODE = "SERV-NOTARIAL-001"
DEFAULT_LINE_DESCRIPTION = "Servicio notarial"
DEFAULT_LINE_UNIT_PRICE = 100000
DEFAULT_LINE_TAX_RATE = 19
DEFAULT_LINE_UNIT_MEASURE = "NIU"
SOURCE_SYSTEM = "easypro"


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


def _normalize_document_type(document_type: str | None) -> str:
    normalized = _first_non_empty(document_type).upper()
    if normalized in {"NIT", "CC"}:
        return normalized
    return "CC"


def _build_customer_from_case(case: Case) -> dict[str, Any]:
    metadata = _safe_json_loads(case.metadata_json)
    metadata_customer = metadata.get("billing_customer") if isinstance(metadata.get("billing_customer"), dict) else {}

    if case.participants:
        participant = case.participants[0]
        person = participant.person
        legal_entity = participant.legal_entity
        if legal_entity is not None:
            legal_name = _first_non_empty(legal_entity.name)
            return {
                "customer_kind": "juridica",
                "document_type": "NIT",
                "document_number": _first_non_empty(legal_entity.nit),
                "legal_name": legal_name,
                "trade_name": _first_non_empty(legal_entity.name, legal_name),
                "email": _first_non_empty(legal_entity.email),
                "phone": _first_non_empty(legal_entity.phone),
                "address": _first_non_empty(legal_entity.address),
            }

        if person is not None:
            legal_name = _first_non_empty(person.full_name)
            return {
                "customer_kind": "natural",
                "document_type": _normalize_document_type(person.document_type),
                "document_number": _first_non_empty(person.document_number),
                "legal_name": legal_name,
                "trade_name": _first_non_empty(metadata_customer.get("trade_name"), legal_name),
                "email": _first_non_empty(person.email),
                "phone": _first_non_empty(person.phone),
                "address": _first_non_empty(person.address),
            }

    if metadata_customer:
        customer_kind = _first_non_empty(metadata_customer.get("customer_kind")).lower() or "natural"
        document_type = _normalize_document_type(metadata_customer.get("document_type"))
        legal_name = _first_non_empty(metadata_customer.get("legal_name"), metadata_customer.get("trade_name"))
        return {
            "customer_kind": "juridica" if customer_kind in {"juridica", "juridical", "legal"} else "natural",
            "document_type": document_type,
            "document_number": _first_non_empty(metadata_customer.get("document_number")),
            "legal_name": legal_name,
            "trade_name": _first_non_empty(metadata_customer.get("trade_name"), legal_name),
            "email": _first_non_empty(metadata_customer.get("email")),
            "phone": _first_non_empty(metadata_customer.get("phone")),
            "address": _first_non_empty(metadata_customer.get("address")),
        }

    raise ValueError("No hay datos suficientes para construir el cliente de facturación.")


def _build_lines_from_case(case: Case) -> list[dict[str, Any]]:
    metadata = _safe_json_loads(case.metadata_json)
    lines = metadata.get("billing_lines")
    if isinstance(lines, list) and lines:
        normalized_lines: list[dict[str, Any]] = []
        for item in lines:
            if not isinstance(item, dict):
                continue
            normalized_lines.append(
                {
                    "code": _first_non_empty(item.get("code"), DEFAULT_LINE_CODE),
                    "description": _first_non_empty(item.get("description"), DEFAULT_LINE_DESCRIPTION),
                    "quantity": int(item.get("quantity") or 1),
                    "unit_price": int(item.get("unit_price") or DEFAULT_LINE_UNIT_PRICE),
                    "discount_amount": int(item.get("discount_amount") or 0),
                    "tax_rate": int(item.get("tax_rate") or DEFAULT_LINE_TAX_RATE),
                    "unit_measure": _first_non_empty(item.get("unit_measure"), DEFAULT_LINE_UNIT_MEASURE),
                }
            )
        if normalized_lines:
            return normalized_lines

    return [
        {
            "code": DEFAULT_LINE_CODE,
            "description": DEFAULT_LINE_DESCRIPTION,
            "quantity": 1,
            "unit_price": DEFAULT_LINE_UNIT_PRICE,
            "discount_amount": 0,
            "tax_rate": DEFAULT_LINE_TAX_RATE,
            "unit_measure": DEFAULT_LINE_UNIT_MEASURE,
        }
    ]


def build_gari_billing_invoice_payload(case: Case, emit_mode: str = "draft") -> dict[str, Any]:
    metadata = _safe_json_loads(case.metadata_json)
    external_reference = f"case_{case.id}"
    payload = {
        "source_system": SOURCE_SYSTEM,
        "external_reference": external_reference,
        "idempotency_key": f"easypro-{external_reference}",
        "emit_mode": emit_mode or "draft",
        "customer": _build_customer_from_case(case),
        "lines": _build_lines_from_case(case),
        "metadata": {
            "case_id": case.id,
            "document_type": "minuta",
            "source_system": SOURCE_SYSTEM,
            "case_type": case.case_type,
            "act_type": case.act_type,
            "notary_id": case.notary_id,
            "notary_label": case.notary.notary_label if case.notary else None,
        },
    }
    if metadata:
        payload["metadata"]["case_metadata"] = metadata
    return payload
