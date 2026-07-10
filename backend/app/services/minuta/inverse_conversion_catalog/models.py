from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from sqlalchemy import CheckConstraint, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


ALLOWED_REVIEW_STATUSES = ("draft", "suggested", "approved", "deprecated", "conflict", "error")
GENERATED_REVIEW_STATUSES = ("draft", "suggested", "conflict", "error")


def status_check(column_name: str) -> CheckConstraint:
    quoted = ", ".join(f"'{status}'" for status in ALLOWED_REVIEW_STATUSES)
    return CheckConstraint(f"{column_name} IN ({quoted})", name=f"ck_{column_name}_review_status")


class FieldDefinition(Base, TimestampMixin):
    __tablename__ = "field_definitions"
    __table_args__ = (status_check("status"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    field_code: Mapped[str] = mapped_column(String(160), nullable=False, unique=True, index=True)
    display_name: Mapped[str | None] = mapped_column(String(240), nullable=True)
    data_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    field_group: Mapped[str | None] = mapped_column(String(120), nullable=True)
    legal_role: Mapped[str | None] = mapped_column(String(120), nullable=True)
    act_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="suggested")
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    source: Mapped[str | None] = mapped_column(String(160), nullable=True)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class FieldAlias(Base, TimestampMixin):
    __tablename__ = "field_aliases"
    __table_args__ = (status_check("status"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    raw_field_code: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    canonical_field_code: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    field_definition_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("field_definitions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    frequency: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="suggested")
    source: Mapped[str | None] = mapped_column(String(160), nullable=True)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class CorpusDocument(Base, TimestampMixin):
    __tablename__ = "corpus_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(260), nullable=False, index=True)
    source_zip: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    notary_name: Mapped[str | None] = mapped_column(String(240), nullable=True, index=True)
    project_name: Mapped[str | None] = mapped_column(String(240), nullable=True, index=True)
    document_type: Mapped[str | None] = mapped_column(String(160), nullable=True)
    act_type: Mapped[str | None] = mapped_column(String(160), nullable=True, index=True)
    is_tagged: Mapped[bool] = mapped_column(nullable=False, default=False)
    marker_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    red_text_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    processing_status: Mapped[str] = mapped_column(String(40), nullable=False, default="draft")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class CorpusDocumentField(Base, TimestampMixin):
    __tablename__ = "corpus_document_fields"
    __table_args__ = (status_check("status"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    corpus_document_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("corpus_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    raw_field_code: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    canonical_field_code: Mapped[str | None] = mapped_column(String(160), nullable=True, index=True)
    example_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    occurrences: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="draft")
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class FieldPattern(Base, TimestampMixin):
    __tablename__ = "field_patterns"
    __table_args__ = (status_check("status"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    field_definition_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("field_definitions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    raw_field_code: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    canonical_field_code: Mapped[str | None] = mapped_column(String(160), nullable=True, index=True)
    notary_name: Mapped[str | None] = mapped_column(String(240), nullable=True, index=True)
    project_name: Mapped[str | None] = mapped_column(String(240), nullable=True, index=True)
    document_type: Mapped[str | None] = mapped_column(String(160), nullable=True)
    act_type: Mapped[str | None] = mapped_column(String(160), nullable=True, index=True)
    text_before: Mapped[str | None] = mapped_column(Text, nullable=True)
    text_after: Mapped[str | None] = mapped_column(Text, nullable=True)
    example_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    pattern_source_file: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    frequency: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="draft")
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


@dataclass(frozen=True)
class MarkerLocation:
    paragraph_index: int | None = None
    table_index: int | None = None
    row_index: int | None = None
    cell_index: int | None = None

    def label(self) -> str:
        parts: list[str] = []
        if self.table_index is not None:
            parts.append(f"table {self.table_index}")
            if self.row_index is not None:
                parts.append(f"row {self.row_index}")
            if self.cell_index is not None:
                parts.append(f"cell {self.cell_index}")
        if self.paragraph_index is not None:
            parts.append(f"paragraph {self.paragraph_index}")
        return " ".join(parts) or "unknown"


@dataclass(frozen=True)
class MarkerOccurrence:
    raw_marker: str
    raw_field_code: str
    text: str
    text_before: str
    text_after: str
    location: MarkerLocation
    start_index: int
    end_index: int


@dataclass(frozen=True)
class RedTextOccurrence:
    text: str
    location: MarkerLocation


@dataclass(frozen=True)
class ExtractedPattern:
    raw_field_code: str
    canonical_field_code: str | None
    text_before: str
    text_after: str
    location: MarkerLocation
    confidence: float
    pattern_source_file: str | None = None


@dataclass(frozen=True)
class AliasSuggestion:
    raw_field_code: str
    canonical_field_code: str
    frequency: int
    status: str
    confidence: float
    reason: str
    context_samples: tuple[str, ...] = ()


@dataclass
class ImportedDocument:
    filename: str
    source_zip: str | None
    source_path: str
    notary_name: str | None = None
    project_name: str | None = None
    document_type: str | None = None
    act_type: str | None = None
    is_tagged: bool = False
    marker_count: int = 0
    red_text_count: int = 0
    processing_status: str = "draft"
    error_message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime | None = None
    fields: list["ImportedField"] = field(default_factory=list)
    patterns: list[ExtractedPattern] = field(default_factory=list)


@dataclass(frozen=True)
class ImportedField:
    raw_field_code: str
    canonical_field_code: str | None
    occurrences: int
    example_value: str | None = None
    status: str = "draft"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ImportResult:
    documents: list[ImportedDocument] = field(default_factory=list)
    field_frequency: dict[str, int] = field(default_factory=dict)
    patterns: list[ExtractedPattern] = field(default_factory=list)
    aliases: list[AliasSuggestion] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)

    @property
    def processed_count(self) -> int:
        return sum(1 for document in self.documents if document.processing_status == "suggested")

    @property
    def error_count(self) -> int:
        return sum(1 for document in self.documents if document.processing_status in {"error", "unsupported"})
