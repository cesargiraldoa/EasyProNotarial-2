"use client";

import { type ReactNode, useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Database,
  Globe,
  LockKeyhole,
  RefreshCw,
  ServerCog,
  ShieldAlert,
  Zap,
} from "lucide-react";
import { getExecutiveDashboard, type DashboardAlert, type DashboardSystemStatusItem, type ExecutiveDashboard } from "@/lib/api";
import { LiveClock } from "@/components/ui/live-clock";
import { formatDateTime } from "@/lib/datetime";

type ServiceTone = "online" | "warning" | "degraded" | "offline";

function normalizeServiceStatus(status: string): ServiceTone {
  const normalized = status.trim().toLowerCase();
  if (["ok", "online", "healthy", "success"].includes(normalized)) return "online";
  if (["warning"].includes(normalized)) return "warning";
  if (["critical", "offline", "down"].includes(normalized)) return "offline";
  return "degraded";
}

function serviceStatusLabel(status: ServiceTone) {
  if (status === "online") return "Online";
  if (status === "warning") return "Warning";
  if (status === "offline") return "Offline";
  return "Degraded";
}

function serviceBadgeClasses(status: ServiceTone) {
  if (status === "online") return "bg-emerald-500/12 text-emerald-700 ring-1 ring-emerald-500/25 dark:text-emerald-300";
  if (status === "warning") return "bg-amber-500/12 text-amber-700 ring-1 ring-amber-500/25 dark:text-amber-300";
  if (status === "offline") return "bg-rose-500/14 text-rose-700 ring-1 ring-rose-500/25 dark:text-rose-300";
  return "bg-sky-500/12 text-sky-700 ring-1 ring-sky-500/25 dark:text-sky-300";
}

function serviceDotClasses(status: ServiceTone) {
  if (status === "online") return "bg-emerald-500";
  if (status === "warning") return "bg-amber-500";
  if (status === "offline") return "bg-rose-500";
  return "bg-sky-500";
}

function alertClasses(level: string) {
  const normalized = level.trim().toLowerCase();
  if (normalized === "critical") return "ep-kpi-critical";
  if (normalized === "warning") return "ep-kpi-warning";
  return "ep-kpi-success";
}

function resolveIcon(key: string) {
  switch (key) {
    case "backend":
      return ServerCog;
    case "frontend":
      return Globe;
    case "database":
      return Database;
    case "auth":
      return LockKeyhole;
    default:
      return Activity;
  }
}

function ServiceCard({ item }: { item: DashboardSystemStatusItem }) {
  const Icon = resolveIcon(item.key);
  const tone = normalizeServiceStatus(item.status);

  return (
    <article className="ep-card-soft rounded-[1.5rem] p-5">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <div className="rounded-2xl bg-primary/10 p-3">
            <Icon className="h-5 w-5 text-primary" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className={`h-2.5 w-2.5 rounded-full ${serviceDotClasses(tone)}`} />
              <p className="text-sm font-semibold text-primary">{item.label}</p>
            </div>
            <p className="mt-2 text-sm leading-6 text-secondary">{item.detail}</p>
          </div>
        </div>
        <span className={`rounded-full px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] ${serviceBadgeClasses(tone)}`}>
          {serviceStatusLabel(tone)}
        </span>
      </div>
    </article>
  );
}

function SummaryMetric({ label, value, tone }: { label: string; value: ReactNode; tone?: ServiceTone }) {
  return (
    <div className="ep-card-muted rounded-[1.25rem] px-4 py-4">
      <p className="text-[11px] uppercase tracking-[0.18em] text-secondary">{label}</p>
      <div className="mt-2 flex items-center gap-2">
        {tone ? <span className={`h-2.5 w-2.5 rounded-full ${serviceDotClasses(tone)}`} /> : null}
        <p className="text-sm font-semibold text-primary">{value}</p>
      </div>
    </div>
  );
}

export function SystemStatusWorkspace() {
  const [dashboard, setDashboard] = useState<ExecutiveDashboard | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setIsLoading(true);
      setError(null);
      try {
        const data = await getExecutiveDashboard();
        if (!cancelled) {
          setDashboard(data);
        }
      } catch (loadError) {
        if (!cancelled) {
          setError(loadError instanceof Error ? loadError.message : "No fue posible cargar el System Status.");
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, []);

  const serviceItems = useMemo(() => {
    if (!dashboard) return [];
    const ordered = ["backend", "frontend", "database", "auth"];
    return ordered
      .map((key) => dashboard.system_status.find((item) => item.key === key))
      .filter((item): item is DashboardSystemStatusItem => Boolean(item));
  }, [dashboard]);

  const globalTone = useMemo<ServiceTone>(() => {
    if (!dashboard) return "degraded";
    const tones = serviceItems.map((item) => normalizeServiceStatus(item.status));
    if (tones.includes("offline")) return "offline";
    if (tones.includes("warning")) return "warning";
    if (tones.includes("degraded")) return "degraded";
    return "online";
  }, [dashboard, serviceItems]);

  const globalStatusText = useMemo(() => {
    if (globalTone === "online") return "Sistema estable";
    if (globalTone === "warning") return "Sistema con advertencias";
    if (globalTone === "offline") return "Sistema con fallas críticas";
    return "Sistema degradado";
  }, [globalTone]);

  const alertCount = dashboard?.critical_alerts.length ?? 0;
  const leadingAlert = dashboard?.critical_alerts[0];

  if (isLoading && !dashboard) {
    return <div className="ep-card rounded-[2rem] p-6 text-secondary">Cargando estado del sistema...</div>;
  }

  if (error && !dashboard) {
    return <div className="ep-kpi-critical rounded-[2rem] px-6 py-5 text-sm">{error}</div>;
  }

  if (!dashboard) {
    return <div className="ep-card rounded-[2rem] p-6 text-secondary">No hay información disponible.</div>;
  }

  return (
    <div className="space-y-6">
      <section className="ep-card rounded-[2rem] p-6 sm:p-7">
        <div className="grid gap-5 xl:grid-cols-[minmax(0,1.2fr)_minmax(320px,0.8fr)]">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-primary/10 bg-primary/5 px-3 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-primary">
              <ShieldAlert className="h-3.5 w-3.5" />
              System Status
            </div>
            <div className="mt-5 flex flex-wrap items-center gap-3">
              <span className={`rounded-full px-3 py-1.5 text-[11px] font-semibold uppercase tracking-[0.16em] ${serviceBadgeClasses(globalTone)}`}>
                {globalStatusText}
              </span>
              <span className="text-sm text-secondary">{formatDateTime(dashboard.generated_at)}</span>
            </div>
            <h1 className="mt-4 text-3xl font-semibold tracking-[-0.05em] text-primary sm:text-[2.2rem]">Estado general del entorno y servicios clave.</h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-secondary">
              Lectura rápida para backend, frontend, base de datos y autenticación.
            </p>
          </div>

          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
            <SummaryMetric label="Entorno" value={globalStatusText} tone={globalTone} />
            <SummaryMetric label="Hora actual" value={<LiveClock />} />
            <SummaryMetric label="Último corte" value={formatDateTime(dashboard.generated_at)} />
            <SummaryMetric label="Alertas críticas" value={String(alertCount)} tone={alertCount > 0 ? "warning" : "online"} />
            <SummaryMetric label="Severidad principal" value={leadingAlert?.title ?? "Sin alertas activas"} tone={leadingAlert ? normalizeServiceStatus(leadingAlert.level === "critical" ? "offline" : "warning") : "online"} />
          </div>
        </div>

        <div className="mt-5 rounded-[1.4rem] border border-line bg-[color:rgb(var(--panel-strong))] px-4 py-4">
          <div className="flex items-start gap-3">
            <div className="rounded-2xl bg-primary/10 p-2.5">
              <Zap className="h-4 w-4 text-primary" />
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.18em] text-secondary">Resumen crítico</p>
              <p className="mt-1 text-sm font-semibold text-primary">{leadingAlert?.title ?? "Sin hallazgos críticos en este corte."}</p>
              <p className="mt-2 text-sm leading-6 text-secondary">{leadingAlert?.detail ?? "Todos los servicios monitoreados responden dentro del estado esperado para esta vista."}</p>
            </div>
          </div>
        </div>
      </section>

      <section className="space-y-4">
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-secondary">Servicios</p>
            <h2 className="mt-1 text-2xl font-semibold text-primary">Estado operativo por componente</h2>
          </div>
          <div className="ep-pill rounded-full px-4 py-2 text-sm text-secondary">Backend · Frontend · Base de datos · Auth</div>
        </div>
        <div className="grid gap-4 xl:grid-cols-2">
          {serviceItems.map((item) => (
            <ServiceCard key={item.key} item={item} />
          ))}
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[minmax(0,0.95fr)_minmax(0,1.05fr)]">
        <article className="ep-card rounded-[1.8rem] p-5 sm:p-6">
          <div className="flex items-center gap-3">
            <div className="rounded-2xl bg-primary/10 p-3">
              <RefreshCw className="h-5 w-5 text-primary" />
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.18em] text-secondary">Sincronización</p>
              <h3 className="mt-1 text-xl font-semibold text-primary">Importación y referencias</h3>
            </div>
          </div>

          <div className="mt-5 grid gap-3">
            <div className="ep-card-muted rounded-[1.35rem] px-4 py-4">
              <p className="text-[11px] uppercase tracking-[0.16em] text-secondary">Última importación relevante</p>
              <p className="mt-2 text-sm font-semibold text-primary">{dashboard.latest_import_reference ?? "Sin referencia disponible"}</p>
            </div>
            <div className="ep-card-muted rounded-[1.35rem] px-4 py-4">
              <p className="text-[11px] uppercase tracking-[0.16em] text-secondary">Piloto visible</p>
              <p className="mt-2 text-sm font-semibold text-primary">{dashboard.pilot_reference ? `${dashboard.pilot_reference.municipality}, ${dashboard.pilot_reference.department}` : "Sin piloto definido"}</p>
            </div>
            <div className="ep-card-muted rounded-[1.35rem] px-4 py-4">
              <p className="text-[11px] uppercase tracking-[0.16em] text-secondary">Observación</p>
              <p className="mt-2 text-sm text-secondary">Esta sección concentra referencias operativas sin competir con el bloque principal de estado.</p>
            </div>
          </div>
        </article>

        <article className="ep-card rounded-[1.8rem] p-5 sm:p-6">
          <div className="flex items-center gap-3">
            <div className="rounded-2xl bg-amber-500/14 p-3">
              <AlertTriangle className="h-5 w-5 text-amber-600 dark:text-amber-300" />
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.18em] text-secondary">Alertas</p>
              <h3 className="mt-1 text-xl font-semibold text-primary">Detalle priorizado</h3>
            </div>
          </div>

          <div className="mt-5 space-y-3">
            {dashboard.critical_alerts.length === 0 ? (
              <div className="ep-card-muted rounded-[1.35rem] px-4 py-4 text-sm text-secondary">Sin alertas activas para el corte actual.</div>
            ) : null}
            {dashboard.critical_alerts.map((alert: DashboardAlert) => (
              <div key={`${alert.level}-${alert.title}`} className={`${alertClasses(alert.level)} rounded-[1.35rem] px-4 py-4`}>
                <div className="flex items-center gap-2">
                  <span className={`h-2.5 w-2.5 rounded-full ${serviceDotClasses(alert.level === "critical" ? "offline" : alert.level === "warning" ? "warning" : "online")}`} />
                  <p className="text-sm font-semibold text-primary">{alert.title}</p>
                </div>
                <p className="mt-2 text-sm leading-6 text-secondary">{alert.detail}</p>
              </div>
            ))}
          </div>
        </article>
      </section>
    </div>
  );
}
