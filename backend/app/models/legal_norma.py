from __future__ import annotations

from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class LegalNorma(TimestampMixin, Base):
    __tablename__ = "legal_normas"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    tipo: Mapped[str] = mapped_column(String(40), index=True)
    numero: Mapped[str] = mapped_column(String(80), index=True)
    anio: Mapped[int] = mapped_column(Integer, index=True)
    articulo: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    materia: Mapped[str] = mapped_column(String(160), index=True)
    autoridad: Mapped[str] = mapped_column(String(160))
    estado: Mapped[str] = mapped_column(String(40), index=True)
    vigencia_formal: Mapped[str] = mapped_column(String(80), index=True)
    aplicabilidad_operativa: Mapped[str] = mapped_column(String(80), index=True)
    vigencia_desde: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    vigencia_hasta: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    url_oficial: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    confianza: Mapped[str] = mapped_column(String(20), index=True)
    fecha_verificacion: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    texto: Mapped[str | None] = mapped_column(Text, nullable=True)
    notas: Mapped[str | None] = mapped_column(Text, nullable=True)
    slug: Mapped[str] = mapped_column(String(180), unique=True, index=True)

    relaciones_origen: Mapped[list["LegalNormaRelacion"]] = relationship(
        back_populates="norma_origen",
        foreign_keys="LegalNormaRelacion.norma_origen_id",
        cascade="all, delete-orphan",
    )
    relaciones_destino: Mapped[list["LegalNormaRelacion"]] = relationship(
        back_populates="norma_destino",
        foreign_keys="LegalNormaRelacion.norma_destino_id",
    )


class LegalNormaRelacion(TimestampMixin, Base):
    __tablename__ = "legal_norma_relaciones"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    norma_origen_id: Mapped[int] = mapped_column(ForeignKey("legal_normas.id", ondelete="CASCADE"), index=True)
    norma_destino_id: Mapped[int] = mapped_column(ForeignKey("legal_normas.id", ondelete="CASCADE"), index=True)
    tipo: Mapped[str] = mapped_column(String(40), index=True)
    articulo_afectado: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    fecha_efecto: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    notas: Mapped[str | None] = mapped_column(Text, nullable=True)

    norma_origen: Mapped[LegalNorma] = relationship(
        back_populates="relaciones_origen",
        foreign_keys=[norma_origen_id],
    )
    norma_destino: Mapped[LegalNorma] = relationship(
        back_populates="relaciones_destino",
        foreign_keys=[norma_destino_id],
    )
