import { getToken } from "@/lib/auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8001";

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
};

export type MinutaNotaria = {
  nombre_notaria: string | null;
  municipio_notaria: string | null;
  numero_escritura: string | null;
};

export type MinutaDatos = {
  personas: MinutaPersona[];
  valores: MinutaValor[];
  inmueble: MinutaInmueble | null;
  notaria: MinutaNotaria | null;
  actos: string[];
  decisiones: Record<string, boolean | null>;
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
  if (response.status === 401) throw new Error("La sesión expiró. Ingresa nuevamente.");
  if (response.status === 403) throw new Error("No tienes permisos para ejecutar esta acción.");
  let detail = text;
  try {
    const parsed = JSON.parse(text) as { detail?: unknown };
    if (parsed.detail) detail = typeof parsed.detail === "string" ? parsed.detail : JSON.stringify(parsed.detail);
  } catch { /* plain text error */ }
  throw new Error(detail || "No fue posible completar la solicitud.");
}

// ─── Public API ───────────────────────────────────────────────────────────────

export async function analyzeMinuta(file: File): Promise<MinutaAnalisisResult> {
  const form = new FormData();
  form.append("archivo", file);
  const response = await fetch(`${API_URL}/api/v1/minuta/analizar`, {
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
): Promise<{ blob: Blob; filename: string }> {
  const form = new FormData();
  form.append("archivo", file);
  form.append("datos_anteriores", JSON.stringify(datosAnteriores));
  form.append("datos_nuevos", JSON.stringify(datosNuevos));
  const response = await fetch(`${API_URL}/api/v1/minuta/generar`, {
    method: "POST",
    headers: authHeaders(),
    body: form,
    cache: "no-store",
    credentials: "include",
  });
  if (!response.ok) await handleError(response);
  const blob = await response.blob();
  const cd = response.headers.get("content-disposition") ?? "";
  const match = cd.match(/filename="?([^";\n]+)"?/);
  const filename = match?.[1] ?? `minuta_generada_${file.name}`;
  return { blob, filename };
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
