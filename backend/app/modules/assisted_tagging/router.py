from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user, get_db, get_manageable_notary_ids
from app.models.assisted_tagging import AssistedTaggingJob
from app.models.user import User
from app.modules.minuta.router import _make_file_token, _resolve_public_api_base
from app.services.minuta.assisted_tagging import AssistedTaggingService

router = APIRouter(prefix="/minutas/assisted-tagging", tags=["assisted-tagging"])
service = AssistedTaggingService()


def _notary_id_for_user(current_user: User) -> int:
    manageable = sorted(get_manageable_notary_ids(current_user))
    chosen = current_user.default_notary_id or (manageable[0] if manageable else None)
    if chosen is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="No fue posible determinar la notaria del usuario.")
    if manageable and chosen not in manageable:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para esta notaria.")
    return int(chosen)


def _load_job(db: Session, job_id: int, current_user: User) -> AssistedTaggingJob:
    job = db.query(AssistedTaggingJob).options(joinedload(AssistedTaggingJob.fields)).filter(AssistedTaggingJob.id == job_id).first()
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job de etiquetado no encontrado.")
    manageable = get_manageable_notary_ids(current_user)
    if manageable and job.notary_id not in manageable:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para este job.")
    return job


def _json_list(value: str | None) -> list:
    try:
        parsed = json.loads(value or "[]")
    except json.JSONDecodeError:
        return []
    return parsed if isinstance(parsed, list) else []


def _serialize_job(job: AssistedTaggingJob, request: Request | None = None) -> dict:
    onlyoffice_path = None
    download_url = None
    if request is not None and job.pretagged_docx_storage_path:
        token = _make_file_token(
            job.pretagged_docx_storage_path,
            Path(job.pretagged_docx_storage_path).name,
            f"preetiquetada_{job.source_filename}",
            job.notary_id,
        )
        onlyoffice_path = f"/dashboard/minutas/editor/{token}"
        base_url = _resolve_public_api_base(request)
        download_url = f"{base_url}/api/v1/minuta/onlyoffice/file?token={token}"
    return {
        "id": job.id,
        "job_uuid": job.job_uuid,
        "status": job.status,
        "document_type": job.document_type,
        "source_filename": job.source_filename,
        "template_id": job.template_id,
        "onlyoffice_path": onlyoffice_path,
        "download_url": download_url,
        "approved_docx_uploaded": bool(job.approved_docx_storage_path),
        "warnings": _json_list(job.warnings_json),
        "error_message": job.error_message,
        "fields": [
            {
                "field_code": field.field_code,
                "label": field.label,
                "section": field.section,
                "confidence": field.confidence,
                "occurrences": field.occurrences,
                "status": field.status,
                "warning": field.warning,
            }
            for field in job.fields
        ],
        "created_at": job.created_at,
        "updated_at": job.updated_at,
    }


@router.post("/jobs", status_code=status.HTTP_201_CREATED)
async def create_job(
    request: Request,
    document_type: str = Form(...),
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not archivo.filename or not archivo.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El archivo debe ser un DOCX valido.")
    content = await archivo.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El archivo esta vacio.")
    job = service.create_job(
        db,
        filename=archivo.filename,
        content=content,
        document_type=document_type,
        notary_id=_notary_id_for_user(current_user),
        user_id=current_user.id,
    )
    db.commit()
    db.refresh(job)
    return _serialize_job(_load_job(db, job.id, current_user), request)


@router.post("/jobs/{job_id}/run")
def run_job(job_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    job = _load_job(db, job_id, current_user)
    if job.status not in {"uploaded", "failed"}:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Este job ya fue procesado.")
    service.run_job(db, job)
    db.commit()
    return _serialize_job(_load_job(db, job.id, current_user), request)


@router.get("/jobs/{job_id}")
def get_job(job_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return _serialize_job(_load_job(db, job_id, current_user), request)


@router.post("/jobs/{job_id}/approve")
def approve_job(
    job_id: int,
    request: Request,
    confirm_no_changes: bool = Form(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = _load_job(db, job_id, current_user)
    if job.status not in {"human_review", "pretagged"}:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El job no esta listo para aprobar.")
    try:
        service.approve_job(db, job, user_id=current_user.id, confirm_no_changes=confirm_no_changes)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    db.commit()
    return _serialize_job(_load_job(db, job.id, current_user), request)


@router.post("/jobs/{job_id}/approved-docx")
async def upload_approved_docx(
    job_id: int,
    request: Request,
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = _load_job(db, job_id, current_user)
    if job.status not in {"human_review", "pretagged"}:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El job no esta en revision humana.")
    if not archivo.filename or not archivo.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El archivo aprobado debe ser un DOCX valido.")
    try:
        service.upload_approved_docx(db, job, filename=archivo.filename, content=await archivo.read())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    db.commit()
    return _serialize_job(_load_job(db, job.id, current_user), request)


@router.post("/jobs/{job_id}/reject")
def reject_job(
    job_id: int,
    request: Request,
    reason: str | None = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = _load_job(db, job_id, current_user)
    service.reject_job(db, job, reason)
    db.commit()
    return _serialize_job(_load_job(db, job.id, current_user), request)
