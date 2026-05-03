"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { ArrowLeft, Download, Upload } from "lucide-react";
import { addInternalNote, approveDocumentCase, getDocumentCase, uploadFinalSigned, type DocumentFlowCase } from "@/lib/document-flow";
import { getCurrentUser, type CurrentUser } from "@/lib/api";
import { formatDateTime } from "@/lib/datetime";

const baseTabs = ["Minuta", "Diligenciamiento", "Observaciones"] as const;
const superAdminTabs = ["Minuta", "Diligenciamiento", "Observaciones", "Historial técnico"] as const;

const stateLabels: Record<string, string> = {
  borrador: "Borrador",
  en_diligenciamiento: "En diligenciamiento",
  revision_cliente: "Revisión del cliente",
  ajustes_solicitados: "Ajustes solicitados",
  revision_aprobador: "Revisión del aprobador",
  devuelto_aprobador: "Devuelto por aprobador",
  revision_notario: "Revisión del notario",
  rechazado_notario: "Rechazado por notario",
  aprobado_notario: "Aprobado por notario",
  generado: "Generado",
  firmado_cargado: "Firmado y cargado",
  cerrado: "Cerrado",
};

function pretty(value: string) {
  return formatDateTime(value);
}

function prettyState(value: string | null | undefined) {
  if (!value) return "Sin estado";
  return stateLabels[value] ?? value.replace(/_/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());
}

function normalizeText(value: string) {
  return value.trim().toLowerCase();
}

function collectRoleCodes(user: CurrentUser | null) {
  return Array.from(new Set([...(user?.role_codes ?? []), ...(user?.roles ?? [])].map((role) => role.toLowerCase())));
}

function prettyEventType(value: string | null | undefined) {
  if (!value) return "Evento";
  const normalized = normalizeText(value);
  const labels: Record<string, string> = {
    case_created: "Minuta creada",
    act_data_saved: "Datos diligenciados actualizados",
    draft_generated: "Word generado",
    approved: "Minuta aprobada",
    internal_note_added: "Observación agregada",
    final_signed_uploaded: "Minuta firmada cargada",
  };
  return labels[normalized] ?? value.replace(/_/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());
}

function safeJson(value: string | null | undefined) {
  if (!value) return null;
  try {
    return JSON.parse(value) as unknown;
  } catch {
    return null;
  }
}

function stringifyTechnicalValue(value: unknown) {
  if (value == null) {
    return "";
  }
  if (typeof value === "string") {
    return value;
  }
  if (typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
}

function parseActData(caseDetail: DocumentFlowCase | null) {
  const raw = caseDetail?.act_data?.data_json;
  if (!raw) return {} as Record<string, string>;
  try {
    const parsed = JSON.parse(raw) as Record<string, unknown>;
    return Object.fromEntries(Object.entries(parsed ?? {}).map(([key, value]) => [key, String(value ?? "")]));
  } catch {
    return {} as Record<string, string>;
  }
}

async function generateFromTemplate(caseId: number, actData: Record<string, string>) {
  const token = localStorage.getItem("easypro2_session");
  const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? "";
  const response = await fetch(`${baseUrl}/api/v1/document-flow/cases/${caseId}/generate-from-template`, {
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
  return response.json() as Promise<{ status: string; message: string; case_id: number; docx_path: string }>;
}

export function CaseDetailWorkspace({ caseId, initialTab }: { caseId: number; initialTab?: string }) {
  const [caseDetail, setCaseDetail] = useState<DocumentFlowCase | null>(null);
  const [tab, setTab] = useState("Minuta");
  const [finalFile, setFinalFile] = useState<File | null>(null);
  const [approvalComment, setApprovalComment] = useState("");
  const [internalNote, setInternalNote] = useState("");
  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isApproving, setIsApproving] = useState(false);
  const [isSavingNote, setIsSavingNote] = useState(false);

  useEffect(() => {
    if (!Number.isFinite(caseId) || caseId <= 0) {
      setError("El identificador de la minuta no es válido.");
      setIsLoading(false);
      return;
    }
    void load();
  }, [caseId]);

  useEffect(() => {
    if (initialTab === "datos") {
      setTab("Diligenciamiento");
    } else if (initialTab === "trazabilidad") {
      setTab(collectRoleCodes(currentUser).includes("super_admin") ? "Historial técnico" : "Observaciones");
    } else if (initialTab === "observaciones") {
      setTab("Observaciones");
    } else if (initialTab === "historial-tecnico") {
      setTab("Historial técnico");
    } else {
      setTab("Minuta");
    }
  }, [currentUser, initialTab]);

  async function load() {
    setIsLoading(true);
    setError(null);
    try {
      const [data, user] = await Promise.all([getDocumentCase(caseId), getCurrentUser()]);
      setCaseDetail(data);
      setCurrentUser(user);
    } catch (issue) {
      setCaseDetail(null);
      setCurrentUser(null);
      setError(issue instanceof Error ? issue.message : "No fue posible cargar la minuta.");
    } finally {
      setIsLoading(false);
    }
  }

  const actData = parseActData(caseDetail);
  const documents = Array.isArray(caseDetail?.documents) ? caseDetail.documents : [];
  const participants = Array.isArray(caseDetail?.participants) ? caseDetail.participants : [];
  const workflowEvents = Array.isArray(caseDetail?.workflow_events) ? caseDetail.workflow_events : [];
  const internalNotes = Array.isArray(caseDetail?.internal_notes) ? caseDetail.internal_notes : [];
  const clientComments = Array.isArray(caseDetail?.client_comments) ? caseDetail.client_comments : [];
  const normalizedRoleCodes = useMemo(() => collectRoleCodes(currentUser), [currentUser]);
  const isSuperAdmin = normalizedRoleCodes.includes("super_admin");
  const isProtocolist = normalizedRoleCodes.includes("protocolist");
  const isApprover = normalizedRoleCodes.includes("approver");
  const isNotary = normalizedRoleCodes.includes("notary") || normalizedRoleCodes.includes("titular_notary") || normalizedRoleCodes.includes("substitute_notary");
  const isAdminNotary = normalizedRoleCodes.includes("admin_notary");
  const canSeeTechnicalHistory = isSuperAdmin;
  const tabs = useMemo(() => (canSeeTechnicalHistory ? superAdminTabs : baseTabs), [canSeeTechnicalHistory]);
  const draftDocument = documents.find((item) => item.category === "draft") ?? null;
  const latestWordVersion = draftDocument?.versions?.[0] ?? null;
  const approvalRoleCode = resolveApprovalRole();
  const canApprove = Boolean(approvalRoleCode);

  useEffect(() => {
    if (!(tabs as readonly string[]).includes(tab)) {
      setTab(tabs[0]);
    }
  }, [tab, tabs]);

  async function fileToBase64(file: File) {
    return new Promise<string>((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(String(reader.result).split(",")[1] ?? "");
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }

  async function handleGenerateDocument() {
    setError(null);
    setFeedback(null);
    setIsGenerating(true);
    try {
      const result = await generateFromTemplate(caseId, actData);
      await load();
      setFeedback(result.message || "Minuta generada correctamente.");
    } catch (issue) {
      setError(issue instanceof Error ? issue.message : "No fue posible generar la minuta.");
    } finally {
      setIsGenerating(false);
    }
  }

  async function handleFinalUpload() {
    if (!finalFile) {
      setError("Selecciona un archivo antes de cargar la minuta definitiva.");
      return;
    }
    setError(null);
    setFeedback(null);
    setIsUploading(true);
    try {
      await uploadFinalSigned(caseId, finalFile.name, await fileToBase64(finalFile), "Minuta definitiva cargada desde detalle.");
      await load();
      setFeedback("Minuta definitiva cargada.");
    } catch (issue) {
      setError(issue instanceof Error ? issue.message : "No fue posible cargar la minuta definitiva.");
    } finally {
      setIsUploading(false);
    }
  }

  async function handleDownload(downloadUrl: string, filename: string) {
    try {
      if (downloadUrl.startsWith("https://")) {
        const a = document.createElement("a");
        a.href = downloadUrl;
        a.download = filename;
        a.target = "_blank";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        return;
      }

      const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8001";
      const { getToken } = await import("@/lib/auth");
      const token = getToken();
      const res = await fetch(`${API_URL}${downloadUrl}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (!res.ok) throw new Error("No fue posible descargar el archivo.");
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (issue) {
      setError(issue instanceof Error ? issue.message : "Error al descargar.");
    }
  }

  function resolveApprovalRole() {
    if (!caseDetail || !currentUser) {
      return null;
    }

    if (isSuperAdmin && !isApprover && !isNotary && !isAdminNotary) {
      return null;
    }

    if (isApprover || caseDetail.approver_user_id === currentUser.id) {
      return "approver";
    }

    if (isNotary || isAdminNotary || caseDetail.titular_notary_user_id === currentUser.id) {
      return "titular_notary";
    }

    if (isAdminNotary || caseDetail.substitute_notary_user_id === currentUser.id) {
      return "substitute_notary";
    }

    return null;
  }

  async function handleApprove() {
    if (!approvalRoleCode) {
      setError("No tienes un rol disponible para aprobar esta minuta.");
      return;
    }
    setError(null);
    setFeedback(null);
    setIsApproving(true);
    try {
      await approveDocumentCase(caseId, approvalRoleCode, approvalComment.trim());
      setApprovalComment("");
      await load();
      setFeedback("Aprobación registrada.");
    } catch (issue) {
      setError(issue instanceof Error ? issue.message : "No fue posible registrar la aprobación.");
    } finally {
      setIsApproving(false);
    }
  }

  async function handleSaveInternalNote() {
    const note = internalNote.trim();
    if (!note) {
      setError("Escribe una observación interna antes de guardar.");
      return;
    }
    setError(null);
    setFeedback(null);
    setIsSavingNote(true);
    try {
      await addInternalNote(caseId, note);
      setInternalNote("");
      await load();
      setFeedback("Observación interna guardada.");
    } catch (issue) {
      setError(issue instanceof Error ? issue.message : "No fue posible guardar la observación interna.");
    } finally {
      setIsSavingNote(false);
    }
  }

  async function handleRequestAdjustments() {
    const note = internalNote.trim();
    if (!note) {
      setError("Escribe una observación antes de solicitar ajustes.");
      return;
    }
    setError(null);
    setFeedback(null);
    setIsSavingNote(true);
    try {
      await addInternalNote(caseId, note);
      setInternalNote("");
      await load();
      setFeedback("Solicitud de ajustes registrada. La minuta vuelve a corrección manual.");
    } catch (issue) {
      setError(issue instanceof Error ? issue.message : "No fue posible registrar la solicitud de ajustes.");
    } finally {
      setIsSavingNote(false);
    }
  }

  function participantDisplay(item: (typeof participants)[number]) {
    const person = item.person;
    return {
      role: item.role_label || "Interviniente",
      name: person?.full_name || "Sin nombre",
      document: [person?.document_type || "DOC", person?.document_number || "Sin número"].join(" "),
      meta: [person?.nationality || "Sin nacionalidad", person?.marital_status || "Sin estado civil"].join(" · "),
      extra: [person?.profession || "Sin profesión", person?.municipality || "Sin municipio"].join(" · "),
      contact: [person?.address || "Sin dirección", person?.phone || "Sin teléfono"].join(" · "),
    };
  }

  function renderActivitySummary(item: (typeof workflowEvents)[number]) {
    return (
      <div key={item.id} className="ep-card-soft rounded-[1.5rem] p-4">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-sm font-semibold text-primary">{prettyEventType(item.event_type)}</p>
          <span className="text-xs text-secondary">{pretty(item.created_at)}</span>
        </div>
        <p className="mt-2 text-sm text-secondary">Actor: {item.actor_user_name || "Sistema"}</p>
        {item.comment ? <p className="mt-2 text-sm text-secondary">{item.comment}</p> : null}
      </div>
    );
  }

  function renderTechnicalEvent(item: (typeof workflowEvents)[number]) {
    return (
      <div key={item.id} className="ep-card-soft rounded-[1.5rem] p-4">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm font-semibold text-primary">{prettyEventType(item.event_type)}</p>
            <p className="text-xs text-secondary">
              Actor: {item.actor_user_name || "Sistema"}
              {item.actor_role_code ? ` · ${item.actor_role_code}` : ""}
            </p>
          </div>
          <span className="text-xs text-secondary">{pretty(item.created_at)}</span>
        </div>
        <div className="mt-3 grid gap-3 lg:grid-cols-2">
          <div className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-3">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-secondary">Detalle técnico</p>
            <div className="mt-2 space-y-2 text-xs text-secondary">
              {item.from_state ? <p>Desde: {item.from_state}</p> : null}
              {item.to_state ? <p>Hacia: {item.to_state}</p> : null}
              {item.field_name ? <p>Campo: {item.field_name}</p> : null}
              {item.approved_version_id ? <p>Versión aprobada: {item.approved_version_id}</p> : null}
              {item.comment ? <p>Comentario: {item.comment}</p> : null}
            </div>
          </div>
          <div className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-3">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-secondary">Valores técnicos</p>
            <div className="mt-2 space-y-2 text-xs text-secondary">
              {item.old_value ? <pre className="whitespace-pre-wrap break-words">{stringifyTechnicalValue(item.old_value)}</pre> : <p>Sin old_value</p>}
              {item.new_value ? <pre className="whitespace-pre-wrap break-words">{stringifyTechnicalValue(item.new_value)}</pre> : <p>Sin new_value</p>}
            </div>
          </div>
        </div>
        {item.metadata_json ? (
          <div className="mt-3 rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-3">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-secondary">metadata_json</p>
            <pre className="mt-2 whitespace-pre-wrap break-words text-xs text-secondary">{item.metadata_json}</pre>
          </div>
        ) : null}
      </div>
    );
  }

  if (isLoading) {
    return <div className="ep-card rounded-[2rem] p-6 text-secondary">Cargando minuta...</div>;
  }

  if (error && !caseDetail) {
    return <div className="ep-kpi-critical rounded-[2rem] px-6 py-5 text-sm">{error}</div>;
  }

  if (!caseDetail) {
    return <div className="ep-card rounded-[2rem] p-6 text-secondary">Sin datos de la minuta todavía.</div>;
  }

  return (
    <div className="space-y-6">
      <section className="ep-card rounded-[2rem] p-6">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <Link href="/dashboard/casos" className="inline-flex items-center gap-2 text-sm font-semibold text-primary">
              <ArrowLeft className="h-4 w-4" />
              Volver a la bandeja
            </Link>
            <p className="mt-4 text-sm font-semibold uppercase tracking-[0.22em] text-accent">Detalle de la minuta</p>
            <h1 className="mt-2 text-3xl font-semibold tracking-[-0.05em] text-primary">{caseDetail.act_type || "Minuta"}</h1>
            <p className="mt-3 text-base text-secondary">
              {caseDetail.internal_case_number || "Sin número interno"} · {caseDetail.notary_label || "Sin notaría"}
            </p>
            <span className="mt-4 inline-flex rounded-full bg-primary/10 px-3 py-1 text-sm font-semibold text-primary">
              {prettyState(caseDetail.current_state)}
            </span>
          </div>
          <div className="grid gap-3 sm:grid-cols-2 lg:w-[430px]">
            <div className="ep-card-muted rounded-[1.5rem] p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-secondary">Escritura oficial</p>
              <p className="mt-2 text-lg font-semibold text-primary">{caseDetail.official_deed_number || "Pendiente"}</p>
            </div>
            <div className="ep-card-muted rounded-[1.5rem] p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-secondary">Responsable actual</p>
              <p className="mt-2 text-lg font-semibold text-primary">{caseDetail.current_owner_user_name || "Sin asignar"}</p>
            </div>
            <div className="ep-card-muted rounded-[1.5rem] p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-secondary">Borrador actual</p>
              <p className="mt-2 text-lg font-semibold text-primary">
                {draftDocument?.current_version_number ? `v${draftDocument.current_version_number}` : "Sin generar"}
              </p>
            </div>
            <div className="ep-card-muted rounded-[1.5rem] p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-secondary">Plantilla</p>
              <p className="mt-2 text-lg font-semibold text-primary">{caseDetail.template_name || "Sin plantilla"}</p>
            </div>
          </div>
        </div>
      </section>

      <section className="ep-card rounded-[2rem] p-6">
        <div className="flex flex-wrap gap-2">
          {tabs.map((item) => (
            <button
              key={item}
              type="button"
              onClick={() => setTab(item)}
              className={`rounded-full px-4 py-2 text-sm font-semibold ${tab === item ? "bg-primary text-white" : "ep-pill text-secondary"}`}
            >
              {item}
            </button>
          ))}
        </div>

        <div className="mt-6">
          {tab === "Minuta" ? (
            <div className="space-y-5">
              <div className="ep-card-muted rounded-[1.5rem] px-4 py-4 text-sm text-secondary">
                {caseDetail.final_signed_uploaded
                  ? "La minuta final ya está cargada."
                  : caseDetail.current_state === "borrador"
                    ? "Falta diligenciar el formulario para generar el Word de la minuta."
                    : caseDetail.current_state === "revision_cliente"
                      ? "La minuta está esperando revisión del cliente."
                      : caseDetail.current_state === "revision_aprobador" || caseDetail.current_state === "revision_notario"
                        ? "La minuta está lista para revisión y decisión."
                        : "Continúa el flujo desde aquí."}
              </div>
              <section className="space-y-4 rounded-[1.5rem] border border-[var(--line)] bg-[var(--panel-soft)] p-4">
                <div className="space-y-2">
                  <p className="text-sm font-semibold text-primary">Revisión manual</p>
                  <p className="text-sm text-secondary">
                    Revisa el Word generado, corrige desde diligenciamiento y deja observaciones manuales según tu rol.
                  </p>
                  <p className="text-sm text-secondary">
                    Si necesitas solicitar ajustes, usa la pestaña Observaciones para dejar la nota manual de revisión.
                  </p>
                </div>
                <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
                  <div className="ep-card-soft rounded-[1.25rem] p-4">
                    <p className="text-xs uppercase tracking-[0.18em] text-secondary">Estado actual</p>
                    <p className="mt-2 text-sm font-semibold text-primary">{prettyState(caseDetail.current_state)}</p>
                  </div>
                  <div className="ep-card-soft rounded-[1.25rem] p-4">
                    <p className="text-xs uppercase tracking-[0.18em] text-secondary">Responsable actual</p>
                    <p className="mt-2 text-sm font-semibold text-primary">{caseDetail.current_owner_user_name || "Sin asignar"}</p>
                  </div>
                  <div className="ep-card-soft rounded-[1.25rem] p-4">
                    <p className="text-xs uppercase tracking-[0.18em] text-secondary">Protocolista</p>
                    <p className="mt-2 text-sm font-semibold text-primary">{caseDetail.protocolist_user_name || "Sin asignar"}</p>
                  </div>
                  <div className="ep-card-soft rounded-[1.25rem] p-4">
                    <p className="text-xs uppercase tracking-[0.18em] text-secondary">Aprobador</p>
                    <p className="mt-2 text-sm font-semibold text-primary">{caseDetail.approver_user_name || "Sin asignar"}</p>
                  </div>
                  <div className="ep-card-soft rounded-[1.25rem] p-4">
                    <p className="text-xs uppercase tracking-[0.18em] text-secondary">Última actualización</p>
                    <p className="mt-2 text-sm font-semibold text-primary">{pretty(caseDetail.updated_at)}</p>
                  </div>
                  <div className="ep-card-soft rounded-[1.25rem] p-4">
                    <p className="text-xs uppercase tracking-[0.18em] text-secondary">Word disponible</p>
                    <p className="mt-2 text-sm font-semibold text-primary">{latestWordVersion ? `Si, v${latestWordVersion.version_number}` : "No"}</p>
                  </div>
                </div>
                <div className="hidden">
                  <p className="text-sm font-semibold text-primary">Agregar observación interna</p>
                  <textarea
                    value={internalNote}
                    onChange={(event) => setInternalNote(event.target.value)}
                    rows={3}
                    placeholder="Escribe aquí la observación interna de revisión"
                    className="ep-textarea rounded-2xl px-4 py-3"
                  />
                  <button
                    type="button"
                    onClick={() => void handleSaveInternalNote()}
                    disabled={isSavingNote}
                    className="inline-flex items-center gap-2 rounded-2xl border border-[var(--line)] px-5 py-3 text-sm font-semibold text-primary disabled:opacity-60"
                  >
                    {isSavingNote ? "Guardando..." : "Guardar observación"}
                  </button>
                </div>
                <div className="grid gap-4 lg:grid-cols-2">
                  <div className="space-y-3">
                    <p className="text-sm font-semibold text-primary">Observaciones internas existentes</p>
                    {internalNotes.length > 0 ? (
                      <div className="space-y-2">
                        {internalNotes.map((item) => (
                          <div key={item.id} className="ep-card-soft rounded-[1.25rem] p-4">
                            <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
                              <p className="text-sm font-semibold text-primary">{item.created_by_user_name || "Sistema"}</p>
                              <span className="text-xs text-secondary">{pretty(item.created_at)}</span>
                            </div>
                            <p className="mt-2 text-sm text-secondary">{item.note || item.comment || "Sin texto"}</p>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="ep-card-muted rounded-[1.5rem] px-4 py-6 text-sm text-secondary">Sin observaciones internas todavía.</div>
                    )}
                  </div>
                  <div className="space-y-3">
                    <p className="text-sm font-semibold text-primary">Comentarios registrados</p>
                    {clientComments.length > 0 ? (
                      <div className="space-y-2">
                        {clientComments.map((item) => (
                          <div key={item.id} className="ep-card-soft rounded-[1.25rem] p-4">
                            <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
                              <p className="text-sm font-semibold text-primary">{item.created_by_user_name || "Cliente"}</p>
                              <span className="text-xs text-secondary">{pretty(item.created_at)}</span>
                            </div>
                            <p className="mt-2 text-sm text-secondary">{item.comment || item.note || "Sin texto"}</p>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="ep-card-muted rounded-[1.5rem] px-4 py-6 text-sm text-secondary">Sin comentarios registrados todavía.</div>
                    )}
                  </div>
                </div>
              {canSeeTechnicalHistory ? (
                <section className="space-y-3 rounded-[1.5rem] border border-[var(--line)] bg-[var(--panel-soft)] p-4">
                  <p className="text-sm font-semibold text-primary">Actividad operativa reciente</p>
                  {workflowEvents.length > 0 ? (
                    <div className="space-y-2">
                      {workflowEvents.slice(0, 8).map((item) => renderActivitySummary(item))}
                    </div>
                  ) : (
                    <div className="ep-card-muted rounded-[1.5rem] px-4 py-6 text-sm text-secondary">Sin actividad operativa todavía.</div>
                  )}
                </section>
              ) : null}
              </section>
              <div className="flex flex-wrap items-center gap-3">
                {isProtocolist || isAdminNotary ? (
                  <button
                    type="button"
                    onClick={() => void handleGenerateDocument()}
                    disabled={isGenerating}
                    className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white disabled:opacity-60"
                  >
                    <Upload className="h-4 w-4" />
                    {isGenerating ? "Generando..." : "Generar Word"}
                  </button>
                ) : null}
                {draftDocument?.versions?.[0] ? (
                  <button
                    type="button"
                    onClick={() => void handleDownload(draftDocument.versions[0].download_url || "", `v${draftDocument.versions[0].version_number}.${draftDocument.versions[0].file_format || "docx"}`)}
                    className="inline-flex items-center gap-2 rounded-2xl border border-[var(--line)] px-5 py-3 text-sm font-semibold text-primary"
                  >
                    <Download className="h-4 w-4" />
                    Descargar Word
                  </button>
                ) : null}
              </div>

              <div className="space-y-3">
                <p className="text-sm font-semibold text-primary">Versiones del borrador</p>
                {draftDocument && Array.isArray(draftDocument.versions) && draftDocument.versions.length > 0 ? (
                  <div className="space-y-2">
                    {draftDocument.versions.map((version) => (
                      <button
                        key={version.id}
                        type="button"
                        onClick={() => void handleDownload(version.download_url || "", `v${version.version_number}.${version.file_format || "docx"}`)}
                        className="flex w-full items-center justify-between rounded-xl border border-[var(--line)] px-4 py-3 text-left hover:bg-[var(--panel)]"
                      >
                        <div>
                          <p className="text-sm font-semibold text-primary">v{version.version_number}</p>
                          <p className="text-xs text-secondary">{pretty(version.created_at)}</p>
                        </div>
                        <span className="inline-flex items-center gap-2 text-sm font-semibold text-primary">
                          <Download className="h-4 w-4" />
                          Descargar
                        </span>
                      </button>
                    ))}
                  </div>
                ) : (
                  <div className="ep-card-muted rounded-[1.5rem] px-4 py-6 text-sm text-secondary">Sin versiones del borrador todavía.</div>
                )}
              </div>

              <div className="space-y-3">
                <p className="text-sm font-semibold text-primary">Minuta PDF final firmada</p>
                <label className="ep-card-muted flex items-center justify-between gap-3 rounded-2xl px-4 py-4 text-sm text-secondary">
                  <span className="inline-flex items-center gap-2">
                    <Upload className="h-4 w-4 text-primary" />
                    Cargar PDF firmado
                  </span>
                  <input type="file" accept=".pdf" onChange={(event) => setFinalFile(event.target.files?.[0] ?? null)} />
                </label>
                <button
                  type="button"
                  onClick={() => void handleFinalUpload()}
                  disabled={!finalFile || isUploading}
                  className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white disabled:opacity-60"
                >
                  <Upload className="h-4 w-4" />
                  {isUploading ? "Cargando..." : "Cargar firmado"}
                </button>
              </div>

              {canApprove ? (
                <div className="space-y-3 rounded-[1.5rem] border border-[var(--line)] bg-[var(--panel-soft)] p-4">
                  <p className="text-sm font-semibold text-primary">Aprobación manual</p>
                  <p className="text-sm text-secondary">
                    Puedes registrar aprobación con comentario. Si el documento requiere más trabajo, deja una nota y solicita ajustes manuales.
                  </p>
                  <textarea
                    value={approvalComment}
                    onChange={(event) => setApprovalComment(event.target.value)}
                    rows={3}
                    placeholder="Comentario de aprobación"
                    className="ep-textarea rounded-2xl px-4 py-3"
                  />
                  <div className="flex flex-wrap gap-3">
                    <button
                      type="button"
                      onClick={() => void handleApprove()}
                      disabled={isApproving}
                      className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white disabled:opacity-60"
                    >
                      {isApproving ? "Registrando..." : "Aprobar minuta"}
                    </button>
                    <button
                      type="button"
                      onClick={() => void handleRequestAdjustments()}
                      disabled={isSavingNote}
                      className="inline-flex items-center gap-2 rounded-2xl border border-[var(--line)] px-5 py-3 text-sm font-semibold text-primary disabled:opacity-60"
                    >
                      {isSavingNote ? "Guardando..." : "Solicitar ajustes"}
                    </button>
                  </div>
                </div>
              ) : null}
            </div>
          ) : null}

          {tab === "Observaciones" ? (
            <div className="space-y-6">
              <section className="space-y-4 rounded-[1.5rem] border border-[var(--line)] bg-[var(--panel-soft)] p-4">
                <div className="space-y-2">
                  <p className="text-sm font-semibold text-primary">Observaciones internas</p>
                  <p className="text-sm text-secondary">Usa este espacio para solicitar ajustes o dejar notas de revisión manual.</p>
                </div>
                <textarea
                  value={internalNote}
                  onChange={(event) => setInternalNote(event.target.value)}
                  rows={4}
                  placeholder="Escribe aquí la observación interna de revisión"
                  className="ep-textarea rounded-2xl px-4 py-3"
                />
                {canApprove ? (
                  <p className="text-sm text-secondary">La observación se guardará como nota interna y dejará la minuta lista para corrección manual.</p>
                ) : null}
                <button
                  type="button"
                  onClick={() => void (canApprove ? handleRequestAdjustments() : handleSaveInternalNote())}
                  disabled={isSavingNote}
                  className={`inline-flex items-center gap-2 rounded-2xl px-5 py-3 text-sm font-semibold disabled:opacity-60 ${canApprove ? "bg-primary text-white" : "border border-[var(--line)] text-primary"}`}
                >
                  {isSavingNote ? "Guardando..." : canApprove ? "Solicitar ajustes" : "Guardar observación"}
                </button>
              </section>

              <div className="grid gap-4 lg:grid-cols-2">
                <div className="space-y-3">
                  <p className="text-sm font-semibold text-primary">Observaciones internas existentes</p>
                  {internalNotes.length > 0 ? (
                    <div className="space-y-2">
                      {internalNotes.map((item) => (
                        <div key={item.id} className="ep-card-soft rounded-[1.25rem] p-4">
                          <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
                            <p className="text-sm font-semibold text-primary">{item.created_by_user_name || "Sistema"}</p>
                            <span className="text-xs text-secondary">{pretty(item.created_at)}</span>
                          </div>
                          <p className="mt-2 text-sm text-secondary">{item.note || item.comment || "Sin texto"}</p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="ep-card-muted rounded-[1.5rem] px-4 py-6 text-sm text-secondary">Sin observaciones internas todavía.</div>
                  )}
                </div>
                <div className="space-y-3">
                  <p className="text-sm font-semibold text-primary">Comentarios registrados</p>
                  {clientComments.length > 0 ? (
                    <div className="space-y-2">
                      {clientComments.map((item) => (
                        <div key={item.id} className="ep-card-soft rounded-[1.25rem] p-4">
                          <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
                            <p className="text-sm font-semibold text-primary">{item.created_by_user_name || "Cliente"}</p>
                            <span className="text-xs text-secondary">{pretty(item.created_at)}</span>
                          </div>
                          <p className="mt-2 text-sm text-secondary">{item.comment || item.note || "Sin texto"}</p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="ep-card-muted rounded-[1.5rem] px-4 py-6 text-sm text-secondary">Sin comentarios registrados todavía.</div>
                  )}
                </div>
              </div>

              {canSeeTechnicalHistory ? (
                <section className="space-y-3 rounded-[1.5rem] border border-[var(--line)] bg-[var(--panel-soft)] p-4">
                  <p className="text-sm font-semibold text-primary">Actividad operativa reciente</p>
                  {workflowEvents.length > 0 ? (
                    <div className="space-y-2">
                      {workflowEvents.slice(0, 8).map((item) => renderActivitySummary(item))}
                    </div>
                  ) : (
                    <div className="ep-card-muted rounded-[1.5rem] px-4 py-6 text-sm text-secondary">Sin actividad operativa todavía.</div>
                  )}
                </section>
              ) : null}
            </div>
          ) : null}

          {tab === "Historial técnico" ? (
            <div className="space-y-4">
              <section className="space-y-3 rounded-[1.5rem] border border-[var(--line)] bg-[var(--panel-soft)] p-4">
                <p className="text-sm font-semibold text-primary">Contexto técnico de la minuta</p>
                <div className="grid gap-3 lg:grid-cols-2">
                  <div className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-3">
                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-secondary">metadata_json</p>
                    <pre className="mt-2 whitespace-pre-wrap break-words text-xs text-secondary">{stringifyTechnicalValue(safeJson(caseDetail.metadata_json) ?? caseDetail.metadata_json)}</pre>
                  </div>
                  <div className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-3">
                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-secondary">data_json</p>
                    <pre className="mt-2 whitespace-pre-wrap break-words text-xs text-secondary">{stringifyTechnicalValue(safeJson(caseDetail.act_data?.data_json) ?? caseDetail.act_data?.data_json ?? "{}")}</pre>
                  </div>
                </div>
                <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
                  <div className="ep-card-soft rounded-[1.25rem] p-4">
                    <p className="text-xs uppercase tracking-[0.18em] text-secondary">Aprobado por</p>
                    <p className="mt-2 text-sm font-semibold text-primary">{caseDetail.approved_by_user_name || "Sin aprobar"}</p>
                  </div>
                  <div className="ep-card-soft rounded-[1.25rem] p-4">
                    <p className="text-xs uppercase tracking-[0.18em] text-secondary">Rol de aprobación</p>
                    <p className="mt-2 text-sm font-semibold text-primary">{caseDetail.approved_by_role_code || "Sin rol"}</p>
                  </div>
                  <div className="ep-card-soft rounded-[1.25rem] p-4">
                    <p className="text-xs uppercase tracking-[0.18em] text-secondary">Versión aprobada</p>
                    <p className="mt-2 text-sm font-semibold text-primary">{caseDetail.approved_document_version_id ?? "Sin versión"}</p>
                  </div>
                  <div className="ep-card-soft rounded-[1.25rem] p-4">
                    <p className="text-xs uppercase tracking-[0.18em] text-secondary">Firmado cargado</p>
                    <p className="mt-2 text-sm font-semibold text-primary">{caseDetail.final_signed_uploaded ? "Sí" : "No"}</p>
                  </div>
                </div>
              </section>
              <section className="space-y-3 rounded-[1.5rem] border border-[var(--line)] bg-[var(--panel-soft)] p-4">
                <p className="text-sm font-semibold text-primary">Eventos de trazabilidad</p>
                {workflowEvents.length > 0 ? (
                  <div className="space-y-2">
                    {workflowEvents.map((item) => renderTechnicalEvent(item))}
                  </div>
                ) : (
                  <div className="ep-card-muted rounded-[1.5rem] px-4 py-6 text-sm text-secondary">Sin historial técnico todavía.</div>
                )}
              </section>
            </div>
          ) : null}

          {tab === "Diligenciamiento" ? (
            <div className="space-y-6">
              <div className="grid gap-4 lg:grid-cols-2">
                {Object.entries(actData).length > 0 ? (
                  Object.entries(actData).map(([key, value]) => (
                    <div key={key} className="ep-card-soft rounded-[1.5rem] p-4">
                      <p className="text-xs uppercase tracking-[0.18em] text-secondary">{key}</p>
                      <p className="mt-2 text-sm font-semibold text-primary">{value || "Sin dato"}</p>
                    </div>
                  ))
                ) : (
                  <div className="ep-card-muted rounded-[1.5rem] px-4 py-6 text-sm text-secondary">Sin datos del diligenciamiento todavía.</div>
                )}
              </div>

              <div className="space-y-3">
                <p className="text-sm font-semibold text-primary">Intervinientes</p>
                {participants.length > 0 ? (
                  <div className="grid gap-4 lg:grid-cols-2">
                    {participants.map((item) => {
                      const summary = participantDisplay(item);
                      return (
                        <div key={item.id} className="ep-card-soft rounded-[1.5rem] p-5">
                          <div className="flex items-center justify-between gap-3">
                            <p className="text-sm font-semibold text-primary">{summary.role}</p>
                            <span className="ep-pill rounded-full px-3 py-1 text-xs text-secondary">{summary.document}</span>
                          </div>
                          <p className="mt-3 text-lg font-semibold text-primary">{summary.name}</p>
                          <p className="mt-2 text-sm text-secondary">{summary.meta}</p>
                          <p className="mt-2 text-sm text-secondary">{summary.extra}</p>
                          <p className="mt-2 text-sm text-secondary">{summary.contact}</p>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <div className="ep-card-muted rounded-[1.5rem] px-4 py-6 text-sm text-secondary">Sin intervinientes todavía.</div>
                )}
              </div>
            </div>
          ) : null}

          {tab === "__legacy_observaciones__" ? (
            <div className="space-y-3">
              {workflowEvents.length > 0 ? (
                workflowEvents.map((item) => (
                  <div key={item.id} className="ep-card-soft rounded-[1.5rem] p-4">
                    <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                      <p className="text-sm font-semibold text-primary">{item.event_type || "evento"}</p>
                      <span className="text-xs text-secondary">{pretty(item.created_at)}</span>
                    </div>
                    <p className="mt-2 text-sm text-secondary">
                      Actor: {item.actor_user_name || "Sistema"}
                      {item.actor_role_code ? ` · ${item.actor_role_code}` : ""}
                    </p>
                    {item.comment ? <p className="mt-2 text-sm text-secondary">{item.comment}</p> : null}
                    {item.new_value ? <p className="mt-2 text-sm text-secondary">Nuevo valor: {item.new_value}</p> : null}
                  </div>
                ))
              ) : (
                <div className="ep-card-muted rounded-[1.5rem] px-4 py-6 text-sm text-secondary">Sin historial todavía.</div>
              )}
            </div>
          ) : null}
        </div>

        {feedback ? <div className="ep-kpi-success mt-6 rounded-2xl px-4 py-3 text-sm">{feedback}</div> : null}
        {error ? <div className="ep-kpi-critical mt-6 rounded-2xl px-4 py-3 text-sm">{error}</div> : null}
      </section>
    </div>
  );
}
