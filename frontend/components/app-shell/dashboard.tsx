"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  ArrowRight,
  BarChart3,
  CalendarClock,
  Clock3,
  Filter,
  LineChart,
  RefreshCw,
  ShieldAlert,
  Target,
  UsersRound,
} from "lucide-react";
import {
  getExecutiveDashboard,
  type DashboardAlert,
  type DashboardChartDatum,
  type DashboardKpi,
  type DashboardTrendDatum,
  type ExecutiveDashboard,
  type ExecutiveDashboardFilters,
} from "@/lib/api";
import { LiveClock } from "@/components/ui/live-clock";
import { formatDateTime } from "@/lib/datetime";

function toneClasses(tone: string) {
  if (tone === "critical") return "ep-kpi-critical";
  if (tone === "warning") return "ep-kpi-warning";
  if (tone === "success") return "ep-kpi-success";
  return "ep-card";
}

function statusClasses(level: string) {
  if (level === "warning") return "bg-amber-500";
  if (level === "critical") return "bg-rose-500";
  return "bg-emerald-500";
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

function AlertsCard({ alerts }: { alerts: DashboardAlert[] }) {
  return (
    <article className="ep-card min-w-0 rounded-[1.9rem] p-6">
      <div className="flex min-w-0 items-start gap-3">
        <div className="rounded-2xl bg-amber-500/15 p-3">
          <AlertTriangle className="h-5 w-5 text-amber-600 dark:text-amber-300" />
        </div>
        <div className="min-w-0">
          <p className="text-sm font-semibold text-primary">Alertas y bloqueos</p>
          <p className="mt-1 text-sm leading-6 text-secondary">Lo que exige atención ejecutiva antes de entrar al detalle.</p>
        </div>
      </div>
      <div className="mt-6 space-y-3">
        {alerts.length === 0 ? <div className="ep-card-muted rounded-2xl px-4 py-4 text-sm text-secondary">Sin alertas críticas para los filtros actuales.</div> : null}
        {alerts.map((alert) => (
          <div key={`${alert.level}-${alert.title}`} className="ep-card-muted rounded-[1.4rem] px-4 py-4">
            <div className="flex items-center gap-2">
              <span className={`h-2.5 w-2.5 rounded-full ${statusClasses(alert.level)}`} />
              <p className="text-sm font-semibold text-primary">{alert.title}</p>
            </div>
            <p className="mt-2 text-sm leading-6 text-secondary">{alert.detail}</p>
          </div>
        ))}
      </div>
    </article>
  );
}

function FocusListCard({ title, subtitle, items }: { title: string; subtitle: string; items: Array<{ label: string; detail: string }> }) {
  return (
    <article className="ep-card min-w-0 rounded-[1.9rem] p-6">
      <div className="flex min-w-0 items-start gap-3">
        <div className="rounded-2xl bg-primary/10 p-3">
          <Target className="h-5 w-5 text-primary" />
        </div>
        <div className="min-w-0">
          <p className="text-sm font-semibold text-primary">{title}</p>
          <p className="mt-1 text-sm leading-6 text-secondary">{subtitle}</p>
        </div>
      </div>
      <div className="mt-6 space-y-3">
        {items.map((item) => (
          <div key={item.label} className="ep-card-muted rounded-[1.4rem] px-4 py-4">
            <p className="text-sm font-semibold text-primary">{item.label}</p>
            <p className="mt-2 text-sm leading-6 text-secondary">{item.detail}</p>
          </div>
        ))}
      </div>
    </article>
  );
}

export function DashboardOverview() {
  const [filters, setFilters] = useState<ExecutiveDashboardFilters>({});
  const [draftFilters, setDraftFilters] = useState<ExecutiveDashboardFilters>({});
  const [dashboard, setDashboard] = useState<ExecutiveDashboard | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void loadDashboard(filters);
  }, [filters]);

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
  const topState = dashboard?.documents_by_state[0];
  const topNotary = dashboard?.documents_by_notary[0];
  const topOwner = dashboard?.owner_ranking[0];
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

  const pendingItems = [
    {
      label: "Cola madura",
      detail: `${formatNumber(findKpi(dashboard, "elaborated"))} minutas listas para revisión o cierre.`,
    },
    {
      label: "Firmados pendientes",
      detail: `${formatNumber(findKpi(dashboard, "critical_alerts"))} pendientes visibles requieren cierre documental.`,
    },
    {
      label: "Clientes por responder",
      detail: `${formatNumber(dashboard.documents_by_state.find((item) => item.label === "revision_cliente")?.value ?? 0)} expedientes esperan respuesta del cliente.`,
    },
  ];

  const agendaItems = [
    {
      label: "Mover cuello de botella",
      detail: topState ? `${topState.label} concentra ${formatNumber(topState.value)} minutas y debe destrabarse primero.` : "No hay un estado dominante en este corte.",
    },
    {
      label: "Revisar capacidad",
      detail: topOwner ? `${topOwner.label} es el responsable con mayor carga visible.` : "No hay responsables destacados para este filtro.",
    },
    {
      label: "Enfocar seguimiento",
      detail: topNotary ? `${topNotary.label} concentra el mayor volumen documental.` : "No hay concentración notarial visible en este corte.",
    },
  ];

  const operationalNotes = [
    {
      label: "Estado dominante",
      detail: topState ? `${topState.label} concentra la mayor presión del flujo con ${formatNumber(topState.value)} minutas.` : "Sin presión operativa dominante para este filtro.",
    },
    {
      label: "Responsable a reforzar",
      detail: topOwner ? `${topOwner.label} lidera la carga visible y puede requerir redistribución.` : "Sin responsable principal en el corte actual.",
    },
    {
      label: "Notaría foco",
      detail: pilot ? `${pilot.municipality}, ${pilot.department} sigue como referencia operativa para demo.` : "No hay notaría piloto definida para este corte.",
    },
  ];

  return (
    <div className="space-y-8 xl:space-y-9">
      <section className="ep-card rounded-[2rem] p-6 sm:p-7">
        <div className="flex flex-col gap-6 xl:flex-row xl:items-start xl:justify-between">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 rounded-full border border-primary/10 bg-primary/8 px-3 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-primary">
              <ShieldAlert className="h-3.5 w-3.5" />
              Resumen ejecutivo
            </div>
            <h1 className="mt-4 text-3xl font-semibold tracking-[-0.05em] text-primary sm:text-[2.6rem] sm:leading-[1.02]">
              Qué está pasando hoy, qué requiere atención y qué mover primero.
            </h1>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 xl:w-[520px]">
            <div className="ep-card-muted rounded-[1.5rem] p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-secondary">Hora actual</p>
              <p className="mt-2 text-base font-semibold text-primary"><LiveClock /></p>
            </div>
            <div className="ep-card-muted rounded-[1.5rem] p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-secondary">Última actualización</p>
              <p className="mt-2 text-base font-semibold text-primary">{formatDateTime(dashboard.generated_at)}</p>
            </div>
            <div className="rounded-[1.5rem] bg-primary p-4 text-white shadow-panel sm:col-span-2">
              <p className="text-xs uppercase tracking-[0.18em] text-white/70">Notaría piloto</p>
              <p className="mt-2 text-base font-semibold">{pilot ? `${pilot.municipality}, ${pilot.department}` : "Sin referencia"}</p>
            </div>
          </div>
        </div>

        <form onSubmit={applyFilters} className="ep-filter-panel mt-7 rounded-[1.8rem] p-4 sm:p-5">
          <div className="flex items-center gap-3">
            <Filter className="h-4 w-4 text-primary" />
            <p className="text-sm font-semibold text-primary">Filtros ejecutivos</p>
          </div>
          <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-12">
            <label className="grid gap-2 text-sm font-medium text-primary xl:col-span-2">Fecha desde<input type="date" value={draftFilters.date_from ?? ""} onChange={(event) => updateDraft("date_from", event.target.value)} className="ep-input h-12 rounded-2xl px-4" /></label>
            <label className="grid gap-2 text-sm font-medium text-primary xl:col-span-2">Fecha hasta<input type="date" value={draftFilters.date_to ?? ""} onChange={(event) => updateDraft("date_to", event.target.value)} className="ep-input h-12 rounded-2xl px-4" /></label>
            <label className="grid gap-2 text-sm font-medium text-primary xl:col-span-2">Notaría<select value={draftFilters.notary_id ?? ""} onChange={(event) => updateDraft("notary_id", event.target.value)} className="ep-select h-12 rounded-2xl px-4">{dashboard.filter_options.notaries.map((option) => <option key={`${option.id ?? "all"}-${option.label}`} value={option.id?.toString() ?? ""}>{option.label}</option>)}</select></label>
            <label className="grid gap-2 text-sm font-medium text-primary xl:col-span-2">Estado<select value={draftFilters.state ?? ""} onChange={(event) => updateDraft("state", event.target.value)} className="ep-select h-12 rounded-2xl px-4">{dashboard.filter_options.states.map((option) => <option key={option.label} value={option.label === "Todos los estados" ? "" : option.label}>{option.label}</option>)}</select></label>
            <label className="grid gap-2 text-sm font-medium text-primary xl:col-span-2">Tipo de acto<select value={draftFilters.act_type ?? ""} onChange={(event) => updateDraft("act_type", event.target.value)} className="ep-select h-12 rounded-2xl px-4">{dashboard.filter_options.act_types.map((option) => <option key={option.label} value={option.label === "Todos los actos" ? "" : option.label}>{option.label}</option>)}</select></label>
            <label className="grid gap-2 text-sm font-medium text-primary xl:col-span-2">Responsable<select value={draftFilters.owner_user_id ?? ""} onChange={(event) => updateDraft("owner_user_id", event.target.value)} className="ep-select h-12 rounded-2xl px-4">{dashboard.filter_options.owners.map((option) => <option key={`${option.id ?? "all"}-${option.label}`} value={option.id?.toString() ?? ""}>{option.label}</option>)}</select></label>
          </div>
          <div className="mt-5 flex flex-wrap gap-3">
            <button type="submit" disabled={isLoading} className="inline-flex items-center gap-2 rounded-full bg-primary px-5 py-3 text-sm font-semibold text-white shadow-panel disabled:opacity-70">
              <RefreshCw className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
              Aplicar filtros
            </button>
            <button type="button" onClick={resetFilters} className="ep-card-soft inline-flex items-center gap-2 rounded-full px-5 py-3 text-sm font-semibold text-primary">
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
              <p className="text-xs uppercase tracking-[0.18em] text-secondary">{item.label}</p>
              <p className="mt-3 text-3xl font-semibold tracking-[-0.05em] text-primary">{formatNumber(item.value)}</p>
              <p className="mt-3 text-sm leading-6 text-secondary">{item.detail}</p>
            </article>
          );
        })}
      </section>

      <section className="grid gap-6 xl:grid-cols-[minmax(0,1.52fr)_minmax(300px,0.78fr)] 2xl:grid-cols-[minmax(0,1.58fr)_minmax(340px,0.74fr)]">
        <article className="ep-card min-w-0 overflow-hidden rounded-[2rem]">
          <div className="grid gap-6 bg-[radial-gradient(circle_at_top_left,rgba(80,214,144,0.12),transparent_32%),linear-gradient(180deg,rgba(var(--panel),1)_0%,rgba(var(--panel-strong),1)_100%)] p-6 sm:p-7">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
              <div className="max-w-3xl">
              </div>
            </div>

            <div className="grid gap-4 xl:grid-cols-12">
              <div className="ep-card-soft rounded-[1.8rem] p-5 sm:p-6 xl:col-span-7">
                <p className="text-xs uppercase tracking-[0.16em] text-secondary">Foco del día</p>
                <h3 className="mt-3 text-3xl font-semibold tracking-[-0.05em] text-primary">{topState?.label ?? "Sin estado dominante"}</h3>
                <p className="mt-3 text-sm leading-7 text-secondary">
                  {topState ? `${formatNumber(topState.value)} minutas concentran la mayor presión operativa visible. Conviene revisar responsables, bloqueos y tiempo en cola antes de entrar al detalle individual.` : "No hay presión operativa registrada para el filtro actual."}
                </p>
                <div className="mt-6 grid gap-3 md:grid-cols-3">
                  <div className="ep-card-muted rounded-[1.35rem] px-4 py-4">
                    <p className="text-xs uppercase tracking-[0.16em] text-secondary">Responsable con más carga</p>
                    <p className="mt-2 text-lg font-semibold text-primary">{topOwner?.label ?? "Sin responsable"}</p>
                    <p className="mt-2 text-sm leading-6 text-secondary">{topOwner ? `${formatNumber(topOwner.value)} minutas visibles en su carga.` : "Sin responsables activos en este filtro."}</p>
                  </div>
                  <div className="ep-card-muted rounded-[1.35rem] px-4 py-4">
                    <p className="text-xs uppercase tracking-[0.16em] text-secondary">Notaría a observar</p>
                    <p className="mt-2 text-lg font-semibold text-primary">{topNotary?.label ?? "Sin referencia"}</p>
                    <p className="mt-2 text-sm leading-6 text-secondary">{topNotary ? `${formatNumber(topNotary.value)} documentos asociados.` : "Sin concentración visible por notaría."}</p>
                  </div>
                  <div className="ep-card-muted rounded-[1.35rem] px-4 py-4">
                    <p className="text-xs uppercase tracking-[0.16em] text-secondary">Siguiente decisión</p>
                    <p className="mt-2 text-lg font-semibold text-primary">Revisar cola y reasignación</p>
                    <p className="mt-2 text-sm leading-6 text-secondary">Prioriza minutas bloqueadas, carga por responsable y pendientes de cierre.</p>
                  </div>
                </div>
                <div className="mt-6">
                  <a href="/dashboard/casos" className="inline-flex items-center gap-2 rounded-full bg-primary px-5 py-3 text-sm font-semibold text-white shadow-panel">
                    Abrir minutas
                    <ArrowRight className="h-4 w-4" />
                  </a>
                </div>
              </div>

              <div className="grid gap-4 xl:col-span-5">
                <div className="ep-card-muted rounded-[1.5rem] px-5 py-5 shadow-soft">
                  <div className="flex items-center gap-2 text-primary"><Clock3 className="h-4 w-4" /><p className="text-sm font-semibold">Minutas en trámite</p></div>
                  <p className="mt-3 text-3xl font-semibold text-primary">{formatNumber(findKpi(dashboard, "in_progress"))}</p>
                  <p className="mt-2 text-sm leading-6 text-secondary">Pulso general del tablero para iniciar la lectura.</p>
                </div>
                <div className="ep-card-muted rounded-[1.5rem] px-5 py-5 shadow-soft">
                  <div className="flex items-center gap-2 text-primary"><UsersRound className="h-4 w-4" /><p className="text-sm font-semibold">Usuarios activos</p></div>
                  <p className="mt-3 text-3xl font-semibold text-primary">{formatNumber(findKpi(dashboard, "users_active"))}</p>
                  <p className="mt-2 text-sm leading-6 text-secondary">Capacidad operativa disponible para repartir carga hoy.</p>
                </div>
                <div className="ep-card-muted rounded-[1.5rem] px-5 py-5 shadow-soft">
                  <div className="flex items-center gap-2 text-primary"><CalendarClock className="h-4 w-4" /><p className="text-sm font-semibold">Cierre del día</p></div>
                  <p className="mt-3 text-lg font-semibold text-primary">{formatNumber(findKpi(dashboard, "finalized"))} minutas finalizadas</p>
                  <p className="mt-2 text-sm leading-6 text-secondary">Úsalo como referencia rápida de avance antes de revisar gráficos.</p>
                </div>
              </div>
            </div>
          </div>
        </article>

        <div className="min-w-0 max-w-[460px] xl:max-w-none">
          <FocusListCard title="Lectura operativa" subtitle="Secuencia recomendada para tomar decisiones con menos ruido visual." items={operationalNotes} />
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[minmax(340px,1.12fr)_minmax(300px,0.9fr)_minmax(320px,0.98fr)]">
        <div className="min-w-0">
          <AlertsCard alerts={dashboard.critical_alerts} />
        </div>
        <div className="min-w-0">
          <FocusListCard title="Pendientes" subtitle="Tres frentes resumidos sin comprimir más contenido del necesario." items={pendingItems} />
        </div>
        <div className="min-w-0">
          <FocusListCard title="Agenda sugerida" subtitle="Orden corto para la demo y para la operación diaria." items={agendaItems} />
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
        <div className="min-w-0">
          <ChartCard title="Documentos por notaría" subtitle="Distribución multinotaría con foco en concentración visible." data={dashboard.documents_by_notary} />
        </div>
        <div className="min-w-0">
          <ChartCard title="Documentos por estado" subtitle="Dónde está detenido o avanzando el flujo documental." data={dashboard.documents_by_state} />
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[minmax(0,1.24fr)_minmax(340px,0.9fr)]">
        <div className="min-w-0">
          <TrendCard data={dashboard.temporal_trend} />
        </div>
        <div className="min-w-0">
          <ChartCard title="Documentos por tipo de acto" subtitle="Composición documental del periodo filtrado." data={dashboard.documents_by_act_type} />
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[minmax(0,1.15fr)_minmax(340px,0.85fr)]">
        <div className="min-w-0">
          <ChartCard title="Ranking de responsables" subtitle="Usuarios con mayor carga visible para balancear trabajo." data={dashboard.owner_ranking} />
        </div>
        <div className="min-w-0">
          <ChartCard title="Focos activos" subtitle="Lotes o frentes operativos destacados dentro del corte actual." data={dashboard.operational_focus} />
        </div>
      </section>

      {error ? <div className="ep-kpi-critical rounded-2xl px-4 py-3 text-sm">{error}</div> : null}
    </div>
  );
}
