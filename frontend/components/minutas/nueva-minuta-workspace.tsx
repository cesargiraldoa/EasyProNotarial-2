"use client";

import { useRef, useState } from "react";
import {
  AlertCircle, CheckCircle2, ChevronRight, Download,
  FileText, Loader2, Plus, Upload, X,
} from "lucide-react";
import {
  analyzeMinuta, generateMinuta, emptyPersona,
  type MinutaAnalisisResult, type MinutaDatos, type MinutaPersona,
} from "@/lib/minuta";

// ─── Constants ────────────────────────────────────────────────────────────────

const STEPS = ["Subir documento", "Revisar personas", "Generar"];

const TIPO_DOC_OPTIONS = ["CC", "CE", "TI", "PP", "NIT"];
const GENERO_OPTIONS = [
  { value: "M", label: "Masculino (M)" },
  { value: "F", label: "Femenino (F)" },
  { value: "J", label: "Jurídica (J)" },
];
const ESTADO_CIVIL_OPTIONS = [
  "Soltero(a)", "Casado(a)", "Unión marital", "Divorciado(a)", "Viudo(a)",
];

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
          Arrastra un archivo .docx aquí
        </p>
        <p className="text-sm text-muted mt-1">
          o{" "}
          <span className="text-primary underline underline-offset-2">
            haz clic para seleccionar
          </span>
        </p>
      </div>
      <p className="text-xs text-soft">Solo archivos .docx · máx 20 MB</p>
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
            {isB2 ? "B2 — Minuta diligenciada" : "B1 — Plantilla en blanco"}
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
              datos.inmueble.matricula_inmobiliaria && `Matrícula ${datos.inmueble.matricula_inmobiliaria}`,
            ]
              .filter(Boolean)
              .join(" · ")}
          </span>
        </div>
      )}
    </div>
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
  const isPending = (v: string | null) => v === null || v.trim() === "";

  function Field({
    label,
    field,
    as = "input",
    options,
  }: {
    label: string;
    field: keyof MinutaPersona;
    as?: "input" | "select";
    options?: { value: string; label: string }[];
  }) {
    const value = persona[field] as string | null;
    const pending = isPending(value);
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
            <option value="">— seleccionar —</option>
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
            placeholder={pending ? "Sin datos — completar" : ""}
            onChange={(e) => onChange(field, e.target.value)}
            className={baseClass}
          />
        )}
      </label>
    );
  }

  const pendingCount = (
    ["nombre_completo", "tipo_documento", "numero_documento", "genero"] as (keyof MinutaPersona)[]
  ).filter((f) => isPending(persona[f] as string | null)).length;

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
          <Field label="Nombre completo" field="nombre_completo" />
        </div>
        <Field
          label="Tipo documento"
          field="tipo_documento"
          as="select"
          options={TIPO_DOC_OPTIONS.map((v) => ({ value: v, label: v }))}
        />
        <Field label="Número documento" field="numero_documento" />
        <Field label="Género" field="genero" as="select" options={GENERO_OPTIONS} />
        <Field label="Nacionalidad" field="nacionalidad" />
        <Field
          label="Estado civil"
          field="estado_civil"
          as="select"
          options={ESTADO_CIVIL_OPTIONS.map((v) => ({ value: v, label: v }))}
        />
        <Field label="Profesión" field="profesion" />
        <Field label="Domicilio (ciudad)" field="domicilio" />
        <div className="sm:col-span-2">
          <Field label="Dirección completa" field="direccion" />
        </div>
        <Field label="Teléfono / Celular" field="telefono" />
        <Field label="Correo electrónico" field="email" />
      </div>
    </div>
  );
}

// ─── Main workspace ───────────────────────────────────────────────────────────

export function NuevaMinutaWorkspace() {
  const [step, setStep] = useState<0 | 1 | 2>(0);
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [analisisResult, setAnalisisResult] = useState<MinutaAnalisisResult | null>(null);
  const [personas, setPersonas] = useState<MinutaPersona[]>([]);
  const [error, setError] = useState<string | null>(null);

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
  function clearFile() { setFile(null); setAnalisisResult(null); setPersonas([]); setError(null); }

  async function handleAnalizar() {
    if (!file) return;
    setError(null); setIsAnalyzing(true);
    try {
      const result = await analyzeMinuta(file);
      setAnalisisResult(result);
      setPersonas(result.datos.personas.map((p) => ({ ...p })));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al analizar el documento.");
    } finally { setIsAnalyzing(false); }
  }

  function updatePersona(idx: number, field: keyof MinutaPersona, value: string) {
    setPersonas((prev) => prev.map((p, i) => i === idx ? { ...p, [field]: value || null } : p));
  }
  function removePersona(idx: number) { setPersonas((prev) => prev.filter((_, i) => i !== idx)); }
  function addPersona() { setPersonas((prev) => [...prev, emptyPersona(`persona_${prev.length + 1}`)]); }

  async function handleGenerar() {
    if (!file || !analisisResult) return;
    setError(null); setIsGenerating(true);
    try {
      const { blob, filename } = await generateMinuta(
        file,
        { ...analisisResult.datos, personas: analisisResult.datos.personas },
        { ...analisisResult.datos, personas },
      );
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url; a.download = filename;
      document.body.appendChild(a); a.click(); a.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al generar la minuta.");
    } finally { setIsGenerating(false); }
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
                <><Loader2 size={16} className="animate-spin" /> Analizando · ~20 s…</>
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
              ← Volver
            </button>
          </div>

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
              ← Volver
            </button>
          </div>

          <div className="ep-card rounded-2xl p-5 space-y-4">
            <h3 className="font-semibold text-sm text-ink">Resumen de la operación</h3>
            <div className="grid grid-cols-2 gap-3 text-sm">
              {[
                ["Archivo base", file?.name ?? "—"],
                ["Personas", String(personas.length)],
                ["Modo origen", analisisResult?.modo_detectado === "B2" ? "B2 — Diligenciada" : "B1 — Plantilla"],
                ["Valores en doc", String(analisisResult?.datos.valores.length ?? 0)],
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
              <><Loader2 size={18} className="animate-spin" /> Generando minuta…</>
            ) : (
              <><Download size={18} /> Generar y descargar .docx</>
            )}
          </button>
        </div>
      )}
    </div>
  );
}
