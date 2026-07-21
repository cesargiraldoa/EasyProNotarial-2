from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass
from datetime import date
from typing import Iterable, Protocol

from sqlalchemy import false, or_, select
from sqlalchemy.orm import Session

from app.models.legal_clausula import LegalClausula
from app.models.legal_embedding import LegalEmbedding
from app.models.legal_norma import LegalNorma

EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_DIMENSIONS = 384
_NON_OPERATIVE_STATES = {"derogada_total", "inexequible", "suspendida", "compilada"}


class LegalEmbeddingProvider(Protocol):
    provider_name: str
    model_name: str
    dimensions: int

    def encode(self, texts: Iterable[str]) -> list[list[float]]:
        ...


class SentenceTransformerLegalEmbeddingProvider:
    provider_name = "sentence-transformers"
    model_name = EMBEDDING_MODEL_NAME
    dimensions = EMBEDDING_DIMENSIONS

    def __init__(self) -> None:
        self._model = None

    def _load_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as exc:  # pragma: no cover - depends on optional runtime package
                raise RuntimeError("sentence-transformers is required for legal corpus embeddings.") from exc
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def encode(self, texts: Iterable[str]) -> list[list[float]]:
        model = self._load_model()
        vectors = model.encode(list(texts), normalize_embeddings=True)
        return [[float(value) for value in vector] for vector in vectors]


class HashLegalEmbeddingProvider:
    provider_name = "hash"
    model_name = "hash-legal-fallback"
    dimensions = EMBEDDING_DIMENSIONS

    def encode(self, texts: Iterable[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in texts:
            vector = [0.0] * self.dimensions
            for token in _tokens(text):
                digest = hashlib.sha1(token.encode("utf-8")).digest()
                index = int.from_bytes(digest[:4], "big") % self.dimensions
                vector[index] += 1.0
            vectors.append(_normalize(vector))
        return vectors


@dataclass(frozen=True)
class RagHit:
    source_type: str
    source_id: int
    source_ref: str
    titulo: str
    chunk_text: str
    score: float
    acto_code: str | None
    vigencia_desde: date | None
    vigencia_hasta: date | None


_default_provider: LegalEmbeddingProvider | None = None


def get_default_legal_embedding_provider() -> LegalEmbeddingProvider:
    global _default_provider
    if _default_provider is None:
        _default_provider = SentenceTransformerLegalEmbeddingProvider()
    return _default_provider


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9áéíóúñü]+", text.lower())


def _normalize(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b:
        return 0.0
    limit = min(len(a), len(b))
    return max(0.0, sum(a[index] * b[index] for index in range(limit)))


def _decode_vector(value: str | list[float] | None) -> list[float]:
    if value is None:
        return []
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return []
        return [float(item) for item in parsed]
    return [float(item) for item in value]


def _vigente(desde: date | None, hasta: date | None, fecha: date) -> bool:
    return (desde is None or desde <= fecha) and (hasta is None or hasta >= fecha)


def _norma_chunk(norma: LegalNorma) -> str:
    ref = f"{norma.tipo} {norma.numero} de {norma.anio}"
    if norma.articulo:
        ref += f" {norma.articulo}"
    return " ".join(part for part in [ref, norma.materia, norma.texto, norma.notas] if part)


def _clausula_chunk(clausula: LegalClausula) -> str:
    return " ".join(part for part in [clausula.titulo, clausula.texto, clausula.notas] if part)


def _sources(session: Session, source_ids: dict[str, set[int]] | None = None) -> list[tuple[str, int, str, date | None, date | None, str | None]]:
    rows: list[tuple[str, int, str, date | None, date | None, str | None]] = []
    norma_stmt = select(LegalNorma)
    clausula_stmt = select(LegalClausula)
    if source_ids:
        norma_ids = source_ids.get("norma", set())
        clausula_ids = source_ids.get("clausula", set())
        norma_stmt = norma_stmt.where(LegalNorma.id.in_(norma_ids)) if norma_ids else norma_stmt.where(false())
        clausula_stmt = clausula_stmt.where(LegalClausula.id.in_(clausula_ids)) if clausula_ids else clausula_stmt.where(false())

    for norma in session.execute(norma_stmt.order_by(LegalNorma.id)).scalars():
        rows.append(("norma", norma.id, _norma_chunk(norma), norma.vigencia_desde, norma.vigencia_hasta, None))
    for clausula in session.execute(clausula_stmt.order_by(LegalClausula.id)).scalars():
        rows.append(("clausula", clausula.id, _clausula_chunk(clausula), clausula.vigencia_desde, clausula.vigencia_hasta, clausula.acto_code))
    return rows


def _upsert_embedding(
    session: Session,
    source_type: str,
    source_id: int,
    chunk_text: str,
    embedding: list[float],
    vigencia_desde: date | None,
    vigencia_hasta: date | None,
    acto_code: str | None,
) -> bool:
    existing = session.execute(
        select(LegalEmbedding).where(LegalEmbedding.source_type == source_type, LegalEmbedding.source_id == source_id)
    ).scalar_one_or_none()
    values = {
        "chunk_text": chunk_text,
        "embedding": embedding,
        "vigencia_desde": vigencia_desde,
        "vigencia_hasta": vigencia_hasta,
        "acto_code": acto_code,
    }
    if existing is None:
        session.add(LegalEmbedding(source_type=source_type, source_id=source_id, **values))
        return True
    for key, value in values.items():
        setattr(existing, key, value)
    return False


def seed_legal_embeddings(session: Session, provider: LegalEmbeddingProvider | None = None) -> dict[str, int | str]:
    provider = provider or get_default_legal_embedding_provider()
    sources = _sources(session)
    texts = [source[2] for source in sources]
    try:
        vectors = provider.encode(texts) if texts else []
    except Exception:
        provider = HashLegalEmbeddingProvider()
        vectors = provider.encode(texts) if texts else []

    created = 0
    updated = 0
    for (source_type, source_id, chunk_text, desde, hasta, acto_code), vector in zip(sources, vectors, strict=False):
        was_created = _upsert_embedding(session, source_type, source_id, chunk_text, vector, desde, hasta, acto_code)
        created += 1 if was_created else 0
        updated += 0 if was_created else 1
    session.commit()
    return {"created": created, "updated": updated, "provider": provider.provider_name, "model": provider.model_name}


def reindex_legal_sources(
    session: Session,
    source_ids: dict[str, set[int]],
    provider: LegalEmbeddingProvider | None = None,
) -> dict[str, int | str]:
    provider = provider or get_default_legal_embedding_provider()
    sources = _sources(session, source_ids)
    texts = [source[2] for source in sources]
    try:
        vectors = provider.encode(texts) if texts else []
    except Exception:
        provider = HashLegalEmbeddingProvider()
        vectors = provider.encode(texts) if texts else []

    created = 0
    updated = 0
    for (source_type, source_id, chunk_text, desde, hasta, acto_code), vector in zip(sources, vectors, strict=False):
        was_created = _upsert_embedding(session, source_type, source_id, chunk_text, vector, desde, hasta, acto_code)
        created += 1 if was_created else 0
        updated += 0 if was_created else 1
    session.flush()
    return {"created": created, "updated": updated, "provider": provider.provider_name, "model": provider.model_name}


def _source_hit(session: Session, embedding: LegalEmbedding, fecha: date) -> tuple[str, str] | None:
    if embedding.source_type == "norma":
        norma = session.get(LegalNorma, embedding.source_id)
        if norma is None:
            return None
        if norma.aplicabilidad_operativa != "vigente" or norma.estado in _NON_OPERATIVE_STATES:
            return None
        if not _vigente(norma.vigencia_desde, norma.vigencia_hasta, fecha):
            return None
        title = f"{norma.tipo} {norma.numero}/{norma.anio}" + (f" {norma.articulo}" if norma.articulo else "")
        return norma.slug, title

    clausula = session.get(LegalClausula, embedding.source_id)
    if clausula is None:
        return None
    if not _vigente(clausula.vigencia_desde, clausula.vigencia_hasta, fecha):
        return None
    return f"clausula-{clausula.id}", clausula.titulo


def buscar_corpus(
    session: Session,
    query: str,
    fecha: date,
    acto_code: str | None = None,
    top_k: int = 5,
    provider: LegalEmbeddingProvider | None = None,
) -> list[RagHit]:
    provider = provider or get_default_legal_embedding_provider()
    try:
        query_vector = provider.encode([query])[0]
    except Exception:
        provider = HashLegalEmbeddingProvider()
        query_vector = provider.encode([query])[0]

    stmt = (
        select(LegalEmbedding)
        .where(or_(LegalEmbedding.vigencia_desde.is_(None), LegalEmbedding.vigencia_desde <= fecha))
        .where(or_(LegalEmbedding.vigencia_hasta.is_(None), LegalEmbedding.vigencia_hasta >= fecha))
    )
    if acto_code:
        stmt = stmt.where(or_(LegalEmbedding.acto_code.is_(None), LegalEmbedding.acto_code == acto_code))

    hits: list[RagHit] = []
    for embedding in session.execute(stmt).scalars():
        source = _source_hit(session, embedding, fecha)
        if source is None:
            continue
        score = _cosine(query_vector, _decode_vector(embedding.embedding))
        if score <= 0:
            continue
        source_ref, title = source
        hits.append(
            RagHit(
                source_type=embedding.source_type,
                source_id=embedding.source_id,
                source_ref=source_ref,
                titulo=title,
                chunk_text=embedding.chunk_text,
                score=score,
                acto_code=embedding.acto_code,
                vigencia_desde=embedding.vigencia_desde,
                vigencia_hasta=embedding.vigencia_hasta,
            )
        )
    hits.sort(key=lambda item: item.score, reverse=True)
    return hits[:top_k]
