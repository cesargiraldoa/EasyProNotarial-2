"""add legal corpus embeddings

Revision ID: 20260721_add_legal_embeddings
Revises: 20260721_add_legal_corpus_tables
Create Date: 2026-07-21
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.types import UserDefinedType


revision = "20260721_add_legal_embeddings"
down_revision = "20260721_add_legal_corpus_tables"
branch_labels = None
depends_on = None

EMBEDDING_DIMENSIONS = 384


class VectorType(UserDefinedType):
    def __init__(self, dimensions: int = EMBEDDING_DIMENSIONS) -> None:
        self.dimensions = dimensions

    def get_col_spec(self, **kw) -> str:
        return f"vector({self.dimensions})"


def _table_exists(inspector: sa.Inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _index_exists(inspector: sa.Inspector, table_name: str, index_name: str) -> bool:
    return any(index["name"] == index_name for index in inspector.get_indexes(table_name))


def _ensure_vector_extension(bind) -> bool:
    if bind.dialect.name != "postgresql":
        return False
    # Si ya esta instalada, usarla directamente.
    already = bind.execute(
        sa.text("select exists (select 1 from pg_extension where extname = 'vector')")
    ).scalar()
    if already:
        return True
    # Solo intenta crear la extension si su binario esta disponible en el
    # servidor. Asi la migracion no aborta cuando pgvector no esta instalado.
    available = bind.execute(
        sa.text("select exists (select 1 from pg_available_extensions where name = 'vector')")
    ).scalar()
    if not available:
        return False
    # Crear dentro de un SAVEPOINT: si el rol no es superusuario (dev local),
    # el CREATE EXTENSION falla por privilegios; hacemos rollback solo de ese
    # savepoint para no envenenar la transaccion y degradamos a embeddings Text.
    try:
        with bind.begin_nested():
            bind.execute(sa.text("CREATE EXTENSION IF NOT EXISTS vector"))
    except Exception:
        return False
    return bool(bind.execute(sa.text("select exists (select 1 from pg_extension where extname = 'vector')")).scalar())


def _embedding_type(bind, vector_enabled: bool) -> sa.types.TypeEngine:
    if bind.dialect.name == "postgresql" and vector_enabled:
        return VectorType(EMBEDDING_DIMENSIONS)
    return sa.Text()


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    ]


def _create_index_if_missing(
    table_name: str,
    index_name: str,
    columns: list[str],
    unique: bool = False,
    postgresql_using: str | None = None,
    postgresql_ops: dict[str, str] | None = None,
) -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if _table_exists(inspector, table_name) and not _index_exists(inspector, table_name, index_name):
        kwargs = {"unique": unique}
        if postgresql_using and bind.dialect.name == "postgresql":
            kwargs["postgresql_using"] = postgresql_using
        if postgresql_ops and bind.dialect.name == "postgresql":
            kwargs["postgresql_ops"] = postgresql_ops
        op.create_index(index_name, table_name, columns, **kwargs)


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    vector_enabled = _ensure_vector_extension(bind)

    if not _table_exists(inspector, "legal_embeddings"):
        op.create_table(
            "legal_embeddings",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("source_type", sa.String(length=40), nullable=False),
            sa.Column("source_id", sa.Integer(), nullable=False),
            sa.Column("chunk_text", sa.Text(), nullable=False),
            sa.Column("embedding", _embedding_type(bind, vector_enabled), nullable=True),
            sa.Column("vigencia_desde", sa.Date(), nullable=True),
            sa.Column("vigencia_hasta", sa.Date(), nullable=True),
            sa.Column("acto_code", sa.String(length=80), nullable=True),
            *_timestamps(),
            sa.CheckConstraint("source_type in ('norma', 'clausula')", name="ck_legal_embeddings_source_type"),
            sa.UniqueConstraint("source_type", "source_id", name="uq_legal_embeddings_source"),
        )

    indexes = [
        ("ix_legal_embeddings_id", ["id"], False, None, None),
        ("ix_legal_embeddings_source_type", ["source_type"], False, None, None),
        ("ix_legal_embeddings_source_id", ["source_id"], False, None, None),
        ("ix_legal_embeddings_source", ["source_type", "source_id"], True, None, None),
        ("ix_legal_embeddings_vigencia_desde", ["vigencia_desde"], False, None, None),
        ("ix_legal_embeddings_vigencia_hasta", ["vigencia_hasta"], False, None, None),
        ("ix_legal_embeddings_acto_code", ["acto_code"], False, None, None),
    ]
    if vector_enabled:
        # El indice HNSW solo aplica sobre una columna vector real (pgvector).
        indexes.append(("ix_legal_embeddings_embedding_hnsw", ["embedding"], False, "hnsw", {"embedding": "vector_cosine_ops"}))
    for index_name, columns, unique, using, ops in indexes:
        _create_index_if_missing("legal_embeddings", index_name, columns, unique=unique, postgresql_using=using, postgresql_ops=ops)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if _table_exists(inspector, "legal_embeddings"):
        op.drop_table("legal_embeddings")
