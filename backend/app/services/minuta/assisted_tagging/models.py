from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal


JobStatus = Literal[
    "uploaded",
    "processing",
    "pretagged",
    "human_review",
    "approved",
    "rejected",
    "failed",
    "saved_to_library",
]


@dataclass
class DocxTextBlock:
    id: str
    location: str
    text: str
    char_count: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DocxStructure:
    blocks: list[DocxTextBlock]
    filename: str
    paragraph_count: int
    table_count: int

    def to_llm_payload(self) -> dict[str, Any]:
        return {
            "filename": self.filename,
            "paragraph_count": self.paragraph_count,
            "table_count": self.table_count,
            "blocks": [block.to_dict() for block in self.blocks],
        }

    def to_dict(self) -> dict[str, Any]:
        return self.to_llm_payload()


@dataclass
class TaggingFieldProposal:
    field_code: str
    label: str
    text: str
    section: str = "general"
    confidence: float = 0.6
    block_id: str | None = None
    reason: str | None = None
    source: str = "llm"
    occurrences: int = 1
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TaggingValidationResult:
    fields: list[TaggingFieldProposal]
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "fields": [field.to_dict() for field in self.fields],
            "warnings": list(self.warnings),
        }


@dataclass
class ApprovedTemplateResult:
    fields: list[TaggingFieldProposal]
    warnings: list[str]
    technical_docx: bytes
    variable_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "fields": [field.to_dict() for field in self.fields],
            "warnings": list(self.warnings),
            "variable_count": self.variable_count,
        }
