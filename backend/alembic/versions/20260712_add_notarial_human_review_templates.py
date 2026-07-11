"""Add notarial human review and template library.

Revision ID: 20260712_add_notarial_human_review_templates
Revises: 20260711_add_notarial_intelligence_runs
Create Date: 2026-07-12
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260712_add_notarial_human_review_templates"
down_revision = "20260711_add_notarial_intelligence_runs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "notarial_human_review_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("notary_id", sa.Integer(), sa.ForeignKey("notaries.id", ondelete="CASCADE"), nullable=False),
        sa.Column("decision_id", sa.Integer(), sa.ForeignKey("notarial_document_decisions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("run_id", sa.Integer(), sa.ForeignKey("notarial_intelligence_runs.id", ondelete="SET NULL"), nullable=True),
        sa.Column("document_id", sa.Integer(), sa.ForeignKey("notarial_documents.id", ondelete="CASCADE"), nullable=True),
        sa.Column("parse_run_id", sa.Integer(), sa.ForeignKey("notarial_document_parse_runs.id", ondelete="SET NULL"), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", sa.String(length=40), nullable=False, server_default="open"),
        sa.Column("reviewer_user_id", sa.Integer(), nullable=True),
        sa.Column("locked_by_user_id", sa.Integer(), nullable=True),
        sa.Column("lock_token", sa.String(length=120), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.UniqueConstraint("decision_id", "version", name="uq_notarial_human_review_session_decision_version"),
    )
    for column in ("notary_id", "decision_id", "run_id", "document_id", "parse_run_id", "status", "reviewer_user_id", "locked_by_user_id", "lock_token"):
        op.create_index(f"ix_notarial_human_review_sessions_{column}", "notarial_human_review_sessions", [column])

    op.create_table(
        "notarial_human_field_reviews",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("session_id", sa.Integer(), sa.ForeignKey("notarial_human_review_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("notary_id", sa.Integer(), sa.ForeignKey("notaries.id", ondelete="CASCADE"), nullable=False),
        sa.Column("decision_id", sa.Integer(), sa.ForeignKey("notarial_document_decisions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("document_id", sa.Integer(), sa.ForeignKey("notarial_documents.id", ondelete="CASCADE"), nullable=True),
        sa.Column("parse_run_id", sa.Integer(), sa.ForeignKey("notarial_document_parse_runs.id", ondelete="SET NULL"), nullable=True),
        sa.Column("block_id", sa.Integer(), sa.ForeignKey("notarial_document_blocks.id", ondelete="SET NULL"), nullable=True),
        sa.Column("entity_id", sa.Integer(), sa.ForeignKey("notarial_document_entities.id", ondelete="SET NULL"), nullable=True),
        sa.Column("occurrence_key", sa.String(length=240), nullable=False),
        sa.Column("field_code", sa.String(length=200), nullable=True),
        sa.Column("proposed_field_code", sa.String(length=200), nullable=True),
        sa.Column("original_value", sa.Text(), nullable=True),
        sa.Column("proposed_value", sa.Text(), nullable=True),
        sa.Column("action", sa.String(length=40), nullable=False, server_default="pending"),
        sa.Column("apply_scope", sa.String(length=40), nullable=False, server_default="single"),
        sa.Column("fixed_variable_label", sa.String(length=40), nullable=False, server_default="unknown"),
        sa.Column("is_new_field_proposal", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("status", sa.String(length=40), nullable=False, server_default="pending"),
        sa.Column("decided_by_user_id", sa.Integer(), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.UniqueConstraint("session_id", "occurrence_key", name="uq_notarial_human_field_review_session_occurrence"),
    )
    for column in ("session_id", "notary_id", "decision_id", "document_id", "parse_run_id", "block_id", "entity_id", "field_code", "proposed_field_code", "action", "fixed_variable_label", "is_new_field_proposal", "status", "decided_by_user_id"):
        op.create_index(f"ix_notarial_human_field_reviews_{column}", "notarial_human_field_reviews", [column])

    op.create_table(
        "notarial_template_library_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("notary_id", sa.Integer(), sa.ForeignKey("notaries.id", ondelete="CASCADE"), nullable=False),
        sa.Column("library_key", sa.String(length=180), nullable=False),
        sa.Column("name", sa.String(length=240), nullable=False),
        sa.Column("template_kind", sa.String(length=40), nullable=False, server_default="individual"),
        sa.Column("status", sa.String(length=40), nullable=False, server_default="draft"),
        sa.Column("act_code", sa.String(length=120), nullable=True),
        sa.Column("document_type", sa.String(length=160), nullable=True),
        sa.Column("family_id", sa.Integer(), sa.ForeignKey("notarial_document_families.id", ondelete="SET NULL"), nullable=True),
        sa.Column("bank_name", sa.String(length=240), nullable=True),
        sa.Column("project_name", sa.String(length=240), nullable=True),
        sa.Column("source_document_id", sa.Integer(), sa.ForeignKey("notarial_documents.id", ondelete="SET NULL"), nullable=True),
        sa.Column("latest_version_id", sa.Integer(), nullable=True),
        sa.Column("approved_version_id", sa.Integer(), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.UniqueConstraint("notary_id", "library_key", name="uq_notarial_template_library_items_notary_key"),
    )
    for column in ("notary_id", "library_key", "template_kind", "status", "act_code", "document_type", "family_id", "bank_name", "project_name", "source_document_id", "latest_version_id", "approved_version_id"):
        op.create_index(f"ix_notarial_template_library_items_{column}", "notarial_template_library_items", [column])

    op.create_table(
        "notarial_template_versions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("library_item_id", sa.Integer(), sa.ForeignKey("notarial_template_library_items.id", ondelete="CASCADE"), nullable=False),
        sa.Column("notary_id", sa.Integer(), sa.ForeignKey("notaries.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False, server_default="draft"),
        sa.Column("source_decision_id", sa.Integer(), sa.ForeignKey("notarial_document_decisions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("review_session_id", sa.Integer(), sa.ForeignKey("notarial_human_review_sessions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("source_document_id", sa.Integer(), sa.ForeignKey("notarial_documents.id", ondelete="SET NULL"), nullable=True),
        sa.Column("content_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("placeholder_map_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("provenance_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("storage_path", sa.String(length=1000), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("approved_by_user_id", sa.Integer(), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rollback_of_version_id", sa.Integer(), sa.ForeignKey("notarial_template_versions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.UniqueConstraint("library_item_id", "version_number", name="uq_notarial_template_versions_item_number"),
    )
    for column in ("library_item_id", "notary_id", "status", "source_decision_id", "review_session_id", "source_document_id", "created_by_user_id", "approved_by_user_id", "rollback_of_version_id"):
        op.create_index(f"ix_notarial_template_versions_{column}", "notarial_template_versions", [column])

    op.create_table(
        "notarial_human_review_audit",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("notary_id", sa.Integer(), sa.ForeignKey("notaries.id", ondelete="CASCADE"), nullable=False),
        sa.Column("entity_type", sa.String(length=80), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("actor_user_id", sa.Integer(), nullable=True),
        sa.Column("idempotency_key", sa.String(length=180), nullable=True),
        sa.Column("payload_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    for column in ("notary_id", "entity_type", "entity_id", "event_type", "actor_user_id", "idempotency_key"):
        op.create_index(f"ix_notarial_human_review_audit_{column}", "notarial_human_review_audit", [column])


def downgrade() -> None:
    op.drop_table("notarial_human_review_audit")
    op.drop_table("notarial_template_versions")
    op.drop_table("notarial_template_library_items")
    op.drop_table("notarial_human_field_reviews")
    op.drop_table("notarial_human_review_sessions")
