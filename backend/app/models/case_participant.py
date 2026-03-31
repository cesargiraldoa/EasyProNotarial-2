from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class CaseParticipant(TimestampMixin, Base):
    __tablename__ = "case_participants"
    __table_args__ = (UniqueConstraint("case_id", "role_code", name="uq_case_participant_role"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)
    person_id: Mapped[int] = mapped_column(ForeignKey("persons.id"), index=True)
    role_code: Mapped[str] = mapped_column(String(80), index=True)
    role_label: Mapped[str] = mapped_column(String(120))
    snapshot_json: Mapped[str] = mapped_column(Text, default="{}")

    case: Mapped["Case"] = relationship(back_populates="participants")
    person: Mapped["Person"] = relationship(back_populates="case_participations")
