"use client";

import Link from "next/link";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { ArrowLeft, Download, FileSignature, MessageSquareText, NotebookTabs, Upload } from "lucide-react";
import { addClientComment, addInternalNote, exportDocumentCase, getDocumentCase, uploadFinalSigned, type DocumentFlowCase } from "@/lib/document-flow";
import { formatDateTime } from "@/lib/datetime";

const flowSteps = [
  "borrador",
  "en_diligenciamiento",
  "revision_cliente",
  "ajustes_solicitados",
  "revision_aprobador",
  "devuelto_aprobador",
  "revision_notario",
  "rechazado_notario",
  "aprobado_notario",
  "generado",
  "firmado_cargado",
  "cerrado",
];
const tabs = ["Resumen", "Intervinientes", "Datos del acto", "Comentarios del cliente", "Observaciones internas", "Documentos", "Trazabilidad"] as const;

function pretty(value: string) {
  return formatDateTime(value);
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

export function CaseDetailWorkspace({ caseId }: { caseId: number }) {
  const [caseDetail, setCaseDetail] = useState<DocumentFlowCase | null>(null);
  const [tab, setTab] = useState<(typeof tabs)[number]>("Resumen");
  const [clientComment, setClientComment] = useState("");
  const [internalNote, setInternalNote] = useState("");
  const [finalFile, setFinalFile] = useState<File | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!Number.isFinite(caseId) || caseId <= 0) {
      setError("El identificador del caso no es válido.");
      setIsLoading(false);
      return;
    }
    void load();
  }, [caseId]);

  async function load() {
    setIsLoading(true);
    setError(null);
    try {
      setCaseDetail(await getDocumentCase(caseId));
    } catch (issue) {
      setCaseDetail(null);
      setError(issue instanceof Error ? issue.message : "No fue posible cargar el caso.");
    } finally {
      setIsLoading(false);
    }
  }

  const currentStep = useMemo(() => flowSteps.indexOf(caseDetail?.current_state || "borrador"), [caseDetail]);
  const actData = useMemo(() => parseActData(caseDetail), [caseDetail]);
  const documents = Array.isArray(caseDetail?.documents) ? caseDetail.documents : [];
  const participants = Array.isArray(caseDetail?.participants) ? caseDetail.participants : [];
  const clientComments = Array.isArray(caseDetail?.client_comments) ? caseDetail.client_comments : [];
  const internalNotes = Array.isArray(caseDetail?.internal_notes) ? caseDetail.internal_notes : [];
  const workflowEvents = Array.isArray(caseDetail?.workflow_events) ? caseDetail.workflow_events : [];
  const draftDocument = documents.find((item) => item.category === "draft") ?? null;

  async function fileToBase64(file: File) {
    return new Promise<string>((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(String(reader.result).split(",")[1] ?? "");
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }

  async function handleClientComment(event: FormEvent) {
    event.preventDefault();
    if (!clientComment.trim()) return;
    setError(null);
    setFeedback(null);
    try {
      setCaseDetail(await addClientComment(caseId, clientComment));
      setClientComment("");
      setFeedback("Comentario del cliente registrado.");
    } catch (issue) {
      setError(issue instanceof Error ? issue.message : "No fue posible registrar el comentario.");
    }
  }

  async function handleInternalNote(event: FormEvent) {
    event.preventDefault();
    if (!internalNote.trim()) return;
    setError(null);
    setFeedback(null);
    try {
      setCaseDetail(await addInternalNote(caseId, internalNote));
      setInternalNote("");
      setFeedback("Observación interna registrada.");
    } catch (issue) {
      setError(issue instanceof Error ? issue.message : "No fue posible registrar la observación interna.");
    }
  }

  async function handleExport(format: "docx" | "pdf") {
    setError(null);
    setFeedback(null);
    try {
      setCaseDetail(await exportDocumentCase(caseId, format));
      setFeedback(`Exportación ${format.toUpperCase()} lista.`);
    } catch (issue) {
      setError(issue instanceof Error ? issue.message : "No fue posible exportar el documento.");
    }
  }

  async function handleFinalUpload() {
    if (!finalFile) {
      setError("Selecciona un archivo antes de cargar el documento definitivo.");
      return;
    }
    setError(null);
    setFeedback(null);
    try {
      setCaseDetail(await uploadFinalSigned(caseId, finalFile.name, await fileToBase64(finalFile), "Documento definitivo cargado desde detalle."));
      setFeedback("Documento definitivo cargado.");
    } catch (issue) {
      setError(issue instanceof Error ? issue.message : "No fue posible cargar el documento definitivo.");
    }
  }

  if (isLoading) {
    return <div className="ep-card rounded-[2rem] p-6 text-secondary">Cargando caso...</div>;
  }

  if (error && !caseDetail) {
    return <div className="ep-kpi-critical rounded-[2rem] px-6 py-5 text-sm">{error}</div>;
  }

  if (!caseDetail) {
    return <div className="ep-card rounded-[2rem] p-6 text-secondary">Sin datos del caso todavía.</div>;
  }

  return (
    <div className="space-y-6">
      <section className="ep-card rounded-[2rem] p-6">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <Link href="/dashboard/casos" className="inline-flex items-center gap-2 text-sm font-semibold text-primary"><ArrowLeft className="h-4 w-4" />Volver a casos</Link>
            <p className="mt-4 text-sm font-semibold uppercase tracking-[0.22em] text-accent">Detalle del caso</p>
            <h1 className="mt-2 text-3xl font-semibold tracking-[-0.05em] text-primary">{caseDetail.act_type || "Caso documental"}</h1>
            <p className="mt-3 text-base text-secondary">{caseDetail.internal_case_number || "Sin número interno"} · {caseDetail.notary_label || "Sin notaría"}</p>
          </div>
          <div className="grid gap-3 sm:grid-cols-2 lg:w-[430px]">
            <div className="ep-card-muted rounded-[1.5rem] p-4"><p className="text-xs uppercase tracking-[0.2em] text-secondary">Estado</p><p className="mt-2 text-lg font-semibold text-primary">{caseDetail.current_state || "Sin estado"}</p></div>
            <div className="ep-card-muted rounded-[1.5rem] p-4"><p className="text-xs uppercase tracking-[0.2em] text-secondary">Escritura oficial</p><p className="mt-2 text-lg font-semibold text-primary">{caseDetail.official_deed_number || "Pendiente"}</p></div>
            <div className="ep-card-muted rounded-[1.5rem] p-4"><p className="text-xs uppercase tracking-[0.2em] text-secondary">Responsable actual</p><p className="mt-2 text-lg font-semibold text-primary">{caseDetail.current_owner_user_name || "Sin asignar"}</p></div>
            <div className="ep-card-muted rounded-[1.5rem] p-4"><p className="text-xs uppercase tracking-[0.2em] text-secondary">Borrador actual</p><p className="mt-2 text-lg font-semibold text-primary">{draftDocument?.current_version_number ? `v${draftDocument.current_version_number}` : "Sin generar"}</p></div>
          </div>
        </div>
      </section>

      <section className="ep-card rounded-[2rem] p-6">
        <p className="text-xs uppercase tracking-[0.2em] text-secondary">Flujo documental</p>
        <div className="mt-4 grid gap-3 xl:grid-cols-6">
          {flowSteps.map((item, index) => <div key={item} className={`rounded-[1.35rem] border px-4 py-4 ${index === currentStep ? "border-primary/30 bg-primary text-white" : index < currentStep ? "border-emerald-500/20 bg-emerald-500/10" : "border-[var(--line)] bg-[var(--panel-soft)]"}`}><p className={`text-sm font-semibold ${index === currentStep ? "text-white" : "text-primary"}`}>{item}</p></div>)}
        </div>
      </section>

      <section className="ep-card rounded-[2rem] p-6">
        <div className="flex flex-wrap gap-2">{tabs.map((item) => <button key={item} type="button" onClick={() => setTab(item)} className={`rounded-full px-4 py-2 text-sm font-semibold ${tab === item ? "bg-primary text-white" : "ep-pill text-secondary"}`}>{item}</button>)}</div>
        <div className="mt-6">
          {tab === "Resumen" ? <div className="grid gap-4 lg:grid-cols-2"><div className="ep-card-soft rounded-[1.5rem] p-5"><p className="text-sm font-semibold text-primary">Plantilla</p><p className="mt-2 text-sm text-secondary">{caseDetail.template_name || "Sin plantilla"}</p><p className="mt-4 text-sm font-semibold text-primary">Creador</p><p className="mt-2 text-sm text-secondary">{caseDetail.created_by_user_name || "Sistema"}</p><p className="mt-4 text-sm font-semibold text-primary">Fecha de creación</p><p className="mt-2 text-sm text-secondary">{pretty(caseDetail.created_at)}</p></div><div className="ep-card-soft rounded-[1.5rem] p-5"><p className="text-sm font-semibold text-primary">Aprobación</p><p className="mt-2 text-sm text-secondary">{caseDetail.approved_by_user_name ? `${caseDetail.approved_by_user_name} · ${caseDetail.approved_by_role_code || "rol"}` : "Pendiente"}</p><p className="mt-4 text-sm font-semibold text-primary">Documento firmado final</p><p className="mt-2 text-sm text-secondary">{caseDetail.final_signed_uploaded ? "Cargado" : "Pendiente"}</p></div></div> : null}
          {tab === "Intervinientes" ? (
            participants.length > 0 ? <div className="grid gap-4 lg:grid-cols-2">{participants.map((item) => <div key={item.id} className="ep-card-soft rounded-[1.5rem] p-5"><div className="flex items-center justify-between"><p className="text-sm font-semibold text-primary">{item.role_label || "Interviniente"}</p><span className="ep-pill rounded-full px-3 py-1 text-xs text-secondary">{item.person.document_type || "DOC"} {item.person.document_number || "Sin número"}</span></div><p className="mt-3 text-lg font-semibold text-primary">{item.person.full_name || "Sin nombre"}</p><p className="mt-2 text-sm text-secondary">{item.person.nationality || "Sin nacionalidad"} · {item.person.marital_status || "Sin estado civil"}</p><p className="mt-2 text-sm text-secondary">{item.person.profession || "Sin profesión"} · {item.person.municipality || "Sin municipio"}</p><p className="mt-2 text-sm text-secondary">{item.person.address || "Sin dirección"} · {item.person.phone || "Sin teléfono"}</p></div>)}</div> : <div className="ep-card-muted rounded-[1.5rem] px-4 py-6 text-sm text-secondary">Sin intervinientes todavía.</div>
          ) : null}
          {tab === "Datos del acto" ? (
            Object.keys(actData).length > 0 ? <div className="grid gap-4 lg:grid-cols-2">{Object.entries(actData).map(([key, value]) => <div key={key} className="ep-card-soft rounded-[1.5rem] p-4"><p className="text-xs uppercase tracking-[0.18em] text-secondary">{key}</p><p className="mt-2 text-sm font-semibold text-primary">{String(value || "Sin dato")}</p></div>)}</div> : <div className="ep-card-muted rounded-[1.5rem] px-4 py-6 text-sm text-secondary">Sin datos del acto todavía.</div>
          ) : null}
          {tab === "Comentarios del cliente" ? <div className="space-y-4"><form onSubmit={handleClientComment} className="space-y-3"><textarea value={clientComment} onChange={(event) => setClientComment(event.target.value)} rows={4} className="ep-textarea w-full rounded-2xl px-4 py-3" placeholder="Registrar comentario del cliente..." /><button type="submit" className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white"><MessageSquareText className="h-4 w-4" />Agregar comentario</button></form><div className="space-y-3">{clientComments.length > 0 ? clientComments.map((item) => <div key={item.id} className="ep-card-soft rounded-[1.5rem] p-4"><p className="text-sm font-semibold text-primary">{item.created_by_user_name || "Usuario"}</p><p className="mt-2 text-sm text-secondary">{item.comment || "Sin comentario"}</p><p className="mt-2 text-xs text-secondary">{pretty(item.created_at)}</p></div>) : <div className="ep-card-muted rounded-[1.5rem] px-4 py-6 text-sm text-secondary">Sin comentarios del cliente todavía.</div>}</div></div> : null}
          {tab === "Observaciones internas" ? <div className="space-y-4"><form onSubmit={handleInternalNote} className="space-y-3"><textarea value={internalNote} onChange={(event) => setInternalNote(event.target.value)} rows={4} className="ep-textarea w-full rounded-2xl px-4 py-3" placeholder="Registrar observación interna..." /><button type="submit" className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white"><NotebookTabs className="h-4 w-4" />Agregar observación</button></form><div className="space-y-3">{internalNotes.length > 0 ? internalNotes.map((item) => <div key={item.id} className="ep-card-soft rounded-[1.5rem] p-4"><p className="text-sm font-semibold text-primary">{item.created_by_user_name || "Usuario"}</p><p className="mt-2 text-sm text-secondary">{item.note || "Sin nota"}</p><p className="mt-2 text-xs text-secondary">{pretty(item.created_at)}</p></div>) : <div className="ep-card-muted rounded-[1.5rem] px-4 py-6 text-sm text-secondary">Sin observaciones internas todavía.</div>}</div></div> : null}
          {tab === "Documentos" ? <div className="space-y-4"><div className="grid gap-4 lg:grid-cols-2"><button type="button" onClick={() => void handleExport("docx")} className="inline-flex items-center justify-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white"><Download className="h-4 w-4" />Exportar Word</button><button type="button" onClick={() => void handleExport("pdf")} className="inline-flex items-center justify-center gap-2 rounded-2xl border border-[var(--line)] px-5 py-3 text-sm font-semibold text-primary"><Download className="h-4 w-4" />Exportar PDF</button></div><label className="ep-card-muted flex items-center justify-between rounded-2xl px-4 py-4 text-sm text-secondary"><span className="inline-flex items-center gap-2"><Upload className="h-4 w-4 text-primary" />Documento definitivo</span><input type="file" accept=".pdf,.doc,.docx" onChange={(event) => setFinalFile(event.target.files?.[0] ?? null)} /></label><button type="button" onClick={() => void handleFinalUpload()} disabled={!finalFile} className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white disabled:opacity-60"><Upload className="h-4 w-4" />Cargar definitivo</button><div className="space-y-3">{documents.length > 0 ? documents.map((document) => <div key={document.id} className="ep-card-soft rounded-[1.5rem] p-4"><div className="flex items-center justify-between"><p className="text-sm font-semibold text-primary">{document.title || "Documento"}</p><span className="ep-pill rounded-full px-3 py-1 text-xs text-secondary">{document.category || "sin categoría"}</span></div><div className="mt-3 space-y-2">{Array.isArray(document.versions) && document.versions.length > 0 ? document.versions.map((version) => <a key={version.id} href={`http://127.0.0.1:8000${version.download_url || ""}`} target="_blank" rel="noreferrer" className="flex items-center justify-between rounded-xl border border-[var(--line)] px-3 py-3 hover:bg-[var(--panel)]"><span className="text-sm text-primary">v{version.version_number} · {(version.file_format || "bin").toUpperCase()}</span><span className="text-xs text-secondary">{pretty(version.created_at)}</span></a>) : <div className="ep-card-muted rounded-xl px-3 py-3 text-sm text-secondary">Sin versiones todavía.</div>}</div></div>) : <div className="ep-card-muted rounded-[1.5rem] px-4 py-6 text-sm text-secondary">Sin documentos todavía.</div>}</div></div> : null}
          {tab === "Trazabilidad" ? <div className="space-y-3">{workflowEvents.length > 0 ? workflowEvents.map((item) => <div key={item.id} className="ep-card-soft rounded-[1.5rem] p-4"><div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between"><p className="text-sm font-semibold text-primary">{item.event_type || "evento"}</p><span className="text-xs text-secondary">{pretty(item.created_at)}</span></div><p className="mt-2 text-sm text-secondary">Actor: {item.actor_user_name || "Sistema"}{item.actor_role_code ? ` · ${item.actor_role_code}` : ""}</p>{item.comment ? <p className="mt-2 text-sm text-secondary">{item.comment}</p> : null}{item.new_value ? <p className="mt-2 text-sm text-secondary">Nuevo valor: {item.new_value}</p> : null}</div>) : <div className="ep-card-muted rounded-[1.5rem] px-4 py-6 text-sm text-secondary">Sin trazabilidad todavía.</div>}</div> : null}
        </div>
        {feedback ? <div className="ep-kpi-success mt-6 rounded-2xl px-4 py-3 text-sm">{feedback}</div> : null}
        {error ? <div className="ep-kpi-critical mt-6 rounded-2xl px-4 py-3 text-sm">{error}</div> : null}
      </section>
    </div>
  );
}


