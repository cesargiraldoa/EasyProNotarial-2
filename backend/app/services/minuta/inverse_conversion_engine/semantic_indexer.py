from __future__ import annotations

from dataclasses import asdict, dataclass

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.minuta.inverse_conversion_engine.semantic_repository import SemanticRepository


@dataclass(frozen=True)
class SemanticIndexResult:
    scanned: int
    prepared: int
    committed: bool
    embeddings_generated: int
    warnings: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


class SemanticIndexer:
    def __init__(self, db: Session, repository: SemanticRepository | None = None) -> None:
        self.db = db
        self.repository = repository or SemanticRepository(db)

    def index_sources(self, commit: bool = False, limit: int | None = None) -> SemanticIndexResult:
        rows = self._source_rows(limit=limit)
        warnings = ["embedding_provider_unavailable_records_stored_with_null_embedding"]
        if commit:
            for row in rows:
                self.repository.upsert_embedding_record(
                    source_type=row["source_type"],
                    source_id=row["source_id"],
                    field_code=row.get("field_code"),
                    canonical_field_code=row.get("canonical_field_code"),
                    content=row["content"],
                    embedding=None,
                    metadata={"source": "semantic_indexer"},
                )
            self.db.commit()
        return SemanticIndexResult(
            scanned=len(rows),
            prepared=len(rows),
            committed=commit,
            embeddings_generated=0,
            warnings=tuple(warnings),
        )

    def _source_rows(self, limit: int | None = None) -> list[dict]:
        rows: list[dict] = []
        rows.extend(self._patterns())
        rows.extend(self._definitions())
        rows.extend(self._aliases())
        rows.extend(self._document_fields())
        return rows[:limit] if limit else rows

    def _patterns(self) -> list[dict]:
        rows = self.db.execute(
            text("select id, raw_field_code, canonical_field_code, text_before, text_after from field_patterns")
        ).fetchall()
        return [
            {
                "source_type": "field_pattern",
                "source_id": row.id,
                "field_code": row.raw_field_code,
                "canonical_field_code": row.canonical_field_code,
                "content": " ".join(part for part in (row.raw_field_code, row.canonical_field_code, row.text_before, row.text_after) if part),
            }
            for row in rows
        ]

    def _definitions(self) -> list[dict]:
        rows = self.db.execute(text("select id, field_code, display_name, description from field_definitions")).fetchall()
        return [
            {
                "source_type": "field_definition",
                "source_id": row.id,
                "field_code": row.field_code,
                "canonical_field_code": row.field_code,
                "content": " ".join(part for part in (row.field_code, row.display_name, row.description) if part),
            }
            for row in rows
        ]

    def _aliases(self) -> list[dict]:
        rows = self.db.execute(text("select id, raw_field_code, canonical_field_code from field_aliases")).fetchall()
        return [
            {
                "source_type": "field_alias",
                "source_id": row.id,
                "field_code": row.raw_field_code,
                "canonical_field_code": row.canonical_field_code,
                "content": f"{row.raw_field_code} {row.canonical_field_code}",
            }
            for row in rows
        ]

    def _document_fields(self) -> list[dict]:
        rows = self.db.execute(
            text("select id, raw_field_code, canonical_field_code, example_value from corpus_document_fields")
        ).fetchall()
        return [
            {
                "source_type": "corpus_document_field",
                "source_id": row.id,
                "field_code": row.raw_field_code,
                "canonical_field_code": row.canonical_field_code,
                "content": " ".join(part for part in (row.raw_field_code, row.canonical_field_code, row.example_value) if part),
            }
            for row in rows
        ]
