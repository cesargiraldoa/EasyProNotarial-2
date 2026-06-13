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
from app.services.minuta.marked_template_detector import detect_marked_template
from app.services.minuta.marked_template_generator import apply_marked_template_replacements
from app.modules.minuta.router import _make_file_token, _resolve_public_api_base

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
        content_out = Path(path_salida).read_bytes()
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
    if case_id is not None:
        case = db.query(Case).filter(Case.id == case_id).first()
        if case is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La minuta indicada no existe.")
        manageable_notary_ids = get_manageable_notary_ids(current_user)
        if case.notary_id not in manageable_notary_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para usar esta minuta.")
    else:
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
    file_token = _make_file_token(storage_path, version.original_filename, display_name, notary_id)
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
        },
    }
