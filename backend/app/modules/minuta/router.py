import json
import logging
import re
import tempfile
import traceback
import uuid as _uuid
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote

logger = logging.getLogger(__name__)

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Query, Request, UploadFile, status
from fastapi.responses import Response
from jose import jwt
import requests as _req
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import get_current_user, get_db
from app.models.case import Case
from app.models.case_document import CaseDocument
from app.models.case_document_version import CaseDocumentVersion
from app.models.user import User
from app.services.minuta.detector import analizar_documento, extraer_texto_estructurado
from app.services.minuta.validador import validar_documento
from app.services.minuta.reemplazador import aplicar_genero_contextual_docx, aplicar_reemplazos_docx, construir_lista_reemplazos
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
)
from app.services.document_persistence import persist_case_document_version
from app.services.minuta.marked_template_state import (
    detect_marked_template_from_bytes,
    merge_marked_template_state,
    safe_marked_template_snapshot,
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


def _make_file_token(
    storage_path: str,
    filename: str,
    display_name: str,
    notary_id: int,
    *,
    case_id: int | None = None,
    document_id: int | None = None,
    version_id: int | None = None,
    user_id: int | None = None,
) -> str:
    payload = {
        "storage_path": storage_path,
        "filename": filename,
        "display_name": display_name,
        "notary_id": notary_id,
        "exp": datetime.utcnow() + timedelta(hours=24),
    }
    if case_id is not None and document_id is not None and version_id is not None:
        payload.update(
            {
                "case_id": int(case_id),
                "document_id": int(document_id),
                "version_id": int(version_id),
                "user_id": int(user_id) if user_id is not None else None,
            }
        )
    return jwt.encode(
        payload,
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


def _build_minuta_document_key(payload: dict) -> str:
    return f"minuta-{payload['filename'].replace('.docx', '')}"


def _user_can_access_notary(current_user: User, notary_id: int | None) -> bool:
    if notary_id is None:
        return True
    if getattr(current_user, "default_notary_id", None) == notary_id:
        return True
    for assignment in getattr(current_user, "role_assignments", []) or []:
        assignment_notary_id = getattr(assignment, "notary_id", None)
        role = getattr(assignment, "role", None)
        role_code = getattr(role, "code", None)
        if role_code in {"super_admin", "admin_notary"} and assignment_notary_id is None:
            return True
        if assignment_notary_id == notary_id:
            return True
    return False


def _validate_minuta_token_access(payload: dict, current_user: User, db: Session) -> None:
    notary_id = payload.get("notary_id")
    case_id = payload.get("case_id")
    if case_id is not None:
        case_obj = db.query(Case).filter(Case.id == case_id).first()
        if case_obj is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado para esta minuta.")
        if notary_id is not None and case_obj.notary_id != notary_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado para esta minuta.")
        notary_id = case_obj.notary_id
    if not _user_can_access_notary(current_user, notary_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado para esta minuta.")


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

    # Capa 2 — validación notarial (no bloquea si falla)
    try:
        actos = resultado.get("datos", {}).get("actos", [])
        datos = resultado.get("datos", {})
        resultado["validacion"] = validar_documento(datos, actos, api_key)
    except Exception as e:
        resultado["validacion"] = {"error": str(e)}

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
        # ── Parse JSON ──────────────────────────────────────────────────────────
        try:
            datos_ant = json.loads(datos_anteriores)
            datos_nv = json.loads(datos_nuevos)
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"JSON inválido en datos_anteriores o datos_nuevos: {exc}",
            )

        api_key = _get_api_key()

        # ── Archivos temporales ──────────────────────────────────────────────────
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_in:
            tmp_in.write(await archivo.read())
            path_entrada = tmp_in.name

        tmp_out = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
        path_salida = tmp_out.name
        tmp_out.close()

        # ── 1. Reemplazos de datos (nombres, documentos, valores, inmueble) ─────
        reemplazos = construir_lista_reemplazos(datos_ant, datos_nv)

        # ── 2. Concordancia de género ────────────────────────────────────────────
        texto_doc = extraer_texto_estructurado(path_entrada)
        personas_viejas = {(p.get("rol") or p.get("ROL") or ""): p for p in datos_ant.get("personas", [])}
        personas_nuevas = {(p.get("rol") or p.get("ROL") or ""): p for p in datos_nv.get("personas", [])}

        cambios_conc_todos: list[dict] = []
        for rol, persona_nueva in personas_nuevas.items():
            persona_vieja = personas_viejas.get(rol, {})
            if necesita_concordancia(persona_vieja, persona_nueva):
                nombre_cambiando = (persona_nueva.get("nombre_completo") or "").strip().upper()
                personas_resto = [
                    {
                        "nombre": p.get("nombre_completo") or "",
                        "genero": p.get("genero") or "",
                    }
                    for p in datos_nv.get("personas", [])
                    if (p.get("nombre_completo") or "").strip().upper() != nombre_cambiando
                    and p.get("nombre_completo")
                ]
                try:
                    resultado_conc = detectar_concordancia(
                        texto_doc, persona_vieja, persona_nueva, api_key,
                        personas_resto=personas_resto,
                    )
                except Exception as e_conc:
                    print(f"[concordancia] Error — saltando: {e_conc}")
                    resultado_conc = {"cambios": []}
                cambios_conc_todos.extend(resultado_conc.get("cambios", []))

        if cambios_conc_todos:
            reemplazos.extend(aplicar_cambios_concordancia_a_reemplazos(cambios_conc_todos))

        # ── 3. Preparar reemplazos de género por persona (se aplican después, con contexto)
        _GENERO_M_A_F = [
            {"viejo": "varón",        "nuevo": "mujer",       "etiqueta": "genero.varon",          "palabra_completa": True},
            {"viejo": "VARÓN",        "nuevo": "MUJER",       "etiqueta": "genero.VARON",          "palabra_completa": True},
            {"viejo": "varon",        "nuevo": "mujer",       "etiqueta": "genero.varon_sin_tilde","palabra_completa": True},
            {"viejo": "soltero",      "nuevo": "soltera",     "etiqueta": "genero.soltero",        "palabra_completa": True},
            {"viejo": "SOLTERO",      "nuevo": "SOLTERA",     "etiqueta": "genero.SOLTERO",        "palabra_completa": True},
            {"viejo": "colombiano",   "nuevo": "colombiana",  "etiqueta": "genero.colombiano",     "palabra_completa": True},
            {"viejo": "COLOMBIANO",   "nuevo": "COLOMBIANA",  "etiqueta": "genero.COLOMBIANO",     "palabra_completa": True},
            {"viejo": "domiciliado",  "nuevo": "domiciliada", "etiqueta": "genero.domiciliado",    "palabra_completa": True},
            {"viejo": "DOMICILIADO",  "nuevo": "DOMICILIADA", "etiqueta": "genero.DOMICILIADO",   "palabra_completa": True},
            {"viejo": "identificado", "nuevo": "identificada","etiqueta": "genero.identificado",   "palabra_completa": True},
            {"viejo": "IDENTIFICADO", "nuevo": "IDENTIFICADA","etiqueta": "genero.IDENTIFICADO",  "palabra_completa": True},
        ]
        _GENERO_F_A_M = [
            {"viejo": "mujer",        "nuevo": "varón",       "etiqueta": "genero.mujer",          "palabra_completa": True},
            {"viejo": "MUJER",        "nuevo": "VARÓN",       "etiqueta": "genero.MUJER",          "palabra_completa": True},
            {"viejo": "soltera",      "nuevo": "soltero",     "etiqueta": "genero.soltera",        "palabra_completa": True},
            {"viejo": "colombiana",   "nuevo": "colombiano",  "etiqueta": "genero.colombiana",     "palabra_completa": True},
            {"viejo": "domiciliada",  "nuevo": "domiciliado", "etiqueta": "genero.domiciliada",    "palabra_completa": True},
            {"viejo": "identificada", "nuevo": "identificado","etiqueta": "genero.identificada",   "palabra_completa": True},
        ]
        todos_nombres_doc = list({
            (p.get("nombre_completo") or p.get("NOMBRE_COMPLETO") or "").strip()
            for lista in [datos_ant.get("personas", []), datos_nv.get("personas", [])]
            for p in lista
            if (p.get("nombre_completo") or p.get("NOMBRE_COMPLETO") or "").strip()
        })

        # Enriquecer con secuencias MAYÚSCULAS encontradas en párrafos del documento
        # que contengan algún nombre ya conocido. Rescata personas que el detector
        # no detectó (ej. SEBASTIÁN cuando el análisis solo devolvió a DANIELA).
        # Solo se scanean párrafos relevantes para evitar falsos positivos globales.
        _RE_MAYUS = re.compile(r'[A-ZÁÉÍÓÚÜÑ]{3,}(?:\s+[A-ZÁÉÍÓÚÜÑ]{3,})+')
        _PALABRAS_NO_NOMBRE = {
            "PARTE", "COMPRADORA", "COMPRADOR", "VENDEDOR", "VENDEDORA",
            "ACREEDOR", "ACREEDORA", "DEUDOR", "DEUDORA", "HIPOTECANTE",
            "OTORGANTE", "FIDEICOMISO", "BANCO", "NOTARIA", "NOTARIO",
            "CONJUNTO", "MUNICIPIO", "DEPARTAMENTO", "REPÚBLICA", "REPUBLICA",
            "COLOMBIA", "ESCRITURA", "INMUEBLE", "APARTAMENTO", "OFICINA",
        }
        _ya_conocidos = {n.upper() for n in todos_nombres_doc}
        for _linea in texto_doc.split("\n"):
            for _m in _RE_MAYUS.finditer(_linea):
                _candidato = _m.group(0)
                palabras = _candidato.split()
                if not (2 <= len(palabras) <= 5):
                    continue
                if any(p in _PALABRAS_NO_NOMBRE for p in palabras):
                    continue
                if _candidato.upper() not in _ya_conocidos:
                    todos_nombres_doc.append(_candidato)
                    _ya_conocidos.add(_candidato.upper())

        pares_genero: list[dict] = []
        for rol, persona_nueva in personas_nuevas.items():
            genero_nuevo = persona_nueva.get("genero") or persona_nueva.get("GENERO") or ""
            nombre_nuevo = (persona_nueva.get("nombre_completo") or persona_nueva.get("NOMBRE_COMPLETO") or "").strip()
            if not nombre_nuevo or genero_nuevo not in ("M", "F"):
                continue
            reemplazos_genero = _GENERO_M_A_F if genero_nuevo == "F" else _GENERO_F_A_M
            pares_genero.append({"nombre": nombre_nuevo, "reemplazos": reemplazos_genero, "genero": genero_nuevo})
        pares_genero.sort(key=lambda x: 0 if x.get("genero") == "F" else 1)

        # ── 4. Aplicar reemplazos de datos al .docx ──────────────────────────────
        logger.info(
            "[generar] reemplazos a aplicar (%d total):\n%s",
            len(reemplazos),
            "\n".join(
                f"  [{i+1:02d}] {'[frase]' if ' ' in r.get('viejo','') else '[palabra]'}"
                f" {r.get('etiqueta','?')} | «{r.get('viejo','')}» → «{r.get('nuevo','')}»"
                f"{' [completa]' if r.get('palabra_completa') else ''}"
                for i, r in enumerate(reemplazos)
            ),
        )
        estadisticas = aplicar_reemplazos_docx(path_entrada, reemplazos, path_salida)
        logger.info(
            "[generar] resultado: %d reemplazos efectivos | no_encontrados=%s",
            estadisticas["total_reemplazos"],
            [x["etiqueta"] for x in estadisticas.get("no_encontrados", [])],
        )

        Path(path_entrada).unlink(missing_ok=True)

        # ── 5. Reemplazos de género contextual (solo en párrafos de cada persona) ─
        if pares_genero:
            stats_genero = aplicar_genero_contextual_docx(path_salida, pares_genero, todos_nombres=todos_nombres_doc)
            logger.info("[generar] género contextual: %s", stats_genero)

        # ── 6. Leer bytes y subir a Supabase Storage ─────────────────────────────
        content = Path(path_salida).read_bytes()
        background_tasks.add_task(Path(path_salida).unlink, True)

        notary_id = current_user.default_notary_id or 0
        file_uuid = str(_uuid.uuid4())
        storage_filename = f"{file_uuid}_minuta.docx"
        original_stem = Path(archivo.filename).stem if archivo.filename else "minuta"
        display_name = f"minuta_generada_{original_stem}.docx"
        storage_key = f"minutas/notary_{notary_id}/{storage_filename}"
        docx_media = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

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

        # 7. Generar token firmado y rutas
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
            "estadisticas": estadisticas,
        }

    except HTTPException:
        raise
    except Exception as e:
        print("=== ERROR DETALLADO ===")
        print(traceback.format_exc())
        print("======================")
        raise HTTPException(status_code=500, detail=str(e))


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
    doc_key = _build_minuta_document_key(payload)

    file_url = f"{base_url}/api/v1/minuta/onlyoffice/file?token={token}"
    callback_url = f"{base_url}/api/v1/minuta/onlyoffice/callback?token={token}"

    config: dict = {
        "document": {
            "fileType": "docx",
            "key": doc_key,
            "title": filename,
            "url": file_url,
            "permissions": {
                "download": False,
                "print": True,
                "edit": True,
                "review": True,
                "comment": True,
            },
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
            "customization": {
                "plugins": True,
            },
        },
        "customization": {
            "plugins": True,
        },
    }

    secret = (get_settings().onlyoffice_jwt_secret or "").strip()
    if secret:
        config["token"] = jwt.encode(config, secret, algorithm="HS256")

    return config


# ─── POST /onlyoffice/forcesave ───────────────────────────────────────────────

@router.post("/onlyoffice/forcesave")
def minuta_onlyoffice_forcesave(
    token: str = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    payload = _decode_file_token(token)
    _validate_minuta_token_access(payload, current_user, db)

    document_key = _build_minuta_document_key(payload)
    command_payload: dict = {
        "c": "forcesave",
        "key": document_key,
        "userdata": "easypro-marked-template-save",
    }
    secret = (get_settings().onlyoffice_jwt_secret or "").strip()
    if secret:
        command_payload["token"] = jwt.encode(command_payload.copy(), secret, algorithm="HS256")

    command_url = (
        get_settings().onlyoffice_documentserver_url.rstrip("/")
        + "/command?shardkey="
        + quote(document_key, safe="")
    )
    log_context = {
        "key": document_key,
        "case_id": payload.get("case_id"),
        "document_id": payload.get("document_id"),
        "version_id": payload.get("version_id"),
    }
    logger.info("minuta onlyoffice forcesave requested", extra=log_context)

    try:
        response = _req.post(command_url, json=command_payload, timeout=20)
        result = response.json()
    except Exception as exc:
        logger.exception("minuta onlyoffice forcesave command failed", extra=log_context)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="OnlyOffice no respondió con JSON válido al solicitar guardado.",
        ) from exc

    if not isinstance(result, dict):
        logger.warning("minuta onlyoffice forcesave returned non-object json", extra=log_context)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="OnlyOffice devolvió una respuesta inválida al solicitar guardado.",
        )

    error_code = result.get("error")
    try:
        error_code = int(error_code)
    except (TypeError, ValueError):
        logger.warning("minuta onlyoffice forcesave returned invalid error code", extra=log_context)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="OnlyOffice devolvió un código inválido al solicitar guardado.",
        )

    if error_code == 0:
        return {"ok": True, "status": "requested", "onlyoffice_error": 0}
    if error_code == 4:
        return {
            "ok": True,
            "status": "no_changes",
            "onlyoffice_error": 4,
            "detail": "OnlyOffice no tenía cambios pendientes para guardar.",
        }

    logger.warning("minuta onlyoffice forcesave rejected", extra={**log_context, "onlyoffice_error": error_code})
    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail={
            "message": "OnlyOffice no pudo iniciar el guardado forzado.",
            "onlyoffice_error": error_code,
        },
    )


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
    db: Session = Depends(get_db),
):
    """
    Recibe el callback de OnlyOffice cuando el usuario guarda el documento.
    Sobreescribe el archivo en Storage con la versión editada.
    """
    payload = _decode_file_token(token)
    storage_path = payload["storage_path"]
    callback_context = {
        "case_id": payload.get("case_id"),
        "document_id": payload.get("document_id"),
        "version_id": payload.get("version_id"),
    }

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
        db.rollback()
        logger.exception("minuta onlyoffice callback download failed", extra=callback_context)
        return {"error": 0}

    try:
        persisted_as_version = _persist_marked_template_callback_version(db, payload, resp.content)
        if persisted_as_version:
            return {"error": 0}

        docx_media = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        if storage_path.startswith("supabase://"):
            bucket, key = parse_supabase_storage_path(storage_path)
            _upload_to_supabase(bucket, key, resp.content, docx_media)
        else:
            Path(storage_path).write_bytes(resp.content)
    except Exception:
        db.rollback()
        logger.exception("minuta onlyoffice callback persistence failed", extra=callback_context)

    return {"error": 0}


def _persist_marked_template_callback_version(db: Session, payload: dict, content: bytes) -> bool:
    case_id = payload.get("case_id")
    document_id = payload.get("document_id")
    version_id = payload.get("version_id")
    if not all(isinstance(value, int) for value in (case_id, document_id, version_id)):
        return False

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
        logger.warning("marked template callback ignored: source version not found")
        return True

    case_obj, document_obj, version_obj = row
    if case_obj.notary_id != payload.get("notary_id"):
        logger.warning("marked template callback ignored: notary mismatch")
        return True

    previous_snapshot = safe_marked_template_snapshot(version_obj.placeholder_snapshot_json)
    try:
        detected = detect_marked_template_from_bytes(content)
    except Exception:
        logger.exception("marked template callback marker scan failed")
        detected = {"fields": []}

    snapshot = merge_marked_template_state(
        previous_snapshot,
        detected,
        document_name=document_obj.title or payload.get("display_name") or "Minuta marcada",
    )
    snapshot["onlyoffice_template_edit"] = {
        "source_version_id": version_obj.id,
        "saved_from_onlyoffice": True,
    }

    persist_case_document_version(
        db,
        case_obj,
        document_obj.category,
        document_obj.title,
        version_obj.file_format or "docx",
        content,
        version_obj.original_filename or payload.get("filename") or "minuta.docx",
        payload.get("user_id"),
        version_obj.generated_from_template_id,
        placeholder_snapshot_json=json.dumps(snapshot, ensure_ascii=False),
    )
    db.commit()
    return True

# deploy 2026-05-23
