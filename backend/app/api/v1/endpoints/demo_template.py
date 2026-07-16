from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db, get_manageable_notary_ids
from app.models.case import Case
from app.models.case_document import CaseDocument
from app.models.case_document_version import CaseDocumentVersion
from app.models.user import User
from app.services.storage import download_storage_bytes


router = APIRouter(prefix="/demo-templates", tags=["demo-templates"])

JAGGUA_SEED_TEMPLATE = Path(__file__).resolve().parents[3] / "seeds" / "templates" / "jaggua-bogota-2c.docx"
JAGGUA_TEMPLATE_CODE = "jaggua-bogota-2c"


@router.get("/jaggua-2-compradores")
def download_jaggua_demo_template(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    manageable_notaries = get_manageable_notary_ids(current_user)
    if not manageable_notaries:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No hay una notaria activa para seleccionar la plantilla.")

    query = (
        db.query(Case, CaseDocument, CaseDocumentVersion)
        .join(CaseDocument, CaseDocument.id == CaseDocumentVersion.case_document_id)
        .join(Case, Case.id == CaseDocument.case_id)
        .filter(CaseDocumentVersion.file_format == "docx")
        .filter(Case.notary_id.in_(manageable_notaries))
        .filter(CaseDocument.category == "marked_template")
    )
    version = _select_explicit_jaggua_version(
        query.order_by(desc(CaseDocumentVersion.created_at), desc(CaseDocumentVersion.id)).all()
    )
    if version is None:
        if not JAGGUA_SEED_TEMPLATE.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La plantilla JAGGUA no esta disponible en esta instalacion.",
            )
        try:
            content = JAGGUA_SEED_TEMPLATE.read_bytes()
        except OSError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="La plantilla JAGGUA existe, pero el servidor no puede leerla.",
            ) from exc
        template_version = "seed"
    else:
        try:
            content = download_storage_bytes(version.storage_path)
        except Exception as exc:  # storage adapter already logs provider detail
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="No fue posible leer la plantilla almacenada.") from exc
        template_version = str(version.id)

    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": "attachment; filename*=UTF-8''MINUTA%20JAGGUA%20HIPOTECA%20BANCO%20DE%20BOGOTA%20-%202%20COMPRADORES.docx",
            "Cache-Control": "no-store",
            "X-Demo-Template-Version": template_version,
        },
    )


def _select_explicit_jaggua_version(
    rows: Iterable[tuple[Case, CaseDocument, CaseDocumentVersion]],
) -> CaseDocumentVersion | None:
    for case_obj, document_obj, version in rows:
        if _is_explicit_jaggua_marked_template(case_obj, document_obj, version):
            return version
    return None


def _safe_json_object(raw: str | None) -> dict:
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _metadata_values(case_obj: Case, document_obj: CaseDocument, version: CaseDocumentVersion) -> list[dict]:
    values: list[dict] = []
    for raw in (case_obj.metadata_json, version.placeholder_snapshot_json):
        parsed = _safe_json_object(raw)
        if parsed:
            values.append(parsed)
            nested = parsed.get("marked_template")
            if isinstance(nested, dict):
                values.append(nested)
            metadata = parsed.get("metadata")
            if isinstance(metadata, dict):
                values.append(metadata)
    if document_obj.title:
        values.append({"document_title": document_obj.title})
    return values


def _is_explicit_jaggua_marked_template(case_obj: Case, document_obj: CaseDocument, version: CaseDocumentVersion) -> bool:
    if document_obj.category != "marked_template":
        return False
    for metadata in _metadata_values(case_obj, document_obj, version):
        identity = (
            metadata.get("demo_template_code")
            or metadata.get("template_code")
            or metadata.get("template_identity")
            or metadata.get("seed_template")
        )
        source = metadata.get("source")
        role = metadata.get("template_role") or metadata.get("document_role")
        if identity == JAGGUA_TEMPLATE_CODE and source in {None, "marked_template"} and role in {"demo_template", "marked_template", "seed_template"}:
            return True
    return False
