"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import {
  AlertCircle, CheckCircle2, ChevronRight, ExternalLink,
  FileText, HelpCircle, Loader2, Plus, Upload, X,
} from "lucide-react";
import {
  analyzeMinuta, detectMarkedTemplate, generateMinuta, generateMarkedTemplate, emptyPersona,
  type MinutaAnalisisResult, type MinutaPersona,
  type MinutaInmueble, type MinutaNotaria, type MinutaValor, type MinutaDatos,
  type MinutaAdquisicion, type MarkedTemplateDetectResult, type MarkedTemplateField, type MinutaGenerarResult,
} from "@/lib/minuta";
import { TIPOS_DOCUMENTO, NOTAS_LINDEROS, ESTADOS_CIVILES_GENERALES, PAISES, getEstadosCiviles, getNacionalidadesPorGenero, isGenderField } from "@/lib/listas-notariales";
import { isPlaceholderDropdownValue } from "@/lib/dropdown-options";
import { DEPARTAMENTOS_COLOMBIA, getMunicipiosByDepartamento, getDepartamentoByMunicipio } from "@/lib/colombia-geo";
import { getCurrentUser } from "@/lib/api";
import { AiProgressModal, type AiStep } from "@/components/ui/ai-progress-modal";
import { MinutasTour, type TourStep } from "@/components/minutas/minutas-tour";

// ─── Constants ────────────────────────────────────────────────────────────────

const IA_STEPS = ["Subir documento", "Revisar personas", "Generar"];
const MARKED_STEPS = ["Subir documento", "Diligenciar campos", "Generar"];

const GENERO_OPTIONS = [
  { value: "M", label: "Masculino (M)" },
  { value: "F", label: "Femenino (F)" },
  { value: "J", label: "Juridica (J)" },
];

const GENTILICIOS_M_A_F: Record<string, string> = {
  "colombiano": "colombiana",
  "venezolano": "venezolana",
  "ecuatoriano": "ecuatoriana",
  "peruano": "peruana",
  "boliviano": "boliviana",
  "chileno": "chilena",
  "argentino": "argentina",
  "uruguayo": "uruguaya",
  "paraguayo": "paraguaya",
  "brasileño": "brasileña",
  "mexicano": "mexicana",
  "español": "española",
  "estadounidense": "estadounidense",
  "italiano": "italiana",
  "francés": "francesa",
  "alemán": "alemana",
  "chino": "china",
  "cubano": "cubana",
  "dominicano": "dominicana",
  "panameño": "panameña",
  "costarricense": "costarricense",
  "hondureño": "hondureña",
  "salvadoreño": "salvadoreña",
  "guatemalteco": "guatemalteca",
  "nicaragüense": "nicaragüense",
};
const GENTILICIOS_F_A_M = Object.fromEntries(
  Object.entries(GENTILICIOS_M_A_F).map(([m, f]) => [f, m])
);

// NotariaEdit extiende MinutaNotaria con fecha_otorgamiento (viene de datos.fechas)
type NotariaEdit = MinutaNotaria & { fecha_otorgamiento: string | null };

const EMPTY_INMUEBLE: MinutaInmueble = {
  tipo: null, numero: null, matricula_inmobiliaria: null,
  conjunto_o_edificio: null, municipio: null, departamento: null,
  coeficiente_copropiedad: null, linderos: null,
  cedula_catastral: null, codigo_catastral: null,
  area_construida: null, area_privada: null, area_total: null,
  direccion: null, barrio: null, piso: null,
  nota_linderos: null, propiedad_horizontal: null,
};
const EMPTY_NOTARIA: NotariaEdit = {
  nombre_notaria: null, municipio_notaria: null,
  numero_escritura: null, fecha_otorgamiento: null,
};
const EMPTY_ADQUISICION: MinutaAdquisicion = {
  forma_adquisicion: null, escritura_numero: null, fecha_escritura_anterior: null,
  notaria_anterior: null, municipio_notaria_anterior: null, vendedor_original: null,
};

// ─── Número a letras (español, pesos moneda corriente) ───────────────────────

const UNIDADES = ["", "UN", "DOS", "TRES", "CUATRO", "CINCO", "SEIS", "SIETE", "OCHO", "NUEVE",
  "DIEZ", "ONCE", "DOCE", "TRECE", "CATORCE", "QUINCE", "DIECISÉIS", "DIECISIETE", "DIECIOCHO", "DIECINUEVE"];
const DECENAS = ["", "", "VEINTE", "TREINTA", "CUARENTA", "CINCUENTA", "SESENTA", "SETENTA", "OCHENTA", "NOVENTA"];
const CENTENAS = ["", "CIENTO", "DOSCIENTOS", "TRESCIENTOS", "CUATROCIENTOS", "QUINIENTOS",
  "SEISCIENTOS", "SETECIENTOS", "OCHOCIENTOS", "NOVECIENTOS"];

function centenas(n: number): string {
  if (n === 100) return "CIEN";
  const c = Math.floor(n / 100);
  const resto = n % 100;
  const partes: string[] = [];
  if (c > 0) partes.push(CENTENAS[c]);
  if (resto > 0 && resto < 20) {
    partes.push(UNIDADES[resto]);
  } else if (resto >= 20) {
    const d = Math.floor(resto / 10);
    const u = resto % 10;
    if (u === 0) partes.push(DECENAS[d]);
    else partes.push(`${DECENAS[d]} Y ${UNIDADES[u]}`);
  }
  return partes.join(" ");
}

function numeroALetras(n: number): string {
  return numeroALetrasConSufijo(n, "PESOS MONEDA CORRIENTE");
}

function numeroALetrasConSufijo(n: number, suffix: string): string {
  if (n === 0) return `CERO ${suffix}`;
  const partes: string[] = [];
  const miles_millones = Math.floor(n / 1_000_000_000);
  const millones = Math.floor((n % 1_000_000_000) / 1_000_000);
  const miles = Math.floor((n % 1_000_000) / 1_000);
  const resto = n % 1_000;

  if (miles_millones > 0) {
    const t = centenas(miles_millones);
    partes.push(miles_millones === 1 ? "MIL MILLONES" : `${t} MIL MILLONES`);
  }
  if (millones > 0) {
    const t = centenas(millones);
    partes.push(millones === 1 ? "UN MILLÓN" : `${t} MILLONES`);
  }
  if (miles > 0) {
    const t = centenas(miles);
    partes.push(miles === 1 ? "MIL" : `${t} MIL`);
  }
  if (resto > 0) {
    partes.push(centenas(resto));
  }
  return partes.join(" ") + ` ${suffix}`;
}

// ─── Step indicator ───────────────────────────────────────────────────────────

function StepBar({ current, labels }: { current: number; labels: string[] }) {
  return (
    <div className="flex items-center gap-0 mb-8">
      {labels.map((label, i) => (
        <div key={i} className="flex items-center gap-0 flex-1 last:flex-none">
          <div className="flex flex-col items-center gap-1.5">
            <div
              className={[
                "w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold transition-all",
                i < current
                  ? "bg-accent text-primary"
                  : i === current
                  ? "bg-primary text-white"
                  : "bg-panel-soft text-soft border border-line",
              ].join(" ")}
            >
              {i < current ? <CheckCircle2 size={16} /> : i + 1}
            </div>
            <span
              className={[
                "text-xs whitespace-nowrap",
                i === current ? "text-primary font-semibold" : "text-soft",
              ].join(" ")}
            >
              {label}
            </span>
          </div>
          {i < labels.length - 1 && (
            <div
              className={[
                "flex-1 h-0.5 mx-2 mb-5 rounded",
                i < current ? "bg-accent" : "bg-line",
              ].join(" ")}
            />
          )}
        </div>
      ))}
    </div>
  );
}

// ─── Upload zone ──────────────────────────────────────────────────────────────

function UploadZone({
  file,
  isDragging,
  onFile,
  onDragOver,
  onDragLeave,
  onDrop,
  onClear,
}: {
  file: File | null;
  isDragging: boolean;
  onFile: (f: File) => void;
  onDragOver: (e: React.DragEvent) => void;
  onDragLeave: () => void;
  onDrop: (e: React.DragEvent) => void;
  onClear: () => void;
}) {
  const inputRef = useRef<HTMLInputElement>(null);

  if (file) {
    return (
      <div className="ep-card-muted rounded-2xl p-5 flex items-center gap-4">
        <div className="w-11 h-11 rounded-xl bg-success-bg flex items-center justify-center shrink-0">
          <FileText size={20} className="text-emerald-600" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="font-semibold text-sm text-ink truncate">{file.name}</p>
          <p className="text-xs text-soft mt-0.5">
            {(file.size / 1024).toFixed(0)} KB · .docx listo para analizar
          </p>
        </div>
        <button
          onClick={onClear}
          className="w-8 h-8 rounded-lg hover:bg-surface-alt flex items-center justify-center transition-colors"
          aria-label="Quitar archivo"
        >
          <X size={16} className="text-soft" />
        </button>
      </div>
    );
  }

  return (
    <label
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onDrop={onDrop}
      className={[
        "flex flex-col items-center justify-center gap-3 rounded-2xl border-2 border-dashed p-10 cursor-pointer transition-all",
        isDragging
          ? "border-primary bg-panel-highlight"
          : "border-line-strong hover:border-primary hover:bg-panel-soft",
      ].join(" ")}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".docx"
        className="hidden"
        onChange={(e) => {
          const f = e.target.files?.[0];
          if (f) onFile(f);
        }}
      />
      <div className="w-14 h-14 rounded-2xl bg-panel-soft flex items-center justify-center">
        <Upload size={24} className="text-primary" />
      </div>
      <div className="text-center">
        <p className="font-semibold text-ink">
          Arrastra un archivo .docx aqui
        </p>
        <p className="text-sm text-muted mt-1">
          o{" "}
          <span className="text-primary underline underline-offset-2">
            haz clic para seleccionar
          </span>
        </p>
      </div>
      <p className="text-xs text-soft">Solo archivos .docx - max 20 MB</p>
    </label>
  );
}

// ─── Analysis summary card ────────────────────────────────────────────────────

function AnalysisSummary({ result }: { result: MinutaAnalisisResult }) {
  const { modo_detectado, confianza_modo, datos, costo_usd } = result;
  const isB2 = modo_detectado === "B2";

  return (
    <div className="ep-card rounded-2xl p-5 mt-5 space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-3">
          <span
            className={[
              "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold tracking-wide",
              isB2 ? "bg-success-bg text-emerald-700" : "bg-blue-50 text-blue-700",
            ].join(" ")}
          >
            <span className={["w-2 h-2 rounded-full", isB2 ? "bg-emerald-500" : "bg-blue-500"].join(" ")} />
            {isB2 ? "B2 - Minuta diligenciada" : "B1 - Plantilla en blanco"}
          </span>
          <span className="text-xs text-soft">
            Confianza {Math.round(confianza_modo * 100)}%
          </span>
        </div>
        <span className="text-xs text-soft">
          Costo: ${costo_usd.toFixed(4)} USD · {result.tokens.total_tokens.toLocaleString()} tokens
        </span>
      </div>

      <div className="grid grid-cols-3 gap-3 text-center">
        {[
          { label: "Personas", value: datos.personas.length },
          { label: "Valores", value: datos.valores.length },
          { label: "Actos", value: datos.actos.length },
        ].map(({ label, value }) => (
          <div key={label} className="ep-card-muted rounded-xl p-3">
            <p className="text-xl font-bold text-primary">{value}</p>
            <p className="text-xs text-soft mt-0.5">{label}</p>
          </div>
        ))}
      </div>

      {datos.actos.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-muted uppercase tracking-wider mb-2">
            Actos detectados
          </p>
          <div className="flex flex-wrap gap-1.5">
            {datos.actos.map((acto) => (
              <span key={acto} className="ep-pill text-xs px-2.5 py-1 rounded-full">
                {acto.replace(/_/g, " ")}
              </span>
            ))}
          </div>
        </div>
      )}

      {datos.inmueble?.matricula_inmobiliaria && (
        <div className="ep-card-muted rounded-xl p-3 text-sm">
          <span className="font-medium text-ink">Inmueble: </span>
          <span className="text-muted">
            {[
              datos.inmueble.conjunto_o_edificio,
              datos.inmueble.tipo,
              datos.inmueble.numero && `Nro. ${datos.inmueble.numero}`,
              datos.inmueble.municipio,
              datos.inmueble.matricula_inmobiliaria && `Matricula ${datos.inmueble.matricula_inmobiliaria}`,
            ]
              .filter(Boolean)
              .join(" · ")}
          </span>
        </div>
      )}
    </div>
  );
}

function groupMarkedFields(fields: MarkedTemplateField[]) {
  const groups = new Map<string, MarkedTemplateField[]>();
  fields.forEach((field) => {
    const bucket = groups.get(field.section) ?? [];
    bucket.push(field);
    groups.set(field.section, bucket);
  });
  return Array.from(groups.entries()).map(([section, sectionFields]) => ({ section, fields: sectionFields }));
}

type MarkedSectionId =
  | "basic"
  | "buyers"
  | "values"
  | "decisions"
  | "protocol"
  | "liquidation"
  | "others";

const MARKED_BUYER_NOTE_KEYS = new Set([
  "nacionalidad_comprador",
  "estado_civil_comprador",
  "profesion_u_oficio",
  "actividad_economica_comprador",
]);

const MARKED_BASIC_ORDER = [
  "numero_escritura",
  "numero_apartamento",
  "numero_matricula",
  "numero_de_piso",
  "linderos",
  "coeficiente_copropiedad",
  "fecha_celebracion_de_la_promesa_compraventa",
];

const MARKED_VALUE_ORDER = [
  "valor_de_la_venta_en_numeros",
  "valor_apartamento_en_letras",
  "en_numeros_cuota_inicial",
  "en_letras_cuota_inicial",
  "origen_cuota_inicial",
  "valor_del_acto_de_la_hipoteca",
  "valor_del_acto_de_la_hipoteca_en_letras",
];

const MARKED_DECISION_ORDER = [
  "inmueble_sera_su_casa",
  "tiene_inmueble_afectado",
  "afectacion_cumple_ley_258",
  "cumple_ley_258",
  "queda_afectado",
  "constitucion_patrimonio_de_familia",
  "acepta_notificacion_electronica",
  "nombre_pareja_o_conyuge",
  "numero_documento_pareja_o_conyuge",
  "celular_pareja_o_conyuge",
  "direccion_pareja_o_conyuge",
  "email_pareja_o_conyuge",
  "pareja_o_conyuge",
];

const MARKED_PROTOCOL_ORDER = [
  "dia_elaboracion_escritura",
  "mes_elaboracion_escritura",
  "protocolista",
  "consecutivo_hojas_papel_notarial",
];

const MARKED_LIQUIDATION_ORDER = [
  "derechos_notariales",
  "iva",
  "aporte_superintendencia",
  "fondo_nacional_notariado",
];

const MARKED_MONTH_LABELS = [
  { value: "1", label: "Enero" },
  { value: "2", label: "Febrero" },
  { value: "3", label: "Marzo" },
  { value: "4", label: "Abril" },
  { value: "5", label: "Mayo" },
  { value: "6", label: "Junio" },
  { value: "7", label: "Julio" },
  { value: "8", label: "Agosto" },
  { value: "9", label: "Septiembre" },
  { value: "10", label: "Octubre" },
  { value: "11", label: "Noviembre" },
  { value: "12", label: "Diciembre" },
];

const MARKED_DECISION_OPTIONS = [
  { value: "", label: "Selecciona..." },
  { value: "Sí", label: "Sí" },
  { value: "No", label: "No" },
  { value: "No aplica", label: "No aplica" },
  { value: "Pendiente", label: "Pendiente" },
];

const JAGGUA_BANCO_BOGOTA_QA_VALUES: Record<string, string> = {
  numero_escritura: "000",
  numero_apartamento: "804",
  numero_matricula: "001-1528731",
  matricula_inmobiliaria: "001-1528731",
  numero_matricula_inmobiliaria: "001-1528731",
  nombre_comprador: "JUAN CAMILO VASQUEZ MIRA",
  nombre_comprador_1: "JUAN CAMILO VASQUEZ MIRA",
  comprador_1_nombre: "JUAN CAMILO VASQUEZ MIRA",
  nombre_del_comprador_1: "JUAN CAMILO VASQUEZ MIRA",
  tipo_documento_comprador: "C.C",
  tipo_documento_comprador_1: "C.C",
  numero_documento_comprador: "1.037.657.164",
  numero_documento_comprador_1: "1.037.657.164",
  comprador_es_hombre_o_mujer: "HOMBRE",
  comprador_1_es_hombre_o_mujer: "HOMBRE",
  nombre_comprador_2: "",
  tipo_documento_comprador_2: "",
  numero_documento_comprador_2: "",
  comprador_2_es_hombre_o_mujer: "",
  nacionalidad_comprador: "colombiano",
  nacionalidad_comprador_1: "colombiano",
  nacionalidad_comprador_2: "",
  municipio_domicilio_comprador: "Envigado Antioquia",
  municipio_domicilio_comprador_1: "Envigado Antioquia",
  municipio_domicilio_comprador_2: "",
  seleccione_si_comprador_esta_de_transito: "de tránsito por este municipio de Caldas, Antioquia,",
  seleccione_si_comprador_1_esta_de_transito: "de tránsito por este municipio de Caldas, Antioquia,",
  seleccione_si_comprador_2_esta_de_transito: "",
  estado_civil_comprador: "soltero sin unión marital de hecho",
  estado_civil_comprador_1: "soltero sin unión marital de hecho",
  estado_civil_comprador_2: "",
  profesion_u_oficio: "empleado",
  profesion_u_oficio_comprador_2: "",
  actividad_economica_comprador: "empleado",
  actividad_economica_comprador_2: "",
  numero_de_piso: "octavo",
  dia_elaboracion_escritura: "nueve (9)",
  mes_elaboracion_escritura: "marzo",
  valor_de_la_venta_en_numeros: "212.600.000",
  valor_venta_numeros: "212.600.000",
  valor_de_la_venta: "212.600.000",
  valor_venta: "212.600.000",
  valor_apartamento_en_letras: "",
  en_numeros_cuota_inicial: "63.040.480",
  en_letras_cuota_inicial: "",
  valor_del_acto_de_la_hipoteca: "149.559.520",
  valor_del_acto_de_la_hipoteca_en_letras: "",
  origen_cuota_inicial: "recursos propios",
  fecha_celebracion_de_la_promesa_compraventa: "19 de noviembre de 2024",
  direccion_comprador: "CARRERA 25 #39 SUR 15, URBANIZACIÓN VITTA APTO 1203 ENVIGADO",
  direccion_comprador_1: "CARRERA 25 #39 SUR 15, URBANIZACIÓN VITTA APTO 1203 ENVIGADO",
  direccion_comprador_2: "",
  celular_comprador: "3003575071",
  celular_comprador_1: "3003575071",
  celular_comprador_2: "",
  email_comprador: "JCAMILOVASQUEZM@GMAIL.COM",
  email_comprador_1: "JCAMILOVASQUEZM@GMAIL.COM",
  email_comprador_2: "",
  inmueble_sera_su_casa: "No",
  tiene_inmueble_afectado: "No",
  afectacion_cumple_ley_258: "No",
  queda_afectado: "No",
  constitucion_patrimonio_de_familia: "Sí",
  acepta_notificacion_electronica: "Sí",
  coeficiente_copropiedad: "0,0000",
  derechos_notariales: "0",
  iva: "0",
  aporte_superintendencia: "0",
  fondo_nacional_notariado: "0",
  consecutivo_hojas_papel_notarial: "000000",
  pareja_o_conyuge: "",
  nombre_pareja_o_conyuge: "",
  numero_documento_pareja_o_conyuge: "",
  linderos:
    "con un área privada construida de 44,76 metros cuadrados, un área total de 49,24 metros cuadrados, una altura de 2,30 metros, cuyo perímetro se encuentra comprendido entre los puntos 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22 y 1 punto de partida, puntos tomados del Plano Nro. A-001, que linda por el nadir, Con el Séptimo piso, por el cenit, Con el Noveno piso. Nomenclatura Carrera 054 No. 153 S - 061 0804.",
};

const JAGGUA_BANCO_BOGOTA_QA_VALUES_NORMALIZED = Object.fromEntries(
  Object.entries(JAGGUA_BANCO_BOGOTA_QA_VALUES).map(([key, value]) => [normalizeMarkedKey(key), value])
);

const MARKED_DECISION_SELECT_KEYS = new Set([
  "inmueble_sera_su_casa",
  "tiene_inmueble_afectado",
  "afectacion_cumple_ley_258",
  "cumple_ley_258",
  "queda_afectado",
  "constitucion_patrimonio_de_familia",
  "acepta_notificacion_electronica",
]);

const MARKED_DECISION_TEXT_KEYS = new Set([
  "nombre_pareja_o_conyuge",
  "numero_documento_pareja_o_conyuge",
  "celular_pareja_o_conyuge",
  "direccion_pareja_o_conyuge",
  "email_pareja_o_conyuge",
  "pareja_o_conyuge",
]);

const MARKED_NATIONALITY_KEYWORDS = ["nacionalidad", "pais", "país", "pais_expedicion", "país_expedicion"];
const MARKED_MUNICIPALITY_KEYWORDS = [
  "municipio",
  "ciudad",
  "domicilio",
  "municipio_domicilio",
  "municipio_notaria",
  "ciudad_expedicion",
  "lugar_expedicion",
];

const MARKED_BUYER_LABELS: Record<1 | 2 | 3, string> = {
  1: "Comprador 1",
  2: "Comprador 2",
  3: "Comprador 3",
};

function normalizeMarkedKey(value: string): string {
  return normalizeMarkedText(value);
}

function markedFieldKey(field: MarkedTemplateField): string {
  return normalizeMarkedKey(field.key);
}

function matchesMarkedKey(field: MarkedTemplateField, keys: string[]): boolean {
  const blob = markedFieldKey(field);
  return keys.some((key) => blob === normalizeMarkedKey(key) || blob.includes(normalizeMarkedKey(key)));
}

function getMarkedBuyerIndex(field: MarkedTemplateField): 1 | 2 | 3 | null {
  const blob = markedFieldKey(field);
  if (blob.includes("comprador_3") || blob.includes("comprador3")) return 3;
  if (blob.includes("comprador_2") || blob.includes("comprador2")) return 2;
  if (blob.includes("comprador_1") || blob.includes("comprador1")) return 1;
  if (blob.includes("comprador")) return 1;
  return null;
}

function isMarkedBuyerSharedField(field: MarkedTemplateField): boolean {
  return MARKED_BUYER_NOTE_KEYS.has(markedFieldKey(field)) || matchesMarkedKey(field, ["comprador_es_hombre_o_mujer"]);
}

function getMarkedSectionId(field: MarkedTemplateField): MarkedSectionId {
  if (isMarkedPartnerDescriptorField(field)) return "decisions";
  if (isMarkedGenderField(field)) {
    const genderRoleKey = getMarkedGenderFieldRoleKey(field.key);
    if (genderRoleKey?.startsWith("comprador")) return "buyers";
  }
  if (matchesMarkedKey(field, MARKED_BASIC_ORDER)) return "basic";
  if (getMarkedBuyerIndex(field) != null || isMarkedBuyerSharedField(field)) return "buyers";
  if (matchesMarkedKey(field, MARKED_VALUE_ORDER)) return "values";
  if (matchesMarkedKey(field, MARKED_DECISION_ORDER)) return "decisions";
  if (matchesMarkedKey(field, MARKED_PROTOCOL_ORDER)) return "protocol";
  if (matchesMarkedKey(field, MARKED_LIQUIDATION_ORDER)) return "liquidation";
  if (["basic", "buyers", "values", "decisions", "protocol", "liquidation", "others"].includes(field.section)) {
    return field.section as MarkedSectionId;
  }
  return "others";
}

function sortMarkedFieldsByOrder(fields: MarkedTemplateField[], order: string[]) {
  const orderIndex = new Map(order.map((key, index) => [normalizeMarkedKey(key), index]));
  return [...fields].sort((a, b) => {
    const aIndex = orderIndex.get(markedFieldKey(a));
    const bIndex = orderIndex.get(markedFieldKey(b));
    if (aIndex != null && bIndex != null) return aIndex - bIndex;
    if (aIndex != null) return -1;
    if (bIndex != null) return 1;
    return 0;
  });
}

function getMarkedLetterTargetKey(field: MarkedTemplateField): string | null {
  const key = markedFieldKey(field);
  if (key === "valor_de_la_venta_en_numeros") return "valor_apartamento_en_letras";
  if (key === "en_numeros_cuota_inicial") return "en_letras_cuota_inicial";
  if (key === "valor_del_acto_de_la_hipoteca") return "valor_del_acto_de_la_hipoteca_en_letras";
  if (key.endsWith("_en_numeros")) return key.replace(/_en_numeros$/, "_en_letras");
  return null;
}

function getMarkedMoneySourceKeyForLetter(field: MarkedTemplateField): string | null {
  const key = markedFieldKey(field);
  if (key === "valor_apartamento_en_letras") return "valor_de_la_venta_en_numeros";
  if (key === "en_letras_cuota_inicial") return "en_numeros_cuota_inicial";
  if (key === "valor_del_acto_de_la_hipoteca_en_letras") return "valor_del_acto_de_la_hipoteca";
  if (key.endsWith("_en_letras")) return key.replace(/_en_letras$/, "_en_numeros");
  return null;
}

function extractMarkedMoneyDigits(value: string | number | null | undefined): string {
  return String(value ?? "").replace(/\D/g, "");
}

function getMarkedLettersSuffix(moneyFieldKey: string, letterFieldKey: string): string {
  const normalizedMoneyKey = normalizeMarkedKey(moneyFieldKey);
  const normalizedLetterKey = normalizeMarkedKey(letterFieldKey);
  if (
    normalizedMoneyKey === "valor_de_la_venta_en_numeros" ||
    normalizedMoneyKey === "valor_de_la_venta" ||
    normalizedMoneyKey === "valor_venta_numeros" ||
    normalizedMoneyKey === "valor_venta" ||
    normalizedLetterKey === "valor_apartamento_en_letras"
  ) {
    return "PESOS MONEDA LEGAL";
  }
  return "PESOS";
}

function getMarkedLettersFromMoneyValue(value: string | number | null | undefined, moneyFieldKey: string, letterFieldKey: string): string {
  const digits = extractMarkedMoneyDigits(value);
  if (!digits) return "";
  const amount = Number(digits);
  if (!Number.isFinite(amount) || amount <= 0) return "";
  return numeroALetrasConSufijo(amount, getMarkedLettersSuffix(moneyFieldKey, letterFieldKey));
}

function getMarkedBuyerFields(fields: MarkedTemplateField[], buyerIndex: 1 | 2 | 3) {
  const exactBuyerFields = fields.filter((field) => getMarkedBuyerIndex(field) === buyerIndex);
  const sharedBuyerOneFields = buyerIndex === 1 ? fields.filter((field) => isMarkedBuyerSharedField(field)) : [];
  const merged = [...sharedBuyerOneFields, ...exactBuyerFields];
  const seen = new Set<string>();
  return merged.filter((field) => {
    if (seen.has(field.key)) return false;
    seen.add(field.key);
    return true;
  });
}

type MarkedGender = "M" | "F" | "J";
type MarkedFieldKind =
  | "text"
  | "textarea"
  | "date"
  | "day"
  | "month"
  | "year"
  | "money"
  | "stateCivil"
  | "gender"
  | "typeDocument"
  | "decision";

const MARKED_GENDER_OPTIONS = [
  { value: "HOMBRE", label: "HOMBRE" },
  { value: "MUJER", label: "MUJER" },
];

const MARKED_GENERAL_ESTADOS_CIVILES = ESTADOS_CIVILES_GENERALES;

function normalizeMarkedText(value: string): string {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "");
}

function markedFieldBlob(field: MarkedTemplateField): string {
  return normalizeMarkedText([field.key, field.label, field.section].join(" "));
}

function isMarkedField(field: MarkedTemplateField, terms: string[]): boolean {
  const blob = markedFieldBlob(field);
  return terms.some((term) => blob.includes(normalizeMarkedText(term)));
}

function isMarkedStateCivilField(field: MarkedTemplateField): boolean {
  return isMarkedField(field, ["estado_civil", "estado civil"]);
}

function isMarkedGenderField(field: MarkedTemplateField): boolean {
  return isGenderField(field.key);
}

function isMarkedDateField(field: MarkedTemplateField): boolean {
  return isMarkedField(field, ["fecha", "dia_elaboracion", "mes_elaboracion", "ano_elaboracion", "año_elaboracion"]);
}

function isMarkedDayField(field: MarkedTemplateField): boolean {
  return isMarkedField(field, ["dia_elaboracion"]);
}

function isMarkedMonthField(field: MarkedTemplateField): boolean {
  return isMarkedField(field, ["mes_elaboracion"]);
}

function isMarkedYearField(field: MarkedTemplateField): boolean {
  return isMarkedField(field, ["ano_elaboracion", "año_elaboracion"]);
}

function isMarkedTypeDocumentField(field: MarkedTemplateField): boolean {
  const blob = markedFieldBlob(field);
  return [
    "tipo_documento",
    "tipo documento",
    "tipo_de_documento",
  ].some((keyword) => blob.includes(normalizeMarkedText(keyword)));
}

function isMarkedMoneyField(field: MarkedTemplateField): boolean {
  return isMarkedField(field, [
    "valor",
    "precio",
    "cuantia",
    "cuantía",
    "cuota",
    "avaluo",
    "avalúo",
    "retencion",
    "retención",
    "derechos",
    "iva",
    "aporte",
    "fondo",
    "impuesto",
    "notariado",
    "superintendencia",
    "transferencia",
    "hipoteca",
  ]);
}

function isMarkedLettersField(field: MarkedTemplateField): boolean {
  return isMarkedField(field, ["en_letras", "letras"]);
}

function isMarkedPartnerDescriptorField(field: MarkedTemplateField): boolean {
  const blob = [field.key, field.label, ...(field.raw_markers ?? [])].join(" ").toLowerCase();
  return [
    "conyuge",
    "companero",
    "companera",
    "pareja",
  ].some((keyword) => blob.includes(keyword));
}

const MARKED_GENDER_DEPENDENT_PREFIXES = [
  "nacionalidad",
  "estado_civil",
] as const;

function getMarkedGenderDependentRoleKey(fieldKey: string): string | null {
  const key = normalizeMarkedKey(fieldKey);
  if (!key) return null;

  for (const prefix of MARKED_GENDER_DEPENDENT_PREFIXES) {
    if (key.startsWith(`${prefix}_`)) {
      return key.slice(prefix.length + 1);
    }
  }

  return null;
}

function getMarkedGenderFieldRoleKey(fieldKey: string): string | null {
  const key = normalizeMarkedKey(fieldKey);
  if (!key) return null;

  const matcher = key.match(/^(?:genero|sexo)_(.+)$/)
    ?? key.match(/^(.+)_(?:genero|sexo)$/)
    ?? key.match(/^(.+)_es_hombre_o_mujer$/)
    ?? key.match(/^(.+)_es_hombre_0_mujer$/)
    ?? key.match(/^es_hombre_o_mujer$/)
    ?? key.match(/^es_hombre_0_mujer$/);

  if (!matcher) return null;
  return matcher[1] ?? null;
}

function humanizeMarkedRoleKey(roleKey: string): string {
  return roleKey
    .split("_")
    .filter(Boolean)
    .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
    .join(" ");
}

function getMarkedGenderFieldCandidatesForRole(roleKey: string | null): string[] {
  const normalizedRole = normalizeMarkedKey(roleKey ?? "");
  const variants = new Set<string>();

  if (normalizedRole) {
    variants.add(normalizedRole);

    if (normalizedRole === "comprador") {
      variants.add("comprador_1");
    } else if (normalizedRole === "comprador_1") {
      variants.add("comprador");
    }
  }

  const candidates: string[] = [];
  for (const variant of variants) {
    candidates.push(
      `${variant}_es_hombre_o_mujer`,
      `${variant}_es_hombre_0_mujer`,
      `genero_${variant}`,
      `${variant}_genero`,
      `${variant}_sexo`,
    );
  }

  if (normalizedRole) {
    candidates.push("genero", "sexo");
  } else {
    candidates.push("genero", "sexo");
  }

  return Array.from(new Set(candidates.map((candidate) => normalizeMarkedKey(candidate))));
}

function getMarkedGenderRelatedFieldKeys(field: MarkedTemplateField): string[] {
  const roleKey = getMarkedGenderDependentRoleKey(field.key);
  return getMarkedGenderFieldCandidatesForRole(roleKey);
}

function getMarkedGenderSyntheticFieldKey(roleKey: string): string {
  return `genero_${normalizeMarkedKey(roleKey)}`;
}

function buildMarkedGenderSyntheticField(
  roleKey: string,
  section: string,
): MarkedTemplateField {
  const normalizedRole = normalizeMarkedKey(roleKey);
  return {
    key: getMarkedGenderSyntheticFieldKey(normalizedRole),
    label: `${humanizeMarkedRoleKey(normalizedRole)} es hombre o mujer`,
    section,
    occurrences: 0,
    marker_types: [],
    raw_markers: [],
  };
}

function getEffectiveMarkedTemplateFields(fields: MarkedTemplateField[]): MarkedTemplateField[] {
  const effectiveFields = [...fields];
  const existingGenderKeys = new Set(fields.filter((field) => isMarkedGenderField(field)).map((field) => markedFieldKey(field)));
  const syntheticInsertions: Array<{ index: number; field: MarkedTemplateField }> = [];
  const insertedKeys = new Set<string>();

  const candidateRoles = new Map<string, { index: number; section: string }>();
  fields.forEach((field, index) => {
    const roleKey = getMarkedGenderDependentRoleKey(field.key);
    if (!roleKey) return;

    const dependentSection = getMarkedSectionId(field);
    const key = normalizeMarkedKey(roleKey);
    if (!candidateRoles.has(key)) {
      candidateRoles.set(key, { index, section: dependentSection });
    }
  });

  candidateRoles.forEach((info, roleKey) => {
    const candidates = getMarkedGenderFieldCandidatesForRole(roleKey);
    const hasRealGenderField = fields.some((field) => isMarkedGenderField(field) && candidates.includes(markedFieldKey(field)));
    if (hasRealGenderField) return;

    const syntheticKey = getMarkedGenderSyntheticFieldKey(roleKey);
    if (existingGenderKeys.has(syntheticKey) || insertedKeys.has(syntheticKey)) return;

    syntheticInsertions.push({
      index: info.index + 1,
      field: buildMarkedGenderSyntheticField(roleKey, info.section),
    });
    insertedKeys.add(syntheticKey);
  });

  syntheticInsertions
    .sort((a, b) => a.index - b.index)
    .forEach(({ index, field }, insertionIndex) => {
      effectiveFields.splice(Math.min(index + insertionIndex, effectiveFields.length), 0, field);
    });

  return effectiveFields;
}

const AMBIGUOUS_MARKED_KEYS = new Set([
  normalizeMarkedKey("nombre"),
  normalizeMarkedKey("documento"),
  normalizeMarkedKey("fecha"),
  normalizeMarkedKey("valor"),
  normalizeMarkedKey("nit"),
  normalizeMarkedKey("escritura"),
  normalizeMarkedKey("numero"),
  normalizeMarkedKey("número"),
]);

function isMarkedAmbiguousField(field: MarkedTemplateField): boolean {
  if (isMarkedPartnerDescriptorField(field)) return false;
  return AMBIGUOUS_MARKED_KEYS.has(markedFieldKey(field));
}

function isMarkedProtocolAutofillField(field: MarkedTemplateField): boolean {
  const blob = markedFieldBlob(field);
  return [
    "protocolista",
    "recepcion",
    "recepcion_y_extension",
    "recepcion_extension",
    "extension",
    "otorgamiento",
  ].some((keyword) => blob.includes(normalizeMarkedText(keyword)));
}

function getMarkedBuyerGroup(field: MarkedTemplateField): "comprador_1" | "comprador_2" | null {
  const blob = markedFieldBlob(field);
  if (blob.includes("comprador_1") || blob.includes("comprador1")) return "comprador_1";
  if (blob.includes("comprador_2") || blob.includes("comprador2")) return "comprador_2";
  return null;
}

function isMarkedNationalityField(field: MarkedTemplateField): boolean {
  const blob = markedFieldBlob(field);
  return MARKED_NATIONALITY_KEYWORDS.some((keyword) => blob.includes(normalizeMarkedText(keyword)));
}

function isMarkedCountryField(field: MarkedTemplateField): boolean {
  const blob = markedFieldBlob(field);
  return ["pais", "país", "pais_expedicion", "país_expedicion"].some((keyword) => blob.includes(normalizeMarkedText(keyword)));
}

function isMarkedMunicipalityField(field: MarkedTemplateField): boolean {
  const blob = markedFieldBlob(field);
  return MARKED_MUNICIPALITY_KEYWORDS.some((keyword) => blob.includes(normalizeMarkedText(keyword)));
}

function getMarkedRelatedGenderFieldKey(
  field: MarkedTemplateField,
  fields: MarkedTemplateField[],
  values: Record<string, string>,
): string | null {
  const candidateKeys = getMarkedGenderRelatedFieldKeys(field);

  const roleSpecificKeys = candidateKeys.filter((candidateKey) => candidateKey !== "genero" && candidateKey !== "sexo");
  const hasRoleSpecificGenderField = fields.some((item) => isMarkedGenderField(item) && roleSpecificKeys.includes(markedFieldKey(item)));
  const searchKeys = hasRoleSpecificGenderField ? roleSpecificKeys : candidateKeys.filter((candidateKey) => candidateKey === "genero" || candidateKey === "sexo");

  for (const candidateKey of searchKeys) {
    const candidate = fields.find((item) => isMarkedGenderField(item) && markedFieldKey(item) === candidateKey);
    if (!candidate) continue;
    if (normalizeMarkedGender(values[candidate.key])) return candidate.key;
  }

  return null;
}

function getMarkedRelatedGender(
  field: MarkedTemplateField,
  fields: MarkedTemplateField[],
  values: Record<string, string>,
): MarkedGender | null {
  const relatedGenderKey = getMarkedRelatedGenderFieldKey(field, fields, values);
  if (!relatedGenderKey) return null;
  return normalizeMarkedGender(values[relatedGenderKey]);
}

function getMarkedNationalityRelatedGender(field: MarkedTemplateField, fields: MarkedTemplateField[], values: Record<string, string>): MarkedGender | null {
  return getMarkedRelatedGender(field, fields, values);
}

function getMarkedNationalityRelatedGenderKey(field: MarkedTemplateField, fields: MarkedTemplateField[], values: Record<string, string>): string | null {
  return getMarkedRelatedGenderFieldKey(field, fields, values);
}

function getMarkedNationalityOptions(gender: MarkedGender | null) {
  return getNacionalidadesPorGenero(gender ?? "");
}

function getMarkedStateCivilRelatedGenderKey(field: MarkedTemplateField, fields: MarkedTemplateField[], values: Record<string, string>): string | null {
  return getMarkedRelatedGenderFieldKey(field, fields, values);
}

function normalizeMarkedGender(value: string | null | undefined): MarkedGender | null {
  const normalized = normalizeMarkedText(String(value ?? ""));
  if (!normalized) return null;
  if (
    normalized.startsWith("hombre") ||
    normalized === "h" ||
    normalized === "masculino" ||
    normalized === "m"
  ) {
    return "M";
  }
  if (
    normalized.startsWith("mujer") ||
    normalized === "f" ||
    normalized === "femenino" ||
    normalized === "fem"
  ) {
    return "F";
  }
  if (
    normalized.includes("persona_juridica") ||
    normalized.includes("juridica") ||
    normalized.includes("persona_moral") ||
    normalized === "j"
  ) {
    return "J";
  }
  return null;
}

function getMarkedGenderLabel(value: string | null | undefined): string {
  const gender = normalizeMarkedGender(value);
  if (gender === "M") return "Hombre";
  if (gender === "F") return "Mujer";
  if (gender === "J") return "Persona jurídica";
  return "";
}

function getMarkedFieldKind(field: MarkedTemplateField): MarkedFieldKind {
  const key = markedFieldKey(field);
  if (MARKED_DECISION_SELECT_KEYS.has(key)) return "decision";
  if (MARKED_DECISION_TEXT_KEYS.has(key)) return "text";
  if (isMarkedTypeDocumentField(field)) return "typeDocument";
  if (key === "dia_elaboracion_escritura") return "day";
  if (key === "mes_elaboracion_escritura") return "month";
  if (key === "fecha_celebracion_de_la_promesa_compraventa") return "date";
  if (
    key === "valor_apartamento_en_letras" ||
    key === "en_letras_cuota_inicial" ||
    key === "valor_del_acto_de_la_hipoteca_en_letras"
  ) {
    return "textarea";
  }
  if (key === "origen_cuota_inicial" || key === "protocolista" || key === "consecutivo_hojas_papel_notarial") {
    return "text";
  }
  if (MARKED_BASIC_ORDER.includes(key)) {
    if (key === "linderos") return "textarea";
    return "text";
  }
  if (
    key === "valor_de_la_venta_en_numeros" ||
    key === "en_numeros_cuota_inicial" ||
    key === "valor_del_acto_de_la_hipoteca" ||
    MARKED_LIQUIDATION_ORDER.includes(key)
  ) return "money";
  if (isMarkedGenderField(field)) return "gender";
  if (isMarkedStateCivilField(field)) return "stateCivil";
  if (isMarkedLettersField(field)) return "textarea";
  if (isMarkedDayField(field)) return "day";
  if (isMarkedMonthField(field)) return "month";
  if (isMarkedYearField(field)) return "year";
  if (isMarkedMoneyField(field)) return "money";
  if (isMarkedDateField(field)) return "date";
  return "text";
}

function normalizeDropdownFieldValue(value: string) {
  return isPlaceholderDropdownValue(value) ? "" : value;
}

function isMarkedDropdownField(field: MarkedTemplateField) {
  const kind = getMarkedFieldKind(field);
  return (
    isMarkedCountryField(field) ||
    isMarkedNationalityField(field) ||
    isMarkedMunicipalityField(field) ||
    kind === "decision" ||
    kind === "gender" ||
    kind === "stateCivil" ||
    kind === "typeDocument" ||
    kind === "day" ||
    kind === "month"
  );
}

function formatMarkedCOP(value: string): string {
  const digits = extractMarkedMoneyDigits(value);
  if (!digits) return "";
  return Number(digits).toLocaleString("es-CO");
}

function parseMarkedCOP(value: string): string {
  return extractMarkedMoneyDigits(value);
}

function getMarkedFieldTokens(field: MarkedTemplateField): string[] {
  return markedFieldBlob(field)
    .split("_")
    .filter((token) => token.length > 2 && !["para", "con", "del", "las", "los", "por", "una", "uno"].includes(token));
}

function scoreMarkedFieldRelation(source: MarkedTemplateField, target: MarkedTemplateField): number {
  if (source.key === target.key) return -1;
  const sourceTokens = new Set(getMarkedFieldTokens(source));
  const targetTokens = new Set(getMarkedFieldTokens(target));
  let score = 0;
  sourceTokens.forEach((token) => {
    if (targetTokens.has(token)) score += 2;
  });
  if (source.section === target.section) score += 2;
  if (getMarkedBuyerGroup(source) && getMarkedBuyerGroup(source) === getMarkedBuyerGroup(target)) score += 2;
  if (isMarkedMoneyField(target)) score += 1;
  if (isMarkedLettersField(source) && isMarkedMoneyField(target)) score += 1;
  return score;
}

function getBestMarkedMoneyFieldForLetter(
  letterField: MarkedTemplateField,
  fields: MarkedTemplateField[],
): MarkedTemplateField | null {
  const candidates = fields.filter((candidate) => isMarkedMoneyField(candidate));
  let best: MarkedTemplateField | null = null;
  let bestScore = Number.NEGATIVE_INFINITY;

  for (const candidate of candidates) {
    const score = scoreMarkedFieldRelation(letterField, candidate);
    if (score > bestScore) {
      best = candidate;
      bestScore = score;
    }
  }

  if (!best || bestScore <= 0) {
    const sameSectionCandidates = candidates.filter((candidate) => candidate.section === letterField.section);
    if (sameSectionCandidates.length === 1) return sameSectionCandidates[0];
  }

  return bestScore > 0 ? best : null;
}

function getLinkedMarkedMoneyFieldForLetter(
  letterField: MarkedTemplateField,
  fields: MarkedTemplateField[],
): MarkedTemplateField | null {
  const linkedMoneyKey = getMarkedMoneySourceKeyForLetter(letterField);
  if (linkedMoneyKey) {
    const normalizedLinkedMoneyKey = normalizeMarkedKey(linkedMoneyKey);
    return (
      fields.find((candidate) => markedFieldKey(candidate) === normalizedLinkedMoneyKey) ??
      getBestMarkedMoneyFieldForLetter(letterField, fields)
    );
  }
  return getBestMarkedMoneyFieldForLetter(letterField, fields);
}

function withDerivedMarkedLetterValues(
  fields: MarkedTemplateField[],
  values: Record<string, string>,
): Record<string, string> {
  const next = { ...values };
  fields.forEach((field) => {
    if (!isMarkedLettersField(field)) return;
    if (String(next[field.key] ?? "").trim()) return;
    const linkedMoneyField = getLinkedMarkedMoneyFieldForLetter(field, fields);
    if (!linkedMoneyField) return;
    const derivedValue = getMarkedLettersFromMoneyValue(next[linkedMoneyField.key] ?? "", linkedMoneyField.key, field.key);
    if (derivedValue) {
      next[field.key] = derivedValue;
    }
  });
  return next;
}

type DerivedMarkedMoneyLetterRule = {
  moneyKey: string;
  letterKey: string;
  fallbackValue?: string;
};

const DERIVED_MARKED_MONEY_LETTER_RULES: DerivedMarkedMoneyLetterRule[] = [
  {
    moneyKey: "valor_de_la_venta_en_numeros",
    letterKey: "valor_apartamento_en_letras",
  },
  {
    moneyKey: "en_numeros_cuota_inicial",
    letterKey: "en_letras_cuota_inicial",
  },
  {
    moneyKey: "valor_del_acto_de_la_hipoteca",
    letterKey: "valor_del_acto_de_la_hipoteca_en_letras",
  },
];

function getMarkedFieldByNormalizedKey(fields: MarkedTemplateField[], normalizedKey: string): MarkedTemplateField | null {
  return fields.find((field) => markedFieldKey(field) === normalizedKey) ?? null;
}

function applyDerivedMarkedMoneyLettersToValues(
  baseValues: Record<string, string>,
  fields: MarkedTemplateField[],
): Record<string, string> {
  const result = { ...baseValues };

  DERIVED_MARKED_MONEY_LETTER_RULES.forEach(({ moneyKey, letterKey }) => {
    const moneyField = getMarkedFieldByNormalizedKey(fields, normalizeMarkedKey(moneyKey));
    const letterField = getMarkedFieldByNormalizedKey(fields, normalizeMarkedKey(letterKey));
    if (!moneyField || !letterField) return;

    const moneyValue = result[moneyField.key] ?? "";
    const letterValue = getMarkedLettersFromMoneyValue(moneyValue, moneyField.key, letterField.key);
    if (letterValue) {
      result[letterField.key] = letterValue;
    }
  });

  const originField = getMarkedFieldByNormalizedKey(fields, normalizeMarkedKey("origen_cuota_inicial"));
  if (
    originField &&
    !String(result[originField.key] ?? "").trim() &&
    process.env.NODE_ENV !== "production"
  ) {
    result[originField.key] = "recursos propios";
  }

  return result;
}

function getDerivedMarkedMoneyLetterDebugRows(
  payload: Record<string, string>,
  fields: MarkedTemplateField[],
) {
  return DERIVED_MARKED_MONEY_LETTER_RULES.map(({ moneyKey, letterKey }) => {
    const moneyField = getMarkedFieldByNormalizedKey(fields, normalizeMarkedKey(moneyKey));
    const letterField = getMarkedFieldByNormalizedKey(fields, normalizeMarkedKey(letterKey));
    return {
      moneyKey: moneyField?.key ?? moneyKey,
      moneyValue: moneyField ? payload[moneyField.key] ?? "" : "",
      letterKey: letterField?.key ?? letterKey,
      letterValue: letterField ? payload[letterField.key] ?? "" : "",
    };
  });
}

function getMarkedStateCivilOptions(gender: MarkedGender | null) {
  if (gender === "M" || gender === "F") {
    return getEstadosCiviles(gender).map((value) => ({ value, label: value }));
  }
  if (gender === "J") {
    return [{ value: "No aplica", label: "No aplica" }];
  }
  return [...MARKED_GENERAL_ESTADOS_CIVILES];
}

function getMarkedConcordanceSuggestion(
  field: MarkedTemplateField,
  fields: MarkedTemplateField[],
  values: Record<string, string>,
): string {
  const gender = getMarkedRelatedGender(field, fields, values);
  if (!gender) return "";

  const blob = markedFieldBlob(field);
  const terms = gender === "M"
    ? [
        ["identificada", "identificado"],
        ["domiciliada", "domiciliado"],
        ["compradora", "comprador"],
        ["soltera", "soltero"],
        ["casada", "casado"],
        ["divorciada", "divorciado"],
        ["viuda", "viudo"],
      ]
    : [
        ["identificado", "identificada"],
        ["domiciliado", "domiciliada"],
        ["comprador", "compradora"],
        ["soltero", "soltera"],
        ["casado", "casada"],
        ["divorciado", "divorciada"],
        ["viudo", "viuda"],
      ];

  for (const [match, suggestion] of terms) {
    if (blob.includes(match)) return suggestion;
  }
  return "";
}

function MarkedTemplateSummary({ result }: { result: MarkedTemplateDetectResult }) {
  return (
    <div className="ep-card rounded-2xl p-5 mt-5 space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-3">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold tracking-wide bg-emerald-50 text-emerald-700">
            <span className="w-2 h-2 rounded-full bg-emerald-500" />
            Plantilla marcada · Sin IA
          </span>
        </div>
        <span className="text-xs text-soft">
          {result.total_fields} campos · {result.total_occurrences} ocurrencias
        </span>
      </div>

      <div className="grid grid-cols-3 gap-3 text-center">
        {[
          { label: "Campos", value: result.total_fields },
          { label: "Ocurrencias", value: result.total_occurrences },
          { label: "Tipos de marca", value: Object.values(result.marker_types).filter((v) => v > 0).length },
        ].map(({ label, value }) => (
          <div key={label} className="ep-card-muted rounded-xl p-3">
            <p className="text-xl font-bold text-primary">{value}</p>
            <p className="text-xs text-soft mt-0.5">{label}</p>
          </div>
        ))}
      </div>

      <div>
        <p className="text-xs font-semibold text-muted uppercase tracking-wider mb-2">
          Marcas detectadas
        </p>
        <div className="flex flex-wrap gap-1.5">
          {[
            ["bracket", "Corchetes", result.marker_types.bracket],
            ["curly", "Llaves", result.marker_types.curly],
            ["parenthesis", "Paréntesis", result.marker_types.parenthesis],
            ["highlight", "Resaltado", result.marker_types.highlight],
          ].map(([key, label, value]) => (
            <span key={String(key)} className="ep-pill text-xs px-2.5 py-1 rounded-full">
              {label}: {String(value)}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}

function MarkedFieldsForm({
  fields,
  values,
  documentName,
  onDocumentNameChange,
  onChange,
  onGenerate,
  onContinueToSummary,
  onApplyQaPreset,
  onCopyEmptyFields,
  onCopyCurrentPayload,
  onDownloadGeneratedQaDocx,
  showQaPresetButton,
  showGeneratedQaDownloadButton,
  isGenerating,
  showPendingWarning,
  showAmbiguousWarning,
}: {
  fields: MarkedTemplateField[];
  values: Record<string, string>;
  documentName: string;
  onDocumentNameChange: (value: string) => void;
  onChange: (key: string, value: string) => void;
  onGenerate: () => void;
  onContinueToSummary: () => void;
  onApplyQaPreset?: () => void;
  onCopyEmptyFields?: () => void;
  onCopyCurrentPayload?: () => void;
  onDownloadGeneratedQaDocx?: () => void;
  showQaPresetButton?: boolean;
  showGeneratedQaDownloadButton?: boolean;
  isGenerating: boolean;
  showPendingWarning: boolean;
  showAmbiguousWarning: boolean;
}) {
  const fieldIndexMap = new Map(fields.map((field, index) => [field.key, index]));
  const [markedGeoDepartments, setMarkedGeoDepartments] = useState<Record<string, string>>({});
  const [currentUserFullName, setCurrentUserFullName] = useState("");
  const [markedManualOverrides, setMarkedManualOverrides] = useState<Record<string, boolean>>({});
  const [markedLetterManualOverrides, setMarkedLetterManualOverrides] = useState<Record<string, boolean>>({});
  const ambiguousFields = fields.filter((field) => isMarkedAmbiguousField(field));
  const visibleFields = fields.filter((field) => !isMarkedAmbiguousField(field));

  useEffect(() => {
    let active = true;
    getCurrentUser()
      .then((user) => {
        if (!active) return;
        const fullName = user.full_name?.trim() ?? "";
        if (fullName) setCurrentUserFullName(fullName);
      })
      .catch(() => {
        if (!active) return;
        setCurrentUserFullName("");
      });

    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    if (!currentUserFullName) return;

    fields.forEach((field) => {
      if (!isMarkedProtocolAutofillField(field)) return;
      if (markedManualOverrides[field.key]) return;
      if ((values[field.key] ?? "").trim()) return;
      onChange(field.key, currentUserFullName);
    });
  }, [currentUserFullName, fields, markedManualOverrides, onChange, values]);

  function handleFieldChange(field: MarkedTemplateField, rawValue: string) {
    const kind = getMarkedFieldKind(field);
    let nextValue = normalizeDropdownFieldValue(rawValue);
    const previousValue = values[field.key] ?? "";

    if (kind === "money") {
      nextValue = parseMarkedCOP(rawValue);
    } else if (kind === "day") {
      nextValue = rawValue.replace(/\D/g, "").slice(0, 2);
    } else if (kind === "year") {
      nextValue = rawValue.replace(/\D/g, "").slice(0, 4);
    }

    onChange(field.key, nextValue);

    if (isMarkedProtocolAutofillField(field) && nextValue !== currentUserFullName) {
      setMarkedManualOverrides((prev) => (prev[field.key] ? prev : { ...prev, [field.key]: true }));
    }

    if (kind === "gender") {
      const normalizedGender = normalizeMarkedGender(nextValue);
      if (!normalizedGender) return;
      const validStateCivilValues = new Set(getMarkedStateCivilOptions(normalizedGender).map((option) => option.value));
      const validNationalityValues = new Set(getMarkedNationalityOptions(normalizedGender).map((option) => option.value));
      fields.forEach((candidate) => {
        if (getMarkedFieldKind(candidate) !== "stateCivil") return;
        const linkedGenderKey = getMarkedStateCivilRelatedGenderKey(candidate, fields, values);
        if (linkedGenderKey !== field.key) return;

        const currentStateCivil = values[candidate.key] ?? "";
        if (currentStateCivil && !validStateCivilValues.has(currentStateCivil)) {
          onChange(candidate.key, "");
        }
      });

      fields.forEach((candidate) => {
        if (!isMarkedNationalityField(candidate)) return;
        const linkedGenderKey = getMarkedNationalityRelatedGenderKey(candidate, fields, values);
        if (linkedGenderKey !== field.key) return;

        const currentNationality = values[candidate.key] ?? "";
        if (currentNationality && !validNationalityValues.has(currentNationality)) {
          onChange(candidate.key, "");
        }
      });
    }

    if (kind === "textarea" && isMarkedLettersField(field)) {
      const linkedMoneyField = getLinkedMarkedMoneyFieldForLetter(field, fields);
      const autoLetterValue = linkedMoneyField
        ? getMarkedLettersFromMoneyValue(values[linkedMoneyField.key] ?? "", linkedMoneyField.key, field.key)
        : "";
      const isManualOverride = nextValue.trim() !== "" && nextValue.trim() !== autoLetterValue;
      setMarkedLetterManualOverrides((prev) => ({ ...prev, [field.key]: isManualOverride }));
      return;
    }

    if (kind !== "money") return;

    fields.forEach((candidate) => {
      if (!isMarkedLettersField(candidate)) return;
      const linkedMoneyField = getLinkedMarkedMoneyFieldForLetter(candidate, fields);
      if (linkedMoneyField?.key !== field.key) return;

      const currentLetterValue = values[candidate.key] ?? "";
      const previousAutoValue = getMarkedLettersFromMoneyValue(previousValue, field.key, candidate.key);
      const nextAutoValue = getMarkedLettersFromMoneyValue(nextValue, field.key, candidate.key);
      const hasManualOverride = Boolean(markedLetterManualOverrides[candidate.key] && currentLetterValue.trim());
      const canAutofill = !currentLetterValue.trim() || currentLetterValue === previousAutoValue || !hasManualOverride;

      if (!canAutofill) return;
      onChange(candidate.key, nextAutoValue);
      setMarkedLetterManualOverrides((prev) => ({ ...prev, [candidate.key]: false }));
    });
  }

  function getMarkedFieldPlaceholder(field: MarkedTemplateField, kind: string, relatedGender?: string | null, needsDepartment = false) {
    if (needsDepartment) return "Primero selecciona departamento";
    if (kind === "money") return "Ej. 250.000.000";
    if (kind === "textarea") return "Se genera automaticamente; puedes ajustar el texto";
    if (kind === "date") return "Selecciona la fecha";
    if (kind === "day" || kind === "month" || kind === "select") return "Selecciona...";

    const haystack = `${field.key} ${field.label}`.toLowerCase();
    if (haystack.includes("linderos")) return "Escribe o pega los linderos";
    if (haystack.includes("correo") || haystack.includes("email")) return "Escribe el correo electronico";
    if (haystack.includes("celular") || haystack.includes("telefono") || haystack.includes("teléfono")) return "Escribe el celular";
    if (haystack.includes("documento")) return "Escribe el numero de documento";
    if (haystack.includes("direccion") || haystack.includes("dirección") || haystack.includes("domicilio")) return "Escribe la direccion";
    if (haystack.includes("nombre")) return "Escribe el nombre completo";
    return "Escribe la nueva informacion";
  }

  function renderControl(field: MarkedTemplateField) {
    const kind = getMarkedFieldKind(field);
    const currentValue = values[field.key] ?? "";
    const displayValue = normalizeDropdownFieldValue(currentValue);
    const isProtocolAutofill = isMarkedProtocolAutofillField(field);

    if (isMarkedCountryField(field)) {
      return (
        <div className="space-y-1">
          <select
            value={displayValue}
            onChange={(e) => handleFieldChange(field, e.target.value)}
            className="ep-input ep-select w-full min-w-0 rounded-2xl px-4 py-3 text-sm transition-all h-11 md:h-12"
          >
            <option value="">Selecciona...</option>
            {PAISES.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <p className="text-[11px] text-soft leading-tight">Catálogo de países centralizado.</p>
        </div>
      );
    }

    if (isMarkedNationalityField(field)) {
      const relatedGender = getMarkedNationalityRelatedGender(field, fields, values);
      const options = getMarkedNationalityOptions(relatedGender);
      return (
        <div className="space-y-1">
          <select
            value={displayValue}
            onChange={(e) => handleFieldChange(field, e.target.value)}
            className="ep-input ep-select w-full min-w-0 rounded-2xl px-4 py-3 text-sm transition-all h-11 md:h-12"
          >
            <option value="">Selecciona...</option>
            {options.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <p className="text-[11px] text-soft leading-tight">
            {relatedGender === "J"
              ? "Se muestran opciones congruentes con persona jurídica"
              : relatedGender == null
              ? "Puedes diligenciar la nacionalidad aunque el género no esté definido."
              : "Opciones filtradas por género relacionado"}
          </p>
        </div>
      );
    }

    if (kind === "typeDocument") {
      return (
        <select
          value={displayValue}
          onChange={(e) => handleFieldChange(field, e.target.value)}
          className="ep-input ep-select w-full min-w-0 rounded-2xl px-4 py-3 text-sm transition-all h-11 md:h-12"
        >
          <option value="">Selecciona tipo de documento</option>
          {TIPOS_DOCUMENTO.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      );
    }

    if (isMarkedMunicipalityField(field)) {
      const storedDept = markedGeoDepartments[field.key] ?? "";
      const inferredDept = currentValue ? getDepartamentoByMunicipio(currentValue) ?? "" : "";
      const currentDept = storedDept || inferredDept;
      const municipalities = currentDept ? getMunicipiosByDepartamento(currentDept) : [];
      const normalizedCurrentMunicipality = currentValue;

      return (
        <div className="space-y-1.5">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <label className="grid gap-1">
              <span className="text-[11px] font-medium text-muted">Departamento</span>
              <select
                value={currentDept}
                onChange={(e) => {
                  const nextDept = e.target.value;
                  setMarkedGeoDepartments((prev) => ({ ...prev, [field.key]: nextDept }));
                  onChange(field.key, "");
                }}
                className="ep-input ep-select w-full min-w-0 rounded-2xl px-4 py-3 text-sm transition-all h-11 md:h-12"
              >
                <option value="">Selecciona...</option>
                {DEPARTAMENTOS_COLOMBIA.map((d) => (
                  <option key={d.codigo} value={d.nombre}>
                    {d.nombre}
                  </option>
                ))}
              </select>
            </label>
            <label className="grid gap-1">
              <span className="text-[11px] font-medium text-muted">
                {field.label.toLowerCase().includes("ciudad") ? "Ciudad" : "Municipio"}
              </span>
              <select
                value={normalizedCurrentMunicipality}
                onChange={(e) => onChange(field.key, e.target.value)}
                className="ep-input ep-select w-full min-w-0 rounded-2xl px-4 py-3 text-sm transition-all h-11 md:h-12"
                disabled={!currentDept}
              >
                <option value="">{currentDept ? "Selecciona..." : "Primero selecciona departamento"}</option>
                {municipalities.map((m, index) => (
                  <option key={`${m.codigo}-${m.nombre}-${index}`} value={m.nombre}>
                    {m.nombre}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <p className="text-[11px] text-soft leading-tight">
            Se guardara el municipio seleccionado.
          </p>
        </div>
      );
    }

    if (kind === "decision") {
      return (
        <select
          value={displayValue}
          onChange={(e) => handleFieldChange(field, e.target.value)}
          className="ep-input ep-select w-full min-w-0 rounded-2xl px-4 py-3 text-sm transition-all h-11 md:h-12"
        >
          {MARKED_DECISION_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      );
    }

    if (kind === "gender") {
      return (
        <select
          value={displayValue}
          onChange={(e) => handleFieldChange(field, e.target.value)}
          className="ep-input ep-select w-full min-w-0 rounded-2xl px-4 py-3 text-sm transition-all h-11 md:h-12"
        >
          <option value="">Selecciona...</option>
          {MARKED_GENDER_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      );
    }

    if (kind === "stateCivil") {
      const relatedGender = getMarkedRelatedGender(field, fields, values);
      const options = getMarkedStateCivilOptions(relatedGender);
      return (
        <div className="space-y-1">
          <select
            value={displayValue}
            onChange={(e) => handleFieldChange(field, e.target.value)}
            className="ep-input ep-select w-full min-w-0 rounded-2xl px-4 py-3 text-sm transition-all h-11 md:h-12"
          >
            <option value="">Selecciona...</option>
            {options.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <p className="text-[11px] text-soft leading-tight">
            {relatedGender === "J"
              ? "Solo se permite No aplica"
              : relatedGender == null
              ? "Puedes diligenciar el estado civil aunque el género no esté definido."
              : "Opciones filtradas por género relacionado"}
          </p>
        </div>
      );
    }

    if (kind === "date") {
      return (
        <input
          type="date"
          value={currentValue}
          onChange={(e) => handleFieldChange(field, e.target.value)}
          className="ep-input w-full min-w-0 rounded-2xl px-4 py-3 text-sm leading-5 transition-all h-11 md:h-12"
        />
      );
    }

    if (kind === "day") {
      return (
        <select
          value={displayValue}
          onChange={(e) => handleFieldChange(field, e.target.value)}
          className="ep-input ep-select w-full min-w-0 rounded-2xl px-4 py-3 text-sm transition-all h-11 md:h-12"
        >
          <option value="">Selecciona día</option>
          {Array.from({ length: 31 }, (_, index) => index + 1).map((day) => (
            <option key={day} value={String(day)}>
              {day}
            </option>
          ))}
        </select>
      );
    }

    if (kind === "month") {
      return (
        <select
          value={displayValue}
          onChange={(e) => handleFieldChange(field, e.target.value)}
          className="ep-input ep-select w-full min-w-0 rounded-2xl px-4 py-3 text-sm transition-all h-11 md:h-12"
        >
          <option value="">Selecciona...</option>
          {MARKED_MONTH_LABELS.map((month) => (
            <option key={month.value} value={month.label}>
              {month.label}
            </option>
          ))}
        </select>
      );
    }

    if (kind === "year") {
      return (
        <input
          type="number"
          inputMode="numeric"
          min={1000}
          max={9999}
          step={1}
          value={currentValue}
          onChange={(e) => handleFieldChange(field, e.target.value)}
          className="ep-input w-full min-w-0 rounded-2xl px-4 py-3 text-sm leading-5 transition-all h-11 md:h-12"
          placeholder="Ano"
        />
      );
    }

    if (kind === "money") {
      return (
        <input
          type="text"
          inputMode="numeric"
          value={formatMarkedCOP(currentValue)}
          onChange={(e) => handleFieldChange(field, e.target.value)}
          className="ep-input w-full min-w-0 rounded-2xl px-4 py-3 text-sm leading-5 transition-all h-11 md:h-12"
          placeholder="Ej. 250.000.000"
        />
      );
    }

    if (kind === "textarea") {
      const suggestion = getMarkedConcordanceSuggestion(field, fields, values);
      const linkedMoneyField = getLinkedMarkedMoneyFieldForLetter(field, fields);
      const linkedMoneyValue = linkedMoneyField ? values[linkedMoneyField.key] ?? "" : "";
      const autoLetterValue = linkedMoneyField
        ? getMarkedLettersFromMoneyValue(linkedMoneyValue, linkedMoneyField.key, field.key)
        : "";
      return (
        <div className="space-y-1">
          <textarea
            value={currentValue}
            onChange={(e) => handleFieldChange(field, e.target.value)}
            className="ep-input w-full min-w-0 rounded-2xl px-4 py-3 text-sm leading-5 transition-all min-h-[110px] resize-y"
            placeholder="Se genera automaticamente; puedes ajustar el texto"
            rows={3}
          />
          {autoLetterValue && currentValue === autoLetterValue && (
            <p className="text-[11px] text-emerald-700">Auto-generado desde el campo numerico relacionado</p>
          )}
          {suggestion && (
            <p className="text-[11px] text-soft leading-tight">
              Sugerencia por genero: <span className="font-medium text-ink">{suggestion}</span>
            </p>
          )}
        </div>
      );
    }

    const suggestion = getMarkedConcordanceSuggestion(field, fields, values);
    return (
      <div className="space-y-1">
        <input
          type="text"
          value={currentValue}
          onChange={(e) => handleFieldChange(field, e.target.value)}
          className="ep-input w-full min-w-0 rounded-2xl px-4 py-3 text-sm leading-5 transition-all h-11 md:h-12"
          placeholder={isProtocolAutofill && !currentValue ? "Se autollenará con tu nombre" : getMarkedFieldPlaceholder(field, kind)}
        />
        {suggestion && (
          <p className="text-[11px] text-soft leading-tight">
            Sugerencia por genero: <span className="font-medium text-ink">{suggestion}</span>
          </p>
        )}
      </div>
    );
  }

  function renderField(field: MarkedTemplateField, extraClassName = "") {
    const kind = getMarkedFieldKind(field);
    const relatedGender = getMarkedRelatedGender(field, fields, values);
    const note = getMarkedBuyerIndex(field) === 1 && MARKED_BUYER_NOTE_KEYS.has(markedFieldKey(field))
      ? "Campo sin índice en plantilla; asociado visualmente a Comprador 1"
      : "";
    const rawMarkerPreview = field.raw_markers?.[0] ?? "";

    return (
      <label key={field.key} className={`grid gap-1.5 ${extraClassName}`}>
        <span className="text-sm font-medium text-muted flex items-center gap-1.5 flex-wrap">
          <span>{field.label}</span>
          {kind === "stateCivil" && relatedGender && (
            <span className="text-[10px] font-semibold text-blue-700 bg-blue-100 px-1.5 py-0.5 rounded-full leading-none">
              género: {getMarkedGenderLabel(relatedGender)}
            </span>
          )}
        </span>
        {renderControl(field)}
        {note && <p className="text-[11px] text-soft leading-tight">{note}</p>}
        {rawMarkerPreview && isMarkedAmbiguousField(field) && (
          <span className="inline-flex w-fit rounded-lg border border-amber-300 bg-amber-50 px-2 py-1 text-[11px] font-mono text-amber-800">
            {rawMarkerPreview.startsWith("{{") || rawMarkerPreview.startsWith("[[") || rawMarkerPreview.startsWith("(")
              ? rawMarkerPreview
              : `{{${rawMarkerPreview.toUpperCase()}}}`}
          </span>
        )}
        <span className="text-[11px] text-soft leading-tight">
          {field.key} · {field.occurrences} ocurrencia{field.occurrences !== 1 ? "s" : ""}
        </span>
      </label>
    );
  }

  const basicFields = sortMarkedFieldsByOrder(
    visibleFields.filter((field) => getMarkedSectionId(field) === "basic"),
    MARKED_BASIC_ORDER,
  );
  const valueFields = sortMarkedFieldsByOrder(
    visibleFields.filter((field) => getMarkedSectionId(field) === "values"),
    MARKED_VALUE_ORDER,
  );
  const decisionFields = sortMarkedFieldsByOrder(
    visibleFields.filter((field) => getMarkedSectionId(field) === "decisions"),
    MARKED_DECISION_ORDER,
  );
  const protocolFields = sortMarkedFieldsByOrder(
    visibleFields.filter((field) => getMarkedSectionId(field) === "protocol"),
    MARKED_PROTOCOL_ORDER,
  );
  const liquidationFields = sortMarkedFieldsByOrder(
    visibleFields.filter((field) => getMarkedSectionId(field) === "liquidation"),
    MARKED_LIQUIDATION_ORDER,
  );
  const decisionSelectFields = decisionFields.filter((field) => MARKED_DECISION_SELECT_KEYS.has(markedFieldKey(field)));
  const decisionTextFields = decisionFields.filter((field) => MARKED_DECISION_TEXT_KEYS.has(markedFieldKey(field)));
  const otherFields = [...visibleFields]
    .filter((field) => getMarkedSectionId(field) === "others")
    .sort((a, b) => (fieldIndexMap.get(a.key) ?? 0) - (fieldIndexMap.get(b.key) ?? 0));
  const buyerGroups = ([1, 2, 3] as const).filter((buyerIndex) =>
    getMarkedBuyerFields(fields, buyerIndex).length > 0
  );

  return (
    <div className="space-y-4">
      <div className="ep-card rounded-2xl overflow-hidden">
        <div className="px-5 py-3.5 border-b border-line/70 flex items-center justify-between gap-3">
          <span className="text-sm font-semibold text-ink">Generación</span>
        </div>
        <div className="p-5">
          <label className="grid gap-1.5">
            <span className="text-sm font-medium text-ink">Nombre de la minuta</span>
            <input
              type="text"
              value={documentName}
              onChange={(e) => onDocumentNameChange(e.target.value)}
              placeholder="Ej: Compraventa Jaggua - Juan Camilo Vásquez - Apto 804"
              className="ep-input w-full rounded-2xl px-4 py-3 text-sm transition-all"
            />
            <p className="text-[11px] text-soft leading-tight">
              Si lo dejas vacío, EasyPro usará el nombre actual por defecto.
            </p>
          </label>
        </div>
      </div>

      {showQaPresetButton ? (
        <div className="rounded-2xl border border-dashed border-line-strong/70 bg-panel-soft/40 px-4 py-3">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-sm font-semibold text-ink">Preset local de QA</p>
              <p className="text-xs text-soft mt-0.5">Autollena los campos detectados para la prueba JAGGUA Banco Bogotá.</p>
            </div>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                onClick={onApplyQaPreset}
                className="inline-flex h-10 items-center justify-center rounded-2xl border border-[var(--line)] bg-white px-4 text-sm font-semibold text-primary transition-all hover:border-primary"
              >
                Autollenar prueba JAGGUA Banco Bogotá
              </button>
              <button
                type="button"
                onClick={onCopyEmptyFields}
                className="inline-flex h-10 items-center justify-center rounded-2xl border border-[var(--line)] bg-white px-4 text-sm font-semibold text-primary transition-all hover:border-primary"
              >
                Copiar campos vacíos
              </button>
              <button
                type="button"
                onClick={onCopyCurrentPayload}
                className="inline-flex h-10 items-center justify-center rounded-2xl border border-[var(--line)] bg-white px-4 text-sm font-semibold text-primary transition-all hover:border-primary"
              >
                Copiar payload actual
              </button>
              {showGeneratedQaDownloadButton ? (
                <button
                  type="button"
                  onClick={onDownloadGeneratedQaDocx}
                  className="inline-flex h-10 items-center justify-center rounded-2xl border border-[var(--line)] bg-white px-4 text-sm font-semibold text-primary transition-all hover:border-primary"
                >
                  Descargar DOCX generado (QA)
                </button>
              ) : null}
            </div>
          </div>
        </div>
      ) : null}

      <div className="ep-card rounded-2xl overflow-hidden">
        <div className="px-5 py-3.5 border-b border-line/70 flex items-center justify-between gap-3">
          <span className="text-sm font-semibold text-ink">Datos básicos e inmueble</span>
          <span className="text-xs text-soft">{basicFields.length} campo{basicFields.length !== 1 ? "s" : ""}</span>
        </div>
        <div className="p-5 grid grid-cols-1 sm:grid-cols-2 gap-4">
          {basicFields.map((field) => (
            <div key={field.key} className={field.key === "linderos" ? "sm:col-span-2" : ""}>
              {renderField(field, field.key === "linderos" ? "sm:col-span-2" : "")}
            </div>
          ))}
        </div>
      </div>

      <div className="space-y-4">
        {buyerGroups.map((buyerIndex) => {
          const buyerFields = sortMarkedFieldsByOrder(getMarkedBuyerFields(fields, buyerIndex), [
            buyerIndex === 1 ? "nombre_comprador_1" : buyerIndex === 2 ? "nombre_comprador_2" : "nombre_comprador_3",
            buyerIndex === 1 ? "tipo_documento_comprador_1" : buyerIndex === 2 ? "tipo_documento_comprador_2" : "tipo_documento_comprador_3",
            buyerIndex === 1 ? "numero_documento_comprador_1" : buyerIndex === 2 ? "numero_documento_comprador_2" : "numero_documento_comprador_3",
            buyerIndex === 1 ? "comprador_es_hombre_o_mujer" : buyerIndex === 2 ? "comprador_2_es_hombre_o_mujer" : "comprador_3_es_hombre_o_mujer",
            buyerIndex === 1 ? "nacionalidad_comprador" : buyerIndex === 2 ? "nacionalidad_comprador_2" : "nacionalidad_comprador_3",
            buyerIndex === 1 ? "municipio_domicilio_comprador" : buyerIndex === 2 ? "municipio_domicilio_comprador_2" : "municipio_domicilio_comprador_3",
            buyerIndex === 1 ? "seleccione_si_comprador_esta_de_transito" : buyerIndex === 2 ? "seleccione_si_comprador_2_esta_de_transito" : "seleccione_si_comprador_3_esta_de_transito",
            buyerIndex === 1 ? "estado_civil_comprador" : buyerIndex === 2 ? "estado_civil_comprador_2" : "estado_civil_comprador_3",
            buyerIndex === 1 ? "direccion_comprador_1" : buyerIndex === 2 ? "direccion_comprador_2" : "direccion_comprador_3",
            buyerIndex === 1 ? "celular_comprador_1" : buyerIndex === 2 ? "celular_comprador_2" : "celular_comprador_3",
            buyerIndex === 1 ? "email_comprador_1" : buyerIndex === 2 ? "email_comprador_2" : "email_comprador_3",
            buyerIndex === 1 ? "profesion_u_oficio" : buyerIndex === 2 ? "profesion_u_oficio_comprador_2" : "profesion_u_oficio_comprador_3",
            buyerIndex === 1 ? "actividad_economica_comprador" : buyerIndex === 2 ? "actividad_economica_comprador_2" : "actividad_economica_comprador_3",
          ]);
          return (
            <div key={buyerIndex} className="ep-card rounded-2xl overflow-hidden">
              <div className="px-5 py-3.5 border-b border-line/70 flex items-center justify-between gap-3">
                <span className="text-sm font-semibold text-ink">{MARKED_BUYER_LABELS[buyerIndex]}</span>
                <span className="text-xs text-soft">{buyerFields.length} campo{buyerFields.length !== 1 ? "s" : ""}</span>
              </div>
              <div className="p-5 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 gap-4">
                {buyerFields.map((field) => (
                  <div key={field.key} className={field.key.includes("direccion") || field.key.includes("municipio_domicilio") || field.key.includes("nacionalidad") || field.key.includes("estado_civil") ? "sm:col-span-2 lg:col-span-2" : ""}>
                    {renderField(field, field.key.includes("direccion") || field.key.includes("municipio_domicilio") || field.key.includes("nacionalidad") || field.key.includes("estado_civil") ? "sm:col-span-2 lg:col-span-2" : "")}
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      <div className="ep-card rounded-2xl overflow-hidden">
        <div className="px-5 py-3.5 border-b border-line/70 flex items-center justify-between gap-3">
          <span className="text-sm font-semibold text-ink">Valores y forma de pago</span>
          <span className="text-xs text-soft">{valueFields.length} campo{valueFields.length !== 1 ? "s" : ""}</span>
        </div>
        <div className="p-5 space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {valueFields.slice(0, 2).map((field) => (
              <div key={field.key} className={field.key.endsWith("_letras") ? "sm:col-span-2" : ""}>
                {renderField(field, field.key.endsWith("_letras") ? "sm:col-span-2" : "")}
              </div>
            ))}
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 gap-4">
            {valueFields.slice(2, 5).map((field) => (
              <div key={field.key} className={field.key === "origen_cuota_inicial" ? "lg:col-span-1" : ""}>
                {renderField(field)}
              </div>
            ))}
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {valueFields.slice(5).map((field) => (
              <div key={field.key}>
                {renderField(field)}
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="ep-card rounded-2xl overflow-hidden">
        <div className="px-5 py-3.5 border-b border-line/70 flex items-center justify-between gap-3">
          <span className="text-sm font-semibold text-ink">Decisiones notariales</span>
          <span className="text-xs text-soft">{decisionFields.length} campo{decisionFields.length !== 1 ? "s" : ""}</span>
        </div>
        <div className="p-5 space-y-5">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {decisionSelectFields.map((field) => (
              <div key={field.key}>
                {renderField(field)}
              </div>
            ))}
          </div>

          {decisionTextFields.length > 0 && (
            <div className="rounded-xl border border-line/70 bg-surface/40 p-4 space-y-4">
              <div>
                <p className="text-sm font-semibold text-ink">Datos del cónyuge/compañero si aplica</p>
                <p className="text-xs text-soft mt-0.5">Se conservan dentro de la misma sección, pero como campos de texto.</p>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {decisionTextFields.map((field) => (
                  <div key={field.key} className="sm:col-span-2">
                    {renderField(field, "sm:col-span-2")}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="ep-card rounded-2xl overflow-hidden">
        <div className="px-5 py-3.5 border-b border-line/70 flex items-center justify-between gap-3">
          <span className="text-sm font-semibold text-ink">Protocolo y otorgamiento</span>
          <span className="text-xs text-soft">{protocolFields.length} campo{protocolFields.length !== 1 ? "s" : ""}</span>
        </div>
        <div className="p-5 grid grid-cols-1 sm:grid-cols-2 gap-4">
          {protocolFields.map((field) => (
            <div key={field.key} className={field.key === "consecutivo_hojas_papel_notarial" ? "sm:col-span-2" : ""}>
              {renderField(field, field.key === "consecutivo_hojas_papel_notarial" ? "sm:col-span-2" : "")}
            </div>
          ))}
        </div>
      </div>

      <div className="ep-card rounded-2xl overflow-hidden">
        <div className="px-5 py-3.5 border-b border-line/70 flex items-center justify-between gap-3">
          <span className="text-sm font-semibold text-ink">Liquidación</span>
          <span className="text-xs text-soft">{liquidationFields.length} campo{liquidationFields.length !== 1 ? "s" : ""}</span>
        </div>
        <div className="p-5 grid grid-cols-1 sm:grid-cols-2 gap-4">
          {liquidationFields.map((field) => (
            <div key={field.key}>
              {renderField(field)}
            </div>
          ))}
        </div>
      </div>

      <div className="ep-card rounded-2xl overflow-hidden">
        <div className="px-5 py-3.5 border-b border-line/70 flex items-center justify-between gap-3">
          <span className="text-sm font-semibold text-ink">Otros</span>
          <span className="text-xs text-soft">{otherFields.length} campo{otherFields.length !== 1 ? "s" : ""}</span>
        </div>
        <div className="p-5">
          {otherFields.length === 0 ? (
            <div className="rounded-xl border border-dashed border-line-strong/70 bg-panel-soft/40 px-4 py-3 text-sm text-soft">
              Sin campos sin clasificar para esta plantilla.
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {otherFields.map((field) => (
                <div key={field.key}>
                  {renderField(field)}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="ep-card rounded-2xl overflow-hidden border border-amber-200">
        <div className="px-5 py-3.5 border-b border-amber-200/80 bg-amber-50/70 flex items-center justify-between gap-3">
          <span className="text-sm font-semibold text-amber-900">Campos ambiguos por corregir</span>
          <span className="text-xs text-amber-700">{ambiguousFields.length} campo{ambiguousFields.length !== 1 ? "s" : ""}</span>
        </div>
        <div className="p-5 space-y-4">
          <p className="text-sm text-amber-900 bg-amber-50 border border-amber-200 rounded-xl px-4 py-3">
            Campo demasiado genérico. Corrige la plantilla o asígnalo manualmente antes de generar.
          </p>
          {ambiguousFields.length === 0 ? (
            <div className="rounded-xl border border-dashed border-line-strong/70 bg-panel-soft/40 px-4 py-3 text-sm text-soft">
              No hay campos ambiguos por corregir en esta plantilla.
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {ambiguousFields.map((field) => (
                <div key={field.key} className="sm:col-span-2">
                  {renderField(field, "sm:col-span-2")}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="sticky bottom-4 z-10 mt-6 rounded-2xl border border-line/70 bg-white/95 backdrop-blur p-4 shadow-lg space-y-3">
        {showAmbiguousWarning && (
          <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
            Hay campos ambiguos. Puedes generar, pero se recomienda corregir la plantilla.
          </div>
        )}
        {showPendingWarning && (
          <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
            Hay campos sin diligenciar; se conservarán sus marcadores en el documento.
          </div>
        )}
        <div className="flex flex-col gap-3 sm:flex-row">
          <button
            type="button"
            onClick={onGenerate}
            disabled={isGenerating}
            className={[
              "w-full h-12 rounded-2xl font-semibold text-sm flex items-center justify-center gap-2 transition-all",
              !isGenerating
                ? "bg-primary text-white hover:opacity-90"
                : "bg-panel-soft text-soft cursor-not-allowed",
            ].join(" ")}
          >
            {isGenerating ? (
              <><Loader2 size={16} className="animate-spin" /> Generando documento</>
            ) : (
              <><ExternalLink size={16} /> Generar documento</>
            )}
          </button>
          <button
            type="button"
            onClick={onContinueToSummary}
            className="w-full h-12 rounded-2xl border border-line-strong text-sm font-semibold text-ink hover:border-primary hover:text-primary transition-all"
          >
            Continuar a generar
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── PersonaField — módulo-level para evitar desmonte/remonte en cada render ──

type PersonaFieldProps = {
  label: string;
  field: keyof MinutaPersona;
  value: string | null;
  as?: "input" | "select";
  options?: { value: string; label: string }[];
  onChange: (field: keyof MinutaPersona, value: string) => void;
};

function PersonaField({ label, field, value, as = "input", options, onChange }: PersonaFieldProps) {
  const pending = value == null || String(value).trim() === "";
  const baseClass =
    "ep-input w-full rounded-xl px-3 py-2 text-sm transition-all " +
    (pending ? "border-amber-300 bg-amber-50 text-amber-900 placeholder:text-amber-400" : "");

  return (
    <label className="grid gap-1">
      <span className="text-xs font-medium text-muted flex items-center gap-1.5">
        {label}
        {pending && (
          <span className="text-[10px] font-semibold text-amber-600 bg-amber-100 px-1.5 py-0.5 rounded-full leading-none">
            pendiente
          </span>
        )}
      </span>
      {as === "select" && options ? (
        <select
          value={value ?? ""}
          onChange={(e) => onChange(field, e.target.value)}
          className={baseClass + " ep-select"}
        >
          <option value="">Selecciona...</option>
          {options.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
      ) : (
        <input
          type="text"
          value={value ?? ""}
          placeholder={pending ? "Sin datos - completar" : ""}
          onChange={(e) => onChange(field, e.target.value)}
          className={baseClass}
        />
      )}
    </label>
  );
}

// ─── Persona card ─────────────────────────────────────────────────────────────

function PersonaCard({
  persona,
  index,
  onChange,
  onRemove,
  id,
}: {
  persona: MinutaPersona;
  index: number;
  onChange: (field: keyof MinutaPersona, value: string) => void;
  onRemove: () => void;
  id?: string;
}) {
  const pendingCount = (
    ["nombre_completo", "tipo_documento", "numero_documento", "genero"] as (keyof MinutaPersona)[]
  ).filter((f) => {
    const v = persona[f];
    return v == null || String(v).trim() === "";
  }).length;

  function handleChange(field: keyof MinutaPersona, value: string) {
    onChange(field, value);
    if (field !== "genero") return;

    const nat = (persona.nacionalidad ?? "").toLowerCase().trim();
    if (value === "F" && nat && GENTILICIOS_M_A_F[nat]) {
      onChange("nacionalidad", GENTILICIOS_M_A_F[nat]);
    } else if (value === "M" && nat && GENTILICIOS_F_A_M[nat]) {
      onChange("nacionalidad", GENTILICIOS_F_A_M[nat]);
    }

    const estadosValidos = getEstadosCiviles(value as "M" | "F" | "J" | "");
    if (persona.estado_civil && !estadosValidos.includes((persona.estado_civil ?? "").toLowerCase())) {
      onChange("estado_civil", "");
    }
  }

  return (
    <div id={id} className="ep-card rounded-2xl overflow-hidden">
      <div className="flex items-center justify-between px-5 py-3.5 border-b border-line/70">
        <div className="flex items-center gap-3">
          <span className="w-7 h-7 rounded-full bg-primary text-white text-xs font-bold flex items-center justify-center">
            {index + 1}
          </span>
          <span className="text-sm font-semibold text-ink">
            {persona.rol.replace(/_/g, " ")}
          </span>
          {pendingCount > 0 && (
            <span className="text-[10px] font-semibold text-amber-700 bg-amber-100 border border-amber-200 px-2 py-0.5 rounded-full">
              {pendingCount} campo{pendingCount > 1 ? "s" : ""} pendiente{pendingCount > 1 ? "s" : ""}
            </span>
          )}
        </div>
        <button
          onClick={onRemove}
          className="w-7 h-7 rounded-lg hover:bg-surface-alt flex items-center justify-center transition-colors"
          aria-label="Eliminar persona"
        >
          <X size={14} className="text-soft" />
        </button>
      </div>

      <div className="p-5 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 gap-4">
        <div className="sm:col-span-2 lg:col-span-2">
          <PersonaField
            label="Nombre completo"
            field="nombre_completo"
            value={String(persona.nombre_completo ?? "")}
            onChange={handleChange}
          />
        </div>
        <PersonaField
          label="Tipo documento"
          field="tipo_documento"
          value={String(persona.tipo_documento ?? "")}
          as="select"
          options={TIPOS_DOCUMENTO}
          onChange={handleChange}
        />
        <PersonaField
          label="Numero documento"
          field="numero_documento"
          value={String(persona.numero_documento ?? "")}
          onChange={handleChange}
        />
        <PersonaField
          label="Genero"
          field="genero"
          value={String(persona.genero ?? "")}
          as="select"
          options={GENERO_OPTIONS}
          onChange={handleChange}
        />
        <PersonaField
          label="Nacionalidad"
          field="nacionalidad"
          value={String(persona.nacionalidad ?? "")}
          onChange={handleChange}
        />
        <PersonaField
          label="Estado civil"
          field="estado_civil"
          value={String(persona.estado_civil ?? "")}
          as="select"
          options={getEstadosCiviles((persona.genero ?? "") as "M" | "F" | "J" | "").map((ec) => ({
            value: ec,
            label: ec.charAt(0).toUpperCase() + ec.slice(1),
          }))}
          onChange={handleChange}
        />
        <PersonaField
          label="Profesion"
          field="profesion"
          value={String(persona.profesion ?? "")}
          onChange={handleChange}
        />
        <PersonaField
          label="Domicilio (ciudad)"
          field="domicilio"
          value={String(persona.domicilio ?? "")}
          onChange={handleChange}
        />
        <div className="sm:col-span-2">
          <PersonaField
            label="Direccion completa"
            field="direccion"
            value={String(persona.direccion ?? "")}
            onChange={handleChange}
          />
        </div>
        <PersonaField
          label="Telefono / Celular"
          field="telefono"
          value={String(persona.telefono ?? "")}
          onChange={handleChange}
        />
        <PersonaField
          label="Correo electronico"
          field="email"
          value={String(persona.email ?? "")}
          onChange={handleChange}
        />
      </div>
    </div>
  );
}

// ─── SectionField — campo genérico para secciones de inmueble/notaría/valores ─

function SectionField({
  label,
  value,
  onChange,
  placeholder,
}: {
  label: string;
  value: string | null;
  onChange: (v: string) => void;
  placeholder?: string;
}) {
  const pending = value == null || String(value).trim() === "";
  return (
    <label className="grid gap-1">
      <span className="text-xs font-medium text-muted flex items-center gap-1.5">
        {label}
        {pending && (
          <span className="text-[10px] font-semibold text-amber-600 bg-amber-100 px-1.5 py-0.5 rounded-full leading-none">
            pendiente
          </span>
        )}
      </span>
      <input
        type="text"
        value={value != null ? String(value) : ""}
        placeholder={placeholder ?? (pending ? "Sin datos - completar" : "")}
        onChange={(e) => onChange(e.target.value)}
        className={
          "ep-input w-full rounded-xl px-3 py-2 text-sm transition-all " +
          (pending ? "border-amber-300 bg-amber-50 text-amber-900 placeholder:text-amber-400" : "")
        }
      />
    </label>
  );
}

// ─── Inmueble card ────────────────────────────────────────────────────────────

const TIPO_INMUEBLE_OPTIONS = [
  "Apartamento", "Casa", "Local", "Oficina",
  "Lote", "Bodega", "Parqueadero", "Depósito",
];

function InmuebleCard({
  inmueble,
  onChange,
}: {
  inmueble: MinutaInmueble;
  onChange: (field: keyof MinutaInmueble, value: string) => void;
}) {
  const baseInput =
    "ep-input w-full rounded-xl px-3 py-2 text-sm transition-all";
  const pendingInput =
    "border-amber-300 bg-amber-50 text-amber-900 placeholder:text-amber-400";
  function cls(val: string | null) {
    return baseInput + ((!val || val.trim() === "") ? " " + pendingInput : "");
  }

  return (
    <div className="ep-card rounded-2xl overflow-hidden">
      <div className="px-5 py-3.5 border-b border-line/70">
        <span className="text-sm font-semibold text-ink">Inmueble</span>
      </div>
      <div className="p-5 space-y-4">

        {/* Fila 1 — tipo + número + piso */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <label className="grid gap-1">
            <span className="text-xs font-medium text-muted">Tipo de inmueble</span>
            <select
              value={inmueble.tipo ?? ""}
              onChange={(e) => onChange("tipo", e.target.value)}
              className={cls(inmueble.tipo) + " ep-select"}
            >
              <option value="">Selecciona...</option>
              {TIPO_INMUEBLE_OPTIONS.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </label>
          <SectionField
            label="Número / Apto"
            value={inmueble.numero}
            onChange={(v) => onChange("numero", v)}
          />
          <SectionField
            label="Piso"
            value={inmueble.piso}
            onChange={(v) => onChange("piso", v)}
          />
        </div>

        {/* Fila 2 — conjunto + barrio */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="sm:col-span-2">
            <SectionField
              label="Conjunto / Edificio"
              value={inmueble.conjunto_o_edificio}
              onChange={(v) => onChange("conjunto_o_edificio", v)}
            />
          </div>
          <SectionField
            label="Barrio"
            value={inmueble.barrio}
            onChange={(v) => onChange("barrio", v)}
          />
        </div>

        {/* Fila 3 — dirección */}
        <SectionField
          label="Dirección"
          value={inmueble.direccion}
          onChange={(v) => onChange("direccion", v)}
        />

        {/* Fila 4 — departamento + municipio + propiedad horizontal */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <label className="grid gap-1">
            <span className="text-xs font-medium text-muted">Departamento</span>
            <select
              value={inmueble.departamento ?? ""}
              onChange={(e) => {
                onChange("departamento", e.target.value);
                onChange("municipio", "");
              }}
              className={cls(inmueble.departamento) + " ep-select"}
            >
              <option value="">Selecciona...</option>
              {DEPARTAMENTOS_COLOMBIA.map(d => (
                <option key={d.codigo} value={d.nombre}>{d.nombre}</option>
              ))}
            </select>
          </label>
          <label className="grid gap-1">
            <span className="text-xs font-medium text-muted">Municipio</span>
            <select
              value={inmueble.municipio ?? ""}
              onChange={(e) => onChange("municipio", e.target.value)}
              className={cls(inmueble.municipio) + " ep-select"}
              disabled={!inmueble.departamento}
            >
              <option value="">Selecciona...</option>
              {getMunicipiosByDepartamento(inmueble.departamento ?? "").map((m, index) => (
                <option key={`${m.codigo}-${m.nombre}-${index}`} value={m.nombre}>{m.nombre}</option>
              ))}
            </select>
          </label>
          <label className="grid gap-1">
            <span className="text-xs font-medium text-muted">Propiedad horizontal</span>
            <select
              value={inmueble.propiedad_horizontal ?? ""}
              onChange={(e) => onChange("propiedad_horizontal", e.target.value)}
              className={cls(inmueble.propiedad_horizontal) + " ep-select"}
            >
              <option value="">Selecciona...</option>
              <option value="SI">Sí</option>
              <option value="NO">No</option>
            </select>
          </label>
        </div>

        {/* Fila 5 — matrícula + cédula catastral + código catastral */}
        <div className="grid grid-cols-2 gap-3">
          <SectionField
            label="Matrícula inmobiliaria"
            value={inmueble.matricula_inmobiliaria}
            onChange={(v) => onChange("matricula_inmobiliaria", v)}
          />
          <SectionField
            label="Cédula catastral"
            value={inmueble.cedula_catastral}
            onChange={(v) => onChange("cedula_catastral", v)}
          />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <SectionField
            label="Código catastral"
            value={inmueble.codigo_catastral}
            onChange={(v) => onChange("codigo_catastral", v)}
          />
        </div>

        {/* Fila 6 — áreas */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <SectionField
            label="Área construida (m²)"
            value={inmueble.area_construida}
            onChange={(v) => onChange("area_construida", v)}
          />
          <SectionField
            label="Área privada (m²)"
            value={inmueble.area_privada}
            onChange={(v) => onChange("area_privada", v)}
          />
          <SectionField
            label="Área total (m²)"
            value={inmueble.area_total}
            onChange={(v) => onChange("area_total", v)}
          />
        </div>

        {/* Fila 7 — coeficiente */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <SectionField
            label="Coeficiente copropiedad"
            value={inmueble.coeficiente_copropiedad}
            onChange={(v) => onChange("coeficiente_copropiedad", v)}
          />
        </div>

        {/* Fila 8 — nota de linderos */}
        <label className="grid gap-1">
          <span className="text-xs font-medium text-muted">Nota de linderos</span>
          <select
            value={inmueble.nota_linderos ?? ""}
            onChange={(e) => onChange("nota_linderos", e.target.value)}
            className={baseInput + " ep-select"}
          >
            <option value="">Sin nota de linderos</option>
            {NOTAS_LINDEROS.map((nota, i) => (
              <option key={i} value={nota}>{nota.substring(0, 80)}…</option>
            ))}
          </select>
        </label>

        {/* Fila 9 — linderos (textarea) */}
        <div className="grid gap-1">
          <span className="text-xs font-medium text-muted flex items-center gap-1.5">
            Linderos
            {(!inmueble.linderos || inmueble.linderos.trim() === "") && (
              <span className="text-[10px] font-semibold text-amber-600 bg-amber-100 px-1.5 py-0.5 rounded-full leading-none">
                pendiente
              </span>
            )}
          </span>
          <textarea
            value={inmueble.linderos ?? ""}
            onChange={(e) => onChange("linderos", e.target.value)}
            rows={5}
            placeholder="Descripción completa de los linderos del inmueble..."
            className={
              baseInput + " resize-y min-h-[80px] " +
              ((!inmueble.linderos || inmueble.linderos.trim() === "") ? pendingInput : "")
            }
          />
        </div>

      </div>
    </div>
  );
}

// ─── Notaría card ─────────────────────────────────────────────────────────────

function NotariaCard({
  notaria,
  onChange,
}: {
  notaria: NotariaEdit;
  onChange: (field: keyof NotariaEdit, value: string) => void;
}) {
  const [depNotaria, setDepNotaria] = useState<string>(() =>
    getDepartamentoByMunicipio(String(notaria.municipio_notaria ?? "")) ?? ""
  );

  // Sincronizar cuando el padre actualiza municipio_notaria (ej: desde handleAnalizar)
  const prevMunicipioRef = useRef(notaria.municipio_notaria);
  if (prevMunicipioRef.current !== notaria.municipio_notaria) {
    prevMunicipioRef.current = notaria.municipio_notaria;
    const inferred = getDepartamentoByMunicipio(String(notaria.municipio_notaria ?? ""));
    if (inferred && inferred !== depNotaria) {
      setDepNotaria(inferred);
    }
  }

  return (
    <div className="ep-card rounded-2xl overflow-hidden">
      <div className="px-5 py-3.5 border-b border-line/70">
        <span className="text-sm font-semibold text-ink">Notaría y fecha</span>
      </div>
      <div className="p-5 grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="sm:col-span-2">
          <SectionField
            label="Nombre notaría"
            value={String(notaria.nombre_notaria ?? "")}
            onChange={(v) => onChange("nombre_notaria", v)}
          />
        </div>
        <label className="grid gap-1">
          <span className="text-xs font-medium text-muted">Departamento notaría</span>
          <select
            value={depNotaria}
            onChange={(e) => {
              setDepNotaria(e.target.value);
              onChange("municipio_notaria", "");
            }}
            className="ep-select ep-input w-full rounded-xl px-3 py-2 text-sm transition-all"
          >
            <option value="">Selecciona...</option>
            {DEPARTAMENTOS_COLOMBIA.map(d => (
              <option key={d.codigo} value={d.nombre}>{d.nombre}</option>
            ))}
          </select>
        </label>
        <label className="grid gap-1">
          <span className="text-xs font-medium text-muted">Municipio notaría</span>
          <select
            value={String(notaria.municipio_notaria ?? "")}
            onChange={(e) => onChange("municipio_notaria", e.target.value)}
            className="ep-select ep-input w-full rounded-xl px-3 py-2 text-sm transition-all"
            disabled={!depNotaria}
          >
            <option value="">Selecciona...</option>
            {getMunicipiosByDepartamento(depNotaria).map((m, index) => (
              <option key={`${m.codigo}-${m.nombre}-${index}`} value={m.nombre}>{m.nombre}</option>
            ))}
          </select>
        </label>
        <SectionField
          label="Número escritura"
          value={String(notaria.numero_escritura ?? "")}
          onChange={(v) => onChange("numero_escritura", v)}
        />
        <label className="grid gap-1">
          <span className="text-xs font-medium text-muted flex items-center gap-1.5">
            Fecha otorgamiento
            {!notaria.fecha_otorgamiento && (
              <span className="text-[10px] font-semibold text-amber-600 bg-amber-100 px-1.5 py-0.5 rounded-full leading-none">
                pendiente
              </span>
            )}
          </span>
          <input
            type="date"
            value={notaria.fecha_otorgamiento ?? ""}
            onChange={(e) => onChange("fecha_otorgamiento", e.target.value)}
            className={
              "ep-input w-full rounded-xl px-3 py-2 text-sm transition-all " +
              (!notaria.fecha_otorgamiento ? "border-amber-300 bg-amber-50 text-amber-900" : "")
            }
          />
        </label>
      </div>
    </div>
  );
}

// ─── Valores card ─────────────────────────────────────────────────────────────

function formatCOP(value: number | string | null): string {
  if (value === null || value === undefined || value === '') return '';
  const num = typeof value === 'string' ? parseInt(value.replace(/\./g, ''), 10) : value;
  if (isNaN(num)) return '';
  return num.toLocaleString('es-CO');
}

function parseCOP(formatted: string): number {
  return parseInt(formatted.replace(/\./g, '').replace(/\D/g, ''), 10) || 0;
}

function ValorRow({
  val, idx, onChangeMonto, onChangeTexto,
}: {
  val: MinutaValor;
  idx: number;
  onChangeMonto: (idx: number, value: string) => void;
  onChangeTexto: (idx: number, value: string) => void;
}) {
  const [textoExpanded, setTextoExpanded] = useState(false);
  const monto = val.monto_numerico ?? 0;
  const letras = monto > 0 ? numeroALetras(monto) : "";

  return (
    <div className="ep-card-muted rounded-xl p-4 space-y-3">
      <div className="flex items-center gap-2">
        <span className="ep-pill text-xs px-2.5 py-1 rounded-full font-semibold">
          {val.tipo.replace(/_/g, " ")}
        </span>
        {val.acto_relacionado != null && (
          <span className="text-xs text-soft">Acto {val.acto_relacionado}</span>
        )}
      </div>
      <label className="grid gap-1">
        <span className="text-xs font-medium text-muted">Monto ($)</span>
        <input
          type="text"
          inputMode="numeric"
          value={formatCOP(val.monto_numerico)}
          onChange={(e) => onChangeMonto(idx, String(parseCOP(e.target.value)))}
          className="ep-input w-full min-w-0 rounded-2xl px-4 py-3 text-sm leading-5 transition-all h-11 md:h-12"
          placeholder="Ej. 250.000.000"
        />
      </label>
      {letras && (
        <div style={{ background: "#f0f9ff", border: "1px solid #bae6fd", borderRadius: "8px", padding: "10px 12px" }}>
          <p style={{ fontSize: "12px", color: "#0369a1", fontWeight: 600, lineHeight: 1.6, margin: 0 }}>
            {letras}
          </p>
        </div>
      )}
      {textoExpanded ? (
        <SectionField
          label="Texto en documento (edición manual)"
          value={String(val.texto_en_documento ?? "")}
          onChange={(v) => onChangeTexto(idx, v)}
        />
      ) : (
        <button
          onClick={() => setTextoExpanded(true)}
          className="text-xs text-soft hover:text-primary underline underline-offset-2"
        >
          ✏ Editar texto manualmente
        </button>
      )}
    </div>
  );
}

function ValoresCard({
  valores,
  onChangeMonto,
  onChangeTexto,
}: {
  valores: MinutaValor[];
  onChangeMonto: (idx: number, value: string) => void;
  onChangeTexto: (idx: number, value: string) => void;
}) {
  if (valores.length === 0) return null;

  return (
    <div className="ep-card rounded-2xl overflow-hidden">
      <div className="px-5 py-3.5 border-b border-line/70">
        <span className="text-sm font-semibold text-ink">Valores monetarios</span>
      </div>
      <div className="p-5 space-y-4">
        {valores.map((val, i) => (
          <ValorRow key={i} val={val} idx={i} onChangeMonto={onChangeMonto} onChangeTexto={onChangeTexto} />
        ))}
      </div>
    </div>
  );
}

// ─── Decisiones card ──────────────────────────────────────────────────────────

const DECISIONES_CONFIG: { key: string; label: string; hint: string }[] = [
  {
    key: "vivienda_familiar",
    label: "¿Afecta vivienda familiar?",
    hint: "El inmueble constituye vivienda familiar del enajenante",
  },
  {
    key: "patrimonio_familia",
    label: "¿Es patrimonio de familia?",
    hint: "El inmueble está afectado a patrimonio de familia inembargable",
  },
  {
    key: "notificacion_electronica",
    label: "¿Acepta notificación electrónica?",
    hint: "Las partes aceptan recibir notificaciones por correo electrónico",
  },
];

function DecisionesCard({
  decisiones,
  onChange,
}: {
  decisiones: Record<string, boolean | null>;
  onChange: (key: string, value: boolean | null) => void;
}) {
  return (
    <div className="ep-card rounded-2xl overflow-hidden">
      <div className="px-5 py-3.5 border-b border-line/70">
        <span className="text-sm font-semibold text-ink">Indagaciones y decisiones</span>
      </div>
      <div className="p-5 space-y-5">
        {DECISIONES_CONFIG.map(({ key, label, hint }) => {
          const val = decisiones[key] ?? null;
          return (
            <div key={key} className="flex items-start justify-between gap-4">
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-ink flex items-center gap-1.5 flex-wrap">
                  {label}
                  {val === null && (
                    <span className="text-[10px] font-semibold text-amber-600 bg-amber-100 px-1.5 py-0.5 rounded-full leading-none">
                      pendiente
                    </span>
                  )}
                </p>
                <p className="text-xs text-soft mt-0.5">{hint}</p>
              </div>
              <div className="flex items-center gap-1 shrink-0">
                {(
                  [
                    { v: null as boolean | null, lbl: "?" },
                    { v: true as boolean | null, lbl: "Sí" },
                    { v: false as boolean | null, lbl: "No" },
                  ]
                ).map(({ v, lbl }) => (
                  <button
                    key={String(v)}
                    type="button"
                    onClick={() => onChange(key, v)}
                    className={[
                      "px-3 py-1.5 rounded-lg text-xs font-semibold transition-all",
                      val === v
                        ? v === true
                          ? "bg-emerald-100 text-emerald-700 border border-emerald-300"
                          : v === false
                          ? "bg-rose-100 text-rose-700 border border-rose-300"
                          : "bg-amber-100 text-amber-700 border border-amber-300"
                        : "bg-panel-soft text-soft border border-line hover:border-primary hover:text-primary",
                    ].join(" ")}
                  >
                    {lbl}
                  </button>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ─── Adquisición card ─────────────────────────────────────────────────────────

function AdquisicionCard({
  adquisicion,
  onChange,
}: {
  adquisicion: MinutaAdquisicion;
  onChange: (field: keyof MinutaAdquisicion, value: string) => void;
}) {
  return (
    <div className="ep-card rounded-2xl overflow-hidden">
      <div className="px-5 py-3.5 border-b border-line/70">
        <span className="text-sm font-semibold text-ink">Antecedente de adquisición</span>
      </div>
      <div className="p-5 grid grid-cols-1 sm:grid-cols-2 gap-4">
        <SectionField
          label="Forma de adquisición"
          value={adquisicion.forma_adquisicion}
          onChange={(v) => onChange("forma_adquisicion", v)}
          placeholder="compraventa, herencia, donación..."
        />
        <SectionField
          label="Número escritura anterior"
          value={adquisicion.escritura_numero}
          onChange={(v) => onChange("escritura_numero", v)}
        />
        <div className="sm:col-span-2">
          <SectionField
            label="Fecha escritura anterior"
            value={adquisicion.fecha_escritura_anterior}
            onChange={(v) => onChange("fecha_escritura_anterior", v)}
            placeholder="tal como aparece en el documento"
          />
        </div>
        <SectionField
          label="Notaría anterior"
          value={adquisicion.notaria_anterior}
          onChange={(v) => onChange("notaria_anterior", v)}
        />
        <SectionField
          label="Municipio notaría anterior"
          value={adquisicion.municipio_notaria_anterior}
          onChange={(v) => onChange("municipio_notaria_anterior", v)}
        />
        <div className="sm:col-span-2">
          <SectionField
            label="Vendedor / causante / donante original"
            value={adquisicion.vendedor_original}
            onChange={(v) => onChange("vendedor_original", v)}
          />
        </div>
      </div>
    </div>
  );
}

// ─── Tour ─────────────────────────────────────────────────────────────────────

const TOUR_KEY = "easypro_minutas_tour_done";
const MARKED_QA_GENERATED_RESULT_KEY = "easypro_marked_template_qa_generated_result";

// ─── Tour steps ───────────────────────────────────────────────────────────────

const TOUR_STEPS: TourStep[] = [
  {
    targetId: "tour-upload-zone",
    titulo: "Sube tu escritura base",
    texto: "Arrastra o selecciona el .docx de una escritura anterior. La IA la usará como plantilla para generar la nueva minuta.",
  },
  {
    targetId: "tour-btn-analizar",
    titulo: "Análisis automático",
    texto: "La IA extrae personas, inmueble, actos y valores del documento. Solo toma unos segundos.",
  },
  {
    targetId: "tour-validacion-banner",
    titulo: "Semáforo de campos",
    texto: "Verde = listo, amarillo = revisar, rojo = campo crítico faltante. Completa los pendientes antes de generar.",
  },
  {
    targetId: "tour-persona-0",
    titulo: "Datos de los intervinientes",
    texto: "Revisa y corrige nombre, documento, género y estado civil de cada persona. El género actualiza automáticamente la concordancia del documento.",
  },
  {
    targetId: "tour-inmueble-card",
    titulo: "Datos del inmueble",
    texto: "Verifica matrícula, municipio, áreas y linderos. Los selectores de departamento y municipio están encadenados.",
  },
  {
    targetId: "tour-valores-card",
    titulo: "Valores y tarifas",
    texto: "Los derechos notariales se calculan automáticamente según la Res. 2026-000964-6. Puedes ajustar cualquier valor manualmente.",
  },
  {
    targetId: "tour-btn-generar",
    titulo: "Genera la escritura",
    texto: "EasyPro reemplaza los datos, aplica concordancia de género y abre el .docx final en el editor. ¡Listo para firmar!",
  },
];

// ─── Main workspace ───────────────────────────────────────────────────────────

export function NuevaMinutaWorkspace() {
  const router = useRouter();
  const [step, setStep] = useState<0 | 1 | 2>(0);
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isDetectingMarkedTemplate, setIsDetectingMarkedTemplate] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [analisisResult, setAnalisisResult] = useState<MinutaAnalisisResult | null>(null);
  const [markedTemplateResult, setMarkedTemplateResult] = useState<MarkedTemplateDetectResult | null>(null);
  const [personas, setPersonas] = useState<MinutaPersona[]>([]);
  const [inmuebleEdit, setInmuebleEdit] = useState<MinutaInmueble>(EMPTY_INMUEBLE);
  const [notariaEdit, setNotariaEdit] = useState<NotariaEdit>(EMPTY_NOTARIA);
  const [valoresEdit, setValoresEdit] = useState<MinutaValor[]>([]);
  const [decisionesEdit, setDecisionesEdit] = useState<Record<string, boolean | null>>({
    vivienda_familiar: null, patrimonio_familia: null, notificacion_electronica: null,
  });
  const [adquisicionEdit, setAdquisicionEdit] = useState<MinutaAdquisicion>(EMPTY_ADQUISICION);
  const [markedFieldValues, setMarkedFieldValues] = useState<Record<string, string>>({});
  const [markedDocumentName, setMarkedDocumentName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [qaFeedback, setQaFeedback] = useState<string | null>(null);
  const [lastMarkedGeneratedResult, setLastMarkedGeneratedResult] = useState<MinutaGenerarResult | null>(null);
  const [aiSteps, setAiSteps] = useState<AiStep[]>([]);
  const [aiProgress, setAiProgress] = useState(0);
  const [aiModalOpen, setAiModalOpen] = useState(false);
  const [aiModalTitle, setAiModalTitle] = useState('');
  const [aiModalSubtitle, setAiModalSubtitle] = useState('');

  // ── Tour state — lives here so workspace re-renders don't reset it ──────────
  const [tourVisible, setTourVisible] = useState(false);
  const [tourStep, setTourStep] = useState(0);

  useEffect(() => {
    if (!localStorage.getItem(TOUR_KEY)) setTourVisible(true);
  }, []);

  useEffect(() => {
    if (process.env.NODE_ENV === "production" || typeof window === "undefined") return;
    try {
      const raw = window.sessionStorage.getItem(MARKED_QA_GENERATED_RESULT_KEY);
      if (!raw) return;
      const parsed = JSON.parse(raw) as MinutaGenerarResult;
      if (parsed && parsed.download_url) {
        setLastMarkedGeneratedResult(parsed);
      }
    } catch {
      // Ignorar estado inválido en entorno local.
    }
  }, []);

  function handleTourNext() {
    if (tourStep < TOUR_STEPS.length - 1) setTourStep(s => s + 1);
    else handleTourFinish();
  }
  function handleTourPrev() { if (tourStep > 0) setTourStep(s => s - 1); }
  function handleTourSkip() { setTourVisible(false); }
  function handleTourFinish() {
    setTourVisible(false);
    localStorage.setItem(TOUR_KEY, "1");
  }
  function handleTourRelaunch() { setTourStep(0); setTourVisible(true); }
  // ────────────────────────────────────────────────────────────────────────────

  function updateStep(id: string, status: AiStep['status'], description?: string) {
    setAiSteps(prev => prev.map(s => s.id === id ? { ...s, status, ...(description ? { description } : {}) } : s));
  }

  function handleDragOver(e: React.DragEvent) { e.preventDefault(); setIsDragging(true); }
  function handleDragLeave() { setIsDragging(false); }
  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    setIsDragging(false);
    const f = e.dataTransfer.files[0];
    if (f && f.name.endsWith(".docx")) {
      setFile(f);
      setAnalisisResult(null);
      setMarkedTemplateResult(null);
      setMarkedFieldValues({});
      setMarkedDocumentName("");
      setPersonas([]);
      setInmuebleEdit(EMPTY_INMUEBLE);
      setNotariaEdit(EMPTY_NOTARIA);
      setValoresEdit([]);
      setDecisionesEdit({ vivienda_familiar: null, patrimonio_familia: null, notificacion_electronica: null });
      setAdquisicionEdit(EMPTY_ADQUISICION);
      setError(null);
    } else setError("Solo se aceptan archivos .docx");
  }
  function handleFileSelected(f: File) {
    if (!f.name.endsWith(".docx")) { setError("Solo se aceptan archivos .docx"); return; }
    setFile(f);
    setAnalisisResult(null);
    setMarkedTemplateResult(null);
    setMarkedFieldValues({});
    setMarkedDocumentName("");
    setPersonas([]);
    setInmuebleEdit(EMPTY_INMUEBLE);
    setNotariaEdit(EMPTY_NOTARIA);
    setValoresEdit([]);
    setDecisionesEdit({ vivienda_familiar: null, patrimonio_familia: null, notificacion_electronica: null });
    setAdquisicionEdit(EMPTY_ADQUISICION);
    setError(null);
  }
  function clearFile() {
    setFile(null);
    setAnalisisResult(null);
    setMarkedTemplateResult(null);
    setMarkedFieldValues({});
    setMarkedDocumentName("");
    setPersonas([]);
    setInmuebleEdit(EMPTY_INMUEBLE);
    setNotariaEdit(EMPTY_NOTARIA);
    setValoresEdit([]);
    setDecisionesEdit({ vivienda_familiar: null, patrimonio_familia: null, notificacion_electronica: null });
    setAdquisicionEdit(EMPTY_ADQUISICION);
    setError(null);
  }

  async function handleDetectMarkedTemplate() {
    if (!file) return;
    setError(null);
    setIsDetectingMarkedTemplate(true);
    try {
      const result = await detectMarkedTemplate(file);
      setMarkedTemplateResult(result);
      setAnalisisResult(null);
      setPersonas([]);
      setInmuebleEdit(EMPTY_INMUEBLE);
      setNotariaEdit(EMPTY_NOTARIA);
      setValoresEdit([]);
      setDecisionesEdit({ vivienda_familiar: null, patrimonio_familia: null, notificacion_electronica: null });
      setAdquisicionEdit(EMPTY_ADQUISICION);
      const effectiveFields = getEffectiveMarkedTemplateFields(result.fields);
      setMarkedFieldValues(
        Object.fromEntries(effectiveFields.map((field) => [field.key, ""]))
      );
      setMarkedDocumentName("");
      setStep(1);
    } catch (err) {
      const message = err instanceof Error && err.message && err.message !== "Failed to fetch"
        ? err.message
        : "No fue posible detectar los campos marcados. Verifica la conexion y la sesion.";
      setError(message);
    } finally {
      setIsDetectingMarkedTemplate(false);
    }
  }

  async function handleAnalizar() {
    if (!file) return;
    setError(null);
    setIsAnalyzing(true);
    setMarkedTemplateResult(null);
    setMarkedFieldValues({});
    setAiModalTitle('Analizando documento');
    setAiModalSubtitle('Esto puede tomar hasta 30 segundos');
    setAiSteps([
      { id: 'upload', label: 'Documento recibido', description: `${file.name} · ${(file.size / 1024).toFixed(0)} KB`, status: 'done' },
      { id: 'detect', label: 'Detectando tipo de acto…', description: 'Clasificando entre B1 y B2', status: 'active' },
      { id: 'personas', label: 'Extrayendo personas', description: 'Compradores, vendedores, entidades', status: 'pending' },
      { id: 'inmueble', label: 'Datos del inmueble y valores', description: 'Municipio, precio, escritura', status: 'pending' },
    ]);
    setAiProgress(25);
    setAiModalOpen(true);
    try {
      const result = await analyzeMinuta(file);
      updateStep('detect', 'done', `Tipo detectado: ${result.modo_detectado ?? 'B2'}`);
      updateStep('personas', 'active');
      setAiProgress(60);
      await new Promise(r => setTimeout(r, 600));
      updateStep('personas', 'done', `${result.datos?.personas?.length ?? 0} personas encontradas`);
      updateStep('inmueble', 'active');
      setAiProgress(85);
      await new Promise(r => setTimeout(r, 500));
      updateStep('inmueble', 'done', 'Inmueble y valores cargados');
      setAiProgress(100);
      await new Promise(r => setTimeout(r, 400));
      setAiModalOpen(false);
      setAnalisisResult(result);
      setMarkedTemplateResult(null);
      setMarkedFieldValues({});
      setPersonas((result.datos.personas ?? []).map((p) => ({ ...p })));
      const inmuebleRaw = (result.datos.inmueble ?? {}) as Partial<MinutaInmueble>;
      const TIPOS_INMUEBLE_MAP: Record<string, string> = {
        'apartamento': 'Apartamento', 'casa': 'Casa', 'local': 'Local',
        'oficina': 'Oficina', 'lote': 'Lote', 'bodega': 'Bodega',
        'parqueadero': 'Parqueadero', 'deposito': 'Depósito', 'depósito': 'Depósito',
      };
      const tipoNormalizado = inmuebleRaw.tipo
        ? TIPOS_INMUEBLE_MAP[inmuebleRaw.tipo.toLowerCase().trim()] ?? inmuebleRaw.tipo
        : null;
      const municipioDetectado = inmuebleRaw.municipio ?? '';
      const departamentoDetectado =
        inmuebleRaw.departamento ??
        getDepartamentoByMunicipio(municipioDetectado) ??
        '';
      setInmuebleEdit({
        ...EMPTY_INMUEBLE,
        ...inmuebleRaw,
        tipo: tipoNormalizado,
        municipio: municipioDetectado || null,
        departamento: departamentoDetectado || null,
      });
      const fechasRaw = (result.datos as Record<string, unknown>).fechas as Record<string, unknown> | null | undefined;
      const fechaRaw = fechasRaw?.fecha_otorgamiento;
      const fechaOtorgamiento = typeof fechaRaw === "string" ? fechaRaw : "";
      setNotariaEdit({ ...EMPTY_NOTARIA, ...(result.datos.notaria ?? {}), fecha_otorgamiento: fechaOtorgamiento });
      setValoresEdit((result.datos.valores ?? []).map((v) => ({
        ...v,
        texto_en_documento:
          v.monto_numerico != null && v.monto_numerico > 0
            ? numeroALetras(v.monto_numerico)
            : v.texto_en_documento,
      })));
      setDecisionesEdit({
        vivienda_familiar: null,
        patrimonio_familia: null,
        notificacion_electronica: null,
        ...(result.datos.decisiones ?? {}),
      });
      setAdquisicionEdit({ ...EMPTY_ADQUISICION, ...(result.datos.adquisicion ?? {}) });
    } catch (err) {
      setAiModalOpen(false);
      setError(err instanceof Error ? err.message : "Error al analizar el documento.");
    } finally {
      setIsAnalyzing(false);
    }
  }

  function updatePersona(idx: number, field: keyof MinutaPersona, value: string) {
    setPersonas((prev) => prev.map((p, i) => i === idx ? { ...p, [field]: value || null } : p));
  }
  function removePersona(idx: number) { setPersonas((prev) => prev.filter((_, i) => i !== idx)); }
  function addPersona() { setPersonas((prev) => [...prev, emptyPersona(`persona_${prev.length + 1}`)]); }

  function updateInmueble(field: keyof MinutaInmueble, value: string) {
    setInmuebleEdit((prev) => ({ ...prev, [field]: value || null }));
  }
  function updateNotaria(field: keyof NotariaEdit, value: string) {
    setNotariaEdit((prev) => ({ ...prev, [field]: value || null }));
  }
  function updateValor(idx: number, value: string) {
    const parsed = parseInt(value.replace(/\D/g, ""), 10);
    setValoresEdit((prev) =>
      prev.map((v, i) => {
        if (i !== idx) return v;
        return {
          ...v,
          monto_numerico: isNaN(parsed) ? 0 : parsed,
          texto_en_documento: parsed > 0 ? numeroALetras(parsed) : v.texto_en_documento,
        };
      })
    );
  }
  function updateValorTexto(idx: number, value: string) {
    setValoresEdit((prev) =>
      prev.map((v, i) => i === idx ? { ...v, texto_en_documento: value || null } : v)
    );
  }
  function updateDecision(key: string, value: boolean | null) {
    setDecisionesEdit((prev) => ({ ...prev, [key]: value }));
  }
  function updateAdquisicion(field: keyof MinutaAdquisicion, value: string) {
    setAdquisicionEdit((prev) => ({ ...prev, [field]: value || null }));
  }

  function updateMarkedFieldValue(key: string, value: string) {
    setMarkedFieldValues((prev) => ({ ...prev, [key]: normalizeDropdownFieldValue(value) }));
  }

  async function copyTextToClipboard(text: string) {
    if (typeof navigator !== "undefined" && navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text);
      return;
    }

    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.setAttribute("readonly", "true");
    textarea.style.position = "absolute";
    textarea.style.left = "-9999px";
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand("copy");
    document.body.removeChild(textarea);
  }

  function applyJagguaBancoBogotaQaPreset() {
    setMarkedFieldValues((prev) => {
      const next = { ...prev };
      markedTemplateFields.forEach((field) => {
        const presetValue = JAGGUA_BANCO_BOGOTA_QA_VALUES_NORMALIZED[markedFieldKey(field)];
        if (presetValue == null) return;
        next[field.key] = isMarkedMoneyField(field) ? parseMarkedCOP(presetValue) : normalizeDropdownFieldValue(presetValue);
      });
      return withDerivedMarkedLetterValues(markedTemplateFields, next);
    });
  }

  async function handleCopyMarkedEmptyFields() {
    const emptyFields = markedTemplateFields
      .filter((field) => !String(markedFieldValues[field.key] ?? "").trim())
      .map((field) => ({
        key: field.key,
        label: field.label,
        section: field.section,
      }));

    const output = emptyFields.length > 0
      ? emptyFields.map((field) => `${field.key} | ${field.label} | ${field.section}`).join("\n")
      : "Sin campos vacíos detectados.";

    try {
      await copyTextToClipboard(output);
      if (process.env.NODE_ENV !== "production") {
        console.table(emptyFields);
      }
      setQaFeedback(
        emptyFields.length > 0
          ? `Se copiaron ${emptyFields.length} campos vacíos al portapapeles.`
          : "No hay campos vacíos en la plantilla detectada."
      );
    } catch (issue) {
      setError(issue instanceof Error ? issue.message : "No fue posible copiar la lista de campos vacíos.");
    }
  }

  async function handleCopyMarkedCurrentPayload() {
    const payload = getSanitizedMarkedFieldValues(markedTemplateFields);
    try {
      await copyTextToClipboard(JSON.stringify(payload, null, 2));
      if (process.env.NODE_ENV !== "production") {
        console.table(payload);
        console.table(getDerivedMarkedMoneyLetterDebugRows(payload, markedTemplateFields));
      }
      setQaFeedback("Payload actual copiado al portapapeles.");
    } catch (issue) {
      setError(issue instanceof Error ? issue.message : "No fue posible copiar el payload actual.");
    }
  }

  async function handleDownloadGeneratedQaDocx() {
    if (!lastMarkedGeneratedResult?.download_url) {
      setError("Todavía no hay un DOCX generado disponible para descargar.");
      return;
    }

    try {
      const response = await fetch(lastMarkedGeneratedResult.download_url, {
        method: "GET",
        credentials: "include",
      });
      if (!response.ok) {
        throw new Error("No fue posible descargar el DOCX generado.");
      }
      const blob = await response.blob();
      const blobUrl = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = blobUrl;
      link.download = lastMarkedGeneratedResult.filename || "minuta_generada.docx";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.setTimeout(() => URL.revokeObjectURL(blobUrl), 60_000);
      setQaFeedback("DOCX generado descargado para QA.");
    } catch (issue) {
      setError(issue instanceof Error ? issue.message : "No fue posible descargar el DOCX generado.");
    }
  }

  function getSanitizedMarkedFieldValues(fields: MarkedTemplateField[]) {
    const valuesWithDerivedLetters = withDerivedMarkedLetterValues(fields, markedFieldValues);
    const baseValues = Object.fromEntries(
      fields.map((field) => {
        const value = valuesWithDerivedLetters[field.key] ?? "";
        if (isMarkedDropdownField(field)) {
          return [field.key, normalizeDropdownFieldValue(value)];
        }
        if (isMarkedMoneyField(field)) {
          return [field.key, value ? formatMarkedCOP(value) : ""];
        }
        return [field.key, value];
      })
    );
    return applyDerivedMarkedMoneyLettersToValues(baseValues, fields);
  }

  async function handleGenerar() {
    if (!file) return;

    if (markedTemplateResult && !analisisResult) {
      if (process.env.NODE_ENV !== "production") {
        console.log("### MARKED GENERATE CLICK ###");
      }
      setError(null);
      setQaFeedback(null);
      setIsGenerating(true);
      setAiModalTitle("Generando documento sin IA");
      setAiModalSubtitle("Aplicando reemplazos determinísticos");
      setAiSteps([
        {
          id: "prepare",
          label: "Documento recibido",
          description: `${file.name} · ${(file.size / 1024).toFixed(0)} KB`,
          status: "done",
        },
        {
          id: "replace",
          label: "Aplicando reemplazos sin IA",
          description: "Reemplazando {{CAMPO}} y variantes detectadas sin IA",
          status: "active",
        },
        {
          id: "save",
          label: "Guardando documento",
          description: "Subiendo el DOCX resultante a storage",
          status: "pending",
        },
        {
          id: "open",
          label: "Abriendo editor",
          description: "Redirigiendo a OnlyOffice",
          status: "pending",
        },
      ]);
      setAiProgress(20);
      setAiModalOpen(true);
      try {
        await new Promise((r) => setTimeout(r, 450));
        setAiProgress(45);
        const sanitizedValues = getSanitizedMarkedFieldValues(markedTemplateFields);
        if (process.env.NODE_ENV !== "production") {
          console.table({
            valor_de_la_venta_en_numeros: sanitizedValues.valor_de_la_venta_en_numeros ?? "",
            valor_apartamento_en_letras: sanitizedValues.valor_apartamento_en_letras ?? "",
            en_numeros_cuota_inicial: sanitizedValues.en_numeros_cuota_inicial ?? "",
            en_letras_cuota_inicial: sanitizedValues.en_letras_cuota_inicial ?? "",
            valor_del_acto_de_la_hipoteca: sanitizedValues.valor_del_acto_de_la_hipoteca ?? "",
            valor_del_acto_de_la_hipoteca_en_letras: sanitizedValues.valor_del_acto_de_la_hipoteca_en_letras ?? "",
            origen_cuota_inicial: sanitizedValues.origen_cuota_inicial ?? "",
          });
        }
        const result = await generateMarkedTemplate(file, sanitizedValues, markedTemplateFields, markedDocumentName);
        if (process.env.NODE_ENV !== "production") {
          console.log("### MARKED GENERATE RESPONSE ###", result);
        }
        setLastMarkedGeneratedResult(result);
        if (process.env.NODE_ENV !== "production" && typeof window !== "undefined") {
          window.sessionStorage.setItem(MARKED_QA_GENERATED_RESULT_KEY, JSON.stringify(result));
        }
        updateStep("replace", "done", "Reemplazos aplicados");
        updateStep("save", "active");
        setAiProgress(80);
        await new Promise((r) => setTimeout(r, 400));
        updateStep("save", "done", "Documento guardado correctamente");
        updateStep("open", "active");
        setAiProgress(95);
        await new Promise((r) => setTimeout(r, 250));
        setAiProgress(100);
        setAiModalOpen(false);
        router.push(result.onlyoffice_path);
      } catch (err) {
        setAiModalOpen(false);
        setError(err instanceof Error ? err.message : "Error al generar la minuta.");
        setIsGenerating(false);
      }
      return;
    }

    if (!analisisResult) return;
    setError(null);
    setIsGenerating(true);
    setAiModalTitle('Generando minuta');
    setAiModalSubtitle('Aplicando reemplazos y concordancia de género');
    setAiSteps([
      { id: 'validate', label: 'Datos validados', description: 'Personas, inmueble y notaría', status: 'done' },
      { id: 'replace', label: 'Aplicando reemplazos', description: 'Sustituyendo campos en el documento', status: 'active' },
      { id: 'concordancia', label: 'Concordancia de género…', description: 'Ajustando artículos y pronombres con IA', status: 'pending' },
      { id: 'upload', label: 'Guardando documento', description: 'Subiendo a Supabase Storage', status: 'pending' },
    ]);
    setAiProgress(20);
    setAiModalOpen(true);
    try {
      const datosNuevos = {
        ...analisisResult.datos,
        personas,
        inmueble: inmuebleEdit,
        valores: valoresEdit,
        notaria: {
          nombre_notaria: notariaEdit.nombre_notaria,
          municipio_notaria: notariaEdit.municipio_notaria,
          numero_escritura: notariaEdit.numero_escritura,
        },
        fechas: { fecha_otorgamiento: notariaEdit.fecha_otorgamiento },
        decisiones: decisionesEdit,
        adquisicion: adquisicionEdit,
      };
      await new Promise(r => setTimeout(r, 800));
      updateStep('replace', 'done', 'Reemplazos aplicados');
      updateStep('concordancia', 'active');
      setAiProgress(55);
      const result = await generateMinuta(
        file,
        { ...analisisResult.datos, personas: analisisResult.datos.personas },
        datosNuevos as unknown as MinutaDatos,
      );
      updateStep('concordancia', 'done', 'Artículos y pronombres ajustados');
      updateStep('upload', 'active');
      setAiProgress(85);
      await new Promise(r => setTimeout(r, 500));
      updateStep('upload', 'done', 'Documento guardado correctamente');
      setAiProgress(100);
      await new Promise(r => setTimeout(r, 400));
      setAiModalOpen(false);
      router.push(result.onlyoffice_path);
    } catch (err) {
      setAiModalOpen(false);
      setError(err instanceof Error ? err.message : "Error al generar la minuta.");
      setIsGenerating(false);
    }
  }

  const canAnalyze = !!file && !isAnalyzing && !isDetectingMarkedTemplate;
  const canDetectMarkedTemplate = !!file && !isDetectingMarkedTemplate && !isAnalyzing;
  const isMarkedTemplateMode = !!markedTemplateResult && !analisisResult;
  const markedTemplateFields = getEffectiveMarkedTemplateFields(markedTemplateResult?.fields ?? []);
  const markedPendingCount = markedTemplateFields.filter((field) => !String(markedFieldValues[field.key] ?? "").trim()).length;
  const markedAmbiguousCount = markedTemplateFields.filter((field) => isMarkedAmbiguousField(field)).length;
  const canGenerate = isMarkedTemplateMode
    ? !!file && !!markedTemplateResult && !isGenerating
    : !!analisisResult && personas.length > 0 && !isGenerating;

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-primary">Nueva minuta</h1>
        <p className="text-sm text-muted mt-1">
          Sube un .docx, revisa los datos detectados y genera la minuta adaptada.
        </p>
      </div>

      <StepBar current={step} labels={isMarkedTemplateMode ? MARKED_STEPS : IA_STEPS} />

      {error && (
        <div className="ep-kpi-critical rounded-xl px-4 py-3 flex items-start gap-3 mb-6">
          <AlertCircle size={16} className="text-rose-500 mt-0.5 shrink-0" />
          <p className="text-sm text-rose-700">{error}</p>
          <button onClick={() => setError(null)} className="ml-auto text-rose-400 hover:text-rose-600">
            <X size={14} />
          </button>
        </div>
      )}

      {qaFeedback && process.env.NODE_ENV !== "production" && (
        <div className="ep-kpi-success rounded-xl px-4 py-3 flex items-start gap-3 mb-6">
          <CheckCircle2 size={16} className="text-emerald-600 mt-0.5 shrink-0" />
          <p className="text-sm">{qaFeedback}</p>
          <button onClick={() => setQaFeedback(null)} className="ml-auto text-emerald-500 hover:text-emerald-700">
            <X size={14} />
          </button>
        </div>
      )}

      {/* ── PASO 1 ── */}
      {step === 0 && (
        <div className="space-y-5">
          <div id="tour-upload-zone">
            <UploadZone
              file={file} isDragging={isDragging}
              onFile={handleFileSelected} onDragOver={handleDragOver}
              onDragLeave={handleDragLeave} onDrop={handleDrop} onClear={clearFile}
            />
          </div>

          {file && (
            <div className="grid gap-3 sm:grid-cols-2">
            <button
              id="tour-btn-analizar"
              onClick={handleAnalizar} disabled={!canAnalyze}
              className={[
                "w-full h-12 rounded-2xl font-semibold text-sm flex items-center justify-center gap-2 transition-all",
                canAnalyze
                  ? "bg-primary text-white hover:opacity-90"
                  : "bg-panel-soft text-soft cursor-not-allowed",
              ].join(" ")}
            >
              {isAnalyzing ? (
                <><Loader2 size={16} className="animate-spin" /> Analizando · ~20 s</>
              ) : (
                <><FileText size={16} /> Analizar con IA</>
              )}
            </button>
            <button
              onClick={handleDetectMarkedTemplate}
              disabled={!canDetectMarkedTemplate}
              className={[
                "w-full h-12 rounded-2xl font-semibold text-sm flex items-center justify-center gap-2 transition-all",
                canDetectMarkedTemplate
                  ? "bg-emerald-600 text-white hover:opacity-90"
                  : "bg-panel-soft text-soft cursor-not-allowed",
              ].join(" ")}
            >
              {isDetectingMarkedTemplate ? (
                <><Loader2 size={16} className="animate-spin" /> Detectando campos</>
              ) : (
                <><FileText size={16} /> Detectar campos marcados</>
              )}
            </button>
          </div>
          )}

          {analisisResult && <AnalysisSummary result={analisisResult} />}
          {markedTemplateResult && <MarkedTemplateSummary result={markedTemplateResult} />}

          {analisisResult && (
            <button
              onClick={() => setStep(1)}
              className="w-full h-12 rounded-2xl bg-primary text-white font-semibold text-sm flex items-center justify-center gap-2 hover:opacity-90 transition-all"
            >
              Revisar personas detectadas <ChevronRight size={16} />
            </button>
          )}
          {markedTemplateResult && (
            <button
              onClick={() => setStep(1)}
              className="w-full h-12 rounded-2xl bg-emerald-600 text-white font-semibold text-sm flex items-center justify-center gap-2 hover:opacity-90 transition-all"
            >
              Diligenciar campos detectados <ChevronRight size={16} />
            </button>
          )}
        </div>
      )}

      {/* ── PASO 2 ── */}
      {step === 1 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between mb-2">
            <p className={isMarkedTemplateMode ? "hidden" : "text-sm text-muted"}>
              {personas.length} persona{personas.length !== 1 ? "s" : ""} ·
              Campos en amarillo requieren completarse.
            </p>
            {isMarkedTemplateMode && markedTemplateResult && (
              <p className="text-sm text-muted">
                {markedTemplateResult.total_fields} campos detectados · Plantilla marcada sin IA.
              </p>
            )}
            <button onClick={() => setStep(0)} className="text-xs text-soft hover:text-primary underline underline-offset-2">
              Volver
            </button>
          </div>

          {isMarkedTemplateMode && markedTemplateResult && (
            <MarkedFieldsForm
              fields={markedTemplateFields}
              values={markedFieldValues}
              documentName={markedDocumentName}
              onDocumentNameChange={setMarkedDocumentName}
              onChange={updateMarkedFieldValue}
              onGenerate={handleGenerar}
              onContinueToSummary={() => setStep(2)}
              onApplyQaPreset={applyJagguaBancoBogotaQaPreset}
              onCopyEmptyFields={() => void handleCopyMarkedEmptyFields()}
              onCopyCurrentPayload={() => void handleCopyMarkedCurrentPayload()}
              onDownloadGeneratedQaDocx={() => void handleDownloadGeneratedQaDocx()}
              showQaPresetButton={process.env.NODE_ENV !== "production"}
              showGeneratedQaDownloadButton={process.env.NODE_ENV !== "production" && Boolean(lastMarkedGeneratedResult?.download_url)}
              isGenerating={isGenerating}
              showPendingWarning={markedPendingCount > 0}
              showAmbiguousWarning={markedAmbiguousCount > 0}
            />
          )}

          <div className={analisisResult ? "space-y-4" : "hidden"}>

          {/* ── Banner de validación notarial ── */}
          {analisisResult?.validacion && !analisisResult.validacion.error && (
            <div id="tour-validacion-banner" className={[
              "flex items-center gap-3 px-4 py-3 rounded-xl border mb-4",
              analisisResult.validacion.resumen.nivel_confianza === "alto"
                ? "bg-success-bg border-emerald-200"
                : analisisResult.validacion.resumen.nivel_confianza === "medio"
                ? "bg-amber-50 border-amber-200"
                : "bg-rose-50 border-rose-200",
            ].join(" ")}>
              <div className="flex-1">
                <p className="text-[13px] font-medium text-ink">
                  {analisisResult.validacion.resumen.listo_para_generar
                    ? "Documento validado — listo para generar"
                    : "Revisar campos antes de generar"}
                </p>
                <p className="text-[12px] text-soft mt-0.5">
                  {analisisResult.validacion.resumen.campos_ok} correctos ·{" "}
                  {analisisResult.validacion.resumen.campos_advertencia} advertencias ·{" "}
                  {analisisResult.validacion.resumen.campos_faltantes} faltantes ·{" "}
                  {analisisResult.validacion.resumen.campos_inferidos} inferidos
                </p>
              </div>
              <span className={[
                "text-[11px] font-semibold px-2 py-1 rounded-lg",
                analisisResult.validacion.resumen.nivel_confianza === "alto"
                  ? "bg-emerald-100 text-emerald-700"
                  : analisisResult.validacion.resumen.nivel_confianza === "medio"
                  ? "bg-amber-100 text-amber-700"
                  : "bg-rose-100 text-rose-700",
              ].join(" ")}>
                Confianza {analisisResult.validacion.resumen.nivel_confianza}
              </span>
            </div>
          )}

          {/* ── Alertas críticas ── */}
          {(analisisResult?.validacion?.alertas_criticas?.length ?? 0) > 0 && (
            <div className="mb-4 flex flex-col gap-1.5">
              {analisisResult!.validacion!.alertas_criticas.map((alerta, i) => (
                <div key={i} className="flex items-start gap-2 px-3 py-2 bg-rose-50 border border-rose-200 rounded-lg">
                  <span className="text-rose-500 text-[12px] mt-0.5">⚠</span>
                  <p className="text-[12px] text-rose-700">{alerta}</p>
                </div>
              ))}
            </div>
          )}

          {/* ── Inferencias aplicadas ── */}
          {(analisisResult?.validacion?.inferencias_aplicadas?.length ?? 0) > 0 && (
            <div className="mb-4 flex flex-col gap-1.5">
              {analisisResult!.validacion!.inferencias_aplicadas.map((inf, i) => (
                <div key={i} className="flex items-start gap-2 px-3 py-2 bg-blue-50 border border-blue-200 rounded-lg">
                  <span className="text-blue-500 text-[12px] mt-0.5">→</span>
                  <p className="text-[12px] text-blue-700">{inf}</p>
                </div>
              ))}
            </div>
          )}

          {personas.map((p, i) => (
            <PersonaCard
              key={i} persona={p} index={i}
              id={i === 0 ? "tour-persona-0" : undefined}
              onChange={(field, value) => updatePersona(i, field, value)}
              onRemove={() => removePersona(i)}
            />
          ))}

          <button
            onClick={addPersona}
            className="w-full h-11 rounded-2xl border-2 border-dashed border-line-strong text-sm text-muted flex items-center justify-center gap-2 hover:border-primary hover:text-primary transition-all"
          >
            <Plus size={15} /> Agregar persona manualmente
          </button>

          <div id="tour-inmueble-card">
            <InmuebleCard inmueble={inmuebleEdit} onChange={updateInmueble} />
          </div>

          <AdquisicionCard adquisicion={adquisicionEdit} onChange={updateAdquisicion} />

          <NotariaCard notaria={notariaEdit} onChange={updateNotaria} />

          <div id="tour-valores-card">
            <ValoresCard valores={valoresEdit} onChangeMonto={updateValor} onChangeTexto={updateValorTexto} />
          </div>

          <DecisionesCard decisiones={decisionesEdit} onChange={updateDecision} />

          <button
            onClick={() => setStep(2)} disabled={!canGenerate}
            className={[
              "w-full h-12 rounded-2xl font-semibold text-sm flex items-center justify-center gap-2 transition-all",
              canGenerate ? "bg-primary text-white hover:opacity-90" : "bg-panel-soft text-soft cursor-not-allowed",
            ].join(" ")}
          >
            Continuar a generar <ChevronRight size={16} />
          </button>

          </div>
        </div>
      )}

      {/* ── PASO 3 ── */}
      {step === 2 && (
        <div className="space-y-5">
          <div className="flex items-center justify-between">
            <p className="text-sm text-muted">Listo para generar con los datos revisados.</p>
            <button onClick={() => setStep(1)} className="text-xs text-soft hover:text-primary underline underline-offset-2">
              Volver
            </button>
          </div>

          <div className="ep-card rounded-2xl p-5 space-y-4">
            <h3 className="font-semibold text-sm text-ink">Resumen de la operacion</h3>
            {isMarkedTemplateMode && markedTemplateResult && (
              <p className="text-sm text-muted">
                {markedTemplateResult.total_fields} campos detectados · plantilla marcada sin IA.
              </p>
            )}
            <div className="grid grid-cols-2 gap-3 text-sm">
              {[
                ["Archivo base", file?.name ?? "-"],
                ["Personas", String(personas.length)],
                ["Modo origen", analisisResult?.modo_detectado === "B2" ? "B2 - Diligenciada" : "B1 - Plantilla"],
                ["Valores en doc", String(valoresEdit.length)],
              ].map(([k, v]) => (
                <div key={k}>
                  <span className="text-soft">{k}: </span>
                  <span className="font-medium text-ink">{v}</span>
                </div>
              ))}
            </div>

            <div>
              <p className="text-xs font-semibold text-muted uppercase tracking-wider mb-2">
                Personas a incluir
              </p>
              <div className="space-y-1.5">
                {personas.map((p, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm">
                    <span className="w-5 h-5 rounded-full bg-panel-soft border border-line text-[10px] font-bold flex items-center justify-center text-muted">
                      {i + 1}
                    </span>
                    <span className="text-soft text-xs">{p.rol.replace(/_/g, " ")}</span>
                    <ChevronRight size={12} className="text-line-strong" />
                    <span className="font-medium text-ink">
                      {p.nombre_completo ?? <span className="text-amber-600 italic">sin nombre</span>}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {inmuebleEdit.matricula_inmobiliaria && (
              <div>
                <p className="text-xs font-semibold text-muted uppercase tracking-wider mb-1">
                  Inmueble
                </p>
                <p className="text-sm text-ink">
                  {[
                    inmuebleEdit.conjunto_o_edificio,
                    inmuebleEdit.numero && `Nro. ${inmuebleEdit.numero}`,
                    inmuebleEdit.matricula_inmobiliaria && `Mat. ${inmuebleEdit.matricula_inmobiliaria}`,
                    inmuebleEdit.municipio,
                  ].filter(Boolean).join(" · ")}
                </p>
              </div>
            )}
          </div>

          <button
            id="tour-btn-generar"
            type="button"
            onClick={handleGenerar} disabled={!canGenerate || isGenerating}
            className={[
              "w-full h-14 rounded-2xl font-bold text-base flex items-center justify-center gap-3 transition-all",
              canGenerate && !isGenerating
                ? "bg-primary text-white hover:opacity-90 shadow-lg"
                : "bg-panel-soft text-soft cursor-not-allowed",
            ].join(" ")}
          >
            {isGenerating ? (
              <><Loader2 size={18} className="animate-spin" /> Generando minuta</>
            ) : isMarkedTemplateMode ? (
              <><ExternalLink size={18} /> Generar documento</>
            ) : (
              <><ExternalLink size={18} /> Generar y abrir en editor</>
            )}
          </button>
        </div>
      )}

      {/* Botón fijo para relanzar el tour — z-[9997] queda debajo del overlay cuando el tour está activo */}
      <button
        onClick={handleTourRelaunch}
        title="Ver tour guiado"
        aria-label="Ver tour guiado"
        className="fixed bottom-6 right-6 z-[9997] w-11 h-11 rounded-full bg-primary text-white flex items-center justify-center shadow-lg hover:opacity-90 transition-opacity"
      >
        <HelpCircle size={20} />
      </button>

      <AiProgressModal
        open={aiModalOpen}
        title={aiModalTitle}
        subtitle={aiModalSubtitle}
        steps={aiSteps}
        progress={aiProgress}
      />

      <MinutasTour
        steps={TOUR_STEPS}
        visible={tourVisible}
        currentStep={tourStep}
        onNext={handleTourNext}
        onPrev={handleTourPrev}
        onSkip={handleTourSkip}
        onFinish={handleTourFinish}
        onRelaunch={handleTourRelaunch}
      />
    </div>
  );
}

