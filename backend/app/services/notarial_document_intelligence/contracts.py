from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BatchStatus(str, Enum):
    INITIALIZED = "initialized"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"


class DocumentProcessingStatus(str, Enum):
    STORED = "stored"
    PARSED = "parsed"
    REUSED = "reused"
    ERROR = "error"
    UNSUPPORTED = "unsupported"


class BlockType(str, Enum):
    PARAGRAPH = "paragraph"
    TABLE_CELL_PARAGRAPH = "table_cell_paragraph"
    UNSTRUCTURED_ELEMENT = "unstructured_element"


class FixedVariableLabel(str, Enum):
    FIXED = "fixed"
    VARIABLE = "variable"
    OPTIONAL = "optional"
    UNKNOWN = "unknown"


class DocumentUpload(BaseModel):
    filename: str
    content: bytes
    content_type: str = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    source_path: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(arbitrary_types_allowed=True)


class IngestBatchRequest(BaseModel):
    name: str
    documents: list[DocumentUpload]
    source_type: str = "manual"
    metadata: dict[str, Any] = Field(default_factory=dict)


class StoredDocument(BaseModel):
    filename: str
    content_hash: str
    storage_path: str
    storage_backend: str
    content_type: str
    file_size_bytes: int


class ParsedBlock(BaseModel):
    block_index: int
    block_type: BlockType
    location_key: str
    text: str
    text_hash: str
    table_index: int | None = None
    row_index: int | None = None
    cell_index: int | None = None
    paragraph_index: int | None = None
    fixed_variable_label: FixedVariableLabel = FixedVariableLabel.UNKNOWN
    metadata: dict[str, Any] = Field(default_factory=dict)


class ParsedDocument(BaseModel):
    parser_name: str
    parser_version: str
    blocks: list[ParsedBlock]
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class IngestedDocumentSummary(BaseModel):
    document_id: int
    filename: str
    content_hash: str
    status: DocumentProcessingStatus
    block_count: int
    storage_path: str
    reused_existing_document: bool = False
    warnings: list[str] = Field(default_factory=list)


class IngestBatchResult(BaseModel):
    batch_id: int
    batch_key: str
    status: BatchStatus
    total_documents: int
    unique_documents: int
    duplicate_documents: int
    error_documents: int
    documents: list[IngestedDocumentSummary]
    warnings: list[str] = Field(default_factory=list)
