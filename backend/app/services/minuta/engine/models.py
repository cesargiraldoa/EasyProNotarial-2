from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class RenderSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    BLOCKER = "blocker"


@dataclass
class RenderIssue:
    code: str
    message: str
    severity: RenderSeverity
    field_key: str | None = None
    placeholder: str | None = None
    location: str | None = None
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class PlaceholderAudit:
    placeholder: str
    field_key: str | None
    inserted_value: str
    location: str
    color_applied: str | None = None
    style_preserved: bool = False
    replaced: bool = False


@dataclass
class RenderAudit:
    replaced: list[PlaceholderAudit] = field(default_factory=list)
    empty: list[PlaceholderAudit] = field(default_factory=list)
    missing: list[PlaceholderAudit] = field(default_factory=list)
    unresolved_placeholders: list[str] = field(default_factory=list)
    residual_tokens: list[str] = field(default_factory=list)
    issues: list[RenderIssue] = field(default_factory=list)
    structure_before: dict[str, int] = field(default_factory=dict)
    structure_after: dict[str, int] = field(default_factory=dict)
    technical_tabs_resolved: int = 0
    notarial_dash_sequences_preserved: int = 0
    red_runs_detected: int = 0

    @property
    def warnings(self) -> list[RenderIssue]:
        return [issue for issue in self.issues if issue.severity == RenderSeverity.WARNING]

    @property
    def blockers(self) -> list[RenderIssue]:
        return [issue for issue in self.issues if issue.severity == RenderSeverity.BLOCKER]

    def to_dict(self) -> dict[str, Any]:
        return {
            "replaced": [item.__dict__ for item in self.replaced],
            "empty": [item.__dict__ for item in self.empty],
            "missing": [item.__dict__ for item in self.missing],
            "unresolved_placeholders": self.unresolved_placeholders,
            "residual_tokens": self.residual_tokens,
            "issues": [
                {**issue.__dict__, "severity": issue.severity.value}
                for issue in self.issues
            ],
            "structure_before": self.structure_before,
            "structure_after": self.structure_after,
            "technical_tabs_resolved": self.technical_tabs_resolved,
            "notarial_dash_sequences_preserved": self.notarial_dash_sequences_preserved,
            "red_runs_detected": self.red_runs_detected,
        }


@dataclass
class NotarialPerson:
    role: str
    full_name: str = ""
    document_type: str = ""
    document_number: str = ""
    gender: str | None = None
    nationality: str = ""
    marital_status: str = ""


@dataclass
class NotarialMoneyValue:
    key: str
    numeric_text: str
    formatted_text: str
    text_in_words: str = ""


@dataclass
class NotarialDateValue:
    key: str
    iso_value: str
    notarial_text: str


@dataclass
class TemplatePlaceholder:
    marker: str
    field_key: str | None
    location: str


@dataclass
class TemplateAnalysis:
    placeholders: list[TemplatePlaceholder] = field(default_factory=list)
    unresolved_placeholders: list[str] = field(default_factory=list)
    residual_tokens: list[str] = field(default_factory=list)
    required_actor_roles: set[str] = field(default_factory=set)
    structure: dict[str, int] = field(default_factory=dict)


@dataclass
class NotarialRenderContext:
    values: dict[str, str]
    normalized_values: dict[str, str]
    fields: list[dict[str, Any]]
    people: list[NotarialPerson] = field(default_factory=list)
    money_values: list[NotarialMoneyValue] = field(default_factory=list)
    dates: list[NotarialDateValue] = field(default_factory=list)


@dataclass
class NotarialRenderResult:
    output_path: Path
    audit: RenderAudit
    statistics: dict[str, Any]

    @property
    def warnings(self) -> list[RenderIssue]:
        return self.audit.warnings

    @property
    def blockers(self) -> list[RenderIssue]:
        return self.audit.blockers
