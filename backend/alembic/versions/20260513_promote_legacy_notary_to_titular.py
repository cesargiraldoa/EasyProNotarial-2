"""promote legacy notary users to titular when missing

Revision ID: 20260513_promote_legacy_notary_to_titular
Revises: 20260512_add_user_identification
Create Date: 2026-05-13 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "20260513_promote_legacy_notary_to_titular"
down_revision = "20260512_add_user_identification"
branch_labels = None
depends_on = None


def _table(bind: sa.engine.Connection, name: str) -> sa.Table:
    metadata = sa.MetaData()
    return sa.Table(name, metadata, autoload_with=bind)


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "users" not in inspector.get_table_names():
        return
    if "roles" not in inspector.get_table_names():
        return
    if "role_assignments" not in inspector.get_table_names():
        return

    users = _table(bind, "users")
    roles = _table(bind, "roles")
    role_assignments = _table(bind, "role_assignments")

    titular_role_id = bind.execute(
        sa.select(roles.c.id).where(roles.c.code == "notary_titular")
    ).scalar_one_or_none()
    legacy_role_id = bind.execute(
        sa.select(roles.c.id).where(roles.c.code == "notary")
    ).scalar_one_or_none()
    if titular_role_id is None or legacy_role_id is None:
        return

    titular_notary_ids = {
        row[0]
        for row in bind.execute(
            sa.select(role_assignments.c.notary_id)
            .select_from(
                role_assignments.join(users, users.c.id == role_assignments.c.user_id).join(
                    roles, roles.c.id == role_assignments.c.role_id
                )
            )
            .where(
                roles.c.code == "notary_titular",
                users.c.is_active.is_(True),
                role_assignments.c.notary_id.isnot(None),
            )
            .distinct()
        ).all()
        if row[0] is not None
    }

    candidate_rows = bind.execute(
        sa.select(role_assignments.c.notary_id, users.c.id.label("user_id"))
        .select_from(
            role_assignments.join(users, users.c.id == role_assignments.c.user_id).join(
                roles, roles.c.id == role_assignments.c.role_id
            )
        )
        .where(
            roles.c.code == "notary",
            users.c.is_active.is_(True),
            role_assignments.c.notary_id.isnot(None),
        )
        .order_by(role_assignments.c.notary_id.asc(), users.c.id.asc())
    ).all()

    selected_users_by_notary: dict[int, int] = {}
    for notary_id, user_id in candidate_rows:
        if notary_id is None or notary_id in titular_notary_ids or notary_id in selected_users_by_notary:
            continue
        selected_users_by_notary[int(notary_id)] = int(user_id)

    if not selected_users_by_notary:
        return

    existing_pairs = {
        (row[0], row[1])
        for row in bind.execute(
            sa.select(role_assignments.c.user_id, role_assignments.c.notary_id)
            .where(
                role_assignments.c.role_id == titular_role_id,
                role_assignments.c.notary_id.in_(list(selected_users_by_notary.keys())),
            )
        ).all()
    }

    for notary_id, user_id in selected_users_by_notary.items():
        if (user_id, notary_id) in existing_pairs:
            continue
        bind.execute(
            role_assignments.insert().values(
                user_id=user_id,
                role_id=int(titular_role_id),
                notary_id=notary_id,
            )
        )


def downgrade() -> None:
    pass
