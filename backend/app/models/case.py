from __future__ import annotations

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Case(TimestampMixin, Base):
    __tablename__ = "cases"
    __table_args__ = (
        UniqueConstraint("notary_id", "year", "consecutive", name="uq_cases_notary_year_consecutive"),
        UniqueConstraint("internal_case_number", name="uq_cases_internal_case_number"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    notary_id: Mapped[int] = mapped_column(ForeignKey("notaries.id"), index=True)
    template_id: Mapped[int | None] = mapped_column(ForeignKey("document_templates.id"), nullable=True, index=True)
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    case_type: Mapped[str] = mapped_column(String(80), index=True)
    act_type: Mapped[str] = mapped_column(String(120), index=True)
    consecutive: Mapped[int] = mapped_column(Integer, index=True)
    year: Mapped[int] = mapped_column(Integer, index=True)
    internal_case_number: Mapped[str | None] = mapped_column(String(40), nullable=True, index=True)
    official_deed_number: Mapped[str | None] = mapped_column(String(40), nullable=True, index=True)
    official_deed_year: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    current_state: Mapped[str] = mapped_column(String(50), index=True)
    current_owner_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    client_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    protocolist_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    approver_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    titular_notary_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    substitute_notary_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    requires_client_review: Mapped[bool] = mapped_column(Boolean, default=False)
    final_signed_uploaded: Mapped[bool] = mapped_column(Boolean, default=False)
    approved_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    approved_by_role_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    approved_document_version_id: Mapped[int | None] = mapped_column(ForeignKey("case_document_versions.id"), nullable=True)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")

    notary: Mapped["Notary"] = relationship(back_populates="cases")
    template: Mapped["DocumentTemplate | None"] = relationship(back_populates="cases")
    created_by_user: Mapped["User | None"] = relationship(back_populates="created_cases", foreign_keys=[created_by_user_id])
    current_owner_user: Mapped["User | None"] = relationship(back_populates="owned_cases", foreign_keys=[current_owner_user_id])
    client_user: Mapped["User | None"] = relationship(back_populates="client_cases", foreign_keys=[client_user_id])
    protocolist_user: Mapped["User | None"] = relationship(back_populates="protocolist_cases", foreign_keys=[protocolist_user_id])
    approver_user: Mapped["User | None"] = relationship(back_populates="approver_cases", foreign_keys=[approver_user_id])
    titular_notary_user: Mapped["User | None"] = relationship(back_populates="titular_cases", foreign_keys=[titular_notary_user_id])
    substitute_notary_user: Mapped["User | None"] = relationship(back_populates="substitute_cases", foreign_keys=[substitute_notary_user_id])
    approved_by_user: Mapped["User | None"] = relationship(back_populates="approved_cases", foreign_keys=[approved_by_user_id])
    approved_document_version: Mapped["CaseDocumentVersion | None"] = relationship(foreign_keys=[approved_document_version_id])
    timeline_events: Mapped[list["CaseTimelineEvent"]] = relationship(
        back_populates="case",
        cascade="all, delete-orphan",
        order_by="desc(CaseTimelineEvent.created_at)",
    )
    participants: Mapped[list["CaseParticipant"]] = relationship(
        back_populates="case",
        cascade="all, delete-orphan",
        order_by="CaseParticipant.created_at.asc()",
    )
    act_data: Mapped["CaseActData | None"] = relationship(back_populates="case", cascade="all, delete-orphan", uselist=False)
    client_comments: Mapped[list["CaseClientComment"]] = relationship(
        back_populates="case",
        cascade="all, delete-orphan",
        order_by="desc(CaseClientComment.created_at)",
    )
    internal_notes: Mapped[list["CaseInternalNote"]] = relationship(
        back_populates="case",
        cascade="all, delete-orphan",
        order_by="desc(CaseInternalNote.created_at)",
    )
    documents: Mapped[list["CaseDocument"]] = relationship(
        back_populates="case",
        cascade="all, delete-orphan",
        order_by="CaseDocument.category.asc()",
    )
    workflow_events: Mapped[list["CaseWorkflowEvent"]] = relationship(
        back_populates="case",
        cascade="all, delete-orphan",
        order_by="desc(CaseWorkflowEvent.created_at)",
    )
