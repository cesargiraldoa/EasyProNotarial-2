import json
import tempfile
import uuid as _uuid
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Query, Request, UploadFile, status
from fastapi.responses import Response
from jose import jwt
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.services.minuta.detector import analizar_documento, extraer_texto_estructurado
from app.services.minuta.reemplazador import aplicar_reemplazos_docx, construir_lista_reemplazos
from app.services.minuta.concordancia import (
    aplicar_cambios_concordancia_a_reemplazos,
    detectar_concordancia,
    necesita_concordancia,
)
from app.services.storage import (
    SUPABASE_CASE_BUCKET,
    _has_supabase_credentials,
    _upload_to_supabase,
    download_storage_bytes,
    parse_supabase_storage_path,
    sanitize_filename,
)

router = APIRouter(prefix="/minuta", tags=["minuta"])


# ─── helpers ─────────────────────────────────────────────────────────────────

def _get_api_key() -> str:
    key = get_settings().openai_api_key
    if not key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OPENAI_API_KEY no configurada en el servidor.",
        )
    return key


def _resolve_public_api_base(request: Request) -> str:
    configured = (get_settings().api_public_url or "").strip()
    if configured:
        return configured.rstrip("/")
    return str(request.base_url).rstrip("/")


def _signing_secret() -> str:
    """Usa onlyoffice_jwt_secret si está configurado, cae a secret_key."""
    s = get_settings()
    return ((s.onlyoffice_jwt_secret or "").strip()) or s.secret_key


def _make_file_token(storage_path: str, filename: str, display_name: str, notary_id: int) -> str:
    return jwt.encode(
        {
            "storage_path": storage_path,
            "filename": filename,
            "display_name": display_name,
            "notary_id": notary_id,
            "exp": datetime.utcnow() + timedelta(hours=24),
        },
        _signing_secret(),
        algorithm="HS256",
    )


def _decode_file_token(token: str) -> dict:
    try:
        return jwt.decode(token, _signing_secret(), algorithms=["HS256"])
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de minuta inválido o expirado.",
        ) from exc


# ─── POST /analizar ───────────────────────────────────────────────────────────

@router.post("/analizar")
async def analizar_minuta(
    archivo: UploadFile = File(..., description="Archivo .docx de la minuta a analizar"),
    current_user: User = Depends(get_current_user),
):
    """
    Recibe un .docx, detecta si es B1 o B2 y extrae personas, valores,
    inmueble, actos y decisiones.
    """
    if not archivo.filename or not archivo.filename.lower().endswith(".docx"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El archivo debe ser un .docx válido.",
        )

    api_key = _get_api_key()

    suffix = Path(archivo.filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await archivo.read())
        tmp_path = tmp.name

    try:
        resultado = analizar_documento(tmp_path, api_key)
    except Exception as exc:
        Path(tmp_path).unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al analizar el documento: {exc}",
        )

    Path(tmp_path).unlink(missing_ok=True)
    return resultado


# ─── POST /generar ────────────────────────────────────────────────────────────

@router.post("/generar")
async def generar_minuta(
    request: Request,
    background_tasks: BackgroundTasks,
    archivo: UploadFile = File(..., description="Archivo .docx base con los datos anteriores"),
    datos_anteriores: str = Form(..., description="JSON con datos del caso anterior (salida de /analizar)"),
    datos_nuevos: str = Form(..., description="JSON con los nuevos datos a aplicar"),
    current_user: User = Depends(get_current_user),
):
    """
    Aplica reemplazos de datos y concordancia de género, sube el .docx resultante
    a Supabase Storage y retorna un JSON con la ruta al editor OnlyOffice.
    """
    if not archivo.filename or not archivo.filename.lower().endswith(".docx"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El archivo debe ser un .docx válido.",
        )

    try:
        datos_ant = json.loads(datos_anteriores)
        datos_nv = json.loads(datos_nuevos)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"JSON inválido en datos_anteriores o datos_nuevos: {exc}",
        )

    api_key = _get_api_key()

    # Archivos temporales de entrada y salida
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_in:
        tmp_in.write(await archivo.read())
        path_entrada = tmp_in.name

    tmp_out = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
    path_salida = tmp_out.name
    tmp_out.close()

    try:
        # 1. Reemplazos de datos (nombres, documentos, valores, inmueble)
        reemplazos = construir_lista_reemplazos(datos_ant, datos_nv)

        # 2. Concordancia de género: por cada persona cuyo género cambia M↔F
        texto_doc = extraer_texto_estructurado(path_entrada)
        personas_viejas = {p["rol"]: p for p in datos_ant.get("personas", [])}
        personas_nuevas = {p["rol"]: p for p in datos_nv.get("personas", [])}

        for rol, persona_nueva in personas_nuevas.items():
            persona_vieja = personas_viejas.get(rol, {})
            if necesita_concordancia(persona_vieja, persona_nueva):
                resultado_conc = detectar_concordancia(
                    texto_doc, persona_vieja, persona_nueva, api_key
                )
                reemplazos_conc = aplicar_cambios_concordancia_a_reemplazos(
                    resultado_conc.get("cambios", [])
                )
                reemplazos.extend(reemplazos_conc)

        # 3. Aplicar todos los reemplazos al .docx
        aplicar_reemplazos_docx(path_entrada, reemplazos, path_salida)

    except Exception as exc:
        Path(path_entrada).unlink(missing_ok=True)
        Path(path_salida).unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar la minuta: {exc}",
        )

    Path(path_entrada).unlink(missing_ok=True)

    # 4. Leer bytes y subir a Supabase Storage
    try:
        content = Path(path_salida).read_bytes()
    except Exception as exc:
        Path(path_salida).unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al leer el archivo generado: {exc}",
        )

    background_tasks.add_task(Path(path_salida).unlink, True)

    notary_id = current_user.default_notary_id or 0
    file_uuid = str(_uuid.uuid4())
    storage_filename = f"{file_uuid}_minuta.docx"
    display_name = f"minuta_generada_{sanitize_filename(Path(archivo.filename).stem)}.docx"
    storage_key = f"minutas/notary_{notary_id}/{storage_filename}"
    docx_media = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    try:
        if _has_supabase_credentials():
            _upload_to_supabase(SUPABASE_CASE_BUCKET, storage_key, content, docx_media)
            storage_path = f"supabase://{SUPABASE_CASE_BUCKET}/{storage_key}"
        else:
            from app.services.storage import CASE_STORAGE
            local_dir = CASE_STORAGE / "minutas" / f"notary_{notary_id}"
            local_dir.mkdir(parents=True, exist_ok=True)
            local_file = local_dir / storage_filename
            local_file.write_bytes(content)
            storage_path = str(local_file)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al guardar la minuta en storage: {exc}",
        )

    # 5. Generar token firmado y ruta al editor
    file_token = _make_file_token(storage_path, storage_filename, display_name, notary_id)
    onlyoffice_path = f"/dashboard/minutas/editor/{file_token}"

    return {
        "case_id": None,
        "document_id": None,
        "version_id": None,
        "filename": display_name,
        "onlyoffice_path": onlyoffice_path,
    }


# ─── GET /onlyoffice-config ───────────────────────────────────────────────────

@router.get("/onlyoffice-config")
def minuta_onlyoffice_config(
    request: Request,
    token: str = Query(...),
    current_user: User = Depends(get_current_user),
):
    """Genera la configuración para inicializar el editor OnlyOffice de la minuta."""
    payload = _decode_file_token(token)
    filename = payload.get("display_name") or payload.get("filename", "minuta.docx")

    base_url = _resolve_public_api_base(request)
    doc_key = f"minuta-{payload['filename'].replace('.docx', '')}"

    file_url = f"{base_url}/api/v1/minuta/onlyoffice/file?token={token}"
    callback_url = f"{base_url}/api/v1/minuta/onlyoffice/callback?token={token}"

    config: dict = {
        "document": {
            "fileType": "docx",
            "key": doc_key,
            "title": filename,
            "url": file_url,
        },
        "documentType": "word",
        "editorConfig": {
            "callbackUrl": callback_url,
            "mode": "edit",
            "lang": "es",
            "user": {
                "id": str(current_user.id),
                "name": current_user.full_name or current_user.email,
            },
        },
    }

    secret = (get_settings().onlyoffice_jwt_secret or "").strip()
    if secret:
        config["token"] = jwt.encode(config, secret, algorithm="HS256")

    return config


# ─── GET /onlyoffice/file ─────────────────────────────────────────────────────

@router.get("/onlyoffice/file")
def minuta_onlyoffice_file(token: str = Query(...)):
    """Sirve el .docx al Document Server de OnlyOffice."""
    payload = _decode_file_token(token)
    storage_path = payload["storage_path"]
    filename = payload.get("display_name") or payload.get("filename", "minuta.docx")

    try:
        content = download_storage_bytes(storage_path)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo de minuta no disponible.",
        ) from exc

    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(content)),
            "Cache-Control": "no-store",
        },
    )


# ─── POST /onlyoffice/callback ────────────────────────────────────────────────

@router.post("/onlyoffice/callback")
async def minuta_onlyoffice_callback(
    request: Request,
    token: str = Query(...),
):
    """
    Recibe el callback de OnlyOffice cuando el usuario guarda el documento.
    Sobreescribe el archivo en Storage con la versión editada.
    """
    payload = _decode_file_token(token)
    storage_path = payload["storage_path"]

    body = await request.json()
    oo_status = int(body.get("status", 0))

    # 1=editing, 2=ready to save, 3=corrupted, 4=closed no changes,
    # 6=error force-saved, 7=force saved
    if oo_status not in (2, 6, 7):
        return {"error": 0}

    url = body.get("url")
    if not url:
        return {"error": 0}

    import requests as _req
    try:
        resp = _req.get(url, timeout=60)
        resp.raise_for_status()
    except Exception:
        return {"error": 0}

    try:
        docx_media = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        if storage_path.startswith("supabase://"):
            bucket, key = parse_supabase_storage_path(storage_path)
            _upload_to_supabase(bucket, key, resp.content, docx_media)
        else:
            Path(storage_path).write_bytes(resp.content)
    except Exception:
        pass

    return {"error": 0}
