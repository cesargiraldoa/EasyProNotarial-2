// Valores oficiales extraídos de Listas_Desplegables.xlsx — Notaría Única de Caldas

import { EASYPRO1_NOTARIAL_CATALOGS, type NotarialCatalogOption } from "./easypro1-notarial-catalogs";
import { sanitizeDropdownOptions } from "./dropdown-options";

export const ESTADOS_CIVILES_F = [
  'soltera con unión marital de hecho y sociedad patrimonial sin declarar',
  'soltera por efectos de divorcio con sociedad conyugal disuelta e ilíquida',
  'soltera con unión marital de hecho con sociedad patrimonial disuelta y liquidada',
  'casada sin sociedad conyugal por efecto de capitulaciones',
  'casada con sociedad conyugal disuelta y liquidada',
  'casada con sociedad conyugal vigente',
  'soltera por efecto de divorcio con sociedad conyugal disuelta y liquidada',
  'soltera con unión marital de hecho sin sociedad patrimonial por efecto de capitulaciones',
  'soltera por efecto de viudedad con sociedad conyugal disuelta e ilíquida',
  'soltera por efecto de viudedad con sociedad conyugal disuelta y liquidada',
  'soltera con unión marital de hecho',
  'soltera sin unión marital de hecho',
]

export const ESTADOS_CIVILES_M = [
  'soltero con unión marital de hecho y sociedad patrimonial sin declarar',
  'soltero con unión marital de hecho con sociedad patrimonial disuelta y liquidada',
  'casado sin sociedad conyugal por efecto de capitulaciones',
  'casado con sociedad conyugal disuelta y liquidada',
  'casado con sociedad conyugal vigente',
  'soltero por efecto de divorcio con sociedad conyugal disuelta y liquidada',
  'soltero con unión marital de hecho sin sociedad patrimonial por efecto de capitulaciones',
  'soltero por efecto de viudedad con sociedad conyugal disuelta e ilíquida',
  'soltero por efecto de viudedad con sociedad conyugal disuelta y liquidada',
  'soltero con unión marital de hecho',
  'soltero sin unión marital de hecho',
]

// Compartidos — aplican a ambos géneros
export const ESTADOS_CIVILES_COMPARTIDOS = [
  'casados entre sí, con sociedad conyugal vigente',
]

export const ESTADOS_CIVILES_GENERALES = [
  { label: 'Soltero', value: 'soltero' },
  { label: 'Soltera', value: 'soltera' },
  { label: 'Casado', value: 'casado' },
  { label: 'Casada', value: 'casada' },
  { label: 'Unión marital de hecho', value: 'unión marital de hecho' },
  { label: 'Divorciado', value: 'divorciado' },
  { label: 'Divorciada', value: 'divorciada' },
  { label: 'Viudo', value: 'viudo' },
  { label: 'Viuda', value: 'viuda' },
]

export const TIPOS_DOCUMENTO = [
  { label: 'Cédula de ciudadanía', value: 'C.C' },
  { label: 'Cédula de extranjería', value: 'C.E' },
  { label: 'Tarjeta de identidad', value: 'T.I' },
  { label: 'Pasaporte', value: 'PAS' },
  { label: 'Permiso de protección temporal', value: 'P.P.T' },
  { label: 'Registro civil', value: 'R.C' },
  { label: 'NIT', value: 'NIT' },
]

function uniqueCatalogOptions(options: { label: string; value: string }[]) {
  const seen = new Set<string>();
  const deduped = options.filter((option) => {
    const key = `${option.value}::${option.label}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
  return sanitizeDropdownOptions(deduped);
}

export const NACIONALIDADES = uniqueCatalogOptions([
  ...(EASYPRO1_NOTARIAL_CATALOGS["NACIONALIDAD"] ?? []),
  { value: "Otro", label: "Otro" },
]);

export const PAISES = uniqueCatalogOptions([
  ...(EASYPRO1_NOTARIAL_CATALOGS["PAIS"] ?? []),
]);

export const NACIONALIDADES_J = uniqueCatalogOptions([
  { value: 'Colombiana', label: 'Colombiana' },
  { value: 'Extranjera', label: 'Extranjera' },
  { value: 'No aplica', label: 'No aplica' },
]);

export const TIPO_DOCUMENTO = sanitizeDropdownOptions(TIPOS_DOCUMENTO);

export const ESTADO_CIVIL = uniqueCatalogOptions(
  ESTADOS_CIVILES_GENERALES.map((option) => ({ value: option.value, label: option.label })),
);

export const OFICINAS_DE_REGISTRO = uniqueCatalogOptions([
  ...(EASYPRO1_NOTARIAL_CATALOGS["OFICINA_REGISTRO"] ?? []),
]);

export const DIAS = uniqueCatalogOptions([
  ...(EASYPRO1_NOTARIAL_CATALOGS["DIAS"] ?? []),
]);

export const TIPO_DE_PREDIO = uniqueCatalogOptions([
  { value: "Urbano", label: "Urbano" },
  { value: "Rural", label: "Rural" },
  { value: "Mixto", label: "Mixto" },
]);

function normalizeCatalogText(value: string) {
  return value
    .trim()
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '');
}

function classifyNationalityLabel(label: string): 'M' | 'F' | 'J' | 'N' {
  const normalized = normalizeCatalogText(label);
  if (!normalized) return 'N';

  if (['colombiana', 'venezolana', 'ecuatoriana', 'peruana', 'argentina', 'espanola', 'chilena', 'panamena', 'mexicana', 'guatemalteca', 'francesa', 'alemana', 'boliviana', 'brasilena', 'cubana', 'costarricense', 'dominicana', 'italiana'].some((term) => normalized === term)) {
    return 'F';
  }
  if (['colombiano', 'venezolano', 'ecuatoriano', 'peruano', 'argentino', 'espanol', 'chileno', 'panameno', 'mexicano', 'guatemalteco', 'frances', 'aleman', 'boliviano', 'brasileno', 'cubano', 'costarricense', 'dominicano', 'italiano'].some((term) => normalized === term)) {
    return 'M';
  }

  const feminineSuffixes = ['a', 'ana', 'esa', 'ina', 'ora', 'era', 'iva', 'ola'];
  const masculineSuffixes = ['o', 'or', 'ol', 'an', 'en', 'in', 'es', 'ero', 'no', 'lo', 'to', 'go', 'co'];

  const feminineMatch = feminineSuffixes.some((suffix) => normalized.endsWith(suffix));
  const masculineMatch = masculineSuffixes.some((suffix) => normalized.endsWith(suffix));

  if (feminineMatch && !masculineMatch) return 'F';
  if (masculineMatch && !feminineMatch) return 'M';
  return 'N';
}

export function getNacionalidadesPorGenero(genero: 'M' | 'F' | 'J' | '' = '') {
  if (genero === 'J') return [...NACIONALIDADES_J];

  if (genero === 'M' || genero === 'F') {
    return NACIONALIDADES.filter((option) => {
      const category = classifyNationalityLabel(option.label);
      if (category === 'N') return true;
      return category === genero;
    });
  }

  return [...NACIONALIDADES];
}

export const NOTAS_LINDEROS = [
  'Por no estar descrito(s) lo(s) lindero(s) de lo(s) biene(s) inmueble(s) objeto del presente acto, en el certificado de tradición y libertad, se procede a transcribirlos, dando cumplimiento a lo orientado por la instrucción administrativa No. 01 del 13-04-2016 de la Superintendencia de Notariado y Registro',
  'A solicitud y ruego de los otorgantes, se procedió a efectuar en este instrumento la transcripción de los linderos del bien objeto de este contrato',
]

// Helper — retorna opciones de estado civil según género
export function getEstadosCiviles(genero: 'M' | 'F' | 'J' | '' = ''): string[] {
  if (genero === 'F') return [...ESTADOS_CIVILES_F, ...ESTADOS_CIVILES_COMPARTIDOS]
  if (genero === 'M') return [...ESTADOS_CIVILES_M, ...ESTADOS_CIVILES_COMPARTIDOS]
  return [...ESTADOS_CIVILES_M, ...ESTADOS_CIVILES_F, ...ESTADOS_CIVILES_COMPARTIDOS]
}

export type MarkedFieldInputType = "select" | "textarea" | "input";

export type MarkedFieldOptionsContext = {
  gender?: 'M' | 'F' | 'J' | null;
};

function normalizeMarkedCatalogKey(value: string) {
  return value
    .trim()
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/_+/g, '_')
    .replace(/^_+|_+$/g, '');
}

export function isGenderField(fieldKey: string): boolean {
  const key = normalizeMarkedCatalogKey(fieldKey);
  if (!key) return false;

  return [
    /^genero(?:_.+)?$/,
    /^sexo(?:_.+)?$/,
    /^.+_(?:genero|sexo)$/,
    /^.+_es_hombre_o_mujer$/,
    /^.+_es_hombre_0_mujer$/,
    /^es_hombre_o_mujer$/,
    /^es_hombre_0_mujer$/,
  ].some((pattern) => pattern.test(key));
}

function markedKeyMatches(fieldKey: string, terms: string[]) {
  const normalizedKey = normalizeMarkedCatalogKey(fieldKey);
  return terms.some((term) => normalizedKey.includes(normalizeMarkedCatalogKey(term)));
}

export function getMarkedFieldListType(fieldKey: string): string | null {
  const key = normalizeMarkedCatalogKey(fieldKey);
  if (!key) return null;

  if (key === "nota_linderos") return "NOTA LINDEROS";
  if (key === "dia_elaboracion_escritura" || key === "dia_elaboracion") return "DIAS";
  if (markedKeyMatches(key, ["estado_civil"])) return "ESTADO CIVIL";
  if (markedKeyMatches(key, ["tipo_documento", "tipo_de_documento"])) return "TIPO DE DOCUMENTO";
  if (markedKeyMatches(key, ["oficina_de_registro", "notaria_de_registro", "notaria_registro"])) return "OFICINAS DE REGISTRO";
  if (markedKeyMatches(key, ["tipo_de_predio"])) return "TIPO DE PREDIO";
  if (markedKeyMatches(key, ["nacionalidad"])) return "NACIONALIDAD";
  return null;
}

export function getMarkedFieldInputType(fieldKey: string): MarkedFieldInputType | null {
  const key = normalizeMarkedCatalogKey(fieldKey);
  if (!key) return null;

  if (markedKeyMatches(key, ["nota_linderos", "dia_elaboracion_escritura", "dia_elaboracion", "estado_civil", "tipo_documento", "tipo_de_documento", "oficina_de_registro", "notaria_de_registro", "notaria_registro", "tipo_de_predio", "nacionalidad"])) {
    return "select";
  }

  if (markedKeyMatches(key, ["linderos", "descripcion_del_inmueble", "acto_de_adquisicion"])) {
    return "textarea";
  }

  return null;
}

export function getOptionsForMarkedField(fieldKey: string, context: MarkedFieldOptionsContext = {}): NotarialCatalogOption[] {
  const listType = getMarkedFieldListType(fieldKey);
  const gender = context.gender ?? "";

  if (listType === "ESTADO CIVIL") {
    return getEstadosCiviles(gender).map((value) => ({ value, label: value }));
  }

  if (listType === "TIPO DE DOCUMENTO") {
    return [...TIPO_DOCUMENTO];
  }

  if (listType === "OFICINAS DE REGISTRO") {
    return [...OFICINAS_DE_REGISTRO];
  }

  if (listType === "NOTA LINDEROS") {
    return [...NOTAS_LINDEROS].map((value) => ({ value, label: value }));
  }

  if (listType === "TIPO DE PREDIO") {
    return [...TIPO_DE_PREDIO];
  }

  if (listType === "DIAS") {
    return [...DIAS];
  }

  if (listType === "NACIONALIDAD") {
    return getNacionalidadesPorGenero(gender as 'M' | 'F' | 'J' | '');
  }

  return [];
}
