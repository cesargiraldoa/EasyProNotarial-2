// Valores oficiales extraídos de Listas_Desplegables.xlsx — Notaría Única de Caldas

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

export const TIPOS_DOCUMENTO = [
  { label: 'Cédula de ciudadanía', value: 'C.C' },
  { label: 'Cédula de extranjería', value: 'C.E' },
  { label: 'Tarjeta de identidad', value: 'T.I' },
  { label: 'Pasaporte', value: 'PAS' },
  { label: 'Permiso de protección temporal', value: 'P.P.T' },
  { label: 'Registro civil', value: 'R.C' },
  { label: 'NIT', value: 'NIT' },
]

export const NOTAS_LINDEROS = [
  'Por no estar descrito(s) lo(s) lindero(s) de lo(s) biene(s) inmueble(s) objeto del presente acto, en el certificado de tradición y libertad, se procede a transcribirlos, dando cumplimiento a lo orientado por la instrucción administrativa No. 01 del 13-04-2016 de la Superintendencia de Notariado y Registro',
  'A solicitud y ruego de los otorgantes, se procedió a efectuar en este instrumento la transcripción de los linderos del bien objeto de este contrato',
]

// Helper — retorna opciones de estado civil según género
export function getEstadosCiviles(genero: 'M' | 'F' | 'J' | ''): string[] {
  if (genero === 'F') return [...ESTADOS_CIVILES_F, ...ESTADOS_CIVILES_COMPARTIDOS]
  if (genero === 'M') return [...ESTADOS_CIVILES_M, ...ESTADOS_CIVILES_COMPARTIDOS]
  return [...ESTADOS_CIVILES_M, ...ESTADOS_CIVILES_F, ...ESTADOS_CIVILES_COMPARTIDOS]
}
