"use client";

import { useRef, useState } from "react";
import { useRouter } from "next/navigation";
import {
  AlertCircle, CheckCircle2, ChevronRight, ExternalLink,
  FileText, Loader2, Plus, Upload, X,
} from "lucide-react";
import {
  analyzeMinuta, generateMinuta, emptyPersona,
  type MinutaAnalisisResult, type MinutaPersona,
  type MinutaInmueble, type MinutaNotaria, type MinutaValor, type MinutaDatos,
} from "@/lib/minuta";
import { TIPOS_DOCUMENTO, NOTAS_LINDEROS, getEstadosCiviles } from "@/lib/listas-notariales";
import { AiProgressModal, type AiStep } from "@/components/ui/ai-progress-modal";

// ─── Constants ────────────────────────────────────────────────────────────────

const STEPS = ["Subir documento", "Revisar personas", "Generar"];

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
  if (n === 0) return "CERO PESOS MONEDA CORRIENTE";
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
  return partes.join(" ") + " PESOS MONEDA CORRIENTE";
}

// ─── Step indicator ───────────────────────────────────────────────────────────

function StepBar({ current }: { current: number }) {
  return (
    <div className="flex items-center gap-0 mb-8">
      {STEPS.map((label, i) => (
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
          {i < STEPS.length - 1 && (
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
          <option value="">seleccionar</option>
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
}: {
  persona: MinutaPersona;
  index: number;
  onChange: (field: keyof MinutaPersona, value: string) => void;
  onRemove: () => void;
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
    <div className="ep-card rounded-2xl overflow-hidden">
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

      <div className="p-5 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div className="sm:col-span-2 lg:col-span-3">
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
              <option value="">Seleccionar...</option>
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

        {/* Fila 4 — municipio + departamento + propiedad horizontal */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <SectionField
            label="Municipio"
            value={inmueble.municipio}
            onChange={(v) => onChange("municipio", v)}
          />
          <SectionField
            label="Departamento"
            value={inmueble.departamento}
            onChange={(v) => onChange("departamento", v)}
          />
          <label className="grid gap-1">
            <span className="text-xs font-medium text-muted">Propiedad horizontal</span>
            <select
              value={inmueble.propiedad_horizontal ?? ""}
              onChange={(e) => onChange("propiedad_horizontal", e.target.value)}
              className={cls(inmueble.propiedad_horizontal) + " ep-select"}
            >
              <option value="">Seleccionar...</option>
              <option value="SI">Sí</option>
              <option value="NO">No</option>
            </select>
          </label>
        </div>

        {/* Fila 5 — matrícula + cédula catastral + código catastral */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
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
        <SectionField
          label="Municipio notaría"
          value={String(notaria.municipio_notaria ?? "")}
          onChange={(v) => onChange("municipio_notaria", v)}
        />
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
      <SectionField
        label="Monto ($)"
        value={String(val.monto_numerico ?? "")}
        onChange={(v) => onChangeMonto(idx, v)}
      />
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

// ─── Main workspace ───────────────────────────────────────────────────────────

export function NuevaMinutaWorkspace() {
  const router = useRouter();
  const [step, setStep] = useState<0 | 1 | 2>(0);
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [analisisResult, setAnalisisResult] = useState<MinutaAnalisisResult | null>(null);
  const [personas, setPersonas] = useState<MinutaPersona[]>([]);
  const [inmuebleEdit, setInmuebleEdit] = useState<MinutaInmueble>(EMPTY_INMUEBLE);
  const [notariaEdit, setNotariaEdit] = useState<NotariaEdit>(EMPTY_NOTARIA);
  const [valoresEdit, setValoresEdit] = useState<MinutaValor[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [aiSteps, setAiSteps] = useState<AiStep[]>([]);
  const [aiProgress, setAiProgress] = useState(0);
  const [aiModalOpen, setAiModalOpen] = useState(false);
  const [aiModalTitle, setAiModalTitle] = useState('');
  const [aiModalSubtitle, setAiModalSubtitle] = useState('');

  function updateStep(id: string, status: AiStep['status'], description?: string) {
    setAiSteps(prev => prev.map(s => s.id === id ? { ...s, status, ...(description ? { description } : {}) } : s));
  }

  function handleDragOver(e: React.DragEvent) { e.preventDefault(); setIsDragging(true); }
  function handleDragLeave() { setIsDragging(false); }
  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    setIsDragging(false);
    const f = e.dataTransfer.files[0];
    if (f && f.name.endsWith(".docx")) { setFile(f); setError(null); }
    else setError("Solo se aceptan archivos .docx");
  }
  function handleFileSelected(f: File) {
    if (!f.name.endsWith(".docx")) { setError("Solo se aceptan archivos .docx"); return; }
    setFile(f); setError(null);
  }
  function clearFile() {
    setFile(null);
    setAnalisisResult(null);
    setPersonas([]);
    setInmuebleEdit(EMPTY_INMUEBLE);
    setNotariaEdit(EMPTY_NOTARIA);
    setValoresEdit([]);
    setError(null);
  }

  async function handleAnalizar() {
    if (!file) return;
    setError(null);
    setIsAnalyzing(true);
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
      setInmuebleEdit({ ...EMPTY_INMUEBLE, ...inmuebleRaw, tipo: tipoNormalizado });
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

  async function handleGenerar() {
    if (!file || !analisisResult) return;
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

  const canAnalyze = !!file && !isAnalyzing;
  const canGenerate = personas.length > 0 && !isGenerating;

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-primary">Nueva minuta</h1>
        <p className="text-sm text-muted mt-1">
          Sube un .docx, revisa los datos detectados y genera la minuta adaptada.
        </p>
      </div>

      <StepBar current={step} />

      {error && (
        <div className="ep-kpi-critical rounded-xl px-4 py-3 flex items-start gap-3 mb-6">
          <AlertCircle size={16} className="text-rose-500 mt-0.5 shrink-0" />
          <p className="text-sm text-rose-700">{error}</p>
          <button onClick={() => setError(null)} className="ml-auto text-rose-400 hover:text-rose-600">
            <X size={14} />
          </button>
        </div>
      )}

      {/* ── PASO 1 ── */}
      {step === 0 && (
        <div className="space-y-5">
          <UploadZone
            file={file} isDragging={isDragging}
            onFile={handleFileSelected} onDragOver={handleDragOver}
            onDragLeave={handleDragLeave} onDrop={handleDrop} onClear={clearFile}
          />

          {!analisisResult && (
            <button
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
          )}

          {analisisResult && <AnalysisSummary result={analisisResult} />}

          {analisisResult && (
            <button
              onClick={() => setStep(1)}
              className="w-full h-12 rounded-2xl bg-primary text-white font-semibold text-sm flex items-center justify-center gap-2 hover:opacity-90 transition-all"
            >
              Revisar personas detectadas <ChevronRight size={16} />
            </button>
          )}
        </div>
      )}

      {/* ── PASO 2 ── */}
      {step === 1 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-muted">
              {personas.length} persona{personas.length !== 1 ? "s" : ""} ·
              Campos en amarillo requieren completarse.
            </p>
            <button onClick={() => setStep(0)} className="text-xs text-soft hover:text-primary underline underline-offset-2">
              Volver
            </button>
          </div>

          {/* ── Banner de validación notarial ── */}
          {analisisResult?.validacion && !analisisResult.validacion.error && (
            <div className={[
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

          <InmuebleCard inmueble={inmuebleEdit} onChange={updateInmueble} />

          <NotariaCard notaria={notariaEdit} onChange={updateNotaria} />

          <ValoresCard valores={valoresEdit} onChangeMonto={updateValor} onChangeTexto={updateValorTexto} />

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
            ) : (
              <><ExternalLink size={18} /> Generar y abrir en editor</>
            )}
          </button>
        </div>
      )}

      <AiProgressModal
        open={aiModalOpen}
        title={aiModalTitle}
        subtitle={aiModalSubtitle}
        steps={aiSteps}
        progress={aiProgress}
      />
    </div>
  );
}
