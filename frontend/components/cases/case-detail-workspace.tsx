"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { type ChangeEvent, type DragEvent, type MouseEvent, useEffect, useMemo, useRef, useState } from "react";
import { ArrowLeft, FileText, Upload, X } from "lucide-react";
import {
  buildCaseOnlyOfficeEditorPath,
  downloadDocumentVersionBlob,
  getDocumentCase,
  uploadFinalSigned,
  type DocumentFlowCase,
} from "@/lib/document-flow";
import { formatDateTime } from "@/lib/datetime";

const stateLabels: Record<string, string> = {
  borrador: "Borrador",
  en_diligenciamiento: "En diligenciamiento",
  revision_cliente: "Revision del cliente",
  ajustes_solicitados: "Ajustes solicitados",
  revision_aprobador: "Revision del aprobador",
  devuelto_aprobador: "Devuelto por aprobador",
  revision_notario: "Revision del notario",
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

export function CaseDetailWorkspace({ caseId }: { caseId: number; initialTab?: string }) {
  const router = useRouter();
  const [caseDetail, setCaseDetail] = useState<DocumentFlowCase | null>(null);
  const [finalFile, setFinalFile] = useState<File | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [isOpeningSignedPdf, setIsOpeningSignedPdf] = useState(false);
  const [isPdfDragActive, setIsPdfDragActive] = useState(false);
  const pdfInputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    if (!Number.isFinite(caseId) || caseId <= 0) {
      setError("El identificador de la minuta no es valido.");
      setIsLoading(false);
      return;
    }
    void load();
  }, [caseId]);

  async function load() {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getDocumentCase(caseId);
      setCaseDetail(data);
    } catch (issue) {
      setCaseDetail(null);
      setError(issue instanceof Error ? issue.message : "No fue posible cargar la minuta.");
    } finally {
      setIsLoading(false);
    }
  }

  const documents = useMemo(() => (Array.isArray(caseDetail?.documents) ? caseDetail.documents : []), [caseDetail?.documents]);
  const draftDocument = documents.find((item) => item.category === "draft") ?? null;
  const markedTemplateDocument = documents.find((item) => item.category === "marked_template") ?? null;
  const finalSignedDocument = documents.find((item) => item.category === "final_signed") ?? null;
  const primaryDocument = draftDocument ?? markedTemplateDocument ?? null;
  const latestWordVersion = primaryDocument?.versions?.find((item) => item.file_format.toLowerCase() === "docx") ?? null;
  const latestFinalSignedVersion = finalSignedDocument?.versions?.find((item) => item.file_format.toLowerCase() === "pdf") ?? null;
  const hasEditableDocumentVersion = Boolean(
    primaryDocument?.id && latestWordVersion?.id && latestWordVersion.file_format.toLowerCase() === "docx"
  );
  const finalSignedDownloadUrl = latestFinalSignedVersion?.download_url ?? null;
  const hasViewableFinalSignedVersion = Boolean(finalSignedDocument?.id && latestFinalSignedVersion?.id && finalSignedDownloadUrl);
  const isMarkedTemplateCase = caseDetail?.act_type === "minuta_marcada" || (primaryDocument?.category ?? "") === "marked_template";
  const caseDisplayTitle = isMarkedTemplateCase ? (primaryDocument?.title || "Minuta marcada") : (caseDetail?.act_type || "Minuta");
  const currentVersionLabel = latestWordVersion ? `v${latestWordVersion.version_number}` : "Sin version DOCX";

  async function fileToBase64(file: File) {
    return new Promise<string>((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(String(reader.result).split(",")[1] ?? "");
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }

  async function handleOpenOnlyOffice() {
    if (!primaryDocument?.id || !latestWordVersion?.id) return;
    const editorPath = buildCaseOnlyOfficeEditorPath(caseId, primaryDocument.id, latestWordVersion.id);
    router.push(editorPath);
  }

  async function handleViewFinalSigned(event?: MouseEvent<HTMLButtonElement>) {
    event?.preventDefault();
    event?.stopPropagation();
    if (!finalSignedDownloadUrl) return;
    setError(null);
    setFeedback(null);
    setIsOpeningSignedPdf(true);
    try {
      const blob = await downloadDocumentVersionBlob(finalSignedDownloadUrl);
      const blobUrl = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = blobUrl;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.setTimeout(() => URL.revokeObjectURL(blobUrl), 60_000);
    } catch (issue) {
      setError(issue instanceof Error ? issue.message : "No fue posible abrir la minuta firmada.");
    } finally {
      setIsOpeningSignedPdf(false);
    }
  }

  function clearSelectedPdf() {
    setFinalFile(null);
    if (pdfInputRef.current) {
      pdfInputRef.current.value = "";
    }
  }

  function updateSelectedPdf(file: File | null) {
    if (!file) {
      clearSelectedPdf();
      return;
    }
    const isPdf = file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf");
    if (!isPdf) {
      clearSelectedPdf();
      setFeedback(null);
      setError("Solo se permiten archivos PDF.");
      return;
    }
    setError(null);
    setFeedback(null);
    setFinalFile(file);
  }

  function handlePdfInputChange(event: ChangeEvent<HTMLInputElement>) {
    updateSelectedPdf(event.target.files?.[0] ?? null);
  }

  function handlePdfDragOver(event: DragEvent<HTMLLabelElement>) {
    event.preventDefault();
    setIsPdfDragActive(true);
  }

  function handlePdfDragLeave() {
    setIsPdfDragActive(false);
  }

  function handlePdfDrop(event: DragEvent<HTMLLabelElement>) {
    event.preventDefault();
    setIsPdfDragActive(false);
    updateSelectedPdf(event.dataTransfer.files?.[0] ?? null);
  }

  async function handleFinalUpload() {
    if (!finalFile) {
      setError("Selecciona un archivo PDF antes de guardar la minuta firmada.");
      return;
    }
    setError(null);
    setFeedback(null);
    setIsUploading(true);
    try {
      const updatedCase = await uploadFinalSigned(
        caseId,
        finalFile.name,
        await fileToBase64(finalFile),
        "Minuta firmada cargada desde detalle."
      );
      setCaseDetail(updatedCase);
      clearSelectedPdf();
      setFeedback("Minuta firmada cargada correctamente.");
    } catch (issue) {
      setError(issue instanceof Error ? issue.message : "No fue posible cargar la minuta firmada.");
    } finally {
      setIsUploading(false);
    }
  }

  if (isLoading) {
    return <div className="ep-card rounded-[2rem] p-6 text-secondary">Cargando minuta...</div>;
  }

  if (!caseDetail) {
    return <div className="ep-card rounded-[2rem] p-6 text-secondary">{error || "No fue posible cargar la minuta."}</div>;
  }

  return (
    <div className="space-y-6">
      <section className="ep-card rounded-[2rem] px-6 py-4">
        <div className="flex flex-col gap-3">
          <div>
            <Link href="/dashboard/casos" className="inline-flex items-center gap-2 text-sm font-semibold text-primary">
              <ArrowLeft className="h-4 w-4" />
              Volver a la bandeja
            </Link>
            <p className="mt-3 text-sm font-semibold uppercase tracking-[0.22em] text-accent">Detalle de la minuta</p>
            <h1 className="mt-2 text-3xl font-semibold tracking-[-0.05em] text-primary">{caseDisplayTitle}</h1>
            <p className="mt-2 text-sm text-secondary">
              {caseDetail.internal_case_number || "Sin numero interno"} · {caseDetail.notary_label || "Sin notaria"}
            </p>
            <div className="mt-3 flex flex-wrap gap-2">
              <span className="inline-flex rounded-full bg-primary/10 px-3 py-1 text-sm font-semibold text-primary">
                {prettyState(caseDetail.current_state)}
              </span>
              <span className="inline-flex rounded-full border border-[var(--line)] bg-white px-3 py-1 text-sm font-semibold text-secondary">
                {currentVersionLabel}
              </span>
              {caseDetail.updated_at ? (
                <span className="inline-flex rounded-full border border-[var(--line)] bg-white px-3 py-1 text-sm text-secondary">
                  Actualizada {pretty(caseDetail.updated_at)}
                </span>
              ) : null}
            </div>
          </div>
        </div>
      </section>

      <section className="ep-card rounded-[2rem] p-6">
        <div className="space-y-6">
          {hasEditableDocumentVersion ? (
            <div className="flex flex-wrap items-center gap-3">
              <button
                type="button"
                onClick={() => void handleOpenOnlyOffice()}
                className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white"
              >
                Editar minuta
              </button>
            </div>
          ) : null}

          <section className="space-y-4 rounded-[1.75rem] border border-[var(--line)] bg-[var(--panel-soft)] p-5">
            <div className="space-y-2">
              <p className="text-sm font-semibold text-primary">Cargar minuta firmada</p>
              <p className="text-sm text-secondary">Arrastra aqui el PDF firmado o seleccionalo desde tu equipo.</p>
            </div>

            {finalFile ? (
              <div className="ep-card-muted flex items-center gap-4 rounded-2xl p-5">
                <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-success-bg">
                  <FileText className="h-5 w-5 text-emerald-600" />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-semibold text-ink">{finalFile.name}</p>
                  <p className="mt-0.5 text-xs text-soft">
                    {(finalFile.size / 1024).toFixed(0)} KB · PDF listo para guardar
                  </p>
                </div>
                <button
                  type="button"
                  onClick={clearSelectedPdf}
                  className="flex h-8 w-8 items-center justify-center rounded-lg transition-colors hover:bg-surface-alt"
                  aria-label="Quitar archivo"
                >
                  <X className="h-4 w-4 text-soft" />
                </button>
              </div>
            ) : (
              <label
                onDragOver={handlePdfDragOver}
                onDragLeave={handlePdfDragLeave}
                onDrop={handlePdfDrop}
                className={[
                  "flex cursor-pointer flex-col items-center justify-center gap-3 rounded-2xl border-2 border-dashed p-10 text-center transition-all",
                  isPdfDragActive
                    ? "border-primary bg-panel-highlight"
                    : "border-line-strong hover:border-primary hover:bg-panel-soft",
                ].join(" ")}
              >
                <input
                  ref={pdfInputRef}
                  type="file"
                  accept=".pdf,application/pdf"
                  className="hidden"
                  onChange={handlePdfInputChange}
                />
                <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-panel-soft">
                  <Upload className="h-6 w-6 text-primary" />
                </div>
                <div className="text-center">
                  <p className="font-semibold text-ink">Arrastra un archivo .pdf aqui</p>
                  <p className="mt-1 text-sm text-muted">
                    o <span className="text-primary underline underline-offset-2">haz clic para seleccionar</span>
                  </p>
                </div>
                <p className="text-xs text-soft">Solo archivos .pdf - max 20 MB</p>
              </label>
            )}

            <div className="flex flex-wrap items-center gap-3">
              <button
                type="button"
                onClick={() => void handleFinalUpload()}
                disabled={!finalFile || isUploading}
                className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white disabled:opacity-60"
              >
                <Upload className="h-4 w-4" />
                {isUploading ? "Guardando..." : "Guardar minuta firmada"}
              </button>
              {hasViewableFinalSignedVersion ? (
                <button
                  type="button"
                  onClick={(event) => void handleViewFinalSigned(event)}
                  disabled={isOpeningSignedPdf}
                  className="inline-flex items-center gap-2 rounded-2xl border border-[var(--line)] bg-white px-5 py-3 text-sm font-semibold text-primary disabled:opacity-60"
                >
                  {isOpeningSignedPdf ? "Abriendo..." : "Ver minuta firmada"}
                </button>
              ) : null}
              {caseDetail.final_signed_uploaded ? (
                <span className="inline-flex rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
                  Minuta firmada cargada
                </span>
              ) : null}
            </div>
          </section>

          {feedback ? <div className="ep-kpi-success rounded-2xl px-4 py-3 text-sm">{feedback}</div> : null}
          {error ? <div className="ep-kpi-critical rounded-2xl px-4 py-3 text-sm">{error}</div> : null}
        </div>
      </section>
    </div>
  );
}
