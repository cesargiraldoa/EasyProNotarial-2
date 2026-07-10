from __future__ import annotations

from app.services.minuta.inverse_conversion_catalog.field_code_normalizer import FieldCodeNormalizer
from app.services.minuta.inverse_conversion_engine.llm_contracts import FieldProposal, ValidationWarning
from app.services.minuta.inverse_conversion_engine.models import EngineCandidate


class ConservativeCandidateValidator:
    def __init__(self, known_field_codes: set[str] | None = None, normalizer: FieldCodeNormalizer | None = None) -> None:
        self.known_field_codes = {code.upper() for code in (known_field_codes or set())}
        self.normalizer = normalizer or FieldCodeNormalizer()

    def validate(self, proposal: FieldProposal, raw_marker: str | None = None, context_before: str | None = None, context_after: str | None = None) -> EngineCandidate:
        warnings: list[ValidationWarning] = []
        candidate = self.normalizer.normalize(proposal.candidate_field_code)
        canonical = self.normalizer.normalize(proposal.canonical_field_code)

        if not proposal.evidence:
            warnings.append(ValidationWarning(code="missing_evidence", message="Proposal has no supporting evidence.", severity="error"))
        if proposal.confidence_score < 60:
            warnings.append(ValidationWarning(code="low_score", message="Candidate confidence is below conservative threshold."))
        if self.known_field_codes and canonical not in self.known_field_codes:
            warnings.append(ValidationWarning(code="unknown_canonical_field", message=f"Canonical field {canonical} is not in field_definitions.", severity="error"))
        if not self.normalizer.can_alias(candidate, canonical):
            warnings.append(ValidationWarning(code="semantic_category_mismatch", message="Candidate and canonical field categories are incompatible.", severity="error"))
        if self._blocked_pair(candidate, canonical):
            warnings.append(ValidationWarning(code="blocked_dangerous_alias", message="Dangerous field consolidation is blocked.", severity="error"))
        if any("conflict" in warning.lower() for warning in proposal.warnings):
            warnings.append(ValidationWarning(code="conflict_requires_review", message="Conflict evidence requires human review."))
        if self._looks_like_fixed_legal_text(raw_marker or ""):
            warnings.append(ValidationWarning(code="fixed_legal_text", message="Fixed legal text must not be treated as a variable.", severity="error"))

        error_codes = {warning.code for warning in warnings if warning.severity == "error"}
        if "blocked_dangerous_alias" in error_codes or "fixed_legal_text" in error_codes:
            status = "blocked"
        elif "semantic_category_mismatch" in error_codes or "unknown_canonical_field" in error_codes:
            status = "conflict"
        elif warnings or proposal.requires_human_review:
            status = "needs_human_review"
        else:
            status = "accepted_suggested"

        return EngineCandidate(
            raw_marker=raw_marker,
            candidate_field_code=candidate,
            canonical_field_code=canonical,
            confidence_score=proposal.confidence_score,
            status=status,
            evidence={"proposal": proposal.model_dump()},
            warnings=tuple(f"{warning.code}:{warning.message}" for warning in warnings),
            requires_human_review=status != "accepted_suggested",
            reasons=tuple(proposal.reasons),
            context_before=context_before,
            context_after=context_after,
        )

    def _blocked_pair(self, candidate: str, canonical: str) -> bool:
        candidate_category = self.normalizer.semantic_category(candidate)
        canonical_category = self.normalizer.semantic_category(canonical)
        if {candidate_category, canonical_category} == {"TIPO_DOCUMENTO", "NUMERO_DOCUMENTO"}:
            return True
        if candidate_category == "MUNICIPIO_EXPEDICION_DOCUMENTO" and canonical_category == "NUMERO_DOCUMENTO":
            return True
        if {candidate_category, canonical_category}.issubset({"DIA", "MES", "ANO"}) and candidate_category != canonical_category:
            return True
        if {candidate_category, canonical_category} == {"NUMERO_ESCRITURA_LETRAS", "NUMERO_ESCRITURA_NUMEROS"}:
            return True
        candidate_ordinal = self.normalizer.ordinal_suffix(candidate)
        canonical_ordinal = self.normalizer.ordinal_suffix(canonical)
        if candidate_ordinal and candidate_ordinal != canonical_ordinal and "COMPRADOR" in candidate and "COMPRADOR" in canonical:
            return True
        if candidate_ordinal and not canonical_ordinal and "COMPRADOR" in candidate and "COMPRADOR" in canonical:
            return True
        return False

    @staticmethod
    def _looks_like_fixed_legal_text(value: str) -> bool:
        cleaned = value.strip().upper()
        fixed_tokens = ("CLAUSULA", "COMPARECIO", "OTORGANTES", "ESCRITURA PUBLICA")
        return len(cleaned.split()) > 4 and any(token in cleaned for token in fixed_tokens)
