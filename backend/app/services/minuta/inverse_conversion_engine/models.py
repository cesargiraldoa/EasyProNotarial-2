from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


ENGINE_STATUSES = {"initialized", "running", "completed", "error"}
CANDIDATE_STATUSES = {"accepted_suggested", "needs_human_review", "blocked", "conflict"}


class InverseConversionEmbedding(Base):
    __tablename__ = "inverse_conversion_embeddings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    source_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    field_code: Mapped[str | None] = mapped_column(String(200), nullable=True, index=True)
    canonical_field_code: Mapped[str | None] = mapped_column(String(200), nullable=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    embedding: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class InverseConversionRun(Base):
    __tablename__ = "inverse_conversion_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    input_type: Mapped[str] = mapped_column(String(80), nullable=False)
    input_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="initialized")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class InverseConversionRunStep(Base):
    __tablename__ = "inverse_conversion_run_steps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    step_name: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    input_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    output_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    warnings_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class InverseConversionCandidateRow(Base):
    __tablename__ = "inverse_conversion_candidates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    raw_marker: Mapped[str | None] = mapped_column(String(200), nullable=True)
    context_before: Mapped[str | None] = mapped_column(Text, nullable=True)
    context_after: Mapped[str | None] = mapped_column(Text, nullable=True)
    candidate_field_code: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    canonical_field_code: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    evidence_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    warnings_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    requires_human_review: Mapped[bool] = mapped_column(nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


@dataclass(frozen=True)
class EngineOptions:
    use_llm: bool = False
    use_semantic: bool = False
    persist_audit: bool = True
    limit: int = 8


@dataclass(frozen=True)
class ExtractedContext:
    raw_marker: str | None
    text_before: str
    text_after: str
    source: str = "input"


@dataclass(frozen=True)
class EngineCandidate:
    raw_marker: str | None
    candidate_field_code: str
    canonical_field_code: str
    confidence_score: float
    status: str
    evidence: dict[str, Any]
    warnings: tuple[str, ...] = ()
    requires_human_review: bool = True
    reasons: tuple[str, ...] = ()
    context_before: str | None = None
    context_after: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EngineRunSummary:
    run_id: int | None
    status: str
    requires_human_review: bool
    candidates: tuple[EngineCandidate, ...]
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
