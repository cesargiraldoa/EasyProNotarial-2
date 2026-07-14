from __future__ import annotations

import re
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from pydantic import BaseModel, ConfigDict
import sqlalchemy as sa
from sqlalchemy import case, or_
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import get_current_user, get_db
from app.models.notarial_field_catalog import NotarialFieldCatalog
from app.models.user import User
from app.services.minuta.detector import analizar_documento


router = APIRouter(prefix="/biblioteca", tags=["biblioteca"])


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
        conditions.append("(scope = 'global' AND notary_id IS NULL) OR (scope = 'notary' AND notary_id = :notary_id)")
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
