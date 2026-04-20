from __future__ import annotations

from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class CaseAct(TimestampMixin, Base):
    __tablename__ = "case_acts"
    __table_args__ = (Index("ix_case_acts_case_id_act_order", "case_id", "act_order"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"), index=True)
    act_code: Mapped[str] = mapped_column(String(80))
    act_label: Mapped[str] = mapped_column(String(200))
    act_order: Mapped[int] = mapped_column(Integer)
    roles_json: Mapped[str] = mapped_column(Text, default="[]")

    case: Mapped["Case"] = relationship(back_populates="acts")
