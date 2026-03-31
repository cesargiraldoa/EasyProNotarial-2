from __future__ import annotations

from sqlalchemy import Boolean, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Person(TimestampMixin, Base):
    __tablename__ = "persons"
    __table_args__ = (UniqueConstraint("document_type", "document_number", name="uq_person_document"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    document_type: Mapped[str] = mapped_column(String(40), index=True)
    document_number: Mapped[str] = mapped_column(String(40), index=True)
    full_name: Mapped[str] = mapped_column(String(160), index=True)
    sex: Mapped[str | None] = mapped_column(String(20), nullable=True)
    nationality: Mapped[str | None] = mapped_column(String(80), nullable=True)
    marital_status: Mapped[str | None] = mapped_column(String(40), nullable=True)
    profession: Mapped[str | None] = mapped_column(String(120), nullable=True)
    municipality: Mapped[str | None] = mapped_column(String(120), nullable=True)
    is_transient: Mapped[bool] = mapped_column(Boolean, default=False)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(120), nullable=True)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")

    case_participations: Mapped[list["CaseParticipant"]] = relationship(back_populates="person")
