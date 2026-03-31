from __future__ import annotations

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class NumberingSequence(TimestampMixin, Base):
    __tablename__ = "numbering_sequences"
    __table_args__ = (UniqueConstraint("sequence_type", "notary_id", "year", name="uq_numbering_sequence_scope"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    sequence_type: Mapped[str] = mapped_column(String(40), index=True)
    notary_id: Mapped[int | None] = mapped_column(ForeignKey("notaries.id"), nullable=True, index=True)
    year: Mapped[int] = mapped_column(index=True)
    current_value: Mapped[int] = mapped_column(default=0)

    notary: Mapped["Notary | None"] = relationship(back_populates="numbering_sequences")
