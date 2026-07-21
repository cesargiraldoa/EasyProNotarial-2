from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class LegalTarifa(TimestampMixin, Base):
    __tablename__ = "legal_tarifas"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    anio: Mapped[int] = mapped_column(Integer, index=True)
    concepto: Mapped[str] = mapped_column(String(240), index=True)
    valor: Mapped[Decimal | None] = mapped_column(Numeric(14, 4), nullable=True)
    formula: Mapped[str | None] = mapped_column(String(500), nullable=True)
    unidad: Mapped[str | None] = mapped_column(String(80), nullable=True)
    norma_id: Mapped[int | None] = mapped_column(ForeignKey("legal_normas.id", ondelete="SET NULL"), nullable=True, index=True)
    vigencia_desde: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    vigencia_hasta: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
