from __future__ import annotations

from collections import defaultdict
from difflib import SequenceMatcher

from app.services.minuta.inverse_conversion_catalog.field_code_normalizer import FieldCodeNormalizer
from app.services.minuta.inverse_conversion_catalog.models import AliasSuggestion, ExtractedPattern


class FieldAliasBuilder:
    """Suggest aliases for human review using tokens, frequency and marker context."""

    def __init__(self, normalizer: FieldCodeNormalizer | None = None) -> None:
        self.normalizer = normalizer or FieldCodeNormalizer()

    def build(
        self,
        field_frequency: dict[str, int],
        patterns: list[ExtractedPattern] | None = None,
    ) -> list[AliasSuggestion]:
        patterns = patterns or []
        all_normalized = {self.normalizer.normalize(code) for code in field_frequency}
        contexts_by_code = self._contexts_by_code(patterns)
        suggestions: list[AliasSuggestion] = []

        for raw_code, frequency in sorted(field_frequency.items(), key=lambda item: (-item[1], item[0])):
            normalized = self.normalizer.normalize(raw_code)
            canonical, status, confidence = self.normalizer.suggest_canonical(normalized, all_normalized)
            reason = "rule"
            if canonical != normalized and not self._is_safe_rule_alias(normalized, canonical):
                canonical = normalized
                status = "conflict"
                confidence = min(confidence, 0.65)
                reason = "blocked_semantic_rule"
            if canonical == normalized:
                canonical, status, confidence, reason = self._canonical_by_similarity(
                    normalized,
                    field_frequency,
                    contexts_by_code,
                )
            if status == "approved":
                status = "suggested"
            suggestions.append(
                AliasSuggestion(
                    raw_field_code=raw_code,
                    canonical_field_code=canonical,
                    frequency=frequency,
                    status=status,
                    confidence=confidence,
                    reason=reason,
                    context_samples=tuple(contexts_by_code.get(raw_code, [])[:3]),
                )
            )

        return suggestions

    def _canonical_by_similarity(
        self,
        normalized: str,
        field_frequency: dict[str, int],
        contexts_by_code: dict[str, list[str]],
    ) -> tuple[str, str, float, str]:
        tokens = self.normalizer.tokens(normalized)
        candidates: list[tuple[float, int, str]] = []
        for other_raw, frequency in field_frequency.items():
            other = self.normalizer.normalize(other_raw)
            if other == normalized:
                continue
            if not self.normalizer.can_alias(normalized, other):
                continue
            other_tokens = self.normalizer.tokens(other)
            token_score = self._jaccard(tokens, other_tokens)
            text_score = SequenceMatcher(None, normalized, other).ratio()
            context_score = self._context_overlap(contexts_by_code.get(normalized, []), contexts_by_code.get(other_raw, []))
            score = (token_score * 0.55) + (text_score * 0.3) + (context_score * 0.15)
            if score >= 0.72:
                candidates.append((score, frequency, other))

        if not candidates:
            return normalized, "suggested", 0.6, "identity"

        candidates.sort(key=lambda item: (-item[0], -item[1], item[2]))
        best = candidates[0]
        ambiguous = len(candidates) > 1 and abs(candidates[0][0] - candidates[1][0]) < 0.08
        canonical = best[2] if best[1] >= field_frequency.get(normalized, 0) else normalized
        return canonical, "conflict" if ambiguous else "suggested", min(best[0], 0.88), "similarity"

    def _is_safe_rule_alias(self, normalized: str, canonical: str) -> bool:
        if normalized == canonical:
            return True
        if canonical == "VALOR_VENTA" and self.normalizer.semantic_category(normalized) == "VALOR_VENTA":
            return True
        return self.normalizer.can_alias(normalized, canonical)

    @staticmethod
    def _jaccard(left: set[str], right: set[str]) -> float:
        if not left or not right:
            return 0.0
        return len(left.intersection(right)) / len(left.union(right))

    @staticmethod
    def _contexts_by_code(patterns: list[ExtractedPattern]) -> dict[str, list[str]]:
        contexts: dict[str, list[str]] = defaultdict(list)
        for pattern in patterns:
            sample = " ".join(part for part in (pattern.text_before, pattern.text_after) if part).strip()
            if sample:
                contexts[pattern.raw_field_code].append(sample)
                contexts[pattern.canonical_field_code or ""].append(sample)
        return contexts

    @staticmethod
    def _context_overlap(left: list[str], right: list[str]) -> float:
        if not left or not right:
            return 0.0
        left_tokens = set(" ".join(left).upper().split())
        right_tokens = set(" ".join(right).upper().split())
        if not left_tokens or not right_tokens:
            return 0.0
        return len(left_tokens.intersection(right_tokens)) / len(left_tokens.union(right_tokens))
