from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class DocumentTemplate(TimestampMixin, Base):
    __tablename__ = "document_templates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(160), index=True)
    slug: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    case_type: Mapped[str] = mapped_column(String(80), default="escritura", index=True)
    document_type: Mapped[str] = mapped_column(String(120), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    scope_type: Mapped[str] = mapped_column(String(20), default="global", index=True)
    notary_id: Mapped[int | None] = mapped_column(ForeignKey("notaries.id"), nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    source_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    storage_path: Mapped[str | None] = mapped_column(String(400), nullable=True)
    internal_variable_map_json: Mapped[str] = mapped_column(Text, default="{}")

    notary: Mapped["Notary | None"] = relationship(back_populates="document_templates")
    required_roles: Mapped[list["TemplateRequiredRole"]] = relationship(
        back_populates="template",
        cascade="all, delete-orphan",
        order_by="TemplateRequiredRole.step_order.asc()",
    )
    fields: Mapped[list["TemplateField"]] = relationship(
        back_populates="template",
        cascade="all, delete-orphan",
        order_by="TemplateField.step_order.asc()",
    )
    cases: Mapped[list["Case"]] = relationship(back_populates="template")
