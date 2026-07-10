from __future__ import annotations

from app.db.session import SessionLocal
from app.services.notarial_document_intelligence.contracts import DocumentUpload, IngestBatchRequest
from app.services.notarial_document_intelligence.ingestion import NotarialDocumentIngestionService
from app.workers.celery_app import celery_app


def ingest_document_batch(payload: dict) -> dict:
    request = IngestBatchRequest(
        name=str(payload.get("name") or "Lote documental"),
        source_type=str(payload.get("source_type") or "worker"),
        metadata=payload.get("metadata") or {},
        documents=[
            DocumentUpload(
                filename=str(item.get("filename") or "documento.docx"),
                content=bytes.fromhex(str(item.get("content_hex") or "")),
                content_type=str(item.get("content_type") or "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
                source_path=item.get("source_path"),
                metadata=item.get("metadata") or {},
            )
            for item in payload.get("documents", [])
            if isinstance(item, dict)
        ],
    )
    db = SessionLocal()
    try:
        result = NotarialDocumentIngestionService(db).ingest_batch(request)
        return result.model_dump(mode="json")
    finally:
        db.close()


if celery_app is not None:
    ingest_document_batch_task = celery_app.task(
        name="notarial_document_intelligence.document.ingest_batch",
        queue="notarial-documental",
    )(ingest_document_batch)
else:
    ingest_document_batch_task = ingest_document_batch
