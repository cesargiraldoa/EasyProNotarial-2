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
