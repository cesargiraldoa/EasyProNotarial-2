"use client";

import { useEffect, useState } from "react";
import { FileUp, Save } from "lucide-react";
import { createTemplate, getTemplates, updateTemplate, type TemplateRecord } from "@/lib/document-flow";
import { getNotaries } from "@/lib/api";

async function fileToBase64(file: File) {
  return new Promise<string>((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result).split(",")[1] ?? "");
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

const defaultVariableMap = JSON.stringify(
  {
    NOMBRE_PODERDANTE: "participants.poderdante.full_name",
    NOMBRE_APODERADO: "participants.apoderado.full_name",
    DIA_ELABORACION_ESCRITURA: "act.dia_elaboracion",
    NUMERO_ESCRITURA: "case.official_deed_number",
  },
  null,
  2,
);

const emptyForm = {
  name: "",
  case_type: "escritura",
  document_type: "",
  description: "",
  scope_type: "global",
  notary_id: "",
  is_active: true,
  internal_variable_map_json: defaultVariableMap,
};

export function TemplatesWorkspace() {
  const [templates, setTemplates] = useState<TemplateRecord[]>([]);
  const [notaries, setNotaries] = useState<Array<{ id: number; notary_label: string; municipality: string }>>([]);
  const [selected, setSelected] = useState<TemplateRecord | null>(null);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [form, setForm] = useState(emptyForm);

  useEffect(() => {
    void load();
  }, []);

  async function load() {
    setIsLoading(true);
    setError(null);
    try {
      const [templateData, notaryData] = await Promise.all([getTemplates(), getNotaries()]);
      const safeTemplates = Array.isArray(templateData) ? templateData : [];
      setTemplates(safeTemplates);
      setNotaries(Array.isArray(notaryData) ? notaryData.map((item) => ({ id: item.id, notary_label: item.notary_label || "Sin nombre", municipality: item.municipality || "Sin municipio" })) : []);
      if (safeTemplates.length > 0) {
        selectTemplate(safeTemplates[0]);
      } else {
        setSelected(null);
        setForm(emptyForm);
      }
    } catch (loadError) {
      setTemplates([]);
      setNotaries([]);
      setSelected(null);
      setError(loadError instanceof Error ? loadError.message : "No fue posible cargar las plantillas.");
    } finally {
      setIsLoading(false);
    }
  }

  function selectTemplate(item: TemplateRecord) {
    setSelected(item);
    setForm({
      name: item.name || emptyForm.name,
      case_type: item.case_type || emptyForm.case_type,
      document_type: item.document_type || emptyForm.document_type,
      description: item.description || "",
      scope_type: item.scope_type || emptyForm.scope_type,
      notary_id: item.notary_id ? String(item.notary_id) : "",
      is_active: item.is_active,
      internal_variable_map_json: item.internal_variable_map_json || defaultVariableMap,
    });
  }

  async function handleSubmit() {
    setFeedback(null);
    setError(null);
    setIsSaving(true);
    try {
      if (!form.name.trim() || form.name.trim().length < 3) {
        setError("El nombre de la plantilla es obligatorio (mínimo 3 caracteres).");
        setIsSaving(false);
        return;
      }
      if (!form.document_type.trim() || form.document_type.trim().length < 2) {
        setError("El tipo de documento es obligatorio.");
        setIsSaving(false);
        return;
      }
      const upload = uploadFile
        ? { filename: uploadFile.name, content_base64: await fileToBase64(uploadFile) }
        : null;
      const payload = {
        ...form,
        notary_id: form.notary_id ? Number(form.notary_id) : null,
        required_roles: [
          { role_code: "poderdante", label: "Poderdante", is_required: true, step_order: 1 },
          { role_code: "apoderado", label: "Apoderado(a)", is_required: true, step_order: 2 },
        ],
        fields: uploadFile ? [] : [
          { field_code: "dia_elaboracion", label: "Día elaboración", field_type: "number", section: "acto", is_required: true, options_json: null, placeholder_key: "DIA_ELABORACION_ESCRITURA", help_text: null, step_order: 1 },
          { field_code: "mes_elaboracion", label: "Mes elaboración", field_type: "text", section: "acto", is_required: true, options_json: null, placeholder_key: "MES_ELABORACION_ESCRITURA", help_text: null, step_order: 2 },
          { field_code: "ano_elaboracion", label: "Año elaboración", field_type: "number", section: "acto", is_required: true, options_json: null, placeholder_key: "ANO_ELABORACION_ESCRITURA", help_text: null, step_order: 3 },
          { field_code: "derechos_notariales", label: "Derechos notariales", field_type: "currency", section: "acto", is_required: true, options_json: null, placeholder_key: "DERECHOS_NOTARIALES", help_text: null, step_order: 4 },
          { field_code: "iva", label: "IVA", field_type: "currency", section: "acto", is_required: true, options_json: null, placeholder_key: "IVA", help_text: null, step_order: 5 },
          { field_code: "aporte_superintendencia", label: "Aporte superintendencia", field_type: "currency", section: "acto", is_required: true, options_json: null, placeholder_key: "APORTE_SUPERINTENDENCIA", help_text: null, step_order: 6 },
          { field_code: "fondo_notariado", label: "Fondo notariado", field_type: "currency", section: "acto", is_required: true, options_json: null, placeholder_key: "FONDO_NOTARIADO", help_text: null, step_order: 7 },
          { field_code: "consecutivos_hojas_papel_notarial", label: "Consecutivos hojas papel notarial", field_type: "text", section: "acto", is_required: true, options_json: null, placeholder_key: "CONSECUTIVOS_HOJAS_PAPEL_NOTARIAL", help_text: null, step_order: 8 },
          { field_code: "extension", label: "Extensión", field_type: "text", section: "acto", is_required: true, options_json: null, placeholder_key: "EXTENSION", help_text: null, step_order: 9 },
        ],
        upload,
      };
      const saved = selected ? await updateTemplate(selected.id, payload) : await createTemplate(payload);
      setSelected(saved);
      setUploadFile(null);
      await load();
      setFeedback("Plantilla guardada correctamente.");
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "No fue posible guardar la plantilla.");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <div className="space-y-6">
      <section className="ep-card rounded-[2rem] p-6">
        <p className="text-sm font-semibold uppercase tracking-[0.22em] text-accent">Plantillas</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-[-0.05em] text-primary">Subir plantilla Word y activar formulario dinamico</h1>
        <p className="mt-3 max-w-3xl text-base leading-7 text-secondary">
          La plantilla Word define los campos detectados por el sistema. Si cambias el archivo, el formulario de diligenciamiento cambia con la plantilla.
        </p>
      </section>
      <section className="grid gap-6 xl:grid-cols-[360px_minmax(0,1fr)]">
        <aside className="ep-card rounded-[2rem] p-5">
          <div className="flex items-center justify-between gap-3">
            <h2 className="text-xl font-semibold text-primary">Plantillas disponibles</h2>
            <button type="button" onClick={() => { setSelected(null); setUploadFile(null); setForm(emptyForm); }} className="text-sm font-semibold text-primary">Nueva plantilla</button>
          </div>
          <div className="mt-4 space-y-3">
            {isLoading ? <div className="ep-card-muted rounded-[1.3rem] px-4 py-4 text-sm text-secondary">Cargando plantillas Word...</div> : null}
            {!isLoading && !error && templates.length === 0 ? <div className="ep-card-muted rounded-[1.3rem] px-4 py-4 text-sm text-secondary">Todavía no hay plantillas cargadas.</div> : null}
            {templates.map((item) => (
              <button key={item.id} type="button" onClick={() => selectTemplate(item)} className={`block w-full rounded-[1.3rem] border px-4 py-4 text-left ${selected?.id === item.id ? "border-primary/30 bg-primary/8" : "border-[var(--line)]"}`}>
                <p className="text-sm font-semibold text-primary">{item.name || "Plantilla sin nombre"}</p>
                <p className="mt-1 text-xs text-secondary">{item.document_type || "Sin tipo de documento"} · {item.is_active ? "Plantilla activa" : "Inactiva"}</p>
                <p className="mt-1 text-xs text-secondary">
                  Campos detectados: {item.fields?.length ?? 0}
                </p>
              </button>
            ))}
          </div>
        </aside>
        <div className="ep-card rounded-[2rem] p-6 space-y-5">
          <div className="grid gap-4 lg:grid-cols-2">
            <label className="grid gap-2 text-sm font-medium text-primary">Nombre<input value={form.name} onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))} className="ep-input h-12 rounded-2xl px-4" /></label>
            <label className="grid gap-2 text-sm font-medium text-primary">Tipo de documento<input value={form.document_type} onChange={(event) => setForm((current) => ({ ...current, document_type: event.target.value }))} className="ep-input h-12 rounded-2xl px-4" /></label>
            <label className="grid gap-2 text-sm font-medium text-primary">Documento / minuta<input value={form.case_type} onChange={(event) => setForm((current) => ({ ...current, case_type: event.target.value }))} className="ep-input h-12 rounded-2xl px-4" /></label>
            <label className="grid gap-2 text-sm font-medium text-primary">Alcance<select value={form.scope_type} onChange={(event) => setForm((current) => ({ ...current, scope_type: event.target.value }))} className="ep-select h-12 rounded-2xl px-4"><option value="global">Global</option><option value="notary">Por notaría</option></select></label>
            <label className="grid gap-2 text-sm font-medium text-primary">Notaría<select value={form.notary_id} onChange={(event) => setForm((current) => ({ ...current, notary_id: event.target.value }))} className="ep-select h-12 rounded-2xl px-4"><option value="">Todas</option>{notaries.map((item) => <option key={item.id} value={item.id}>{item.notary_label} · {item.municipality}</option>)}</select></label>
            <label className="grid gap-2 text-sm font-medium text-primary">Plantilla activa<select value={form.is_active ? "active" : "inactive"} onChange={(event) => setForm((current) => ({ ...current, is_active: event.target.value === "active" }))} className="ep-select h-12 rounded-2xl px-4"><option value="active">Activa</option><option value="inactive">Inactiva</option></select></label>
          </div>
          <label className="grid gap-2 text-sm font-medium text-primary">Descripción<textarea value={form.description} onChange={(event) => setForm((current) => ({ ...current, description: event.target.value }))} rows={3} className="ep-textarea rounded-2xl px-4 py-3" /></label>
          <label className="grid gap-2 text-sm font-medium text-primary">Referencia interna<textarea value={form.internal_variable_map_json} onChange={(event) => setForm((current) => ({ ...current, internal_variable_map_json: event.target.value }))} rows={10} className="ep-textarea rounded-2xl px-4 py-3 font-mono text-xs" /></label>
          <label className="ep-card-muted flex items-center justify-between rounded-[1.5rem] px-4 py-4 text-sm text-secondary"><span className="inline-flex items-center gap-2"><FileUp className="h-4 w-4 text-primary" />Subir plantilla Word</span><input type="file" accept=".docx" onChange={(event) => setUploadFile(event.target.files?.[0] ?? null)} /></label>
          <div className="grid gap-4 lg:grid-cols-2">
            <div className="ep-card-soft rounded-[1.5rem] p-4"><p className="text-sm font-semibold text-primary">Intervinientes requeridos</p><ul className="mt-3 space-y-2 text-sm text-secondary"><li>Poderdante</li><li>Apoderado(a)</li></ul></div>
            <div className="ep-card-soft rounded-[1.5rem] p-4">
              <p className="text-sm font-semibold text-primary">
                Campos detectados{selected?.fields?.length ? ` (${selected.fields.length})` : ""}
              </p>
              {selected?.fields?.length ? (
                <ul className="mt-3 space-y-1">
                  {[...selected.fields]
                    .sort((a, b) => (a.step_order ?? 0) - (b.step_order ?? 0))
                    .map((f) => (
                      <li key={f.field_code} className="text-sm text-secondary">
                        {f.label}
                      </li>
                    ))}
                  </ul>
              ) : (
                <p className="mt-3 text-sm leading-6 text-secondary">El formulario dinamico aparece cuando la plantilla Word trae campos detectados.</p>
              )}
              <p className="mt-3 text-xs uppercase tracking-[0.18em] text-secondary">Formulario dinamico</p>
            </div>
          </div>
          {feedback ? <div className="ep-kpi-success rounded-2xl px-4 py-3 text-sm">{feedback}</div> : null}
          {error ? <div className="ep-kpi-critical rounded-2xl px-4 py-3 text-sm">{error}</div> : null}
          <button type="button" onClick={() => void handleSubmit()} disabled={isSaving} className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white disabled:opacity-60"><Save className="h-4 w-4" />{isSaving ? "Guardando..." : "Guardar plantilla Word"}</button>
        </div>
      </section>
    </div>
  );
}

