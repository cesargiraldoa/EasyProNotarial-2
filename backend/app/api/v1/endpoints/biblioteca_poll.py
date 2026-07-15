from __future__ import annotations

import hashlib
import json
import time
from datetime import timedelta
from typing import Literal

import sqlalchemy as sa
from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, status
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.v1.endpoints.biblioteca import CaseDocumentContext, _resolve_case_document_objects
from app.api.v1.endpoints.biblioteca_async import _process_analysis_run
from app.core.config import get_settings
from app.core.deps import get_current_user, get_db
from app.core.security import ALGORITHM, create_access_token
from app.models.biblioteca_learning import BibliotecaAnalysisRun
from app.models.user import User
from app.services.biblioteca_motor.analysis import OpenAIBibliotecaExtractor
from app.services.storage import download_storage_bytes


router = APIRouter(prefix="/biblioteca", tags=["biblioteca"])
POLL_SCOPE = "biblioteca_analysis_poll"
POLL_TOKEN_TTL = timedelta(hours=1)


class SecureStartAnalysisResponse(BaseModel):
    run_id: int
    status: Literal["queued", "running", "completed"]
    reused: bool = False
    poll_token: str


class SecureAnalysisStatusResponse(BaseModel):
    run_id: int
    status: str
    review_document: dict | None = None
    stats: dict | None = None
    timing: dict | None = None
    error_code: str | None = None
    error_message: str | None = None


def _create_poll_token(run_id: int) -> str:
    return create_access_token(
        subject=f"biblioteca-analysis:{run_id}",
        expires_delta=POLL_TOKEN_TTL,
        extra_claims={"scope": POLL_SCOPE, "run_id": run_id},
    )


def _validate_poll_token(run_id: int, authorization: str | None) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de consulta requerido.")
    raw_token = authorization.split(" ", 1)[1].strip()
    try:
        settings = get_settings()
        payload = jwt.decode(raw_token, settings.secret_key, algorithms=[ALGORITHM])
        token_run_id = int(payload.get("run_id"))
    except (JWTError, TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de consulta inválido.")
    if payload.get("scope") != POLL_SCOPE or token_run_id != run_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de consulta no autorizado.")
    if payload.get("sub") != f"biblioteca-analysis:{run_id}":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de consulta no autorizado.")
    return payload


@router.post(
    "/analisis/iniciar-seguro",
    response_model=SecureStartAnalysisResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def start_secure_analysis(
    payload: CaseDocumentContext,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case_obj, document_obj, version_obj = _resolve_case_document_objects(payload, db, current_user)

    reusable = (
        db.query(BibliotecaAnalysisRun)
        .filter(
            BibliotecaAnalysisRun.notary_id == case_obj.notary_id,
            BibliotecaAnalysisRun.case_id == case_obj.id,
            BibliotecaAnalysisRun.document_id == document_obj.id,
            BibliotecaAnalysisRun.source_version_id == version_obj.id,
            sa.or_(
                BibliotecaAnalysisRun.status.in_(["queued", "running"]),
                sa.and_(
                    BibliotecaAnalysisRun.status == "completed",
                    BibliotecaAnalysisRun.review_version_id.isnot(None),
                ),
            ),
        )
        .order_by(BibliotecaAnalysisRun.id.desc())
        .first()
    )
    if reusable is not None:
        if reusable.status == "queued":
            background_tasks.add_task(_process_analysis_run, reusable.id, getattr(current_user, "id", None))
        return {
            "run_id": reusable.id,
            "status": reusable.status,
            "reused": True,
            "poll_token": _create_poll_token(reusable.id),
        }

    try:
        source_bytes = download_storage_bytes(version_obj.storage_path)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento no disponible.") from exc

    settings = get_settings()
    extractor = OpenAIBibliotecaExtractor(settings.openai_api_key)
    run = BibliotecaAnalysisRun(
        notary_id=case_obj.notary_id,
        case_id=case_obj.id,
        document_id=document_obj.id,
        source_version_id=version_obj.id,
        document_sha256=hashlib.sha256(source_bytes).hexdigest(),
        model=extractor.model,
        prompt_version=extractor.prompt_version,
        status="queued",
        diagnostics_json=json.dumps(
            {
                "transport": "async_background_v2_poll_token",
                "queued_at_epoch": time.time(),
            },
            ensure_ascii=False,
        ),
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    background_tasks.add_task(_process_analysis_run, run.id, getattr(current_user, "id", None))
    return {
        "run_id": run.id,
        "status": "queued",
        "reused": False,
        "poll_token": _create_poll_token(run.id),
    }


@router.get(
    "/analisis/{run_id}/estado-seguro",
    response_model=SecureAnalysisStatusResponse,
)
def get_secure_analysis_status(
    run_id: int,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    _validate_poll_token(run_id, authorization)
    run = db.query(BibliotecaAnalysisRun).filter(BibliotecaAnalysisRun.id == run_id).first()
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Análisis no encontrado.")

    diagnostics = _json_object(run.diagnostics_json)
    response: dict = {
        "run_id": run.id,
        "status": run.status,
        "stats": diagnostics.get("stats"),
        "timing": diagnostics.get("timing"),
        "error_code": run.error_code,
        "error_message": run.error_message,
    }
    if run.status == "completed" and run.review_version_id:
        response["review_document"] = {
            "kind": "case_document",
            "case_id": run.case_id,
            "document_id": run.document_id,
            "version_id": run.review_version_id,
        }
    return response


def _json_object(raw: str | None) -> dict:
    try:
        parsed = json.loads(raw or "{}")
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        return {}
