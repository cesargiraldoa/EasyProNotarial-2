from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal


ProposalType = Literal["project_field", "document_field", "derived_field", "review_required", "fixed_text"]
ApplyStrategy = Literal["all_occurrences", "selected_occurrences", "review_required"]
ReviewDecisionValue = Literal["confirm", "reject", "review_required"]


@dataclass
class RunStyle:
    bold: bool | None = None
    italic: bool | None = None
    underline: bool | None = None
    highlight_color: str | None = None
    font_color: str | None = None
    font_size: float | None = None


@dataclass
class RunMap:
    run_id: str
    block_id: str
    text: str
    start: int
    end: int
    style: RunStyle


@dataclass
class BlockMap:
    block_id: str
    kind: str
    location: str
    raw_text: str
    normalized_text: str
    char_count: int
    is_empty: bool
    structural_hints: dict
    runs: list[RunMap] = field(default_factory=list)


@dataclass
class Occurrence:
    occurrence_id: str
    occurrence_type: str
    text: str
    block_id: str
    location: str
    start: int
    end: int
    before: str
    after: str


@dataclass
class DocumentQuality:
    total_blocks: int
    empty_blocks: int
    total_runs: int
    total_occurrences: int
    warnings: list[str] = field(default_factory=list)


@dataclass
class DocumentMap:
    document_id: str
    source_filename: str
    quality: DocumentQuality
    blocks: list[BlockMap]
    runs: list[RunMap]
    occurrences_index: dict[str, list[Occurrence]]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ProposalOccurrence:
    occurrence_id: str
    block_id: str
    location: str
    text: str
    start: int
    end: int
    before: str
    after: str


@dataclass
class FieldProposal:
    field_key: str
    label: str
    marker: str
    value: str
    confidence: float
    proposal_type: ProposalType
    occurrences: list[ProposalOccurrence]
    apply_strategy: ApplyStrategy
    reason: str
    role: str | None = None
    scope: str | None = None
    evidence: list[str] = field(default_factory=list)


@dataclass
class DocumentProfile:
    document_type: str
    recommended_mode: Literal["documento_individual", "proyecto_inmobiliario", "no_determinado"]
    acts_detected: list[str]
    structural_sections: list[dict]
    parties_summary: list[dict]
    property_summary: dict
    money_summary: list[dict]
    risk_notes: list[str]
    confidence: float
    evidence: list[dict]


@dataclass
class DraftReplacement:
    field_key: str
    marker: str
    value: str
    block_id: str
    location: str


@dataclass
class DraftResult:
    output_path: str
    replacements: list[DraftReplacement]
    skipped: list[dict]


@dataclass
class ValidationResult:
    passed: bool
    output_path: str
    opens: bool
    contains_markers: bool
    marked_fields_count: int
    marked_fields: list[dict]
    errors: list[str] = field(default_factory=list)


@dataclass
class HumanReviewDecision:
    field_key: str
    decision: ReviewDecisionValue
    value: str | None = None
    marker: str | None = None
    apply_strategy: ApplyStrategy | None = None
    occurrence_ids: list[str] = field(default_factory=list)
    notes: str | None = None


@dataclass
class AppliedHumanReviewDecision:
    field_key: str
    value: str
    original_marker: str
    final_marker: str
    decision: str
    replaceable: bool
    block_reason: str | None
    selected_occurrence_ids: list[str]
    original_proposal: dict
    human_decision: dict | None


@dataclass
class HumanReviewResult:
    source_review_file: str | None
    applied_decisions: list[AppliedHumanReviewDecision]
    confirmed_proposals: list[FieldProposal]


def to_plain(value) -> dict:
    return asdict(value)
