import { apiFetch } from "@/lib/api";
import { buildApiUrl } from "@/lib/config";
import type { ActoCode, CaseState } from "@/lib/motor-escritura";

export type LegalNorma = {
  id: number;
  tipo: string;
  numero: string;
  anio: number;
  articulo?: string | null;
  materia: string;
  autoridad: string;
  estado: string;
  vigencia_formal: string;
  aplicabilidad_operativa: string;
  vigencia_desde?: string | null;
  vigencia_hasta?: string | null;
  url_oficial?: string | null;
  confianza: string;
  fecha_verificacion?: string | null;
  texto?: string | null;
  notas?: string | null;
  slug: string;
};

export type LegalClausula = {
  id: number;
  acto_code: string;
  orden: number;
  titulo: string;
  texto: string;
  capa: string;
  norma_id?: number | null;
  notaria_id?: number | null;
  condicional: boolean;
  vigencia_desde?: string | null;
  vigencia_hasta?: string | null;
  notas?: string | null;
};

export type LegalRegla = {
  id: number;
  acto_code: string;
  codigo: string;
  condicion_json: Record<string, unknown>;
  efecto: string;
  severidad: string;
  mensaje: string;
  norma_id?: number | null;
  vigencia_desde?: string | null;
  vigencia_hasta?: string | null;
};

export type LegalTarifa = {
  id: number;
  anio: number;
  concepto: string;
  valor?: string | number | null;
  formula?: string | null;
  unidad?: string | null;
  norma_id?: number | null;
  vigencia_desde?: string | null;
  vigencia_hasta?: string | null;
};

export type CorpusResponse = {
  acto: ActoCode;
  corpus_acto_code: string;
  fecha: string;
  normas: LegalNorma[];
  clausulas: LegalClausula[];
  reglas: LegalRegla[];
  tarifas: LegalTarifa[];
};

export type EscrituraCaseMeta = {
  id: number;
  notary_id: number;
  case_type: string;
  act_type: string;
  consecutive: number;
  year: number;
  current_state: string;
  internal_case_number?: string | null;
  official_deed_number?: string | null;
  official_deed_year?: number | null;
  updated_at: string;
};

export type EscrituraStateResponse = {
  case_id: number;
  acto?: ActoCode | null;
  state: Record<string, unknown>;
  case: EscrituraCaseMeta;
};

export type DocumentoPayload = {
  acto: ActoCode;
  html: string;
  cumplimiento_bloqueantes: number;
  filename?: string;
};

export type DocumentoResponse = {
  version_number: number;
  file_format: string;
  storage_path: string;
  download_url?: string | null;
  document_id: number;
  version_id: number;
};

function escrituraQuery(params: Record<string, string | undefined>) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value?.trim()) query.set(key, value.trim());
  });
  const suffix = query.toString();
  return suffix ? `?${suffix}` : "";
}

export function getCorpus(acto: ActoCode, fecha?: string) {
  return apiFetch<CorpusResponse>(`/api/v1/escritura/corpus${escrituraQuery({ acto, fecha })}`);
}

export function getEscrituraState(caseId: number) {
  return apiFetch<EscrituraStateResponse>(`/api/v1/escritura/cases/${caseId}`);
}

export function saveEscrituraState(caseId: number, acto: ActoCode, state: CaseState) {
  return apiFetch<EscrituraStateResponse>(`/api/v1/escritura/cases/${caseId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: { acto, state },
  });
}

export function generarDocumento(caseId: number, payload: DocumentoPayload) {
  return apiFetch<DocumentoResponse>(`/api/v1/escritura/cases/${caseId}/documento`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: payload,
  });
}

export function escrituraDownloadUrl(downloadUrl: string) {
  return /^https?:\/\//i.test(downloadUrl) ? downloadUrl : buildApiUrl(downloadUrl);
}
