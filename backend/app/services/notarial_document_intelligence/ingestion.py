from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.notarial_document_intelligence import (
    NotarialDocument,
    NotarialDocumentBatch,
    NotarialDocumentBatchItem,
    NotarialDocumentBlock,
    NotarialDocumentParseRun,
    NotarialDocumentSection,
)
from app.services.notarial_document_intelligence.contracts import (
    BatchStatus,
    DocumentProcessingStatus,
    DocumentUpload,
    IngestBatchRequest,
    IngestBatchResult,
    IngestedDocumentSummary,
    ParsedDocument,
)
from app.services.notarial_document_intelligence.parser import NotarialDocumentParser
from app.services.notarial_document_intelligence.storage import NotarialIntelligenceStorage, StoredDocumentResult
from app.services.storage import download_storage_bytes


class NotarialDocumentIngestionService:
    def __init__(
        self,
        db: Session,
        notary_id: int,
        storage: NotarialIntelligenceStorage | None = None,
        parser: NotarialDocumentParser | None = None,
    ) -> None:
        self.db = db
        self.notary_id = notary_id
        self.storage = storage or NotarialIntelligenceStorage()
        self.parser = parser or NotarialDocumentParser()

    def ingest_batch(self, request: IngestBatchRequest) -> IngestBatchResult:
        batch = self._create_batch(request, BatchStatus.RUNNING)
        summaries, warnings, unique, duplicate, errors = self._handle_batch_documents(batch.id, request.documents, parse_now=True)
        batch.total_documents = len(request.documents)
        batch.unique_documents = unique
        batch.duplicate_documents = duplicate
        batch.error_documents = errors
        batch.status = BatchStatus.PARTIAL_ERROR.value if errors and summaries else BatchStatus.ERROR.value if errors else BatchStatus.COMPLETED.value
        batch.finished_at = _now()
        if errors:
            batch.error_message = f"{errors} document(s) failed during ingestion."
        self.db.commit()
        return self._batch_result(batch, summaries, warnings)

    def queue_batch(self, request: IngestBatchRequest) -> IngestBatchResult:
        batch = self._create_batch(request, BatchStatus.QUEUED)
        summaries, warnings, unique, duplicate, errors = self._handle_batch_documents(batch.id, request.documents, parse_now=False)
        batch.total_documents = len(request.documents)
        batch.unique_documents = unique
        batch.duplicate_documents = duplicate
        batch.error_documents = errors
        if errors:
            batch.status = BatchStatus.PARTIAL_ERROR.value if summaries else BatchStatus.ERROR.value
            batch.error_message = f"{errors} document(s) failed while queuing ingestion."
            batch.finished_at = _now()
        self.db.commit()
        return self._batch_result(batch, summaries, warnings)

    def process_queued_batch(self, batch_id: int) -> IngestBatchResult:
        batch = self.db.get(NotarialDocumentBatch, batch_id)
        if batch is None or batch.notary_id != self.notary_id:
            raise ValueError(f"Batch {batch_id} not found.")
        if batch.status not in {BatchStatus.QUEUED.value, BatchStatus.PARTIAL_ERROR.value, BatchStatus.ERROR.value, BatchStatus.RUNNING.value}:
            raise ValueError(f"Batch {batch_id} is not queued for processing.")

        batch.status = BatchStatus.RUNNING.value
        batch.error_message = None
        self.db.commit()

        summaries: list[IngestedDocumentSummary] = []
        warnings: list[str] = []
        errors = 0
        rows = (
            self.db.query(NotarialDocumentBatchItem, NotarialDocument)
            .join(NotarialDocument, NotarialDocument.id == NotarialDocumentBatchItem.document_id)
            .filter(NotarialDocumentBatchItem.batch_id == batch_id, NotarialDocumentBatchItem.notary_id == self.notary_id)
            .order_by(NotarialDocumentBatchItem.item_index.asc())
            .all()
        )
        for item, document in rows:
            if item.status == "processed":
                summaries.append(self._summary_for_document(document, reused=True))
                continue
            try:
                summary = self.reparse_document(document.id, commit=False)
                item.status = "processed"
                summaries.append(summary)
                warnings.extend(summary.warnings)
                self.db.commit()
            except Exception as exc:
                self.db.rollback()
                item = self.db.get(NotarialDocumentBatchItem, item.id)
                document = self.db.get(NotarialDocument, document.id)
                item.status = "error"
                document.processing_status = DocumentProcessingStatus.ERROR.value
                document.error_message = str(exc)
                errors += 1
                warnings.append(f"{document.filename}: {type(exc).__name__}")
                self.db.commit()

        batch = self.db.get(NotarialDocumentBatch, batch_id)
        batch.error_documents = errors
        batch.status = BatchStatus.PARTIAL_ERROR.value if errors and summaries else BatchStatus.ERROR.value if errors else BatchStatus.COMPLETED.value
        batch.finished_at = _now()
        if errors:
            batch.error_message = f"{errors} document(s) failed during queued processing."
        self.db.commit()
        return self._batch_result(batch, summaries, warnings)

    def reparse_document(self, document_id: int, commit: bool = True) -> IngestedDocumentSummary:
        document = self.db.get(NotarialDocument, document_id)
        if document is None or document.notary_id != self.notary_id:
            raise ValueError(f"Document {document_id} not found.")

        parse_run = self._create_parse_run(document.id, self.parser.parser_name, "pending")
        try:
            content = download_storage_bytes(document.storage_path)
            parsed = self.parser.parse_bytes(content, filename=document.filename)
            parse_run.parser_name = parsed.parser_name
            parse_run.parser_version = parsed.parser_version
            self._persist_parsed_blocks(document.id, parse_run.id, parsed)
            self._activate_parse_run(document.id, parse_run.id)
            document.parser_name = parsed.parser_name
            document.parser_version = parsed.parser_version
            document.processing_status = DocumentProcessingStatus.PARSED.value
            document.metadata_json = _json({"reparse": parsed.metadata, "warnings": parsed.warnings})
            document.error_message = None
            block_count = len(parsed.blocks)
            warnings = parsed.warnings
        except Exception as exc:
            parse_run.status = "error"
            parse_run.finished_at = _now()
            parse_run.error_message = str(exc)
            document.error_message = str(exc)
            if commit:
                self.db.commit()
            else:
                self.db.flush()
            raise

        if commit:
            self.db.commit()
        else:
            self.db.flush()

        return IngestedDocumentSummary(
            document_id=document.id,
            filename=document.filename,
            content_hash=document.content_hash,
            status=DocumentProcessingStatus.PARSED,
            block_count=block_count,
            storage_path=document.storage_path,
            reused_existing_document=False,
            warnings=warnings,
        )

    def _create_batch(self, request: IngestBatchRequest, status: BatchStatus) -> NotarialDocumentBatch:
        batch = NotarialDocumentBatch(
            notary_id=self.notary_id,
            batch_key=f"batch_{uuid.uuid4().hex}",
            name=request.name,
            source_type=request.source_type,
            status=status.value,
            metadata_json=_json(request.metadata),
            started_at=_now(),
        )
        self.db.add(batch)
        self.db.flush()
        return batch

    def _handle_batch_documents(
        self,
        batch_id: int,
        documents: list[DocumentUpload],
        parse_now: bool,
    ) -> tuple[list[IngestedDocumentSummary], list[str], int, int, int]:
        summaries: list[IngestedDocumentSummary] = []
        warnings: list[str] = []
        unique_documents = 0
        duplicate_documents = 0
        error_documents = 0
        for item_index, upload in enumerate(documents, start=1):
            try:
                with self.db.begin_nested():
                    summary = self._ingest_document(batch_id, item_index, upload, parse_now=parse_now)
                summaries.append(summary)
                warnings.extend(summary.warnings)
                if summary.reused_existing_document:
                    duplicate_documents += 1
                else:
                    unique_documents += 1
            except Exception as exc:
                error_documents += 1
                warnings.append(f"{upload.filename}: {type(exc).__name__}")
        return summaries, warnings, unique_documents, duplicate_documents, error_documents

    def _ingest_document(self, batch_id: int, item_index: int, upload: DocumentUpload, parse_now: bool) -> IngestedDocumentSummary:
        stored = self._store_upload(upload)
        document, created = self._get_or_create_document(upload, stored)
        if not created and document.processing_status != DocumentProcessingStatus.STORED.value:
            self._link_batch_item(batch_id, item_index, upload, stored, document.id, "reused")
            return self._summary_for_document(document, reused=True)

        if not parse_now:
            self._link_batch_item(batch_id, item_index, upload, stored, document.id, "queued")
            return self._summary_for_document(document, reused=not created)

        parsed = self._parse_upload(upload)
        parse_run = self._create_parse_run(document.id, parsed.parser_name, parsed.parser_version)
        self._persist_parsed_blocks(document.id, parse_run.id, parsed)
        self._activate_parse_run(document.id, parse_run.id)
        document.parser_name = parsed.parser_name
        document.parser_version = parsed.parser_version
        document.processing_status = DocumentProcessingStatus.PARSED.value
        document.metadata_json = _json({"upload": upload.metadata, "parse": parsed.metadata, "warnings": parsed.warnings})
        document.error_message = None
        self._link_batch_item(batch_id, item_index, upload, stored, document.id, "processed")
        return IngestedDocumentSummary(
            document_id=document.id,
            filename=document.filename,
            content_hash=document.content_hash,
            status=DocumentProcessingStatus.PARSED,
            block_count=len(parsed.blocks),
            storage_path=document.storage_path,
            reused_existing_document=False,
            warnings=parsed.warnings,
        )

    def _store_upload(self, upload: DocumentUpload) -> StoredDocumentResult:
        if upload.file_path:
            return self.storage.store_document_path(self.notary_id, upload.filename, upload.file_path, upload.content_type)
        if upload.content is None:
            raise ValueError(f"Upload {upload.filename!r} has no content or file_path.")
        return self.storage.store_document(self.notary_id, upload.filename, upload.content, upload.content_type)

    def _parse_upload(self, upload: DocumentUpload) -> ParsedDocument:
        if upload.file_path:
            return self.parser.parse_path(Path(upload.file_path))
        if upload.content is None:
            raise ValueError(f"Upload {upload.filename!r} has no content or file_path.")
        return self.parser.parse_bytes(upload.content, filename=upload.filename)

    def _get_or_create_document(self, upload: DocumentUpload, stored: StoredDocumentResult) -> tuple[NotarialDocument, bool]:
        existing = (
            self.db.query(NotarialDocument)
            .filter(NotarialDocument.notary_id == self.notary_id, NotarialDocument.content_hash == stored.content_hash)
            .first()
        )
        if existing is not None:
            return existing, False

        document = NotarialDocument(
            notary_id=self.notary_id,
            content_hash=stored.content_hash,
            filename=stored.filename,
            storage_path=stored.storage_path,
            storage_backend=stored.storage_backend,
            content_type=stored.content_type,
            file_size_bytes=stored.file_size_bytes,
            processing_status=DocumentProcessingStatus.STORED.value,
            metadata_json=_json({"upload": upload.metadata, "source_path": upload.source_path}),
        )
        try:
            with self.db.begin_nested():
                self.db.add(document)
                self.db.flush()
            return document, True
        except IntegrityError:
            existing = (
                self.db.query(NotarialDocument)
                .filter(NotarialDocument.notary_id == self.notary_id, NotarialDocument.content_hash == stored.content_hash)
                .one()
            )
            return existing, False

    def _create_parse_run(self, document_id: int, parser_name: str, parser_version: str) -> NotarialDocumentParseRun:
        current_version = (
            self.db.query(NotarialDocumentParseRun.parse_version)
            .filter(NotarialDocumentParseRun.document_id == document_id, NotarialDocumentParseRun.notary_id == self.notary_id)
            .order_by(NotarialDocumentParseRun.parse_version.desc())
            .first()
        )
        parse_run = NotarialDocumentParseRun(
            notary_id=self.notary_id,
            document_id=document_id,
            parse_version=((current_version[0] if current_version else 0) + 1),
            parser_name=parser_name,
            parser_version=parser_version,
            status="running",
            is_active=False,
            started_at=_now(),
        )
        self.db.add(parse_run)
        self.db.flush()
        return parse_run

    def _persist_parsed_blocks(self, document_id: int, parse_run_id: int, parsed: ParsedDocument) -> None:
        section = NotarialDocumentSection(
            notary_id=self.notary_id,
            document_id=document_id,
            parse_run_id=parse_run_id,
            section_key="document",
            title="Documento",
            order_index=1,
            start_block_index=1 if parsed.blocks else None,
            end_block_index=len(parsed.blocks) if parsed.blocks else None,
            classification_status="unknown",
        )
        self.db.add(section)
        self.db.flush()

        for block in parsed.blocks:
            self.db.add(
                NotarialDocumentBlock(
                    notary_id=self.notary_id,
                    document_id=document_id,
                    parse_run_id=parse_run_id,
                    section_id=section.id,
                    block_index=block.block_index,
                    block_type=block.block_type.value,
                    location_key=block.location_key,
                    text=block.text,
                    text_hash=block.text_hash,
                    char_start=block.metadata.get("char_start"),
                    char_end=block.metadata.get("char_end"),
                    table_index=block.table_index,
                    row_index=block.row_index,
                    cell_index=block.cell_index,
                    paragraph_index=block.paragraph_index,
                    fixed_variable_label=block.fixed_variable_label.value,
                    semantic_type=block.semantic_type,
                    semantic_title=block.semantic_title,
                    semantic_section=block.semantic_section,
                    parser_source=block.parser_source,
                    unstructured_category=block.unstructured_category,
                    metadata_json=_json(block.metadata),
                )
            )
        parse_run = self.db.get(NotarialDocumentParseRun, parse_run_id)
        parse_run.status = "completed"
        parse_run.finished_at = _now()
        parse_run.warnings_json = json.dumps(parsed.warnings, ensure_ascii=False)
        parse_run.metadata_json = _json(parsed.metadata)

    def _activate_parse_run(self, document_id: int, parse_run_id: int) -> None:
        self.db.query(NotarialDocumentParseRun).filter(
            NotarialDocumentParseRun.notary_id == self.notary_id,
            NotarialDocumentParseRun.document_id == document_id,
            NotarialDocumentParseRun.id != parse_run_id,
        ).update({"is_active": False}, synchronize_session=False)
        parse_run = self.db.get(NotarialDocumentParseRun, parse_run_id)
        parse_run.is_active = True

    def _summary_for_document(self, document: NotarialDocument, reused: bool) -> IngestedDocumentSummary:
        return IngestedDocumentSummary(
            document_id=document.id,
            filename=document.filename,
            content_hash=document.content_hash,
            status=DocumentProcessingStatus.REUSED if reused and document.processing_status != DocumentProcessingStatus.STORED.value else DocumentProcessingStatus(document.processing_status),
            block_count=self._active_block_count(document.id),
            storage_path=document.storage_path,
            reused_existing_document=reused,
        )

    def _active_block_count(self, document_id: int) -> int:
        active = (
            self.db.query(NotarialDocumentParseRun.id)
            .filter(
                NotarialDocumentParseRun.notary_id == self.notary_id,
                NotarialDocumentParseRun.document_id == document_id,
                NotarialDocumentParseRun.is_active.is_(True),
            )
            .first()
        )
        if active is None:
            return 0
        return self.db.query(NotarialDocumentBlock).filter(NotarialDocumentBlock.parse_run_id == active.id).count()

    def _link_batch_item(
        self,
        batch_id: int,
        item_index: int,
        upload: DocumentUpload,
        stored: StoredDocumentResult,
        document_id: int,
        status: str,
    ) -> None:
        item = NotarialDocumentBatchItem(
            batch_id=batch_id,
            document_id=document_id,
            notary_id=self.notary_id,
            item_index=item_index,
            original_filename=upload.filename,
            content_hash=stored.content_hash,
            status=status,
            metadata_json=_json(upload.metadata),
        )
        self.db.add(item)
        self.db.flush()

    @staticmethod
    def _batch_result(batch: NotarialDocumentBatch, summaries: list[IngestedDocumentSummary], warnings: list[str]) -> IngestBatchResult:
        return IngestBatchResult(
            batch_id=batch.id,
            batch_key=batch.batch_key,
            status=BatchStatus(batch.status),
            total_documents=batch.total_documents,
            unique_documents=batch.unique_documents,
            duplicate_documents=batch.duplicate_documents,
            error_documents=batch.error_documents,
            documents=summaries,
            warnings=warnings,
        )


def _json(value: object) -> str:
    return json.dumps(value or {}, ensure_ascii=False, sort_keys=True)


def _now() -> datetime:
    return datetime.now(timezone.utc)
