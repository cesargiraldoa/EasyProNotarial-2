"use client";

import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";
import { ArrowRight, CheckCircle2 } from "lucide-react";
import { SearchableSelect } from "@/components/ui/searchable-select";
import { ValidatedInput } from "@/components/ui/validated-input";
import {
  createDocumentCase,
  getActiveTemplates,
  saveCaseActData,
  type DocumentFlowCase,
  type TemplateRecord,
} from "@/lib/document-flow";
import { getCurrentUser, getNotaries, getUserOptions, type UserOption } from "@/lib/api";

const steps = [
  "Plantilla",
  "Documento / minuta",
  "Diligenciar",
  "Revisar y generar Word",
];
const documentTypes = ["CC", "CE", "TI", "PP", "NIT"];
const sexOptions = ["F", "M", "No especifica"];
const nationalityOptions = ["Colombiana", "Extranjera", "Venezolana", "Española"];
const maritalStatusOptions = ["Soltero(a)", "Casado(a)", "Unión marital", "Divorciado(a)", "Viudo(a)"];
const professionSuggestions = ["Abogado", "Comerciante", "Administrador", "Ingeniero", "Contador", "Docente"];

type SelectOption = { value: string; label: string };

const demoData: Record<string, string> = {
  numero_escritura: "2045",
  numero_apartamento: "804",
  numero_matricula: "001-1528731",
  nombre_comprador_1: "JUAN CAMILO VASQUEZ MIRA",
  tipo_documento_comprador_1: "C.C.",
  numero_documento_comprador_1: "1.037.657.164",
  nombre_comprador_2: "MARIA FERNANDA LOPEZ GOMEZ",
  tipo_documento_comprador_2: "C.C.",
  numero_documento_comprador_2: "1.045.234.567",
  valor_de_la_venta_en_numeros: "212.600.000",
  valor_del_acto_de_la_hipoteca: "149.559.520",
  dia_elaboracion_escritura: "veintisiete (27)",
  mes_elaboracion_escritura: "abril",
  comprador_es_hombre_o_mujer: "varón",
  nacionalidad_comprador: "colombiana",
  municipio_domicilio_comprador: "Envigado",
  seleccione_si_comprador_esta_de_transito: "de tránsito por Caldas, Antioquia,",
  estado_civil_comprador: "Soltero sin unión marital de hecho",
  comprador_2_es_hombre_o_mujer: "mujer",
  nacionalidad_comprador_2: "colombiana",
  municipio_domicilio_comprador_2: "Medellín",
  seleccione_si_comprador_2_esta_de_transito: "de tránsito por Caldas, Antioquia,",
  estado_civil_comprador_2: "Soltera sin unión marital de hecho",
  fecha_celebracion_de_la_promesa_compraventa: "quince (15) de enero de dos mil veinticinco (2025)",
  numero_de_piso: "octavo (8°)",
  linderos: "con linderos según reglamento de propiedad horizontal",
  valor_apartamento_en_letras: "DOSCIENTOS DOCE MILLONES SEISCIENTOS MIL PESOS MONEDA CORRIENTE",
  en_letras_cuota_inicial: "SESENTA Y DOS MILLONES SEISCIENTOS MIL PESOS MONEDA CORRIENTE",
  en_numeros_cuota_inicial: "62.600.000",
  origen_cuota_inicial: "recursos propios",
  valor_del_acto_de_la_hipoteca_en_letras: "CIENTO CUARENTA Y NUEVE MILLONES QUINIENTOS CINCUENTA Y NUEVE MIL QUINIENTOS VEINTE PESOS MONEDA CORRIENTE",
  direccion_comprador_1: "Carrera 25 # 39 Sur 15, Apto 1203, Envigado",
  direccion_comprador_2: "Calle 10 # 43 A 22, Apto 502, Medellín",
  celular_comprador_1: "3003575071",
  celular_comprador_2: "3115678901",
  email_comprador_1: "jcamilovasquezm@gmail.com",
  email_comprador_2: "mflopez@gmail.com",
  inmueble_sera_su_casa: "el inmueble que adquiere",
  tiene_inmueble_afectado: "no",
  afectacion_cumple_ley_258: "no",
  queda_afectado: "no",
  nombre_pareja_o_conyuge: "",
  numero_documento_pareja_o_conyuge: "",
  constitucion_patrimonio_de_familia: "y a favor de sus hijos menores",
  acepta_notificacion_electronica: "si",
  coeficiente_copropiedad: "0.0234",
  derechos_notariales: "1.245.000",
  iva: "236.550",
  aporte_superintendencia: "12.450",
  fondo_nacional_notariado: "6.225",
  consecutivo_hojas_papel_notarial: "Aa117159580 al Aa117159595",
  profesion_u_oficio: "Ingeniero",
  actividad_economica_comprador: "Empleado",
  profesion_u_oficio_comprador_2: "Abogada",
  actividad_economica_comprador_2: "Independiente",
  protocolista: "Tatiana",
};

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
  const [actData, setActData] = useState<Record<string, string>>({});
  const actDataRef = useRef<Record<string, string>>({});
  const demoFillRunIdRef = useRef(0);
  const demoFillTimeoutsRef = useRef<number[]>([]);
  const demoFillRunningRef = useRef(false);
  const demoFillStartedTemplateIdRef = useRef<number | null>(null);
  const actDataReadyRef = useRef(false);

  useEffect(() => {
    void load();
  }, []);

  useEffect(() => {
    actDataReadyRef.current = false;
    setActData(buildActDataFromTemplate(selectedTemplate));
  }, [selectedTemplate]);

  useEffect(() => {
    if (!selectedTemplate) {
      actDataReadyRef.current = false;
      return;
    }
    const templateFields = Array.isArray(selectedTemplate.fields) ? selectedTemplate.fields : [];
    actDataReadyRef.current = templateFields.every((field) => field.field_code in actData);
    actDataRef.current = actData;
  }, [actData, selectedTemplate]);

  function cancelDemoFill(resetStarted = false) {
    demoFillRunIdRef.current += 1;
    demoFillRunningRef.current = false;
    if (resetStarted) {
      demoFillStartedTemplateIdRef.current = null;
    }
    for (const timeoutId of demoFillTimeoutsRef.current) {
      window.clearTimeout(timeoutId);
    }
    demoFillTimeoutsRef.current = [];
  }

  function updateActField(fieldCode: string, value: string, source: "user" | "demo" = "user") {
    if (source === "user") {
      cancelDemoFill();
    }
    setActData((current) => ({ ...current, [fieldCode]: value }));
  }

  function autoFillDemo() {
    if (step !== 2 || !selectedTemplate) {
      return;
    }
    if (demoFillRunningRef.current) {
      return;
    }
    if (demoFillStartedTemplateIdRef.current === selectedTemplate.id) {
      return;
    }
    if (!actDataReadyRef.current) {
      return;
    }

    const currentActData = actDataRef.current;
    const templateFields = Array.isArray(selectedTemplate.fields) ? selectedTemplate.fields : [];
    const hasCurrentTemplateData = templateFields.every((field) => field.field_code in currentActData);
    if (!hasCurrentTemplateData) {
      return;
    }

    const templateFieldCodes = templateFields.map((field) => field.field_code);
    const demoKeys = Object.keys(demoData);
    const fieldCodes = Object.keys(demoData).filter((key) => key in currentActData);
    if (fieldCodes.length === 0) {
      return;
    }

    cancelDemoFill();
    demoFillRunningRef.current = true;
    demoFillStartedTemplateIdRef.current = selectedTemplate.id;
    const runId = demoFillRunIdRef.current;

    const scheduleField = (fieldIndex: number) => {
      if (runId !== demoFillRunIdRef.current) {
        return;
      }
      if (fieldIndex >= fieldCodes.length) {
        return;
      }

      const fieldCode = fieldCodes[fieldIndex];
      const targetValue = demoData[fieldCode] ?? "";
      let typedValue = "";
      let charIndex = 0;

      const scheduleNextField = () => {
        if (runId !== demoFillRunIdRef.current) {
          return;
        }
        if (fieldIndex + 1 >= fieldCodes.length) {
          demoFillRunningRef.current = false;
          return;
        }
        const nextFieldTimer = window.setTimeout(() => scheduleField(fieldIndex + 1), 80);
        demoFillTimeoutsRef.current.push(nextFieldTimer);
      };

      const typeNextChar = () => {
        if (runId !== demoFillRunIdRef.current) {
          return;
        }
        if (charIndex >= targetValue.length) {
          scheduleNextField();
          return;
        }

        typedValue += targetValue[charIndex] ?? "";
        charIndex += 1;
        updateActField(fieldCode, typedValue, "demo");
        const charTimer = window.setTimeout(typeNextChar, 18);
        demoFillTimeoutsRef.current.push(charTimer);
      };

      if (!targetValue) {
        scheduleNextField();
        return;
      }

      const firstCharTimer = window.setTimeout(typeNextChar, 18);
      demoFillTimeoutsRef.current.push(firstCharTimer);
    };

    scheduleField(0);
  }

  useEffect(() => {
    if (step !== 2) {
      cancelDemoFill(true);
      return;
    }

    void autoFillDemo();
    return () => cancelDemoFill();
  }, [step, selectedTemplate]);

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
      setTemplates(safeTemplates);
      setSelectedTemplate(
        safeTemplates[0] ?? null,
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
  const templateFields = useMemo(() => sortByStepOrder(Array.isArray(selectedTemplate?.fields) ? selectedTemplate.fields : []), [selectedTemplate]);
  const showAside = step >= 2;
  const generalManagerFields = useMemo<Array<{ key: "current_owner_user_id" | "protocolist_user_id" | "approver_user_id" | "titular_notary_user_id"; label: string; value: string }>>(() => [
    { key: "current_owner_user_id", label: "Responsable actual", value: generalForm.current_owner_user_id },
    { key: "protocolist_user_id", label: "Protocolista", value: generalForm.protocolist_user_id },
    { key: "approver_user_id", label: "Aprobador", value: generalForm.approver_user_id },
    { key: "titular_notary_user_id", label: "Notario titular", value: generalForm.titular_notary_user_id },
  ], [generalForm.current_owner_user_id, generalForm.protocolist_user_id, generalForm.approver_user_id, generalForm.titular_notary_user_id]);

  function updateGeneralManager(field: "current_owner_user_id" | "protocolist_user_id" | "approver_user_id" | "titular_notary_user_id", value: string) {
    setGeneralForm((current) => ({ ...current, [field]: value }));
    setExpandedGeneralField(null);
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
    return created;
  }

  async function continueStep() {
    setError(null);
    setFeedback(null);
    setIsSaving(true);
    try {
      let activeCase = caseDetail;
      if (step === 0) {
        if (!selectedTemplate) {
          throw new Error("Selecciona una plantilla antes de continuar.");
        }
      }
      if (step === 1 && !activeCase) {
        activeCase = await handleCreateCase();
      }
      if (step === 2 && activeCase) {
        const updated = await saveCaseActData(activeCase.id, { data_json: JSON.stringify(actData) });
        setCaseDetail(updated);
      }
      if (step === 3 && caseDetail) {
        const base = process.env.NEXT_PUBLIC_API_URL ?? "";
        const token = typeof window !== "undefined" ? localStorage.getItem("easypro2_session") : null;
        const response = await fetch(`${base}/api/v1/document-flow/cases/${caseDetail.id}/generate-from-template`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
          body: JSON.stringify({ act_data: actData }),
        });
        if (!response.ok) {
          const text = await response.text();
          throw new Error(text);
        }
        setFeedback("Documento generado correctamente. Puedes descargarlo desde el detalle de la minuta.");
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
              {caseDetail?.internal_case_number ? `Documento / minuta · ${caseDetail.internal_case_number}` : "Documento / minuta"}
            </p>
            <h1 className="mt-3 text-3xl font-semibold tracking-[-0.05em] text-primary">Crear documento desde una plantilla Word</h1>
            <p className="mt-3 max-w-3xl text-base leading-7 text-secondary">
              Escoge una plantilla, diligencia el formulario dinámico que el sistema detecta y genera el Word sin salir de este flujo.
            </p>
          </div>
          {caseDetail ? (
            <Link href={`/dashboard/casos/${caseDetail.id}`} className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white">
              Abrir detalle del documento <ArrowRight className="h-4 w-4" />
            </Link>
          ) : null}
        </div>
      </section>

      <section className="ep-card z-0 rounded-[2rem] p-6">
        <div className="grid gap-3 xl:grid-cols-4">
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
          <div className="ep-card-muted rounded-[1.5rem] px-4 py-4 text-sm text-secondary">
            La plantilla seleccionada define los campos visibles. Si cambias de plantilla, el formulario cambia con ella.
          </div>
          {isLoading ? <div className="ep-card-muted z-0 rounded-[1.5rem] px-4 py-6 text-sm text-secondary">Cargando plantillas, notarías y usuarios...</div> : null}
          {!isLoading && error && templates.length === 0 ? <div className="ep-kpi-critical z-0 rounded-2xl px-4 py-3 text-sm">{error}</div> : null}
          {!isLoading && !error && templates.length === 0 ? <div className="ep-card-muted z-0 rounded-[1.5rem] px-4 py-6 text-sm text-secondary">No hay plantillas activas todavía.</div> : null}

          {!isLoading && templates.length > 0 ? (
            <>
              {step === 0 ? (
                <div className="space-y-6">
                  <h2 className="text-2xl font-semibold text-primary">1. Seleccionar plantilla</h2>
                  <div className="grid gap-4 lg:grid-cols-2">
                    {templates.map((item) => (
                      <button
                        key={item.id}
                        type="button"
                        onClick={() => setSelectedTemplate(item)}
                        className={`rounded-[1.5rem] border p-5 text-left transition-colors ${
                          selectedTemplate?.id === item.id
                            ? "border-primary/40 bg-primary/8"
                            : "border-[var(--line)] hover:border-primary/20"
                        }`}
                      >
                        <p className="text-lg font-semibold text-primary">{item.name}</p>
                        <p className="mt-1 text-sm text-secondary">Documento / minuta: {item.document_type}</p>
                        {item.description && (
                          <p className="mt-2 text-xs text-secondary">{item.description}</p>
                        )}
                        <p className="mt-3 text-xs text-secondary">
                          Campos detectados: {item.fields?.length ?? 0} · Intervinientes: {item.required_roles?.length ?? 0}
                        </p>
                        <p className="mt-2 text-xs font-semibold uppercase tracking-[0.18em] text-primary">Usar esta plantilla para crear documento</p>
                      </button>
                    ))}
                  </div>
                </div>
              ) : null}

              {step === 1 ? (
                <div className="space-y-5">
                  <h2 className="text-2xl font-semibold text-primary">2. Documento / minuta</h2>
                  <p className="text-sm text-secondary">
                    Define la notaría y quién trabajará el documento. El formulario de abajo sigue siendo dinámico, no está quemado por tipo documental.
                  </p>
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
                    Requiere revisión del cliente
                  </label>
                </div>
              ) : null}

              {step === 2 ? (
                <div className="space-y-5">
                  <h2 className="text-2xl font-semibold text-primary">3. Diligenciar</h2>
                  <p className="text-sm text-secondary">
                    Completa solo los campos detectados por la plantilla seleccionada.
                  </p>
                  {(() => {
                    const templateFields = sortByStepOrder(Array.isArray(selectedTemplate?.fields) ? selectedTemplate.fields : []);

                    if (templateFields.length === 0) {
                      return <p>La plantilla no tiene campos detectados todavía.</p>;
                    }

                    return (
                      <div className="grid grid-cols-1 gap-4">
                        {templateFields.map((field) => {
                          const label = `${field.label || field.field_code}${field.is_required ? " *" : ""}`;
                          const value = actData[field.field_code] ?? "";
                          const options = parseTemplateFieldOptions(field.options_json);

                          if (field.field_type === "select" && options.length > 0) {
                            return (
                              <div key={field.field_code} className="w-full">
                                <SearchableSelect
                                  label={label}
                                  value={value}
                                  options={options}
                                  onChange={(nextValue) => updateActField(field.field_code, nextValue)}
                                />
                              </div>
                            );
                          }

                          if (field.field_type === "textarea") {
                            return (
                              <div key={field.field_code} className="grid gap-2 text-sm font-medium text-primary">
                                <span>{label}</span>
                                <textarea
                                  value={value}
                                  rows={3}
                                  onChange={(event) => updateActField(field.field_code, event.target.value)}
                                  placeholder={field.placeholder_key || ""}
                                  className="ep-textarea"
                                />
                              </div>
                            );
                          }

                          return (
                            <div key={field.field_code} className="w-full">
                              <ValidatedInput
                                label={label}
                                type={field.field_type === "number" || field.field_type === "currency" ? "number" : field.field_type === "date" ? "date" : "text"}
                                value={value}
                                placeholder={field.placeholder_key || ""}
                                onChange={(nextValue) => updateActField(field.field_code, nextValue)}
                              />
                            </div>
                          );
                        })}
                      </div>
                    );
                  })()}
                </div>
              ) : null}

              {step === 3 ? (
                <div className="space-y-5">
                  <h2 className="text-2xl font-semibold text-primary">4. Revisar y generar Word</h2>
                  <div className="ep-card-soft rounded-[1.5rem] p-5 space-y-3">
                    <p className="text-sm font-semibold text-primary">Plantilla seleccionada</p>
                    <p className="text-sm text-secondary">
                      {selectedTemplate?.name ?? "Sin plantilla"}
                    </p>
                    <p className="mt-3 text-sm font-semibold text-primary">Documento / minuta</p>
                    <p className="text-sm text-secondary">
                      {selectedTemplate?.document_type ?? "Sin definir"}
                    </p>
                    <p className="mt-3 text-sm font-semibold text-primary">Campos detectados</p>
                    <p className="text-sm text-secondary">
                      {selectedTemplate?.fields?.length ?? 0} campos configurados
                    </p>
                    <p className="mt-3 text-sm font-semibold text-primary">Número interno</p>
                    <p className="text-sm text-secondary">{caseDetail?.internal_case_number ?? ""}</p>
                  </div>
                  <div className="ep-card-muted rounded-[1.5rem] px-4 py-4 text-sm text-secondary">
                    Todo listo. Al continuar, el sistema generará el Word y podrás abrir el detalle para descargarlo o seguir con la revisión.
                  </div>
                </div>
              ) : null}
            </>
          ) : null}

          {error && !(isLoading && templates.length === 0) ? <div className="ep-kpi-critical rounded-2xl px-4 py-3 text-sm">{error}</div> : null}
          {feedback ? <div className="ep-kpi-success rounded-2xl px-4 py-3 text-sm">{feedback}</div> : null}
          {!isLoading && templates.length > 0 && step < 3 ? (
            <button type="button" onClick={() => void continueStep()} disabled={isSaving} className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white disabled:opacity-60">
              Continuar <ArrowRight className="h-4 w-4" />
            </button>
          ) : null}
          {!isLoading && templates.length > 0 && step === 3 ? (
            <button type="button" onClick={() => void continueStep()} disabled={isSaving} className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white disabled:opacity-60">
              Generar Word <ArrowRight className="h-4 w-4" />
            </button>
          ) : null}
        </div>

        {showAside ? (
          <aside className="space-y-4">
            <div className="ep-card z-0 rounded-[1.8rem] p-5">
              <p className="text-xs uppercase tracking-[0.2em] text-secondary">Documento / minuta activa</p>
              <p className="mt-2 text-lg font-semibold text-primary">{caseDetail?.internal_case_number || "Aún no creado"}</p>
              <p className="mt-3 text-sm text-secondary">Plantilla: {selectedTemplate?.name || "Sin selección"}</p>
              <p className="mt-2 text-sm text-secondary">Estado: {caseDetail?.current_state || "borrador"}</p>
              <p className="mt-2 text-sm text-secondary">Escritura oficial: {caseDetail?.official_deed_number || "Pendiente de aprobación"}</p>
            </div>
            <div className="ep-card z-0 rounded-[1.8rem] p-5">
              <p className="text-xs uppercase tracking-[0.2em] text-secondary">Flujo de trabajo</p>
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

