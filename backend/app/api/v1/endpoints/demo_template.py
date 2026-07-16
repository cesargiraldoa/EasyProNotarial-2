from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db, get_manageable_notary_ids
from app.models.case import Case
from app.models.case_document import CaseDocument
from app.models.case_document_version import CaseDocumentVersion
from app.models.user import User
from app.services.storage import download_storage_bytes


router = APIRouter(prefix="/demo-templates", tags=["demo-templates"])

JAGGUA_SEED_TEMPLATE = Path(__file__).resolve().parents[3] / "seeds" / "templates" / "jaggua-bogota-2c.docx"


@router.get("/jaggua-2-compradores")
def download_jaggua_demo_template(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    manageable_notaries = get_manageable_notary_ids(current_user)
    if not manageable_notaries:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No hay una notaria activa para seleccionar la plantilla.")

    query = (
        db.query(CaseDocumentVersion)
        .join(CaseDocument, CaseDocument.id == CaseDocumentVersion.case_document_id)
        .join(Case, Case.id == CaseDocument.case_id)
        .filter(CaseDocumentVersion.file_format == "docx")
        .filter(Case.notary_id.in_(manageable_notaries))
        .filter(
            func.lower(CaseDocumentVersion.original_filename).like("%jaggua%"),
            func.lower(CaseDocumentVersion.original_filename).like("%bogot%"),
        )
    )
    version = query.order_by(desc(CaseDocumentVersion.created_at), desc(CaseDocumentVersion.id)).first()
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
