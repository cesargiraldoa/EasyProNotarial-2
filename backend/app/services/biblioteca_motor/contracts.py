from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal


ReviewStatus = Literal["pending_review", "accepted", "rejected", "changed", "prepared", "skipped"]
CatalogStatus = Literal["matched", "unmapped"]
EntityType = Literal["natural_person", "legal_person", "financial_entity", "unknown"]
DecisionAction = Literal["accept", "reject", "change"]


@dataclass(frozen=True)
class DetectedCandidate:
    candidate_id: str
    original_text: str
    candidate_type: str
    context_before: str
    context_after: str
    location: dict[str, Any]


@dataclass(frozen=True)
class LegalEntity:
    entity_id: str
    entity_type: EntityType
    display_name: str
    normalized_name: str
    document_number: str | None = None
    nit: str | None = None
    attributes: dict[str, Any] = field(default_factory=dict)
    role_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class LegalRoleAssignment:
    assignment_id: str
    entity_id: str
    role: str
    ordinal: int
    visible_role_code: str


@dataclass(frozen=True)
class FieldDefinition:
    code: str
    label: str
    category: str
    field_type: str = "text"


@dataclass(frozen=True)
class FieldInstance:
    field_instance_id: str
    base_field_code: str
    visible_code: str
    field_code: str
    field_label: str
    category: str
    catalog_status: CatalogStatus
    entity_id: str | None = None
    role: str | None = None
    role_ordinal: int | None = None
    role_assignment_ids: tuple[str, ...] = ()
    status: ReviewStatus = "pending_review"


@dataclass(frozen=True)
class FieldOccurrence:
    occurrence_id: str
    field_instance_id: str
    candidate_id: str
    original_text: str
    location: dict[str, Any]
    context_before: str = ""
    context_after: str = ""
    status: ReviewStatus = "pending_review"
    tag: str | None = None


@dataclass(frozen=True)
class ReviewSuggestion:
    suggestion_id: str
    candidate_id: str
    candidate_type: str
    original_text: str
    field_instance_id: str
    base_field_code: str
    visible_code: str
    field_code: str
    field_label: str
    category: str
    catalog_status: CatalogStatus
    requires_field_assignment: bool
    confidence: float
    source: str
    needs_human_review: bool
    location: dict[str, Any]
    context_before: str
    context_after: str
    reason: str | None = None
    entity_id: str | None = None
    entity_type: EntityType | None = None
    role: str | None = None
    role_ordinal: int | None = None
    occurrence_id: str | None = None
    review_status: ReviewStatus = "pending_review"


@dataclass(frozen=True)
class ReviewDecision:
    decision_id: str
    action: DecisionAction
    occurrence_id: str
    field_instance_id: str | None
    assigned_field_code: str | None = None
    original_text: str | None = None
    decided_by_user_id: int | None = None
    decided_at: str | None = None
    audit: dict[str, Any] = field(default_factory=dict)


def to_dict(value: Any) -> dict[str, Any]:
    return asdict(value)

