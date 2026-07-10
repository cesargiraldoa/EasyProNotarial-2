from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


@dataclass(frozen=True)
class SemanticHit:
    source_type: str
    source_id: int
    field_code: str | None
    canonical_field_code: str | None
    content: str
    score: float
    metadata: dict[str, Any]


class SemanticRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def has_embeddings(self) -> bool:
        try:
            return bool(self.db.execute(text("select count(*) from inverse_conversion_embeddings where embedding is not null")).scalar() or 0)
        except Exception:
            return False

    def upsert_embedding_record(
        self,
        source_type: str,
        source_id: int,
        content: str,
        field_code: str | None = None,
        canonical_field_code: str | None = None,
        embedding: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        content_hash = self.content_hash(source_type, source_id, content)
        payload = {
            "source_type": source_type,
            "source_id": source_id,
            "field_code": field_code,
            "canonical_field_code": canonical_field_code,
            "content": content,
            "content_hash": content_hash,
            "embedding": embedding,
            "metadata_json": json.dumps(metadata or {}, ensure_ascii=False),
        }
        existing = self.db.execute(
            text("select id from inverse_conversion_embeddings where content_hash = :content_hash"),
            {"content_hash": content_hash},
        ).scalar()
        if existing:
            self.db.execute(
                text(
                    """
                    update inverse_conversion_embeddings
                    set content=:content, field_code=:field_code, canonical_field_code=:canonical_field_code,
                        embedding=:embedding, metadata_json=:metadata_json, updated_at=CURRENT_TIMESTAMP
                    where id=:id
                    """
                ),
                {**payload, "id": existing},
            )
        else:
            self.db.execute(
                text(
                    """
                    insert into inverse_conversion_embeddings
                    (source_type, source_id, field_code, canonical_field_code, content, content_hash, embedding, metadata_json)
                    values
                    (:source_type, :source_id, :field_code, :canonical_field_code, :content, :content_hash, :embedding, :metadata_json)
                    """
                ),
                payload,
            )

    def lexical_search(self, query: str, limit: int = 10) -> list[SemanticHit]:
        tokens = [token for token in self._tokens(query) if len(token) >= 3][:8]
        if not tokens:
            return []
        where = " or ".join(f"upper(content) like :token_{index}" for index, _ in enumerate(tokens))
        params = {f"token_{index}": f"%{token}%" for index, token in enumerate(tokens)}
        rows = self.db.execute(
            text(
                f"""
                select source_type, source_id, field_code, canonical_field_code, content, metadata_json
                from inverse_conversion_embeddings
                where {where}
                limit :limit
                """
            ),
            {**params, "limit": limit},
        ).fetchall()
        return [
            SemanticHit(
                source_type=row.source_type,
                source_id=row.source_id,
                field_code=row.field_code,
                canonical_field_code=row.canonical_field_code,
                content=row.content,
                score=self._overlap(query, row.content),
                metadata=json.loads(row.metadata_json or "{}"),
            )
            for row in rows
        ]

    def semantic_search(self, query: str, limit: int = 10) -> list[SemanticHit]:
        if not self.has_embeddings():
            return self.lexical_search(query, limit=limit)
        return self.lexical_search(query, limit=limit)

    @staticmethod
    def content_hash(source_type: str, source_id: int, content: str) -> str:
        return hashlib.sha256(f"{source_type}:{source_id}:{content}".encode("utf-8")).hexdigest()

    @staticmethod
    def _tokens(value: str) -> set[str]:
        return {token.upper() for token in value.replace("_", " ").split() if token.strip()}

    def _overlap(self, left: str, right: str) -> float:
        left_tokens = self._tokens(left)
        right_tokens = self._tokens(right)
        if not left_tokens or not right_tokens:
            return 0.0
        return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)
