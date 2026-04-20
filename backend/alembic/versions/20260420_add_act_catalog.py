"""add act_catalog and case_acts tables

Revision ID: 20260420_add_act_catalog
Revises: 20260419_add_legal_entities
Create Date: 2026-04-20 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "20260420_add_act_catalog"
down_revision = "20260419_add_legal_entities"
branch_labels = None
depends_on = None


def _table_exists(inspector: sa.Inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _index_exists(inspector: sa.Inspector, table_name: str, index_name: str) -> bool:
    return any(index["name"] == index_name for index in inspector.get_indexes(table_name))


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not _table_exists(inspector, "act_catalog"):
        op.create_table(
            "act_catalog",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("code", sa.String(length=80), nullable=False, unique=True),
            sa.Column("label", sa.String(length=200), nullable=False),
            sa.Column("roles_json", sa.Text(), nullable=False, server_default=sa.text("'[]'")),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        )
        inspector = sa.inspect(bind)

    if not _index_exists(inspector, "act_catalog", op.f("ix_act_catalog_id")):
        op.create_index(op.f("ix_act_catalog_id"), "act_catalog", ["id"], unique=False)
    if not _index_exists(inspector, "act_catalog", op.f("ix_act_catalog_code")):
        op.create_index(op.f("ix_act_catalog_code"), "act_catalog", ["code"], unique=True)

    if not _table_exists(inspector, "case_acts"):
        op.create_table(
            "case_acts",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("case_id", sa.Integer(), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
            sa.Column("act_code", sa.String(length=80), nullable=False),
            sa.Column("act_label", sa.String(length=200), nullable=False),
            sa.Column("act_order", sa.Integer(), nullable=False),
            sa.Column("roles_json", sa.Text(), nullable=False, server_default=sa.text("'[]'")),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        )
        inspector = sa.inspect(bind)

    if not _index_exists(inspector, "case_acts", op.f("ix_case_acts_id")):
        op.create_index(op.f("ix_case_acts_id"), "case_acts", ["id"], unique=False)
    if not _index_exists(inspector, "case_acts", op.f("ix_case_acts_case_id")):
        op.create_index(op.f("ix_case_acts_case_id"), "case_acts", ["case_id"], unique=False)
    if not _index_exists(inspector, "case_acts", op.f("ix_case_acts_case_id_act_order")):
        op.create_index(op.f("ix_case_acts_case_id_act_order"), "case_acts", ["case_id", "act_order"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if _index_exists(inspector, "case_acts", op.f("ix_case_acts_case_id_act_order")):
        op.drop_index(op.f("ix_case_acts_case_id_act_order"), table_name="case_acts")
    if _index_exists(inspector, "case_acts", op.f("ix_case_acts_case_id")):
        op.drop_index(op.f("ix_case_acts_case_id"), table_name="case_acts")
    if _index_exists(inspector, "case_acts", op.f("ix_case_acts_id")):
        op.drop_index(op.f("ix_case_acts_id"), table_name="case_acts")
    if _table_exists(inspector, "case_acts"):
        op.drop_table("case_acts")

    inspector = sa.inspect(bind)
    if _index_exists(inspector, "act_catalog", op.f("ix_act_catalog_code")):
        op.drop_index(op.f("ix_act_catalog_code"), table_name="act_catalog")
    if _index_exists(inspector, "act_catalog", op.f("ix_act_catalog_id")):
        op.drop_index(op.f("ix_act_catalog_id"), table_name="act_catalog")
    if _table_exists(inspector, "act_catalog"):
        op.drop_table("act_catalog")
