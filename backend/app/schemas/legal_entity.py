from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class LegalEntityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nit: str
    name: str
    legal_representative: str | None = None
    municipality: str | None = None
    address: str | None = None
    phone: str | None = None
    email: str | None = None


class LegalEntityCreate(BaseModel):
    nit: str = Field(min_length=3, max_length=40)
    name: str = Field(min_length=2, max_length=200)
    legal_representative: str | None = Field(default=None, max_length=160)
    municipality: str | None = Field(default=None, max_length=120)
    address: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=40)
    email: str | None = Field(default=None, max_length=120)


class LegalEntityRepresentativeCreate(BaseModel):
    person_id: int
    power_type: str | None = Field(default=None, max_length=120)


class LegalEntityRepresentativeOut(BaseModel):
    id: int
    legal_entity_id: int
    person_id: int
    person_name: str
    person_document: str
    power_type: str | None = None
    is_active: bool
