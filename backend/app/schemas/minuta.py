from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class MarkedTemplateFieldSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    key: str = Field(min_length=1, max_length=120)
    label: str = Field(min_length=1, max_length=160)
    section: str = Field(min_length=1, max_length=120)
    occurrences: int = Field(ge=1)
    marker_types: list[str] = Field(default_factory=list)
    raw_markers: list[str] = Field(default_factory=list)


class MarkedTemplateDetectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    fields: list[MarkedTemplateFieldSummary] = Field(default_factory=list)
    total_fields: int = Field(ge=0)
    total_occurrences: int = Field(ge=0)
    marker_types: dict[str, int] = Field(default_factory=dict)
