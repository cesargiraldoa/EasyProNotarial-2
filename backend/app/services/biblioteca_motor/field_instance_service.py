from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Any

from app.services.biblioteca_motor.anchor_resolver import AnchoredOccurrence
from app.services.biblioteca_motor.contracts import FieldDefinition
from app.services.biblioteca_motor.llm_extractor import LLMExtraction, LLMFieldInstance


PROVISIONAL_FIELD_PREFIX = "PENDING_FIELD_"


@dataclass(frozen=True)
class ResolvedFieldInstance:
    field_instance_ref: str
    field_instance_id: str
    base_field_code: str
    visible_code: str
    field_code: str
    field_label: str
    category: str
    catalog_status: str
    requires_field_assignment: bool
    entity_id: str | None
    entity_ref: str | None
    entity_type: str | None
    role: str | None
    role_ordinal: int | None
    role_assignment_id: str | None
    candidate_type: str
    llm_suggestion: dict[str, Any]


@dataclass(frozen=True)
class FieldInstanceResolution:
    instances: dict[str, ResolvedFieldInstance]
    suggestions: list[dict[str, Any]]


def resolve_field_instances(
    extraction: LLMExtraction,
    anchored: list[AnchoredOccurrence],
    fields: list[FieldDefinition],
    *,
    document_sha256: str,
    max_suggestions: int,
) -> FieldInstanceResolution:
    field_by_code = {field.code: field for field in fields}
    entity_ids = _entity_ids(extraction, document_sha256)
    role_ordinals, role_assignment_ids = _role_assignments(extraction, entity_ids)
    instance_by_ref = {
        item.field_instance_ref: _resolve_instance(item, extraction, field_by_code, entity_ids, role_ordinals, role_assignment_ids, document_sha256)
        for item in extraction.field_instances
    }
    occurrence_by_ref = {item.occurrence_ref: item for item in extraction.occurrences}
    suggestions: list[dict[str, Any]] = []
    for anchor in anchored:
        instance = instance_by_ref.get(anchor.field_instance_ref)
        llm_occurrence = occurrence_by_ref.get(anchor.occurrence_ref)
        if instance is None or llm_occurrence is None:
            continue
        occurrence_id = _occurrence_id(anchor.occurrence_ref, instance.field_instance_id, anchor.location["location_key"])
        suggestions.append(
            {
                "suggestion_id": "sug_" + _hash(f"{occurrence_id}:{instance.field_instance_id}")[:16],
                "candidate_id": "cand_" + _hash(f"{anchor.exact_text}:{anchor.location['location_key']}")[:16],
                "candidate_type": instance.candidate_type,
                "original_text": anchor.exact_text,
                "field_instance_id": instance.field_instance_id,
                "base_field_code": instance.base_field_code,
                "visible_code": instance.visible_code,
                "field_code": instance.field_code,
                "field_label": instance.field_label,
                "category": instance.category,
                "catalog_status": instance.catalog_status,
                "requires_field_assignment": instance.requires_field_assignment,
                "confidence": min(float(anchor.confidence), float(extraction.confidence)),
                "source": "llm",
                "needs_human_review": True,
                "location": anchor.location,
                "context_before": anchor.context_before,
                "context_after": anchor.context_after,
                "reason": anchor.reason or instance.llm_suggestion.get("reason"),
                "entity_id": instance.entity_id,
                "entity_ref": instance.entity_ref,
                "entity_type": instance.entity_type,
                "role": instance.role,
                "role_ordinal": instance.role_ordinal,
                "role_assignment_id": instance.role_assignment_id,
                "occurrence_id": occurrence_id,
                "review_status": "pending_review",
                "llm_suggestion": instance.llm_suggestion,
                "section_key": _section_key(anchor.location),
            },
        )
    suggestions.sort(key=lambda item: (item["location"]["block_index"], item["location"]["char_start"], item["occurrence_id"]))
    return FieldInstanceResolution(instances=instance_by_ref, suggestions=suggestions[:max_suggestions])


def resolve_decision_target_instance(
    occurrence: dict[str, Any],
    *,
    field_code: str,
    visible_code: str | None = None,
    base_field_code: str | None = None,
) -> str:
    safe_field_code = _safe_code(field_code)
    visible = _safe_code(visible_code or safe_field_code)
    base = _safe_code(base_field_code or visible or safe_field_code)
    entity_id = str(occurrence.get("entity_id") or "entityless")
    role = str(occurrence.get("role") or "roleless")
    candidate_type = str(occurrence.get("candidate_type") or "")
    return "fi_" + _hash(f"{entity_id}:{role}:{base}:{visible}:{safe_field_code}:{candidate_type}")[:18]


def provisional_code(seed: str, candidate_type: str = "FIELD") -> str:
    safe_type = _safe_code(candidate_type or "FIELD") or "FIELD"
    return f"{PROVISIONAL_FIELD_PREFIX}{safe_type}_{_hash(seed)[:12].upper()}"


def _resolve_instance(
    item: LLMFieldInstance,
    extraction: LLMExtraction,
    field_by_code: dict[str, FieldDefinition],
    entity_ids: dict[str, tuple[str, str | None]],
    role_ordinals: dict[tuple[str, str], int],
    role_assignment_ids: dict[tuple[str, str], str],
    document_sha256: str,
) -> ResolvedFieldInstance:
    entity_id, entity_type = entity_ids.get(item.entity_ref or "", (None, None))
    role = _safe_code(item.role or "")
    role_ordinal = role_ordinals.get((entity_id or "", role)) if entity_id and role else None
    role_assignment_id = role_assignment_ids.get((entity_id or "", role)) if entity_id and role else None
    base = _safe_code(item.base_field_code or item.candidate_type)
    suggested = _safe_code(item.suggested_field_code or "")
    visible = _safe_code(item.visible_code or suggested or _visible_from_role(base, role, role_ordinal) or base)
    field = field_by_code.get(suggested) or field_by_code.get(visible) or field_by_code.get(base)
    catalog_status = "matched" if field is not None else "unmapped"
    if field is not None:
        field_code = field.code
        field_label = field.label
        category = field.category
    else:
        field_code = provisional_code(f"{document_sha256}:{item.field_instance_ref}:{visible}", item.candidate_type)
        field_label = item.label or visible.replace("_", " ").title()
        category = item.category or "otro"
    field_instance_id = "fi_" + _hash(
        f"{entity_id or item.entity_ref or 'entityless'}:{role or 'roleless'}:{base}:{visible}:{item.candidate_type}:{item.field_instance_ref}",
    )[:18]
    return ResolvedFieldInstance(
        field_instance_ref=item.field_instance_ref,
        field_instance_id=field_instance_id,
        base_field_code=base,
        visible_code=visible,
        field_code=field_code,
        field_label=field_label,
        category=category,
        catalog_status=catalog_status,
        requires_field_assignment=catalog_status != "matched",
        entity_id=entity_id,
        entity_ref=item.entity_ref,
        entity_type=entity_type,
        role=role or None,
        role_ordinal=role_ordinal,
        role_assignment_id=role_assignment_id,
        candidate_type=item.candidate_type,
        llm_suggestion=item.model_dump(),
    )


def _entity_ids(extraction: LLMExtraction, document_sha256: str) -> dict[str, tuple[str, str | None]]:
    result: dict[str, tuple[str, str | None]] = {}
    for entity in extraction.entities:
        seed = f"{document_sha256}:{entity.entity_ref}:{entity.entity_type}:{_normalize(entity.display_name or '')}:{_normalize(entity.document_number or '')}:{_normalize(entity.nit or '')}"
        result[entity.entity_ref] = ("ent_" + _hash(seed)[:14], entity.entity_type)
    return result


def _role_assignments(
    extraction: LLMExtraction,
    entity_ids: dict[str, tuple[str, str | None]],
) -> tuple[dict[tuple[str, str], int], dict[tuple[str, str], str]]:
    role_entities: dict[str, list[str]] = {}
    for role in extraction.roles:
        entity_id = entity_ids.get(role.entity_ref, ("", None))[0]
        safe_role = _safe_code(role.role)
        if not entity_id or not safe_role:
            continue
        role_entities.setdefault(safe_role, [])
        if entity_id not in role_entities[safe_role]:
            role_entities[safe_role].append(entity_id)
    ordinals: dict[tuple[str, str], int] = {}
    assignment_ids: dict[tuple[str, str], str] = {}
    for role, entities in role_entities.items():
        for index, entity_id in enumerate(entities, start=1):
            key = (entity_id, role)
            ordinals[key] = index
            assignment_ids[key] = "role_" + _hash(f"{entity_id}:{role}")[:14]
    return ordinals, assignment_ids


def _visible_from_role(base: str, role: str, role_ordinal: int | None) -> str | None:
    if not role or not role_ordinal:
        return None
    suffix = f"{role}_{role_ordinal}"
    if base in {"NOMBRE", "RAZON_SOCIAL"}:
        return suffix
    if base in {"DOCUMENTO", "NUMERO_DOCUMENTO", "CEDULA"}:
        return f"CEDULA_{suffix}"
    if base == "NIT":
        return f"NIT_{suffix}"
    return f"{base}_{suffix}"


def _section_key(location: dict[str, Any]) -> str:
    if location.get("block_type") == "table_cell":
        return f"table:{location.get('table_index')}:{location.get('row_index')}:{location.get('cell_index')}"
    return f"paragraph:{location.get('paragraph_index')}"


def _safe_code(value: str) -> str:
    return re.sub(r"[^A-Z0-9_]+", "_", str(value or "").strip().upper()).strip("_")[:120]


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "").upper()).strip()


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _occurrence_id(occurrence_ref: str, field_instance_id: str, location_key: str) -> str:
    return "occ_" + _hash(f"{occurrence_ref}:{field_instance_id}:{location_key}")[:12]
