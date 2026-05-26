"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { BarChart3, Building2, Filter, LineChart, RefreshCw, ShieldAlert } from "lucide-react";
import { PieChart, Pie, Cell, Tooltip } from "recharts";
import {
  getCurrentUser,
  getExecutiveDashboard,
  type DashboardChartDatum,
  type DashboardKpi,
  type DashboardTrendDatum,
  type ExecutiveDashboard,
  type ExecutiveDashboardFilters,
} from "@/lib/api";
import { LiveClock } from "@/components/ui/live-clock";
import { formatDateTime } from "@/lib/datetime";
import { CHART_PALETTE } from "@/lib/color-constants";

function formatEstado(estado: string): string {
  return estado
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function toneClasses(tone: string) {
  if (tone === "critical") return "ep-kpi-critical";
  if (tone === "warning") return "ep-kpi-warning";
  if (tone === "success") return "ep-kpi-success";
  return "ep-card";
}

function formatNumber(value: number) {
  return new Intl.NumberFormat("es-CO").format(value);
}

function findKpi(dashboard: ExecutiveDashboard, key: string) {
  return dashboard.kpis.find((item) => item.key === key)?.value ?? 0;
}

function ChartCard({ title, subtitle, data }: { title: string; subtitle: string; data: DashboardChartDatum[] }) {
  const maxValue = Math.max(...data.map((item) => item.value), 1);

  return (
    <article className="ep-card min-w-0 rounded-[1.9rem] p-6">
      <div className="flex min-w-0 items-start gap-3">
        <div className="rounded-2xl bg-primary/10 p-3">
          <BarChart3 className="h-5 w-5 text-primary" />
        </div>
        <div className="min-w-0">
          <p className="text-sm font-semibold text-primary">{title}</p>
          <p className="mt-1 text-sm leading-6 text-secondary">{subtitle}</p>
        </div>
      </div>
      <div className="mt-6 space-y-4">
        {data.length === 0 ? <div className="ep-card-muted rounded-2xl px-4 py-4 text-sm text-secondary">Sin datos para el filtro actual.</div> : null}
        {data.map((item) => (
          <div key={item.label} className="space-y-2.5">
            <div className="flex items-center justify-between gap-3 text-sm">
              <p className={`truncate font-medium ${item.highlight ? "text-primary" : "text-secondary"}`}>{item.label}</p>
              <span className="shrink-0 font-semibold text-primary">{formatNumber(item.value)}</span>
            </div>
            <div className="h-2.5 rounded-full bg-[var(--panel-soft)]">
              <div className={`h-2.5 rounded-full ${item.highlight ? "bg-primary" : "bg-[color:rgb(var(--secondary)/0.35)]"}`} style={{ width: `${Math.max((item.value / maxValue) * 100, 8)}%` }} />
            </div>
          </div>
        ))}
      </div>
    </article>
  );
}

function TrendCard({ data }: { data: DashboardTrendDatum[] }) {
  const maxValue = Math.max(...data.map((item) => item.value), 1);

  return (
    <article className="ep-card min-w-0 rounded-[1.9rem] p-6">
      <div className="flex min-w-0 items-start gap-3">
        <div className="rounded-2xl bg-primary/10 p-3">
          <LineChart className="h-5 w-5 text-primary" />
        </div>
        <div className="min-w-0">
          <p className="text-sm font-semibold text-primary">Tendencia temporal</p>
          <p className="mt-1 text-sm leading-6 text-secondary">Ritmo de actividad por fecha de actualización, útil para lectura de desktop y laptop.</p>
        </div>
      </div>
      <div className="mt-6 flex min-h-[240px] items-end gap-3 overflow-x-auto pb-2">
        {data.length === 0 ? <div className="ep-card-muted rounded-2xl px-4 py-4 text-sm text-secondary">Sin datos para la ventana seleccionada.</div> : null}
        {data.map((item) => (
          <div key={item.label} className="flex min-w-[78px] flex-col items-center gap-3">
            <div className="text-sm font-semibold text-primary">{item.value}</div>
            <div className="flex h-40 w-full items-end rounded-t-[1rem] bg-[var(--panel-soft)] px-2 pb-0">
              <div className="w-full rounded-t-[1rem] bg-primary" style={{ height: `${Math.max((item.value / maxValue) * 100, 10)}%` }} />
            </div>
            <div className="text-center text-xs font-medium text-secondary">{item.label}</div>
          </div>
        ))}
      </div>
    </article>
  );
}

function CustomTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null;
  const d = payload[0];
  return (
    <div style={{ background: "var(--panel)", border: "0.5px solid var(--line)", borderRadius: 8, padding: "8px 12px", fontSize: 12, color: "var(--ink)", boxShadow: "0 2px 8px rgba(20,30,56,0.08)" }}>
      <p style={{ fontWeight: 500, marginBottom: 2 }}>{d.name}</p>
      <p style={{ color: "var(--text-muted)" }}>{d.value} casos · {d.payload.percent ? (d.payload.percent * 100).toFixed(1) : "—"}%</p>
    </div>
  );
}

function PieActCard({ data }: { data: DashboardChartDatum[] }) {
  return (
    <article className="ep-card rounded-[2rem] p-6">
      <p className="mb-4 text-sm font-semibold text-[var(--ink)]">Tipos de acto</p>
      <div style={{ display: "flex", gap: "1.5rem", alignItems: "center" }}>
        <PieChart width={200} height={200}>
          <Pie
            data={data}
            cx={100}
            cy={100}
            innerRadius={55}
            outerRadius={90}
            paddingAngle={2}
            dataKey="value"
            nameKey="label"
          >
            {data.map((_, i) => (
              <Cell key={i} fill={CHART_PALETTE[i % CHART_PALETTE.length]} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
        </PieChart>
        <div style={{ flex: 1, maxHeight: 200, overflowY: "auto", display: "flex", flexDirection: "column", gap: 6 }}>
          {data.map((entry, i) => (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <div style={{ width: 10, height: 10, borderRadius: 3, background: CHART_PALETTE[i % CHART_PALETTE.length], flexShrink: 0 }} />
              <span style={{ fontSize: 12, color: "var(--text-muted)", flex: 1, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                {entry.label}
              </span>
              <span style={{ fontSize: 12, fontWeight: 500, color: "var(--ink)", flexShrink: 0 }}>
                {entry.value}
              </span>
            </div>
          ))}
        </div>
      </div>
    </article>
  );
}

export function DashboardOverview() {
  const [filters, setFilters] = useState<ExecutiveDashboardFilters>({});
  const [draftFilters, setDraftFilters] = useState<ExecutiveDashboardFilters>({});
  const [dashboard, setDashboard] = useState<ExecutiveDashboard | null>(null);
  const [isSuperAdmin, setIsSuperAdmin] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void Promise.all([loadDashboard(filters), loadCurrentUser()]);
  }, [filters]);

  async function loadCurrentUser() {
    try {
      const user = await getCurrentUser();
      setIsSuperAdmin(user?.roles?.includes("super_admin") ?? false);
    } catch {
      setIsSuperAdmin(false);
    }
  }

  async function loadDashboard(nextFilters: ExecutiveDashboardFilters) {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getExecutiveDashboard(nextFilters);
      setDashboard(data);
      setDraftFilters({
        date_from: data.filters.date_from ?? "",
        date_to: data.filters.date_to ?? "",
        notary_id: data.filters.notary_id?.toString() ?? "",
        state: data.filters.state ?? "",
        act_type: data.filters.act_type ?? "",
        owner_user_id: data.filters.owner_user_id?.toString() ?? "",
      });
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "No fue posible cargar el dashboard ejecutivo.");
    } finally {
      setIsLoading(false);
    }
  }

  function updateDraft<K extends keyof ExecutiveDashboardFilters>(field: K, value: ExecutiveDashboardFilters[K]) {
    setDraftFilters((current) => ({ ...current, [field]: value }));
  }

  function applyFilters(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFilters({
      date_from: draftFilters.date_from?.trim() || undefined,
      date_to: draftFilters.date_to?.trim() || undefined,
      notary_id: draftFilters.notary_id?.trim() || undefined,
      state: draftFilters.state?.trim() || undefined,
      act_type: draftFilters.act_type?.trim() || undefined,
      owner_user_id: draftFilters.owner_user_id?.trim() || undefined,
    });
  }

  function resetFilters() {
    setDraftFilters({});
    setFilters({});
  }

  const leadKpis = useMemo(() => dashboard?.kpis.slice(0, 5) ?? [], [dashboard]);
  const docsByType = useMemo(() => dashboard?.documents_by_act_type ?? [], [dashboard]);
  const docsByState = useMemo(
    () => (dashboard?.documents_by_state ?? []).map((item) => ({ ...item, label: formatEstado(item.label) })),
    [dashboard],
  );
  const pilot = dashboard?.pilot_reference;

  if (isLoading && !dashboard) {
    return <div className="ep-card rounded-[2rem] p-6 text-secondary">Cargando resumen ejecutivo...</div>;
  }

  if (error && !dashboard) {
    return <div className="ep-kpi-critical rounded-[2rem] px-6 py-5 text-sm">{error}</div>;
  }

  if (!dashboard) {
    return <div className="ep-card rounded-[2rem] p-6 text-secondary">No hay datos disponibles.</div>;
  }

  return (
    <div className="space-y-8 xl:space-y-9">
      <section className="ep-card rounded-[2rem] p-6 sm:p-7">
        <div className="flex flex-col gap-6 xl:flex-row xl:items-start xl:justify-between">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 rounded-full border border-primary/10 bg-primary/8 px-3 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-primary">
              <ShieldAlert className="h-3.5 w-3.5" />
              Resumen ejecutivo
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 xl:w-[520px]">
            <div className="ep-card-muted rounded-[1.5rem] p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-secondary">Hora actual</p>
              <p className="mt-2 text-base font-semibold text-primary"><LiveClock /></p>
            </div>
            <div className="ep-card-muted rounded-[1.5rem] p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-secondary">ÚLTIMA ACTUALIZACIÓN</p>
              <p className="mt-2 text-base font-semibold text-primary">{formatDateTime(dashboard.generated_at)}</p>
            </div>
            <div className="flex items-center gap-3 rounded-xl border border-[var(--line)] bg-[var(--surface)] px-4 py-3 sm:col-span-2">
              <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-primary">
                <Building2 className="h-4 w-4 text-white" />
              </div>
              <div>
                <p className="text-[11px] uppercase tracking-wide text-[var(--text-muted)]">Notaría piloto</p>
                <p className="text-[14px] font-medium text-[var(--ink)]">{pilot ? `${pilot.municipality}, ${pilot.department}` : "Sin referencia"}</p>
              </div>
            </div>
          </div>
        </div>

        <form onSubmit={applyFilters} className="ep-filter-panel mt-7 rounded-[1.8rem] p-4 sm:p-5">
          <div className="flex items-center gap-3">
            <Filter className="h-4 w-4 text-primary" />
            <p className="text-sm font-semibold text-primary">Filtros ejecutivos</p>
          </div>
          <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <label className="grid gap-2 text-sm font-medium text-primary">Fecha desde<input type="date" value={draftFilters.date_from ?? ""} onChange={(event) => updateDraft("date_from", event.target.value)} className="ep-input h-12 rounded-lg px-4" /></label>
            <label className="grid gap-2 text-sm font-medium text-primary">Fecha hasta<input type="date" value={draftFilters.date_to ?? ""} onChange={(event) => updateDraft("date_to", event.target.value)} className="ep-input h-12 rounded-lg px-4" /></label>
            {isSuperAdmin ? (
              <div className="grid gap-2 text-sm font-medium text-primary">
                <label>Notaría</label>
                <select value={draftFilters.notary_id ?? ""} onChange={(event) => updateDraft("notary_id", event.target.value)} className="ep-select h-12 rounded-lg px-4">{dashboard.filter_options.notaries.map((option) => <option key={`${option.id ?? "all"}-${option.label}`} value={option.id?.toString() ?? ""}>{option.label}</option>)}</select>
              </div>
            ) : null}
            <label className="grid gap-2 text-sm font-medium text-primary">Estado<select value={draftFilters.state ?? ""} onChange={(event) => updateDraft("state", event.target.value)} className="ep-select h-12 rounded-lg px-4">{dashboard.filter_options.states.map((option) => <option key={option.label} value={option.label === "Todos los estados" ? "" : option.label}>{option.label}</option>)}</select></label>
            <label className="grid gap-2 text-sm font-medium text-primary">Tipo de acto<select value={draftFilters.act_type ?? ""} onChange={(event) => updateDraft("act_type", event.target.value)} className="ep-select h-12 rounded-lg px-4">{dashboard.filter_options.act_types.map((option) => <option key={option.label} value={option.label === "Todos los actos" ? "" : option.label}>{option.label}</option>)}</select></label>
            <label className="grid gap-2 text-sm font-medium text-primary">Responsable<select value={draftFilters.owner_user_id ?? ""} onChange={(event) => updateDraft("owner_user_id", event.target.value)} className="ep-select h-12 rounded-lg px-4">{dashboard.filter_options.owners.map((option) => <option key={`${option.id ?? "all"}-${option.label}`} value={option.id?.toString() ?? ""}>{option.label}</option>)}</select></label>
          </div>
          <div className="mt-5 flex flex-wrap gap-3">
            <button type="submit" disabled={isLoading} className="inline-flex items-center gap-2 rounded-lg bg-primary px-5 py-2.5 text-sm font-medium text-white hover:opacity-90 transition-opacity disabled:opacity-70">
              <RefreshCw className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
              Aplicar filtros
            </button>
            <button type="button" onClick={resetFilters} className="inline-flex items-center gap-2 rounded-lg border border-[var(--line)] bg-[var(--surface)] px-5 py-2.5 text-sm font-medium text-[var(--text-muted)] transition-colors hover:bg-[var(--line)]">
              Limpiar
            </button>
          </div>
        </form>
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-12">
        {leadKpis.map((item: DashboardKpi, index) => {
          const span = index < 2 ? "xl:col-span-3" : "xl:col-span-2";
          return (
            <article key={item.key} className={`${toneClasses(item.tone)} ${span} rounded-[1.7rem] p-5 shadow-soft`}>
              <p className="text-xs text-secondary">{item.label}</p>
              <p className="mt-3 text-3xl font-semibold tracking-[-0.05em] text-primary">{formatNumber(item.value)}</p>
              <p className="mt-3 text-sm leading-6 text-secondary">{item.detail}</p>
            </article>
          );
        })}
      </section>

      <section className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
        <div className="min-w-0">
          <ChartCard title="Documentos por estado" subtitle="Dónde está detenido o avanzando el flujo documental." data={docsByState} />
        </div>
        <div className="min-w-0">
          <TrendCard data={dashboard.temporal_trend} />
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[minmax(0,1.15fr)_minmax(340px,0.85fr)]">
        <div className="min-w-0">
          <ChartCard title="Ranking de responsables" subtitle="Usuarios con mayor carga visible para balancear trabajo." data={dashboard.owner_ranking} />
        </div>
        <div className="min-w-0">
          <PieActCard data={docsByType} />
        </div>
      </section>

      {error ? <div className="ep-kpi-critical rounded-2xl px-4 py-3 text-sm">{error}</div> : null}
    </div>
  );
}
