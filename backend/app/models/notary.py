from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Notary(TimestampMixin, Base):
    __tablename__ = "notaries"
    __table_args__ = (
        UniqueConstraint("catalog_identity_key", name="uq_notaries_catalog_identity_key"),
        UniqueConstraint("municipality", "notary_label", "email", name="uq_notaries_catalog_identity"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    catalog_identity_key: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    commercial_name: Mapped[str] = mapped_column(String(120))
    legal_name: Mapped[str] = mapped_column(String(160))
    department: Mapped[str] = mapped_column(String(80), default="Antioquia", index=True)
    municipality: Mapped[str] = mapped_column(String(120), index=True)
    notary_label: Mapped[str] = mapped_column(String(160), index=True)
    logo_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    primary_color: Mapped[str] = mapped_column(String(20), default="#0D2E5D")
    secondary_color: Mapped[str] = mapped_column(String(20), default="#4D5B7C")
    base_color: Mapped[str] = mapped_column(String(20), default="#F4F7FB")
    accent_color: Mapped[str] = mapped_column(String(20), default="#50D690")
    city: Mapped[str] = mapped_column(String(80))
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(Text, nullable=True)
    email: Mapped[str | None] = mapped_column(String(120), nullable=True)
    current_notary_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    business_hours: Mapped[str | None] = mapped_column(Text, nullable=True)
    institutional_data: Mapped[str] = mapped_column(Text, default="")
    commercial_status: Mapped[str] = mapped_column(String(40), default="prospecto", index=True)
    commercial_owner: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    commercial_owner_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    main_contact_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    main_contact_title: Mapped[str | None] = mapped_column(String(120), nullable=True)
    commercial_phone: Mapped[str | None] = mapped_column(Text, nullable=True)
    commercial_email: Mapped[str | None] = mapped_column(String(120), nullable=True)
    last_management_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    next_management_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    commercial_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[str] = mapped_column(String(20), default="media", index=True)
    lead_source: Mapped[str | None] = mapped_column(String(120), nullable=True)
    potential: Mapped[str | None] = mapped_column(String(40), nullable=True)
    internal_observations: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    users: Mapped[list["User"]] = relationship(back_populates="default_notary", foreign_keys="User.default_notary_id")
    role_assignments: Mapped[list["RoleAssignment"]] = relationship(back_populates="notary")
    commercial_owner_user: Mapped["User | None"] = relationship(back_populates="owned_notaries", foreign_keys=[commercial_owner_user_id])
    commercial_activities: Mapped[list["NotaryCommercialActivity"]] = relationship(back_populates="notary", cascade="all, delete-orphan", order_by="desc(NotaryCommercialActivity.occurred_at)")
    crm_audit_logs: Mapped[list["NotaryCrmAuditLog"]] = relationship(back_populates="notary", cascade="all, delete-orphan", order_by="desc(NotaryCrmAuditLog.created_at)")
    cases: Mapped[list["Case"]] = relationship(back_populates="notary", cascade="all, delete-orphan", order_by="desc(Case.updated_at)")
    document_templates: Mapped[list["DocumentTemplate"]] = relationship(back_populates="notary")
    numbering_sequences: Mapped[list["NumberingSequence"]] = relationship(back_populates="notary")
