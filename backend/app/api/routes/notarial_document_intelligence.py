from __future__ import annotations

import io
import zipfile
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.notarial_document_intelligence import (
    NotarialDocument,
    NotarialDocumentBatch,
    NotarialDocumentBatchItem,
    NotarialDocumentBlock,
)
from app.models.user import User
from app.services.notarial_document_intelligence.contracts import DocumentUpload, IngestBatchRequest, IngestBatchResult
from app.services.notarial_document_intelligence.ingestion import NotarialDocumentIngestionService
from app.workers.document_worker import process_queued_document_batch_task


router = APIRouter(prefix="/notarial-intelligence", tags=["notarial-document-intelligence"])

DOCX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
MAX_DOCUMENTS_PER_BATCH = 500


class BatchDocumentSummary(BaseModel):
    document_id: int
    filename: str
    content_hash: str
    processing_status: str
    storage_backend: str
    block_count: int


class BatchDetailResponse(BaseModel):
    batch_id: int
    batch_key: str
    name: str
    source_type: str
    status: str
    total_documents: int
    unique_documents: int
    duplicate_documents: int
    error_documents: int
    documents: list[BatchDocumentSummary]
    metadata: dict[str, Any]


class ReparseDocumentResponse(BaseModel):
    document_id: int
    status: str
    block_count: int
    warnings: list[str]


def get_ingestion_service(db: Session = Depends(get_db)) -> NotarialDocumentIngestionService:
    return NotarialDocumentIngestionService(db)


@router.post("/batches/ingest", response_model=IngestBatchResult)
async def ingest_batch(
    name: str = Form("Lote documental"),
    source_type: str = Form("manual"),
    async_processing: bool = Form(False),
    files: list[UploadFile] = File(...),
    service: NotarialDocumentIngestionService = Depends(get_ingestion_service),
    current_user: User = Depends(get_current_user),
):
    del current_user
    uploads = await _read_uploads(files)
    if not uploads:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="No se encontraron DOCX para procesar.")
    if len(uploads) > MAX_DOCUMENTS_PER_BATCH:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"El lote excede el maximo de {MAX_DOCUMENTS_PER_BATCH} documentos.",
        )

    request = IngestBatchRequest(name=name, source_type=source_type, documents=uploads)
    if async_processing:
        if not hasattr(process_queued_document_batch_task, "delay"):
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Celery no esta disponible en este entorno.")
        queued = service.queue_batch(request)
        task = process_queued_document_batch_task.delay(queued.batch_id)
        return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content={"batch_id": queued.batch_id, "task_id": task.id})

    return service.ingest_batch(request)


@router.get("/batches/{batch_id}", response_model=BatchDetailResponse)
def get_batch_detail(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    del current_user
    batch = db.get(NotarialDocumentBatch, batch_id)
    if batch is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lote no encontrado.")

    rows = (
        db.query(NotarialDocumentBatchItem, NotarialDocument)
        .join(NotarialDocument, NotarialDocument.id == NotarialDocumentBatchItem.document_id)
        .filter(NotarialDocumentBatchItem.batch_id == batch_id)
        .order_by(NotarialDocumentBatchItem.item_index.asc())
        .all()
    )
    documents = []
    for _, document in rows:
        block_count = db.query(NotarialDocumentBlock).filter(NotarialDocumentBlock.document_id == document.id).count()
        documents.append(
            BatchDocumentSummary(
                document_id=document.id,
                filename=document.filename,
                content_hash=document.content_hash,
                processing_status=document.processing_status,
                storage_backend=document.storage_backend,
                block_count=block_count,
            )
        )

    return BatchDetailResponse(
        batch_id=batch.id,
        batch_key=batch.batch_key,
        name=batch.name,
        source_type=batch.source_type,
        status=batch.status,
        total_documents=batch.total_documents,
        unique_documents=batch.unique_documents,
        duplicate_documents=batch.duplicate_documents,
        error_documents=batch.error_documents,
        documents=documents,
        metadata={},
    )


@router.post("/documents/{document_id}/reparse", response_model=ReparseDocumentResponse)
def reparse_document(
    document_id: int,
    service: NotarialDocumentIngestionService = Depends(get_ingestion_service),
    current_user: User = Depends(get_current_user),
):
    del current_user
    try:
        result = service.reparse_document(document_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return ReparseDocumentResponse(
        document_id=result.document_id,
        status=result.status.value,
        block_count=result.block_count,
        warnings=result.warnings,
    )


async def _read_uploads(files: list[UploadFile]) -> list[DocumentUpload]:
    uploads: list[DocumentUpload] = []
    for file in files:
        filename = file.filename or ""
        content = await file.read()
        if not content:
            continue
        if filename.lower().endswith(".zip"):
            uploads.extend(_extract_docx_from_zip(filename, content))
        elif filename.lower().endswith(".docx"):
            uploads.append(DocumentUpload(filename=Path(filename).name, content=content, content_type=file.content_type or DOCX_MEDIA_TYPE))
        else:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Archivo no soportado: {filename}")
    return uploads


def _extract_docx_from_zip(zip_filename: str, content: bytes) -> list[DocumentUpload]:
    uploads: list[DocumentUpload] = []
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            for info in archive.infolist():
                if info.is_dir() or not info.filename.lower().endswith(".docx"):
                    continue
                safe_name = _safe_zip_docx_name(info.filename)
                uploads.append(
                    DocumentUpload(
                        filename=safe_name,
                        content=archive.read(info),
                        content_type=DOCX_MEDIA_TYPE,
                        source_path=f"{zip_filename}:{info.filename}",
                    )
                )
    except zipfile.BadZipFile as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="ZIP invalido.") from exc
    return uploads


def _safe_zip_docx_name(raw_name: str) -> str:
    normalized = raw_name.replace("\\", "/")
    parts = [part for part in normalized.split("/") if part and part not in {".", ".."}]
    if not parts:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Entrada ZIP invalida.")
    return Path(parts[-1]).name
