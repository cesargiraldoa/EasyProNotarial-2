"""add legal corpus tables

Revision ID: 20260721_add_legal_corpus_tables
Revises: 20260716_seed_biblioteca_demo_fields
Create Date: 2026-07-21
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260721_add_legal_corpus_tables"
down_revision = "20260716_seed_biblioteca_demo_fields"
branch_labels = None
depends_on = None


def _table_exists(inspector: sa.Inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _index_exists(inspector: sa.Inspector, table_name: str, index_name: str) -> bool:
    return any(index["name"] == index_name for index in inspector.get_indexes(table_name))


def _create_index_if_missing(table_name: str, index_name: str, columns: list[str], unique: bool = False) -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if _table_exists(inspector, table_name) and not _index_exists(inspector, table_name, index_name):
        op.create_index(index_name, table_name, columns, unique=unique)


def _jsonb_type(bind) -> sa.types.TypeEngine:
    if bind.dialect.name == "postgresql":
        return postgresql.JSONB()
    return sa.JSON()


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    ]


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    jsonb_type = _jsonb_type(bind)

    if not _table_exists(inspector, "legal_normas"):
        op.create_table(
            "legal_normas",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("tipo", sa.String(length=40), nullable=False),
            sa.Column("numero", sa.String(length=80), nullable=False),
            sa.Column("anio", sa.Integer(), nullable=False),
            sa.Column("articulo", sa.String(length=80), nullable=True),
            sa.Column("materia", sa.String(length=160), nullable=False),
            sa.Column("autoridad", sa.String(length=160), nullable=False),
            sa.Column("estado", sa.String(length=40), nullable=False),
            sa.Column("vigencia_formal", sa.String(length=80), nullable=False),
            sa.Column("aplicabilidad_operativa", sa.String(length=80), nullable=False),
            sa.Column("vigencia_desde", sa.Date(), nullable=True),
            sa.Column("vigencia_hasta", sa.Date(), nullable=True),
            sa.Column("url_oficial", sa.String(length=1000), nullable=True),
            sa.Column("confianza", sa.String(length=20), nullable=False),
            sa.Column("fecha_verificacion", sa.Date(), nullable=True),
            sa.Column("texto", sa.Text(), nullable=True),
            sa.Column("notas", sa.Text(), nullable=True),
            sa.Column("slug", sa.String(length=180), nullable=False),
            *_timestamps(),
            sa.UniqueConstraint("slug", name="uq_legal_normas_slug"),
        )
        inspector = sa.inspect(bind)

    if not _table_exists(inspector, "legal_norma_relaciones"):
        op.create_table(
            "legal_norma_relaciones",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("norma_origen_id", sa.Integer(), sa.ForeignKey("legal_normas.id", ondelete="CASCADE"), nullable=False),
            sa.Column("norma_destino_id", sa.Integer(), sa.ForeignKey("legal_normas.id", ondelete="CASCADE"), nullable=False),
            sa.Column("tipo", sa.String(length=40), nullable=False),
            sa.Column("articulo_afectado", sa.String(length=80), nullable=True),
            sa.Column("fecha_efecto", sa.Date(), nullable=True),
            sa.Column("notas", sa.Text(), nullable=True),
            *_timestamps(),
        )
        inspector = sa.inspect(bind)

    if not _table_exists(inspector, "legal_clausulas"):
        op.create_table(
            "legal_clausulas",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("acto_code", sa.String(length=80), nullable=False),
            sa.Column("orden", sa.Integer(), nullable=False),
            sa.Column("titulo", sa.String(length=240), nullable=False),
            sa.Column("texto", sa.Text(), nullable=False),
            sa.Column("capa", sa.String(length=40), nullable=False),
            sa.Column("norma_id", sa.Integer(), sa.ForeignKey("legal_normas.id", ondelete="SET NULL"), nullable=True),
            sa.Column("notaria_id", sa.Integer(), nullable=True),
            sa.Column("condicional", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.Column("vigencia_desde", sa.Date(), nullable=True),
            sa.Column("vigencia_hasta", sa.Date(), nullable=True),
            sa.Column("notas", sa.Text(), nullable=True),
            *_timestamps(),
        )
        inspector = sa.inspect(bind)

    if not _table_exists(inspector, "legal_reglas"):
        op.create_table(
            "legal_reglas",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("acto_code", sa.String(length=80), nullable=False),
            sa.Column("codigo", sa.String(length=160), nullable=False),
            sa.Column("condicion_json", jsonb_type, nullable=False),
            sa.Column("efecto", sa.Text(), nullable=False),
            sa.Column("severidad", sa.String(length=20), nullable=False),
            sa.Column("mensaje", sa.Text(), nullable=False),
            sa.Column("norma_id", sa.Integer(), sa.ForeignKey("legal_normas.id", ondelete="SET NULL"), nullable=True),
            sa.Column("vigencia_desde", sa.Date(), nullable=True),
            sa.Column("vigencia_hasta", sa.Date(), nullable=True),
            *_timestamps(),
            sa.UniqueConstraint("codigo", name="uq_legal_reglas_codigo"),
        )
        inspector = sa.inspect(bind)

    if not _table_exists(inspector, "legal_tarifas"):
        op.create_table(
            "legal_tarifas",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("anio", sa.Integer(), nullable=False),
            sa.Column("concepto", sa.String(length=240), nullable=False),
            sa.Column("valor", sa.Numeric(14, 4), nullable=True),
            sa.Column("formula", sa.String(length=500), nullable=True),
            sa.Column("unidad", sa.String(length=80), nullable=True),
            sa.Column("norma_id", sa.Integer(), sa.ForeignKey("legal_normas.id", ondelete="SET NULL"), nullable=True),
            sa.Column("vigencia_desde", sa.Date(), nullable=True),
            sa.Column("vigencia_hasta", sa.Date(), nullable=True),
            *_timestamps(),
        )
        inspector = sa.inspect(bind)

    if not _table_exists(inspector, "legal_jurisprudencias"):
        op.create_table(
            "legal_jurisprudencias",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("tipo", sa.String(length=20), nullable=False),
            sa.Column("numero", sa.String(length=40), nullable=False),
            sa.Column("anio", sa.Integer(), nullable=False),
            sa.Column("providencia", sa.String(length=160), nullable=False),
            sa.Column("regla_operacional", sa.Text(), nullable=False),
            sa.Column("norma_relacionada_id", sa.Integer(), sa.ForeignKey("legal_normas.id", ondelete="SET NULL"), nullable=True),
            sa.Column("fecha", sa.Date(), nullable=True),
            sa.Column("url_oficial", sa.String(length=1000), nullable=True),
            sa.Column("confianza", sa.String(length=20), nullable=False),
            *_timestamps(),
        )
        inspector = sa.inspect(bind)

    indexes = {
        "legal_normas": [
            ("ix_legal_normas_id", ["id"], False),
            ("ix_legal_normas_tipo", ["tipo"], False),
            ("ix_legal_normas_numero", ["numero"], False),
            ("ix_legal_normas_anio", ["anio"], False),
            ("ix_legal_normas_articulo", ["articulo"], False),
            ("ix_legal_normas_materia", ["materia"], False),
            ("ix_legal_normas_estado", ["estado"], False),
            ("ix_legal_normas_vigencia_formal", ["vigencia_formal"], False),
            ("ix_legal_normas_aplicabilidad_operativa", ["aplicabilidad_operativa"], False),
            ("ix_legal_normas_vigencia_desde", ["vigencia_desde"], False),
            ("ix_legal_normas_vigencia_hasta", ["vigencia_hasta"], False),
            ("ix_legal_normas_confianza", ["confianza"], False),
            ("ix_legal_normas_fecha_verificacion", ["fecha_verificacion"], False),
            ("ix_legal_normas_slug", ["slug"], True),
            ("ix_legal_normas_numero_anio_articulo", ["numero", "anio", "articulo"], False),
        ],
        "legal_norma_relaciones": [
            ("ix_legal_norma_relaciones_id", ["id"], False),
            ("ix_legal_norma_relaciones_norma_origen_id", ["norma_origen_id"], False),
            ("ix_legal_norma_relaciones_norma_destino_id", ["norma_destino_id"], False),
            ("ix_legal_norma_relaciones_tipo", ["tipo"], False),
            ("ix_legal_norma_relaciones_articulo_afectado", ["articulo_afectado"], False),
            ("ix_legal_norma_relaciones_fecha_efecto", ["fecha_efecto"], False),
            ("ix_legal_norma_relaciones_pair_tipo", ["norma_origen_id", "norma_destino_id", "tipo"], False),
        ],
        "legal_clausulas": [
            ("ix_legal_clausulas_id", ["id"], False),
            ("ix_legal_clausulas_acto_code", ["acto_code"], False),
            ("ix_legal_clausulas_orden", ["orden"], False),
            ("ix_legal_clausulas_capa", ["capa"], False),
            ("ix_legal_clausulas_norma_id", ["norma_id"], False),
            ("ix_legal_clausulas_notaria_id", ["notaria_id"], False),
            ("ix_legal_clausulas_condicional", ["condicional"], False),
            ("ix_legal_clausulas_vigencia_desde", ["vigencia_desde"], False),
            ("ix_legal_clausulas_vigencia_hasta", ["vigencia_hasta"], False),
            ("ix_legal_clausulas_acto_orden", ["acto_code", "orden"], False),
        ],
        "legal_reglas": [
            ("ix_legal_reglas_id", ["id"], False),
            ("ix_legal_reglas_acto_code", ["acto_code"], False),
            ("ix_legal_reglas_codigo", ["codigo"], True),
            ("ix_legal_reglas_severidad", ["severidad"], False),
            ("ix_legal_reglas_norma_id", ["norma_id"], False),
            ("ix_legal_reglas_vigencia_desde", ["vigencia_desde"], False),
            ("ix_legal_reglas_vigencia_hasta", ["vigencia_hasta"], False),
        ],
        "legal_tarifas": [
            ("ix_legal_tarifas_id", ["id"], False),
            ("ix_legal_tarifas_anio", ["anio"], False),
            ("ix_legal_tarifas_concepto", ["concepto"], False),
            ("ix_legal_tarifas_norma_id", ["norma_id"], False),
            ("ix_legal_tarifas_vigencia_desde", ["vigencia_desde"], False),
            ("ix_legal_tarifas_vigencia_hasta", ["vigencia_hasta"], False),
            ("ix_legal_tarifas_anio_concepto", ["anio", "concepto"], True),
        ],
        "legal_jurisprudencias": [
            ("ix_legal_jurisprudencias_id", ["id"], False),
            ("ix_legal_jurisprudencias_tipo", ["tipo"], False),
            ("ix_legal_jurisprudencias_numero", ["numero"], False),
            ("ix_legal_jurisprudencias_anio", ["anio"], False),
            ("ix_legal_jurisprudencias_providencia", ["providencia"], False),
            ("ix_legal_jurisprudencias_norma_relacionada_id", ["norma_relacionada_id"], False),
            ("ix_legal_jurisprudencias_fecha", ["fecha"], False),
            ("ix_legal_jurisprudencias_confianza", ["confianza"], False),
            ("ix_legal_jurisprudencias_tipo_numero_anio", ["tipo", "numero", "anio"], True),
        ],
    }
    for table_name, table_indexes in indexes.items():
        for index_name, columns, unique in table_indexes:
            _create_index_if_missing(table_name, index_name, columns, unique=unique)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    for table_name in (
        "legal_jurisprudencias",
        "legal_tarifas",
        "legal_reglas",
        "legal_clausulas",
        "legal_norma_relaciones",
        "legal_normas",
    ):
        inspector = sa.inspect(bind)
        if _table_exists(inspector, table_name):
            op.drop_table(table_name)
