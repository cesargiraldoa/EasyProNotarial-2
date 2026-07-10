from __future__ import annotations

from app.services.minuta.inverse_conversion_catalog.field_code_normalizer import FieldCodeNormalizer
from app.services.minuta.inverse_conversion_catalog.models import ExtractedPattern, MarkerOccurrence


class PatternExtractor:
    """Build reviewable context patterns only from existing human markers."""

    def __init__(self, normalizer: FieldCodeNormalizer | None = None) -> None:
        self.normalizer = normalizer or FieldCodeNormalizer()

    def extract(
        self,
        occurrence: MarkerOccurrence,
        canonical_lookup: dict[str, str] | None = None,
        pattern_source_file: str | None = None,
    ) -> ExtractedPattern:
        canonical_lookup = canonical_lookup or {}
        normalized = self.normalizer.normalize(occurrence.raw_field_code)
        canonical = canonical_lookup.get(occurrence.raw_field_code) or canonical_lookup.get(normalized)
        confidence = 0.55 if canonical else 0.35
        if occurrence.text_before and occurrence.text_after:
            confidence += 0.15
        return ExtractedPattern(
            raw_field_code=occurrence.raw_field_code,
            canonical_field_code=canonical,
            text_before=occurrence.text_before,
            text_after=occurrence.text_after,
            location=occurrence.location,
            confidence=min(confidence, 0.85),
            pattern_source_file=pattern_source_file,
        )

    def extract_many(
        self,
        occurrences: list[MarkerOccurrence],
        canonical_lookup: dict[str, str] | None = None,
        pattern_source_file: str | None = None,
    ) -> list[ExtractedPattern]:
        return [
            self.extract(
                occurrence,
                canonical_lookup=canonical_lookup,
                pattern_source_file=pattern_source_file,
            )
            for occurrence in occurrences
        ]
