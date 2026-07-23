"""link learned template-library items to a bank (legal_entity)

Revision ID: 20260723_add_bank_to_template_library
Revises: 20260721_add_legal_embeddings
Create Date: 2026-07-23 00:00:00.000000
"""

from __future__ import annotations

from alembic import context, op
import sqlalchemy as sa


revision = "20260723_add_bank_to_template_library"
down_revision = "20260721_add_legal_embeddings"
branch_labels = None
depends_on = None

TABLE = "notarial_template_library_items"
COLUMN = "legal_entity_id"
FK_NAME = "fk_notarial_template_library_items_legal_entity_id"
IX_NAME = "ix_notarial_template_library_items_legal_entity_id"


def _table_exists(inspector: sa.Inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _column_exists(inspector: sa.Inspector, table_name: str, column_name: str) -> bool:
    return any(column["name"] == column_name for column in inspector.get_columns(table_name))


def _index_exists(inspector: sa.Inspector, table_name: str, index_name: str) -> bool:
    return any(index["name"] == index_name for index in inspector.get_indexes(table_name))


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not _table_exists(inspector, TABLE):
        return

    if not _column_exists(inspector, TABLE, COLUMN):
        if context.get_context().dialect.name == "sqlite":
            with op.batch_alter_table(TABLE) as batch_op:
                batch_op.add_column(sa.Column(COLUMN, sa.Integer(), nullable=True))
                batch_op.create_foreign_key(FK_NAME, "legal_entities", [COLUMN], ["id"], ondelete="SET NULL")
                batch_op.create_index(IX_NAME, [COLUMN], unique=False)
        else:
            op.add_column(TABLE, sa.Column(COLUMN, sa.Integer(), nullable=True))
            op.create_foreign_key(FK_NAME, TABLE, "legal_entities", [COLUMN], ["id"], ondelete="SET NULL")
            op.create_index(IX_NAME, TABLE, [COLUMN], unique=False)
    elif not _index_exists(inspector, TABLE, IX_NAME):
        op.create_index(IX_NAME, TABLE, [COLUMN], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not _table_exists(inspector, TABLE) or not _column_exists(inspector, TABLE, COLUMN):
        return

    if context.get_context().dialect.name == "sqlite":
        with op.batch_alter_table(TABLE) as batch_op:
            if _index_exists(inspector, TABLE, IX_NAME):
                batch_op.drop_index(IX_NAME)
            batch_op.drop_column(COLUMN)
    else:
        if _index_exists(inspector, TABLE, IX_NAME):
            op.drop_index(IX_NAME, table_name=TABLE)
        op.drop_constraint(FK_NAME, TABLE, type_="foreignkey")
        op.drop_column(TABLE, COLUMN)
