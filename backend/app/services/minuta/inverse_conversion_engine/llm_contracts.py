from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class FieldProposalEvidence(BaseModel):
    evidence_type: str
    source: str | None = None
    text_before: str | None = None
    text_after: str | None = None
    score: float = 0.0


class FieldProposal(BaseModel):
    candidate_field_code: str
    canonical_field_code: str
    confidence_score: float = Field(ge=0.0, le=100.0)
    reasons: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    requires_human_review: bool = True
    evidence: list[FieldProposalEvidence] = Field(default_factory=list)


class LLMProposalRequest(BaseModel):
    raw_marker: str | None = None
    context_before: str | None = None
    context_after: str | None = None
    lexical_evidence: list[dict[str, Any]] = Field(default_factory=list)
    semantic_evidence: list[dict[str, Any]] = Field(default_factory=list)
    instructions: str = (
        "Use only supplied evidence. Do not invent fields. Return typed JSON. "
        "Never approve changes. Mark requires_human_review when uncertain."
    )


class LLMProposalResponse(BaseModel):
    proposals: list[FieldProposal] = Field(default_factory=list)
    used_llm: bool = False
    warnings: list[str] = Field(default_factory=list)


class ValidationWarning(BaseModel):
    code: str
    message: str
    severity: str = "warning"


class CandidateDecision(BaseModel):
    candidate_field_code: str
    canonical_field_code: str
    status: str
    confidence_score: float
    requires_human_review: bool
    warnings: list[ValidationWarning] = Field(default_factory=list)


class EngineFinalResult(BaseModel):
    run_id: int | None
    status: str
    requires_human_review: bool
    candidates: list[CandidateDecision]
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
