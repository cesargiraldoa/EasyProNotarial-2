from __future__ import annotations

import hashlib
import json
import logging
import time
from typing import Literal

import sqlalchemy as sa
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.v1.endpoints.biblioteca import (
    CaseDocumentContext,
    _resolve_case_document_objects,
    _user_can_access_notary,
)
from app.core.config import get_settings
from app.core.deps import get_current_user, get_db
from app.db.session import SessionLocal
from app.models.biblioteca_learning import BibliotecaAnalysisRun
from app.models.case import Case
from app.models.case_document import CaseDocument
from app.models.case_document_version import CaseDocumentVersion
from app.models.notarial_field_catalog import NotarialFieldCatalog
from app.models.user import User
from app.services.biblioteca_motor.analysis import (
    OpenAIBibliotecaExtractor,
    analyze_biblioteca_document,
    build_analysis_failure_payload,
)
from app.services.biblioteca_motor.llm_extractor import LLMExtractorError
from app.services.biblioteca_motor.notary_prompt_service import (
    active_profile_payload,
    retrieve_relevant_examples,
)
from app.services.biblioteca_motor.review_document import prepare_review_document
from app.services.document_persistence import persist_case_document_version
from app.services.storage import download_storage_bytes


router = APIRouter(prefix="/biblioteca", tags=["biblioteca"])
logger = logging.getLogger(__name__)


class StartAnalysisResponse(BaseModel):
    run_id: int
    status: Literal["queued", "running"]
    reused: bool = False


class AnalysisStatusResponse(BaseModel):
    run_id: int
    status: str
    review_document: dict | None = None
    stats: dict | None = None
    timing: dict | None = None
    error_code: str | None = None
    error_message: str | None = None


@router.post(
    "/analisis/iniciar",
    response_model=StartAnalysisResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def start_analysis(
    payload: CaseDocumentContext,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case_obj, document_obj, version_obj = _resolve_case_document_objects(
        payload,
        db,
        current_user,
    )

    existing = (
        db.query(BibliotecaAnalysisRun)
        .filter(
            BibliotecaAnalysisRun.notary_id == case_obj.notary_id,
            BibliotecaAnalysisRun.case_id == case_obj.id,
            BibliotecaAnalysisRun.document_id == document_obj.id,
            BibliotecaAnalysisRun.source_version_id == version_obj.id,
            BibliotecaAnalysisRun.status.in_(["queued", "running"]),
        )
        .order_by(BibliotecaAnalysisRun.id.desc())
        .first()
    )
    if existing is not None:
        return {
            "run_id": existing.id,
            "status": existing.status,
            "reused": True,
        }

    try:
        source_bytes = download_storage_bytes(version_obj.storage_path)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento no disponible.",
        ) from exc

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
                "transport": "async_background_v1",
                "queued_at_epoch": time.time(),
            },
            ensure_ascii=False,
        ),
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    background_tasks.add_task(
        _process_analysis_run,
        run.id,
        getattr(current_user, "id", None),
    )
    return {"run_id": run.id, "status": "queued", "reused": False}


@router.get("/analisis/{run_id}", response_model=AnalysisStatusResponse)
def get_analysis_status(
    run_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    run = db.query(BibliotecaAnalysisRun).filter(BibliotecaAnalysisRun.id == run_id).first()
    if run is None or not _user_can_access_notary(current_user, run.notary_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analisis no encontrado.")

    diagnostics = _json_object(run.diagnostics_json)
    payload: dict = {
        "run_id": run.id,
        "status": run.status,
        "stats": diagnostics.get("stats"),
        "timing": diagnostics.get("timing"),
        "error_code": run.error_code,
        "error_message": run.error_message,
    }
    if run.status == "completed" and run.review_version_id:
        payload["review_document"] = {
            "kind": "case_document",
            "case_id": run.case_id,
            "document_id": run.document_id,
            "version_id": run.review_version_id,
        }
    return payload


def _process_analysis_run(run_id: int, user_id: int | None) -> None:
    db = SessionLocal()
    try:
        claimed = (
            db.query(BibliotecaAnalysisRun)
            .filter(
                BibliotecaAnalysisRun.id == run_id,
                BibliotecaAnalysisRun.status == "queued",
            )
            .update({BibliotecaAnalysisRun.status: "running"}, synchronize_session=False)
        )
        db.commit()
        if claimed != 1:
            return

        run = db.query(BibliotecaAnalysisRun).filter(BibliotecaAnalysisRun.id == run_id).first()
        if run is None:
            return
        row = (
            db.query(Case, CaseDocument, CaseDocumentVersion)
            .join(CaseDocument, CaseDocument.case_id == Case.id)
            .join(CaseDocumentVersion, CaseDocumentVersion.case_document_id == CaseDocument.id)
            .filter(
                Case.id == run.case_id,
                CaseDocument.id == run.document_id,
                CaseDocumentVersion.id == run.source_version_id,
            )
            .first()
        )
        if row is None:
            raise RuntimeError("source_document_not_found")
        case_obj, document_obj, version_obj = row

        source_bytes = download_storage_bytes(version_obj.storage_path)
        fields = _field_catalog_for_notary(db, run.notary_id)
        active_profile, profile_version = active_profile_payload(db, run.notary_id)
        examples = retrieve_relevant_examples(db, notary_id=run.notary_id)
        settings = get_settings()
        extractor = OpenAIBibliotecaExtractor(settings.openai_api_key)
        run.model = extractor.model
        run.prompt_version = extractor.prompt_version
        run.profile_version = profile_version
        db.commit()

        started = time.perf_counter()
        result = analyze_biblioteca_document(
            source_bytes,
            fields,
            extractor=extractor,
            notary_id=run.notary_id,
            active_profile=active_profile,
            profile_version=profile_version,
            examples=examples,
        )
        review_started = time.perf_counter()
        review = prepare_review_document(
            source_bytes,
            result.get("suggestions") or [],
            analysis_id=result["analysis_id"],
        )
        review_ms = max(0, int((time.perf_counter() - review_started) * 1000))
        stats = {
            **(result.get("stats") or {}),
            "groups": len(review.groups),
            "wrapped_suggestions": review.wrapped_count,
            "review_skipped_suggestions": len(review.skipped),
        }
        timing = {
            **(result.get("timing") or {}),
            "review_ms": review_ms,
            "async_total_ms": max(0, int((time.perf_counter() - started) * 1000)),
        }
        snapshot = {
            "biblioteca_review": {
                "analysis_id": result["analysis_id"],
                "analysis_run_id": run.id,
                "source_version_id": version_obj.id,
                "document_type": result.get("document_type"),
                "model": result.get("model"),
                "prompt_version": result.get("prompt_version"),
                "profile_version": result.get("profile_version"),
                "groups": review.groups,
                "stats": stats,
            }
        }
        new_version = persist_case_document_version(
            db,
            case_obj,
            document_obj.category,
            document_obj.title,
            version_obj.file_format or "docx",
            review.docx_bytes,
            version_obj.original_filename or f"{document_obj.title}.docx",
            user_id,
            version_obj.generated_from_template_id,
            placeholder_snapshot_json=json.dumps(snapshot, ensure_ascii=False),
        )

        usage = result.get("usage") or {}
        run.review_version_id = new_version.id
        run.status = "completed"
        run.document_type = result.get("document_type")
        run.input_tokens = usage.get("input_tokens")
        run.output_tokens = usage.get("output_tokens")
        run.cost_usd = usage.get("cost_usd")
        run.latency_ms = timing.get("async_total_ms")
        run.detected_fields = int(stats.get("detected_candidates") or 0)
        run.anchored_fields = int(stats.get("anchored_suggestions") or 0)
        run.skipped_fields = int(stats.get("skipped_suggestions") or 0)
        run.error_code = None
        run.error_message = None
        run.diagnostics_json = json.dumps(
            {
                "transport": "async_background_v1",
                "analysis_id": result.get("analysis_id"),
                "stats": stats,
                "timing": timing,
                "diagnostics": result.get("diagnostics") or {},
            },
            ensure_ascii=False,
        )
        db.commit()
        logger.info(
            "biblioteca async review completed run_id=%s source_version_id=%s review_version_id=%s detected=%s wrapped=%s total_ms=%s",
            run.id,
            run.source_version_id,
            run.review_version_id,
            run.detected_fields,
            review.wrapped_count,
            run.latency_ms,
        )
    except LLMExtractorError as exc:
        db.rollback()
        code, _status_code = build_analysis_failure_payload(exc)
        _mark_failed(db, run_id, code, str(exc))
    except Exception as exc:
        db.rollback()
        logger.exception("biblioteca async review failed run_id=%s", run_id)
        _mark_failed(db, run_id, "analysis_job_failed", str(exc))
    finally:
        db.close()


def _mark_failed(db: Session, run_id: int, code: str, message: str) -> None:
    run = db.query(BibliotecaAnalysisRun).filter(BibliotecaAnalysisRun.id == run_id).first()
    if run is None:
        return
    run.status = "failed"
    run.error_code = code[:120]
    run.error_message = message[:1000]
    db.commit()


def _field_catalog_for_notary(
    db: Session,
    notary_id: int | None,
) -> list[NotarialFieldCatalog]:
    query = db.query(NotarialFieldCatalog).filter(NotarialFieldCatalog.is_active.is_(True))
    if notary_id is None:
        query = query.filter(
            NotarialFieldCatalog.scope == "global",
            NotarialFieldCatalog.notary_id.is_(None),
        )
    else:
        query = query.filter(
            sa.or_(
                sa.and_(
                    NotarialFieldCatalog.scope == "global",
                    NotarialFieldCatalog.notary_id.is_(None),
                ),
                sa.and_(
                    NotarialFieldCatalog.scope == "notary",
                    NotarialFieldCatalog.notary_id == notary_id,
                ),
            )
        )
    return query.order_by(NotarialFieldCatalog.category.asc(), NotarialFieldCatalog.code.asc()).all()


def _json_object(raw: str | None) -> dict:
    try:
        parsed = json.loads(raw or "{}")
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        return {}
