"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { ArrowRight, CheckCircle2, FileSignature } from "lucide-react";
import { PersonLookup } from "@/components/persons/person-lookup";
import { SearchableSelect } from "@/components/ui/searchable-select";
import { ValidatedInput } from "@/components/ui/validated-input";
import {
  createDocumentCase,
  generateCaseDraft,
  getActiveTemplates,
  saveCaseActData,
  saveCaseParticipants,
  type PersonRecord,
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

type SearchableOption = { value: string; label: string };
type ParticipantAssignment = { person_id: number | null; person: PersonPayload | null };

function safeString(value: unknown) {
  return typeof value === "string" ? value : "";
}

function normalizeUserOptions(users: UserOption[]): SelectOption[] {
  return (Array.isArray(users) ? users : []).map((item) => ({
    value: String(item.id ?? ""),
    label: [safeString(item.full_name), safeString(item.email)].filter(Boolean).join(" · ") || "Usuario sin nombre",
  })).filter((item) => item.value);
}

function sortByStepOrder<T extends { step_order?: number | null }>(items: T[]) {
  return [...items].sort((a, b) => Number(a.step_order ?? 0) - Number(b.step_order ?? 0));
}

function buildActDataFromTemplate(template: TemplateRecord | null) {
  const fields = sortByStepOrder(Array.isArray(template?.fields) ? template.fields : []);
  const initialData: Record<string, string> = {};
  const today = new Date();
  const commonValues = {
    dia_elaboracion: String(today.getDate()),
    mes_elaboracion: today.toLocaleDateString("es-CO", { month: "long" }),
    ano_elaboracion: String(today.getFullYear()),
  };

  for (const field of fields) {
    initialData[field.field_code] = "";
  }

  for (const [key, value] of Object.entries(commonValues)) {
    if (key in initialData) {
      initialData[key] = value;
    }
  }

  return initialData;
}

function parseTemplateFieldOptions(optionsJson: string | null | undefined): SelectOption[] {
  if (!optionsJson) {
    return [];
  }

  try {
    const parsed = JSON.parse(optionsJson);
    if (!Array.isArray(parsed)) {
      return [];
    }

    return parsed
      .map((item, index) => {
        if (typeof item === "string") {
          return { value: item, label: item };
        }
        if (item && typeof item === "object") {
          const rawValue = safeString((item as { value?: unknown; label?: unknown }).value);
          const rawLabel = safeString((item as { value?: unknown; label?: unknown }).label);
          const value = rawValue || rawLabel;
          const label = rawLabel || rawValue || `Opción ${index + 1}`;
          if (value || label) {
            return { value, label };
          }
        }
        return null;
      })
      .filter((item): item is SelectOption => Boolean(item?.value));
  } catch {
    return [];
  }
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
  const [showSubstituteNotary, setShowSubstituteNotary] = useState(false);
  const [expandedGeneralField, setExpandedGeneralField] = useState<string | null>(null);
  const [expandedParticipantRoles, setExpandedParticipantRoles] = useState<Record<string, boolean>>({});
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
  const [participants, setParticipants] = useState<Record<string, ParticipantAssignment>>({});
  const [participantDetails, setParticipantDetails] = useState<Record<string, PersonPayload | null>>({});
  const [actData, setActData] = useState<Record<string, string>>({});

  useEffect(() => {
    void load();
  }, []);

  useEffect(() => {
    if (!selectedTemplate) {
      return;
    }
    const nextParticipants = Object.fromEntries(
      sortByStepOrder(Array.isArray(selectedTemplate.required_roles) ? selectedTemplate.required_roles : [])
        .map((role) => [role.role_code, { person_id: null, person: null }]),
    ) as Record<string, ParticipantAssignment>;
    setParticipants(nextParticipants);
    setParticipantDetails(Object.fromEntries(Object.keys(nextParticipants).map((roleCode) => [roleCode, null])) as Record<string, PersonPayload | null>);
  }, [selectedTemplate, step]);

  useEffect(() => {
    setActData(buildActDataFromTemplate(selectedTemplate));
  }, [selectedTemplate]);

  useEffect(() => {
    if (step !== 2) {
      return;
    }
    const roles = sortByStepOrder(Array.isArray(selectedTemplate?.required_roles) ? selectedTemplate.required_roles : []);
    const nextExpanded = Object.fromEntries(
      roles.map((role, index) => [role.role_code, index === 0 || Number(role.step_order ?? 0) === 1]),
    ) as Record<string, boolean>;
    setExpandedParticipantRoles(nextExpanded);
  }, [selectedTemplate, step]);

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
      const defaultNotaryRaw = currentUser?.default_notary_id;
      const defaultNotaryId = String(defaultNotaryRaw ?? "");
      console.log("notary_id seteado:", String(defaultNotaryRaw ?? ""));

      setTemplates(safeTemplates);
      setSelectedTemplate(
        safeTemplates.find((item) => item.slug === "poder-general") ?? safeTemplates[0] ?? null,
      );
      setNotaries(notaryOptions);
      setCanSelectNotary(isSuperAdmin);
      setGeneralForm((current) => ({
        ...current,
        notary_id: !isSuperAdmin ? defaultNotaryId : current.notary_id,
        client_user_id: current.client_user_id,
        current_owner_user_id: "",
        protocolist_user_id: "",
        approver_user_id: "",
        titular_notary_user_id: "",
        substitute_notary_user_id: "",
      }));
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
  const templateRoles = useMemo(() => sortByStepOrder(Array.isArray(selectedTemplate?.required_roles) ? selectedTemplate.required_roles : []), [selectedTemplate]);
  const templateFields = useMemo(() => sortByStepOrder(Array.isArray(selectedTemplate?.fields) ? selectedTemplate.fields : []), [selectedTemplate]);
  const showAside = step >= 3;
  const generalManagerFields = useMemo<Array<{ key: "current_owner_user_id" | "protocolist_user_id" | "approver_user_id" | "titular_notary_user_id"; label: string; value: string }>>(() => [
    { key: "current_owner_user_id", label: "Responsable actual", value: generalForm.current_owner_user_id },
    { key: "protocolist_user_id", label: "Protocolista", value: generalForm.protocolist_user_id },
    { key: "approver_user_id", label: "Aprobador", value: generalForm.approver_user_id },
    { key: "titular_notary_user_id", label: "Notario titular", value: generalForm.titular_notary_user_id },
  ], [generalForm.current_owner_user_id, generalForm.protocolist_user_id, generalForm.approver_user_id, generalForm.titular_notary_user_id]);

  function assignExistingParticipant(role: string, person: PersonRecord) {
    const summary: PersonPayload = {
      document_type: person.document_type || "CC",
      document_number: person.document_number || "",
      full_name: person.full_name || "",
      sex: person.sex || "",
      nationality: person.nationality || "",
      marital_status: person.marital_status || "",
      profession: person.profession || "",
      municipality: person.municipality || "",
      is_transient: Boolean(person.is_transient),
      phone: person.phone || "",
      address: person.address || "",
      email: person.email || "",
      metadata_json: person.metadata_json || "{}",
    };
    setParticipants((current) => ({
      ...current,
      [role]: { person_id: person.id, person: null },
    }));
    setParticipantDetails((current) => ({ ...current, [role]: summary }));
  }

  function assignNewParticipant(role: string, person: PersonPayload) {
    const nextPerson: PersonPayload = {
      document_type: person.document_type || "CC",
      document_number: person.document_number || "",
      full_name: person.full_name || "",
      sex: person.sex || "",
      nationality: person.nationality || "",
      marital_status: person.marital_status || "",
      profession: person.profession || "",
      municipality: person.municipality || "",
      is_transient: Boolean(person.is_transient),
      phone: person.phone || "",
      address: person.address || "",
      email: person.email || "",
      metadata_json: person.metadata_json || "{}",
    };
    setParticipants((current) => ({
      ...current,
      [role]: { person_id: null, person: nextPerson },
    }));
    setParticipantDetails((current) => ({ ...current, [role]: nextPerson }));
  }

  function clearParticipant(role: string) {
    setParticipants((current) => ({
      ...current,
      [role]: { person_id: null, person: null },
    }));
    setParticipantDetails((current) => ({ ...current, [role]: null }));
  }

  function updateGeneralManager(field: "current_owner_user_id" | "protocolist_user_id" | "approver_user_id" | "titular_notary_user_id", value: string) {
    setGeneralForm((current) => ({ ...current, [field]: value }));
    setExpandedGeneralField(null);
  }

  function validateParticipants() {
    const requiredRoles = templateRoles.filter((role) => role.is_required);

    for (const role of requiredRoles) {
      const item = participants[role.role_code] ?? { person_id: null, person: null };
      if (item.person_id == null && item.person == null) {
        return `Selecciona o crea la persona para ${role.label || role.role_code}.`;
      }
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
        const updated = await saveCaseParticipants(
          caseDetail.id,
          templateRoles.map((role) => ({
              role_code: role.role_code,
              role_label: role.label,
              person_id: participants[role.role_code]?.person_id ?? null,
              person: participants[role.role_code]?.person ?? null,
            })),
        );
        setCaseDetail(updated);
      }
      if (step === 3 && caseDetail) {
        const missingRequiredField = templateFields.find((field) => field.is_required && !(actData[field.field_code] ?? "").trim());
        if (missingRequiredField) {
          throw new Error(`Completa el campo obligatorio ${missingRequiredField.label || missingRequiredField.field_code}.`);
        }
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

  return (
    <div className="space-y-6">
      <section className="ep-card z-0 rounded-[2rem] p-6">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.22em] text-accent">
              {caseDetail?.internal_case_number ? `Crear Minuta · ${caseDetail.internal_case_number}` : "Crear Minuta"}
            </p>
          </div>
          {caseDetail ? (
            <Link href={`/dashboard/casos/${caseDetail.id}`} className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white">
              Abrir detalle de la minuta <ArrowRight className="h-4 w-4" />
            </Link>
          ) : null}
        </div>
      </section>

      <section className="ep-card z-0 rounded-[2rem] p-6">
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

      <section className={`grid gap-6 ${showAside ? "xl:grid-cols-[minmax(0,1.2fr)_360px]" : "xl:grid-cols-1"}`}>
        <div className="ep-card z-0 rounded-[2rem] p-6 space-y-6">
          {isLoading ? <div className="ep-card-muted z-0 rounded-[1.5rem] px-4 py-6 text-sm text-secondary">Cargando plantillas, notarías y usuarios...</div> : null}
          {!isLoading && error && templates.length === 0 ? <div className="ep-kpi-critical z-0 rounded-2xl px-4 py-3 text-sm">{error}</div> : null}
          {!isLoading && !error && templates.length === 0 ? <div className="ep-card-muted z-0 rounded-[1.5rem] px-4 py-6 text-sm text-secondary">No hay plantillas activas todavía.</div> : null}

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
                  <div className="grid gap-4">
                    {canSelectNotary ? (
                      <SearchableSelect label="Notaría" value={generalForm.notary_id} options={notaries} onChange={(value) => setGeneralForm((current) => ({ ...current, notary_id: value }))} />
                    ) : null}
                    {generalManagerFields.map((field) => {
                      const isExpanded = expandedGeneralField === field.key;
                      const selectedLabel = userOptions.find((item) => item.value === field.value)?.label || "Sin asignar";
                      return (
                        <div key={field.key} className="ep-card-soft z-0 rounded-[1.6rem] p-4 space-y-3" style={{ position: "relative", zIndex: "auto" }}>
                          <button
                            type="button"
                            onClick={() => setExpandedGeneralField((current) => (current === field.key ? null : field.key))}
                            className="flex w-full items-center justify-between gap-3 rounded-[1.1rem] px-4 py-3 text-left"
                          >
                            <span className="text-sm font-medium text-primary">{field.label}</span>
                            <span className="text-sm font-medium text-secondary">{selectedLabel}</span>
                          </button>
                          {isExpanded ? (
                            <SearchableSelect
                              label={field.label}
                              value={field.value}
                              options={userOptions}
                              onChange={(value) => updateGeneralManager(field.key, value)}
                            />
                          ) : null}
                        </div>
                      );
                    })}
                    {showSubstituteNotary ? (
                      <div className="space-y-3">
                        <SearchableSelect label="Notario suplente" value={generalForm.substitute_notary_user_id} options={userOptions} onChange={(value) => setGeneralForm((current) => ({ ...current, substitute_notary_user_id: value }))} />
                        <button
                          type="button"
                          onClick={() => setShowSubstituteNotary(false)}
                          className="inline-flex items-center gap-2 text-sm font-semibold text-primary"
                        >
                          - Ocultar notario suplente
                        </button>
                      </div>
                    ) : (
                      <button
                        type="button"
                        onClick={() => setShowSubstituteNotary(true)}
                        className="inline-flex items-center gap-2 text-sm font-semibold text-primary"
                      >
                        + Agregar notario suplente
                      </button>
                    )}
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
                  {templateRoles.map((role) => {
                    const assignment = participants[role.role_code] ?? { person_id: null, person: null };
                    const displayPerson = participantDetails[role.role_code] ?? assignment.person;
                    const roleStatus = role.is_required ? "Bloque obligatorio" : "Bloque opcional";
                    const isExpanded = Boolean(expandedParticipantRoles[role.role_code]);
                    const isComplete = Boolean(displayPerson?.document_number && displayPerson?.full_name);
                    return (
                      <div key={role.role_code} className="ep-card-soft rounded-[1.8rem] p-5 space-y-4">
                        <button
                          type="button"
                          onClick={() => setExpandedParticipantRoles((current) => ({ ...current, [role.role_code]: !current[role.role_code] }))}
                          className="flex w-full min-h-12 items-center justify-between gap-3 rounded-[1.25rem] px-4 py-3 text-left"
                        >
                          <div className="space-y-1">
                            <p className="text-sm font-medium text-primary">{role.label || role.role_code}</p>
                            <h3 className="text-sm font-medium text-secondary">{roleStatus}</h3>
                          </div>
                          <span className="ep-pill rounded-full px-3 py-1 text-xs font-semibold text-secondary">{isComplete ? "Completo" : "Incompleto"}</span>
                          </button>
                        {isExpanded ? (
                          <div className="space-y-4">
                            {assignment.person_id !== null || assignment.person !== null ? (
                              <div className="rounded-[1.35rem] border border-emerald-500/20 bg-emerald-500/10 p-4">
                                <div className="flex items-start justify-between gap-3">
                                  <div>
                                    <p className="text-sm font-semibold text-primary">{displayPerson?.full_name || "Persona asignada"}</p>
                                    <p className="mt-1 text-sm text-secondary">
                                      {displayPerson?.document_type || "DOC"} {displayPerson?.document_number || "Sin número"} · {displayPerson?.municipality || "Sin municipio"}
                                    </p>
                                  </div>
                                  <CheckCircle2 className="mt-0.5 h-5 w-5 text-emerald-600" />
                                </div>
                                <button
                                  type="button"
                                  onClick={() => clearParticipant(role.role_code)}
                                  className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-primary"
                                >
                                  Cambiar
                                </button>
                              </div>
                            ) : (
                              <PersonLookup
                                onPick={(selected) => assignExistingParticipant(role.role_code, selected)}
                                onNotFound={(person) => assignNewParticipant(role.role_code, person)}
                              />
                            )}
                          </div>
                        ) : null}
                      </div>
                    );
                  })}
                </div>
              ) : null}

              {step === 3 ? (
                <div className="space-y-5">
                  <h2 className="text-2xl font-semibold text-primary">4. Datos del acto</h2>
                  {templateFields.length > 0 ? (
                    <div className="grid grid-cols-1 gap-4">
                      {templateFields.map((field) => {
                        const label = `${field.label || field.field_code}${field.is_required ? " *" : ""}`;
                        const value = actData[field.field_code] ?? "";

                        if (field.field_type === "select") {
                          return (
                            <div key={field.field_code} className="w-full">
                              <SearchableSelect
                                label={label}
                                value={value}
                                options={parseTemplateFieldOptions(field.options_json)}
                                onChange={(nextValue) => setActData((current) => ({ ...current, [field.field_code]: nextValue }))}
                              />
                            </div>
                          );
                        }

                        if (field.field_type === "textarea") {
                          return (
                            <label key={field.field_code} className="grid gap-2 text-sm font-medium text-primary">
                              <span>{label}</span>
                              <textarea
                                value={value}
                                onChange={(event) => setActData((current) => ({ ...current, [field.field_code]: event.target.value }))}
                                placeholder={field.placeholder_key || ""}
                                className="ep-input rounded-2xl px-4 py-3 w-full"
                              />
                            </label>
                          );
                        }

                        if (field.field_type === "date") {
                          return (
                            <label key={field.field_code} className="grid gap-2 text-sm font-medium text-primary">
                              <span>{label}</span>
                              <input
                                type="date"
                                value={value}
                                onChange={(event) => setActData((current) => ({ ...current, [field.field_code]: event.target.value }))}
                                className="ep-input h-12 rounded-2xl px-4"
                              />
                            </label>
                          );
                        }

                        if (field.field_type === "currency") {
                          return (
                            <label key={field.field_code} className="grid gap-2 text-sm font-medium text-primary">
                              <span>{label}</span>
                              <div className="relative">
                                <span className="pointer-events-none absolute inset-y-0 left-4 flex items-center text-sm text-secondary">$</span>
                                <input
                                  type="number"
                                  value={value}
                                  onChange={(event) => setActData((current) => ({ ...current, [field.field_code]: event.target.value }))}
                                  placeholder={field.placeholder_key || ""}
                                  className="ep-input h-12 rounded-2xl px-4 pl-8"
                                />
                              </div>
                            </label>
                          );
                        }

                        if (field.field_type === "number") {
                          return (
                            <ValidatedInput
                              key={field.field_code}
                              label={label}
                              type="number"
                              value={value}
                              placeholder={field.placeholder_key || ""}
                              onChange={(nextValue) => setActData((current) => ({ ...current, [field.field_code]: nextValue }))}
                            />
                          );
                        }

                        return (
                          <ValidatedInput
                            key={field.field_code}
                            label={label}
                            value={value}
                            placeholder={field.placeholder_key || ""}
                            onChange={(nextValue) => setActData((current) => ({ ...current, [field.field_code]: nextValue }))}
                          />
                        );
                      })}
                    </div>
                  ) : (
                    <div className="ep-card-muted z-0 rounded-[1.5rem] px-4 py-6 text-sm text-secondary">La plantilla seleccionada no tiene campos configurados.</div>
                  )}
                </div>
              ) : null}

              {step === 4 ? (
                <div className="space-y-5">
                  <h2 className="text-2xl font-semibold text-primary">5. Revisión y generar borrador</h2>
                  <div className="ep-card-soft z-0 rounded-[1.6rem] p-5 text-sm leading-6 text-secondary">
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

        {showAside ? (
          <aside className="space-y-4">
            <div className="ep-card z-0 rounded-[1.8rem] p-5">
              <p className="text-xs uppercase tracking-[0.2em] text-secondary">Minuta activa</p>
              <p className="mt-2 text-lg font-semibold text-primary">{caseDetail?.internal_case_number || "Aún no creado"}</p>
              <p className="mt-3 text-sm text-secondary">Plantilla: {selectedTemplate?.name || "Sin selección"}</p>
              <p className="mt-2 text-sm text-secondary">Estado: {caseDetail?.current_state || "borrador"}</p>
              <p className="mt-2 text-sm text-secondary">Escritura oficial: {caseDetail?.official_deed_number || "Pendiente de aprobación"}</p>
            </div>
            <div className="ep-card z-0 rounded-[1.8rem] p-5">
              <p className="text-xs uppercase tracking-[0.2em] text-secondary">Reglas funcionales</p>
              <ul className="mt-3 space-y-2 text-sm leading-6 text-secondary">
                <li>La plantilla define el trámite.</li>
                <li>El número oficial no se asigna al crear.</li>
                <li>Poderdante y apoderado son obligatorios.</li>
                <li>Las personas se reutilizan por tipo y número.</li>
              </ul>
            </div>
          </aside>
        ) : null}
      </section>
    </div>
  );
}

