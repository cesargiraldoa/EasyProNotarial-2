from __future__ import annotations

from app.db.session import SessionLocal
from app.services.notarial_document_intelligence.ingestion import NotarialDocumentIngestionService
from app.workers.celery_app import celery_app


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
        autoretry_for=(Exception,),
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
