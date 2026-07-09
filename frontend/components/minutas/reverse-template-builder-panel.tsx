"use client";

import { useRef, useState, type DragEvent } from "react";
import {
  AlertCircle,
  ArrowLeft,
  CheckCircle2,
  FileSearch,
  FileText,
  Loader2,
  Upload,
  X,
} from "lucide-react";

import {
  analyzeReverseTemplateSingle,
  type ReverseTemplateAnalyzeResult,
  type ReverseTemplateCandidate,
} from "@/lib/minuta";

type Props = {
  onBackToMarkedFlow: () => void;
};

function confidenceLabel(confidence: number) {
  if (confidence >= 0.8) return "Alta";
  if (confidence >= 0.5) return "Media";
  return "Baja";
}

function confidenceClasses(confidence: number) {
  if (confidence >= 0.8) return "bg-emerald-50 text-emerald-700 border-emerald-200";
  if (confidence >= 0.5) return "bg-amber-50 text-amber-700 border-amber-200";
  return "bg-rose-50 text-rose-700 border-rose-200";
}

function candidateContext(candidate: ReverseTemplateCandidate) {
  const first = candidate.contexts[0];
  if (!first) return "Sin contexto disponible.";
  return [first.before, candidate.text, first.after].filter(Boolean).join(" ");
}

function CandidateRow({ candidate }: { candidate: ReverseTemplateCandidate }) {
  return (
    <div className="rounded-xl border border-line bg-surface p-4">
      <div className="grid gap-3 md:grid-cols-[1.1fr_1fr_0.8fr_0.7fr]">
        <div className="min-w-0">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-soft">Texto detectado</p>
          <p className="mt-1 truncate text-sm font-semibold text-ink" title={candidate.text}>
            {candidate.text}
          </p>
        </div>
        <div className="min-w-0">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-soft">Etiqueta sugerida</p>
          <p className="mt-1 truncate text-sm text-ink" title={candidate.label}>
            {candidate.label}
          </p>
          <p className="truncate text-xs text-soft" title={candidate.suggested_key}>
            {candidate.suggested_key}
          </p>
        </div>
        <div className="min-w-0">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-soft">Seccion / tipo</p>
          <p className="mt-1 truncate text-sm text-ink">{candidate.section}</p>
          <p className="truncate text-xs text-soft">{candidate.type}</p>
        </div>
        <div className="flex flex-wrap items-start gap-2 md:justify-end">
          <span className={["rounded-full border px-2.5 py-1 text-xs font-semibold", confidenceClasses(candidate.confidence)].join(" ")}>
            {confidenceLabel(candidate.confidence)} · {Math.round(candidate.confidence * 100)}%
          </span>
          <span className="rounded-full border border-line bg-panel-soft px-2.5 py-1 text-xs font-semibold text-muted">
            {candidate.occurrences} ocurr.
          </span>
          <span className="rounded-full border border-line bg-panel-soft px-2.5 py-1 text-xs font-semibold text-muted">
            {candidate.status}
          </span>
        </div>
      </div>
      <p className="mt-3 line-clamp-2 text-xs leading-5 text-muted">
        {candidateContext(candidate)}
      </p>
      {candidate.contexts[0]?.location && (
        <p className="mt-2 text-[11px] text-soft">{candidate.contexts[0].location}</p>
      )}
    </div>
  );
}

export function ReverseTemplateBuilderPanel({ onBackToMarkedFlow }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<ReverseTemplateAnalyzeResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  function selectFile(nextFile: File) {
    if (!nextFile.name.toLowerCase().endsWith(".docx")) {
      setError("Solo se aceptan documentos .docx diligenciados.");
      return;
    }
    setFile(nextFile);
    setResult(null);
    setError(null);
  }

  function handleDrop(event: DragEvent<HTMLLabelElement>) {
    event.preventDefault();
    setIsDragging(false);
    const nextFile = event.dataTransfer.files[0];
    if (nextFile) selectFile(nextFile);
  }

  async function handleAnalyze() {
    if (!file) return;
    setError(null);
    setIsAnalyzing(true);
    try {
      const payload = await analyzeReverseTemplateSingle(file);
      setResult(payload);
    } catch (err) {
      const message = err instanceof Error && err.message
        ? err.message
        : "No fue posible analizar el documento. Verifica que sea un DOCX valido.";
      setError(message);
    } finally {
      setIsAnalyzing(false);
    }
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold text-primary">Crear plantilla inteligente</h2>
          <p className="mt-1 text-sm text-muted">
            Analiza una minuta ya diligenciada para encontrar datos convertibles en campos.
          </p>
        </div>
        <button
          type="button"
          onClick={onBackToMarkedFlow}
          className="inline-flex h-10 items-center gap-2 rounded-xl border border-line px-3 text-sm font-semibold text-muted hover:border-primary hover:text-primary"
        >
          <ArrowLeft size={16} />
          Flujo actual
        </button>
      </div>

      <div className="grid gap-3 md:grid-cols-2">
        <button
          type="button"
          className="rounded-2xl border-2 border-primary bg-panel-highlight p-4 text-left"
        >
          <span className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-primary text-white">
            <FileSearch size={18} />
          </span>
          <p className="mt-3 text-sm font-bold text-ink">Documento individual diligenciado</p>
          <p className="mt-1 text-xs leading-5 text-muted">
            Detecta candidatos determinísticos en un DOCX de una escritura ya diligenciada.
          </p>
        </button>
        <button
          type="button"
          disabled
          className="rounded-2xl border border-line bg-panel-soft p-4 text-left opacity-70"
        >
          <span className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-surface-alt text-soft">
            <FileText size={18} />
          </span>
          <p className="mt-3 text-sm font-bold text-soft">Proyecto inmobiliario</p>
          <p className="mt-1 text-xs leading-5 text-soft">
            Próximamente: comparación de varias escrituras del mismo proyecto.
          </p>
        </button>
      </div>

      {error && (
        <div className="flex items-start gap-3 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3">
          <AlertCircle size={16} className="mt-0.5 shrink-0 text-rose-500" />
          <p className="text-sm text-rose-700">{error}</p>
          <button type="button" onClick={() => setError(null)} className="ml-auto text-rose-400 hover:text-rose-600">
            <X size={14} />
          </button>
        </div>
      )}

      <label
        onDragOver={(event) => {
          event.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        className={[
          "flex cursor-pointer flex-col items-center justify-center gap-3 rounded-2xl border-2 border-dashed p-8 transition-all",
          isDragging ? "border-primary bg-panel-highlight" : "border-line-strong hover:border-primary hover:bg-panel-soft",
        ].join(" ")}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".docx"
          className="hidden"
          onChange={(event) => {
            const nextFile = event.target.files?.[0];
            if (nextFile) selectFile(nextFile);
          }}
        />
        <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-panel-soft">
          <Upload size={22} className="text-primary" />
        </div>
        <div className="text-center">
          <p className="text-sm font-semibold text-ink">
            {file ? file.name : "Sube un DOCX diligenciado"}
          </p>
          <p className="mt-1 text-xs text-muted">
            {file ? `${(file.size / 1024).toFixed(0)} KB listos para analizar` : "Arrastra el archivo o haz clic para seleccionarlo"}
          </p>
        </div>
      </label>

      <div className="flex flex-wrap gap-3">
        <button
          type="button"
          onClick={handleAnalyze}
          disabled={!file || isAnalyzing}
          className={[
            "inline-flex h-12 flex-1 items-center justify-center gap-2 rounded-2xl px-4 text-sm font-semibold transition-all sm:flex-none",
            file && !isAnalyzing
              ? "bg-primary text-white hover:opacity-90"
              : "cursor-not-allowed bg-panel-soft text-soft",
          ].join(" ")}
        >
          {isAnalyzing ? (
            <>
              <Loader2 size={16} className="animate-spin" />
              Analizando documento
            </>
          ) : (
            <>
              <FileSearch size={16} />
              Analizar candidatos
            </>
          )}
        </button>
        {file && (
          <button
            type="button"
            onClick={() => {
              setFile(null);
              setResult(null);
              setError(null);
              if (inputRef.current) inputRef.current.value = "";
            }}
            className="inline-flex h-12 items-center justify-center gap-2 rounded-2xl border border-line px-4 text-sm font-semibold text-muted hover:border-primary hover:text-primary"
          >
            <X size={16} />
            Quitar archivo
          </button>
        )}
      </div>

      {result && (
        <div className="space-y-4">
          <div className="rounded-2xl border border-line bg-panel p-5">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="text-sm font-bold text-ink">Candidatos detectados</p>
                <p className="mt-1 text-xs text-soft">{result.filename} · modo {result.mode}</p>
              </div>
              <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-3 py-1 text-xs font-bold text-emerald-700">
                <CheckCircle2 size={13} />
                Análisis completado
              </span>
            </div>
            <div className="mt-4 grid grid-cols-2 gap-3 text-center md:grid-cols-4">
              {[
                ["Total", result.summary.total_candidates],
                ["Alta confianza", result.summary.high_confidence],
                ["Media", result.summary.medium_confidence],
                ["Baja", result.summary.low_confidence],
              ].map(([label, value]) => (
                <div key={String(label)} className="rounded-xl bg-panel-soft p-3">
                  <p className="text-xl font-bold text-primary">{String(value)}</p>
                  <p className="mt-0.5 text-xs text-soft">{String(label)}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="space-y-3">
            {result.candidates.length > 0 ? (
              result.candidates.map((candidate) => (
                <CandidateRow key={candidate.id} candidate={candidate} />
              ))
            ) : (
              <div className="rounded-2xl border border-line bg-panel-soft p-5 text-sm text-muted">
                No se detectaron candidatos en el documento.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
