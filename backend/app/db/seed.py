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
