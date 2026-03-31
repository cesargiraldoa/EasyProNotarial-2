from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TemplateRequiredRolePayload(BaseModel):
    role_code: str = Field(min_length=2, max_length=80)
    label: str = Field(min_length=2, max_length=120)
    is_required: bool = True
    step_order: int = 1


class TemplateFieldPayload(BaseModel):
    field_code: str = Field(min_length=2, max_length=120)
    label: str = Field(min_length=2, max_length=160)
    field_type: str = Field(default="text", max_length=40)
    section: str = Field(default="acto", max_length=80)
    is_required: bool = True
    options_json: str | None = None
    placeholder_key: str | None = None
    help_text: str | None = None
    step_order: int = 1


class TemplateUploadPayload(BaseModel):
    filename: str = Field(min_length=3, max_length=255)
    content_base64: str = Field(min_length=10)


class TemplateBase(BaseModel):
    name: str = Field(min_length=3, max_length=160)
    case_type: str = Field(default="escritura", min_length=2, max_length=80)
    document_type: str = Field(min_length=2, max_length=120)
    description: str | None = None
    scope_type: str = Field(default="global", max_length=20)
    notary_id: int | None = None
    is_active: bool = True
    internal_variable_map_json: str = "{}"
    required_roles: list[TemplateRequiredRolePayload] = []
    fields: list[TemplateFieldPayload] = []
    upload: TemplateUploadPayload | None = None


class TemplateCreate(TemplateBase):
    pass


class TemplateUpdate(TemplateBase):
    pass


class TemplateRequiredRoleSummary(TemplateRequiredRolePayload):
    model_config = ConfigDict(from_attributes=True)

    id: int


class TemplateFieldSummary(TemplateFieldPayload):
    model_config = ConfigDict(from_attributes=True)

    id: int


class TemplateSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    case_type: str
    document_type: str
    description: str | None = None
    scope_type: str
    notary_id: int | None = None
    notary_label: str | None = None
    is_active: bool
    source_filename: str | None = None
    storage_path: str | None = None
    internal_variable_map_json: str
    created_at: datetime
    updated_at: datetime
    required_roles: list[TemplateRequiredRoleSummary] = []
    fields: list[TemplateFieldSummary] = []
