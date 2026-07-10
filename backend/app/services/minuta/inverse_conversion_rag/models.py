from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class RagQuery:
    field_code: str | None = None
    text: str | None = None
    text_before: str | None = None
    text_after: str | None = None
    limit: int = 10


@dataclass(frozen=True)
class PatternEvidence:
    raw_field_code: str
    canonical_field_code: str | None
    text_before: str | None
    text_after: str | None
    frequency: int
    confidence: float
    status: str
    pattern_source_file: str | None = None
    document_type: str | None = None
    act_type: str | None = None


@dataclass(frozen=True)
class DocumentEvidence:
    document_id: int
    filename: str
    source_path: str | None
    document_type: str | None
    act_type: str | None
    marker_count: int
    occurrences: int = 0


@dataclass(frozen=True)
class FieldCandidate:
    candidate_field_code: str
    canonical_field_code: str
    display_name: str | None
    status: str
    confidence_score: float
    frequency: int
    evidence_type: str
    source_documents: tuple[DocumentEvidence, ...] = ()
    matched_aliases: tuple[str, ...] = ()
    matched_patterns: tuple[PatternEvidence, ...] = ()
    text_before_examples: tuple[str, ...] = ()
    text_after_examples: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class RagEvidence:
    candidate_field_code: str
    canonical_field_code: str
    display_name: str | None
    confidence_score: float
    evidence_type: str
    source_documents: tuple[DocumentEvidence, ...]
    matched_aliases: tuple[str, ...]
    matched_patterns: tuple[PatternEvidence, ...]
    text_before_examples: tuple[str, ...]
    text_after_examples: tuple[str, ...]
    frequency: int
    status: str
    reasons: tuple[str, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class RetrievalResult:
    query: RagQuery
    candidates: tuple[RagEvidence, ...]
    total_candidates: int
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
