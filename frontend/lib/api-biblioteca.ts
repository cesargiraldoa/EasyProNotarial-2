import { apiFetch } from "@/lib/api";

export type FieldCatalogItem = {
  id: number;
  code: string;
  label: string;
  field_type: string;
  category: string;
  description: string | null;
  options_json: string | null;
  scope: string;
  notary_id: number | null;
};

export type BibliotecaTemplate = {
  id: number;
  library_key: string;
  name: string;
  template_kind: string;
  status: string;
  act_code: string | null;
  document_type: string | null;
  bank_name: string | null;
  project_name: string | null;
  source_document_id: number | null;
  latest_version_id: number | null;
  metadata_json: string;
  created_at: string;
  updated_at: string;
};

function buildQuery(params: Record<string, string | undefined> = {}) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value && value.trim()) {
      query.set(key, value.trim());
    }
  });
  const suffix = query.toString();
  return suffix ? `?${suffix}` : "";
}

export async function getCamposCatalogo(params: {
  category?: string;
  scope?: string;
  search?: string;
} = {}): Promise<FieldCatalogItem[]> {
  const token = typeof window !== "undefined" ? (window.localStorage.getItem("easypro2_session") || window.sessionStorage.getItem("easypro2_session")) : null;
  console.info("[biblioteca] sesión", token ? "presente" : "ausente");
  const result = await apiFetch<FieldCatalogItem[]>(`/api/v1/biblioteca/campos${buildQuery(params)}`);
  return result;
}

export async function getBibliotecaTemplates(params: {
  act_code?: string;
  document_type?: string;
  bank_name?: string;
  status?: string;
} = {}): Promise<BibliotecaTemplate[]> {
  try {
    return await apiFetch<BibliotecaTemplate[]>(`/api/v1/biblioteca/templates${buildQuery(params)}`);
  } catch {
    return [];
  }
}
