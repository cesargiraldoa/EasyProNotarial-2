"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { MapPinned, RefreshCw, Target } from "lucide-react";
import {
  getNotaries,
  getNotaryFilterOptions,
  importAntioquiaSource,
  type NotaryFilterOptions,
  type NotaryFilters,
  type NotaryRecord
} from "@/lib/api";

const PAGE_SIZE = 20;

const emptyFilters: NotaryFilters = {
  commercial_status: "",
  municipality: "",
  commercial_owner: "",
  priority: "",
  q: ""
};

const statusColorMap: Record<string, string> = {
  prospecto: "bg-slate-200 text-slate-700",
  contactado: "bg-blue-100 text-blue-700",
  negociación: "bg-amber-100 text-amber-700",
  "reunión agendada": "bg-orange-100 text-orange-700",
  "propuesta enviada": "bg-violet-100 text-violet-700",
  "cerrado ganado": "bg-emerald-100 text-emerald-700",
  "cerrado perdido": "bg-red-100 text-red-700"
};

function normalizeStatus(status: string): string {
  return status.trim().toLowerCase();
}

function badgeTone(status: string): string {
  return statusColorMap[normalizeStatus(status)] ?? "bg-slate-100 text-slate-700";
}

function summarizeStatus(notaries: NotaryRecord[]) {
  const summary = new Map<string, number>();
  for (const notary of notaries) {
    const key = notary.commercial_status || "sin estado";
    summary.set(key, (summary.get(key) ?? 0) + 1);
  }
  return Array.from(summary.entries()).sort((a, b) => b[1] - a[1]);
}

export function CommercialWorkspace() {
  const [notaries, setNotaries] = useState<NotaryRecord[]>([]);
  const [filters, setFilters] = useState<NotaryFilters>(emptyFilters);
  const [filterOptions, setFilterOptions] = useState<NotaryFilterOptions>({
    municipalities: [],
    commercial_owners: [],
    priorities: [],
    commercial_statuses: []
  });
  const [isLoading, setIsLoading] = useState(true);
  const [isImporting, setIsImporting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);

  useEffect(() => {
    void Promise.all([loadNotaries(emptyFilters), loadFilterOptions()]);
  }, []);

  async function loadNotaries(nextFilters: NotaryFilters) {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getNotaries(nextFilters);
      setNotaries(data);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "No fue posible cargar el workspace comercial.");
    } finally {
      setIsLoading(false);
    }
  }

  async function loadFilterOptions() {
    try {
      const data = await getNotaryFilterOptions();
      setFilterOptions(data);
    } catch {
      // Mantener vista operativa sin bloquear filtros pre-cargados.
    }
  }

  async function handleReimport() {
    setIsImporting(true);
    setError(null);
    try {
      await importAntioquiaSource(true);
      await Promise.all([loadNotaries(filters), loadFilterOptions()]);
    } catch (importError) {
      setError(importError instanceof Error ? importError.message : "No fue posible reimportar el catálogo.");
    } finally {
      setIsImporting(false);
    }
  }

  function updateFilter<K extends keyof NotaryFilters>(field: K, value: string) {
    const nextFilters = { ...filters, [field]: value };
    setFilters(nextFilters);
    setCurrentPage(1);
    void loadNotaries(nextFilters);
  }

  const statusSummary = useMemo(() => summarizeStatus(notaries), [notaries]);
  const totalNotaries = notaries.length;
  const highPriorityCount = useMemo(
    () => notaries.filter((notary) => ["alta", "crítica"].includes(notary.priority.toLowerCase())).length,
    [notaries]
  );
  const activeOwnersCount = useMemo(() => {
    const owners = new Set(
      notaries
        .map((notary) => notary.commercial_owner_display?.trim() || "")
        .filter((owner) => owner.length > 0)
    );
    return owners.size;
  }, [notaries]);
  const crmStatesCount = statusSummary.length;

  const totalPages = Math.max(1, Math.ceil(notaries.length / PAGE_SIZE));
  const pageStart = (currentPage - 1) * PAGE_SIZE;
  const currentRows = notaries.slice(pageStart, pageStart + PAGE_SIZE);

  function goToPage(page: number) {
    const boundedPage = Math.min(Math.max(page, 1), totalPages);
    setCurrentPage(boundedPage);
  }

  return (
    <div className="space-y-6">
      <section className="ep-card rounded-[2rem] p-6">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
          <div className="max-w-3xl">
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-accent">Comercial</p>
            <h1 className="mt-3 text-3xl font-semibold tracking-[-0.05em] text-primary sm:text-4xl">Comercial</h1>
            <p className="mt-3 text-base leading-7 text-secondary">Gestión comercial y prospección de notarías</p>
          </div>
          <button
            onClick={handleReimport}
            disabled={isImporting}
            className="inline-flex items-center justify-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white shadow-panel transition hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-70"
          >
            <RefreshCw className={`h-4 w-4 ${isImporting ? "animate-spin" : ""}`} />
            {isImporting ? "Reimportando..." : "Reimportar catálogo"}
          </button>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-4">
          <div className="ep-card-muted rounded-[1.5rem] p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-secondary">Total notarías</p>
            <p className="mt-3 text-3xl font-semibold text-primary">{totalNotaries}</p>
          </div>
          <div className="ep-card-muted rounded-[1.5rem] p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-secondary">Alta prioridad</p>
            <p className="mt-3 text-3xl font-semibold text-primary">{highPriorityCount}</p>
          </div>
          <div className="ep-card-muted rounded-[1.5rem] p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-secondary">Responsables activos</p>
            <p className="mt-3 text-3xl font-semibold text-primary">{activeOwnersCount}</p>
          </div>
          <div className="rounded-[1.5rem] bg-primary p-4 text-white shadow-panel">
            <p className="text-xs uppercase tracking-[0.2em] text-white/72">Estados CRM</p>
            <p className="mt-3 text-3xl font-semibold">{crmStatesCount}</p>
          </div>
        </div>
      </section>

      <section className="ep-card rounded-[2rem] p-6">
        <div className="ep-filter-panel grid gap-4 rounded-[1.75rem] p-4 lg:grid-cols-5">
          <label className="grid gap-2 text-sm font-medium text-primary">
            Estado comercial
            <select
              value={filters.commercial_status ?? ""}
              onChange={(event) => updateFilter("commercial_status", event.target.value)}
              className="ep-select h-12 rounded-2xl px-4"
            >
              <option value="">Todos</option>
              {filterOptions.commercial_statuses.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>

          <label className="grid gap-2 text-sm font-medium text-primary">
            Municipio
            <select
              value={filters.municipality ?? ""}
              onChange={(event) => updateFilter("municipality", event.target.value)}
              className="ep-select h-12 rounded-2xl px-4"
            >
              <option value="">Todos</option>
              {filterOptions.municipalities.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>

          <label className="grid gap-2 text-sm font-medium text-primary">
            Responsable
            <select
              value={filters.commercial_owner ?? ""}
              onChange={(event) => updateFilter("commercial_owner", event.target.value)}
              className="ep-select h-12 rounded-2xl px-4"
            >
              <option value="">Todos</option>
              {filterOptions.commercial_owners.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>

          <label className="grid gap-2 text-sm font-medium text-primary">
            Prioridad
            <select
              value={filters.priority ?? ""}
              onChange={(event) => updateFilter("priority", event.target.value)}
              className="ep-select h-12 rounded-2xl px-4"
            >
              <option value="">Todas</option>
              {filterOptions.priorities.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>

          <label className="grid gap-2 text-sm font-medium text-primary">
            Buscar
            <input
              value={filters.q ?? ""}
              onChange={(event) => updateFilter("q", event.target.value)}
              placeholder="Municipio, notaría, correo..."
              className="ep-input h-12 rounded-2xl px-4"
            />
          </label>
        </div>

        {error ? <div className="ep-kpi-critical mt-5 rounded-2xl px-4 py-3 text-sm">{error}</div> : null}

        <div className="mt-6 grid gap-4 xl:grid-cols-[minmax(0,1.2fr)_340px]">
          <div className="overflow-hidden rounded-[1.5rem] border border-slate-200/70 bg-white/80">
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead className="bg-slate-50/90 text-left text-xs uppercase tracking-[0.14em] text-secondary">
                  <tr>
                    <th className="px-4 py-3">Notaría</th>
                    <th className="px-4 py-3">Municipio</th>
                    <th className="px-4 py-3">Estado comercial</th>
                    <th className="px-4 py-3">Responsable</th>
                    <th className="px-4 py-3">Prioridad</th>
                    <th className="px-4 py-3">Gestiones</th>
                    <th className="px-4 py-3">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {isLoading ? (
                    <tr>
                      <td colSpan={7} className="px-4 py-6 text-secondary">
                        Cargando registros comerciales...
                      </td>
                    </tr>
                  ) : null}

                  {!isLoading && currentRows.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="px-4 py-6 text-secondary">
                        No hay notarías para los filtros seleccionados.
                      </td>
                    </tr>
                  ) : null}

                  {!isLoading
                    ? currentRows.map((notary) => (
                        <tr key={notary.id} className="border-t border-slate-200/70 text-primary">
                          <td className="px-4 py-3">
                            <p className="font-semibold">{notary.notary_label}</p>
                            <p className="text-xs text-secondary">{notary.department}</p>
                          </td>
                          <td className="px-4 py-3">{notary.municipality || "Sin municipio"}</td>
                          <td className="px-4 py-3">
                            <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${badgeTone(notary.commercial_status)}`}>
                              {notary.commercial_status || "sin estado"}
                            </span>
                          </td>
                          <td className="px-4 py-3">{notary.commercial_owner_display || "Sin asignar"}</td>
                          <td className="px-4 py-3">{notary.priority}</td>
                          <td className="px-4 py-3">{notary.activity_count}</td>
                          <td className="px-4 py-3">
                            <Link
                              href={`/dashboard/comercial/${notary.id}`}
                              className="inline-flex items-center rounded-xl bg-primary px-3 py-2 text-xs font-semibold text-white"
                            >
                              Ver CRM
                            </Link>
                          </td>
                        </tr>
                      ))
                    : null}
                </tbody>
              </table>
            </div>

            <div className="flex items-center justify-between border-t border-slate-200/70 px-4 py-3 text-sm text-secondary">
              <span>
                Página {currentPage} de {totalPages}
              </span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => goToPage(currentPage - 1)}
                  disabled={currentPage <= 1}
                  className="rounded-xl border border-slate-300 px-3 py-1.5 text-primary disabled:cursor-not-allowed disabled:opacity-40"
                >
                  Anterior
                </button>
                <button
                  onClick={() => goToPage(currentPage + 1)}
                  disabled={currentPage >= totalPages}
                  className="rounded-xl border border-slate-300 px-3 py-1.5 text-primary disabled:cursor-not-allowed disabled:opacity-40"
                >
                  Siguiente
                </button>
              </div>
            </div>
          </div>

          <aside className="space-y-4">
            <div className="ep-card-soft rounded-[1.6rem] p-5">
              <div className="flex items-center gap-3">
                <Target className="h-5 w-5 text-primary" />
                <p className="text-lg font-semibold text-primary">Radar comercial</p>
              </div>
              <div className="mt-4 space-y-3 text-sm text-secondary">
                {statusSummary.length === 0 ? (
                  <div className="ep-card-muted rounded-2xl px-4 py-3">Sin datos para resumir.</div>
                ) : (
                  statusSummary.map(([label, count]) => (
                    <div key={label} className="flex items-center justify-between ep-card-muted rounded-2xl px-4 py-3">
                      <span>{label}</span>
                      <span className="font-semibold text-primary">{count}</span>
                    </div>
                  ))
                )}
              </div>
            </div>

            <div className="ep-card-soft rounded-[1.6rem] p-5">
              <div className="flex items-center gap-3">
                <MapPinned className="h-5 w-5 text-primary" />
                <p className="text-lg font-semibold text-primary">Cobertura</p>
              </div>
              <p className="mt-3 text-sm leading-6 text-secondary">
                {filterOptions.municipalities.length} municipios disponibles en el catálogo comercial.
              </p>
            </div>
          </aside>
        </div>
      </section>
    </div>
  );
}
