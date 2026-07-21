"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { ArrowLeft, FileDown, Home, Landmark, Loader2, Save, ScrollText, ShieldCheck } from "lucide-react";
import { CumplimientoPanel } from "@/components/escritura/cumplimiento-panel";
import { EscrituraForm } from "@/components/escritura/escritura-form";
import { EscrituraPreview } from "@/components/escritura/escritura-preview";
import { LiquidacionPanel } from "@/components/escritura/liquidacion-panel";
import {
  escrituraDownloadUrl,
  generarDocumento,
  getCorpus,
  getEscrituraState,
  saveEscrituraState,
  type CorpusResponse,
  type DocumentoResponse,
  type EscrituraCaseMeta,
} from "@/lib/api-escritura";
import { defaults, generar, type ActoCode, type CancelacionState, type CaseState, type CompraventaState } from "@/lib/motor-escritura";

type Props = {
  caseId: number;
};

const actos: Array<{ code: ActoCode; title: string; description: string; includes: string; icon: typeof Home }> = [
  {
    code: "compraventa",
    title: "Compraventa",
    description: "Transferencia de dominio pagada de contado o con recursos propios.",
    includes: "Comparecencia, objeto, titulo, saneamiento, precio, notas, liquidacion y firmas.",
    icon: Home,
  },
  {
    code: "hipoteca",
    title: "Compraventa + Hipoteca",
    description: "Compra financiada con credito y garantia a favor del banco.",
    includes: "Compraventa completa, acto de hipoteca, acreedor, aceptacion y ratificacion Ley 258.",
    icon: Landmark,
  },
  {
    code: "cancelacion",
    title: "Cancelacion de hipoteca",
    description: "El acreedor libera el gravamen hipotecario una vez pagado el credito.",
    includes: "Banco, apoderado, hipoteca previa, inmueble liberado, acto sin cuantia y firma fuera de sede.",
    icon: ScrollText,
  },
];

function cloneState<T extends CaseState>(state: T): T {
  return JSON.parse(JSON.stringify(state)) as T;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function isCompraventaState(value: unknown): value is CompraventaState {
  return isRecord(value) && Array.isArray(value.V) && Array.isArray(value.C);
}

function isCancelacionState(value: unknown): value is CancelacionState {
  return isRecord(value) && typeof value.cNum === "string";
}

function hasSavedState(value: Record<string, unknown>) {
  return Object.keys(value).length > 0;
}

function stateDate(acto: ActoCode, state: CaseState) {
  if (acto === "cancelacion" && isCancelacionState(state)) return state.cFechaOtorg;
  if (isCompraventaState(state)) return state.fechaOtorg;
  return undefined;
}

function stateForActo(acto: ActoCode, saved: Record<string, unknown>) {
  if (hasSavedState(saved)) {
    if (acto === "cancelacion" && isCancelacionState(saved)) {
      return cloneState(saved);
    }
    if (acto !== "cancelacion" && isCompraventaState(saved)) {
      return cloneState({ ...saved, credito: acto === "hipoteca" ? true : Boolean(saved.credito) });
    }
  }
  return cloneState(defaults[acto]);
}

function humanActo(acto: ActoCode) {
  if (acto === "hipoteca") return "Compraventa con hipoteca";
  if (acto === "cancelacion") return "Cancelacion de hipoteca";
  return "Compraventa";
}

function parseApiError(error: unknown) {
  const raw = error instanceof Error ? error.message : String(error ?? "");
  if (raw.includes("hay bloqueantes por resolver")) return "hay bloqueantes por resolver";
  if (raw.startsWith("{")) {
    try {
      const parsed = JSON.parse(raw) as { detail?: unknown; message?: unknown };
      const detail = typeof parsed.detail === "string" ? parsed.detail : typeof parsed.message === "string" ? parsed.message : "";
      if (detail.trim()) return detail.trim();
    } catch {
      return raw;
    }
  }
  return raw || "No fue posible completar la solicitud.";
}

export function EscrituraWorkspace({ caseId }: Props) {
  const [acto, setActo] = useState<ActoCode | null>(null);
  const [state, setState] = useState<CaseState | null>(null);
  const [caseMeta, setCaseMeta] = useState<EscrituraCaseMeta | null>(null);
  const [corpus, setCorpus] = useState<CorpusResponse | null>(null);
  const [corpusError, setCorpusError] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [documento, setDocumento] = useState<DocumentoResponse | null>(null);
  const [isLoadingState, setIsLoadingState] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  const resultado = useMemo(() => {
    if (!acto || !state) return null;
    return generar(acto, state);
  }, [acto, state]);

  async function selectActo(nextActo: ActoCode) {
    setActo(nextActo);
    setState(null);
    setDocumento(null);
    setFeedback(null);
    setError(null);
    setCorpus(null);
    setCorpusError(null);
    setIsLoadingState(true);
    try {
      const saved = await getEscrituraState(caseId);
      const nextState = stateForActo(nextActo, saved.state);
      setState(nextState);
      setCaseMeta(saved.case);
      try {
        const corpusResult = await getCorpus(nextActo, stateDate(nextActo, nextState));
        setCorpus(corpusResult);
      } catch (issue) {
        setCorpusError(parseApiError(issue));
      }
    } catch (issue) {
      setError(parseApiError(issue));
      setState(null);
      setCaseMeta(null);
    } finally {
      setIsLoadingState(false);
    }
  }

  async function handleSave() {
    if (!acto || !state) return;
    setIsSaving(true);
    setFeedback(null);
    setError(null);
    try {
      const saved = await saveEscrituraState(caseId, acto, state);
      setCaseMeta(saved.case);
      setFeedback("Estado guardado.");
    } catch (issue) {
      setError(parseApiError(issue));
    } finally {
      setIsSaving(false);
    }
  }

  async function handleGenerate() {
    if (!acto || !state || !resultado) return;
    setIsGenerating(true);
    setFeedback(null);
    setError(null);
    setDocumento(null);
    try {
      const generated = await generarDocumento(caseId, {
        acto,
        html: resultado.html,
        cumplimiento_bloqueantes: resultado.cumplimiento.tiles.bloqueante,
        filename: `escritura_${caseId}_${acto}.docx`,
      });
      setDocumento(generated);
      setFeedback(`Documento generado en version ${generated.version_number}.`);
    } catch (issue) {
      setError(parseApiError(issue));
    } finally {
      setIsGenerating(false);
    }
  }

  const selectedTitle = acto ? humanActo(acto) : "Escritura asistida";
  const downloadHref = documento?.download_url ? escrituraDownloadUrl(documento.download_url) : null;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <Link href={`/dashboard/casos/${caseId}`} className="inline-flex items-center gap-2 text-sm font-semibold text-secondary hover:text-primary">
            <ArrowLeft className="h-4 w-4" aria-hidden="true" />
            Volver al caso
          </Link>
          <h1 className="mt-3 font-serif text-3xl font-semibold text-primary">{selectedTitle}</h1>
          <p className="mt-1 max-w-3xl text-sm leading-6 text-secondary">
            Captura deterministica con escritura, cumplimiento y liquidacion generados en vivo desde el motor.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={handleSave}
            disabled={!acto || !state || isSaving || isLoadingState}
            className="inline-flex items-center gap-2 rounded-xl border border-line-strong bg-white px-4 py-2 text-sm font-semibold text-primary shadow-sm hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isSaving ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : <Save className="h-4 w-4" aria-hidden="true" />}
            Guardar
          </button>
          <button
            type="button"
            onClick={handleGenerate}
            disabled={!acto || !state || !resultado || isGenerating || isLoadingState}
            className="inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isGenerating ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : <FileDown className="h-4 w-4" aria-hidden="true" />}
            Generar documento
          </button>
        </div>
      </div>

      <ActoLauncher selectedActo={acto} loadingActo={isLoadingState ? acto : null} onSelect={selectActo} />

      {caseMeta || corpus || corpusError || feedback || error || documento ? (
        <div className="flex flex-wrap items-center gap-2 rounded-xl border border-line bg-white/80 px-4 py-3 text-sm shadow-sm">
          {caseMeta ? (
            <span className="rounded-full bg-slate-100 px-3 py-1 font-semibold text-secondary">
              Caso {caseMeta.internal_case_number || caseMeta.id} · {caseMeta.current_state.replace(/_/g, " ")}
            </span>
          ) : null}
          {corpus ? (
            <span className="rounded-full bg-primary/10 px-3 py-1 font-semibold text-primary">
              Corpus {corpus.fecha}: {corpus.normas.length} normas · {corpus.reglas.length} reglas
            </span>
          ) : null}
          {corpusError ? <span className="rounded-full bg-amber-50 px-3 py-1 font-semibold text-amber-700">Corpus: {corpusError}</span> : null}
          {feedback ? <span className="rounded-full bg-emerald-50 px-3 py-1 font-semibold text-emerald-700">{feedback}</span> : null}
          {error ? <span className="rounded-full bg-red-50 px-3 py-1 font-semibold text-red-700">{error}</span> : null}
          {downloadHref ? (
            <a href={downloadHref} className="inline-flex items-center gap-2 rounded-full bg-primary px-3 py-1 font-semibold text-white hover:bg-primary/90">
              <FileDown className="h-3.5 w-3.5" aria-hidden="true" />
              Descargar v{documento?.version_number}
            </a>
          ) : null}
        </div>
      ) : null}

      {isLoadingState ? (
        <div className="ep-card flex items-center gap-3 rounded-[1.25rem] p-6 text-secondary">
          <Loader2 className="h-5 w-5 animate-spin" aria-hidden="true" />
          Cargando estado de captura...
        </div>
      ) : null}

      {acto && state && resultado ? (
        <div className="grid grid-cols-1 gap-5 xl:grid-cols-[380px_minmax(0,1fr)_340px]">
          <EscrituraForm acto={acto} state={state} onChange={(nextState) => setState(nextState)} />
          <main className="min-w-0 space-y-4">
            <EstadoBar ok={resultado.estado.ok} texto={resultado.estado.texto} />
            <EscrituraPreview html={resultado.html} />
          </main>
          <aside className="space-y-5 xl:sticky xl:top-4 xl:max-h-[calc(100vh-2rem)] xl:overflow-auto">
            <CumplimientoPanel cumplimiento={resultado.cumplimiento} />
            <LiquidacionPanel html={resultado.liquidacionHtml} />
          </aside>
        </div>
      ) : null}
    </div>
  );
}

function ActoLauncher({ selectedActo, loadingActo, onSelect }: { selectedActo: ActoCode | null; loadingActo: ActoCode | null; onSelect: (acto: ActoCode) => void }) {
  return (
    <section className="ep-card rounded-[1.25rem] p-5" aria-label="Elige el acto">
      <div className="mb-4">
        <p className="text-xs font-semibold uppercase tracking-[0.12em] text-secondary">Elige el acto</p>
        <h2 className="font-serif text-2xl font-semibold text-primary">Plantilla de captura</h2>
      </div>
      <div className="grid gap-4 lg:grid-cols-3">
        {actos.map((item) => {
          const Icon = item.icon;
          const active = selectedActo === item.code;
          const loading = loadingActo === item.code;
          return (
            <button
              key={item.code}
              type="button"
              aria-pressed={active}
              onClick={() => onSelect(item.code)}
              className={`min-h-40 rounded-xl border p-5 text-left shadow-sm transition hover:-translate-y-0.5 hover:border-primary hover:shadow-md ${active ? "border-primary bg-primary/8" : "border-line-strong bg-white"}`}
            >
              <span className="inline-flex h-11 w-11 items-center justify-center rounded-xl bg-primary/10 text-primary">
                {loading ? <Loader2 className="h-5 w-5 animate-spin" aria-hidden="true" /> : <Icon className="h-5 w-5" aria-hidden="true" />}
              </span>
              <span className="mt-4 block font-serif text-xl font-semibold text-primary">{item.title}</span>
              <span className="mt-1 block text-sm leading-6 text-secondary">{item.description}</span>
              <span className="mt-3 block text-xs leading-5 text-secondary">{item.includes}</span>
            </button>
          );
        })}
      </div>
    </section>
  );
}

function EstadoBar({ ok, texto }: { ok: boolean; texto: string }) {
  return (
    <div className={`flex items-center gap-3 rounded-xl border px-4 py-3 text-sm font-semibold ${ok ? "border-emerald-200 bg-emerald-50 text-emerald-700" : "border-red-200 bg-red-50 text-red-700"}`}>
      <span className={`inline-flex h-7 w-7 items-center justify-center rounded-full text-white ${ok ? "bg-emerald-600" : "bg-red-600"}`}>
        <ShieldCheck className="h-4 w-4" aria-hidden="true" />
      </span>
      <span>{texto}</span>
    </div>
  );
}
