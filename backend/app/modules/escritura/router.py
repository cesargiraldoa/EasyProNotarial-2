from __future__ import annotations

import json
import re
from dataclasses import asdict
from datetime import date
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user, get_db, get_manageable_notary_ids, get_role_codes, require_roles
from app.models.case import Case
from app.models.case_act_data import CaseActData
from app.models.case_document import CaseDocument
from app.models.case_document_version import CaseDocumentVersion
from app.models.case_state_definition import CaseStateDefinition
from app.models.notary import Notary
from app.models.user import User
from app.schemas.escritura import (
    ActoCode,
    BibliotecaClausulaOut,
    CorpusBusquedaHit,
    CorpusBusquedaResponse,
    CorpusResponse,
    DocumentoIn,
    DocumentoOut,
    EscrituraStateIn,
    EscrituraStateOut,
    GariClasificacionIn,
    GariClasificacionOut,
    GariExtraccionOut,
    GariProsaIn,
    GariProsaOut,
    GariRevisionIn,
    GariRevisionOut,
    LegalClausulaOut,
    LegalNormaOut,
    LegalReglaOut,
    LegalTarifaOut,
    NuevoCasoEscrituraIn,
    NuevoCasoEscrituraOut,
    PlantillaAdminDetailOut,
    PlantillaAdminIn,
    PlantillaAdminItemOut,
    PlantillaSemillaOut,
    PlantillaSemillaTokenOut,
)
from app.services.document_persistence import get_or_create_document, persist_case_document_version
from app.services.escritura_reglas import evaluar_reglas
from app.services.escritura_gari import (
    GariLLMClient,
    clasificar_acto,
    extract_upload_text,
    get_gari_llm_client,
    proponer_campos_desde_texto,
    redactar_prosa,
    revisar_escritura,
)
from app.services.gari_document_service import build_gari_docx_buffer
from app.services.legal_corpus import clausulas_vigentes, normas_vigentes, reglas_vigentes, tarifas_vigentes
from app.services.legal_rag import buscar_corpus
from app.services.plantilla_semilla import (
    get_plantilla_admin,
    list_plantillas_admin,
    resolver_plantilla_semilla,
    upsert_plantilla_admin,
)

router = APIRouter(prefix="/escritura", tags=["escritura"])

WRITE_ROLES = (
    "super_admin",
    "admin_notary",
    "protocolist",
    "approver",
    "notary",
    "notary_titular",
    "notary_suplente",
)

BLOCK_TAGS = {"p", "div", "tr", "h4", "h3", "li"}
SKIPPED_SPAN_CLASSES = {"fill", "cite"}
MAPA_SITUACIONES_PATH = Path(__file__).resolve().parents[4] / "docs" / "ecosistema-notarial" / "mapa-situaciones.md"


def _corpus_acto_code(acto: ActoCode) -> str:
    if acto == "cancelacion":
        return "cancelacion_hipoteca"
    return acto


def _case_query(db: Session):
    return (
        db.query(Case)
        .options(
            joinedload(Case.act_data),
            joinedload(Case.documents).joinedload(CaseDocument.versions).joinedload(CaseDocumentVersion.created_by_user),
        )
    )


def load_case_for_user(db: Session, case_id: int, current_user: User) -> Case:
    case = _case_query(db).filter(Case.id == case_id).first()
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caso no encontrado.")

    role_codes = get_role_codes(current_user)
    if "super_admin" not in role_codes and case.notary_id not in get_manageable_notary_ids(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado para este caso.")
    return case


def _parse_state(data_json: str | None) -> dict:
    if not data_json or not data_json.strip():
        return {}
    try:
        parsed = json.loads(data_json)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="data_json del caso no es JSON valido.") from exc
    if not isinstance(parsed, dict):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="data_json del caso debe ser un objeto JSON.")
    return parsed


def _state_date(acto: ActoCode, state: dict) -> date | None:
    raw = state.get("cFechaOtorg") if acto == "cancelacion" else state.get("fechaOtorg")
    if not isinstance(raw, str) or not raw.strip():
        return None
    try:
        return date.fromisoformat(raw.strip())
    except ValueError:
        return None


def _mapa_situaciones_text() -> str:
    try:
        return MAPA_SITUACIONES_PATH.read_text(encoding="utf-8")
    except OSError:
        return ""


def _revision_source_text(case: Case, payload: GariRevisionIn) -> str:
    html = (payload.html or "").strip()
    if html:
        return html
    draft = case.act_data.gari_draft_text if case.act_data else None
    if draft and draft.strip():
        return draft.strip()
    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="No hay texto de escritura para revisar.")


def _serialize_state(case: Case, acto: ActoCode | None = None) -> EscrituraStateOut:
    return EscrituraStateOut(
        case_id=case.id,
        acto=acto,
        state=_parse_state(case.act_data.data_json if case.act_data else "{}"),
        case={
            "id": case.id,
            "notary_id": case.notary_id,
            "case_type": case.case_type,
            "act_type": case.act_type,
            "consecutive": case.consecutive,
            "year": case.year,
            "current_state": case.current_state,
            "internal_case_number": case.internal_case_number,
            "official_deed_number": case.official_deed_number,
            "official_deed_year": case.official_deed_year,
            "updated_at": case.updated_at,
        },
    )


def _filename_for(case: Case, payload: DocumentoIn) -> str:
    raw = (payload.filename or "").strip()
    if not raw:
        raw = f"escritura_{case.internal_case_number or case.id}_{payload.acto}.docx"
    if Path(raw).suffix.lower() != ".docx":
        raw = f"{raw}.docx"
    return raw


def _title_for(payload: DocumentoIn) -> str:
    labels = {
        "compraventa": "Escritura asistida - compraventa",
        "hipoteca": "Escritura asistida - compraventa con hipoteca",
        "cancelacion": "Escritura asistida - cancelacion de hipoteca",
    }
    return labels[payload.acto]


class _StructuredTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self._parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        normalized_tag = tag.lower()
        attr_map = {key.lower(): value or "" for key, value in attrs}
        classes = set(attr_map.get("class", "").split())
        if normalized_tag == "span" and classes.intersection(SKIPPED_SPAN_CLASSES):
            self._skip_depth += 1
            return
        if self._skip_depth:
            return
        if normalized_tag in BLOCK_TAGS or normalized_tag == "br":
            self._newline()

    def handle_endtag(self, tag: str) -> None:
        normalized_tag = tag.lower()
        if self._skip_depth:
            if normalized_tag == "span":
                self._skip_depth -= 1
            return
        if normalized_tag in BLOCK_TAGS:
            self._newline()

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        self._parts.append(data)

    def handle_entityref(self, name: str) -> None:
        if not self._skip_depth:
            self._parts.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        if not self._skip_depth:
            self._parts.append(f"&#{name};")

    def _newline(self) -> None:
        if not self._parts or self._parts[-1] != "\n":
            self._parts.append("\n")

    def text(self) -> str:
        raw = unescape("".join(self._parts)).replace("\xa0", " ")
        raw = re.sub(r"-{2,}", "", raw)
        lines = [re.sub(r"[ \t]+", " ", line).strip() for line in raw.splitlines()]
        return "\n".join(line for line in lines if line)


def html_to_structured_text(html: str) -> str:
    parser = _StructuredTextParser()
    parser.feed(html)
    parser.close()
    text = parser.text()
    if not text:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El HTML no contiene texto de escritura.")
    return text


@router.get("/corpus", response_model=CorpusResponse)
def get_escritura_corpus(
    acto: ActoCode = Query(...),
    fecha: date | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ = current_user
    effective_date = fecha or date.today()
    corpus_acto = _corpus_acto_code(acto)
    return CorpusResponse(
        acto=acto,
        corpus_acto_code=corpus_acto,
        fecha=effective_date,
        normas=[LegalNormaOut.model_validate(item) for item in normas_vigentes(db, corpus_acto, effective_date)],
        clausulas=[LegalClausulaOut.model_validate(item) for item in clausulas_vigentes(db, corpus_acto, effective_date)],
        reglas=[LegalReglaOut.model_validate(item) for item in reglas_vigentes(db, corpus_acto, effective_date)],
        tarifas=[LegalTarifaOut.model_validate(item) for item in tarifas_vigentes(db, corpus_acto, effective_date)],
    )


@router.get("/corpus/buscar", response_model=CorpusBusquedaResponse)
def buscar_escritura_corpus(
    q: str = Query(..., min_length=1),
    acto: ActoCode | None = Query(default=None),
    fecha: date | None = Query(default=None),
    top_k: int = Query(default=5, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ = current_user
    effective_date = fecha or date.today()
    corpus_acto = _corpus_acto_code(acto) if acto else None
    hits = buscar_corpus(db, q, effective_date, acto_code=corpus_acto, top_k=top_k)
    return CorpusBusquedaResponse(
        q=q,
        acto=acto,
        corpus_acto_code=corpus_acto,
        fecha=effective_date,
        hits=[CorpusBusquedaHit(**asdict(hit)) for hit in hits],
    )


@router.get("/biblioteca", response_model=list[BibliotecaClausulaOut])
def get_escritura_biblioteca(
    acto: ActoCode = Query(...),
    fecha: date | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ = current_user
    effective_date = fecha or date.today()
    corpus_acto = _corpus_acto_code(acto)
    return [
        BibliotecaClausulaOut.model_validate(item, from_attributes=True)
        for item in clausulas_vigentes(db, corpus_acto, effective_date)
    ]


@router.post("/cases", response_model=NuevoCasoEscrituraOut, status_code=status.HTTP_201_CREATED)
def crear_caso_escritura(
    payload: NuevoCasoEscrituraIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*WRITE_ROLES)),
):
    """Crea un caso de escritura vacío y devuelve su id para abrir el workspace.

    Es el punto de entrada del flujo acto-primero: no exige subir ningún .docx.
    El acto real se elige en el workspace (ActoLauncher); aquí solo se
    inicializa el caso con la notaría del usuario, estado inicial y consecutivo."""
    acto: ActoCode = payload.acto or "compraventa"

    notary_id = current_user.default_notary_id
    if notary_id is None:
        manageable = sorted(get_manageable_notary_ids(current_user))
        notary_id = manageable[0] if manageable else None
    if notary_id is None:
        first_notary = db.query(Notary.id).order_by(Notary.id.asc()).first()
        notary_id = first_notary[0] if first_notary else None
    if notary_id is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No hay notaría configurada para crear el caso.",
        )

    state_def = (
        db.query(CaseStateDefinition)
        .filter(CaseStateDefinition.case_type == "escritura", CaseStateDefinition.is_active.is_(True))
        .order_by(CaseStateDefinition.step_order.asc())
        .first()
    )
    current_state = state_def.code if state_def else "borrador"

    year = date.today().year
    max_consecutive = (
        db.query(func.max(Case.consecutive))
        .filter(Case.notary_id == notary_id, Case.year == year)
        .scalar()
    )
    consecutive = (max_consecutive or 0) + 1

    case = Case(
        notary_id=notary_id,
        created_by_user_id=current_user.id,
        case_type="escritura",
        act_type=acto,
        consecutive=consecutive,
        year=year,
        current_state=current_state,
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    return NuevoCasoEscrituraOut(case_id=case.id, acto=acto, current_state=current_state, notary_id=notary_id)


@router.get("/plantilla-semilla", response_model=PlantillaSemillaOut)
def get_plantilla_semilla(
    acto: ActoCode = Query(...),
    fuente: str = Query(default="banco"),
    legal_entity_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cuerpo base (plantilla semilla) para elegir acto+fuente+banco.

    Devuelve la plantilla de la entidad; si no existe, cae a la genérica del
    acto (`is_fallback = True`). 404 si el acto no tiene ninguna plantilla."""
    notary_ids = get_manageable_notary_ids(current_user)
    resuelta = resolver_plantilla_semilla(
        db,
        notary_ids=notary_ids,
        act_code=acto,
        fuente=fuente,
        legal_entity_id=legal_entity_id,
    )
    if resuelta is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay plantilla semilla para este acto todavía.",
        )
    return PlantillaSemillaOut(
        id=resuelta.id,
        acto=acto,
        fuente=resuelta.fuente or fuente,
        name=resuelta.name,
        body_html=resuelta.body_html,
        tokens=[PlantillaSemillaTokenOut(**token) for token in resuelta.tokens],
        bank_name=resuelta.bank_name,
        legal_entity_id=resuelta.legal_entity_id,
        notaria=resuelta.notaria,
        is_fallback=resuelta.is_fallback,
    )


@router.get("/plantillas-semilla", response_model=list[PlantillaAdminItemOut])
def listar_plantillas_admin(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Registro maestro: lista los moldes semilla de las notarías del usuario."""
    notary_ids = get_manageable_notary_ids(current_user)
    items = list_plantillas_admin(db, notary_ids)
    return [PlantillaAdminItemOut(**item.__dict__) for item in items]


@router.get("/plantillas-semilla/{item_id}", response_model=PlantillaAdminDetailOut)
def obtener_plantilla_admin(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Registro maestro: un molde con su cuerpo HTML para editarlo."""
    notary_ids = get_manageable_notary_ids(current_user)
    resuelta = get_plantilla_admin(db, item_id, notary_ids)
    if resuelta is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Molde no encontrado.")
    return PlantillaAdminDetailOut(
        id=resuelta.id,
        acto=resuelta.acto,
        fuente=resuelta.fuente,
        name=resuelta.name,
        body_html=resuelta.body_html,
        tokens=[PlantillaSemillaTokenOut(**token) for token in resuelta.tokens],
        bank_name=resuelta.bank_name,
        legal_entity_id=resuelta.legal_entity_id,
        notaria=resuelta.notaria,
    )


@router.post("/plantillas-semilla", response_model=PlantillaAdminDetailOut, status_code=status.HTTP_201_CREATED)
def guardar_plantilla_admin(
    payload: PlantillaAdminIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*WRITE_ROLES)),
):
    """Registro maestro: crea o actualiza un molde (acto+fuente+banco). Sin seed ni código."""
    notary_id = current_user.default_notary_id
    if notary_id is None:
        manageable = sorted(get_manageable_notary_ids(current_user))
        notary_id = manageable[0] if manageable else None
    if notary_id is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No hay notaría configurada para guardar el molde.",
        )
    try:
        item = upsert_plantilla_admin(
            db,
            notary_id=notary_id,
            acto=payload.acto,
            fuente=payload.fuente,
            legal_entity_id=payload.legal_entity_id,
            name=payload.name,
            body_html=payload.body_html,
            tokens=payload.tokens,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    resuelta = get_plantilla_admin(db, item.id, [notary_id])
    if resuelta is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No se pudo releer el molde guardado.")
    return PlantillaAdminDetailOut(
        id=resuelta.id,
        acto=resuelta.acto,
        fuente=resuelta.fuente,
        name=resuelta.name,
        body_html=resuelta.body_html,
        tokens=[PlantillaSemillaTokenOut(**token) for token in resuelta.tokens],
        bank_name=resuelta.bank_name,
        legal_entity_id=resuelta.legal_entity_id,
        notaria=resuelta.notaria,
    )


@router.post("/cases/{case_id}/extraer", response_model=GariExtraccionOut)
async def extraer_escritura_case(
    case_id: int,
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*WRITE_ROLES)),
    llm: GariLLMClient = Depends(get_gari_llm_client),
):
    load_case_for_user(db, case_id, current_user)
    content = await archivo.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Archivo vacio.")
    upload_text = await extract_upload_text(archivo.filename, content)
    if not upload_text.text.strip():
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="No fue posible extraer texto del archivo.")
    return GariExtraccionOut.model_validate(
        proponer_campos_desde_texto(llm, filename=upload_text.filename, text=upload_text.text)
    )


@router.post("/redaccion/prosa", response_model=GariProsaOut)
def redactar_escritura_prosa(
    payload: GariProsaIn,
    current_user: User = Depends(require_roles(*WRITE_ROLES)),
    llm: GariLLMClient = Depends(get_gari_llm_client),
):
    _ = current_user
    return GariProsaOut.model_validate(
        redactar_prosa(llm, acto=payload.acto, contexto=payload.contexto, instruccion=payload.instruccion)
    )


@router.post("/clasificar", response_model=GariClasificacionOut)
def clasificar_escritura(
    payload: GariClasificacionIn,
    current_user: User = Depends(require_roles(*WRITE_ROLES)),
    llm: GariLLMClient = Depends(get_gari_llm_client),
):
    _ = current_user
    return GariClasificacionOut.model_validate(
        clasificar_acto(llm, descripcion=payload.descripcion, mapa_situaciones=_mapa_situaciones_text())
    )


@router.post("/cases/{case_id}/revisar", response_model=GariRevisionOut)
def revisar_escritura_case(
    case_id: int,
    payload: GariRevisionIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*WRITE_ROLES)),
    llm: GariLLMClient = Depends(get_gari_llm_client),
):
    case = load_case_for_user(db, case_id, current_user)
    state = _parse_state(case.act_data.data_json if case.act_data else "{}")
    effective_date = _state_date(payload.acto, state) or date.today()
    source_text = _revision_source_text(case, payload)
    return GariRevisionOut.model_validate(
        revisar_escritura(
            llm,
            db,
            acto=payload.acto,
            corpus_acto_code=_corpus_acto_code(payload.acto),
            fecha=effective_date,
            html_o_texto=source_text,
            rag_searcher=buscar_corpus,
        )
    )


@router.get("/cases/{case_id}", response_model=EscrituraStateOut)
def get_escritura_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _serialize_state(load_case_for_user(db, case_id, current_user))


@router.put("/cases/{case_id}", response_model=EscrituraStateOut)
def save_escritura_case(
    case_id: int,
    payload: EscrituraStateIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*WRITE_ROLES)),
):
    case = load_case_for_user(db, case_id, current_user)
    act_data = case.act_data
    if act_data is None:
        act_data = CaseActData(case_id=case.id, data_json="{}")
        db.add(act_data)
        db.flush()
        case.act_data = act_data

    act_data.data_json = json.dumps(payload.state, ensure_ascii=False)
    db.commit()
    return _serialize_state(load_case_for_user(db, case_id, current_user), payload.acto)


@router.post("/cases/{case_id}/documento", response_model=DocumentoOut)
def generate_escritura_document(
    case_id: int,
    payload: DocumentoIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*WRITE_ROLES)),
):
    case = load_case_for_user(db, case_id, current_user)
    state = _parse_state(case.act_data.data_json if case.act_data else "{}")
    effective_date = _state_date(payload.acto, state) or date.today()
    hallazgos = evaluar_reglas(db, _corpus_acto_code(payload.acto), effective_date, {**state, "acto": payload.acto})
    bloqueantes = [hallazgo for hallazgo in hallazgos if hallazgo.severidad == "BLOCK"]
    if bloqueantes:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "hay bloqueantes por resolver",
                "bloqueantes": [asdict(hallazgo) for hallazgo in bloqueantes],
            },
        )

    structured_text = html_to_structured_text(payload.html)
    if case.act_data is None:
        case.act_data = CaseActData(case_id=case.id, data_json="{}")
        db.add(case.act_data)
        db.flush()
    case.act_data.gari_draft_text = structured_text

    title = _title_for(payload)
    filename = _filename_for(case, payload)
    docx_buffer = build_gari_docx_buffer(structured_text)
    get_or_create_document(db, case, "escritura", title)
    version = persist_case_document_version(
        db=db,
        case=case,
        category="escritura",
        title=title,
        file_format="docx",
        source_content=docx_buffer.getvalue(),
        original_filename=filename,
        created_by_user_id=current_user.id,
        template_id=case.template_id,
        placeholder_snapshot_json=json.dumps({"source": "escritura_asistida", "acto": payload.acto}, ensure_ascii=False),
    )
    db.commit()
    return DocumentoOut(
        version_number=version.version_number,
        file_format=version.file_format,
        storage_path=version.storage_path,
        download_url=f"/api/v1/document-flow/cases/{case.id}/documents/{version.case_document_id}/versions/{version.id}/download",
        document_id=version.case_document_id,
        version_id=version.id,
    )
