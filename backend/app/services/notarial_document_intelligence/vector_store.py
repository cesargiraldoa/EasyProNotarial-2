from __future__ import annotations

import json
import math
from dataclasses import dataclass
from typing import Sequence

from sqlalchemy import bindparam, text
from sqlalchemy.orm import Session

from app.models.notarial_document_intelligence import NotarialDocumentEmbedding


DEFAULT_EMBEDDING_DIMENSIONS = 384


@dataclass(frozen=True)
class VectorSearchResult:
    embedding_id: int
    source_type: str
    source_id: int
    distance: float


class NotarialVectorStore:
    def __init__(self, db: Session, dimensions: int = DEFAULT_EMBEDDING_DIMENSIONS) -> None:
        self.db = db
        self.dimensions = dimensions

    def encode_vector(self, vector: Sequence[float]) -> str:
        values = [float(value) for value in vector]
        if len(values) != self.dimensions:
            raise ValueError(f"Embedding dimension mismatch: expected {self.dimensions}, got {len(values)}.")
        return json.dumps(values, separators=(",", ":"))

    def search(
        self,
        notary_id: int,
        query_vector: Sequence[float],
        *,
        embedding_version_id: int,
        limit: int = 10,
        document_id: int | None = None,
        exclude_document_id: int | None = None,
        source_type: str | None = None,
        source_ids: Sequence[int] | None = None,
    ) -> list[VectorSearchResult]:
        query = self.encode_vector(query_vector)
        source_ids = [int(item) for item in source_ids or []]
        if self.db.bind is not None and self.db.bind.dialect.name == "postgresql":
            return self._search_postgresql(
                notary_id,
                query,
                embedding_version_id=embedding_version_id,
                limit=limit,
                document_id=document_id,
                exclude_document_id=exclude_document_id,
                source_type=source_type,
                source_ids=source_ids,
            )
        return self._search_sqlite(
            notary_id,
            query,
            embedding_version_id=embedding_version_id,
            limit=limit,
            document_id=document_id,
            exclude_document_id=exclude_document_id,
            source_type=source_type,
            source_ids=source_ids,
        )

    def _search_postgresql(
        self,
        notary_id: int,
        query: str,
        *,
        embedding_version_id: int,
        limit: int,
        document_id: int | None,
        exclude_document_id: int | None,
        source_type: str | None,
        source_ids: Sequence[int],
    ) -> list[VectorSearchResult]:
        source_filter = ""
        if source_ids:
            source_filter = "and source_id in :source_ids"
        sql = text(f"""
            select id, source_type, source_id, embedding <=> cast(:query_vector as vector) as distance
            from notarial_document_embeddings
            where notary_id = :notary_id
              and embedding_version_id = :embedding_version_id
              and (:document_id is null or document_id = :document_id)
              and (:exclude_document_id is null or document_id != :exclude_document_id)
              and (:source_type is null or source_type = :source_type)
              {source_filter}
              and embedding is not null
            order by embedding <=> cast(:query_vector as vector)
            limit :limit
        """)
        if source_ids:
            sql = sql.bindparams(bindparam("source_ids", expanding=True))
        params = {
            "notary_id": notary_id,
            "embedding_version_id": embedding_version_id,
            "document_id": document_id,
            "exclude_document_id": exclude_document_id,
            "source_type": source_type,
            "query_vector": query,
            "limit": limit,
        }
        if source_ids:
            params["source_ids"] = list(source_ids)
        rows = self.db.execute(sql, params).all()
        return [
            VectorSearchResult(
                embedding_id=int(row.id),
                source_type=str(row.source_type),
                source_id=int(row.source_id),
                distance=float(row.distance),
            )
            for row in rows
        ]

    def _search_sqlite(
        self,
        notary_id: int,
        query: str,
        *,
        embedding_version_id: int,
        limit: int,
        document_id: int | None,
        exclude_document_id: int | None,
        source_type: str | None,
        source_ids: Sequence[int],
    ) -> list[VectorSearchResult]:
        query_vector = json.loads(query)
        rows = (
            self.db.query(NotarialDocumentEmbedding)
            .filter(
                NotarialDocumentEmbedding.notary_id == notary_id,
                NotarialDocumentEmbedding.embedding_version_id == embedding_version_id,
                NotarialDocumentEmbedding.embedding.isnot(None),
            )
        )
        if document_id is not None:
            rows = rows.filter(NotarialDocumentEmbedding.document_id == document_id)
        if exclude_document_id is not None:
            rows = rows.filter(NotarialDocumentEmbedding.document_id != exclude_document_id)
        if source_type is not None:
            rows = rows.filter(NotarialDocumentEmbedding.source_type == source_type)
        if source_ids:
            rows = rows.filter(NotarialDocumentEmbedding.source_id.in_(list(source_ids)))

        scored: list[VectorSearchResult] = []
        for row in rows.all():
            stored_vector = json.loads(row.embedding or "[]")
            if len(stored_vector) != self.dimensions:
                continue
            scored.append(
                VectorSearchResult(
                    embedding_id=row.id,
                    source_type=row.source_type,
                    source_id=row.source_id,
                    distance=_cosine_distance(query_vector, stored_vector),
                )
            )
        return sorted(scored, key=lambda item: item.distance)[:limit]


def _cosine_distance(left: Sequence[float], right: Sequence[float]) -> float:
    numerator = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0 or right_norm == 0:
        return 1.0
    return 1.0 - (numerator / (left_norm * right_norm))
