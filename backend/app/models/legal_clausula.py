from __future__ import annotations

from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class LegalClausula(TimestampMixin, Base):
    __tablename__ = "legal_clausulas"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    acto_code: Mapped[str] = mapped_column(String(80), index=True)
    orden: Mapped[int] = mapped_column(Integer, index=True)
    titulo: Mapped[str] = mapped_column(String(240))
    texto: Mapped[str] = mapped_column(Text)
    capa: Mapped[str] = mapped_column(String(40), index=True)
    norma_id: Mapped[int | None] = mapped_column(ForeignKey("legal_normas.id", ondelete="SET NULL"), nullable=True, index=True)
    notaria_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    condicional: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    vigencia_desde: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    vigencia_hasta: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    notas: Mapped[str | None] = mapped_column(Text, nullable=True)
