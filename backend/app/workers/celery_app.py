from __future__ import annotations

from app.core.config import get_settings

try:
    from celery import Celery
except ImportError:  # pragma: no cover - exercised only in environments without celery installed
    Celery = None


def build_celery_app():
    if Celery is None:
        raise RuntimeError("Celery is not installed. Install backend requirements before starting workers.")
    settings = get_settings()
    broker_url = settings.celery_broker_url or settings.redis_url
    result_backend = settings.celery_result_backend or settings.redis_url
    app = Celery(
        "easypro2_notarial_intelligence",
        broker=broker_url,
        backend=result_backend,
        include=[
            "app.workers.document_worker",
            "app.workers.intelligence_worker",
        ],
    )
    app.conf.update(
        task_default_queue="notarial-documental",
        task_acks_late=True,
        task_reject_on_worker_lost=True,
        task_track_started=True,
        worker_prefetch_multiplier=1,
        task_soft_time_limit=300,
        task_time_limit=360,
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        timezone="America/Bogota",
        enable_utc=True,
    )
    return app


celery_app = build_celery_app() if Celery is not None else None
