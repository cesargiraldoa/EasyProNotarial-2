from __future__ import annotations

from collections import Counter

from app.services.minuta.inverse_conversion_catalog.field_code_normalizer import FieldCodeNormalizer
from app.services.minuta.inverse_conversion_rag.models import FieldCandidate


class InverseConversionRanker:
    def __init__(self, normalizer: FieldCodeNormalizer | None = None) -> None:
        self.normalizer = normalizer or FieldCodeNormalizer()

    def score_candidate(
        self,
        candidate_code: str,
        query_field_code: str | None = None,
        query_text: str | None = None,
        text_before: str | None = None,
        text_after: str | None = None,
        canonical_code: str | None = None,
        aliases: list[str] | None = None,
        pattern_texts: list[str] | None = None,
        frequency: int = 0,
        status: str = "suggested",
    ) -> tuple[float, tuple[str, ...], tuple[str, ...]]:
        aliases = aliases or []
        pattern_texts = pattern_texts or []
        canonical = self.normalizer.normalize(canonical_code or candidate_code)
        candidate = self.normalizer.normalize(candidate_code)
        reasons: list[str] = []
        warnings: list[str] = []
        score = 0.0

        if query_field_code:
            query = self.normalizer.normalize(query_field_code)
            if candidate == query or canonical == query:
                score += 60.0
                reasons.append("exact_field_code_match")
            elif query in {self.normalizer.normalize(alias) for alias in aliases}:
                score += 45.0
                reasons.append("alias_match")
            elif self.normalizer.can_alias(query, canonical):
                score += 20.0
                reasons.append("compatible_semantic_category")
            else:
                score -= 35.0
                warnings.append("different_semantic_category")

        query_context = " ".join(part for part in (query_text, text_before, text_after) if part)
        overlap = self._overlap(query_context, " ".join([candidate, canonical, *aliases, *pattern_texts]))
        if overlap:
            score += min(overlap * 30.0, 20.0)
            reasons.append(f"token_overlap:{overlap:.2f}")

        if text_before or text_after:
            before_after_overlap = self._overlap(" ".join(part for part in (text_before, text_after) if part), " ".join(pattern_texts))
            if before_after_overlap:
                score += min(before_after_overlap * 40.0, 18.0)
                reasons.append(f"before_after_similarity:{before_after_overlap:.2f}")

        if frequency:
            score += min(float(frequency), 25.0)
            reasons.append("frequency_signal")

        if status == "conflict":
            score -= 18.0
            warnings.append("candidate_status_conflict")
        elif status == "suggested":
            score += 5.0
            reasons.append("candidate_status_suggested")

        return max(0.0, round(score, 4)), tuple(reasons), tuple(warnings)

    def sort_candidates(self, candidates: list[FieldCandidate], limit: int = 10) -> list[FieldCandidate]:
        return sorted(
            candidates,
            key=lambda candidate: (
                -candidate.confidence_score,
                candidate.status == "conflict",
                -candidate.frequency,
                candidate.canonical_field_code,
            ),
        )[:limit]

    def _overlap(self, left: str | None, right: str | None) -> float:
        left_tokens = self.normalizer.tokens(left)
        right_tokens = self.normalizer.tokens(right)
        if not left_tokens or not right_tokens:
            return 0.0
        return len(left_tokens.intersection(right_tokens)) / len(left_tokens.union(right_tokens))
