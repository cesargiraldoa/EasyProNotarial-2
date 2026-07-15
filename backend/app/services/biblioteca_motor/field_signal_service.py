from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from app.models.biblioteca_learning import FieldSignal


@dataclass(frozen=True)
class SignalContext:
    notary_id: int | None
    analysis_run_id: int | None
    case_id: int | None
    document_id: int | None
    source_version_id: int | None
    review_version_id: int | None
    decision_version_id: int | None
    document_type: str | None
    model: str | None
    prompt_version: str | None
    profile_version: int | None
    user_id: int | None


def record_field_signal(
    db: Session,
    *,
    context: SignalContext,
    occurrence: dict[str, Any],
    human_decision: str,
    final_field_code: str | None,
    final_field_instance_id: str | None,
) -> FieldSignal:
    original_text = str(occurrence.get("original_text") or "")
    context_text = " ".join(
        part
        for part in [
            str(occurrence.get("context_before") or "")[-120:],
            original_text,
            str(occurrence.get("context_after") or "")[:120],
        ]
        if part
    )
    signal = FieldSignal(
        notary_id=context.notary_id,
        analysis_run_id=context.analysis_run_id,
        case_id=context.case_id,
        document_id=context.document_id,
        source_version_id=context.source_version_id,
        review_version_id=context.review_version_id,
        decision_version_id=context.decision_version_id,
        document_type=context.document_type,
        section_key=occurrence.get("section_key") or _section_from_location(occurrence.get("location") or {}),
        entity_type=occurrence.get("entity_type"),
        role=occurrence.get("role"),
        candidate_type=occurrence.get("candidate_type"),
        anonymized_context=anonymize_context(context_text),
        exact_text_sha256=hashlib.sha256(original_text.encode("utf-8")).hexdigest(),
        llm_suggestion_json=json.dumps(_safe_llm_suggestion(occurrence), ensure_ascii=False, sort_keys=True),
        confidence=float(occurrence.get("confidence") or 0),
        human_decision=human_decision,
        final_field_code=final_field_code,
        final_field_instance_id=final_field_instance_id,
        user_id=context.user_id,
        model=context.model,
        prompt_version=context.prompt_version,
        profile_version=context.profile_version,
        metadata_json=json.dumps(
            {
                "occurrence_id": occurrence.get("occurrence_id"),
                "catalog_status": occurrence.get("catalog_status"),
                "visible_code": occurrence.get("visible_code"),
            },
            ensure_ascii=False,
            sort_keys=True,
        ),
    )
    db.add(signal)
    db.flush()
    return signal


def anonymize_context(value: str) -> str:
    text = str(value or "")
    text = re.sub(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", "[EMAIL]", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(?:NIT\.?\s*)?\d{3}[.\s]?\d{3}[.\s]?\d{3}-?\d\b", "[NIT]", text, flags=re.IGNORECASE)
    text = re.sub(r"\b\d{1,3}(?:[.\s]\d{3}){1,4}\b", "[NUM]", text)
    text = re.sub(r"\b\d{6,15}\b", "[NUM]", text)
    text = re.sub(r"\b[A-ZÁÉÍÓÚÜÑ]{2,}(?:\s+[A-ZÁÉÍÓÚÜÑ]{2,}){1,5}\b", "[NOMBRE]", text)
    text = re.sub(r"\b[A-ZÁÉÍÓÚÜÑ][a-záéíóúüñ]+(?:\s+[A-ZÁÉÍÓÚÜÑ][a-záéíóúüñ]+){1,4}\b", "[NOMBRE]", text)
    return re.sub(r"\s+", " ", text).strip()[:500]


def _safe_llm_suggestion(occurrence: dict[str, Any]) -> dict[str, Any]:
    return {
        "field_instance_id": occurrence.get("field_instance_id"),
        "base_field_code": occurrence.get("base_field_code"),
        "visible_code": occurrence.get("visible_code"),
        "field_code": occurrence.get("field_code"),
        "category": occurrence.get("category"),
        "candidate_type": occurrence.get("candidate_type"),
        "role": occurrence.get("role"),
        "entity_type": occurrence.get("entity_type"),
        "reason": occurrence.get("reason"),
    }


def _section_from_location(location: dict[str, Any]) -> str | None:
    if not location:
        return None
    if location.get("block_type") == "table_cell":
        return f"table:{location.get('table_index')}:{location.get('row_index')}:{location.get('cell_index')}"
    return f"paragraph:{location.get('paragraph_index')}"
