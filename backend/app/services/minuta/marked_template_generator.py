from __future__ import annotations

import re
from pathlib import Path

from app.services.minuta.engine import NotarialDocumentEngine
from app.services.minuta.engine.notarial_document_engine import NotarialRenderBlockedError
from app.services.minuta.rules.common_rules import normalize_key, normalize_value
from app.services.minuta.rules.gender_rules import validate_gender_concordance as _validate_gender_concordance_issues
from app.services.minuta.rules.money_rules import format_money_value as _format_money_value
from app.services.minuta.rules.money_rules import is_money_field as _is_money_field

SECOND_BUYER_KEYS = {
    "nombre_comprador_2",
    "tipo_documento_comprador_2",
    "numero_documento_comprador_2",
    "comprador_2_es_hombre_o_mujer",
    "nacionalidad_comprador_2",
    "municipio_domicilio_comprador_2",
    "estado_civil_comprador_2",
    "direccion_comprador_2",
    "celular_comprador_2",
    "email_comprador_2",
    "profesion_u_oficio_comprador_2",
    "actividad_economica_comprador_2",
}


def is_second_buyer_empty(normalized_values: dict[str, str]) -> bool:
    return all(not normalize_value(normalized_values.get(key, "")) for key in SECOND_BUYER_KEYS)


def cleanup_empty_second_buyer_text(text: str) -> str:
    if not text:
        return text
    line = text.replace("\xa0", " ")
    empty_label = re.compile(
        r"^(?:DIRECCI[ÓO]N|CELULAR|CORREO|PROFESI[ÓO]N\s+U\s+OFICIO|ACTIVIDAD\s+ECON[ÓO]MICA|ESTADO\s+CIVIL)\s*:\s*\.?\s*$",
        re.IGNORECASE,
    )
    if empty_label.match(line.strip()):
        return ""
    replacements = [
        (r"\s+y\s*-\s*-\s*", ""),
        (r"\s+y\s*,\s*de las condiciones", " de las condiciones"),
        (r"\s+y\s*,\s*identificado", ", identificado"),
        (r"\s+y\s*,\s*quien", " quien"),
        (r"\s+y\s*,\s*respectivamente", ""),
        (r",\s*respectivamente", ""),
        (r"\s+y\s+respectivamente", ""),
        (r"\s+y\s*,\s*", " "),
    ]
    for pattern, replacement in replacements:
        line = re.sub(pattern, replacement, line, flags=re.IGNORECASE)
    line = re.sub(r"\s{2,}", " ", line)
    line = re.sub(r"\s+([,.;:])", r"\1", line).strip()
    return "" if empty_label.match(line) else line


def _normalize_money_values_for_fields(normalized_values: dict[str, str], fields: list[dict]) -> dict[str, str]:
    result = dict(normalized_values)
    for field in fields:
        if not isinstance(field, dict) or not _is_money_field(field):
            continue
        key = normalize_key(field.get("key") or "")
        if key and key in result:
            result[key] = _format_money_value(result[key])
    return result


def _derive_missing_marked_values(normalized_values: dict[str, str], normalized_field_keys: set[str]) -> dict[str, str]:
    from app.services.minuta.engine.context_builder import ContextBuilder

    fields = [{"key": key, "label": key, "section": "values", "raw_markers": []} for key in normalized_field_keys]
    context = ContextBuilder().build(normalized_values, fields)
    derived = context.normalized_values
    return derived


def validate_gender_concordance(normalized_values: dict[str, str]) -> list[dict[str, str]]:
    return [
        {
            "role": issue.details.get("role", ""),
            "field_key": issue.field_key or "",
            "value": str(issue.details.get("value", "")),
            "expected_gender": str(issue.details.get("gender", "")),
            "message": issue.message,
        }
        for issue in _validate_gender_concordance_issues(normalized_values)
    ]


def apply_marked_template_replacements(
    docx_path_origen: str | Path,
    docx_path_destino: str | Path,
    values: dict,
    fields: list[dict] | None = None,
) -> dict:
    result = NotarialDocumentEngine().render_marked_template(
        source_path=docx_path_origen,
        destination_path=docx_path_destino,
        values=values or {},
        fields=fields or [],
    )
    audit = result.audit.to_dict()
    return {
        **result.statistics,
        "audit": audit,
        "not_found": [
            {"key": item.get("field_key"), "old": item.get("placeholder"), "new": item.get("inserted_value", "")}
            for item in audit["missing"]
        ],
        "gender_concordance_warnings": [
            issue
            for issue in audit["issues"]
            if issue.get("code", "").startswith("gender_")
        ],
        "blockers": [
            issue
            for issue in audit["issues"]
            if issue.get("severity") == "blocker"
        ],
        "warnings": [
            issue
            for issue in audit["issues"]
            if issue.get("severity") == "warning"
        ],
    }


__all__ = [
    "NotarialRenderBlockedError",
    "_derive_missing_marked_values",
    "_format_money_value",
    "_is_money_field",
    "_normalize_money_values_for_fields",
    "apply_marked_template_replacements",
    "cleanup_empty_second_buyer_text",
    "is_second_buyer_empty",
    "validate_gender_concordance",
]
