from __future__ import annotations

from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class LegalJurisprudencia(TimestampMixin, Base):
    __tablename__ = "legal_jurisprudencias"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    tipo: Mapped[str] = mapped_column(String(20), index=True)
    numero: Mapped[str] = mapped_column(String(40), index=True)
    anio: Mapped[int] = mapped_column(Integer, index=True)
    providencia: Mapped[str] = mapped_column(String(160), index=True)
    regla_operacional: Mapped[str] = mapped_column(Text)
    norma_relacionada_id: Mapped[int | None] = mapped_column(ForeignKey("legal_normas.id", ondelete="SET NULL"), nullable=True, index=True)
    fecha: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    url_oficial: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    confianza: Mapped[str] = mapped_column(String(20), index=True)
