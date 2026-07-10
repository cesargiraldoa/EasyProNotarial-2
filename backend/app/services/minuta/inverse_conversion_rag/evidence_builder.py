from __future__ import annotations

from collections import defaultdict

from app.services.minuta.inverse_conversion_catalog.models import (
    CorpusDocument,
    CorpusDocumentField,
    FieldAlias,
    FieldDefinition,
    FieldPattern,
)
from app.services.minuta.inverse_conversion_rag.models import (
    DocumentEvidence,
    FieldCandidate,
    PatternEvidence,
    RagEvidence,
)
from app.services.minuta.inverse_conversion_rag.ranker import InverseConversionRanker


class EvidenceBuilder:
    def __init__(self, ranker: InverseConversionRanker | None = None) -> None:
        self.ranker = ranker or InverseConversionRanker()

    def build_candidates(
        self,
        definitions: list[FieldDefinition],
        aliases: list[FieldAlias],
        patterns: list[FieldPattern],
        documents: list[tuple[CorpusDocument, CorpusDocumentField]],
        query_field_code: str | None = None,
        query_text: str | None = None,
        text_before: str | None = None,
        text_after: str | None = None,
        limit: int = 10,
    ) -> list[RagEvidence]:
        definition_by_code = {definition.field_code: definition for definition in definitions}
        aliases_by_canonical: dict[str, list[FieldAlias]] = defaultdict(list)
        for alias in aliases:
            aliases_by_canonical[alias.canonical_field_code].append(alias)
            aliases_by_canonical[alias.raw_field_code].append(alias)

        patterns_by_code: dict[str, list[FieldPattern]] = defaultdict(list)
        for pattern in patterns:
            patterns_by_code[pattern.canonical_field_code or pattern.raw_field_code].append(pattern)
            patterns_by_code[pattern.raw_field_code].append(pattern)

        documents_by_code: dict[str, list[tuple[CorpusDocument, CorpusDocumentField]]] = defaultdict(list)
        for document, document_field in documents:
            documents_by_code[document_field.canonical_field_code or document_field.raw_field_code].append((document, document_field))
            documents_by_code[document_field.raw_field_code].append((document, document_field))

        codes = set(definition_by_code)
        codes.update(alias.canonical_field_code for alias in aliases)
        codes.update(alias.raw_field_code for alias in aliases)
        codes.update(pattern.canonical_field_code or pattern.raw_field_code for pattern in patterns)
        codes.update(pattern.raw_field_code for pattern in patterns)
        codes.update(field.canonical_field_code or field.raw_field_code for _, field in documents)
        codes.update(field.raw_field_code for _, field in documents)

        candidates: list[FieldCandidate] = []
        for code in sorted(codes):
            definition = definition_by_code.get(code)
            related_aliases = aliases_by_canonical.get(code, [])
            related_patterns = self._dedupe_patterns(patterns_by_code.get(code, []))
            related_documents = self._dedupe_documents(documents_by_code.get(code, []))
            canonical = definition.field_code if definition else self._canonical_from_aliases(code, related_aliases)
            status = self._status(definition, related_aliases, related_patterns)
            frequency = self._frequency(related_aliases, related_patterns, related_documents)
            pattern_texts = [
                " ".join(part for part in (pattern.text_before, pattern.text_after) if part)
                for pattern in related_patterns
            ]
            alias_codes = [alias.raw_field_code for alias in related_aliases] + [alias.canonical_field_code for alias in related_aliases]
            score, reasons, warnings = self.ranker.score_candidate(
                candidate_code=code,
                canonical_code=canonical,
                query_field_code=query_field_code,
                query_text=query_text,
                text_before=text_before,
                text_after=text_after,
                aliases=alias_codes,
                pattern_texts=pattern_texts,
                frequency=frequency,
                status=status,
            )
            if score <= 0:
                continue
            candidates.append(
                FieldCandidate(
                    candidate_field_code=code,
                    canonical_field_code=canonical,
                    display_name=definition.display_name if definition else None,
                    status=status,
                    confidence_score=score,
                    frequency=frequency,
                    evidence_type=self._evidence_type(definition, related_aliases, related_patterns, related_documents),
                    source_documents=tuple(self._document_evidence(related_documents)),
                    matched_aliases=tuple(sorted(set(alias_codes))),
                    matched_patterns=tuple(self._pattern_evidence(related_patterns)),
                    text_before_examples=tuple(self._examples(pattern.text_before for pattern in related_patterns)),
                    text_after_examples=tuple(self._examples(pattern.text_after for pattern in related_patterns)),
                    reasons=reasons,
                    warnings=warnings,
                )
            )

        return [self._to_rag_evidence(candidate) for candidate in self.ranker.sort_candidates(candidates, limit=limit)]

    @staticmethod
    def _to_rag_evidence(candidate: FieldCandidate) -> RagEvidence:
        return RagEvidence(
            candidate_field_code=candidate.candidate_field_code,
            canonical_field_code=candidate.canonical_field_code,
            display_name=candidate.display_name,
            confidence_score=candidate.confidence_score,
            evidence_type=candidate.evidence_type,
            source_documents=candidate.source_documents,
            matched_aliases=candidate.matched_aliases,
            matched_patterns=candidate.matched_patterns,
            text_before_examples=candidate.text_before_examples,
            text_after_examples=candidate.text_after_examples,
            frequency=candidate.frequency,
            status=candidate.status,
            reasons=candidate.reasons,
            warnings=candidate.warnings,
        )

    @staticmethod
    def _canonical_from_aliases(code: str, aliases: list[FieldAlias]) -> str:
        for alias in aliases:
            if alias.raw_field_code == code:
                return alias.canonical_field_code
        return code

    @staticmethod
    def _status(definition: FieldDefinition | None, aliases: list[FieldAlias], patterns: list[FieldPattern]) -> str:
        statuses = [item.status for item in [definition, *aliases, *patterns] if item is not None]
        if "conflict" in statuses:
            return "conflict"
        if "suggested" in statuses:
            return "suggested"
        return statuses[0] if statuses else "suggested"

    @staticmethod
    def _frequency(
        aliases: list[FieldAlias],
        patterns: list[FieldPattern],
        documents: list[tuple[CorpusDocument, CorpusDocumentField]],
    ) -> int:
        alias_frequency = sum(alias.frequency or 0 for alias in aliases)
        pattern_frequency = sum(pattern.frequency or 0 for pattern in patterns)
        document_frequency = sum(field.occurrences or 0 for _, field in documents)
        return max(alias_frequency, pattern_frequency, document_frequency)

    @staticmethod
    def _evidence_type(
        definition: FieldDefinition | None,
        aliases: list[FieldAlias],
        patterns: list[FieldPattern],
        documents: list[tuple[CorpusDocument, CorpusDocumentField]],
    ) -> str:
        parts = []
        if definition:
            parts.append("field_definition")
        if aliases:
            parts.append("alias")
        if patterns:
            parts.append("pattern")
        if documents:
            parts.append("document")
        return "+".join(parts) or "unknown"

    @staticmethod
    def _pattern_evidence(patterns: list[FieldPattern]) -> list[PatternEvidence]:
        return [
            PatternEvidence(
                raw_field_code=pattern.raw_field_code,
                canonical_field_code=pattern.canonical_field_code,
                text_before=pattern.text_before,
                text_after=pattern.text_after,
                frequency=pattern.frequency,
                confidence=pattern.confidence,
                status=pattern.status,
                pattern_source_file=pattern.pattern_source_file,
                document_type=pattern.document_type,
                act_type=pattern.act_type,
            )
            for pattern in patterns[:5]
        ]

    @staticmethod
    def _document_evidence(rows: list[tuple[CorpusDocument, CorpusDocumentField]]) -> list[DocumentEvidence]:
        return [
            DocumentEvidence(
                document_id=document.id,
                filename=document.filename,
                source_path=document.source_path,
                document_type=document.document_type,
                act_type=document.act_type,
                marker_count=document.marker_count,
                occurrences=document_field.occurrences,
            )
            for document, document_field in rows[:5]
        ]

    @staticmethod
    def _examples(values) -> list[str]:
        examples = []
        for value in values:
            cleaned = (value or "").strip()
            if cleaned and cleaned not in examples:
                examples.append(cleaned)
            if len(examples) >= 5:
                break
        return examples

    @staticmethod
    def _dedupe_patterns(patterns: list[FieldPattern]) -> list[FieldPattern]:
        seen = set()
        deduped = []
        for pattern in patterns:
            key = (pattern.id, pattern.raw_field_code, pattern.text_before, pattern.text_after)
            if key not in seen:
                seen.add(key)
                deduped.append(pattern)
        return deduped

    @staticmethod
    def _dedupe_documents(rows: list[tuple[CorpusDocument, CorpusDocumentField]]) -> list[tuple[CorpusDocument, CorpusDocumentField]]:
        seen = set()
        deduped = []
        for document, document_field in rows:
            key = (document.id, document_field.id)
            if key not in seen:
                seen.add(key)
                deduped.append((document, document_field))
        return deduped
