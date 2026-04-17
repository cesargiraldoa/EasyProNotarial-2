from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user, get_role_codes, get_db, require_roles
from app.models.case import Case
from app.models.case_act_data import CaseActData
from app.models.case_client_comment import CaseClientComment
from app.models.case_document import CaseDocument
from app.models.case_document_version import CaseDocumentVersion
from app.models.case_internal_note import CaseInternalNote
from app.models.case_participant import CaseParticipant
from app.models.case_timeline_event import CaseTimelineEvent
from app.models.case_workflow_event import CaseWorkflowEvent
from app.models.document_template import DocumentTemplate
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
from app.schemas.person import PersonCreate
from app.schemas.template import TemplateFieldSummary, TemplateRequiredRoleSummary, TemplateSummary
from app.services.document_generation import build_case_text_snapshot, extract_text_from_docx, generate_plain_pdf, render_docx_template, serialize_placeholder_snapshot
from app.services.gari_document_service import generate_notarial_document, resolver_escritura, save_gari_document_as_docx
from app.services.storage import guess_media_type, next_case_file_path, save_base64_file

router = APIRouter(prefix="/document-flow", tags=["document-flow"])

NOTARY_APPROVER_ROLES = {"titular_notary", "substitute_notary"}


def safe_json(value: str | None) -> str:
    if value is None or not value.strip():
        return "{}"
    try:
        return json.dumps(json.loads(value), ensure_ascii=False)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El contenido debe ser JSON vlido.") from exc


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
        joinedload(Case.act_data),
        joinedload(Case.client_comments).joinedload(CaseClientComment.created_by_user),
        joinedload(Case.internal_notes).joinedload(CaseInternalNote.created_by_user),
        joinedload(Case.documents).joinedload(CaseDocument.versions).joinedload(CaseDocumentVersion.created_by_user),
    )


def load_case_or_404(db: Session, case_id: int) -> Case:
    case = detail_query(db).filter(Case.id == case_id).first()
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caso no encontrado.")
    return case


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
    return CaseDocumentSummary(
        id=document.id,
        category=document.category,
        title=document.title,
        current_version_number=document.current_version_number,
        versions=[serialize_document_version(case_id, document.id, version) for version in document.versions],
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
    replacements["{{NUMERO_ESCRITURA}}"] = case.official_deed_number or "PENDIENTE ASIGNACIN"
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La plantilla seleccionada no existe o est inactiva.")
    if db.query(Notary.id).filter(Notary.id == payload.notary_id).first() is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="La notara seleccionada no existe.")
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
    required_roles = {item.role_code for item in case.template.required_roles if item.is_required} if case.template else set()
    provided_roles = {item.role_code for item in payload}
    missing = sorted(required_roles - provided_roles)
    if missing:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Faltan intervinientes obligatorios: {', '.join(missing)}.")
    case.participants.clear()
    db.flush()
    person_ids: list[int] = []
    for item in payload:
        person = db.query(Person).filter(Person.id == item.person_id).first() if item.person_id else None
        if person is None and item.person is not None:
            person = resolve_or_create_person(db, item.person)
        if person is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Debes seleccionar o crear la persona para {item.role_label}.")
        person_ids.append(person.id)
        snapshot = {"document_type": person.document_type, "document_number": person.document_number, "full_name": person.full_name, "sex": person.sex, "nationality": person.nationality, "marital_status": person.marital_status, "profession": person.profession, "municipality": person.municipality, "is_transient": person.is_transient, "phone": person.phone, "address": person.address, "email": person.email}
        case.participants.append(CaseParticipant(case_id=case.id, person_id=person.id, role_code=item.role_code.strip(), role_label=item.role_label.strip(), snapshot_json=json.dumps(snapshot, ensure_ascii=False)))
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
        }
        for item in case.participants
    ]

    template_reference_text = None
    if case.template and case.template.storage_path:
        try:
            template_reference_text = extract_text_from_docx(case.template.storage_path)
        except Exception:
            template_reference_text = None

    # Construir campos_caso desde act_data
    campos_caso = {k: v for k, v in act_data.items() if v not in (None, "", [])}

    es_escritura_vis = act_data.get("proyecto") is not None

    if es_escritura_vis:
        try:
            resolucion = resolver_escritura(
                proyecto=act_data.get("proyecto", "aragua"),
                tipo_inmueble=act_data.get("tipo_inmueble", "apartamento"),
                num_compradores=act_data.get("num_compradores") or len(case.participants),
                banco_hipotecante=act_data.get("banco_hipotecante"),
                campos_caso=campos_caso,
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        if resolucion["campos_faltantes"]:
            raise HTTPException(
                status_code=422,
                detail=f"Faltan campos requeridos para generar la escritura: {', '.join(resolucion['campos_faltantes'])}"
            )
        max_tokens = resolucion["max_tokens_estimado"]
        variante_id = resolucion["variante_id"]
    else:
        max_tokens = 4000
        variante_id = None

    try:
        generated_text = generate_notarial_document(
            act_type=case.act_type,
            notary_label=case.notary.notary_label,
            notary_name=case.notary.current_notary_name or case.notary.legal_name or case.notary.notary_label,
            participants=participants,
            act_data=act_data,
            template_reference_text=template_reference_text,
            correction_text=payload.correction_text,
            max_tokens=max_tokens,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="No fue posible generar el documento con Gari.") from exc

    case.act_data.gari_draft_text = generated_text
    db.flush()

    temp_output = next_case_file_path(case.id, "gari-temp", 1, "docx", f"gari_case_{case.id}.docx")
    gari_document_url = save_gari_document_as_docx(generated_text, temp_output)
    version = add_document_version(
        db,
        case,
        "draft",
        "Borrador documental Gari",
        "docx",
        gari_document_url,
        f"{case.internal_case_number or case.id}_gari.docx",
        current_user.id,
        case.template_id,
        json.dumps({"source": "gari", "model": "gpt-4o"}, ensure_ascii=False),
    )

    previous_state = case.current_state
    if case.current_state in {"borrador", "en_diligenciamiento", "revision_cliente", "ajustes_solicitados"}:
        case.current_state = "generado"

    comment = f"Corrección aplicada: {payload.correction_text}" if payload.correction_text else payload.comment or "Borrador generado con Gari"
    append_timeline(db, case.id, current_user.id, "gari_draft_generated", previous_state, case.current_state, comment, {"version": version.version_number, "variante_id": variante_id})
    append_workflow(db, case, current_user, "gari_draft_generated", actor_role_code="protocolist", comment=comment, from_state=previous_state, to_state=case.current_state, metadata={"version": version.version_number, "source": "gari", "variante_id": variante_id})
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
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Debes generar al menos una versin documental antes de aprobar.")
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
    append_timeline(db, case.id, current_user.id, "state_changed", previous_state, case.current_state, payload.comment or "Aprobacin registrada")
    db.commit()
    return serialize_case_detail(load_case_or_404(db, case.id))


@router.post("/cases/{case_id}/export", response_model=CaseDetail)
def export_case_document(case_id: int, payload: ExportRequest, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary", "protocolist", "approver", "notary"))):
    case = load_case_or_404(db, case_id)
    latest_draft = latest_document_version(case, "draft", "docx")
    if latest_draft is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="No existe borrador documental para exportar.")
    if payload.file_format == "docx":
        version = add_document_version(db, case, "export_word", "Exportacin Word", "docx", latest_draft.storage_path, latest_draft.original_filename, current_user.id, case.template_id, latest_draft.placeholder_snapshot_json)
    else:
        act_data = json.loads(case.act_data.data_json if case.act_data else "{}")
        participants = [{"role_label": item.role_label, "full_name": item.person.full_name, "document_type": item.person.document_type, "document_number": item.person.document_number} for item in case.participants]
        temp_pdf = next_case_file_path(case.id, "temp-export", 1, "pdf", f"case_{case.id}.pdf")
        generate_plain_pdf(temp_pdf, case.act_type, build_case_text_snapshot(case.official_deed_number or case.internal_case_number or str(case.id), case.act_type, participants, act_data))
        version = add_document_version(db, case, "export_pdf", "Exportacin PDF", "pdf", temp_pdf, f"{case.internal_case_number or case.id}.pdf", current_user.id, case.template_id, latest_draft.placeholder_snapshot_json)
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Versin documental no encontrada.")
    if version.storage_path.startswith("https://"):
        return RedirectResponse(url=version.storage_path, status_code=302)
    path = Path(version.storage_path)
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El archivo solicitado no est disponible.")
    return FileResponse(path, media_type=guess_media_type(path), filename=version.original_filename)


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
