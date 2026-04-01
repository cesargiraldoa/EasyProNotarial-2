from __future__ import annotations

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class CaseActData(TimestampMixin, Base):
    __tablename__ = "case_act_data"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), unique=True, index=True)
    data_json: Mapped[str] = mapped_column(Text, default="{}")
    gari_draft_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    case: Mapped["Case"] = relationship(back_populates="act_data")
