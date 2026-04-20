from __future__ import annotations

import json
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.person import PersonCreate, PersonSummary
from app.schemas.template import TemplateSummary

CaseStateCode = Literal[
    "borrador",
    "en_diligenciamiento",
    "revision_cliente",
    "ajustes_solicitados",
    "revision_aprobador",
    "devuelto_aprobador",
    "revision_notario",
    "rechazado_notario",
    "aprobado_notario",
    "generado",
    "firmado_cargado",
    "cerrado",
]


class CaseStateDefinitionSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_type: str
    code: str
    label: str
    step_order: int
    is_initial: bool
    is_terminal: bool
    is_active: bool


class CaseTimelineEventSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_type: str
    from_state: str | None = None
    to_state: str | None = None
    comment: str | None = None
    metadata_json: str | None = None
    actor_user_id: int | None = None
    actor_user_name: str | None = None
    created_at: datetime


class CaseWorkflowEventSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_type: str
    actor_user_id: int | None = None
    actor_user_name: str | None = None
    actor_role_code: str | None = None
    from_state: str | None = None
    to_state: str | None = None
    field_name: str | None = None
    old_value: str | None = None
    new_value: str | None = None
    comment: str | None = None
    approved_version_id: int | None = None
    metadata_json: str | None = None
    created_at: datetime


class CaseCommentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_by_user_id: int | None = None
    created_by_user_name: str | None = None
    comment: str | None = None
    note: str | None = None
    created_at: datetime


class CaseParticipantPayload(BaseModel):
    role_code: str = Field(min_length=2, max_length=80)
    role_label: str = Field(min_length=2, max_length=120)
    person_id: int | None = None
    person: PersonCreate | None = None
    legal_entity_id: int | None = None


class CaseParticipantSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role_code: str
    role_label: str
    person_id: int
    person: PersonSummary
    snapshot_json: str
    created_at: datetime
    updated_at: datetime


class CaseActDataPayload(BaseModel):
    data_json: str = "{}"


class CaseActDataSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_id: int
    data_json: str
    gari_draft_text: str | None = None
    created_at: datetime
    updated_at: datetime

    @property
    def data(self) -> dict:
        try:
            return json.loads(self.data_json or "{}")
        except json.JSONDecodeError:
            return {}


class CaseDocumentVersionSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    version_number: int
    file_format: str
    storage_path: str
    original_filename: str
    generated_from_template_id: int | None = None
    created_by_user_id: int | None = None
    created_by_user_name: str | None = None
    placeholder_snapshot_json: str
    created_at: datetime
    download_url: str | None = None


class CaseDocumentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: str
    title: str
    current_version_number: int
    versions: list[CaseDocumentVersionSummary] = []


class CaseBase(BaseModel):
    notary_id: int
    template_id: int | None = None
    case_type: str = Field(min_length=2, max_length=80)
    act_type: str = Field(min_length=2, max_length=120)
    current_state: CaseStateCode = "borrador"
    current_owner_user_id: int | None = None
    client_user_id: int | None = None
    protocolist_user_id: int | None = None
    approver_user_id: int | None = None
    titular_notary_user_id: int | None = None
    substitute_notary_user_id: int | None = None
    requires_client_review: bool = False
    final_signed_uploaded: bool = False
    metadata_json: str = "{}"


class CaseCreate(CaseBase):
    consecutive: int | None = None
    year: int | None = None


class CaseCreateFromTemplate(BaseModel):
    template_id: int
    notary_id: int
    client_user_id: int | None = None
    current_owner_user_id: int | None = None
    protocolist_user_id: int | None = None
    approver_user_id: int | None = None
    titular_notary_user_id: int | None = None
    substitute_notary_user_id: int | None = None
    requires_client_review: bool = False
    metadata_json: str = "{}"


class CaseUpdate(CaseBase):
    consecutive: int
    year: int


class CaseStateUpdate(BaseModel):
    current_state: CaseStateCode
    comment: str | None = Field(default=None, max_length=4000)


class CaseOwnerUpdate(BaseModel):
    current_owner_user_id: int | None = None
    comment: str | None = Field(default=None, max_length=4000)


class CaseTimelineEventCreate(BaseModel):
    comment: str = Field(min_length=2, max_length=4000)
    metadata_json: str | None = None


class CaseCommentCreate(BaseModel):
    comment: str = Field(min_length=2, max_length=4000)


class CaseInternalNoteCreate(BaseModel):
    note: str = Field(min_length=2, max_length=4000)


class DraftGenerationRequest(BaseModel):
    comment: str | None = None


class GariGenerationRequest(BaseModel):
    comment: str | None = None
    correction_text: str | None = None


class ApprovalRequest(BaseModel):
    role_code: str = Field(min_length=2, max_length=80)
    comment: str | None = None


class ExportRequest(BaseModel):
    file_format: Literal["docx", "pdf"]


class FinalUploadRequest(BaseModel):
    filename: str = Field(min_length=3, max_length=255)
    content_base64: str = Field(min_length=10)
    comment: str | None = None


class CaseSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    notary_id: int
    notary_label: str
    template_id: int | None = None
    template_name: str | None = None
    case_type: str
    act_type: str
    consecutive: int
    year: int
    internal_case_number: str | None = None
    official_deed_number: str | None = None
    official_deed_year: int | None = None
    current_state: str
    current_owner_user_id: int | None = None
    current_owner_user_name: str | None = None
    created_by_user_id: int | None = None
    created_by_user_name: str | None = None
    client_user_id: int | None = None
    client_user_name: str | None = None
    protocolist_user_id: int | None = None
    protocolist_user_name: str | None = None
    approver_user_id: int | None = None
    approver_user_name: str | None = None
    titular_notary_user_id: int | None = None
    titular_notary_user_name: str | None = None
    substitute_notary_user_id: int | None = None
    substitute_notary_user_name: str | None = None
    requires_client_review: bool
    final_signed_uploaded: bool
    approved_at: datetime | None = None
    approved_by_user_id: int | None = None
    approved_by_user_name: str | None = None
    approved_by_role_code: str | None = None
    approved_document_version_id: int | None = None
    metadata_json: str
    created_at: datetime
    updated_at: datetime

    @property
    def metadata(self) -> dict:
        try:
            return json.loads(self.metadata_json or "{}")
        except json.JSONDecodeError:
            return {}


class CaseDetail(CaseSummary):
    template: TemplateSummary | None = None
    state_definitions: list[CaseStateDefinitionSummary] = []
    timeline_events: list[CaseTimelineEventSummary] = []
    workflow_events: list[CaseWorkflowEventSummary] = []
    participants: list[CaseParticipantSummary] = []
    act_data: CaseActDataSummary | None = None
    client_comments: list[CaseCommentSummary] = []
    internal_notes: list[CaseCommentSummary] = []
    documents: list[CaseDocumentSummary] = []


class CaseFilterOptions(BaseModel):
    case_types: list[str]
    act_types: list[str]
    states: list[str]
    owners: list[str]
    notaries: list[str]
