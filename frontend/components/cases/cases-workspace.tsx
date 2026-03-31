"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { ArrowRight, ClipboardCheck, FileText, Filter, RefreshCw, UserRound } from "lucide-react";
import { getCaseFilters, getCases, type CaseFilterOptions, type CaseFilters, type CaseRecord } from "@/lib/api";

const emptyFilters: CaseFilters = {
  current_state: "",
  case_type: "",
  notary_id: "",
  current_owner_user_id: "",
  q: ""
};

function statusSummary(cases: CaseRecord[]) {
  const summary = new Map<string, number>();
  for (const item of cases) {
    summary.set(item.current_state, (summary.get(item.current_state) ?? 0) + 1);
  }
  return Array.from(summary.entries()).sort((a, b) => b[1] - a[1]);
}

export function CasesWorkspace() {
  const [cases, setCases] = useState<CaseRecord[]>([]);
  const [filters, setFilters] = useState<CaseFilters>(emptyFilters);
  const [filterOptions, setFilterOptions] = useState<CaseFilterOptions>({ case_types: [], act_types: [], states: [], owners: [], notaries: [] });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void Promise.all([loadCases(emptyFilters), loadFilters()]);
  }, []);

  async function loadCases(nextFilters: CaseFilters) {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getCases(nextFilters);
      setCases(data);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "No fue posible cargar los casos.");
    } finally {
      setIsLoading(false);
    }
  }

  async function loadFilters() {
    try {
      setFilterOptions(await getCaseFilters());
    } catch {
      // Mantener vista usable sin filtros.
    }
  }

  function updateFilter<K extends keyof CaseFilters>(field: K, value: string) {
    const nextFilters = { ...filters, [field]: value };
    setFilters(nextFilters);
    void loadCases(nextFilters);
  }

  const stateStats = useMemo(() => statusSummary(cases), [cases]);
  const clientReviewCount = useMemo(() => cases.filter((item) => item.requires_client_review).length, [cases]);
  const finalSignedCount = useMemo(() => cases.filter((item) => item.final_signed_uploaded).length, [cases]);

  const ownerOptions = useMemo(() => {
    const seen = new Map<string, string>();
    cases.forEach((item) => {
      if (item.current_owner_user_id && item.current_owner_user_name) {
        seen.set(String(item.current_owner_user_id), item.current_owner_user_name);
      }
    });
    return Array.from(seen.entries());
  }, [cases]);

  const notaryOptions = useMemo(() => {
    const seen = new Map<string, string>();
    cases.forEach((item) => {
      seen.set(String(item.notary_id), item.notary_label);
    });
    return Array.from(seen.entries());
  }, [cases]);

  return (
    <div className="space-y-6">
      <section className="ep-card rounded-[2rem] p-6">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
          <div className="max-w-3xl">
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-accent">Casos documentales</p>
            <h1 className="mt-3 text-3xl font-semibold tracking-[-0.05em] text-primary sm:text-4xl">Flujo base de escrituras con estados, responsables y trazabilidad</h1>
            <p className="mt-3 text-base leading-7 text-secondary">El producto ya está ordenado alrededor del proceso real: comercial, asignación de notaría, caso, revisión, aprobación, firma y cierre.</p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Link href="/dashboard/casos/crear" className="inline-flex items-center gap-2 rounded-2xl border border-[var(--line)] px-5 py-3 text-sm font-semibold text-primary">
              Crear caso
            </Link>
            <button onClick={() => void loadCases(filters)} className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white shadow-panel">
              <RefreshCw className="h-4 w-4" />
              Refrescar casos
            </button>
          </div>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-4">
          <div className="ep-card-muted rounded-[1.5rem] p-4"><p className="text-xs uppercase tracking-[0.2em] text-secondary">Casos visibles</p><p className="mt-3 text-3xl font-semibold text-primary">{cases.length}</p></div>
          <div className="ep-card-muted rounded-[1.5rem] p-4"><p className="text-xs uppercase tracking-[0.2em] text-secondary">Con revisión cliente</p><p className="mt-3 text-3xl font-semibold text-primary">{clientReviewCount}</p></div>
          <div className="ep-card-muted rounded-[1.5rem] p-4"><p className="text-xs uppercase tracking-[0.2em] text-secondary">Firmado cargado</p><p className="mt-3 text-3xl font-semibold text-primary">{finalSignedCount}</p></div>
          <div className="rounded-[1.5rem] bg-primary p-4 text-white shadow-panel"><p className="text-xs uppercase tracking-[0.2em] text-white/72">Estados activos</p><p className="mt-3 text-3xl font-semibold">{stateStats.length}</p></div>
        </div>
      </section>

      <section className="ep-card rounded-[2rem] p-6">
        <div className="flex flex-col gap-5 xl:flex-row xl:items-end xl:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.22em] text-accent">Filtros de proceso</p>
            <h2 className="mt-2 text-2xl font-semibold text-primary">Listado operativo de casos</h2>
          </div>
          <div className="ep-pill inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm text-secondary"><Filter className="h-4 w-4 text-primary" />Estado, tipo de caso, responsable y notaría</div>
        </div>

        <div className="ep-filter-panel mt-6 grid gap-4 rounded-[1.75rem] p-4 lg:grid-cols-5">
          <label className="grid gap-2 text-sm font-medium text-primary">Estado<select value={filters.current_state ?? ""} onChange={(event) => updateFilter("current_state", event.target.value)} className="ep-select h-12 rounded-2xl px-4"><option value="">Todos</option>{filterOptions.states.map((item) => <option key={item} value={item}>{item}</option>)}</select></label>
          <label className="grid gap-2 text-sm font-medium text-primary">Tipo de caso<select value={filters.case_type ?? ""} onChange={(event) => updateFilter("case_type", event.target.value)} className="ep-select h-12 rounded-2xl px-4"><option value="">Todos</option>{filterOptions.case_types.map((item) => <option key={item} value={item}>{item}</option>)}</select></label>
          <label className="grid gap-2 text-sm font-medium text-primary">Responsable<select value={filters.current_owner_user_id ?? ""} onChange={(event) => updateFilter("current_owner_user_id", event.target.value)} className="ep-select h-12 rounded-2xl px-4"><option value="">Todos</option>{ownerOptions.map(([id, name]) => <option key={id} value={id}>{name}</option>)}</select></label>
          <label className="grid gap-2 text-sm font-medium text-primary">Notaría<select value={filters.notary_id ?? ""} onChange={(event) => updateFilter("notary_id", event.target.value)} className="ep-select h-12 rounded-2xl px-4"><option value="">Todas</option>{notaryOptions.map(([id, label]) => <option key={id} value={id}>{label}</option>)}</select></label>
          <label className="grid gap-2 text-sm font-medium text-primary">Buscar<input value={filters.q ?? ""} onChange={(event) => updateFilter("q", event.target.value)} placeholder="Acto, caso, notaría..." className="ep-input h-12 rounded-2xl px-4" /></label>
        </div>

        {error ? <div className="ep-kpi-critical mt-5 rounded-2xl px-4 py-3 text-sm">{error}</div> : null}

        <div className="mt-6 grid gap-4 xl:grid-cols-[minmax(0,1.15fr)_320px]">
          <div className="space-y-3">
            {isLoading ? <div className="ep-card-muted rounded-[1.5rem] px-4 py-6 text-sm text-secondary">Cargando casos...</div> : null}
            {!isLoading && cases.length === 0 ? <div className="ep-card-muted rounded-[1.5rem] px-4 py-6 text-sm text-secondary">No hay casos para los filtros seleccionados.</div> : null}
            {cases.map((item) => (
              <Link key={item.id} href={`/dashboard/casos/${item.id}`} className="block ep-card-soft rounded-[1.6rem] p-5 transition hover:-translate-y-0.5 hover:border-primary/25 hover:shadow-soft">
                <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                  <div className="min-w-0">
                    <div className="flex items-center gap-3">
                      <span className="rounded-full bg-primary/10 px-3 py-1 text-xs font-semibold text-primary">{item.case_type}</span>
                      <h3 className="truncate text-lg font-semibold text-primary">{item.act_type}</h3>
                    </div>
                    <p className="mt-2 text-sm text-secondary">Caso {item.year}-{String(item.consecutive).padStart(4, "0")} · {item.notary_label}</p>
                    <p className="mt-2 text-sm leading-6 text-secondary">Responsable actual: {item.current_owner_user_name || "Sin asignar"}</p>
                  </div>
                  <div className="grid gap-2 text-sm text-secondary lg:min-w-[230px]">
                    <span className="ep-badge rounded-full px-3 py-1 font-semibold text-primary">{item.current_state}</span>
                    <span>Cliente: {item.client_user_name || "No aplica"}</span>
                    <span>Revisión cliente: {item.requires_client_review ? "Sí" : "No"}</span>
                    <span>Firmado final: {item.final_signed_uploaded ? "Cargado" : "Pendiente"}</span>
                  </div>
                </div>
                <div className="mt-4 flex items-center justify-between text-sm text-primary">
                  <span>{item.protocolist_user_name || "Sin protocolista"}</span>
                  <span className="inline-flex items-center gap-2 font-semibold">Ver detalle <ArrowRight className="h-4 w-4" /></span>
                </div>
              </Link>
            ))}
          </div>

          <aside className="space-y-4">
            <div className="rounded-[1.6rem] bg-primary p-5 text-white shadow-panel">
              <div className="flex items-center gap-3"><ClipboardCheck className="h-5 w-5 text-accent" /><p className="text-lg font-semibold">Proceso documental</p></div>
              <p className="mt-3 text-sm leading-6 text-white/82">El núcleo del caso ya diferencia diligenciamiento, revisión cliente, aprobador, notario, firmado y cierre.</p>
            </div>
            <div className="ep-card-soft rounded-[1.6rem] p-5">
              <div className="flex items-center gap-3"><FileText className="h-5 w-5 text-primary" /><p className="text-lg font-semibold text-primary">Estados</p></div>
              <div className="mt-4 space-y-3 text-sm text-secondary">
                {stateStats.slice(0, 5).map(([label, count]) => (
                  <div key={label} className="flex items-center justify-between ep-card-muted rounded-2xl px-4 py-3"><span>{label}</span><span className="font-semibold text-primary">{count}</span></div>
                ))}
              </div>
            </div>
            <div className="ep-card-soft rounded-[1.6rem] p-5">
              <div className="flex items-center gap-3"><UserRound className="h-5 w-5 text-primary" /><p className="text-lg font-semibold text-primary">Roles base</p></div>
              <p className="mt-3 text-sm leading-6 text-secondary">Protocolista, Cliente, Aprobador, Notario titular y Notario suplente quedan modelados dentro del caso.</p>
            </div>
          </aside>
        </div>
      </section>
    </div>
  );
}
