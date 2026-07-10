from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class MarkedCandidateContext:
    location: str
    before: str = ""
    after: str = ""

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "MarkedCandidateContext":
        return cls(
            location=str(payload.get("location") or ""),
            before=str(payload.get("before") or ""),
            after=str(payload.get("after") or ""),
        )


@dataclass(frozen=True)
class MarkedCandidate:
    id: str
    text: str
    suggested_key: str
    label: str = ""
    status: str = "pending"
    confidence: float = 0.0
    occurrences: int = 0
    contexts: tuple[MarkedCandidateContext, ...] = field(default_factory=tuple)
    type: str = ""
    section: str = ""

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "MarkedCandidate":
        contexts = tuple(
            MarkedCandidateContext.from_dict(item)
            for item in payload.get("contexts", [])
            if isinstance(item, dict)
        )
        return cls(
            id=str(payload.get("id") or ""),
            text=str(payload.get("text") or ""),
            suggested_key=str(payload.get("suggested_key") or ""),
            label=str(payload.get("label") or ""),
            status=str(payload.get("status") or "pending"),
            confidence=float(payload.get("confidence") or 0.0),
            occurrences=int(payload.get("occurrences") or 0),
            contexts=contexts,
            type=str(payload.get("type") or ""),
            section=str(payload.get("section") or ""),
        )

    @property
    def is_accepted(self) -> bool:
        return self.status == "accepted" and bool(self.text.strip())


@dataclass(frozen=True)
class MarkedDocxWriteResult:
    output_path: Path
    filename: str
    accepted_candidates: int
    marked_occurrences: int
    skipped_candidates: int = 0
