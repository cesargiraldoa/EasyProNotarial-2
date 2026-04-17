"use client";

import Link from "next/link";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { ArrowLeft, Download, FileSignature, MessageSquareText, NotebookTabs, Sparkles, Upload } from "lucide-react";
import { addClientComment, addInternalNote, exportDocumentCase, generateWithGari, getDocumentCase, uploadFinalSigned, type DocumentFlowCase } from "@/lib/document-flow";
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
const tabs = ["Resumen", "Intervinientes", "Datos del acto", "Comentarios del cliente", "Observaciones internas", "Documentos", "Trazabilidad", "Documento Gari"] as const;

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
  const [isGeneratingGari, setIsGeneratingGari] = useState(false);
  const [gariText, setGariText] = useState<string | null>(null);
  const [reviewerMode, setReviewerMode] = useState(false);
  const [correctionNote, setCorrectionNote] = useState("");
  const [isRegenerating, setIsRegenerating] = useState(false);
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

  useEffect(() => {
    setGariText(caseDetail?.act_data?.gari_draft_text ?? null);
  }, [caseDetail]);

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

  async function handleGenerateGari() {
    setIsGeneratingGari(true);
    setError(null);
    setFeedback(null);
    try {
      const updated = await generateWithGari(caseId, "Generado con Gari desde detalle del caso");
      setCaseDetail(updated);
      setGariText(updated?.act_data?.gari_draft_text ?? null);
      setFeedback("Documento generado por Gari correctamente.");
    } catch (issue) {
      setError(issue instanceof Error ? issue.message : "No fue posible generar el documento con Gari.");
    } finally {
      setIsGeneratingGari(false);
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
          {tab === "Documentos" ? <div className="space-y-4"><div className="rounded-2xl border border-[#00E5A0]/30 bg-[#00E5A0]/5 p-5 space-y-3"><div className="flex items-center gap-3"><div className="w-8 h-8 rounded-full bg-[#00E5A0]/20 flex items-center justify-center"><Sparkles className="h-4 w-4 text-[#00E5A0]" /></div><div><p className="text-sm font-semibold text-primary">Gari ? Generaci?n documental</p><p className="text-xs text-secondary">Gari redacta el documento completo en lenguaje notarial colombiano</p></div></div><button type="button" onClick={() => void handleGenerateGari()} disabled={isGeneratingGari} className="inline-flex items-center gap-2 rounded-2xl px-5 py-3 text-sm font-semibold text-[#0D1B2A] bg-[#00E5A0] hover:bg-[#00C98A] transition disabled:opacity-60 disabled:cursor-not-allowed"><Sparkles className="h-4 w-4" />{isGeneratingGari ? "Gari est? redactando..." : "Generar con Gari"}</button>{gariText && (<p className="text-xs text-[#00E5A0]">Documento Gari disponible ? ver en tab "Documento Gari"</p>)}</div><div className="grid gap-4 lg:grid-cols-2"><button type="button" onClick={() => void handleExport("docx")} className="inline-flex items-center justify-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white"><Download className="h-4 w-4" />Exportar Word</button><button type="button" onClick={() => void handleExport("pdf")} className="inline-flex items-center justify-center gap-2 rounded-2xl border border-[var(--line)] px-5 py-3 text-sm font-semibold text-primary"><Download className="h-4 w-4" />Exportar PDF</button></div><label className="ep-card-muted flex items-center justify-between rounded-2xl px-4 py-4 text-sm text-secondary"><span className="inline-flex items-center gap-2"><Upload className="h-4 w-4 text-primary" />Documento definitivo</span><input type="file" accept=".pdf,.doc,.docx" onChange={(event) => setFinalFile(event.target.files?.[0] ?? null)} /></label><button type="button" onClick={() => void handleFinalUpload()} disabled={!finalFile} className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white disabled:opacity-60"><Upload className="h-4 w-4" />Cargar definitivo</button><div className="space-y-3">{documents.length > 0 ? documents.map((document) => <div key={document.id} className="ep-card-soft rounded-[1.5rem] p-4"><div className="flex items-center justify-between"><p className="text-sm font-semibold text-primary">{document.title || "Documento"}</p><span className="ep-pill rounded-full px-3 py-1 text-xs text-secondary">{document.category || "sin categoría"}</span></div><div className="mt-3 space-y-2">{Array.isArray(document.versions) && document.versions.length > 0 ? document.versions.map((version) => <button key={version.id} type="button" onClick={() => void handleDownload(version.download_url || "", `v${version.version_number}.${version.file_format || "docx"}`)} className="flex w-full items-center justify-between rounded-xl border border-[var(--line)] px-3 py-3 hover:bg-[var(--panel)] text-left"><span className="text-sm text-primary">v{version.version_number} ? {(version.file_format || "bin").toUpperCase()}</span><span className="text-xs text-secondary">{pretty(version.created_at)}</span></button>) : <div className="ep-card-muted rounded-xl px-3 py-3 text-sm text-secondary">Sin versiones todavía.</div>}</div></div>) : <div className="ep-card-muted rounded-[1.5rem] px-4 py-6 text-sm text-secondary">Sin documentos todavía.</div>}</div></div> : null}
          {tab === "Documento Gari" ? (
            <div className="space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => setReviewerMode(false)}
                    className={`rounded-full px-4 py-2 text-sm font-semibold transition ${!reviewerMode ? "bg-primary text-white" : "ep-pill text-secondary"}`}
                  >
                    Ver borrador
                  </button>
                  <button
                    type="button"
                    onClick={() => setReviewerMode(true)}
                    className={`rounded-full px-4 py-2 text-sm font-semibold transition ${reviewerMode ? "bg-primary text-white" : "ep-pill text-secondary"}`}
                  >
                    Modo revisor
                  </button>
                </div>
                <div className="flex items-center gap-2">
                  {draftDocument?.versions?.[0] && (
                    <button
                      type="button"
                      onClick={() => void handleDownload(
                        draftDocument.versions[draftDocument.versions.length - 1].download_url ?? "",
                        `gari_borrador_v${draftDocument.versions[draftDocument.versions.length - 1].version_number}.docx`
                      )}
                      className="inline-flex items-center gap-2 rounded-full border border-[var(--line)] px-4 py-2 text-sm font-semibold text-primary"
                    >
                      <Download className="h-4 w-4" />
                      Descargar Word
                    </button>
                  )}
                  <button
                    type="button"
                    onClick={() => void handleGenerateGari()}
                    disabled={isGeneratingGari}
                    className="inline-flex items-center gap-2 rounded-full bg-[#00E5A0] px-4 py-2 text-sm font-semibold text-[#0D1B2A] hover:bg-[#00C98A] transition disabled:opacity-60"
                  >
                    <Sparkles className="h-4 w-4" />
                    {isGeneratingGari ? "Generando..." : "Regenerar con Gari"}
                  </button>
                </div>
              </div>

              {draftDocument && Array.isArray(draftDocument.versions) && draftDocument.versions.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {draftDocument.versions.map((v) => (
                    <span key={v.id} className="ep-pill rounded-full px-3 py-1 text-xs text-secondary">
                      v{v.version_number}  {v.file_format?.toUpperCase() ?? "DOCX"}  {formatDateTime(v.created_at)}
                    </span>
                  ))}
                </div>
              )}

              {gariText || (draftDocument && Array.isArray(draftDocument.versions) && draftDocument.versions.length > 0) ? (
                <div className="flex gap-4 items-start">
                  <div
                    className="flex-1 min-w-0 rounded-2xl border border-[var(--line)] bg-white text-[#1A1A1A] overflow-auto"
                    style={{ minHeight: "70vh" }}
                  >
                    <div
                      className="mx-auto px-16 py-14"
                      style={{
                        maxWidth: "780px",
                        fontFamily: "Georgia, 'Times New Roman', serif",
                        fontSize: "13px",
                        lineHeight: "1.85",
                        color: "#1A1A1A",
                      }}
                    >
                      {gariText ? (
                        gariText
                          .split(/\[\[--\]\]|\n/)
                          .map((line, i) => {
                            const trimmed = line.trim();
                            if (!trimmed) return <div key={i} style={{ height: "0.75em" }} />;
                            const isBold = trimmed.startsWith("**") && trimmed.endsWith("**");
                            const clean = isBold ? trimmed.slice(2, -2) : trimmed;
                            const isHeader = isBold || /^(PRIMERO|SEGUNDO|TERCERO|CUARTO|QUINTO|SEXTO|SÉPTIMO|OCTAVO|NOVENO|DÉCIMO|ESCRITURA PÚBLICA|ACTO:|FECHA:|DE:|A:|VALOR:|OTORGAMIENTO|ACEPTACION|DERECHOS NOTARIALES|SUPERFONDO|PARÁGRAFO|PARAGRAFO|CONSTANCIA|AUTORIZACIÓN|NOTA)/i.test(clean);
                            return (
                              <p
                                key={i}
                                style={{
                                  fontWeight: isHeader ? "700" : "400",
                                  textAlign: "justify",
                                  marginBottom: isHeader ? "0.8em" : "0.4em",
                                  marginTop: isHeader ? "1em" : "0",
                                }}
                              >
                                {clean}
                              </p>
                            );
                          })
                      ) : (
                        <div style={{ textAlign: "center", padding: "3rem 0", color: "#8892A4" }}>
                          <p style={{ fontSize: "14px" }}>El texto del documento está disponible en el archivo Word descargable.</p>
                          <p style={{ fontSize: "13px", marginTop: "0.5rem" }}>Usa el botón "Descargar Word" para ver el contenido completo.</p>
                        </div>
                      )}
                    </div>
                  </div>

                  {reviewerMode && (
                    <div className="w-80 shrink-0 space-y-4">
                      <div className="ep-card-soft rounded-2xl p-5 space-y-3">
                        <p className="text-sm font-semibold text-primary">Instrucciones de corrección</p>
                        <p className="text-xs text-secondary">Describe qué debe cambiar Gari en la próxima versión.</p>
                        <textarea
                          value={correctionNote}
                          onChange={(e) => setCorrectionNote(e.target.value)}
                          rows={6}
                          className="ep-textarea w-full rounded-xl px-3 py-2 text-sm"
                          placeholder="Ej: Corregir el estado civil del poderdante, agregar cláusula de..., cambiar el municipio de expedición..."
                        />
                        <button
                          type="button"
                          disabled={isRegenerating || !correctionNote.trim()}
                          onClick={async () => {
                            setIsRegenerating(true);
                            setError(null);
                            try {
                              const updated = await generateWithGari(caseId, correctionNote, correctionNote);
                              setCaseDetail(updated);
                              setGariText(updated?.act_data?.gari_draft_text ?? null);
                              setCorrectionNote("");
                              setFeedback("Nueva versión generada con las correcciones.");
                            } catch (issue) {
                              setError(issue instanceof Error ? issue.message : "Error al regenerar.");
                            } finally {
                              setIsRegenerating(false);
                            }
                          }}
                          className="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-[#00E5A0] px-4 py-3 text-sm font-semibold text-[#0D1B2A] hover:bg-[#00C98A] transition disabled:opacity-60"
                        >
                          <Sparkles className="h-4 w-4" />
                          {isRegenerating ? "Regenerando..." : "Aplicar correcciones"}
                        </button>
                      </div>

                      {draftDocument && Array.isArray(draftDocument.versions) && draftDocument.versions.length > 0 && (
                        <div className="ep-card-soft rounded-2xl p-5 space-y-3">
                          <p className="text-sm font-semibold text-primary">Historial de versiones</p>
                          <div className="space-y-2">
                            {[...draftDocument.versions].reverse().map((v) => (
                              <div key={v.id} className="flex items-center justify-between rounded-xl border border-[var(--line)] px-3 py-2">
                                <div>
                                  <p className="text-sm font-semibold text-primary">v{v.version_number}</p>
                                  <p className="text-xs text-secondary">{formatDateTime(v.created_at)}</p>
                                </div>
                                <button
                                  type="button"
                                  onClick={() => void handleDownload(
                                    v.download_url ?? "",
                                    `gari_v${v.version_number}.docx`
                                  )}
                                  className="rounded-lg border border-[var(--line)] p-1.5 text-secondary hover:text-primary transition"
                                >
                                  <Download className="h-3.5 w-3.5" />
                                </button>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      <button
                        type="button"
                        onClick={async () => {
                          try {
                            const { approveDocumentCase } = await import("@/lib/document-flow");
                            await approveDocumentCase(caseId, "approver", "Documento aprobado");
                            setFeedback("Documento aprobado. Listo para firma del notario.");
                            const updated = await getDocumentCase(caseId);
                            setCaseDetail(updated);
                          } catch (e) {
                            setError(e instanceof Error ? e.message : "Error al aprobar.");
                          }
                        }}
                        className="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-primary px-4 py-3 text-sm font-semibold text-white hover:opacity-90 transition"
                      >
                        <FileSignature className="h-4 w-4" />
                        Aprobar documento
                      </button>
                    </div>
                  )}
                </div>
              ) : (
                <div className="ep-card-muted rounded-2xl px-6 py-12 text-center space-y-4">
                  <Sparkles className="h-8 w-8 text-[#00E5A0] mx-auto" />
                  <p className="text-sm font-semibold text-primary">Aún no hay documento generado por Gari</p>
                  <p className="text-sm text-secondary">Ve al tab Documentos y presiona "Generar con Gari" para crear el borrador.</p>
                  <button
                    type="button"
                    onClick={() => setTab("Documentos")}
                    className="inline-flex items-center gap-2 rounded-full bg-[#00E5A0] px-5 py-2.5 text-sm font-semibold text-[#0D1B2A] hover:bg-[#00C98A] transition"
                  >
                    <Sparkles className="h-4 w-4" />
                    Ir a Documentos
                  </button>
                </div>
              )}
            </div>
          ) : null}
          {tab === "Trazabilidad" ? <div className="space-y-3">{workflowEvents.length > 0 ? workflowEvents.map((item) => <div key={item.id} className="ep-card-soft rounded-[1.5rem] p-4"><div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between"><p className="text-sm font-semibold text-primary">{item.event_type || "evento"}</p><span className="text-xs text-secondary">{pretty(item.created_at)}</span></div><p className="mt-2 text-sm text-secondary">Actor: {item.actor_user_name || "Sistema"}{item.actor_role_code ? ` · ${item.actor_role_code}` : ""}</p>{item.comment ? <p className="mt-2 text-sm text-secondary">{item.comment}</p> : null}{item.new_value ? <p className="mt-2 text-sm text-secondary">Nuevo valor: {item.new_value}</p> : null}</div>) : <div className="ep-card-muted rounded-[1.5rem] px-4 py-6 text-sm text-secondary">Sin trazabilidad todavía.</div>}</div> : null}
        </div>
        {feedback ? <div className="ep-kpi-success mt-6 rounded-2xl px-4 py-3 text-sm">{feedback}</div> : null}
        {error ? <div className="ep-kpi-critical mt-6 rounded-2xl px-4 py-3 text-sm">{error}</div> : null}
      </section>
    </div>
  );
}


