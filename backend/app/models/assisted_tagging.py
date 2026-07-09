from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class AssistedTaggingJob(TimestampMixin, Base):
    __tablename__ = "assisted_tagging_jobs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    job_uuid: Mapped[str] = mapped_column(String(36), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(32), default="uploaded", index=True)
    notary_id: Mapped[int] = mapped_column(ForeignKey("notaries.id"), index=True)
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    approved_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    document_type: Mapped[str] = mapped_column(String(120), index=True)
    source_filename: Mapped[str] = mapped_column(String(255))
    original_docx_storage_path: Mapped[str] = mapped_column(String(500))
    pretagged_docx_storage_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    approved_docx_storage_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    technical_template_storage_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    template_id: Mapped[int | None] = mapped_column(ForeignKey("document_templates.id"), nullable=True, index=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    warnings_json: Mapped[str] = mapped_column(Text, default="[]")
    structure_json: Mapped[str] = mapped_column(Text, default="{}")
    llm_response_json: Mapped[str] = mapped_column(Text, default="{}")
    audit_json: Mapped[str] = mapped_column(Text, default="{}")
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    fields: Mapped[list["AssistedTaggingField"]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
        order_by="AssistedTaggingField.id.asc()",
    )


class AssistedTaggingField(Base):
    __tablename__ = "assisted_tagging_fields"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("assisted_tagging_jobs.id"), index=True)
    field_code: Mapped[str] = mapped_column(String(120), index=True)
    label: Mapped[str] = mapped_column(String(160))
    original_text: Mapped[str] = mapped_column(Text)
    section: Mapped[str] = mapped_column(String(80), default="general", index=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    occurrences: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(32), default="proposed", index=True)
    source: Mapped[str] = mapped_column(String(32), default="llm")
    warning: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")

    job: Mapped[AssistedTaggingJob] = relationship(back_populates="fields")
