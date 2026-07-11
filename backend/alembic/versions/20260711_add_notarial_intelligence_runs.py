"""Add notarial intelligence run tracking.

Revision ID: 20260711_add_notarial_intelligence_runs
Revises: 20260710_add_notarial_document_intelligence
Create Date: 2026-07-11
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260711_add_notarial_intelligence_runs"
down_revision = "20260710_add_notarial_document_intelligence"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "notarial_intelligence_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("run_key", sa.String(length=240), nullable=False),
        sa.Column("notary_id", sa.Integer(), sa.ForeignKey("notaries.id", ondelete="CASCADE"), nullable=False),
        sa.Column("document_id", sa.Integer(), sa.ForeignKey("notarial_documents.id", ondelete="CASCADE"), nullable=True),
        sa.Column("parse_run_id", sa.Integer(), sa.ForeignKey("notarial_document_parse_runs.id", ondelete="SET NULL"), nullable=True),
        sa.Column("run_type", sa.String(length=60), nullable=False, server_default="document"),
        sa.Column("status", sa.String(length=40), nullable=False, server_default="queued"),
        sa.Column("classifier_version", sa.String(length=120), nullable=False),
        sa.Column("embedding_version_key", sa.String(length=240), nullable=False),
        sa.Column("llm_provider", sa.String(length=120), nullable=True),
        sa.Column("llm_model", sa.String(length=160), nullable=True),
        sa.Column("llm_mode", sa.String(length=40), nullable=False, server_default="off"),
        sa.Column("prompt_version", sa.String(length=120), nullable=True),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("task_id", sa.String(length=180), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("result_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("metadata_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.UniqueConstraint("run_key", name="uq_notarial_intelligence_runs_run_key"),
    )
    op.create_index("ix_notarial_intelligence_runs_notary_status", "notarial_intelligence_runs", ["notary_id", "status"])
    op.create_index("ix_notarial_intelligence_runs_document", "notarial_intelligence_runs", ["notary_id", "document_id"])
    op.create_index("ix_notarial_intelligence_runs_task_id", "notarial_intelligence_runs", ["task_id"])

    op.create_table(
        "notarial_block_alignments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("run_id", sa.Integer(), sa.ForeignKey("notarial_intelligence_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("notary_id", sa.Integer(), sa.ForeignKey("notaries.id", ondelete="CASCADE"), nullable=False),
        sa.Column("target_document_id", sa.Integer(), sa.ForeignKey("notarial_documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("target_parse_run_id", sa.Integer(), sa.ForeignKey("notarial_document_parse_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("target_block_id", sa.Integer(), sa.ForeignKey("notarial_document_blocks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_document_id", sa.Integer(), sa.ForeignKey("notarial_documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_parse_run_id", sa.Integer(), sa.ForeignKey("notarial_document_parse_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_block_id", sa.Integer(), sa.ForeignKey("notarial_document_blocks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("alignment_key", sa.String(length=240), nullable=False),
        sa.Column("structural_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("lexical_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("combined_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("label", sa.String(length=40), nullable=False, server_default="unknown"),
        sa.Column("metadata_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.UniqueConstraint("run_id", "target_block_id", "source_block_id", name="uq_notarial_block_alignments_run_blocks"),
    )
    op.create_index("ix_notarial_block_alignments_run", "notarial_block_alignments", ["run_id"])
    op.create_index("ix_notarial_block_alignments_target", "notarial_block_alignments", ["target_document_id", "target_block_id"])
    op.create_index("ix_notarial_block_alignments_source", "notarial_block_alignments", ["source_document_id", "source_block_id"])

    op.create_table(
        "notarial_benchmark_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("notary_id", sa.Integer(), sa.ForeignKey("notaries.id", ondelete="CASCADE"), nullable=False),
        sa.Column("corpus_version", sa.String(length=120), nullable=False),
        sa.Column("model_version", sa.String(length=240), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False, server_default="completed"),
        sa.Column("metrics_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("metadata_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index("ix_notarial_benchmark_runs_notary_corpus", "notarial_benchmark_runs", ["notary_id", "corpus_version"])


def downgrade() -> None:
    op.drop_index("ix_notarial_benchmark_runs_notary_corpus", table_name="notarial_benchmark_runs")
    op.drop_table("notarial_benchmark_runs")
    op.drop_index("ix_notarial_block_alignments_source", table_name="notarial_block_alignments")
    op.drop_index("ix_notarial_block_alignments_target", table_name="notarial_block_alignments")
    op.drop_index("ix_notarial_block_alignments_run", table_name="notarial_block_alignments")
    op.drop_table("notarial_block_alignments")
    op.drop_index("ix_notarial_intelligence_runs_task_id", table_name="notarial_intelligence_runs")
    op.drop_index("ix_notarial_intelligence_runs_document", table_name="notarial_intelligence_runs")
    op.drop_index("ix_notarial_intelligence_runs_notary_status", table_name="notarial_intelligence_runs")
    op.drop_table("notarial_intelligence_runs")
