import { apiFetch } from "@/lib/api";
import { getToken } from "@/lib/auth";
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

export type CorpusBusquedaHit = {
  source_type: string;
  source_id: number;
  source_ref: string;
  titulo: string;
  chunk_text: string;
  score: number;
  acto_code?: string | null;
  vigencia_desde?: string | null;
  vigencia_hasta?: string | null;
};

export type CorpusBusquedaResponse = {
  q: string;
  acto?: ActoCode | null;
  corpus_acto_code?: string | null;
  fecha: string;
  hits: CorpusBusquedaHit[];
};

export type BibliotecaClausula = {
  id: number;
  acto_code: string;
  titulo: string;
  texto: string;
  capa: string;
  orden: number;
  condicional: boolean;
  vigencia_desde?: string | null;
  vigencia_hasta?: string | null;
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

export type EscrituraStatePayload = CaseState | Record<string, unknown>;

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

export type GariCampoSugerido = {
  valor: unknown;
  confianza: number;
  fuente: string;
};

export type GariExtraccionResponse = {
  sugerencias: Record<string, GariCampoSugerido>;
  por_validar: boolean;
  estado: string;
  modelo: string;
  prompt_version: string;
};

export type GariProsaResponse = {
  html_sugerido: string;
  sugerencia: boolean;
  estado: string;
  modelo: string;
  prompt_version: string;
};

export type GariClasificacionResponse = {
  acto_sugerido: ActoCode;
  ramas: string[];
  sugerencia: boolean;
  estado: string;
  modelo: string;
  prompt_version: string;
};

export type GariRevisionHallazgo = {
  tipo: string;
  detalle: string;
  cita_slug?: string | null;
};

export type GariRevisionResponse = {
  hallazgos: GariRevisionHallazgo[];
  sugerencia: boolean;
  estado: string;
  modelo: string;
  prompt_version: string;
};

function escrituraQuery(params: Record<string, string | undefined>) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value?.trim()) query.set(key, value.trim());
  });
  const suffix = query.toString();
  return suffix ? `?${suffix}` : "";
}

async function apiUpload<T>(path: string, formData: FormData): Promise<T> {
  const token = getToken();
  const headers = new Headers();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const response = await fetch(buildApiUrl(path), {
    method: "POST",
    headers,
    body: formData,
    cache: "no-store",
    credentials: "include",
  });
  const text = await response.text();
  if (!response.ok) throw new Error(text || "No fue posible completar la solicitud.");
  return text.trim() ? (JSON.parse(text) as T) : (null as T);
}

export function getCorpus(acto: ActoCode, fecha?: string) {
  return apiFetch<CorpusResponse>(`/api/v1/escritura/corpus${escrituraQuery({ acto, fecha })}`);
}

export function buscarCorpus(q: string, acto?: ActoCode, fecha?: string, topK?: number) {
  return apiFetch<CorpusBusquedaResponse>(
    `/api/v1/escritura/corpus/buscar${escrituraQuery({ q, acto, fecha, top_k: topK ? String(topK) : undefined })}`,
  );
}

export function getBibliotecaEscritura(acto: ActoCode, fecha?: string) {
  return apiFetch<BibliotecaClausula[]>(`/api/v1/escritura/biblioteca${escrituraQuery({ acto, fecha })}`);
}

export type PlantillaSemillaToken = {
  token: string;
  label?: string | null;
  field?: string | null;
  section?: string | null;
};

export type PlantillaSemilla = {
  id: number;
  acto: ActoCode;
  fuente: string;
  name: string;
  body_html: string;
  tokens: PlantillaSemillaToken[];
  bank_name?: string | null;
  legal_entity_id?: number | null;
  notaria?: string | null;
  is_fallback: boolean;
};

export type NuevoCasoEscritura = {
  case_id: number;
  acto: ActoCode;
  current_state: string;
  notary_id: number;
};

export function crearCasoEscritura(acto?: ActoCode) {
  return apiFetch<NuevoCasoEscritura>("/api/v1/escritura/cases", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ acto: acto ?? null }),
  });
}

export function getPlantillaSemilla(acto: ActoCode, fuente: string, legalEntityId?: number | null) {
  return apiFetch<PlantillaSemilla>(
    `/api/v1/escritura/plantilla-semilla${escrituraQuery({
      acto,
      fuente,
      legal_entity_id: legalEntityId != null ? String(legalEntityId) : undefined,
    })}`,
  );
}

export function getEscrituraState(caseId: number) {
  return apiFetch<EscrituraStateResponse>(`/api/v1/escritura/cases/${caseId}`);
}

export function saveEscrituraState(caseId: number, acto: ActoCode, state: EscrituraStatePayload) {
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

export function extraerEscritura(caseId: number, archivo: File) {
  const formData = new FormData();
  formData.set("archivo", archivo);
  return apiUpload<GariExtraccionResponse>(`/api/v1/escritura/cases/${caseId}/extraer`, formData);
}

export function redactarProsaGari(acto: ActoCode, contexto: CaseState, instruccion: string) {
  return apiFetch<GariProsaResponse>("/api/v1/escritura/redaccion/prosa", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: { acto, contexto, instruccion },
  });
}

export function clasificarEscritura(descripcion: string) {
  return apiFetch<GariClasificacionResponse>("/api/v1/escritura/clasificar", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: { descripcion },
  });
}

export function revisarEscritura(caseId: number, acto: ActoCode, html?: string) {
  return apiFetch<GariRevisionResponse>(`/api/v1/escritura/cases/${caseId}/revisar`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: { acto, html },
  });
}

export function escrituraDownloadUrl(downloadUrl: string) {
  return /^https?:\/\//i.test(downloadUrl) ? downloadUrl : buildApiUrl(downloadUrl);
}
