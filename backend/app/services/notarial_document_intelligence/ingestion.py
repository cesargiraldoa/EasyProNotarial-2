from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.services.storage import download_storage_bytes
from app.models.notarial_document_intelligence import (
    NotarialDocument,
    NotarialDocumentBatch,
    NotarialDocumentBatchItem,
    NotarialDocumentBlock,
    NotarialDocumentSection,
)
from app.services.notarial_document_intelligence.contracts import (
    BatchStatus,
    DocumentProcessingStatus,
    DocumentUpload,
    IngestBatchRequest,
    IngestBatchResult,
    IngestedDocumentSummary,
)
from app.services.notarial_document_intelligence.parser import NotarialDocumentParser
from app.services.notarial_document_intelligence.storage import NotarialIntelligenceStorage, StoredDocumentResult


class NotarialDocumentIngestionService:
    def __init__(
        self,
        db: Session,
        storage: NotarialIntelligenceStorage | None = None,
        parser: NotarialDocumentParser | None = None,
    ) -> None:
        self.db = db
        self.storage = storage or NotarialIntelligenceStorage()
        self.parser = parser or NotarialDocumentParser()

    def ingest_batch(self, request: IngestBatchRequest) -> IngestBatchResult:
        batch = NotarialDocumentBatch(
            batch_key=f"batch_{uuid.uuid4().hex}",
            name=request.name,
            source_type=request.source_type,
            status=BatchStatus.RUNNING.value,
            metadata_json=_json(request.metadata),
            started_at=_now(),
        )
        self.db.add(batch)
        self.db.flush()

        summaries: list[IngestedDocumentSummary] = []
        warnings: list[str] = []
        unique_documents = 0
        duplicate_documents = 0
        error_documents = 0

        for item_index, upload in enumerate(request.documents, start=1):
            try:
                with self.db.begin_nested():
                    summary = self._ingest_document(batch.id, item_index, upload)
                summaries.append(summary)
                warnings.extend(summary.warnings)
                if summary.reused_existing_document:
                    duplicate_documents += 1
                else:
                    unique_documents += 1
            except Exception as exc:
                error_documents += 1
                warnings.append(f"{upload.filename}: {type(exc).__name__}")

        batch.total_documents = len(request.documents)
        batch.unique_documents = unique_documents
        batch.duplicate_documents = duplicate_documents
        batch.error_documents = error_documents
        batch.status = BatchStatus.ERROR.value if error_documents else BatchStatus.COMPLETED.value
        batch.finished_at = _now()
        if error_documents:
            batch.error_message = f"{error_documents} document(s) failed during ingestion."
        self.db.commit()

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

    def _ingest_document(self, batch_id: int, item_index: int, upload: DocumentUpload) -> IngestedDocumentSummary:
        stored = self.storage.store_document(upload.filename, upload.content, upload.content_type)
        existing = self.db.query(NotarialDocument).filter(NotarialDocument.content_hash == stored.content_hash).first()
        if existing is not None:
            self._link_batch_item(batch_id, item_index, upload, stored, existing.id, "reused")
            return IngestedDocumentSummary(
                document_id=existing.id,
                filename=existing.filename,
                content_hash=existing.content_hash,
                status=DocumentProcessingStatus.REUSED,
                block_count=self.db.query(NotarialDocumentBlock).filter(NotarialDocumentBlock.document_id == existing.id).count(),
                storage_path=existing.storage_path,
                reused_existing_document=True,
            )

        parsed = self.parser.parse_bytes(upload.content, filename=upload.filename)
        document = NotarialDocument(
            content_hash=stored.content_hash,
            filename=stored.filename,
            storage_path=stored.storage_path,
            storage_backend=stored.storage_backend,
            content_type=stored.content_type,
            file_size_bytes=stored.file_size_bytes,
            parser_name=parsed.parser_name,
            parser_version=parsed.parser_version,
            processing_status=DocumentProcessingStatus.PARSED.value,
            metadata_json=_json({"upload": upload.metadata, "parse": parsed.metadata, "warnings": parsed.warnings}),
        )
        self.db.add(document)
        self.db.flush()

        section = NotarialDocumentSection(
            document_id=document.id,
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
                    document_id=document.id,
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
                    metadata_json=_json(block.metadata),
                )
            )

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

    def reparse_document(self, document_id: int) -> IngestedDocumentSummary:
        document = self.db.get(NotarialDocument, document_id)
        if document is None:
            raise ValueError(f"Document {document_id} not found.")

        content = download_storage_bytes(document.storage_path)
        parsed = self.parser.parse_bytes(content, filename=document.filename)

        self.db.query(NotarialDocumentBlock).filter(NotarialDocumentBlock.document_id == document.id).delete()
        self.db.query(NotarialDocumentSection).filter(NotarialDocumentSection.document_id == document.id).delete()
        self.db.flush()

        section = NotarialDocumentSection(
            document_id=document.id,
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
                    document_id=document.id,
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
                    metadata_json=_json(block.metadata),
                )
            )

        document.parser_name = parsed.parser_name
        document.parser_version = parsed.parser_version
        document.processing_status = DocumentProcessingStatus.PARSED.value
        document.metadata_json = _json({"reparse": parsed.metadata, "warnings": parsed.warnings})
        document.error_message = None
        self.db.commit()

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
            item_index=item_index,
            original_filename=upload.filename,
            content_hash=stored.content_hash,
            status=status,
            metadata_json=_json(upload.metadata),
        )
        self.db.add(item)
        self.db.flush()


def _json(value: object) -> str:
    return json.dumps(value or {}, ensure_ascii=False, sort_keys=True)


def _now() -> datetime:
    return datetime.now(timezone.utc)
