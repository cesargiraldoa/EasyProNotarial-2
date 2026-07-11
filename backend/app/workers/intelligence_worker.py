from __future__ import annotations

from sqlalchemy.exc import DisconnectionError, OperationalError

from app.db.session import SessionLocal
from app.services.notarial_document_intelligence.engine import NotarialIntelligenceEngine
from app.services.notarial_document_intelligence.ingestion import TRANSIENT_PROCESSING_ERRORS
from app.services.notarial_document_intelligence.llm_provider import IntelligenceMode
from app.workers.celery_app import celery_app


TRANSIENT_INTELLIGENCE_ERRORS = (*TRANSIENT_PROCESSING_ERRORS, OperationalError, DisconnectionError, TimeoutError, ConnectionError)


def process_document_intelligence(document_id: int, notary_id: int, llm_mode: str = IntelligenceMode.OFF.value) -> dict:
    db = SessionLocal()
    try:
        result = NotarialIntelligenceEngine(db).run_document(
            notary_id=notary_id,
            document_id=document_id,
            llm_mode=IntelligenceMode(llm_mode),
        )
        return result.__dict__
    finally:
        db.close()


def reindex_notarial_embeddings(notary_id: int) -> dict:
    db = SessionLocal()
    try:
        return NotarialIntelligenceEngine(db).reindex_notary(notary_id)
    finally:
        db.close()


if celery_app is not None:
    @celery_app.task(
        name="notarial_document_intelligence.engine.process_document",
        queue="notarial-intelligence",
        bind=True,
        autoretry_for=TRANSIENT_INTELLIGENCE_ERRORS,
        retry_backoff=True,
        retry_backoff_max=120,
        retry_jitter=True,
        retry_kwargs={"max_retries": 3},
        soft_time_limit=600,
        time_limit=720,
    )
    def process_document_intelligence_task(self, document_id: int, notary_id: int, llm_mode: str = IntelligenceMode.OFF.value) -> dict:
        return process_document_intelligence(document_id, notary_id, llm_mode)

    @celery_app.task(
        name="notarial_document_intelligence.engine.reindex_embeddings",
        queue="notarial-intelligence",
        bind=True,
        autoretry_for=TRANSIENT_INTELLIGENCE_ERRORS,
        retry_backoff=True,
        retry_backoff_max=120,
        retry_jitter=True,
        retry_kwargs={"max_retries": 3},
        soft_time_limit=1800,
        time_limit=2100,
    )
    def reindex_notarial_embeddings_task(self, notary_id: int) -> dict:
        return reindex_notarial_embeddings(notary_id)
else:
    process_document_intelligence_task = process_document_intelligence
    reindex_notarial_embeddings_task = reindex_notarial_embeddings


__all__ = [
    "process_document_intelligence",
    "process_document_intelligence_task",
    "reindex_notarial_embeddings",
    "reindex_notarial_embeddings_task",
]
