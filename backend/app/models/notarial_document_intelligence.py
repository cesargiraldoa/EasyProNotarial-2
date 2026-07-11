from __future__ import annotations

import json
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import TypeDecorator

from app.models.base import Base, TimestampMixin

try:
    from pgvector.sqlalchemy import Vector as PGVector
except ImportError:  # pragma: no cover - optional outside PostgreSQL deployments
    PGVector = None


class EmbeddingVectorType(TypeDecorator):
    impl = Text
    cache_ok = True

    def __init__(self, dimensions: int = 384) -> None:
        super().__init__()
        self.dimensions = dimensions

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql" and PGVector is not None:
            return dialect.type_descriptor(PGVector(self.dimensions))
        return dialect.type_descriptor(Text())

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql" and PGVector is not None:
            if isinstance(value, str):
                return json.loads(value)
            return value
        if isinstance(value, str):
            return value
        return json.dumps([float(item) for item in value], separators=(",", ":"))

    def process_result_value(self, value, dialect):
        if value is None or isinstance(value, str):
            return value
        return json.dumps([float(item) for item in value], separators=(",", ":"))


class NotarialDocumentBatch(Base, TimestampMixin):
    __tablename__ = "notarial_document_batches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    notary_id: Mapped[int] = mapped_column(Integer, ForeignKey("notaries.id", ondelete="CASCADE"), nullable=False, index=True)
    batch_key: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(240), nullable=False)
    source_type: Mapped[str] = mapped_column(String(80), nullable=False, default="manual")
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="initialized", index=True)
    total_documents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    unique_documents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    duplicate_documents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_documents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)


class NotarialDocument(Base, TimestampMixin):
    __tablename__ = "notarial_documents"
    __table_args__ = (
        UniqueConstraint("notary_id", "content_hash", name="uq_notarial_documents_notary_hash"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    notary_id: Mapped[int] = mapped_column(Integer, ForeignKey("notaries.id", ondelete="CASCADE"), nullable=False, index=True)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String(260), nullable=False, index=True)
    storage_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    storage_backend: Mapped[str] = mapped_column(String(40), nullable=False, default="local")
    content_type: Mapped[str] = mapped_column(String(160), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    parser_name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    parser_version: Mapped[str | None] = mapped_column(String(80), nullable=True)
    processing_status: Mapped[str] = mapped_column(String(40), nullable=False, default="stored", index=True)
    document_type: Mapped[str | None] = mapped_column(String(160), nullable=True, index=True)
    document_subtype: Mapped[str | None] = mapped_column(String(160), nullable=True)
    notary_name: Mapped[str | None] = mapped_column(String(240), nullable=True, index=True)
    project_name: Mapped[str | None] = mapped_column(String(240), nullable=True, index=True)
    bank_name: Mapped[str | None] = mapped_column(String(240), nullable=True, index=True)
    family_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("notarial_document_families.id", ondelete="SET NULL"), nullable=True, index=True)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)


class NotarialDocumentBatchItem(Base):
    __tablename__ = "notarial_document_batch_items"
    __table_args__ = (
        UniqueConstraint("batch_id", "item_index", name="uq_notarial_document_batch_items_batch_index"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    batch_id: Mapped[int] = mapped_column(Integer, ForeignKey("notarial_document_batches.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id: Mapped[int] = mapped_column(Integer, ForeignKey("notarial_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    notary_id: Mapped[int] = mapped_column(Integer, ForeignKey("notaries.id", ondelete="CASCADE"), nullable=False, index=True)
    item_index: Mapped[int] = mapped_column(Integer, nullable=False)
    original_filename: Mapped[str] = mapped_column(String(260), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="processed")
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class NotarialDocumentSection(Base, TimestampMixin):
    __tablename__ = "notarial_document_sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    notary_id: Mapped[int] = mapped_column(Integer, ForeignKey("notaries.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id: Mapped[int] = mapped_column(Integer, ForeignKey("notarial_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    parse_run_id: Mapped[int] = mapped_column(Integer, ForeignKey("notarial_document_parse_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    section_key: Mapped[str] = mapped_column(String(120), nullable=False)
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    start_block_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    end_block_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    classification_status: Mapped[str] = mapped_column(String(40), nullable=False, default="unknown")
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class NotarialDocumentBlock(Base, TimestampMixin):
    __tablename__ = "notarial_document_blocks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    notary_id: Mapped[int] = mapped_column(Integer, ForeignKey("notaries.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id: Mapped[int] = mapped_column(Integer, ForeignKey("notarial_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    parse_run_id: Mapped[int] = mapped_column(Integer, ForeignKey("notarial_document_parse_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    section_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("notarial_document_sections.id", ondelete="SET NULL"), nullable=True, index=True)
    block_index: Mapped[int] = mapped_column(Integer, nullable=False)
    block_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    location_key: Mapped[str] = mapped_column(String(260), nullable=False, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    text_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    char_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    char_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    table_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    row_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cell_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    paragraph_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fixed_variable_label: Mapped[str] = mapped_column(String(40), nullable=False, default="unknown", index=True)
    semantic_type: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    semantic_title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    semantic_section: Mapped[str | None] = mapped_column(String(160), nullable=True, index=True)
    parser_source: Mapped[str] = mapped_column(String(80), nullable=False, default="python-docx")
    unstructured_category: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class NotarialDocumentParseRun(Base, TimestampMixin):
    __tablename__ = "notarial_document_parse_runs"
    __table_args__ = (
        UniqueConstraint("document_id", "parse_version", name="uq_notarial_parse_runs_document_version"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    notary_id: Mapped[int] = mapped_column(Integer, ForeignKey("notaries.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id: Mapped[int] = mapped_column(Integer, ForeignKey("notarial_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    parse_version: Mapped[int] = mapped_column(Integer, nullable=False)
    parser_name: Mapped[str] = mapped_column(String(120), nullable=False)
    parser_version: Mapped[str] = mapped_column(String(160), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="running", index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    warnings_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class NotarialTaskPublication(Base, TimestampMixin):
    __tablename__ = "notarial_task_publications"
    __table_args__ = (
        UniqueConstraint("request_key", name="uq_notarial_task_publications_request_key"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    request_key: Mapped[str] = mapped_column(String(180), nullable=False, index=True)
    notary_id: Mapped[int] = mapped_column(Integer, ForeignKey("notaries.id", ondelete="CASCADE"), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    target_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    document_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("notarial_documents.id", ondelete="CASCADE"), nullable=True, index=True)
    parse_run_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("notarial_document_parse_runs.id", ondelete="CASCADE"), nullable=True, index=True)
    task_name: Mapped[str] = mapped_column(String(180), nullable=False)
    task_args_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="pending", index=True)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    task_id: Mapped[str | None] = mapped_column(String(180), nullable=True, index=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class NotarialIntelligenceRun(Base, TimestampMixin):
    __tablename__ = "notarial_intelligence_runs"
    __table_args__ = (
        UniqueConstraint("run_key", name="uq_notarial_intelligence_runs_run_key"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_key: Mapped[str] = mapped_column(String(240), nullable=False, index=True)
    notary_id: Mapped[int] = mapped_column(Integer, ForeignKey("notaries.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("notarial_documents.id", ondelete="CASCADE"), nullable=True, index=True)
    parse_run_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("notarial_document_parse_runs.id", ondelete="SET NULL"), nullable=True, index=True)
    run_type: Mapped[str] = mapped_column(String(60), nullable=False, default="document", index=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="queued", index=True)
    classifier_version: Mapped[str] = mapped_column(String(120), nullable=False)
    embedding_version_key: Mapped[str] = mapped_column(String(240), nullable=False)
    llm_provider: Mapped[str | None] = mapped_column(String(120), nullable=True)
    llm_model: Mapped[str | None] = mapped_column(String(160), nullable=True)
    llm_mode: Mapped[str] = mapped_column(String(40), nullable=False, default="off")
    prompt_version: Mapped[str | None] = mapped_column(String(120), nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    task_id: Mapped[str | None] = mapped_column(String(180), nullable=True, index=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class NotarialDocumentEntity(Base, TimestampMixin):
    __tablename__ = "notarial_document_entities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    notary_id: Mapped[int] = mapped_column(Integer, ForeignKey("notaries.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id: Mapped[int] = mapped_column(Integer, ForeignKey("notarial_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    parse_run_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("notarial_document_parse_runs.id", ondelete="SET NULL"), nullable=True, index=True)
    block_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("notarial_document_blocks.id", ondelete="SET NULL"), nullable=True, index=True)
    entity_type: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    canonical_field_code: Mapped[str | None] = mapped_column(String(200), nullable=True, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    role: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    source: Mapped[str] = mapped_column(String(80), nullable=False, default="deterministic")
    requires_human_review: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class NotarialDocumentFamily(Base, TimestampMixin):
    __tablename__ = "notarial_document_families"
    __table_args__ = (
        UniqueConstraint("notary_id", "family_key", name="uq_notarial_document_families_notary_key"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    notary_id: Mapped[int] = mapped_column(Integer, ForeignKey("notaries.id", ondelete="CASCADE"), nullable=False, index=True)
    family_key: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(240), nullable=False)
    document_type: Mapped[str | None] = mapped_column(String(160), nullable=True, index=True)
    notary_name: Mapped[str | None] = mapped_column(String(240), nullable=True, index=True)
    project_name: Mapped[str | None] = mapped_column(String(240), nullable=True, index=True)
    bank_name: Mapped[str | None] = mapped_column(String(240), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="suggested")
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class NotarialDocumentFamilyMember(Base):
    __tablename__ = "notarial_document_family_members"
    __table_args__ = (
        UniqueConstraint("family_id", "document_id", name="uq_notarial_family_members_family_document"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    family_id: Mapped[int] = mapped_column(Integer, ForeignKey("notarial_document_families.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id: Mapped[int] = mapped_column(Integer, ForeignKey("notarial_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    source: Mapped[str] = mapped_column(String(80), nullable=False, default="deterministic")
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class NotarialDocumentCluster(Base, TimestampMixin):
    __tablename__ = "notarial_document_clusters"
    __table_args__ = (
        UniqueConstraint("notary_id", "cluster_key", name="uq_notarial_document_clusters_notary_key"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    notary_id: Mapped[int] = mapped_column(Integer, ForeignKey("notaries.id", ondelete="CASCADE"), nullable=False, index=True)
    cluster_key: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(240), nullable=False)
    cluster_type: Mapped[str] = mapped_column(String(80), nullable=False, default="document")
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="suggested")
    algorithm: Mapped[str | None] = mapped_column(String(120), nullable=True)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class NotarialDocumentClusterMember(Base):
    __tablename__ = "notarial_document_cluster_members"
    __table_args__ = (
        UniqueConstraint("cluster_id", "document_id", name="uq_notarial_cluster_members_cluster_document"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cluster_id: Mapped[int] = mapped_column(Integer, ForeignKey("notarial_document_clusters.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id: Mapped[int] = mapped_column(Integer, ForeignKey("notarial_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    similarity_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class NotarialEmbeddingVersion(Base, TimestampMixin):
    __tablename__ = "notarial_embedding_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    version_key: Mapped[str] = mapped_column(String(160), nullable=False, unique=True, index=True)
    provider: Mapped[str] = mapped_column(String(120), nullable=False)
    model_name: Mapped[str] = mapped_column(String(240), nullable=False)
    dimensions: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="shadow")
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class NotarialDocumentEmbedding(Base, TimestampMixin):
    __tablename__ = "notarial_document_embeddings"
    __table_args__ = (
        UniqueConstraint("embedding_version_id", "source_type", "source_id", name="uq_notarial_embeddings_version_source"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    notary_id: Mapped[int] = mapped_column(Integer, ForeignKey("notaries.id", ondelete="CASCADE"), nullable=False, index=True)
    embedding_version_id: Mapped[int] = mapped_column(Integer, ForeignKey("notarial_embedding_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("notarial_documents.id", ondelete="CASCADE"), nullable=True, index=True)
    source_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    source_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    embedding_dimensions: Mapped[int] = mapped_column(Integer, nullable=False, default=384)
    embedding: Mapped[str | None] = mapped_column(EmbeddingVectorType(384), nullable=True)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class NotarialDocumentEvidence(Base, TimestampMixin):
    __tablename__ = "notarial_document_evidences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    notary_id: Mapped[int] = mapped_column(Integer, ForeignKey("notaries.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("notarial_documents.id", ondelete="CASCADE"), nullable=True, index=True)
    parse_run_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("notarial_document_parse_runs.id", ondelete="SET NULL"), nullable=True, index=True)
    block_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("notarial_document_blocks.id", ondelete="SET NULL"), nullable=True, index=True)
    entity_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("notarial_document_entities.id", ondelete="SET NULL"), nullable=True, index=True)
    evidence_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(80), nullable=False, default="deterministic")
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class NotarialBlockAlignment(Base, TimestampMixin):
    __tablename__ = "notarial_block_alignments"
    __table_args__ = (
        UniqueConstraint("run_id", "target_block_id", "source_block_id", name="uq_notarial_block_alignments_run_blocks"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(Integer, ForeignKey("notarial_intelligence_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    notary_id: Mapped[int] = mapped_column(Integer, ForeignKey("notaries.id", ondelete="CASCADE"), nullable=False, index=True)
    target_document_id: Mapped[int] = mapped_column(Integer, ForeignKey("notarial_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    target_parse_run_id: Mapped[int] = mapped_column(Integer, ForeignKey("notarial_document_parse_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    target_block_id: Mapped[int] = mapped_column(Integer, ForeignKey("notarial_document_blocks.id", ondelete="CASCADE"), nullable=False, index=True)
    source_document_id: Mapped[int] = mapped_column(Integer, ForeignKey("notarial_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    source_parse_run_id: Mapped[int] = mapped_column(Integer, ForeignKey("notarial_document_parse_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    source_block_id: Mapped[int] = mapped_column(Integer, ForeignKey("notarial_document_blocks.id", ondelete="CASCADE"), nullable=False, index=True)
    alignment_key: Mapped[str] = mapped_column(String(240), nullable=False, index=True)
    structural_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    lexical_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    combined_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    label: Mapped[str] = mapped_column(String(40), nullable=False, default="unknown", index=True)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class NotarialDocumentDecision(Base, TimestampMixin):
    __tablename__ = "notarial_document_decisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    notary_id: Mapped[int] = mapped_column(Integer, ForeignKey("notaries.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("notarial_documents.id", ondelete="CASCADE"), nullable=True, index=True)
    parse_run_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("notarial_document_parse_runs.id", ondelete="SET NULL"), nullable=True, index=True)
    block_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("notarial_document_blocks.id", ondelete="SET NULL"), nullable=True, index=True)
    entity_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("notarial_document_entities.id", ondelete="SET NULL"), nullable=True, index=True)
    decision_type: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    deterministic_decision_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    llm_decision_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    hybrid_decision_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    human_decision_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="pending", index=True)
    decided_by_user_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class NotarialBenchmarkRun(Base, TimestampMixin):
    __tablename__ = "notarial_benchmark_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    notary_id: Mapped[int] = mapped_column(Integer, ForeignKey("notaries.id", ondelete="CASCADE"), nullable=False, index=True)
    corpus_version: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    model_version: Mapped[str] = mapped_column(String(240), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="completed", index=True)
    metrics_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
