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
