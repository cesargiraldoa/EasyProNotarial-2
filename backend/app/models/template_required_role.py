from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class TemplateRequiredRole(Base):
    __tablename__ = "template_required_roles"
    __table_args__ = (UniqueConstraint("template_id", "role_code", name="uq_template_required_roles"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    template_id: Mapped[int] = mapped_column(ForeignKey("document_templates.id"), index=True)
    role_code: Mapped[str] = mapped_column(String(80), index=True)
    label: Mapped[str] = mapped_column(String(120))
    is_required: Mapped[bool] = mapped_column(Boolean, default=True)
    step_order: Mapped[int] = mapped_column(default=1)

    template: Mapped["DocumentTemplate"] = relationship(back_populates="required_roles")
