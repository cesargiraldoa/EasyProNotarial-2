from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PersonBase(BaseModel):
    document_type: str = Field(min_length=2, max_length=40)
    document_number: str = Field(min_length=3, max_length=40)
    full_name: str = Field(min_length=3, max_length=160)
    sex: str | None = Field(default=None, max_length=20)
    nationality: str | None = Field(default=None, max_length=80)
    marital_status: str | None = Field(default=None, max_length=40)
    profession: str | None = Field(default=None, max_length=120)
    municipality: str | None = Field(default=None, max_length=120)
    is_transient: bool = False
    phone: str | None = Field(default=None, max_length=40)
    address: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = None
    metadata_json: str = "{}"


class PersonCreate(PersonBase):
    pass


class PersonUpdate(PersonBase):
    pass


class PersonSummary(PersonBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
