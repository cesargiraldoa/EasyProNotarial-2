from __future__ import annotations

from datetime import date

from sqlalchemy import Date, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin
from app.models.notarial_document_intelligence import EmbeddingVectorType


class LegalEmbedding(TimestampMixin, Base):
    __tablename__ = "legal_embeddings"
    __table_args__ = (
        UniqueConstraint("source_type", "source_id", name="uq_legal_embeddings_source"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    source_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float] | str | None] = mapped_column(EmbeddingVectorType(384), nullable=True)
    vigencia_desde: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    vigencia_hasta: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    acto_code: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
