from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin
from app.models.legal_types import LegalJSONB


class LegalRegla(TimestampMixin, Base):
    __tablename__ = "legal_reglas"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    acto_code: Mapped[str] = mapped_column(String(80), index=True)
    codigo: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    condicion_json: Mapped[dict[str, Any]] = mapped_column(LegalJSONB, nullable=False)
    efecto: Mapped[str] = mapped_column(Text)
    severidad: Mapped[str] = mapped_column(String(20), index=True)
    mensaje: Mapped[str] = mapped_column(Text)
    norma_id: Mapped[int | None] = mapped_column(ForeignKey("legal_normas.id", ondelete="SET NULL"), nullable=True, index=True)
    vigencia_desde: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    vigencia_hasta: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
