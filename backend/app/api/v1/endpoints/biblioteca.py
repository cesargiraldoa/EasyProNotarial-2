from __future__ import annotations

import re
import hashlib
import json
import logging
import tempfile
import time
from pathlib import Path
from typing import Annotated, Literal

from fastapi import APIRouter, Body, Depends, File, HTTPException, Query, UploadFile, status
from pydantic import BaseModel, ConfigDict, Field
import sqlalchemy as sa
from sqlalchemy import case, or_
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import get_current_user, get_db, get_manageable_notary_ids, get_role_codes
from app.models.case import Case
from app.models.case_document import CaseDocument
from app.models.case_document_version import CaseDocumentVersion
from app.models.notarial_field_catalog import NotarialFieldCatalog
from app.models.user import User
from app.modules.minuta.router import _decode_file_token
from app.services.biblioteca_motor.analysis import OpenAIBibliotecaClassifier, analyze_biblioteca_document
from app.services.biblioteca_motor.review_document import cascade_field_controls_in_docx, prepare_review_document
from app.services.document_persistence import persist_case_document_version
from app.services.minuta.detector import analizar_documento
from app.services.storage import download_storage_bytes


router = APIRouter(prefix="/biblioteca", tags=["biblioteca"])
logger = logging.getLogger(__name__)


class FieldCatalogItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    label: str
    field_type: str
    category: str
    description: str | None = None
    options_json: str | None = None
    scope: str
    notary_id: int | None = None


class SugerenciaCampo(BaseModel):
    texto_original: str
    campo_sugerido: str
    categoria: str
    confianza: float
    metodo: str
    ocurrencias: int


class AnalizarDocumentoResponse(BaseModel):
    modo_detectado: str
    sugerencias: list[SugerenciaCampo]
    texto_original: str
    costo_usd: float


class CaseDocumentContext(BaseModel):
    kind: Literal["case_document"]
    case_id: int
    document_id: int
    version_id: int


class MinutaDocumentContext(BaseModel):
    kind: Literal["minuta"]
    editor_token: str


AnalyzeActualRequest = Annotated[CaseDocumentContext | MinutaDocumentContext, Field(discriminator="kind")]


class AnalyzeActualResponse(BaseModel):
    analysis_id: str
    document: dict
    mode: str
    status: str
    suggestions: list[dict]
    stats: dict
    diagnostics: dict | None = None
    timing: dict | None = None


class AnalyzeAndPrepareResponse(BaseModel):
    analysis_id: str
    review_document: dict
    groups: list[dict]
    stats: dict
    diagnostics: dict | None = None
    timing: dict | None = None


class CascadeBackendRequest(BaseModel):
    document_context: AnalyzeActualRequest
    field_instance_id: str
    value: str


class CascadeBackendResponse(BaseModel):
    review_document: dict
    updated_controls: int


@router.get("/campos", response_model=list[FieldCatalogItem])
def list_field_catalog(
    category: str | None = Query(default=None),
    scope: str | None = Query(default=None),
    search: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notary_id = current_user.default_notary_id
    # Construir SQL nativo para evitar bugs de ORM con IS NULL en OR
    conditions = ["is_active = true"]
    params: dict = {}

    if notary_id is None:
        conditions.append("scope = 'global' AND notary_id IS NULL")
    else:
        conditions.append("((scope = 'global' AND notary_id IS NULL) OR (scope = 'notary' AND notary_id = :notary_id))")
        params["notary_id"] = notary_id

    if category:
        conditions.append("category = :category")
        params["category"] = category.strip()
    if scope:
        conditions.append("scope = :scope")
        params["scope"] = scope.strip()
    if search:
        conditions.append("(code ILIKE :search OR label ILIKE :search)")
        params["search"] = f"%{search.strip()}%"

    where = " AND ".join(conditions)
    sql = sa.text(f"""
        SELECT * FROM notarial_field_catalog
        WHERE {where}
        ORDER BY CASE WHEN scope = 'global' THEN 0 ELSE 1 END,
                 category ASC, code ASC
    """)

    rows = db.execute(sql, params).mappings().all()
    return [NotarialFieldCatalog(**dict(row)) for row in rows]


@router.post("/analizar", response_model=AnalizarDocumentoResponse)
async def analizar_documento_biblioteca(
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Recibe un .docx, detecta campos variables y devuelve sugerencias
    para el plugin de OnlyOffice del Motor de Biblioteca.
    """
    if not archivo.filename or not archivo.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=422, detail="El archivo debe ser un .docx válido.")

    settings = get_settings()
    api_key = settings.openai_api_key
    if not api_key:
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY no configurada.")

    suffix = Path(archivo.filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await archivo.read())
        tmp_path = tmp.name

    try:
        resultado = analizar_documento(tmp_path, api_key)
    except Exception as exc:
        Path(tmp_path).unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Error al analizar el documento: {exc}")
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    sugerencias = _build_sugerencias(resultado)

    return AnalizarDocumentoResponse(
        modo_detectado=resultado.get("modo_detectado", "B2"),
        sugerencias=sugerencias,
        texto_original=resultado.get("texto_original", ""),
        costo_usd=resultado.get("costo_usd", 0.0),
    )


def _build_sugerencias(resultado: dict) -> list[SugerenciaCampo]:
    """
    Transforma el output estructurado del detector en lista de sugerencias
    para el plugin de OnlyOffice.
    """
    datos = resultado.get("datos", {})
    texto = resultado.get("texto_original", "")
    sugerencias: list[SugerenciaCampo] = []
    vistos: set[str] = set()

    def _contar(valor: str) -> int:
        if not valor or not texto:
            return 0
        return len(re.findall(re.escape(valor), texto, re.IGNORECASE))

    def _agregar(texto_original: str, campo: str, categoria: str, confianza: float, metodo: str):
        if not texto_original or not campo:
            return
        key = texto_original.upper().strip()
        if key in vistos:
            return
        vistos.add(key)
        ocurrencias = _contar(texto_original)
        if ocurrencias == 0:
            return
        sugerencias.append(SugerenciaCampo(
            texto_original=texto_original,
            campo_sugerido=campo,
            categoria=categoria,
            confianza=confianza,
            metodo=metodo,
            ocurrencias=ocurrencias,
        ))

    for i, persona in enumerate(datos.get("personas", []) or [], start=1):
        rol = (persona.get("rol") or f"persona_{i}").upper()
        nombre = persona.get("nombre_completo")
        cedula = persona.get("numero_documento")
        if nombre:
            _agregar(nombre, rol, "persona", 0.92, "ia")
        if cedula:
            campo_cedula = f"CEDULA_{rol}"
            _agregar(cedula, campo_cedula, "persona", 0.95, "deterministico")

    for valor in datos.get("valores", []) or []:
        texto_val = valor.get("texto_en_documento")
        tipo = (valor.get("tipo") or "valor").upper()
        if texto_val:
            _agregar(texto_val, tipo, "valor", 0.97, "deterministico")

    inmueble = datos.get("inmueble") or {}
    mapeo_inmueble = {
        "matricula_inmobiliaria": ("MATRICULA_INMOBILIARIA", 0.98),
        "municipio": ("MUNICIPIO_INMUEBLE", 0.95),
        "departamento": ("DEPARTAMENTO_INMUEBLE", 0.95),
        "direccion": ("DIRECCION_INMUEBLE", 0.90),
        "numero": ("NUMERO_INMUEBLE", 0.88),
        "conjunto_o_edificio": ("CONJUNTO_EDIFICIO", 0.90),
        "cedula_catastral": ("CEDULA_CATASTRAL", 0.97),
        "area_construida": ("AREA_CONSTRUIDA", 0.92),
        "piso": ("PISO_INMUEBLE", 0.88),
        "linderos": ("LINDEROS", 0.85),
    }
    for campo_bd, (campo_canonico, conf) in mapeo_inmueble.items():
        valor = inmueble.get(campo_bd)
        if valor:
            _agregar(str(valor), campo_canonico, "inmueble", conf, "deterministico")

    notaria = datos.get("notaria") or {}
    if notaria.get("numero_escritura") and notaria["numero_escritura"] != "PENDIENTE":
        _agregar(notaria["numero_escritura"], "NUMERO_ESCRITURA", "notaria", 0.95, "deterministico")
    if notaria.get("nombre_notaria"):
        _agregar(notaria["nombre_notaria"], "NOMBRE_NOTARIA", "notaria", 0.90, "ia")
    if notaria.get("municipio_notaria"):
        _agregar(notaria["municipio_notaria"], "MUNICIPIO_NOTARIA", "notaria", 0.90, "ia")

    fechas = datos.get("fechas") or {}
    if fechas.get("fecha_otorgamiento"):
        _agregar(fechas["fecha_otorgamiento"], "FECHA_ESCRITURA", "fecha", 0.90, "ia")

    sugerencias.sort(key=lambda s: (-s.confianza, 0 if s.metodo == "deterministico" else 1))
    return sugerencias


@router.post("/analizar-actual", response_model=AnalyzeActualResponse)
def analizar_documento_actual(
    payload: AnalyzeActualRequest = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    storage_path, document_info = _resolve_current_document(payload, db, current_user)
    download_started = time.perf_counter()
    try:
        docx_bytes = download_storage_bytes(storage_path)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento no disponible.") from exc
    download_ms = max(0, int((time.perf_counter() - download_started) * 1000))

    fields = _field_catalog_for_user(db, current_user)
    settings = get_settings()
    classifier = OpenAIBibliotecaClassifier(settings.openai_api_key) if settings.openai_api_key else None
    result = analyze_biblioteca_document(docx_bytes, fields, ai_classifier=classifier)
    result["timing"]["download_ms"] = download_ms
    result["timing"]["total_ms"] = int(result["timing"].get("total_ms", 0)) + download_ms
    result["document"] = {**document_info, "sha256": hashlib.sha256(docx_bytes).hexdigest()}
    logger.info(
        "biblioteca analysis completed analysis_id=%s kind=%s candidates=%s suggestions=%s ai_status=%s total_ms=%s",
        result["analysis_id"],
        document_info.get("kind"),
        result["stats"].get("deterministic_candidates"),
        result["stats"].get("suggestions"),
        (result.get("diagnostics") or {}).get("ai", {}).get("status"),
        result["timing"].get("total_ms"),
    )
    return result


@router.post("/analizar-y-preparar", response_model=AnalyzeAndPrepareResponse)
def analizar_y_preparar_documento(
    payload: AnalyzeActualRequest = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.kind != "case_document":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La version de revision requiere un documento de caso versionado.",
        )
    case_obj, document_obj, version_obj = _resolve_case_document_objects(payload, db, current_user)
    download_started = time.perf_counter()
    try:
        docx_bytes = download_storage_bytes(version_obj.storage_path)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento no disponible.") from exc
    download_ms = max(0, int((time.perf_counter() - download_started) * 1000))

    fields = _field_catalog_for_user(db, current_user)
    settings = get_settings()
    classifier = OpenAIBibliotecaClassifier(settings.openai_api_key) if settings.openai_api_key else None
    result = analyze_biblioteca_document(docx_bytes, fields, ai_classifier=classifier)
    result["timing"]["download_ms"] = download_ms
    result["timing"]["total_ms"] = int(result["timing"].get("total_ms", 0)) + download_ms

    review_started = time.perf_counter()
    try:
        review = prepare_review_document(docx_bytes, result.get("suggestions") or [], analysis_id=result["analysis_id"])
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="No fue posible preparar el documento de revision.") from exc
    review_ms = max(0, int((time.perf_counter() - review_started) * 1000))

    stats = {
        **(result.get("stats") or {}),
        "groups": len(review.groups),
        "wrapped_suggestions": review.wrapped_count,
        "skipped_suggestions": len(review.skipped),
    }
    diagnostics = {
        **(result.get("diagnostics") or {}),
        "review": {"wrapped": review.wrapped_count, "skipped": len(review.skipped)},
    }
    snapshot = {
        "biblioteca_review": {
            "analysis_id": result["analysis_id"],
            "source_version_id": version_obj.id,
            "groups": review.groups,
            "stats": stats,
        },
    }
    new_version = persist_case_document_version(
        db,
        case_obj,
        document_obj.category,
        document_obj.title,
        version_obj.file_format or "docx",
        review.docx_bytes,
        version_obj.original_filename or f"{document_obj.title}.docx",
        getattr(current_user, "id", None),
        version_obj.generated_from_template_id,
        placeholder_snapshot_json=json.dumps(snapshot, ensure_ascii=False),
    )
    db.commit()
    db.refresh(new_version)

    timing = {
        **(result.get("timing") or {}),
        "review_ms": review_ms,
        "total_ms": int((result.get("timing") or {}).get("total_ms") or 0) + review_ms,
    }
    logger.info(
        "biblioteca review prepared analysis_id=%s kind=case_document candidates=%s suggestions=%s groups=%s wrapped=%s ai_status=%s total_ms=%s",
        result["analysis_id"],
        stats.get("deterministic_candidates"),
        stats.get("suggestions"),
        stats.get("groups"),
        stats.get("wrapped_suggestions"),
        (diagnostics.get("ai") or {}).get("status"),
        timing.get("total_ms"),
    )

    return {
        "analysis_id": result["analysis_id"],
        "review_document": {
            "kind": "case_document",
            "case_id": case_obj.id,
            "document_id": document_obj.id,
            "version_id": new_version.id,
        },
        "groups": review.groups,
        "stats": stats,
        "diagnostics": diagnostics,
        "timing": timing,
    }


@router.post("/actualizar-campo", response_model=CascadeBackendResponse)
def actualizar_campo_backend(
    payload: CascadeBackendRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.document_context.kind != "case_document":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La cascada backend requiere un documento de caso versionado.",
        )
    case_obj, document_obj, version_obj = _resolve_case_document_objects(payload.document_context, db, current_user)
    try:
        docx_bytes = download_storage_bytes(version_obj.storage_path)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento no disponible.") from exc
    updated_docx, updated_controls = cascade_field_controls_in_docx(docx_bytes, payload.field_instance_id, payload.value)
    new_version = persist_case_document_version(
        db,
        case_obj,
        document_obj.category,
        document_obj.title,
        version_obj.file_format or "docx",
        updated_docx,
        version_obj.original_filename or f"{document_obj.title}.docx",
        getattr(current_user, "id", None),
        version_obj.generated_from_template_id,
        placeholder_snapshot_json=json.dumps(
            {
                "biblioteca_cascade": {
                    "source_version_id": version_obj.id,
                    "field_instance_id": payload.field_instance_id,
                    "updated_controls": updated_controls,
                },
            },
            ensure_ascii=False,
        ),
    )
    db.commit()
    db.refresh(new_version)
    return {
        "review_document": {
            "kind": "case_document",
            "case_id": case_obj.id,
            "document_id": document_obj.id,
            "version_id": new_version.id,
        },
        "updated_controls": updated_controls,
    }


def _resolve_current_document(
    payload: CaseDocumentContext | MinutaDocumentContext,
    db: Session,
    current_user: User,
) -> tuple[str, dict]:
    if payload.kind == "case_document":
        return _resolve_case_document(payload, db, current_user)
    return _resolve_minuta_document(payload, current_user)


def _resolve_case_document(
    payload: CaseDocumentContext,
    db: Session,
    current_user: User,
) -> tuple[str, dict]:
    row = (
        db.query(CaseDocumentVersion, Case.notary_id)
        .join(CaseDocument, CaseDocumentVersion.case_document_id == CaseDocument.id)
        .join(Case, CaseDocument.case_id == Case.id)
        .filter(
            Case.id == payload.case_id,
            CaseDocument.id == payload.document_id,
            CaseDocumentVersion.id == payload.version_id,
        )
        .first()
    )
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento no encontrado.")
    version, notary_id = row
    if not _user_can_access_notary(current_user, notary_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento no encontrado.")
    return version.storage_path, {
        "kind": "case_document",
        "case_id": payload.case_id,
        "document_id": payload.document_id,
        "version_id": payload.version_id,
    }


def _resolve_case_document_objects(
    payload: CaseDocumentContext,
    db: Session,
    current_user: User,
) -> tuple[Case, CaseDocument, CaseDocumentVersion]:
    row = (
        db.query(Case, CaseDocument, CaseDocumentVersion)
        .join(CaseDocument, CaseDocument.case_id == Case.id)
        .join(CaseDocumentVersion, CaseDocumentVersion.case_document_id == CaseDocument.id)
        .filter(
            Case.id == payload.case_id,
            CaseDocument.id == payload.document_id,
            CaseDocumentVersion.id == payload.version_id,
        )
        .first()
    )
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento no encontrado.")
    case_obj, document_obj, version_obj = row
    if not _user_can_access_notary(current_user, case_obj.notary_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento no encontrado.")
    return case_obj, document_obj, version_obj


def _resolve_minuta_document(
    payload: MinutaDocumentContext,
    current_user: User,
) -> tuple[str, dict]:
    token_payload = _decode_file_token(payload.editor_token)

    notary_id = token_payload.get("notary_id")
    if not isinstance(notary_id, int) or not _user_can_access_notary(current_user, notary_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento no encontrado.")
    storage_path = str(token_payload.get("storage_path") or "").strip()
    if not storage_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento no encontrado.")
    return storage_path, {"kind": "minuta"}


def _user_can_access_notary(current_user: User, notary_id: int | None) -> bool:
    if notary_id is None:
        return False
    role_codes = get_role_codes(current_user)
    if "super_admin" in role_codes:
        return True
    return notary_id in get_manageable_notary_ids(current_user)


def _field_catalog_for_user(db: Session, current_user: User) -> list[NotarialFieldCatalog]:
    notary_id = current_user.default_notary_id
    query = db.query(NotarialFieldCatalog).filter(NotarialFieldCatalog.is_active.is_(True))
    if notary_id is None:
        query = query.filter(NotarialFieldCatalog.scope == "global", NotarialFieldCatalog.notary_id.is_(None))
    else:
        query = query.filter(
            or_(
                sa.and_(NotarialFieldCatalog.scope == "global", NotarialFieldCatalog.notary_id.is_(None)),
                sa.and_(NotarialFieldCatalog.scope == "notary", NotarialFieldCatalog.notary_id == notary_id),
            ),
        )
    return query.order_by(
        case((NotarialFieldCatalog.scope == "global", 0), else_=1),
        NotarialFieldCatalog.category.asc(),
        NotarialFieldCatalog.code.asc(),
    ).all()
