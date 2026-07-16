from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

from app.models.case import Case
from app.models.case_document import CaseDocument
from app.models.case_document_version import CaseDocumentVersion
from app.services.minuta.marked_template_detector import detect_marked_template


def detect_marked_template_from_bytes(content: bytes) -> dict[str, Any]:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    try:
        return detect_marked_template(tmp_path)
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def safe_marked_template_snapshot(raw: str | None) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    if not isinstance(parsed, dict):
        return {}
    if parsed.get("source") == "marked_template":
        return parsed
    nested = parsed.get("marked_template")
    return nested if isinstance(nested, dict) and nested.get("source") == "marked_template" else {}


def _field_key(field: dict[str, Any]) -> str:
    return str(field.get("key") or "").strip()


def merge_marked_template_state(
    previous_snapshot: dict[str, Any] | None,
    detected_result: dict[str, Any] | None,
    *,
    document_name: str,
) -> dict[str, Any]:
    previous_snapshot = previous_snapshot or {}
    detected_fields = [
        field
        for field in (detected_result or {}).get("fields", [])
        if isinstance(field, dict) and _field_key(field)
    ]
    previous_fields = [
        field
        for field in previous_snapshot.get("fields", [])
        if isinstance(field, dict) and _field_key(field)
    ]

    merged_by_key: dict[str, dict[str, Any]] = {}
    for field in previous_fields:
        merged_by_key[_field_key(field)] = dict(field)
    for field in detected_fields:
        key = _field_key(field)
        current = merged_by_key.get(key)
        if current is None:
            merged_by_key[key] = dict(field)
            continue
        raw_markers = list(current.get("raw_markers") or [])
        for marker in field.get("raw_markers") or []:
            if marker not in raw_markers:
                raw_markers.append(marker)
        marker_types = sorted(set(current.get("marker_types") or []) | set(field.get("marker_types") or []))
        current.update(
            {
                "label": current.get("label") or field.get("label") or key,
                "section": current.get("section") or field.get("section") or "Otros",
                "occurrences": max(int(current.get("occurrences") or 0), int(field.get("occurrences") or 0)),
                "marker_types": marker_types,
                "raw_markers": raw_markers,
            }
        )

    values_source = previous_snapshot.get("values") if isinstance(previous_snapshot.get("values"), dict) else {}
    values = {
        key: "" if values_source.get(key) is None else str(values_source.get(key))
        for key in merged_by_key
    }
    return {
        "source": "marked_template",
        "fields": list(merged_by_key.values()),
        "values": values,
        "document_name": previous_snapshot.get("document_name") or document_name,
    }


def build_marked_template_edit_payload(
    case: Case,
    document: CaseDocument,
    version: CaseDocumentVersion,
    snapshot: dict[str, Any],
    *,
    saved_from_onlyoffice: bool,
) -> dict[str, Any]:
    return {
        "caseId": case.id,
        "documentId": document.id,
        "versionId": version.id,
        "documentName": str(snapshot.get("document_name") or document.title or "Minuta marcada"),
        "sourceDocumentTitle": document.title or str(snapshot.get("document_name") or "Minuta marcada"),
        "fields": snapshot.get("fields") if isinstance(snapshot.get("fields"), list) else [],
        "values": snapshot.get("values") if isinstance(snapshot.get("values"), dict) else {},
        "saved": saved_from_onlyoffice,
    }
