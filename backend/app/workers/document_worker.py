from __future__ import annotations

from sqlalchemy.exc import DisconnectionError, OperationalError

from app.db.session import SessionLocal
from app.models.notarial_document_intelligence import NotarialTaskPublication
from app.services.notarial_document_intelligence.ingestion import (
    PermanentDocumentProcessingError,
    NotarialDocumentIngestionService,
    PUBLICATION_RECOVERABLE_STATUSES,
    TASK_PROCESS_INTELLIGENCE_RUN,
    TASK_PROCESS_QUEUED_BATCH,
    TASK_REPARSE_DOCUMENT,
    TRANSIENT_PROCESSING_ERRORS,
)
from app.workers.celery_app import celery_app
from app.workers.intelligence_worker import process_intelligence_run_task


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


def dispatch_recoverable_publications(limit_per_notary: int = 50) -> dict:
    db = SessionLocal()
    try:
        notary_ids = [
            row[0]
            for row in db.query(NotarialTaskPublication.notary_id)
            .filter(NotarialTaskPublication.status.in_(sorted(PUBLICATION_RECOVERABLE_STATUSES)))
            .distinct()
            .all()
        ]
    finally:
        db.close()

    results: dict[int, list[dict]] = {}
    publishers = {
        TASK_PROCESS_QUEUED_BATCH: process_queued_document_batch_task.delay,
        TASK_REPARSE_DOCUMENT: reparse_document_task.delay,
        TASK_PROCESS_INTELLIGENCE_RUN: process_intelligence_run_task.delay,
    }
    for notary_id in notary_ids:
        session = SessionLocal()
        try:
            service = NotarialDocumentIngestionService(session, notary_id=notary_id)
            results[notary_id] = service.dispatch_recoverable_publications(publishers, limit=limit_per_notary)
        finally:
            session.close()
    return {"notaries": results}


if celery_app is not None:
    @celery_app.task(
        name="notarial_document_intelligence.publications.dispatch_recoverable",
        queue="notarial-documental",
        bind=True,
        autoretry_for=TRANSIENT_RETRY_ERRORS,
        retry_backoff=True,
        retry_backoff_max=60,
        retry_jitter=True,
        retry_kwargs={"max_retries": 3},
        soft_time_limit=120,
        time_limit=180,
    )
    def dispatch_recoverable_publications_task(self, limit_per_notary: int = 50) -> dict:
        return dispatch_recoverable_publications(limit_per_notary=limit_per_notary)

    celery_app.conf.beat_schedule = {
        **(getattr(celery_app.conf, "beat_schedule", None) or {}),
        "dispatch-recoverable-notarial-publications": {
            "task": "notarial_document_intelligence.publications.dispatch_recoverable",
            "schedule": 60.0,
            "args": (50,),
        },
    }
else:
    dispatch_recoverable_publications_task = dispatch_recoverable_publications


if celery_app is not None:
    @celery_app.task(
        name="notarial_document_intelligence.diagnostics.transient_retry_probe",
        queue="notarial-documental",
        bind=True,
        autoretry_for=(TimeoutError,),
        retry_backoff=True,
        retry_jitter=False,
        retry_kwargs={"max_retries": 2},
        soft_time_limit=30,
        time_limit=60,
    )
    def transient_retry_probe_task(self) -> dict:
        if self.request.retries == 0:
            raise TimeoutError("transient probe failure")
        return {"status": "completed", "retries": self.request.retries}
else:
    def transient_retry_probe_task() -> dict:
        return {"status": "completed", "retries": 0}
