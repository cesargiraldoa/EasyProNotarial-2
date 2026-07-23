export type ActoCode = "compraventa" | "hipoteca" | "cancelacion";
export type GeneroCode = "M" | "F" | "NB" | "T";
export type TipoPersona = "natural" | "juridica";
export type TipoDoc = "CC" | "CE" | "PA" | "TI" | "RC" | "PPT" | "NIT";
export type EstadoCivil = "soltero" | "casado_sc" | "union" | "divorciado" | "viudo";
export type CumplimientoTipo = "ok" | "obl" | "warn" | "crit";

export interface Party {
  tipo: TipoPersona;
  genero: GeneroCode;
  tipoDoc: TipoDoc;
  nombre: string;
  id: string;
  ciudad: string;
  estado: EstadoCivil;
  repr: string;
  cuota: number;
  direccion: string;
  telefono: string;
  correo: string;
  ocupacion: string;
  notiElec: boolean;
  pep: boolean;
}

export interface AuxParty {
  tipoDoc: TipoDoc;
  nombre: string;
  id: string;
  ciudad: string;
  direccion: string;
  telefono: string;
  correo: string;
  ocupacion: string;
}

export type FolioEstado = "matriz" | "segregado" | "englobe" | "desenglobe" | "mayor_extension" | "falsa_tradicion";

export interface CompraventaInmueble {
  descripcion: string;
  linderos: string;
  matricula: string;
  catastral: string;
  nupre: string;
  avaluoCatastral?: number;
}

export interface EncadenamientosCompraventa {
  cancelacionHipotecaPrevia?: boolean;
  cancelacionPatrimonioFamilia?: boolean;
  afectacionViviendaFamiliar?: boolean;
  hipotecaPrevia?: {
    acreedor?: string;
    nit?: string;
    escritura?: string;
    fecha?: string;
    notaria?: string;
    registroFecha?: string;
    orip?: string;
    monto?: number;
  };
  patrimonioFamilia?: {
    escritura?: string;
    fecha?: string;
    notaria?: string;
    beneficiarios?: string;
  };
  afectacion?: {
    beneficiarios?: string;
  };
}

export interface CompraventaDivisas {
  parteExtranjeraNoResidente?: boolean;
  pagoDivisas?: boolean;
  registroInversionExtranjera?: boolean;
  canalizacionMercadoCambiario?: boolean;
  poderExteriorApostillado?: boolean;
  declaracionCambio?: string;
  paisOrigenFondos?: string;
  moneda?: string;
  valorDivisas?: number;
}

export interface CompraventaRural {
  predioRural?: boolean;
  baldioAdjudicado?: boolean;
  restriccionTemporal?: boolean;
  superaUaf?: boolean;
  autorizacionAnt?: boolean;
  derechoPreferencia?: boolean;
  municipioRegionUaf?: string;
  areaHectareas?: number;
  uafHectareas?: number;
}

export type ApoyoTipo = "acuerdo" | "adjudicacion";

export interface CompraventaCapacidad {
  menorVendedor?: boolean;
  ventaBienMenor?: boolean;
  autorizacionVentaMenor?: boolean;
  autorizacionDetalle?: string;
  discapacidadConApoyos?: boolean;
  apoyoAcreditado?: boolean;
  apoyoNombre?: string;
  apoyoDocumento?: string;
  apoyoTipo?: ApoyoTipo;
  apoyoActo?: string;
}

export interface CompraventaState {
  derecho: "dominio" | "nuda" | "usufructo" | "cuota" | "uso";
  credito: boolean;
  banco: string;
  bancoNit: string;
  plazoAnios: number;
  numCuotas: number;
  apoderadoBanco: string;
  poderBancoEP: string;
  poderBancoNot: string;
  avaluoCatastral: number;
  nupre: string;
  inmuebles?: CompraventaInmueble[];
  folioEstado?: FolioEstado;
  encadenamientos?: EncadenamientosCompraventa;
  divisas?: CompraventaDivisas;
  rural?: CompraventaRural;
  capacidad?: CompraventaCapacidad;
  apod: boolean;
  apodN: string;
  apodP: string;
  afect: "no" | "si" | "nosabe";
  inmdesc: string;
  linderos: string;
  matricula: string;
  catastral: string;
  ph: boolean;
  phReg: string;
  vis: "no" | "sfve" | "otra";
  tituloNum: string;
  tituloFecha: string;
  tituloNotaria: string;
  gravamen: "libre" | "hipoteca_previa" | "patrimonio" | "usufructo" | "servidumbre" | "leasing" | "embargo";
  tipoNegocio: "compraventa" | "permuta" | "dacion" | "retroventa" | "reserva";
  tituloTipo: "compraventa" | "sucesion" | "donacion" | "remate" | "prescripcion";
  subsidio: boolean;
  subsidioEnt: string;
  posesion2: boolean;
  firmaRuego: boolean;
  interprete: boolean;
  pep: boolean;
  cuentaTercero: boolean;
  pep_indagado: boolean;
  rupta_verificado: boolean;
  numEscritura: string;
  fechaOtorg: string;
  huella: boolean;
  testigosOn: boolean;
  hojaInicial: string;
  pepAny: boolean;
  testigos: AuxParty[];
  ruego: AuxParty;
  total: number;
  inicial: number;
  saldo: number;
  ax: {
    tradicion: boolean;
    predial: boolean;
    admin: boolean;
    cedulas: boolean;
  };
  V: Party[];
  C: Party[];
}

export interface CancelacionState {
  cNum: string;
  cFechaOtorg: string;
  cNotario: string;
  cNotarioGenero: GeneroCode;
  cCalidad: string;
  cActoAdmin: string;
  cBanco: string;
  cBancoNit: string;
  cBancoDom: string;
  cRepTipo: "apoderado" | "replegal";
  cRepCargo: string;
  cApoNombre: string;
  cApoGenero: GeneroCode;
  cApoCC: string;
  cPoderEP: string;
  cPoderFecha: string;
  cPoderNotaria: string;
  cDeudor: string;
  cHipEP: string;
  cHipFecha: string;
  cHipNotaria: string;
  cHipRegFecha: string;
  cOrip: string;
  cHipMonto: number;
  cInmdesc: string;
  cMatricula: string;
  cCatastral: string;
  cNupre: string;
  cHojas: string;
  cRecaudo: number;
  cCorreoNotif: string;
  cSinCuantia: boolean;
  cNoPazSalvo: boolean;
  cSarlaft: boolean;
  cNotiElec: boolean;
}

export type CaseState = CompraventaState | CancelacionState;

interface EvaluacionItem {
  t: CumplimientoTipo;
  h: string;
  p: string;
  n: string;
}

export interface Resultado {
  html: string;
  liquidacionHtml: string;
  cumplimiento: {
    items: { tipo: CumplimientoTipo; titulo: string; detalle: string; norma: string }[];
    tiles: { cumple: number; advertencia: number; bloqueante: number };
  };
  estado: { ok: boolean; texto: string };
}

export const UNI = [
  "",
  "UNO",
  "DOS",
  "TRES",
  "CUATRO",
  "CINCO",
  "SEIS",
  "SIETE",
  "OCHO",
  "NUEVE",
  "DIEZ",
  "ONCE",
  "DOCE",
  "TRECE",
  "CATORCE",
  "QUINCE",
  "DIECISÉIS",
  "DIECISIETE",
  "DIECIOCHO",
  "DIECINUEVE",
  "VEINTE",
  "VEINTIUNO",
  "VEINTIDÓS",
  "VEINTITRÉS",
  "VEINTICUATRO",
  "VEINTICINCO",
  "VEINTISÉIS",
  "VEINTISIETE",
  "VEINTIOCHO",
  "VEINTINUEVE",
] as const;

export const DEC = ["", "", "", "TREINTA", "CUARENTA", "CINCUENTA", "SESENTA", "SETENTA", "OCHENTA", "NOVENTA"] as const;
export const CEN = [
  "",
  "CIENTO",
  "DOSCIENTOS",
  "TRESCIENTOS",
  "CUATROCIENTOS",
  "QUINIENTOS",
  "SEISCIENTOS",
  "SETECIENTOS",
  "OCHOCIENTOS",
  "NOVECIENTOS",
] as const;

const MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"] as const;

export const TARIFAS = {
  anio: 2026,
  resNotarial: "RES-2026-000964-6",
  resRegistral: "RES-2026-001726-6",
  ipc: "5,10%",
  cuantiaMin: 189700,
  derNotarialBase: 22500,
  derNotarialPorMil: 0.003,
  iva: 0.19,
  impuestoRegistro: 0.01,
  retencion: 0.01,
  visDesc: 0.5,
} as const;

type TarifaConfig = {
  anio: number;
  resNotarial: string;
  resRegistral: string;
  ipc: string;
  cuantiaMin: number;
  derNotarialBase: number;
  derNotarialPorMil: number;
  iva: number;
  impuestoRegistro: number;
  retencion: number;
  visDesc: number;
};

export type MotorCorpusTarifa = {
  anio?: number;
  concepto: string;
  valor?: string | number | null;
  formula?: string | null;
  unidad?: string | null;
};

export type MotorCorpus = {
  tarifas?: MotorCorpusTarifa[] | null;
};

function numberTarifa(tarifas: MotorCorpusTarifa[] | undefined | null, concepto: string, fallback: number): number {
  const item = tarifas?.find((tarifa) => tarifa.concepto === concepto);
  if (item?.valor == null) return fallback;
  const raw = typeof item.valor === "number" ? item.valor : String(item.valor).trim();
  const value = typeof raw === "number" ? raw : Number(raw.includes(",") ? raw.replace(/\./g, "").replace(",", ".") : raw);
  return Number.isFinite(value) ? value : fallback;
}

function percentLabel(value: number): string {
  return (value * 100).toFixed(2).replace(".", ",") + "%";
}

function tarifasConfig(corpus?: MotorCorpus): TarifaConfig {
  const tarifas = corpus?.tarifas;
  if (!tarifas?.length) return TARIFAS;
  const ipc = numberTarifa(tarifas, "ajuste_ipc_tarifas_notariales", TARIFAS.ipc === "5,10%" ? 0.051 : 0);
  return {
    ...TARIFAS,
    anio: tarifas.find((tarifa) => typeof tarifa.valor !== "undefined")?.anio ?? TARIFAS.anio,
    ipc: percentLabel(ipc),
    cuantiaMin: numberTarifa(tarifas, "derechos_notariales_umbral_minimo", TARIFAS.cuantiaMin),
    derNotarialBase: numberTarifa(tarifas, "derechos_notariales_minimo_acto_con_cuantia", TARIFAS.derNotarialBase),
    derNotarialPorMil: numberTarifa(tarifas, "derechos_notariales_por_mil", TARIFAS.derNotarialPorMil),
    iva: numberTarifa(tarifas, "iva_sobre_derechos_notariales", TARIFAS.iva),
    impuestoRegistro: numberTarifa(tarifas, "impuesto_registro_antioquia_referencia", TARIFAS.impuestoRegistro),
    retencion: numberTarifa(tarifas, "retencion_fuente_vendedor_persona_natural", TARIFAS.retencion),
    visDesc: numberTarifa(tarifas, "descuento_vis_vip_derechos_notariales", TARIFAS.visDesc),
  };
}

export const GENEROS: [GeneroCode, string][] = [
  ["M", "Masculino"],
  ["F", "Femenino"],
  ["NB", "No binario"],
  ["T", "Transgénero"],
];

const TIPODOC: Record<TipoDoc, string> = {
  CC: "C.C.",
  CE: "C.E.",
  PA: "Pasaporte",
  TI: "T.I.",
  RC: "R.C.",
  PPT: "PPT",
  NIT: "NIT",
};

const DOCFRASE: Partial<Record<TipoDoc, string>> = {
  CC: "la cédula de ciudadanía",
  CE: "la cédula de extranjería",
  PA: "el pasaporte",
  TI: "la tarjeta de identidad",
  RC: "el registro civil",
  PPT: "el permiso por protección temporal (PPT)",
};

export function dos(n: number): string {
  if (n < 30) return UNI[n] ?? "";
  const d = Math.floor(n / 10);
  const u = n % 10;
  return DEC[d] + (u ? " Y " + UNI[u] : "");
}

export function tres(n: number): string {
  if (n === 100) return "CIEN";
  const c = Math.floor(n / 100);
  const r = n % 100;
  return (c ? CEN[c] : "") + (c && r ? " " : "") + (r ? dos(r) : "");
}

export function enLetras(n: number): string {
  n = Math.floor(n);
  if (n === 0) return "CERO";
  const mill = Math.floor(n / 1000000);
  const mil = Math.floor((n % 1000000) / 1000);
  const cen = n % 1000;
  let o = "";
  if (mill) o += mill === 1 ? "UN MILLÓN" : enLetras(mill) + " MILLONES";
  if (mil) o += (o ? " " : "") + (mil === 1 ? "MIL" : tres(mil) + " MIL");
  if (cen) o += (o ? " " : "") + tres(cen);
  return o.trim();
}

export function pts(n?: number): string {
  n = n || 0;
  const neg = n < 0;
  const s = Math.abs(n).toFixed(2);
  const pr = s.split(".");
  const ip = (pr[0] ?? "0").replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  const dc = pr[1] === "00" ? "" : "," + pr[1];
  return (neg ? "-" : "") + ip + dc;
}

export function parseMoney(str: string | number | null | undefined): number {
  if (str == null) return 0;
  const v = ("" + str).replace(/\s/g, "").replace(/\./g, "").replace(",", ".");
  const n = parseFloat(v);
  return Number.isNaN(n) ? 0 : n;
}

export function fmtMoneyStr(raw: string | number): string {
  const v = ("" + raw).replace(/[^\d,]/g, "");
  const parts = v.split(",");
  const ip = (parts[0] ?? "").replace(/^0+(?=\d)/, "") || "";
  const dc = parts.length > 1 ? "," + parts.slice(1).join("").slice(0, 2) : "";
  const fi = ip.replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  return fi + dc;
}

export function money(n?: number): string {
  n = n || 0;
  const ent = Math.floor(n);
  const cent = Math.round((n - ent) * 100);
  let t = enLetras(ent) + " PESOS";
  if (cent > 0) t += " CON " + enLetras(cent) + " CENTAVOS";
  return t + " MONEDA LEGAL COLOMBIANA ($" + pts(n) + ")";
}

export function diaTexto(d: number): string {
  let w = enLetras(d).toLowerCase();
  if (w === "uno") w = "un";
  else if (w.slice(-9) === "veintiuno") w = w.slice(0, -9) + "veintiún";
  else if (w.slice(-4) === " uno") w = w.slice(0, -4) + " un";
  return w;
}

export function fechaText(v?: string): string {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(v || "");
  if (!m) return v || "____";
  const y = +m[1];
  const mo = +m[2];
  const d = +m[3];
  if (mo < 1 || mo > 12 || d < 1 || d > 31) return v || "____";
  return diaTexto(d) + " (" + d + ") " + (d === 1 ? "día" : "días") + " del mes de " + MESES[mo - 1] + " del año " + enLetras(y).toLowerCase() + " (" + y + ")";
}

export function fechaCorta(v?: string): string {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(v || "");
  if (!m) return v || "____";
  return +m[3] + " de " + MESES[+m[2] - 1] + " de " + m[1];
}

export function esc(s: unknown): string {
  return (s == null ? "" : "" + s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

export function attr(s: unknown): string {
  return (s == null ? "" : "" + s).replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;");
}

function fmt(n: number): string {
  return "$" + pts(n);
}

export function I(s: string): string {
  return '<span class="ins">' + esc(s) + "</span>";
}

export function IF(id: string, s: unknown): string {
  return '<span class="ins" data-f="' + id + '">' + esc(s) + "</span>";
}

export function R(s: string, cite: string): string {
  return '<span class="rulec">' + s + '</span><span class="cite">' + cite + "</span>";
}

export function D(cite: string): string {
  return '<span class="cite">' + cite + "</span>";
}

export function genEnding(g: GeneroCode): "o" | "a" | "e" {
  return g === "F" ? "a" : g === "NB" || g === "T" ? "e" : "o";
}

export function genArt(g: GeneroCode): "el" | "la" | "le" {
  return g === "F" ? "la" : g === "NB" || g === "T" ? "le" : "el";
}

export function labelEstado(e: EstadoCivil, genero: GeneroCode): string {
  const x = genEnding(genero);
  return {
    soltero: "solter" + x,
    casado_sc: "casad" + x + " con sociedad conyugal vigente",
    union: "en unión marital de hecho",
    divorciado: "divorciad" + x,
    viudo: "viud" + x,
  }[e] || e;
}

function docLabel(c: TipoDoc): string {
  return TIPODOC[c] || "C.C.";
}

function docFrase(c: TipoDoc): string {
  return DOCFRASE[c] || DOCFRASE.CC || "la cédula de ciudadanía";
}

export function casadoOUnion(list: Party[]): boolean {
  return list.some((p) => p.tipo !== "juridica" && (p.estado === "casado_sc" || p.estado === "union"));
}

export function anyNatural(list: Party[]): boolean {
  return list.some((p) => p.tipo !== "juridica");
}

export function anyJuridica(s: CompraventaState): boolean {
  return s.V.concat(s.C).some((p) => p.tipo === "juridica");
}

export function sumaCuotas(list: Party[]): number {
  return list.reduce((a, p) => a + (p.cuota || 0), 0);
}

export function pers(p: Party, side: "v" | "c", i: number): string {
  const f = side + i;
  const gn = genEnding(p.genero);
  const dom = p.ciudad ? ", domiciliad" + (p.tipo === "juridica" ? "a" : gn) + " en " + IF(f + "ciudad", p.ciudad) : "";
  if (p.tipo === "juridica") {
    return IF(f + "nombre", p.nombre) + ", persona jurídica identificada con NIT " + IF(f + "id", p.id) + dom + ", representada legalmente por " + IF(f + "repr", p.repr) + ", quien acredita su existencia y representación con el certificado que se protocoliza con este instrumento";
  }
  return IF(f + "nombre", p.nombre) + ", mayor de edad" + dom + ", identificad" + gn + " con " + IF(f + "tipoDoc", docFrase(p.tipoDoc)) + " número " + IF(f + "id", p.id) + ", de estado civil " + IF(f + "estado", labelEstado(p.estado, p.genero));
}

export function persList(list: Party[], side: "v" | "c"): string {
  return list.map((p, i) => pers(p, side, i)).join("; y ");
}

export function buyersFavor(C: Party[]): string {
  if (C.length === 1) return IF("c0nombre", C[0].nombre);
  const eq = C.every((p) => p.cuota === C[0].cuota);
  const names = C.map((p, i) => IF("c" + i + "nombre", p.nombre) + (eq ? "" : " (en un " + IF("c" + i + "cuota", p.cuota + "%") + ")")).join(" y ");
  return names + (eq ? ", en común y proindiviso y por partes iguales," : ", en común y proindiviso en las proporciones indicadas,");
}

const defaultParties = {
  vendedores: [
    { tipo: "natural", genero: "M", tipoDoc: "CC", nombre: "RODRIGO ELÍAS CASTAÑO MEJÍA", id: "71.555.201", ciudad: "Medellín", estado: "casado_sc", repr: "", cuota: 50, direccion: "Calle 10 Sur # 22-14", telefono: "315 6620114", correo: "rcastano@correo.com", ocupacion: "Comerciante", notiElec: true, pep: false },
    { tipo: "natural", genero: "F", tipoDoc: "CC", nombre: "MARTA LUCÍA ARANGO POSADA", id: "43.220.118", ciudad: "Medellín", estado: "casado_sc", repr: "", cuota: 50, direccion: "Calle 10 Sur # 22-14", telefono: "315 6620115", correo: "marango@correo.com", ocupacion: "Docente", notiElec: true, pep: false },
  ] satisfies Party[],
  compradores: [
    { tipo: "natural", genero: "F", tipoDoc: "CC", nombre: "LAURA XIMENA ORTIZ VÉLEZ", id: "1.017.884.330", ciudad: "Envigado", estado: "soltero", repr: "", cuota: 100, direccion: "Cra 43A # 30 Sur-90", telefono: "304 5512090", correo: "lortiz@correo.com", ocupacion: "Ingeniera", notiElec: true, pep: false },
  ] satisfies Party[],
  testigos: [
    { tipoDoc: "CC", nombre: "SEBASTIÁN RÍOS MEJÍA", id: "1.036.640.220", ciudad: "Medellín", direccion: "", telefono: "", correo: "", ocupacion: "" },
    { tipoDoc: "CC", nombre: "VALENTINA GÓMEZ LOAIZA", id: "1.128.445.117", ciudad: "Medellín", direccion: "", telefono: "", correo: "", ocupacion: "" },
  ] satisfies AuxParty[],
  ruego: { tipoDoc: "CC", nombre: "GLORIA PATRICIA MEJÍA RÚA", id: "32.556.101", ciudad: "Medellín", direccion: "", telefono: "", correo: "", ocupacion: "" } satisfies AuxParty,
};

function cloneCompraventaDefault(credito: boolean): CompraventaState {
  const V = defaultParties.vendedores.map((p) => ({ ...p }));
  const C = defaultParties.compradores.map((p) => ({ ...p }));
  return {
    derecho: "dominio",
    credito,
    banco: "BANCO DAVIVIENDA S.A.",
    bancoNit: "860.034.313-7",
    plazoAnios: 20,
    numCuotas: 240,
    apoderadoBanco: "CLAUDIA HELENA MAZO ARBOLEDA",
    poderBancoEP: "1.245 del 12-02-2024",
    poderBancoNot: "Notaría 20 de Medellín",
    avaluoCatastral: 121923000,
    nupre: "AAB0071ONED",
    apod: false,
    apodN: "CARLOS MARIO GÓMEZ RÚA",
    apodP: "E.P. 812 del 2 de julio de 2026, Notaría 8 de Medellín",
    afect: "no",
    inmdesc: "APARTAMENTO NRO. 1402 de la Torre 3 del Conjunto Residencial Miravalle — Propiedad Horizontal, situado en la Calle 30 Sur #27-45 del municipio de Envigado (Antioquia), destinado a vivienda, con un área privada aproximada de 68,40 m²",
    linderos: "Su área y linderos están determinados por el perímetro comprendido entre los puntos 1 al 28 y 1, punto de partida, de la planta del piso 14 de la Torre 3, plano RPH-19",
    matricula: "001-1502334",
    catastral: "05266010300030014020",
    ph: true,
    phReg: "E.P. 1.982 del 3 de mayo de 2019, Notaría 12 de Medellín",
    vis: "no",
    tituloNum: "2.410",
    tituloFecha: "2019-06-18",
    tituloNotaria: "Notaría 12 de Medellín",
    gravamen: "libre",
    tipoNegocio: "compraventa",
    tituloTipo: "compraventa",
    subsidio: false,
    subsidioEnt: "Caja de Compensación COMFAMA",
    posesion2: true,
    firmaRuego: false,
    interprete: false,
    pep: false,
    cuentaTercero: false,
    pep_indagado: false,
    rupta_verificado: false,
    numEscritura: "2.847",
    fechaOtorg: "2026-08-14",
    huella: true,
    testigosOn: false,
    hojaInicial: "Aa-112942941",
    pepAny: false,
    testigos: defaultParties.testigos.map((p) => ({ ...p })),
    ruego: { ...defaultParties.ruego },
    total: 420000000,
    inicial: 120000000,
    saldo: 300000000,
    ax: { tradicion: false, predial: true, admin: false, cedulas: true },
    V,
    C,
  };
}

const defaultCancelacion: CancelacionState = {
  cNum: "1.206",
  cFechaOtorg: "2026-03-06",
  cNotario: "JULIANA OLIVA ZULUAGA ARISMENDY",
  cNotarioGenero: "F",
  cCalidad: "Interina",
  cActoAdmin: "Decreto Nro. 1419 del 29 de Julio de 2022",
  cBanco: "BANCOLOMBIA S.A.",
  cBancoNit: "890.903.938-8",
  cBancoDom: "Medellín",
  cRepTipo: "apoderado",
  cRepCargo: "Apoderada Especial",
  cApoNombre: "PAULINA ANDREA BELTRÁN AGUDELO",
  cApoGenero: "F",
  cApoCC: "43.993.129",
  cPoderEP: "2.604",
  cPoderFecha: "26 de Septiembre de 2018",
  cPoderNotaria: "Notaría Veintinueve (29) del Círculo Notarial de Medellín",
  cDeudor: "ANGÉLICA MARÍA ROMÁN RUIZ",
  cHipEP: "1.858",
  cHipFecha: "18 de Mayo de 2017",
  cHipNotaria: "Notaría Sexta (6ª) de Medellín",
  cHipRegFecha: "11 de Julio de 2017",
  cOrip: "Medellín - Zona Norte",
  cHipMonto: 69714000,
  cInmdesc: "APARTAMENTO NRO. 106 — ETAPA 2 — TORRE 1 — CERRO AZUL CONJUNTO RESIDENCIAL — PROPIEDAD HORIZONTAL — Avenida 31 Nro. 66-29 del municipio de Bello (Antioquia)",
  cMatricula: "01N-5428500",
  cCatastral: "050880100080500170014903010024",
  cNupre: "AAX0018YUHA",
  cHojas: "Aa-118420033",
  cRecaudo: 19300,
  cCorreoNotif: "escriturasrelusuario@gmail.com",
  cSinCuantia: true,
  cNoPazSalvo: false,
  cSarlaft: true,
  cNotiElec: true,
};

export const defaults: Record<ActoCode, CaseState> = {
  compraventa: cloneCompraventaDefault(false),
  hipoteca: cloneCompraventaDefault(true),
  cancelacion: { ...defaultCancelacion },
};

// Parte y auxiliar en blanco: un caso NUEVO nace vacío para diligenciarlo
// desde el formulario (no con los datos de ejemplo del motor).
function emptyParty(): Party {
  return {
    tipo: "natural", genero: "M", tipoDoc: "CC", nombre: "", id: "", ciudad: "",
    estado: "soltero", repr: "", cuota: 100, direccion: "", telefono: "", correo: "",
    ocupacion: "", notiElec: false, pep: false,
  };
}
function emptyAux(): AuxParty {
  return { tipoDoc: "CC", nombre: "", id: "", ciudad: "", direccion: "", telefono: "", correo: "", ocupacion: "" };
}

function blankCompraventa(credito: boolean): CompraventaState {
  return {
    ...cloneCompraventaDefault(credito),
    banco: "", bancoNit: "", plazoAnios: 0, numCuotas: 0, apoderadoBanco: "",
    poderBancoEP: "", poderBancoNot: "", avaluoCatastral: 0, nupre: "",
    apod: false, apodN: "", apodP: "",
    afect: "no", inmdesc: "", linderos: "", matricula: "", catastral: "",
    ph: false, phReg: "", vis: "no", tituloNum: "", tituloFecha: "", tituloNotaria: "",
    gravamen: "libre", tipoNegocio: "compraventa", tituloTipo: "compraventa",
    subsidio: false, subsidioEnt: "", posesion2: false, firmaRuego: false, interprete: false,
    pep: false, cuentaTercero: false, pep_indagado: false, rupta_verificado: false,
    numEscritura: "", fechaOtorg: "", huella: false, testigosOn: false, hojaInicial: "", pepAny: false,
    testigos: [emptyAux()], ruego: emptyAux(),
    total: 0, inicial: 0, saldo: 0,
    ax: { tradicion: false, predial: false, admin: false, cedulas: false },
    V: [emptyParty()], C: [emptyParty()],
  };
}

const blankCancelacion: CancelacionState = {
  ...defaultCancelacion,
  cNum: "", cFechaOtorg: "", cNotario: "", cCalidad: "", cActoAdmin: "",
  cBanco: "", cBancoNit: "", cBancoDom: "", cRepCargo: "", cApoNombre: "", cApoCC: "",
  cPoderEP: "", cPoderFecha: "", cPoderNotaria: "", cDeudor: "", cHipEP: "", cHipFecha: "",
  cHipNotaria: "", cHipRegFecha: "", cOrip: "", cHipMonto: 0, cInmdesc: "", cMatricula: "",
  cCatastral: "", cNupre: "", cHojas: "", cRecaudo: 0, cCorreoNotif: "",
};

// Estado inicial vacío para casos nuevos (el de `defaults` es el ejemplo demo).
export const emptyDefaults: Record<ActoCode, CaseState> = {
  compraventa: blankCompraventa(false),
  hipoteca: blankCompraventa(true),
  cancelacion: { ...blankCancelacion },
};

function legacyInmueble(s: CompraventaState): CompraventaInmueble {
  return {
    descripcion: s.inmdesc,
    linderos: s.linderos,
    matricula: s.matricula,
    catastral: s.catastral,
    nupre: s.nupre,
    avaluoCatastral: s.avaluoCatastral,
  };
}

export function inmueblesCompraventa(s: CompraventaState): CompraventaInmueble[] {
  const list = Array.isArray(s.inmuebles) ? s.inmuebles.filter(Boolean) : [];
  return list.length ? list.map((inmueble) => ({
    descripcion: inmueble.descripcion || "",
    linderos: inmueble.linderos || "",
    matricula: inmueble.matricula || "",
    catastral: inmueble.catastral || "",
    nupre: inmueble.nupre || "",
    avaluoCatastral: Number.isFinite(inmueble.avaluoCatastral) ? inmueble.avaluoCatastral : 0,
  })) : [legacyInmueble(s)];
}

function usaInmueblesExplicitos(s: CompraventaState): boolean {
  return Array.isArray(s.inmuebles) && s.inmuebles.length > 0;
}

function inmuebleField(s: CompraventaState, index: number, key: keyof CompraventaInmueble): string {
  if (!usaInmueblesExplicitos(s) && index === 0) {
    if (key === "descripcion") return "inmdesc";
    if (key === "avaluoCatastral") return "avaluoCatastral";
    return key;
  }
  return "inmuebles." + index + "." + key;
}

function descripcionInmueble(s: CompraventaState, inmueble: CompraventaInmueble, index: number): string {
  return IF(inmuebleField(s, index, "descripcion"), inmueble.descripcion)
    + ". FOLIO DE MATRÍCULA INMOBILIARIA NRO. " + IF(inmuebleField(s, index, "matricula"), inmueble.matricula || "________")
    + ". CÉDULA CATASTRAL: " + IF(inmuebleField(s, index, "catastral"), inmueble.catastral || "________")
    + ". NUPRE: " + IF(inmuebleField(s, index, "nupre"), inmueble.nupre || "________")
    + ". Cuyos linderos generales son: " + IF(inmuebleField(s, index, "linderos"), inmueble.linderos);
}

function folioEstadosActivos(s: CompraventaState): boolean {
  return Boolean(s.folioEstado && s.folioEstado !== "matriz");
}

function folioEstadoLabel(estado: FolioEstado): string {
  const labels: Record<FolioEstado, string> = {
    matriz: "Matriz",
    segregado: "Segregado",
    englobe: "Englobe",
    desenglobe: "Desenglobe",
    mayor_extension: "Mayor extensión",
    falsa_tradicion: "Falsa tradición",
  };
  return labels[estado];
}

function folioEstadoCita(estado: FolioEstado): string {
  return estado === "falsa_tradicion" ? "Ley 1561/2012" : "Ley 1579/2012";
}

function folioEstadoTexto(estado: FolioEstado): string {
  const textos: Record<FolioEstado, string> = {
    matriz: "",
    segregado: "El folio corresponde a un inmueble segregado; las partes declaran que la segregación y su antecedente registral fueron revisados en el certificado de tradición y libertad.",
    englobe: "El folio refleja un englobe; las partes declaran que el nuevo folio integra los predios de origen y que se verificó la continuidad del tracto registral.",
    desenglobe: "El folio proviene de un desenglobe; las partes declaran que el predio transferido quedó individualizado con matrícula, cabida y linderos propios.",
    mayor_extension: "El inmueble se desprende de uno de mayor extensión; se advierte que deben coincidir el antecedente, el área remanente y la individualización registral del predio objeto de transferencia.",
    falsa_tradicion: "El folio registra antecedente de falsa tradición; se advierte que esta escritura no sanea por sí sola el dominio y que debe verificarse el trámite de saneamiento aplicable antes del registro.",
  };
  return textos[estado];
}

function encadenamientosActivos(s: CompraventaState): EncadenamientosCompraventa {
  return s.encadenamientos || {};
}

function anyEncadenamiento(s: CompraventaState): boolean {
  const enc = encadenamientosActivos(s);
  return Boolean(enc.cancelacionHipotecaPrevia || enc.cancelacionPatrimonioFamilia || enc.afectacionViviendaFamiliar);
}

function renderEncadenamientos(s: CompraventaState, compradorLabel: string): string {
  const enc = encadenamientosActivos(s);
  let h = "";
  if (enc.cancelacionHipotecaPrevia) {
    const hip = enc.hipotecaPrevia || {};
    h += '<div class="sech" data-sec="enc-cancelacion-hipoteca" style="text-align:center;font-weight:700;font-family:var(--sans);font-size:12px;letter-spacing:.06em;margin:22px 0 14px;padding:6px 0;border-top:1px solid var(--line-strong);border-bottom:1px solid var(--line-strong);color:var(--accent)">ACTO PREVIO: CANCELACIÓN DE HIPOTECA</div>';
    h += '<p class="cl"><span class="clh">PRIMERO: CANCELACIÓN DE HIPOTECA PREVIA.</span> ' + R("Comparece el acreedor hipotecario " + IF("encadenamientos.hipotecaPrevia.acreedor", hip.acreedor || "________") + (hip.nit ? ", identificado con NIT " + IF("encadenamientos.hipotecaPrevia.nit", hip.nit) : "") + ", y manifiesta que cancela en su totalidad la hipoteca constituida mediante Escritura Pública número " + IF("encadenamientos.hipotecaPrevia.escritura", hip.escritura || "________") + " del " + IF("encadenamientos.hipotecaPrevia.fecha", hip.fecha ? fechaCorta(hip.fecha) : "________") + " de la " + IF("encadenamientos.hipotecaPrevia.notaria", hip.notaria || "________") + ", registrada el " + IF("encadenamientos.hipotecaPrevia.registroFecha", hip.registroFecha || "________") + " en la Oficina de Registro de Instrumentos Públicos de " + IF("encadenamientos.hipotecaPrevia.orip", hip.orip || "________") + ".", "art. 2457 C.C. · Ley 1579/2012") + '<span class="fill"></span></p>';
  }
  if (enc.cancelacionPatrimonioFamilia) {
    const pat = enc.patrimonioFamilia || {};
    h += '<div class="sech" data-sec="enc-cancelacion-patrimonio" style="text-align:center;font-weight:700;font-family:var(--sans);font-size:12px;letter-spacing:.06em;margin:22px 0 14px;padding:6px 0;border-top:1px solid var(--line-strong);border-bottom:1px solid var(--line-strong);color:var(--accent)">ACTO PREVIO: CANCELACIÓN DE PATRIMONIO DE FAMILIA</div>';
    h += '<p class="cl"><span class="clh">PRIMERO: CANCELACIÓN DE PATRIMONIO DE FAMILIA.</span> ' + R("Los interesados manifiestan que cancelan el patrimonio de familia constituido mediante Escritura Pública número " + IF("encadenamientos.patrimonioFamilia.escritura", pat.escritura || "________") + " del " + IF("encadenamientos.patrimonioFamilia.fecha", pat.fecha ? fechaCorta(pat.fecha) : "________") + " de la " + IF("encadenamientos.patrimonioFamilia.notaria", pat.notaria || "________") + (pat.beneficiarios ? ", respecto de " + IF("encadenamientos.patrimonioFamilia.beneficiarios", pat.beneficiarios) : "") + ", para que el inmueble pueda transferirse libre de dicha limitación.", "Ley 70/1931 · Ley 495/1999") + '<span class="fill"></span></p>';
  }
  if (enc.afectacionViviendaFamiliar) {
    const afect = enc.afectacion || {};
    h += '<div class="sech" data-sec="enc-afectacion-vivienda" style="text-align:center;font-weight:700;font-family:var(--sans);font-size:12px;letter-spacing:.06em;margin:22px 0 14px;padding:6px 0;border-top:1px solid var(--line-strong);border-bottom:1px solid var(--line-strong);color:var(--accent)">ACTO POSTERIOR: AFECTACIÓN A VIVIENDA FAMILIAR</div>';
    h += '<p class="cl"><span class="clh">PRIMERO: AFECTACIÓN A VIVIENDA FAMILIAR.</span> ' + R("Compareciendo nuevamente " + compradorLabel + ", manifiesta que el inmueble adquirido por este instrumento queda afectado a vivienda familiar en favor de su núcleo familiar" + (afect.beneficiarios ? ", integrado por " + IF("encadenamientos.afectacion.beneficiarios", afect.beneficiarios) : "") + ".", "art. 6 · Ley 258/1996") + '<span class="fill"></span></p>';
  }
  return h;
}

function divisasActivas(s: CompraventaState): CompraventaDivisas {
  return s.divisas || {};
}

function ruralActiva(s: CompraventaState): CompraventaRural {
  return s.rural || {};
}

function capacidadActiva(s: CompraventaState): CompraventaCapacidad {
  return s.capacidad || {};
}

function formatHectareas(value: number | undefined): string {
  return typeof value === "number" && Number.isFinite(value) && value > 0 ? String(value).replace(".", ",") + " hectáreas" : "________ hectáreas";
}

function partesExtranjeras(s: CompraventaState): string {
  const naturales = s.V.concat(s.C).filter((party) => party.tipo === "natural" && ["CE", "PA", "PPT"].includes(party.tipoDoc));
  if (!naturales.length) return "la parte extranjera o no residente";
  return naturales.map((party) => esc(party.nombre || "________")).join("; ");
}

function renderSituacionesEspeciales(s: CompraventaState): string {
  const divisas = divisasActivas(s);
  const rural = ruralActiva(s);
  const capacidad = capacidadActiva(s);
  let h = "";

  if (divisas.parteExtranjeraNoResidente || divisas.pagoDivisas) {
    const declaracion = divisas.declaracionCambio ? " identificada como " + IF("divisas.declaracionCambio", divisas.declaracionCambio) : "";
    const monedaValor = divisas.valorDivisas ? " por " + IF("divisas.moneda", divisas.moneda || "USD") + " " + IF("divisas.valorDivisas", fmtMoneyStr(String(divisas.valorDivisas))) : "";
    const origen = divisas.paisOrigenFondos ? ", con origen declarado en " + IF("divisas.paisOrigenFondos", divisas.paisOrigenFondos) : "";
    const identidad = divisas.parteExtranjeraNoResidente ? "Cuando interviene " + partesExtranjeras(s) + ", se deja constancia de la identificación con pasaporte, cédula de extranjería o PPT según corresponda; si el poder proviene del exterior, deberá protocolizarse apostillado o legalizado y traducido cuando aplique. " : "";
    const pago = divisas.pagoDivisas ? "Si el precio se paga en divisas" + monedaValor + origen + ", las partes declaran que la operación se canaliza por el mercado cambiario mediante la declaración de cambio" + declaracion + " y que se realizará el registro de inversión extranjera ante el Banco de la República cuando proceda." : "";
    h += '<p class="para" data-sec="divisas"><span class="clh">Parágrafo — Extranjería, no residencia y régimen cambiario.</span> '
      + R((identidad + pago).trim(), "Ley 9/1991 · Dcto 1068/2015 · Circular DCIN Banrep")
      + "</p>";
  }

  if (rural.predioRural || rural.baldioAdjudicado || rural.superaUaf || rural.derechoPreferencia) {
    const area = formatHectareas(rural.areaHectareas);
    const uaf = formatHectareas(rural.uafHectareas);
    const region = rural.municipioRegionUaf ? " para " + IF("rural.municipioRegionUaf", rural.municipioRegionUaf) : "";
    h += '<p class="para" data-sec="rural-uaf"><span class="clh">Parágrafo — Predio rural, UAF y baldíos.</span> '
      + R("Las partes declaran que el inmueble se identifica como predio rural no sometido a propiedad horizontal, con cabida aproximada de " + area + " y Unidad Agrícola Familiar de referencia de " + uaf + region + ". Si el predio proviene de baldío adjudicado o supera la UAF, deberá verificarse la restricción de enajenación, acumulación, autorización de la Agencia Nacional de Tierras y eventual derecho de preferencia antes del otorgamiento o registro.", "arts. 39 y 72 · Ley 160/1994")
      + "</p>";
  }

  if (capacidad.menorVendedor || capacidad.ventaBienMenor || capacidad.discapacidadConApoyos) {
    const autorizacion = capacidad.autorizacionDetalle ? " Se protocoliza " + IF("capacidad.autorizacionDetalle", capacidad.autorizacionDetalle) + "." : " La autorización judicial o notarial vigente deberá protocolizarse si el bien pertenece a una persona menor de edad.";
    const apoyo = capacidad.apoyoNombre ? " La persona de apoyo " + IF("capacidad.apoyoNombre", capacidad.apoyoNombre) + (capacidad.apoyoDocumento ? ", identificada con " + IF("capacidad.apoyoDocumento", capacidad.apoyoDocumento) : "") + ", asiste en la comunicación y comprensión del acto sin sustituir la voluntad de la persona titular." : " La persona de apoyo, cuando sea usada, asiste en la comunicación y comprensión del acto sin sustituir la voluntad de la persona titular.";
    h += '<p class="para" data-sec="capacidad-apoyos"><span class="clh">Parágrafo — Capacidad, representación y apoyos.</span> '
      + R("Cuando se vende un bien de persona menor de edad, comparece su representante legal en los términos autorizados y se deja constancia de la autorización aplicable." + autorizacion + " La persona con discapacidad conserva capacidad legal plena; si utiliza apoyos, deben acreditarse mediante acuerdo o adjudicación de apoyos vigente." + apoyo, "Ley 1996/2019 arts. 6, 15 y 16 · Dcto 1429/2020")
      + "</p>";
  }

  return h;
}

export function renderEscritura(s: CompraventaState, tarifas: TarifaConfig = TARIFAS): string {
  const V = s.V;
  const C = s.C;
  const vpl = V.length > 1;
  const VEND = vpl ? "LOS VENDEDORES" : "EL VENDEDOR";
  const vend = vpl ? "los vendedores" : "el vendedor";
  const tf = vpl ? "n" : "";
  const adq = vpl ? "eron" : "ó";
  const cpl = C.length > 1;
  const COMPRA = cpl ? "LOS COMPRADORES" : "LA PARTE COMPRADORA";
  const cManif = cpl ? "manifestaron" : "manifestó";
  const cAcept = cpl ? "aceptan" : "acepta";
  const cAdq = cpl ? "adquieren" : "adquiere";
  const HIP = cpl ? "LOS HIPOTECANTES" : "LA HIPOTECANTE";
  const hN = cpl ? "n" : "";
  const natBuyer = anyNatural(C);
  const inmuebles = inmueblesCompraventa(s);
  const multiInmuebles = usaInmueblesExplicitos(s) && inmuebles.length > 1;
  const firstInmueble = inmuebles[0] || legacyInmueble(s);
  const mat = firstInmueble.matricula || "________";
  const folios = inmuebles.map((inmueble, index) => IF(inmuebleField(s, index, "matricula"), inmueble.matricula || "________")).join(", ");
  const catastrales = inmuebles.map((inmueble, index) => IF(inmuebleField(s, index, "catastral"), inmueble.catastral || "—")).join(", ");
  const ubicacion = multiInmuebles ? inmuebles.map((inmueble, index) => IF(inmuebleField(s, index, "descripcion"), inmueble.descripcion.slice(0, 55) + (inmueble.descripcion.length > 55 ? "…" : ""))).join(" · ") : s.inmdesc.slice(0, 80) + (s.inmdesc.length > 80 ? "…" : "");
  const NEG: Record<CompraventaState["tipoNegocio"], string> = { compraventa: "compraventa", permuta: "permuta", dacion: "dación en pago", retroventa: "compraventa con pacto de retroventa", reserva: "compraventa con reserva de dominio" };
  const negTit = NEG[s.tipoNegocio] || "compraventa";
  const negCod = ({ compraventa: "0125 — COMPRAVENTA", permuta: "0126 — PERMUTA", dacion: "0157 — DACIÓN EN PAGO", retroventa: "0125 — COMPRAVENTA (RETROVENTA)", reserva: "0125 — COMPRAVENTA (RESERVA DE DOMINIO)" } as Record<CompraventaState["tipoNegocio"], string>)[s.tipoNegocio] || "0125 — COMPRAVENTA";
  const TMODO: Record<CompraventaState["tituloTipo"], string> = { compraventa: "compraventa mediante ", sucesion: "adjudicación en la sucesión de su causante, según ", donacion: "donación, según ", remate: "adjudicación en remate, según ", prescripcion: "sentencia de pertenencia (prescripción adquisitiva), según " };
  const tmodo = TMODO[s.tituloTipo] || "";
  let h = "";

  h += '<div class="calif"><h4>Superintendencia de Notariado y Registro · Formato de Calificación</h4><div class="r">'
    + '<span class="k">' + (multiInmuebles ? "Folios matrícula" : "Folio matrícula") + "</span><span>" + (multiInmuebles ? folios : IF("matricula", s.matricula || "—")) + "</span>"
    + '<span class="k">Cód. catastral</span><span>' + (multiInmuebles ? catastrales : IF("catastral", s.catastral || "—")) + "</span>"
    + '<span class="k">Ubicación</span><span>' + (multiInmuebles ? ubicacion : IF("inmdesc", ubicacion)) + "</span></div>"
    + '<table><tr><td>CÓD. ' + negCod + (({ nuda: " (NUDA PROPIEDAD)", usufructo: " (USUFRUCTO)", cuota: " (DERECHOS Y ACCIONES)", uso: " (USO Y HABITACIÓN)" } as Partial<Record<CompraventaState["derecho"], string>>)[s.derecho] || "") + "</td><td>" + IF("total", "$" + pts(s.total)) + "</td></tr>"
    + (s.credito ? '<tr><td>CÓD. 0219 — HIPOTECA ABIERTA SIN LÍMITE</td><td>' + IF("saldo", "$" + pts(s.saldo)) + "</td></tr>" : "") + "</table></div>";

  h += '<p class="cl" data-sec="comparecencia">En la ciudad de Medellín, Departamento de Antioquia, República de Colombia, a los ' + IF("fechaOtorg", fechaText(s.fechaOtorg)) + ", ante el Notario Dieciséis del Círculo Notarial de Medellín, ";
  if (s.apod) {
    h += "compareció " + IF("apodNombre", s.apodN) + ", mayor de edad, quien obra en nombre y representación de " + persList(V, "v") + ", en virtud del poder conferido por " + IF("apodPoder", s.apodP) + ", que se protocoliza " + D("Dcto 1069/2015") + ", y en adelante la parte representada se denominará " + VEND + ", y por su conducto manifest" + adq + ":";
  } else {
    h += "se presentó" + (vpl ? "ron" : "") + " " + persList(V, "v") + "; quien" + (vpl ? "es" : "") + " obra" + tf + " en su propio nombre, y en el texto de este instrumento se llamará" + tf + " " + VEND + ", y manifest" + adq + ":";
  }
  h += '<span class="fill"></span></p>';

  const DER: Record<CompraventaState["derecho"], string> = { dominio: "el derecho de dominio y la posesión", nuda: "la nuda propiedad, reservándose el usufructo vitalicio,", usufructo: "el derecho de usufructo", cuota: "los derechos y acciones (cuota proindiviso) que le corresponden", uso: "el derecho de uso y habitación" };
  const derechoTxt = DER[s.derecho] || DER.dominio;
  if (multiInmuebles) {
    h += '<p class="cl" data-sec="objeto"><span class="clh">PRIMERO: OBJETO DEL NEGOCIO Y DESCRIPCIÓN DE LOS BIENES INMUEBLES.</span> Por medio del presente instrumento transfiere' + tf + " a título de " + negTit + " en favor de " + buyersFavor(C) + " " + derechoTxt + " sobre los siguientes bienes inmuebles: " + inmuebles.map((inmueble, index) => (index + 1) + ") " + descripcionInmueble(s, inmueble, index)).join("; ") + '.<span class="fill"></span></p>';
    h += '<p class="para"><span class="clh">Parágrafo primero.</span> No obstante la mención de la cabida, área y linderos, los inmuebles se transfieren como cuerpos ciertos.</p>';
  } else {
    h += '<p class="cl" data-sec="objeto"><span class="clh">PRIMERO: OBJETO DEL NEGOCIO Y DESCRIPCIÓN DEL BIEN INMUEBLE.</span> Por medio del presente instrumento transfiere' + tf + " a título de " + negTit + " en favor de " + buyersFavor(C) + " " + derechoTxt + " sobre el siguiente bien inmueble: " + IF("inmdesc", s.inmdesc) + ". FOLIO DE MATRÍCULA INMOBILIARIA NRO. " + IF("matricula", mat) + ". Cuyos linderos generales son: " + IF("linderos", s.linderos) + '.<span class="fill"></span></p>';
    h += '<p class="para"><span class="clh">Parágrafo primero.</span> No obstante la mención de la cabida, área y linderos, el inmueble se transfiere como cuerpo cierto.</p>';
  }
  if (s.ph) {
    h += '<p class="para" data-sec="ph"><span class="clh">Parágrafo segundo — Régimen de propiedad horizontal.</span> ' + R("El inmueble hace parte integrante del conjunto sometido al régimen de propiedad horizontal, cuyo reglamento fue elevado a " + IF("phReg", s.phReg) + ", debidamente inscrito en el respectivo folio de matrícula.", "Ley 675/2001") + "</p>";
    h += '<p class="para"><span class="clh">Parágrafo tercero.</span> ' + R("La transferencia comprende además el derecho de copropiedad en el coeficiente señalado para el inmueble en el respectivo reglamento.", "arts. 25–26 · Ley 675/2001") + "</p>";
  }
  if (folioEstadosActivos(s)) {
    const estado = s.folioEstado as FolioEstado;
    h += '<p class="para" data-sec="estado-folio"><span class="clh">Parágrafo — Estado del folio: ' + esc(folioEstadoLabel(estado)) + ".</span> " + R(folioEstadoTexto(estado), folioEstadoCita(estado)) + "</p>";
  }

  h += '<p class="cl" data-sec="titulo"><span class="clh">SEGUNDO: TÍTULO DE ADQUISICIÓN.</span> Que ' + vend + " adquiri" + (vpl ? "eron" : "ó") + (multiInmuebles ? " los inmuebles por " : " el inmueble por ") + tmodo + "la Escritura Pública número " + IF("tituloNum", s.tituloNum) + " del " + IF("tituloFecha", fechaCorta(s.tituloFecha)) + " de la " + IF("tituloNotaria", s.tituloNotaria) + (multiInmuebles ? ", registrada bajo los folios de matrícula inmobiliaria números " + folios : ", registrada bajo el folio de matrícula inmobiliaria número " + IF("matricula", mat)) + '.<span class="fill"></span></p>';
  if (s.tipoNegocio === "retroventa") h += '<p class="para"><span class="clh">Parágrafo — Pacto de retroventa.</span> ' + R("El vendedor se reserva la facultad de recobrar el inmueble reembolsando el precio, dentro del término máximo de cuatro (4) años; se inscribe para su oponibilidad.", "art. 1939 C.C.") + "</p>";
  if (s.tipoNegocio === "reserva") h += '<p class="para"><span class="clh">Parágrafo — Reserva de dominio.</span> ' + R("El vendedor se reserva el dominio hasta el pago total del precio (nota: en inmuebles su eficacia se asimila a condición resolutoria por incumplimiento).", "art. 1935 C.C.") + "</p>";
  if (s.tipoNegocio === "dacion") h += '<p class="para"><span class="clh">Parágrafo — Dación en pago.</span> La transferencia se hace para extinguir la obligación preexistente que se identifica en este instrumento.</p>';

  h += '<p class="cl" data-sec="saneamiento"><span class="clh">TERCERO: SANEAMIENTO Y LIMITACIONES AL DOMINIO.</span> Garantiza' + tf + " " + vend + (multiInmuebles ? " la absoluta propiedad de los inmuebles, que se encuentran libres" : " la absoluta propiedad del inmueble, que se encuentra libre") + " de gravámenes y limitaciones tales como hipoteca, embargo, demanda civil, condiciones resolutorias, uso o usufructo y medidas cautelares, obligándose al saneamiento por evicción o vicios redhibitorios " + D("arts. 1893, 1914 C.C.") + '.<span class="fill"></span></p>';
  if (s.gravamen === "hipoteca_previa") h += '<p class="para"><span class="clh">Parágrafo primero.</span> En cuanto a hipotecas, ' + (multiInmuebles ? "los inmuebles soportan" : "el inmueble soporta") + " una hipoteca previa constituida por " + vend + (encadenamientosActivos(s).cancelacionHipotecaPrevia ? ", que se cancela en acto previo de este mismo instrumento." : ", que se pagará con parte del crédito y se cancelará con posterioridad al registro.") + "</p>";
  if (s.gravamen === "patrimonio" && encadenamientosActivos(s).cancelacionPatrimonioFamilia) h += '<p class="para"><span class="clh">Parágrafo — Patrimonio de familia.</span> El patrimonio de familia vigente se cancela en acto previo de este mismo instrumento.</p>';
  if (casadoOUnion(V)) {
    const decl = s.afect === "si" ? "que el inmueble SÍ se encuentra afectado a vivienda familiar" : s.afect === "nosabe" ? "que no precisan si el inmueble está afectado a vivienda familiar" : "que el inmueble que ahora enajena" + (vpl ? "n" : "") + " no está afectado a vivienda familiar";
    h += '<p class="para" data-sec="ley258"><span class="clh">Parágrafo — Efectos de la Ley 258 de 1996.</span> ' + R("Advertido" + (vpl ? "s" : "") + " del Artículo 6.º de la Ley 258 de 1996, modificada por la Ley 854 de 2003, e indagado" + (vpl ? "s" : "") + " expresamente, " + vend + " manifest" + adq + " bajo juramento " + decl + ".", "art. 6 · Ley 258/1996") + "</p>";
  }
  if (anyEncadenamiento(s)) h += renderEncadenamientos(s, COMPRA);
  h += renderSituacionesEspeciales(s);

  h += '<p class="cl" data-sec="precio"><span class="clh">CUARTO: PRECIO DE VENTA.</span> El precio de la compraventa lo constituye la suma de ' + IF("total", money(s.total)) + ", que " + COMPRA + ' cancelará así:<span class="fill"></span></p>';
  h += '<p class="para"><span class="clh">a)</span> La suma de ' + IF("inicial", money(s.inicial)) + ", con recursos propios, que " + vend + " declara" + tf + " recibida a satisfacción.</p>";
  if (s.credito) h += '<p class="para"><span class="clh">b)</span> Y el saldo de ' + IF("saldo", money(s.saldo)) + ", que " + COMPRA + " entregará con el producto de un préstamo que tramita ante el " + IF("banco", s.banco) + ", desembolsable al registro de la hipoteca que constituye a su favor; de no aprobarse el crédito, se obliga a cancelar el saldo con recursos propios.</p>";
  if (s.subsidio) h += '<p class="para"><span class="clh">c)</span> ' + R("Parte del precio se cubre con el subsidio familiar de vivienda otorgado por " + esc(s.subsidioEnt) + ", cuyo acto de asignación se protocoliza; se advierte la eventual constitución de patrimonio de familia y las restricciones inherentes al subsidio.", "Ley 3ª/1991") + "</p>";
  h += '<p class="para"><span class="clh">Parágrafo primero — Renuncia a la condición resolutoria.</span> No obstante la forma de pago, la parte vendedora renuncia a la acción resolutoria y otorga el título firme e irresoluble ' + D("art. 1546 C.C.") + ".</p>";
  h += '<p class="para"><span class="clh">Parágrafo segundo — Valor real.</span> ' + R("Las partes declaran bajo la gravedad del juramento que el valor y precio expresado es real, no inferior al costo, y que no existen sumas convenidas por fuera de este instrumento público.", "art. 61 Ley 2010/2019 (art. 90 E.T.)") + "</p>";
  h += '<p class="para"><span class="clh">Parágrafo tercero — Origen de los ingresos.</span> ' + R("La parte compradora declara que los recursos provienen de actividades lícitas y que no figura en listados de prevención de lavado de activos (OFAC u otros).", "Ley 2195/2022 · SIPLAFT") + "</p>";
  if (s.vis === "sfve") h += '<p class="para" data-sec="vis"><span class="clh">Parágrafo cuarto — Vivienda de interés social.</span> ' + R("Se advierte la prohibición de enajenar el inmueble por el término de cinco (5) años y la condición resolutoria a favor de la entidad otorgante del subsidio en caso de revocatoria.", "art. 13 · Ley 2079/2021") + "</p>";

  h += '<p class="cl"><span class="clh">QUINTO: ENTREGA.</span> La entrega real y material se realizará ' + (s.credito ? "al desembolso del crédito" : "a la firma de esta escritura") + ', a satisfacción de la parte compradora, con sus usos y servidumbres.<span class="fill"></span></p>';
  h += '<p class="cl"><span class="clh">SEXTO: GASTOS.</span> Los gastos notariales e impuesto de registro se cubren por partes iguales ' + D("art. 230 Ley 223/1995") + "; la retención en la fuente del 1%, recaudada por el Notario, es de cargo de " + vend + " " + D("art. 398 E.T.") + '.<span class="fill"></span></p>';

  h += '<p class="cl" data-sec="aceptacion">Presente ' + COMPRA + ", " + persList(C, "c") + ", obrando en su propio nombre, " + cManif + ':<span class="fill"></span></p>';
  h += '<p class="para"><span class="clh">A)</span> Que ' + cAcept + " la presente escritura y las declaraciones en ella contenidas.</p>";
  h += '<p class="para"><span class="clh">B)</span> Que ' + cAcept + " que la entrega se haga en la forma del numeral quinto.</p>";
  if (s.ph) h += '<p class="para"><span class="clh">C)</span> Que ' + (cpl ? "manifiestan" : "manifiesta") + " conocer y acatar el reglamento de propiedad horizontal al que se somete el inmueble que " + cAdq + ".</p>";
  if (natBuyer) h += '<p class="cl">' + R("EFECTOS DE LA LEY 258 DE 1996: Compareciendo nuevamente " + COMPRA + ", " + cManif + " que el inmueble que " + cAdq + " " + (s.vis === "sfve" ? "SÍ queda afectado a vivienda familiar" : "NO queda afectado a vivienda familiar") + ".", "art. 6 · Ley 258/1996") + '<span class="fill"></span></p>';

  if (s.credito) {
    const hipNames = C.map((p, i) => IF("c" + i + "nombre", p.nombre)).join(" y ");
    h += '<div class="sech" data-sec="hipoteca" style="text-align:center;font-weight:700;font-family:var(--sans);font-size:12px;letter-spacing:.06em;margin:22px 0 14px;padding:6px 0;border-top:1px solid var(--line-strong);border-bottom:1px solid var(--line-strong);color:var(--accent)">HIPOTECA ABIERTA CON CUANTÍA INDETERMINADA</div>';
    const ACR = "EL ACREEDOR";
    const monto = money(s.saldo);
    h += '<p class="cl">Compareci' + (cpl ? "eron" : "ó") + " " + hipNames + ", de las condiciones civiles indicadas, quien" + (cpl ? "es" : "") + " obra" + hN + " en su propio nombre y en adelante se denominará" + hN + " " + HIP + ", y " + (cpl ? "manifestaron" : "manifestó") + ':<span class="fill"></span></p>';
    h += '<p class="cl"><span class="clh">PRIMERO: OBJETO — CONSTITUCIÓN DE HIPOTECA.</span> Que ' + HIP + " constituye" + hN + " HIPOTECA ABIERTA, DE PRIMER GRADO Y SIN LÍMITE DE CUANTÍA a favor del " + IF("banco", s.banco) + ", establecimiento de crédito con domicilio en Medellín, con NIT " + IF("bancoNit", s.bancoNit) + ", quien en adelante se denominará " + ACR + (multiInmuebles ? ", sobre los inmuebles con FOLIOS DE MATRÍCULA INMOBILIARIA NROS. " + folios + ", anteriormente descritos y alinderados, " : ", sobre el inmueble con FOLIO DE MATRÍCULA INMOBILIARIA NRO. " + IF("matricula", mat) + ", anteriormente descrito y alinderado, ") + R("conforme con los artículos 2432 y siguientes del Código Civil.", "arts. 2432 ss · C.C.") + '<span class="fill"></span></p>';
    h += '<p class="para"><span class="clh">Parágrafo.</span> La hipoteca se extiende ' + (multiInmuebles ? "a los inmuebles con todas sus mejoras, anexidades y construcciones presentes o futuras" : "al inmueble con todas sus mejoras, anexidades y construcciones presentes o futuras") + ", frutos pendientes, rentas y cánones, y a las indemnizaciones de seguros y de expropiación " + D("arts. 2445–2446 C.C.") + ".</p>";
    if (cpl) h += '<p class="cl"><span class="clh">SEGUNDO: SOLIDARIDAD.</span> ' + HIP + ", en su condición de constituyentes del gravamen, se obligan solidariamente frente a " + ACR + ' respecto de la totalidad de las obligaciones garantizadas.<span class="fill"></span></p>';
    const nT = cpl ? "TERCERO" : "SEGUNDO";
    const nO = cpl ? "CUARTO" : "TERCERO";
    const nV = cpl ? "QUINTO" : "CUARTO";
    const nSx = cpl ? "SEXTO" : "QUINTO";
    const nSp = cpl ? "SÉPTIMO" : "SEXTO";
    const nOc = cpl ? "OCTAVO" : "SÉPTIMO";
    const nNv = cpl ? "NOVENO" : "OCTAVO";
    const nDx = cpl ? "DÉCIMO" : "NOVENO";
    const nD1 = cpl ? "DÉCIMO PRIMERO" : "DÉCIMO";
    h += '<p class="cl"><span class="clh">' + nT + ": TÍTULO DE ADQUISICIÓN DEL HIPOTECANTE.</span> El inmueble que se hipoteca fue adquirido por " + HIP + ' a título de compraventa, según consta en este mismo instrumento.<span class="fill"></span></p>';
    h += '<p class="cl"><span class="clh">' + nO + ": OBLIGACIONES GARANTIZADAS.</span> Con la presente hipoteca se garantiza el Crédito Hipotecario de Vivienda Individual a Largo Plazo aprobado por " + ACR + " a " + HIP + " por la suma de " + IF("saldo", monto) + ", que será pagada dentro del plazo de " + IF("plazoAnios", s.plazoAnios + " años") + " en " + IF("numCuotas", s.numCuotas + " cuotas") + ' mensuales sucesivas, mes vencido, la primera un mes después del desembolso.<span class="fill"></span></p>';
    h += '<p class="para"><span class="clh">Parágrafo — Hipoteca abierta.</span> Por ser hipoteca abierta y sin límite de cuantía, garantiza además toda clase de obligaciones, en moneda legal o en UVR, presentes o futuras, directas o indirectas, que ' + HIP + " haya contraído o llegue" + hN + " a contraer a favor de " + ACR + " —préstamos, descuentos, avales, garantías, tarjetas de crédito, sobregiros—, con sus intereses remuneratorios y moratorios, costas y gastos de cobranza; no se extingue por prorrogarse, cambiarse o renovarse las obligaciones garantizadas.</p>";
    h += '<p class="cl"><span class="clh">' + nV + ": VALOR DEL ACTO.</span> Para efectos exclusivos de la liquidación de derechos notariales y de registro se fija la suma de " + IF("saldo", monto) + ". " + R("Se protocoliza la carta de aprobación del crédito expedida por " + ACR + ", sin que ello implique modificación del carácter de hipoteca abierta sin límite de cuantía; " + HIP + " declara" + hN + " no haber recibido desembolsos anteriores.", "art. 58 · Ley 788/2002") + '<span class="fill"></span></p>';
    h += '<p class="cl"><span class="clh">' + nSx + ": DECLARACIONES DEL HIPOTECANTE.</span> " + HIP + " declara" + hN + ": a) que el inmueble es de su exclusiva propiedad y está libre de gravámenes distintos de esta hipoteca; b) que la garantía se extiende a mejoras e indemnizaciones; c) que entregará a " + ACR + " la primera copia con mérito ejecutivo dentro de los treinta (30) días siguientes al registro; d) que notificará a " + ACR + ' cualquier enajenación o gravamen posterior; e) que atenderá las obligaciones urbanísticas y de conservación del inmueble.<span class="fill"></span></p>';
    h += '<p class="cl"><span class="clh">' + nSp + ": SEGUROS.</span> " + HIP + " se obliga" + hN + " a amparar el inmueble contra incendio y terremoto, y su propia vida (deudor), con compañía aceptada por " + ACR + ", cediéndole el derecho sobre las indemnizaciones hasta concurrencia de la deuda; en su defecto, " + ACR + " podrá —sin estar obligado— contratar los seguros con cargo a " + HIP + " " + D("art. 1101 C.Com.") + '.<span class="fill"></span></p>';
    h += '<p class="cl"><span class="clh">' + nOc + ": EXTINCIÓN DEL PLAZO (ACELERACIÓN).</span> " + ACR + " podrá declarar vencidos los plazos y exigir el pago total: a) por mora en el pago de cualquier obligación; b) si " + HIP + " enajena" + hN + " o grava" + hN + ' el inmueble sin autorización; c) por embargo o acción judicial que afecte el inmueble; d) por falsedad en la información suministrada; e) por destinación del crédito distinta de la pactada; f) por no contratar o mantener los seguros; g) por demérito de la garantía según avalúo de perito de Lonja.<span class="fill"></span></p>';
    h += '<p class="cl"><span class="clh">' + nNv + ": VIGENCIA Y AUSENCIA DE NOVACIÓN.</span> La hipoteca permanecerá vigente mientras exista alguna obligación pendiente a favor de " + ACR + ". Las prórrogas, novaciones o modificaciones de las obligaciones no extinguen la garantía " + D("art. 2457 C.C.") + '.<span class="fill"></span></p>';
    h += '<p class="cl"><span class="clh">' + nDx + ": CESIÓN.</span> " + ACR + " podrá ceder total o parcialmente el crédito y la garantía sin necesidad de nueva comparecencia de " + HIP + ", quien desde ahora acepta" + hN + " la cesión " + D("art. 24 · Ley 546/1999") + '.<span class="fill"></span></p>';
    h += '<p class="cl"><span class="clh">' + nD1 + ": GASTOS.</span> Los gastos, derechos notariales e impuesto de registro que genere esta hipoteca son de cargo de " + HIP + '.<span class="fill"></span></p>';
    h += '<p class="cl" data-sec="acreedor">Presente ' + IF("apoderadoBanco", s.apoderadoBanco) + ", mayor de edad, en su condición de Apoderado(a) Especial de " + IF("banco", s.banco) + ", según poder conferido por Escritura Pública " + IF("poderBancoEP", s.poderBancoEP) + " de la " + IF("poderBancoNot", s.poderBancoNot) + ", manifestó: Que en nombre de " + ACR + ' ACEPTA la hipoteca y las declaraciones contenidas en este instrumento, por hallarse a entera satisfacción.<span class="fill"></span></p>';
    if (casadoOUnion(C)) h += '<p class="cl">' + R("EFECTOS DE LA LEY 258 DE 1996: Compareciendo nuevamente " + HIP + ", manifiesta" + hN + " que la afectación a vivienda familiar constituida en este mismo instrumento no será oponible a la presente hipoteca, la cual acepta" + hN + " y ratifica" + hN + ".", "art. 6 · Ley 258/1996") + '<span class="fill"></span></p>';
  }

  if (s.interprete) h += '<p class="cl">' + R("Comparece un intérprete que tradujo íntegramente el instrumento a el (los) otorgante(s) que no domina(n) el idioma; se deja constancia de su comprensión y aprobación.", "art. 38 · Dcto 960/70") + '<span class="fill"></span></p>';
  if (s.firmaRuego) h += '<p class="cl">' + R("Manifestando uno de los otorgantes no saber o no poder firmar, firma por él a su ruego un tercero, en presencia de dos testigos hábiles que también suscriben; se toma su impresión dactilar.", "art. 39 · Dcto 960/70") + '<span class="fill"></span></p>';
  if (s.pepAny || s.cuentaTercero) h += '<p class="para"><span class="clh">Parágrafo — Debida diligencia.</span> ' + R((s.cuentaTercero ? "Se identifica al beneficiario final por cuya cuenta se actúa. " : "") + (s.pepAny ? "Se deja constancia de la condición de Persona Expuesta Políticamente y de la debida diligencia reforzada aplicada." : ""), "Dcto 830/2021") + "</p>";
  h += otorgamiento(s, tarifas);
  return h;
}

export function otorgamiento(s: CompraventaState, tarifas: TarifaConfig = TARIFAS): string {
  const V = s.V;
  const C = s.C;
  const vpl = V.length > 1;
  const vend = vpl ? "los vendedores" : "el vendedor";
  const L = liquidar(s, tarifas);
  const derNot = L.items[0].v;
  const iva = L.items[1].v;
  const impReg = L.items[2].v;
  const ret = L.items[3].v;
  const inmuebles = inmueblesCompraventa(s);
  const multiInmuebles = usaInmueblesExplicitos(s) && inmuebles.length > 1;
  const sech = "text-align:center;font-weight:700;font-family:var(--sans);font-size:12px;letter-spacing:.06em;margin:24px 0 14px;padding:6px 0;border-top:1px solid var(--line-strong);border-bottom:1px solid var(--line-strong);color:var(--accent)";
  let h = '<div class="sech" data-sec="otorgamiento" style="' + sech + '">OTORGAMIENTO Y AUTORIZACIÓN</div>';
  h += '<p class="cl"><span class="clh">LECTURA Y OTORGAMIENTO.</span> ' + R("Leído el presente instrumento por los comparecientes, advertidos del derecho a revisarlo y de la responsabilidad penal por faltar a la verdad, y enterados de su contenido, alcance y efectos legales, lo aprobaron y firman en un mismo acto ante el Notario que autoriza, con lo cual queda perfeccionado el otorgamiento.", "Dcto 960/1970") + '<span class="fill"></span></p>';
  const docs: string[] = [];
  if (s.apod) docs.push("el poder que acredita la representación de la parte vendedora");
  if (anyJuridica(s)) docs.push("el certificado de existencia y representación legal");
  if (s.ax.tradicion) docs.push("el certificado de tradición y libertad del inmueble");
  if (s.ax.predial) docs.push("el paz y salvo del impuesto predial");
  if (s.ph && s.ax.admin) docs.push("el paz y salvo de expensas de la copropiedad");
  if (s.subsidio) docs.push("el acto de asignación del subsidio de vivienda");
  if (docs.length) h += '<p class="cl" data-sec="protocolizacion"><span class="clh">DOCUMENTOS QUE SE PROTOCOLIZAN.</span> ' + R("Se agregan al protocolo, como parte integrante de esta escritura, los siguientes documentos habilitantes: " + docs.join("; ") + ".", "Dcto 1069/2015") + '<span class="fill"></span></p>';
  h += '<p class="cl" data-sec="fiscal"><span class="clh">CONSTANCIAS FISCALES.</span> El Notario deja constancia de que, actuando como agente retenedor, recaudó la retención en la fuente a cargo de ' + vend + " por " + I(fmt(ret)) + " " + D("art. 398 E.T.") + "; que los derechos notariales de esta escritura ascienden a " + I(fmt(derNot)) + " más IVA de " + I(fmt(iva)) + "; y que el impuesto de registro liquidado es de " + I(fmt(impReg)) + " " + D("RES-2026-000964-6") + '.<span class="fill"></span></p>';
  h += '<p class="cl" data-sec="liquidacion"><span class="clh">DERECHOS, RECAUDOS Y VALORES A PAGAR.</span> Conforme a las tarifas vigentes (' + esc(tarifas.resNotarial) + '), los valores causados con este instrumento son los siguientes:<span class="fill"></span></p>';
  h += '<p class="para">a) Derechos notariales' + (s.vis !== "no" ? " (con descuento del 50% por VIS)" : "") + ": " + I(fmt(derNot)) + ". — b) Impuesto sobre las ventas (IVA 19%): " + I(fmt(iva)) + ". — c) Impuesto de registro (1%): " + I(fmt(impReg)) + ". — d) Retención en la fuente (1%), a cargo de " + vend + ", recaudada por el Notario: " + I(fmt(ret)) + '.<span class="fill"></span></p>';
  h += '<p class="para">Total de gastos e impuestos, sin incluir la retención: ' + I(fmt(L.totalGastos)) + ", que se cubre por las partes por iguales, correspondiendo " + I(fmt(L.comprador)) + " a la parte compradora y " + I(fmt(L.vendedor)) + ' a la parte vendedora (incluida la retención).<span class="fill"></span></p>';
  const cpl = C.length > 1;
  const cDecl = cpl ? "los compradores declaran" : "la parte compradora declara";
  h += '<div class="sech" data-sec="notas" style="' + sech + '">NOTAS Y CONSTANCIAS FINALES</div>';
  let nn = 0;
  const nota = (t: string): string => {
    nn++;
    return '<p class="para"><span class="clh">NOTA ' + nn + ".</span> " + t + "</p>";
  };
  if (s.credito) {
    h += nota("El valor base para la liquidación de derechos corresponde a la suma indicada por la entidad crediticia en la carta de aprobación que se protocoliza con este instrumento.");
    h += nota(R("El (la) apoderado(a) de " + esc(s.banco) + " suscribe fuera del despacho notarial, conforme al artículo 12 del Decreto 2148 de 1983 (compilado en el Decreto 1069 de 2015).", "art. 12 · Dcto 2148/1983"));
    h += nota(R("La presente escritura debe registrarse dentro de los noventa (90) días siguientes; transcurridos dos (2) meses causará intereses moratorios.", "Ley 1579/2012"));
  }
  h += nota("El (los) compareciente(s) hace(n) constar que ha(n) verificado cuidadosamente su nombre completo, número de documento de identidad y demás datos personales consignados.");
  h += nota(R("AUTORIZACIÓN DE TRATAMIENTO DE DATOS PERSONALES: los comparecientes autorizan a la Notaría, como responsable, a almacenar y tratar sus datos. STRADATA SEARCH: en cumplimiento de la Circular 1536 del 17 de septiembre de 2013 de la S.N.R. y del artículo 17 de la Ley 1581 de 2012, se consultó la información de los intervinientes.", "Circular SNR 1536/2013 · Ley 1581/2012"));
  if (anyNatural(C)) h += nota(R("REDAM: ante la indisponibilidad de la base de datos del Registro de Deudores Alimentarios Morosos, " + cDecl + " bajo juramento no tener obligaciones alimentarias en mora superiores a tres (3) meses.", "Ley 2097/2021 · Dcto 1310/2022"));
  if (s.ph) h += nota(R("PAZ Y SALVO DE EXPENSAS: se " + (s.ax.admin ? "protocoliza el paz y salvo de las expensas comunes de la copropiedad" : "deja constancia de que no existe administración ni se causan expensas comunes, y el comprador se hace solidario por las que llegaren a existir") + ".", "art. 29 · Ley 675/2001"));
  h += nota(R("IDENTIFICACIÓN BIOMÉTRICA: la identidad de los comparecientes se verificó mediante autenticación biométrica.", "art. 18 · Dcto Ley 019/2012"));
  h += nota("NOTIFICACIONES ELECTRÓNICAS: cada otorgante manifestó su consentimiento según se indica en su respectiva ficha de firma.");
  const anx: string[] = [];
  if (s.ax.tradicion) anx.push("certificado de tradición y libertad");
  if (s.ax.predial) anx.push("paz y salvo del impuesto predial y de valorización");
  if (s.ph && s.ax.admin) anx.push("paz y salvo de expensas comunes");
  if (anx.length) h += '<p class="para"><span class="clh">ANEXOS.</span> Se presentaron y se agregan: ' + anx.join("; ") + ".</p>";
  if (multiInmuebles) {
    h += '<p class="para"><span class="clh">AVALÚOS CATASTRALES DE LOS INMUEBLES.</span> ' + inmuebles.map((inmueble, index) => "Inmueble " + (index + 1) + ": " + IF(inmuebleField(s, index, "avaluoCatastral"), money(inmueble.avaluoCatastral || 0)) + ". NUPRE: " + IF(inmuebleField(s, index, "nupre"), inmueble.nupre || "—")).join(" — ") + ".</p>";
  } else {
    h += '<p class="para"><span class="clh">AVALÚO CATASTRAL DEL INMUEBLE.</span> ' + IF("avaluoCatastral", money(s.avaluoCatastral)) + ". NUPRE: " + IF("nupre", s.nupre) + ".</p>";
  }
  h += '<p class="cl"><span class="clh">AUTORIZACIÓN.</span> ' + R("El suscrito Notario Dieciséis del Círculo de Medellín AUTORIZA el presente instrumento —Escritura número " + esc(s.numEscritura) + "—, previa verificación del cumplimiento de los requisitos legales y de la identidad de los comparecientes, e imparte la fe pública que la ley le confía.", "Dcto 960/1970") + '<span class="fill"></span></p>';

  const blank = '<span style="color:var(--line-strong)">____________________</span>';
  const fld = (label: string, val: string): string => '<div style="font-family:var(--sans);font-size:10px;color:var(--ink-soft);margin-top:1px"><span style="color:var(--ink-faint)">' + label + ":</span> " + (val ? '<span style="color:var(--ink)">' + val + "</span>" : blank) + "</div>";
  const chk = (label: string, val?: boolean): string => {
    const box = (on: boolean): string => '<span style="color:' + (on ? "var(--ins)" : "var(--line-strong)") + ';font-weight:700">' + (on ? "☒" : "▢") + "</span>";
    return '<div style="font-family:var(--sans);font-size:10px;color:var(--ink-faint);margin-top:1px">' + label + " &nbsp;Sí " + box(val === true) + "&nbsp; No " + box(val === false) + "</div>";
  };
  const firmante = (nombre: string, ident: string, o: { direccion?: string; muni?: string; telefono?: string; correo?: string; ocupacion?: string; estado?: string; noti?: boolean; pep?: boolean; apoderaDe?: string } = {}): string => '<div style="margin-top:22px;break-inside:avoid"><div style="border-top:1px solid var(--ink);margin-bottom:4px"></div>'
    + '<div style="font-family:var(--serif);font-weight:600;font-size:12px;line-height:1.3">' + nombre + "</div>"
    + '<div style="font-family:var(--sans);font-size:10px;color:var(--ink)">' + ident + "</div>"
    + fld("Dirección", o.direccion || "") + fld("Municipio", o.muni || "") + fld("Teléfono", o.telefono || "") + fld("Correo electrónico", o.correo || "")
    + fld("Profesión u ocupación", o.ocupacion || "") + (o.estado ? fld("Estado civil", o.estado) : "")
    + chk("Autoriza notificaciones electrónicas:", o.noti)
    + chk("Persona Expuesta Políticamente (Decreto 1674 de 2016):", o.pep)
    + '<div style="font-family:var(--sans);font-size:10px;color:var(--ink-faint);margin-top:1px">Biometría: <span style="color:var(--line-strong)">___________</span></div>'
    + (o.apoderaDe ? '<div style="font-family:var(--sans);font-size:10px;color:var(--ink);margin-top:2px"><b>Apoderado(a) especial de:</b> ' + o.apoderaDe + "</div>" : "")
    + "</div>";
  const ficha = (p: Party): string => {
    const estado = p.tipo === "juridica" ? "" : labelEstado(p.estado, p.genero);
    return firmante(esc(p.nombre), p.tipo === "juridica" ? "NIT " + esc(p.id) + (p.repr ? " — Rep. legal " + esc(p.repr) : "") : docLabel(p.tipoDoc) + " " + esc(p.id), { muni: esc(p.ciudad), estado, direccion: esc(p.direccion), telefono: esc(p.telefono), correo: esc(p.correo), ocupacion: esc(p.ocupacion), noti: !!p.notiElec, pep: !!p.pep });
  };
  const fichaAux = (p: AuxParty, role: string): string => firmante(p.nombre ? esc(p.nombre) : "____________________________", docLabel(p.tipoDoc) + " " + (p.id ? esc(p.id) : "____________") + " · " + role, { muni: esc(p.ciudad), direccion: esc(p.direccion), telefono: esc(p.telefono), correo: esc(p.correo), ocupacion: esc(p.ocupacion) });
  let sigs = "";
  if (s.apod) {
    const pd = V.map((p) => esc(p.nombre) + " — C.C. " + esc(p.id)).join("; ");
    sigs += firmante(esc(s.apodN), "C.C. ____________", { apoderaDe: pd });
  } else V.forEach((p) => { sigs += ficha(p); });
  C.forEach((p) => { sigs += ficha(p); });
  if (s.credito) sigs += firmante(s.apoderadoBanco ? esc(s.apoderadoBanco) : "____________________________", "Apoderado(a) especial · C.C. ____________", { apoderaDe: esc(s.banco) + " — NIT " + esc(s.bancoNit) });
  if (s.interprete) sigs += firmante("____________________________", "Intérprete oficial · art. 38 Dcto 960/1970");
  if (s.firmaRuego) sigs += fichaAux(s.ruego, "Firma a ruego del otorgante que no puede firmar · art. 39");
  if (s.firmaRuego || s.testigosOn) s.testigos.forEach((p) => { sigs += fichaAux(p, "Testigo instrumental"); });
  h += '<p class="cl"><span class="clh">HOJAS DE PAPEL NOTARIAL.</span> Se extendió en las hojas de papel notarial números ' + IF("hojaInicial", s.hojaInicial) + ' y siguientes.<span class="fill"></span></p>';
  h += '<div data-sec="firmas" style="margin-top:22px"><div style="font-family:var(--sans);font-size:9px;color:var(--ink-faint);letter-spacing:.02em;margin-bottom:6px">VIENE DE LA HOJA DE PAPEL NOTARIAL NRO. ' + IF("hojaInicial", s.hojaInicial) + " DE LA ESCRITURA PÚBLICA NÚMERO " + esc(s.numEscritura) + " DE LA NOTARÍA DIECISÉIS DE MEDELLÍN. ——————</div>"
    + '<div style="text-align:center;font-family:var(--sans);font-size:10.5px;letter-spacing:.07em;color:var(--ink-soft);text-transform:uppercase;margin-bottom:2px">Firmas de los otorgantes</div>'
    + '<div style="display:grid;grid-template-columns:1fr 1fr;gap:2px 34px">' + sigs + "</div>";
  h += '<div style="margin-top:34px;text-align:center"><div style="border-top:1px solid var(--ink);width:55%;margin:0 auto 5px"></div><div style="font-family:var(--serif);font-weight:600;font-size:12.5px">JUAN CAMILO OROZCO GAVIRIA</div><div style="font-family:var(--sans);font-size:10.5px;color:var(--ink-soft)">Notario Dieciséis Encargado de Medellín · Autoriza — Escritura Nro. ' + esc(s.numEscritura) + "</div></div></div>";
  return h;
}

export function evaluar(s: CompraventaState): EvaluacionItem[] {
  const it: EvaluacionItem[] = [];
  const V = s.V;
  const C = s.C;
  const inmuebles = inmueblesCompraventa(s);
  const multiInmuebles = usaInmueblesExplicitos(s) && inmuebles.length > 1;
  inmuebles.forEach((inmueble, index) => {
    const label = multiInmuebles ? "Inmueble " + (index + 1) : "Inmueble";
    if (!inmueble.matricula.trim()) it.push({ t: "crit", h: label + " no plenamente identificado", p: "Falta la matrícula inmobiliaria: el registro devolvería el título.", n: "art. 16 · Ley 1579/2012" });
    if (!inmueble.linderos.trim()) it.push({ t: "crit", h: multiInmuebles ? "Faltan los linderos del inmueble " + (index + 1) : "Faltan los linderos", p: "Sin linderos, cabida y área el inmueble no queda individualizado para el registro.", n: "art. 8 · Ley 1579/2012" });
  });
  if (s.inicial + s.saldo !== s.total) it.push({ t: "crit", h: "Descuadre en el precio", p: "La suma de los pagos (" + pts(s.inicial + s.saldo) + ") no coincide con el total (" + pts(s.total) + ").", n: "art. 90 E.T." });
  const sc = sumaCuotas(C);
  if (C.length > 1 && sc !== 100) it.push({ t: "crit", h: "Las cuotas de los compradores no suman 100%", p: "Suman " + sc + "%. El proindiviso debe cubrir el 100% del derecho transferido.", n: "" });
  const sv = sumaCuotas(V);
  if (V.length > 1 && sv !== 100) it.push({ t: "warn", h: "Las cuotas de los vendedores no suman 100%", p: "Suman " + sv + "%. Verificar las participaciones que cada vendedor transfiere.", n: "" });
  const enc = encadenamientosActivos(s);
  if (s.gravamen === "patrimonio" && !enc.cancelacionPatrimonioFamilia) it.push({ t: "crit", h: "Patrimonio de familia sin cancelar", p: "Debe cancelarse antes de vender (escritura con ambos cónyuges; con menores, autorización judicial).", n: "Ley 70/1931 · 495/1999" });
  if (s.gravamen === "embargo") it.push({ t: "crit", h: "Medida cautelar vigente", p: "El embargo o la demanda debe levantarse para poder transferir.", n: "art. 16 · Ley 1579/2012" });
  if (casadoOUnion(V) && s.afect === "si") it.push({ t: "crit", h: "Requiere consentimiento del cónyuge", p: "Bien afectado a vivienda familiar: exige firma de ambos cónyuges/compañeros so pena de nulidad.", n: "art. 3 · Ley 258/1996" });
  if (s.apod) it.push({ t: "warn", h: "Vigencia del poder", p: "La parte vendedora comparece por apoderado: verificar poder vigente con facultades expresas para enajenar.", n: "Dcto 1069/2015" });
  if (multiInmuebles) it.push({ t: "obl", h: "Varios inmuebles en un instrumento", p: "La cláusula de objeto enumera " + inmuebles.length + " inmuebles con folio, linderos y datos catastrales propios.", n: "arts. 8 y 16 · Ley 1579/2012" });
  if (folioEstadosActivos(s)) {
    const estado = s.folioEstado as FolioEstado;
    it.push({ t: "warn", h: "Estado del folio: " + folioEstadoLabel(estado), p: folioEstadoTexto(estado), n: folioEstadoCita(estado) });
  }
  if (enc.cancelacionHipotecaPrevia) it.push({ t: "obl", h: "Cancelación de hipoteca previa encadenada", p: "El instrumento incluye acto previo de cancelación de hipoteca antes de la transferencia.", n: "art. 2457 C.C. · Ley 1579/2012" });
  if (enc.cancelacionPatrimonioFamilia) it.push({ t: "obl", h: "Cancelación de patrimonio de familia encadenada", p: "El instrumento cancela el patrimonio de familia antes de transferir el dominio.", n: "Ley 70/1931 · Ley 495/1999" });
  if (enc.afectacionViviendaFamiliar) it.push({ t: "obl", h: "Afectación a vivienda familiar encadenada", p: "El instrumento constituye la afectación a vivienda familiar después de la compra.", n: "art. 6 · Ley 258/1996" });
  const divisas = divisasActivas(s);
  if (divisas.parteExtranjeraNoResidente) it.push({ t: "obl", h: "Parte extranjera o no residente", p: "La comparecencia identifica pasaporte, cédula de extranjería o PPT; si hay poder otorgado en el exterior, debe protocolizarse apostillado/legalizado.", n: "Dcto 1069/2015 · régimen cambiario" });
  if (divisas.parteExtranjeraNoResidente && s.apod && !divisas.poderExteriorApostillado) it.push({ t: "warn", h: "Poder del exterior por validar", p: "Si el poder fue otorgado fuera de Colombia, verificar apostilla o legalización y traducción oficial cuando aplique.", n: "Dcto 1069/2015" });
  if (divisas.pagoDivisas) {
    it.push({ t: "obl", h: "Declaración de cambio", p: "La operación en divisas debe quedar soportada con declaración de cambio y trazabilidad de origen de fondos.", n: "Circular DCIN Banrep" });
    if (!divisas.canalizacionMercadoCambiario) it.push({ t: "warn", h: "Canalización por mercado cambiario pendiente", p: "El pago en divisas debe canalizarse por el mercado cambiario cuando corresponda.", n: "Ley 9/1991 · Dcto 1068/2015" });
    if (!divisas.registroInversionExtranjera) it.push({ t: "warn", h: "Registro de inversión extranjera pendiente", p: "Cuando la adquisición configure inversión extranjera, registrar la operación ante el Banco de la República.", n: "Ley 9/1991 · Circular DCIN Banrep" });
  }
  const rural = ruralActiva(s);
  if (rural.predioRural) it.push({ t: "obl", h: "Predio rural identificado sin PH", p: "El instrumento deja constancia de cabida, UAF de referencia y revisión de restricciones agrarias.", n: "Ley 160/1994" });
  if (rural.superaUaf && !rural.autorizacionAnt) it.push({ t: "crit", h: "UAF excedida sin autorización", p: "La adquisición de terrenos inicialmente adjudicados como baldíos no puede exceder la UAF sin la autorización o habilitación aplicable.", n: "art. 72 · Ley 160/1994" });
  if (rural.baldioAdjudicado && rural.restriccionTemporal) it.push({ t: "warn", h: "Baldío adjudicado con restricción temporal", p: "Verificar término de restricción, autorización ANT y antecedentes antes del otorgamiento o registro.", n: "arts. 39 y 72 · Ley 160/1994" });
  if (rural.derechoPreferencia) it.push({ t: "warn", h: "Derecho de preferencia agrario", p: "Debe revisarse si procede oferta previa o autorización de la ANT u otro beneficiario preferente.", n: "art. 39 · Ley 160/1994" });
  const capacidad = capacidadActiva(s);
  if ((capacidad.menorVendedor || capacidad.ventaBienMenor) && !capacidad.autorizacionVentaMenor) it.push({ t: "warn", h: "Venta de bien de menor sin autorización", p: "Debe protocolizarse autorización judicial o notarial vigente antes de completar la venta del bien de una persona menor de edad.", n: "Ley 1996/2019 · Dcto 1429/2020" });
  if ((capacidad.menorVendedor || capacidad.ventaBienMenor) && capacidad.autorizacionVentaMenor) it.push({ t: "obl", h: "Autorización para venta de bien de menor", p: "La autorización aplicable queda relacionada para revisión del notario.", n: "Ley 1996/2019 · Dcto 1429/2020" });
  if (capacidad.discapacidadConApoyos && !capacidad.apoyoAcreditado) it.push({ t: "warn", h: "Apoyos no acreditados", p: "La persona conserva capacidad legal plena; si utiliza apoyos, el acuerdo o adjudicación vigente debe acreditarse.", n: "Ley 1996/2019 arts. 6, 15 y 16" });
  if (capacidad.discapacidadConApoyos && capacidad.apoyoAcreditado) it.push({ t: "obl", h: "Apoyos acreditados", p: "El instrumento deja constancia del apoyo sin sustituir la voluntad de la persona titular.", n: "Ley 1996/2019 arts. 6, 15 y 16" });
  it.push({ t: "obl", h: "Declaración de valor real", p: "Declaración juramentada incluida — evita la base de 4×.", n: "art. 90 E.T." });
  it.push({ t: "obl", h: "Declaración de origen de fondos", p: "Cláusula SIPLAFT presente para la parte compradora.", n: "Ley 2195/2022" });
  it.push({ t: "obl", h: "Retención en la fuente del 1%", p: "Constancia de recaudo por el Notario incluida.", n: "art. 398 E.T." });
  if (casadoOUnion(V)) {
    if (s.afect === "no") it.push({ t: "ok", h: "Afectación a vivienda familiar", p: "Indagación y declaración juramentada de no afectación incluidas.", n: "art. 6 · Ley 258/1996" });
    else if (s.afect === "nosabe") it.push({ t: "warn", h: "Afectación a vivienda familiar sin definir", p: "El vendedor no precisó la afectación: verificar contra el folio antes de otorgar.", n: "art. 6 · Ley 258/1996" });
  }
  if (s.ph) {
    if (s.ax.admin) it.push({ t: "ok", h: "Paz y salvo de administración", p: "Aportado y relacionado en anexos.", n: "art. 29 · Ley 675/2001" });
    else it.push({ t: "warn", h: "Paz y salvo de administración faltante", p: "En PH conviene aportarlo; sin él, constancia + solidaridad del comprador por expensas.", n: "art. 29 · Ley 675/2001" });
  }
  if (!s.ax.tradicion) it.push({ t: "warn", h: "Certificado de tradición no aportado", p: "Sin folio vigente no se pueden verificar gravámenes ni la libertad del bien.", n: "Ley 1579/2012" });
  if (s.vis === "sfve") it.push({ t: "obl", h: "Advertencias VIS incluidas", p: "Prohibición de enajenar 5 años + condición resolutoria; constituir patrimonio de familia.", n: "art. 13 · Ley 2079/2021" });
  if (s.gravamen === "hipoteca_previa") it.push({ t: "warn", h: "Hipoteca previa a cancelar", p: "Cláusula de cancelación incluida; confirmar paz y salvo del acreedor anterior.", n: "" });
  if (s.credito) it.push({ t: "ok", h: "Sección de hipoteca completa", p: C.length > 1 ? "Los compradores figuran como hipotecantes." : "Constitución, objeto de la garantía y aceleración de plazos ensambladas.", n: "" });
  if (C.length > 1) it.push({ t: "ok", h: "Adquisición en común y proindiviso", p: C.length + " compradores con cuotas que suman " + sc + "%.", n: "" });
  if (anyJuridica(s)) {
    it.push({ t: "obl", h: "Existencia y representación de la persona jurídica", p: "Certificado de existencia y representación legal vigente (menos de 30 días) y facultades del representante.", n: "C. Comercio" });
    it.push({ t: "warn", h: "Autorización del órgano social", p: "Si los estatutos o la cuantía lo exigen, protocolizar el acta de junta o asamblea que autoriza el negocio.", n: "C. Comercio" });
  }
  if (s.gravamen === "leasing") it.push({ t: "crit", h: "Leasing habitacional vigente", p: "Durante el contrato la entidad es la propietaria: debe terminarse el leasing (o ejercerse la opción) antes de transferir.", n: "Ley 795/2003" });
  if (s.gravamen === "usufructo") it.push({ t: "warn", h: "Usufructo vigente", p: "Se vende la nuda propiedad o el usufructuario debe comparecer renunciando/consolidando.", n: "C.C. 823" });
  if (s.gravamen === "servidumbre") it.push({ t: "ok", h: "Servidumbre relacionada", p: "Se describe y el comprador la respeta (activa se transfiere, pasiva grava).", n: "C.C. 879" });
  if (s.tipoNegocio === "reserva") it.push({ t: "warn", h: "Reserva de dominio sobre inmueble", p: "Su eficacia real es discutida; en inmuebles se asimila a condición resolutoria. Validar con el notario.", n: "C.C. 1935" });
  if (s.tipoNegocio === "retroventa") it.push({ t: "obl", h: "Pacto de retroventa", p: "Plazo máximo de 4 años; se inscribe para oponibilidad y limita la disposición del comprador.", n: "art. 1939 C.C." });
  if (s.tipoNegocio === "dacion") it.push({ t: "warn", h: "Dación en pago", p: "Identificar la obligación que se extingue; efectos tributarios propios.", n: "C.C. 1627" });
  if (s.tituloTipo === "sucesion") it.push({ t: "warn", h: "Título por sucesión", p: "Verificar partición registrada e impuestos sucesorales al día.", n: "CGP" });
  if (s.tituloTipo === "donacion") it.push({ t: "warn", h: "Título por donación", p: "Verificar insinuación (si superó 50 SMLMV) y posibles cargas/revocación.", n: "C.C. 1458" });
  if (s.subsidio) it.push({ t: "obl", h: "Subsidio de vivienda", p: "Protocolizar el acto de asignación; verificar patrimonio de familia y restricciones del subsidio.", n: "Ley 3ª/1991" });
  if (s.firmaRuego) it.push({ t: "obl", h: "Firma a ruego con testigos", p: "Firma un tercero a ruego + dos testigos hábiles; huella del compareciente.", n: "art. 39 · Dcto 960/70" });
  if (s.interprete) it.push({ t: "obl", h: "Intérprete / traductor", p: "Comparece intérprete; documentos en otro idioma traducidos oficialmente.", n: "art. 38 · Dcto 960/70" });
  if (s.pepAny) it.push({ t: "warn", h: "PEP — debida diligencia reforzada", p: "Persona Expuesta Políticamente: declaración y verificación de fuente de riqueza.", n: "Dcto 830/2021" });
  if (s.cuentaTercero) it.push({ t: "warn", h: "Beneficiario final", p: "Actúa por cuenta de tercero: identificar y registrar el beneficiario final.", n: "Dcto 830/2021" });
  it.push(s.posesion2 ? { t: "ok", h: "Ganancia ocasional (15%)", p: "Posesión ≥ 2 años: la utilidad grava como ganancia ocasional al 15% (se liquida en renta, no en notaría).", n: "art. 313 E.T." } : { t: "warn", h: "Utilidad como renta ordinaria", p: "Posesión < 2 años: la utilidad tributa como renta ordinaria (tarifa marginal), no como ganancia ocasional.", n: "E.T. 300" });
  it.push({ t: "ok", h: "Otorgamiento en unidad de acto", p: "Lectura, aprobación y firma de los comparecientes ante el notario — las cuatro fases del art. 13.", n: "Dcto 960/1970" });
  it.push({ t: "obl", h: "Protocolización de documentos habilitantes", p: "Los soportes del acto (poder, certificados, paz y salvos, subsidio) se agregan al protocolo.", n: "Dcto 1069/2015" });
  it.push({ t: "obl", h: "Autorización notarial", p: "Constancia de autorización de la Escritura Nro. " + esc(s.numEscritura) + " e imposición de la fe pública, con las constancias fiscales de retención, derechos e impuesto de registro.", n: "Dcto 960/1970" });
  if (!s.numEscritura.trim()) it.push({ t: "warn", h: "Falta el número de escritura", p: "La autorización y las copias requieren el número de instrumento del protocolo.", n: "Dcto 960/1970" });
  return it;
}

export function liquidar(s: CompraventaState, tarifas: TarifaConfig = TARIFAS): {
  items: { c: string; t: string; v: number; cargo: string; tip: string }[];
  totalGastos: number;
  comprador: number;
  vendedor: number;
} {
  const v = s.total || 0;
  let derNot = v <= tarifas.cuantiaMin ? tarifas.derNotarialBase : Math.round(tarifas.derNotarialBase + (v - tarifas.cuantiaMin) * tarifas.derNotarialPorMil);
  const vis = s.vis !== "no";
  if (vis) derNot = Math.round(derNot * (1 - tarifas.visDesc));
  const iva = Math.round(derNot * tarifas.iva);
  const impReg = Math.round(v * tarifas.impuestoRegistro);
  const ret = Math.round(v * tarifas.retencion);
  const shared = derNot + iva + impReg;
  const comp = Math.round(shared / 2);
  return {
    items: [
      { c: "Derechos notariales" + (vis ? " (−50% VIS)" : ""), t: "3‰ · mín. " + fmt(tarifas.derNotarialBase), v: derNot, cargo: "Partes iguales", tip: tarifas.resNotarial },
      { c: "IVA", t: "19% sobre derechos notariales", v: iva, cargo: "Partes iguales", tip: "" },
      { c: "Impuesto de registro", t: "1% del valor (Antioquia)", v: impReg, cargo: "Partes iguales", tip: "art. 230 Ley 223/1995" },
      { c: "Retención en la fuente", t: "1% del valor", v: ret, cargo: "Vendedor", tip: "art. 398 E.T." },
    ],
    totalGastos: shared,
    comprador: comp,
    vendedor: shared - comp + ret,
  };
}

export function renderLiquidacion(s: CompraventaState, tarifas: TarifaConfig = TARIFAS): string {
  const L = liquidar(s, tarifas);
  let h = '<h3>Liquidación de gastos y tributos</h3><div class="resline">Tarifas ' + tarifas.anio + " · Notarial " + esc(tarifas.resNotarial) + " · Registral " + esc(tarifas.resRegistral) + "<br>Vigentes desde feb-" + tarifas.anio + " · ajuste IPC " + tarifas.ipc + '</div><div class="tblw"><table><thead><tr><th>Concepto</th><th>Tarifa</th><th class="n">Valor</th><th>A cargo</th></tr></thead><tbody>';
  L.items.forEach((i) => {
    h += "<tr><td>" + esc(i.c) + (i.tip ? ' <span class="cite">' + esc(i.tip) + "</span>" : "") + '</td><td class="who">' + esc(i.t) + '</td><td class="n">' + fmt(i.v) + '</td><td class="who">' + esc(i.cargo) + "</td></tr>";
  });
  h += '<tr class="tot"><td colspan="2">Total gastos e impuestos (sin retención)</td><td class="n">' + fmt(L.totalGastos) + "</td><td></td></tr></tbody></table></div>";
  h += '<div class="split"><div class="box"><div class="l">A cargo de la parte compradora</div><div class="v">' + fmt(L.comprador) + '</div></div><div class="box"><div class="l">A cargo del vendedor <span class="who">(incl. retención)</span></div><div class="v">' + fmt(L.vendedor) + "</div></div></div>";
  h += '<div class="note">Cifras con las resoluciones ' + tarifas.anio + ". Cada año se actualiza reemplazando un solo bloque de configuración. Derechos de registro nacionales (SNR) y tarifas de otros departamentos se parametrizan aparte. Validar contra la resolución oficial.</div>";
  return h;
}

export function renderCancelacion(s: CancelacionState, tarifas: TarifaConfig = TARIFAS): string {
  const gA = genEnding(s.cApoGenero);
  const artA = s.cApoGenero === "F" ? "la" : s.cApoGenero === "NB" || s.cApoGenero === "T" ? "le" : "el";
  const sr = s.cApoGenero === "F" ? "señora" : s.cApoGenero === "NB" || s.cApoGenero === "T" ? "señore" : "señor";
  const notEnd = genEnding(s.cNotarioGenero);
  const notArt = genArt(s.cNotarioGenero);
  const notDoc = s.cNotarioGenero === "F" ? "doctora" : s.cNotarioGenero === "NB" || s.cNotarioGenero === "T" ? "doctore" : "doctor";
  const banco = s.cBanco || "____";
  const mat = s.cMatricula || "________";
  const deudor = s.cDeudor || "____";
  let h = "";
  h += '<div class="calif"><h4>Superintendencia de Notariado y Registro · Formato de Calificación · Art. 8 Par. 4 Ley 1579/2012</h4><div class="r">'
    + '<span class="k">Folio matrícula</span><span>' + IF("cMatricula", mat) + "</span>"
    + '<span class="k">Cód. catastral</span><span>' + IF("cCatastral", s.cCatastral || "—") + "</span>"
    + '<span class="k">NUPRE</span><span>' + IF("cNupre", s.cNupre || "—") + "</span>"
    + '<span class="k">Ubicación</span><span>' + IF("cInmdesc", (s.cInmdesc || "—").slice(0, 90) + ((s.cInmdesc || "").length > 90 ? "…" : "")) + "</span></div>"
    + '<table><tr><td>CÓD. 0775 — CANCELACIÓN DE HIPOTECA</td><td>' + (s.cSinCuantia ? "ACTO SIN CUANTÍA" : IF("cHipMonto", "$" + pts(s.cHipMonto))) + "</td></tr></table>"
    + '<div class="r" style="margin-top:6px"><span class="k">DE</span><span>' + IF("cBanco", banco) + '</span><span class="k">A</span><span>' + IF("cDeudor", deudor) + "</span></div></div>";
  h += '<p class="cl" data-sec="comparecencia">En la ciudad de Medellín, Departamento de Antioquia, República de Colombia, a los ' + IF("cFechaOtorg", fechaText(s.cFechaOtorg)) + ", al despacho de la NOTARÍA DIECISÉIS DEL CÍRCULO NOTARIAL DE MEDELLÍN, cuy" + notEnd + " Notari" + notEnd + " " + IF("cCalidad", s.cCalidad || "—") + " es " + notArt + " " + notDoc + " " + IF("cNotario", s.cNotario) + " (según " + IF("cActoAdmin", s.cActoAdmin) + ').<span class="fill"></span></p>';
  h += '<p class="cl">Se presentó ' + artA + " " + sr + " " + IF("cApoNombre", s.cApoNombre) + ", quien dijo ser mayor de edad, domiciliad" + gA + " en la ciudad de Medellín, identificad" + gA + " con la cédula de ciudadanía número " + IF("cApoCC", s.cApoCC) + ' y manifestó:<span class="fill"></span></p>';
  const repText = s.cRepTipo === "apoderado"
    ? "según Poder Especial otorgado mediante la Escritura Pública número " + IF("cPoderEP", s.cPoderEP) + " de fecha " + IF("cPoderFecha", s.cPoderFecha) + " de la " + IF("cPoderNotaria", s.cPoderNotaria) + ", copia del cual se adjunta para su protocolización con el presente instrumento"
    : "circunstancias que se acreditan con el correspondiente certificado de existencia y representación legal expedido por la Cámara de Comercio de Medellín para Antioquia; copia del cual se adjunta para su protocolización con el presente instrumento";
  h += '<p class="cl" data-sec="primero"><span class="clh">PRIMERO:</span> ' + R("Que comparece al otorgamiento del presente instrumento, obrando en nombre y representación de " + IF("cBanco", banco) + ", establecimiento bancario, con domicilio principal en la ciudad de " + IF("cBancoDom", s.cBancoDom || "Medellín") + ", representación que ejerce en su carácter de " + IF("cRepCargo", s.cRepCargo) + ", " + repText + ".", "C. Comercio") + '<span class="fill"></span></p>';
  h += '<p class="cl" data-sec="segundo"><span class="clh">SEGUNDO:</span> ' + R("Que por medio de la Escritura Pública número " + IF("cHipEP", s.cHipEP) + " del " + IF("cHipFecha", s.cHipFecha) + " de la " + IF("cHipNotaria", s.cHipNotaria) + ", debidamente registrada el " + IF("cHipRegFecha", s.cHipRegFecha) + " en la Oficina de Registro de Instrumentos Públicos de " + IF("cOrip", s.cOrip) + ", bajo el (los) FOLIO (S) DE MATRÍCULA INMOBILIARIA NÚMERO (S) " + IF("cMatricula", mat) + " el (la, los) señor (a, es) " + IF("cDeudor", deudor) + ", constituyó (eron) en favor de " + IF("cBanco", banco) + ", Hipoteca Global o Abierta de Primer Grado y sin límite en la cuantía, por la cantidad inicial de " + IF("cHipMonto", money(s.cHipMonto)) + ", sobre el siguiente bien inmueble: " + IF("cInmdesc", s.cInmdesc) + ". FOLIO (S) DE MATRÍCULA INMOBILIARIA NRO (S): " + IF("cMatricula", mat) + ". Inmueble que se determina por los linderos y demás especificaciones consignados en la mencionada escritura pública que se cancela.", "Ley 1579/2012") + '<span class="fill"></span></p>';
  h += '<p class="cl" data-sec="tercero"><span class="clh">TERCERO:</span> ' + R("Que obrando en el carácter expresado CANCELA la Hipoteca constituida mediante la Escritura Pública número " + IF("cHipEP", s.cHipEP) + " del " + IF("cHipFecha", s.cHipFecha) + " de la " + IF("cHipNotaria", s.cHipNotaria) + ", debidamente registrada el " + IF("cHipRegFecha", s.cHipRegFecha) + " en la Oficina de Registro de Instrumentos Públicos de " + IF("cOrip", s.cOrip) + ", bajo el (los) FOLIO (S) DE MATRÍCULA INMOBILIARIA NÚMERO (S) " + IF("cMatricula", mat) + " antes mencionada, y en consecuencia, queda (n) libre (s) del gravamen el (los) inmueble (s) descrito (s) en la cláusula segunda de esta escritura.", "art. 2457 C.C.") + '<span class="fill"></span></p>';
  if (s.cNoPazSalvo) h += '<p class="cl"><span class="clh">CUARTO:</span> La cancelación de esta hipoteca no implica paz y salvo a favor del Deudor, ya que este acto solo conlleva la cancelación del gravamen hipotecario identificado en la cláusula anterior, sin que se refiera a un paz y salvo o exoneración total de las obligaciones que por otros conceptos pudiere tener el Deudor, ya sea como deudor principal, avalista o deudor solidario.<span class="fill"></span></p>';
  if (s.cSinCuantia) h += '<p class="cl" data-sec="sincuantia">' + R("EL PRESENTE INSTRUMENTO SE CONSIDERA COMO ACTO SIN CUANTÍA DE CONFORMIDAD CON LA LEY 546 DE 1999.", "art. 23 · Ley 546/1999") + '<span class="fill"></span></p>';
  const artAcap = artA.charAt(0).toUpperCase() + artA.slice(1);
  h += '<p class="cl">' + artAcap + ' exponente leyó personalmente el presente instrumento, lo aprobó y en constancia lo firma.<span class="fill"></span></p>';
  h += '<p class="cl">Se advirtió el registro dentro del término legal para ello.<span class="fill"></span></p>';
  const L = liquidarCanc(s, tarifas);
  h += '<p class="cl" data-sec="liquidacion"><span class="clh">DERECHOS, RECAUDOS Y VALORES A PAGAR.</span> Conforme a las tarifas vigentes (' + esc(tarifas.resNotarial) + "), por tratarse de " + (s.cSinCuantia ? "un acto sin cuantía (Ley 546/1999)" : "un acto de cancelación") + ", los valores causados son: derechos notariales " + I(fmt(L.derNot)) + " más IVA de " + I(fmt(L.iva)) + "; RECAUDO SUPERINTENDENCIA Y FONDO: " + IF("cRecaudo", "$" + pts(L.recaudo)) + '.<span class="fill"></span></p>';
  h += '<p class="cl"><span class="clh">HOJAS DE PAPEL NOTARIAL.</span> Se extendió en las hojas de papel notarial números ' + IF("cHojas", s.cHojas) + ' y siguientes.<span class="fill"></span></p>';
  const sech = "text-align:center;font-weight:700;font-family:var(--sans);font-size:12px;letter-spacing:.06em;margin:24px 0 14px;padding:6px 0;border-top:1px solid var(--line-strong);border-bottom:1px solid var(--line-strong);color:var(--accent)";
  h += '<div class="sech" data-sec="notas" style="' + sech + '">NOTAS Y CONSTANCIAS FINALES</div>';
  let nn = 0;
  const nota = (t: string): string => {
    nn++;
    return '<p class="para"><span class="clh">NOTA ' + nn + ".</span> " + t + "</p>";
  };
  h += nota(R((s.cApoGenero === "F" ? "La doctora " : "El doctor ") + esc(s.cApoNombre) + ", identificad" + gA + " con la cédula de ciudadanía número " + esc(s.cApoCC) + ", actuando en su condición de " + esc(s.cRepCargo) + " de " + esc(banco) + ", por autorización de la suscrita notaria, suscribe la presente escritura pública fuera de las instalaciones de la Notaría Dieciséis de Medellín, en su despacho.", "art. 12 · Dcto 2148/1983"));
  h += nota(R("A los otorgantes se les hizo la advertencia que deben presentar esta escritura para registro, en la Oficina correspondiente, dentro del término perentorio de dos (2) meses contados a partir de la fecha de otorgamiento, cuyo incumplimiento causará intereses moratorios por mes o fracción de mes de retardo.", "Ley 1579/2012"));
  h += nota("El (los) compareciente(s) hace(n) constar que ha(n) verificado cuidadosamente su nombre completo, el número de documento de identidad, y declara(n) que toda la información consignada es correcta, asumiendo la responsabilidad por cualquier inexactitud.");
  if (s.cNotiElec) h += nota("NOTIFICACIONES ELECTRÓNICAS.- El (los) compareciente(s) manifiesta(n) que SÍ da(n) su consentimiento, que se entiende concedido con la firma de la presente escritura, para ser notificado por medio electrónico sobre el estado del trámite ante la Oficina de Instrumentos Públicos, a través del correo electrónico: " + IF("cCorreoNotif", s.cCorreoNotif) + ".");
  if (s.cSarlaft) h += nota(R("SARLAFT — AUTORIZACIÓN DE TRATAMIENTO DE DATOS PERSONALES: la Notaría, como responsable que almacena y recolecta datos personales, requiere y obtiene la autorización del compareciente para recaudar, almacenar y usar los datos suministrados. STRADATA SEARCH: en cumplimiento de la Circular 1536 del 17 de septiembre de 2013 de la S.N.R. y del Artículo 17 de la Ley 282 de 1996, se consultó la información del (los) otorgante(s) en el programa STRADATA.", "Circular SNR 1536/2013 · Ley 1581/2012"));
  h += '<div data-sec="firmas" style="margin-top:26px"><div style="font-family:var(--sans);font-size:9px;color:var(--ink-faint);letter-spacing:.02em;margin-bottom:6px">VIENE DE LA HOJA DE PAPEL NOTARIAL NRO. ' + IF("cHojas", s.cHojas) + " DE LA ESCRITURA PÚBLICA NÚMERO " + esc(s.cNum) + " DE LA NOTARÍA DIECISÉIS DE MEDELLÍN. ——————</div>"
    + '<div style="text-align:center;font-family:var(--sans);font-size:10.5px;letter-spacing:.07em;color:var(--ink-soft);text-transform:uppercase;margin-bottom:2px">Firma del otorgante</div>'
    + '<div style="margin-top:18px"><div style="border-top:1px solid var(--ink);width:60%;margin-bottom:4px"></div>'
    + '<div style="font-family:var(--serif);font-weight:600;font-size:12.5px">' + esc(s.cApoNombre || "____________________________") + "</div>"
    + '<div style="font-family:var(--sans);font-size:10px;color:var(--ink)">C.C. ' + esc(s.cApoCC || "____________") + " · " + esc(s.cRepCargo) + " de " + esc(banco) + " — NIT " + esc(s.cBancoNit) + "</div>"
    + '<div style="font-family:var(--sans);font-size:10px;color:var(--ink-faint);margin-top:2px">Firma fuera de la sede (art. 12 Dcto 2148/1983) · Biometría: <span style="color:var(--line-strong)">___________</span></div></div>'
    + '<div style="margin-top:34px;text-align:center"><div style="border-top:1px solid var(--ink);width:55%;margin:0 auto 5px"></div><div style="font-family:var(--serif);font-weight:600;font-size:12.5px">' + esc(s.cNotario || "____________________") + '</div><div style="font-family:var(--sans);font-size:10.5px;color:var(--ink-soft)">Notari' + notEnd + " Dieciséis " + esc(s.cCalidad || "") + " de Medellín · Autoriza — Escritura Nro. " + esc(s.cNum) + "</div></div></div>";
  return h;
}

export function liquidarCanc(s: CancelacionState, tarifas: TarifaConfig = TARIFAS): { derNot: number; iva: number; recaudo: number; total: number } {
  const derNot = tarifas.derNotarialBase;
  const iva = Math.round(derNot * tarifas.iva);
  const recaudo = s.cRecaudo || 19300;
  return { derNot, iva, recaudo, total: derNot + iva + recaudo };
}

export function renderLiquidacionCanc(s: CancelacionState, tarifas: TarifaConfig = TARIFAS): string {
  const L = liquidarCanc(s, tarifas);
  let h = '<h3>Liquidación de gastos y tributos</h3><div class="resline">Tarifas ' + tarifas.anio + " · Notarial " + esc(tarifas.resNotarial) + "<br>" + (s.cSinCuantia ? "Acto sin cuantía (Ley 546/1999) — sin impuesto de registro con cuantía" : "Cancelación de hipoteca") + '</div><div class="tblw"><table><thead><tr><th>Concepto</th><th>Tarifa</th><th class="n">Valor</th><th>A cargo</th></tr></thead><tbody>';
  h += '<tr><td>Derechos notariales <span class="cite">' + esc(tarifas.resNotarial) + '</span></td><td class="who">Acto sin cuantía</td><td class="n">' + fmt(L.derNot) + '</td><td class="who">Interesado</td></tr>';
  h += '<tr><td>IVA</td><td class="who">19% sobre derechos</td><td class="n">' + fmt(L.iva) + '</td><td class="who">Interesado</td></tr>';
  h += '<tr><td>Recaudo Superintendencia y Fondo</td><td class="who">Tarifa fija S.N.R.</td><td class="n">' + fmt(L.recaudo) + '</td><td class="who">Interesado</td></tr>';
  h += '<tr class="tot"><td colspan="2">Total a pagar</td><td class="n">' + fmt(L.total) + "</td><td></td></tr></tbody></table></div>";
  h += '<div class="note">La cancelación de hipoteca de vivienda es acto sin cuantía (art. 23 Ley 546/1999): no causa impuesto de registro con cuantía ni derechos notariales proporcionales. Validar contra la resolución oficial del año.</div>';
  return h;
}

export function evaluarCanc(s: CancelacionState): EvaluacionItem[] {
  const it: EvaluacionItem[] = [];
  if (!s.cMatricula.trim()) it.push({ t: "crit", h: "Inmueble sin folio de matrícula", p: "Sin la matrícula inmobiliaria el registro no puede tomar razón de la cancelación.", n: "art. 8 · Ley 1579/2012" });
  if (!s.cHipEP.trim() || !s.cHipFecha.trim() || !s.cHipNotaria.trim() || !s.cHipRegFecha.trim()) it.push({ t: "crit", h: "Hipoteca a cancelar no identificada", p: "Falta la E.P. de constitución, su notaría o la fecha de registro: sin el tracto registral el registro devuelve el título.", n: "Ley 1579/2012" });
  if (!s.cApoCC.trim()) it.push({ t: "crit", h: "Compareciente sin identificar", p: "Falta el documento de identidad del apoderado/representante que firma por el banco.", n: "Dcto 960/1970" });
  if (s.cRepTipo === "apoderado") {
    if (!s.cPoderEP.trim()) it.push({ t: "warn", h: "Poder del apoderado sin identificar", p: "Indicar la E.P. del poder especial que se protocoliza.", n: "Dcto 1069/2015" });
    else it.push({ t: "obl", h: "Personería del acreedor (apoderado)", p: "Poder especial identificado y protocolizado.", n: "Dcto 1069/2015" });
  } else {
    it.push({ t: "obl", h: "Personería del acreedor (rep. legal)", p: "Se protocoliza el certificado de existencia y representación legal.", n: "C. Comercio" });
  }
  it.push({ t: "obl", h: "Declaración expresa de cancelación", p: "El acreedor, titular del crédito, cancela el gravamen (cláusula tercera).", n: "art. 2457 C.C." });
  it.push({ t: "obl", h: "Advertencia de registro (2 meses)", p: "NOTA 2 incluida — término perentorio e intereses moratorios.", n: "Ley 1579/2012" });
  if (s.cNotiElec) it.push({ t: "ok", h: "Notificaciones electrónicas", p: "NOTA 4 con consentimiento y correo de notificación.", n: "Dcto 1069/2015" });
  if (s.cSarlaft) it.push({ t: "obl", h: "SARLAFT / tratamiento de datos", p: "NOTA 5 con autorización de datos y consulta STRADATA.", n: "Circular SNR 1536/2013 · Ley 1581/2012" });
  else it.push({ t: "warn", h: "Falta la NOTA de SARLAFT", p: "El tratamiento de datos y la consulta STRADATA son mínimos exigibles; conviene incluirla.", n: "Circular SNR 1536/2013 · Ley 1581/2012" });
  if (s.cSinCuantia) it.push({ t: "ok", h: "Acto sin cuantía (vivienda)", p: "Cancelación de crédito de vivienda: acto sin cuantía (Ley 546/1999).", n: "art. 23 · Ley 546/1999" });
  else it.push({ t: "warn", h: "Acto con cuantía", p: "No marcado como vivienda: se liquidará con cuantía. Verificar la naturaleza del crédito.", n: "art. 23 · Ley 546/1999" });
  it.push({ t: "ok", h: "Firma fuera de la sede", p: "NOTA 1 — el apoderado del banco suscribe en su despacho (art. 12 Dcto 2148/1983).", n: "art. 12 · Dcto 2148/1983" });
  it.push({ t: "obl", h: "Autorización notarial", p: "Constancia de autorización de la Escritura Nro. " + esc(s.cNum) + " e imposición de la fe pública.", n: "Dcto 960/1970" });
  if (!s.cNum.trim()) it.push({ t: "warn", h: "Falta el número de escritura", p: "La autorización y las copias requieren el número de instrumento del protocolo.", n: "Dcto 960/1970" });
  return it;
}

function cumplimiento(items: EvaluacionItem[]): Resultado["cumplimiento"] {
  let cumple = 0;
  let advertencia = 0;
  let bloqueante = 0;
  items.forEach((i) => {
    if (i.t === "crit") bloqueante++;
    else if (i.t === "warn") advertencia++;
    else cumple++;
  });
  const order: Record<CumplimientoTipo, number> = { crit: 0, warn: 1, obl: 2, ok: 3 };
  const sorted = [...items].sort((a, b) => order[a.t] - order[b.t]);
  return {
    items: sorted.map((i) => ({ tipo: i.t, titulo: i.h, detalle: i.p, norma: i.n })),
    tiles: { cumple, advertencia, bloqueante },
  };
}

function estadoDesdeCrit(crit: number): { ok: boolean; texto: string } {
  if (crit > 0) return { ok: false, texto: "× No se puede otorgar aún — " + crit + " bloqueante" + (crit > 1 ? "s" : "") + " por resolver." };
  return { ok: true, texto: "✓ Lista para revisión y firma del notario. Sin bloqueantes." };
}

function asCompraventaState(state: CaseState): CompraventaState {
  return state as CompraventaState;
}

function asCancelacionState(state: CaseState): CancelacionState {
  return state as CancelacionState;
}

export function generar(acto: ActoCode, state: CaseState, corpus?: MotorCorpus): Resultado {
  const tarifas = tarifasConfig(corpus);
  if (acto === "cancelacion") {
    const s = asCancelacionState(state);
    const items = evaluarCanc(s);
    const cump = cumplimiento(items);
    return {
      html: renderCancelacion(s, tarifas),
      liquidacionHtml: renderLiquidacionCanc(s, tarifas),
      cumplimiento: cump,
      estado: estadoDesdeCrit(cump.tiles.bloqueante),
    };
  }
  const base = asCompraventaState(state);
  const s = { ...base, credito: acto === "hipoteca", pepAny: base.pep || base.V.concat(base.C).some((p) => p.pep) };
  const items = evaluar(s);
  const cump = cumplimiento(items);
  return {
    html: renderEscritura(s, tarifas),
    liquidacionHtml: renderLiquidacion(s, tarifas),
    cumplimiento: cump,
    estado: estadoDesdeCrit(cump.tiles.bloqueante),
  };
}
