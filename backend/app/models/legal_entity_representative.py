from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.models.base import Base, TimestampMixin


class LegalEntityRepresentative(TimestampMixin, Base):
    __tablename__ = "legal_entity_representatives"
    __table_args__ = (UniqueConstraint("legal_entity_id", "person_id", name="uq_entity_representative"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    legal_entity_id: Mapped[int] = mapped_column(ForeignKey("legal_entities.id"), index=True)
    person_id: Mapped[int] = mapped_column(ForeignKey("persons.id"), index=True)
    power_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    legal_entity: Mapped["LegalEntity"] = relationship(back_populates="representatives")
    person: Mapped["Person"] = relationship(back_populates="legal_entity_representations")
