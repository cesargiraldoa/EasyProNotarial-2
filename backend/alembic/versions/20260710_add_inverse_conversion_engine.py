"""add inverse conversion production engine tables

Revision ID: 20260710_add_inverse_conversion_engine
Revises: 20260709_add_inverse_conversion_catalog
Create Date: 2026-07-10 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.types import UserDefinedType


revision = "20260710_add_inverse_conversion_engine"
down_revision = "20260709_add_inverse_conversion_catalog"
branch_labels = None
depends_on = None


class VectorType(UserDefinedType):
    def get_col_spec(self, **kw) -> str:
        return "vector"


SOURCE_TYPES = ("field_pattern", "corpus_document_field", "field_definition", "field_alias", "document_chunk")
RUN_STATUSES = ("initialized", "running", "completed", "error")
CANDIDATE_STATUSES = ("accepted_suggested", "needs_human_review", "blocked", "conflict")


def _table_exists(inspector: sa.Inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _index_exists(inspector: sa.Inspector, table_name: str, index_name: str) -> bool:
    return any(index["name"] == index_name for index in inspector.get_indexes(table_name))


def _quoted(values: tuple[str, ...]) -> str:
    return ", ".join(f"'{value}'" for value in values)


def _timestamps(include_updated: bool = True) -> list[sa.Column]:
    columns = [sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP"))]
    if include_updated:
        columns.append(sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")))
    return columns


def _embedding_type(bind, vector_enabled: bool) -> sa.types.TypeEngine:
    if bind.dialect.name == "postgresql" and vector_enabled:
        return VectorType()
    return sa.Text()


def _ensure_vector_extension(bind) -> bool:
    if bind.dialect.name != "postgresql":
        return False
    exists = bind.execute(sa.text("select exists (select 1 from pg_extension where extname = 'vector')")).scalar()
    if exists:
        return True
    try:
        with op.get_context().autocommit_block():
            op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    except Exception:
        return bool(bind.execute(sa.text("select exists (select 1 from pg_extension where extname = 'vector')")).scalar())
    return bool(bind.execute(sa.text("select exists (select 1 from pg_extension where extname = 'vector')")).scalar())


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    vector_enabled = _ensure_vector_extension(bind)

    if not _table_exists(inspector, "inverse_conversion_embeddings"):
        op.create_table(
            "inverse_conversion_embeddings",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("source_type", sa.String(length=80), nullable=False),
            sa.Column("source_id", sa.Integer(), nullable=False),
            sa.Column("field_code", sa.String(length=200), nullable=True),
            sa.Column("canonical_field_code", sa.String(length=200), nullable=True),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column("content_hash", sa.String(length=64), nullable=False),
            sa.Column("embedding", _embedding_type(bind, vector_enabled), nullable=True),
            sa.Column("metadata_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            *_timestamps(),
            sa.CheckConstraint(f"source_type IN ({_quoted(SOURCE_TYPES)})", name="ck_inverse_conversion_embeddings_source_type"),
            sa.UniqueConstraint("content_hash", name="uq_inverse_conversion_embeddings_content_hash"),
        )
        inspector = sa.inspect(bind)

    if not _table_exists(inspector, "inverse_conversion_runs"):
        op.create_table(
            "inverse_conversion_runs",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("input_type", sa.String(length=80), nullable=False),
            sa.Column("input_hash", sa.String(length=64), nullable=False),
            sa.Column("status", sa.String(length=40), nullable=False, server_default=sa.text("'initialized'")),
            sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("error_message", sa.Text(), nullable=True),
            sa.Column("metadata_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            sa.CheckConstraint(f"status IN ({_quoted(RUN_STATUSES)})", name="ck_inverse_conversion_runs_status"),
        )
        inspector = sa.inspect(bind)

    if not _table_exists(inspector, "inverse_conversion_run_steps"):
        op.create_table(
            "inverse_conversion_run_steps",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("run_id", sa.Integer(), sa.ForeignKey("inverse_conversion_runs.id", ondelete="CASCADE"), nullable=False),
            sa.Column("step_name", sa.String(length=120), nullable=False),
            sa.Column("status", sa.String(length=40), nullable=False),
            sa.Column("input_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            sa.Column("output_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            sa.Column("warnings_json", sa.Text(), nullable=False, server_default=sa.text("'[]'")),
            *_timestamps(include_updated=False),
        )
        inspector = sa.inspect(bind)

    if not _table_exists(inspector, "inverse_conversion_candidates"):
        op.create_table(
            "inverse_conversion_candidates",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("run_id", sa.Integer(), sa.ForeignKey("inverse_conversion_runs.id", ondelete="CASCADE"), nullable=False),
            sa.Column("raw_marker", sa.String(length=200), nullable=True),
            sa.Column("context_before", sa.Text(), nullable=True),
            sa.Column("context_after", sa.Text(), nullable=True),
            sa.Column("candidate_field_code", sa.String(length=200), nullable=False),
            sa.Column("canonical_field_code", sa.String(length=200), nullable=False),
            sa.Column("confidence_score", sa.Float(), nullable=False, server_default=sa.text("0")),
            sa.Column("status", sa.String(length=40), nullable=False),
            sa.Column("evidence_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            sa.Column("warnings_json", sa.Text(), nullable=False, server_default=sa.text("'[]'")),
            sa.Column("requires_human_review", sa.Boolean(), nullable=False, server_default=sa.text("true")),
            *_timestamps(include_updated=False),
            sa.CheckConstraint(f"status IN ({_quoted(CANDIDATE_STATUSES)})", name="ck_inverse_conversion_candidates_status"),
        )

    indexes = [
        ("inverse_conversion_embeddings", "ix_inverse_conversion_embeddings_source", ["source_type", "source_id"], False),
        ("inverse_conversion_embeddings", "ix_inverse_conversion_embeddings_field_code", ["field_code"], False),
        ("inverse_conversion_embeddings", "ix_inverse_conversion_embeddings_canonical_field_code", ["canonical_field_code"], False),
        ("inverse_conversion_embeddings", "ix_inverse_conversion_embeddings_content_hash", ["content_hash"], True),
        ("inverse_conversion_runs", "ix_inverse_conversion_runs_input_hash", ["input_hash"], False),
        ("inverse_conversion_run_steps", "ix_inverse_conversion_run_steps_run_id", ["run_id"], False),
        ("inverse_conversion_candidates", "ix_inverse_conversion_candidates_run_id", ["run_id"], False),
        ("inverse_conversion_candidates", "ix_inverse_conversion_candidates_canonical_field_code", ["canonical_field_code"], False),
    ]
    for table_name, index_name, columns, unique in indexes:
        inspector = sa.inspect(bind)
        if _table_exists(inspector, table_name) and not _index_exists(inspector, table_name, index_name):
            op.create_index(index_name, table_name, columns, unique=unique)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    for table_name in (
        "inverse_conversion_candidates",
        "inverse_conversion_run_steps",
        "inverse_conversion_runs",
        "inverse_conversion_embeddings",
    ):
        inspector = sa.inspect(bind)
        if _table_exists(inspector, table_name):
            op.drop_table(table_name)
