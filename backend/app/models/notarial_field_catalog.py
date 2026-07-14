from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class NotarialFieldCatalog(Base, TimestampMixin):
    __tablename__ = "notarial_field_catalog"
    __table_args__ = (
        UniqueConstraint("code", "notary_id", name="uq_notarial_field_catalog_code_notary"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(120), index=True)
    label: Mapped[str] = mapped_column(String(200))
    field_type: Mapped[str] = mapped_column(String(40), default="text")
    category: Mapped[str] = mapped_column(String(80), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    options_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    scope: Mapped[str] = mapped_column(String(20), default="global", index=True)
    notary_id: Mapped[int | None] = mapped_column(ForeignKey("notaries.id", ondelete="SET NULL"), nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_by_user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")
