from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class TemplateField(Base):
    __tablename__ = "template_fields"
    __table_args__ = (UniqueConstraint("template_id", "field_code", name="uq_template_fields"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    template_id: Mapped[int] = mapped_column(ForeignKey("document_templates.id"), index=True)
    field_code: Mapped[str] = mapped_column(String(120), index=True)
    label: Mapped[str] = mapped_column(String(160))
    field_type: Mapped[str] = mapped_column(String(40), default="text")
    section: Mapped[str] = mapped_column(String(80), default="acto")
    is_required: Mapped[bool] = mapped_column(Boolean, default=True)
    options_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    placeholder_key: Mapped[str | None] = mapped_column(String(160), nullable=True)
    help_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    step_order: Mapped[int] = mapped_column(default=1)

    template: Mapped["DocumentTemplate"] = relationship(back_populates="fields")
