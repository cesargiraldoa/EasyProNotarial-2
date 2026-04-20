"""add legal_entities tables

Revision ID: 20260419_add_legal_entities
Revises: add_role_permissions_table
Create Date: 2026-04-19 00:00:00.000000
"""

from __future__ import annotations

from alembic import context, op
import sqlalchemy as sa


revision = "20260419_add_legal_entities"
down_revision = "add_role_permissions_table"
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

    if not _table_exists(inspector, "legal_entities"):
        op.create_table(
            "legal_entities",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("nit", sa.String(length=40), nullable=False),
            sa.Column("name", sa.String(length=200), nullable=False),
            sa.Column("legal_representative", sa.String(length=160), nullable=True),
            sa.Column("municipality", sa.String(length=120), nullable=True),
            sa.Column("address", sa.String(length=255), nullable=True),
            sa.Column("phone", sa.String(length=40), nullable=True),
            sa.Column("email", sa.String(length=120), nullable=True),
            sa.Column("metadata_json", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.UniqueConstraint("nit", name="uq_legal_entities_nit"),
        )
        inspector = sa.inspect(bind)
    if not _index_exists(inspector, "legal_entities", op.f("ix_legal_entities_id")):
        op.create_index(op.f("ix_legal_entities_id"), "legal_entities", ["id"], unique=False)
    if not _index_exists(inspector, "legal_entities", op.f("ix_legal_entities_nit")):
        op.create_index(op.f("ix_legal_entities_nit"), "legal_entities", ["nit"], unique=False)
    if not _index_exists(inspector, "legal_entities", op.f("ix_legal_entities_name")):
        op.create_index(op.f("ix_legal_entities_name"), "legal_entities", ["name"], unique=False)

    if not _table_exists(inspector, "legal_entity_representatives"):
        op.create_table(
            "legal_entity_representatives",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("legal_entity_id", sa.Integer(), sa.ForeignKey("legal_entities.id"), nullable=False),
            sa.Column("person_id", sa.Integer(), sa.ForeignKey("persons.id"), nullable=False),
            sa.Column("power_type", sa.String(length=120), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.UniqueConstraint("legal_entity_id", "person_id", name="uq_entity_representative"),
        )
        inspector = sa.inspect(bind)
    if not _index_exists(inspector, "legal_entity_representatives", op.f("ix_legal_entity_representatives_id")):
        op.create_index(op.f("ix_legal_entity_representatives_id"), "legal_entity_representatives", ["id"], unique=False)
    if not _index_exists(inspector, "legal_entity_representatives", op.f("ix_legal_entity_representatives_legal_entity_id")):
        op.create_index(op.f("ix_legal_entity_representatives_legal_entity_id"), "legal_entity_representatives", ["legal_entity_id"], unique=False)
    if not _index_exists(inspector, "legal_entity_representatives", op.f("ix_legal_entity_representatives_person_id")):
        op.create_index(op.f("ix_legal_entity_representatives_person_id"), "legal_entity_representatives", ["person_id"], unique=False)

    inspector = sa.inspect(bind)
    if not _column_exists(inspector, "case_participants", "legal_entity_id"):
        if context.get_context().dialect.name == "sqlite":
            with op.batch_alter_table("case_participants") as batch_op:
                batch_op.add_column(sa.Column("legal_entity_id", sa.Integer(), nullable=True))
                batch_op.create_foreign_key(
                    "fk_case_participants_legal_entity_id",
                    "legal_entities",
                    ["legal_entity_id"],
                    ["id"],
                )
                batch_op.create_index(
                    "ix_case_participants_legal_entity_id",
                    ["legal_entity_id"],
                    unique=False,
                )
        else:
            op.add_column("case_participants", sa.Column("legal_entity_id", sa.Integer(), nullable=True))
            op.create_foreign_key(
                "fk_case_participants_legal_entity_id",
                "case_participants",
                "legal_entities",
                ["legal_entity_id"],
                ["id"],
            )
            op.create_index(
                "ix_case_participants_legal_entity_id",
                "case_participants",
                ["legal_entity_id"],
                unique=False,
            )
    elif not _index_exists(inspector, "case_participants", "ix_case_participants_legal_entity_id"):
        op.create_index(
            "ix_case_participants_legal_entity_id",
            "case_participants",
            ["legal_entity_id"],
            unique=False,
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if _column_exists(inspector, "case_participants", "legal_entity_id"):
        if context.get_context().dialect.name == "sqlite":
            with op.batch_alter_table("case_participants") as batch_op:
                if _index_exists(inspector, "case_participants", "ix_case_participants_legal_entity_id"):
                    batch_op.drop_index("ix_case_participants_legal_entity_id")
                batch_op.drop_column("legal_entity_id")
        else:
            if _index_exists(inspector, "case_participants", "ix_case_participants_legal_entity_id"):
                op.drop_index("ix_case_participants_legal_entity_id", table_name="case_participants")
            op.drop_constraint("fk_case_participants_legal_entity_id", "case_participants", type_="foreignkey")
            op.drop_column("case_participants", "legal_entity_id")

    inspector = sa.inspect(bind)
    if _table_exists(inspector, "legal_entity_representatives"):
        if _index_exists(inspector, "legal_entity_representatives", op.f("ix_legal_entity_representatives_person_id")):
            op.drop_index(op.f("ix_legal_entity_representatives_person_id"), table_name="legal_entity_representatives")
        if _index_exists(inspector, "legal_entity_representatives", op.f("ix_legal_entity_representatives_legal_entity_id")):
            op.drop_index(op.f("ix_legal_entity_representatives_legal_entity_id"), table_name="legal_entity_representatives")
        if _index_exists(inspector, "legal_entity_representatives", op.f("ix_legal_entity_representatives_id")):
            op.drop_index(op.f("ix_legal_entity_representatives_id"), table_name="legal_entity_representatives")
        op.drop_table("legal_entity_representatives")

    inspector = sa.inspect(bind)
    if _table_exists(inspector, "legal_entities"):
        if _index_exists(inspector, "legal_entities", op.f("ix_legal_entities_name")):
            op.drop_index(op.f("ix_legal_entities_name"), table_name="legal_entities")
        if _index_exists(inspector, "legal_entities", op.f("ix_legal_entities_nit")):
            op.drop_index(op.f("ix_legal_entities_nit"), table_name="legal_entities")
        if _index_exists(inspector, "legal_entities", op.f("ix_legal_entities_id")):
            op.drop_index(op.f("ix_legal_entities_id"), table_name="legal_entities")
        op.drop_table("legal_entities")
