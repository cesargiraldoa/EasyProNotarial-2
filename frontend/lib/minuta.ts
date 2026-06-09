import { getToken } from "@/lib/auth";
import { buildApiUrl } from "@/lib/config";

// ─── Types ────────────────────────────────────────────────────────────────────

export type MinutaPersona = {
  rol: string;
  nombre_completo: string | null;
  tipo_documento: string | null;
  numero_documento: string | null;
  genero: string | null;
  estado_civil: string | null;
  nacionalidad: string | null;
  domicilio: string | null;
  direccion: string | null;
  telefono: string | null;
  email: string | null;
  profesion: string | null;
  actividad_economica: string | null;
};

export type MinutaValor = {
  tipo: string;
  monto_numerico: number | null;
  texto_en_documento: string | null;
  acto_relacionado: number | null;
};

export type MinutaInmueble = {
  tipo: string | null;
  numero: string | null;
  matricula_inmobiliaria: string | null;
  conjunto_o_edificio: string | null;
  municipio: string | null;
  departamento: string | null;
  coeficiente_copropiedad: string | null;
  linderos: string | null;
  cedula_catastral: string | null;
  codigo_catastral: string | null;
  area_construida: string | null;
  area_privada: string | null;
  area_total: string | null;
  direccion: string | null;
  barrio: string | null;
  piso: string | null;
  nota_linderos: string | null;
  propiedad_horizontal: string | null;
};

export type MinutaNotaria = {
  nombre_notaria: string | null;
  municipio_notaria: string | null;
  numero_escritura: string | null;
};

export interface MinutaFechas {
  fecha_otorgamiento: string;
  fecha_otorgamiento_letras: string;
}

export type MinutaAdquisicion = {
  forma_adquisicion: string | null;
  escritura_numero: string | null;
  fecha_escritura_anterior: string | null;
  notaria_anterior: string | null;
  municipio_notaria_anterior: string | null;
  vendedor_original: string | null;
};

export type MinutaDatos = {
  personas: MinutaPersona[];
  valores: MinutaValor[];
  inmueble: MinutaInmueble | null;
  notaria: MinutaNotaria | null;
  actos: string[];
  decisiones: Record<string, boolean | null>;
  fechas?: MinutaFechas;
  adquisicion?: MinutaAdquisicion | null;
};

export type MinutaAnalisisResult = {
  archivo: string;
  modo_detectado: "B1" | "B2";
  confianza_modo: number;
  senales_clasificacion: {
    b2: { cedulas: number; nombres_mayus: number; valores_monetarios: number; total: number };
    b1: { placeholders_xxx: number; lineas_subrayadas: number; brackets: number; llaves: number; total: number };
  };
  datos: MinutaDatos;
  costo_usd: number;
  tokens: { prompt_tokens: number; completion_tokens: number; total_tokens: number };
  chars: number;
  texto_original?: string;
  validacion?: MinutaValidacion;
};

export interface MinutaValidacionCampo {
  estado: 'ok' | 'advertencia' | 'faltante' | 'inferido'
  mensaje: string | null
  valor_inferido?: string | null
}

export interface MinutaValidacion {
  resumen: {
    total_campos: number
    campos_ok: number
    campos_advertencia: number
    campos_faltantes: number
    campos_inferidos: number
    nivel_confianza: 'alto' | 'medio' | 'bajo'
    listo_para_generar: boolean
  }
  personas: Array<{
    rol: string
    nombre: string
    validaciones: Record<string, MinutaValidacionCampo>
  }>
  inmueble: Record<string, MinutaValidacionCampo>
  notaria: Record<string, MinutaValidacionCampo>
  valores: Array<{ tipo: string; estado: string; mensaje: string | null }>
  alertas_criticas: string[]
  inferencias_aplicadas: string[]
  campos_faltantes_obligatorios: string[]
  tokens?: { prompt_tokens: number; completion_tokens: number; total_tokens: number }
  costo_usd?: number
  error?: string
}

export type MinutaGenerarResult = {
  case_id: number | null;
  document_id: number | null;
  version_id: number | null;
  filename: string;
  onlyoffice_path: string;
  download_url?: string;
  estadisticas?: {
    total_reemplazos: number;
    por_etiqueta: Record<string, number>;
    no_encontrados: { etiqueta: string; viejo: string; nuevo: string }[];
  };
};

export type MarkedTemplateField = {
  key: string;
  label: string;
  section: string;
  occurrences: number;
  marker_types: string[];
  raw_markers: string[];
};

export type MarkedTemplateDetectResult = {
  fields: MarkedTemplateField[];
  total_fields: number;
  total_occurrences: number;
  marker_types: {
    bracket: number;
    curly: number;
    parenthesis: number;
    highlight: number;
  };
};

// ─── Internal helpers ─────────────────────────────────────────────────────────

function authHeaders(): Headers {
  const headers = new Headers();
  const token = getToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  return headers;
}

async function handleError(response: Response): Promise<never> {
  const text = await response.text().catch(() => "");
  if (response.status === 401) throw new Error("La sesion expiro. Ingresa nuevamente.");
  if (response.status === 403) throw new Error("No tienes permisos para ejecutar esta accion.");
  let detail = text;
  try {
    const parsed = JSON.parse(text) as { detail?: unknown };
    if (parsed.detail) detail = typeof parsed.detail === "string" ? parsed.detail : JSON.stringify(parsed.detail);
  } catch { /* plain text error */ }
  throw new Error(detail || "No fue posible completar la solicitud.");
}

/**
 * Limpia cada campo string de cada persona antes de JSON.stringify.
 * Elimina caracteres de control (saltos de linea, tabs, NULL, etc.) que
 * producen JSON malformado al llegar como campo multipart al backend.
 */
function sanitizeDatos(datos: MinutaDatos): MinutaDatos {
  const cleanStr = (v: string): string =>
    v
      .replace(/\r\n/g, " ")
      .replace(/[\r\n\t\x00]/g, " ")
      .replace(/\s+/g, " ")
      .trim();

  return {
    ...datos,
    personas: datos.personas.map((p) => ({
      rol: cleanStr(p.rol) || p.rol,
      nombre_completo: p.nombre_completo != null ? cleanStr(p.nombre_completo) || null : null,
      tipo_documento: p.tipo_documento != null ? cleanStr(p.tipo_documento) || null : null,
      numero_documento: p.numero_documento != null ? cleanStr(p.numero_documento) || null : null,
      genero: p.genero != null ? cleanStr(p.genero) || null : null,
      estado_civil: p.estado_civil != null ? cleanStr(p.estado_civil) || null : null,
      nacionalidad: p.nacionalidad != null ? cleanStr(p.nacionalidad) || null : null,
      domicilio: p.domicilio != null ? cleanStr(p.domicilio) || null : null,
      direccion: p.direccion != null ? cleanStr(p.direccion) || null : null,
      telefono: p.telefono != null ? cleanStr(p.telefono) || null : null,
      email: p.email != null ? cleanStr(p.email) || null : null,
      profesion: p.profesion != null ? cleanStr(p.profesion) || null : null,
      actividad_economica: p.actividad_economica != null ? cleanStr(p.actividad_economica) || null : null,
    })),
  };
}

// ─── Public API ───────────────────────────────────────────────────────────────

export async function analyzeMinuta(file: File): Promise<MinutaAnalisisResult> {
  const form = new FormData();
  form.append("archivo", file);
  const response = await fetch(buildApiUrl("/api/v1/minuta/analizar"), {
    method: "POST",
    headers: authHeaders(),
    body: form,
    cache: "no-store",
    credentials: "include",
  });
  if (!response.ok) await handleError(response);
  return response.json() as Promise<MinutaAnalisisResult>;
}

export async function generateMinuta(
  file: File,
  datosAnteriores: MinutaDatos,
  datosNuevos: MinutaDatos,
): Promise<MinutaGenerarResult> {
  const form = new FormData();
  form.append("archivo", file);
  form.append("datos_anteriores", JSON.stringify(sanitizeDatos(datosAnteriores)));
  form.append("datos_nuevos", JSON.stringify(sanitizeDatos(datosNuevos)));
  const response = await fetch(buildApiUrl("/api/v1/minuta/generar"), {
    method: "POST",
    headers: authHeaders(),
    body: form,
    cache: "no-store",
    credentials: "include",
  });
  if (!response.ok) await handleError(response);
  return response.json() as Promise<MinutaGenerarResult>;
}

export async function detectMarkedTemplate(file: File): Promise<MarkedTemplateDetectResult> {
  const form = new FormData();
  form.append("archivo", file);
  const response = await fetch(buildApiUrl("/api/v1/minutas/marked-template/detect"), {
    method: "POST",
    headers: authHeaders(),
    body: form,
    cache: "no-store",
    credentials: "include",
  });
  if (!response.ok) await handleError(response);
  return response.json() as Promise<MarkedTemplateDetectResult>;
}

export async function generateMarkedTemplate(
  file: File,
  values: Record<string, string>,
  fields: MarkedTemplateField[],
): Promise<MinutaGenerarResult> {
  const form = new FormData();
  form.append("archivo", file);
  form.append("values", JSON.stringify(values ?? {}));
  form.append("fields", JSON.stringify(fields ?? []));
  const response = await fetch(buildApiUrl("/api/v1/minutas/marked-template/generate"), {
    method: "POST",
    headers: authHeaders(),
    body: form,
    cache: "no-store",
    credentials: "include",
  });
  if (!response.ok) await handleError(response);
  return response.json() as Promise<MinutaGenerarResult>;
}

export async function getMinutaOnlyOfficeConfig(token: string): Promise<Record<string, unknown>> {
  const response = await fetch(
    buildApiUrl(`/api/v1/minuta/onlyoffice-config?token=${encodeURIComponent(token)}`),
    {
      method: "GET",
      headers: authHeaders(),
      cache: "no-store",
      credentials: "include",
    },
  );
  if (!response.ok) await handleError(response);
  return response.json() as Promise<Record<string, unknown>>;
}

// ─── Util ─────────────────────────────────────────────────────────────────────

export function emptyPersona(rol = ""): MinutaPersona {
  return {
    rol,
    nombre_completo: null,
    tipo_documento: null,
    numero_documento: null,
    genero: null,
    estado_civil: null,
    nacionalidad: null,
    domicilio: null,
    direccion: null,
    telefono: null,
    email: null,
    profesion: null,
    actividad_economica: null,
  };
}
