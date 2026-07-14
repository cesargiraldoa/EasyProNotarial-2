"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { ArrowRight, BookOpen, Upload } from "lucide-react";
import {
  getBibliotecaTemplates,
  getCamposCatalogo,
  type BibliotecaTemplate,
  type FieldCatalogItem,
} from "@/lib/api-biblioteca";
import { formatDateTime } from "@/lib/datetime";

const fieldCategories = ["persona", "valor", "inmueble", "fecha", "notaria", "otro"];

function uniqueOptions(values: Array<string | null>) {
  return Array.from(new Set(values.filter((value): value is string => Boolean(value?.trim())))).sort((a, b) => a.localeCompare(b));
}

function statusBadgeClass(status: string) {
  if (status === "active") return "bg-emerald-50 text-emerald-700 border border-emerald-100";
  if (status === "draft") return "bg-slate-100 text-secondary border border-slate-200";
  return "bg-primary/10 text-primary border border-primary/10";
}

function fieldTypeBadgeClass(fieldType: string) {
  if (fieldType === "monetary") return "bg-emerald-50 text-emerald-700 border border-emerald-100";
  if (fieldType === "date") return "bg-blue-50 text-blue-700 border border-blue-100";
  if (fieldType === "list") return "bg-purple-50 text-purple-700 border border-purple-100";
  if (fieldType === "number") return "bg-orange-50 text-orange-700 border border-orange-100";
  return "bg-slate-100 text-secondary border border-slate-200";
}

export function BibliotecaWorkspace() {
  const [templates, setTemplates] = useState<BibliotecaTemplate[]>([]);
  const [campos, setCampos] = useState<FieldCatalogItem[]>([]);
  const [actCode, setActCode] = useState("");
  const [documentType, setDocumentType] = useState("");
  const [bankName, setBankName] = useState("");
  const [templateStatus, setTemplateStatus] = useState("");
  const [templateSearch, setTemplateSearch] = useState("");
  const [fieldCategory, setFieldCategory] = useState("");
  const [fieldSearch, setFieldSearch] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [fieldsLoading, setFieldsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const hasLoadedInitialDataRef = useRef(false);

  useEffect(() => {
    if (hasLoadedInitialDataRef.current) {
      return;
    }

    hasLoadedInitialDataRef.current = true;
    let isMounted = true;

    async function loadInitialData() {
      setIsLoading(true);
      setFieldsLoading(true);
      setError(null);

      const [templatesResult, camposResult] = await Promise.allSettled([
        getBibliotecaTemplates(),
        getCamposCatalogo(),
      ]);

      if (!isMounted) {
        return;
      }

      setTemplates(templatesResult.status === "fulfilled" ? templatesResult.value : []);

      if (camposResult.status === "fulfilled") {
        setCampos(camposResult.value);
      } else {
        setCampos([]);
        setError(camposResult.reason instanceof Error ? camposResult.reason.message : "No fue posible cargar el catalogo de campos.");
      }

      setIsLoading(false);
      setFieldsLoading(false);
    }

    void loadInitialData();

    return () => {
      isMounted = false;
    };
  }, []);

  function clearFilters() {
    setActCode("");
    setDocumentType("");
    setBankName("");
    setTemplateStatus("");
    setTemplateSearch("");
  }

  const templateMetrics = useMemo(() => {
    return templates.reduce(
      (accumulator, template) => {
        accumulator.total += 1;
        if (template.status === "active") accumulator.active += 1;
        if (template.status === "draft") accumulator.draft += 1;
        return accumulator;
      },
      { total: 0, active: 0, draft: 0 }
    );
  }, [templates]);

  const globalFieldsCount = useMemo(() => campos.filter((campo) => campo.scope === "global").length, [campos]);
  const actOptions = useMemo(() => uniqueOptions(templates.map((template) => template.act_code)), [templates]);
  const documentTypeOptions = useMemo(() => uniqueOptions(templates.map((template) => template.document_type)), [templates]);
  const bankOptions = useMemo(() => uniqueOptions(templates.map((template) => template.bank_name)), [templates]);

  const filteredTemplates = useMemo(() => {
    const search = templateSearch.trim().toLowerCase();
    return templates.filter((template) => {
      if (actCode && template.act_code !== actCode) return false;
      if (documentType && template.document_type !== documentType) return false;
      if (bankName && template.bank_name !== bankName) return false;
      if (templateStatus && template.status !== templateStatus) return false;
      if (!search) return true;
      return [template.name, template.act_code, template.document_type, template.bank_name]
        .filter(Boolean)
        .some((value) => String(value).toLowerCase().includes(search));
    });
  }, [templates, actCode, documentType, bankName, templateStatus, templateSearch]);

  const filteredCampos = useMemo(() => {
    const search = fieldSearch.trim().toLowerCase();
    return campos.filter((campo) => {
      if (fieldCategory && campo.category !== fieldCategory) return false;
      if (!search) return true;
      return campo.code.toLowerCase().includes(search) || campo.label.toLowerCase().includes(search);
    });
  }, [campos, fieldCategory, fieldSearch]);

  return (
    <div className="space-y-6">
      <section className="ep-card rounded-[2rem] p-6">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.22em] text-accent">Motor de Biblioteca</p>
            <h1 className="mt-2 text-3xl font-semibold text-primary">Biblioteca de Plantillas</h1>
            <p className="mt-3 max-w-3xl text-base leading-7 text-secondary">
              Selecciona una plantilla existente o sube un documento para crear una nueva.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <button onClick={() => alert("Proximamente")} className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white shadow-panel">
              <Upload className="h-4 w-4" />
              Subir documento
            </button>
          </div>
        </div>

        <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <div className="ep-card-muted rounded-[1.5rem] p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-secondary">Total plantillas</p>
            <p className="mt-3 text-3xl font-semibold text-primary">{templateMetrics.total}</p>
          </div>
          <div className="ep-card-muted rounded-[1.5rem] p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-secondary">Activas</p>
            <p className="mt-3 text-3xl font-semibold text-primary">{templateMetrics.active}</p>
          </div>
          <div className="ep-card-muted rounded-[1.5rem] p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-secondary">En borrador</p>
            <p className="mt-3 text-3xl font-semibold text-primary">{templateMetrics.draft}</p>
          </div>
          <div className="ep-card-muted rounded-[1.5rem] p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-secondary">Campos globales</p>
            <p className="mt-3 text-3xl font-semibold text-primary">{globalFieldsCount}</p>
          </div>
        </div>
      </section>

      <section className="ep-card rounded-[2rem] p-6">
        <div className="ep-filter-panel grid grid-cols-2 gap-3 rounded-[1.75rem] p-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-secondary">Tipo de acto</label>
            <select value={actCode} onChange={(event) => setActCode(event.target.value)} className="ep-select h-10 rounded-2xl px-3 text-sm">
              <option value="">Todos</option>
              {actOptions.map((item) => <option key={item} value={item}>{item}</option>)}
            </select>
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-secondary">Tipo de documento</label>
            <select value={documentType} onChange={(event) => setDocumentType(event.target.value)} className="ep-select h-10 rounded-2xl px-3 text-sm">
              <option value="">Todos</option>
              {documentTypeOptions.map((item) => <option key={item} value={item}>{item}</option>)}
            </select>
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-secondary">Banco</label>
            <select value={bankName} onChange={(event) => setBankName(event.target.value)} className="ep-select h-10 rounded-2xl px-3 text-sm">
              <option value="">Todos</option>
              {bankOptions.map((item) => <option key={item} value={item}>{item}</option>)}
            </select>
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-secondary">Estado</label>
            <select value={templateStatus} onChange={(event) => setTemplateStatus(event.target.value)} className="ep-select h-10 rounded-2xl px-3 text-sm">
              <option value="">Todos</option>
              <option value="active">active</option>
              <option value="draft">draft</option>
            </select>
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-secondary">Buscar</label>
            <input value={templateSearch} onChange={(event) => setTemplateSearch(event.target.value)} placeholder="Nombre, acto, banco..." className="ep-input h-10 rounded-2xl px-3 text-sm" />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-secondary opacity-0">Acciones</label>
            <button type="button" onClick={clearFilters} className="inline-flex h-10 items-center justify-center rounded-2xl border border-[var(--line)] px-4 text-sm font-semibold text-primary">
              Limpiar filtros
            </button>
          </div>
        </div>

        {error ? <div className="ep-kpi-critical mt-5 rounded-2xl px-4 py-3 text-sm">{error}</div> : null}

        <div className="mt-6">
          {isLoading ? <div className="ep-card-muted rounded-[1.5rem] px-4 py-6 text-sm text-secondary">Cargando biblioteca...</div> : null}
          {!isLoading && filteredTemplates.length === 0 ? (
            <div className="ep-card-muted rounded-[1.5rem] px-6 py-12 text-center">
              <BookOpen className="mx-auto h-10 w-10 text-secondary mb-4" />
              <p className="text-sm font-semibold text-primary">La biblioteca esta vacia</p>
              <p className="text-sm text-secondary mt-2">Sube un documento para crear la primera plantilla.</p>
            </div>
          ) : null}
          {!isLoading && filteredTemplates.length > 0 ? (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
              {filteredTemplates.map((template) => (
                <article key={template.id} className="ep-card-soft rounded-[1.6rem] p-5 transition hover:-translate-y-0.5 hover:border-primary/25 hover:shadow-soft">
                  <div className="flex items-start justify-between gap-3">
                    <span className="ep-badge rounded-full px-3 py-1 text-xs font-semibold text-primary">{template.act_code || "Sin tipo"}</span>
                    <span className={`rounded-full px-3 py-1 text-xs font-semibold ${statusBadgeClass(template.status)}`}>{template.status}</span>
                  </div>
                  <h3 className="mt-4 text-lg font-semibold text-primary">{template.name}</h3>
                  <div className="mt-3 space-y-1 text-sm text-secondary">
                    {template.document_type ? <p>{template.document_type}</p> : null}
                    {template.bank_name ? <p>{template.bank_name}</p> : null}
                    <p>Actualizada: {formatDateTime(template.updated_at)}</p>
                  </div>
                  <button type="button" onClick={() => alert("Proximamente")} className="mt-5 inline-flex items-center gap-2 text-sm font-semibold text-primary">
                    Usar plantilla <ArrowRight className="h-4 w-4" />
                  </button>
                </article>
              ))}
            </div>
          ) : null}
        </div>
      </section>

      <section className="ep-card rounded-[2rem] p-6">
        <div>
          <h2 className="text-2xl font-semibold text-primary">Catalogo de campos</h2>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-secondary">
            Campos disponibles para insertar en documentos desde el plugin de OnlyOffice.
          </p>
        </div>

        <div className="ep-filter-panel mt-6 grid gap-3 rounded-[1.75rem] p-4 sm:grid-cols-2 lg:grid-cols-3">
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-secondary">Categoria</label>
            <select value={fieldCategory} onChange={(event) => setFieldCategory(event.target.value)} className="ep-select h-10 rounded-2xl px-3 text-sm">
              <option value="">Todas</option>
              {fieldCategories.map((category) => <option key={category} value={category}>{category}</option>)}
            </select>
          </div>
          <div className="flex flex-col gap-1 lg:col-span-2">
            <label className="text-xs font-medium text-secondary">Buscar campo</label>
            <input value={fieldSearch} onChange={(event) => setFieldSearch(event.target.value)} placeholder="Codigo o nombre..." className="ep-input h-10 rounded-2xl px-3 text-sm" />
          </div>
        </div>

        <div className="mt-6 overflow-hidden rounded-[1.5rem] border border-[var(--line)]">
          {fieldsLoading ? <div className="ep-card-muted px-4 py-6 text-sm text-secondary">Cargando catalogo de campos...</div> : null}
          {!fieldsLoading ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-[var(--line)] text-left text-sm">
                <thead className="bg-[var(--surface-muted)] text-xs uppercase tracking-[0.16em] text-secondary">
                  <tr>
                    <th className="px-4 py-3 font-semibold">Codigo</th>
                    <th className="px-4 py-3 font-semibold">Nombre</th>
                    <th className="px-4 py-3 font-semibold">Tipo</th>
                    <th className="px-4 py-3 font-semibold">Categoria</th>
                    <th className="px-4 py-3 font-semibold">Alcance</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[var(--line)] bg-white">
                  {filteredCampos.map((campo) => (
                    <tr key={campo.id}>
                      <td className="px-4 py-3 font-semibold text-primary">{campo.code}</td>
                      <td className="px-4 py-3 text-secondary">{campo.label}</td>
                      <td className="px-4 py-3">
                        <span className={`rounded-full px-3 py-1 text-xs font-semibold ${fieldTypeBadgeClass(campo.field_type)}`}>{campo.field_type}</span>
                      </td>
                      <td className="px-4 py-3 text-secondary">{campo.category}</td>
                      <td className="px-4 py-3">
                        <span className={`rounded-full px-3 py-1 text-xs font-semibold ${campo.scope === "global" ? "bg-blue-50 text-blue-700 border border-blue-100" : "bg-slate-100 text-secondary border border-slate-200"}`}>
                          {campo.scope === "global" ? "Global" : "Notaria"}
                        </span>
                      </td>
                    </tr>
                  ))}
                  {filteredCampos.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="px-4 py-8 text-center text-sm text-secondary">No hay campos para los filtros seleccionados.</td>
                    </tr>
                  ) : null}
                </tbody>
              </table>
            </div>
          ) : null}
        </div>
      </section>
    </div>
  );
}
