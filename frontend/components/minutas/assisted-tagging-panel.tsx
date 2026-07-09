"use client";

import { useRef, useState, type DragEvent } from "react";
import {
  AlertCircle,
  ArrowLeft,
  CheckCircle2,
  Download,
  ExternalLink,
  FileText,
  Loader2,
  Upload,
  X,
} from "lucide-react";

import {
  approveAssistedTaggingJob,
  createAssistedTaggingJob,
  rejectAssistedTaggingJob,
  runAssistedTaggingJob,
  uploadApprovedAssistedTaggingDocx,
  type AssistedTaggingJob,
} from "@/lib/minuta";

type Props = {
  onBackToMarkedFlow: () => void;
};

const DOCUMENT_TYPES = [
  "Compraventa",
  "Compraventa con hipoteca",
  "Hipoteca",
  "Cancelación de hipoteca",
  "Salida del país",
  "Poder",
  "Registro civil",
  "Patrimonio de familia",
  "Sucesión",
  "Otro",
];

function statusLabel(status: string) {
  const labels: Record<string, string> = {
    uploaded: "DOCX cargado",
    processing: "Etiquetando",
    pretagged: "Pre-etiquetado",
    human_review: "Revision humana",
    approved: "Aprobado",
    rejected: "Rechazado",
    failed: "Fallido",
    saved_to_library: "Guardado en biblioteca",
  };
  return labels[status] ?? status;
}

export function AssistedTaggingPanel({ onBackToMarkedFlow }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [documentType, setDocumentType] = useState(DOCUMENT_TYPES[0]);
  const [isDragging, setIsDragging] = useState(false);
  const [isWorking, setIsWorking] = useState(false);
  const [job, setJob] = useState<AssistedTaggingJob | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [approvedFile, setApprovedFile] = useState<File | null>(null);
  const [confirmNoChanges, setConfirmNoChanges] = useState(false);

  function selectFile(nextFile: File) {
    if (!nextFile.name.toLowerCase().endsWith(".docx")) {
      setError("Solo se aceptan documentos DOCX.");
      return;
    }
    setFile(nextFile);
    setJob(null);
    setError(null);
  }

  function handleDrop(event: DragEvent<HTMLLabelElement>) {
    event.preventDefault();
    setIsDragging(false);
    const nextFile = event.dataTransfer.files[0];
    if (nextFile) selectFile(nextFile);
  }

  async function handleTag() {
    if (!file) return;
    setIsWorking(true);
    setError(null);
    try {
      const created = await createAssistedTaggingJob(file, documentType);
      const processed = await runAssistedTaggingJob(created.id);
      setJob(processed);
      setApprovedFile(null);
      setConfirmNoChanges(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "No fue posible etiquetar la minuta.");
    } finally {
      setIsWorking(false);
    }
  }

  async function handleApprove() {
    if (!job) return;
    setIsWorking(true);
    setError(null);
    try {
      setJob(await approveAssistedTaggingJob(job.id, confirmNoChanges && !job.approved_docx_uploaded));
    } catch (err) {
      setError(err instanceof Error ? err.message : "No fue posible aprobar la plantilla.");
    } finally {
      setIsWorking(false);
    }
  }

  async function handleUploadApprovedDocx() {
    if (!job || !approvedFile) return;
    setIsWorking(true);
    setError(null);
    try {
      const nextJob = await uploadApprovedAssistedTaggingDocx(job.id, approvedFile);
      setJob(nextJob);
      setConfirmNoChanges(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "No fue posible subir el DOCX aprobado.");
    } finally {
      setIsWorking(false);
    }
  }

  async function handleReject() {
    if (!job) return;
    setIsWorking(true);
    setError(null);
    try {
      setJob(await rejectAssistedTaggingJob(job.id, "Rechazado desde revision humana."));
    } catch (err) {
      setError(err instanceof Error ? err.message : "No fue posible rechazar el job.");
    } finally {
      setIsWorking(false);
    }
  }

  const readyForReview = Boolean(job?.onlyoffice_path || job?.download_url);
  const saved = job?.status === "saved_to_library";
  const canApprove = Boolean(job?.approved_docx_uploaded || confirmNoChanges);

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold text-primary">Crear plantilla inteligente</h2>
          <p className="mt-1 text-sm text-muted">
            Sube una minuta elaborada, revisa el DOCX con variables en rojo y apruebala para biblioteca.
          </p>
        </div>
        <button
          type="button"
          onClick={onBackToMarkedFlow}
          className="inline-flex h-10 items-center gap-2 rounded-xl border border-line px-3 text-sm font-semibold text-muted hover:border-primary hover:text-primary"
        >
          <ArrowLeft size={16} />
          Volver
        </button>
      </div>

      {error && (
        <div className="flex items-start gap-3 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3">
          <AlertCircle size={16} className="mt-0.5 shrink-0 text-rose-500" />
          <p className="text-sm text-rose-700">{error}</p>
          <button type="button" onClick={() => setError(null)} className="ml-auto text-rose-400 hover:text-rose-600">
            <X size={14} />
          </button>
        </div>
      )}

      <div className="rounded-2xl border border-line bg-panel p-5">
        <label className="grid gap-2 text-sm font-semibold text-ink">
          Tipo de minuta
          <select
            value={documentType}
            onChange={(event) => setDocumentType(event.target.value)}
            className="h-11 rounded-xl border border-line bg-surface px-3 text-sm text-ink outline-none focus:border-primary"
          >
            {DOCUMENT_TYPES.map((type) => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>
        </label>
      </div>

      <label
        onDragOver={(event) => {
          event.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        className={[
          "flex cursor-pointer flex-col items-center justify-center gap-3 rounded-2xl border-2 border-dashed p-8 transition-all",
          isDragging ? "border-primary bg-panel-highlight" : "border-line-strong hover:border-primary hover:bg-panel-soft",
        ].join(" ")}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".docx"
          className="hidden"
          onChange={(event) => {
            const nextFile = event.target.files?.[0];
            if (nextFile) selectFile(nextFile);
          }}
        />
        <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-panel-soft">
          <Upload size={22} className="text-primary" />
        </div>
        <div className="text-center">
          <p className="text-sm font-semibold text-ink">{file ? file.name : "Sube un DOCX elaborado"}</p>
          <p className="mt-1 text-xs text-muted">
            {file ? `${(file.size / 1024).toFixed(0)} KB listos para etiquetar` : "Arrastra el archivo o haz clic para seleccionarlo"}
          </p>
        </div>
      </label>

      <button
        type="button"
        onClick={handleTag}
        disabled={!file || isWorking}
        className={[
          "inline-flex h-12 w-full items-center justify-center gap-2 rounded-2xl px-4 text-sm font-semibold transition-all",
          file && !isWorking ? "bg-primary text-white hover:opacity-90" : "cursor-not-allowed bg-panel-soft text-soft",
        ].join(" ")}
      >
        {isWorking && !job ? <Loader2 size={16} className="animate-spin" /> : <FileText size={16} />}
        Etiquetar minuta
      </button>

      {job && (
        <div className="space-y-4 rounded-2xl border border-line bg-panel p-5">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <p className="text-sm font-bold text-ink">{statusLabel(job.status)}</p>
              <p className="mt-1 text-xs text-soft">{job.source_filename} · {job.document_type}</p>
            </div>
            {saved && (
              <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-3 py-1 text-xs font-bold text-emerald-700">
                <CheckCircle2 size={13} />
                Biblioteca
              </span>
            )}
          </div>

          {readyForReview && (
            <div className="space-y-3">
              <div className="grid gap-3 sm:grid-cols-2">
                {job.onlyoffice_path && (
                  <a
                    href={job.onlyoffice_path}
                    className="inline-flex h-11 items-center justify-center gap-2 rounded-xl bg-primary px-4 text-sm font-semibold text-white hover:opacity-90"
                  >
                    <ExternalLink size={16} />
                    Abrir en OnlyOffice
                  </a>
                )}
                {job.download_url && (
                  <a
                    href={job.download_url}
                    className="inline-flex h-11 items-center justify-center gap-2 rounded-xl border border-line px-4 text-sm font-semibold text-muted hover:border-primary hover:text-primary"
                  >
                    <Download size={16} />
                    Descargar DOCX
                  </a>
                )}
              </div>
              <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3">
                <p className="text-sm font-semibold text-amber-800">Aprobacion segura</p>
                <p className="mt-1 text-xs leading-5 text-amber-800">
                  EasyPro no puede garantizar desde aqui que OnlyOffice ya sincronizo la ultima edicion. Sube el DOCX corregido/aprobado antes de aprobar, o confirma que no hiciste cambios sobre el pre-etiquetado.
                </p>
              </div>
              <div className="rounded-xl border border-line bg-panel-soft p-3">
                <label className="grid gap-2 text-xs font-semibold uppercase tracking-wider text-soft">
                  DOCX corregido/aprobado
                  <input
                    type="file"
                    accept=".docx"
                    onChange={(event) => {
                      const nextFile = event.target.files?.[0] ?? null;
                      setApprovedFile(nextFile);
                      if (nextFile) setConfirmNoChanges(false);
                    }}
                    className="text-sm normal-case tracking-normal text-muted"
                  />
                </label>
                <div className="mt-3 flex flex-wrap items-center gap-3">
                  <button
                    type="button"
                    onClick={handleUploadApprovedDocx}
                    disabled={!approvedFile || isWorking}
                    className={[
                      "inline-flex h-10 items-center justify-center gap-2 rounded-xl px-3 text-sm font-semibold",
                      approvedFile && !isWorking ? "bg-primary text-white hover:opacity-90" : "cursor-not-allowed bg-surface-alt text-soft",
                    ].join(" ")}
                  >
                    {isWorking && approvedFile ? <Loader2 size={16} className="animate-spin" /> : <Upload size={16} />}
                    Subir aprobado
                  </button>
                  {job.approved_docx_uploaded && (
                    <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-emerald-700">
                      <CheckCircle2 size={14} />
                      DOCX aprobado cargado
                    </span>
                  )}
                </div>
                {!job.approved_docx_uploaded && (
                  <label className="mt-3 flex items-start gap-2 text-xs leading-5 text-muted">
                    <input
                      type="checkbox"
                      checked={confirmNoChanges}
                      onChange={(event) => setConfirmNoChanges(event.target.checked)}
                      className="mt-1"
                    />
                    Confirmo que no hice cambios en Word ni OnlyOffice y que puedo aprobar el DOCX pre-etiquetado original.
                  </label>
                )}
              </div>
            </div>
          )}

          {job.fields.length > 0 && (
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-soft">Campos detectados</p>
              <div className="mt-3 grid gap-2">
                {job.fields.slice(0, 12).map((field) => (
                  <div key={field.field_code} className="flex items-center justify-between gap-3 rounded-xl bg-panel-soft px-3 py-2">
                    <div className="min-w-0">
                      <p className="truncate text-sm font-semibold text-ink">{field.label}</p>
                      <p className="truncate text-xs text-soft">{field.section} · {field.occurrences} ocurr.</p>
                    </div>
                    <span className="rounded-full bg-surface px-2.5 py-1 text-xs font-semibold text-muted">
                      {Math.round(field.confidence * 100)}%
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {job.warnings.length > 0 && (
            <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3">
              <p className="text-xs font-semibold uppercase tracking-wider text-amber-700">Advertencias</p>
              <ul className="mt-2 space-y-1 text-sm text-amber-800">
                {job.warnings.map((warning, index) => <li key={`${warning}-${index}`}>{warning}</li>)}
              </ul>
            </div>
          )}

          {job.status === "human_review" && (
            <div className="grid gap-3 sm:grid-cols-2">
              <button
                type="button"
                onClick={handleApprove}
                disabled={isWorking || !canApprove}
                className="inline-flex h-11 items-center justify-center gap-2 rounded-xl bg-emerald-600 px-4 text-sm font-semibold text-white hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {isWorking ? <Loader2 size={16} className="animate-spin" /> : <CheckCircle2 size={16} />}
                Aprobar y guardar
              </button>
              <button
                type="button"
                onClick={handleReject}
                disabled={isWorking}
                className="inline-flex h-11 items-center justify-center gap-2 rounded-xl border border-line px-4 text-sm font-semibold text-muted hover:border-rose-300 hover:text-rose-700 disabled:opacity-60"
              >
                <X size={16} />
                Rechazar
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
