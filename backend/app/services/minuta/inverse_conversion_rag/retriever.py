from __future__ import annotations

from app.services.minuta.inverse_conversion_rag.evidence_builder import EvidenceBuilder
from app.services.minuta.inverse_conversion_rag.models import RagQuery, RetrievalResult
from app.services.minuta.inverse_conversion_rag.repository import InverseConversionReadOnlyRepository


class InverseConversionRetriever:
    def __init__(
        self,
        repository: InverseConversionReadOnlyRepository,
        evidence_builder: EvidenceBuilder | None = None,
    ) -> None:
        self.repository = repository
        self.evidence_builder = evidence_builder or EvidenceBuilder()

    def retrieve_by_field_code(self, field_code: str, limit: int = 10) -> RetrievalResult:
        evidence = self.repository.get_field_evidence(field_code, limit=max(limit * 3, 20))
        definition = evidence["definition"]
        definitions = [definition] if definition is not None else self.repository.search_field_definitions(field_code, limit=limit)
        candidates = self.evidence_builder.build_candidates(
            definitions=definitions,
            aliases=evidence["aliases"],
            patterns=evidence["patterns"],
            documents=evidence["documents"],
            query_field_code=field_code,
            limit=limit,
        )
        return RetrievalResult(
            query=RagQuery(field_code=field_code, limit=limit),
            candidates=tuple(candidates),
            total_candidates=len(candidates),
            metadata={"mode": "field_code"},
        )

    def retrieve_by_text_context(self, text: str, limit: int = 10) -> RetrievalResult:
        definitions = self.repository.search_field_definitions(text, limit=max(limit * 2, 20))
        aliases = self.repository.search_aliases(text, limit=max(limit * 3, 30))
        patterns = self.repository.search_patterns_by_text(text, limit=max(limit * 4, 40))
        documents = self._documents_for_patterns(patterns, limit=max(limit * 3, 20))
        candidates = self.evidence_builder.build_candidates(
            definitions=definitions,
            aliases=aliases,
            patterns=patterns,
            documents=documents,
            query_text=text,
            limit=limit,
        )
        return RetrievalResult(
            query=RagQuery(text=text, limit=limit),
            candidates=tuple(candidates),
            total_candidates=len(candidates),
            metadata={"mode": "text_context"},
        )

    def retrieve_by_before_after(self, text_before: str | None, text_after: str | None, limit: int = 10) -> RetrievalResult:
        patterns = self.repository.search_similar_context(text_before, text_after, limit=max(limit * 4, 40))
        documents = self._documents_for_patterns(patterns, limit=max(limit * 3, 20))
        definitions = self._definitions_for_patterns(patterns, limit=max(limit * 2, 20))
        aliases = self._aliases_for_patterns(patterns, limit=max(limit * 3, 30))
        candidates = self.evidence_builder.build_candidates(
            definitions=definitions,
            aliases=aliases,
            patterns=patterns,
            documents=documents,
            text_before=text_before,
            text_after=text_after,
            limit=limit,
        )
        return RetrievalResult(
            query=RagQuery(text_before=text_before, text_after=text_after, limit=limit),
            candidates=tuple(candidates),
            total_candidates=len(candidates),
            metadata={"mode": "before_after"},
        )

    def retrieve_candidates_for_marker(
        self,
        raw_marker: str,
        context_before: str | None,
        context_after: str | None,
        limit: int = 10,
    ) -> RetrievalResult:
        field_result = self.retrieve_by_field_code(raw_marker, limit=limit)
        context_result = self.retrieve_by_before_after(context_before, context_after, limit=limit)
        by_code = {candidate.canonical_field_code: candidate for candidate in context_result.candidates}
        for candidate in field_result.candidates:
            by_code[candidate.canonical_field_code] = candidate
        candidates = sorted(by_code.values(), key=lambda item: (-item.confidence_score, item.canonical_field_code))[:limit]
        return RetrievalResult(
            query=RagQuery(field_code=raw_marker, text_before=context_before, text_after=context_after, limit=limit),
            candidates=tuple(candidates),
            total_candidates=len(candidates),
            metadata={"mode": "marker_with_context"},
        )

    def _documents_for_patterns(self, patterns, limit: int):
        rows = []
        for pattern in patterns:
            rows.extend(self.repository.search_documents_by_field(pattern.canonical_field_code or pattern.raw_field_code, limit=limit))
        return rows[:limit]

    def _definitions_for_patterns(self, patterns, limit: int):
        definitions = []
        seen = set()
        for pattern in patterns:
            code = pattern.canonical_field_code or pattern.raw_field_code
            definition = self.repository.get_field_definition(code)
            if definition is not None and definition.field_code not in seen:
                seen.add(definition.field_code)
                definitions.append(definition)
            if len(definitions) >= limit:
                break
        return definitions

    def _aliases_for_patterns(self, patterns, limit: int):
        aliases = []
        seen = set()
        for pattern in patterns:
            for alias in self.repository.search_aliases(pattern.canonical_field_code or pattern.raw_field_code, limit=limit):
                key = (alias.raw_field_code, alias.canonical_field_code)
                if key not in seen:
                    seen.add(key)
                    aliases.append(alias)
            if len(aliases) >= limit:
                break
        return aliases[:limit]
