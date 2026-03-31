"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { ArrowRight, Filter, MapPinned, RefreshCw, ShieldCheck, Sparkles, Target } from "lucide-react";
import {
  getNotaries,
  getNotaryFilterOptions,
  importAntioquiaSource,
  type NotaryFilterOptions,
  type NotaryFilters,
  type NotaryImportSummary,
  type NotaryRecord
} from "@/lib/api";

const emptyFilters: NotaryFilters = {
  commercial_status: "",
  municipality: "",
  commercial_owner: "",
  priority: "",
  q: ""
};

function summarizeStatus(notaries: NotaryRecord[]) {
  const summary = new Map<string, number>();
  for (const notary of notaries) {
    summary.set(notary.commercial_status, (summary.get(notary.commercial_status) ?? 0) + 1);
  }
  return Array.from(summary.entries()).sort((a, b) => b[1] - a[1]);
}

export function NotariesCatalog() {
  const [notaries, setNotaries] = useState<NotaryRecord[]>([]);
  const [filters, setFilters] = useState<NotaryFilters>(emptyFilters);
  const [filterOptions, setFilterOptions] = useState<NotaryFilterOptions>({
    municipalities: [],
    commercial_owners: [],
    priorities: [],
    commercial_statuses: []
  });
  const [importResult, setImportResult] = useState<NotaryImportSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isImporting, setIsImporting] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
      setError(loadError instanceof Error ? loadError.message : "No fue posible cargar el catálogo de notarías.");
    } finally {
      setIsLoading(false);
    }
  }

  async function loadFilterOptions() {
    try {
      const data = await getNotaryFilterOptions();
      setFilterOptions(data);
    } catch {
      // Mantener la vista operativa si falla el endpoint de filtros.
    }
  }

  async function handleImport() {
    setIsImporting(true);
    setError(null);
    try {
      const result = await importAntioquiaSource(true);
      setImportResult(result);
      await Promise.all([loadNotaries(filters), loadFilterOptions()]);
    } catch (importError) {
      setError(importError instanceof Error ? importError.message : "No fue posible importar el archivo real de Antioquia.");
    } finally {
      setIsImporting(false);
    }
  }

  function updateFilter<K extends keyof NotaryFilters>(field: K, value: string) {
    const nextFilters = { ...filters, [field]: value };
    setFilters(nextFilters);
    void loadNotaries(nextFilters);
  }

  const statusSummary = useMemo(() => summarizeStatus(notaries), [notaries]);
  const highPriorityCount = useMemo(
    () => notaries.filter((notary) => ["alta", "crítica"].includes(notary.priority)).length,
    [notaries]
  );

  return (
    <div className="space-y-6">
      <section className="grid gap-6 xl:grid-cols-[minmax(0,1.1fr)_360px]">
        <article className="ep-card rounded-[2rem] p-6">
          <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
            <div className="max-w-3xl">
              <p className="text-sm font-semibold uppercase tracking-[0.24em] text-accent">Catálogo maestro de notarías</p>
              <h1 className="mt-3 text-3xl font-semibold tracking-[-0.05em] text-primary sm:text-4xl">Antioquia cargada sobre la entidad base Notary con CRM y responsables reales</h1>
              <p className="mt-3 text-base leading-7 text-secondary">La notaría sigue siendo la unidad central del sistema. El catálogo maestro, el branding, el CRM y la auditoría viven sobre la misma entidad.</p>
            </div>
            <div className="flex flex-col gap-3 sm:flex-row lg:flex-col">
              <button onClick={handleImport} disabled={isImporting} className="inline-flex items-center justify-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white shadow-panel transition hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-70">
                <RefreshCw className={`h-4 w-4 ${isImporting ? "animate-spin" : ""}`} />
                {isImporting ? "Importando Antioquia..." : "Reimportar archivo real"}
              </button>
              <p className="max-w-xs text-xs leading-5 text-secondary">Fuente fija: Notarias_Antioquia_EasyProNotarial.xlsx. Se actualiza por duplicado municipality + notary_label + email.</p>
            </div>
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-4">
            <div className="ep-card-muted rounded-[1.5rem] p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-secondary">Notarías visibles</p>
              <p className="mt-3 text-3xl font-semibold text-primary">{notaries.length}</p>
              <p className="mt-2 text-sm text-secondary">Catálogo maestro activo para operación y prospección.</p>
            </div>
            <div className="ep-card-muted rounded-[1.5rem] p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-secondary">Alta prioridad</p>
              <p className="mt-3 text-3xl font-semibold text-primary">{highPriorityCount}</p>
              <p className="mt-2 text-sm text-secondary">Registros en foco comercial inmediato.</p>
            </div>
            <div className="ep-card-muted rounded-[1.5rem] p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-secondary">Responsables</p>
              <p className="mt-3 text-3xl font-semibold text-primary">{filterOptions.commercial_owners.length}</p>
              <p className="mt-2 text-sm text-secondary">Usuarios o responsables heredados disponibles para filtro.</p>
            </div>
            <div className="rounded-[1.5rem] bg-primary p-4 text-white shadow-panel">
              <p className="text-xs uppercase tracking-[0.2em] text-white/72">Estados CRM</p>
              <p className="mt-3 text-3xl font-semibold">{statusSummary.length}</p>
              <p className="mt-2 text-sm text-white/80">Seguimiento comercial visible y auditable.</p>
            </div>
          </div>
        </article>

        <aside className="space-y-4 ep-card rounded-[2rem] p-6">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-secondary">Resultado de importación</p>
            <h2 className="mt-2 text-2xl font-semibold text-primary">Carga real del maestro de Antioquia</h2>
          </div>

          {importResult ? (
            <div className="space-y-3">
              <div className="grid gap-3 sm:grid-cols-3">
                <div className="ep-card-muted rounded-2xl px-4 py-3"><p className="text-xs uppercase tracking-[0.18em] text-secondary">Creados</p><p className="mt-2 text-2xl font-semibold text-primary">{importResult.created}</p></div>
                <div className="ep-card-muted rounded-2xl px-4 py-3"><p className="text-xs uppercase tracking-[0.18em] text-secondary">Actualizados</p><p className="mt-2 text-2xl font-semibold text-primary">{importResult.updated}</p></div>
                <div className="ep-card-muted rounded-2xl px-4 py-3"><p className="text-xs uppercase tracking-[0.18em] text-secondary">Omitidos</p><p className="mt-2 text-2xl font-semibold text-primary">{importResult.omitted}</p></div>
              </div>
              <div className="ep-card-muted rounded-[1.5rem] p-4 text-sm text-secondary">
                <p><span className="font-semibold text-primary">Procesados:</span> {importResult.processed}</p>
                <p><span className="font-semibold text-primary">Errores por fila:</span> {importResult.errors.length}</p>
                <p className="mt-2 break-all"><span className="font-semibold text-primary">Fuente:</span> {importResult.source_path}</p>
              </div>
            </div>
          ) : (
            <div className="ep-card-muted rounded-[1.5rem] p-4 text-sm leading-6 text-secondary">
              Ejecuta la importación real para refrescar el catálogo maestro de Antioquia desde el archivo local obligatorio.
            </div>
          )}
        </aside>
      </section>

      <section className="ep-card rounded-[2rem] p-6">
        <div className="flex flex-col gap-5 xl:flex-row xl:items-end xl:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.22em] text-accent">Filtros comerciales</p>
            <h2 className="mt-2 text-2xl font-semibold text-primary">Catálogo visible con filtros operativos</h2>
          </div>
          <div className="ep-pill inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm text-secondary">
            <Filter className="h-4 w-4 text-primary" />
            Estado, municipio, responsable y prioridad activos
          </div>
        </div>

        <div className="ep-filter-panel mt-6 grid gap-4 rounded-[1.75rem] p-4 lg:grid-cols-5">
          <label className="grid gap-2 text-sm font-medium text-primary">
            Estado comercial
            <select value={filters.commercial_status ?? ""} onChange={(event) => updateFilter("commercial_status", event.target.value)} className="ep-select h-12 rounded-2xl px-4">
              <option value="">Todos</option>
              {filterOptions.commercial_statuses.map((item) => <option key={item} value={item}>{item}</option>)}
            </select>
          </label>
          <label className="grid gap-2 text-sm font-medium text-primary">
            Municipio
            <select value={filters.municipality ?? ""} onChange={(event) => updateFilter("municipality", event.target.value)} className="ep-select h-12 rounded-2xl px-4">
              <option value="">Todos</option>
              {filterOptions.municipalities.map((item) => <option key={item} value={item}>{item}</option>)}
            </select>
          </label>
          <label className="grid gap-2 text-sm font-medium text-primary">
            Responsable
            <select value={filters.commercial_owner ?? ""} onChange={(event) => updateFilter("commercial_owner", event.target.value)} className="ep-select h-12 rounded-2xl px-4">
              <option value="">Todos</option>
              {filterOptions.commercial_owners.map((item) => <option key={item} value={item}>{item}</option>)}
            </select>
          </label>
          <label className="grid gap-2 text-sm font-medium text-primary">
            Prioridad
            <select value={filters.priority ?? ""} onChange={(event) => updateFilter("priority", event.target.value)} className="ep-select h-12 rounded-2xl px-4">
              <option value="">Todas</option>
              {filterOptions.priorities.map((item) => <option key={item} value={item}>{item}</option>)}
            </select>
          </label>
          <label className="grid gap-2 text-sm font-medium text-primary">
            Buscar
            <input value={filters.q ?? ""} onChange={(event) => updateFilter("q", event.target.value)} placeholder="Municipio, notaría, correo..." className="ep-input h-12 rounded-2xl px-4" />
          </label>
        </div>

        {error ? <div className="ep-kpi-critical mt-5 rounded-2xl px-4 py-3 text-sm">{error}</div> : null}

        <div className="mt-6 grid gap-4 xl:grid-cols-[minmax(0,1.2fr)_340px]">
          <div className="space-y-3">
            {isLoading ? <div className="ep-card-muted rounded-[1.5rem] px-4 py-6 text-sm text-secondary">Cargando catálogo...</div> : null}
            {!isLoading && notaries.length === 0 ? <div className="ep-card-muted rounded-[1.5rem] px-4 py-6 text-sm text-secondary">No hay notarías para los filtros seleccionados.</div> : null}
            {notaries.map((notary) => (
              <Link key={notary.id} href={`/dashboard/notarias/${notary.id}`} className="block ep-card-soft rounded-[1.6rem] p-5 transition hover:-translate-y-0.5 hover:border-primary/25 hover:shadow-soft">
                <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                  <div className="min-w-0">
                    <div className="flex items-center gap-3">
                      <span className="h-4 w-4 rounded-full border border-white/40 shadow-sm" style={{ backgroundColor: notary.primary_color }} />
                      <h3 className="truncate text-lg font-semibold text-primary">{notary.notary_label}</h3>
                    </div>
                    <p className="mt-2 text-sm text-secondary">{notary.department} | {notary.municipality}</p>
                    <p className="mt-2 text-sm leading-6 text-secondary">{notary.address || "Sin dirección"}</p>
                    <p className="mt-1 text-sm leading-6 text-secondary">{notary.current_notary_name || "Sin notario asignado en catálogo"}</p>
                  </div>
                  <div className="grid gap-2 text-sm text-secondary lg:min-w-[240px]">
                    <span className="ep-badge rounded-full px-3 py-1 font-semibold text-primary">{notary.commercial_status}</span>
                    <span>Responsable: {notary.commercial_owner_display || "Sin asignar"}</span>
                    <span>Prioridad: {notary.priority}</span>
                    <span>Gestiones: {notary.activity_count}</span>
                  </div>
                </div>
                <div className="mt-4 flex items-center justify-between text-sm text-primary">
                  <span>{notary.email || notary.commercial_email || "Sin correo"}</span>
                  <span className="inline-flex items-center gap-2 font-semibold">Ver detalle CRM <ArrowRight className="h-4 w-4" /></span>
                </div>
              </Link>
            ))}
          </div>

          <aside className="space-y-4">
            <div className="rounded-[1.6rem] bg-primary p-5 text-white shadow-panel">
              <div className="flex items-center gap-3">
                <Sparkles className="h-5 w-5 text-accent" />
                <p className="text-lg font-semibold">Base para CRM comercial</p>
              </div>
              <p className="mt-3 text-sm leading-6 text-white/82">Cada notaría conserva branding editable y ahora suma estado comercial, responsable real, contactos, próximas gestiones y auditoría mínima.</p>
            </div>
            <div className="ep-card-soft rounded-[1.6rem] p-5">
              <div className="flex items-center gap-3">
                <Target className="h-5 w-5 text-primary" />
                <p className="text-lg font-semibold text-primary">Radar comercial</p>
              </div>
              <div className="mt-4 space-y-3 text-sm text-secondary">
                {statusSummary.slice(0, 5).map(([label, count]) => (
                  <div key={label} className="flex items-center justify-between ep-card-muted rounded-2xl px-4 py-3">
                    <span>{label}</span>
                    <span className="font-semibold text-primary">{count}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="ep-card-soft rounded-[1.6rem] p-5">
              <div className="flex items-center gap-3">
                <MapPinned className="h-5 w-5 text-primary" />
                <p className="text-lg font-semibold text-primary">Cobertura</p>
              </div>
              <p className="mt-3 text-sm leading-6 text-secondary">{filterOptions.municipalities.length} municipios disponibles para segmentación comercial y operativa.</p>
            </div>
            <div className="ep-card-soft rounded-[1.6rem] p-5">
              <div className="flex items-center gap-3">
                <ShieldCheck className="h-5 w-5 text-primary" />
                <p className="text-lg font-semibold text-primary">Auditoría base</p>
              </div>
              <p className="mt-3 text-sm leading-6 text-secondary">Los cambios de estado, responsable y nuevas gestiones quedan rastreados por usuario y fecha.</p>
            </div>
          </aside>
        </div>
      </section>
    </div>
  );
}
