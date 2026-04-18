"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { RefreshCw } from "lucide-react";
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer
} from "recharts";
import {
  getNotaries,
  getNotaryFilterOptions,
  importAntioquiaSource,
  type NotaryFilterOptions,
  type NotaryFilters,
  type NotaryRecord
} from "@/lib/api";

const PAGE_SIZE = 20;

type StatusConfig = {
  key: string;
  label: string;
  badgeClass: string;
  chartColor: string;
};

const STATUS_CONFIG: StatusConfig[] = [
  { key: "prospecto", label: "Prospecto", badgeClass: "bg-slate-200 text-slate-700", chartColor: "#94a3b8" },
  { key: "contactado", label: "Contactado", badgeClass: "bg-blue-100 text-blue-700", chartColor: "#3b82f6" },
  { key: "en seguimiento", label: "En seguimiento", badgeClass: "bg-cyan-100 text-cyan-700", chartColor: "#06b6d4" },
  {
    key: "reunión agendada",
    label: "Reunión agendada",
    badgeClass: "bg-orange-100 text-orange-700",
    chartColor: "#f97316"
  },
  {
    key: "propuesta enviada",
    label: "Propuesta enviada",
    badgeClass: "bg-violet-100 text-violet-700",
    chartColor: "#8b5cf6"
  },
  { key: "negociación", label: "Negociación", badgeClass: "bg-amber-100 text-amber-700", chartColor: "#f59e0b" },
  {
    key: "cerrado ganado",
    label: "Cerrado ganado",
    badgeClass: "bg-emerald-100 text-emerald-700",
    chartColor: "#10b981"
  },
  { key: "cerrado perdido", label: "Cerrado perdido", badgeClass: "bg-red-100 text-red-700", chartColor: "#ef4444" },
  {
    key: "no interesado",
    label: "No interesado",
    badgeClass: "bg-slate-700 text-slate-100",
    chartColor: "#334155"
  }
];

const statusByKey = new Map<string, StatusConfig>(STATUS_CONFIG.map((status) => [status.key, status]));

const emptyFilters: NotaryFilters = {
  commercial_status: "",
  municipality: "",
  commercial_owner: "",
  priority: "",
  q: ""
};

function normalizeStatus(status: string): string {
  return status.trim().toLowerCase();
}

function badgeTone(status: string): string {
  return statusByKey.get(normalizeStatus(status))?.badgeClass ?? "bg-slate-100 text-slate-700";
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
  const [activeTab, setActiveTab] = useState<"lista" | "graficos">("lista");

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

  const statusCounts = useMemo(() => {
    const counts = new Map<string, number>(STATUS_CONFIG.map((status) => [status.key, 0]));
    for (const notary of notaries) {
      const normalized = normalizeStatus(notary.commercial_status || "");
      if (counts.has(normalized)) {
        counts.set(normalized, (counts.get(normalized) ?? 0) + 1);
      }
    }

    return STATUS_CONFIG.map((status) => ({
      ...status,
      count: counts.get(status.key) ?? 0
    }));
  }, [notaries]);

  const pieData = useMemo(
    () =>
      statusCounts
        .filter((item) => item.count > 0)
        .map((item) => ({
          name: item.label,
          value: item.count,
          color: item.chartColor
        })),
    [statusCounts]
  );

  const topMunicipalitiesData = useMemo(() => {
    const totals = new Map<string, number>();
    for (const notary of notaries) {
      const municipality = notary.municipality?.trim() || "Sin municipio";
      totals.set(municipality, (totals.get(municipality) ?? 0) + notary.activity_count);
    }

    return Array.from(totals.entries())
      .map(([municipality, gestiones]) => ({ municipality, gestiones }))
      .sort((a, b) => b.gestiones - a.gestiones)
      .slice(0, 10)
      .reverse();
  }, [notaries]);

  const ownersActivityData = useMemo(() => {
    const totals = new Map<string, number>();
    for (const notary of notaries) {
      const owner = notary.commercial_owner_display?.trim() || "Sin asignar";
      totals.set(owner, (totals.get(owner) ?? 0) + notary.activity_count);
    }

    return Array.from(totals.entries())
      .map(([responsable, gestiones]) => ({ responsable, gestiones }))
      .filter((item) => item.gestiones > 0)
      .sort((a, b) => b.gestiones - a.gestiones);
  }, [notaries]);

  const commercialProgressRate = useMemo(() => {
    if (totalNotaries === 0) {
      return 0;
    }

    const prospectCount = statusCounts.find((status) => status.key === "prospecto")?.count ?? 0;
    return ((totalNotaries - prospectCount) / totalNotaries) * 100;
  }, [statusCounts, totalNotaries]);

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

        <div className="mt-6 grid gap-4 md:grid-cols-3">
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
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          {statusCounts.map((status) => (
            <span key={status.key} className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${status.badgeClass}`}>
              {status.label}: {status.count}
            </span>
          ))}
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

        <div className="mt-6 flex gap-1 rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-1 w-fit">
          <button
            onClick={() => setActiveTab("lista")}
            className={
              activeTab === "lista"
                ? "rounded-xl bg-primary px-5 py-2 text-sm font-semibold text-white"
                : "rounded-xl px-5 py-2 text-sm font-medium text-secondary hover:bg-[var(--panel-soft)]"
            }
          >
            Lista
          </button>
          <button
            onClick={() => setActiveTab("graficos")}
            className={
              activeTab === "graficos"
                ? "rounded-xl bg-primary px-5 py-2 text-sm font-semibold text-white"
                : "rounded-xl px-5 py-2 text-sm font-medium text-secondary hover:bg-[var(--panel-soft)]"
            }
          >
            Gráficos
          </button>
        </div>

        {activeTab === "lista" && (
          <div className="mt-4 overflow-hidden rounded-[1.5rem] border border-slate-200/70 bg-white/80">
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
                            <span
                              className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${badgeTone(notary.commercial_status)}`}
                            >
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
        )}

        {activeTab === "graficos" && (
          <div className="mt-4 grid gap-4 xl:grid-cols-2">
            <div className="ep-card-soft rounded-[1.5rem] p-4">
              <p className="mb-3 text-sm font-semibold text-primary">Distribución por estado comercial</p>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie data={pieData} dataKey="value" nameKey="name" innerRadius={70} outerRadius={110} paddingAngle={2}>
                    {pieData.map((entry) => (
                      <Cell key={entry.name} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
              <div className="mt-3 flex flex-wrap gap-2 text-xs">
                {pieData.length > 0 ? (
                  pieData.map((item) => (
                    <span key={item.name} className="inline-flex items-center gap-2 rounded-full bg-slate-100 px-3 py-1 text-slate-700">
                      <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: item.color }} />
                      {item.name}: {item.value}
                    </span>
                  ))
                ) : (
                  <span className="text-secondary">Sin datos para el gráfico.</span>
                )}
              </div>
            </div>

            <div className="ep-card-soft rounded-[1.5rem] p-4">
              <p className="mb-3 text-sm font-semibold text-primary">Top 10 municipios por gestiones</p>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={topMunicipalitiesData} layout="vertical" margin={{ top: 8, right: 12, left: 12, bottom: 8 }}>
                  <XAxis type="number" />
                  <YAxis type="category" dataKey="municipality" width={120} />
                  <Tooltip />
                  <Bar dataKey="gestiones" fill="#2563eb" radius={[0, 6, 6, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="ep-card-soft rounded-[1.5rem] p-4">
              <p className="mb-3 text-sm font-semibold text-primary">Gestiones por responsable</p>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={ownersActivityData} margin={{ top: 8, right: 12, left: 0, bottom: 36 }}>
                  <XAxis dataKey="responsable" angle={-25} textAnchor="end" interval={0} height={70} />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="gestiones" fill="#0ea5e9" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="ep-card-soft rounded-[1.5rem] p-6">
              <p className="text-sm font-semibold text-primary">Tasa de avance comercial</p>
              <p className="mt-5 text-5xl font-semibold tracking-[-0.04em] text-primary">{commercialProgressRate.toFixed(1)}%</p>
              <p className="mt-3 text-sm leading-6 text-secondary">
                Porcentaje de notarías que avanzaron más allá de estado prospecto, calculado como (total - prospecto) /
                total * 100.
              </p>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
