from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

CommercialStatus = Literal[
    "prospecto",
    "contactado",
    "en seguimiento",
    "reunión agendada",
    "propuesta enviada",
    "negociación",
    "cerrado ganado",
    "cerrado perdido",
    "no interesado",
]
PriorityLevel = Literal["baja", "media", "alta", "crítica"]
PotentialLevel = Literal["bajo", "medio", "alto", "estratégico"]


class NotaryAuditLogSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_type: str
    field_name: str | None = None
    old_value: str | None = None
    new_value: str | None = None
    comment: str | None = None
    actor_user_id: int | None = None
    actor_user_name: str | None = None
    created_at: datetime


class NotaryBase(BaseModel):
    legal_name: str = Field(min_length=2, max_length=160)
    commercial_name: str = Field(min_length=2, max_length=120)
    city: str = Field(min_length=2, max_length=80)
    department: str = Field(default="Antioquia", min_length=2, max_length=80)
    municipality: str = Field(min_length=2, max_length=120)
    notary_label: str = Field(min_length=1, max_length=160)
    address: str | None = Field(default=None, max_length=255)
    phone: str | None = None
    email: EmailStr | None = None
    current_notary_name: str | None = Field(default=None, max_length=160)
    business_hours: str | None = None
    logo_url: str | None = Field(default=None, max_length=255)
    primary_color: str = Field(default="#0D2E5D", max_length=20)
    secondary_color: str = Field(default="#4D5B7C", max_length=20)
    base_color: str = Field(default="#F4F7FB", max_length=20)
    institutional_data: str = Field(default="", max_length=4000)
    commercial_status: CommercialStatus = "prospecto"
    commercial_owner: str | None = Field(default=None, max_length=120)
    commercial_owner_user_id: int | None = None
    main_contact_name: str | None = Field(default=None, max_length=160)
    main_contact_title: str | None = Field(default=None, max_length=120)
    commercial_phone: str | None = None
    commercial_email: EmailStr | None = None
    last_management_at: datetime | None = None
    next_management_at: datetime | None = None
    commercial_notes: str | None = None
    priority: PriorityLevel = "media"
    lead_source: str | None = Field(default=None, max_length=120)
    potential: PotentialLevel | None = None
    internal_observations: str | None = None
    is_active: bool = True


class NotaryCreate(NotaryBase):
    pass


class NotaryUpdate(NotaryBase):
    pass


class NotaryStatusUpdate(BaseModel):
    is_active: bool


class CommercialActivityBase(BaseModel):
    occurred_at: datetime
    management_type: str = Field(min_length=2, max_length=60)
    comment: str = Field(min_length=2, max_length=4000)
    responsible: str | None = Field(default=None, max_length=120)
    responsible_user_id: int | None = None
    result: str | None = Field(default=None, max_length=160)
    next_action: str | None = None


class CommercialActivityCreate(CommercialActivityBase):
    pass


class CommercialActivitySummary(CommercialActivityBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    notary_id: int
    responsible_user_name: str | None = None


class NotarySummary(NotaryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    accent_color: str
    activity_count: int = 0
    commercial_owner_display: str | None = None
    commercial_owner_user_name: str | None = None


class NotaryDetail(NotarySummary):
    commercial_activities: list[CommercialActivitySummary] = []
    crm_audit_logs: list[NotaryAuditLogSummary] = []


class NotaryImportSourceRow(BaseModel):
    MUNICIPIO: str = Field(min_length=2, max_length=120)
    NOTARÍA: str = Field(min_length=1, max_length=160)
    DIRECCIÓN: str | None = Field(default=None, max_length=255)
    TELÉFONO: str | None = None
    CORREO_ELECTRÓNICO: EmailStr | None = None
    NOTARIO_A: str | None = Field(default=None, max_length=160, alias="NOTARIO/A")
    HORARIO: str | None = None

    model_config = ConfigDict(populate_by_name=True)


class NotaryImportRequest(BaseModel):
    rows: list[NotaryImportSourceRow] = Field(min_length=1)
    overwrite_existing: bool = True


class NotaryFileImportRequest(BaseModel):
    source_path: str = Field(default=r"C:\EasyProNotarial-2\Archivos_referencia\Notarias_Antioquia_EasyProNotarial.xlsx")
    overwrite_existing: bool = True


class NotaryImportResult(BaseModel):
    row_number: int
    action: str
    notary_id: int | None = None
    slug: str | None = None
    duplicate_key: str | None = None


class NotaryImportRowError(BaseModel):
    row_number: int
    municipality: str | None = None
    notary_label: str | None = None
    error: str


class NotaryImportSummary(BaseModel):
    source_path: str | None = None
    processed: int
    created: int
    updated: int
    omitted: int
    errors: list[NotaryImportRowError]
    results: list[NotaryImportResult]


class NotaryFilterOptions(BaseModel):
    municipalities: list[str]
    commercial_owners: list[str]
    priorities: list[str]
    commercial_statuses: list[str]


