from datetime import date, datetime

from pydantic import BaseModel


class DashboardFilterOption(BaseModel):
    id: int | None = None
    label: str


class DashboardFilters(BaseModel):
    date_from: date | None = None
    date_to: date | None = None
    notary_id: int | None = None
    state: str | None = None
    act_type: str | None = None
    owner_user_id: int | None = None


class DashboardKpi(BaseModel):
    key: str
    label: str
    value: int
    detail: str | None = None
    tone: str = "default"


class DashboardChartDatum(BaseModel):
    label: str
    value: int
    highlight: bool = False


class DashboardTrendDatum(BaseModel):
    label: str
    value: int


class DashboardAlert(BaseModel):
    level: str
    title: str
    detail: str


class DashboardPilotReference(BaseModel):
    notary_id: int | None = None
    notary_label: str
    municipality: str
    department: str
    total_cases: int
    active_cases: int
    finalized_cases: int
    notes: str | None = None


class DashboardSystemStatusItem(BaseModel):
    key: str
    label: str
    status: str
    detail: str


class DashboardFilterOptions(BaseModel):
    notaries: list[DashboardFilterOption]
    states: list[DashboardFilterOption]
    act_types: list[DashboardFilterOption]
    owners: list[DashboardFilterOption]


class SuperAdminDashboardResponse(BaseModel):
    generated_at: datetime
    filters: DashboardFilters
    filter_options: DashboardFilterOptions
    kpis: list[DashboardKpi]
    documents_by_notary: list[DashboardChartDatum]
    documents_by_state: list[DashboardChartDatum]
    documents_by_act_type: list[DashboardChartDatum]
    temporal_trend: list[DashboardTrendDatum]
    owner_ranking: list[DashboardChartDatum]
    operational_focus: list[DashboardChartDatum]
    critical_alerts: list[DashboardAlert]
    system_status: list[DashboardSystemStatusItem]
    pilot_reference: DashboardPilotReference | None = None
    latest_import_reference: str | None = None