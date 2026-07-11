from __future__ import annotations

import shutil
import tempfile
import zipfile
import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import get_current_user, get_db, require_permission
from app.models.notarial_document_intelligence import (
    NotarialDocument,
    NotarialDocumentBatch,
    NotarialDocumentBatchItem,
    NotarialDocumentBlock,
    NotarialIntelligenceRun,
    NotarialDocumentParseRun,
)
from app.models.user import User
from app.services.notarial_document_intelligence.contracts import AcceptedBatchResponse, AcceptedReparseResponse, BatchStatus, DocumentUpload, IngestBatchRequest, IngestBatchResult
from app.services.notarial_document_intelligence.engine import NotarialIntelligenceEngine
from app.services.notarial_document_intelligence.ingestion import (
    NotarialDocumentIngestionService,
    TASK_PROCESS_INTELLIGENCE_RUN,
    TASK_PROCESS_QUEUED_BATCH,
    TASK_REPARSE_DOCUMENT,
    TaskPublicationError,
)
from app.services.notarial_document_intelligence.llm_provider import IntelligenceMode
from app.workers.document_worker import process_queued_document_batch_task, reparse_document_task
from app.workers.intelligence_worker import process_intelligence_run_task


router = APIRouter(prefix="/notarial-intelligence", tags=["notarial-document-intelligence"])

DOCX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
MAX_DOCUMENTS_PER_BATCH = 500
MAX_FILE_BYTES = 50 * 1024 * 1024
MAX_BATCH_BYTES = 500 * 1024 * 1024
MAX_ZIP_COMPRESSED_BYTES = 250 * 1024 * 1024
MAX_ZIP_UNCOMPRESSED_BYTES = 500 * 1024 * 1024
MAX_ZIP_COMPRESSION_RATIO = 100
CHUNK_SIZE = 1024 * 1024


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


class ParseRunDetailResponse(BaseModel):
    document_id: int
    parse_run_id: int
    parse_version: int
    status: str
    is_active: bool
    parser_name: str
    parser_version: str
    error_message: str | None
    warnings: list[Any]
    metadata: dict[str, Any]


class PublicationDispatchResponse(BaseModel):
    dispatched: int
    results: list[dict[str, Any]]


class IntelligenceRunRequest(BaseModel):
    llm_mode: IntelligenceMode = IntelligenceMode.OFF


class IntelligenceRunResponse(BaseModel):
    run_id: int
    document_id: int
    parse_run_id: int | None = None
    task_id: str | None = None
    status: str
    status_url: str


class ReindexResponse(BaseModel):
    run_id: int
    task_id: str | None = None
    status: str
    status_url: str


class IntelligenceRunDetailResponse(BaseModel):
    run_id: int
    run_key: str
    run_type: str
    document_id: int | None
    parse_run_id: int | None
    status: str
    llm_mode: str
    task_id: str | None
    attempts: int
    error_message: str | None
    result: dict[str, Any]
    metadata: dict[str, Any]


class BenchmarkResponse(BaseModel):
    notary_id: int
    documents: int
    families: int
    decisions: int
    existing_embeddings: int
    benchmark_run_id: int
    corpus_version: str
    model_version: str
    metrics: dict[str, Any]
    coverage: dict[str, int]


def _current_notary_id(current_user: User) -> int:
    notary_id = getattr(current_user, "default_notary_id", None)
    if notary_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario sin notaria activa.")
    return int(notary_id)


def get_ingestion_service(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NotarialDocumentIngestionService:
    return NotarialDocumentIngestionService(db, notary_id=_current_notary_id(current_user))


@router.post(
    "/batches/ingest",
    response_model=IngestBatchResult | AcceptedBatchResponse,
    responses={202: {"model": AcceptedBatchResponse}},
)
async def ingest_batch(
    name: str = Form("Lote documental"),
    source_type: str = Form("manual"),
    async_processing: bool = Form(False),
    files: list[UploadFile] = File(...),
    response: Response = None,
    service: NotarialDocumentIngestionService = Depends(get_ingestion_service),
    current_user: User = Depends(require_permission("notarial_intelligence.ingest", scoped_to_default_notary=True)),
):
    notary_id = _current_notary_id(current_user)
    with tempfile.TemporaryDirectory(prefix="easypro2-notarial-upload-") as tmp_dir:
        uploads = await _read_uploads(files, Path(tmp_dir))
        if not uploads:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="No se encontraron DOCX para procesar.")
        request = IngestBatchRequest(name=name, source_type=source_type, documents=uploads)
        if async_processing:
            if not hasattr(process_queued_document_batch_task, "delay"):
                raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Celery no esta disponible en este entorno.")
            queued = service.queue_batch(request)
            try:
                publication = service.get_publication_for_target("batch", queued.batch_id)
                task_id = service.publish_task_publication(publication.id, process_queued_document_batch_task.delay)
            except TaskPublicationError as exc:
                raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="No fue posible publicar la tarea documental.") from exc
            response.status_code = status.HTTP_202_ACCEPTED
            return AcceptedBatchResponse(
                batch_id=queued.batch_id,
                batch_key=queued.batch_key,
                task_id=task_id,
                status=BatchStatus.QUEUED,
                status_url=f"{get_settings().api_v1_prefix}/notarial-intelligence/batches/{queued.batch_id}",
            )

        return service.ingest_batch(request)


@router.get("/batches/{batch_id}", response_model=BatchDetailResponse)
def get_batch_detail(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("notarial_intelligence.read", scoped_to_default_notary=True)),
):
    notary_id = _current_notary_id(current_user)
    batch = (
        db.query(NotarialDocumentBatch)
        .filter(NotarialDocumentBatch.id == batch_id, NotarialDocumentBatch.notary_id == notary_id)
        .first()
    )
    if batch is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lote no encontrado.")

    rows = (
        db.query(NotarialDocumentBatchItem, NotarialDocument)
        .join(NotarialDocument, NotarialDocument.id == NotarialDocumentBatchItem.document_id)
        .filter(NotarialDocumentBatchItem.batch_id == batch_id, NotarialDocumentBatchItem.notary_id == notary_id)
        .order_by(NotarialDocumentBatchItem.item_index.asc())
        .all()
    )
    documents = []
    for _, document in rows:
        block_count = (
            db.query(NotarialDocumentBlock)
            .join(NotarialDocumentParseRun, NotarialDocumentParseRun.id == NotarialDocumentBlock.parse_run_id)
            .filter(
                NotarialDocumentBlock.document_id == document.id,
                NotarialDocumentBlock.notary_id == notary_id,
                NotarialDocumentParseRun.is_active.is_(True),
            )
            .count()
        )
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
        metadata=_json_object(batch.metadata_json),
    )


@router.get("/documents/{document_id}/parse-runs/{parse_run_id}", response_model=ParseRunDetailResponse)
def get_parse_run_detail(
    document_id: int,
    parse_run_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("notarial_intelligence.read", scoped_to_default_notary=True)),
):
    notary_id = _current_notary_id(current_user)
    parse_run = (
        db.query(NotarialDocumentParseRun)
        .filter(
            NotarialDocumentParseRun.id == parse_run_id,
            NotarialDocumentParseRun.document_id == document_id,
            NotarialDocumentParseRun.notary_id == notary_id,
        )
        .first()
    )
    if parse_run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parse run no encontrado.")
    return ParseRunDetailResponse(
        document_id=document_id,
        parse_run_id=parse_run.id,
        parse_version=parse_run.parse_version,
        status=parse_run.status,
        is_active=parse_run.is_active,
        parser_name=parse_run.parser_name,
        parser_version=parse_run.parser_version,
        error_message=parse_run.error_message,
        warnings=_json_list(parse_run.warnings_json),
        metadata=_json_object(parse_run.metadata_json),
    )


def _json_object(raw: str | None) -> dict[str, Any]:
    try:
        payload = json.loads(raw or "{}")
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _json_list(raw: str | None) -> list[Any]:
    try:
        payload = json.loads(raw or "[]")
    except json.JSONDecodeError:
        return []
    return payload if isinstance(payload, list) else []


@router.post(
    "/documents/{document_id}/reparse",
    response_model=AcceptedReparseResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def reparse_document(
    document_id: int,
    response: Response = None,
    service: NotarialDocumentIngestionService = Depends(get_ingestion_service),
    current_user: User = Depends(require_permission("notarial_intelligence.reparse", scoped_to_default_notary=True)),
):
    notary_id = _current_notary_id(current_user)
    try:
        service.get_document_for_notary(document_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    if not hasattr(reparse_document_task, "delay"):
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Celery no esta disponible en este entorno.")
    try:
        parse_run = service.queue_reparse_document(document_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    try:
        publication = service.get_publication_for_target("reparse", parse_run.id)
        task_id = service.publish_task_publication(publication.id, reparse_document_task.delay)
    except TaskPublicationError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="No fue posible publicar el reparse documental.") from exc
    if response is not None:
        response.status_code = status.HTTP_202_ACCEPTED
    return AcceptedReparseResponse(
        document_id=document_id,
        parse_run_id=parse_run.id,
        task_id=task_id,
        status=parse_run.status,
        status_url=f"{get_settings().api_v1_prefix}/notarial-intelligence/documents/{document_id}/parse-runs/{parse_run.id}",
    )


@router.post("/publications/reconcile", response_model=PublicationDispatchResponse)
def reconcile_publications(
    service: NotarialDocumentIngestionService = Depends(get_ingestion_service),
    current_user: User = Depends(require_permission("notarial_intelligence.ingest", scoped_to_default_notary=True)),
):
    _current_notary_id(current_user)
    publishers = {}
    if hasattr(process_queued_document_batch_task, "delay"):
        publishers[TASK_PROCESS_QUEUED_BATCH] = process_queued_document_batch_task.delay
    if hasattr(reparse_document_task, "delay"):
        publishers[TASK_REPARSE_DOCUMENT] = reparse_document_task.delay
    if hasattr(process_intelligence_run_task, "delay"):
        publishers[TASK_PROCESS_INTELLIGENCE_RUN] = process_intelligence_run_task.delay
    if not publishers:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Celery no esta disponible en este entorno.")
    results = service.dispatch_recoverable_publications(publishers)
    return PublicationDispatchResponse(dispatched=len(results), results=results)


@router.post("/documents/{document_id}/intelligence/run", response_model=IntelligenceRunResponse)
def run_document_intelligence(
    document_id: int,
    request: IntelligenceRunRequest,
    response: Response = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("notarial_intelligence.reparse", scoped_to_default_notary=True)),
):
    notary_id = _current_notary_id(current_user)
    document = db.get(NotarialDocument, document_id)
    if document is None or document.notary_id != notary_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento no encontrado.")
    if not hasattr(process_intelligence_run_task, "delay"):
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Celery no esta disponible en este entorno.")
    engine = NotarialIntelligenceEngine(db)
    run = engine.create_document_run(notary_id, document_id, llm_mode=request.llm_mode)
    service = NotarialDocumentIngestionService(db, notary_id=notary_id)
    publication = service.ensure_task_publication(
        request_key=f"intelligence_run:{run.id}",
        target_type="intelligence_run",
        target_id=run.id,
        task_name=TASK_PROCESS_INTELLIGENCE_RUN,
        task_args=[run.id],
        document_id=document_id,
        parse_run_id=run.parse_run_id,
        metadata={"source": "run_document_intelligence"},
    )
    try:
        task_id = service.publish_task_publication(publication.id, process_intelligence_run_task.delay)
    except TaskPublicationError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="No fue posible publicar la tarea de inteligencia.") from exc
    if response is not None:
        response.status_code = status.HTTP_202_ACCEPTED
    return IntelligenceRunResponse(
        run_id=run.id,
        document_id=document_id,
        parse_run_id=run.parse_run_id,
        task_id=task_id,
        status=run.status,
        status_url=f"{get_settings().api_v1_prefix}/notarial-intelligence/intelligence/runs/{run.id}",
    )


@router.post("/embeddings/reindex", response_model=ReindexResponse)
def reindex_embeddings(
    response: Response = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("notarial_intelligence.ingest", scoped_to_default_notary=True)),
):
    notary_id = _current_notary_id(current_user)
    if not hasattr(process_intelligence_run_task, "delay"):
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Celery no esta disponible en este entorno.")
    run = NotarialIntelligenceEngine(db).create_reindex_run(notary_id)
    service = NotarialDocumentIngestionService(db, notary_id=notary_id)
    publication = service.ensure_task_publication(
        request_key=f"intelligence_run:{run.id}",
        target_type="intelligence_run",
        target_id=run.id,
        task_name=TASK_PROCESS_INTELLIGENCE_RUN,
        task_args=[run.id],
        metadata={"source": "reindex_embeddings"},
    )
    try:
        task_id = service.publish_task_publication(publication.id, process_intelligence_run_task.delay)
    except TaskPublicationError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="No fue posible publicar la reindexacion.") from exc
    if response is not None:
        response.status_code = status.HTTP_202_ACCEPTED
    return ReindexResponse(run_id=run.id, task_id=task_id, status=run.status, status_url=f"{get_settings().api_v1_prefix}/notarial-intelligence/intelligence/runs/{run.id}")


@router.get("/intelligence/runs/{run_id}", response_model=IntelligenceRunDetailResponse)
def get_intelligence_run(
    run_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("notarial_intelligence.read", scoped_to_default_notary=True)),
):
    notary_id = _current_notary_id(current_user)
    run = db.get(NotarialIntelligenceRun, run_id)
    if run is None or run.notary_id != notary_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run no encontrado.")
    return IntelligenceRunDetailResponse(
        run_id=run.id,
        run_key=run.run_key,
        run_type=run.run_type,
        document_id=run.document_id,
        parse_run_id=run.parse_run_id,
        status=run.status,
        llm_mode=run.llm_mode,
        task_id=run.task_id,
        attempts=run.attempts,
        error_message=run.error_message,
        result=_json_object(run.result_json),
        metadata=_json_object(run.metadata_json),
    )


@router.get("/benchmark", response_model=BenchmarkResponse)
def benchmark_notarial_corpus(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("notarial_intelligence.read", scoped_to_default_notary=True)),
):
    notary_id = _current_notary_id(current_user)
    return BenchmarkResponse(**NotarialIntelligenceEngine(db).benchmark_notary(notary_id))


async def _read_uploads(files: list[UploadFile], tmp_dir: Path) -> list[DocumentUpload]:
    uploads: list[DocumentUpload] = []
    total_bytes = 0
    total_uncompressed_bytes = 0
    for file in files:
        filename = file.filename or ""
        spooled_path, size = await _spool_upload(file, tmp_dir)
        if size == 0:
            continue
        total_bytes += size
        if total_bytes > MAX_BATCH_BYTES:
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="El lote excede el tamano maximo permitido.")
        if filename.lower().endswith(".zip"):
            if size > MAX_ZIP_COMPRESSED_BYTES:
                raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="ZIP demasiado grande.")
            zip_uploads, total_uncompressed_bytes = _extract_docx_from_zip(filename, spooled_path, tmp_dir, total_uncompressed_bytes)
            uploads.extend(zip_uploads)
        elif filename.lower().endswith(".docx"):
            _validate_docx_file(spooled_path)
            total_uncompressed_bytes += size
            if total_uncompressed_bytes > MAX_ZIP_UNCOMPRESSED_BYTES:
                raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="El lote excede el tamano descomprimido maximo permitido.")
            uploads.append(DocumentUpload(filename=Path(filename).name, file_path=str(spooled_path), content_type=file.content_type or DOCX_MEDIA_TYPE))
        else:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Archivo no soportado: {filename}")
        if len(uploads) > MAX_DOCUMENTS_PER_BATCH:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"El lote excede el maximo de {MAX_DOCUMENTS_PER_BATCH} documentos.")
    return uploads


async def _spool_upload(file: UploadFile, tmp_dir: Path) -> tuple[Path, int]:
    target = tmp_dir / f"upload_{len(list(tmp_dir.glob('upload_*')))}_{Path(file.filename or 'archivo').name}"
    size = 0
    with target.open("wb") as handle:
        while True:
            chunk = await file.read(CHUNK_SIZE)
            if not chunk:
                break
            size += len(chunk)
            if size > MAX_FILE_BYTES:
                raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Archivo demasiado grande.")
            handle.write(chunk)
    return target, size


def _extract_docx_from_zip(zip_filename: str, zip_path: Path, tmp_dir: Path, current_uncompressed_bytes: int) -> tuple[list[DocumentUpload], int]:
    uploads: list[DocumentUpload] = []
    try:
        with zipfile.ZipFile(zip_path) as archive:
            for info in archive.infolist():
                if info.flag_bits & 0x1:
                    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="ZIP cifrado no permitido.")
                safe_name = _safe_zip_docx_name(info.filename)
                if info.is_dir():
                    continue
                if not safe_name.lower().endswith(".docx"):
                    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Entrada no soportada en ZIP: {safe_name}")
                if info.file_size > MAX_FILE_BYTES:
                    raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Entrada DOCX demasiado grande dentro del ZIP.")
                current_uncompressed_bytes += info.file_size
                if current_uncompressed_bytes > MAX_ZIP_UNCOMPRESSED_BYTES:
                    raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="ZIP bomb detectado: contenido descomprimido excede el limite global del lote.")
                if info.compress_size and (info.file_size / max(info.compress_size, 1)) > MAX_ZIP_COMPRESSION_RATIO:
                    raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="ZIP bomb detectado: ratio de compresion inseguro.")
                target = tmp_dir / f"zip_{len(uploads)}_{safe_name}"
                with archive.open(info) as source, target.open("wb") as destination:
                    copied = 0
                    while True:
                        chunk = source.read(CHUNK_SIZE)
                        if not chunk:
                            break
                        copied += len(chunk)
                        if copied > MAX_FILE_BYTES:
                            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Entrada DOCX demasiado grande dentro del ZIP.")
                        destination.write(chunk)
                _validate_docx_file(target)
                uploads.append(
                    DocumentUpload(
                        filename=safe_name,
                        file_path=str(target),
                        content_type=DOCX_MEDIA_TYPE,
                        source_path=f"{zip_filename}:{info.filename}",
                    )
                )
    except zipfile.BadZipFile as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="ZIP invalido.") from exc
    return uploads, current_uncompressed_bytes


def _safe_zip_docx_name(raw_name: str) -> str:
    normalized = raw_name.replace("\\", "/")
    parts = [part for part in normalized.split("/") if part and part != "."]
    if not parts or any(part == ".." for part in parts) or normalized.startswith("/"):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Ruta insegura dentro del ZIP.")
    return Path(parts[-1]).name


def _validate_docx_file(path: Path) -> None:
    try:
        with zipfile.ZipFile(path) as archive:
            names = set(archive.namelist())
            if "[Content_Types].xml" not in names or "word/document.xml" not in names:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="DOCX invalido.")
    except zipfile.BadZipFile as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="DOCX invalido.") from exc
