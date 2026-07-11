from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from typing import Sequence

from sqlalchemy.orm import Session

from app.models.notarial_document_intelligence import (
    NotarialDocument,
    NotarialDocumentBlock,
    NotarialDocumentEmbedding,
    NotarialDocumentEvidence,
    NotarialDocumentParseRun,
    NotarialEmbeddingVersion,
)
from app.services.notarial_document_intelligence.embedding_provider import EmbeddingProvider, NotarialEmbeddingService
from app.services.notarial_document_intelligence.vector_store import NotarialVectorStore


@dataclass(frozen=True)
class HybridRagHit:
    block_id: int
    document_id: int
    parse_run_id: int
    location_key: str
    text: str
    score: float
    lexical_score: float
    vector_score: float
    structural_score: float


class NotarialHybridRagService:
    def __init__(self, db: Session, embedding_provider: EmbeddingProvider | None = None) -> None:
        self.db = db
        self.embedding_service = NotarialEmbeddingService(db, provider=embedding_provider)

    def search(
        self,
        notary_id: int,
        query: str,
        *,
        document_type: str | None = None,
        semantic_type: str | None = None,
        exclude_document_id: int | None = None,
        limit: int = 8,
    ) -> list[HybridRagHit]:
        blocks = self._candidate_blocks(notary_id, document_type=document_type, semantic_type=semantic_type, exclude_document_id=exclude_document_id)
        if not blocks and document_type is not None:
            blocks = self._candidate_blocks(notary_id, document_type=None, semantic_type=semantic_type, exclude_document_id=exclude_document_id)
        lexical = {block.id: _lexical_score(query, block.text) for block in blocks}
        structural = {block.id: _structural_score(block, semantic_type=semantic_type) for block in blocks}
        vector = self._vector_scores(notary_id, query, blocks)
        hits = [
            HybridRagHit(
                block_id=block.id,
                document_id=block.document_id,
                parse_run_id=block.parse_run_id,
                location_key=block.location_key,
                text=block.text,
                score=(0.45 * lexical.get(block.id, 0.0)) + (0.4 * vector.get(block.id, 0.0)) + (0.15 * structural.get(block.id, 0.0)),
                lexical_score=lexical.get(block.id, 0.0),
                vector_score=vector.get(block.id, 0.0),
                structural_score=structural.get(block.id, 0.0),
            )
            for block in blocks
        ]
        return sorted(hits, key=lambda hit: hit.score, reverse=True)[:limit]

    def persist_hits(
        self,
        notary_id: int,
        *,
        target_document_id: int,
        target_parse_run_id: int,
        hits: Sequence[HybridRagHit],
        intelligence_run_id: int | None = None,
        evidence_type: str = "hybrid_rag",
    ) -> None:
        for hit in hits:
            self.db.add(
                NotarialDocumentEvidence(
                    notary_id=notary_id,
                    document_id=target_document_id,
                    parse_run_id=target_parse_run_id,
                    block_id=None,
                    evidence_type=evidence_type,
                    source="hybrid_rag",
                    score=hit.score,
                    payload_json=json.dumps(
                        {
                            "intelligence_run_id": intelligence_run_id,
                            "target_document_id": target_document_id,
                            "target_parse_run_id": target_parse_run_id,
                            "source_document_id": hit.document_id,
                            "source_parse_run_id": hit.parse_run_id,
                            "source_block_id": hit.block_id,
                            "source_location_key": hit.location_key,
                            "lexical_score": hit.lexical_score,
                            "vector_score": hit.vector_score,
                            "structural_score": hit.structural_score,
                            "snippet": hit.text[:500],
                        },
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                )
            )

    def _candidate_blocks(self, notary_id: int, *, document_type: str | None, semantic_type: str | None, exclude_document_id: int | None) -> list[NotarialDocumentBlock]:
        query = (
            self.db.query(NotarialDocumentBlock)
            .join(NotarialDocumentParseRun, NotarialDocumentParseRun.id == NotarialDocumentBlock.parse_run_id)
            .join(NotarialDocument, NotarialDocument.id == NotarialDocumentBlock.document_id)
            .filter(
                NotarialDocumentBlock.notary_id == notary_id,
                NotarialDocumentParseRun.is_active.is_(True),
                NotarialDocumentParseRun.status == "completed",
            )
        )
        if document_type is not None:
            query = query.filter(NotarialDocument.document_type == document_type)
        if semantic_type is not None:
            query = query.filter(NotarialDocumentBlock.semantic_type == semantic_type)
        if exclude_document_id is not None:
            query = query.filter(NotarialDocumentBlock.document_id != exclude_document_id)
        return query.order_by(NotarialDocumentBlock.document_id.asc(), NotarialDocumentBlock.block_index.asc()).all()

    def _vector_scores(self, notary_id: int, query: str, blocks: list[NotarialDocumentBlock]) -> dict[int, float]:
        if not blocks:
            return {}
        version = (
            self.db.query(NotarialEmbeddingVersion)
            .filter(
                NotarialEmbeddingVersion.provider == self.embedding_service.provider.provider_name,
                NotarialEmbeddingVersion.model_name == self.embedding_service.provider.model_name,
                NotarialEmbeddingVersion.dimensions == self.embedding_service.provider.dimensions,
            )
            .order_by(NotarialEmbeddingVersion.id.desc())
            .first()
        )
        if version is None:
            return {}
        query_vector = self.embedding_service.provider.encode([query])[0]
        if self.db.get_bind().dialect.name == "postgresql":
            store = NotarialVectorStore(self.db, dimensions=version.dimensions)
            rows = store.search(notary_id, query_vector, embedding_version_id=version.id, limit=max(len(blocks), 20))
            return {row.source_id: max(0.0, 1.0 - row.distance) for row in rows}
        query_encoded = self.embedding_service.vector_store.encode_vector(query_vector)
        query_values = json.loads(query_encoded)
        embeddings = (
            self.db.query(NotarialDocumentEmbedding)
            .filter(
                NotarialDocumentEmbedding.embedding_version_id == version.id,
                NotarialDocumentEmbedding.source_type == "block",
                NotarialDocumentEmbedding.source_id.in_([block.id for block in blocks]),
            )
            .all()
        )
        scores = {}
        for row in embeddings:
            scores[row.source_id] = max(0.0, 1.0 - _cosine_distance(query_values, json.loads(row.embedding or "[]")))
        return scores


def _lexical_score(query: str, text: str) -> float:
    query_tokens = set(_tokens(query))
    text_tokens = set(_tokens(text))
    if not query_tokens or not text_tokens:
        return 0.0
    return len(query_tokens & text_tokens) / len(query_tokens | text_tokens)


def _structural_score(block: NotarialDocumentBlock, *, semantic_type: str | None) -> float:
    score = 0.2
    if semantic_type and block.semantic_type == semantic_type:
        score += 0.6
    if block.block_type == "table_cell_paragraph":
        score += 0.1
    if block.fixed_variable_label in {"variable", "optional"}:
        score += 0.1
    return min(score, 1.0)


def _tokens(value: str) -> list[str]:
    return re.findall(r"[a-z0-9áéíóúñ]{3,}", (value or "").lower())


def _cosine_distance(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right) or not left:
        return 1.0
    numerator = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0 or right_norm == 0:
        return 1.0
    return 1.0 - (numerator / (left_norm * right_norm))
