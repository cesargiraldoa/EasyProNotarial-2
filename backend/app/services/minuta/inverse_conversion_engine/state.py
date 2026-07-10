from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.services.minuta.inverse_conversion_engine.models import EngineCandidate, EngineOptions, ExtractedContext


@dataclass
class InverseConversionState:
    run_id: int | None = None
    input_type: str = "text"
    input_text: str | None = None
    raw_marker: str | None = None
    context_before: str | None = None
    context_after: str | None = None
    input_document_path: str | None = None
    options: EngineOptions = field(default_factory=EngineOptions)
    extracted_contexts: list[ExtractedContext] = field(default_factory=list)
    lexical_evidence: list[Any] = field(default_factory=list)
    semantic_evidence: list[Any] = field(default_factory=list)
    llm_proposals: list[Any] = field(default_factory=list)
    validated_candidates: list[EngineCandidate] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    requires_human_review: bool = True
    final_result: dict[str, Any] = field(default_factory=dict)

    def to_step_input(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "input_type": self.input_type,
            "raw_marker": self.raw_marker,
            "context_before": self.context_before,
            "context_after": self.context_after,
            "input_document_path": self.input_document_path,
        }
