"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { ArrowRight, CheckCircle2, FileSignature } from "lucide-react";
import { PersonLookup } from "@/components/persons/person-lookup";
import { HybridAutocomplete } from "@/components/ui/hybrid-autocomplete";
import { SearchableSelect } from "@/components/ui/searchable-select";
import { ValidatedInput } from "@/components/ui/validated-input";
import {
  createDocumentCase,
  generateCaseDraft,
  getActiveTemplates,
  saveCaseActData,
  saveCaseParticipants,
  type DocumentFlowCase,
  type PersonPayload,
  type TemplateRecord,
} from "@/lib/document-flow";
import { getCurrentUser, getNotaries, getUserOptions, type UserOption } from "@/lib/api";

const steps = [
  "Seleccionar plantilla",
  "Datos generales",
  "Intervinientes",
  "Datos del acto",
  "Revisión y generar borrador",
];
const documentTypes = ["CC", "CE", "TI", "PP", "NIT"];
const sexOptions = ["F", "M", "No especifica"];
const nationalityOptions = ["Colombiana", "Extranjera", "Venezolana", "Española"];
const maritalStatusOptions = ["Soltero(a)", "Casado(a)", "Unión marital", "Divorciado(a)", "Viudo(a)"];
const professionSuggestions = ["Abogado", "Comerciante", "Administrador", "Ingeniero", "Contador", "Docente"];

type SelectOption = { value: string; label: string };

function blankPerson(): PersonPayload {
  return {
    document_type: "CC",
    document_number: "",
    full_name: "",
    sex: "",
    nationality: "Colombiana",
    marital_status: "",
    profession: "",
    municipality: "",
    is_transient: false,
    phone: "",
    address: "",
    email: "",
    metadata_json: "{}",
  };
}

function safeString(value: unknown) {
  return typeof value === "string" ? value : "";
}

function normalizeUserOptions(users: UserOption[]): SelectOption[] {
  return (Array.isArray(users) ? users : []).map((item) => ({
    value: String(item.id ?? ""),
    label: [safeString(item.full_name), safeString(item.email)].filter(Boolean).join(" · ") || "Usuario sin nombre",
  })).filter((item) => item.value);
}

export function CreateCaseWizard() {
  const [step, setStep] = useState(0);
  const [templates, setTemplates] = useState<TemplateRecord[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<TemplateRecord | null>(null);
  const [notaries, setNotaries] = useState<SelectOption[]>([]);
  const [users, setUsers] = useState<UserOption[]>([]);
  const [caseDetail, setCaseDetail] = useState<DocumentFlowCase | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [canSelectNotary, setCanSelectNotary] = useState(true);
  const [generalForm, setGeneralForm] = useState({
    notary_id: "",
    client_user_id: "",
    current_owner_user_id: "",
    protocolist_user_id: "",
    approver_user_id: "",
    titular_notary_user_id: "",
    substitute_notary_user_id: "",
    requires_client_review: true,
    metadata_json: JSON.stringify({ clase: "Poder General" }, null, 2),
  });
  const [participants, setParticipants] = useState<Record<string, PersonPayload>>({
    poderdante: blankPerson(),
    apoderado: blankPerson(),
  });
  const [actData, setActData] = useState<Record<string, string>>({
    dia_elaboracion: String(new Date().getDate()),
    mes_elaboracion: "marzo",
    ano_elaboracion: String(new Date().getFullYear()),
    derechos_notariales: "185000",
    iva: "35150",
    aporte_superintendencia: "6500",
    fondo_notariado: "5200",
    consecutivos_hojas_papel_notarial: "",
    extension: "",
    clase_cuantia_acto: "Sin cuantía",
  });

  useEffect(() => {
    void load();
  }, []);

  async function load() {
    setIsLoading(true);
    setError(null);
    try {
      const [templateData, notaryData, userData, currentUser] = await Promise.all([
        getActiveTemplates(),
        getNotaries(),
        getUserOptions(true),
        getCurrentUser(),
      ]);
      const safeTemplates = Array.isArray(templateData) ? templateData : [];
      const safeNotaries = Array.isArray(notaryData) ? notaryData : [];
      const safeUsers = Array.isArray(userData) ? userData : [];
      const notaryOptions = safeNotaries
        .map((item) => ({
          value: String(item.id ?? ""),
          label: [safeString(item.notary_label), safeString(item.municipality)].filter(Boolean).join(" · ") || "Notaría sin nombre",
        }))
        .filter((item) => item.value);
      const isSuperAdmin = Array.isArray(currentUser?.role_codes) && currentUser.role_codes.includes("super_admin");
      const defaultNotaryId = String((currentUser as { default_notary_id?: number | null })?.default_notary_id ?? "");
      const defaultNotaryOption = defaultNotaryId ? notaryOptions.find((item) => item.value === defaultNotaryId) : null;

      setTemplates(safeTemplates);
      setSelectedTemplate(
        safeTemplates.find((item) => item.slug === "poder-general") ?? safeTemplates[0] ?? null,
      );
      setNotaries(notaryOptions);
      setCanSelectNotary(isSuperAdmin);
      if (!isSuperAdmin && defaultNotaryOption) {
        setGeneralForm((current) => ({ ...current, notary_id: defaultNotaryOption.value }));
      }
      setUsers(safeUsers);
    } catch (loadError) {
      setTemplates([]);
      setSelectedTemplate(null);
      setNotaries([]);
      setUsers([]);
      setError(loadError instanceof Error ? loadError.message : "No fue posible cargar la base del wizard.");
    } finally {
      setIsLoading(false);
    }
  }

  const userOptions = useMemo(() => normalizeUserOptions(users), [users]);

  function updateParticipant(role: string, field: keyof PersonPayload, value: string | boolean) {
    setParticipants((current) => ({
      ...current,
      [role]: { ...(current[role] ?? blankPerson()), [field]: value },
    }));
  }

  function validateParticipants() {
    for (const role of ["poderdante", "apoderado"]) {
      const item = participants[role] ?? blankPerson();
      if (!item.document_number || !item.full_name || !item.marital_status || !item.municipality) {
        return `Completa los datos obligatorios de ${role}.`;
      }
    }
    if (
      participants.poderdante?.document_type === participants.apoderado?.document_type &&
      participants.poderdante?.document_number &&
      participants.poderdante.document_number === participants.apoderado?.document_number
    ) {
      return "Advertencia: poderdante y apoderado no deberían ser la misma persona.";
    }
    return null;
  }

  async function handleCreateCase() {
    if (!selectedTemplate || !generalForm.notary_id) {
      throw new Error("Debes seleccionar la notaría y la plantilla para crear la minuta.");
    }
    const created = await createDocumentCase({
      template_id: selectedTemplate.id,
      notary_id: Number(generalForm.notary_id),
      client_user_id: generalForm.client_user_id ? Number(generalForm.client_user_id) : null,
      current_owner_user_id: generalForm.current_owner_user_id ? Number(generalForm.current_owner_user_id) : null,
      protocolist_user_id: generalForm.protocolist_user_id ? Number(generalForm.protocolist_user_id) : null,
      approver_user_id: generalForm.approver_user_id ? Number(generalForm.approver_user_id) : null,
      titular_notary_user_id: generalForm.titular_notary_user_id ? Number(generalForm.titular_notary_user_id) : null,
      substitute_notary_user_id: generalForm.substitute_notary_user_id ? Number(generalForm.substitute_notary_user_id) : null,
      requires_client_review: generalForm.requires_client_review,
      metadata_json: generalForm.metadata_json,
    });
    setCaseDetail(created);
  }

  async function continueStep() {
    setError(null);
    setFeedback(null);
    setIsSaving(true);
    try {
      if (step === 0) {
        if (!selectedTemplate) {
          throw new Error("No hay una plantilla activa disponible para iniciar la minuta.");
        }
      }
      if (step === 1 && !caseDetail) {
        await handleCreateCase();
      }
      if (step === 2 && caseDetail) {
        const participantError = validateParticipants();
        if (participantError) {
          throw new Error(participantError);
        }
        const updated = await saveCaseParticipants(caseDetail.id, [
          { role_code: "poderdante", role_label: "Poderdante", person: participants.poderdante ?? blankPerson() },
          { role_code: "apoderado", role_label: "Apoderado(a)", person: participants.apoderado ?? blankPerson() },
        ]);
        setCaseDetail(updated);
      }
      if (step === 3 && caseDetail) {
        const updated = await saveCaseActData(caseDetail.id, { data_json: JSON.stringify(actData) });
        setCaseDetail(updated);
      }
      if (step === 4 && caseDetail) {
        const updated = await generateCaseDraft(caseDetail.id, "Borrador generado desde el wizard de Crear Caso.");
        setCaseDetail(updated);
        setFeedback("Minuta creada y borrador Word v1 generado correctamente.");
        return;
      }
      setStep((current) => Math.min(current + 1, steps.length - 1));
    } catch (stepError) {
      setError(stepError instanceof Error ? stepError.message : "No fue posible avanzar en el wizard.");
    } finally {
      setIsSaving(false);
    }
  }

  const templateRoles = Array.isArray(selectedTemplate?.required_roles) ? selectedTemplate.required_roles : [];

  return (
    <div className="space-y-6">
      <section className="ep-card rounded-[2rem] p-6">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.22em] text-accent">Crear Minuta</p>
            <h1 className="mt-2 text-3xl font-semibold tracking-[-0.05em] text-primary">Wizard documental inicial para Poder General</h1>
            <p className="mt-3 max-w-3xl text-base leading-7 text-secondary">
              El alcance de hoy prioriza la prueba real: plantilla, creación de la minuta, intervinientes, datos del acto y generación del borrador Word.
            </p>
          </div>
          {caseDetail ? (
            <Link href={`/dashboard/casos/${caseDetail.id}`} className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white">
              Abrir detalle de la minuta <ArrowRight className="h-4 w-4" />
            </Link>
          ) : null}
        </div>
      </section>

      <section className="ep-card rounded-[2rem] p-6">
        <div className="grid gap-3 xl:grid-cols-5">
          {steps.map((item, index) => (
            <div key={item} className={`rounded-[1.35rem] border px-4 py-4 ${index === step ? "border-primary/30 bg-primary text-white" : index < step ? "border-emerald-500/20 bg-emerald-500/10" : "border-[var(--line)] bg-[var(--panel-soft)]"}`}>
              <div className="flex items-center gap-3">
                <div className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-semibold ${index === step ? "bg-white/15 text-white" : index < step ? "bg-emerald-500/20 text-primary" : "bg-[var(--panel)] text-primary"}`}>
                  {index < step ? <CheckCircle2 className="h-4 w-4" /> : index + 1}
                </div>
                <p className={`text-sm font-semibold ${index === step ? "text-white" : "text-primary"}`}>{item}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[minmax(0,1.2fr)_360px]">
        <div className="ep-card rounded-[2rem] p-6 space-y-6">
          {isLoading ? <div className="ep-card-muted rounded-[1.5rem] px-4 py-6 text-sm text-secondary">Cargando plantillas, notarías y usuarios...</div> : null}
          {!isLoading && error && templates.length === 0 ? <div className="ep-kpi-critical rounded-2xl px-4 py-3 text-sm">{error}</div> : null}
          {!isLoading && !error && templates.length === 0 ? <div className="ep-card-muted rounded-[1.5rem] px-4 py-6 text-sm text-secondary">No hay plantillas activas todavía.</div> : null}

          {!isLoading && templates.length > 0 ? (
            <>
              {step === 0 ? (
                <div className="space-y-5">
                  <h2 className="text-2xl font-semibold text-primary">1. Seleccionar plantilla</h2>
                  <div className="grid gap-4 lg:grid-cols-2">
                    {templates.map((item) => (
                      <button key={item.id} type="button" onClick={() => setSelectedTemplate(item)} className={`rounded-[1.5rem] border p-5 text-left ${selectedTemplate?.id === item.id ? "border-primary/30 bg-primary/8" : "border-[var(--line)]"}`}>
                        <p className="text-lg font-semibold text-primary">{item.name || "Plantilla sin nombre"}</p>
                        <p className="mt-2 text-sm text-secondary">{item.document_type || "Sin tipo documental"}</p>
                        <p className="mt-3 text-xs text-secondary">Roles: {(Array.isArray(item.required_roles) ? item.required_roles : []).map((role) => role.label).filter(Boolean).join(", ") || "Sin roles configurados"}</p>
                      </button>
                    ))}
                  </div>
                </div>
              ) : null}

              {step === 1 ? (
                <div className="space-y-5">
                  <h2 className="text-2xl font-semibold text-primary">2. Datos generales de la minuta</h2>
                  <div className="grid gap-4 lg:grid-cols-2">
                    {canSelectNotary ? (
                      <SearchableSelect label="Notaría" value={generalForm.notary_id} options={notaries} onChange={(value) => setGeneralForm((current) => ({ ...current, notary_id: value }))} />
                    ) : null}
                    <SearchableSelect label="Responsable actual" value={generalForm.current_owner_user_id} options={userOptions} onChange={(value) => setGeneralForm((current) => ({ ...current, current_owner_user_id: value }))} />
                    <SearchableSelect label="Protocolista" value={generalForm.protocolist_user_id} options={userOptions} onChange={(value) => setGeneralForm((current) => ({ ...current, protocolist_user_id: value }))} />
                    <SearchableSelect label="Aprobador" value={generalForm.approver_user_id} options={userOptions} onChange={(value) => setGeneralForm((current) => ({ ...current, approver_user_id: value }))} />
                    <SearchableSelect label="Notario titular" value={generalForm.titular_notary_user_id} options={userOptions} onChange={(value) => setGeneralForm((current) => ({ ...current, titular_notary_user_id: value }))} />
                    <SearchableSelect label="Notario suplente" value={generalForm.substitute_notary_user_id} options={userOptions} onChange={(value) => setGeneralForm((current) => ({ ...current, substitute_notary_user_id: value }))} />
                  </div>
                  <label className="ep-card-muted flex items-center gap-3 rounded-2xl px-4 py-3 text-sm text-secondary">
                    <input type="checkbox" checked={generalForm.requires_client_review} onChange={(event) => setGeneralForm((current) => ({ ...current, requires_client_review: event.target.checked }))} />
                    Requiere revisión cliente
                  </label>
                </div>
              ) : null}

              {step === 2 ? (
                <div className="space-y-6">
                  <h2 className="text-2xl font-semibold text-primary">3. Intervinientes</h2>
                  {([
                    ["poderdante", "Poderdante"],
                    ["apoderado", "Apoderado(a)"],
                  ] as const).map(([role, label]) => {
                    const person = participants[role] ?? blankPerson();
                    return (
                      <div key={role} className="ep-card-soft rounded-[1.8rem] p-5 space-y-4">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-xs uppercase tracking-[0.2em] text-accent">{label}</p>
                            <h3 className="text-xl font-semibold text-primary">Bloque obligatorio</h3>
                          </div>
                          <span className="ep-pill rounded-full px-3 py-1 text-xs text-secondary">{person.document_number && person.full_name ? "Completo" : "Incompleto"}</span>
                        </div>
                        <PersonLookup onPick={(selected) => setParticipants((current) => ({ ...current, [role]: { ...blankPerson(), ...current[role], ...selected, metadata_json: current[role]?.metadata_json || "{}" } }))} />
                        <div className="grid gap-4 lg:grid-cols-2">
                          <SearchableSelect label="Tipo de documento" value={person.document_type} options={documentTypes.map((item) => ({ value: item, label: item }))} onChange={(value) => updateParticipant(role, "document_type", value)} />
                          <ValidatedInput label="Número de documento" value={person.document_number || ""} onChange={(value) => updateParticipant(role, "document_number", value)} />
                          <ValidatedInput label="Nombre completo" value={person.full_name || ""} onChange={(value) => updateParticipant(role, "full_name", value)} />
                          <SearchableSelect label="Sexo" value={person.sex || ""} options={sexOptions.map((item) => ({ value: item, label: item }))} onChange={(value) => updateParticipant(role, "sex", value)} />
                          <SearchableSelect label="Nacionalidad" value={person.nationality || ""} options={nationalityOptions.map((item) => ({ value: item, label: item }))} onChange={(value) => updateParticipant(role, "nationality", value)} />
                          <SearchableSelect label="Estado civil" value={person.marital_status || ""} options={maritalStatusOptions.map((item) => ({ value: item, label: item }))} onChange={(value) => updateParticipant(role, "marital_status", value)} />
                          <HybridAutocomplete label="Profesión u oficio" value={person.profession || ""} options={professionSuggestions} onChange={(value) => updateParticipant(role, "profession", value)} />
                          <ValidatedInput label="Municipio de domicilio" value={person.municipality || ""} onChange={(value) => updateParticipant(role, "municipality", value)} />
                          <ValidatedInput label="Teléfono" value={person.phone || ""} onChange={(value) => updateParticipant(role, "phone", value)} />
                          <ValidatedInput label="Email" type="email" value={person.email || ""} onChange={(value) => updateParticipant(role, "email", value)} />
                        </div>
                        <label className="grid gap-2 text-sm font-medium text-primary">
                          <span>Dirección</span>
                          <input value={person.address || ""} onChange={(event) => updateParticipant(role, "address", event.target.value)} className="ep-input h-12 rounded-2xl px-4" />
                        </label>
                        <label className="ep-card-muted flex items-center gap-3 rounded-2xl px-4 py-3 text-sm text-secondary">
                          <input type="checkbox" checked={Boolean(person.is_transient)} onChange={(event) => updateParticipant(role, "is_transient", event.target.checked)} />
                          ¿Está de tránsito?
                        </label>
                      </div>
                    );
                  })}
                </div>
              ) : null}

              {step === 3 ? (
                <div className="space-y-5">
                  <h2 className="text-2xl font-semibold text-primary">4. Datos del acto</h2>
                  <div className="grid gap-4 lg:grid-cols-2">
                    {Object.entries({
                      dia_elaboracion: "Día elaboración",
                      mes_elaboracion: "Mes elaboración",
                      ano_elaboracion: "Año elaboración",
                      derechos_notariales: "Derechos notariales",
                      iva: "IVA",
                      aporte_superintendencia: "Aporte superintendencia",
                      fondo_notariado: "Fondo notariado",
                      consecutivos_hojas_papel_notarial: "Consecutivos hojas papel notarial",
                      extension: "Extensión",
                      clase_cuantia_acto: "Clase/cuantía del acto",
                    }).map(([key, label]) => (
                      <ValidatedInput key={key} label={label} value={actData[key] ?? ""} onChange={(value) => setActData((current) => ({ ...current, [key]: value }))} />
                    ))}
                  </div>
                </div>
              ) : null}

              {step === 4 ? (
                <div className="space-y-5">
                  <h2 className="text-2xl font-semibold text-primary">5. Revisión y generar borrador</h2>
                  <div className="ep-card-soft rounded-[1.6rem] p-5 text-sm leading-6 text-secondary">
                    <p>Plantilla: <span className="font-semibold text-primary">{selectedTemplate?.name || "Sin plantilla"}</span></p>
                    <p className="mt-2">Intervinientes: {templateRoles.map((role) => role.label).filter(Boolean).join(", ") || "Poderdante y Apoderado(a)"}</p>
                    <p className="mt-2">Número interno: <span className="font-semibold text-primary">{caseDetail?.internal_case_number || "Se generar? al crear la minuta"}</span></p>
                    <p className="mt-2">El usuario final nunca ver? placeholders; solo los datos amigables capturados en el wizard.</p>
                  </div>
                  <button type="button" onClick={() => void continueStep()} disabled={isSaving} className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white disabled:opacity-60">
                    <FileSignature className="h-4 w-4" />Generar borrador Word v1
                  </button>
                </div>
              ) : null}
            </>
          ) : null}

          {error && !(isLoading && templates.length === 0) ? <div className="ep-kpi-critical rounded-2xl px-4 py-3 text-sm">{error}</div> : null}
          {feedback ? <div className="ep-kpi-success rounded-2xl px-4 py-3 text-sm">{feedback}</div> : null}
          {!isLoading && templates.length > 0 && step < 4 ? (
            <button type="button" onClick={() => void continueStep()} disabled={isSaving} className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white disabled:opacity-60">
              Continuar <ArrowRight className="h-4 w-4" />
            </button>
          ) : null}
        </div>

        <aside className="space-y-4">
          <div className="ep-card rounded-[1.8rem] p-5">
            <p className="text-xs uppercase tracking-[0.2em] text-secondary">Minuta activa</p>
            <p className="mt-2 text-lg font-semibold text-primary">{caseDetail?.internal_case_number || "Aún no creado"}</p>
            <p className="mt-3 text-sm text-secondary">Plantilla: {selectedTemplate?.name || "Sin selección"}</p>
            <p className="mt-2 text-sm text-secondary">Estado: {caseDetail?.current_state || "borrador"}</p>
            <p className="mt-2 text-sm text-secondary">Escritura oficial: {caseDetail?.official_deed_number || "Pendiente de aprobación"}</p>
          </div>
          <div className="ep-card rounded-[1.8rem] p-5">
            <p className="text-xs uppercase tracking-[0.2em] text-secondary">Reglas funcionales</p>
            <ul className="mt-3 space-y-2 text-sm leading-6 text-secondary">
              <li>La plantilla define el trámite.</li>
              <li>El número oficial no se asigna al crear.</li>
              <li>Poderdante y apoderado son obligatorios.</li>
              <li>Las personas se reutilizan por tipo y número.</li>
            </ul>
          </div>
        </aside>
      </section>
    </div>
  );
}

