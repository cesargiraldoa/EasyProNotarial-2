from __future__ import annotations

from sqlalchemy.exc import DisconnectionError, OperationalError

from app.db.session import SessionLocal
from app.services.notarial_document_intelligence.ingestion import (
    PermanentDocumentProcessingError,
    NotarialDocumentIngestionService,
    TRANSIENT_PROCESSING_ERRORS,
)
from app.workers.celery_app import celery_app


TRANSIENT_RETRY_ERRORS = (*TRANSIENT_PROCESSING_ERRORS, OperationalError, DisconnectionError, TimeoutError, ConnectionError)


def process_queued_document_batch(batch_id: int, notary_id: int) -> dict:
    db = SessionLocal()
    try:
        result = NotarialDocumentIngestionService(db, notary_id=notary_id).process_queued_batch(batch_id)
        return result.model_dump(mode="json")
    finally:
        db.close()


if celery_app is not None:
    @celery_app.task(
        name="notarial_document_intelligence.document.process_queued_batch",
        queue="notarial-documental",
        bind=True,
        autoretry_for=TRANSIENT_RETRY_ERRORS,
        retry_backoff=True,
        retry_backoff_max=60,
        retry_jitter=True,
        retry_kwargs={"max_retries": 3},
        soft_time_limit=300,
        time_limit=360,
    )
    def process_queued_document_batch_task(self, batch_id: int, notary_id: int) -> dict:
        return process_queued_document_batch(batch_id, notary_id)
else:
    process_queued_document_batch_task = process_queued_document_batch


def reparse_document(document_id: int, notary_id: int, parse_run_id: int | None = None) -> dict:
    db = SessionLocal()
    try:
        try:
            result = NotarialDocumentIngestionService(db, notary_id=notary_id).reparse_document(
                document_id,
                parse_run_id=parse_run_id,
            )
            return result.model_dump(mode="json")
        except PermanentDocumentProcessingError as exc:
            return {"document_id": document_id, "parse_run_id": parse_run_id, "status": "error", "error": str(exc)}
    finally:
        db.close()


if celery_app is not None:
    @celery_app.task(
        name="notarial_document_intelligence.document.reparse",
        queue="notarial-documental",
        bind=True,
        autoretry_for=TRANSIENT_RETRY_ERRORS,
        retry_backoff=True,
        retry_backoff_max=60,
        retry_jitter=True,
        retry_kwargs={"max_retries": 3},
        soft_time_limit=300,
        time_limit=360,
    )
    def reparse_document_task(self, document_id: int, notary_id: int, parse_run_id: int | None = None) -> dict:
        return reparse_document(document_id, notary_id, parse_run_id)
else:
    reparse_document_task = reparse_document
