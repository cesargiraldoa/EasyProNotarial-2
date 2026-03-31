const BROKEN_TEXT_MARKERS = ["Ã", "Â", "â", "ƒ", "’", "‚", "\u00ad", "\ufffd"];

const COMMON_TEXT_REPAIRS: Array<[string, string]> = [
  ["Gesti?n", "Gestión"],
  ["Notar?a", "Notaría"],
  ["Revisi?n", "Revisión"],
  ["Validaci?n", "Validación"],
  ["Operaci?n", "Operación"],
  ["Sesi?n", "Sesión"],
  ["Configuraci?n", "Configuración"],
  ["Aprobaci?n", "Aprobación"],
  ["observaci?n", "observación"],
  ["Observaci?n", "Observación"],
  ["Exportaci?n", "Exportación"],
  ["creaci?n", "creación"],
  ["descripci?n", "descripción"],
  ["Descripci?n", "Descripción"],
  ["distribuci?n", "distribución"],
  ["Composici?n", "Composición"],
  ["atenci?n", "atención"],
  ["presi?n", "presión"],
  ["acci?n", "acción"],
  ["asignaci?n", "asignación"],
  ["m?s", "más"],
  ["M?s", "Más"],
  ["d?a", "día"],
  ["D?a", "Día"],
  ["a?o", "año"],
  ["A?o", "Año"],
  ["cuant?a", "cuantía"],
  ["Extensi?n", "Extensión"],
  ["Versi?n", "Versión"],
  ["versi?n", "versión"],
  ["todav?a", "todavía"],
  ["n?mero", "número"],
  ["N?mero", "Número"],
  ["v?lido", "válido"],
  ["profesi?n", "profesión"],
  ["direcci?n", "dirección"],
  ["notar?a", "notaría"],
  ["notarÃ­as", "notarías"],
  ["Bogot?", "Bogotá"],
  ["C?rculo", "Círculo"],
  ["cat?logo", "catálogo"],
  ["p?blica", "pública"],
  ["Mar?a", "María"],
  ["Mej?a", "Mejía"],
  ["Ben?tez", "Benítez"],
  ["G?mez", "Gómez"],
  ["Andr?s", "Andrés"],
  ["Medell?n", "Medellín"],
  ["Espa?ola", "Española"],
  ["Uni?n", "Unión"],
  ["?tiles", "útiles"],
];

function tryDecodeMojibake(value: string): string {
  try {
    const bytes = Uint8Array.from([...value].map((char) => char.charCodeAt(0) & 0xff));
    return new TextDecoder("utf-8", { fatal: false }).decode(bytes);
  } catch {
    return value;
  }
}

export function repairText(value: string | null | undefined): string {
  if (!value) return "";

  let result = value.trim();
  if (!result) return "";

  for (const [broken, fixed] of COMMON_TEXT_REPAIRS) {
    result = result.replaceAll(broken, fixed);
  }

  for (let attempt = 0; attempt < 4; attempt += 1) {
    if (!BROKEN_TEXT_MARKERS.some((marker) => result.includes(marker))) {
      break;
    }

    const repaired = tryDecodeMojibake(result);
    if (!repaired || repaired === result) {
      break;
    }
    result = repaired;
  }

  return result.replace(/\s{2,}/g, " ").trim();
}

export function cleanText(value: unknown, fallback = ""): string {
  if (typeof value !== "string") return fallback;
  const repaired = repairText(value);
  return repaired || fallback;
}

export function cleanNullableText(value: unknown): string | null {
  if (typeof value !== "string") return null;
  const repaired = repairText(value);
  return repaired || null;
}

export function sanitizeTextDeep<T>(value: T): T {
  if (typeof value === "string") {
    return repairText(value) as T;
  }
  if (Array.isArray(value)) {
    return value.map((item) => sanitizeTextDeep(item)) as T;
  }
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>).map(([key, item]) => [key, sanitizeTextDeep(item)]),
    ) as T;
  }
  return value;
}

export function joinReadable(parts: Array<string | null | undefined>, separator = " · "): string {
  return parts.map((part) => repairText(part)).filter(Boolean).join(separator);
}
