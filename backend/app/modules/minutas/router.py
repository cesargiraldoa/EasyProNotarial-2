from __future__ import annotations

import json
import re
from datetime import datetime
import tempfile
import traceback
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db, get_manageable_notary_ids
from app.models.case import Case
from app.models.case_document import CaseDocument
from app.models.case_document_version import CaseDocumentVersion
from app.models.notary import Notary
from app.models.user import User
from app.schemas.minuta import MarkedTemplateDetectionResponse
from app.services.case_numbering import (
    build_case_number_conflict_detail,
    build_internal_case_number,
    is_case_number_integrity_error,
    resolve_next_sequence,
)
from app.services.document_persistence import persist_case_document_version
from app.services.minuta.engine.context_builder import ContextBuilder
from app.services.minuta.marked_template_detector import detect_marked_template
from app.services.minuta.marked_template_state import (
    build_marked_template_edit_payload,
    detect_marked_template_from_bytes,
    merge_marked_template_state,
    safe_marked_template_snapshot,
)
from app.services.minuta.marked_template_generator import NotarialRenderBlockedError, apply_marked_template_replacements
from app.services.minuta.rules.common_rules import normalize_key, normalize_value
from app.modules.minuta.router import _decode_file_token, _make_file_token, _resolve_public_api_base
from app.services.storage import download_storage_bytes

router = APIRouter(prefix="/minutas", tags=["minutas"])


def _sanitize_marked_document_name(raw_name: str | None, fallback_filename: str) -> tuple[str, str]:
    fallback_stem = Path(fallback_filename or "minuta").stem or "minuta"
    candidate = (raw_name or "").strip()
    if not candidate:
        return f"minuta_generada_{fallback_stem}.docx", f"minuta_generada_{fallback_stem}"

    candidate = re.sub(r'[\x00-\x1f<>:"/\\\\|?*]+', " ", candidate)
    candidate = re.sub(r"\s+", " ", candidate).strip(" .")
    if not candidate:
        return f"minuta_generada_{fallback_stem}.docx", f"minuta_generada_{fallback_stem}"

    suffix = Path(candidate).suffix.lower()
    if suffix == ".docx":
        stem = candidate[: -len(suffix)].strip()
    else:
        stem = candidate
        suffix = ".docx"

    stem = re.sub(r"\s+", " ", stem).strip(" .")
    if not stem:
        stem = f"minuta_generada_{fallback_stem}"

    stem = stem[:180].rstrip(" .")
    if not stem:
        stem = f"minuta_generada_{fallback_stem}"

    return f"{stem}{suffix}", stem


def _resolve_marked_template_notary_id(db: Session, current_user: User) -> int:
    notary_ids = sorted(get_manageable_notary_ids(current_user))
    if notary_ids:
        chosen_notary_id = current_user.default_notary_id or notary_ids[0]
        if db.query(Notary.id).filter(Notary.id == chosen_notary_id).first() is not None:
            return chosen_notary_id
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="No fue posible determinar la notaría para persistir la minuta.",
    )


def _create_marked_template_case(db: Session, current_user: User, filename: str) -> Case:
    notary_id = _resolve_marked_template_notary_id(db, current_user)
    notary = db.query(Notary).filter(Notary.id == notary_id).first()
    if notary is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La notaría asociada al usuario no existe.",
        )

    year = datetime.utcnow().year
    for attempt in range(3):
        consecutive = resolve_next_sequence(db, "internal_case", notary_id, year)
        case = Case(
            notary_id=notary_id,
            created_by_user_id=current_user.id,
            case_type="minuta",
            act_type="minuta_marcada",
            consecutive=consecutive,
            year=year,
            internal_case_number=build_internal_case_number(notary, year, consecutive),
            current_state="generado",
            current_owner_user_id=current_user.id,
            metadata_json=json.dumps({"source": "marked_template", "filename": filename}, ensure_ascii=False),
        )
        db.add(case)
        try:
            db.flush()
            return case
        except IntegrityError as exc:
            db.rollback()
            if is_case_number_integrity_error(exc) and attempt < 2:
                continue
            if is_case_number_integrity_error(exc):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=build_case_number_conflict_detail(notary, year, consecutive),
                ) from exc
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No fue posible crear la minuta persistente.",
            ) from exc


def _latest_marked_template_snapshot(case: Case) -> dict | None:
    versions = [
        version
        for document in (case.documents or [])
        for version in (document.versions or [])
        if (version.file_format or "").lower() == "docx"
    ]
    for version in sorted(versions, key=lambda item: (item.created_at or datetime.min, item.id), reverse=True):
        try:
            snapshot = json.loads(version.placeholder_snapshot_json or "{}")
        except json.JSONDecodeError:
            continue
        if snapshot.get("source") == "marked_template" and isinstance(snapshot.get("fields"), list) and isinstance(snapshot.get("values"), dict):
            return snapshot
    return None


def _previous_value_marker_fields(snapshot: dict) -> list[dict]:
    fields = [field for field in (snapshot.get("fields") or []) if isinstance(field, dict)]
    values = snapshot.get("values") if isinstance(snapshot.get("values"), dict) else {}
    if not fields or not values:
        return []

    previous_context = ContextBuilder().build(values, fields)
    result: list[dict] = []
    seen_markers: set[str] = set()
    for field in fields:
        key = normalize_key(field.get("key") or "")
        if not key:
            continue
        marker = normalize_value(previous_context.normalized_values.get(key, ""))
        if len(marker) < 3 or marker in seen_markers:
            continue
        seen_markers.add(marker)
        result.append({**field, "raw_markers": [marker]})
    return result


@router.post("/marked-template/detect", response_model=MarkedTemplateDetectionResponse)
async def detect_marked_template_endpoint(
    archivo: UploadFile = File(..., description="Archivo .docx de minuta marcada por humano"),
    current_user: User = Depends(get_current_user),
):
    if not archivo.filename or not archivo.filename.lower().endswith(".docx"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El archivo debe ser un .docx válido.",
        )

    content = await archivo.read()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El archivo está vacío.",
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        resultado = detect_marked_template(tmp_path)
    except Exception as exc:
        Path(tmp_path).unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al detectar campos marcados: {exc}",
        )

    Path(tmp_path).unlink(missing_ok=True)

    if not resultado.get("fields"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No se encontraron campos marcados en el documento.",
        )

    return resultado


@router.post("/marked-template/generate")
async def generate_marked_template_endpoint(
    request: Request,
    archivo: UploadFile = File(..., description="Archivo .docx de minuta marcada por humano"),
    values: str = Form(..., description="JSON con los valores del formulario marcado"),
    fields: str | None = Form(None, description="JSON opcional con metadata de campos detectados"),
    document_name: str | None = Form(None, description="Nombre opcional de salida para la minuta"),
    case_id: int | None = Form(None, description="ID opcional del caso existente"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not archivo.filename or not archivo.filename.lower().endswith(".docx"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El archivo debe ser un .docx válido.",
        )

    try:
        values_data = json.loads(values)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"JSON inválido en values: {exc}",
        ) from exc

    if not isinstance(values_data, dict):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El campo values debe ser un objeto JSON.",
        )

    fields_data: list[dict] = []
    if fields:
        try:
            parsed_fields = json.loads(fields)
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"JSON inválido en fields: {exc}",
            ) from exc
        if not isinstance(parsed_fields, list):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El campo fields debe ser una lista JSON.",
            )
        fields_data = parsed_fields

    case: Case | None = None
    previous_snapshot: dict | None = None
    if case_id is not None:
        case = db.query(Case).filter(Case.id == case_id).first()
        if case is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La minuta indicada no existe.")
        manageable_notary_ids = get_manageable_notary_ids(current_user)
        if case.notary_id not in manageable_notary_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para usar esta minuta.")
        previous_snapshot = _latest_marked_template_snapshot(case)

    content = await archivo.read()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El archivo está vacío.",
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_in:
        tmp_in.write(content)
        path_entrada = tmp_in.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_out:
        path_salida = tmp_out.name

    try:
        stats_raw = apply_marked_template_replacements(path_entrada, path_salida, values_data, fields_data)
        if int(stats_raw.get("total_replacements", 0) or 0) == 0 and previous_snapshot:
            fallback_fields = _previous_value_marker_fields(previous_snapshot)
            if fallback_fields:
                stats_raw = apply_marked_template_replacements(path_entrada, path_salida, values_data, fallback_fields)
        content_out = Path(path_salida).read_bytes()
    except NotarialRenderBlockedError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "La plantilla no es compatible con los datos diligenciados.",
                "blockers": [
                    {**issue.__dict__, "severity": issue.severity.value}
                    for issue in exc.issues
                    if issue.severity.value == "blocker"
                ],
                "warnings": [
                    {**issue.__dict__, "severity": issue.severity.value}
                    for issue in exc.issues
                    if issue.severity.value == "warning"
                ],
            },
        ) from exc
    except HTTPException:
        raise
    except Exception as exc:
        print("=== ERROR DETALLADO (marked-template/generate) ===")
        print(traceback.format_exc())
        print("==============================================")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar el documento marcado: {exc}",
        ) from exc
    finally:
        Path(path_entrada).unlink(missing_ok=True)
        Path(path_salida).unlink(missing_ok=True)

    display_name, document_title = _sanitize_marked_document_name(document_name, archivo.filename or "minuta.docx")
    if case is None:
        case = _create_marked_template_case(db, current_user, display_name)

    version = persist_case_document_version(
        db,
        case,
        "marked_template",
        document_title,
        "docx",
        content_out,
        display_name,
        current_user.id,
        template_id=None,
        placeholder_snapshot_json=json.dumps(
            {
                "source": "marked_template",
                "fields": fields_data,
                "values": values_data,
                "document_name": document_title,
            },
            ensure_ascii=False,
        ),
    )
    db.commit()

    storage_path = version.storage_path
    notary_id = case.notary_id
    file_token = _make_file_token(
        storage_path,
        version.original_filename,
        display_name,
        notary_id,
        case_id=case.id,
        document_id=version.case_document_id,
        version_id=version.id,
        user_id=current_user.id,
    )
    onlyoffice_path = f"/dashboard/minutas/editor/{file_token}"
    base_url = _resolve_public_api_base(request)
    download_url = f"{base_url}/api/v1/minuta/onlyoffice/file?token={file_token}"

    return {
        "case_id": case.id,
        "document_id": version.case_document_id,
        "version_id": version.id,
        "filename": display_name,
        "onlyoffice_path": onlyoffice_path,
        "download_url": download_url,
        "audit": stats_raw.get("audit", {}),
        "warnings": stats_raw.get("warnings", []),
        "blockers": stats_raw.get("blockers", []),
        "statistics": {
            "total_replacements": int(stats_raw.get("total_replacements", 0) or 0),
            "empty_count": int(stats_raw.get("empty_count", 0) or 0),
            "missing_count": int(stats_raw.get("missing_count", 0) or 0),
            "unresolved_placeholders_count": int(stats_raw.get("unresolved_placeholders_count", 0) or 0),
            "residual_tokens_count": int(stats_raw.get("residual_tokens_count", 0) or 0),
            "warnings_count": int(stats_raw.get("warnings_count", 0) or 0),
            "blockers_count": int(stats_raw.get("blockers_count", 0) or 0),
            "technical_tabs_resolved": int(stats_raw.get("technical_tabs_resolved", 0) or 0),
            "notarial_dash_sequences_preserved": int(stats_raw.get("notarial_dash_sequences_preserved", 0) or 0),
            "red_runs_detected": int(stats_raw.get("red_runs_detected", 0) or 0),
            "empty_signature_blocks_detected": int(stats_raw.get("empty_signature_blocks_detected", 0) or 0),
            "empty_signature_blocks_removed": int(stats_raw.get("empty_signature_blocks_removed", 0) or 0),
            "optional_segments_omitted": int(stats_raw.get("optional_segments_omitted", 0) or 0),
            "optional_segments_omitted_keys": stats_raw.get("optional_segments_omitted_keys", []) or [],
        },
        "estadisticas": {
            "total_reemplazos": int(stats_raw.get("total_replacements", 0) or 0),
            "por_etiqueta": stats_raw.get("by_key", {}) or {},
            "no_encontrados": [
                {
                    "etiqueta": item.get("key", ""),
                    "viejo": item.get("old", ""),
                    "nuevo": item.get("new", ""),
                }
                for item in (stats_raw.get("not_found", []) or [])
                if isinstance(item, dict)
            ],
            "advertencias_concordancia": [
                item
                for item in (stats_raw.get("gender_concordance_warnings", []) or [])
                if isinstance(item, dict)
            ],
        },
    }


@router.get("/marked-template/editor-state")
def marked_template_editor_state(
    token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    payload = _decode_file_token(token)
    case_id = payload.get("case_id")
    document_id = payload.get("document_id")
    version_id = payload.get("version_id")
    if not all(isinstance(value, int) for value in (case_id, document_id, version_id)):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La minuta abierta no tiene metadatos de formulario recuperables.",
        )

    row = (
        db.query(Case, CaseDocument, CaseDocumentVersion)
        .join(CaseDocument, CaseDocument.case_id == Case.id)
        .join(CaseDocumentVersion, CaseDocumentVersion.case_document_id == CaseDocument.id)
        .filter(
            Case.id == case_id,
            CaseDocument.id == document_id,
            CaseDocumentVersion.id == version_id,
        )
        .first()
    )
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La minuta indicada no existe.")
    case_obj, document_obj, source_version = row
    if case_obj.notary_id not in get_manageable_notary_ids(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para usar esta minuta.")

    latest_version = (
        db.query(CaseDocumentVersion)
        .filter(CaseDocumentVersion.case_document_id == document_obj.id)
        .order_by(CaseDocumentVersion.version_number.desc(), CaseDocumentVersion.id.desc())
        .first()
    ) or source_version
    previous_snapshot = safe_marked_template_snapshot(source_version.placeholder_snapshot_json)
    latest_snapshot = safe_marked_template_snapshot(latest_version.placeholder_snapshot_json)
    snapshot = latest_snapshot or previous_snapshot

    if latest_version.id == source_version.id or not latest_snapshot:
        try:
            latest_content = download_storage_bytes(latest_version.storage_path)
            detected = detect_marked_template_from_bytes(latest_content)
        except Exception:
            detected = {"fields": []}
        snapshot = merge_marked_template_state(
            previous_snapshot,
            detected,
            document_name=document_obj.title or payload.get("display_name") or "Minuta marcada",
        )

    return build_marked_template_edit_payload(
        case_obj,
        document_obj,
        latest_version,
        snapshot,
        saved_from_onlyoffice=latest_version.id != source_version.id,
    )
