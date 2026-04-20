from __future__ import annotations

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.models.base import Base, TimestampMixin


class LegalEntity(TimestampMixin, Base):
    __tablename__ = "legal_entities"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nit: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    legal_representative: Mapped[str | None] = mapped_column(String(160), nullable=True)
    municipality: Mapped[str | None] = mapped_column(String(120), nullable=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    email: Mapped[str | None] = mapped_column(String(120), nullable=True)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")

    representatives: Mapped[list["LegalEntityRepresentative"]] = relationship(
        back_populates="legal_entity",
        cascade="all, delete-orphan",
    )
    case_participations: Mapped[list["CaseParticipant"]] = relationship(back_populates="legal_entity")
