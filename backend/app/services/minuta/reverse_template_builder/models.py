from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class TextBlock:
    text: str
    location: str


@dataclass
class CandidateContext:
    location: str
    before: str
    after: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CandidateOccurrence:
    text: str
    suggested_key: str
    label: str
    section: str
    type: str
    confidence: float
    context: CandidateContext


@dataclass
class Candidate:
    id: str
    text: str
    suggested_key: str
    label: str
    section: str
    type: str
    confidence: float
    occurrences: int
    contexts: list[CandidateContext] = field(default_factory=list)
    status: str = "pending"

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["confidence"] = round(float(self.confidence), 2)
        return payload
