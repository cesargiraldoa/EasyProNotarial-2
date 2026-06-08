from __future__ import annotations

import json
import tempfile
import traceback
from pathlib import Path

import uuid as _uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status

from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.minuta import MarkedTemplateDetectionResponse
from app.services.minuta.marked_template_detector import detect_marked_template
from app.services.minuta.marked_template_generator import apply_marked_template_replacements
from app.services.storage import SUPABASE_CASE_BUCKET, _has_supabase_credentials, _upload_to_supabase, sanitize_filename
from app.modules.minuta.router import _make_file_token, _resolve_public_api_base

router = APIRouter(prefix="/minutas", tags=["minutas"])


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
    current_user: User = Depends(get_current_user),
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

    notary_id = current_user.default_notary_id or 0
    file_uuid = str(_uuid.uuid4())
    storage_filename = f"{file_uuid}_minuta.docx"
    display_name = f"minuta_generada_{sanitize_filename(Path(archivo.filename).stem)}.docx"
    storage_key = f"minutas/notary_{notary_id}/{storage_filename}"
    docx_media = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    if _has_supabase_credentials():
        _upload_to_supabase(SUPABASE_CASE_BUCKET, storage_key, content_out, docx_media)
        storage_path = f"supabase://{SUPABASE_CASE_BUCKET}/{storage_key}"
    else:
        from app.services.storage import CASE_STORAGE

        local_dir = CASE_STORAGE / "minutas" / f"notary_{notary_id}"
        local_dir.mkdir(parents=True, exist_ok=True)
        local_file = local_dir / storage_filename
        local_file.write_bytes(content_out)
        storage_path = str(local_file)

    file_token = _make_file_token(storage_path, storage_filename, display_name, notary_id)
    onlyoffice_path = f"/dashboard/minutas/editor/{file_token}"
    base_url = _resolve_public_api_base(request)
    download_url = f"{base_url}/api/v1/minuta/onlyoffice/file?token={file_token}"

    return {
        "case_id": None,
        "document_id": None,
        "version_id": None,
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
