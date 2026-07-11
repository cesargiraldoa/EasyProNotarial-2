from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Protocol, Sequence

from sqlalchemy.orm import Session

from app.models.notarial_document_intelligence import (
    NotarialDocumentBlock,
    NotarialDocumentEmbedding,
    NotarialDocumentParseRun,
    NotarialEmbeddingVersion,
)
from app.services.notarial_document_intelligence.vector_store import NotarialVectorStore


DEFAULT_SENTENCE_TRANSFORMER_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_EMBEDDING_DIMENSIONS = 384


class EmbeddingProvider(Protocol):
    provider_name: str
    model_name: str
    dimensions: int

    def encode(self, texts: Sequence[str]) -> list[list[float]]:
        ...


@dataclass
class SentenceTransformerEmbeddingProvider:
    model_name: str = DEFAULT_SENTENCE_TRANSFORMER_MODEL
    dimensions: int = DEFAULT_EMBEDDING_DIMENSIONS
    provider_name: str = "sentence-transformers"

    def __post_init__(self) -> None:
        self._model = None

    def _load_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as exc:  # pragma: no cover - exercised in deployments missing optional dependency
                raise RuntimeError("sentence-transformers is required for real notarial embeddings.") from exc
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def encode(self, texts: Sequence[str]) -> list[list[float]]:
        model = self._load_model()
        vectors = model.encode(list(texts), normalize_embeddings=True)
        return [[float(value) for value in vector] for vector in vectors]


@dataclass
class HashEmbeddingProvider:
    """Deterministic local provider for unit tests and offline fixtures only."""

    dimensions: int = DEFAULT_EMBEDDING_DIMENSIONS
    provider_name: str = "hash-fixture"
    model_name: str = "sha256-token-fixture"

    def encode(self, texts: Sequence[str]) -> list[list[float]]:
        return [_hash_vector(text, self.dimensions) for text in texts]


class NotarialEmbeddingService:
    def __init__(self, db: Session, provider: EmbeddingProvider | None = None) -> None:
        self.db = db
        self.provider = provider or SentenceTransformerEmbeddingProvider()
        self.vector_store = NotarialVectorStore(db, dimensions=self.provider.dimensions)

    def version_key(self) -> str:
        raw = f"{self.provider.provider_name}:{self.provider.model_name}:{self.provider.dimensions}"
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]
        return f"{self.provider.provider_name}:{self.provider.model_name}:{self.provider.dimensions}:{digest}"

    def get_or_create_version(self, status: str = "active") -> NotarialEmbeddingVersion:
        version_key = self.version_key()
        version = self.db.query(NotarialEmbeddingVersion).filter(NotarialEmbeddingVersion.version_key == version_key).first()
        if version is not None:
            return version
        version = NotarialEmbeddingVersion(
            version_key=version_key,
            provider=self.provider.provider_name,
            model_name=self.provider.model_name,
            dimensions=self.provider.dimensions,
            status=status,
            metadata_json=json.dumps({"normalized": True}, ensure_ascii=False, sort_keys=True),
        )
        self.db.add(version)
        self.db.flush()
        return version

    def reindex_document(self, notary_id: int, document_id: int, parse_run_id: int | None = None) -> dict[str, int | str]:
        active_parse_run_id = parse_run_id or self._active_parse_run_id(notary_id, document_id)
        if active_parse_run_id is None:
            return {"document_id": document_id, "indexed": 0, "skipped": 0, "version_key": self.version_key()}

        blocks = (
            self.db.query(NotarialDocumentBlock)
            .filter(
                NotarialDocumentBlock.notary_id == notary_id,
                NotarialDocumentBlock.document_id == document_id,
                NotarialDocumentBlock.parse_run_id == active_parse_run_id,
            )
            .order_by(NotarialDocumentBlock.block_index.asc())
            .all()
        )
        candidates = [block for block in blocks if (block.text or "").strip()]
        version = self.get_or_create_version()
        existing_by_source = {
            row.source_id: row
            for row in self.db.query(NotarialDocumentEmbedding).filter(
                NotarialDocumentEmbedding.embedding_version_id == version.id,
                NotarialDocumentEmbedding.source_type == "block",
                NotarialDocumentEmbedding.source_id.in_([block.id for block in candidates] or [0]),
            )
        }
        to_encode = [block for block in candidates if existing_by_source.get(block.id) is None or existing_by_source[block.id].content_hash != block.text_hash]
        vectors = self.provider.encode([block.text for block in to_encode]) if to_encode else []
        for block, vector in zip(to_encode, vectors):
            existing = existing_by_source.get(block.id)
            encoded = self.vector_store.encode_vector(vector)
            if existing is None:
                self.db.add(
                    NotarialDocumentEmbedding(
                        notary_id=notary_id,
                        document_id=document_id,
                        embedding_version_id=version.id,
                        source_type="block",
                        source_id=block.id,
                        content_hash=block.text_hash,
                        embedding_dimensions=self.provider.dimensions,
                        embedding=encoded,
                        metadata_json=json.dumps({"location_key": block.location_key}, ensure_ascii=False, sort_keys=True),
                    )
                )
            else:
                existing.content_hash = block.text_hash
                existing.embedding = encoded
                existing.embedding_dimensions = self.provider.dimensions
        return {"document_id": document_id, "indexed": len(to_encode), "skipped": len(candidates) - len(to_encode), "version_key": version.version_key}

    def _active_parse_run_id(self, notary_id: int, document_id: int) -> int | None:
        row = (
            self.db.query(NotarialDocumentParseRun.id)
            .filter(
                NotarialDocumentParseRun.notary_id == notary_id,
                NotarialDocumentParseRun.document_id == document_id,
                NotarialDocumentParseRun.is_active.is_(True),
                NotarialDocumentParseRun.status == "completed",
            )
            .first()
        )
        return int(row[0]) if row is not None else None


def _hash_vector(text: str, dimensions: int) -> list[float]:
    values: list[float] = []
    seed = text.encode("utf-8")
    counter = 0
    while len(values) < dimensions:
        digest = hashlib.sha256(seed + counter.to_bytes(4, "big")).digest()
        for byte in digest:
            values.append(((byte / 255.0) * 2.0) - 1.0)
            if len(values) == dimensions:
                break
        counter += 1
    norm = sum(value * value for value in values) ** 0.5
    return [value / norm for value in values] if norm else values
