"""add notarial document intelligence platform tables

Revision ID: 20260710_add_notarial_document_intelligence
Revises: 20260710_add_inverse_conversion_engine
Create Date: 2026-07-10 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.types import UserDefinedType


revision = "20260710_add_notarial_document_intelligence"
down_revision = "20260710_add_inverse_conversion_engine"
branch_labels = None
depends_on = None


class VectorType(UserDefinedType):
    def __init__(self, dimensions: int = 384) -> None:
        self.dimensions = dimensions

    def get_col_spec(self, **kw) -> str:
        return f"vector({self.dimensions})"


BATCH_STATUSES = ("initialized", "queued", "running", "completed", "partial_error", "error", "publication_failed")
DOCUMENT_STATUSES = ("stored", "parsed", "reused", "error", "unsupported")
PARSE_RUN_STATUSES = ("queued", "running", "completed", "error")
PUBLICATION_STATUSES = ("pending", "publishing", "published", "publication_failed")
REVIEW_STATUSES = ("pending", "accepted", "rejected", "blocked")
EMBEDDING_DIMENSIONS = 384
NOTARIAL_INTELLIGENCE_MODULE = "notarial_intelligence"
NOTARIAL_INTELLIGENCE_ROLE_ACCESS = {
    "super_admin": True,
    "admin_notary": True,
    "notary": True,
    "notary_titular": True,
    "notary_suplente": True,
    "approver": True,
    "protocolist": True,
    "client": False,
}


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


def _ensure_vector_extension(bind) -> bool:
    if bind.dialect.name != "postgresql":
        return False
    exists = bind.execute(sa.text("select exists (select 1 from pg_extension where extname = 'vector')")).scalar()
    if exists:
        return True
    with op.get_context().autocommit_block():
        op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    return bool(bind.execute(sa.text("select exists (select 1 from pg_extension where extname = 'vector')")).scalar())


def _embedding_type(bind, vector_enabled: bool) -> sa.types.TypeEngine:
    if bind.dialect.name == "postgresql" and vector_enabled:
        return VectorType(EMBEDDING_DIMENSIONS)
    return sa.Text()


def _seed_notarial_intelligence_permissions(bind, inspector: sa.Inspector) -> None:
    if not _table_exists(inspector, "roles") or not _table_exists(inspector, "role_permissions"):
        return

    roles = sa.table(
        "roles",
        sa.column("id", sa.Integer),
        sa.column("code", sa.String),
    )
    role_permissions = sa.table(
        "role_permissions",
        sa.column("id", sa.Integer),
        sa.column("role_id", sa.Integer),
        sa.column("module_code", sa.String),
        sa.column("can_access", sa.Boolean),
    )
    role_rows = bind.execute(sa.select(roles.c.id, roles.c.code)).all()
    role_ids_by_code = {row.code: row.id for row in role_rows}
    for role_code, can_access in NOTARIAL_INTELLIGENCE_ROLE_ACCESS.items():
        role_id = role_ids_by_code.get(role_code)
        if role_id is None:
            continue
        existing = bind.execute(
            sa.select(role_permissions.c.id).where(
                role_permissions.c.role_id == role_id,
                role_permissions.c.module_code == NOTARIAL_INTELLIGENCE_MODULE,
            )
        ).first()
        if existing is None:
            bind.execute(
                sa.insert(role_permissions).values(
                    role_id=role_id,
                    module_code=NOTARIAL_INTELLIGENCE_MODULE,
                    can_access=can_access,
                )
            )
        else:
            bind.execute(sa.update(role_permissions).where(role_permissions.c.id == existing.id).values(can_access=can_access))


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

    if not _table_exists(inspector, "notarial_document_batches"):
        op.create_table(
            "notarial_document_batches",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("notary_id", sa.Integer(), sa.ForeignKey("notaries.id", ondelete="CASCADE"), nullable=False),
            sa.Column("batch_key", sa.String(length=120), nullable=False),
            sa.Column("name", sa.String(length=240), nullable=False),
            sa.Column("source_type", sa.String(length=80), nullable=False, server_default=sa.text("'manual'")),
            sa.Column("status", sa.String(length=40), nullable=False, server_default=sa.text("'initialized'")),
            sa.Column("total_documents", sa.Integer(), nullable=False, server_default=sa.text("0")),
            sa.Column("unique_documents", sa.Integer(), nullable=False, server_default=sa.text("0")),
            sa.Column("duplicate_documents", sa.Integer(), nullable=False, server_default=sa.text("0")),
            sa.Column("error_documents", sa.Integer(), nullable=False, server_default=sa.text("0")),
            sa.Column("metadata_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("error_message", sa.Text(), nullable=True),
            *_timestamps(),
            sa.CheckConstraint(f"status IN ({_quoted(BATCH_STATUSES)})", name="ck_notarial_document_batches_status"),
            sa.UniqueConstraint("batch_key", name="uq_notarial_document_batches_batch_key"),
        )
        inspector = sa.inspect(bind)

    if not _table_exists(inspector, "notarial_document_families"):
        op.create_table(
            "notarial_document_families",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("notary_id", sa.Integer(), sa.ForeignKey("notaries.id", ondelete="CASCADE"), nullable=False),
            sa.Column("family_key", sa.String(length=160), nullable=False),
            sa.Column("label", sa.String(length=240), nullable=False),
            sa.Column("document_type", sa.String(length=160), nullable=True),
            sa.Column("notary_name", sa.String(length=240), nullable=True),
            sa.Column("project_name", sa.String(length=240), nullable=True),
            sa.Column("bank_name", sa.String(length=240), nullable=True),
            sa.Column("status", sa.String(length=40), nullable=False, server_default=sa.text("'suggested'")),
            sa.Column("confidence", sa.Float(), nullable=False, server_default=sa.text("0")),
            sa.Column("metadata_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            *_timestamps(),
            sa.UniqueConstraint("notary_id", "family_key", name="uq_notarial_document_families_notary_key"),
        )
        inspector = sa.inspect(bind)

    if not _table_exists(inspector, "notarial_documents"):
        op.create_table(
            "notarial_documents",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("notary_id", sa.Integer(), sa.ForeignKey("notaries.id", ondelete="CASCADE"), nullable=False),
            sa.Column("content_hash", sa.String(length=64), nullable=False),
            sa.Column("filename", sa.String(length=260), nullable=False),
            sa.Column("storage_path", sa.String(length=1000), nullable=False),
            sa.Column("storage_backend", sa.String(length=40), nullable=False, server_default=sa.text("'local'")),
            sa.Column("content_type", sa.String(length=160), nullable=False),
            sa.Column("file_size_bytes", sa.Integer(), nullable=False, server_default=sa.text("0")),
            sa.Column("parser_name", sa.String(length=80), nullable=True),
            sa.Column("parser_version", sa.String(length=80), nullable=True),
            sa.Column("processing_status", sa.String(length=40), nullable=False, server_default=sa.text("'stored'")),
            sa.Column("document_type", sa.String(length=160), nullable=True),
            sa.Column("document_subtype", sa.String(length=160), nullable=True),
            sa.Column("notary_name", sa.String(length=240), nullable=True),
            sa.Column("project_name", sa.String(length=240), nullable=True),
            sa.Column("bank_name", sa.String(length=240), nullable=True),
            sa.Column("family_id", sa.Integer(), sa.ForeignKey("notarial_document_families.id", ondelete="SET NULL"), nullable=True),
            sa.Column("metadata_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            sa.Column("error_message", sa.Text(), nullable=True),
            *_timestamps(),
            sa.CheckConstraint(f"processing_status IN ({_quoted(DOCUMENT_STATUSES)})", name="ck_notarial_documents_processing_status"),
            sa.UniqueConstraint("notary_id", "content_hash", name="uq_notarial_documents_notary_hash"),
        )
        inspector = sa.inspect(bind)

    if not _table_exists(inspector, "notarial_document_batch_items"):
        op.create_table(
            "notarial_document_batch_items",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("batch_id", sa.Integer(), sa.ForeignKey("notarial_document_batches.id", ondelete="CASCADE"), nullable=False),
            sa.Column("document_id", sa.Integer(), sa.ForeignKey("notarial_documents.id", ondelete="CASCADE"), nullable=False),
            sa.Column("notary_id", sa.Integer(), sa.ForeignKey("notaries.id", ondelete="CASCADE"), nullable=False),
            sa.Column("item_index", sa.Integer(), nullable=False),
            sa.Column("original_filename", sa.String(length=260), nullable=False),
            sa.Column("content_hash", sa.String(length=64), nullable=False),
            sa.Column("status", sa.String(length=40), nullable=False, server_default=sa.text("'processed'")),
            sa.Column("metadata_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            *_timestamps(include_updated=False),
            sa.UniqueConstraint("batch_id", "item_index", name="uq_notarial_document_batch_items_batch_index"),
        )
        inspector = sa.inspect(bind)

    if not _table_exists(inspector, "notarial_document_parse_runs"):
        op.create_table(
            "notarial_document_parse_runs",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("notary_id", sa.Integer(), sa.ForeignKey("notaries.id", ondelete="CASCADE"), nullable=False),
            sa.Column("document_id", sa.Integer(), sa.ForeignKey("notarial_documents.id", ondelete="CASCADE"), nullable=False),
            sa.Column("parse_version", sa.Integer(), nullable=False),
            sa.Column("parser_name", sa.String(length=120), nullable=False),
            sa.Column("parser_version", sa.String(length=160), nullable=False),
            sa.Column("status", sa.String(length=40), nullable=False, server_default=sa.text("'running'")),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("warnings_json", sa.Text(), nullable=False, server_default=sa.text("'[]'")),
            sa.Column("error_message", sa.Text(), nullable=True),
            sa.Column("metadata_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            *_timestamps(),
            sa.CheckConstraint(f"status IN ({_quoted(PARSE_RUN_STATUSES)})", name="ck_notarial_parse_runs_status"),
            sa.UniqueConstraint("document_id", "parse_version", name="uq_notarial_parse_runs_document_version"),
        )
        inspector = sa.inspect(bind)

    if not _table_exists(inspector, "notarial_task_publications"):
        op.create_table(
            "notarial_task_publications",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("request_key", sa.String(length=180), nullable=False),
            sa.Column("notary_id", sa.Integer(), sa.ForeignKey("notaries.id", ondelete="CASCADE"), nullable=False),
            sa.Column("target_type", sa.String(length=40), nullable=False),
            sa.Column("target_id", sa.Integer(), nullable=False),
            sa.Column("document_id", sa.Integer(), sa.ForeignKey("notarial_documents.id", ondelete="CASCADE"), nullable=True),
            sa.Column("parse_run_id", sa.Integer(), sa.ForeignKey("notarial_document_parse_runs.id", ondelete="CASCADE"), nullable=True),
            sa.Column("task_name", sa.String(length=180), nullable=False),
            sa.Column("task_args_json", sa.Text(), nullable=False, server_default=sa.text("'[]'")),
            sa.Column("status", sa.String(length=40), nullable=False, server_default=sa.text("'pending'")),
            sa.Column("attempts", sa.Integer(), nullable=False, server_default=sa.text("0")),
            sa.Column("last_error", sa.Text(), nullable=True),
            sa.Column("task_id", sa.String(length=180), nullable=True),
            sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("metadata_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            *_timestamps(),
            sa.CheckConstraint(f"status IN ({_quoted(PUBLICATION_STATUSES)})", name="ck_notarial_task_publications_status"),
            sa.UniqueConstraint("request_key", name="uq_notarial_task_publications_request_key"),
        )
        inspector = sa.inspect(bind)

    if not _table_exists(inspector, "notarial_document_sections"):
        op.create_table(
            "notarial_document_sections",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("notary_id", sa.Integer(), sa.ForeignKey("notaries.id", ondelete="CASCADE"), nullable=False),
            sa.Column("document_id", sa.Integer(), sa.ForeignKey("notarial_documents.id", ondelete="CASCADE"), nullable=False),
            sa.Column("parse_run_id", sa.Integer(), sa.ForeignKey("notarial_document_parse_runs.id", ondelete="CASCADE"), nullable=False),
            sa.Column("section_key", sa.String(length=120), nullable=False),
            sa.Column("title", sa.String(length=500), nullable=True),
            sa.Column("order_index", sa.Integer(), nullable=False, server_default=sa.text("0")),
            sa.Column("start_block_index", sa.Integer(), nullable=True),
            sa.Column("end_block_index", sa.Integer(), nullable=True),
            sa.Column("classification_status", sa.String(length=40), nullable=False, server_default=sa.text("'unknown'")),
            sa.Column("metadata_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            *_timestamps(),
        )
        inspector = sa.inspect(bind)

    if not _table_exists(inspector, "notarial_document_blocks"):
        op.create_table(
            "notarial_document_blocks",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("notary_id", sa.Integer(), sa.ForeignKey("notaries.id", ondelete="CASCADE"), nullable=False),
            sa.Column("document_id", sa.Integer(), sa.ForeignKey("notarial_documents.id", ondelete="CASCADE"), nullable=False),
            sa.Column("parse_run_id", sa.Integer(), sa.ForeignKey("notarial_document_parse_runs.id", ondelete="CASCADE"), nullable=False),
            sa.Column("section_id", sa.Integer(), sa.ForeignKey("notarial_document_sections.id", ondelete="SET NULL"), nullable=True),
            sa.Column("block_index", sa.Integer(), nullable=False),
            sa.Column("block_type", sa.String(length=80), nullable=False),
            sa.Column("location_key", sa.String(length=260), nullable=False),
            sa.Column("text", sa.Text(), nullable=False),
            sa.Column("text_hash", sa.String(length=64), nullable=False),
            sa.Column("char_start", sa.Integer(), nullable=True),
            sa.Column("char_end", sa.Integer(), nullable=True),
            sa.Column("table_index", sa.Integer(), nullable=True),
            sa.Column("row_index", sa.Integer(), nullable=True),
            sa.Column("cell_index", sa.Integer(), nullable=True),
            sa.Column("paragraph_index", sa.Integer(), nullable=True),
            sa.Column("fixed_variable_label", sa.String(length=40), nullable=False, server_default=sa.text("'unknown'")),
            sa.Column("semantic_type", sa.String(length=80), nullable=True),
            sa.Column("semantic_title", sa.String(length=500), nullable=True),
            sa.Column("semantic_section", sa.String(length=160), nullable=True),
            sa.Column("parser_source", sa.String(length=80), nullable=False, server_default=sa.text("'python-docx'")),
            sa.Column("unstructured_category", sa.String(length=120), nullable=True),
            sa.Column("metadata_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            *_timestamps(),
        )
        inspector = sa.inspect(bind)

    if not _table_exists(inspector, "notarial_document_entities"):
        op.create_table(
            "notarial_document_entities",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("notary_id", sa.Integer(), sa.ForeignKey("notaries.id", ondelete="CASCADE"), nullable=False),
            sa.Column("document_id", sa.Integer(), sa.ForeignKey("notarial_documents.id", ondelete="CASCADE"), nullable=False),
            sa.Column("parse_run_id", sa.Integer(), sa.ForeignKey("notarial_document_parse_runs.id", ondelete="SET NULL"), nullable=True),
            sa.Column("block_id", sa.Integer(), sa.ForeignKey("notarial_document_blocks.id", ondelete="SET NULL"), nullable=True),
            sa.Column("entity_type", sa.String(length=120), nullable=False),
            sa.Column("canonical_field_code", sa.String(length=200), nullable=True),
            sa.Column("text", sa.Text(), nullable=False),
            sa.Column("normalized_text", sa.Text(), nullable=True),
            sa.Column("role", sa.String(length=120), nullable=True),
            sa.Column("confidence", sa.Float(), nullable=False, server_default=sa.text("0")),
            sa.Column("source", sa.String(length=80), nullable=False, server_default=sa.text("'deterministic'")),
            sa.Column("requires_human_review", sa.Boolean(), nullable=False, server_default=sa.text("true")),
            sa.Column("metadata_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            *_timestamps(),
        )
        inspector = sa.inspect(bind)

    if not _table_exists(inspector, "notarial_document_family_members"):
        op.create_table(
            "notarial_document_family_members",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("family_id", sa.Integer(), sa.ForeignKey("notarial_document_families.id", ondelete="CASCADE"), nullable=False),
            sa.Column("document_id", sa.Integer(), sa.ForeignKey("notarial_documents.id", ondelete="CASCADE"), nullable=False),
            sa.Column("confidence", sa.Float(), nullable=False, server_default=sa.text("0")),
            sa.Column("source", sa.String(length=80), nullable=False, server_default=sa.text("'deterministic'")),
            sa.Column("metadata_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            *_timestamps(include_updated=False),
            sa.UniqueConstraint("family_id", "document_id", name="uq_notarial_family_members_family_document"),
        )
        inspector = sa.inspect(bind)

    if not _table_exists(inspector, "notarial_document_clusters"):
        op.create_table(
            "notarial_document_clusters",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("notary_id", sa.Integer(), sa.ForeignKey("notaries.id", ondelete="CASCADE"), nullable=False),
            sa.Column("cluster_key", sa.String(length=160), nullable=False),
            sa.Column("label", sa.String(length=240), nullable=False),
            sa.Column("cluster_type", sa.String(length=80), nullable=False, server_default=sa.text("'document'")),
            sa.Column("status", sa.String(length=40), nullable=False, server_default=sa.text("'suggested'")),
            sa.Column("algorithm", sa.String(length=120), nullable=True),
            sa.Column("metadata_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            *_timestamps(),
            sa.UniqueConstraint("notary_id", "cluster_key", name="uq_notarial_document_clusters_notary_key"),
        )
        inspector = sa.inspect(bind)

    if not _table_exists(inspector, "notarial_document_cluster_members"):
        op.create_table(
            "notarial_document_cluster_members",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("cluster_id", sa.Integer(), sa.ForeignKey("notarial_document_clusters.id", ondelete="CASCADE"), nullable=False),
            sa.Column("document_id", sa.Integer(), sa.ForeignKey("notarial_documents.id", ondelete="CASCADE"), nullable=False),
            sa.Column("similarity_score", sa.Float(), nullable=False, server_default=sa.text("0")),
            sa.Column("metadata_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            *_timestamps(include_updated=False),
            sa.UniqueConstraint("cluster_id", "document_id", name="uq_notarial_cluster_members_cluster_document"),
        )
        inspector = sa.inspect(bind)

    if not _table_exists(inspector, "notarial_embedding_versions"):
        op.create_table(
            "notarial_embedding_versions",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("version_key", sa.String(length=160), nullable=False),
            sa.Column("provider", sa.String(length=120), nullable=False),
            sa.Column("model_name", sa.String(length=240), nullable=False),
            sa.Column("dimensions", sa.Integer(), nullable=False),
            sa.Column("status", sa.String(length=40), nullable=False, server_default=sa.text("'shadow'")),
            sa.Column("metadata_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            *_timestamps(),
            sa.CheckConstraint(f"dimensions = {EMBEDDING_DIMENSIONS}", name="ck_notarial_embedding_versions_dimensions"),
            sa.UniqueConstraint("version_key", name="uq_notarial_embedding_versions_version_key"),
        )
        inspector = sa.inspect(bind)

    if not _table_exists(inspector, "notarial_document_embeddings"):
        op.create_table(
            "notarial_document_embeddings",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("notary_id", sa.Integer(), sa.ForeignKey("notaries.id", ondelete="CASCADE"), nullable=False),
            sa.Column("embedding_version_id", sa.Integer(), sa.ForeignKey("notarial_embedding_versions.id", ondelete="CASCADE"), nullable=False),
            sa.Column("document_id", sa.Integer(), sa.ForeignKey("notarial_documents.id", ondelete="CASCADE"), nullable=True),
            sa.Column("source_type", sa.String(length=80), nullable=False),
            sa.Column("source_id", sa.Integer(), nullable=False),
            sa.Column("content_hash", sa.String(length=64), nullable=False),
            sa.Column("embedding_dimensions", sa.Integer(), nullable=False, server_default=sa.text(str(EMBEDDING_DIMENSIONS))),
            sa.Column("embedding", _embedding_type(bind, vector_enabled), nullable=True),
            sa.Column("metadata_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            *_timestamps(),
            sa.CheckConstraint(f"embedding_dimensions = {EMBEDDING_DIMENSIONS}", name="ck_notarial_document_embeddings_dimensions"),
            sa.UniqueConstraint("embedding_version_id", "source_type", "source_id", name="uq_notarial_embeddings_version_source"),
        )
        inspector = sa.inspect(bind)

    if not _table_exists(inspector, "notarial_document_evidences"):
        op.create_table(
            "notarial_document_evidences",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("notary_id", sa.Integer(), sa.ForeignKey("notaries.id", ondelete="CASCADE"), nullable=False),
            sa.Column("document_id", sa.Integer(), sa.ForeignKey("notarial_documents.id", ondelete="CASCADE"), nullable=True),
            sa.Column("parse_run_id", sa.Integer(), sa.ForeignKey("notarial_document_parse_runs.id", ondelete="SET NULL"), nullable=True),
            sa.Column("block_id", sa.Integer(), sa.ForeignKey("notarial_document_blocks.id", ondelete="SET NULL"), nullable=True),
            sa.Column("entity_id", sa.Integer(), sa.ForeignKey("notarial_document_entities.id", ondelete="SET NULL"), nullable=True),
            sa.Column("evidence_type", sa.String(length=80), nullable=False),
            sa.Column("source", sa.String(length=80), nullable=False, server_default=sa.text("'deterministic'")),
            sa.Column("score", sa.Float(), nullable=False, server_default=sa.text("0")),
            sa.Column("payload_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            *_timestamps(),
        )
        inspector = sa.inspect(bind)

    if not _table_exists(inspector, "notarial_document_decisions"):
        op.create_table(
            "notarial_document_decisions",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("notary_id", sa.Integer(), sa.ForeignKey("notaries.id", ondelete="CASCADE"), nullable=False),
            sa.Column("document_id", sa.Integer(), sa.ForeignKey("notarial_documents.id", ondelete="CASCADE"), nullable=True),
            sa.Column("parse_run_id", sa.Integer(), sa.ForeignKey("notarial_document_parse_runs.id", ondelete="SET NULL"), nullable=True),
            sa.Column("block_id", sa.Integer(), sa.ForeignKey("notarial_document_blocks.id", ondelete="SET NULL"), nullable=True),
            sa.Column("entity_id", sa.Integer(), sa.ForeignKey("notarial_document_entities.id", ondelete="SET NULL"), nullable=True),
            sa.Column("decision_type", sa.String(length=120), nullable=False),
            sa.Column("deterministic_decision_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            sa.Column("llm_decision_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            sa.Column("hybrid_decision_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            sa.Column("human_decision_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            sa.Column("status", sa.String(length=40), nullable=False, server_default=sa.text("'pending'")),
            sa.Column("decided_by_user_id", sa.Integer(), nullable=True),
            sa.Column("metadata_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            *_timestamps(),
            sa.CheckConstraint(f"status IN ({_quoted(REVIEW_STATUSES)})", name="ck_notarial_document_decisions_status"),
        )

    indexes = [
        ("notarial_document_batches", "ix_notarial_document_batches_notary_id", ["notary_id"], False),
        ("notarial_document_batches", "ix_notarial_document_batches_notary_status", ["notary_id", "status"], False),
        ("notarial_documents", "ix_notarial_documents_notary_hash", ["notary_id", "content_hash"], True),
        ("notarial_documents", "ix_notarial_documents_notary_status", ["notary_id", "processing_status"], False),
        ("notarial_documents", "ix_notarial_documents_notary_family", ["notary_id", "family_id"], False),
        ("notarial_documents", "ix_notarial_documents_notary_type", ["notary_id", "document_type"], False),
        ("notarial_documents", "ix_notarial_documents_notary_project", ["notary_id", "project_name"], False),
        ("notarial_documents", "ix_notarial_documents_notary_bank", ["notary_id", "bank_name"], False),
        ("notarial_document_batch_items", "ix_notarial_batch_items_notary_batch", ["notary_id", "batch_id"], False),
        ("notarial_document_batch_items", "ix_notarial_batch_items_notary_document", ["notary_id", "document_id"], False),
        ("notarial_document_parse_runs", "ix_notarial_parse_runs_notary_document", ["notary_id", "document_id"], False),
        ("notarial_document_parse_runs", "ix_notarial_parse_runs_document_active", ["document_id", "is_active"], False),
        ("notarial_task_publications", "ix_notarial_task_publications_notary_status", ["notary_id", "status"], False),
        ("notarial_task_publications", "ix_notarial_task_publications_target", ["target_type", "target_id"], False),
        ("notarial_task_publications", "ix_notarial_task_publications_parse_run", ["parse_run_id"], False),
        ("notarial_document_sections", "ix_notarial_sections_notary_document", ["notary_id", "document_id"], False),
        ("notarial_document_sections", "ix_notarial_sections_parse_run", ["parse_run_id"], False),
        ("notarial_document_blocks", "ix_notarial_blocks_notary_document", ["notary_id", "document_id"], False),
        ("notarial_document_blocks", "ix_notarial_blocks_parse_run", ["parse_run_id"], False),
        ("notarial_document_blocks", "ix_notarial_blocks_location_key", ["location_key"], False),
        ("notarial_document_blocks", "ix_notarial_blocks_semantic_type", ["semantic_type"], False),
        ("notarial_document_entities", "ix_notarial_entities_notary_document", ["notary_id", "document_id"], False),
        ("notarial_document_entities", "ix_notarial_entities_parse_run", ["parse_run_id"], False),
        ("notarial_document_entities", "ix_notarial_entities_notary_field", ["notary_id", "canonical_field_code"], False),
        ("notarial_document_families", "ix_notarial_families_notary_key", ["notary_id", "family_key"], True),
        ("notarial_document_clusters", "ix_notarial_clusters_notary_key", ["notary_id", "cluster_key"], True),
        ("notarial_document_embeddings", "ix_notarial_embeddings_notary_version", ["notary_id", "embedding_version_id"], False),
        ("notarial_document_embeddings", "ix_notarial_embeddings_notary_document", ["notary_id", "document_id"], False),
        ("notarial_document_embeddings", "ix_notarial_embeddings_version_source", ["embedding_version_id", "source_type", "source_id"], True),
        ("notarial_document_evidences", "ix_notarial_evidences_notary_document", ["notary_id", "document_id"], False),
        ("notarial_document_evidences", "ix_notarial_evidences_parse_run", ["parse_run_id"], False),
        ("notarial_document_decisions", "ix_notarial_decisions_notary_status", ["notary_id", "status"], False),
        ("notarial_document_decisions", "ix_notarial_decisions_parse_run", ["parse_run_id"], False),
    ]
    for table_name, index_name, columns, unique in indexes:
        _create_index_if_missing(table_name, index_name, columns, unique=unique)

    if bind.dialect.name == "postgresql" and vector_enabled:
        _create_index_if_missing(
            "notarial_document_embeddings",
            "ix_notarial_embeddings_embedding_hnsw",
            ["embedding"],
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_cosine_ops"},
        )

    _seed_notarial_intelligence_permissions(bind, sa.inspect(bind))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if _table_exists(inspector, "role_permissions"):
        role_permissions = sa.table(
            "role_permissions",
            sa.column("module_code", sa.String),
        )
        bind.execute(sa.delete(role_permissions).where(role_permissions.c.module_code == NOTARIAL_INTELLIGENCE_MODULE))
    for table_name in (
        "notarial_document_decisions",
        "notarial_document_evidences",
        "notarial_document_embeddings",
        "notarial_embedding_versions",
        "notarial_document_cluster_members",
        "notarial_document_clusters",
        "notarial_document_family_members",
        "notarial_document_entities",
        "notarial_document_blocks",
        "notarial_document_sections",
        "notarial_task_publications",
        "notarial_document_parse_runs",
        "notarial_document_batch_items",
        "notarial_documents",
        "notarial_document_families",
        "notarial_document_batches",
    ):
        inspector = sa.inspect(bind)
        if _table_exists(inspector, table_name):
            op.drop_table(table_name)
