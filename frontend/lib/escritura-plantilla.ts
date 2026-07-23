// Relleno de plantillas semilla: sustituye {{tokens}} por los valores del
// formulario y resuelve los condicionales [[if ...]]...[[/if]]. El resultado
// es el cuerpo base que se carga en el editor de Redacción para completarse.

export type PlantillaState = Record<string, unknown>;

const MONEY_TOKENS = new Set(["total", "inicial", "saldo", "avaluoCatastral"]);
const DATE_TOKENS = new Set(["fechaOtorg", "tituloFecha"]);

const MESES = [
  "enero", "febrero", "marzo", "abril", "mayo", "junio",
  "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
];

const ENUM_LABELS: Record<string, Record<string, string>> = {
  derecho: {
    dominio: "el derecho de dominio",
    nuda: "la nuda propiedad",
    usufructo: "el derecho de usufructo",
    cuota: "la cuota parte de dominio",
    uso: "el derecho de uso y habitación",
  },
  tipoNegocio: {
    compraventa: "compraventa",
    permuta: "permuta",
    dacion: "dación en pago",
    retroventa: "compraventa con pacto de retroventa",
    reserva: "compraventa con reserva de dominio",
  },
  tituloTipo: {
    compraventa: "compraventa",
    sucesion: "adjudicación en sucesión",
    donacion: "donación",
    remate: "adjudicación en remate",
    prescripcion: "sentencia de pertenencia (prescripción)",
  },
  gravamen: {
    libre: "libre de todo gravamen y limitación al dominio",
    hipoteca_previa: "con hipoteca previa",
    patrimonio: "afectado con patrimonio de familia inembargable",
    usufructo: "con usufructo vigente",
    servidumbre: "con servidumbres constituidas",
    leasing: "en leasing habitacional",
    embargo: "con medida de embargo",
  },
  afect: { no: "no", si: "sí", nosabe: "no sabe" },
  estado: {
    soltero: "soltero(a)",
    casado_sc: "casado(a) con sociedad conyugal vigente",
    union: "en unión marital de hecho",
    divorciado: "divorciado(a)",
    viudo: "viudo(a)",
  },
};

export function resolvePath(state: PlantillaState, path: string): unknown {
  const segments = path.split(".");
  let current: unknown = state;
  for (const segment of segments) {
    if (current == null) return undefined;
    if (Array.isArray(current)) {
      const index = Number(segment);
      current = Number.isInteger(index) ? current[index] : undefined;
    } else if (typeof current === "object") {
      current = (current as Record<string, unknown>)[segment];
    } else {
      return undefined;
    }
  }
  return current;
}

function formatMoney(value: unknown): string {
  const num = typeof value === "number" ? value : Number(value);
  if (!Number.isFinite(num) || num === 0) return "";
  return "$" + Math.round(num).toLocaleString("es-CO");
}

function formatDate(value: unknown): string {
  if (typeof value !== "string" || !value.trim()) return "";
  const match = /^(\d{4})-(\d{2})-(\d{2})/.exec(value.trim());
  if (!match) return value.trim();
  const [, year, month, day] = match;
  const mes = MESES[Number(month) - 1] ?? month;
  return `${Number(day)} de ${mes} de ${year}`;
}

function lastSegment(token: string): string {
  const parts = token.split(".");
  return parts[parts.length - 1];
}

export function formatToken(token: string, value: unknown): string {
  if (MONEY_TOKENS.has(token)) return formatMoney(value);
  if (DATE_TOKENS.has(token)) return formatDate(value);
  const key = lastSegment(token);
  const labels = ENUM_LABELS[key];
  if (labels && typeof value === "string" && value in labels) return labels[value];
  if (value == null) return "";
  if (typeof value === "boolean") return value ? "sí" : "";
  return String(value).trim();
}

function evalCondition(condition: string, state: PlantillaState): boolean {
  const cond = condition.trim();
  const inMatch = /^(\S+)\s+in\s+(.+)$/.exec(cond);
  if (inMatch) {
    const value = resolvePath(state, inMatch[1]);
    const options = inMatch[2].split("|").map((option) => option.trim());
    return typeof value === "string" && options.includes(value);
  }
  const value = resolvePath(state, cond);
  // `vis` es un enum ("no"|"sfve"|"otra"): verdadero cuando no es "no".
  if (cond === "vis") return typeof value === "string" && value !== "no" && value !== "";
  return Boolean(value);
}

// Resuelve [[if COND]]...[[/if]] de adentro hacia afuera (soporta anidamiento).
export function applyConditionals(html: string, state: PlantillaState): string {
  const innermost = /\[\[if ([^\]]+)\]\]((?:(?!\[\[if )[\s\S])*?)\[\[\/if\]\]/;
  let output = html;
  let guard = 0;
  while (innermost.test(output) && guard < 500) {
    output = output.replace(innermost, (_match, condition: string, inner: string) =>
      evalCondition(condition, state) ? inner : "",
    );
    guard += 1;
  }
  return output;
}

const BLANK = "__________";

export function fillPlantilla(bodyHtml: string, state: PlantillaState): string {
  const withConditionals = applyConditionals(bodyHtml, state);
  return withConditionals.replace(/\{\{([a-zA-Z0-9_.]+)\}\}/g, (_match, token: string) => {
    const value = resolvePath(state, token);
    const formatted = formatToken(token, value);
    return formatted || BLANK;
  });
}
