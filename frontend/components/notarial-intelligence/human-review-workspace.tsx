"use client";

import { useEffect, useMemo, useState } from "react";
import { Check, Download, History, RefreshCw, RotateCcw, Save, Search, X } from "lucide-react";
import {
  applyHumanFieldDecision,
  approveHumanReviewSession,
  createHumanReviewSession,
  getTemplateLibrary,
  rollbackTemplateLibraryItem,
  templateVersionDocxUrl,
  type HumanReviewDetail,
  type HumanReviewField,
  type TemplateLibraryItem,
} from "@/lib/api";

const fieldLabels = ["fixed", "variable", "optional", "unknown"];

function statusTone(status: string) {
  if (status === "approved") return "bg-emerald-50 text-emerald-700 border-emerald-200";
  if (status === "rejected") return "bg-rose-50 text-rose-700 border-rose-200";
  if (status === "proposed_catalog_review") return "bg-amber-50 text-amber-700 border-amber-200";
  return "bg-slate-50 text-slate-700 border-slate-200";
}

export function HumanReviewWorkspace() {
  const [decisionId, setDecisionId] = useState("");
  const [templateName, setTemplateName] = useState("Plantilla revisada");
  const [templateKind, setTemplateKind] = useState("individual");
  const [review, setReview] = useState<HumanReviewDetail | null>(null);
  const [library, setLibrary] = useState<TemplateLibraryItem[]>([]);
  const [selectedFieldId, setSelectedFieldId] = useState<number | null>(null);
  const [isBusy, setIsBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const selectedField = useMemo(
    () => review?.fields.find((field) => field.id === selectedFieldId) ?? review?.fields[0] ?? null,
    [review, selectedFieldId],
  );

  useEffect(() => {
    void refreshLibrary();
  }, []);

  async function refreshLibrary() {
    const payload = await getTemplateLibrary();
    setLibrary(payload.items ?? []);
  }

  async function openReview() {
    const id = Number(decisionId);
    if (!Number.isFinite(id) || id <= 0) {
      setError("Ingresa un decision_id válido.");
      return;
    }
    setIsBusy(true);
    setError(null);
    setMessage(null);
    try {
      const payload = await createHumanReviewSession(id);
      setReview(payload);
      setSelectedFieldId(payload.fields[0]?.id ?? null);
      setMessage("Sesión de revisión abierta.");
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "No fue posible abrir la revisión.");
    } finally {
      setIsBusy(false);
    }
  }

  async function decide(field: HumanReviewField, action: string, overrides: Partial<HumanReviewField> = {}) {
    if (!review) return;
    setIsBusy(true);
    setError(null);
    setMessage(null);
    try {
      const result = await applyHumanFieldDecision(review.session.id, field.id, {
        action,
        proposed_field_code: overrides.proposed_field_code ?? field.proposed_field_code ?? field.field_code,
        proposed_value: overrides.proposed_value ?? field.proposed_value ?? field.original_value,
        apply_scope: overrides.apply_scope ?? field.apply_scope ?? "single",
        fixed_variable_label: overrides.fixed_variable_label ?? field.fixed_variable_label ?? "unknown",
      });
      setReview({ ...review, fields: result.fields });
      setMessage("Decisión aplicada.");
    } catch (decisionError) {
      setError(decisionError instanceof Error ? decisionError.message : "No fue posible aplicar la decisión.");
    } finally {
      setIsBusy(false);
    }
  }

  async function approve() {
    if (!review) return;
    setIsBusy(true);
    setError(null);
    setMessage(null);
    try {
      await approveHumanReviewSession(review.session.id, templateName, templateKind);
      const refreshed = await createHumanReviewSession(review.session.decision_id);
      setReview(refreshed);
      await refreshLibrary();
      setMessage("Plantilla aprobada y versionada.");
    } catch (approveError) {
      setError(approveError instanceof Error ? approveError.message : "No fue posible aprobar la plantilla.");
    } finally {
      setIsBusy(false);
    }
  }

  async function rollback(item: TemplateLibraryItem) {
    const versionId = item.approved_version_id ?? item.latest_version_id;
    if (!versionId) return;
    setIsBusy(true);
    setError(null);
    try {
      await rollbackTemplateLibraryItem(item.id, versionId);
      await refreshLibrary();
      setMessage("Rollback registrado como nueva versión aprobada.");
    } catch (rollbackError) {
      setError(rollbackError instanceof Error ? rollbackError.message : "No fue posible hacer rollback.");
    } finally {
      setIsBusy(false);
    }
  }

  return (
    <main className="mx-auto flex w-full max-w-7xl flex-col gap-6 px-4 py-6 lg:px-8">
      <section className="flex flex-col gap-4 border-b border-[var(--line)] pb-5 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-secondary">Inteligencia documental</p>
          <h1 className="mt-2 text-2xl font-semibold text-primary">Revisión humana y biblioteca</h1>
        </div>
        <div className="flex flex-col gap-2 sm:flex-row">
          <input value={decisionId} onChange={(event) => setDecisionId(event.target.value)} placeholder="decision_id" className="ep-input h-11 min-w-40 px-3" />
          <button type="button" onClick={() => void openReview()} disabled={isBusy} className="inline-flex h-11 items-center gap-2 rounded-lg bg-primary px-4 text-sm font-semibold text-white disabled:opacity-60">
            <Search className="h-4 w-4" /> Abrir
          </button>
        </div>
      </section>

      {error ? <div className="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</div> : null}
      {message ? <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{message}</div> : null}

      <section className="grid gap-6 xl:grid-cols-[minmax(0,1.35fr)_minmax(360px,0.65fr)]">
        <div className="min-w-0">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-primary">Campos por revisar</h2>
            <button type="button" onClick={() => void refreshLibrary()} className="inline-flex items-center gap-2 rounded-lg border border-[var(--line)] px-3 py-2 text-sm text-secondary">
              <RefreshCw className="h-4 w-4" /> Biblioteca
            </button>
          </div>
          <div className="overflow-hidden rounded-lg border border-[var(--line)]">
            <div className="grid grid-cols-[80px_minmax(160px,1fr)_minmax(180px,1fr)_120px_140px] bg-[var(--surface-muted)] px-3 py-2 text-xs font-semibold uppercase tracking-wide text-secondary">
              <span>ID</span><span>Código</span><span>Valor</span><span>Etiqueta</span><span>Estado</span>
            </div>
            {(review?.fields ?? []).map((field) => (
              <button key={field.id} type="button" onClick={() => setSelectedFieldId(field.id)} className={`grid w-full grid-cols-[80px_minmax(160px,1fr)_minmax(180px,1fr)_120px_140px] items-center gap-3 border-t border-[var(--line)] px-3 py-3 text-left text-sm ${selectedFieldId === field.id ? "bg-primary/5" : "bg-white"}`}>
                <span className="font-mono text-xs text-secondary">{field.id}</span>
                <span className="truncate font-semibold text-primary">{field.proposed_field_code ?? field.field_code ?? "SIN_CODIGO"}</span>
                <span className="truncate text-secondary">{field.proposed_value ?? field.original_value ?? ""}</span>
                <span className="text-secondary">{field.fixed_variable_label}</span>
                <span className={`w-fit rounded-full border px-2 py-1 text-xs ${statusTone(field.status)}`}>{field.status}</span>
              </button>
            ))}
            {!review ? <div className="px-4 py-8 text-sm text-secondary">Abre una decisión híbrida para iniciar la revisión.</div> : null}
          </div>
        </div>

        <aside className="flex flex-col gap-4">
          <div className="rounded-lg border border-[var(--line)] bg-white p-4">
            <h2 className="text-lg font-semibold text-primary">Acción</h2>
            {selectedField ? (
              <FieldDecisionPanel field={selectedField} disabled={isBusy} onDecide={decide} />
            ) : (
              <p className="mt-3 text-sm text-secondary">Selecciona un campo.</p>
            )}
          </div>
          <div className="rounded-lg border border-[var(--line)] bg-white p-4">
            <h2 className="text-lg font-semibold text-primary">Aprobación</h2>
            <div className="mt-3 grid gap-3">
              <input value={templateName} onChange={(event) => setTemplateName(event.target.value)} className="ep-input h-10 px-3" />
              <select value={templateKind} onChange={(event) => setTemplateKind(event.target.value)} className="ep-select h-10 px-3">
                <option value="individual">Individual</option>
                <option value="master">Maestra</option>
              </select>
              <button type="button" disabled={!review || isBusy} onClick={() => void approve()} className="inline-flex items-center justify-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white disabled:opacity-60">
                <Save className="h-4 w-4" /> Aprobar plantilla
              </button>
            </div>
          </div>
        </aside>
      </section>

      <section className="grid gap-6 xl:grid-cols-2">
        <div>
          <h2 className="mb-3 text-lg font-semibold text-primary">Original vs propuesta</h2>
          <div className="grid gap-3">
            {(review?.visual_review ?? []).map((block) => (
              <div key={block.block_id} className="rounded-lg border border-[var(--line)] bg-white p-4">
                <p className="font-mono text-xs text-secondary">{block.location_key}</p>
                <div className="mt-3 grid gap-3 md:grid-cols-2">
                  <p className="rounded-md bg-slate-50 p-3 text-sm text-secondary">{block.original_text}</p>
                  <p className="rounded-md bg-amber-50 p-3 text-sm font-medium text-primary">{block.proposed_text}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div>
          <h2 className="mb-3 text-lg font-semibold text-primary">Biblioteca</h2>
          <div className="grid gap-3">
            {library.map((item) => {
              const versionId = item.approved_version_id ?? item.latest_version_id;
              return (
                <div key={item.id} className="rounded-lg border border-[var(--line)] bg-white p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="font-semibold text-primary">{item.name}</p>
                      <p className="mt-1 text-sm text-secondary">{item.template_kind} · {item.act_code ?? "sin acto"} · {item.status}</p>
                    </div>
                    <History className="h-4 w-4 text-secondary" />
                  </div>
                  <div className="mt-4 flex flex-wrap gap-2">
                    {versionId ? (
                      <a href={templateVersionDocxUrl(versionId)} className="inline-flex items-center gap-2 rounded-lg border border-[var(--line)] px-3 py-2 text-sm text-primary">
                        <Download className="h-4 w-4" /> DOCX
                      </a>
                    ) : null}
                    {versionId ? (
                      <button type="button" onClick={() => void rollback(item)} className="inline-flex items-center gap-2 rounded-lg border border-[var(--line)] px-3 py-2 text-sm text-secondary">
                        <RotateCcw className="h-4 w-4" /> Rollback
                      </button>
                    ) : null}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>
    </main>
  );
}

function FieldDecisionPanel({ field, disabled, onDecide }: { field: HumanReviewField; disabled: boolean; onDecide: (field: HumanReviewField, action: string, overrides?: Partial<HumanReviewField>) => Promise<void> }) {
  const [code, setCode] = useState(field.proposed_field_code ?? field.field_code ?? "");
  const [value, setValue] = useState(field.proposed_value ?? field.original_value ?? "");
  const [scope, setScope] = useState(field.apply_scope || "single");
  const [label, setLabel] = useState(field.fixed_variable_label || "unknown");

  useEffect(() => {
    setCode(field.proposed_field_code ?? field.field_code ?? "");
    setValue(field.proposed_value ?? field.original_value ?? "");
    setScope(field.apply_scope || "single");
    setLabel(field.fixed_variable_label || "unknown");
  }, [field.id, field.proposed_field_code, field.field_code, field.proposed_value, field.original_value, field.apply_scope, field.fixed_variable_label]);

  const overrides = { proposed_field_code: code, proposed_value: value, apply_scope: scope, fixed_variable_label: label };

  return (
    <div className="mt-4 grid gap-3">
      <label className="grid gap-1 text-sm font-medium text-primary">Código canónico<input value={code} onChange={(event) => setCode(event.target.value)} className="ep-input h-10 px-3" /></label>
      <label className="grid gap-1 text-sm font-medium text-primary">Valor<input value={value} onChange={(event) => setValue(event.target.value)} className="ep-input h-10 px-3" /></label>
      <div className="grid grid-cols-2 gap-3">
        <select value={scope} onChange={(event) => setScope(event.target.value)} className="ep-select h-10 px-3">
          <option value="single">Una aparición</option>
          <option value="all">Todas</option>
        </select>
        <select value={label} onChange={(event) => setLabel(event.target.value)} className="ep-select h-10 px-3">
          {fieldLabels.map((item) => <option key={item} value={item}>{item}</option>)}
        </select>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <button type="button" disabled={disabled} onClick={() => void onDecide(field, "accept", overrides)} className="inline-flex items-center justify-center gap-2 rounded-lg bg-emerald-600 px-3 py-2 text-sm font-semibold text-white disabled:opacity-60"><Check className="h-4 w-4" /> Aceptar</button>
        <button type="button" disabled={disabled} onClick={() => void onDecide(field, "reject", overrides)} className="inline-flex items-center justify-center gap-2 rounded-lg bg-rose-600 px-3 py-2 text-sm font-semibold text-white disabled:opacity-60"><X className="h-4 w-4" /> Rechazar</button>
        <button type="button" disabled={disabled} onClick={() => void onDecide(field, "correct", overrides)} className="inline-flex items-center justify-center gap-2 rounded-lg border border-[var(--line)] px-3 py-2 text-sm font-semibold text-primary disabled:opacity-60">Corregir</button>
        <button type="button" disabled={disabled} onClick={() => void onDecide(field, "propose_new", overrides)} className="inline-flex items-center justify-center gap-2 rounded-lg border border-[var(--line)] px-3 py-2 text-sm font-semibold text-primary disabled:opacity-60">Proponer</button>
      </div>
    </div>
  );
}
