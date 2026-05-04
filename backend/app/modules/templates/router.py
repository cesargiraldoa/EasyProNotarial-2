from __future__ import annotations

import json
import re

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user, get_db, require_roles
from app.models.document_template import DocumentTemplate
from app.models.notary import Notary
from app.models.template_field import TemplateField
from app.models.template_required_role import TemplateRequiredRole
from app.models.user import User
from app.schemas.template import TemplateCreate, TemplateFieldSummary, TemplateRequiredRoleSummary, TemplateSummary, TemplateUpdate
from app.services.document_generation import extract_highlighted_fields_from_docx
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
        fields=[TemplateFieldSummary.model_validate(item) for item in template.fields if item.label and len(item.label.strip()) >= 2],
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

    extracted_fields = None
    if payload.upload:
        source_filename, storage_path = save_template_upload(payload.upload.filename, payload.upload.content_base64, template.slug or slugify(payload.name))
        template.source_filename = source_filename
        template.storage_path = storage_path
        if (payload.upload.filename or "").lower().endswith(".docx"):
            extracted_fields = extract_highlighted_fields_from_docx(storage_path)

    template.required_roles.clear()
    template.fields.clear()
    db.flush()
    for item in payload.required_roles:
        template.required_roles.append(TemplateRequiredRole(role_code=item.role_code.strip(), label=item.label.strip(), is_required=item.is_required, step_order=item.step_order))
    if extracted_fields:
        for item in extracted_fields:
            template.fields.append(
                TemplateField(
                    field_code=item["field_code"].strip(),
                    label=item["label"].strip(),
                    field_type="text",
                    section="general",
                    is_required=True,
                    options_json=None,
                    placeholder_key=None,
                    help_text=None,
                    step_order=item["display_order"],
                )
            )
    else:
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
def create_template(payload: TemplateCreate = Body(...), db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary"))):
    template = DocumentTemplate(slug=slugify(payload.name))
    persist_template_payload(db, template, payload)
    db.add(template)
    db.commit()
    db.refresh(template)
    return serialize_template(load_template_or_404(db, template.id))


@router.put("/{template_id}", response_model=TemplateSummary)
def update_template(template_id: int, payload: TemplateUpdate = Body(...), db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary"))):
    template = load_template_or_404(db, template_id)
    persist_template_payload(db, template, payload)
    db.commit()
    return serialize_template(load_template_or_404(db, template.id))

