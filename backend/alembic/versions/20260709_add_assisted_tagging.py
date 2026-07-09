"""add assisted tagging jobs

Revision ID: 20260709_add_assisted_tagging
Revises: 20260513_promote_legacy_notary_to_titular
Create Date: 2026-07-09 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "20260709_add_assisted_tagging"
down_revision = "20260513_promote_legacy_notary_to_titular"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    existing = set(inspector.get_table_names())

    if "assisted_tagging_jobs" not in existing:
        op.create_table(
            "assisted_tagging_jobs",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("job_uuid", sa.String(length=36), nullable=False),
            sa.Column("status", sa.String(length=32), nullable=False),
            sa.Column("notary_id", sa.Integer(), nullable=False),
            sa.Column("created_by_user_id", sa.Integer(), nullable=False),
            sa.Column("approved_by_user_id", sa.Integer(), nullable=True),
            sa.Column("document_type", sa.String(length=120), nullable=False),
            sa.Column("source_filename", sa.String(length=255), nullable=False),
            sa.Column("original_docx_storage_path", sa.String(length=500), nullable=False),
            sa.Column("pretagged_docx_storage_path", sa.String(length=500), nullable=True),
            sa.Column("approved_docx_storage_path", sa.String(length=500), nullable=True),
            sa.Column("technical_template_storage_path", sa.String(length=500), nullable=True),
            sa.Column("template_id", sa.Integer(), nullable=True),
            sa.Column("error_message", sa.Text(), nullable=True),
            sa.Column("warnings_json", sa.Text(), nullable=False, server_default="[]"),
            sa.Column("structure_json", sa.Text(), nullable=False, server_default="{}"),
            sa.Column("llm_response_json", sa.Text(), nullable=False, server_default="{}"),
            sa.Column("audit_json", sa.Text(), nullable=False, server_default="{}"),
            sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["approved_by_user_id"], ["users.id"]),
            sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
            sa.ForeignKeyConstraint(["notary_id"], ["notaries.id"]),
            sa.ForeignKeyConstraint(["template_id"], ["document_templates.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("job_uuid"),
        )
        op.create_index(op.f("ix_assisted_tagging_jobs_id"), "assisted_tagging_jobs", ["id"], unique=False)
        op.create_index(op.f("ix_assisted_tagging_jobs_job_uuid"), "assisted_tagging_jobs", ["job_uuid"], unique=False)
        op.create_index(op.f("ix_assisted_tagging_jobs_status"), "assisted_tagging_jobs", ["status"], unique=False)
        op.create_index(op.f("ix_assisted_tagging_jobs_notary_id"), "assisted_tagging_jobs", ["notary_id"], unique=False)
        op.create_index(op.f("ix_assisted_tagging_jobs_created_by_user_id"), "assisted_tagging_jobs", ["created_by_user_id"], unique=False)
        op.create_index(op.f("ix_assisted_tagging_jobs_document_type"), "assisted_tagging_jobs", ["document_type"], unique=False)
        op.create_index(op.f("ix_assisted_tagging_jobs_template_id"), "assisted_tagging_jobs", ["template_id"], unique=False)

    if "assisted_tagging_fields" not in existing:
        op.create_table(
            "assisted_tagging_fields",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("job_id", sa.Integer(), nullable=False),
            sa.Column("field_code", sa.String(length=120), nullable=False),
            sa.Column("label", sa.String(length=160), nullable=False),
            sa.Column("original_text", sa.Text(), nullable=False),
            sa.Column("section", sa.String(length=80), nullable=False),
            sa.Column("confidence", sa.Float(), nullable=False),
            sa.Column("occurrences", sa.Integer(), nullable=False),
            sa.Column("status", sa.String(length=32), nullable=False),
            sa.Column("source", sa.String(length=32), nullable=False),
            sa.Column("warning", sa.Text(), nullable=True),
            sa.Column("metadata_json", sa.Text(), nullable=False, server_default="{}"),
            sa.ForeignKeyConstraint(["job_id"], ["assisted_tagging_jobs.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_assisted_tagging_fields_id"), "assisted_tagging_fields", ["id"], unique=False)
        op.create_index(op.f("ix_assisted_tagging_fields_job_id"), "assisted_tagging_fields", ["job_id"], unique=False)
        op.create_index(op.f("ix_assisted_tagging_fields_field_code"), "assisted_tagging_fields", ["field_code"], unique=False)
        op.create_index(op.f("ix_assisted_tagging_fields_section"), "assisted_tagging_fields", ["section"], unique=False)
        op.create_index(op.f("ix_assisted_tagging_fields_status"), "assisted_tagging_fields", ["status"], unique=False)


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    existing = set(inspector.get_table_names())
    if "assisted_tagging_fields" in existing:
        op.drop_index(op.f("ix_assisted_tagging_fields_status"), table_name="assisted_tagging_fields")
        op.drop_index(op.f("ix_assisted_tagging_fields_section"), table_name="assisted_tagging_fields")
        op.drop_index(op.f("ix_assisted_tagging_fields_field_code"), table_name="assisted_tagging_fields")
        op.drop_index(op.f("ix_assisted_tagging_fields_job_id"), table_name="assisted_tagging_fields")
        op.drop_index(op.f("ix_assisted_tagging_fields_id"), table_name="assisted_tagging_fields")
        op.drop_table("assisted_tagging_fields")
    if "assisted_tagging_jobs" in existing:
        op.drop_index(op.f("ix_assisted_tagging_jobs_template_id"), table_name="assisted_tagging_jobs")
        op.drop_index(op.f("ix_assisted_tagging_jobs_document_type"), table_name="assisted_tagging_jobs")
        op.drop_index(op.f("ix_assisted_tagging_jobs_created_by_user_id"), table_name="assisted_tagging_jobs")
        op.drop_index(op.f("ix_assisted_tagging_jobs_notary_id"), table_name="assisted_tagging_jobs")
        op.drop_index(op.f("ix_assisted_tagging_jobs_status"), table_name="assisted_tagging_jobs")
        op.drop_index(op.f("ix_assisted_tagging_jobs_job_uuid"), table_name="assisted_tagging_jobs")
        op.drop_index(op.f("ix_assisted_tagging_jobs_id"), table_name="assisted_tagging_jobs")
        op.drop_table("assisted_tagging_jobs")
