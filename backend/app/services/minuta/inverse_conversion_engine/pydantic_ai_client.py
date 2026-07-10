from __future__ import annotations

import os

from app.services.minuta.inverse_conversion_engine.llm_contracts import (
    FieldProposal,
    FieldProposalEvidence,
    LLMProposalRequest,
    LLMProposalResponse,
)


class PydanticAIProposalClient:
    """Typed proposal client.

    The default mode is disabled and deterministic. Importing pydantic_ai is optional
    so the engine works without API keys or provider setup.
    """

    def __init__(self, enabled: bool | None = None) -> None:
        self.enabled = bool(enabled) if enabled is not None else bool(os.getenv("INVERSE_CONVERSION_LLM_ENABLED"))
        self.api_key_present = bool(os.getenv("OPENAI_API_KEY"))

    def propose(self, request: LLMProposalRequest) -> LLMProposalResponse:
        if not self.enabled or not self.api_key_present:
            return self._disabled_response(request)
        try:
            import pydantic_ai  # noqa: F401
        except Exception:
            return LLMProposalResponse(
                proposals=[],
                used_llm=False,
                warnings=["pydantic_ai_unavailable_using_disabled_mode"],
            )
        return self._disabled_response(request, warning="llm_provider_not_configured_using_disabled_mode")

    def _disabled_response(self, request: LLMProposalRequest, warning: str = "llm_disabled") -> LLMProposalResponse:
        proposals: list[FieldProposal] = []
        for evidence in request.lexical_evidence[:5]:
            candidate_code = evidence.get("canonical_field_code") or evidence.get("candidate_field_code")
            if not candidate_code:
                continue
            proposals.append(
                FieldProposal(
                    candidate_field_code=evidence.get("candidate_field_code") or candidate_code,
                    canonical_field_code=candidate_code,
                    confidence_score=float(evidence.get("confidence_score") or 0.0),
                    reasons=["deterministic_from_lexical_evidence"],
                    warnings=[],
                    requires_human_review=True,
                    evidence=[
                        FieldProposalEvidence(
                            evidence_type=evidence.get("evidence_type") or "lexical",
                            score=float(evidence.get("confidence_score") or 0.0),
                        )
                    ],
                )
            )
        return LLMProposalResponse(proposals=proposals, used_llm=False, warnings=[warning])
