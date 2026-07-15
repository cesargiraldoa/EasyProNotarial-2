from __future__ import annotations

import logging
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.case import Case
from app.models.case_document import CaseDocument
from app.models.case_document_version import CaseDocumentVersion
from app.services.storage import download_storage_bytes, save_case_file

logger = logging.getLogger(__name__)


def _resolve_media_type(file_format: str, original_filename: str) -> str:
    if file_format.lower() == "docx":
        return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    suffix = Path(original_filename).suffix.lower()
    if suffix == ".docx":
        return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    return "application/octet-stream"


def get_or_create_document(db: Session, case: Case, category: str, title: str) -> CaseDocument:
    document = db.query(CaseDocument).filter(CaseDocument.case_id == case.id, CaseDocument.category == category).first()
    if document is None:
        document = CaseDocument(case_id=case.id, category=category, title=title, current_version_number=0)
        db.add(document)
        db.flush()
    else:
        document.title = title
    return document


def persist_case_document_version(
    db: Session,
    case: Case,
    category: str,
    title: str,
    file_format: str,
    source_content: bytes | str | Path,
    original_filename: str,
    created_by_user_id: int | None,
    template_id: int | None = None,
    placeholder_snapshot_json: str = "{}",
) -> CaseDocumentVersion:
    document = get_or_create_document(db, case, category, title)
    version_number = document.current_version_number + 1

    if isinstance(source_content, (bytes, bytearray)):
        source_bytes = bytes(source_content)
    else:
        source_bytes = download_storage_bytes(source_content)

    media_type = _resolve_media_type(file_format, original_filename)
    stored_filename, storage_path = save_case_file(source_bytes, case.id, category, version_number, original_filename, media_type)

    document.current_version_number = version_number
    version = CaseDocumentVersion(
        case_document_id=document.id,
        version_number=version_number,
        file_format=file_format,
        storage_path=storage_path,
        original_filename=stored_filename,
        generated_from_template_id=template_id,
        placeholder_snapshot_json=placeholder_snapshot_json,
        created_by_user_id=created_by_user_id,
    )
    db.add(version)
    db.flush()
    storage_backend = "supabase" if str(storage_path).startswith("supabase://") else "local"
    logger.info(
        "Versión documental persistida",
        extra={
            "case_id": case.id,
            "document_id": document.id,
            "version_id": version.id,
            "storage_backend": storage_backend,
            "file_format": file_format,
        },
    )
    return version
