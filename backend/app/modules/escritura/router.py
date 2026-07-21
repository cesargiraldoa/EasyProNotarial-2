from __future__ import annotations

import json
import re
from datetime import date
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user, get_db, get_manageable_notary_ids, get_role_codes, require_roles
from app.models.case import Case
from app.models.case_act_data import CaseActData
from app.models.case_document import CaseDocument
from app.models.case_document_version import CaseDocumentVersion
from app.models.user import User
from app.schemas.escritura import (
    ActoCode,
    CorpusResponse,
    DocumentoIn,
    DocumentoOut,
    EscrituraStateIn,
    EscrituraStateOut,
    LegalClausulaOut,
    LegalNormaOut,
    LegalReglaOut,
    LegalTarifaOut,
)
from app.services.document_persistence import get_or_create_document, persist_case_document_version
from app.services.gari_document_service import build_gari_docx_buffer
from app.services.legal_corpus import clausulas_vigentes, normas_vigentes, reglas_vigentes, tarifas_vigentes

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
    if payload.cumplimiento_bloqueantes > 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="hay bloqueantes por resolver")

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
