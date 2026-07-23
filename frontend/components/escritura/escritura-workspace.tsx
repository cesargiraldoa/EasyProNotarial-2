"use client";

import Link from "next/link";
import { useMemo, useRef, useState } from "react";
import { ArrowLeft, Bot, Check, FileDown, Home, Landmark, Loader2, PencilLine, Save, ScrollText, SearchCheck, ShieldCheck, Upload, WandSparkles } from "lucide-react";
import { CumplimientoPanel } from "@/components/escritura/cumplimiento-panel";
import { CertificadoCumplimiento } from "@/components/escritura/certificado-cumplimiento";
import { CalculadoraLiquidacion } from "@/components/escritura/calculadora-liquidacion";
import { EscrituraRedaccionEditor, type EscrituraEditorHandle, type RedaccionComment, type RedaccionDraft } from "@/components/escritura/escritura-editor";
import { EscrituraForm } from "@/components/escritura/escritura-form";
import { EscrituraPreview } from "@/components/escritura/escritura-preview";
import { LiquidacionPanel } from "@/components/escritura/liquidacion-panel";
import {
  clasificarEscritura,
  escrituraDownloadUrl,
  extraerEscritura,
  generarDocumento,
  getBibliotecaEscritura,
  getCorpus,
  getEscrituraState,
  redactarProsaGari,
  revisarEscritura,
  saveEscrituraState,
  type BibliotecaClausula,
  type CorpusResponse,
  type DocumentoResponse,
  type EscrituraCaseMeta,
  type GariClasificacionResponse,
  type GariExtraccionResponse,
  type GariRevisionResponse,
} from "@/lib/api-escritura";
import { bibliotecaItemFromClausula, type BibliotecaRedaccionItem } from "@/lib/escritura-redaccion-biblioteca";
import { defaults, generar, type ActoCode, type CancelacionState, type CaseState, type CompraventaState } from "@/lib/motor-escritura";

type Props = {
  caseId: number;
};

type WorkspaceMode = "captura" | "redaccion" | "cumplimiento";
type GariOperation = "extraer" | "prosa" | "clasificar" | "revisar";

const REDACCION_KEY = "__redaccion";

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

function applyStatePath(state: CaseState, path: string, value: unknown): CaseState {
  const next = cloneState(state);
  const parts = path.split(".").filter(Boolean);
  if (!parts.length) return next;
  let cursor: Record<string, unknown> | unknown[] = next as unknown as Record<string, unknown>;
  for (let index = 0; index < parts.length - 1; index++) {
    const part = parts[index];
    const upcoming = parts[index + 1];
    if (Array.isArray(cursor) && /^\d+$/.test(part)) {
      const arrayIndex = Number(part);
      const current = cursor[arrayIndex];
      if (!isRecord(current) && !Array.isArray(current)) cursor[arrayIndex] = /^\d+$/.test(upcoming) ? [] : {};
      cursor = cursor[arrayIndex] as Record<string, unknown> | unknown[];
      continue;
    }
    if (!Array.isArray(cursor)) {
      const current = cursor[part];
      if (!isRecord(current) && !Array.isArray(current)) cursor[part] = /^\d+$/.test(upcoming) ? [] : {};
      cursor = cursor[part] as Record<string, unknown> | unknown[];
    }
  }
  const last = parts[parts.length - 1];
  if (Array.isArray(cursor) && /^\d+$/.test(last)) cursor[Number(last)] = value;
  else if (!Array.isArray(cursor)) cursor[last] = value;
  return next;
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

function isRedaccionComment(value: unknown): value is RedaccionComment {
  return (
    isRecord(value) &&
    typeof value.id === "string" &&
    typeof value.quote === "string" &&
    typeof value.text === "string" &&
    typeof value.resolved === "boolean"
  );
}

function isRedaccionDraft(value: unknown): value is RedaccionDraft {
  return (
    isRecord(value) &&
    (value.acto === "compraventa" || value.acto === "hipoteca" || value.acto === "cancelacion") &&
    typeof value.html === "string" &&
    Array.isArray(value.comments) &&
    value.comments.every(isRedaccionComment) &&
    typeof value.updated_at === "string"
  );
}

function redaccionDraftFrom(state: Record<string, unknown>, acto: ActoCode) {
  const draft = state[REDACCION_KEY];
  return isRedaccionDraft(draft) && draft.acto === acto ? draft : null;
}

function stateWithDraft(state: CaseState, draft: RedaccionDraft | null) {
  const payload: Record<string, unknown> = { ...(state as unknown as Record<string, unknown>) };
  if (draft) payload[REDACCION_KEY] = draft;
  else delete payload[REDACCION_KEY];
  return payload;
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

function redaccionItemFromApi(clausula: BibliotecaClausula): BibliotecaRedaccionItem {
  return bibliotecaItemFromClausula(clausula);
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
  const editorRef = useRef<EscrituraEditorHandle | null>(null);
  const [acto, setActo] = useState<ActoCode | null>(null);
  const [state, setState] = useState<CaseState | null>(null);
  const [mode, setMode] = useState<WorkspaceMode>("captura");
  const [dockOpen, setDockOpen] = useState(true);
  const [caseMeta, setCaseMeta] = useState<EscrituraCaseMeta | null>(null);
  const [corpus, setCorpus] = useState<CorpusResponse | null>(null);
  const [corpusError, setCorpusError] = useState<string | null>(null);
  const [biblioteca, setBiblioteca] = useState<BibliotecaRedaccionItem[] | null>(null);
  const [bibliotecaError, setBibliotecaError] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [documento, setDocumento] = useState<DocumentoResponse | null>(null);
  const [redaccionDraft, setRedaccionDraft] = useState<RedaccionDraft | null>(null);
  const [redaccionDirty, setRedaccionDirty] = useState(false);
  const [gariOperation, setGariOperation] = useState<GariOperation | null>(null);
  const [gariExtraccion, setGariExtraccion] = useState<GariExtraccionResponse | null>(null);
  const [gariClasificacion, setGariClasificacion] = useState<GariClasificacionResponse | null>(null);
  const [gariRevision, setGariRevision] = useState<GariRevisionResponse | null>(null);
  const [clasificacionText, setClasificacionText] = useState("");
  const [prosaInstruction, setProsaInstruction] = useState("");
  const [isLoadingState, setIsLoadingState] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  const resultado = useMemo(() => {
    if (!acto || !state) return null;
    return generar(acto, state, corpus ? { tarifas: corpus.tarifas } : undefined);
  }, [acto, state, corpus]);

  async function selectActo(nextActo: ActoCode) {
    if (mode === "redaccion" && redaccionDirty && !window.confirm("Al cambiar de acto se perderan las ediciones de Redaccion no guardadas. Continuar?")) {
      return;
    }
    setActo(nextActo);
    setState(null);
    setMode("captura");
    setRedaccionDraft(null);
    setRedaccionDirty(false);
    setDocumento(null);
    setFeedback(null);
    setError(null);
    setCorpus(null);
    setCorpusError(null);
    setBiblioteca(null);
    setBibliotecaError(null);
    setGariOperation(null);
    setGariExtraccion(null);
    setGariClasificacion(null);
    setGariRevision(null);
    setIsLoadingState(true);
    try {
      const saved = await getEscrituraState(caseId);
      const nextState = stateForActo(nextActo, saved.state);
      setState(nextState);
      setRedaccionDraft(redaccionDraftFrom(saved.state, nextActo));
      setCaseMeta(saved.case);
      try {
        const corpusResult = await getCorpus(nextActo, stateDate(nextActo, nextState));
        setCorpus(corpusResult);
      } catch (issue) {
        setCorpusError(parseApiError(issue));
      }
      try {
        const clausulas = await getBibliotecaEscritura(nextActo, stateDate(nextActo, nextState));
        setBiblioteca(clausulas.map(redaccionItemFromApi));
      } catch (issue) {
        setBibliotecaError(parseApiError(issue));
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
    if (mode === "redaccion" && editorRef.current) {
      try {
        await handleSaveRedaccionDraft(editorRef.current.getDraft());
      } catch {
        return;
      }
      return;
    }
    setIsSaving(true);
    setFeedback(null);
    setError(null);
    try {
      const saved = await saveEscrituraState(caseId, acto, stateWithDraft(state, redaccionDraft));
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
    const html = mode === "redaccion" && editorRef.current ? editorRef.current.getHtmlForExport() : resultado.html;
    await handleGenerateFromHtml(html, mode);
  }

  async function handleGenerateFromHtml(html: string, sourceMode: WorkspaceMode) {
    if (!acto || !state || !resultado) return;
    setIsGenerating(true);
    setFeedback(null);
    setError(null);
    setDocumento(null);
    try {
      const generated = await generarDocumento(caseId, {
        acto,
        html,
        cumplimiento_bloqueantes: resultado.cumplimiento.tiles.bloqueante,
        filename: `escritura_${caseId}_${acto}${sourceMode === "redaccion" ? "_redaccion" : ""}.docx`,
      });
      setDocumento(generated);
      setFeedback(`Documento generado en version ${generated.version_number}.`);
    } catch (issue) {
      setError(parseApiError(issue));
    } finally {
      setIsGenerating(false);
    }
  }

  async function handleSaveRedaccionDraft(draft: RedaccionDraft) {
    if (!acto || !state) return;
    setIsSaving(true);
    setFeedback(null);
    setError(null);
    try {
      const saved = await saveEscrituraState(caseId, acto, stateWithDraft(state, draft));
      setCaseMeta(saved.case);
      setRedaccionDraft(draft);
      setRedaccionDirty(false);
      editorRef.current?.markClean();
      setFeedback("Borrador de redaccion guardado.");
    } catch (issue) {
      setError(parseApiError(issue));
      throw issue;
    } finally {
      setIsSaving(false);
    }
  }

  async function handleExtraerArchivo(file: File | null) {
    if (!file || !acto || !state) return;
    setGariOperation("extraer");
    setFeedback(null);
    setError(null);
    try {
      const result = await extraerEscritura(caseId, file);
      setGariExtraccion(result);
      setFeedback("Gari propuso campos para validar.");
    } catch (issue) {
      setError(parseApiError(issue));
    } finally {
      setGariOperation(null);
    }
  }

  function acceptGariField(field: string, value: unknown) {
    if (!state) return;
    setState(applyStatePath(state, field, value));
    setFeedback(`Sugerencia aplicada en ${field}. Revisa y guarda el estado.`);
  }

  async function handleClasificar() {
    const descripcion = clasificacionText.trim();
    if (!descripcion) {
      setError("Describe el caso para clasificarlo con Gari.");
      return;
    }
    setGariOperation("clasificar");
    setFeedback(null);
    setError(null);
    try {
      const result = await clasificarEscritura(descripcion);
      setGariClasificacion(result);
      setFeedback("Gari propuso una clasificacion para validar.");
    } catch (issue) {
      setError(parseApiError(issue));
    } finally {
      setGariOperation(null);
    }
  }

  async function handleRedactarGari() {
    if (!acto || !state) return null;
    const instruccion = prosaInstruction.trim();
    if (!instruccion) {
      setError("Escribe una instruccion para redactar con Gari.");
      return null;
    }
    setGariOperation("prosa");
    setFeedback(null);
    setError(null);
    try {
      const result = await redactarProsaGari(acto, state, instruccion);
      setFeedback("Gari redacto una sugerencia editable para validar.");
      return result.html_sugerido;
    } catch (issue) {
      setError(parseApiError(issue));
      return null;
    } finally {
      setGariOperation(null);
    }
  }

  async function handleRevisarGari() {
    if (!acto || !state || !resultado) return;
    const html = mode === "redaccion" && editorRef.current ? editorRef.current.getHtmlForExport() : resultado.html;
    setGariOperation("revisar");
    setFeedback(null);
    setError(null);
    try {
      const result = await revisarEscritura(caseId, acto, html);
      setGariRevision(result);
      setFeedback("Gari propuso hallazgos QA para validar.");
    } catch (issue) {
      setError(parseApiError(issue));
    } finally {
      setGariOperation(null);
    }
  }

  function showCaptura() {
    if (mode === "redaccion" && redaccionDirty && !window.confirm("Volver a Captura descarta las ediciones de Redaccion no guardadas. Continuar?")) {
      return;
    }
    setMode("captura");
  }

  function showRedaccion() {
    if (!acto || !state || !resultado) return;
    setMode("redaccion");
  }

  function showCumplimiento() {
    if (!acto || !state || !resultado) return;
    if (mode === "redaccion" && redaccionDirty && !window.confirm("Ir a Cumplimiento descarta las ediciones de Redaccion no guardadas. Continuar?")) {
      return;
    }
    setMode("cumplimiento");
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
            Captura deterministica y redaccion manual sobre la escritura generada por el motor.
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
            {mode === "redaccion" ? "Guardar borrador" : "Guardar"}
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
        <GariPanel
          operation={gariOperation}
          extraccion={gariExtraccion}
          clasificacion={gariClasificacion}
          revision={gariRevision}
          clasificacionText={clasificacionText}
          prosaInstruction={prosaInstruction}
          onClasificacionText={setClasificacionText}
          onProsaInstruction={setProsaInstruction}
          onExtraerArchivo={handleExtraerArchivo}
          onAcceptField={acceptGariField}
          onClasificar={handleClasificar}
          onRevisar={handleRevisarGari}
        />
      ) : null}

      {acto && state && resultado ? (
        mode === "cumplimiento" ? (
          <div className="space-y-4">
            <ModeSwitch mode={mode} onCaptura={showCaptura} onRedaccion={showRedaccion} onCumplimiento={showCumplimiento} />
            <CertificadoCumplimiento
              cumplimiento={resultado.cumplimiento}
              caso={{ codigo: `CAS-${caseId}`, acto: humanActo(acto) }}
            />
            <CalculadoraLiquidacion
              liquidacionHtml={resultado.liquidacionHtml}
              caso={{ codigo: `CAS-${caseId}` }}
            />
          </div>
        ) : (
        <div className={`grid grid-cols-1 gap-5 ${dockOpen ? "xl:grid-cols-[400px_minmax(0,1fr)_340px]" : "xl:grid-cols-[400px_minmax(0,1fr)_64px]"}`}>
          <EscrituraForm acto={acto} state={state} onChange={(nextState) => setState(nextState)} />
          {mode === "captura" ? (
            <>
              <main className="min-w-0 space-y-4">
                <EstadoBar ok={resultado.estado.ok} texto={resultado.estado.texto} />
                <ModeSwitch mode={mode} onCaptura={showCaptura} onRedaccion={showRedaccion} onCumplimiento={showCumplimiento} />
                <EscrituraPreview html={resultado.html} />
              </main>
              <aside className="space-y-3 xl:sticky xl:top-4 xl:max-h-[calc(100vh-2rem)] xl:overflow-auto">
                <div className="flex items-center justify-between gap-2 rounded-xl border border-line-strong bg-white p-2 shadow-sm">
                  {dockOpen ? (
                    <span className="px-1 text-xs font-semibold uppercase tracking-[0.08em] text-secondary">Cumplimiento</span>
                  ) : (
                    <span className="flex flex-col gap-0.5 px-1 font-mono text-[11px] leading-tight" aria-hidden="true">
                      <span className="text-emerald-600">{resultado.cumplimiento.tiles.cumple} ✓</span>
                      <span className="text-amber-600">{resultado.cumplimiento.tiles.advertencia} ⚠</span>
                      <span className="text-red-600">{resultado.cumplimiento.tiles.bloqueante} ⛔</span>
                    </span>
                  )}
                  <button
                    type="button"
                    onClick={() => setDockOpen((v) => !v)}
                    aria-label={dockOpen ? "Colapsar cumplimiento" : "Expandir cumplimiento"}
                    className="inline-flex h-8 w-8 flex-none items-center justify-center rounded-lg border border-line-strong bg-slate-50 text-secondary hover:text-primary"
                  >
                    {dockOpen ? "»" : "«"}
                  </button>
                </div>
                <div className={dockOpen ? "space-y-5" : "hidden"}>
                  <CumplimientoPanel cumplimiento={resultado.cumplimiento} />
                  <LiquidacionPanel html={resultado.liquidacionHtml} />
                </div>
              </aside>
            </>
          ) : (
            <section className="min-w-0 space-y-4 xl:col-span-2">
              <EstadoBar ok={resultado.estado.ok} texto={resultado.estado.texto} />
              <ModeSwitch mode={mode} onCaptura={showCaptura} onRedaccion={showRedaccion} onCumplimiento={showCumplimiento} />
              <EscrituraRedaccionEditor
                ref={editorRef}
                acto={acto}
                state={state}
                sourceHtml={resultado.html}
                cumplimiento={resultado.cumplimiento}
                liquidacionHtml={resultado.liquidacionHtml}
                draft={redaccionDraft}
                bloqueantes={resultado.cumplimiento.tiles.bloqueante}
                isSaving={isSaving}
                isGenerating={isGenerating}
                bibliotecaItems={biblioteca}
                bibliotecaError={bibliotecaError}
                isGariBusy={gariOperation === "prosa"}
                onRedactarGari={handleRedactarGari}
                onSaveDraft={handleSaveRedaccionDraft}
                onExportWord={(html) => handleGenerateFromHtml(html, "redaccion")}
                onDirtyChange={setRedaccionDirty}
              />
            </section>
          )}
        </div>
        )
      ) : null}
    </div>
  );
}

function ModeSwitch({ mode, onCaptura, onRedaccion, onCumplimiento }: { mode: WorkspaceMode; onCaptura: () => void; onRedaccion: () => void; onCumplimiento: () => void }) {
  const label = mode === "redaccion" ? "Redaccion manual" : mode === "cumplimiento" ? "Certificado de cumplimiento" : "Captura estructurada";
  return (
    <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-line-strong bg-white p-3 shadow-sm">
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.12em] text-secondary">Modo</p>
        <p className="text-sm font-semibold text-primary">{label}</p>
      </div>
      <div className="inline-flex rounded-xl border border-line-strong bg-slate-50 p-1">
        <button
          type="button"
          onClick={onCaptura}
          aria-pressed={mode === "captura"}
          className={`inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-semibold ${mode === "captura" ? "bg-white text-primary shadow-sm" : "text-secondary hover:text-primary"}`}
        >
          <ScrollText className="h-4 w-4" aria-hidden="true" />
          Captura
        </button>
        <button
          type="button"
          onClick={onRedaccion}
          aria-pressed={mode === "redaccion"}
          className={`inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-semibold ${mode === "redaccion" ? "bg-white text-primary shadow-sm" : "text-secondary hover:text-primary"}`}
        >
          <PencilLine className="h-4 w-4" aria-hidden="true" />
          Redaccion
        </button>
        <button
          type="button"
          onClick={onCumplimiento}
          aria-pressed={mode === "cumplimiento"}
          className={`inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-semibold ${mode === "cumplimiento" ? "bg-white text-primary shadow-sm" : "text-secondary hover:text-primary"}`}
        >
          <ShieldCheck className="h-4 w-4" aria-hidden="true" />
          Cumplimiento
        </button>
      </div>
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

function valueLabel(value: unknown) {
  if (typeof value === "string") return value;
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  try {
    return JSON.stringify(value);
  } catch {
    return String(value);
  }
}

function GariPanel({
  operation,
  extraccion,
  clasificacion,
  revision,
  clasificacionText,
  prosaInstruction,
  onClasificacionText,
  onProsaInstruction,
  onExtraerArchivo,
  onAcceptField,
  onClasificar,
  onRevisar,
}: {
  operation: GariOperation | null;
  extraccion: GariExtraccionResponse | null;
  clasificacion: GariClasificacionResponse | null;
  revision: GariRevisionResponse | null;
  clasificacionText: string;
  prosaInstruction: string;
  onClasificacionText: (value: string) => void;
  onProsaInstruction: (value: string) => void;
  onExtraerArchivo: (file: File | null) => void;
  onAcceptField: (field: string, value: unknown) => void;
  onClasificar: () => void;
  onRevisar: () => void;
}) {
  const busy = Boolean(operation);
  const sugerencias = Object.entries(extraccion?.sugerencias ?? {});
  return (
    <section className="rounded-xl border border-primary/20 bg-white p-4 shadow-sm" aria-label="Gari asistente">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.12em] text-primary">
            <Bot className="h-4 w-4" aria-hidden="true" />
            Gari
          </p>
          <h2 className="font-serif text-xl font-semibold text-primary">Sugerencias de IA — validar</h2>
        </div>
        {operation ? (
          <span className="inline-flex items-center gap-2 rounded-full bg-primary/10 px-3 py-1 text-xs font-semibold text-primary">
            <Loader2 className="h-3.5 w-3.5 animate-spin" aria-hidden="true" />
            Procesando {operation}
          </span>
        ) : null}
      </div>
      <div className="grid gap-4 lg:grid-cols-3">
        <div className="space-y-3 rounded-lg border border-line bg-slate-50 p-3">
          <div className="flex items-center gap-2 text-sm font-semibold text-primary">
            <Upload className="h-4 w-4" aria-hidden="true" />
            Prellenado
          </div>
          <input
            aria-label="Subir documento para extraer con Gari"
            type="file"
            disabled={busy}
            onChange={(event) => {
              onExtraerArchivo(event.currentTarget.files?.[0] ?? null);
              event.currentTarget.value = "";
            }}
            className="block w-full text-xs text-secondary file:mr-3 file:rounded-lg file:border-0 file:bg-white file:px-3 file:py-2 file:text-xs file:font-semibold file:text-primary"
          />
          {sugerencias.length ? (
            <div className="space-y-2">
              {sugerencias.map(([field, suggestion]) => (
                <div key={field} className="rounded-lg border border-line-strong bg-white p-3 text-sm">
                  <div className="font-semibold text-primary">{field}</div>
                  <div className="mt-1 text-secondary">{valueLabel(suggestion.valor)}</div>
                  <div className="mt-1 text-xs text-secondary">
                    Confianza {Math.round(suggestion.confianza * 100)}% · {suggestion.fuente}
                  </div>
                  <button
                    type="button"
                    onClick={() => onAcceptField(field, suggestion.valor)}
                    className="mt-2 inline-flex items-center gap-2 rounded-lg bg-primary px-3 py-1.5 text-xs font-semibold text-white hover:bg-primary/90"
                  >
                    <Check className="h-3.5 w-3.5" aria-hidden="true" />
                    Aceptar {field}
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs leading-5 text-secondary">Sube una escritura o certificado para recibir campos sugeridos por validar.</p>
          )}
        </div>
        <div className="space-y-3 rounded-lg border border-line bg-slate-50 p-3">
          <div className="flex items-center gap-2 text-sm font-semibold text-primary">
            <WandSparkles className="h-4 w-4" aria-hidden="true" />
            Clasificar y redactar
          </div>
          <textarea
            value={clasificacionText}
            onChange={(event) => onClasificacionText(event.target.value)}
            placeholder="Describe el caso para clasificarlo"
            className="min-h-20 w-full rounded-lg border border-line-strong bg-white px-3 py-2 text-sm text-primary outline-none focus:border-primary focus:ring-2 focus:ring-primary/15"
          />
          <button
            type="button"
            disabled={busy}
            onClick={onClasificar}
            className="inline-flex items-center gap-2 rounded-lg border border-line-strong bg-white px-3 py-2 text-sm font-semibold text-primary shadow-sm hover:bg-slate-50 disabled:opacity-50"
          >
            <SearchCheck className="h-4 w-4" aria-hidden="true" />
            Clasificar caso
          </button>
          {clasificacion ? (
            <div className="rounded-lg border border-line-strong bg-white p-3 text-sm">
              <div className="font-semibold text-primary">Acto sugerido: {humanActo(clasificacion.acto_sugerido)}</div>
              <div className="mt-1 text-xs text-secondary">Ramas: {clasificacion.ramas.join(", ") || "sin ramas"}</div>
              <div className="mt-1 text-xs font-semibold text-amber-700">Sugerencia IA: validar antes de activar.</div>
            </div>
          ) : null}
          <textarea
            value={prosaInstruction}
            onChange={(event) => onProsaInstruction(event.target.value)}
            placeholder="Instruccion para Redactar con Gari en el editor"
            className="min-h-20 w-full rounded-lg border border-line-strong bg-white px-3 py-2 text-sm text-primary outline-none focus:border-primary focus:ring-2 focus:ring-primary/15"
          />
          <p className="text-xs leading-5 text-secondary">El boton del editor inserta la prosa como bloque editable por validar.</p>
        </div>
        <div className="space-y-3 rounded-lg border border-line bg-slate-50 p-3">
          <div className="flex items-center gap-2 text-sm font-semibold text-primary">
            <SearchCheck className="h-4 w-4" aria-hidden="true" />
            Revisor QA
          </div>
          <button
            type="button"
            disabled={busy}
            onClick={onRevisar}
            className="inline-flex items-center gap-2 rounded-lg border border-line-strong bg-white px-3 py-2 text-sm font-semibold text-primary shadow-sm hover:bg-slate-50 disabled:opacity-50"
          >
            Revisar con Gari
          </button>
          {revision?.hallazgos.length ? (
            <div className="space-y-2">
              {revision.hallazgos.map((item, index) => (
                <div key={`${item.tipo}-${index}`} className="rounded-lg border border-line-strong bg-white p-3 text-sm">
                  <div className="font-semibold text-primary">{item.tipo}</div>
                  <div className="mt-1 text-secondary">{item.detalle}</div>
                  <div className="mt-1 text-xs font-semibold text-primary">{item.cita_slug || "sin cita RAG"}</div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs leading-5 text-secondary">Los hallazgos son sugerencias; los bloqueos siguen saliendo del motor y reglas server-side.</p>
          )}
        </div>
      </div>
    </section>
  );
}
