from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class BibliotecaAnalysisRun(Base, TimestampMixin):
    __tablename__ = "biblioteca_analysis_runs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    notary_id: Mapped[int | None] = mapped_column(ForeignKey("notaries.id", ondelete="SET NULL"), nullable=True, index=True)
    case_id: Mapped[int | None] = mapped_column(ForeignKey("cases.id", ondelete="SET NULL"), nullable=True, index=True)
    document_id: Mapped[int | None] = mapped_column(ForeignKey("case_documents.id", ondelete="SET NULL"), nullable=True, index=True)
    source_version_id: Mapped[int | None] = mapped_column(ForeignKey("case_document_versions.id", ondelete="SET NULL"), nullable=True, index=True)
    review_version_id: Mapped[int | None] = mapped_column(ForeignKey("case_document_versions.id", ondelete="SET NULL"), nullable=True, index=True)
    document_sha256: Mapped[str] = mapped_column(String(64), index=True)
    document_type: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    model: Mapped[str] = mapped_column(String(80))
    prompt_version: Mapped[str] = mapped_column(String(40), index=True)
    profile_version: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="running", index=True)
    input_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cost_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    detected_fields: Mapped[int] = mapped_column(Integer, default=0)
    anchored_fields: Mapped[int] = mapped_column(Integer, default=0)
    skipped_fields: Mapped[int] = mapped_column(Integer, default=0)
    error_code: Mapped[str | None] = mapped_column(String(120), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    diagnostics_json: Mapped[str] = mapped_column(Text, default="{}")


class FieldSignal(Base, TimestampMixin):
    __tablename__ = "field_signals"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    notary_id: Mapped[int | None] = mapped_column(ForeignKey("notaries.id", ondelete="SET NULL"), nullable=True, index=True)
    analysis_run_id: Mapped[int | None] = mapped_column(ForeignKey("biblioteca_analysis_runs.id", ondelete="SET NULL"), nullable=True, index=True)
    case_id: Mapped[int | None] = mapped_column(ForeignKey("cases.id", ondelete="SET NULL"), nullable=True, index=True)
    document_id: Mapped[int | None] = mapped_column(ForeignKey("case_documents.id", ondelete="SET NULL"), nullable=True, index=True)
    source_version_id: Mapped[int | None] = mapped_column(ForeignKey("case_document_versions.id", ondelete="SET NULL"), nullable=True, index=True)
    review_version_id: Mapped[int | None] = mapped_column(ForeignKey("case_document_versions.id", ondelete="SET NULL"), nullable=True, index=True)
    decision_version_id: Mapped[int | None] = mapped_column(ForeignKey("case_document_versions.id", ondelete="SET NULL"), nullable=True, index=True)
    document_type: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    section_key: Mapped[str | None] = mapped_column(String(160), nullable=True, index=True)
    entity_type: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    role: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    candidate_type: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    anonymized_context: Mapped[str] = mapped_column(Text, default="")
    exact_text_sha256: Mapped[str] = mapped_column(String(64), index=True)
    llm_suggestion_json: Mapped[str] = mapped_column(Text, default="{}")
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    human_decision: Mapped[str] = mapped_column(String(40), index=True)
    final_field_code: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    final_field_instance_id: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    model: Mapped[str | None] = mapped_column(String(80), nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String(40), nullable=True)
    profile_version: Mapped[int | None] = mapped_column(Integer, nullable=True)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")


class NotaryPromptProfile(Base, TimestampMixin):
    __tablename__ = "notary_prompt_profiles"
    __table_args__ = (
        UniqueConstraint("notary_id", "version", name="uq_notary_prompt_profiles_notary_version"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    notary_id: Mapped[int | None] = mapped_column(ForeignKey("notaries.id", ondelete="SET NULL"), nullable=True, index=True)
    version: Mapped[int] = mapped_column(Integer, index=True)
    status: Mapped[str] = mapped_column(String(40), default="draft", index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    compiled_rules_json: Mapped[str] = mapped_column(Text, default="{}")
    aliases_json: Mapped[str] = mapped_column(Text, default="{}")
    positive_patterns_json: Mapped[str] = mapped_column(Text, default="[]")
    negative_patterns_json: Mapped[str] = mapped_column(Text, default="[]")
    field_preferences_json: Mapped[str] = mapped_column(Text, default="{}")
    source_signal_count: Mapped[int] = mapped_column(Integer, default=0)
    last_source_signal_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
