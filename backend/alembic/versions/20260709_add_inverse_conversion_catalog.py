"""add inverse conversion catalog tables

Revision ID: 20260709_add_inverse_conversion_catalog
Revises: 20260513_promote_legacy_notary_to_titular
Create Date: 2026-07-09 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "20260709_add_inverse_conversion_catalog"
down_revision = "20260513_promote_legacy_notary_to_titular"
branch_labels = None
depends_on = None

STATUSES = ("draft", "suggested", "approved", "deprecated", "conflict", "error")


def _table_exists(inspector: sa.Inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _index_exists(inspector: sa.Inspector, table_name: str, index_name: str) -> bool:
    return any(index["name"] == index_name for index in inspector.get_indexes(table_name))


def _status_check(name: str = "status") -> sa.CheckConstraint:
    quoted = ", ".join(f"'{status}'" for status in STATUSES)
    return sa.CheckConstraint(f"{name} IN ({quoted})")


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    ]


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not _table_exists(inspector, "field_definitions"):
        op.create_table(
            "field_definitions",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("field_code", sa.String(length=160), nullable=False),
            sa.Column("display_name", sa.String(length=240), nullable=True),
            sa.Column("data_type", sa.String(length=80), nullable=True),
            sa.Column("field_group", sa.String(length=120), nullable=True),
            sa.Column("legal_role", sa.String(length=120), nullable=True),
            sa.Column("act_type", sa.String(length=120), nullable=True),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("status", sa.String(length=40), nullable=False, server_default=sa.text("'suggested'")),
            sa.Column("confidence", sa.Float(), nullable=False, server_default=sa.text("0")),
            sa.Column("source", sa.String(length=160), nullable=True),
            sa.Column("metadata_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            *_timestamps(),
            _status_check(),
        )
        inspector = sa.inspect(bind)

    if not _table_exists(inspector, "corpus_documents"):
        op.create_table(
            "corpus_documents",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("filename", sa.String(length=260), nullable=False),
            sa.Column("source_zip", sa.String(length=500), nullable=True),
            sa.Column("source_path", sa.String(length=1000), nullable=True),
            sa.Column("notary_name", sa.String(length=240), nullable=True),
            sa.Column("project_name", sa.String(length=240), nullable=True),
            sa.Column("document_type", sa.String(length=160), nullable=True),
            sa.Column("act_type", sa.String(length=160), nullable=True),
            sa.Column("is_tagged", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.Column("marker_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
            sa.Column("red_text_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
            sa.Column("processing_status", sa.String(length=40), nullable=False, server_default=sa.text("'draft'")),
            sa.Column("error_message", sa.Text(), nullable=True),
            sa.Column("metadata_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            *_timestamps(),
        )
        inspector = sa.inspect(bind)

    if not _table_exists(inspector, "field_aliases"):
        op.create_table(
            "field_aliases",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("raw_field_code", sa.String(length=200), nullable=False),
            sa.Column("canonical_field_code", sa.String(length=160), nullable=False),
            sa.Column("field_definition_id", sa.Integer(), sa.ForeignKey("field_definitions.id", ondelete="SET NULL"), nullable=True),
            sa.Column("frequency", sa.Integer(), nullable=False, server_default=sa.text("0")),
            sa.Column("status", sa.String(length=40), nullable=False, server_default=sa.text("'suggested'")),
            sa.Column("source", sa.String(length=160), nullable=True),
            sa.Column("metadata_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            *_timestamps(),
            _status_check(),
        )
        inspector = sa.inspect(bind)

    if not _table_exists(inspector, "corpus_document_fields"):
        op.create_table(
            "corpus_document_fields",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("corpus_document_id", sa.Integer(), sa.ForeignKey("corpus_documents.id", ondelete="CASCADE"), nullable=False),
            sa.Column("raw_field_code", sa.String(length=200), nullable=False),
            sa.Column("canonical_field_code", sa.String(length=160), nullable=True),
            sa.Column("example_value", sa.Text(), nullable=True),
            sa.Column("occurrences", sa.Integer(), nullable=False, server_default=sa.text("0")),
            sa.Column("status", sa.String(length=40), nullable=False, server_default=sa.text("'draft'")),
            sa.Column("metadata_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            *_timestamps(),
            _status_check(),
        )
        inspector = sa.inspect(bind)

    if not _table_exists(inspector, "field_patterns"):
        op.create_table(
            "field_patterns",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("field_definition_id", sa.Integer(), sa.ForeignKey("field_definitions.id", ondelete="SET NULL"), nullable=True),
            sa.Column("raw_field_code", sa.String(length=200), nullable=False),
            sa.Column("canonical_field_code", sa.String(length=160), nullable=True),
            sa.Column("notary_name", sa.String(length=240), nullable=True),
            sa.Column("project_name", sa.String(length=240), nullable=True),
            sa.Column("document_type", sa.String(length=160), nullable=True),
            sa.Column("act_type", sa.String(length=160), nullable=True),
            sa.Column("text_before", sa.Text(), nullable=True),
            sa.Column("text_after", sa.Text(), nullable=True),
            sa.Column("example_value", sa.Text(), nullable=True),
            sa.Column("pattern_source_file", sa.String(length=1000), nullable=True),
            sa.Column("frequency", sa.Integer(), nullable=False, server_default=sa.text("1")),
            sa.Column("confidence", sa.Float(), nullable=False, server_default=sa.text("0")),
            sa.Column("status", sa.String(length=40), nullable=False, server_default=sa.text("'draft'")),
            sa.Column("metadata_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            *_timestamps(),
            _status_check(),
        )
        inspector = sa.inspect(bind)

    indexes = [
        ("field_definitions", "ix_field_definitions_field_code", ["field_code"], True),
        ("field_aliases", "ix_field_aliases_raw_field_code", ["raw_field_code"], False),
        ("field_aliases", "ix_field_aliases_canonical_field_code", ["canonical_field_code"], False),
        ("corpus_documents", "ix_corpus_documents_filename", ["filename"], False),
        ("corpus_documents", "ix_corpus_documents_notary_name_project_name", ["notary_name", "project_name"], False),
        ("corpus_document_fields", "ix_corpus_document_fields_document_id", ["corpus_document_id"], False),
        ("corpus_document_fields", "ix_corpus_document_fields_raw_field_code", ["raw_field_code"], False),
        ("field_patterns", "ix_field_patterns_raw_field_code", ["raw_field_code"], False),
        ("field_patterns", "ix_field_patterns_canonical_field_code", ["canonical_field_code"], False),
    ]
    for table_name, index_name, columns, unique in indexes:
        inspector = sa.inspect(bind)
        if _table_exists(inspector, table_name) and not _index_exists(inspector, table_name, index_name):
            op.create_index(index_name, table_name, columns, unique=unique)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    for table_name in (
        "field_patterns",
        "corpus_document_fields",
        "field_aliases",
        "corpus_documents",
        "field_definitions",
    ):
        inspector = sa.inspect(bind)
        if _table_exists(inspector, table_name):
            op.drop_table(table_name)
