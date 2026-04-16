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