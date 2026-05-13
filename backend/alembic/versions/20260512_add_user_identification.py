"""add document identification fields to users

Revision ID: 20260512_add_user_identification
Revises: 20260420_add_act_catalog
Create Date: 2026-05-12 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "20260512_add_user_identification"
down_revision = "20260420_add_act_catalog"
branch_labels = None
depends_on = None


def _table_exists(inspector: sa.Inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _column_exists(inspector: sa.Inspector, table_name: str, column_name: str) -> bool:
    return any(column["name"] == column_name for column in inspector.get_columns(table_name))


def _index_exists(inspector: sa.Inspector, table_name: str, index_name: str) -> bool:
    return any(index["name"] == index_name for index in inspector.get_indexes(table_name))


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not _table_exists(inspector, "users"):
        return

    if not _column_exists(inspector, "users", "document_type"):
        op.add_column("users", sa.Column("document_type", sa.String(length=40), nullable=True))
    if not _column_exists(inspector, "users", "document_number"):
        op.add_column("users", sa.Column("document_number", sa.String(length=40), nullable=True))

    inspector = sa.inspect(bind)
    if not _index_exists(inspector, "users", "uq_users_document_type_document_number"):
        op.create_index(
            "uq_users_document_type_document_number",
            "users",
            ["document_type", "document_number"],
            unique=True,
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if _table_exists(inspector, "users"):
        inspector = sa.inspect(bind)
        if _index_exists(inspector, "users", "uq_users_document_type_document_number"):
            op.drop_index("uq_users_document_type_document_number", table_name="users")
        inspector = sa.inspect(bind)
        if _column_exists(inspector, "users", "document_number"):
            op.drop_column("users", "document_number")
        inspector = sa.inspect(bind)
        if _column_exists(inspector, "users", "document_type"):
            op.drop_column("users", "document_type")
