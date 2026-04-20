import { apiFetch } from "@/lib/api";

export type LegalEntityRecord = {
  id: number;
  nit: string;
  name: string;
  legal_representative?: string | null;
  municipality?: string | null;
  address?: string | null;
  phone?: string | null;
  email?: string | null;
};

export type LegalEntityPayload = Omit<LegalEntityRecord, "id">;

export type LegalEntityRepresentativeRecord = {
  id: number;
  legal_entity_id: number;
  person_id: number;
  person_name: string;
  person_document: string;
  power_type?: string | null;
  is_active: boolean;
};

export type LegalEntityRepresentativePayload = {
  person_id: number;
  power_type?: string | null;
};

function cleanOptionalText(value: string | null | undefined) {
  const next = value?.trim();
  return next ? next : null;
}

function buildQuery(q: string) {
  const query = q.trim();
  return query ? `?q=${encodeURIComponent(query)}` : "";
}

function normalizeEntity(payload: LegalEntityRecord): LegalEntityRecord {
  return {
    ...payload,
    nit: payload.nit.trim(),
    name: payload.name.trim(),
    legal_representative: cleanOptionalText(payload.legal_representative),
    municipality: cleanOptionalText(payload.municipality),
    address: cleanOptionalText(payload.address),
    phone: cleanOptionalText(payload.phone),
    email: cleanOptionalText(payload.email),
  };
}

function normalizeRepresentative(payload: LegalEntityRepresentativeRecord): LegalEntityRepresentativeRecord {
  return {
    ...payload,
    person_name: payload.person_name.trim(),
    person_document: payload.person_document.trim(),
    power_type: cleanOptionalText(payload.power_type),
  };
}

export async function searchLegalEntities(q: string): Promise<LegalEntityRecord[]> {
  const path = `/api/v1/legal-entities${buildQuery(q)}`;
  const data = await apiFetch<LegalEntityRecord[]>(path);
  return Array.isArray(data) ? data.map(normalizeEntity) : [];
}

export async function createLegalEntity(payload: LegalEntityPayload): Promise<LegalEntityRecord> {
  const data = await apiFetch<LegalEntityRecord>("/api/v1/legal-entities", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      ...payload,
      nit: payload.nit.trim(),
      name: payload.name.trim(),
      legal_representative: cleanOptionalText(payload.legal_representative),
      municipality: cleanOptionalText(payload.municipality),
      address: cleanOptionalText(payload.address),
      phone: cleanOptionalText(payload.phone),
      email: cleanOptionalText(payload.email),
    }),
  });
  return normalizeEntity(data);
}

export async function getLegalEntityRepresentatives(entityId: number): Promise<LegalEntityRepresentativeRecord[]> {
  const data = await apiFetch<LegalEntityRepresentativeRecord[]>(`/api/v1/legal-entities/${entityId}/representatives`);
  return Array.isArray(data) ? data.map(normalizeRepresentative) : [];
}

export async function createLegalEntityRepresentative(
  entityId: number,
  payload: LegalEntityRepresentativePayload,
): Promise<LegalEntityRepresentativeRecord> {
  const data = await apiFetch<LegalEntityRepresentativeRecord>(`/api/v1/legal-entities/${entityId}/representatives`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      person_id: payload.person_id,
      power_type: cleanOptionalText(payload.power_type),
    }),
  });
  return normalizeRepresentative(data);
}
