from __future__ import annotations

from app.workers.celery_app import celery_app


def classify_document_batch(batch_id: int) -> dict:
    raise RuntimeError(
        f"Intelligence classification worker for batch {batch_id} is not enabled until the embeddings/RAG/LLM phase is implemented."
    )


if celery_app is not None:
    classify_document_batch_task = celery_app.task(
        name="notarial_document_intelligence.intelligence.classify_batch",
        queue="notarial-intelligence",
    )(classify_document_batch)
else:
    classify_document_batch_task = classify_document_batch
