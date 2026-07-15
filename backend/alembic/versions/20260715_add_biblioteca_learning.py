"""add biblioteca learning tables

Revision ID: 20260715_add_biblioteca_learning
Revises: 20260714_add_notarial_field_catalog
Create Date: 2026-07-15
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260715_add_biblioteca_learning"
down_revision = "20260714_add_notarial_field_catalog"
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


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not _table_exists(inspector, "biblioteca_analysis_runs"):
        op.create_table(
            "biblioteca_analysis_runs",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("notary_id", sa.Integer(), sa.ForeignKey("notaries.id", ondelete="SET NULL"), nullable=True),
            sa.Column("case_id", sa.Integer(), sa.ForeignKey("cases.id", ondelete="SET NULL"), nullable=True),
            sa.Column("document_id", sa.Integer(), sa.ForeignKey("case_documents.id", ondelete="SET NULL"), nullable=True),
            sa.Column("source_version_id", sa.Integer(), sa.ForeignKey("case_document_versions.id", ondelete="SET NULL"), nullable=True),
            sa.Column("review_version_id", sa.Integer(), sa.ForeignKey("case_document_versions.id", ondelete="SET NULL"), nullable=True),
            sa.Column("document_sha256", sa.String(length=64), nullable=False),
            sa.Column("document_type", sa.String(length=120), nullable=True),
            sa.Column("model", sa.String(length=80), nullable=False),
            sa.Column("prompt_version", sa.String(length=40), nullable=False),
            sa.Column("profile_version", sa.Integer(), nullable=True),
            sa.Column("status", sa.String(length=40), nullable=False, server_default=sa.text("'running'")),
            sa.Column("input_tokens", sa.Integer(), nullable=True),
            sa.Column("output_tokens", sa.Integer(), nullable=True),
            sa.Column("latency_ms", sa.Integer(), nullable=True),
            sa.Column("cost_usd", sa.Float(), nullable=True),
            sa.Column("detected_fields", sa.Integer(), nullable=False, server_default=sa.text("0")),
            sa.Column("anchored_fields", sa.Integer(), nullable=False, server_default=sa.text("0")),
            sa.Column("skipped_fields", sa.Integer(), nullable=False, server_default=sa.text("0")),
            sa.Column("error_code", sa.String(length=120), nullable=True),
            sa.Column("error_message", sa.Text(), nullable=True),
            sa.Column("diagnostics_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        )

    if not _table_exists(inspector, "field_signals"):
        op.create_table(
            "field_signals",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("notary_id", sa.Integer(), sa.ForeignKey("notaries.id", ondelete="SET NULL"), nullable=True),
            sa.Column("analysis_run_id", sa.Integer(), sa.ForeignKey("biblioteca_analysis_runs.id", ondelete="SET NULL"), nullable=True),
            sa.Column("case_id", sa.Integer(), sa.ForeignKey("cases.id", ondelete="SET NULL"), nullable=True),
            sa.Column("document_id", sa.Integer(), sa.ForeignKey("case_documents.id", ondelete="SET NULL"), nullable=True),
            sa.Column("source_version_id", sa.Integer(), sa.ForeignKey("case_document_versions.id", ondelete="SET NULL"), nullable=True),
            sa.Column("review_version_id", sa.Integer(), sa.ForeignKey("case_document_versions.id", ondelete="SET NULL"), nullable=True),
            sa.Column("decision_version_id", sa.Integer(), sa.ForeignKey("case_document_versions.id", ondelete="SET NULL"), nullable=True),
            sa.Column("document_type", sa.String(length=120), nullable=True),
            sa.Column("section_key", sa.String(length=160), nullable=True),
            sa.Column("entity_type", sa.String(length=80), nullable=True),
            sa.Column("role", sa.String(length=80), nullable=True),
            sa.Column("candidate_type", sa.String(length=80), nullable=True),
            sa.Column("anonymized_context", sa.Text(), nullable=False, server_default=sa.text("''")),
            sa.Column("exact_text_sha256", sa.String(length=64), nullable=False),
            sa.Column("llm_suggestion_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            sa.Column("confidence", sa.Float(), nullable=True),
            sa.Column("human_decision", sa.String(length=40), nullable=False),
            sa.Column("final_field_code", sa.String(length=120), nullable=True),
            sa.Column("final_field_instance_id", sa.String(length=120), nullable=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("model", sa.String(length=80), nullable=True),
            sa.Column("prompt_version", sa.String(length=40), nullable=True),
            sa.Column("profile_version", sa.Integer(), nullable=True),
            sa.Column("metadata_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        )

    if not _table_exists(inspector, "notary_prompt_profiles"):
        op.create_table(
            "notary_prompt_profiles",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("notary_id", sa.Integer(), sa.ForeignKey("notaries.id", ondelete="SET NULL"), nullable=True),
            sa.Column("version", sa.Integer(), nullable=False),
            sa.Column("status", sa.String(length=40), nullable=False, server_default=sa.text("'draft'")),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.Column("compiled_rules_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            sa.Column("aliases_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            sa.Column("positive_patterns_json", sa.Text(), nullable=False, server_default=sa.text("'[]'")),
            sa.Column("negative_patterns_json", sa.Text(), nullable=False, server_default=sa.text("'[]'")),
            sa.Column("field_preferences_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            sa.Column("source_signal_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
            sa.Column("last_source_signal_id", sa.Integer(), nullable=True),
            sa.Column("generated_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("activated_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.UniqueConstraint("notary_id", "version", name="uq_notary_prompt_profiles_notary_version"),
        )

    for table_name, indexes in {
        "biblioteca_analysis_runs": [
            ("ix_biblioteca_analysis_runs_id", ["id"]),
            ("ix_biblioteca_analysis_runs_notary_id", ["notary_id"]),
            ("ix_biblioteca_analysis_runs_case_id", ["case_id"]),
            ("ix_biblioteca_analysis_runs_document_id", ["document_id"]),
            ("ix_biblioteca_analysis_runs_source_version_id", ["source_version_id"]),
            ("ix_biblioteca_analysis_runs_review_version_id", ["review_version_id"]),
            ("ix_biblioteca_analysis_runs_document_sha256", ["document_sha256"]),
            ("ix_biblioteca_analysis_runs_document_type", ["document_type"]),
            ("ix_biblioteca_analysis_runs_prompt_version", ["prompt_version"]),
            ("ix_biblioteca_analysis_runs_status", ["status"]),
        ],
        "field_signals": [
            ("ix_field_signals_id", ["id"]),
            ("ix_field_signals_notary_id", ["notary_id"]),
            ("ix_field_signals_analysis_run_id", ["analysis_run_id"]),
            ("ix_field_signals_case_id", ["case_id"]),
            ("ix_field_signals_document_id", ["document_id"]),
            ("ix_field_signals_source_version_id", ["source_version_id"]),
            ("ix_field_signals_review_version_id", ["review_version_id"]),
            ("ix_field_signals_decision_version_id", ["decision_version_id"]),
            ("ix_field_signals_document_type", ["document_type"]),
            ("ix_field_signals_section_key", ["section_key"]),
            ("ix_field_signals_entity_type", ["entity_type"]),
            ("ix_field_signals_role", ["role"]),
            ("ix_field_signals_candidate_type", ["candidate_type"]),
            ("ix_field_signals_exact_text_sha256", ["exact_text_sha256"]),
            ("ix_field_signals_human_decision", ["human_decision"]),
            ("ix_field_signals_final_field_code", ["final_field_code"]),
            ("ix_field_signals_final_field_instance_id", ["final_field_instance_id"]),
            ("ix_field_signals_user_id", ["user_id"]),
        ],
        "notary_prompt_profiles": [
            ("ix_notary_prompt_profiles_id", ["id"]),
            ("ix_notary_prompt_profiles_notary_id", ["notary_id"]),
            ("ix_notary_prompt_profiles_version", ["version"]),
            ("ix_notary_prompt_profiles_status", ["status"]),
            ("ix_notary_prompt_profiles_is_active", ["is_active"]),
        ],
    }.items():
        for index_name, columns in indexes:
            _create_index_if_missing(table_name, index_name, columns)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    for table_name in ("field_signals", "notary_prompt_profiles", "biblioteca_analysis_runs"):
        if _table_exists(inspector, table_name):
            op.drop_table(table_name)
