import { cleanNullableText, cleanText, repairText, sanitizeTextDeep } from "@/lib/text";
import { getToken } from "@/lib/auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8001";
const SESSION_KEY = "easypro2_session";

export type LoginPayload = {
  email: string;
  password: string;
};

export type CurrentUser = {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  roles: string[];
  role_codes: string[];
  permissions?: Array<{ module_code: string; can_access: boolean }>;
  default_notary?: string | null;
  default_notary_id?: number | null;
  assignments: Array<{
    id: number;
    role_id: number;
    role_code: string;
    role_name: string;
    notary_id?: number | null;
    notary_label?: string | null;
  }>;
};

export type NotaryPayload = {
  legal_name: string;
  commercial_name: string;
  city: string;
  department: string;
  municipality: string;
  notary_label: string;
  address: string;
  phone: string;
  email: string;
  current_notary_name: string;
  business_hours: string;
  logo_url: string;
  primary_color: string;
  secondary_color: string;
  base_color: string;
  institutional_data: string;
  commercial_status: string;
  commercial_owner: string;
  commercial_owner_user_id: number | null;
  main_contact_name: string;
  main_contact_title: string;
  commercial_phone: string;
  commercial_email: string;
  last_management_at: string;
  next_management_at: string;
  commercial_notes: string;
  priority: string;
  lead_source: string;
  potential: string;
  internal_observations: string;
  is_active: boolean;
};

export type CommercialActivityPayload = {
  occurred_at: string;
  management_type: string;
  comment: string;
  responsible: string;
  responsible_user_id: number | null;
  result: string;
  next_action: string;
};

export type CommercialActivityRecord = CommercialActivityPayload & {
  id: number;
  notary_id: number;
  responsible_user_name?: string | null;
};

export type NotaryAuditRecord = {
  id: number;
  event_type: string;
  field_name?: string | null;
  old_value?: string | null;
  new_value?: string | null;
  comment?: string | null;
  actor_user_id?: number | null;
  actor_user_name?: string | null;
  created_at: string;
};

export type NotaryRecord = NotaryPayload & {
  id: number;
  slug: string;
  accent_color: string;
  activity_count: number;
  commercial_owner_display?: string | null;
  commercial_owner_user_name?: string | null;
};

export type NotaryDetail = NotaryRecord & {
  commercial_activities: CommercialActivityRecord[];
  crm_audit_logs: NotaryAuditRecord[];
};

export type NotaryFilters = {
  commercial_status?: string;
  municipality?: string;
  commercial_owner?: string;
  priority?: string;
  q?: string;
};

export type NotaryFilterOptions = {
  municipalities: string[];
  commercial_owners: string[];
  priorities: string[];
  commercial_statuses: string[];
};

export type NotaryImportSummary = {
  source_path?: string | null;
  processed: number;
  created: number;
  updated: number;
  omitted: number;
  errors: Array<{ row_number: number; municipality?: string | null; notary_label?: string | null; error: string }>;
  results: Array<{ row_number: number; action: string; notary_id?: number | null; slug?: string | null; duplicate_key?: string | null }>;
};

export type RoleCatalogItem = {
  id: number;
  code: string;
  name: string;
  scope: string;
  description: string;
};

export type RolePermissionItem = {
  module_code: string;
  can_access: boolean;
};

export type UserAssignmentPayload = {
  role_code: string;
  notary_id: number | null;
};

export type UserPayload = {
  email: string;
  full_name: string;
  password: string | null;
  is_active: boolean;
  phone: string;
  job_title: string;
  default_notary_id: number | null;
  assignments: UserAssignmentPayload[];
};

export type UserRecord = {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  phone?: string | null;
  job_title?: string | null;
  default_notary_id?: number | null;
  default_notary_label?: string | null;
  roles: string[];
  assignments: Array<{ id: number; role_id: number; role_code: string; role_name: string; notary_id?: number | null; notary_label?: string | null }>;
};

export type UserOption = {
  id: number;
  full_name: string;
  email: string;
  is_active: boolean;
  default_notary_id?: number | null;
  default_notary_label?: string | null;
};

export type CasePayload = {
  notary_id: number;
  case_type: string;
  act_type: string;
  consecutive: number;
  year: number;
  current_state: string;
  current_owner_user_id: number | null;
  client_user_id: number | null;
  protocolist_user_id: number | null;
  approver_user_id: number | null;
  titular_notary_user_id: number | null;
  substitute_notary_user_id: number | null;
  requires_client_review: boolean;
  final_signed_uploaded: boolean;
  metadata_json: string;
};

export type CaseRecord = CasePayload & {
  id: number;
  notary_label: string;
  current_owner_user_name?: string | null;
  client_user_name?: string | null;
  protocolist_user_name?: string | null;
  approver_user_name?: string | null;
  titular_notary_user_name?: string | null;
  substitute_notary_user_name?: string | null;
  created_at: string;
  updated_at: string;
};

export type CaseStateDefinition = {
  id: number;
  case_type: string;
  code: string;
  label: string;
  step_order: number;
  is_initial: boolean;
  is_terminal: boolean;
  is_active: boolean;
};

export type CaseTimelineEvent = {
  id: number;
  event_type: string;
  from_state?: string | null;
  to_state?: string | null;
  comment?: string | null;
  metadata_json?: string | null;
  actor_user_id?: number | null;
  actor_user_name?: string | null;
  created_at: string;
};

export type CaseDetail = CaseRecord & {
  state_definitions: CaseStateDefinition[];
  timeline_events: CaseTimelineEvent[];
};

export type CaseFilters = {
  current_state?: string;
  case_type?: string;
  act_type?: string;
  date_from?: string;
  date_to?: string;
  notary_id?: string;
  current_owner_user_id?: string;
  q?: string;
};

export type CaseFilterOptions = {
  case_types: string[];
  act_types: string[];
  states: string[];
  owners: string[];
  notaries: string[];
};

export type DashboardFilterOption = {
  id?: number | null;
  label: string;
};

export type DashboardKpi = {
  key: string;
  label: string;
  value: number;
  detail?: string | null;
  tone: string;
};

export type DashboardChartDatum = {
  label: string;
  value: number;
  highlight: boolean;
};

export type DashboardTrendDatum = {
  label: string;
  value: number;
};

export type DashboardAlert = {
  level: string;
  title: string;
  detail: string;
};

export type DashboardSystemStatusItem = {
  key: string;
  label: string;
  status: string;
  detail: string;
};

export type DashboardPilotReference = {
  notary_id?: number | null;
  notary_label: string;
  municipality: string;
  department: string;
  total_cases: number;
  active_cases: number;
  finalized_cases: number;
  notes?: string | null;
};

export type ExecutiveDashboardFilters = {
  date_from?: string;
  date_to?: string;
  notary_id?: string;
  state?: string;
  act_type?: string;
  owner_user_id?: string;
};

export type ExecutiveDashboard = {
  generated_at: string;
  filters: {
    date_from?: string | null;
    date_to?: string | null;
    notary_id?: number | null;
    state?: string | null;
    act_type?: string | null;
    owner_user_id?: number | null;
  };
  filter_options: {
    notaries: DashboardFilterOption[];
    states: DashboardFilterOption[];
    act_types: DashboardFilterOption[];
    owners: DashboardFilterOption[];
  };
  kpis: DashboardKpi[];
  documents_by_notary: DashboardChartDatum[];
  documents_by_state: DashboardChartDatum[];
  documents_by_act_type: DashboardChartDatum[];
  temporal_trend: DashboardTrendDatum[];
  owner_ranking: DashboardChartDatum[];
  operational_focus: DashboardChartDatum[];
  critical_alerts: DashboardAlert[];
  system_status: DashboardSystemStatusItem[];
  pilot_reference?: DashboardPilotReference | null;
  latest_import_reference?: string | null;
};
function getCookieToken() {
  if (typeof document === "undefined") {
    return null;
  }
  const match = document.cookie.match(new RegExp(`(?:^|; )${SESSION_KEY}=([^;]+)`));
  return match ? decodeURIComponent(match[1]) : null;
}

function getStoredToken() {
  if (typeof window === "undefined") {
    return null;
  }
  try {
    return window.localStorage.getItem(SESSION_KEY) || window.sessionStorage.getItem(SESSION_KEY) || null;
  } catch {
    return null;
  }
}

function getSessionToken() {
  return getCookieToken() || getStoredToken();
}

function persistSessionToken(token: string, rememberSession: boolean) {
  if (typeof document !== "undefined") {
    const cookie = rememberSession
      ? `${SESSION_KEY}=${encodeURIComponent(token)}; path=/; max-age=2592000; SameSite=None; Secure`
      : `${SESSION_KEY}=${encodeURIComponent(token)}; path=/; SameSite=None; Secure`;
    document.cookie = cookie;
  }
  if (typeof window !== "undefined") {
    try {
      window.localStorage.removeItem(SESSION_KEY);
      window.sessionStorage.removeItem(SESSION_KEY);
      if (rememberSession) {
        window.localStorage.setItem(SESSION_KEY, token);
      } else {
        window.sessionStorage.setItem(SESSION_KEY, token);
      }
    } catch {
      // ignore storage failures in local env
    }
  }
}

async function parseResponse<T>(response: Response): Promise<T> {
  const text = await response.text();
  if (!response.ok) {
    if (response.status === 401) {
      throw new Error("La sesión expiró o no es válida.");
    }
    if (response.status === 403) {
      throw new Error("No tienes permisos para ejecutar esta acción.");
    }
    throw new Error(repairText(text) || "No fue posible completar la solicitud.");
  }
  if (!text.trim()) {
    return null as T;
  }
  return sanitizeTextDeep(JSON.parse(text) as T);
}

function normalizeApiError(error: unknown, fallbackMessage = "No fue posible completar la solicitud.") {
  if (error instanceof Error) {
    const message = repairText(error.message).trim();
    const normalized = message.toLowerCase();

    if (!message || normalized === "failed to fetch" || normalized.includes("networkerror") || normalized.includes("load failed")) {
      return new Error("No fue posible conectarse con el servidor. Verifica que el backend de Easy Pro esté arriba.");
    }

    if (normalized.includes("unexpected end of json input") || normalized.includes("json")) {
      return new Error("El servidor respondió con un formato inesperado. Intenta recargar la vista.");
    }

    return new Error(message);
  }

  return new Error(fallbackMessage);
}

type JsonRequestInit = Omit<RequestInit, "body"> & { body?: unknown };

export async function apiFetch<T>(path: string, init: JsonRequestInit = {}): Promise<T> {
  const token = getSessionToken();
  const headers = new Headers(init.headers ?? {});
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  const body = init.body !== undefined ? JSON.stringify(init.body) : undefined;
  try {
    const response = await fetch(`${API_URL}${path}`, {
      ...init,
      headers,
      body: body as BodyInit | null | undefined,
      cache: init.cache ?? "no-store",
      credentials: "include"
    });
    return await parseResponse<T>(response);
  } catch (error) {
    throw normalizeApiError(error);
  }
}

function normalizeDateTime(value: string) { return value.trim() || null; }

function ensureArray<T>(value: T[] | null | undefined): T[] {
  return Array.isArray(value) ? value : [];
}

function ensureStringArray(value: unknown): string[] {
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === "string").map((item) => repairText(item)) : [];
}

function normalizeUserOptionsResponse(value: unknown): UserOption[] {
  return ensureArray(value as UserOption[]);
}

function normalizeNotaryResponse(value: unknown): NotaryRecord[] {
  return ensureArray(value as NotaryRecord[]);
}

function normalizeCaseResponse(value: unknown): CaseRecord[] {
  return ensureArray(value as CaseRecord[]);
}

function normalizeCaseFilterOptions(value: unknown): CaseFilterOptions {
  const payload = typeof value === "object" && value ? (value as Partial<CaseFilterOptions>) : {};
  return {
    case_types: ensureStringArray(payload.case_types),
    act_types: ensureStringArray(payload.act_types),
    states: ensureStringArray(payload.states),
    owners: ensureStringArray(payload.owners),
    notaries: ensureStringArray(payload.notaries),
  };
}

function buildQuery(params: Record<string, string | undefined> = {}) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => { if (value && value.trim()) query.set(key, value.trim()); });
  const suffix = query.toString();
  return suffix ? `?${suffix}` : "";
}

function normalizeNotaryPayload(payload: NotaryPayload) {
  return { ...payload, department: payload.department.trim() || "Antioquia", municipality: payload.municipality.trim(), notary_label: payload.notary_label.trim(), address: payload.address.trim() || null, phone: payload.phone.trim() || null, email: payload.email.trim() || null, current_notary_name: payload.current_notary_name.trim() || null, business_hours: payload.business_hours.trim() || null, logo_url: payload.logo_url.trim() || null, base_color: payload.base_color.trim() || "#F4F7FB", institutional_data: payload.institutional_data.trim(), commercial_status: payload.commercial_status, commercial_owner: payload.commercial_owner.trim() || null, commercial_owner_user_id: payload.commercial_owner_user_id, main_contact_name: payload.main_contact_name.trim() || null, main_contact_title: payload.main_contact_title.trim() || null, commercial_phone: payload.commercial_phone.trim() || null, commercial_email: payload.commercial_email.trim() || null, last_management_at: normalizeDateTime(payload.last_management_at), next_management_at: normalizeDateTime(payload.next_management_at), commercial_notes: payload.commercial_notes.trim() || null, priority: payload.priority, lead_source: payload.lead_source.trim() || null, potential: payload.potential.trim() || null, internal_observations: payload.internal_observations.trim() || null };
}
function normalizeUserPayload(payload: UserPayload) {
  return { ...payload, email: payload.email.trim().toLowerCase(), full_name: repairText(payload.full_name), password: payload.password?.trim() || null, phone: cleanNullableText(payload.phone), job_title: cleanNullableText(payload.job_title), assignments: payload.assignments.filter((assignment) => assignment.role_code) };
}
function normalizeCasePayload(payload: CasePayload) {
  return { ...payload, case_type: cleanText(payload.case_type), act_type: cleanText(payload.act_type), metadata_json: payload.metadata_json.trim() || "{}" };
}

export async function login(payload: LoginPayload) {
  try {
    const response = await fetch(`${API_URL}/api/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      credentials: "include"
    });
    return await parseResponse<{ access_token: string; token_type: string; user: CurrentUser }>(response);
  } catch (error) {
    throw normalizeApiError(error, "No fue posible iniciar sesión.");
  }
}

export function completeLogin(token: string, rememberSession: boolean) {
  persistSessionToken(token, rememberSession);
}

export function logout() {
  document.cookie = `${SESSION_KEY}=; path=/; max-age=0; SameSite=Lax`;
  if (typeof window !== "undefined") {
    try {
      window.localStorage.removeItem(SESSION_KEY);
      window.sessionStorage.removeItem(SESSION_KEY);
    } catch {
      // ignore storage failures
    }
  }
}

function decodeJwtPayload(token: string | null): Record<string, unknown> {
  if (!token) {
    return {};
  }
  const parts = token.split(".");
  if (parts.length < 2) {
    return {};
  }
  try {
    const payload = parts[1].replace(/-/g, "+").replace(/_/g, "/");
    const padded = payload + "=".repeat((4 - (payload.length % 4)) % 4);
    const raw = typeof atob === "function"
      ? atob(padded)
      : Buffer.from(padded, "base64").toString("binary");
    return JSON.parse(raw) as Record<string, unknown>;
  } catch {
    return {};
  }
}

export async function getCurrentUser(): Promise<CurrentUser> {
  const currentUser = await apiFetch<CurrentUser>("/api/v1/auth/me");
  const tokenPayload = decodeJwtPayload(getToken());
  const tokenNotaryId = typeof tokenPayload.notary_id === "number"
    ? tokenPayload.notary_id
    : typeof tokenPayload.notary_id === "string"
      ? Number(tokenPayload.notary_id)
      : null;
  return {
    ...currentUser,
    default_notary_id: currentUser.default_notary_id ?? (Number.isFinite(tokenNotaryId as number) ? (tokenNotaryId as number) : null),
  };
}
export async function getNotaries(filters: NotaryFilters = {}): Promise<NotaryRecord[]> { return normalizeNotaryResponse(await apiFetch<NotaryRecord[]>(`/api/v1/notaries${buildQuery(filters)}`)); }
export async function getNotaryFilterOptions(): Promise<NotaryFilterOptions> { return apiFetch<NotaryFilterOptions>("/api/v1/notaries/filters"); }
export async function getNotary(id: number): Promise<NotaryDetail> { return apiFetch<NotaryDetail>(`/api/v1/notaries/${id}`); }
export async function updateNotary(id: number, payload: NotaryPayload): Promise<NotaryRecord> { return apiFetch<NotaryRecord>(`/api/v1/notaries/${id}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: normalizeNotaryPayload(payload) }); }
export async function createCommercialActivity(id: number, payload: CommercialActivityPayload): Promise<CommercialActivityRecord> { return apiFetch<CommercialActivityRecord>(`/api/v1/notaries/${id}/commercial-activities`, { method: "POST", headers: { "Content-Type": "application/json" }, body: { ...payload, responsible: payload.responsible.trim() || null, result: payload.result.trim() || null, next_action: payload.next_action.trim() || null } }); }
export async function importAntioquiaSource(overwriteExisting = true): Promise<NotaryImportSummary> { return apiFetch<NotaryImportSummary>("/api/v1/notaries/imports/antioquia-source", { method: "POST", headers: { "Content-Type": "application/json" }, body: { overwrite_existing: overwriteExisting } }); }
export async function getRoleCatalog(): Promise<RoleCatalogItem[]> { return apiFetch<RoleCatalogItem[]>("/api/v1/users/roles"); }
export async function getUsers(): Promise<UserRecord[]> { return apiFetch<UserRecord[]>("/api/v1/users"); }
export async function getUserOptions(activeOnly = true): Promise<UserOption[]> { return normalizeUserOptionsResponse(await apiFetch<UserOption[]>(`/api/v1/users/options${activeOnly ? "?active_only=true" : "?active_only=false"}`)); }
export async function createUser(payload: UserPayload): Promise<UserRecord> { return apiFetch<UserRecord>("/api/v1/users", { method: "POST", headers: { "Content-Type": "application/json" }, body: normalizeUserPayload(payload) }); }
export async function updateUser(id: number, payload: UserPayload): Promise<UserRecord> { return apiFetch<UserRecord>(`/api/v1/users/${id}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: normalizeUserPayload(payload) }); }
export async function getCases(filters: CaseFilters = {}): Promise<CaseRecord[]> { return normalizeCaseResponse(await apiFetch<CaseRecord[]>(`/api/v1/cases${buildQuery(filters)}`)); }
export async function getCaseFilters(): Promise<CaseFilterOptions> { return normalizeCaseFilterOptions(await apiFetch<CaseFilterOptions>("/api/v1/cases/filters")); }
export async function getCase(id: number): Promise<CaseDetail> { return apiFetch<CaseDetail>(`/api/v1/cases/${id}`); }
export async function createCase(payload: Omit<CasePayload, "consecutive" | "year"> & { consecutive?: number; year?: number }): Promise<CaseDetail> { return apiFetch<CaseDetail>("/api/v1/cases", { method: "POST", headers: { "Content-Type": "application/json" }, body: normalizeCasePayload({ ...payload, consecutive: payload.consecutive ?? 0, year: payload.year ?? new Date().getFullYear() } as CasePayload) }); }
export async function updateCase(id: number, payload: CasePayload): Promise<CaseDetail> { return apiFetch<CaseDetail>(`/api/v1/cases/${id}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: normalizeCasePayload(payload) }); }
export async function updateCaseState(id: number, currentState: string, comment = ""): Promise<CaseDetail> { return apiFetch<CaseDetail>(`/api/v1/cases/${id}/state`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: { current_state: currentState, comment: comment.trim() || null } }); }
export async function updateCaseOwner(id: number, userId: number | null, comment = ""): Promise<CaseDetail> { return apiFetch<CaseDetail>(`/api/v1/cases/${id}/owner`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: { current_owner_user_id: userId, comment: comment.trim() || null } }); }
export async function addCaseComment(id: number, comment: string, metadataJson = ""): Promise<CaseDetail> { return apiFetch<CaseDetail>(`/api/v1/cases/${id}/timeline-events`, { method: "POST", headers: { "Content-Type": "application/json" }, body: { comment, metadata_json: metadataJson.trim() || null } }); }



export async function getExecutiveDashboard(filters: ExecutiveDashboardFilters = {}): Promise<ExecutiveDashboard> { return apiFetch<ExecutiveDashboard>(`/api/v1/dashboard/superadmin${buildQuery(filters)}`); }

export async function createRole(payload: {
  code: string; name: string; scope: string; description: string;
}): Promise<RoleCatalogItem> {
  return apiFetch<RoleCatalogItem>("/api/v1/users/roles", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: payload
  });
}

export async function updateRole(
  roleId: number,
  payload: { name: string; description: string }
): Promise<RoleCatalogItem> {
  return apiFetch<RoleCatalogItem>(`/api/v1/users/roles/${roleId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: payload
  });
}

export async function deleteRole(roleId: number): Promise<{ deleted: boolean }> {
  return apiFetch<{ deleted: boolean }>(`/api/v1/users/roles/${roleId}`, { method: "DELETE" });
}

export async function getRolePermissions(roleId: number): Promise<RolePermissionItem[]> {
  return apiFetch<RolePermissionItem[]>(`/api/v1/users/roles/${roleId}/permissions`);
}

export async function updateRolePermissions(roleId: number, permissions: RolePermissionItem[]): Promise<RolePermissionItem[]> {
  return apiFetch<RolePermissionItem[]>(`/api/v1/users/roles/${roleId}/permissions`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: permissions
  });
}


