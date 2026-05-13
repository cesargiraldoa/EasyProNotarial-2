from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("document_type", "document_number", name="uq_users_document_type_document_number"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(160))
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    document_type: Mapped[str | None] = mapped_column(String(40), nullable=True, index=True)
    document_number: Mapped[str | None] = mapped_column(String(40), nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    job_title: Mapped[str | None] = mapped_column(String(80), nullable=True)
    default_notary_id: Mapped[int | None] = mapped_column(ForeignKey("notaries.id"), nullable=True)

    default_notary: Mapped["Notary | None"] = relationship(back_populates="users", foreign_keys=[default_notary_id])
    role_assignments: Mapped[list["RoleAssignment"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    owned_notaries: Mapped[list["Notary"]] = relationship(back_populates="commercial_owner_user", foreign_keys="Notary.commercial_owner_user_id")
    commercial_activities: Mapped[list["NotaryCommercialActivity"]] = relationship(back_populates="responsible_user", foreign_keys="NotaryCommercialActivity.responsible_user_id")
    crm_audit_logs: Mapped[list["NotaryCrmAuditLog"]] = relationship(back_populates="actor_user", foreign_keys="NotaryCrmAuditLog.actor_user_id")
    owned_cases: Mapped[list["Case"]] = relationship(back_populates="current_owner_user", foreign_keys="Case.current_owner_user_id")
    created_cases: Mapped[list["Case"]] = relationship(back_populates="created_by_user", foreign_keys="Case.created_by_user_id")
    approved_cases: Mapped[list["Case"]] = relationship(back_populates="approved_by_user", foreign_keys="Case.approved_by_user_id")
    client_cases: Mapped[list["Case"]] = relationship(back_populates="client_user", foreign_keys="Case.client_user_id")
    protocolist_cases: Mapped[list["Case"]] = relationship(back_populates="protocolist_user", foreign_keys="Case.protocolist_user_id")
    approver_cases: Mapped[list["Case"]] = relationship(back_populates="approver_user", foreign_keys="Case.approver_user_id")
    titular_cases: Mapped[list["Case"]] = relationship(back_populates="titular_notary_user", foreign_keys="Case.titular_notary_user_id")
    substitute_cases: Mapped[list["Case"]] = relationship(back_populates="substitute_notary_user", foreign_keys="Case.substitute_notary_user_id")
    case_timeline_events: Mapped[list["CaseTimelineEvent"]] = relationship(back_populates="actor_user", foreign_keys="CaseTimelineEvent.actor_user_id")
    client_case_comments: Mapped[list["CaseClientComment"]] = relationship(back_populates="created_by_user", foreign_keys="CaseClientComment.created_by_user_id")
    internal_case_notes: Mapped[list["CaseInternalNote"]] = relationship(back_populates="created_by_user", foreign_keys="CaseInternalNote.created_by_user_id")
    case_document_versions: Mapped[list["CaseDocumentVersion"]] = relationship(back_populates="created_by_user", foreign_keys="CaseDocumentVersion.created_by_user_id")
    case_workflow_events: Mapped[list["CaseWorkflowEvent"]] = relationship(back_populates="actor_user", foreign_keys="CaseWorkflowEvent.actor_user_id")
