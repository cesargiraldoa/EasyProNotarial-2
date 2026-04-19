"""add role_permissions table

Revision ID: add_role_permissions_table
Revises: None
Create Date: 2026-04-18 00:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "add_role_permissions_table"
down_revision = None
branch_labels = None
depends_on = None


MODULOS = [
    "resumen",
    "comercial",
    "notarias",
    "usuarios",
    "roles",
    "minutas",
    "crear_minuta",
    "actos_plantillas",
    "lotes",
    "system_status",
    "configuracion",
]

DEFAULT_PERMISSIONS = {
    "super_admin": {module: True for module in MODULOS},
    "admin_notary": {
        "resumen": True,
        "comercial": False,
        "notarias": False,
        "usuarios": True,
        "roles": True,
        "minutas": True,
        "crear_minuta": True,
        "actos_plantillas": True,
        "lotes": True,
        "system_status": False,
        "configuracion": True,
    },
    "notary": {
        "resumen": True,
        "comercial": False,
        "notarias": False,
        "usuarios": True,
        "roles": False,
        "minutas": True,
        "crear_minuta": True,
        "actos_plantillas": True,
        "lotes": True,
        "system_status": False,
        "configuracion": False,
    },
    "approver": {
        "resumen": True,
        "comercial": False,
        "notarias": False,
        "usuarios": False,
        "roles": False,
        "minutas": True,
        "crear_minuta": True,
        "actos_plantillas": True,
        "lotes": True,
        "system_status": False,
        "configuracion": False,
    },
    "protocolist": {
        "resumen": True,
        "comercial": False,
        "notarias": False,
        "usuarios": False,
        "roles": False,
        "minutas": True,
        "crear_minuta": True,
        "actos_plantillas": True,
        "lotes": True,
        "system_status": False,
        "configuracion": False,
    },
    "client": {
        "resumen": True,
        "comercial": False,
        "notarias": False,
        "usuarios": False,
        "roles": False,
        "minutas": True,
        "crear_minuta": False,
        "actos_plantillas": False,
        "lotes": False,
        "system_status": False,
        "configuracion": False,
    },
}


def _seed_permissions(connection: sa.engine.Connection) -> None:
    roles = sa.table(
        "roles",
        sa.column("id", sa.Integer),
        sa.column("code", sa.String),
    )
    role_permissions = sa.table(
        "role_permissions",
        sa.column("id", sa.Integer),
        sa.column("role_id", sa.Integer),
        sa.column("module_code", sa.String),
        sa.column("can_access", sa.Boolean),
    )

    role_rows = connection.execute(sa.select(roles.c.id, roles.c.code)).all()
    role_ids_by_code = {row.code: row.id for row in role_rows}

    for role_code, module_flags in DEFAULT_PERMISSIONS.items():
        role_id = role_ids_by_code.get(role_code)
        if role_id is None:
            continue
        for module_code in MODULOS:
            can_access = bool(module_flags.get(module_code, False))
            existing = connection.execute(
                sa.select(role_permissions.c.id).where(
                    role_permissions.c.role_id == role_id,
                    role_permissions.c.module_code == module_code,
                )
            ).first()
            if existing is None:
                connection.execute(
                    sa.insert(role_permissions).values(
                        role_id=role_id,
                        module_code=module_code,
                        can_access=can_access,
                    )
                )
            else:
                connection.execute(
                    sa.update(role_permissions)
                    .where(role_permissions.c.id == existing.id)
                    .values(can_access=can_access)
                )


def upgrade() -> None:
    op.create_table(
        "role_permissions",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id"), nullable=False),
        sa.Column("module_code", sa.String(length=80), nullable=False),
        sa.Column("can_access", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.UniqueConstraint("role_id", "module_code", name="uq_role_permissions"),
    )
    op.create_index(op.f("ix_role_permissions_id"), "role_permissions", ["id"], unique=False)
    op.create_index(op.f("ix_role_permissions_module_code"), "role_permissions", ["module_code"], unique=False)
    op.create_index(op.f("ix_role_permissions_role_id"), "role_permissions", ["role_id"], unique=False)

    connection = op.get_bind()
    _seed_permissions(connection)


def downgrade() -> None:
    op.drop_index(op.f("ix_role_permissions_role_id"), table_name="role_permissions")
    op.drop_index(op.f("ix_role_permissions_module_code"), table_name="role_permissions")
    op.drop_index(op.f("ix_role_permissions_id"), table_name="role_permissions")
    op.drop_table("role_permissions")
