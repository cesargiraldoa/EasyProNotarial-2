from __future__ import annotations

import json
import logging
import re

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user, get_db, has_role, require_roles
from app.models.document_template import DocumentTemplate
from app.models.notary import Notary
from app.models.template_field import TemplateField
from app.models.template_required_role import TemplateRequiredRole
from app.models.user import User
from app.schemas.template import TemplateCreate, TemplateFieldSummary, TemplateRequiredRoleSummary, TemplateSummary, TemplateUpdate
from app.services.document_generation import extract_highlighted_fields_from_docx
from app.services.storage import resolve_template_source_path, save_template_upload

router = APIRouter(prefix="/templates", tags=["templates"])
logger = logging.getLogger(__name__)


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return cleaned or "plantilla"


def load_template_or_404(db: Session, template_id: int) -> DocumentTemplate:
    template = db.query(DocumentTemplate).options(joinedload(DocumentTemplate.required_roles), joinedload(DocumentTemplate.fields), joinedload(DocumentTemplate.notary)).filter(DocumentTemplate.id == template_id).first()
    if template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plantilla no encontrada.")
    return template


def serialize_template(template: DocumentTemplate) -> TemplateSummary:
    valid_fields = [
        item
        for item in template.fields
        if (item.field_code and len(item.field_code.strip()) >= 2) and (item.label and len(item.label.strip()) >= 2)
    ]
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
        fields=[TemplateFieldSummary.model_validate(item) for item in valid_fields],
    )


def validate_template_scope(db: Session, payload: TemplateCreate | TemplateUpdate) -> None:
    if payload.scope_type not in {"global", "notary"}:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="scope_type debe ser global o notary.")
    if payload.notary_id is not None and db.query(Notary.id).filter(Notary.id == payload.notary_id).first() is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="La notaría seleccionada no existe.")


def persist_template_payload(db: Session, template: DocumentTemplate, payload: TemplateCreate | TemplateUpdate) -> DocumentTemplate:
    logger.info(
        "templates.save.start name=%s scope=%s notary_id=%s upload=%s filename=%s",
        payload.name.strip(),
        payload.scope_type,
        payload.notary_id,
        bool(payload.upload),
        getattr(payload.upload, "filename", None) if payload.upload else None,
    )
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
        logger.info(
            "templates.save.upload filename=%s base64_size=%s",
            payload.upload.filename,
            len(payload.upload.content_base64 or ""),
        )
        try:
            source_filename, storage_path = save_template_upload(payload.upload.filename, payload.upload.content_base64, template.slug or slugify(payload.name))
            template.source_filename = source_filename
            template.storage_path = storage_path
            logger.info("templates.save.upload.saved filename=%s storage_path=%s", source_filename, storage_path)
            if (payload.upload.filename or "").lower().endswith(".docx"):
                logger.info("templates.save.extract.start filename=%s", payload.upload.filename)
                extracted_fields = extract_highlighted_fields_from_docx(resolve_template_source_path(storage_path))
                logger.info("templates.save.extract.ok filename=%s fields=%s", payload.upload.filename, len(extracted_fields or []))
        except Exception:
            logger.exception("templates.save.upload.failed filename=%s", payload.upload.filename)
            raise

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
    logger.info(
        "templates.save.complete name=%s upload=%s extracted_fields=%s",
        template.name,
        bool(payload.upload),
        len(extracted_fields or []),
    )
    return template


@router.get("", response_model=list[TemplateSummary])
def list_templates(active_only: bool = Query(default=False), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(DocumentTemplate).options(joinedload(DocumentTemplate.required_roles), joinedload(DocumentTemplate.fields), joinedload(DocumentTemplate.notary)).order_by(DocumentTemplate.updated_at.desc(), DocumentTemplate.id.desc())
    if not has_role(current_user, "super_admin"):
        if current_user.default_notary_id is None:
            return []
        query = query.filter(DocumentTemplate.notary_id == current_user.default_notary_id)
    if active_only:
        query = query.filter(DocumentTemplate.is_active.is_(True))
    return [serialize_template(item) for item in query.all()]


@router.get("/active", response_model=list[TemplateSummary])
def list_active_templates(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(DocumentTemplate).options(joinedload(DocumentTemplate.required_roles), joinedload(DocumentTemplate.fields), joinedload(DocumentTemplate.notary)).filter(DocumentTemplate.is_active.is_(True))
    if not has_role(current_user, "super_admin"):
        if current_user.default_notary_id is None:
            return []
        query = query.filter(DocumentTemplate.notary_id == current_user.default_notary_id)
    items = query.order_by(DocumentTemplate.name.asc()).all()
    return [serialize_template(item) for item in items]


@router.get("/{template_id}", response_model=TemplateSummary)
def get_template(template_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return serialize_template(load_template_or_404(db, template_id))


@router.post("", response_model=TemplateSummary, status_code=status.HTTP_201_CREATED)
def create_template(payload: TemplateCreate = Body(...), db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary"))):
    if not has_role(current_user, "super_admin"):
        if current_user.default_notary_id is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El usuario no tiene notaría por defecto asignada.")
        payload.scope_type = "notary"
        payload.notary_id = current_user.default_notary_id
    template = DocumentTemplate(slug=slugify(payload.name))
    persist_template_payload(db, template, payload)
    db.add(template)
    db.commit()
    db.refresh(template)
    logger.info("templates.create.saved template_id=%s name=%s", template.id, template.name)
    return serialize_template(load_template_or_404(db, template.id))


@router.put("/{template_id}", response_model=TemplateSummary)
def update_template(template_id: int, payload: TemplateUpdate = Body(...), db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary"))):
    template = load_template_or_404(db, template_id)
    if not has_role(current_user, "super_admin"):
        if current_user.default_notary_id is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El usuario no tiene notaría por defecto asignada.")
        if template.notary_id != current_user.default_notary_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para editar esta plantilla.")
        payload.scope_type = "notary"
        payload.notary_id = current_user.default_notary_id
    persist_template_payload(db, template, payload)
    db.commit()
    logger.info("templates.update.saved template_id=%s name=%s", template.id, template.name)
    return serialize_template(load_template_or_404(db, template.id))
