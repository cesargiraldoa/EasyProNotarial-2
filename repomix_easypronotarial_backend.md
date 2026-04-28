This file is a merged representation of a subset of the codebase, containing files not matching ignore patterns, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of a subset of the repository's contents that is considered the most important context.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Files matching these patterns are excluded: .venv, venv, __pycache__, .pytest_cache, .mypy_cache, .ruff_cache, .git, *.log, *.tmp, .env, .env.*, storage, uploads, media
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
activity-test.json
alembic.ini
alembic/env.py
alembic/versions/20260418_add_role_permissions_table.py
alembic/versions/20260419_add_legal_entities.py
alembic/versions/20260420_add_act_catalog.py
app/__init__.py
app/api/router.py
app/core/__init__.py
app/core/config.py
app/core/datetime_utils.py
app/core/deps.py
app/core/security.py
app/db/__init__.py
app/db/base.py
app/db/init_db.py
app/db/seed.py
app/db/session.py
app/main.py
app/models/__init__.py
app/models/act_catalog.py
app/models/base.py
app/models/case_act_data.py
app/models/case_act.py
app/models/case_client_comment.py
app/models/case_document_version.py
app/models/case_document.py
app/models/case_internal_note.py
app/models/case_participant.py
app/models/case_state_definition.py
app/models/case_timeline_event.py
app/models/case_workflow_event.py
app/models/case.py
app/models/document_template.py
app/models/legal_entity_representative.py
app/models/legal_entity.py
app/models/notary_commercial_activity.py
app/models/notary_crm_audit_log.py
app/models/notary.py
app/models/numbering_sequence.py
app/models/person.py
app/models/role_assignment.py
app/models/role_permission.py
app/models/role.py
app/models/template_field.py
app/models/template_required_role.py
app/models/user.py
app/modules/__init__.py
app/modules/act_catalog/__init__.py
app/modules/act_catalog/router.py
app/modules/auth/__init__.py
app/modules/auth/router.py
app/modules/cases/router.py
app/modules/dashboard/router.py
app/modules/document_flow/router.py
app/modules/legal_entities/__init__.py
app/modules/legal_entities/router.py
app/modules/notaries/__init__.py
app/modules/notaries/router.py
app/modules/persons/router.py
app/modules/templates/router.py
app/modules/users/__init__.py
app/modules/users/router.py
app/schemas/__init__.py
app/schemas/act_catalog.py
app/schemas/auth.py
app/schemas/case.py
app/schemas/dashboard.py
app/schemas/legal_entity.py
app/schemas/notary.py
app/schemas/person.py
app/schemas/template.py
app/schemas/user.py
app/seeds/__init__.py
app/seeds/seed_act_catalog.py
app/seeds/seed_document_templates.py
app/seeds/seed_legal_entities.py
app/seeds/templates/aragua-parq-1c.docx
app/seeds/templates/aragua-parq-2c.docx
app/seeds/templates/aragua-parq-3c.docx
app/seeds/templates/correccion-registro-civil.docx
app/seeds/templates/jaggua-bogota-1c.docx
app/seeds/templates/jaggua-bogota-2c.docx
app/seeds/templates/salida-del-pais.docx
app/seeds/templates/torre6-contado.docx
app/services/__init__.py
app/services/auth.py
app/services/document_generation.py
app/services/gari_document_service.py
app/services/notary_imports.py
app/services/storage.py
railway.toml
requirements.txt
scripts/check_db.py
scripts/migrate_to_postgres.py
scripts/seed_notarias_piloto.py
```

# Files

## File: activity-test.json
```json
{"occurred_at":"2026-03-23T18:30:00Z","management_type":"Reunion virtual","comment":"Validacion end-to-end del historial comercial.","responsible":"QA Codex","result":"seguimiento confirmado","next_action":"Enviar resumen ejecutivo y coordinar siguiente llamada."}
```

## File: alembic.ini
```ini
[alembic]
script_location = alembic
prepend_sys_path = .
sqlalchemy.url = sqlite:///C:/EasyProNotarial-2/easypro2/backend/easypro2.db

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
```

## File: alembic/env.py
```python
from __future__ import annotations

import sys
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.core.config import get_settings
from app.models.base import Base
import app.models  # noqa: F401

config = context.config
config.set_main_option("sqlalchemy.url", get_settings().database_url.replace("%", "%%"))

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

## File: alembic/versions/20260418_add_role_permissions_table.py
```python
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
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "role_permissions" not in inspector.get_table_names():
        op.create_table(
            "role_permissions",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id"), nullable=False),
            sa.Column("module_code", sa.String(length=80), nullable=False),
            sa.Column("can_access", sa.Boolean(), nullable=False, server_default=sa.text("0")),
            sa.UniqueConstraint("role_id", "module_code", name="uq_role_permissions"),
        )
        inspector = sa.inspect(bind)

    if not any(index["name"] == op.f("ix_role_permissions_id") for index in inspector.get_indexes("role_permissions")):
        op.create_index(op.f("ix_role_permissions_id"), "role_permissions", ["id"], unique=False)
    if not any(index["name"] == op.f("ix_role_permissions_module_code") for index in inspector.get_indexes("role_permissions")):
        op.create_index(op.f("ix_role_permissions_module_code"), "role_permissions", ["module_code"], unique=False)
    if not any(index["name"] == op.f("ix_role_permissions_role_id") for index in inspector.get_indexes("role_permissions")):
        op.create_index(op.f("ix_role_permissions_role_id"), "role_permissions", ["role_id"], unique=False)

    connection = op.get_bind()
    _seed_permissions(connection)


def downgrade() -> None:
    op.drop_index(op.f("ix_role_permissions_role_id"), table_name="role_permissions")
    op.drop_index(op.f("ix_role_permissions_module_code"), table_name="role_permissions")
    op.drop_index(op.f("ix_role_permissions_id"), table_name="role_permissions")
    op.drop_table("role_permissions")
```

## File: alembic/versions/20260419_add_legal_entities.py
```python
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
```

## File: alembic/versions/20260420_add_act_catalog.py
```python
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
```

## File: app/__init__.py
```python

```

## File: app/api/router.py
```python
from fastapi import APIRouter

from app.modules.auth.router import router as auth_router
from app.modules.act_catalog.router import act_catalog_router
from app.modules.cases.router import router as cases_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.document_flow.router import router as document_flow_router
from app.modules.legal_entities.router import router as legal_entities_router
from app.modules.notaries.router import router as notaries_router
from app.modules.persons.router import router as persons_router
from app.modules.templates.router import router as templates_router
from app.modules.users.router import router as users_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(notaries_router)
api_router.include_router(users_router)
api_router.include_router(cases_router)
api_router.include_router(act_catalog_router)
api_router.include_router(templates_router)
api_router.include_router(persons_router)
api_router.include_router(document_flow_router)
api_router.include_router(legal_entities_router)
api_router.include_router(dashboard_router)
```

## File: app/core/__init__.py
```python

```

## File: app/core/config.py
```python
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"
DEFAULT_DATABASE_PATH = BASE_DIR / "easypro2.db"
DEFAULT_DATABASE_URL = f"sqlite:///{DEFAULT_DATABASE_PATH.as_posix()}"


class Settings(BaseSettings):
    app_name: str = "EasyPro 2 API"
    environment: str = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"
    frontend_url: str = "http://localhost:5179"
    database_url: str = DEFAULT_DATABASE_URL
    secret_key: str = "change-this-in-production"
    access_token_expire_minutes: int = 480
    openai_api_key: str = ""

    model_config = SettingsConfigDict(env_file=str(ENV_FILE), env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

## File: app/core/datetime_utils.py
```python
from datetime import datetime, timedelta, timezone

BOGOTA_TIME_ZONE = timezone(timedelta(hours=-5), name="America/Bogota")


def assume_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def to_bogota(value: datetime | None) -> datetime | None:
    normalized = assume_utc(value)
    if normalized is None:
        return None
    return normalized.astimezone(BOGOTA_TIME_ZONE)


def format_bogota_datetime(value: datetime | None, fmt: str = "%Y-%m-%d %H:%M") -> str | None:
    localized = to_bogota(value)
    if localized is None:
        return None
    return localized.strftime(fmt)
```

## File: app/core/deps.py
```python
from collections.abc import Callable

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session, joinedload

from app.core.config import get_settings
from app.core.security import ALGORITHM
from app.db.session import SessionLocal
from app.models.role_assignment import RoleAssignment
from app.models.user import User

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/login", auto_error=False)


ROLE_PERMISSIONS = {
    "super_admin": {"users.read", "users.write", "notaries.read", "notaries.write", "notaries.import", "crm.manage", "crm.audit.read", "cases.read", "cases.write"},
    "admin_notary": {"users.read", "users.write", "notaries.read", "notaries.write", "crm.manage", "crm.audit.read", "cases.read", "cases.write"},
    "notary": {"notaries.read", "crm.manage", "crm.audit.read", "cases.read", "cases.write"},
    "approver": {"notaries.read", "crm.manage", "cases.read", "cases.write"},
    "protocolist": {"notaries.read", "crm.manage", "cases.read", "cases.write"},
    "client": {"notaries.read", "cases.read"},
}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(request: Request, token: str | None = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    raw_token = token or request.cookies.get("easypro2_session")
    if not raw_token:
        raise credentials_exception
    try:
        payload = jwt.decode(raw_token, settings.secret_key, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except (JWTError, TypeError, ValueError):
        raise credentials_exception

    user = (
        db.query(User)
        .options(
            joinedload(User.default_notary),
            joinedload(User.role_assignments).joinedload(RoleAssignment.role),
            joinedload(User.role_assignments).joinedload(RoleAssignment.notary),
        )
        .filter(User.id == user_id, User.is_active.is_(True))
        .first()
    )
    if user is None:
        raise credentials_exception
    return user


def get_role_codes(user: User) -> set[str]:
    return {assignment.role.code for assignment in user.role_assignments}


def get_manageable_notary_ids(user: User) -> set[int]:
    notary_ids = {assignment.notary_id for assignment in user.role_assignments if assignment.notary_id is not None}
    if user.default_notary_id is not None:
        notary_ids.add(user.default_notary_id)
    return notary_ids


def has_role(user: User, *role_codes: str, notary_id: int | None = None) -> bool:
    expected = set(role_codes)
    for assignment in user.role_assignments:
        if assignment.role.code not in expected:
            continue
        if assignment.notary_id is None or notary_id is None or assignment.notary_id == notary_id:
            return True
    return False


def get_permissions(user: User) -> list[str]:
    permissions: set[str] = set()
    for role_code in get_role_codes(user):
        permissions.update(ROLE_PERMISSIONS.get(role_code, set()))
    return sorted(permissions)


def require_roles(*role_codes: str) -> Callable[[User], User]:
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if has_role(current_user, *role_codes):
            return current_user
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado para esta acción.")

    return dependency


def require_permission(permission: str) -> Callable[[User], User]:
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if permission in get_permissions(current_user):
            return current_user
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado para esta acción.")

    return dependency
```

## File: app/core/security.py
```python
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from app.core.config import get_settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
ALGORITHM = "HS256"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(subject: str, expires_delta: timedelta | None = None, extra_claims: dict[str, Any] | None = None) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    payload: dict[str, Any] = {"sub": subject, "exp": expire}
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)
```

## File: app/db/__init__.py
```python

```

## File: app/db/base.py
```python
from app.models import (
    ActCatalog,
    Case,
    CaseAct,
    CaseActData,
    CaseClientComment,
    CaseDocument,
    CaseDocumentVersion,
    CaseInternalNote,
    CaseParticipant,
    CaseStateDefinition,
    CaseTimelineEvent,
    CaseWorkflowEvent,
    DocumentTemplate,
    LegalEntity,
    LegalEntityRepresentative,
    Notary,
    NotaryCommercialActivity,
    NotaryCrmAuditLog,
    NumberingSequence,
    Person,
    Role,
    RoleAssignment,
    TemplateField,
    TemplateRequiredRole,
    User,
)
from app.models.base import Base
```

## File: app/db/init_db.py
```python
from __future__ import annotations

from sqlalchemy import inspect, text

from app.db.base import Base
from app.db.seed import seed_database
from app.db.session import SessionLocal, engine
from app.models.act_catalog import ActCatalog
from app.models.case import Case
from app.models.case_act import CaseAct
from app.models.case_act_data import CaseActData
from app.models.case_client_comment import CaseClientComment
from app.models.case_document import CaseDocument
from app.models.case_document_version import CaseDocumentVersion
from app.models.case_internal_note import CaseInternalNote
from app.models.case_participant import CaseParticipant
from app.models.case_state_definition import CaseStateDefinition
from app.models.case_timeline_event import CaseTimelineEvent
from app.models.case_workflow_event import CaseWorkflowEvent
from app.models.document_template import DocumentTemplate
from app.models.notary import Notary
from app.models.notary_commercial_activity import NotaryCommercialActivity
from app.models.notary_crm_audit_log import NotaryCrmAuditLog
from app.models.person import Person
from app.models.role import Role
from app.models.template_field import TemplateField
from app.models.template_required_role import TemplateRequiredRole
from app.models.user import User
from app.services.storage import ensure_storage_dirs

BROKEN_TEXT_MARKERS = ("\u00c3", "\u00c2", "\u00e2", "\u0192", "\u2019", "\u201a", "\u00ad", "\ufffd")

COMMON_TEXT_REPAIRS = {
    "Gesti?n": "Gestión",
    "Notar?a": "Notaría",
    "Revisi?n": "Revisión",
    "Bogot?": "Bogotá",
    "C?rculo": "Círculo",
    "Mar?a": "María",
    "Mej?a": "Mejía",
    "Ben?tez": "Benítez",
    "G?mez": "Gómez",
    "Andr?s": "Andrés",
    "Medell?n": "Medellín",
    "D?a": "Día",
    "A?o": "Año",
    "Extensi?n": "Extensión",
    "cuant?a": "cuantía",
    "?tiles": "útiles",
    "ASIGNACI?N": "ASIGNACIÓN",
}


def repair_text(value: str | None) -> str | None:
    if value is None:
        return None
    result = value.strip()
    if not result:
        return result
    if "\\u" in result:
        try:
            result = result.encode("utf-8").decode("unicode_escape")
        except UnicodeError:
            pass
    for broken, fixed in COMMON_TEXT_REPAIRS.items():
        result = result.replace(broken, fixed)
    for _ in range(4):
        if not any(marker in result for marker in BROKEN_TEXT_MARKERS):
            break
        updated = result
        for encoding in ("cp1252", "latin1"):
            try:
                candidate = updated.encode(encoding, errors="ignore").decode("utf-8", errors="ignore")
            except UnicodeError:
                continue
            if candidate and candidate != updated:
                updated = candidate
        if updated == result:
            break
        result = updated
    return result.replace("  ", " ").strip()


def repair_model_strings(db) -> None:
    repairs = {
        Role: ["name", "description"],
        User: ["full_name", "job_title", "phone"],
        Notary: [
            "commercial_name", "legal_name", "city", "department", "municipality",
            "notary_label", "address", "phone", "email", "current_notary_name",
            "business_hours", "commercial_owner", "main_contact_name", "main_contact_title",
            "commercial_phone", "commercial_email", "commercial_notes", "lead_source",
            "potential", "internal_observations", "institutional_data",
        ],
        Case: ["case_type", "act_type", "metadata_json", "internal_case_number", "official_deed_number", "approved_by_role_code"],
        ActCatalog: ["code", "label", "roles_json"],
        CaseAct: ["act_code", "act_label", "roles_json"],
        CaseStateDefinition: ["case_type", "code", "label"],
        DocumentTemplate: ["name", "slug", "case_type", "document_type", "description", "scope_type", "source_filename", "storage_path", "internal_variable_map_json"],
        TemplateRequiredRole: ["role_code", "label"],
        TemplateField: ["field_code", "label", "field_type", "section", "options_json", "placeholder_key", "help_text"],
        Person: ["document_type", "document_number", "full_name", "sex", "nationality", "marital_status", "profession", "municipality", "phone", "address", "email", "metadata_json"],
        CaseParticipant: ["role_code", "role_label", "snapshot_json"],
        CaseActData: ["data_json", "gari_draft_text"],
        CaseClientComment: ["comment"],
        CaseInternalNote: ["note"],
        CaseDocument: ["category", "title"],
        CaseDocumentVersion: ["file_format", "storage_path", "original_filename", "placeholder_snapshot_json"],
        CaseWorkflowEvent: ["actor_role_code", "event_type", "from_state", "to_state", "field_name", "old_value", "new_value", "comment", "metadata_json"],
        NotaryCommercialActivity: ["management_type", "comment", "responsible", "result", "next_action"],
        NotaryCrmAuditLog: ["field_name", "old_value", "new_value", "comment", "event_type"],
    }
    dirty = False
    for model, fields in repairs.items():
        for row in db.query(model).all():
            for field in fields:
                current = getattr(row, field, None)
                repaired = repair_text(current)
                if repaired != current:
                    setattr(row, field, repaired)
                    dirty = True
    if dirty:
        db.commit()


def ensure_notary_columns() -> None:
    inspector = inspect(engine)
    if "notaries" not in inspector.get_table_names():
        return
    existing_columns = {column["name"] for column in inspector.get_columns("notaries")}
    required_columns = {
        "address": "ALTER TABLE notaries ADD COLUMN address VARCHAR(255)",
        "phone": "ALTER TABLE notaries ADD COLUMN phone TEXT",
        "email": "ALTER TABLE notaries ADD COLUMN email VARCHAR(120)",
        "department": "ALTER TABLE notaries ADD COLUMN department VARCHAR(80) DEFAULT 'Antioquia'",
        "municipality": "ALTER TABLE notaries ADD COLUMN municipality VARCHAR(120) DEFAULT ''",
        "notary_label": "ALTER TABLE notaries ADD COLUMN notary_label VARCHAR(160) DEFAULT ''",
        "catalog_identity_key": "ALTER TABLE notaries ADD COLUMN catalog_identity_key VARCHAR(255) DEFAULT ''",
        "current_notary_name": "ALTER TABLE notaries ADD COLUMN current_notary_name VARCHAR(160)",
        "business_hours": "ALTER TABLE notaries ADD COLUMN business_hours TEXT",
        "commercial_status": "ALTER TABLE notaries ADD COLUMN commercial_status VARCHAR(40) DEFAULT 'prospecto'",
        "base_color": "ALTER TABLE notaries ADD COLUMN base_color VARCHAR(20) DEFAULT '#F4F7FB'",
        "commercial_owner": "ALTER TABLE notaries ADD COLUMN commercial_owner VARCHAR(120)",
        "commercial_owner_user_id": "ALTER TABLE notaries ADD COLUMN commercial_owner_user_id INTEGER",
        "main_contact_name": "ALTER TABLE notaries ADD COLUMN main_contact_name VARCHAR(160)",
        "main_contact_title": "ALTER TABLE notaries ADD COLUMN main_contact_title VARCHAR(120)",
        "commercial_phone": "ALTER TABLE notaries ADD COLUMN commercial_phone TEXT",
        "commercial_email": "ALTER TABLE notaries ADD COLUMN commercial_email VARCHAR(120)",
        "last_management_at": "ALTER TABLE notaries ADD COLUMN last_management_at TIMESTAMP",
        "next_management_at": "ALTER TABLE notaries ADD COLUMN next_management_at TIMESTAMP",
        "commercial_notes": "ALTER TABLE notaries ADD COLUMN commercial_notes TEXT",
        "priority": "ALTER TABLE notaries ADD COLUMN priority VARCHAR(20) DEFAULT 'media'",
        "lead_source": "ALTER TABLE notaries ADD COLUMN lead_source VARCHAR(120)",
        "potential": "ALTER TABLE notaries ADD COLUMN potential VARCHAR(40)",
        "internal_observations": "ALTER TABLE notaries ADD COLUMN internal_observations TEXT",
    }
    with engine.begin() as connection:
        for column_name, ddl in required_columns.items():
            if column_name not in existing_columns:
                connection.execute(text(ddl))


def ensure_commercial_activity_columns() -> None:
    inspector = inspect(engine)
    if "notary_commercial_activities" not in inspector.get_table_names():
        return
    existing_columns = {column["name"] for column in inspector.get_columns("notary_commercial_activities")}
    with engine.begin() as connection:
        if "responsible_user_id" not in existing_columns:
            connection.execute(text("ALTER TABLE notary_commercial_activities ADD COLUMN responsible_user_id INTEGER"))


def ensure_case_columns() -> None:
    inspector = inspect(engine)
    if "cases" not in inspector.get_table_names():
        return
    existing_columns = {column["name"] for column in inspector.get_columns("cases")}
    required_columns = {
        "template_id": "ALTER TABLE cases ADD COLUMN template_id INTEGER",
        "created_by_user_id": "ALTER TABLE cases ADD COLUMN created_by_user_id INTEGER",
        "internal_case_number": "ALTER TABLE cases ADD COLUMN internal_case_number VARCHAR(40)",
        "official_deed_number": "ALTER TABLE cases ADD COLUMN official_deed_number VARCHAR(40)",
        "official_deed_year": "ALTER TABLE cases ADD COLUMN official_deed_year INTEGER",
        "approved_at": "ALTER TABLE cases ADD COLUMN approved_at TIMESTAMP",
        "approved_by_user_id": "ALTER TABLE cases ADD COLUMN approved_by_user_id INTEGER",
        "approved_by_role_code": "ALTER TABLE cases ADD COLUMN approved_by_role_code VARCHAR(80)",
        "approved_document_version_id": "ALTER TABLE cases ADD COLUMN approved_document_version_id INTEGER",
    }
    with engine.begin() as connection:
        for column_name, ddl in required_columns.items():
            if column_name not in existing_columns:
                connection.execute(text(ddl))


def ensure_case_act_data_columns() -> None:
    inspector = inspect(engine)
    if "case_act_data" not in inspector.get_table_names():
        return
    existing_columns = {column["name"] for column in inspector.get_columns("case_act_data")}
    with engine.begin() as connection:
        if "gari_draft_text" not in existing_columns:
            connection.execute(text("ALTER TABLE case_act_data ADD COLUMN gari_draft_text TEXT"))


def ensure_case_participant_columns() -> None:
    inspector = inspect(engine)
    if "case_participants" not in inspector.get_table_names():
        return
    existing_columns = {column["name"] for column in inspector.get_columns("case_participants")}
    with engine.begin() as connection:
        if "legal_entity_id" not in existing_columns:
            connection.execute(text("ALTER TABLE case_participants ADD COLUMN legal_entity_id INTEGER"))
    # Refresh metadata after the optional ALTER TABLE so downstream checks see the new column.
    inspector = inspect(engine)
    indexes = {index["name"] for index in inspector.get_indexes("case_participants")}
    if "ix_case_participants_legal_entity_id" not in indexes:
        with engine.begin() as connection:
            connection.execute(text("CREATE INDEX ix_case_participants_legal_entity_id ON case_participants (legal_entity_id)"))
    foreign_keys = {fk.get("name") for fk in inspector.get_foreign_keys("case_participants")}
    if "fk_case_participants_legal_entity_id" not in foreign_keys:
        with engine.begin() as connection:
            connection.execute(text(
                "ALTER TABLE case_participants "
                "ADD CONSTRAINT fk_case_participants_legal_entity_id "
                "FOREIGN KEY (legal_entity_id) REFERENCES legal_entities (id)"
            ))


def init_db() -> None:
    ensure_storage_dirs()
    Base.metadata.create_all(bind=engine)
    ensure_notary_columns()
    ensure_commercial_activity_columns()
    ensure_case_columns()
    ensure_case_act_data_columns()
    ensure_case_participant_columns()
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        from app.models.role import Role
        role_count = db.query(Role).count()
        if role_count == 0:
            seed_database(db)
        repair_model_strings(db)
    finally:
        db.close()
```

## File: app/db/seed.py
```python
from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import or_, text
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.case import Case
from app.models.case_act_data import CaseActData
from app.models.case_document import CaseDocument
from app.models.case_document_version import CaseDocumentVersion
from app.models.case_participant import CaseParticipant
from app.models.case_state_definition import CaseStateDefinition
from app.models.case_timeline_event import CaseTimelineEvent
from app.models.case_workflow_event import CaseWorkflowEvent
from app.models.document_template import DocumentTemplate
from app.models.notary import Notary
from app.models.notary_commercial_activity import NotaryCommercialActivity
from app.models.numbering_sequence import NumberingSequence
from app.models.person import Person
from app.models.role import Role
from app.models.role_assignment import RoleAssignment
from app.models.template_field import TemplateField
from app.models.template_required_role import TemplateRequiredRole
from app.models.user import User
from app.seeds.seed_act_catalog import seed_act_catalog
from app.modules.notaries.router import build_catalog_identity_key
from app.services.document_generation import build_case_text_snapshot, generate_plain_pdf, render_docx_template, serialize_placeholder_snapshot
from app.services.storage import copy_template_file, next_case_file_path, template_file_path

ROLE_DEFINITIONS = [
    ("super_admin", "SuperAdmin", "global", "Gestión global de la plataforma"),
    ("admin_notary", "Admin Notaría", "notary", "Gestión administrativa de la notaría"),
    ("notary", "Notario", "notary", "Firma y validación notarial"),
    ("approver", "Aprobador", "notary", "Revisión y aprobación documental"),
    ("protocolist", "Protocolista", "notary", "Gestión protocolaria y radicación"),
    ("client", "Cliente", "notary", "Consulta y seguimiento del caso"),
]

CASE_STATE_DEFINITIONS = [
    ("escritura", "borrador", "Borrador", 1, True, False),
    ("escritura", "en_diligenciamiento", "En diligenciamiento", 2, False, False),
    ("escritura", "revision_cliente", "Revisión cliente", 3, False, False),
    ("escritura", "ajustes_solicitados", "Ajustes solicitados", 4, False, False),
    ("escritura", "revision_aprobador", "Revisión aprobador", 5, False, False),
    ("escritura", "devuelto_aprobador", "Devuelto aprobador", 6, False, False),
    ("escritura", "revision_notario", "Revisión notario", 7, False, False),
    ("escritura", "rechazado_notario", "Rechazado notario", 8, False, False),
    ("escritura", "aprobado_notario", "Aprobado notario", 9, False, False),
    ("escritura", "generado", "Generado", 10, False, False),
    ("escritura", "firmado_cargado", "Firmado cargado", 11, False, False),
    ("escritura", "cerrado", "Cerrado", 12, False, True),
]

SEED_USERS = [
    {"email": "superadmin@easypro.co", "full_name": "Super Administrador", "job_title": "SuperAdmin", "roles": [("super_admin", None)]},
    {"email": "admin@notaria75.co", "full_name": "Laura Benítez", "job_title": "Admin Notaría", "roles": [("admin_notary", "seed")]},
    {"email": "notario@notaria75.co", "full_name": "Dr. Roberto Valenzuela", "job_title": "Notario Titular", "roles": [("notary", "seed")]},
    {"email": "aprobador@notaria75.co", "full_name": "Ana María Torres", "job_title": "Aprobadora", "roles": [("approver", "seed")]},
    {"email": "protocolista@notaria75.co", "full_name": "Carlos Mejía", "job_title": "Protocolista", "roles": [("protocolist", "seed")]},
    {"email": "cliente@notaria75.co", "full_name": "Juliana Pardo", "job_title": "Cliente Corporativo", "roles": [("client", "seed")]},
    {"email": "laura.restrepo@easypro.co", "full_name": "Laura Restrepo", "job_title": "Coordinadora Comercial", "roles": []},
    {"email": "equipo.easypro@easypro.co", "full_name": "Equipo EasyPro", "job_title": "Mesa Comercial", "roles": []},
]

POWER_GENERAL_VARIABLE_MAP = {
    "NOMBRE_PODERDANTE": "participants.poderdante.full_name",
    "TIPO_DOCUMENTO_PODERDANTE": "participants.poderdante.document_type",
    "NUMERO_DOCUMENTO_PODERDANTE": "participants.poderdante.document_number",
    "NACIONALIDAD_PODERDANTE": "participants.poderdante.nationality",
    "ESTADO_CIVIL_PODERDANTE": "participants.poderdante.marital_status",
    "PROFESION_U_OFICIO_PODERDANTE": "participants.poderdante.profession",
    "MUNICIPIO_DE_DOMICILIO_PODERDANTE": "participants.poderdante.municipality",
    "SELECCIONE_SI_PODERDANTE_ESTA_DE_TRANSITO": "participants.poderdante.is_transient",
    "TELEFONO_PODERDANTE": "participants.poderdante.phone",
    "DIRECCION_PODERDANTE": "participants.poderdante.address",
    "EMAIL_PODERDANTE": "participants.poderdante.email",
    "PODERDANTE_ES_HOMBRE_O_MUJER": "participants.poderdante.sex_label",
    "NOMBRE_APODERADO": "participants.apoderado.full_name",
    "NUMERO_DOCUMENTO_APODERADO": "participants.apoderado.document_number",
    "NACIONALIDAD_APODERADO": "participants.apoderado.nationality",
    "ESTADO_CIVIL_APODERADO": "participants.apoderado.marital_status",
    "PROFESION_U_OFICIO_APODERADO": "participants.apoderado.profession",
    "MUNICIPIO_DE_DOMICILIO_APODERADO": "participants.apoderado.municipality",
    "SELECCIONE_SI_APODERADO_ESTA_DE_TRANSITO": "participants.apoderado.is_transient",
    "TELEFONO_APODERADO": "participants.apoderado.phone",
    "DIRECCION_APODERADO": "participants.apoderado.address",
    "EMAIL_APODERADO": "participants.apoderado.email",
    "APODERADO_ES_HOMBRE_O_MUJER": "participants.apoderado.sex_label",
    "DIA_ELABORACION_ESCRITURA": "act.dia_elaboracion",
    "MES_ELABORACION_ESCRITURA": "act.mes_elaboracion",
    "ANO_ELABORACION_ESCRITURA": "act.ano_elaboracion",
    "DERECHOS_NOTARIALES": "act.derechos_notariales",
    "IVA": "act.iva",
    "APORTE_SUPERINTENDENCIA": "act.aporte_superintendencia",
    "FONDO_NOTARIADO": "act.fondo_notariado",
    "CONSECUTIVOS_HOJAS_PAPEL_NOTARIAL": "act.consecutivos_hojas_papel_notarial",
    "EXTENSION": "act.extension",
    "NUMERO_ESCRITURA": "case.official_deed_number",
}

POWER_GENERAL_FIELDS = [
    ("dia_elaboracion", "Día elaboración", "number", "acto", True, None, "DIA_ELABORACION_ESCRITURA", 1),
    ("mes_elaboracion", "Mes elaboración", "text", "acto", True, None, "MES_ELABORACION_ESCRITURA", 2),
    ("ano_elaboracion", "Año elaboración", "number", "acto", True, None, "ANO_ELABORACION_ESCRITURA", 3),
    ("derechos_notariales", "Derechos notariales", "currency", "acto", True, None, "DERECHOS_NOTARIALES", 4),
    ("iva", "IVA", "currency", "acto", True, None, "IVA", 5),
    ("aporte_superintendencia", "Aporte superintendencia", "currency", "acto", True, None, "APORTE_SUPERINTENDENCIA", 6),
    ("fondo_notariado", "Fondo notariado", "currency", "acto", True, None, "FONDO_NOTARIADO", 7),
    ("consecutivos_hojas_papel_notarial", "Consecutivos hojas papel notarial", "text", "acto", True, None, "CONSECUTIVOS_HOJAS_PAPEL_NOTARIAL", 8),
    ("extension", "Extensión", "text", "acto", True, None, "EXTENSION", 9),
    ("clase_cuantia_acto", "Clase o cuantía del acto", "text", "acto", False, None, None, 10),
]

PERSON_BLUEPRINTS = [
    {
        "document_type": "CC",
        "document_number": "43123456",
        "full_name": "Marta Cecilia Restrepo Gómez",
        "sex": "F",
        "nationality": "Colombiana",
        "marital_status": "Casado(a)",
        "profession": "Comerciante",
        "municipality": "Caldas",
        "is_transient": False,
        "phone": "3001234567",
        "address": "Carrera 49 # 128 Sur 34",
        "email": "marta.restrepo@example.com",
        "metadata_json": json.dumps({"source": "seed"}, ensure_ascii=False),
    },
    {
        "document_type": "CC",
        "document_number": "1037654321",
        "full_name": "Andrés Felipe Toro Valencia",
        "sex": "M",
        "nationality": "Colombiana",
        "marital_status": "Soltero(a)",
        "profession": "Abogado",
        "municipality": "Medellín",
        "is_transient": True,
        "phone": "3117654321",
        "address": "Calle 10 # 38-45",
        "email": "andres.toro@example.com",
        "metadata_json": json.dumps({"source": "seed"}, ensure_ascii=False),
    },
]


def upsert_person(db: Session, payload: dict) -> Person:
    person = db.query(Person).filter(Person.document_type == payload["document_type"], Person.document_number == payload["document_number"]).first()
    if person is None:
        person = Person(**payload)
        db.add(person)
        db.flush()
    else:
        for key, value in payload.items():
            setattr(person, key, value)
    return person


def ensure_power_general_template(db: Session, notary: Notary | None) -> DocumentTemplate | None:
    source_path = template_file_path("poder-general.docx")
    if not source_path.exists():
        return None

    template = db.query(DocumentTemplate).filter(DocumentTemplate.slug == "poder-general").first()
    if template is None:
        template = DocumentTemplate(
            name="Poder General",
            slug="poder-general",
            case_type="escritura",
            document_type="Poder General",
            description="Plantilla real de escritura pública tipo Poder General para el MVP documental.",
            scope_type="global",
            notary_id=notary.id if notary else None,
            is_active=True,
            internal_variable_map_json=json.dumps(POWER_GENERAL_VARIABLE_MAP, ensure_ascii=False),
        )
        db.add(template)
        db.flush()

    filename, storage_path = copy_template_file(source_path, template.slug)
    template.source_filename = filename
    template.storage_path = storage_path
    template.name = "Poder General"
    template.case_type = "escritura"
    template.document_type = "Poder General"
    template.description = "Plantilla real de escritura pública tipo Poder General para el MVP documental."
    template.scope_type = "global"
    template.notary_id = notary.id if notary else template.notary_id
    template.is_active = True
    template.internal_variable_map_json = json.dumps(POWER_GENERAL_VARIABLE_MAP, ensure_ascii=False)
    db.commit()

    db.query(TemplateRequiredRole).filter(TemplateRequiredRole.template_id == template.id).delete(synchronize_session=False)
    db.query(TemplateField).filter(TemplateField.template_id == template.id).delete(synchronize_session=False)
    db.flush()

    db.add_all([
        TemplateRequiredRole(template_id=template.id, role_code="poderdante", label="Poderdante", is_required=True, step_order=1),
        TemplateRequiredRole(template_id=template.id, role_code="apoderado", label="Apoderado(a)", is_required=True, step_order=2),
    ])

    for field_code, label, field_type, section, is_required, options_json, placeholder_key, step_order in POWER_GENERAL_FIELDS:
        db.add(
            TemplateField(
                template_id=template.id,
                field_code=field_code,
                label=label,
                field_type=field_type,
                section=section,
                is_required=is_required,
                options_json=options_json,
                placeholder_key=placeholder_key,
                help_text=None,
                step_order=step_order,
            )
        )
    db.commit()
    db.refresh(template)
    return template


def ensure_compraventa_vis_template(db: Session, notary: Notary | None) -> DocumentTemplate:
    template = db.query(DocumentTemplate).filter(DocumentTemplate.slug == "compraventa-vis").first()
    if template is None:
        template = DocumentTemplate(
            name="Compraventa VIS",
            slug="compraventa-vis",
            case_type="escritura",
            document_type="Compraventa de Interés Social",
            description="Escritura pública de compraventa VIS — proyectos ARAGUA y JAGGUA — Constructora Contex",
            scope_type="global",
            notary_id=notary.id if notary else None,
            is_active=True,
        )
        db.add(template)
        db.flush()

    template.name = "Compraventa VIS"
    template.case_type = "escritura"
    template.document_type = "Compraventa de Interés Social"
    template.description = "Escritura pública de compraventa VIS — proyectos ARAGUA y JAGGUA — Constructora Contex"
    template.scope_type = "global"
    template.notary_id = notary.id if notary else template.notary_id
    template.is_active = True
    db.commit()

    db.query(TemplateRequiredRole).filter(TemplateRequiredRole.template_id == template.id).delete(synchronize_session=False)
    db.query(TemplateField).filter(TemplateField.template_id == template.id).delete(synchronize_session=False)
    db.flush()

    db.add_all([
        TemplateRequiredRole(template_id=template.id, role_code="comprador_1", label="Comprador(a) 1", is_required=True, step_order=1),
        TemplateRequiredRole(template_id=template.id, role_code="comprador_2", label="Comprador(a) 2", is_required=False, step_order=2),
        TemplateRequiredRole(template_id=template.id, role_code="comprador_3", label="Comprador(a) 3", is_required=False, step_order=3),
        TemplateRequiredRole(template_id=template.id, role_code="apoderado_fideicomiso", label="Apoderado(a) Fideicomiso", is_required=True, step_order=4),
        TemplateRequiredRole(template_id=template.id, role_code="apoderado_fideicomitente", label="Apoderado(a) Fideicomitente", is_required=True, step_order=5),
        TemplateRequiredRole(template_id=template.id, role_code="apoderado_banco_libera", label="Apoderado(a) banco que libera", is_required=True, step_order=6),
        TemplateRequiredRole(template_id=template.id, role_code="apoderado_banco_hipoteca", label="Apoderado(a) banco hipotecante", is_required=False, step_order=7),
    ])

    db.add_all([
        TemplateField(template_id=template.id, field_code="proyecto", label="Proyecto", field_type="select", section="acto", is_required=True, options_json=json.dumps(["aragua", "jaggua"], ensure_ascii=False), step_order=1),
        TemplateField(template_id=template.id, field_code="tipo_inmueble", label="Tipo de inmueble", field_type="select", section="acto", is_required=True, options_json=json.dumps(["apartamento", "parqueadero"], ensure_ascii=False), step_order=2),
        TemplateField(template_id=template.id, field_code="banco_hipotecante", label="Banco hipotecante", field_type="select", section="acto", is_required=False, options_json=json.dumps(["fna", "bogota", "davivienda"], ensure_ascii=False), step_order=3),
        TemplateField(template_id=template.id, field_code="numero_apartamento", label="Número apartamento/parqueadero", field_type="text", section="acto", is_required=True, step_order=4),
        TemplateField(template_id=template.id, field_code="matricula_inmobiliaria", label="Matrícula inmobiliaria", field_type="text", section="acto", is_required=True, step_order=5),
        TemplateField(template_id=template.id, field_code="cedula_catastral", label="Cédula catastral", field_type="text", section="acto", is_required=True, step_order=6),
        TemplateField(template_id=template.id, field_code="linderos", label="Linderos del inmueble", field_type="textarea", section="acto", is_required=True, step_order=7),
        TemplateField(template_id=template.id, field_code="numero_piso", label="Número de piso", field_type="text", section="acto", is_required=False, step_order=8),
        TemplateField(template_id=template.id, field_code="area_privada", label="Área privada (m²)", field_type="number", section="acto", is_required=True, step_order=9),
        TemplateField(template_id=template.id, field_code="area_total", label="Área total (m²)", field_type="number", section="acto", is_required=False, step_order=10),
        TemplateField(template_id=template.id, field_code="altura", label="Altura (m)", field_type="number", section="acto", is_required=False, step_order=11),
        TemplateField(template_id=template.id, field_code="coeficiente_copropiedad", label="Coeficiente copropiedad (%)", field_type="number", section="acto", is_required=True, step_order=12),
        TemplateField(template_id=template.id, field_code="avaluo_catastral", label="Avalúo catastral ($)", field_type="number", section="acto", is_required=True, step_order=13),
        TemplateField(template_id=template.id, field_code="valor_venta", label="Valor de la venta ($)", field_type="number", section="acto", is_required=True, step_order=14),
        TemplateField(template_id=template.id, field_code="valor_venta_letras", label="Valor en letras", field_type="text", section="acto", is_required=True, step_order=15),
        TemplateField(template_id=template.id, field_code="cuota_inicial", label="Cuota inicial ($)", field_type="number", section="acto", is_required=False, step_order=16),
        TemplateField(template_id=template.id, field_code="cuota_inicial_letras", label="Cuota inicial en letras", field_type="text", section="acto", is_required=False, step_order=17),
        TemplateField(template_id=template.id, field_code="valor_hipoteca", label="Valor hipoteca ($)", field_type="number", section="acto", is_required=False, step_order=18),
        TemplateField(template_id=template.id, field_code="valor_hipoteca_letras", label="Valor hipoteca en letras", field_type="text", section="acto", is_required=False, step_order=19),
        TemplateField(template_id=template.id, field_code="origen_cuota_inicial", label="Origen cuota inicial", field_type="text", section="acto", is_required=False, step_order=20),
        TemplateField(template_id=template.id, field_code="fecha_promesa_compraventa", label="Fecha promesa compraventa", field_type="text", section="acto", is_required=True, step_order=21),
        TemplateField(template_id=template.id, field_code="inmueble_sera_casa_habitacion", label="¿Será casa de habitación?", field_type="select", section="acto", is_required=True, options_json=json.dumps(["SI", "NO"], ensure_ascii=False), step_order=22),
        TemplateField(template_id=template.id, field_code="tiene_bien_afectado", label="¿Tiene otro bien afectado?", field_type="select", section="acto", is_required=True, options_json=json.dumps(["SI", "NO"], ensure_ascii=False), step_order=23),
        TemplateField(template_id=template.id, field_code="paz_salvo_predial_numero", label="Paz y salvo predial N°", field_type="text", section="acto", is_required=True, step_order=24),
        TemplateField(template_id=template.id, field_code="paz_salvo_predial_fecha", label="Fecha paz y salvo", field_type="text", section="acto", is_required=True, step_order=25),
        TemplateField(template_id=template.id, field_code="paz_salvo_predial_vigencia", label="Vigencia paz y salvo", field_type="text", section="acto", is_required=True, step_order=26),
        TemplateField(template_id=template.id, field_code="dia_elaboracion", label="Día elaboración escritura", field_type="text", section="acto", is_required=True, step_order=27),
        TemplateField(template_id=template.id, field_code="mes_elaboracion", label="Mes elaboración escritura", field_type="text", section="acto", is_required=True, step_order=28),
        TemplateField(template_id=template.id, field_code="ano_elaboracion", label="Año elaboración escritura", field_type="number", section="acto", is_required=True, step_order=29),
    ])
    db.commit()
    db.refresh(template)
    return template


def seed_database(db: Session) -> None:
    role_map = {role.code: role for role in db.query(Role).all()}
    for code, name, scope, description in ROLE_DEFINITIONS:
        role = role_map.get(code)
        if role is None:
            role = Role(code=code, name=name, scope=scope, description=description)
            db.add(role)
        else:
            role.name = name
            role.scope = scope
            role.description = description
    db.commit()
    role_map = {role.code: role for role in db.query(Role).all()}

    existing_states = {(item.case_type, item.code): item for item in db.query(CaseStateDefinition).all()}
    for case_type, code, label, step_order, is_initial, is_terminal in CASE_STATE_DEFINITIONS:
        item = existing_states.get((case_type, code))
        if item is None:
            db.add(CaseStateDefinition(case_type=case_type, code=code, label=label, step_order=step_order, is_initial=is_initial, is_terminal=is_terminal, is_active=True))
        else:
            item.label = label
            item.step_order = step_order
            item.is_initial = is_initial
            item.is_terminal = is_terminal
            item.is_active = True
    db.commit()

    seed_email = "contacto@notaria75.co"
    catalog_identity_key = build_catalog_identity_key("Bogotá D.C.", "EasyPro Notarial Bogotá", seed_email)
    notary = db.query(Notary).filter(or_(Notary.catalog_identity_key == catalog_identity_key, Notary.email == seed_email, Notary.slug == "bogota-d-c-easypro-notarial-bogota")).first()
    if notary is None:
        notary = Notary(
            slug="bogota-d-c-easypro-notarial-bogota",
            catalog_identity_key=catalog_identity_key,
            commercial_name="EasyPro Notarial Bogotá",
            legal_name="Notaría 75 del Círculo de Bogotá",
            department="Antioquia",
            municipality="Bogotá D.C.",
            notary_label="EasyPro Notarial Bogotá",
            primary_color="#0D2E5D",
            secondary_color="#4D5B7C",
            base_color="#F4F7FB",
            accent_color="#50D690",
            city="Bogotá D.C.",
            address="Calle 100 # 10-20",
            phone="+57 601 0000000",
            email=seed_email,
            current_notary_name="Dr. Roberto Valenzuela",
            business_hours="L-V 8:00 a. m. - 5:00 p. m.",
            institutional_data="NIT 900000000-1 | Horario L-V 8:00 a. m. - 5:00 p. m.",
            commercial_status="prospecto",
            commercial_owner="Laura Benítez",
            main_contact_name="Laura Benítez",
            main_contact_title="Administradora",
            commercial_phone="+57 310 0000000",
            commercial_email="crm@easypro.co",
            commercial_notes="Registro semilla para validar catálogo y CRM comercial.",
            priority="media",
            lead_source="Base inicial",
            potential="alto",
            internal_observations="Mantener como notaría demo del sistema.",
            is_active=True,
        )
        db.add(notary)
        db.commit()
        db.refresh(notary)
    else:
        notary.catalog_identity_key = catalog_identity_key
        notary.commercial_name = "EasyPro Notarial Bogotá"
        notary.legal_name = "Notaría 75 del Círculo de Bogotá"
        notary.department = notary.department or "Antioquia"
        notary.municipality = notary.municipality or "Bogotá D.C."
        notary.notary_label = notary.notary_label or "EasyPro Notarial Bogotá"
        notary.city = notary.city or "Bogotá D.C."
        notary.address = notary.address or "Calle 100 # 10-20"
        notary.phone = notary.phone or "+57 601 0000000"
        notary.email = notary.email or seed_email
        notary.base_color = notary.base_color or "#F4F7FB"
        notary.current_notary_name = notary.current_notary_name or "Dr. Roberto Valenzuela"
        notary.business_hours = notary.business_hours or "L-V 8:00 a. m. - 5:00 p. m."
        notary.commercial_status = notary.commercial_status or "prospecto"
        notary.commercial_owner = notary.commercial_owner or "Laura Benítez"
        notary.priority = notary.priority or "media"
        db.commit()

    persisted_users: dict[str, User] = {}
    for user_data in SEED_USERS:
        user = db.query(User).filter(User.email == user_data["email"]).first()
        if user is None:
            user = User(
                email=user_data["email"],
                full_name=user_data["full_name"],
                password_hash=get_password_hash("ChangeMe123!"),
                job_title=user_data["job_title"],
                default_notary_id=notary.id,
                is_active=True,
            )
            db.add(user)
            db.flush()
        else:
            user.full_name = user_data["full_name"]
            user.job_title = user_data["job_title"]
            user.is_active = True
            user.default_notary_id = user.default_notary_id or notary.id
        persisted_users[user.email] = user
    db.commit()

    for user_data in SEED_USERS:
        user = persisted_users[user_data["email"]]
        db.query(RoleAssignment).filter(RoleAssignment.user_id == user.id).delete(synchronize_session=False)
        for role_code, notary_scope in user_data["roles"]:
            db.add(RoleAssignment(user_id=user.id, role_id=role_map[role_code].id, notary_id=notary.id if notary_scope == "seed" else None))
    db.commit()

    owner_map = {user.full_name: user.id for user in db.query(User).all()}
    for persisted_notary in db.query(Notary).all():
        if persisted_notary.commercial_owner in owner_map:
            persisted_notary.commercial_owner_user_id = owner_map[persisted_notary.commercial_owner]
    for activity in db.query(NotaryCommercialActivity).all():
        if activity.responsible in owner_map:
            activity.responsible_user_id = owner_map[activity.responsible]
    db.commit()

    seed_act_catalog(db)

    template = ensure_power_general_template(db, notary)

    people = {payload["document_number"]: upsert_person(db, payload) for payload in PERSON_BLUEPRINTS}
    db.commit()

    power_case = None
    pilot_notary = db.query(Notary).filter(Notary.department == "Antioquia", Notary.municipality == "Caldas").order_by(Notary.id.asc()).first()
    if template is not None and pilot_notary is not None:
        internal_case_number = "CAS-2026-0001"
        power_case = db.query(Case).filter(Case.internal_case_number == internal_case_number).first()
        if power_case is None:
            power_case = Case(
                notary_id=pilot_notary.id,
                template_id=template.id,
                created_by_user_id=persisted_users["protocolista@notaria75.co"].id,
                case_type="escritura",
                act_type="Poder General",
                consecutive=1,
                year=2026,
                internal_case_number=internal_case_number,
                current_state="generado",
                current_owner_user_id=persisted_users["protocolista@notaria75.co"].id,
                client_user_id=persisted_users["cliente@notaria75.co"].id,
                protocolist_user_id=persisted_users["protocolista@notaria75.co"].id,
                approver_user_id=persisted_users["aprobador@notaria75.co"].id,
                titular_notary_user_id=persisted_users["notario@notaria75.co"].id,
                substitute_notary_user_id=persisted_users["admin@notaria75.co"].id,
                requires_client_review=True,
                final_signed_uploaded=False,
                metadata_json=json.dumps({"radication": "CAL-PG-2026-0001", "pilot": "Caldas Antioquia"}, ensure_ascii=False),
            )
            db.add(power_case)
            db.flush()
        else:
            power_case.template_id = template.id
            power_case.notary_id = pilot_notary.id
            power_case.created_by_user_id = persisted_users["protocolista@notaria75.co"].id
            power_case.act_type = "Poder General"
            power_case.current_state = "generado"
            power_case.current_owner_user_id = persisted_users["protocolista@notaria75.co"].id
            power_case.client_user_id = persisted_users["cliente@notaria75.co"].id
            power_case.protocolist_user_id = persisted_users["protocolista@notaria75.co"].id
            power_case.approver_user_id = persisted_users["aprobador@notaria75.co"].id
            power_case.titular_notary_user_id = persisted_users["notario@notaria75.co"].id
            power_case.substitute_notary_user_id = persisted_users["admin@notaria75.co"].id
            power_case.requires_client_review = True
            power_case.metadata_json = json.dumps({"radication": "CAL-PG-2026-0001", "pilot": "Caldas Antioquia"}, ensure_ascii=False)
        db.commit()

        db.query(CaseParticipant).filter(CaseParticipant.case_id == power_case.id).delete(synchronize_session=False)
        db.add(CaseParticipant(case_id=power_case.id, person_id=people["43123456"].id, role_code="poderdante", role_label="Poderdante", snapshot_json=json.dumps(PERSON_BLUEPRINTS[0], ensure_ascii=False)))
        db.add(CaseParticipant(case_id=power_case.id, person_id=people["1037654321"].id, role_code="apoderado", role_label="Apoderado(a)", snapshot_json=json.dumps(PERSON_BLUEPRINTS[1], ensure_ascii=False)))

        act_payload = {
            "dia_elaboracion": 23,
            "mes_elaboracion": "marzo",
            "ano_elaboracion": 2026,
            "derechos_notariales": 185000,
            "iva": 35150,
            "aporte_superintendencia": 6500,
            "fondo_notariado": 5200,
            "consecutivos_hojas_papel_notarial": "PG-12001 a PG-12003",
            "extension": "Tres hojas útiles",
            "clase_cuantia_acto": "Sin cuantía",
        }
        act_data = db.query(CaseActData).filter(CaseActData.case_id == power_case.id).first()
        if act_data is None:
            act_data = CaseActData(case_id=power_case.id, data_json=json.dumps(act_payload, ensure_ascii=False))
            db.add(act_data)
        else:
            act_data.data_json = json.dumps(act_payload, ensure_ascii=False)
        db.commit()

        db.query(NumberingSequence).filter(NumberingSequence.notary_id == pilot_notary.id, NumberingSequence.year == 2026).delete(synchronize_session=False)
        db.add(NumberingSequence(sequence_type="internal_case", notary_id=pilot_notary.id, year=2026, current_value=1))
        db.add(NumberingSequence(sequence_type="official_deed", notary_id=pilot_notary.id, year=2026, current_value=0))
        db.commit()

        if db.query(CaseTimelineEvent).filter(CaseTimelineEvent.case_id == power_case.id).count() == 0:
            db.add(CaseTimelineEvent(case_id=power_case.id, actor_user_id=persisted_users["protocolista@notaria75.co"].id, event_type="case_created", from_state=None, to_state="borrador", comment="Caso creado desde plantilla Poder General", metadata_json=json.dumps({"source": "seed"}, ensure_ascii=False)))
            db.add(CaseTimelineEvent(case_id=power_case.id, actor_user_id=persisted_users["protocolista@notaria75.co"].id, event_type="draft_generated", from_state="en_diligenciamiento", to_state="generado", comment="Borrador inicial generado", metadata_json=json.dumps({"source": "seed"}, ensure_ascii=False)))
        if db.query(CaseWorkflowEvent).filter(CaseWorkflowEvent.case_id == power_case.id).count() == 0:
            db.add(CaseWorkflowEvent(case_id=power_case.id, actor_user_id=persisted_users["protocolista@notaria75.co"].id, actor_role_code="protocolist", event_type="participants_saved", comment="Intervinientes iniciales registrados", metadata_json=json.dumps({"source": "seed"}, ensure_ascii=False)))
            db.add(CaseWorkflowEvent(case_id=power_case.id, actor_user_id=persisted_users["protocolista@notaria75.co"].id, actor_role_code="protocolist", event_type="act_data_saved", comment="Datos del acto iniciales registrados", metadata_json=json.dumps({"source": "seed"}, ensure_ascii=False)))
        db.commit()

        if template.storage_path:
            participants = [
                {"role_label": "Poderdante", **PERSON_BLUEPRINTS[0]},
                {"role_label": "Apoderado(a)", **PERSON_BLUEPRINTS[1]},
            ]
            replacements = {
                "{{NOMBRE_PODERDANTE}}": PERSON_BLUEPRINTS[0]["full_name"],
                "{{TIPO_DOCUMENTO_PODERDANTE}}": PERSON_BLUEPRINTS[0]["document_type"],
                "{{NUMERO_DOCUMENTO_PODERDANTE}}": PERSON_BLUEPRINTS[0]["document_number"],
                "{{NACIONALIDAD_PODERDANTE}}": PERSON_BLUEPRINTS[0]["nationality"],
                "{{ESTADO_CIVIL_PODERDANTE}}": PERSON_BLUEPRINTS[0]["marital_status"],
                "{{PROFESION_U_OFICIO_PODERDANTE}}": PERSON_BLUEPRINTS[0]["profession"],
                "{{MUNICIPIO_DE_DOMICILIO_PODERDANTE}}": PERSON_BLUEPRINTS[0]["municipality"],
                "{{SELECCIONE_SI_PODERDANTE_ESTA_DE_TRANSITO}}": "NO",
                "{{TELEFONO_PODERDANTE}}": PERSON_BLUEPRINTS[0]["phone"],
                "{{DIRECCION_PODERDANTE}}": PERSON_BLUEPRINTS[0]["address"],
                "{{EMAIL_PODERDANTE}}": PERSON_BLUEPRINTS[0]["email"],
                "{{PODERDANTE_ES_HOMBRE_O_MUJER}}": "mujer",
                "{{NOMBRE_APODERADO}}": PERSON_BLUEPRINTS[1]["full_name"],
                "{{NUMERO_DOCUMENTO_APODERADO}}": PERSON_BLUEPRINTS[1]["document_number"],
                "{{NACIONALIDAD_APODERADO}}": PERSON_BLUEPRINTS[1]["nationality"],
                "{{ESTADO_CIVIL_APODERADO}}": PERSON_BLUEPRINTS[1]["marital_status"],
                "{{PROFESION_U_OFICIO_APODERADO}}": PERSON_BLUEPRINTS[1]["profession"],
                "{{MUNICIPIO_DE_DOMICILIO_APODERADO}}": PERSON_BLUEPRINTS[1]["municipality"],
                "{{SELECCIONE_SI_APODERADO_ESTA_DE_TRANSITO}}": "SI",
                "{{TELEFONO_APODERADO}}": PERSON_BLUEPRINTS[1]["phone"],
                "{{DIRECCION_APODERADO}}": PERSON_BLUEPRINTS[1]["address"],
                "{{EMAIL_APODERADO}}": PERSON_BLUEPRINTS[1]["email"],
                "{{APODERADO_ES_HOMBRE_O_MUJER}}": "hombre",
                "{{DIA_ELABORACION_ESCRITURA}}": str(act_payload["dia_elaboracion"]),
                "{{MES_ELABORACION_ESCRITURA}}": act_payload["mes_elaboracion"],
                "{{ANO_ELABORACION_ESCRITURA}}": str(act_payload["ano_elaboracion"]),
                "{{DERECHOS_NOTARIALES}}": f"${act_payload['derechos_notariales']:,}".replace(",", "."),
                "{{IVA}}": f"${act_payload['iva']:,}".replace(",", "."),
                "{{APORTE_SUPERINTENDENCIA}}": f"${act_payload['aporte_superintendencia']:,}".replace(",", "."),
                "{{FONDO_NOTARIADO}}": f"${act_payload['fondo_notariado']:,}".replace(",", "."),
                "{{CONSECUTIVOS_HOJAS_PAPEL_NOTARIAL}}": act_payload["consecutivos_hojas_papel_notarial"],
                "{{EXTENSION}}": act_payload["extension"],
                "{{NUMERO_ESCRITURA}}": "PENDIENTE ASIGNACIÓN",
            }
            draft_doc = db.query(CaseDocument).filter(CaseDocument.case_id == power_case.id, CaseDocument.category == "draft").first()
            if draft_doc is None:
                draft_doc = CaseDocument(case_id=power_case.id, category="draft", title="Borrador documental", current_version_number=0)
                db.add(draft_doc)
                db.flush()
            if db.query(CaseDocumentVersion).filter(CaseDocumentVersion.case_document_id == draft_doc.id).count() == 0:
                version_number = 1
                docx_path = next_case_file_path(power_case.id, "draft", version_number, "docx", f"poder_general_v{version_number}.docx")
                pdf_path = next_case_file_path(power_case.id, "export_pdf", version_number, "pdf", f"poder_general_v{version_number}.pdf")
                render_docx_template(template.storage_path, docx_path, replacements)
                generate_plain_pdf(pdf_path, "Poder General", build_case_text_snapshot(power_case.internal_case_number or "CAS-2026-0001", power_case.act_type, participants, act_payload))
                draft_doc.current_version_number = 1
                db.add(CaseDocumentVersion(case_document_id=draft_doc.id, version_number=1, file_format="docx", storage_path=str(docx_path), original_filename=docx_path.name, generated_from_template_id=template.id, placeholder_snapshot_json=serialize_placeholder_snapshot(replacements), created_by_user_id=persisted_users["protocolista@notaria75.co"].id))
                export_pdf_doc = db.query(CaseDocument).filter(CaseDocument.case_id == power_case.id, CaseDocument.category == "export_pdf").first()
                if export_pdf_doc is None:
                    export_pdf_doc = CaseDocument(case_id=power_case.id, category="export_pdf", title="Exportación PDF", current_version_number=0)
                    db.add(export_pdf_doc)
                    db.flush()
                export_pdf_doc.current_version_number = 1
                db.add(CaseDocumentVersion(case_document_id=export_pdf_doc.id, version_number=1, file_format="pdf", storage_path=str(pdf_path), original_filename=pdf_path.name, generated_from_template_id=template.id, placeholder_snapshot_json=serialize_placeholder_snapshot(replacements), created_by_user_id=persisted_users["protocolista@notaria75.co"].id))
                db.add(CaseWorkflowEvent(case_id=power_case.id, actor_user_id=persisted_users["protocolista@notaria75.co"].id, actor_role_code="protocolist", event_type="draft_generated", comment="Borrador documental versión 1 generado", metadata_json=json.dumps({"version": 1}, ensure_ascii=False)))
        db.commit()

    tablas = [
        "cases",
        "case_documents",
        "case_document_versions",
        "case_participants",
        "case_act_data",
        "case_timeline_events",
        "case_workflow_events",
    ]

    for tabla in tablas:
        db.execute(text(f"""
            SELECT setval(
                pg_get_serial_sequence('{tabla}', 'id'),
                COALESCE((SELECT MAX(id) FROM {tabla}), 0) + 1,
                false
            )
        """))
    db.commit()

if __name__ == "__main__":
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        seed_notary = db.query(Notary).filter(Notary.slug == "bogota-d-c-easypro-notarial-bogota").first()
        ensure_power_general_template(db, seed_notary)
        ensure_compraventa_vis_template(db, seed_notary)
    finally:
        db.close()
```

## File: app/db/session.py
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings

settings = get_settings()
database_url = settings.database_url
engine_kwargs = {"pool_pre_ping": True}

if database_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(database_url, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

## File: app/main.py
```python
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response

from app.api.router import api_router
from app.core.config import get_settings
from app.db.init_db import init_db
from app.db.session import SessionLocal
from dotenv import load_dotenv

load_dotenv()
settings = get_settings()


class FlexibleCORSMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.allowed_origins = self._load_allowed_origins()
        print(f"[CORS DEBUG] Allowed origins loaded: {sorted(self.allowed_origins)}")

    def _load_allowed_origins(self) -> set[str]:
        origins = {
            "https://easypro-notarial-2.vercel.app",
            "http://127.0.0.1:5179",
            "http://localhost:5179",
            "http://localhost:3000",
        }

        env_values = [
            settings.frontend_url,
            os.getenv("FRONTEND_URL", ""),
            os.getenv("FRONTEND_URLS", ""),
            os.getenv("CORS_ALLOWED_ORIGINS", ""),
        ]
        for value in env_values:
            if not value:
                continue
            for origin in value.split(","):
                cleaned = origin.strip().rstrip("/")
                if cleaned:
                    origins.add(cleaned)
        return origins

    def _is_allowed_origin(self, origin: str) -> bool:
        normalized = origin.rstrip("/")
        if normalized in self.allowed_origins:
            return True
        return normalized.startswith("https://easypro-notarial-2-pr") and normalized.endswith(".vercel.app")

    async def dispatch(self, request: StarletteRequest, call_next):
        origin = request.headers.get("origin", "").rstrip("/")
        is_allowed = self._is_allowed_origin(origin)
        cors_headers = {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "GET,POST,PUT,PATCH,DELETE,OPTIONS",
            "Access-Control-Allow-Headers": "Authorization,Content-Type,Accept,Origin,X-Requested-With",
            "Access-Control-Max-Age": "600",
        }
        if request.method == "OPTIONS":
            if is_allowed:
                return Response(status_code=200, headers=cors_headers)
            return Response(status_code=400)
        response = await call_next(request)
        if is_allowed:
            for key, value in cors_headers.items():
                response.headers[key] = value
        return response


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(FlexibleCORSMiddleware)
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/health")
def health():
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
    finally:
        db.close()
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.environment,
    }
```

## File: app/models/__init__.py
```python
from app.models.act_catalog import ActCatalog
from app.models.case import Case
from app.models.case_act import CaseAct
from app.models.case_act_data import CaseActData
from app.models.case_client_comment import CaseClientComment
from app.models.case_document import CaseDocument
from app.models.case_document_version import CaseDocumentVersion
from app.models.case_internal_note import CaseInternalNote
from app.models.case_participant import CaseParticipant
from app.models.case_state_definition import CaseStateDefinition
from app.models.case_timeline_event import CaseTimelineEvent
from app.models.case_workflow_event import CaseWorkflowEvent
from app.models.document_template import DocumentTemplate
from app.models.legal_entity import LegalEntity
from app.models.legal_entity_representative import LegalEntityRepresentative
from app.models.notary import Notary
from app.models.notary_commercial_activity import NotaryCommercialActivity
from app.models.notary_crm_audit_log import NotaryCrmAuditLog
from app.models.numbering_sequence import NumberingSequence
from app.models.person import Person
from app.models.role import Role
from app.models.role_assignment import RoleAssignment
from app.models.role_permission import RolePermission
from app.models.template_field import TemplateField
from app.models.template_required_role import TemplateRequiredRole
from app.models.user import User
```

## File: app/models/act_catalog.py
```python
from __future__ import annotations

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class ActCatalog(TimestampMixin, Base):
    __tablename__ = "act_catalog"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    label: Mapped[str] = mapped_column(String(200))
    roles_json: Mapped[str] = mapped_column(Text, default="[]")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
```

## File: app/models/base.py
```python
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

## File: app/models/case_act_data.py
```python
from __future__ import annotations

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class CaseActData(TimestampMixin, Base):
    __tablename__ = "case_act_data"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), unique=True, index=True)
    data_json: Mapped[str] = mapped_column(Text, default="{}")
    gari_draft_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    case: Mapped["Case"] = relationship(back_populates="act_data")
```

## File: app/models/case_act.py
```python
from __future__ import annotations

from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class CaseAct(TimestampMixin, Base):
    __tablename__ = "case_acts"
    __table_args__ = (Index("ix_case_acts_case_id_act_order", "case_id", "act_order"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"), index=True)
    act_code: Mapped[str] = mapped_column(String(80))
    act_label: Mapped[str] = mapped_column(String(200))
    act_order: Mapped[int] = mapped_column(Integer)
    roles_json: Mapped[str] = mapped_column(Text, default="[]")

    case: Mapped["Case"] = relationship(back_populates="acts")
```

## File: app/models/case_client_comment.py
```python
from __future__ import annotations

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class CaseClientComment(TimestampMixin, Base):
    __tablename__ = "case_client_comments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    comment: Mapped[str] = mapped_column(Text)

    case: Mapped["Case"] = relationship(back_populates="client_comments")
    created_by_user: Mapped["User | None"] = relationship(back_populates="client_case_comments")
```

## File: app/models/case_document_version.py
```python
from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class CaseDocumentVersion(TimestampMixin, Base):
    __tablename__ = "case_document_versions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    case_document_id: Mapped[int] = mapped_column(ForeignKey("case_documents.id"), index=True)
    version_number: Mapped[int] = mapped_column(index=True)
    file_format: Mapped[str] = mapped_column(String(20), index=True)
    storage_path: Mapped[str] = mapped_column(String(400))
    original_filename: Mapped[str] = mapped_column(String(255))
    generated_from_template_id: Mapped[int | None] = mapped_column(ForeignKey("document_templates.id"), nullable=True)
    placeholder_snapshot_json: Mapped[str] = mapped_column(Text, default="{}")
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)

    document: Mapped["CaseDocument"] = relationship(back_populates="versions")
    generated_from_template: Mapped["DocumentTemplate | None"] = relationship()
    created_by_user: Mapped["User | None"] = relationship(back_populates="case_document_versions")
```

## File: app/models/case_document.py
```python
from __future__ import annotations

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class CaseDocument(TimestampMixin, Base):
    __tablename__ = "case_documents"
    __table_args__ = (UniqueConstraint("case_id", "category", name="uq_case_document_category"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)
    category: Mapped[str] = mapped_column(String(40), index=True)
    title: Mapped[str] = mapped_column(String(160))
    current_version_number: Mapped[int] = mapped_column(default=0)

    case: Mapped["Case"] = relationship(back_populates="documents")
    versions: Mapped[list["CaseDocumentVersion"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="desc(CaseDocumentVersion.version_number)",
    )
```

## File: app/models/case_internal_note.py
```python
from __future__ import annotations

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class CaseInternalNote(TimestampMixin, Base):
    __tablename__ = "case_internal_notes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    note: Mapped[str] = mapped_column(Text)

    case: Mapped["Case"] = relationship(back_populates="internal_notes")
    created_by_user: Mapped["User | None"] = relationship(back_populates="internal_case_notes")
```

## File: app/models/case_participant.py
```python
from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class CaseParticipant(TimestampMixin, Base):
    __tablename__ = "case_participants"
    __table_args__ = (UniqueConstraint("case_id", "role_code", name="uq_case_participant_role"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)
    person_id: Mapped[int] = mapped_column(ForeignKey("persons.id"), index=True)
    legal_entity_id: Mapped[int | None] = mapped_column(ForeignKey("legal_entities.id"), nullable=True, index=True)
    role_code: Mapped[str] = mapped_column(String(80), index=True)
    role_label: Mapped[str] = mapped_column(String(120))
    snapshot_json: Mapped[str] = mapped_column(Text, default="{}")

    case: Mapped["Case"] = relationship(back_populates="participants")
    person: Mapped["Person"] = relationship(back_populates="case_participations")
    legal_entity: Mapped["LegalEntity | None"] = relationship(back_populates="case_participations")
```

## File: app/models/case_state_definition.py
```python
from sqlalchemy import Boolean, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class CaseStateDefinition(TimestampMixin, Base):
    __tablename__ = "case_state_definitions"
    __table_args__ = (
        UniqueConstraint("case_type", "code", name="uq_case_state_definitions_case_type_code"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    case_type: Mapped[str] = mapped_column(String(80), index=True)
    code: Mapped[str] = mapped_column(String(50), index=True)
    label: Mapped[str] = mapped_column(String(120))
    step_order: Mapped[int] = mapped_column(Integer, index=True)
    is_initial: Mapped[bool] = mapped_column(Boolean, default=False)
    is_terminal: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
```

## File: app/models/case_timeline_event.py
```python
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class CaseTimelineEvent(TimestampMixin, Base):
    __tablename__ = "case_timeline_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"), index=True)
    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(50), index=True)
    from_state: Mapped[str | None] = mapped_column(String(50), nullable=True)
    to_state: Mapped[str | None] = mapped_column(String(50), nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    case: Mapped["Case"] = relationship(back_populates="timeline_events")
    actor_user: Mapped["User | None"] = relationship(back_populates="case_timeline_events", foreign_keys=[actor_user_id])
```

## File: app/models/case_workflow_event.py
```python
from __future__ import annotations

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class CaseWorkflowEvent(TimestampMixin, Base):
    __tablename__ = "case_workflow_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)
    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    actor_role_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    event_type: Mapped[str] = mapped_column(String(80), index=True)
    from_state: Mapped[str | None] = mapped_column(String(50), nullable=True)
    to_state: Mapped[str | None] = mapped_column(String(50), nullable=True)
    field_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    approved_version_id: Mapped[int | None] = mapped_column(ForeignKey("case_document_versions.id"), nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    case: Mapped["Case"] = relationship(back_populates="workflow_events")
    actor_user: Mapped["User | None"] = relationship(back_populates="case_workflow_events", foreign_keys=[actor_user_id])
    approved_version: Mapped["CaseDocumentVersion | None"] = relationship(foreign_keys=[approved_version_id])
```

## File: app/models/case.py
```python
from __future__ import annotations

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Case(TimestampMixin, Base):
    __tablename__ = "cases"
    __table_args__ = (
        UniqueConstraint("notary_id", "year", "consecutive", name="uq_cases_notary_year_consecutive"),
        UniqueConstraint("internal_case_number", name="uq_cases_internal_case_number"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    notary_id: Mapped[int] = mapped_column(ForeignKey("notaries.id"), index=True)
    template_id: Mapped[int | None] = mapped_column(ForeignKey("document_templates.id"), nullable=True, index=True)
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    case_type: Mapped[str] = mapped_column(String(80), index=True)
    act_type: Mapped[str] = mapped_column(String(120), index=True)
    consecutive: Mapped[int] = mapped_column(Integer, index=True)
    year: Mapped[int] = mapped_column(Integer, index=True)
    internal_case_number: Mapped[str | None] = mapped_column(String(40), nullable=True, index=True)
    official_deed_number: Mapped[str | None] = mapped_column(String(40), nullable=True, index=True)
    official_deed_year: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    current_state: Mapped[str] = mapped_column(String(50), index=True)
    current_owner_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    client_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    protocolist_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    approver_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    titular_notary_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    substitute_notary_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    requires_client_review: Mapped[bool] = mapped_column(Boolean, default=False)
    final_signed_uploaded: Mapped[bool] = mapped_column(Boolean, default=False)
    approved_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    approved_by_role_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    approved_document_version_id: Mapped[int | None] = mapped_column(ForeignKey("case_document_versions.id"), nullable=True)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")

    notary: Mapped["Notary"] = relationship(back_populates="cases")
    template: Mapped["DocumentTemplate | None"] = relationship(back_populates="cases")
    created_by_user: Mapped["User | None"] = relationship(back_populates="created_cases", foreign_keys=[created_by_user_id])
    current_owner_user: Mapped["User | None"] = relationship(back_populates="owned_cases", foreign_keys=[current_owner_user_id])
    client_user: Mapped["User | None"] = relationship(back_populates="client_cases", foreign_keys=[client_user_id])
    protocolist_user: Mapped["User | None"] = relationship(back_populates="protocolist_cases", foreign_keys=[protocolist_user_id])
    approver_user: Mapped["User | None"] = relationship(back_populates="approver_cases", foreign_keys=[approver_user_id])
    titular_notary_user: Mapped["User | None"] = relationship(back_populates="titular_cases", foreign_keys=[titular_notary_user_id])
    substitute_notary_user: Mapped["User | None"] = relationship(back_populates="substitute_cases", foreign_keys=[substitute_notary_user_id])
    approved_by_user: Mapped["User | None"] = relationship(back_populates="approved_cases", foreign_keys=[approved_by_user_id])
    approved_document_version: Mapped["CaseDocumentVersion | None"] = relationship(foreign_keys=[approved_document_version_id])
    timeline_events: Mapped[list["CaseTimelineEvent"]] = relationship(
        back_populates="case",
        cascade="all, delete-orphan",
        order_by="desc(CaseTimelineEvent.created_at)",
    )
    participants: Mapped[list["CaseParticipant"]] = relationship(
        back_populates="case",
        cascade="all, delete-orphan",
        order_by="CaseParticipant.created_at.asc()",
    )
    act_data: Mapped["CaseActData | None"] = relationship(back_populates="case", cascade="all, delete-orphan", uselist=False)
    client_comments: Mapped[list["CaseClientComment"]] = relationship(
        back_populates="case",
        cascade="all, delete-orphan",
        order_by="desc(CaseClientComment.created_at)",
    )
    internal_notes: Mapped[list["CaseInternalNote"]] = relationship(
        back_populates="case",
        cascade="all, delete-orphan",
        order_by="desc(CaseInternalNote.created_at)",
    )
    documents: Mapped[list["CaseDocument"]] = relationship(
        back_populates="case",
        cascade="all, delete-orphan",
        order_by="CaseDocument.category.asc()",
    )
    workflow_events: Mapped[list["CaseWorkflowEvent"]] = relationship(
        back_populates="case",
        cascade="all, delete-orphan",
        order_by="desc(CaseWorkflowEvent.created_at)",
    )
    acts: Mapped[list["CaseAct"]] = relationship(
        back_populates="case",
        cascade="all, delete-orphan",
        order_by="CaseAct.act_order.asc()",
    )
```

## File: app/models/document_template.py
```python
from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class DocumentTemplate(TimestampMixin, Base):
    __tablename__ = "document_templates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(160), index=True)
    slug: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    case_type: Mapped[str] = mapped_column(String(80), default="escritura", index=True)
    document_type: Mapped[str] = mapped_column(String(120), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    scope_type: Mapped[str] = mapped_column(String(20), default="global", index=True)
    notary_id: Mapped[int | None] = mapped_column(ForeignKey("notaries.id"), nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    source_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    storage_path: Mapped[str | None] = mapped_column(String(400), nullable=True)
    internal_variable_map_json: Mapped[str] = mapped_column(Text, default="{}")

    notary: Mapped["Notary | None"] = relationship(back_populates="document_templates")
    required_roles: Mapped[list["TemplateRequiredRole"]] = relationship(
        back_populates="template",
        cascade="all, delete-orphan",
        order_by="TemplateRequiredRole.step_order.asc()",
    )
    fields: Mapped[list["TemplateField"]] = relationship(
        back_populates="template",
        cascade="all, delete-orphan",
        order_by="TemplateField.step_order.asc()",
    )
    cases: Mapped[list["Case"]] = relationship(back_populates="template")
```

## File: app/models/legal_entity_representative.py
```python
from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.models.base import Base, TimestampMixin


class LegalEntityRepresentative(TimestampMixin, Base):
    __tablename__ = "legal_entity_representatives"
    __table_args__ = (UniqueConstraint("legal_entity_id", "person_id", name="uq_entity_representative"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    legal_entity_id: Mapped[int] = mapped_column(ForeignKey("legal_entities.id"), index=True)
    person_id: Mapped[int] = mapped_column(ForeignKey("persons.id"), index=True)
    power_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    legal_entity: Mapped["LegalEntity"] = relationship(back_populates="representatives")
    person: Mapped["Person"] = relationship(back_populates="legal_entity_representations")
```

## File: app/models/legal_entity.py
```python
from __future__ import annotations

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.models.base import Base, TimestampMixin


class LegalEntity(TimestampMixin, Base):
    __tablename__ = "legal_entities"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nit: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    legal_representative: Mapped[str | None] = mapped_column(String(160), nullable=True)
    municipality: Mapped[str | None] = mapped_column(String(120), nullable=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    email: Mapped[str | None] = mapped_column(String(120), nullable=True)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")

    representatives: Mapped[list["LegalEntityRepresentative"]] = relationship(
        back_populates="legal_entity",
        cascade="all, delete-orphan",
    )
    case_participations: Mapped[list["CaseParticipant"]] = relationship(back_populates="legal_entity")
```

## File: app/models/notary_commercial_activity.py
```python
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class NotaryCommercialActivity(TimestampMixin, Base):
    __tablename__ = "notary_commercial_activities"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    notary_id: Mapped[int] = mapped_column(ForeignKey("notaries.id", ondelete="CASCADE"), index=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    management_type: Mapped[str] = mapped_column(String(60))
    comment: Mapped[str] = mapped_column(Text)
    responsible: Mapped[str] = mapped_column(String(120))
    responsible_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    result: Mapped[str | None] = mapped_column(String(160), nullable=True)
    next_action: Mapped[str | None] = mapped_column(Text, nullable=True)

    notary: Mapped["Notary"] = relationship(back_populates="commercial_activities")
    responsible_user: Mapped["User | None"] = relationship(
        back_populates="commercial_activities",
        foreign_keys=[responsible_user_id],
    )
```

## File: app/models/notary_crm_audit_log.py
```python
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class NotaryCrmAuditLog(TimestampMixin, Base):
    __tablename__ = "notary_crm_audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    notary_id: Mapped[int] = mapped_column(ForeignKey("notaries.id", ondelete="CASCADE"), index=True)
    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(50), index=True)
    field_name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    notary: Mapped["Notary"] = relationship(back_populates="crm_audit_logs")
    actor_user: Mapped["User | None"] = relationship(
        back_populates="crm_audit_logs",
        foreign_keys=[actor_user_id],
    )
```

## File: app/models/notary.py
```python
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Notary(TimestampMixin, Base):
    __tablename__ = "notaries"
    __table_args__ = (
        UniqueConstraint("catalog_identity_key", name="uq_notaries_catalog_identity_key"),
        UniqueConstraint("municipality", "notary_label", "email", name="uq_notaries_catalog_identity"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    catalog_identity_key: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    commercial_name: Mapped[str] = mapped_column(String(120))
    legal_name: Mapped[str] = mapped_column(String(160))
    department: Mapped[str] = mapped_column(String(80), default="Antioquia", index=True)
    municipality: Mapped[str] = mapped_column(String(120), index=True)
    notary_label: Mapped[str] = mapped_column(String(160), index=True)
    logo_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    primary_color: Mapped[str] = mapped_column(String(20), default="#0D2E5D")
    secondary_color: Mapped[str] = mapped_column(String(20), default="#4D5B7C")
    base_color: Mapped[str] = mapped_column(String(20), default="#F4F7FB")
    accent_color: Mapped[str] = mapped_column(String(20), default="#50D690")
    city: Mapped[str] = mapped_column(String(80))
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(Text, nullable=True)
    email: Mapped[str | None] = mapped_column(String(120), nullable=True)
    current_notary_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    business_hours: Mapped[str | None] = mapped_column(Text, nullable=True)
    institutional_data: Mapped[str] = mapped_column(Text, default="")
    commercial_status: Mapped[str] = mapped_column(String(40), default="prospecto", index=True)
    commercial_owner: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    commercial_owner_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    main_contact_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    main_contact_title: Mapped[str | None] = mapped_column(String(120), nullable=True)
    commercial_phone: Mapped[str | None] = mapped_column(Text, nullable=True)
    commercial_email: Mapped[str | None] = mapped_column(String(120), nullable=True)
    last_management_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    next_management_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    commercial_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[str] = mapped_column(String(20), default="media", index=True)
    lead_source: Mapped[str | None] = mapped_column(String(120), nullable=True)
    potential: Mapped[str | None] = mapped_column(String(40), nullable=True)
    internal_observations: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    users: Mapped[list["User"]] = relationship(back_populates="default_notary", foreign_keys="User.default_notary_id")
    role_assignments: Mapped[list["RoleAssignment"]] = relationship(back_populates="notary")
    commercial_owner_user: Mapped["User | None"] = relationship(back_populates="owned_notaries", foreign_keys=[commercial_owner_user_id])
    commercial_activities: Mapped[list["NotaryCommercialActivity"]] = relationship(back_populates="notary", cascade="all, delete-orphan", order_by="desc(NotaryCommercialActivity.occurred_at)")
    crm_audit_logs: Mapped[list["NotaryCrmAuditLog"]] = relationship(back_populates="notary", cascade="all, delete-orphan", order_by="desc(NotaryCrmAuditLog.created_at)")
    cases: Mapped[list["Case"]] = relationship(back_populates="notary", cascade="all, delete-orphan", order_by="desc(Case.updated_at)")
    document_templates: Mapped[list["DocumentTemplate"]] = relationship(back_populates="notary")
    numbering_sequences: Mapped[list["NumberingSequence"]] = relationship(back_populates="notary")
```

## File: app/models/numbering_sequence.py
```python
from __future__ import annotations

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class NumberingSequence(TimestampMixin, Base):
    __tablename__ = "numbering_sequences"
    __table_args__ = (UniqueConstraint("sequence_type", "notary_id", "year", name="uq_numbering_sequence_scope"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    sequence_type: Mapped[str] = mapped_column(String(40), index=True)
    notary_id: Mapped[int | None] = mapped_column(ForeignKey("notaries.id"), nullable=True, index=True)
    year: Mapped[int] = mapped_column(index=True)
    current_value: Mapped[int] = mapped_column(default=0)

    notary: Mapped["Notary | None"] = relationship(back_populates="numbering_sequences")
```

## File: app/models/person.py
```python
from __future__ import annotations

from sqlalchemy import Boolean, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Person(TimestampMixin, Base):
    __tablename__ = "persons"
    __table_args__ = (UniqueConstraint("document_type", "document_number", name="uq_person_document"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    document_type: Mapped[str] = mapped_column(String(40), index=True)
    document_number: Mapped[str] = mapped_column(String(40), index=True)
    full_name: Mapped[str] = mapped_column(String(160), index=True)
    sex: Mapped[str | None] = mapped_column(String(20), nullable=True)
    nationality: Mapped[str | None] = mapped_column(String(80), nullable=True)
    marital_status: Mapped[str | None] = mapped_column(String(40), nullable=True)
    profession: Mapped[str | None] = mapped_column(String(120), nullable=True)
    municipality: Mapped[str | None] = mapped_column(String(120), nullable=True)
    is_transient: Mapped[bool] = mapped_column(Boolean, default=False)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(120), nullable=True)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")

    case_participations: Mapped[list["CaseParticipant"]] = relationship(back_populates="person")
    legal_entity_representations: Mapped[list["LegalEntityRepresentative"]] = relationship(back_populates="person")
```

## File: app/models/role_assignment.py
```python
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class RoleAssignment(TimestampMixin, Base):
    __tablename__ = "role_assignments"
    __table_args__ = (
        UniqueConstraint("user_id", "role_id", "notary_id", name="uq_user_role_notary"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), index=True)
    notary_id: Mapped[int | None] = mapped_column(ForeignKey("notaries.id"), nullable=True, index=True)

    user: Mapped["User"] = relationship(back_populates="role_assignments")
    role: Mapped["Role"] = relationship(back_populates="assignments")
    notary: Mapped["Notary | None"] = relationship(back_populates="role_assignments")
```

## File: app/models/role_permission.py
```python
from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class RolePermission(Base):
    __tablename__ = "role_permissions"
    __table_args__ = (
        UniqueConstraint("role_id", "module_code", name="uq_role_permissions"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), index=True)
    module_code: Mapped[str] = mapped_column(String(80), index=True)
    can_access: Mapped[bool] = mapped_column(Boolean, default=False)

    role: Mapped["Role"] = relationship(back_populates="permissions")
```

## File: app/models/role.py
```python
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Role(TimestampMixin, Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    scope: Mapped[str] = mapped_column(String(30), default="notary")
    description: Mapped[str] = mapped_column(String(255), default="")

    assignments: Mapped[list["RoleAssignment"]] = relationship(back_populates="role")
    permissions: Mapped[list["RolePermission"]] = relationship(back_populates="role")
```

## File: app/models/template_field.py
```python
from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class TemplateField(Base):
    __tablename__ = "template_fields"
    __table_args__ = (UniqueConstraint("template_id", "field_code", name="uq_template_fields"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    template_id: Mapped[int] = mapped_column(ForeignKey("document_templates.id"), index=True)
    field_code: Mapped[str] = mapped_column(String(120), index=True)
    label: Mapped[str] = mapped_column(String(160))
    field_type: Mapped[str] = mapped_column(String(40), default="text")
    section: Mapped[str] = mapped_column(String(80), default="acto")
    is_required: Mapped[bool] = mapped_column(Boolean, default=True)
    options_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    placeholder_key: Mapped[str | None] = mapped_column(String(160), nullable=True)
    help_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    step_order: Mapped[int] = mapped_column(default=1)

    template: Mapped["DocumentTemplate"] = relationship(back_populates="fields")
```

## File: app/models/template_required_role.py
```python
from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class TemplateRequiredRole(Base):
    __tablename__ = "template_required_roles"
    __table_args__ = (UniqueConstraint("template_id", "role_code", name="uq_template_required_roles"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    template_id: Mapped[int] = mapped_column(ForeignKey("document_templates.id"), index=True)
    role_code: Mapped[str] = mapped_column(String(80), index=True)
    label: Mapped[str] = mapped_column(String(120))
    is_required: Mapped[bool] = mapped_column(Boolean, default=True)
    step_order: Mapped[int] = mapped_column(default=1)

    template: Mapped["DocumentTemplate"] = relationship(back_populates="required_roles")
```

## File: app/models/user.py
```python
from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(160))
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    job_title: Mapped[str | None] = mapped_column(String(80), nullable=True)
    default_notary_id: Mapped[int | None] = mapped_column(ForeignKey("notaries.id"), nullable=True)

    default_notary: Mapped["Notary | None"] = relationship(back_populates="users", foreign_keys=[default_notary_id])
    role_assignments: Mapped[list["RoleAssignment"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    owned_notaries: Mapped[list["Notary"]] = relationship(back_populates="commercial_owner_user", foreign_keys="Notary.commercial_owner_user_id")
    commercial_activities: Mapped[list["NotaryCommercialActivity"]] = relationship(back_populates="responsible_user", foreign_keys="NotaryCommercialActivity.responsible_user_id")
    crm_audit_logs: Mapped[list["NotaryCrmAuditLog"]] = relationship(back_populates="actor_user", foreign_keys="NotaryCrmAuditLog.actor_user_id")
    owned_cases: Mapped[list["Case"]] = relationship(back_populates="current_owner_user", foreign_keys="Case.current_owner_user_id")
    created_cases: Mapped[list["Case"]] = relationship(back_populates="created_by_user", foreign_keys="Case.created_by_user_id")
    approved_cases: Mapped[list["Case"]] = relationship(back_populates="approved_by_user", foreign_keys="Case.approved_by_user_id")
    client_cases: Mapped[list["Case"]] = relationship(back_populates="client_user", foreign_keys="Case.client_user_id")
    protocolist_cases: Mapped[list["Case"]] = relationship(back_populates="protocolist_user", foreign_keys="Case.protocolist_user_id")
    approver_cases: Mapped[list["Case"]] = relationship(back_populates="approver_user", foreign_keys="Case.approver_user_id")
    titular_cases: Mapped[list["Case"]] = relationship(back_populates="titular_notary_user", foreign_keys="Case.titular_notary_user_id")
    substitute_cases: Mapped[list["Case"]] = relationship(back_populates="substitute_notary_user", foreign_keys="Case.substitute_notary_user_id")
    case_timeline_events: Mapped[list["CaseTimelineEvent"]] = relationship(back_populates="actor_user", foreign_keys="CaseTimelineEvent.actor_user_id")
    client_case_comments: Mapped[list["CaseClientComment"]] = relationship(back_populates="created_by_user", foreign_keys="CaseClientComment.created_by_user_id")
    internal_case_notes: Mapped[list["CaseInternalNote"]] = relationship(back_populates="created_by_user", foreign_keys="CaseInternalNote.created_by_user_id")
    case_document_versions: Mapped[list["CaseDocumentVersion"]] = relationship(back_populates="created_by_user", foreign_keys="CaseDocumentVersion.created_by_user_id")
    case_workflow_events: Mapped[list["CaseWorkflowEvent"]] = relationship(back_populates="actor_user", foreign_keys="CaseWorkflowEvent.actor_user_id")
```

## File: app/modules/__init__.py
```python

```

## File: app/modules/act_catalog/__init__.py
```python

```

## File: app/modules/act_catalog/router.py
```python
from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.act_catalog import ActCatalog
from app.schemas.act_catalog import ActCatalogOut


act_catalog_router = APIRouter(prefix="/act-catalog", tags=["act-catalog"])


def load_case_or_404(db: Session, case_id: int) -> Case:
    case = db.query(Case).filter(Case.id == case_id).first()
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Minuta no encontrada.")
    return case


LEGACY_CASE_ACTS_BY_VARIANT: dict[str, list[dict[str, str | int]]] = {
    "aragua_apto_1c": [
        {"act_code": "liberacion_hipoteca", "act_label": "Liberación parcial de hipoteca", "act_order": 1, "roles_json": json.dumps(["banco_libera", "fideicomiso"], ensure_ascii=False)},
        {"act_code": "protocolizacion_cto", "act_label": "Protocolización CTO", "act_order": 2, "roles_json": json.dumps(["fideicomiso", "constructora"], ensure_ascii=False)},
        {"act_code": "compraventa_vis", "act_label": "Compraventa VIS", "act_order": 3, "roles_json": json.dumps(["fideicomiso", "compradores"], ensure_ascii=False)},
        {"act_code": "renuncia_resolutoria", "act_label": "Renuncia condición resolutoria", "act_order": 4, "roles_json": json.dumps(["fideicomiso", "compradores"], ensure_ascii=False)},
        {"act_code": "cancelacion_comodato", "act_label": "Cancelación comodato precario", "act_order": 5, "roles_json": json.dumps(["fideicomiso", "constructora"], ensure_ascii=False)},
        {"act_code": "patrimonio_familia", "act_label": "Constitución patrimonio de familia", "act_order": 6, "roles_json": json.dumps(["compradores"], ensure_ascii=False)},
        {"act_code": "poder_especial", "act_label": "Poder especial", "act_order": 7, "roles_json": json.dumps(["compradores", "constructora"], ensure_ascii=False)},
    ],
    "aragua_apto_2c": [
        {"act_code": "liberacion_hipoteca", "act_label": "Liberación parcial de hipoteca", "act_order": 1, "roles_json": json.dumps(["banco_libera", "fideicomiso"], ensure_ascii=False)},
        {"act_code": "protocolizacion_cto", "act_label": "Protocolización CTO", "act_order": 2, "roles_json": json.dumps(["fideicomiso", "constructora"], ensure_ascii=False)},
        {"act_code": "compraventa_vis", "act_label": "Compraventa VIS", "act_order": 3, "roles_json": json.dumps(["fideicomiso", "compradores"], ensure_ascii=False)},
        {"act_code": "renuncia_resolutoria", "act_label": "Renuncia condición resolutoria", "act_order": 4, "roles_json": json.dumps(["fideicomiso", "compradores"], ensure_ascii=False)},
        {"act_code": "cancelacion_comodato", "act_label": "Cancelación comodato precario", "act_order": 5, "roles_json": json.dumps(["fideicomiso", "constructora"], ensure_ascii=False)},
        {"act_code": "patrimonio_familia", "act_label": "Constitución patrimonio de familia", "act_order": 6, "roles_json": json.dumps(["compradores"], ensure_ascii=False)},
        {"act_code": "poder_especial", "act_label": "Poder especial", "act_order": 7, "roles_json": json.dumps(["compradores", "constructora"], ensure_ascii=False)},
    ],
    "aragua_parq_2c": [
        {"act_code": "liberacion_hipoteca", "act_label": "Liberación parcial de hipoteca", "act_order": 1, "roles_json": json.dumps(["banco_libera", "fideicomiso"], ensure_ascii=False)},
        {"act_code": "protocolizacion_cto", "act_label": "Protocolización CTO", "act_order": 2, "roles_json": json.dumps(["fideicomiso", "constructora"], ensure_ascii=False)},
        {"act_code": "compraventa_vis", "act_label": "Compraventa VIS", "act_order": 3, "roles_json": json.dumps(["fideicomiso", "compradores"], ensure_ascii=False)},
        {"act_code": "renuncia_resolutoria", "act_label": "Renuncia condición resolutoria", "act_order": 4, "roles_json": json.dumps(["fideicomiso", "compradores"], ensure_ascii=False)},
        {"act_code": "cancelacion_comodato", "act_label": "Cancelación comodato precario", "act_order": 5, "roles_json": json.dumps(["fideicomiso", "constructora"], ensure_ascii=False)},
        {"act_code": "poder_especial", "act_label": "Poder especial", "act_order": 6, "roles_json": json.dumps(["compradores", "constructora"], ensure_ascii=False)},
    ],
    "aragua_parq_3c": [
        {"act_code": "liberacion_hipoteca", "act_label": "Liberación parcial de hipoteca", "act_order": 1, "roles_json": json.dumps(["banco_libera", "fideicomiso"], ensure_ascii=False)},
        {"act_code": "protocolizacion_cto", "act_label": "Protocolización CTO", "act_order": 2, "roles_json": json.dumps(["fideicomiso", "constructora"], ensure_ascii=False)},
        {"act_code": "compraventa_vis", "act_label": "Compraventa VIS", "act_order": 3, "roles_json": json.dumps(["fideicomiso", "compradores"], ensure_ascii=False)},
        {"act_code": "renuncia_resolutoria", "act_label": "Renuncia condición resolutoria", "act_order": 4, "roles_json": json.dumps(["fideicomiso", "compradores"], ensure_ascii=False)},
        {"act_code": "cancelacion_comodato", "act_label": "Cancelación comodato precario", "act_order": 5, "roles_json": json.dumps(["fideicomiso", "constructora"], ensure_ascii=False)},
        {"act_code": "poder_especial", "act_label": "Poder especial", "act_order": 6, "roles_json": json.dumps(["compradores", "constructora"], ensure_ascii=False)},
    ],
    "jaggua_fna_1c": [
        {"act_code": "liberacion_hipoteca", "act_label": "Liberación parcial de hipoteca", "act_order": 1, "roles_json": json.dumps(["banco_libera", "fideicomiso"], ensure_ascii=False)},
        {"act_code": "protocolizacion_cto", "act_label": "Protocolización CTO", "act_order": 2, "roles_json": json.dumps(["fideicomiso", "constructora"], ensure_ascii=False)},
        {"act_code": "compraventa_vis", "act_label": "Compraventa VIS", "act_order": 3, "roles_json": json.dumps(["fideicomiso", "compradores"], ensure_ascii=False)},
        {"act_code": "renuncia_resolutoria", "act_label": "Renuncia condición resolutoria", "act_order": 4, "roles_json": json.dumps(["fideicomiso", "compradores"], ensure_ascii=False)},
        {"act_code": "cancelacion_comodato", "act_label": "Cancelación comodato precario", "act_order": 5, "roles_json": json.dumps(["fideicomiso", "constructora"], ensure_ascii=False)},
        {"act_code": "constitucion_hipoteca", "act_label": "Constitución hipoteca 1er grado", "act_order": 6, "roles_json": json.dumps(["compradores", "banco_hipoteca"], ensure_ascii=False)},
        {"act_code": "patrimonio_familia", "act_label": "Constitución patrimonio de familia", "act_order": 7, "roles_json": json.dumps(["compradores"], ensure_ascii=False)},
        {"act_code": "poder_especial", "act_label": "Poder especial", "act_order": 8, "roles_json": json.dumps(["compradores", "constructora"], ensure_ascii=False)},
    ],
    "jaggua_fna_2c": [
        {"act_code": "liberacion_hipoteca", "act_label": "Liberación parcial de hipoteca", "act_order": 1, "roles_json": json.dumps(["banco_libera", "fideicomiso"], ensure_ascii=False)},
        {"act_code": "protocolizacion_cto", "act_label": "Protocolización CTO", "act_order": 2, "roles_json": json.dumps(["fideicomiso", "constructora"], ensure_ascii=False)},
        {"act_code": "compraventa_vis", "act_label": "Compraventa VIS", "act_order": 3, "roles_json": json.dumps(["fideicomiso", "compradores"], ensure_ascii=False)},
        {"act_code": "renuncia_resolutoria", "act_label": "Renuncia condición resolutoria", "act_order": 4, "roles_json": json.dumps(["fideicomiso", "compradores"], ensure_ascii=False)},
        {"act_code": "cancelacion_comodato", "act_label": "Cancelación comodato precario", "act_order": 5, "roles_json": json.dumps(["fideicomiso", "constructora"], ensure_ascii=False)},
        {"act_code": "constitucion_hipoteca", "act_label": "Constitución hipoteca 1er grado", "act_order": 6, "roles_json": json.dumps(["compradores", "banco_hipoteca"], ensure_ascii=False)},
        {"act_code": "patrimonio_familia", "act_label": "Constitución patrimonio de familia", "act_order": 7, "roles_json": json.dumps(["compradores"], ensure_ascii=False)},
        {"act_code": "poder_especial", "act_label": "Poder especial", "act_order": 8, "roles_json": json.dumps(["compradores", "constructora"], ensure_ascii=False)},
    ],
    "jaggua_bogota_1c": [
        {"act_code": "liberacion_hipoteca", "act_label": "Liberación parcial de hipoteca", "act_order": 1, "roles_json": json.dumps(["banco_libera", "fideicomiso"], ensure_ascii=False)},
        {"act_code": "protocolizacion_cto", "act_label": "Protocolización CTO", "act_order": 2, "roles_json": json.dumps(["fideicomiso", "constructora"], ensure_ascii=False)},
        {"act_code": "compraventa_vis", "act_label": "Compraventa VIS", "act_order": 3, "roles_json": json.dumps(["fideicomiso", "compradores"], ensure_ascii=False)},
        {"act_code": "renuncia_resolutoria", "act_label": "Renuncia condición resolutoria", "act_order": 4, "roles_json": json.dumps(["fideicomiso", "compradores"], ensure_ascii=False)},
        {"act_code": "constitucion_hipoteca", "act_label": "Constitución hipoteca 1er grado", "act_order": 5, "roles_json": json.dumps(["compradores", "banco_hipoteca"], ensure_ascii=False)},
        {"act_code": "patrimonio_familia", "act_label": "Constitución patrimonio de familia", "act_order": 6, "roles_json": json.dumps(["compradores"], ensure_ascii=False)},
        {"act_code": "poder_especial", "act_label": "Poder especial", "act_order": 7, "roles_json": json.dumps(["compradores", "constructora"], ensure_ascii=False)},
    ],
    "jaggua_bogota_2c": [
        {"act_code": "liberacion_hipoteca", "act_label": "Liberación parcial de hipoteca", "act_order": 1, "roles_json": json.dumps(["banco_libera", "fideicomiso"], ensure_ascii=False)},
        {"act_code": "protocolizacion_cto", "act_label": "Protocolización CTO", "act_order": 2, "roles_json": json.dumps(["fideicomiso", "constructora"], ensure_ascii=False)},
        {"act_code": "compraventa_vis", "act_label": "Compraventa VIS", "act_order": 3, "roles_json": json.dumps(["fideicomiso", "compradores"], ensure_ascii=False)},
        {"act_code": "renuncia_resolutoria", "act_label": "Renuncia condición resolutoria", "act_order": 4, "roles_json": json.dumps(["fideicomiso", "compradores"], ensure_ascii=False)},
        {"act_code": "constitucion_hipoteca", "act_label": "Constitución hipoteca 1er grado", "act_order": 5, "roles_json": json.dumps(["compradores", "banco_hipoteca"], ensure_ascii=False)},
        {"act_code": "patrimonio_familia", "act_label": "Constitución patrimonio de familia", "act_order": 6, "roles_json": json.dumps(["compradores"], ensure_ascii=False)},
        {"act_code": "poder_especial", "act_label": "Poder especial", "act_order": 7, "roles_json": json.dumps(["compradores", "constructora"], ensure_ascii=False)},
    ],
    "correccion-registro-civil": [
        {"act_code": "correccion_rc", "act_label": "Corrección de Registro Civil", "act_order": 1, "roles_json": json.dumps(["inscrito"], ensure_ascii=False)},
    ],
    "salida-del-pais": [
        {"act_code": "salida_pais", "act_label": "Permiso de salida del país", "act_order": 1, "roles_json": json.dumps(["padre_otorgante", "madre_aceptante", "menor"], ensure_ascii=False)},
    ],
}


@act_catalog_router.get("", response_model=list[ActCatalogOut])
def get_act_catalog(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    acts = db.query(ActCatalog).filter(ActCatalog.is_active.is_(True)).order_by(ActCatalog.id.asc()).all()
    return [ActCatalogOut.model_validate(item) for item in acts]
```

## File: app/modules/auth/__init__.py
```python

```

## File: app/modules/auth/router.py
```python
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user, get_db
from app.models.role import Role
from app.models.role_assignment import RoleAssignment
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import RolePermissionItem, UserRoleAssignmentSummary
from app.services.auth import AuthenticationError, authenticate_user, build_login_response, serialize_user

router = APIRouter(prefix="/auth", tags=["auth"])


MODULE_CODES = [
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


class AuthenticatedUserWithPermissions(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    is_active: bool
    roles: list[str]
    role_codes: list[str]
    permissions: list[RolePermissionItem]
    default_notary: str | None = None
    assignments: list[UserRoleAssignmentSummary] = Field(default_factory=list)


def load_user_with_permissions(db: Session, user_id: int) -> User:
    user = (
        db.query(User)
        .options(
            joinedload(User.default_notary),
            joinedload(User.role_assignments).joinedload(RoleAssignment.role).joinedload(Role.permissions),
            joinedload(User.role_assignments).joinedload(RoleAssignment.notary),
        )
        .filter(User.id == user_id)
        .first()
    )
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
    return user


def build_permission_union(user: User) -> list[RolePermissionItem]:
    permission_map = {module_code: False for module_code in MODULE_CODES}
    for assignment in user.role_assignments:
        for permission in assignment.role.permissions:
            if permission.module_code not in permission_map:
                permission_map[permission.module_code] = False
            permission_map[permission.module_code] = permission_map[permission.module_code] or permission.can_access
    ordered_module_codes = list(MODULE_CODES)
    for module_code in sorted(permission_map):
        if module_code not in ordered_module_codes:
            ordered_module_codes.append(module_code)
    return [RolePermissionItem(module_code=module_code, can_access=permission_map[module_code]) for module_code in ordered_module_codes]


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    try:
        user = authenticate_user(db, payload.email, payload.password)
    except AuthenticationError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error))
    return build_login_response(user)


@router.get("/me", response_model=AuthenticatedUserWithPermissions)
def me(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    user = load_user_with_permissions(db, current_user.id)
    payload = serialize_user(user)
    payload["permissions"] = build_permission_union(user)
    return payload
```

## File: app/modules/cases/router.py
```python
import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, aliased, joinedload

from app.core.deps import get_current_user, get_db, get_role_codes, require_roles
from app.models.case import Case
from app.models.case_state_definition import CaseStateDefinition
from app.models.case_timeline_event import CaseTimelineEvent
from app.models.notary import Notary
from app.models.user import User
from app.schemas.case import (
    CaseCreate,
    CaseDetail,
    CaseFilterOptions,
    CaseOwnerUpdate,
    CaseStateDefinitionSummary,
    CaseStateUpdate,
    CaseSummary,
    CaseTimelineEventCreate,
    CaseTimelineEventSummary,
    CaseUpdate,
)

router = APIRouter(prefix="/cases", tags=["cases"])

DEFAULT_CASE_TYPE = "escritura"


def safe_json(value: str | None) -> str:
    if value is None or not value.strip():
        return "{}"
    try:
        return json.dumps(json.loads(value), ensure_ascii=False)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="metadata_json debe ser JSON válido.") from exc


def load_case_or_404(db: Session, case_id: int) -> Case:
    case = (
        db.query(Case)
        .options(
            joinedload(Case.notary),
            joinedload(Case.current_owner_user),
            joinedload(Case.client_user),
            joinedload(Case.protocolist_user),
            joinedload(Case.approver_user),
            joinedload(Case.titular_notary_user),
            joinedload(Case.substitute_notary_user),
            joinedload(Case.timeline_events).joinedload(CaseTimelineEvent.actor_user),
        )
        .filter(Case.id == case_id)
        .first()
    )
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caso no encontrado.")
    return case


def get_state_definitions(db: Session, case_type: str) -> list[CaseStateDefinition]:
    definitions = (
        db.query(CaseStateDefinition)
        .filter(CaseStateDefinition.case_type == case_type, CaseStateDefinition.is_active.is_(True))
        .order_by(CaseStateDefinition.step_order.asc())
        .all()
    )
    if definitions:
        return definitions
    return (
        db.query(CaseStateDefinition)
        .filter(CaseStateDefinition.case_type == DEFAULT_CASE_TYPE, CaseStateDefinition.is_active.is_(True))
        .order_by(CaseStateDefinition.step_order.asc())
        .all()
    )


def serialize_timeline_event(event: CaseTimelineEvent) -> CaseTimelineEventSummary:
    return CaseTimelineEventSummary(
        id=event.id,
        event_type=event.event_type,
        from_state=event.from_state,
        to_state=event.to_state,
        comment=event.comment,
        metadata_json=event.metadata_json,
        actor_user_id=event.actor_user_id,
        actor_user_name=event.actor_user.full_name if event.actor_user else None,
        created_at=event.created_at,
    )


def serialize_case_summary(case: Case) -> CaseSummary:
    return CaseSummary(
        id=case.id,
        notary_id=case.notary_id,
        notary_label=case.notary.notary_label,
        case_type=case.case_type,
        act_type=case.act_type,
        consecutive=case.consecutive,
        year=case.year,
        current_state=case.current_state,
        current_owner_user_id=case.current_owner_user_id,
        current_owner_user_name=case.current_owner_user.full_name if case.current_owner_user else None,
        client_user_id=case.client_user_id,
        client_user_name=case.client_user.full_name if case.client_user else None,
        protocolist_user_id=case.protocolist_user_id,
        protocolist_user_name=case.protocolist_user.full_name if case.protocolist_user else None,
        approver_user_id=case.approver_user_id,
        approver_user_name=case.approver_user.full_name if case.approver_user else None,
        titular_notary_user_id=case.titular_notary_user_id,
        titular_notary_user_name=case.titular_notary_user.full_name if case.titular_notary_user else None,
        substitute_notary_user_id=case.substitute_notary_user_id,
        substitute_notary_user_name=case.substitute_notary_user.full_name if case.substitute_notary_user else None,
        requires_client_review=case.requires_client_review,
        final_signed_uploaded=case.final_signed_uploaded,
        metadata_json=case.metadata_json,
        created_at=case.created_at,
        updated_at=case.updated_at,
    )


def serialize_case_detail(db: Session, case: Case) -> CaseDetail:
    summary = serialize_case_summary(case)
    state_definitions = [CaseStateDefinitionSummary.model_validate(item) for item in get_state_definitions(db, case.case_type)]
    return CaseDetail(
        **summary.model_dump(),
        state_definitions=state_definitions,
        timeline_events=[serialize_timeline_event(item) for item in case.timeline_events],
    )


def validate_user_reference(db: Session, user_id: int | None, field_name: str) -> None:
    if user_id is None:
        return
    if db.query(User.id).filter(User.id == user_id, User.is_active.is_(True)).first() is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"{field_name} no existe o está inactivo.")


def resolve_next_consecutive(db: Session, notary_id: int, year: int) -> int:
    current = db.query(func.max(Case.consecutive)).filter(Case.notary_id == notary_id, Case.year == year).scalar()
    return (current or 0) + 1


def hydrate_case(db: Session, case: Case, payload: CaseCreate | CaseUpdate) -> None:
    if db.query(Notary.id).filter(Notary.id == payload.notary_id).first() is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="La notaría no existe.")

    for user_id, label in [
        (payload.current_owner_user_id, "El responsable actual"),
        (payload.client_user_id, "El cliente"),
        (payload.protocolist_user_id, "El protocolista"),
        (payload.approver_user_id, "El aprobador"),
        (payload.titular_notary_user_id, "El notario titular"),
        (payload.substitute_notary_user_id, "El notario suplente"),
    ]:
        validate_user_reference(db, user_id, label)

    state_codes = {item.code for item in get_state_definitions(db, payload.case_type)}
    if payload.current_state not in state_codes:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El estado actual no está configurado para el tipo de caso.")

    case.notary_id = payload.notary_id
    case.case_type = payload.case_type.strip()
    case.act_type = payload.act_type.strip()
    case.current_state = payload.current_state
    case.current_owner_user_id = payload.current_owner_user_id
    case.client_user_id = payload.client_user_id
    case.protocolist_user_id = payload.protocolist_user_id
    case.approver_user_id = payload.approver_user_id
    case.titular_notary_user_id = payload.titular_notary_user_id
    case.substitute_notary_user_id = payload.substitute_notary_user_id
    case.requires_client_review = payload.requires_client_review
    case.final_signed_uploaded = payload.final_signed_uploaded
    case.metadata_json = safe_json(payload.metadata_json)


def append_timeline(db: Session, case_id: int, actor_user_id: int | None, event_type: str, from_state: str | None = None, to_state: str | None = None, comment: str | None = None, metadata: dict | None = None) -> None:
    db.add(
        CaseTimelineEvent(
            case_id=case_id,
            actor_user_id=actor_user_id,
            event_type=event_type,
            from_state=from_state,
            to_state=to_state,
            comment=comment,
            metadata_json=json.dumps(metadata or {}, ensure_ascii=False) if metadata is not None else None,
        )
    )


@router.get("", response_model=list[CaseSummary])
def list_cases(
    current_state: str | None = Query(default=None),
    case_type: str | None = Query(default=None),
    notary_id: int | None = Query(default=None),
    current_owner_user_id: int | None = Query(default=None),
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    owner_alias = aliased(User)
    role_codes = get_role_codes(current_user)
    query = (
        db.query(Case)
        .options(
            joinedload(Case.notary),
            joinedload(Case.current_owner_user),
            joinedload(Case.client_user),
            joinedload(Case.protocolist_user),
            joinedload(Case.approver_user),
            joinedload(Case.titular_notary_user),
            joinedload(Case.substitute_notary_user),
        )
        .outerjoin(owner_alias, owner_alias.id == Case.current_owner_user_id)
        .order_by(Case.updated_at.desc(), Case.id.desc())
    )
    if "super_admin" not in role_codes:
        query = query.filter(Case.notary_id == current_user.default_notary_id)
    if current_state:
        query = query.filter(Case.current_state == current_state)
    if case_type:
        query = query.filter(Case.case_type == case_type)
    if notary_id:
        query = query.filter(Case.notary_id == notary_id)
    if current_owner_user_id:
        query = query.filter(Case.current_owner_user_id == current_owner_user_id)
    if q:
        search = f"%{q.strip()}%"
        query = query.join(Notary, Notary.id == Case.notary_id).filter(
            or_(
                Case.act_type.ilike(search),
                Case.case_type.ilike(search),
                Notary.notary_label.ilike(search),
                owner_alias.full_name.ilike(search),
            )
        )
    return [serialize_case_summary(item) for item in query.all()]


@router.get("/filters", response_model=CaseFilterOptions)
def get_case_filters(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cases = db.query(Case).options(joinedload(Case.notary), joinedload(Case.current_owner_user)).all()
    return CaseFilterOptions(
        case_types=sorted({item.case_type for item in cases if item.case_type}),
        act_types=sorted({item.act_type for item in cases if item.act_type}),
        states=sorted({item.current_state for item in cases if item.current_state}),
        owners=sorted({item.current_owner_user.full_name for item in cases if item.current_owner_user}),
        notaries=sorted({item.notary.notary_label for item in cases if item.notary}),
    )


@router.get("/state-definitions", response_model=list[CaseStateDefinitionSummary])
def list_state_definitions(case_type: str = Query(default=DEFAULT_CASE_TYPE), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return [CaseStateDefinitionSummary.model_validate(item) for item in get_state_definitions(db, case_type)]


@router.get("/{case_id}", response_model=CaseDetail)
def get_case(case_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    case = load_case_or_404(db, case_id)
    return serialize_case_detail(db, case)


@router.post("", response_model=CaseDetail, status_code=status.HTTP_201_CREATED)
def create_case(payload: CaseCreate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary", "protocolist", "approver", "notary"))):
    now = datetime.utcnow()
    year = payload.year or now.year
    consecutive = payload.consecutive or resolve_next_consecutive(db, payload.notary_id, year)
    case = Case(consecutive=consecutive, year=year, current_state=payload.current_state)
    hydrate_case(db, case, payload)
    db.add(case)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un caso con ese consecutivo para la notaría y año.") from exc
    append_timeline(db, case.id, current_user.id, "case_created", None, case.current_state, comment="Caso creado", metadata={"case_type": case.case_type, "act_type": case.act_type})
    db.commit()
    return serialize_case_detail(db, load_case_or_404(db, case.id))


@router.put("/{case_id}", response_model=CaseDetail)
def update_case(case_id: int, payload: CaseUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary", "protocolist", "approver", "notary"))):
    case = load_case_or_404(db, case_id)
    previous_owner = case.current_owner_user.full_name if case.current_owner_user else None
    previous_state = case.current_state
    case.consecutive = payload.consecutive
    case.year = payload.year
    hydrate_case(db, case, payload)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un caso con ese consecutivo para la notaría y año.") from exc
    if previous_state != case.current_state:
        append_timeline(db, case.id, current_user.id, "state_changed", previous_state, case.current_state, comment="Estado actualizado")
    current_owner = case.current_owner_user.full_name if case.current_owner_user else None
    if previous_owner != current_owner:
        append_timeline(db, case.id, current_user.id, "owner_changed", None, None, comment=f"Responsable actual: {current_owner or 'Sin asignar'}")
    db.commit()
    return serialize_case_detail(db, load_case_or_404(db, case.id))


@router.patch("/{case_id}/state", response_model=CaseDetail)
def update_case_state(case_id: int, payload: CaseStateUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary", "protocolist", "approver", "notary"))):
    case = load_case_or_404(db, case_id)
    allowed_states = {item.code for item in get_state_definitions(db, case.case_type)}
    if payload.current_state not in allowed_states:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El estado no está configurado para este tipo de caso.")
    previous_state = case.current_state
    case.current_state = payload.current_state
    append_timeline(db, case.id, current_user.id, "state_changed", previous_state, case.current_state, payload.comment)
    db.commit()
    return serialize_case_detail(db, load_case_or_404(db, case.id))


@router.patch("/{case_id}/owner", response_model=CaseDetail)
def update_case_owner(case_id: int, payload: CaseOwnerUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary", "protocolist", "approver", "notary"))):
    case = load_case_or_404(db, case_id)
    validate_user_reference(db, payload.current_owner_user_id, "El responsable actual")
    previous_owner = case.current_owner_user.full_name if case.current_owner_user else None
    case.current_owner_user_id = payload.current_owner_user_id
    new_owner = db.query(User).filter(User.id == payload.current_owner_user_id).first().full_name if payload.current_owner_user_id else None
    append_timeline(db, case.id, current_user.id, "owner_changed", None, None, payload.comment or f"Responsable actual: {new_owner or 'Sin asignar'}", metadata={"previous_owner": previous_owner, "new_owner": new_owner})
    db.commit()
    return serialize_case_detail(db, load_case_or_404(db, case.id))


@router.post("/{case_id}/timeline-events", response_model=CaseDetail)
def add_case_timeline_event(case_id: int, payload: CaseTimelineEventCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    case = load_case_or_404(db, case_id)
    append_timeline(
        db,
        case.id,
        current_user.id,
        "comment_added",
        case.current_state,
        case.current_state,
        payload.comment,
        metadata=json.loads(payload.metadata_json) if payload.metadata_json else None,
    )
    db.commit()
    return serialize_case_detail(db, load_case_or_404(db, case.id))
```

## File: app/modules/dashboard/router.py
```python
import json
from collections import Counter, defaultdict
from datetime import date, datetime, time, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session, joinedload

from app.core.config import get_settings
from app.core.datetime_utils import format_bogota_datetime, to_bogota
from app.core.deps import get_current_user, get_db, get_role_codes
from app.models.case import Case
from app.models.notary import Notary
from app.models.user import User
from app.schemas.dashboard import (
    DashboardAlert,
    DashboardChartDatum,
    DashboardFilterOption,
    DashboardFilterOptions,
    DashboardFilters,
    DashboardKpi,
    DashboardPilotReference,
    DashboardSystemStatusItem,
    DashboardTrendDatum,
    SuperAdminDashboardResponse,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
settings = get_settings()

FINALIZED_STATES = {"firmado_cargado", "cerrado"}
ELABORATED_STATES = {"aprobado_notario", "generado", "firmado_cargado", "cerrado"}
ALERT_STATES = {"ajustes_solicitados", "devuelto_aprobador", "rechazado_notario"}
BROKEN_TEXT_MARKERS = ("\u00c3", "\u00c2", "\u00e2", "\u0192", "\u2019", "\u201a", "\u00ad")


def clean_text(value: str | None) -> str:
    if not value:
        return ""

    result = value.strip()
    if "\\u" in result:
        try:
            result = result.encode("utf-8").decode("unicode_escape")
        except UnicodeError:
            pass

    for _ in range(4):
        if not any(marker in result for marker in BROKEN_TEXT_MARKERS):
            break

        updated = result
        for encoding in ("cp1252", "latin1"):
            try:
                candidate = updated.encode(encoding, errors="ignore").decode("utf-8", errors="ignore")
            except UnicodeError:
                continue
            if candidate and candidate != updated:
                updated = candidate

        if updated == result:
            break
        result = updated

    return result.replace("  ", " ").strip()


def safe_metadata(value: str | None) -> dict:
    if not value:
        return {}
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        return {}


def top_counter(counter: Counter[str], *, limit: int = 6, highlight_label: str | None = None) -> list[DashboardChartDatum]:
    items = counter.most_common(limit)
    clean_highlight = clean_text(highlight_label)
    return [
        DashboardChartDatum(label=clean_text(label), value=value, highlight=clean_text(label) == clean_highlight)
        for label, value in items
    ]


def infer_online_users(cases: list[Case], active_users: list[User]) -> int:
    recent_threshold = datetime.now(timezone.utc) - timedelta(days=14)
    online_ids: set[int] = set()
    for case in cases:
        if case.updated_at and case.updated_at >= recent_threshold:
            for user_id in [
                case.current_owner_user_id,
                case.protocolist_user_id,
                case.approver_user_id,
                case.titular_notary_user_id,
                case.substitute_notary_user_id,
                case.client_user_id,
            ]:
                if user_id is not None:
                    online_ids.add(user_id)
    if online_ids:
        return len(online_ids)
    return min(len(active_users), 3)


@router.get("/superadmin", response_model=SuperAdminDashboardResponse)
def get_superadmin_dashboard(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    notary_id: int | None = Query(default=None),
    state: str | None = Query(default=None),
    act_type: str | None = Query(default=None),
    owner_user_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role_codes = get_role_codes(current_user)
    is_super_admin = "super_admin" in role_codes
    scope_notary_id = None if is_super_admin else current_user.default_notary_id
    effective_notary_id = notary_id if is_super_admin else scope_notary_id

    query = (
        db.query(Case)
        .options(
            joinedload(Case.notary),
            joinedload(Case.current_owner_user),
            joinedload(Case.client_user),
            joinedload(Case.protocolist_user),
            joinedload(Case.approver_user),
            joinedload(Case.titular_notary_user),
            joinedload(Case.substitute_notary_user),
        )
        .order_by(Case.updated_at.desc(), Case.id.desc())
    )

    if date_from is not None:
        query = query.filter(Case.updated_at >= datetime.combine(date_from, time.min))
    if date_to is not None:
        query = query.filter(Case.updated_at <= datetime.combine(date_to, time.max))
    if effective_notary_id is not None:
        query = query.filter(Case.notary_id == effective_notary_id)
    if state:
        query = query.filter(Case.current_state == state)
    if act_type:
        query = query.filter(Case.act_type == act_type)
    if owner_user_id is not None:
        query = query.filter(Case.current_owner_user_id == owner_user_id)

    cases = query.all()
    all_users_query = db.query(User).options(joinedload(User.default_notary))
    all_notaries_query = db.query(Notary)
    if not is_super_admin:
        all_users_query = all_users_query.filter(User.default_notary_id == scope_notary_id)
        all_notaries_query = all_notaries_query.filter(Notary.id == scope_notary_id)
    all_users = all_users_query.all()
    all_notaries = all_notaries_query.order_by(Notary.municipality.asc(), Notary.notary_label.asc()).all()
    active_users = [user for user in all_users if user.is_active]
    pilot_notary = (
        db.query(Notary)
        .filter(Notary.id == scope_notary_id)
        .first()
        if not is_super_admin
        else db.query(Notary)
        .filter(Notary.department == "Antioquia", Notary.municipality == "Caldas")
        .order_by(Notary.id.asc())
        .first()
    )

    notary_counter: Counter[str] = Counter()
    state_counter: Counter[str] = Counter()
    act_counter: Counter[str] = Counter()
    owner_counter: Counter[str] = Counter()
    trend_counter: defaultdict[str, int] = defaultdict(int)
    active_project_counter: Counter[str] = Counter()

    for case in cases:
        notary_label = clean_text(case.notary.notary_label if case.notary else "Sin notar\u00eda")
        notary_counter[notary_label] += 1
        state_counter[clean_text(case.current_state)] += 1
        act_counter[clean_text(case.act_type)] += 1
        if case.current_owner_user:
            owner_counter[clean_text(case.current_owner_user.full_name)] += 1
        localized_updated_at = to_bogota(case.updated_at) or case.updated_at
        trend_counter[localized_updated_at.strftime("%d %b")] += 1
        metadata = safe_metadata(case.metadata_json)
        project = clean_text(str(metadata.get("project") or metadata.get("radication") or ""))
        if project and case.current_state not in FINALIZED_STATES:
            active_project_counter[project] += 1

    in_progress_cases = sum(1 for case in cases if case.current_state not in FINALIZED_STATES)
    elaborated_cases = sum(1 for case in cases if case.current_state in ELABORATED_STATES)
    finalized_cases = sum(1 for case in cases if case.current_state in FINALIZED_STATES)
    active_lots = len(active_project_counter)
    critical_case_alerts = [case for case in cases if case.current_state in ALERT_STATES]
    critical_signed_alerts = [case for case in cases if not case.final_signed_uploaded and case.current_state in {"aprobado_notario", "generado", "firmado_cargado"}]
    online_users = infer_online_users(cases, active_users)

    alerts: list[DashboardAlert] = []
    if critical_case_alerts:
        alerts.append(
            DashboardAlert(
                level="critical",
                title="Estados con bloqueo operativo",
                detail=f"{len(critical_case_alerts)} casos est\u00e1n en ajustes, devoluci\u00f3n o rechazo notarial.",
            )
        )
    if critical_signed_alerts:
        alerts.append(
            DashboardAlert(
                level="warning",
                title="Firmados pendientes de carga",
                detail=f"{len(critical_signed_alerts)} casos ya avanzaron pero a\u00fan no tienen firmado final cargado.",
            )
        )
    if pilot_notary is not None:
        alerts.append(
            DashboardAlert(
                level="info",
                title="Piloto operativo real",
                detail="Caldas, Antioquia queda visible como referencia actual de operaci\u00f3n EasyPro 1.",
            )
        )

    db.execute(text("SELECT 1"))
    latest_import_notary_query = db.query(Notary)
    if not is_super_admin:
        latest_import_notary_query = latest_import_notary_query.filter(Notary.id == scope_notary_id)
    else:
        latest_import_notary_query = latest_import_notary_query.filter(Notary.department == "Antioquia")
    latest_import_notary = latest_import_notary_query.order_by(Notary.updated_at.desc()).first()
    latest_import_reference = None
    if latest_import_notary is not None and latest_import_notary.updated_at is not None:
        latest_import_reference = (
            f"{format_bogota_datetime(latest_import_notary.updated_at) or ''} | "
            f"{clean_text(latest_import_notary.municipality)} | {clean_text(latest_import_notary.notary_label)}"
        )

    pilot_reference = None
    if pilot_notary is not None:
        pilot_cases = [case for case in cases if case.notary_id == pilot_notary.id]
        pilot_reference = DashboardPilotReference(
            notary_id=pilot_notary.id,
            notary_label=clean_text(pilot_notary.notary_label),
            municipality=clean_text(pilot_notary.municipality),
            department=clean_text(pilot_notary.department),
            total_cases=len(pilot_cases),
            active_cases=sum(1 for case in pilot_cases if case.current_state not in FINALIZED_STATES),
            finalized_cases=sum(1 for case in pilot_cases if case.current_state in FINALIZED_STATES),
            notes="Notar\u00eda piloto real referenciada para demo ejecutiva y validaci\u00f3n operativa.",
        )

    system_status = [
        DashboardSystemStatusItem(key="backend", label="Backend", status="online", detail="API operando en 127.0.0.1:8000"),
        DashboardSystemStatusItem(key="frontend", label="Frontend", status="online", detail=f"Shell disponible en {settings.frontend_url}"),
        DashboardSystemStatusItem(key="database", label="Base de datos", status="online", detail="Consulta de verificaci\u00f3n completada."),
        DashboardSystemStatusItem(key="auth", label="Autenticaci\u00f3n", status="online", detail=f"Sesi\u00f3n validada para {current_user.email}"),
        DashboardSystemStatusItem(key="imports", label="\u00daltima importaci\u00f3n relevante", status="online", detail=latest_import_reference or "Sin referencia de importaci\u00f3n inferida."),
        DashboardSystemStatusItem(key="alerts", label="Alertas cr\u00edticas", status="warning" if alerts else "online", detail=f"{len(alerts)} alertas visibles en el tablero."),
    ]

    notary_options = [DashboardFilterOption(id=None, label="Todas las notar\u00edas")] + [
        DashboardFilterOption(id=notary.id, label=f"{clean_text(notary.municipality)} | {clean_text(notary.notary_label)}")
        for notary in all_notaries
    ]
    state_options = [DashboardFilterOption(id=None, label="Todos los estados")] + [
        DashboardFilterOption(id=None, label=clean_text(item[0])) for item in sorted(db.query(Case.current_state).distinct().all()) if item[0]
    ]
    act_options = [DashboardFilterOption(id=None, label="Todos los actos")] + [
        DashboardFilterOption(id=None, label=clean_text(item[0])) for item in sorted(db.query(Case.act_type).distinct().all()) if item[0]
    ]
    owner_options = [DashboardFilterOption(id=None, label="Todos los responsables")] + [
        DashboardFilterOption(id=user.id, label=clean_text(user.full_name)) for user in active_users
    ]

    pilot_label = clean_text(pilot_notary.notary_label) if pilot_notary else None

    return SuperAdminDashboardResponse(
        generated_at=datetime.now(timezone.utc),
        filters=DashboardFilters(
            date_from=date_from,
            date_to=date_to,
            notary_id=notary_id,
            state=state,
            act_type=act_type,
            owner_user_id=owner_user_id,
        ),
        filter_options=DashboardFilterOptions(
            notaries=notary_options,
            states=state_options,
            act_types=act_options,
            owners=owner_options,
        ),
        kpis=[
            DashboardKpi(key="in_progress", label="Casos en tr\u00e1mite", value=in_progress_cases, detail="Casos activos dentro del flujo documental."),
            DashboardKpi(key="elaborated", label="Casos elaborados", value=elaborated_cases, detail="Casos ya generados o aprobados para cierre."),
            DashboardKpi(key="finalized", label="Casos finalizados", value=finalized_cases, detail="Casos firmados o cerrados.", tone="success"),
            DashboardKpi(key="users_total", label="Usuarios totales", value=len(all_users), detail="Usuarios registrados en el sistema."),
            DashboardKpi(key="users_active", label="Usuarios activos", value=len(active_users), detail="Usuarios habilitados para operar."),
            DashboardKpi(key="users_online", label="Usuarios en l\u00ednea", value=online_users, detail="M\u00e9trica inferida a partir de actividad reciente."),
            DashboardKpi(key="lots", label="Lotes en curso", value=active_lots, detail="Lotes inferidos por proyectos activos."),
            DashboardKpi(
                key="critical_alerts",
                label="Alertas cr\u00edticas",
                value=len(alerts),
                detail="Bloqueos y pendientes que requieren atenci\u00f3n.",
                tone="critical" if alerts else "default",
            ),
        ],
        documents_by_notary=top_counter(notary_counter, limit=8, highlight_label=pilot_label),
        documents_by_state=top_counter(state_counter, limit=8),
        documents_by_act_type=top_counter(act_counter, limit=8),
        temporal_trend=[DashboardTrendDatum(label=label, value=value) for label, value in sorted(trend_counter.items())],
        owner_ranking=top_counter(owner_counter, limit=6),
        operational_focus=[
            DashboardChartDatum(label=clean_text(label), value=value, highlight=clean_text(label) == "EasyPro 1 Caldas")
            for label, value in active_project_counter.most_common(6)
        ],
        critical_alerts=alerts,
        system_status=system_status,
        pilot_reference=pilot_reference,
        latest_import_reference=latest_import_reference,
    )
```

## File: app/modules/document_flow/router.py
```python
from __future__ import annotations

import json
import shutil
import io
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse, RedirectResponse, StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user, get_role_codes, get_db, require_roles
from app.models.case import Case
from app.models.case_act import CaseAct
from app.models.case_act_data import CaseActData
from app.models.case_client_comment import CaseClientComment
from app.models.case_document import CaseDocument
from app.models.case_document_version import CaseDocumentVersion
from app.models.case_internal_note import CaseInternalNote
from app.models.case_participant import CaseParticipant
from app.models.case_timeline_event import CaseTimelineEvent
from app.models.case_workflow_event import CaseWorkflowEvent
from app.models.document_template import DocumentTemplate
from app.models.legal_entity import LegalEntity
from app.models.notary import Notary
from app.models.numbering_sequence import NumberingSequence
from app.models.person import Person
from app.models.user import User
from app.schemas.case import (
    ApprovalRequest,
    CaseActDataPayload,
    CaseActDataSummary,
    CaseCommentCreate,
    CaseCommentSummary,
    CaseCreateFromTemplate,
    CaseDetail,
    CaseDocumentSummary,
    CaseDocumentVersionSummary,
    CaseInternalNoteCreate,
    CaseParticipantPayload,
    CaseParticipantSummary,
    CaseTimelineEventCreate,
    CaseTimelineEventSummary,
    CaseWorkflowEventSummary,
    DraftGenerationRequest,
    ExportRequest,
    FinalUploadRequest,
    GariGenerationRequest,
)
from app.schemas.act_catalog import CaseActOut, CaseActsPayload
from app.schemas.person import PersonCreate
from app.schemas.template import TemplateFieldSummary, TemplateRequiredRoleSummary, TemplateSummary
from app.services.document_generation import build_case_text_snapshot, extract_text_from_docx, generate_plain_pdf, render_docx_template, serialize_placeholder_snapshot
from app.services.gari_document_service import (
    build_gari_docx_buffer,
    generate_notarial_document,
    resolver_escritura_desde_template,
    save_gari_document_as_docx,
)
from app.services.storage import next_case_file_path, save_base64_file
from app.modules.act_catalog.router import LEGACY_CASE_ACTS_BY_VARIANT

router = APIRouter(prefix="/document-flow", tags=["document-flow"])

NOTARY_APPROVER_ROLES = {"titular_notary", "substitute_notary"}


def guess_media_type(path: Path) -> str:
    ext = path.suffix.lower()
    types = {
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".pdf": "application/pdf",
        ".doc": "application/msword",
        ".txt": "text/plain",
    }
    return types.get(ext, "application/octet-stream")


def safe_json(value: str | None) -> str:
    if value is None or not value.strip():
        return "{}"
    try:
        return json.dumps(json.loads(value), ensure_ascii=False)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El contenido debe ser JSON válido.") from exc


def detail_query(db: Session):
    return db.query(Case).options(
        joinedload(Case.notary),
        joinedload(Case.template).joinedload(DocumentTemplate.required_roles),
        joinedload(Case.template).joinedload(DocumentTemplate.fields),
        joinedload(Case.current_owner_user),
        joinedload(Case.created_by_user),
        joinedload(Case.client_user),
        joinedload(Case.protocolist_user),
        joinedload(Case.approver_user),
        joinedload(Case.titular_notary_user),
        joinedload(Case.substitute_notary_user),
        joinedload(Case.approved_by_user),
        joinedload(Case.timeline_events).joinedload(CaseTimelineEvent.actor_user),
        joinedload(Case.workflow_events).joinedload(CaseWorkflowEvent.actor_user),
        joinedload(Case.participants).joinedload(CaseParticipant.person),
        joinedload(Case.participants).joinedload(CaseParticipant.legal_entity),
        joinedload(Case.acts),
        joinedload(Case.act_data),
        joinedload(Case.client_comments).joinedload(CaseClientComment.created_by_user),
        joinedload(Case.internal_notes).joinedload(CaseInternalNote.created_by_user),
        joinedload(Case.documents).joinedload(CaseDocument.versions).joinedload(CaseDocumentVersion.created_by_user),
    )


def load_case_or_404(db: Session, case_id: int) -> Case:
    case = db.query(Case).filter(Case.id == case_id).first()
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Minuta no encontrada.")
    return case


@router.put("/cases/{case_id}/acts", response_model=list[CaseActOut])
def replace_case_acts(
    case_id: int,
    payload: CaseActsPayload,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    case = load_case_or_404(db, case_id)
    db.query(CaseAct).filter(CaseAct.case_id == case.id).delete(synchronize_session=False)
    db.flush()

    new_acts = []
    for act in payload.acts:
        new_act = CaseAct(
            case_id=case.id,
            act_code=act.code,
            act_label=act.label,
            act_order=act.act_order,
            roles_json=act.roles_json,
        )
        db.add(new_act)
        new_acts.append(new_act)

    db.commit()
    for item in new_acts:
        db.refresh(item)
    return new_acts


@router.get("/cases/{case_id}/acts", response_model=list[CaseActOut])
def get_case_acts(
    case_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    case = load_case_or_404(db, case_id)
    acts = db.query(CaseAct).filter(CaseAct.case_id == case.id).order_by(CaseAct.act_order.asc()).all()
    return acts


def serialize_template(template: DocumentTemplate | None) -> TemplateSummary | None:
    if template is None:
        return None
    return TemplateSummary(
        id=template.id,
        name=template.name,
        slug=template.slug,
        case_type=template.case_type,
        document_type=template.document_type,
        description=template.description,
        scope_type=template.scope_type,
        notary_id=template.notary_id,
        notary_label=template.notary.notary_label if template.notary else None,
        is_active=template.is_active,
        source_filename=template.source_filename,
        storage_path=template.storage_path,
        internal_variable_map_json=template.internal_variable_map_json,
        created_at=template.created_at,
        updated_at=template.updated_at,
        required_roles=[TemplateRequiredRoleSummary.model_validate(item) for item in template.required_roles],
        fields=[TemplateFieldSummary.model_validate(item) for item in template.fields],
    )


def serialize_timeline(item: CaseTimelineEvent) -> CaseTimelineEventSummary:
    return CaseTimelineEventSummary(
        id=item.id,
        event_type=item.event_type,
        from_state=item.from_state,
        to_state=item.to_state,
        comment=item.comment,
        metadata_json=item.metadata_json,
        actor_user_id=item.actor_user_id,
        actor_user_name=item.actor_user.full_name if item.actor_user else None,
        created_at=item.created_at,
    )


def serialize_workflow(item: CaseWorkflowEvent) -> CaseWorkflowEventSummary:
    return CaseWorkflowEventSummary(
        id=item.id,
        event_type=item.event_type,
        actor_user_id=item.actor_user_id,
        actor_user_name=item.actor_user.full_name if item.actor_user else None,
        actor_role_code=item.actor_role_code,
        from_state=item.from_state,
        to_state=item.to_state,
        field_name=item.field_name,
        old_value=item.old_value,
        new_value=item.new_value,
        comment=item.comment,
        approved_version_id=item.approved_version_id,
        metadata_json=item.metadata_json,
        created_at=item.created_at,
    )


def serialize_comment(item: CaseClientComment | CaseInternalNote, field_name: str) -> CaseCommentSummary:
    return CaseCommentSummary(
        id=item.id,
        created_by_user_id=item.created_by_user_id,
        created_by_user_name=item.created_by_user.full_name if item.created_by_user else None,
        comment=getattr(item, field_name, None) if field_name == "comment" else None,
        note=getattr(item, field_name, None) if field_name == "note" else None,
        created_at=item.created_at,
    )


def serialize_document_version(case_id: int, document_id: int, version: CaseDocumentVersion) -> CaseDocumentVersionSummary:
    return CaseDocumentVersionSummary(
        id=version.id,
        version_number=version.version_number,
        file_format=version.file_format,
        storage_path=version.storage_path,
        original_filename=version.original_filename,
        generated_from_template_id=version.generated_from_template_id,
        created_by_user_id=version.created_by_user_id,
        created_by_user_name=version.created_by_user.full_name if version.created_by_user else None,
        placeholder_snapshot_json=version.placeholder_snapshot_json,
        created_at=version.created_at,
        download_url=f"/api/v1/document-flow/cases/{case_id}/documents/{document_id}/versions/{version.id}/download",
    )


def serialize_document(case_id: int, document: CaseDocument) -> CaseDocumentSummary:
    latest = max(document.versions, key=lambda version: version.version_number, default=None)
    return CaseDocumentSummary(
        id=document.id,
        category=document.category,
        title=document.title,
        current_version_number=document.current_version_number,
        versions=[serialize_document_version(case_id, document.id, latest)] if latest else [],
    )


def serialize_participant(item: CaseParticipant) -> CaseParticipantSummary:
    return CaseParticipantSummary(
        id=item.id,
        role_code=item.role_code,
        role_label=item.role_label,
        person_id=item.person_id,
        person=item.person,
        snapshot_json=item.snapshot_json,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def serialize_case_detail(case: Case) -> CaseDetail:
    return CaseDetail(
        id=case.id,
        notary_id=case.notary_id,
        notary_label=case.notary.notary_label,
        template_id=case.template_id,
        template_name=case.template.name if case.template else None,
        template=serialize_template(case.template),
        case_type=case.case_type,
        act_type=case.act_type,
        consecutive=case.consecutive,
        year=case.year,
        internal_case_number=case.internal_case_number,
        official_deed_number=case.official_deed_number,
        official_deed_year=case.official_deed_year,
        current_state=case.current_state,
        current_owner_user_id=case.current_owner_user_id,
        current_owner_user_name=case.current_owner_user.full_name if case.current_owner_user else None,
        created_by_user_id=case.created_by_user_id,
        created_by_user_name=case.created_by_user.full_name if case.created_by_user else None,
        client_user_id=case.client_user_id,
        client_user_name=case.client_user.full_name if case.client_user else None,
        protocolist_user_id=case.protocolist_user_id,
        protocolist_user_name=case.protocolist_user.full_name if case.protocolist_user else None,
        approver_user_id=case.approver_user_id,
        approver_user_name=case.approver_user.full_name if case.approver_user else None,
        titular_notary_user_id=case.titular_notary_user_id,
        titular_notary_user_name=case.titular_notary_user.full_name if case.titular_notary_user else None,
        substitute_notary_user_id=case.substitute_notary_user_id,
        substitute_notary_user_name=case.substitute_notary_user.full_name if case.substitute_notary_user else None,
        requires_client_review=case.requires_client_review,
        final_signed_uploaded=case.final_signed_uploaded,
        approved_at=case.approved_at,
        approved_by_user_id=case.approved_by_user_id,
        approved_by_user_name=case.approved_by_user.full_name if case.approved_by_user else None,
        approved_by_role_code=case.approved_by_role_code,
        approved_document_version_id=case.approved_document_version_id,
        metadata_json=case.metadata_json,
        created_at=case.created_at,
        updated_at=case.updated_at,
        state_definitions=[],
        timeline_events=[serialize_timeline(item) for item in case.timeline_events],
        workflow_events=[serialize_workflow(item) for item in case.workflow_events],
        participants=[serialize_participant(item) for item in case.participants],
        act_data=CaseActDataSummary.model_validate(case.act_data) if case.act_data else None,
        client_comments=[serialize_comment(item, "comment") for item in case.client_comments],
        internal_notes=[serialize_comment(item, "note") for item in case.internal_notes],
        documents=[serialize_document(case.id, item) for item in case.documents],
    )


def append_timeline(db: Session, case_id: int, actor_user_id: int | None, event_type: str, from_state: str | None = None, to_state: str | None = None, comment: str | None = None, metadata: dict | None = None) -> None:
    db.add(CaseTimelineEvent(case_id=case_id, actor_user_id=actor_user_id, event_type=event_type, from_state=from_state, to_state=to_state, comment=comment, metadata_json=json.dumps(metadata or {}, ensure_ascii=False) if metadata is not None else None))


def append_workflow(db: Session, case: Case, actor_user: User | None, event_type: str, actor_role_code: str | None = None, field_name: str | None = None, old_value: str | None = None, new_value: str | None = None, comment: str | None = None, approved_version_id: int | None = None, metadata: dict | None = None, from_state: str | None = None, to_state: str | None = None) -> None:
    db.add(CaseWorkflowEvent(case_id=case.id, actor_user_id=actor_user.id if actor_user else None, actor_role_code=actor_role_code, event_type=event_type, field_name=field_name, old_value=old_value, new_value=new_value, comment=comment, approved_version_id=approved_version_id, metadata_json=json.dumps(metadata or {}, ensure_ascii=False) if metadata is not None else None, from_state=from_state, to_state=to_state))


def resolve_existing_max_sequence(db: Session, sequence_type: str, notary_id: int, year: int) -> int:
    if sequence_type == "internal_case":
        return int(
            db.query(func.max(Case.consecutive))
            .filter(Case.notary_id == notary_id, Case.year == year)
            .scalar()
            or 0
        )
    if sequence_type == "official_deed":
        values = (
            db.query(Case.official_deed_number)
            .filter(Case.notary_id == notary_id, Case.official_deed_year == year, Case.official_deed_number.isnot(None))
            .all()
        )
        max_value = 0
        for (official_number,) in values:
            if not official_number:
                continue
            prefix = str(official_number).split("-", 1)[0]
            if prefix.isdigit():
                max_value = max(max_value, int(prefix))
        return max_value
    return 0


def resolve_next_sequence(db: Session, sequence_type: str, notary_id: int, year: int) -> int:
    sequence = db.query(NumberingSequence).filter(NumberingSequence.sequence_type == sequence_type, NumberingSequence.notary_id == notary_id, NumberingSequence.year == year).first()
    existing_max = resolve_existing_max_sequence(db, sequence_type, notary_id, year)
    if sequence is None:
        sequence = NumberingSequence(sequence_type=sequence_type, notary_id=notary_id, year=year, current_value=existing_max)
        db.add(sequence)
        db.flush()
    elif sequence.current_value < existing_max:
        sequence.current_value = existing_max
        db.flush()
    sequence.current_value += 1
    db.flush()
    return sequence.current_value


def resolve_or_create_person(db: Session, payload: PersonCreate) -> Person:
    person = db.query(Person).filter(Person.document_type == payload.document_type.strip().upper(), Person.document_number == payload.document_number.strip()).first()
    if person is None:
        person = Person()
        db.add(person)
    person.document_type = payload.document_type.strip().upper()
    person.document_number = payload.document_number.strip()
    person.full_name = payload.full_name.strip()
    person.sex = payload.sex.strip() if payload.sex else None
    person.nationality = payload.nationality.strip() if payload.nationality else None
    person.marital_status = payload.marital_status.strip() if payload.marital_status else None
    person.profession = payload.profession.strip() if payload.profession else None
    person.municipality = payload.municipality.strip() if payload.municipality else None
    person.is_transient = payload.is_transient
    person.phone = payload.phone.strip() if payload.phone else None
    person.address = payload.address.strip() if payload.address else None
    person.email = str(payload.email).strip().lower() if payload.email else None
    person.metadata_json = safe_json(payload.metadata_json)
    db.flush()
    return person


def build_placeholder_replacements(case: Case) -> dict[str, str]:
    replacements: dict[str, str] = {}
    participant_map = {item.role_code: item.person for item in case.participants}
    for role_code, prefix in {"poderdante": "PODERDANTE", "apoderado": "APODERADO"}.items():
        person = participant_map.get(role_code)
        if person is None:
            continue
        sex_label = "mujer" if (person.sex or "").upper().startswith("F") else "hombre"
        replacements[f"{{{{NOMBRE_{prefix}}}}}"] = person.full_name
        replacements[f"{{{{TIPO_DOCUMENTO_{prefix}}}}}"] = person.document_type
        replacements[f"{{{{NUMERO_DOCUMENTO_{prefix}}}}}"] = person.document_number
        replacements[f"{{{{NACIONALIDAD_{prefix}}}}}"] = person.nationality or ""
        replacements[f"{{{{ESTADO_CIVIL_{prefix}}}}}"] = person.marital_status or ""
        replacements[f"{{{{PROFESION_U_OFICIO_{prefix}}}}}"] = person.profession or ""
        replacements[f"{{{{MUNICIPIO_DE_DOMICILIO_{prefix}}}}}"] = person.municipality or ""
        replacements[f"{{{{SELECCIONE_SI_{prefix}_ESTA_DE_TRANSITO}}}}"] = "SI" if person.is_transient else "NO"
        replacements[f"{{{{TELEFONO_{prefix}}}}}"] = person.phone or ""
        replacements[f"{{{{DIRECCION_{prefix}}}}}"] = person.address or ""
        replacements[f"{{{{EMAIL_{prefix}}}}}"] = person.email or ""
        replacements[f"{{{{{prefix}_ES_HOMBRE_O_MUJER}}}}"] = sex_label
    act_data = json.loads(case.act_data.data_json if case.act_data else "{}")
    field_map = {
        "dia_elaboracion": "DIA_ELABORACION_ESCRITURA",
        "mes_elaboracion": "MES_ELABORACION_ESCRITURA",
        "ano_elaboracion": "ANO_ELABORACION_ESCRITURA",
        "derechos_notariales": "DERECHOS_NOTARIALES",
        "iva": "IVA",
        "aporte_superintendencia": "APORTE_SUPERINTENDENCIA",
        "fondo_notariado": "FONDO_NOTARIADO",
        "consecutivos_hojas_papel_notarial": "CONSECUTIVOS_HOJAS_PAPEL_NOTARIAL",
        "extension": "EXTENSION",
    }
    for key, placeholder in field_map.items():
        value = act_data.get(key, "")
        if isinstance(value, (int, float)) and key in {"derechos_notariales", "iva", "aporte_superintendencia", "fondo_notariado"}:
            value = f"${value:,.0f}".replace(",", ".")
        replacements[f"{{{{{placeholder}}}}}"] = str(value)
    replacements["{{NUMERO_ESCRITURA}}"] = case.official_deed_number or "PENDIENTE ASIGNACIÓN"
    return replacements


def get_or_create_document(db: Session, case: Case, category: str, title: str) -> CaseDocument:
    document = db.query(CaseDocument).filter(CaseDocument.case_id == case.id, CaseDocument.category == category).first()
    if document is None:
        document = CaseDocument(case_id=case.id, category=category, title=title, current_version_number=0)
        db.add(document)
        db.flush()
    else:
        document.title = title
    return document


def latest_document_version(case: Case, category: str, file_format: str | None = None) -> CaseDocumentVersion | None:
    for document in case.documents:
        if document.category != category:
            continue
        for version in document.versions:
            if file_format is None or version.file_format == file_format:
                return version
    return None


def add_document_version(db: Session, case: Case, category: str, title: str, file_format: str, source_path: str | Path, original_filename: str, created_by_user_id: int | None, template_id: int | None = None, placeholder_snapshot_json: str = "{}") -> CaseDocumentVersion:
    document = get_or_create_document(db, case, category, title)
    version_number = document.current_version_number + 1

    source_raw = str(source_path)
    is_remote_source = source_raw.startswith("http://") or source_raw.startswith("https://")
    if is_remote_source:
        storage_path = source_raw
        stored_filename = original_filename
    else:
        target_path = next_case_file_path(case.id, category, version_number, file_format, original_filename)
        source = Path(source_path)
        if source != target_path:
            shutil.copy2(source, target_path)
        storage_path = str(target_path)
        stored_filename = target_path.name

    document.current_version_number = version_number
    version = CaseDocumentVersion(case_document_id=document.id, version_number=version_number, file_format=file_format, storage_path=storage_path, original_filename=stored_filename, generated_from_template_id=template_id, placeholder_snapshot_json=placeholder_snapshot_json, created_by_user_id=created_by_user_id)
    db.add(version)
    db.flush()
    return version


def generate_draft_for_case(db: Session, case: Case, current_user: User, comment: str | None = None) -> CaseDocumentVersion:
    if case.template is None or not case.template.storage_path:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El caso no tiene una plantilla documental disponible.")
    required_roles = {item.role_code for item in case.template.required_roles if item.is_required}
    provided_roles = {item.role_code for item in case.participants}
    missing = sorted(required_roles - provided_roles)
    if missing:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Faltan intervinientes obligatorios: {', '.join(missing)}.")
    if case.act_data is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Debes registrar los datos del acto antes de generar el borrador.")
    replacements = build_placeholder_replacements(case)
    temp_output = next_case_file_path(case.id, "draft-temp", 1, "docx", f"draft_case_{case.id}.docx")
    render_docx_template(case.template.storage_path, temp_output, replacements)
    version = add_document_version(db, case, "draft", "Borrador documental", "docx", temp_output, f"{case.template.slug}.docx", current_user.id, case.template_id, serialize_placeholder_snapshot(replacements))
    previous_state = case.current_state
    if case.current_state in {"borrador", "en_diligenciamiento", "revision_cliente", "ajustes_solicitados"}:
        case.current_state = "generado"
    append_timeline(db, case.id, current_user.id, "draft_generated", previous_state, case.current_state, comment or "Borrador generado")
    append_workflow(db, case, current_user, "draft_generated", actor_role_code="protocolist", comment=comment or "Borrador generado", approved_version_id=version.id, metadata={"version": version.version_number}, from_state=previous_state, to_state=case.current_state)
    return version


@router.post("/cases/from-template", response_model=CaseDetail, status_code=status.HTTP_201_CREATED)
def create_case_from_template(payload: CaseCreateFromTemplate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary", "protocolist", "approver", "notary"))):
    template = db.query(DocumentTemplate).options(joinedload(DocumentTemplate.required_roles), joinedload(DocumentTemplate.fields), joinedload(DocumentTemplate.notary)).filter(DocumentTemplate.id == payload.template_id, DocumentTemplate.is_active.is_(True)).first()
    if template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La plantilla seleccionada no existe o está inactiva.")
    if db.query(Notary.id).filter(Notary.id == payload.notary_id).first() is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="La notaría seleccionada no existe.")
    year = datetime.utcnow().year
    consecutive = resolve_next_sequence(db, "internal_case", payload.notary_id, year)
    case = Case(notary_id=payload.notary_id, template_id=template.id, created_by_user_id=current_user.id, case_type=template.case_type, act_type=template.document_type, consecutive=consecutive, year=year, internal_case_number=f"CAS-{year}-{consecutive:04d}", current_state="borrador", current_owner_user_id=payload.current_owner_user_id or payload.protocolist_user_id or current_user.id, client_user_id=payload.client_user_id, protocolist_user_id=payload.protocolist_user_id, approver_user_id=payload.approver_user_id, titular_notary_user_id=payload.titular_notary_user_id, substitute_notary_user_id=payload.substitute_notary_user_id, requires_client_review=payload.requires_client_review, final_signed_uploaded=False, metadata_json=safe_json(payload.metadata_json))
    db.add(case)
    db.flush()
    append_timeline(db, case.id, current_user.id, "case_created", None, case.current_state, "Caso creado desde plantilla", {"template_id": template.id})
    append_workflow(db, case, current_user, "case_created", actor_role_code="protocolist", comment="Caso creado desde plantilla", metadata={"template_id": template.id})
    db.commit()
    return serialize_case_detail(load_case_or_404(db, case.id))


@router.get("/cases/{case_id}", response_model=CaseDetail)
def get_case_detail(case_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return serialize_case_detail(load_case_or_404(db, case_id))


@router.put("/cases/{case_id}/participants", response_model=CaseDetail)
def save_case_participants(case_id: int, payload: list[CaseParticipantPayload], db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary", "protocolist", "approver", "notary"))):
    case = load_case_or_404(db, case_id)
    if not payload:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Debes agregar al menos un interviniente.")
    case.participants.clear()
    db.flush()
    person_ids: list[int] = []
    for item in payload:
        person = None
        if item.person_id is not None:
            person = db.query(Person).filter(Person.id == item.person_id).first()
            if person is None:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"No existe la persona seleccionada para {item.role_label}.")
        elif item.person is not None:
            person = resolve_or_create_person(db, item.person)
        if person is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Debes seleccionar o crear la persona para {item.role_label}.")
        person_ids.append(person.id)
        snapshot = {"document_type": person.document_type, "document_number": person.document_number, "full_name": person.full_name, "sex": person.sex, "nationality": person.nationality, "marital_status": person.marital_status, "profession": person.profession, "municipality": person.municipality, "is_transient": person.is_transient, "phone": person.phone, "address": person.address, "email": person.email}
        case_participant = CaseParticipant(case_id=case.id, person_id=person.id, role_code=item.role_code.strip(), role_label=item.role_label.strip(), snapshot_json=json.dumps(snapshot, ensure_ascii=False))
        if item.legal_entity_id is not None:
            legal_entity = db.query(LegalEntity).filter(LegalEntity.id == item.legal_entity_id).first()
            if legal_entity is None:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"No existe la entidad jurídica seleccionada para {item.role_label}.")
            case_participant.legal_entity_id = legal_entity.id
            snapshot["represented_entity_name"] = legal_entity.name
            snapshot["represented_entity_nit"] = legal_entity.nit
            case_participant.snapshot_json = json.dumps(snapshot, ensure_ascii=False)
        case.participants.append(case_participant)
    if len(person_ids) != len(set(person_ids)):
        append_workflow(db, case, current_user, "participants_warning", actor_role_code="protocolist", comment="Poderdante y apoderado corresponden a la misma persona.")
    append_workflow(db, case, current_user, "participants_saved", actor_role_code="protocolist", comment="Intervinientes actualizados")
    db.commit()
    return serialize_case_detail(load_case_or_404(db, case.id))


@router.put("/cases/{case_id}/act-data", response_model=CaseDetail)
def save_case_act_data(case_id: int, payload: CaseActDataPayload, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary", "protocolist", "approver", "notary"))):
    case = load_case_or_404(db, case_id)
    if case.act_data is None:
        case.act_data = CaseActData(case_id=case.id, data_json="{}")
        db.add(case.act_data)
        db.flush()
    old_value = case.act_data.data_json
    case.act_data.data_json = safe_json(payload.data_json)
    append_workflow(db, case, current_user, "act_data_saved", actor_role_code="protocolist", field_name="act_data", old_value=old_value, new_value=case.act_data.data_json, comment="Datos del acto actualizados")
    db.commit()
    return serialize_case_detail(load_case_or_404(db, case.id))


@router.post("/cases/{case_id}/client-comments", response_model=CaseDetail)
def add_client_comment(case_id: int, payload: CaseCommentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    case = load_case_or_404(db, case_id)
    db.add(CaseClientComment(case_id=case.id, created_by_user_id=current_user.id, comment=payload.comment.strip()))
    append_workflow(db, case, current_user, "client_comment_added", actor_role_code="client" if "client" in get_role_codes(current_user) else None, comment=payload.comment.strip())
    db.commit()
    return serialize_case_detail(load_case_or_404(db, case.id))


@router.post("/cases/{case_id}/internal-notes", response_model=CaseDetail)
def add_internal_note(case_id: int, payload: CaseInternalNoteCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    case = load_case_or_404(db, case_id)
    db.add(CaseInternalNote(case_id=case.id, created_by_user_id=current_user.id, note=payload.note.strip()))
    append_workflow(db, case, current_user, "internal_note_added", comment=payload.note.strip())
    db.commit()
    return serialize_case_detail(load_case_or_404(db, case.id))


@router.post("/cases/{case_id}/generate-draft", response_model=CaseDetail)
def generate_case_draft(case_id: int, payload: DraftGenerationRequest, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary", "protocolist"))):
    case = load_case_or_404(db, case_id)
    generate_draft_for_case(db, case, current_user, payload.comment)
    db.commit()
    return serialize_case_detail(load_case_or_404(db, case.id))


@router.post("/cases/{case_id}/generate-with-gari", response_model=CaseDetail)
def generate_case_draft_with_gari(case_id: int, payload: GariGenerationRequest, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary", "protocolist"))):
    case = load_case_or_404(db, case_id)
    if case.act_data is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Debes registrar los datos del acto antes de generar el borrador con Gari.")
    if not case.participants:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Debes registrar intervinientes antes de generar el borrador con Gari.")

    act_data = json.loads(case.act_data.data_json or "{}")
    if not act_data:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Debes registrar los datos del acto antes de generar el borrador con Gari.")

    participants = [
        {
            "role_code": item.role_code,
            "role_label": item.role_label,
            "full_name": item.person.full_name,
            "document_type": item.person.document_type,
            "document_number": item.person.document_number,
            "sex": item.person.sex,
            "nationality": item.person.nationality,
            "marital_status": item.person.marital_status,
            "profession": item.person.profession,
            "municipality": item.person.municipality,
            "is_transient": item.person.is_transient,
            "phone": item.person.phone,
            "address": item.person.address,
            "email": item.person.email,
            "represented_entity_name": item.legal_entity.name if item.legal_entity else "",
            "represented_entity_nit": item.legal_entity.nit if item.legal_entity else "",
        }
        for item in case.participants
    ]

    template_reference_text = None
    if case.template and case.template.storage_path:
        try:
            template_reference_text = extract_text_from_docx(case.template.storage_path)
        except Exception:
            template_reference_text = None

    campos_caso = {k: v for k, v in act_data.items() if v not in (None, "", [])}

    if case.template:
        resolucion = resolver_escritura_desde_template(case.template)
        campos_faltantes = [
            c for c in resolucion["campos_requeridos"]
            if not campos_caso.get(c)
        ]
        if campos_faltantes:
            raise HTTPException(
                status_code=422,
                detail=f"Faltan campos requeridos: {', '.join(campos_faltantes)}"
            )
        max_tokens = resolucion["max_tokens_estimado"]
        variante_id = resolucion["variante_id"]
    else:
        max_tokens = 4000
        variante_id = None

    case_acts = [
        {
            "act_code": item.act_code,
            "act_label": item.act_label,
            "act_order": item.act_order,
            "roles_json": item.roles_json,
        }
        for item in case.acts
    ]
    if not case_acts and variante_id:
        case_acts = LEGACY_CASE_ACTS_BY_VARIANT.get(variante_id, [])

    try:
        previous_draft = case.act_data.gari_draft_text if case.act_data else None
        correction_note = payload.comment if payload.comment and payload.comment.strip() else None
        generated_text = generate_notarial_document(
            act_type=case.act_type,
            notary_label=case.notary.notary_label,
            notary_name=case.notary.current_notary_name or case.notary.legal_name or case.notary.notary_label,
            participants=participants,
            case_acts=case_acts,
            act_data=act_data,
            template_reference_text=template_reference_text,
            max_tokens=max_tokens,
            variante_id=variante_id,
            correction_note=correction_note,
            previous_draft=previous_draft,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="No fue posible generar el documento con Gari.") from exc

    # Reparar encoding UTF-8 si viene roto (latin-1 leído como utf-8)
    if isinstance(generated_text, bytes):
        generated_text = generated_text.decode('utf-8')
    try:
        generated_text = generated_text.encode('latin-1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass

    case.act_data.gari_draft_text = generated_text
    db.flush()

    output_path = f"cases/case-{case.id}/draft/{case.internal_case_number or case.id}_gari.docx"
    signed_url = save_gari_document_as_docx(generated_text, output_path)

    version = add_document_version(
        db,
        case,
        "draft",
        "Borrador documental Gari",
        "docx",
        signed_url,
        f"{case.internal_case_number or case.id}_gari.docx",
        current_user.id,
        case.template_id,
        json.dumps({"source": "gari", "model": "gpt-4o"}, ensure_ascii=False),
    )
    version.storage_path = output_path
    db.flush()

    previous_state = case.current_state
    if case.current_state in {"borrador", "en_diligenciamiento", "revision_cliente", "ajustes_solicitados"}:
        case.current_state = "generado"

    comment_text = f"Corrección aplicada: {correction_note}" if correction_note else payload.comment or "Borrador generado con Gari"
    append_timeline(db, case.id, current_user.id, "gari_draft_generated", previous_state, case.current_state, comment_text, {"version": version.version_number, "variante_id": variante_id})
    append_workflow(db, case, current_user, "gari_draft_generated", actor_role_code="protocolist", comment=comment_text, from_state=previous_state, to_state=case.current_state, metadata={"version": version.version_number, "source": "gari", "variante_id": variante_id})
    db.commit()
    return serialize_case_detail(load_case_or_404(db, case.id))


@router.post("/cases/{case_id}/approve", response_model=CaseDetail)
def approve_case(case_id: int, payload: ApprovalRequest, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary", "approver", "notary"))):
    case = load_case_or_404(db, case_id)
    if payload.role_code not in {"approver", "titular_notary", "substitute_notary"}:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="role_code debe ser approver, titular_notary o substitute_notary.")
    actor_roles = get_role_codes(current_user)
    if "super_admin" not in actor_roles and "admin_notary" not in actor_roles:
        if payload.role_code == "approver" and case.approver_user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo el aprobador asignado puede revisar este caso.")
        if payload.role_code == "titular_notary" and case.titular_notary_user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo el notario titular asignado puede aprobar como titular.")
        if payload.role_code == "substitute_notary" and case.substitute_notary_user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo el notario suplente asignado puede aprobar como suplente.")
    latest_draft = latest_document_version(case, "draft", "docx")
    if latest_draft is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Debes generar al menos una versión documental antes de aprobar.")
    previous_state = case.current_state
    if payload.role_code == "approver":
        case.current_state = "revision_notario"
        append_workflow(db, case, current_user, "case_reviewed", actor_role_code="approver", approved_version_id=latest_draft.id, comment=payload.comment or "Caso revisado por aprobador", from_state=previous_state, to_state=case.current_state)
    else:
        if case.approved_by_role_code in NOTARY_APPROVER_ROLES and case.approved_by_role_code != payload.role_code:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El documento ya fue aprobado por el otro rol notarial.")
        year = datetime.utcnow().year
        if not case.official_deed_number:
            official_number = resolve_next_sequence(db, "official_deed", case.notary_id, year)
            case.official_deed_number = f"{official_number:04d}-{year}"
            case.official_deed_year = year
        case.current_state = "aprobado_notario"
        case.approved_at = datetime.utcnow()
        case.approved_by_user_id = current_user.id
        case.approved_by_role_code = payload.role_code
        case.approved_document_version_id = latest_draft.id
        append_workflow(db, case, current_user, "case_approved", actor_role_code=payload.role_code, approved_version_id=latest_draft.id, comment=payload.comment or "Documento aprobado", from_state=previous_state, to_state=case.current_state, new_value=case.official_deed_number)
    append_timeline(db, case.id, current_user.id, "state_changed", previous_state, case.current_state, payload.comment or "Aprobación registrada")
    db.commit()
    return serialize_case_detail(load_case_or_404(db, case.id))


@router.post("/cases/{case_id}/export", response_model=CaseDetail)
def export_case_document(case_id: int, payload: ExportRequest, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary", "protocolist", "approver", "notary"))):
    case = load_case_or_404(db, case_id)
    latest_draft = latest_document_version(case, "draft", "docx")
    if latest_draft is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="No existe borrador documental para exportar.")
    if payload.file_format == "docx":
        version = add_document_version(db, case, "export_word", "Exportación Word", "docx", latest_draft.storage_path, latest_draft.original_filename, current_user.id, case.template_id, latest_draft.placeholder_snapshot_json)
    else:
        act_data = json.loads(case.act_data.data_json if case.act_data else "{}")
        participants = [{"role_label": item.role_label, "full_name": item.person.full_name, "document_type": item.person.document_type, "document_number": item.person.document_number} for item in case.participants]
        temp_pdf = next_case_file_path(case.id, "temp-export", 1, "pdf", f"case_{case.id}.pdf")
        generate_plain_pdf(temp_pdf, case.act_type, build_case_text_snapshot(case.official_deed_number or case.internal_case_number or str(case.id), case.act_type, participants, act_data))
        version = add_document_version(db, case, "export_pdf", "Exportación PDF", "pdf", temp_pdf, f"{case.internal_case_number or case.id}.pdf", current_user.id, case.template_id, latest_draft.placeholder_snapshot_json)
    append_workflow(db, case, current_user, "document_exported", comment=f"Documento exportado en formato {payload.file_format.upper()}", approved_version_id=version.id, metadata={"format": payload.file_format})
    db.commit()
    return serialize_case_detail(load_case_or_404(db, case.id))


@router.post("/cases/{case_id}/final-upload", response_model=CaseDetail)
def upload_final_document(case_id: int, payload: FinalUploadRequest, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary", "protocolist", "notary"))):
    case = load_case_or_404(db, case_id)
    extension = Path(payload.filename).suffix.lstrip(".") or "pdf"
    target = next_case_file_path(case.id, "final_signed", 1, extension, payload.filename)
    save_base64_file(payload.content_base64, target)
    version = add_document_version(db, case, "final_signed", "Documento definitivo firmado", extension, target, payload.filename, current_user.id, case.template_id, "{}")
    previous_state = case.current_state
    case.final_signed_uploaded = True
    if case.current_state != "cerrado":
        case.current_state = "firmado_cargado"
    append_workflow(db, case, current_user, "final_signed_uploaded", comment=payload.comment or "Documento definitivo cargado", approved_version_id=version.id, from_state=previous_state, to_state=case.current_state)
    append_timeline(db, case.id, current_user.id, "final_signed_uploaded", previous_state, case.current_state, payload.comment or "Documento definitivo cargado")
    db.commit()
    return serialize_case_detail(load_case_or_404(db, case.id))


@router.get("/cases/{case_id}/documents", response_model=list[CaseDocumentSummary])
def list_case_documents(case_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    case = load_case_or_404(db, case_id)
    return [serialize_document(case.id, item) for item in case.documents]


@router.get("/cases/{case_id}/documents/{document_id}/versions/{version_id}/download")
def download_case_document(case_id: int, document_id: int, version_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    case = load_case_or_404(db, case_id)
    version = None
    for document in case.documents:
        if document.id != document_id:
            continue
        for item in document.versions:
            if item.id == version_id:
                version = item
                break
    if version is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Versión documental no encontrada.")

    # Detectar si es documento Gari y regenerar en tiempo real desde el texto
    snapshot = json.loads(version.placeholder_snapshot_json or "{}")
    if snapshot.get("source") == "gari" and case.act_data and case.act_data.gari_draft_text:
        buf = build_gari_docx_buffer(case.act_data.gari_draft_text)
        filename = version.original_filename or f"{case.internal_case_number or case.id}_gari.docx"
        return StreamingResponse(
            buf,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    storage = version.storage_path or ""

    # 1) Si es URL completa ya firmada → regenerar signed URL o redirigir
    if storage.startswith("http://") or storage.startswith("https://"):
        try:
            from app.services.gari_document_service import get_supabase_client
            import re

            match = re.search(r"(cases/.*)", storage)
            if match:
                supabase_path = match.group(1).split("?")[0]
                supabase = get_supabase_client()
                result = supabase.storage.from_("documentos").create_signed_url(
                    supabase_path, 300
                )
                new_url = result.get("signedURL") or result.get("signedUrl") or storage
                return RedirectResponse(url=new_url, status_code=302)
        except Exception:
            pass
        return RedirectResponse(url=storage, status_code=302)

    # 2) Si existe como archivo local → servir directo
    path = Path(storage)
    if path.exists():
        return FileResponse(path, media_type=guess_media_type(path), filename=version.original_filename)

    # 3) Si es path relativo de Supabase (no existe local) → generar signed URL
    try:
        from app.services.gari_document_service import get_supabase_client
        supabase = get_supabase_client()
        result = supabase.storage.from_("documentos").create_signed_url(storage, 300)
        new_url = result.get("signedURL") or result.get("signedUrl")
        if new_url:
            return RedirectResponse(url=new_url, status_code=302)
    except Exception:
        pass

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El archivo solicitado no está disponible.")


@router.get("/cases/{case_id}/gari-download")
def download_gari_document(case_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    case = load_case_or_404(db, case_id)
    if not (case.act_data and case.act_data.gari_draft_text and case.act_data.gari_draft_text.strip()):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay borrador Gari para este caso")
    buf = build_gari_docx_buffer(case.act_data.gari_draft_text)
    filename = f"{case.internal_case_number or case.id}_gari.docx"
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/cases/{case_id}/timeline-events", response_model=CaseDetail)
def add_case_timeline_event(case_id: int, payload: CaseTimelineEventCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    case = load_case_or_404(db, case_id)
    metadata = json.loads(payload.metadata_json) if payload.metadata_json else None
    append_timeline(db, case.id, current_user.id, "comment_added", case.current_state, case.current_state, payload.comment, metadata)
    append_workflow(db, case, current_user, "comment_added", comment=payload.comment, metadata=metadata)
    db.commit()
    return serialize_case_detail(load_case_or_404(db, case.id))


@router.get("/persons/lookup")
def lookup_person(document_type: str | None = Query(default=None), document_number: str | None = Query(default=None), q: str | None = Query(default=None), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Person).order_by(Person.full_name.asc())
    if document_type and document_number:
        query = query.filter(Person.document_type == document_type.upper().strip(), Person.document_number == document_number.strip())
    elif q:
        search = f"%{q.strip()}%"
        query = query.filter((Person.full_name.ilike(search)) | (Person.document_number.ilike(search)) | (Person.email.ilike(search)))
    return [
        {
            "id": item.id,
            "document_type": item.document_type,
            "document_number": item.document_number,
            "full_name": item.full_name,
            "sex": item.sex,
            "nationality": item.nationality,
            "marital_status": item.marital_status,
            "profession": item.profession,
            "municipality": item.municipality,
            "is_transient": item.is_transient,
            "phone": item.phone,
            "address": item.address,
            "email": item.email,
        }
        for item in query.limit(25).all()
    ]
```

## File: app/modules/legal_entities/__init__.py
```python

```

## File: app/modules/legal_entities/router.py
```python
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user, get_db, require_roles
from app.models.legal_entity import LegalEntity
from app.models.legal_entity_representative import LegalEntityRepresentative
from app.models.person import Person
from app.models.user import User
from app.schemas.legal_entity import (
    LegalEntityCreate,
    LegalEntityOut,
    LegalEntityRepresentativeCreate,
    LegalEntityRepresentativeOut,
)

router = APIRouter(prefix="/legal-entities", tags=["legal-entities"])


def serialize_legal_entity(entity: LegalEntity) -> LegalEntityOut:
    return LegalEntityOut.model_validate(entity)


def serialize_representative(item: LegalEntityRepresentative) -> LegalEntityRepresentativeOut:
    person = item.person
    return LegalEntityRepresentativeOut(
        id=item.id,
        legal_entity_id=item.legal_entity_id,
        person_id=item.person_id,
        person_name=person.full_name if person else "",
        person_document=f"{person.document_type} {person.document_number}".strip() if person else "",
        power_type=item.power_type,
        is_active=item.is_active,
    )


def load_entity_or_404(db: Session, entity_id: int) -> LegalEntity:
    entity = db.query(LegalEntity).filter(LegalEntity.id == entity_id).first()
    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entidad jurídica no encontrada.")
    return entity


def load_person_or_404(db: Session, person_id: int) -> Person:
    person = db.query(Person).filter(Person.id == person_id).first()
    if person is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Persona no encontrada.")
    return person


@router.get("", response_model=list[LegalEntityOut])
def list_legal_entities(
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(LegalEntity).order_by(LegalEntity.name.asc())
    if q:
        search = f"%{q.strip()}%"
        query = query.filter(or_(LegalEntity.name.ilike(search), LegalEntity.nit.ilike(search)))
    return [serialize_legal_entity(item) for item in query.all()]


@router.post("", response_model=LegalEntityOut)
def create_legal_entity(
    payload: LegalEntityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("super_admin", "admin_notary", "protocolist", "approver", "notary")),
):
    nit = payload.nit.strip()
    existing = db.query(LegalEntity).filter(LegalEntity.nit == nit).first()
    if existing is not None:
        return serialize_legal_entity(existing)

    entity = LegalEntity(
        nit=nit,
        name=payload.name.strip(),
        legal_representative=payload.legal_representative.strip() if payload.legal_representative else None,
        municipality=payload.municipality.strip() if payload.municipality else None,
        address=payload.address.strip() if payload.address else None,
        phone=payload.phone.strip() if payload.phone else None,
        email=payload.email.strip().lower() if payload.email else None,
    )
    db.add(entity)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.query(LegalEntity).filter(LegalEntity.nit == nit).first()
        if existing is None:
            raise
        return serialize_legal_entity(existing)
    db.refresh(entity)
    return serialize_legal_entity(entity)


@router.get("/{entity_id}/representatives", response_model=list[LegalEntityRepresentativeOut])
def list_entity_representatives(
    entity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    load_entity_or_404(db, entity_id)
    representatives = (
        db.query(LegalEntityRepresentative)
        .options(joinedload(LegalEntityRepresentative.person))
        .filter(
            LegalEntityRepresentative.legal_entity_id == entity_id,
            LegalEntityRepresentative.is_active.is_(True),
        )
        .order_by(LegalEntityRepresentative.id.asc())
        .all()
    )
    return [serialize_representative(item) for item in representatives]


@router.post("/{entity_id}/representatives", response_model=LegalEntityRepresentativeOut)
def create_or_reactivate_representative(
    entity_id: int,
    payload: LegalEntityRepresentativeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("super_admin", "admin_notary", "protocolist", "approver", "notary")),
):
    entity = load_entity_or_404(db, entity_id)
    person = load_person_or_404(db, payload.person_id)

    representative = (
        db.query(LegalEntityRepresentative)
        .options(joinedload(LegalEntityRepresentative.person))
        .filter(
            LegalEntityRepresentative.legal_entity_id == entity.id,
            LegalEntityRepresentative.person_id == person.id,
        )
        .first()
    )
    if representative is None:
        representative = LegalEntityRepresentative(
            legal_entity_id=entity.id,
            person_id=person.id,
            power_type=payload.power_type.strip() if payload.power_type else None,
            is_active=True,
        )
        db.add(representative)
    else:
        representative.power_type = payload.power_type.strip() if payload.power_type else representative.power_type
        representative.is_active = True

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No fue posible registrar el apoderado.") from exc

    db.refresh(representative)
    representative = (
        db.query(LegalEntityRepresentative)
        .options(joinedload(LegalEntityRepresentative.person))
        .filter(LegalEntityRepresentative.id == representative.id)
        .first()
    )
    if representative is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Apoderado no encontrado.")
    return serialize_representative(representative)
```

## File: app/modules/notaries/__init__.py
```python

```

## File: app/modules/notaries/router.py
```python
import re
import unicodedata

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import ValidationError
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, aliased, joinedload

from app.core.deps import get_current_user, get_db, has_role, require_roles
from app.models.notary import Notary
from app.models.notary_commercial_activity import NotaryCommercialActivity
from app.models.notary_crm_audit_log import NotaryCrmAuditLog
from app.models.user import User
from app.schemas.notary import (
    CommercialActivityCreate,
    CommercialActivitySummary,
    NotaryCreate,
    NotaryDetail,
    NotaryFileImportRequest,
    NotaryFilterOptions,
    NotaryImportRequest,
    NotaryImportResult,
    NotaryImportRowError,
    NotaryImportSummary,
    NotaryStatusUpdate,
    NotarySummary,
    NotaryUpdate,
)
from app.services.notary_imports import DEFAULT_ANTIOQUIA_SOURCE_PATH, NotaryImportFileError, load_xlsx_rows

router = APIRouter(prefix="/notaries", tags=["notaries"])

COMMERCIAL_STATUSES = [
    "prospecto",
    "contactado",
    "en seguimiento",
    "reunión agendada",
    "propuesta enviada",
    "negociación",
    "cerrado ganado",
    "cerrado perdido",
    "no interesado",
]
PRIORITIES = ["baja", "media", "alta", "crítica"]


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", normalized.lower()).strip("-")
    return cleaned or "notary"


def ensure_unique_slug(db: Session, base_slug: str, current_id: int | None = None) -> str:
    slug = base_slug
    counter = 2
    while True:
        query = db.query(Notary).filter(Notary.slug == slug)
        if current_id is not None:
            query = query.filter(Notary.id != current_id)
        if query.first() is None:
            return slug
        slug = f"{base_slug}-{counter}"
        counter += 1


def normalize_catalog_field(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def normalize_email(value: str | None) -> str | None:
    normalized = normalize_catalog_field(value)
    return normalized.lower() if normalized else None


def build_catalog_identity_key(municipality: str, notary_label: str, email: str | None) -> str:
    normalized_email = email or "no-email"
    return "::".join([slugify(municipality), slugify(notary_label), slugify(normalized_email)])


def duplicate_key_string(municipality: str, notary_label: str, email: str | None) -> str:
    return " | ".join(part for part in [municipality, notary_label, email] if part)


def commercial_owner_display(notary: Notary) -> str | None:
    if notary.commercial_owner_user is not None:
        return notary.commercial_owner_user.full_name
    return notary.commercial_owner


def serialize_activity(activity: NotaryCommercialActivity) -> CommercialActivitySummary:
    return CommercialActivitySummary(
        id=activity.id,
        notary_id=activity.notary_id,
        occurred_at=activity.occurred_at,
        management_type=activity.management_type,
        comment=activity.comment,
        responsible=activity.responsible,
        responsible_user_id=activity.responsible_user_id,
        responsible_user_name=activity.responsible_user.full_name if activity.responsible_user else None,
        result=activity.result,
        next_action=activity.next_action,
    )


def serialize_audit(log: NotaryCrmAuditLog):
    return {
        "id": log.id,
        "event_type": log.event_type,
        "field_name": log.field_name,
        "old_value": log.old_value,
        "new_value": log.new_value,
        "comment": log.comment,
        "actor_user_id": log.actor_user_id,
        "actor_user_name": log.actor_user.full_name if log.actor_user else None,
        "created_at": log.created_at,
    }


def attach_notary_summary(notary: Notary, activity_count: int) -> NotarySummary:
    return NotarySummary.model_validate(
        {
            **notary.__dict__,
            "activity_count": activity_count,
            "commercial_owner_display": commercial_owner_display(notary),
            "commercial_owner_user_name": notary.commercial_owner_user.full_name if notary.commercial_owner_user else None,
        }
    )


def attach_notary_detail(notary: Notary) -> NotaryDetail:
    return NotaryDetail.model_validate(
        {
            **notary.__dict__,
            "activity_count": len(notary.commercial_activities),
            "commercial_owner_display": commercial_owner_display(notary),
            "commercial_owner_user_name": notary.commercial_owner_user.full_name if notary.commercial_owner_user else None,
            "commercial_activities": [serialize_activity(activity).model_dump() for activity in notary.commercial_activities],
            "crm_audit_logs": [serialize_audit(log) for log in notary.crm_audit_logs],
        }
    )


def find_duplicate_notary(
    db: Session,
    municipality: str,
    notary_label: str,
    email: str | None,
    current_id: int | None = None,
) -> Notary | None:
    identity_key = build_catalog_identity_key(municipality, notary_label, email)
    query = db.query(Notary).filter(Notary.catalog_identity_key == identity_key)
    if current_id is not None:
        query = query.filter(Notary.id != current_id)
    return query.first()


def ensure_catalog_duplicate_is_available(
    db: Session,
    municipality: str,
    notary_label: str,
    email: str | None,
    current_id: int | None = None,
) -> None:
    existing = find_duplicate_notary(db, municipality, notary_label, email, current_id=current_id)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una notaría con la combinación municipality + notary_label + email.",
        )


def resolve_owner(db: Session, owner_user_id: int | None, owner_text: str | None) -> tuple[int | None, str | None, str | None]:
    normalized_text = normalize_catalog_field(owner_text)
    if owner_user_id is None:
        return None, normalized_text, normalized_text
    user = db.query(User).filter(User.id == owner_user_id, User.is_active.is_(True)).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El responsable comercial no existe o está inactivo.")
    return user.id, user.full_name, user.full_name


def hydrate_notary_payload(db: Session, notary: Notary, payload: NotaryCreate | NotaryUpdate) -> None:
    municipality = normalize_catalog_field(payload.municipality) or payload.city
    notary_label = normalize_catalog_field(payload.notary_label) or payload.commercial_name
    email = normalize_email(str(payload.email) if payload.email else None)
    owner_user_id, owner_text, _ = resolve_owner(db, payload.commercial_owner_user_id, payload.commercial_owner)
    notary.catalog_identity_key = build_catalog_identity_key(municipality, notary_label, email)
    notary.department = normalize_catalog_field(payload.department) or "Antioquia"
    notary.municipality = municipality
    notary.notary_label = notary_label
    notary.legal_name = payload.legal_name
    notary.commercial_name = payload.commercial_name
    notary.city = payload.city
    notary.address = normalize_catalog_field(payload.address)
    notary.phone = normalize_catalog_field(payload.phone)
    notary.email = email
    notary.current_notary_name = normalize_catalog_field(payload.current_notary_name)
    notary.business_hours = normalize_catalog_field(payload.business_hours)
    notary.logo_url = normalize_catalog_field(payload.logo_url)
    notary.primary_color = payload.primary_color
    notary.secondary_color = payload.secondary_color
    notary.base_color = payload.base_color
    notary.accent_color = payload.secondary_color
    notary.institutional_data = payload.institutional_data
    notary.commercial_status = payload.commercial_status
    notary.commercial_owner_user_id = owner_user_id
    notary.commercial_owner = owner_text
    notary.main_contact_name = normalize_catalog_field(payload.main_contact_name)
    notary.main_contact_title = normalize_catalog_field(payload.main_contact_title)
    notary.commercial_phone = normalize_catalog_field(payload.commercial_phone)
    notary.commercial_email = normalize_email(str(payload.commercial_email) if payload.commercial_email else None)
    notary.last_management_at = payload.last_management_at
    notary.next_management_at = payload.next_management_at
    notary.commercial_notes = normalize_catalog_field(payload.commercial_notes)
    notary.priority = payload.priority
    notary.lead_source = normalize_catalog_field(payload.lead_source)
    notary.potential = payload.potential
    notary.internal_observations = normalize_catalog_field(payload.internal_observations)
    notary.is_active = payload.is_active


def create_audit_log(
    db: Session,
    notary_id: int,
    actor_user: User | None,
    event_type: str,
    field_name: str | None,
    old_value: str | None,
    new_value: str | None,
    comment: str | None = None,
) -> None:
    db.add(
        NotaryCrmAuditLog(
            notary_id=notary_id,
            actor_user_id=actor_user.id if actor_user else None,
            event_type=event_type,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value,
            comment=comment,
        )
    )


def apply_import_mapping(notary: Notary, row: dict[str, str]) -> tuple[str, str, str | None]:
    municipality = normalize_catalog_field(row.get("MUNICIPIO"))
    notary_label = normalize_catalog_field(row.get("NOTARÍA"))
    if municipality is None or notary_label is None:
        raise ValueError("La fila no tiene MUNICIPIO o NOTARÍA válidos.")

    normalized_email = normalize_email(row.get("CORREO ELECTRÓNICO"))
    notary.catalog_identity_key = build_catalog_identity_key(municipality, notary_label, normalized_email)
    notary.department = "Antioquia"
    notary.municipality = municipality
    notary.notary_label = notary_label
    notary.city = municipality
    notary.legal_name = notary_label
    notary.commercial_name = notary_label
    notary.address = normalize_catalog_field(row.get("DIRECCIÓN"))
    notary.phone = normalize_catalog_field(row.get("TELÉFONO"))
    notary.email = normalized_email
    notary.current_notary_name = normalize_catalog_field(row.get("NOTARIO/A"))
    notary.business_hours = normalize_catalog_field(row.get("HORARIO"))
    notary.is_active = True
    if not notary.primary_color:
        notary.primary_color = "#0D2E5D"
    if not notary.secondary_color:
        notary.secondary_color = "#4D5B7C"
    if not notary.base_color:
        notary.base_color = "#F4F7FB"
    if not notary.accent_color:
        notary.accent_color = notary.secondary_color or "#4D5B7C"
    return municipality, notary_label, normalized_email


def process_import_rows(
    db: Session,
    rows: list[dict[str, str]],
    overwrite_existing: bool,
    source_path: str | None = None,
    start_row_number: int = 2,
) -> NotaryImportSummary:
    results: list[NotaryImportResult] = []
    row_errors: list[NotaryImportRowError] = []
    created = 0
    updated = 0
    omitted = 0

    for row_index, row_data in enumerate(rows, start=start_row_number):
        municipality = normalize_catalog_field(row_data.get("MUNICIPIO"))
        notary_label = normalize_catalog_field(row_data.get("NOTARÍA"))
        email = normalize_email(row_data.get("CORREO ELECTRÓNICO"))

        try:
            if municipality is None or notary_label is None:
                raise ValueError("La fila no tiene MUNICIPIO o NOTARÍA válidos.")

            duplicate = find_duplicate_notary(db, municipality, notary_label, email)

            if duplicate is None:
                slug_base = slugify(f"{municipality}-{notary_label}")
                duplicate = Notary(slug=ensure_unique_slug(db, slug_base), catalog_identity_key=build_catalog_identity_key(municipality, notary_label, email))
                apply_import_mapping(duplicate, row_data)
                db.add(duplicate)
                action = "created"
                created += 1
            elif overwrite_existing:
                apply_import_mapping(duplicate, row_data)
                action = "updated"
                updated += 1
            else:
                action = "omitted"
                omitted += 1

            if action != "omitted":
                try:
                    with db.begin_nested():
                        db.add(duplicate)
                        db.flush()
                except IntegrityError as exc:
                    raise ValueError("Conflicto de unicidad al importar la fila.") from exc

            results.append(
                NotaryImportResult(
                    row_number=row_index,
                    action=action,
                    notary_id=duplicate.id,
                    slug=duplicate.slug,
                    duplicate_key=duplicate_key_string(municipality, notary_label, email),
                )
            )
        except ValueError as exc:
            db.rollback()
            row_errors.append(
                NotaryImportRowError(
                    row_number=row_index,
                    municipality=municipality,
                    notary_label=notary_label,
                    error=str(exc),
                )
            )

    db.commit()
    return NotaryImportSummary(
        source_path=source_path,
        processed=len(rows),
        created=created,
        updated=updated,
        omitted=omitted,
        errors=row_errors,
        results=results,
    )


@router.get("", response_model=list[NotarySummary])
def list_notaries(
    commercial_status: str | None = Query(default=None),
    municipality: str | None = Query(default=None),
    commercial_owner: str | None = Query(default=None),
    priority: str | None = Query(default=None),
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    owner_alias = aliased(User)
    activity_counts = (
        db.query(
            NotaryCommercialActivity.notary_id.label("notary_id"),
            func.count(NotaryCommercialActivity.id).label("activity_count"),
        )
        .group_by(NotaryCommercialActivity.notary_id)
        .subquery()
    )
    query = (
        db.query(Notary, func.coalesce(activity_counts.c.activity_count, 0).label("activity_count"))
        .outerjoin(activity_counts, activity_counts.c.notary_id == Notary.id)
        .outerjoin(owner_alias, owner_alias.id == Notary.commercial_owner_user_id)
        .options(joinedload(Notary.commercial_owner_user))
        .order_by(Notary.municipality.asc(), Notary.notary_label.asc())
    )

    if commercial_status:
        query = query.filter(Notary.commercial_status == commercial_status)
    if municipality:
        query = query.filter(Notary.municipality == municipality)
    if commercial_owner:
        query = query.filter(or_(Notary.commercial_owner == commercial_owner, owner_alias.full_name == commercial_owner))
    if priority:
        query = query.filter(Notary.priority == priority)
    if q:
        search = f"%{q.strip()}%"
        query = query.filter(
            Notary.municipality.ilike(search)
            | Notary.notary_label.ilike(search)
            | Notary.email.ilike(search)
            | Notary.current_notary_name.ilike(search)
            | Notary.commercial_owner.ilike(search)
            | owner_alias.full_name.ilike(search)
        )

    return [attach_notary_summary(notary, activity_count) for notary, activity_count in query.all()]


@router.get("/filters", response_model=NotaryFilterOptions)
def get_notary_filter_options(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    notaries = db.query(Notary).options(joinedload(Notary.commercial_owner_user)).all()
    municipalities = sorted({notary.municipality for notary in notaries if notary.municipality})
    commercial_owners = sorted({commercial_owner_display(notary) for notary in notaries if commercial_owner_display(notary)})
    priorities = sorted({notary.priority for notary in notaries if notary.priority})
    statuses = sorted({notary.commercial_status for notary in notaries if notary.commercial_status})
    return NotaryFilterOptions(
        municipalities=municipalities,
        commercial_owners=commercial_owners,
        priorities=priorities or PRIORITIES,
        commercial_statuses=statuses or COMMERCIAL_STATUSES,
    )


@router.get("/{notary_id}", response_model=NotaryDetail)
def get_notary(notary_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    notary = (
        db.query(Notary)
        .options(
            joinedload(Notary.commercial_owner_user),
            joinedload(Notary.commercial_activities).joinedload(NotaryCommercialActivity.responsible_user),
            joinedload(Notary.crm_audit_logs).joinedload(NotaryCrmAuditLog.actor_user),
        )
        .filter(Notary.id == notary_id)
        .first()
    )
    if notary is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notaría no encontrada.")
    return attach_notary_detail(notary)


@router.post("", response_model=NotarySummary, status_code=status.HTTP_201_CREATED)
def create_notary(payload: NotaryCreate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary"))):
    municipality = normalize_catalog_field(payload.municipality) or payload.city
    notary_label = normalize_catalog_field(payload.notary_label) or payload.commercial_name
    email = normalize_email(str(payload.email) if payload.email else None)
    ensure_catalog_duplicate_is_available(db, municipality, notary_label, email)

    notary = Notary(
        slug=ensure_unique_slug(db, slugify(f"{municipality}-{notary_label}")),
        catalog_identity_key=build_catalog_identity_key(municipality, notary_label, email),
    )
    hydrate_notary_payload(db, notary, payload)
    db.add(notary)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Conflicto de unicidad al crear la notaría.") from exc
    db.refresh(notary)
    return attach_notary_summary(notary, 0)


@router.put("/{notary_id}", response_model=NotarySummary)
def update_notary(notary_id: int, payload: NotaryUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary"))):
    notary = (
        db.query(Notary)
        .options(joinedload(Notary.commercial_owner_user))
        .filter(Notary.id == notary_id)
        .first()
    )
    if notary is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notaría no encontrada.")

    municipality = normalize_catalog_field(payload.municipality) or payload.city
    notary_label = normalize_catalog_field(payload.notary_label) or payload.commercial_name
    email = normalize_email(str(payload.email) if payload.email else None)
    ensure_catalog_duplicate_is_available(db, municipality, notary_label, email, current_id=notary.id)

    previous_status = notary.commercial_status
    previous_owner = commercial_owner_display(notary)
    previous_owner_user_id = notary.commercial_owner_user_id

    notary.slug = ensure_unique_slug(db, slugify(f"{municipality}-{notary_label}"), current_id=notary.id)
    hydrate_notary_payload(db, notary, payload)
    try:
        db.flush()
        if previous_status != notary.commercial_status:
            create_audit_log(db, notary.id, current_user, "status_changed", "commercial_status", previous_status, notary.commercial_status)
        current_owner = commercial_owner_display(notary)
        if previous_owner != current_owner or previous_owner_user_id != notary.commercial_owner_user_id:
            create_audit_log(db, notary.id, current_user, "owner_changed", "commercial_owner", previous_owner, current_owner)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Conflicto de unicidad al actualizar la notaría.") from exc
    db.refresh(notary)
    activity_count = db.query(NotaryCommercialActivity).filter(NotaryCommercialActivity.notary_id == notary.id).count()
    return attach_notary_summary(notary, activity_count)


@router.patch("/{notary_id}/status", response_model=NotarySummary)
def update_notary_status(notary_id: int, payload: NotaryStatusUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary"))):
    notary = db.query(Notary).options(joinedload(Notary.commercial_owner_user)).filter(Notary.id == notary_id).first()
    if notary is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notaría no encontrada.")

    previous_value = "activa" if notary.is_active else "inactiva"
    notary.is_active = payload.is_active
    create_audit_log(db, notary.id, current_user, "status_changed", "is_active", previous_value, "activa" if payload.is_active else "inactiva")
    db.commit()
    db.refresh(notary)
    activity_count = db.query(NotaryCommercialActivity).filter(NotaryCommercialActivity.notary_id == notary.id).count()
    return attach_notary_summary(notary, activity_count)


@router.get("/{notary_id}/commercial-activities", response_model=list[CommercialActivitySummary])
def list_commercial_activities(notary_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if db.query(Notary.id).filter(Notary.id == notary_id).first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notaría no encontrada.")
    activities = (
        db.query(NotaryCommercialActivity)
        .options(joinedload(NotaryCommercialActivity.responsible_user))
        .filter(NotaryCommercialActivity.notary_id == notary_id)
        .order_by(NotaryCommercialActivity.occurred_at.desc(), NotaryCommercialActivity.id.desc())
        .all()
    )
    return [serialize_activity(activity) for activity in activities]


@router.post("/{notary_id}/commercial-activities", response_model=CommercialActivitySummary, status_code=status.HTTP_201_CREATED)
def create_commercial_activity(notary_id: int, payload: CommercialActivityCreate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary", "notary", "approver", "protocolist"))):
    notary = db.query(Notary).filter(Notary.id == notary_id).first()
    if notary is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notaría no encontrada.")

    responsible_text = normalize_catalog_field(payload.responsible)
    responsible_user = None
    if payload.responsible_user_id is not None:
        responsible_user = db.query(User).filter(User.id == payload.responsible_user_id, User.is_active.is_(True)).first()
        if responsible_user is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El responsable de la gestión no existe o está inactivo.")
        responsible_text = responsible_user.full_name

    if not responsible_text:
        responsible_text = current_user.full_name
        responsible_user = current_user

    activity = NotaryCommercialActivity(
        notary_id=notary_id,
        occurred_at=payload.occurred_at,
        management_type=payload.management_type,
        comment=payload.comment,
        responsible=responsible_text,
        responsible_user_id=responsible_user.id if responsible_user else None,
        result=payload.result,
        next_action=payload.next_action,
    )
    db.add(activity)
    notary.last_management_at = payload.occurred_at
    create_audit_log(
        db,
        notary_id,
        current_user,
        "activity_added",
        "commercial_activity",
        None,
        payload.management_type,
        comment=payload.comment,
    )
    db.commit()
    db.refresh(activity)
    activity = db.query(NotaryCommercialActivity).options(joinedload(NotaryCommercialActivity.responsible_user)).filter(NotaryCommercialActivity.id == activity.id).first()
    return serialize_activity(activity)


@router.post("/imports/master-catalog", response_model=NotaryImportSummary, status_code=status.HTTP_201_CREATED)
def import_master_catalog(payload: NotaryImportRequest, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary"))):
    rows = [row.model_dump(by_alias=True) for row in payload.rows]
    return process_import_rows(db, rows, overwrite_existing=payload.overwrite_existing, source_path="payload://master-catalog", start_row_number=1)


@router.post("/imports/antioquia-source", response_model=NotaryImportSummary, status_code=status.HTTP_201_CREATED)
def import_antioquia_source(payload: NotaryFileImportRequest, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary"))):
    source_path = payload.source_path or str(DEFAULT_ANTIOQUIA_SOURCE_PATH)
    try:
        workbook = load_xlsx_rows(source_path)
    except NotaryImportFileError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    return process_import_rows(
        db,
        workbook.rows,
        overwrite_existing=payload.overwrite_existing,
        source_path=source_path,
        start_row_number=2,
    )
```

## File: app/modules/persons/router.py
```python
from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db, require_roles
from app.models.person import Person
from app.models.user import User
from app.schemas.person import PersonCreate, PersonSummary, PersonUpdate

router = APIRouter(prefix="/persons", tags=["persons"])


def serialize_person(person: Person) -> PersonSummary:
    return PersonSummary.model_validate(person)


def safe_person_json(value: str | None) -> str:
    if not value:
        return "{}"
    return json.dumps(json.loads(value), ensure_ascii=False)


def load_person_or_404(db: Session, person_id: int) -> Person:
    person = db.query(Person).filter(Person.id == person_id).first()
    if person is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Persona no encontrada.")
    return person


def hydrate_person(person: Person, payload: PersonCreate | PersonUpdate) -> None:
    person.document_type = payload.document_type.strip().upper()
    person.document_number = payload.document_number.strip()
    person.full_name = payload.full_name.strip()
    person.sex = payload.sex.strip() if payload.sex else None
    person.nationality = payload.nationality.strip() if payload.nationality else None
    person.marital_status = payload.marital_status.strip() if payload.marital_status else None
    person.profession = payload.profession.strip() if payload.profession else None
    person.municipality = payload.municipality.strip() if payload.municipality else None
    person.is_transient = payload.is_transient
    person.phone = payload.phone.strip() if payload.phone else None
    person.address = payload.address.strip() if payload.address else None
    person.email = str(payload.email).strip().lower() if payload.email else None
    person.metadata_json = safe_person_json(payload.metadata_json)


@router.get("", response_model=list[PersonSummary])
def list_persons(q: str | None = Query(default=None), document_type: str | None = Query(default=None), document_number: str | None = Query(default=None), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Person).order_by(Person.full_name.asc())
    if document_type and document_number:
        query = query.filter(Person.document_type == document_type.upper().strip(), Person.document_number == document_number.strip())
    elif q:
        search = f"%{q.strip()}%"
        query = query.filter(or_(Person.full_name.ilike(search), Person.document_number.ilike(search), Person.email.ilike(search)))
    return [serialize_person(item) for item in query.limit(25).all()]


@router.get("/{person_id}", response_model=PersonSummary)
def get_person(person_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return serialize_person(load_person_or_404(db, person_id))


@router.post("", response_model=PersonSummary, status_code=status.HTTP_201_CREATED)
def create_person(payload: PersonCreate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary", "protocolist", "approver", "notary"))):
    person = Person()
    hydrate_person(person, payload)
    db.add(person)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe una persona con ese tipo y número de documento.") from exc
    db.refresh(person)
    return serialize_person(person)


@router.put("/{person_id}", response_model=PersonSummary)
def update_person(person_id: int, payload: PersonUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary", "protocolist", "approver", "notary"))):
    person = load_person_or_404(db, person_id)
    hydrate_person(person, payload)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe una persona con ese tipo y número de documento.") from exc
    db.refresh(person)
    return serialize_person(person)
```

## File: app/modules/templates/router.py
```python
from __future__ import annotations

import json
import re

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user, get_db, require_roles
from app.models.document_template import DocumentTemplate
from app.models.notary import Notary
from app.models.template_field import TemplateField
from app.models.template_required_role import TemplateRequiredRole
from app.models.user import User
from app.schemas.template import TemplateCreate, TemplateFieldSummary, TemplateRequiredRoleSummary, TemplateSummary, TemplateUpdate
from app.services.storage import save_template_upload

router = APIRouter(prefix="/templates", tags=["templates"])


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return cleaned or "plantilla"


def load_template_or_404(db: Session, template_id: int) -> DocumentTemplate:
    template = db.query(DocumentTemplate).options(joinedload(DocumentTemplate.required_roles), joinedload(DocumentTemplate.fields), joinedload(DocumentTemplate.notary)).filter(DocumentTemplate.id == template_id).first()
    if template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plantilla no encontrada.")
    return template


def serialize_template(template: DocumentTemplate) -> TemplateSummary:
    return TemplateSummary(
        id=template.id,
        name=template.name,
        slug=template.slug,
        case_type=template.case_type,
        document_type=template.document_type,
        description=template.description,
        scope_type=template.scope_type,
        notary_id=template.notary_id,
        notary_label=template.notary.notary_label if template.notary else None,
        is_active=template.is_active,
        source_filename=template.source_filename,
        storage_path=template.storage_path,
        internal_variable_map_json=template.internal_variable_map_json,
        created_at=template.created_at,
        updated_at=template.updated_at,
        required_roles=[TemplateRequiredRoleSummary.model_validate(item) for item in template.required_roles],
        fields=[TemplateFieldSummary.model_validate(item) for item in template.fields],
    )


def validate_template_scope(db: Session, payload: TemplateCreate | TemplateUpdate) -> None:
    if payload.scope_type not in {"global", "notary"}:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="scope_type debe ser global o notary.")
    if payload.notary_id is not None and db.query(Notary.id).filter(Notary.id == payload.notary_id).first() is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="La notaría seleccionada no existe.")


def persist_template_payload(db: Session, template: DocumentTemplate, payload: TemplateCreate | TemplateUpdate) -> DocumentTemplate:
    validate_template_scope(db, payload)
    template.name = payload.name.strip()
    template.slug = slugify(payload.name) if not template.slug else template.slug
    template.case_type = payload.case_type.strip()
    template.document_type = payload.document_type.strip()
    template.description = payload.description.strip() if payload.description else None
    template.scope_type = payload.scope_type
    template.notary_id = payload.notary_id
    template.is_active = payload.is_active
    template.internal_variable_map_json = json.dumps(json.loads(payload.internal_variable_map_json or "{}"), ensure_ascii=False)

    if payload.upload:
        source_filename, storage_path = save_template_upload(payload.upload.filename, payload.upload.content_base64, template.slug or slugify(payload.name))
        template.source_filename = source_filename
        template.storage_path = storage_path

    template.required_roles.clear()
    template.fields.clear()
    db.flush()
    for item in payload.required_roles:
        template.required_roles.append(TemplateRequiredRole(role_code=item.role_code.strip(), label=item.label.strip(), is_required=item.is_required, step_order=item.step_order))
    for item in payload.fields:
        options_json = None
        if item.options_json:
            options_json = json.dumps(json.loads(item.options_json), ensure_ascii=False)
        template.fields.append(TemplateField(field_code=item.field_code.strip(), label=item.label.strip(), field_type=item.field_type.strip(), section=item.section.strip(), is_required=item.is_required, options_json=options_json, placeholder_key=item.placeholder_key.strip() if item.placeholder_key else None, help_text=item.help_text.strip() if item.help_text else None, step_order=item.step_order))
    return template


@router.get("", response_model=list[TemplateSummary])
def list_templates(active_only: bool = Query(default=False), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(DocumentTemplate).options(joinedload(DocumentTemplate.required_roles), joinedload(DocumentTemplate.fields), joinedload(DocumentTemplate.notary)).order_by(DocumentTemplate.updated_at.desc(), DocumentTemplate.id.desc())
    if active_only:
        query = query.filter(DocumentTemplate.is_active.is_(True))
    return [serialize_template(item) for item in query.all()]


@router.get("/active", response_model=list[TemplateSummary])
def list_active_templates(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    items = db.query(DocumentTemplate).options(joinedload(DocumentTemplate.required_roles), joinedload(DocumentTemplate.fields), joinedload(DocumentTemplate.notary)).filter(DocumentTemplate.is_active.is_(True)).order_by(DocumentTemplate.name.asc()).all()
    return [serialize_template(item) for item in items]


@router.get("/{template_id}", response_model=TemplateSummary)
def get_template(template_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return serialize_template(load_template_or_404(db, template_id))


@router.post("", response_model=TemplateSummary, status_code=status.HTTP_201_CREATED)
def create_template(payload: TemplateCreate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary"))):
    template = DocumentTemplate(slug=slugify(payload.name))
    persist_template_payload(db, template, payload)
    db.add(template)
    db.commit()
    db.refresh(template)
    return serialize_template(load_template_or_404(db, template.id))


@router.put("/{template_id}", response_model=TemplateSummary)
def update_template(template_id: int, payload: TemplateUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary"))):
    template = load_template_or_404(db, template_id)
    persist_template_payload(db, template, payload)
    db.commit()
    return serialize_template(load_template_or_404(db, template.id))
```

## File: app/modules/users/__init__.py
```python

```

## File: app/modules/users/router.py
```python
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user, get_db, get_role_codes, has_role, require_roles
from app.core.security import get_password_hash
from app.models.notary import Notary
from app.models.role import Role
from app.models.role_assignment import RoleAssignment
from app.models.role_permission import RolePermission
from app.models.user import User
from app.schemas.user import (
    RoleCreate,
    RoleCatalogItem,
    RolePermissionItem,
    RoleUpdate,
    UserCreate,
    UserDetail,
    UserOption,
    UserRoleAssignmentSummary,
    UserStatusUpdate,
    UserSummary,
    UserUpdate,
)

router = APIRouter(prefix="/users", tags=["users"])


ROLE_ORDER = ["super_admin", "admin_notary", "notary", "approver", "protocolist", "client"]
MODULE_CODES = [
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


def serialize_assignment(assignment: RoleAssignment) -> UserRoleAssignmentSummary:
    return UserRoleAssignmentSummary(
        id=assignment.id,
        role_id=assignment.role_id,
        role_code=assignment.role.code,
        role_name=assignment.role.name,
        notary_id=assignment.notary_id,
        notary_label=assignment.notary.notary_label if assignment.notary else None,
    )


def serialize_user(user: User) -> UserSummary:
    assignment_names = []
    for assignment in user.role_assignments:
        suffix = f" ({assignment.notary.notary_label})" if assignment.notary else ""
        assignment_names.append(f"{assignment.role.name}{suffix}")

    return UserSummary(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        phone=user.phone,
        job_title=user.job_title,
        default_notary_id=user.default_notary_id,
        default_notary_label=user.default_notary.notary_label if user.default_notary else None,
        roles=assignment_names,
        assignments=[serialize_assignment(assignment) for assignment in user.role_assignments],
    )


def load_user_or_404(db: Session, user_id: int) -> User:
    user = (
        db.query(User)
        .options(
            joinedload(User.default_notary),
            joinedload(User.role_assignments).joinedload(RoleAssignment.role),
            joinedload(User.role_assignments).joinedload(RoleAssignment.notary),
        )
        .filter(User.id == user_id)
        .first()
    )
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
    return user


def get_assignable_roles(db: Session, current_user: User) -> list[Role]:
    query = db.query(Role)
    if not has_role(current_user, "super_admin"):
        query = query.filter(Role.code != "super_admin")
    roles = query.all()
    return sorted(roles, key=lambda role: ROLE_ORDER.index(role.code) if role.code in ROLE_ORDER else 999)


def load_role_or_404(db: Session, role_id: int) -> Role:
    role = (
        db.query(Role)
        .options(joinedload(Role.permissions))
        .filter(Role.id == role_id)
        .first()
    )
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado.")
    return role


def serialize_role_permissions(role: Role) -> list[RolePermissionItem]:
    permission_map = {permission.module_code: permission.can_access for permission in role.permissions}
    ordered_module_codes = list(MODULE_CODES)
    for module_code in sorted(permission_map):
        if module_code not in ordered_module_codes:
            ordered_module_codes.append(module_code)
    return [
        RolePermissionItem(
            module_code=module_code,
            can_access=permission_map.get(module_code, False),
        )
        for module_code in ordered_module_codes
    ]


def ensure_assignment_permissions(current_user: User, role: Role, notary_id: int | None) -> None:
    manageable_notary_ids = get_manageable_notary_ids(current_user)
    if role.code == "super_admin" and not has_role(current_user, "super_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo SuperAdmin puede asignar ese rol.")
    if role.scope == "notary":
        if notary_id is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"El rol {role.name} requiere notaría asociada.")
        if has_role(current_user, "super_admin"):
            return
        if notary_id not in manageable_notary_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No puedes asignar roles fuera de tus notarías.")
    elif role.scope == "global" and not has_role(current_user, "super_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No puedes asignar roles globales.")


def sync_assignments(db: Session, user: User, payload_assignments, current_user: User) -> None:
    role_map = {role.code: role for role in db.query(Role).all()}
    normalized_pairs: set[tuple[int, int | None]] = set()
    db.query(RoleAssignment).filter(RoleAssignment.user_id == user.id).delete(synchronize_session=False)
    db.flush()

    for assignment_payload in payload_assignments:
        role = role_map.get(assignment_payload.role_code)
        if role is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Rol desconocido: {assignment_payload.role_code}")
        ensure_assignment_permissions(current_user, role, assignment_payload.notary_id)
        pair = (role.id, assignment_payload.notary_id)
        if pair in normalized_pairs:
            continue
        normalized_pairs.add(pair)
        db.add(
            RoleAssignment(
                user_id=user.id,
                role_id=role.id,
                notary_id=assignment_payload.notary_id if role.scope == "notary" else None,
            )
        )
    db.flush()


@router.get("/roles", response_model=list[RoleCatalogItem])
def list_roles(db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary"))):
    return get_assignable_roles(db, current_user)


@router.post("/roles", response_model=RoleCatalogItem, status_code=status.HTTP_201_CREATED)
def create_role(payload: RoleCreate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary"))):
    code = payload.code.strip()
    name = payload.name.strip()
    scope = payload.scope.strip()
    description = payload.description.strip()

    if code == "super_admin" and not has_role(current_user, "super_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo SuperAdmin puede crear ese rol.")
    if db.query(Role.id).filter(Role.code == code).first() is not None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Ya existe un rol con ese code.")
    if db.query(Role.id).filter(Role.name == name).first() is not None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Ya existe un rol con ese nombre.")
    role = Role(
        code=code,
        name=name,
        scope=scope,
        description=description,
    )
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


@router.patch("/roles/{role_id}", response_model=RoleCatalogItem)
def update_role(role_id: int, payload: RoleUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary"))):
    role = db.query(Role).filter(Role.id == role_id).first()
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado.")
    if role.code == "super_admin" and not has_role(current_user, "super_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo SuperAdmin puede editar ese rol.")
    duplicate_name = db.query(Role.id).filter(Role.name == payload.name.strip(), Role.id != role.id).first()
    if duplicate_name is not None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Ya existe un rol con ese nombre.")
    role.name = payload.name.strip()
    role.description = payload.description.strip()
    db.commit()
    db.refresh(role)
    return role


@router.delete("/roles/{role_id}")
def delete_role(role_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin"))):
    role = db.query(Role).filter(Role.id == role_id).first()
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado.")
    if role.code == "super_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No se puede eliminar el rol super_admin.")
    if db.query(RoleAssignment.id).filter(RoleAssignment.role_id == role.id).first() is not None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="No se puede eliminar un rol con usuarios asignados.")
    db.delete(role)
    db.commit()
    return {"deleted": True}


@router.get("/roles/{role_id}/permissions", response_model=list[RolePermissionItem])
def get_role_permissions(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("super_admin", "admin_notary")),
):
    role = load_role_or_404(db, role_id)
    return serialize_role_permissions(role)


@router.put("/roles/{role_id}/permissions", response_model=list[RolePermissionItem])
def update_role_permissions(
    role_id: int,
    payload: list[RolePermissionItem],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("super_admin", "admin_notary")),
):
    role = load_role_or_404(db, role_id)
    if role.code == "super_admin" and not has_role(current_user, "super_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo SuperAdmin puede modificar esos permisos.")

    existing_permissions = {permission.module_code: permission for permission in role.permissions}
    normalized_payload: dict[str, RolePermissionItem] = {}
    for item in payload:
        normalized_payload[item.module_code] = item

    for item in normalized_payload.values():
        current_permission = existing_permissions.get(item.module_code)
        if current_permission is None:
            db.add(
                RolePermission(
                    role_id=role.id,
                    module_code=item.module_code,
                    can_access=item.can_access,
                )
            )
        else:
            current_permission.can_access = item.can_access

    db.commit()
    role = load_role_or_404(db, role.id)
    return serialize_role_permissions(role)


@router.get("/options", response_model=list[UserOption])
def list_user_options(
    active_only: bool = Query(default=True),
    role_code: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role_codes = get_role_codes(current_user)
    query = db.query(User).options(joinedload(User.default_notary)).order_by(User.full_name.asc())
    if "super_admin" not in role_codes:
        query = query.filter(User.default_notary_id == current_user.default_notary_id)
    if role_code:
        query = (
            query.join(User.role_assignments)
            .join(RoleAssignment.role)
            .filter(Role.code == role_code)
            .distinct()
        )
    if active_only:
        query = query.filter(User.is_active.is_(True))
    users = query.all()
    return [
        UserOption(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            is_active=user.is_active,
            default_notary_id=user.default_notary_id,
            default_notary_label=user.default_notary.notary_label if user.default_notary else None,
        )
        for user in users
    ]


@router.get("", response_model=list[UserSummary])
def list_users(db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary", "notary"))):
    role_codes = get_role_codes(current_user)
    query = (
        db.query(User)
        .options(
            joinedload(User.default_notary),
            joinedload(User.role_assignments).joinedload(RoleAssignment.role),
            joinedload(User.role_assignments).joinedload(RoleAssignment.notary),
        )
        .order_by(User.full_name.asc())
    )
    if "super_admin" not in role_codes:
        query = query.filter(User.default_notary_id == current_user.default_notary_id)
    return [serialize_user(user) for user in query.all()]


@router.get("/{user_id}", response_model=UserDetail)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary"))):
    user = load_user_or_404(db, user_id)
    if not has_role(current_user, "super_admin"):
        manageable_notary_ids = get_manageable_notary_ids(current_user)
        visible = user.default_notary_id in manageable_notary_ids or any(
            assignment.notary_id in manageable_notary_ids for assignment in user.role_assignments if assignment.notary_id is not None
        )
        if not visible:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado para ver este usuario.")
    return serialize_user(user)


@router.post("", response_model=UserDetail, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary"))):
    if db.query(User).filter(User.email == payload.email).first() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un usuario con ese correo.")

    if payload.default_notary_id is not None:
        if db.query(Notary.id).filter(Notary.id == payload.default_notary_id).first() is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="La notaría por defecto no existe.")
        if not has_role(current_user, "super_admin") and payload.default_notary_id not in get_manageable_notary_ids(current_user):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No puedes asignar usuarios a esa notaría.")

    user = User(
        email=str(payload.email).lower(),
        full_name=payload.full_name.strip(),
        password_hash=get_password_hash(payload.password),
        is_active=payload.is_active,
        phone=payload.phone.strip() if payload.phone else None,
        job_title=payload.job_title.strip() if payload.job_title else None,
        default_notary_id=payload.default_notary_id,
    )
    db.add(user)
    db.flush()
    sync_assignments(db, user, payload.assignments, current_user)
    db.commit()
    return serialize_user(load_user_or_404(db, user.id))


@router.put("/{user_id}", response_model=UserDetail)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary"))):
    user = load_user_or_404(db, user_id)

    if not has_role(current_user, "super_admin"):
        manageable_notary_ids = get_manageable_notary_ids(current_user)
        visible = user.default_notary_id in manageable_notary_ids or any(
            assignment.notary_id in manageable_notary_ids for assignment in user.role_assignments if assignment.notary_id is not None
        )
        if not visible:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado para editar este usuario.")

    duplicate = db.query(User).filter(User.email == payload.email, User.id != user.id).first()
    if duplicate is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe otro usuario con ese correo.")

    if payload.default_notary_id is not None:
        if db.query(Notary.id).filter(Notary.id == payload.default_notary_id).first() is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="La notaría por defecto no existe.")
        if not has_role(current_user, "super_admin") and payload.default_notary_id not in get_manageable_notary_ids(current_user):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No puedes asignar usuarios a esa notaría.")

    user.email = str(payload.email).lower()
    user.full_name = payload.full_name.strip()
    user.is_active = payload.is_active
    user.phone = payload.phone.strip() if payload.phone else None
    user.job_title = payload.job_title.strip() if payload.job_title else None
    user.default_notary_id = payload.default_notary_id
    if payload.password:
        user.password_hash = get_password_hash(payload.password)

    sync_assignments(db, user, payload.assignments, current_user)
    db.commit()
    return serialize_user(load_user_or_404(db, user.id))


@router.patch("/{user_id}/status", response_model=UserDetail)
def update_user_status(user_id: int, payload: UserStatusUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary"))):
    user = load_user_or_404(db, user_id)
    if not has_role(current_user, "super_admin"):
        manageable_notary_ids = get_manageable_notary_ids(current_user)
        visible = user.default_notary_id in manageable_notary_ids or any(
            assignment.notary_id in manageable_notary_ids for assignment in user.role_assignments if assignment.notary_id is not None
        )
        if not visible:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado para actualizar este usuario.")
    user.is_active = payload.is_active
    db.commit()
    return serialize_user(load_user_or_404(db, user.id))
```

## File: app/schemas/__init__.py
```python

```

## File: app/schemas/act_catalog.py
```python
from __future__ import annotations

import json

from pydantic import BaseModel, ConfigDict, validator


class ActCatalogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    label: str
    roles_json: str
    is_active: bool


class ActItemIn(BaseModel):
    code: str
    label: str
    act_order: int
    roles_json: str = "[]"

    @validator("roles_json", pre=True)
    def clean_roles_json(cls, v):
        if isinstance(v, list):
            return json.dumps(v, ensure_ascii=False)
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                return json.dumps(parsed, ensure_ascii=False)
            except Exception:
                return "[]"
        return "[]"


class CaseActOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_id: int
    act_code: str
    act_label: str
    act_order: int
    roles_json: str


class CaseActsPayload(BaseModel):
    acts: list[ActItemIn]
```

## File: app/schemas/auth.py
```python
from pydantic import BaseModel, ConfigDict, EmailStr

from app.schemas.user import UserRoleAssignmentSummary


class AuthenticatedUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    is_active: bool
    roles: list[str]
    role_codes: list[str]
    permissions: list[str]
    default_notary: str | None = None
    assignments: list[UserRoleAssignmentSummary] = []


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AuthenticatedUser
```

## File: app/schemas/case.py
```python
from __future__ import annotations

import json
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.person import PersonCreate, PersonSummary
from app.schemas.template import TemplateSummary

CaseStateCode = Literal[
    "borrador",
    "en_diligenciamiento",
    "revision_cliente",
    "ajustes_solicitados",
    "revision_aprobador",
    "devuelto_aprobador",
    "revision_notario",
    "rechazado_notario",
    "aprobado_notario",
    "generado",
    "firmado_cargado",
    "cerrado",
]


class CaseStateDefinitionSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_type: str
    code: str
    label: str
    step_order: int
    is_initial: bool
    is_terminal: bool
    is_active: bool


class CaseTimelineEventSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_type: str
    from_state: str | None = None
    to_state: str | None = None
    comment: str | None = None
    metadata_json: str | None = None
    actor_user_id: int | None = None
    actor_user_name: str | None = None
    created_at: datetime


class CaseWorkflowEventSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_type: str
    actor_user_id: int | None = None
    actor_user_name: str | None = None
    actor_role_code: str | None = None
    from_state: str | None = None
    to_state: str | None = None
    field_name: str | None = None
    old_value: str | None = None
    new_value: str | None = None
    comment: str | None = None
    approved_version_id: int | None = None
    metadata_json: str | None = None
    created_at: datetime


class CaseCommentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_by_user_id: int | None = None
    created_by_user_name: str | None = None
    comment: str | None = None
    note: str | None = None
    created_at: datetime


class CaseParticipantPayload(BaseModel):
    role_code: str = Field(min_length=2, max_length=80)
    role_label: str = Field(min_length=2, max_length=120)
    person_id: int | None = None
    person: PersonCreate | None = None
    legal_entity_id: int | None = None


class CaseParticipantSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role_code: str
    role_label: str
    person_id: int
    person: PersonSummary
    snapshot_json: str
    created_at: datetime
    updated_at: datetime


class CaseActDataPayload(BaseModel):
    data_json: str = "{}"


class CaseActDataSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_id: int
    data_json: str
    gari_draft_text: str | None = None
    created_at: datetime
    updated_at: datetime

    @property
    def data(self) -> dict:
        try:
            return json.loads(self.data_json or "{}")
        except json.JSONDecodeError:
            return {}


class CaseDocumentVersionSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    version_number: int
    file_format: str
    storage_path: str
    original_filename: str
    generated_from_template_id: int | None = None
    created_by_user_id: int | None = None
    created_by_user_name: str | None = None
    placeholder_snapshot_json: str
    created_at: datetime
    download_url: str | None = None


class CaseDocumentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: str
    title: str
    current_version_number: int
    versions: list[CaseDocumentVersionSummary] = []


class CaseBase(BaseModel):
    notary_id: int
    template_id: int | None = None
    case_type: str = Field(min_length=2, max_length=80)
    act_type: str = Field(min_length=2, max_length=120)
    current_state: CaseStateCode = "borrador"
    current_owner_user_id: int | None = None
    client_user_id: int | None = None
    protocolist_user_id: int | None = None
    approver_user_id: int | None = None
    titular_notary_user_id: int | None = None
    substitute_notary_user_id: int | None = None
    requires_client_review: bool = False
    final_signed_uploaded: bool = False
    metadata_json: str = "{}"


class CaseCreate(CaseBase):
    consecutive: int | None = None
    year: int | None = None


class CaseCreateFromTemplate(BaseModel):
    template_id: int
    notary_id: int
    client_user_id: int | None = None
    current_owner_user_id: int | None = None
    protocolist_user_id: int | None = None
    approver_user_id: int | None = None
    titular_notary_user_id: int | None = None
    substitute_notary_user_id: int | None = None
    requires_client_review: bool = False
    metadata_json: str = "{}"


class CaseUpdate(CaseBase):
    consecutive: int
    year: int


class CaseStateUpdate(BaseModel):
    current_state: CaseStateCode
    comment: str | None = Field(default=None, max_length=4000)


class CaseOwnerUpdate(BaseModel):
    current_owner_user_id: int | None = None
    comment: str | None = Field(default=None, max_length=4000)


class CaseTimelineEventCreate(BaseModel):
    comment: str = Field(min_length=2, max_length=4000)
    metadata_json: str | None = None


class CaseCommentCreate(BaseModel):
    comment: str = Field(min_length=2, max_length=4000)


class CaseInternalNoteCreate(BaseModel):
    note: str = Field(min_length=2, max_length=4000)


class DraftGenerationRequest(BaseModel):
    comment: str | None = None


class GariGenerationRequest(BaseModel):
    comment: str | None = None
    correction_text: str | None = None


class ApprovalRequest(BaseModel):
    role_code: str = Field(min_length=2, max_length=80)
    comment: str | None = None


class ExportRequest(BaseModel):
    file_format: Literal["docx", "pdf"]


class FinalUploadRequest(BaseModel):
    filename: str = Field(min_length=3, max_length=255)
    content_base64: str = Field(min_length=10)
    comment: str | None = None


class CaseSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    notary_id: int
    notary_label: str
    template_id: int | None = None
    template_name: str | None = None
    case_type: str
    act_type: str
    consecutive: int
    year: int
    internal_case_number: str | None = None
    official_deed_number: str | None = None
    official_deed_year: int | None = None
    current_state: str
    current_owner_user_id: int | None = None
    current_owner_user_name: str | None = None
    created_by_user_id: int | None = None
    created_by_user_name: str | None = None
    client_user_id: int | None = None
    client_user_name: str | None = None
    protocolist_user_id: int | None = None
    protocolist_user_name: str | None = None
    approver_user_id: int | None = None
    approver_user_name: str | None = None
    titular_notary_user_id: int | None = None
    titular_notary_user_name: str | None = None
    substitute_notary_user_id: int | None = None
    substitute_notary_user_name: str | None = None
    requires_client_review: bool
    final_signed_uploaded: bool
    approved_at: datetime | None = None
    approved_by_user_id: int | None = None
    approved_by_user_name: str | None = None
    approved_by_role_code: str | None = None
    approved_document_version_id: int | None = None
    metadata_json: str
    created_at: datetime
    updated_at: datetime

    @property
    def metadata(self) -> dict:
        try:
            return json.loads(self.metadata_json or "{}")
        except json.JSONDecodeError:
            return {}


class CaseDetail(CaseSummary):
    template: TemplateSummary | None = None
    state_definitions: list[CaseStateDefinitionSummary] = []
    timeline_events: list[CaseTimelineEventSummary] = []
    workflow_events: list[CaseWorkflowEventSummary] = []
    participants: list[CaseParticipantSummary] = []
    act_data: CaseActDataSummary | None = None
    client_comments: list[CaseCommentSummary] = []
    internal_notes: list[CaseCommentSummary] = []
    documents: list[CaseDocumentSummary] = []


class CaseFilterOptions(BaseModel):
    case_types: list[str]
    act_types: list[str]
    states: list[str]
    owners: list[str]
    notaries: list[str]
```

## File: app/schemas/dashboard.py
```python
from datetime import date, datetime

from pydantic import BaseModel


class DashboardFilterOption(BaseModel):
    id: int | None = None
    label: str


class DashboardFilters(BaseModel):
    date_from: date | None = None
    date_to: date | None = None
    notary_id: int | None = None
    state: str | None = None
    act_type: str | None = None
    owner_user_id: int | None = None


class DashboardKpi(BaseModel):
    key: str
    label: str
    value: int
    detail: str | None = None
    tone: str = "default"


class DashboardChartDatum(BaseModel):
    label: str
    value: int
    highlight: bool = False


class DashboardTrendDatum(BaseModel):
    label: str
    value: int


class DashboardAlert(BaseModel):
    level: str
    title: str
    detail: str


class DashboardPilotReference(BaseModel):
    notary_id: int | None = None
    notary_label: str
    municipality: str
    department: str
    total_cases: int
    active_cases: int
    finalized_cases: int
    notes: str | None = None


class DashboardSystemStatusItem(BaseModel):
    key: str
    label: str
    status: str
    detail: str


class DashboardFilterOptions(BaseModel):
    notaries: list[DashboardFilterOption]
    states: list[DashboardFilterOption]
    act_types: list[DashboardFilterOption]
    owners: list[DashboardFilterOption]


class SuperAdminDashboardResponse(BaseModel):
    generated_at: datetime
    filters: DashboardFilters
    filter_options: DashboardFilterOptions
    kpis: list[DashboardKpi]
    documents_by_notary: list[DashboardChartDatum]
    documents_by_state: list[DashboardChartDatum]
    documents_by_act_type: list[DashboardChartDatum]
    temporal_trend: list[DashboardTrendDatum]
    owner_ranking: list[DashboardChartDatum]
    operational_focus: list[DashboardChartDatum]
    critical_alerts: list[DashboardAlert]
    system_status: list[DashboardSystemStatusItem]
    pilot_reference: DashboardPilotReference | None = None
    latest_import_reference: str | None = None
```

## File: app/schemas/legal_entity.py
```python
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class LegalEntityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nit: str
    name: str
    legal_representative: str | None = None
    municipality: str | None = None
    address: str | None = None
    phone: str | None = None
    email: str | None = None


class LegalEntityCreate(BaseModel):
    nit: str = Field(min_length=3, max_length=40)
    name: str = Field(min_length=2, max_length=200)
    legal_representative: str | None = Field(default=None, max_length=160)
    municipality: str | None = Field(default=None, max_length=120)
    address: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=40)
    email: str | None = Field(default=None, max_length=120)


class LegalEntityRepresentativeCreate(BaseModel):
    person_id: int
    power_type: str | None = Field(default=None, max_length=120)


class LegalEntityRepresentativeOut(BaseModel):
    id: int
    legal_entity_id: int
    person_id: int
    person_name: str
    person_document: str
    power_type: str | None = None
    is_active: bool
```

## File: app/schemas/notary.py
```python
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

CommercialStatus = Literal[
    "prospecto",
    "contactado",
    "en seguimiento",
    "reunión agendada",
    "propuesta enviada",
    "negociación",
    "cerrado ganado",
    "cerrado perdido",
    "no interesado",
]
PriorityLevel = Literal["baja", "media", "alta", "crítica"]
PotentialLevel = Literal["bajo", "medio", "alto", "estratégico"]


class NotaryAuditLogSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_type: str
    field_name: str | None = None
    old_value: str | None = None
    new_value: str | None = None
    comment: str | None = None
    actor_user_id: int | None = None
    actor_user_name: str | None = None
    created_at: datetime


class NotaryBase(BaseModel):
    legal_name: str = Field(min_length=2, max_length=160)
    commercial_name: str = Field(min_length=2, max_length=120)
    city: str = Field(min_length=2, max_length=80)
    department: str = Field(default="Antioquia", min_length=2, max_length=80)
    municipality: str = Field(min_length=2, max_length=120)
    notary_label: str = Field(min_length=1, max_length=160)
    address: str | None = Field(default=None, max_length=255)
    phone: str | None = None
    email: EmailStr | None = None
    current_notary_name: str | None = Field(default=None, max_length=160)
    business_hours: str | None = None
    logo_url: str | None = Field(default=None, max_length=255)
    primary_color: str = Field(default="#0D2E5D", max_length=20)
    secondary_color: str = Field(default="#4D5B7C", max_length=20)
    base_color: str = Field(default="#F4F7FB", max_length=20)
    institutional_data: str = Field(default="", max_length=4000)
    commercial_status: CommercialStatus = "prospecto"
    commercial_owner: str | None = Field(default=None, max_length=120)
    commercial_owner_user_id: int | None = None
    main_contact_name: str | None = Field(default=None, max_length=160)
    main_contact_title: str | None = Field(default=None, max_length=120)
    commercial_phone: str | None = None
    commercial_email: EmailStr | None = None
    last_management_at: datetime | None = None
    next_management_at: datetime | None = None
    commercial_notes: str | None = None
    priority: PriorityLevel = "media"
    lead_source: str | None = Field(default=None, max_length=120)
    potential: PotentialLevel | None = None
    internal_observations: str | None = None
    is_active: bool = True


class NotaryCreate(NotaryBase):
    pass


class NotaryUpdate(NotaryBase):
    pass


class NotaryStatusUpdate(BaseModel):
    is_active: bool


class CommercialActivityBase(BaseModel):
    occurred_at: datetime
    management_type: str = Field(min_length=2, max_length=60)
    comment: str = Field(min_length=2, max_length=4000)
    responsible: str | None = Field(default=None, max_length=120)
    responsible_user_id: int | None = None
    result: str | None = Field(default=None, max_length=160)
    next_action: str | None = None


class CommercialActivityCreate(CommercialActivityBase):
    pass


class CommercialActivitySummary(CommercialActivityBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    notary_id: int
    responsible_user_name: str | None = None


class NotarySummary(NotaryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    accent_color: str
    activity_count: int = 0
    commercial_owner_display: str | None = None
    commercial_owner_user_name: str | None = None


class NotaryDetail(NotarySummary):
    commercial_activities: list[CommercialActivitySummary] = []
    crm_audit_logs: list[NotaryAuditLogSummary] = []


class NotaryImportSourceRow(BaseModel):
    MUNICIPIO: str = Field(min_length=2, max_length=120)
    NOTARÍA: str = Field(min_length=1, max_length=160)
    DIRECCIÓN: str | None = Field(default=None, max_length=255)
    TELÉFONO: str | None = None
    CORREO_ELECTRÓNICO: EmailStr | None = None
    NOTARIO_A: str | None = Field(default=None, max_length=160, alias="NOTARIO/A")
    HORARIO: str | None = None

    model_config = ConfigDict(populate_by_name=True)


class NotaryImportRequest(BaseModel):
    rows: list[NotaryImportSourceRow] = Field(min_length=1)
    overwrite_existing: bool = True


class NotaryFileImportRequest(BaseModel):
    source_path: str = Field(default=r"C:\EasyProNotarial-2\Archivos_referencia\Notarias_Antioquia_EasyProNotarial.xlsx")
    overwrite_existing: bool = True


class NotaryImportResult(BaseModel):
    row_number: int
    action: str
    notary_id: int | None = None
    slug: str | None = None
    duplicate_key: str | None = None


class NotaryImportRowError(BaseModel):
    row_number: int
    municipality: str | None = None
    notary_label: str | None = None
    error: str


class NotaryImportSummary(BaseModel):
    source_path: str | None = None
    processed: int
    created: int
    updated: int
    omitted: int
    errors: list[NotaryImportRowError]
    results: list[NotaryImportResult]


class NotaryFilterOptions(BaseModel):
    municipalities: list[str]
    commercial_owners: list[str]
    priorities: list[str]
    commercial_statuses: list[str]
```

## File: app/schemas/person.py
```python
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PersonBase(BaseModel):
    document_type: str = Field(min_length=2, max_length=40)
    document_number: str = Field(min_length=3, max_length=40)
    full_name: str = Field(min_length=3, max_length=160)
    sex: str | None = Field(default=None, max_length=20)
    nationality: str | None = Field(default=None, max_length=80)
    marital_status: str | None = Field(default=None, max_length=40)
    profession: str | None = Field(default=None, max_length=120)
    municipality: str | None = Field(default=None, max_length=120)
    is_transient: bool = False
    phone: str | None = Field(default=None, max_length=40)
    address: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = None
    metadata_json: str = "{}"


class PersonCreate(PersonBase):
    pass


class PersonUpdate(PersonBase):
    pass


class PersonSummary(PersonBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
```

## File: app/schemas/template.py
```python
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TemplateRequiredRolePayload(BaseModel):
    role_code: str = Field(min_length=2, max_length=80)
    label: str = Field(min_length=2, max_length=120)
    is_required: bool = True
    step_order: int = 1


class TemplateFieldPayload(BaseModel):
    field_code: str = Field(min_length=2, max_length=120)
    label: str = Field(min_length=2, max_length=160)
    field_type: str = Field(default="text", max_length=40)
    section: str = Field(default="acto", max_length=80)
    is_required: bool = True
    options_json: str | None = None
    placeholder_key: str | None = None
    help_text: str | None = None
    step_order: int = 1


class TemplateUploadPayload(BaseModel):
    filename: str = Field(min_length=3, max_length=255)
    content_base64: str = Field(min_length=10)


class TemplateBase(BaseModel):
    name: str = Field(min_length=3, max_length=160)
    case_type: str = Field(default="escritura", min_length=2, max_length=80)
    document_type: str = Field(min_length=2, max_length=120)
    description: str | None = None
    scope_type: str = Field(default="global", max_length=20)
    notary_id: int | None = None
    is_active: bool = True
    internal_variable_map_json: str = "{}"
    required_roles: list[TemplateRequiredRolePayload] = []
    fields: list[TemplateFieldPayload] = []
    upload: TemplateUploadPayload | None = None


class TemplateCreate(TemplateBase):
    pass


class TemplateUpdate(TemplateBase):
    pass


class TemplateRequiredRoleSummary(TemplateRequiredRolePayload):
    model_config = ConfigDict(from_attributes=True)

    id: int


class TemplateFieldSummary(TemplateFieldPayload):
    model_config = ConfigDict(from_attributes=True)

    id: int


class TemplateSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    case_type: str
    document_type: str
    description: str | None = None
    scope_type: str
    notary_id: int | None = None
    notary_label: str | None = None
    is_active: bool
    source_filename: str | None = None
    storage_path: str | None = None
    internal_variable_map_json: str
    created_at: datetime
    updated_at: datetime
    required_roles: list[TemplateRequiredRoleSummary] = []
    fields: list[TemplateFieldSummary] = []
```

## File: app/schemas/user.py
```python
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRoleAssignmentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role_id: int
    role_code: str
    role_name: str
    notary_id: int | None = None
    notary_label: str | None = None


class RoleCatalogItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    scope: str
    description: str


class RoleCreate(BaseModel):
    code: str = Field(min_length=2, max_length=50)
    name: str = Field(min_length=2, max_length=80)
    scope: str = Field(min_length=2, max_length=30)
    description: str = Field(default="", max_length=255)


class RoleUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    description: str = Field(default="", max_length=255)


class RolePermissionItem(BaseModel):
    module_code: str = Field(min_length=1, max_length=80)
    can_access: bool


class UserRoleAssignmentInput(BaseModel):
    role_code: str = Field(min_length=2, max_length=50)
    notary_id: int | None = None


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=160)
    is_active: bool = True
    phone: str | None = Field(default=None, max_length=40)
    job_title: str | None = Field(default=None, max_length=80)
    default_notary_id: int | None = None
    assignments: list[UserRoleAssignmentInput] = []


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=120)


class UserUpdate(UserBase):
    password: str | None = Field(default=None, min_length=8, max_length=120)


class UserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    is_active: bool
    phone: str | None = None
    job_title: str | None = None
    default_notary_id: int | None = None
    default_notary_label: str | None = None
    roles: list[str]
    assignments: list[UserRoleAssignmentSummary]


class UserDetail(UserSummary):
    pass


class UserOption(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    is_active: bool
    default_notary_id: int | None = None
    default_notary_label: str | None = None


class UserStatusUpdate(BaseModel):
    is_active: bool
```

## File: app/seeds/__init__.py
```python

```

## File: app/seeds/seed_act_catalog.py
```python
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.act_catalog import ActCatalog

SEED_ACTS = [
    {"code": "liberacion_hipoteca", "label": "Liberación parcial de hipoteca", "roles": ["banco_libera", "fideicomiso"]},
    {"code": "protocolizacion_cto", "label": "Protocolización CTO", "roles": ["fideicomiso", "constructora"]},
    {"code": "compraventa_vis", "label": "Compraventa VIS", "roles": ["fideicomiso", "compradores"]},
    {"code": "renuncia_resolutoria", "label": "Renuncia condición resolutoria", "roles": ["fideicomiso", "compradores"]},
    {"code": "cancelacion_comodato", "label": "Cancelación comodato precario", "roles": ["fideicomiso", "constructora"]},
    {"code": "constitucion_hipoteca", "label": "Constitución hipoteca 1er grado", "roles": ["compradores", "banco_hipoteca"]},
    {"code": "patrimonio_familia", "label": "Constitución patrimonio de familia", "roles": ["compradores"]},
    {"code": "poder_especial", "label": "Poder especial", "roles": ["compradores", "constructora"]},
    {"code": "correccion_rc", "label": "Corrección de Registro Civil", "roles": ["inscrito"]},
    {"code": "salida_pais", "label": "Permiso de salida del país", "roles": ["padre_otorgante", "madre_aceptante", "menor"]},
    {"code": "poder_general", "label": "Poder general", "roles": ["poderdante", "apoderado"]},
]


def seed_act_catalog(db: Session) -> tuple[int, int]:
    created = 0
    updated = 0
    for payload in SEED_ACTS:
        code = payload["code"].strip()
        label = payload["label"].strip()
        roles_json = json.dumps(payload["roles"], ensure_ascii=False)
        existing = db.query(ActCatalog).filter(ActCatalog.code == code).first()
        if existing is None:
            db.add(
                ActCatalog(
                    code=code,
                    label=label,
                    roles_json=roles_json,
                    is_active=True,
                )
            )
            created += 1
            continue
        existing.label = label
        existing.roles_json = roles_json
        existing.is_active = True
        updated += 1
    db.commit()
    return created, updated


def main() -> None:
    with SessionLocal() as db:
        created, updated = seed_act_catalog(db)
        print(f"[OK] Actos insertados: {created}; actualizados: {updated}.")


if __name__ == "__main__":
    main()
```

## File: app/seeds/seed_document_templates.py
```python
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.document_template import DocumentTemplate
from app.models.template_field import TemplateField
from app.models.template_required_role import TemplateRequiredRole
from app.services.gari_document_service import get_supabase_client
from app.services.storage import copy_template_file

SEED_DIR = Path(__file__).resolve().parent
SEED_TEMPLATES_DIR = SEED_DIR / "templates"
SUPABASE_BUCKET = "documentos"
SUPABASE_TEMPLATE_PREFIX = "templates"


def role_def(role_code: str, label: str, is_required: bool, step_order: int) -> dict[str, Any]:
    return {
        "role_code": role_code,
        "label": label,
        "is_required": is_required,
        "step_order": step_order,
    }


def field_def(
    field_code: str,
    label: str,
    step_order: int,
    *,
    field_type: str = "text",
    is_required: bool = True,
    section: str = "acto",
    placeholder_key: str | None = None,
    options_json: str | None = None,
) -> dict[str, Any]:
    return {
        "field_code": field_code,
        "label": label,
        "field_type": field_type,
        "section": section,
        "is_required": is_required,
        "step_order": step_order,
        "placeholder_key": placeholder_key,
        "options_json": options_json,
    }


TEMPLATE_DEFINITIONS: list[dict[str, Any]] = [
    {
        "slug": "aragua-parq-1c",
        "name": "Aragua Parqueadero 1 Comprador",
        "case_type": "escritura",
        "document_type": "Compraventa VIS",
        "description": "Compraventa VIS para Parqueadero Aragua con un comprador principal.",
        "scope_type": "global",
        "is_active": True,
        "required_roles": [
            role_def("comprador_1", "Comprador(a) 1", True, 1),
            role_def("apoderado_banco_libera", "Apoderado(a) Banco que libera", True, 2),
            role_def("apoderado_fideicomiso", "Apoderado(a) del Fideicomiso", True, 3),
            role_def("apoderado_fideicomitente", "Apoderado(a) del Fideicomitente", True, 4),
        ],
        "fields": [
            field_def("numero_parqueadero", "Número de parqueadero", 1),
            field_def("numero_matricula", "Matrícula inmobiliaria", 2),
            field_def("valor_de_la_venta", "Valor de la venta", 3, field_type="currency"),
            field_def("dia_elaboracion", "Día elaboración", 4),
            field_def("mes_elaboracion", "Mes elaboración", 5),
            field_def("ano_elaboracion", "Año elaboración", 6),
            field_def("derechos_notariales", "Derechos notariales", 7, field_type="currency"),
            field_def("iva", "IVA", 8, field_type="currency"),
            field_def("superintendencia", "Superintendencia", 9, field_type="currency"),
            field_def("fondo_notariado", "Fondo notariado", 10, field_type="currency"),
            field_def("consecutivo_hojas", "Consecutivo hojas protocolo", 11, is_required=False),
        ],
    },
    {
        "slug": "aragua-parq-2c",
        "name": "Aragua Parqueadero 2 Compradores",
        "case_type": "escritura",
        "document_type": "Compraventa VIS",
        "description": "Compraventa VIS para Parqueadero Aragua con dos compradores.",
        "scope_type": "global",
        "is_active": True,
        "required_roles": [
            role_def("comprador_1", "Comprador(a) 1", True, 1),
            role_def("comprador_2", "Comprador(a) 2", False, 2),
            role_def("apoderado_banco_libera", "Apoderado(a) Banco que libera", True, 3),
            role_def("apoderado_fideicomiso", "Apoderado(a) del Fideicomiso", True, 4),
            role_def("apoderado_fideicomitente", "Apoderado(a) del Fideicomitente", True, 5),
        ],
        "fields": [
            field_def("numero_parqueadero", "Número de parqueadero", 1),
            field_def("numero_matricula", "Matrícula inmobiliaria", 2),
            field_def("valor_de_la_venta", "Valor de la venta", 3, field_type="currency"),
            field_def("dia_elaboracion", "Día elaboración", 4),
            field_def("mes_elaboracion", "Mes elaboración", 5),
            field_def("ano_elaboracion", "Año elaboración", 6),
            field_def("derechos_notariales", "Derechos notariales", 7, field_type="currency"),
            field_def("iva", "IVA", 8, field_type="currency"),
            field_def("superintendencia", "Superintendencia", 9, field_type="currency"),
            field_def("fondo_notariado", "Fondo notariado", 10, field_type="currency"),
            field_def("consecutivo_hojas", "Consecutivo hojas protocolo", 11, is_required=False),
        ],
    },
    {
        "slug": "aragua-parq-3c",
        "name": "Aragua Parqueadero 3 Compradores",
        "case_type": "escritura",
        "document_type": "Compraventa VIS",
        "description": "Compraventa VIS para Parqueadero Aragua con tres compradores.",
        "scope_type": "global",
        "is_active": True,
        "required_roles": [
            role_def("comprador_1", "Comprador(a) 1", True, 1),
            role_def("comprador_2", "Comprador(a) 2", False, 2),
            role_def("comprador_3", "Comprador(a) 3", False, 3),
            role_def("apoderado_banco_libera", "Apoderado(a) Banco que libera", True, 4),
            role_def("apoderado_fideicomiso", "Apoderado(a) del Fideicomiso", True, 5),
            role_def("apoderado_fideicomitente", "Apoderado(a) del Fideicomitente", True, 6),
        ],
        "fields": [
            field_def("numero_parqueadero", "Número de parqueadero", 1),
            field_def("numero_matricula", "Matrícula inmobiliaria", 2),
            field_def("valor_de_la_venta", "Valor de la venta", 3, field_type="currency"),
            field_def("dia_elaboracion", "Día elaboración", 4),
            field_def("mes_elaboracion", "Mes elaboración", 5),
            field_def("ano_elaboracion", "Año elaboración", 6),
            field_def("derechos_notariales", "Derechos notariales", 7, field_type="currency"),
            field_def("iva", "IVA", 8, field_type="currency"),
            field_def("superintendencia", "Superintendencia", 9, field_type="currency"),
            field_def("fondo_notariado", "Fondo notariado", 10, field_type="currency"),
            field_def("consecutivo_hojas", "Consecutivo hojas protocolo", 11, is_required=False),
        ],
    },
    {
        "slug": "torre6-contado",
        "name": "Torre 6 Contado (Davivienda)",
        "case_type": "escritura",
        "document_type": "Compraventa VIS",
        "description": "Compraventa VIS Torre 6 en modalidad de contado con soporte de Davivienda.",
        "scope_type": "global",
        "is_active": True,
        "required_roles": [
            role_def("comprador_1", "Comprador(a) 1", True, 1),
            role_def("apoderado_banco_libera", "Apoderado(a) Banco que libera", True, 2),
            role_def("apoderado_fideicomiso", "Apoderado(a) del Fideicomiso", True, 3),
            role_def("apoderado_fideicomitente", "Apoderado(a) del Fideicomitente", True, 4),
        ],
        "fields": [
            field_def("numero_apartamento", "Número de apartamento", 1),
            field_def("numero_matricula", "Matrícula inmobiliaria", 2),
            field_def("valor_de_la_venta", "Valor de la venta", 3, field_type="currency"),
            field_def("dia_elaboracion", "Día elaboración", 4),
            field_def("mes_elaboracion", "Mes elaboración", 5),
            field_def("ano_elaboracion", "Año elaboración", 6),
            field_def("derechos_notariales", "Derechos notariales", 7, field_type="currency"),
            field_def("iva", "IVA", 8, field_type="currency"),
            field_def("superintendencia", "Superintendencia", 9, field_type="currency"),
            field_def("fondo_notariado", "Fondo notariado", 10, field_type="currency"),
            field_def("consecutivo_hojas", "Consecutivo hojas protocolo", 11, is_required=False),
        ],
    },
    {
        "slug": "jaggua-bogota-1c",
        "name": "Jaggua Bogotá 1 Comprador (Banco de Bogotá)",
        "case_type": "escritura",
        "document_type": "Compraventa VIS + Hipoteca",
        "description": "Compraventa VIS con hipoteca para el proyecto Jaggua Bogotá con un comprador.",
        "scope_type": "global",
        "is_active": True,
        "required_roles": [
            role_def("comprador_1", "Comprador(a) 1", True, 1),
            role_def("apoderado_banco_libera", "Apoderado(a) FNA que libera", True, 2),
            role_def("apoderado_fideicomiso", "Apoderado(a) del Fideicomiso", True, 3),
            role_def("apoderado_fideicomitente", "Apoderado(a) del Fideicomitente", True, 4),
            role_def("apoderado_banco_hipoteca", "Apoderado(a) Banco de Bogotá hipoteca", True, 5),
        ],
        "fields": [
            field_def("numero_apartamento", "Número de apartamento", 1),
            field_def("numero_matricula", "Matrícula inmobiliaria", 2),
            field_def("valor_de_la_venta", "Valor de la venta", 3, field_type="currency"),
            field_def("valor_del_acto_hipoteca", "Valor del acto de hipoteca", 4, field_type="currency"),
            field_def("dia_elaboracion", "Día elaboración", 5),
            field_def("mes_elaboracion", "Mes elaboración", 6),
            field_def("ano_elaboracion", "Año elaboración", 7),
            field_def("derechos_notariales", "Derechos notariales", 8, field_type="currency"),
            field_def("iva", "IVA", 9, field_type="currency"),
            field_def("superintendencia", "Superintendencia", 10, field_type="currency"),
            field_def("fondo_notariado", "Fondo notariado", 11, field_type="currency"),
            field_def("consecutivo_hojas", "Consecutivo hojas protocolo", 12, is_required=False),
        ],
    },
    {
        "slug": "jaggua-bogota-2c",
        "name": "Jaggua Bogotá 2 Compradores (Banco de Bogotá)",
        "case_type": "escritura",
        "document_type": "Compraventa VIS + Hipoteca",
        "description": "Compraventa VIS con hipoteca para el proyecto Jaggua Bogotá con dos compradores.",
        "scope_type": "global",
        "is_active": True,
        "required_roles": [
            role_def("comprador_1", "Comprador(a) 1", True, 1),
            role_def("comprador_2", "Comprador(a) 2", False, 2),
            role_def("apoderado_banco_libera", "Apoderado(a) FNA que libera", True, 3),
            role_def("apoderado_fideicomiso", "Apoderado(a) del Fideicomiso", True, 4),
            role_def("apoderado_fideicomitente", "Apoderado(a) del Fideicomitente", True, 5),
            role_def("apoderado_banco_hipoteca", "Apoderado(a) Banco de Bogotá hipoteca", True, 6),
        ],
        "fields": [
            field_def("numero_apartamento", "Número de apartamento", 1),
            field_def("numero_matricula", "Matrícula inmobiliaria", 2),
            field_def("valor_de_la_venta", "Valor de la venta", 3, field_type="currency"),
            field_def("valor_del_acto_hipoteca", "Valor del acto de hipoteca", 4, field_type="currency"),
            field_def("dia_elaboracion", "Día elaboración", 5),
            field_def("mes_elaboracion", "Mes elaboración", 6),
            field_def("ano_elaboracion", "Año elaboración", 7),
            field_def("derechos_notariales", "Derechos notariales", 8, field_type="currency"),
            field_def("iva", "IVA", 9, field_type="currency"),
            field_def("superintendencia", "Superintendencia", 10, field_type="currency"),
            field_def("fondo_notariado", "Fondo notariado", 11, field_type="currency"),
            field_def("consecutivo_hojas", "Consecutivo hojas protocolo", 12, is_required=False),
        ],
    },
    {
        "slug": "correccion-registro-civil",
        "name": "Corrección de Registro Civil",
        "case_type": "escritura",
        "document_type": "Corrección RC",
        "description": "Corrección de registro civil con soporte de inconsistencia y resoluciones notariales.",
        "scope_type": "global",
        "is_active": True,
        "required_roles": [
            role_def("inscrito", "Inscrito(a) / Compareciente", True, 1),
        ],
        "fields": [
            field_def("notaria_donde_inscrito", "Notaría donde está inscrito", 1),
            field_def("numero_libro", "Número de libro", 2),
            field_def("numero_folio", "Número de folio", 3),
            field_def("inconsistencias_a_corregir", "Inconsistencias a corregir", 4, field_type="textarea"),
            field_def("numero_resolucion_notario", "Número resolución notario encargado", 5, is_required=False),
            field_def("fecha_resolucion_notario", "Fecha resolución notario encargado", 6, field_type="date", is_required=False),
            field_def("dia_elaboracion", "Día elaboración", 7),
            field_def("mes_elaboracion", "Mes elaboración", 8),
            field_def("ano_elaboracion", "Año elaboración", 9),
            field_def("derechos_notariales", "Derechos notariales", 10, field_type="currency"),
            field_def("iva", "IVA", 11, field_type="currency"),
            field_def("superintendencia", "Superintendencia", 12, field_type="currency"),
            field_def("fondo_notariado", "Fondo notariado", 13, field_type="currency"),
            field_def("consecutivo_hojas", "Consecutivo hojas protocolo", 14, is_required=False),
        ],
    },
    {
        "slug": "salida-del-pais",
        "name": "Permiso de Salida del País",
        "case_type": "escritura",
        "document_type": "Salida del País",
        "description": "Permiso de salida del país para comparecientes y menor de edad.",
        "scope_type": "global",
        "is_active": True,
        "required_roles": [
            role_def("otorgante", "Padre otorgante", True, 1),
            role_def("aceptante", "Madre aceptante", True, 2),
            role_def("menor", "Menor de edad", True, 3),
        ],
        "fields": [
            field_def("dia_elaboracion", "Día elaboración", 1),
            field_def("mes_elaboracion", "Mes elaboración", 2),
            field_def("ano_elaboracion", "Año elaboración", 3),
            field_def("derechos_notariales", "Derechos notariales", 4, field_type="currency"),
            field_def("iva", "IVA", 5, field_type="currency"),
            field_def("superintendencia", "Superintendencia", 6, field_type="currency"),
            field_def("fondo_notariado", "Fondo notariado", 7, field_type="currency"),
            field_def("consecutivo_hojas", "Consecutivo hojas protocolo", 8, is_required=False),
        ],
    },
]


def sync_template_source_file(slug: str) -> tuple[str | None, str | None]:
    source_path = SEED_TEMPLATES_DIR / f"{slug}.docx"
    if not source_path.exists():
        return None, None

    source_filename, storage_path = copy_template_file(source_path, slug)
    local_storage_path = Path(storage_path)
    try:
        supabase = get_supabase_client()
    except Exception as exc:  # pragma: no cover - external dependency
        print(f"[WARN] No fue posible inicializar Supabase para {slug}: {exc}")
        return source_filename, str(local_storage_path)

    try:
        supabase.storage.from_(SUPABASE_BUCKET).upload(
            path=f"{SUPABASE_TEMPLATE_PREFIX}/{slug}.docx",
            file=local_storage_path.read_bytes(),
            file_options={
                "content-type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "upsert": "true",
            },
        )
        print(f"[OK] Subida a Supabase completada para {slug}.docx")
    except Exception as exc:  # pragma: no cover - external dependency
        print(f"[WARN] No fue posible subir {slug}.docx a Supabase: {exc}")
    return source_filename, str(local_storage_path)


def upsert_template(db: Session, definition: dict[str, Any]) -> DocumentTemplate:
    template = db.query(DocumentTemplate).filter(DocumentTemplate.slug == definition["slug"]).first()
    if template is None:
        template = DocumentTemplate()
        db.add(template)

    template.name = definition["name"]
    template.slug = definition["slug"]
    template.case_type = definition["case_type"]
    template.document_type = definition["document_type"]
    template.description = definition.get("description")
    template.scope_type = definition.get("scope_type", "global")
    template.notary_id = None
    template.is_active = bool(definition.get("is_active", True))
    template.internal_variable_map_json = definition.get("internal_variable_map_json", "{}")
    db.flush()
    return template


def replace_roles_and_fields(db: Session, template: DocumentTemplate, definition: dict[str, Any]) -> None:
    db.query(TemplateRequiredRole).filter(TemplateRequiredRole.template_id == template.id).delete(synchronize_session=False)
    db.query(TemplateField).filter(TemplateField.template_id == template.id).delete(synchronize_session=False)
    db.flush()

    for role in definition["required_roles"]:
        db.add(
            TemplateRequiredRole(
                template_id=template.id,
                role_code=role["role_code"],
                label=role["label"],
                is_required=role["is_required"],
                step_order=role["step_order"],
            )
        )

    for field in definition["fields"]:
        db.add(
            TemplateField(
                template_id=template.id,
                field_code=field["field_code"],
                label=field["label"],
                field_type=field["field_type"],
                section=field["section"],
                is_required=field["is_required"],
                options_json=field["options_json"],
                placeholder_key=field["placeholder_key"],
                help_text=None,
                step_order=field["step_order"],
            )
        )


def seed_document_templates() -> None:
    SEED_TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

    with SessionLocal() as db:
        for definition in TEMPLATE_DEFINITIONS:
            template = upsert_template(db, definition)
            replace_roles_and_fields(db, template, definition)
            db.commit()

            source_filename, storage_path = sync_template_source_file(template.slug)
            template.source_filename = source_filename
            template.storage_path = storage_path
            db.commit()
            print(f"[OK] Plantilla '{template.slug}' sincronizada.")


def main() -> None:
    seed_document_templates()


if __name__ == "__main__":
    main()
```

## File: app/seeds/seed_legal_entities.py
```python
from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.legal_entity import LegalEntity

SEED_LEGAL_ENTITIES = [
    {"nit": "830.054.539-0", "name": "Fiduciaria Bancolombia S.A."},
    {"nit": "900.082.107-5", "name": "Constructora Contex S.A.S. BIC"},
    {"nit": "890.903.938-8", "name": "Bancolombia S.A."},
    {"nit": "860.034.313-7", "name": "Banco Davivienda S.A."},
    {"nit": "899.999.284-4", "name": "Fondo Nacional del Ahorro S.A."},
    {"nit": "860.002.964-4", "name": "Banco de Bogotá S.A."},
]


def seed_legal_entities(db: Session) -> tuple[int, int]:
    created = 0
    skipped = 0
    for payload in SEED_LEGAL_ENTITIES:
        nit = payload["nit"].strip()
        name = payload["name"].strip()
        existing = db.query(LegalEntity).filter(LegalEntity.nit == nit).first()
        if existing is not None:
            skipped += 1
            continue
        db.add(LegalEntity(nit=nit, name=name))
        created += 1
    db.commit()
    return created, skipped


def main() -> None:
    with SessionLocal() as db:
        created, skipped = seed_legal_entities(db)
        print(f"[OK] Entidades jurídicas insertadas: {created}; existentes omitidas: {skipped}.")


if __name__ == "__main__":
    main()
```

## File: app/services/__init__.py
```python

```

## File: app/services/auth.py
```python
from datetime import timedelta

from sqlalchemy.orm import Session, joinedload

from app.core.config import get_settings
from app.core.deps import get_permissions, get_role_codes
from app.core.security import create_access_token, verify_password
from app.models.role_assignment import RoleAssignment
from app.models.user import User
from app.schemas.user import UserRoleAssignmentSummary


class AuthenticationError(Exception):
    pass


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = (
        db.query(User)
        .options(
            joinedload(User.default_notary),
            joinedload(User.role_assignments).joinedload(RoleAssignment.role),
            joinedload(User.role_assignments).joinedload(RoleAssignment.notary),
        )
        .filter(User.email == email)
        .first()
    )
    if user is None or not user.is_active or not verify_password(password, user.password_hash):
        raise AuthenticationError("Credenciales inválidas.")
    return user


def serialize_assignments(user: User) -> list[UserRoleAssignmentSummary]:
    return [
        UserRoleAssignmentSummary(
            id=assignment.id,
            role_id=assignment.role_id,
            role_code=assignment.role.code,
            role_name=assignment.role.name,
            notary_id=assignment.notary_id,
            notary_label=assignment.notary.notary_label if assignment.notary else None,
        )
        for assignment in sorted(
            user.role_assignments,
            key=lambda item: (item.role.name, item.notary.notary_label if item.notary else ""),
        )
    ]


def serialize_user(user: User) -> dict:
    assignment_labels = []
    for assignment in user.role_assignments:
        suffix = f"@{assignment.notary.slug}" if assignment.notary else "@global"
        assignment_labels.append(f"{assignment.role.code}{suffix}")

    role_codes = sorted(get_role_codes(user))
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "roles": assignment_labels,
        "role_codes": role_codes,
        "permissions": get_permissions(user),
        "default_notary": user.default_notary.notary_label if user.default_notary else None,
        "assignments": serialize_assignments(user),
    }


def build_login_response(user: User) -> dict:
    settings = get_settings()
    claims = {
        "email": user.email,
        "roles": sorted(get_role_codes(user)),
        "notary_id": user.default_notary_id,
        "permissions": get_permissions(user),
    }
    token = create_access_token(
        subject=str(user.id),
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        extra_claims=claims,
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": serialize_user(user),
    }
```

## File: app/services/document_generation.py
```python
from __future__ import annotations

import html
import json
import re
import zipfile
from pathlib import Path

PLACEHOLDER_PATTERN = re.compile(r"\{\{.*?\}\}", re.DOTALL)
XML_TAG_PATTERN = re.compile(r"<[^>]+>")


def normalize_placeholder(raw: str) -> str:
    plain = XML_TAG_PATTERN.sub("", raw)
    plain = plain.replace("\n", "").replace("\r", "").replace("\t", "")
    plain = re.sub(r"\s+", "", plain)
    return plain


def render_docx_template(source_path: str | Path, destination_path: str | Path, replacements: dict[str, str]) -> None:
    source = Path(source_path)
    destination = Path(destination_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(source, "r") as source_zip, zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as dest_zip:
        for item in source_zip.infolist():
            data = source_zip.read(item.filename)
            if item.filename.endswith(".xml"):
                text = data.decode("utf-8", errors="ignore")

                def replace_match(match: re.Match[str]) -> str:
                    token = normalize_placeholder(match.group(0))
                    if token in replacements:
                        return html.escape(str(replacements[token] or ""))
                    return match.group(0)

                text = PLACEHOLDER_PATTERN.sub(replace_match, text)
                data = text.encode("utf-8")
            dest_zip.writestr(item, data)


def extract_text_from_docx(source_path: str | Path) -> str:
    """
    Extrae el texto plano del Word para usarlo como referencia para Gari.
    """
    source = Path(source_path)
    text_parts: list[str] = []
    with zipfile.ZipFile(source, "r") as zf:
        if "word/document.xml" in zf.namelist():
            xml_content = zf.read("word/document.xml").decode("utf-8", errors="ignore")
            clean = re.sub(r"<[^>]+>", " ", xml_content)
            clean = re.sub(r"\s+", " ", clean).strip()
            text_parts.append(clean)
    return "\n".join(text_parts)


def generate_plain_pdf(destination_path: str | Path, title: str, lines: list[str]) -> None:
    escaped_lines: list[str] = []
    for raw in [title, *lines]:
        text = (raw or "").replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        escaped_lines.append(text)

    content_lines = ["BT", "/F1 12 Tf", "50 800 Td"]
    first = True
    for line in escaped_lines:
        if first:
            content_lines.append(f"({line}) Tj")
            first = False
        else:
            content_lines.append("0 -16 Td")
            content_lines.append(f"({line}) Tj")
    content_lines.append("ET")
    stream = "\n".join(content_lines).encode("latin-1", errors="replace")

    objects = [
        b"1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n",
        b"2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj\n",
        b"3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>endobj\n",
        f"4 0 obj<< /Length {len(stream)} >>stream\n".encode("ascii") + stream + b"\nendstream endobj\n",
        b"5 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>endobj\n",
    ]

    destination = Path(destination_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as handle:
        handle.write(b"%PDF-1.4\n")
        offsets = [0]
        for obj in objects:
            offsets.append(handle.tell())
            handle.write(obj)
        xref_start = handle.tell()
        handle.write(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
        handle.write(b"0000000000 65535 f \n")
        for offset in offsets[1:]:
            handle.write(f"{offset:010d} 00000 n \n".encode("ascii"))
        handle.write(f"trailer<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF".encode("ascii"))


def build_case_text_snapshot(case_number: str, act_type: str, participants: list[dict], act_data: dict) -> list[str]:
    lines = [
        f"Caso: {case_number}",
        f"Acto: {act_type}",
        "Intervinientes:",
    ]
    for item in participants:
        lines.append(f"- {item.get('role_label')}: {item.get('full_name')} ({item.get('document_type')} {item.get('document_number')})")
    lines.append("Datos del acto:")
    for key, value in act_data.items():
        lines.append(f"- {key}: {value}")
    return lines


def serialize_placeholder_snapshot(replacements: dict[str, str]) -> str:
    return json.dumps(replacements, ensure_ascii=False, indent=2)
```

## File: app/services/gari_document_service.py
```python
from __future__ import annotations

import json

import io
import os
from pathlib import Path

from docx import Document as DocxDocument
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt
from openai import OpenAI
from supabase import Client, create_client

from app.core.config import get_settings


SYSTEM_PROMPT_GARI = """Eres Gari, motor de redacción notarial colombiano de EasyPro.

IDENTIDAD Y ROL:
- Redactas instrumentos públicos notariales en Colombia con precisión jurídica total.
- Sigues el Decreto 960 de 1970, Decreto 2148 de 1983 y demás normas notariales colombianas.
- Solo produces el texto del documento. Nunca incluyes explicaciones, comentarios ni metadata.

REGLAS DE FORMATO NOTARIAL OBLIGATORIAS:
- NO uses guiones de relleno (- - - - -) en el cuerpo del documento
- El sistema los agregará automáticamente al formatear
- Solo usa saltos de línea entre secciones
- Separa cada acto con una línea en blanco
- Números siempre en texto seguido del numeral: "diecinueve (19)", "dos mil veintiséis (2026)"
- Valores monetarios: "$6.000.000" Y "seis millones de pesos colombianos ($6.000.000)"
- Negrilla para títulos de actos: **PRIMER ACTO: LIBERACIÓN PARCIAL DE HIPOTECA**
- Cada acto inicia en nueva sección con su número ordinal en negrilla
- Los intervinientes se presentan con su calidad completa: "quien obra en calidad de apoderado especial de [ENTIDAD] identificada con NIT [NIT]"

ESTRUCTURA OBLIGATORIA DEL DOCUMENTO:
1. Encabezado: NOTARÍA + NÚMERO ESCRITURA + CLASE Y CUANTÍA DE ACTOS + PERSONAS QUE INTERVIENEN
2. Apertura: ciudad, fecha en texto, notario titular
3. Un bloque por cada acto en el orden exacto indicado en el prompt
4. Cada acto: comparecencia del interviniente  declaraciones  aceptación
5. Liquidación de derechos notariales
6. Constancias legales (Ley 1581/2012, Art. 102 Decreto 960/1970)
7. Firmas de todos los comparecientes + Notario

REGLAS DE INTERVINIENTES:
- Cada apoderado SIEMPRE menciona: "quien obra como apoderado especial de [ENTIDAD, NIT]"
- La personería se acredita con: "escritura pública número X de la Notaría Y de [ciudad], la cual se protocoliza"
- El género gramatical SIEMPRE debe concordar con el sexo del interviniente
- Si el interviniente está de tránsito: "domiciliado en [municipio], de tránsito por Caldas"

MODO CORRECCIÓN:
- Cuando recibes un borrador anterior + instrucción de corrección
- Aplica SOLO el cambio solicitado
- Reproduce el resto del documento sin alteraciones
- No resumas ni acortes el documento

PROHIBICIONES ABSOLUTAS:
- Nunca inventes datos que no estén en el prompt
- Nunca uses placeholders como [DATO] o {{VARIABLE}}
- Nunca agregues comentarios fuera del texto notarial
- Nunca omitas actos que estén en la lista de actos requeridos

PRIORIDAD ABSOLUTA:
Debes generar TODOS los actos indicados en la instrucción de generación.
Es más importante generar todos los actos que usar muchos guiones de relleno.
Si debes elegir entre guiones decorativos y contenido de actos, siempre elige el contenido.
"""


def get_supabase_client() -> Client:
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not url or not key:
        raise ValueError("SUPABASE_URL y SUPABASE_SERVICE_KEY requeridos")
    return create_client(url, key)


def get_openai_client() -> OpenAI:
    settings = get_settings()
    api_key = getattr(settings, "openai_api_key", "") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY no configurada")
    return OpenAI(api_key=api_key)


def build_gari_prompt(
    act_type: str,
    notary_label: str,
    notary_name: str,
    participants: list[dict],
    case_acts: list[dict] | None = None,
    act_data: dict | None = None,
    template_reference_text: str | None = None,
    variante_id: str | None = None,
    correction_note: str | None = None,
    previous_draft: str | None = None,
) -> str:
    """Construye el prompt para Gari con actos dinamicos por caso."""
    act_data = act_data or {}

    def _matches_participant_role(role: str, role_code: str) -> bool:
        if role == "compradores" and role_code.startswith("comprador"):
            return True
        if role == "fideicomiso" and role_code == "apoderado_fideicomiso":
            return True
        if role == "banco_libera" and role_code == "apoderado_banco_libera":
            return True
        if role == "constructora" and role_code == "apoderado_fideicomitente":
            return True
        if role == "banco_hipoteca" and role_code == "apoderado_banco_hipoteca":
            return True
        return role_code == role

    actos_section = ""
    for act in sorted(case_acts or [], key=lambda item: int(item.get("act_order", 0) or 0)):
        act_code = str(act.get("act_code", "") or "")
        act_label = str(act.get("act_label", "") or "")
        act_order = int(act.get("act_order", 0) or 0)
        roles_raw = act.get("roles_json", "[]")
        try:
            roles = json.loads(roles_raw) if isinstance(roles_raw, str) else list(roles_raw or [])
        except json.JSONDecodeError:
            roles = []

        relevant_participants: list[dict] = []
        for role in roles:
            for participant in participants:
                role_code = str(participant.get("role_code", "") or "")
                if _matches_participant_role(str(role), role_code):
                    relevant_participants.append(participant)

        actos_section += f"\nACTO {act_order}  {act_label.upper()}\n"
        if act_code:
            actos_section += f"  CODIGO: {act_code}\n"
        for participant in relevant_participants:
            nombre = participant.get("full_name", "") or ""
            doc = f"{participant.get('document_type', '')} {participant.get('document_number', '')}".strip()
            entidad = participant.get("represented_entity_name", "") or ""
            nit = participant.get("represented_entity_nit", "") or ""
            rol = participant.get("role_label", "") or participant.get("role_code", "") or ""
            if entidad:
                actos_section += f"  {rol}: {nombre} {doc}  obrando como apoderado de {entidad} NIT {nit}\n"
            else:
                actos_section += f"  {rol}: {nombre} {doc}\n"

    act_data_text = ""
    for key, value in act_data.items():
        act_data_text += f"\n- {key}: {value}"

    reference_section = ""
    if template_reference_text:
        _ref_text = template_reference_text[:14000]
        _truncated = len(template_reference_text) > 14000
        reference_section = f"""
PLANTILLA DE REFERENCIA DEL ACTO:
{"[NOTA: texto de referencia truncado por longitud - mantener estructura y estilo del fragmento mostrado]" if _truncated else ""}
---
{_ref_text}
---
"""

    correction_section = ""
    if correction_note and previous_draft:
        correction_section = f"""
MODO CORRECCION ACTIVO:
El siguiente es el borrador actual que debes corregir:
---BORRADOR ACTUAL---
{previous_draft[:8000]}
---FIN BORRADOR---

Instruccion de correccion: {correction_note}

INSTRUCCION CRITICA: Aplica UNICAMENTE el cambio solicitado en la instruccion anterior.
No reescribas parrafos que no fueron mencionados. No cambies datos que no se pidan.
Devuelve el documento completo con solo esa correccion aplicada.
"""
    elif correction_note:
        correction_section = f"""
INSTRUCCION DE CORRECCION: {correction_note}
Aplica unicamente este cambio. No modifiques nada mas del documento.
"""

    prompt = f"""Eres un experto en derecho notarial colombiano. Tu tarea es redactar un instrumento publico notarial completo y correcto juridicamente.

1. NOTARIA Y NOTARIO TITULAR
NOTARIA: {notary_label}
NOTARIO TITULAR: {notary_name}
TIPO DE ACTO: {act_type}

2. ACTOS ESTRUCTURADOS
{actos_section}

3. DATOS DEL ACTO
{act_data_text}

4. INSTRUCCION DE FORMATO NOTARIAL
Redacta la escritura publica completa en español formal notarial colombiano con EXACTAMENTE este formato:

SECCION 1  ENCABEZADO:
- - - NOTARIA UNICA DEL CIRCULO DE CALDAS - - -
INSTRUMENTO PUBLICO NUMERO: numero_escritura
CLASES DE ACTOS:
1) NOMBRE ACTO: inmueble y matricula si aplica
   PERSONAS QUE INTERVIENEN: lista
   VALOR DEL ACTO: valor o SIN CUANTIA
repetir por cada acto

SECCION 2  CUERPO:
En el municipio de Caldas, Departamento de Antioquia, Republica de Colombia,
a los dia del mes de mes del año año, ante el despacho de la NOTARIA UNICA
DEL CIRCULO DE CALDAS, cuyo Notario Titular es el doctor nombre_notario,
se otorgo escritura publica en los siguientes terminos:
- - - - - - - - - - - - - - - - - - - - - - -
PRIMER ACTO: NOMBRE
Comparecencia completa del apoderado con todos sus datos
PRIMERO: clausula
SEGUNDO: clausula
repetir por cada acto

SECCION 3  CIERRE:
Otorgamiento y Autorizacion
Tratamiento de Datos Personales (Ley 1581/2012)
Derechos notariales: valor
IVA: valor
Superintendencia de notariado: valor
Hojas de protocolo: numeros
Firmas de todos los comparecientes con nombre, CC, celular, direccion, email

Usa guiones de separacion exactamente como: - - - - - - - - - - - - - - - - -
Nunca uses placeholders ni corchetes en el documento final.
Nunca omitas actos de la lista.

{reference_section}

{correction_section}
"""

    return prompt


def generate_notarial_document(
    act_type: str,
    notary_label: str,
    notary_name: str,
    participants: list[dict],
    case_acts: list[dict] | None = None,
    act_data: dict | None = None,
    template_reference_text: str | None = None,
    max_tokens: int = 4000,
    variante_id: str | None = None,
    correction_note: str | None = None,
    previous_draft: str | None = None,
) -> str:
    """Genera el documento notarial completo usando GPT-4o."""
    client = get_openai_client()
    prompt = build_gari_prompt(
        act_type=act_type,
        notary_label=notary_label,
        notary_name=notary_name,
        participants=participants,
        case_acts=case_acts,
        act_data=act_data or {},
        template_reference_text=template_reference_text,
        variante_id=variante_id,
        correction_note=correction_note,
        previous_draft=previous_draft,
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT_GARI,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.2,
        max_tokens=max(max_tokens, 16000),
    )

    return response.choices[0].message.content or ""


def build_gari_docx_buffer(text: str) -> io.BytesIO:
    """Construye un documento .docx en memoria con formato notarial colombiano correcto."""
    import re
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    doc = DocxDocument()

    # ── Página carta colombiana ──────────────────────────────────────────────
    section = doc.sections[0]
    section.page_width    = Cm(21.6)
    section.page_height   = Cm(27.9)
    section.left_margin   = Cm(3.2)
    section.right_margin  = Cm(2.2)
    section.top_margin    = Cm(3.5)
    section.bottom_margin = Cm(1.0)

    # ── Header: número de página centrado ───────────────────────────────────
    header = section.header
    p_hdr = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
    p_hdr.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_hdr = p_hdr.add_run()
    fldChar1 = OxmlElement("w:fldChar")
    fldChar1.set(qn("w:fldCharType"), "begin")
    instrText = OxmlElement("w:instrText")
    instrText.text = "PAGE"
    fldChar2 = OxmlElement("w:fldChar")
    fldChar2.set(qn("w:fldCharType"), "end")
    run_hdr._r.append(fldChar1)
    run_hdr._r.append(instrText)
    run_hdr._r.append(fldChar2)

    # ── Constantes ───────────────────────────────────────────────────────────
    LONGITUD_OBJETIVO = 95

    # Detecta títulos de acto: PRIMER ACTO:, SEGUNDO ACTO:, etc.
    # NO captura "VALOR DEL ACTO:" ni "TIPO DE ACTO:"
    _RE_TITULO_ACTO = re.compile(
        r"^(PRIMER|SEGUNDO|TERCER|CUARTO|QUINTO|SEXTO|S[ÉE]PTIMO|OCTAVO|NOVENO|D[ÉE]CIMO"
        r"|UNDÉCIMO|UNDECIMO|DUODÉCIMO|DUODECIMO)\s+ACTO\s*:",
        re.IGNORECASE,
    )

    # ── Helpers ──────────────────────────────────────────────────────────────
    def _set_spacing(p):
        p.paragraph_format.space_before = 0
        p.paragraph_format.space_after  = 0

    def _add_para(texto_final: str, bold: bool, alignment) -> None:
        p = doc.add_paragraph()
        p.alignment = alignment
        _set_spacing(p)
        run = p.add_run(texto_final)
        run.bold = bold

    def _rellenar_guiones(linea: str) -> str:
        """Añade '- ' al final de la línea hasta LONGITUD_OBJETIVO caracteres."""
        if len(linea) >= LONGITUD_OBJETIVO:
            return linea
        relleno = ""
        while len(linea) + 1 + len(relleno) + 2 <= LONGITUD_OBJETIVO:
            relleno += "- "
        return (linea + " " + relleno).rstrip()

    def _titulo_con_guiones(linea: str) -> str:
        """Coloca el título entre guiones: '- - - - PRIMER ACTO: X - - - -'"""
        lado = "- - - - - - - - - "
        return lado + linea + " " + lado.rstrip()

    # ── Procesamiento línea a línea ──────────────────────────────────────────
    for line in text.split("\n"):

        # PASO 1 — limpiar markdown bold (**)
        linea = line.strip().lstrip("*").rstrip("*").strip()

        # PASO 2 — filtrar separadores puros (solo guiones y espacios, sin letras)
        if linea and re.match(r"^[-\s]+$", linea) and len(linea) > 3:
            continue  # descartar completamente — no crear párrafo

        # PASO 3 — línea vacía → párrafo vacío de separación
        if not linea:
            p = doc.add_paragraph()
            _set_spacing(p)
            continue

        # PASO 4 — clasificar tipo de línea

        # A) TÍTULO DE ACTO — ordinal + "ACTO:" al inicio
        if _RE_TITULO_ACTO.match(linea):
            texto_final = _titulo_con_guiones(linea)
            _add_para(texto_final, bold=True, alignment=WD_ALIGN_PARAGRAPH.CENTER)
            continue

        # B) LÍNEA DE FIRMA — guiones bajos (___…)
        if linea.startswith("_"):
            _add_para(linea, bold=False, alignment=WD_ALIGN_PARAGRAPH.LEFT)
            continue

        # C) PIE DE NOTARIO — línea de roles al cierre
        if linea.lower().startswith("recepción") or linea.lower().startswith("recepcion"):
            _add_para(linea, bold=True, alignment=WD_ALIGN_PARAGRAPH.CENTER)
            continue

        # D) CONTENIDO NORMAL — todo lo demás
        if len(linea) < LONGITUD_OBJETIVO:
            texto_final = _rellenar_guiones(linea)
        else:
            texto_final = linea
        _add_para(texto_final, bold=True, alignment=WD_ALIGN_PARAGRAPH.JUSTIFY)

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer


def save_gari_document_as_docx(text: str, output_path: str | Path) -> str:
    """Genera el .docx en memoria y lo sube a Supabase Storage. Retorna signed URL."""
    buffer = build_gari_docx_buffer(text)
    file_bytes = buffer.getvalue()

    supabase = get_supabase_client()
    storage_path = str(output_path).replace("\\", "/")
    supabase.storage.from_("documentos").upload(
        path=storage_path,
        file=file_bytes,
        file_options={
            "content-type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "upsert": "true",
        },
    )

    signed = supabase.storage.from_("documentos").create_signed_url(storage_path, 3600)
    url = signed.get("signedUrl") or signed.get("signedURL") or ""
    if not url:
        raise ValueError(f"Supabase no retornó signed URL para {storage_path}. Respuesta: {signed}")
    return url


def resolver_escritura(
    proyecto: str,
    tipo_inmueble: str,
    num_compradores: int,
    banco_hipotecante: str | None,
    campos_caso: dict,
) -> dict:
    """Resuelve la variante de escritura y valida campos requeridos para el caso."""

    def _esta_vacio(valor: object) -> bool:
        if valor is None:
            return True
        if isinstance(valor, str):
            return valor.strip() == ""
        if isinstance(valor, (list, dict, tuple, set)):
            return len(valor) == 0
        return False

    actos_aragua_apto = [
        "liberacion_hipoteca",
        "cto",
        "compraventa_vis",
        "renuncia_resolutoria",
        "cancelacion_comodato",
        "patrimonio_familia",
        "poder_especial",
    ]
    campos_aragua_apto = [
        "numero_apartamento",
        "matricula_inmobiliaria",
        "cedula_catastral",
        "linderos",
        "numero_piso",
        "area_privada",
        "area_total",
        "altura",
        "coeficiente_copropiedad",
        "avaluo_catastral",
        "valor_venta",
        "fecha_promesa_compraventa",
        "paz_salvo_predial_numero",
        "paz_salvo_predial_fecha",
        "paz_salvo_predial_vigencia",
    ]

    actos_aragua_parq = [
        "liberacion_hipoteca",
        "cto",
        "compraventa_vis",
        "renuncia_resolutoria",
        "cancelacion_comodato",
        "poder_especial",
    ]
    campos_aragua_parq = [
        "numero_parqueadero",
        "matricula_inmobiliaria",
        "cedula_catastral",
        "linderos",
        "area_privada",
        "altura",
        "coeficiente_copropiedad",
        "avaluo_catastral",
        "valor_venta",
        "fecha_promesa_compraventa",
        "paz_salvo_predial_numero",
        "paz_salvo_predial_fecha",
        "paz_salvo_predial_vigencia",
    ]

    actos_jaggua_fna = [
        "liberacion_hipoteca",
        "cto",
        "compraventa_vis",
        "renuncia_resolutoria",
        "cancelacion_comodato",
        "hipoteca_primer_grado",
        "patrimonio_familia",
        "poder_especial",
    ]
    campos_jaggua_fna = [
        "numero_apartamento",
        "matricula_inmobiliaria",
        "linderos",
        "numero_piso",
        "area_privada",
        "area_total",
        "altura",
        "coeficiente_copropiedad",
        "valor_venta",
        "cuota_inicial",
        "valor_hipoteca",
        "origen_cuota_inicial",
        "fecha_promesa_compraventa",
        "inmueble_sera_casa_habitacion",
        "tiene_bien_afectado",
    ]

    actos_jaggua_bogota = [
        "liberacion_hipoteca",
        "cto",
        "compraventa_vis",
        "renuncia_resolutoria",
        "hipoteca_primer_grado",
        "patrimonio_familia",
        "poder_especial",
    ]
    campos_jaggua_bogota = [
        "numero_apartamento",
        "matricula_inmobiliaria",
        "linderos",
        "numero_piso",
        "area_privada",
        "area_total",
        "altura",
        "valor_venta",
        "cuota_inicial",
        "valor_hipoteca",
        "origen_cuota_inicial",
        "fecha_promesa_compraventa",
        "inmueble_sera_casa_habitacion",
        "tiene_bien_afectado",
    ]

    variantes = {
        ("aragua", "apartamento", 1, None): {
            "variante_id": "aragua_apto_1c",
            "plantilla_id": "aragua_apto_1c",
            "actos_requeridos": actos_aragua_apto,
            "campos_requeridos": campos_aragua_apto,
            "banco_nit": "890.903.938-8",
            "max_tokens_estimado": 5500,
        },
        ("aragua", "apartamento", 2, None): {
            "variante_id": "aragua_apto_2c",
            "plantilla_id": "aragua_apto_2c",
            "actos_requeridos": actos_aragua_apto,
            "campos_requeridos": campos_aragua_apto,
            "banco_nit": "890.903.938-8",
            "max_tokens_estimado": 5800,
        },
        ("aragua", "parqueadero", 2, None): {
            "variante_id": "aragua_parq_2c",
            "plantilla_id": "aragua_parq_2c",
            "actos_requeridos": actos_aragua_parq,
            "campos_requeridos": campos_aragua_parq,
            "banco_nit": "890.903.938-8",
            "max_tokens_estimado": 5200,
        },
        ("aragua", "parqueadero", 3, None): {
            "variante_id": "aragua_parq_3c",
            "plantilla_id": "aragua_parq_3c",
            "actos_requeridos": actos_aragua_parq,
            "campos_requeridos": campos_aragua_parq,
            "banco_nit": "890.903.938-8",
            "max_tokens_estimado": 5400,
        },
        ("jaggua", "apartamento", 1, "fna"): {
            "variante_id": "jaggua_fna_1c",
            "plantilla_id": "jaggua_fna_1c",
            "actos_requeridos": actos_jaggua_fna,
            "campos_requeridos": campos_jaggua_fna,
            "banco_nit": "899.999.284-4",
            "max_tokens_estimado": 6500,
        },
        ("jaggua", "apartamento", 2, "fna"): {
            "variante_id": "jaggua_fna_2c",
            "plantilla_id": "jaggua_fna_2c",
            "actos_requeridos": actos_jaggua_fna,
            "campos_requeridos": campos_jaggua_fna,
            "banco_nit": "899.999.284-4",
            "max_tokens_estimado": 6800,
        },
        ("jaggua", "apartamento", 1, "bogota"): {
            "variante_id": "jaggua_bogota_1c",
            "plantilla_id": "jaggua_bogota_1c",
            "actos_requeridos": actos_jaggua_bogota,
            "campos_requeridos": campos_jaggua_bogota,
            "banco_nit": "860.002.964-4",
            "max_tokens_estimado": 6800,
        },
        ("jaggua", "apartamento", 2, "bogota"): {
            "variante_id": "jaggua_bogota_2c",
            "plantilla_id": "jaggua_bogota_2c",
            "actos_requeridos": actos_jaggua_bogota,
            "campos_requeridos": campos_jaggua_bogota,
            "banco_nit": "860.002.964-4",
            "max_tokens_estimado": 7200,
        },
    }

    proyecto_norm = (proyecto or "").strip().lower()
    tipo_inmueble_norm = (tipo_inmueble or "").strip().lower()
    banco_norm = (banco_hipotecante or "").strip().lower() or None

    key = (proyecto_norm, tipo_inmueble_norm, num_compradores, banco_norm)
    if key not in variantes:
        raise ValueError(
            "No existe una variante de escritura para la combinación "
            f"proyecto={proyecto_norm}, tipo_inmueble={tipo_inmueble_norm}, "
            f"num_compradores={num_compradores}, banco_hipotecante={banco_norm}."
        )

    variante = variantes[key]
    campos_requeridos = variante["campos_requeridos"]
    campos_faltantes = [
        campo for campo in campos_requeridos if _esta_vacio(campos_caso.get(campo))
    ]

    return {
        "variante_id": variante["variante_id"],
        "plantilla_id": variante["plantilla_id"],
        "actos_requeridos": list(variante["actos_requeridos"]),
        "campos_requeridos": list(campos_requeridos),
        "campos_faltantes": campos_faltantes,
        "banco_nit": variante["banco_nit"],
        "max_tokens_estimado": variante["max_tokens_estimado"],
    }


def resolver_escritura_desde_template(template) -> dict:
    """
    Reemplaza resolver_escritura(). Recibe el objeto DocumentTemplate de BD.
    Retorna variante_id, campos_requeridos y max_tokens sin hardcodear nada.
    """
    campos_requeridos = [
        f.field_code for f in (template.fields or []) if f.is_required
    ]
    max_tokens = 16000
    return {
        "variante_id": template.slug,
        "plantilla_id": template.slug,
        "campos_requeridos": campos_requeridos,
        "campos_faltantes": [],
        "max_tokens_estimado": max_tokens,
    }


if __name__ == "__main__":
    ejemplo_aragua = resolver_escritura(
        proyecto="aragua",
        tipo_inmueble="apartamento",
        num_compradores=1,
        banco_hipotecante=None,
        campos_caso={
            "numero_apartamento": "1201",
            "matricula_inmobiliaria": "50N-123456",
            "cedula_catastral": "AA-001",
            "linderos": "Norte con...",
            "numero_piso": "12",
            "area_privada": "80",
            "area_total": "90",
            "altura": "2.40",
            "coeficiente_copropiedad": "1.25%",
            "avaluo_catastral": "180000000",
            "valor_venta": "250000000",
            "fecha_promesa_compraventa": "2026-04-01",
            "paz_salvo_predial_numero": "PSP-55",
            "paz_salvo_predial_fecha": "2026-03-20",
            "paz_salvo_predial_vigencia": "2026",
        },
    )
    print("Ejemplo aragua apartamento 1c:")
    print(ejemplo_aragua)

    ejemplo_jaggua = resolver_escritura(
        proyecto="jaggua",
        tipo_inmueble="apartamento",
        num_compradores=2,
        banco_hipotecante="bogota",
        campos_caso={
            "numero_apartamento": "905",
            "matricula_inmobiliaria": "50C-765432",
            "linderos": "Sur con...",
            "numero_piso": "9",
            "area_privada": "70",
            "area_total": "78",
            "altura": "2.35",
            "valor_venta": "320000000",
            "cuota_inicial": "80000000",
            "valor_hipoteca": "240000000",
            "origen_cuota_inicial": "Ahorros",
            "fecha_promesa_compraventa": "2026-04-10",
            "inmueble_sera_casa_habitacion": True,
            "tiene_bien_afectado": False,
        },
    )
    print("Ejemplo jaggua bogota 2c:")
    print(ejemplo_jaggua)
```

## File: app/services/notary_imports.py
```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

DEFAULT_ANTIOQUIA_SOURCE_PATH = Path(r"C:\EasyProNotarial-2\Archivos_referencia\Notarias_Antioquia_EasyProNotarial.xlsx")
REQUIRED_COLUMNS = [
    "MUNICIPIO",
    "NOTARÍA",
    "DIRECCIÓN",
    "TELÉFONO",
    "CORREO ELECTRÓNICO",
    "NOTARIO/A",
    "HORARIO",
]

MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"


@dataclass
class WorkbookSheetData:
    sheet_name: str
    rows: list[dict[str, str]]


class NotaryImportFileError(ValueError):
    pass


def validate_source_file(source_path: str | Path) -> Path:
    path = Path(source_path)
    if not path.exists():
        raise NotaryImportFileError(f"Archivo no encontrado: {path}")
    if path.suffix.lower() != ".xlsx":
        raise NotaryImportFileError("El archivo de importación debe ser .xlsx")
    return path


def _read_shared_strings(workbook: ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in workbook.namelist():
        return []
    root = ET.fromstring(workbook.read("xl/sharedStrings.xml"))
    strings: list[str] = []
    for item in root.findall(f"{{{MAIN_NS}}}si"):
        fragments = [node.text or "" for node in item.iter(f"{{{MAIN_NS}}}t")]
        strings.append("".join(fragments))
    return strings


def _resolve_first_sheet(workbook: ZipFile) -> tuple[str, str]:
    wb = ET.fromstring(workbook.read("xl/workbook.xml"))
    sheets = wb.find(f"{{{MAIN_NS}}}sheets")
    if sheets is None or not list(sheets):
        raise NotaryImportFileError("El workbook no contiene hojas disponibles.")
    first_sheet = list(sheets)[0]
    sheet_name = first_sheet.attrib.get("name", "Sheet1")
    rel_id = first_sheet.attrib.get(f"{{{REL_NS}}}id")
    if not rel_id:
        raise NotaryImportFileError("No fue posible resolver la relación de la hoja principal.")

    rels = ET.fromstring(workbook.read("xl/_rels/workbook.xml.rels"))
    for relation in rels.findall(f"{{{PKG_REL_NS}}}Relationship"):
        if relation.attrib.get("Id") == rel_id:
            return sheet_name, f"xl/{relation.attrib['Target']}"
    raise NotaryImportFileError("No fue posible localizar la hoja principal dentro del archivo.")


def _read_cell_value(cell: ET.Element, shared_strings: list[str]) -> str:
    cell_type = cell.attrib.get("t")
    if cell_type == "inlineStr":
        fragments = [node.text or "" for node in cell.iter(f"{{{MAIN_NS}}}t")]
        return "".join(fragments)

    value_node = cell.find(f"{{{MAIN_NS}}}v")
    if value_node is None:
        return ""
    raw_value = value_node.text or ""
    if cell_type == "s":
        return shared_strings[int(raw_value)]
    return raw_value


def load_xlsx_rows(source_path: str | Path) -> WorkbookSheetData:
    path = validate_source_file(source_path)
    with ZipFile(path) as workbook:
        shared_strings = _read_shared_strings(workbook)
        sheet_name, sheet_target = _resolve_first_sheet(workbook)
        sheet = ET.fromstring(workbook.read(sheet_target))

    sheet_data = sheet.find(f"{{{MAIN_NS}}}sheetData")
    if sheet_data is None:
        raise NotaryImportFileError("La hoja principal no contiene datos.")

    parsed_rows: list[dict[str, str]] = []
    headers: dict[str, str] | None = None

    for row in list(sheet_data):
        row_values: dict[str, str] = {}
        for cell in list(row):
            ref = cell.attrib.get("r", "")
            column = "".join(character for character in ref if character.isalpha())
            row_values[column] = _read_cell_value(cell, shared_strings).strip()

        if not row_values:
            continue

        if headers is None:
            headers = row_values
            continue

        mapped_row = {
            header_name: row_values.get(column_name, "")
            for column_name, header_name in headers.items()
            if header_name
        }
        if any(value for value in mapped_row.values()):
            parsed_rows.append(mapped_row)

    if headers is None:
        raise NotaryImportFileError("No se encontró la fila de encabezados.")

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in headers.values()]
    if missing_columns:
        raise NotaryImportFileError(f"Faltan columnas requeridas: {', '.join(missing_columns)}")

    return WorkbookSheetData(sheet_name=sheet_name, rows=parsed_rows)
```

## File: app/services/storage.py
```python
from __future__ import annotations

import base64
import mimetypes
import shutil
from pathlib import Path

from app.core.config import BASE_DIR

STORAGE_ROOT = BASE_DIR / "storage"
TEMPLATE_STORAGE = STORAGE_ROOT / "templates"
CASE_STORAGE = STORAGE_ROOT / "cases"


def ensure_storage_dirs() -> None:
    for directory in (STORAGE_ROOT, TEMPLATE_STORAGE, CASE_STORAGE):
        directory.mkdir(parents=True, exist_ok=True)


def template_file_path(filename: str) -> Path:
    ensure_storage_dirs()
    return TEMPLATE_STORAGE / sanitize_filename(filename)


def sanitize_filename(filename: str) -> str:
    keep = [char if char.isalnum() or char in {"-", "_", "."} else "_" for char in filename.strip()]
    sanitized = "".join(keep).strip("._") or "archivo"
    return sanitized


def copy_template_file(source_path: str | Path, slug: str) -> tuple[str, str]:
    ensure_storage_dirs()
    source = Path(source_path)
    extension = source.suffix.lower() or ".docx"
    filename = sanitize_filename(f"{slug}{extension}")
    destination = TEMPLATE_STORAGE / filename
    shutil.copy2(source, destination)
    return filename, str(destination)


def save_base64_file(content_base64: str, destination: str | Path) -> Path:
    ensure_storage_dirs()
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    data = base64.b64decode(content_base64)
    target.write_bytes(data)
    return target


def save_template_upload(filename: str, content_base64: str, slug: str) -> tuple[str, str]:
    ensure_storage_dirs()
    safe_name = sanitize_filename(filename)
    extension = Path(safe_name).suffix.lower() or ".docx"
    final_name = sanitize_filename(f"{slug}{extension}")
    destination = TEMPLATE_STORAGE / final_name
    save_base64_file(content_base64, destination)
    return final_name, str(destination)


def next_case_file_path(case_id: int, category: str, version_number: int, file_format: str, filename: str | None = None) -> Path:
    ensure_storage_dirs()
    extension = f".{file_format.lower().lstrip('.')}"
    safe_name = sanitize_filename(filename or f"{category}_v{version_number}{extension}")
    if not safe_name.lower().endswith(extension):
        safe_name = f"{safe_name}{extension}"
    directory = CASE_STORAGE / f"case-{case_id}" / category
    directory.mkdir(parents=True, exist_ok=True)
    return directory / safe_name


def guess_media_type(path: str | Path) -> str:
    media_type, _ = mimetypes.guess_type(str(path))
    return media_type or "application/octet-stream"
```

## File: railway.toml
```toml

```

## File: requirements.txt
```
fastapi==0.115.12
uvicorn[standard]==0.34.0
sqlalchemy==2.0.40
psycopg2-binary==2.9.10
pydantic-settings==2.8.1
python-jose[cryptography]==3.4.0
passlib[bcrypt]==1.7.4
email-validator==2.2.0
openai>=1.0.0
python-docx>=0.8.11
supabase==2.28.3
python-dotenv
```

## File: scripts/migrate_to_postgres.py
```python
import sqlite3
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")

from app.db.session import SessionLocal
from sqlalchemy import text

BOOLEAN_PREFIXES = ("is_", "has_", "requires_", "allow_", "final_", "show_")

TABLES_IN_ORDER = [
    "roles", "notaries", "users", "role_assignments",
    "notary_commercial_activities", "notary_crm_audit_logs",
    "case_state_definitions", "numbering_sequences",
    "document_templates", "template_fields", "template_required_roles",
    "persons", "cases", "case_act_data", "case_participants",
    "case_timeline_events", "case_workflow_events", "case_documents",
    "case_document_versions", "case_client_comments", "case_internal_notes",
]

def convert_booleans(row_dict):
    for key, val in row_dict.items():
        if isinstance(val, int) and any(key.startswith(p) for p in BOOLEAN_PREFIXES):
            row_dict[key] = bool(val)
    return row_dict

def migrate():
    sqlite_conn = sqlite3.connect("easypro2.db")
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()
    pg_session = SessionLocal()

    try:
        # Deshabilitar foreign key checks
        pg_session.execute(text("SET session_replication_role = replica"))
        pg_session.commit()
        print("Foreign keys deshabilitados.")

        for table in TABLES_IN_ORDER:
            print(f"Migrando {table}...")
            sqlite_cursor.execute(f"SELECT * FROM {table}")
            rows = sqlite_cursor.fetchall()
            if not rows:
                print(f"  -> Sin registros.")
                continue
            columns = [desc[0] for desc in sqlite_cursor.description]
            col_names = ", ".join(columns)
            placeholders = ", ".join([f":{c}" for c in columns])
            for row in rows:
                row_dict = convert_booleans(dict(row))
                pg_session.execute(
                    text(f"INSERT INTO {table} ({col_names}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"),
                    row_dict
                )
            pg_session.commit()
            print(f"  -> {len(rows)} registros migrados.")

        # Rehabilitar foreign keys
        pg_session.execute(text("SET session_replication_role = DEFAULT"))
        pg_session.commit()
        print("\nForeign keys rehabilitados.")
        print("Migracion completada exitosamente.")

    except Exception as e:
        pg_session.rollback()
        print(f"Error: {e}")
        raise
    finally:
        sqlite_conn.close()
        pg_session.close()

if __name__ == "__main__":
    migrate()
```

## File: scripts/seed_notarias_piloto.py
```python
from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

load_dotenv(ROOT / ".env")

from app.db.session import SessionLocal  # noqa: E402
from app.core.security import get_password_hash  # noqa: E402


PASSWORD_PLAIN = "Notaria2026*"
PASSWORD_HASH = get_password_hash(PASSWORD_PLAIN)


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", normalized.lower()).strip("-")
    return cleaned or "notary"


def build_catalog_identity_key(municipality: str, notary_label: str, email: str | None) -> str:
    normalized_email = email or "no-email"
    return "::".join([slugify(municipality), slugify(notary_label), slugify(normalized_email)])


def fetch_one_dict(conn, sql: str, params: dict[str, object]) -> dict[str, object] | None:
    return conn.execute(text(sql), params).mappings().first()


def sync_serial_sequence(conn, table_name: str) -> None:
    conn.execute(
        text(
            f"""
            SELECT setval(
                pg_get_serial_sequence('{table_name}', 'id'),
                COALESCE((SELECT MAX(id) FROM {table_name}), 0) + 1,
                false
            )
            """
        )
    )


def ensure_notary(conn, summary: dict[str, int | str]) -> int:
    row = fetch_one_dict(
        conn,
        """
        SELECT id, notary_label, municipality
        FROM notaries
        WHERE notary_label ILIKE :pattern OR municipality ILIKE :pattern
        ORDER BY id ASC
        LIMIT 1
        """,
        {"pattern": "%bello%"},
    )
    if row:
        summary["bello_notary"] = "existía"
        return int(row["id"])

    catalog_identity_key = build_catalog_identity_key("Bello", "Primera de Bello", None)
    result = conn.execute(
        text(
            """
            INSERT INTO notaries (
                slug,
                catalog_identity_key,
                commercial_name,
                legal_name,
                department,
                municipality,
                notary_label,
                primary_color,
                secondary_color,
                base_color,
                accent_color,
                city,
                institutional_data,
                commercial_status,
                priority,
                is_active
            )
            VALUES (
                :slug,
                :catalog_identity_key,
                :commercial_name,
                :legal_name,
                :department,
                :municipality,
                :notary_label,
                :primary_color,
                :secondary_color,
                :base_color,
                :accent_color,
                :city,
                :institutional_data,
                :commercial_status,
                :priority,
                :is_active
            )
            RETURNING id
            """
        ),
        {
            "slug": slugify("Primera de Bello"),
            "catalog_identity_key": catalog_identity_key,
            "commercial_name": "Notaría Primera del Círculo de Bello",
            "legal_name": "Notaría Primera del Círculo de Bello",
            "department": "Antioquia",
            "municipality": "Bello",
            "notary_label": "Primera de Bello",
            "primary_color": "#0D2E5D",
            "secondary_color": "#4D5B7C",
            "base_color": "#F4F7FB",
            "accent_color": "#50D690",
            "city": "Bello",
            "institutional_data": "",
            "commercial_status": "prospecto",
            "priority": "media",
            "is_active": True,
        },
    )
    new_id = int(result.scalar_one())
    summary["bello_notary"] = "creada"
    return new_id


def ensure_caldas_notary_id(conn, summary: dict[str, int | str]) -> int:
    row = fetch_one_dict(
        conn,
        """
        SELECT id, notary_label
        FROM notaries
        WHERE notary_label ILIKE :pattern
        ORDER BY id ASC
        LIMIT 1
        """,
        {"pattern": "%caldas%"},
    )
    if row:
        caldas_id = int(row["id"])
        summary["caldas_notary"] = f"existía (id={caldas_id})"
        return caldas_id

    fallback_row = fetch_one_dict(
        conn,
        """
        SELECT id, notary_label
        FROM notaries
        WHERE id = :id
        """,
        {"id": 21},
    )
    if fallback_row:
        summary["caldas_notary"] = "existía (id=21)"
        return 21

    raise RuntimeError("No se encontró la Notaría Única de Caldas por label ni por id=21.")


def ensure_role_ids(conn) -> dict[str, int]:
    code_map = {
        "titular_notary": "notary",
        "substitute_notary": "notary",
        "admin_notary": "admin_notary",
        "approver": "approver",
        "protocolist": "protocolist",
    }
    role_ids: dict[str, int] = {}
    for code in sorted(set(code_map.values())):
        row = fetch_one_dict(
            conn,
            "SELECT id, code FROM roles WHERE code = :code LIMIT 1",
            {"code": code},
        )
        if row:
            role_ids[str(row["code"])] = int(row["id"])
    missing = [code for code in sorted(set(code_map.values())) if code not in role_ids]
    if missing:
        raise RuntimeError(f"Faltan roles requeridos en la tabla roles: {', '.join(missing)}")
    for alias, canonical in code_map.items():
        role_ids[alias] = role_ids[canonical]
    return role_ids


def ensure_user(conn, email: str, full_name: str, default_notary_id: int, summary: dict[str, int | str]) -> tuple[int, bool]:
    row = fetch_one_dict(
        conn,
        "SELECT id, email, full_name, default_notary_id FROM users WHERE email = :email LIMIT 1",
        {"email": email},
    )
    if row:
        conn.execute(
            text(
                """
                UPDATE users
                SET full_name = :full_name,
                    default_notary_id = :default_notary_id
                WHERE id = :id
                """
            ),
            {"id": row["id"], "full_name": full_name, "default_notary_id": default_notary_id},
        )
        summary["users_existing"] = int(summary["users_existing"]) + 1
        return int(row["id"]), False

    result = conn.execute(
        text(
            """
            INSERT INTO users (
                email,
                full_name,
                password_hash,
                is_active,
                default_notary_id
            )
            VALUES (
                :email,
                :full_name,
                :password_hash,
                :is_active,
                :default_notary_id
            )
            RETURNING id
            """
        ),
        {
            "email": email,
            "full_name": full_name,
            "password_hash": PASSWORD_HASH,
            "is_active": True,
            "default_notary_id": default_notary_id,
        },
    )
    user_id = int(result.scalar_one())
    summary["users_created"] = int(summary["users_created"]) + 1
    return user_id, True


def ensure_assignment(conn, user_id: int, role_id: int, notary_id: int, summary: dict[str, int | str]) -> None:
    row = fetch_one_dict(
        conn,
        """
        SELECT id
        FROM role_assignments
        WHERE user_id = :user_id AND role_id = :role_id AND notary_id = :notary_id
        LIMIT 1
        """,
        {"user_id": user_id, "role_id": role_id, "notary_id": notary_id},
    )
    if row:
        summary["assignments_existing"] = int(summary["assignments_existing"]) + 1
        return

    conn.execute(
        text(
            """
            INSERT INTO role_assignments (user_id, role_id, notary_id)
            VALUES (:user_id, :role_id, :notary_id)
            """
        ),
        {"user_id": user_id, "role_id": role_id, "notary_id": notary_id},
    )
    summary["assignments_created"] = int(summary["assignments_created"]) + 1


def main() -> None:
    summary: dict[str, int | str] = {
        "bello_notary": "existía",
        "caldas_notary": "existía",
        "users_created": 0,
        "users_existing": 0,
        "assignments_created": 0,
        "assignments_existing": 0,
    }

    caldas_users = [
        ("jose.hernandez@notariacaldas.co", "José Manuel Hernández Franco", "titular_notary"),
        ("esteban.ocampo@notariacaldas.co", "Esteban Ocampo", "admin_notary"),
        ("tatiana.henao@notariacaldas.co", "Tatiana Henao", "approver"),
        ("paola.henao@notariacaldas.co", "Paola Henao", "protocolist"),
        ("santiago.caldas@notariacaldas.co", "Santiago", "protocolist"),
        ("yeison.caldas@notariacaldas.co", "Yeison", "protocolist"),
        ("bibiana.caldas@notariacaldas.co", "Bibiana", "protocolist"),
    ]
    bello_users = [
        ("juan.munoz@notariabello.co", "Juan Hernando Muñoz Muñoz", "titular_notary"),
        ("liliana.gutierrez@notariabello.co", "Liliana María Gutiérrez", "approver"),
        ("tatiana.henao@notariabello.co", "Tatiana Henao", "protocolist"),
        ("adriana.bermudez@notariabello.co", "Adriana Bermúdez", "protocolist"),
        ("ermick.jose@notariabello.co", "Ermick José", "protocolist"),
        ("emilsen.lujan@notariabello.co", "Emilsen Luján", "protocolist"),
        ("leidy.perez@notariabello.co", "Leidy Pérez", "protocolist"),
        ("juan.carlos@notariabello.co", "Juan Carlos", "protocolist"),
    ]

    with SessionLocal() as session:
        with session.begin():
            conn = session

            sync_serial_sequence(conn, "notaries")
            sync_serial_sequence(conn, "users")
            sync_serial_sequence(conn, "role_assignments")

            bello_id = ensure_notary(conn, summary)
            caldas_id = ensure_caldas_notary_id(conn, summary)
            role_ids = ensure_role_ids(conn)

            for email, _, _ in caldas_users + bello_users:
                conn.execute(
                    text(
                        """
                        UPDATE users
                        SET password_hash = :password_hash
                        WHERE email = :email
                        """
                    ),
                    {"email": email, "password_hash": PASSWORD_HASH},
                )

            for email, full_name, role_code in caldas_users:
                user_id, _ = ensure_user(conn, email, full_name, caldas_id, summary)
            for email, full_name, role_code in bello_users:
                user_id, _ = ensure_user(conn, email, full_name, bello_id, summary)

            email_to_user_id = {
                email: int(
                    conn.execute(
                        text("SELECT id FROM users WHERE email = :email"),
                        {"email": email},
                    ).scalar_one()
                )
                for email, _, _ in caldas_users + bello_users
            }

            for email, _, role_code in caldas_users:
                ensure_assignment(conn, email_to_user_id[email], role_ids[role_code], caldas_id, summary)
            for email, _, role_code in bello_users:
                ensure_assignment(conn, email_to_user_id[email], role_ids[role_code], bello_id, summary)

    print("Resumen seed notarias piloto")
    print(f"Notaría Bello: {summary['bello_notary']}")
    print(f"Notaría Caldas: {summary['caldas_notary']}")
    print(f"Usuarios creados: {summary['users_created']}")
    print(f"Usuarios ya existentes: {summary['users_existing']}")
    print(f"Roles creados: {summary['assignments_created']}")
    print(f"Roles ya existentes: {summary['assignments_existing']}")


if __name__ == "__main__":
    main()
```
