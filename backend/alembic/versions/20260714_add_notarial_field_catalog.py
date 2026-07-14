"""add notarial field catalog

Revision ID: 20260714_add_notarial_field_catalog
Revises: 20260712_add_notarial_human_review_templates
Create Date: 2026-07-14
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260714_add_notarial_field_catalog"
down_revision = "20260712_add_notarial_human_review_templates"
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

    if not _table_exists(inspector, "notarial_field_catalog"):
        op.create_table(
            "notarial_field_catalog",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("code", sa.String(length=120), nullable=False),
            sa.Column("label", sa.String(length=200), nullable=False),
            sa.Column("field_type", sa.String(length=40), nullable=False, server_default=sa.text("'text'")),
            sa.Column("category", sa.String(length=80), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("options_json", sa.Text(), nullable=True),
            sa.Column("scope", sa.String(length=20), nullable=False, server_default=sa.text("'global'")),
            sa.Column("notary_id", sa.Integer(), sa.ForeignKey("notaries.id", ondelete="SET NULL"), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
            sa.Column("created_by_user_id", sa.Integer(), nullable=True),
            sa.Column("metadata_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.UniqueConstraint("code", "notary_id", name="uq_notarial_field_catalog_code_notary"),
        )

    indexes = [
        ("ix_notarial_field_catalog_id", ["id"]),
        ("ix_notarial_field_catalog_code", ["code"]),
        ("ix_notarial_field_catalog_category", ["category"]),
        ("ix_notarial_field_catalog_scope", ["scope"]),
        ("ix_notarial_field_catalog_notary_id", ["notary_id"]),
        ("ix_notarial_field_catalog_is_active", ["is_active"]),
    ]
    for index_name, columns in indexes:
        _create_index_if_missing("notarial_field_catalog", index_name, columns)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if _table_exists(inspector, "notarial_field_catalog"):
        op.drop_table("notarial_field_catalog")
