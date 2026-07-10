"""add notarial document intelligence platform tables

Revision ID: 20260710_add_notarial_document_intelligence
Revises: 20260710_add_inverse_conversion_engine
Create Date: 2026-07-10 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "20260710_add_notarial_document_intelligence"
down_revision = "20260710_add_inverse_conversion_engine"
branch_labels = None
depends_on = None


def _table_exists(inspector: sa.Inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _index_exists(inspector: sa.Inspector, table_name: str, index_name: str) -> bool:
    return any(index["name"] == index_name for index in inspector.get_indexes(table_name))


def _timestamps(include_updated: bool = True) -> list[sa.Column]:
    columns = [sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP"))]
    if include_updated:
        columns.append(sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")))
    return columns


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not _table_exists(inspector, "notarial_document_batches"):
        op.create_table(
            "notarial_document_batches",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
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
            sa.UniqueConstraint("batch_key", name="uq_notarial_document_batches_batch_key"),
        )
        inspector = sa.inspect(bind)

    if not _table_exists(inspector, "notarial_document_families"):
        op.create_table(
            "notarial_document_families",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
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
            sa.UniqueConstraint("family_key", name="uq_notarial_document_families_family_key"),
        )
        inspector = sa.inspect(bind)

    if not _table_exists(inspector, "notarial_documents"):
        op.create_table(
            "notarial_documents",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
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
            sa.UniqueConstraint("content_hash", name="uq_notarial_documents_content_hash"),
        )
        inspector = sa.inspect(bind)

    if not _table_exists(inspector, "notarial_document_batch_items"):
        op.create_table(
            "notarial_document_batch_items",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("batch_id", sa.Integer(), sa.ForeignKey("notarial_document_batches.id", ondelete="CASCADE"), nullable=False),
            sa.Column("document_id", sa.Integer(), sa.ForeignKey("notarial_documents.id", ondelete="CASCADE"), nullable=False),
            sa.Column("item_index", sa.Integer(), nullable=False),
            sa.Column("original_filename", sa.String(length=260), nullable=False),
            sa.Column("content_hash", sa.String(length=64), nullable=False),
            sa.Column("status", sa.String(length=40), nullable=False, server_default=sa.text("'processed'")),
            sa.Column("metadata_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            *_timestamps(include_updated=False),
            sa.UniqueConstraint("batch_id", "item_index", name="uq_notarial_document_batch_items_batch_index"),
        )
        inspector = sa.inspect(bind)

    if not _table_exists(inspector, "notarial_document_sections"):
        op.create_table(
            "notarial_document_sections",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("document_id", sa.Integer(), sa.ForeignKey("notarial_documents.id", ondelete="CASCADE"), nullable=False),
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
            sa.Column("document_id", sa.Integer(), sa.ForeignKey("notarial_documents.id", ondelete="CASCADE"), nullable=False),
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
            sa.Column("metadata_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            *_timestamps(),
        )
        inspector = sa.inspect(bind)

    if not _table_exists(inspector, "notarial_document_entities"):
        op.create_table(
            "notarial_document_entities",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("document_id", sa.Integer(), sa.ForeignKey("notarial_documents.id", ondelete="CASCADE"), nullable=False),
            sa.Column("block_id", sa.Integer(), sa.ForeignKey("notarial_document_blocks.id", ondelete="CASCADE"), nullable=True),
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
            sa.Column("cluster_key", sa.String(length=160), nullable=False),
            sa.Column("label", sa.String(length=240), nullable=False),
            sa.Column("cluster_type", sa.String(length=80), nullable=False, server_default=sa.text("'document'")),
            sa.Column("status", sa.String(length=40), nullable=False, server_default=sa.text("'suggested'")),
            sa.Column("algorithm", sa.String(length=120), nullable=True),
            sa.Column("metadata_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            *_timestamps(),
            sa.UniqueConstraint("cluster_key", name="uq_notarial_document_clusters_cluster_key"),
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
            sa.UniqueConstraint("version_key", name="uq_notarial_embedding_versions_version_key"),
        )
        inspector = sa.inspect(bind)

    if not _table_exists(inspector, "notarial_document_embeddings"):
        op.create_table(
            "notarial_document_embeddings",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("embedding_version_id", sa.Integer(), sa.ForeignKey("notarial_embedding_versions.id", ondelete="CASCADE"), nullable=False),
            sa.Column("document_id", sa.Integer(), sa.ForeignKey("notarial_documents.id", ondelete="CASCADE"), nullable=True),
            sa.Column("source_type", sa.String(length=80), nullable=False),
            sa.Column("source_id", sa.Integer(), nullable=False),
            sa.Column("content_hash", sa.String(length=64), nullable=False),
            sa.Column("embedding", sa.Text(), nullable=True),
            sa.Column("metadata_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            *_timestamps(),
            sa.UniqueConstraint("embedding_version_id", "source_type", "source_id", name="uq_notarial_embeddings_version_source"),
        )
        inspector = sa.inspect(bind)

    if not _table_exists(inspector, "notarial_document_evidences"):
        op.create_table(
            "notarial_document_evidences",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("document_id", sa.Integer(), sa.ForeignKey("notarial_documents.id", ondelete="CASCADE"), nullable=True),
            sa.Column("block_id", sa.Integer(), sa.ForeignKey("notarial_document_blocks.id", ondelete="CASCADE"), nullable=True),
            sa.Column("entity_id", sa.Integer(), sa.ForeignKey("notarial_document_entities.id", ondelete="CASCADE"), nullable=True),
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
            sa.Column("document_id", sa.Integer(), sa.ForeignKey("notarial_documents.id", ondelete="CASCADE"), nullable=True),
            sa.Column("block_id", sa.Integer(), sa.ForeignKey("notarial_document_blocks.id", ondelete="CASCADE"), nullable=True),
            sa.Column("entity_id", sa.Integer(), sa.ForeignKey("notarial_document_entities.id", ondelete="CASCADE"), nullable=True),
            sa.Column("decision_type", sa.String(length=120), nullable=False),
            sa.Column("deterministic_decision_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            sa.Column("llm_decision_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            sa.Column("hybrid_decision_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            sa.Column("human_decision_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            sa.Column("status", sa.String(length=40), nullable=False, server_default=sa.text("'pending'")),
            sa.Column("decided_by_user_id", sa.Integer(), nullable=True),
            sa.Column("metadata_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            *_timestamps(),
        )

    indexes = [
        ("notarial_document_batches", "ix_notarial_document_batches_batch_key", ["batch_key"], True),
        ("notarial_document_batches", "ix_notarial_document_batches_status", ["status"], False),
        ("notarial_documents", "ix_notarial_documents_content_hash", ["content_hash"], True),
        ("notarial_documents", "ix_notarial_documents_filename", ["filename"], False),
        ("notarial_documents", "ix_notarial_documents_processing_status", ["processing_status"], False),
        ("notarial_documents", "ix_notarial_documents_document_type", ["document_type"], False),
        ("notarial_documents", "ix_notarial_documents_family_id", ["family_id"], False),
        ("notarial_document_batch_items", "ix_notarial_document_batch_items_batch_id", ["batch_id"], False),
        ("notarial_document_batch_items", "ix_notarial_document_batch_items_document_id", ["document_id"], False),
        ("notarial_document_batch_items", "ix_notarial_document_batch_items_content_hash", ["content_hash"], False),
        ("notarial_document_sections", "ix_notarial_document_sections_document_id", ["document_id"], False),
        ("notarial_document_blocks", "ix_notarial_document_blocks_document_id", ["document_id"], False),
        ("notarial_document_blocks", "ix_notarial_document_blocks_location_key", ["location_key"], False),
        ("notarial_document_entities", "ix_notarial_document_entities_document_id", ["document_id"], False),
        ("notarial_document_entities", "ix_notarial_document_entities_canonical_field_code", ["canonical_field_code"], False),
        ("notarial_document_families", "ix_notarial_document_families_family_key", ["family_key"], True),
        ("notarial_document_clusters", "ix_notarial_document_clusters_cluster_key", ["cluster_key"], True),
        ("notarial_embedding_versions", "ix_notarial_embedding_versions_version_key", ["version_key"], True),
        ("notarial_document_embeddings", "ix_notarial_document_embeddings_version_source", ["embedding_version_id", "source_type", "source_id"], True),
        ("notarial_document_evidences", "ix_notarial_document_evidences_evidence_type", ["evidence_type"], False),
        ("notarial_document_decisions", "ix_notarial_document_decisions_status", ["status"], False),
    ]
    for table_name, index_name, columns, unique in indexes:
        inspector = sa.inspect(bind)
        if _table_exists(inspector, table_name) and not _index_exists(inspector, table_name, index_name):
            op.create_index(index_name, table_name, columns, unique=unique)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
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
        "notarial_document_batch_items",
        "notarial_documents",
        "notarial_document_families",
        "notarial_document_batches",
    ):
        inspector = sa.inspect(bind)
        if _table_exists(inspector, table_name):
            op.drop_table(table_name)
