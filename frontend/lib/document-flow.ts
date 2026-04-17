import { cleanNullableText, cleanText, sanitizeTextDeep } from "@/lib/text";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";
const SESSION_KEY = "easypro2_session";

function getCookieToken() {
  if (typeof document === "undefined") return null;
  const match = document.cookie.match(new RegExp(`(?:^|; )${SESSION_KEY}=([^;]+)`));
  return match ? decodeURIComponent(match[1]) : null;
}

function getStoredToken() {
  if (typeof window === "undefined") return null;
  try {
    return window.localStorage.getItem(SESSION_KEY) || window.sessionStorage.getItem(SESSION_KEY) || null;
  } catch {
    return null;
  }
}

async function parseResponse<T>(response: Response): Promise<T> {
  const text = await response.text();
  if (!response.ok) {
    throw new Error(text || "No fue posible completar la solicitud.");
  }
  if (!text.trim()) {
    return null as T;
  }
  return sanitizeTextDeep(JSON.parse(text) as T);
}

async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = getCookieToken() || getStoredToken();
  const headers = new Headers(init.headers ?? {});
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const response = await fetch(`${API_URL}${path}`, { ...init, headers, cache: "no-store", credentials: "include" });
  return parseResponse<T>(response);
}

const asString = (value: unknown, fallback = "") => cleanText(value, fallback);
const asNullableString = (value: unknown) => cleanNullableText(value);
const asNumber = (value: unknown, fallback = 0) => (typeof value === "number" && Number.isFinite(value) ? value : fallback);
const asNullableNumber = (value: unknown) => (typeof value === "number" && Number.isFinite(value) ? value : null);
const asBoolean = (value: unknown, fallback = false) => (typeof value === "boolean" ? value : fallback);
const asArray = <T>(value: unknown, mapper: (item: unknown) => T): T[] => Array.isArray(value) ? value.map(mapper) : [];

export type TemplateRequiredRole = { id: number; role_code: string; label: string; is_required: boolean; step_order: number };
export type TemplateField = { id: number; field_code: string; label: string; field_type: string; section: string; is_required: boolean; options_json?: string | null; placeholder_key?: string | null; help_text?: string | null; step_order: number };
export type TemplateRecord = { id: number; name: string; slug: string; case_type: string; document_type: string; description?: string | null; scope_type: string; notary_id?: number | null; notary_label?: string | null; is_active: boolean; source_filename?: string | null; storage_path?: string | null; internal_variable_map_json: string; required_roles: TemplateRequiredRole[]; fields: TemplateField[] };
export type PersonRecord = { id: number; document_type: string; document_number: string; full_name: string; sex?: string | null; nationality?: string | null; marital_status?: string | null; profession?: string | null; municipality?: string | null; is_transient: boolean; phone?: string | null; address?: string | null; email?: string | null; metadata_json?: string };
export type PersonPayload = Omit<PersonRecord, "id">;
export type DocumentFlowCasePayload = { template_id: number; notary_id: number; client_user_id: number | null; current_owner_user_id: number | null; protocolist_user_id: number | null; approver_user_id: number | null; titular_notary_user_id: number | null; substitute_notary_user_id: number | null; requires_client_review: boolean; metadata_json: string };
export type CaseParticipantPayload = { role_code: string; role_label: string; person_id?: number | null; person?: PersonPayload | null };
export type CaseActDataPayload = { data_json: string };
export type CaseComment = { id: number; created_by_user_id?: number | null; created_by_user_name?: string | null; comment?: string | null; note?: string | null; created_at: string };
export type CaseWorkflowEvent = { id: number; event_type: string; actor_user_id?: number | null; actor_user_name?: string | null; actor_role_code?: string | null; from_state?: string | null; to_state?: string | null; field_name?: string | null; old_value?: string | null; new_value?: string | null; comment?: string | null; approved_version_id?: number | null; metadata_json?: string | null; created_at: string };
export type CaseTimelineEvent = { id: number; event_type: string; from_state?: string | null; to_state?: string | null; comment?: string | null; metadata_json?: string | null; actor_user_id?: number | null; actor_user_name?: string | null; created_at: string };
export type CaseDocumentVersion = { id: number; version_number: number; file_format: string; storage_path: string; original_filename: string; generated_from_template_id?: number | null; created_by_user_id?: number | null; created_by_user_name?: string | null; placeholder_snapshot_json: string; created_at: string; download_url?: string | null };
export type CaseDocument = { id: number; category: string; title: string; current_version_number: number; versions: CaseDocumentVersion[] };
export type CaseParticipant = { id: number; role_code: string; role_label: string; person_id: number; person: PersonRecord; snapshot_json: string; created_at: string; updated_at: string };
export type CaseActData = { id: number; case_id: number; data_json?: string; gari_draft_text?: string | null; created_at: string; updated_at: string };
export type DocumentFlowCase = { id: number; notary_id: number; notary_label: string; template_id?: number | null; template_name?: string | null; template?: TemplateRecord | null; case_type: string; act_type: string; consecutive: number; year: number; internal_case_number?: string | null; official_deed_number?: string | null; official_deed_year?: number | null; current_state: string; current_owner_user_id?: number | null; current_owner_user_name?: string | null; created_by_user_id?: number | null; created_by_user_name?: string | null; client_user_id?: number | null; client_user_name?: string | null; protocolist_user_id?: number | null; protocolist_user_name?: string | null; approver_user_id?: number | null; approver_user_name?: string | null; titular_notary_user_id?: number | null; titular_notary_user_name?: string | null; substitute_notary_user_id?: number | null; substitute_notary_user_name?: string | null; requires_client_review: boolean; final_signed_uploaded: boolean; approved_at?: string | null; approved_by_user_id?: number | null; approved_by_user_name?: string | null; approved_by_role_code?: string | null; approved_document_version_id?: number | null; metadata_json: string; created_at: string; updated_at: string; timeline_events: CaseTimelineEvent[]; workflow_events: CaseWorkflowEvent[]; participants: CaseParticipant[]; act_data?: CaseActData | null; client_comments: CaseComment[]; internal_notes: CaseComment[]; documents: CaseDocument[] };

function normalizeTemplateRole(value: unknown): TemplateRequiredRole {
  const item = (value ?? {}) as Record<string, unknown>;
  return { id: asNumber(item.id), role_code: asString(item.role_code), label: asString(item.label), is_required: asBoolean(item.is_required, true), step_order: asNumber(item.step_order, 1) };
}
function normalizeTemplateField(value: unknown): TemplateField {
  const item = (value ?? {}) as Record<string, unknown>;
  return { id: asNumber(item.id), field_code: asString(item.field_code), label: asString(item.label), field_type: asString(item.field_type, "text"), section: asString(item.section, "acto"), is_required: asBoolean(item.is_required, true), options_json: asNullableString(item.options_json), placeholder_key: asNullableString(item.placeholder_key), help_text: asNullableString(item.help_text), step_order: asNumber(item.step_order, 1) };
}
function normalizeTemplate(value: unknown): TemplateRecord {
  const item = (value ?? {}) as Record<string, unknown>;
  return {
    id: asNumber(item.id),
    name: asString(item.name, "Plantilla sin nombre"),
    slug: asString(item.slug),
    case_type: asString(item.case_type, "escritura"),
    document_type: asString(item.document_type, "Documento"),
    description: asNullableString(item.description),
    scope_type: asString(item.scope_type, "global"),
    notary_id: asNullableNumber(item.notary_id),
    notary_label: asNullableString(item.notary_label),
    is_active: asBoolean(item.is_active, false),
    source_filename: asNullableString(item.source_filename),
    storage_path: asNullableString(item.storage_path),
    internal_variable_map_json: asString(item.internal_variable_map_json, "{}"),
    required_roles: asArray(item.required_roles, normalizeTemplateRole),
    fields: asArray(item.fields, normalizeTemplateField),
  };
}
function normalizePerson(value: unknown): PersonRecord {
  const item = (value ?? {}) as Record<string, unknown>;
  return {
    id: asNumber(item.id),
    document_type: asString(item.document_type, "CC"),
    document_number: asString(item.document_number),
    full_name: asString(item.full_name, "Persona sin nombre"),
    sex: asNullableString(item.sex),
    nationality: asNullableString(item.nationality),
    marital_status: asNullableString(item.marital_status),
    profession: asNullableString(item.profession),
    municipality: asNullableString(item.municipality),
    is_transient: asBoolean(item.is_transient, false),
    phone: asNullableString(item.phone),
    address: asNullableString(item.address),
    email: asNullableString(item.email),
    metadata_json: asString(item.metadata_json, "{}"),
  };
}
function normalizeComment(value: unknown): CaseComment {
  const item = (value ?? {}) as Record<string, unknown>;
  return { id: asNumber(item.id), created_by_user_id: asNullableNumber(item.created_by_user_id), created_by_user_name: asNullableString(item.created_by_user_name), comment: asNullableString(item.comment), note: asNullableString(item.note), created_at: asString(item.created_at) };
}
function normalizeWorkflowEvent(value: unknown): CaseWorkflowEvent {
  const item = (value ?? {}) as Record<string, unknown>;
  return { id: asNumber(item.id), event_type: asString(item.event_type), actor_user_id: asNullableNumber(item.actor_user_id), actor_user_name: asNullableString(item.actor_user_name), actor_role_code: asNullableString(item.actor_role_code), from_state: asNullableString(item.from_state), to_state: asNullableString(item.to_state), field_name: asNullableString(item.field_name), old_value: asNullableString(item.old_value), new_value: asNullableString(item.new_value), comment: asNullableString(item.comment), approved_version_id: asNullableNumber(item.approved_version_id), metadata_json: asNullableString(item.metadata_json), created_at: asString(item.created_at) };
}
function normalizeTimelineEvent(value: unknown): CaseTimelineEvent {
  const item = (value ?? {}) as Record<string, unknown>;
  return { id: asNumber(item.id), event_type: asString(item.event_type), from_state: asNullableString(item.from_state), to_state: asNullableString(item.to_state), comment: asNullableString(item.comment), metadata_json: asNullableString(item.metadata_json), actor_user_id: asNullableNumber(item.actor_user_id), actor_user_name: asNullableString(item.actor_user_name), created_at: asString(item.created_at) };
}
function normalizeDocumentVersion(value: unknown): CaseDocumentVersion {
  const item = (value ?? {}) as Record<string, unknown>;
  return { id: asNumber(item.id), version_number: asNumber(item.version_number), file_format: asString(item.file_format, "docx"), storage_path: asString(item.storage_path), original_filename: asString(item.original_filename, "archivo"), generated_from_template_id: asNullableNumber(item.generated_from_template_id), created_by_user_id: asNullableNumber(item.created_by_user_id), created_by_user_name: asNullableString(item.created_by_user_name), placeholder_snapshot_json: asString(item.placeholder_snapshot_json, "{}"), created_at: asString(item.created_at), download_url: asNullableString(item.download_url) };
}
function normalizeDocument(value: unknown): CaseDocument {
  const item = (value ?? {}) as Record<string, unknown>;
  return { id: asNumber(item.id), category: asString(item.category), title: asString(item.title, "Documento"), current_version_number: asNumber(item.current_version_number), versions: asArray(item.versions, normalizeDocumentVersion) };
}
function normalizeParticipant(value: unknown): CaseParticipant {
  const item = (value ?? {}) as Record<string, unknown>;
  return { id: asNumber(item.id), role_code: asString(item.role_code), role_label: asString(item.role_label), person_id: asNumber(item.person_id), person: normalizePerson(item.person), snapshot_json: asString(item.snapshot_json, "{}"), created_at: asString(item.created_at), updated_at: asString(item.updated_at) };
}
function normalizeActData(value: unknown): CaseActData | null {
  if (!value || typeof value !== "object") return null;
  const item = value as Record<string, unknown>;
  return { id: asNumber(item.id), case_id: asNumber(item.case_id), data_json: asString(item.data_json, "{}"), created_at: asString(item.created_at), updated_at: asString(item.updated_at) };
}
function normalizeCase(value: unknown): DocumentFlowCase {
  const item = (value ?? {}) as Record<string, unknown>;
  return {
    id: asNumber(item.id),
    notary_id: asNumber(item.notary_id),
    notary_label: asString(item.notary_label, "Sin notaría"),
    template_id: asNullableNumber(item.template_id),
    template_name: asNullableString(item.template_name),
    template: item.template ? normalizeTemplate(item.template) : null,
    case_type: asString(item.case_type, "escritura"),
    act_type: asString(item.act_type, "Documento"),
    consecutive: asNumber(item.consecutive),
    year: asNumber(item.year),
    internal_case_number: asNullableString(item.internal_case_number),
    official_deed_number: asNullableString(item.official_deed_number),
    official_deed_year: asNullableNumber(item.official_deed_year),
    current_state: asString(item.current_state, "borrador"),
    current_owner_user_id: asNullableNumber(item.current_owner_user_id),
    current_owner_user_name: asNullableString(item.current_owner_user_name),
    created_by_user_id: asNullableNumber(item.created_by_user_id),
    created_by_user_name: asNullableString(item.created_by_user_name),
    client_user_id: asNullableNumber(item.client_user_id),
    client_user_name: asNullableString(item.client_user_name),
    protocolist_user_id: asNullableNumber(item.protocolist_user_id),
    protocolist_user_name: asNullableString(item.protocolist_user_name),
    approver_user_id: asNullableNumber(item.approver_user_id),
    approver_user_name: asNullableString(item.approver_user_name),
    titular_notary_user_id: asNullableNumber(item.titular_notary_user_id),
    titular_notary_user_name: asNullableString(item.titular_notary_user_name),
    substitute_notary_user_id: asNullableNumber(item.substitute_notary_user_id),
    substitute_notary_user_name: asNullableString(item.substitute_notary_user_name),
    requires_client_review: asBoolean(item.requires_client_review, false),
    final_signed_uploaded: asBoolean(item.final_signed_uploaded, false),
    approved_at: asNullableString(item.approved_at),
    approved_by_user_id: asNullableNumber(item.approved_by_user_id),
    approved_by_user_name: asNullableString(item.approved_by_user_name),
    approved_by_role_code: asNullableString(item.approved_by_role_code),
    approved_document_version_id: asNullableNumber(item.approved_document_version_id),
    metadata_json: asString(item.metadata_json, "{}"),
    created_at: asString(item.created_at),
    updated_at: asString(item.updated_at),
    timeline_events: asArray(item.timeline_events, normalizeTimelineEvent),
    workflow_events: asArray(item.workflow_events, normalizeWorkflowEvent),
    participants: asArray(item.participants, normalizeParticipant),
    act_data: normalizeActData(item.act_data),
    client_comments: asArray(item.client_comments, normalizeComment),
    internal_notes: asArray(item.internal_notes, normalizeComment),
    documents: asArray(item.documents, normalizeDocument),
  };
}

export async function getActiveTemplates() { return asArray(await apiFetch<unknown>("/api/v1/templates/active"), normalizeTemplate); }
export async function getTemplates() { return asArray(await apiFetch<unknown>("/api/v1/templates"), normalizeTemplate); }
export async function createDocumentCase(payload: DocumentFlowCasePayload) { return normalizeCase(await apiFetch<unknown>("/api/v1/document-flow/cases/from-template", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) })); }
export async function getDocumentCase(caseId: number) { return normalizeCase(await apiFetch<unknown>(`/api/v1/document-flow/cases/${caseId}`)); }
export async function saveCaseParticipants(caseId: number, payload: CaseParticipantPayload[]) { return normalizeCase(await apiFetch<unknown>(`/api/v1/document-flow/cases/${caseId}/participants`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) })); }
export async function saveCaseActData(caseId: number, payload: CaseActDataPayload) { return normalizeCase(await apiFetch<unknown>(`/api/v1/document-flow/cases/${caseId}/act-data`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) })); }
export async function addClientComment(caseId: number, comment: string) { return normalizeCase(await apiFetch<unknown>(`/api/v1/document-flow/cases/${caseId}/client-comments`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ comment }) })); }
export async function addInternalNote(caseId: number, note: string) { return normalizeCase(await apiFetch<unknown>(`/api/v1/document-flow/cases/${caseId}/internal-notes`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ note }) })); }
export async function generateCaseDraft(caseId: number, comment = "") { return normalizeCase(await apiFetch<unknown>(`/api/v1/document-flow/cases/${caseId}/generate-draft`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ comment: comment || null }) })); }
export async function generateWithGari(caseId: number, comment?: string, correctionText?: string): Promise<DocumentFlowCase> {
  return normalizeCase(await apiFetch<unknown>(`/api/v1/document-flow/cases/${caseId}/generate-with-gari`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ comment: comment || null, correction_text: correctionText || null }),
  }));
}
export async function approveDocumentCase(caseId: number, role_code: string, comment = "") { return normalizeCase(await apiFetch<unknown>(`/api/v1/document-flow/cases/${caseId}/approve`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ role_code, comment: comment || null }) })); }
export async function exportDocumentCase(caseId: number, file_format: "docx" | "pdf") { return normalizeCase(await apiFetch<unknown>(`/api/v1/document-flow/cases/${caseId}/export`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ file_format }) })); }
export async function uploadFinalSigned(caseId: number, filename: string, content_base64: string, comment = "") { return normalizeCase(await apiFetch<unknown>(`/api/v1/document-flow/cases/${caseId}/final-upload`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ filename, content_base64, comment: comment || null }) })); }
export async function lookupPersons(params: { document_type?: string; document_number?: string; q?: string }) { const query = new URLSearchParams(); if (params.document_type) query.set("document_type", params.document_type); if (params.document_number) query.set("document_number", params.document_number); if (params.q) query.set("q", params.q); return asArray(await apiFetch<unknown>(`/api/v1/document-flow/persons/lookup?${query.toString()}`), normalizePerson); }
export async function createTemplate(payload: unknown) { return normalizeTemplate(await apiFetch<unknown>("/api/v1/templates", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) })); }
export async function updateTemplate(id: number, payload: unknown) { return normalizeTemplate(await apiFetch<unknown>(`/api/v1/templates/${id}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) })); }


