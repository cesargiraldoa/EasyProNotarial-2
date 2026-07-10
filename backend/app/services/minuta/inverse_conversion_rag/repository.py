from __future__ import annotations

from sqlalchemy import and_, event, func, or_
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.services.minuta.inverse_conversion_catalog.field_code_normalizer import FieldCodeNormalizer
from app.services.minuta.inverse_conversion_catalog.models import (
    CorpusDocument,
    CorpusDocumentField,
    FieldAlias,
    FieldDefinition,
    FieldPattern,
)


class ReadOnlyViolation(RuntimeError):
    pass


class InverseConversionReadOnlyRepository:
    """Read-only SQL repository over the inverse conversion catalog tables."""

    _WRITE_PREFIXES = ("insert", "update", "delete", "merge", "alter", "drop", "create", "truncate", "grant", "revoke")

    def __init__(self, db: Session, normalizer: FieldCodeNormalizer | None = None, enforce_read_only: bool = True) -> None:
        self.db = db
        self.normalizer = normalizer or FieldCodeNormalizer()
        self._engine: Engine | None = db.get_bind()
        self._enforce_read_only = enforce_read_only
        if enforce_read_only and self._engine is not None:
            event.listen(self._engine, "before_cursor_execute", self._guard_read_only)

    def close(self) -> None:
        if self._enforce_read_only and self._engine is not None:
            event.remove(self._engine, "before_cursor_execute", self._guard_read_only)
            self._engine = None

    def _guard_read_only(self, conn, cursor, statement, parameters, context, executemany) -> None:
        first = (statement or "").strip().split(None, 1)[0].lower()
        if first in self._WRITE_PREFIXES:
            raise ReadOnlyViolation(f"Inverse conversion RAG repository only allows SELECT statements, got {first!r}.")

    def get_field_definition(self, field_code: str) -> FieldDefinition | None:
        normalized = self.normalizer.normalize(field_code)
        return self.db.query(FieldDefinition).filter(FieldDefinition.field_code == normalized).one_or_none()

    def search_field_definitions(self, query: str, limit: int = 10) -> list[FieldDefinition]:
        normalized = self.normalizer.normalize(query)
        like_values = self._like_values(query, normalized)
        filters = [
            FieldDefinition.field_code.ilike(value) for value in like_values
        ] + [
            FieldDefinition.display_name.ilike(value) for value in like_values
        ]
        return (
            self.db.query(FieldDefinition)
            .filter(or_(*filters))
            .order_by(FieldDefinition.status.asc(), FieldDefinition.confidence.desc(), FieldDefinition.field_code.asc())
            .limit(limit)
            .all()
        )

    def search_aliases(self, query: str, limit: int = 20) -> list[FieldAlias]:
        normalized = self.normalizer.normalize(query)
        like_values = self._like_values(query, normalized)
        filters = []
        for value in like_values:
            filters.extend([FieldAlias.raw_field_code.ilike(value), FieldAlias.canonical_field_code.ilike(value)])
        return (
            self.db.query(FieldAlias)
            .filter(or_(*filters))
            .order_by(FieldAlias.status.asc(), FieldAlias.frequency.desc(), FieldAlias.raw_field_code.asc())
            .limit(limit)
            .all()
        )

    def search_patterns_by_field(self, field_code: str, limit: int = 20) -> list[FieldPattern]:
        codes = self.related_field_codes(field_code)
        return (
            self.db.query(FieldPattern)
            .filter(or_(FieldPattern.raw_field_code.in_(codes), FieldPattern.canonical_field_code.in_(codes)))
            .order_by(FieldPattern.frequency.desc(), FieldPattern.confidence.desc(), FieldPattern.raw_field_code.asc())
            .limit(limit)
            .all()
        )

    def search_patterns_by_text(self, text: str, limit: int = 20) -> list[FieldPattern]:
        filters = self._pattern_text_filters(text)
        if not filters:
            return []
        return (
            self.db.query(FieldPattern)
            .filter(or_(*filters))
            .order_by(FieldPattern.frequency.desc(), FieldPattern.confidence.desc(), FieldPattern.raw_field_code.asc())
            .limit(limit)
            .all()
        )

    def search_documents_by_field(self, field_code: str, limit: int = 20) -> list[tuple[CorpusDocument, CorpusDocumentField]]:
        codes = self.related_field_codes(field_code)
        return (
            self.db.query(CorpusDocument, CorpusDocumentField)
            .join(CorpusDocumentField, CorpusDocumentField.corpus_document_id == CorpusDocument.id)
            .filter(or_(CorpusDocumentField.raw_field_code.in_(codes), CorpusDocumentField.canonical_field_code.in_(codes)))
            .order_by(CorpusDocumentField.occurrences.desc(), CorpusDocument.filename.asc())
            .limit(limit)
            .all()
        )

    def search_similar_context(self, text_before: str | None, text_after: str | None, limit: int = 20) -> list[FieldPattern]:
        filters = []
        filters.extend(self._context_filters(FieldPattern.text_before, text_before))
        filters.extend(self._context_filters(FieldPattern.text_after, text_after))
        if not filters:
            return []
        return (
            self.db.query(FieldPattern)
            .filter(or_(*filters))
            .order_by(FieldPattern.frequency.desc(), FieldPattern.confidence.desc(), FieldPattern.raw_field_code.asc())
            .limit(limit)
            .all()
        )

    def get_field_evidence(self, field_code: str, limit: int = 20) -> dict:
        definition = self.get_field_definition(field_code)
        aliases = self.search_aliases(field_code, limit=limit)
        patterns = self.search_patterns_by_field(field_code, limit=limit)
        documents = self.search_documents_by_field(field_code, limit=limit)
        return {
            "definition": definition,
            "aliases": aliases,
            "patterns": patterns,
            "documents": documents,
        }

    def related_field_codes(self, field_code: str) -> set[str]:
        normalized = self.normalizer.normalize(field_code)
        codes = {normalized}
        aliases = (
            self.db.query(FieldAlias)
            .filter(or_(FieldAlias.raw_field_code == normalized, FieldAlias.canonical_field_code == normalized))
            .all()
        )
        for alias in aliases:
            codes.add(alias.raw_field_code)
            codes.add(alias.canonical_field_code)
        return codes

    def field_frequency(self, field_code: str) -> int:
        codes = self.related_field_codes(field_code)
        result = (
            self.db.query(func.coalesce(func.sum(CorpusDocumentField.occurrences), 0))
            .filter(or_(CorpusDocumentField.raw_field_code.in_(codes), CorpusDocumentField.canonical_field_code.in_(codes)))
            .scalar()
        )
        return int(result or 0)

    def _pattern_text_filters(self, text: str | None):
        filters = []
        for value in self._token_like_values(text):
            filters.extend(
                [
                    FieldPattern.raw_field_code.ilike(value),
                    FieldPattern.canonical_field_code.ilike(value),
                    FieldPattern.text_before.ilike(value),
                    FieldPattern.text_after.ilike(value),
                ]
            )
        return filters

    def _context_filters(self, column, text: str | None):
        return [column.ilike(value) for value in self._token_like_values(text)]

    def _like_values(self, raw: str | None, normalized: str | None) -> list[str]:
        values = []
        for value in (raw, normalized):
            cleaned = (value or "").strip()
            if cleaned:
                values.append(f"%{cleaned}%")
        values.extend(self._token_like_values(normalized))
        return list(dict.fromkeys(values)) or ["%%"]

    def _token_like_values(self, text: str | None) -> list[str]:
        tokens = sorted(self.normalizer.tokens(text), key=len, reverse=True)
        return [f"%{token}%" for token in tokens if len(token) >= 3][:8]
