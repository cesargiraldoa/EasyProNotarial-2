"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { ArrowRight, Filter, RefreshCw } from "lucide-react";
import { getCaseFilters, getCases, getCurrentUser, getNotaries, type CaseFilterOptions, type CaseFilters, type CaseRecord, type CurrentUser, type NotaryRecord } from "@/lib/api";
import { formatDateTime } from "@/lib/datetime";
import { formatNotaryOptionLabel } from "@/lib/notaries";

const emptyFilters: CaseFilters = {
  current_state: "",
  case_type: "",
  act_type: "",
  date_from: "",
  date_to: "",
  notary_id: "",
  current_owner_user_id: "",
  q: ""
};

function collectRoleCodes(user: CurrentUser | null) {
  return Array.from(new Set([...(user?.role_codes ?? []), ...(user?.roles ?? [])].map((role) => role.toLowerCase())));
}

function classifyCaseState(state: string): "elaboracion" | "revision" | "aprobados" | "rechazados" | "otro" {
  if (["borrador", "en_diligenciamiento", "generado"].includes(state)) {
    return "elaboracion";
  }
  if (["revision_cliente", "ajustes_solicitados", "revision_aprobador", "devuelto_aprobador", "revision_notario"].includes(state)) {
    return "revision";
  }
  if (["aprobado_notario", "firmado_cargado", "cerrado"].includes(state)) {
    return "aprobados";
  }
  if (state === "rechazado_notario") {
    return "rechazados";
  }
  return "otro";
}

function normalizeActTypeLabel(value: string): string {
  if (value === "Cancelaci³n de hipoteca") {
    return "Cancelación de hipoteca";
  }
  return value;
}

function suggestedAction(item: CaseRecord, roleCodes: string[]) {
  const roles = new Set(roleCodes);
  if (roles.has("super_admin")) {
    return "Ver detalle / auditar";
  }
  if (roles.has("protocolist")) {
    if (item.final_signed_uploaded) {
      return "Descargar Word";
    }
    if (item.current_state === "borrador" || item.current_state === "en_diligenciamiento") {
      return "Continuar diligenciamiento";
    }
    if (item.current_state === "revision_cliente" || item.current_state === "ajustes_solicitados" || item.current_state === "revision_aprobador" || item.current_state === "revision_notario" || item.current_state === "devuelto_aprobador" || item.current_state === "rechazado_notario") {
      return "Corregir según observaciones";
    }
    return "Generar Word";
  }
  if (roles.has("approver") || roles.has("notary") || roles.has("titular_notary") || roles.has("substitute_notary") || roles.has("admin_notary")) {
    if (item.current_state === "revision_aprobador" || item.current_state === "revision_notario") {
      return "Revisar minuta";
    }
    return "Aprobar / observar";
  }
  return "Ver detalle";
}

export function CasesWorkspace() {
  const [cases, setCases] = useState<CaseRecord[]>([]);
  const [filters, setFilters] = useState<CaseFilters>(emptyFilters);
  const [filterOptions, setFilterOptions] = useState<CaseFilterOptions>({ case_types: [], act_types: [], states: [], owners: [], notaries: [] });
  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null);
  const [notaries, setNotaries] = useState<NotaryRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void Promise.all([loadCases(emptyFilters), loadFilters(), loadCurrentUser(), loadNotaries()]);
  }, []);

  async function loadNotaries() {
    try {
      setNotaries(await getNotaries());
    } catch {
      setNotaries([]);
    }
  }

  async function loadCases(nextFilters: CaseFilters) {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getCases(nextFilters);
      setCases(data);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "No fue posible cargar las minutas.");
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

  async function loadCurrentUser() {
    try {
      const user = await getCurrentUser();
      setCurrentUser(user);
    } catch {
      setCurrentUser(null);
    }
  }

  function updateFilter<K extends keyof CaseFilters>(field: K, value: string) {
    const nextFilters = { ...filters, [field]: value };
    setFilters(nextFilters);
    void loadCases(nextFilters);
  }

  function clearFilters() {
    setFilters(emptyFilters);
    void loadCases(emptyFilters);
  }

  const caseMetrics = useMemo(() => {
    return cases.reduce(
      (accumulator, item) => {
        accumulator.total += 1;
        accumulator[classifyCaseState(item.current_state)] += 1;
        return accumulator;
      },
      { total: 0, elaboracion: 0, revision: 0, aprobados: 0, rechazados: 0, otro: 0 }
    );
  }, [cases]);
  const normalizedRoleCodes = useMemo(() => collectRoleCodes(currentUser), [currentUser]);

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
    return notaries.map((notary) => [String(notary.id), formatNotaryOptionLabel(notary)]);
  }, [notaries]);

  return (
    <div className="space-y-6">
      <section className="ep-card rounded-[2rem] p-6">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.22em] text-accent">Bandeja de minutas</p>
            <h1 className="mt-2 text-3xl font-semibold text-primary">Minutas</h1>
            <p className="mt-3 max-w-3xl text-base leading-7 text-secondary">
              Aquí se ve la bandeja operativa: crear minuta, revisar avance, abrir detalle y continuar según el estado.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Link href="/dashboard/casos/crear" className="inline-flex items-center gap-2 rounded-2xl border border-[var(--line)] px-5 py-3 text-sm font-semibold text-primary">
              Crear minuta
            </Link>
            <button onClick={() => void loadCases(filters)} className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white shadow-panel">
              <RefreshCw className="h-4 w-4" />
              Actualizar bandeja
            </button>
          </div>
        </div>

        <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
          <div className="ep-card-muted rounded-[1.5rem] p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-secondary">Total documentos</p>
            <p className="mt-3 text-3xl font-semibold text-primary">{caseMetrics.total}</p>
          </div>
          <div className="ep-card-muted rounded-[1.5rem] p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-secondary">En elaboración</p>
            <p className="mt-3 text-3xl font-semibold text-primary">{caseMetrics.elaboracion}</p>
          </div>
          <div className="ep-card-muted rounded-[1.5rem] p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-secondary">En revisión</p>
            <p className="mt-3 text-3xl font-semibold text-primary">{caseMetrics.revision}</p>
          </div>
          <div className="ep-card-muted rounded-[1.5rem] p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-secondary">Aprobados</p>
            <p className="mt-3 text-3xl font-semibold text-primary">{caseMetrics.aprobados}</p>
          </div>
          <div className="rounded-[1.5rem] bg-primary p-4 text-white shadow-panel">
            <p className="text-xs uppercase tracking-[0.2em] text-white/72">Rechazados</p>
            <p className="mt-3 text-3xl font-semibold">{caseMetrics.rechazados}</p>
          </div>
        </div>
      </section>

      <section className="ep-card rounded-[2rem] p-6">
        <div className="flex flex-col gap-5 xl:flex-row xl:items-end xl:justify-between">
          <div />
        </div>

        <div className="ep-filter-panel mt-6 grid grid-cols-2 gap-3 rounded-[1.75rem] p-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-secondary">Fecha desde</label>
            <input
              type="date"
              value={filters.date_from ?? ""}
              onChange={(event) => updateFilter("date_from", event.target.value)}
              className="ep-input h-10 rounded-2xl px-3 text-sm"
            />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-secondary">Fecha hasta</label>
            <input
              type="date"
              value={filters.date_to ?? ""}
              onChange={(event) => updateFilter("date_to", event.target.value)}
              className="ep-input h-10 rounded-2xl px-3 text-sm"
            />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-secondary">Estado</label>
            <select value={filters.current_state ?? ""} onChange={(event) => updateFilter("current_state", event.target.value)} className="ep-select h-10 rounded-2xl px-3 text-sm"><option value="">Todos</option>{filterOptions.states.map((item) => <option key={item} value={item}>{item}</option>)}</select>
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-secondary">Tipo de minuta</label>
            <select value={filters.case_type ?? ""} onChange={(event) => updateFilter("case_type", event.target.value)} className="ep-select h-10 rounded-2xl px-3 text-sm"><option value="">Todos</option>{filterOptions.case_types.map((item) => <option key={item} value={item}>{item}</option>)}</select>
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-secondary">Tipo de acto</label>
            <select value={filters.act_type ?? ""} onChange={(event) => updateFilter("act_type", event.target.value)} className="ep-select h-10 rounded-2xl px-3 text-sm"><option value="">Todos</option>{filterOptions.act_types.map((item) => <option key={item} value={item}>{normalizeActTypeLabel(item)}</option>)}</select>
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-secondary">Responsable</label>
            <select value={filters.current_owner_user_id ?? ""} onChange={(event) => updateFilter("current_owner_user_id", event.target.value)} className="ep-select h-10 rounded-2xl px-3 text-sm"><option value="">Todos</option>{ownerOptions.map(([id, name]) => <option key={id} value={id}>{name}</option>)}</select>
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-secondary">Notaría</label>
            <select value={filters.notary_id ?? ""} onChange={(event) => updateFilter("notary_id", event.target.value)} className="ep-select h-10 rounded-2xl px-3 text-sm"><option value="">Todas</option>{notaryOptions.map(([id, label]) => <option key={id} value={id}>{label}</option>)}</select>
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-secondary">Buscar</label>
            <input value={filters.q ?? ""} onChange={(event) => updateFilter("q", event.target.value)} placeholder="Acto, minuta, notaría..." className="ep-input h-10 rounded-2xl px-3 text-sm" />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-secondary opacity-0">Acciones</label>
            <button
              type="button"
              onClick={clearFilters}
              className="inline-flex h-10 items-center justify-center gap-2 rounded-2xl border border-[var(--line)] px-4 text-sm font-semibold text-primary"
            >
              Limpiar filtros
            </button>
          </div>
        </div>

        {error ? <div className="ep-kpi-critical mt-5 rounded-2xl px-4 py-3 text-sm">{error}</div> : null}

        <div className="mt-6 grid gap-4">
          <div className="space-y-3">
            {isLoading ? <div className="ep-card-muted rounded-[1.5rem] px-4 py-6 text-sm text-secondary">Cargando minutas...</div> : null}
            {!isLoading && cases.length === 0 ? <div className="ep-card-muted rounded-[1.5rem] px-4 py-6 text-sm text-secondary">No hay minutas para los filtros seleccionados.</div> : null}
            {cases.map((item) => (
              <Link key={item.id} href={`/dashboard/casos/${item.id}`} className="block ep-card-soft rounded-[1.6rem] p-5 transition hover:-translate-y-0.5 hover:border-primary/25 hover:shadow-soft">
                <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                  <div className="min-w-0">
                    <div className="flex items-center gap-3">
                      <span className="rounded-full bg-primary/10 px-3 py-1 text-xs font-semibold text-primary">Minuta</span>
                      <h3 className="truncate text-lg font-semibold text-primary">{item.act_type}</h3>
                    </div>
                    <p className="mt-2 text-sm text-secondary">Plantilla dinámica · Minuta {item.year}-{String(item.consecutive).padStart(4, "0")} · {formatNotaryOptionLabel(notaries.find((notary) => notary.id === item.notary_id) ?? { notary_label: item.notary_label, municipality: "", commercial_name: "" })}</p>
                    <p className="mt-2 text-sm leading-6 text-secondary">Responsable: {item.current_owner_user_name || "Sin asignar"}</p>
                  </div>
                  <div className="grid gap-2 text-sm text-secondary lg:min-w-[230px]">
                    <span className="ep-badge rounded-full px-3 py-1 font-semibold text-primary">{item.current_state}</span>
                    <span>Última actualización: {formatDateTime(item.updated_at)}</span>
                    <span>Acción sugerida: {suggestedAction(item, normalizedRoleCodes)}</span>
                    <span>Firmado final: {item.final_signed_uploaded ? "Cargado" : "Pendiente"}</span>
                  </div>
                </div>
                <div className="mt-4 flex items-center justify-between text-sm text-primary">
                  <span>{item.protocolist_user_name || "Protocolista: sin asignar"}</span>
                  <span className="inline-flex items-center gap-2 font-semibold">Ver detalle <ArrowRight className="h-4 w-4" /></span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
