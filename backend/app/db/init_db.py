from __future__ import annotations

from sqlalchemy import inspect, text

from app.db.base import Base
from app.db.seed import seed_database
from app.db.session import SessionLocal, engine
from app.models.case import Case
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
            "commercial_name", "legal_name", "city", "department", "municipality", "notary_label", "address", "phone", "email",
            "current_notary_name", "business_hours", "commercial_owner", "main_contact_name", "main_contact_title", "commercial_phone",
            "commercial_email", "commercial_notes", "lead_source", "potential", "internal_observations", "institutional_data",
        ],
        Case: ["case_type", "act_type", "metadata_json", "internal_case_number", "official_deed_number", "approved_by_role_code"],
        CaseStateDefinition: ["case_type", "code", "label"],
        DocumentTemplate: ["name", "slug", "case_type", "document_type", "description", "scope_type", "source_filename", "storage_path", "internal_variable_map_json"],
        TemplateRequiredRole: ["role_code", "label"],
        TemplateField: ["field_code", "label", "field_type", "section", "options_json", "placeholder_key", "help_text"],
        Person: ["document_type", "document_number", "full_name", "sex", "nationality", "marital_status", "profession", "municipality", "phone", "address", "email", "metadata_json"],
        CaseParticipant: ["role_code", "role_label", "snapshot_json"],
        CaseActData: ["data_json"],
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
        "address": 'ALTER TABLE notaries ADD COLUMN address VARCHAR(255)',
        "phone": 'ALTER TABLE notaries ADD COLUMN phone TEXT',
        "email": 'ALTER TABLE notaries ADD COLUMN email VARCHAR(120)',
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
        "last_management_at": "ALTER TABLE notaries ADD COLUMN last_management_at DATETIME",
        "next_management_at": "ALTER TABLE notaries ADD COLUMN next_management_at DATETIME",
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
        connection.execute(text("UPDATE notaries SET department = COALESCE(NULLIF(department, ''), 'Antioquia')"))
        connection.execute(text("UPDATE notaries SET municipality = COALESCE(NULLIF(municipality, ''), city)"))
        connection.execute(text("UPDATE notaries SET notary_label = COALESCE(NULLIF(notary_label, ''), commercial_name)"))
        connection.execute(text("UPDATE notaries SET commercial_status = COALESCE(NULLIF(commercial_status, ''), 'prospecto')"))
        connection.execute(text("UPDATE notaries SET base_color = COALESCE(NULLIF(base_color, ''), '#F4F7FB')"))
        connection.execute(text("UPDATE notaries SET priority = COALESCE(NULLIF(priority, ''), 'media')"))
        connection.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS uq_notaries_catalog_identity_key_idx ON notaries (catalog_identity_key)"))
        connection.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS uq_notaries_catalog_identity_idx ON notaries (municipality, notary_label, email)"))


def ensure_commercial_activity_columns() -> None:
    inspector = inspect(engine)
    if "notary_commercial_activities" not in inspector.get_table_names():
        return
    existing_columns = {column["name"] for column in inspector.get_columns("notary_commercial_activities")}
    with engine.begin() as connection:
        if "responsible_user_id" not in existing_columns:
            connection.execute(text("ALTER TABLE notary_commercial_activities ADD COLUMN responsible_user_id INTEGER"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS ix_notary_commercial_activities_responsible_user_id ON notary_commercial_activities (responsible_user_id)"))


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
        "approved_at": "ALTER TABLE cases ADD COLUMN approved_at DATETIME",
        "approved_by_user_id": "ALTER TABLE cases ADD COLUMN approved_by_user_id INTEGER",
        "approved_by_role_code": "ALTER TABLE cases ADD COLUMN approved_by_role_code VARCHAR(80)",
        "approved_document_version_id": "ALTER TABLE cases ADD COLUMN approved_document_version_id INTEGER",
    }
    with engine.begin() as connection:
        for column_name, ddl in required_columns.items():
            if column_name not in existing_columns:
                connection.execute(text(ddl))
        connection.execute(text("CREATE INDEX IF NOT EXISTS ix_cases_template_id ON cases (template_id)"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS ix_cases_created_by_user_id ON cases (created_by_user_id)"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS ix_cases_internal_case_number ON cases (internal_case_number)"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS ix_cases_official_deed_number ON cases (official_deed_number)"))


def ensure_case_indexes() -> None:
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    with engine.begin() as connection:
        if "cases" in tables:
            connection.execute(text("CREATE INDEX IF NOT EXISTS ix_cases_current_state ON cases (current_state)"))
            connection.execute(text("CREATE INDEX IF NOT EXISTS ix_cases_current_owner_user_id ON cases (current_owner_user_id)"))
            connection.execute(text("CREATE INDEX IF NOT EXISTS ix_cases_notary_id ON cases (notary_id)"))
            connection.execute(text("CREATE INDEX IF NOT EXISTS ix_cases_case_type ON cases (case_type)"))
        if "case_state_definitions" in tables:
            connection.execute(text("CREATE INDEX IF NOT EXISTS ix_case_state_definitions_case_type_step_order ON case_state_definitions (case_type, step_order)"))
        if "case_timeline_events" in tables:
            connection.execute(text("CREATE INDEX IF NOT EXISTS ix_case_timeline_events_case_id ON case_timeline_events (case_id)"))
            connection.execute(text("CREATE INDEX IF NOT EXISTS ix_case_timeline_events_actor_user_id ON case_timeline_events (actor_user_id)"))
        if "persons" in tables:
            connection.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_person_document_unique ON persons (document_type, document_number)"))
            connection.execute(text("CREATE INDEX IF NOT EXISTS ix_person_full_name ON persons (full_name)"))
        if "document_templates" in tables:
            connection.execute(text("CREATE INDEX IF NOT EXISTS ix_document_templates_active_scope ON document_templates (is_active, scope_type)"))
        if "template_required_roles" in tables:
            connection.execute(text("CREATE INDEX IF NOT EXISTS ix_template_required_roles_template_id ON template_required_roles (template_id)"))
        if "template_fields" in tables:
            connection.execute(text("CREATE INDEX IF NOT EXISTS ix_template_fields_template_id ON template_fields (template_id)"))
        if "case_participants" in tables:
            connection.execute(text("CREATE INDEX IF NOT EXISTS ix_case_participants_case_id ON case_participants (case_id)"))
            connection.execute(text("CREATE INDEX IF NOT EXISTS ix_case_participants_person_id ON case_participants (person_id)"))
        if "case_document_versions" in tables:
            connection.execute(text("CREATE INDEX IF NOT EXISTS ix_case_document_versions_document_id ON case_document_versions (case_document_id)"))
        if "case_workflow_events" in tables:
            connection.execute(text("CREATE INDEX IF NOT EXISTS ix_case_workflow_events_case_id ON case_workflow_events (case_id)"))
        if "numbering_sequences" in tables:
            connection.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_numbering_sequences_scope ON numbering_sequences (sequence_type, notary_id, year)"))


def init_db() -> None:
    ensure_storage_dirs()
    Base.metadata.create_all(bind=engine)
    ensure_notary_columns()
    ensure_commercial_activity_columns()
    ensure_case_columns()
    ensure_case_indexes()
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        seed_database(db)
        repair_model_strings(db)
    finally:
        db.close()
