"use client";

import { useState } from "react";
import { CheckCircle2, FileText, Loader2 } from "lucide-react";

const DEMO_TEMPLATE_URL = "/demo/minuta-jaggua-hipoteca-banco-bogota-2-compradores.docx";
const DEMO_TEMPLATE_NAME = "MINUTA JAGGUA HIPOTECA BANCO DE BOGOTÁ - 2 COMPRADORES.docx";

export function DemoTemplateQuickPick() {
  const [loading, setLoading] = useState(false);
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function useStoredTemplate() {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(DEMO_TEMPLATE_URL, { cache: "no-store" });
      if (!response.ok) throw new Error("No fue posible cargar la plantilla disponible.");
      const blob = await response.blob();
      const file = new File([blob], DEMO_TEMPLATE_NAME, {
        type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      });
      const input = document.querySelector<HTMLInputElement>('input[type="file"][accept=".docx"]');
      if (!input) throw new Error("No se encontró el flujo de plantilla etiquetada.");
      const transfer = new DataTransfer();
      transfer.items.add(file);
      input.files = transfer.files;
      input.dispatchEvent(new Event("change", { bubbles: true }));
      setLoaded(true);
    } catch (issue) {
      setError(issue instanceof Error ? issue.message : "No fue posible seleccionar la plantilla.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-3xl px-4 pt-8">
      <div className="rounded-2xl border border-line bg-panel p-5">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex min-w-0 items-center gap-3">
            <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-panel-highlight text-primary">
              <FileText size={20} />
            </span>
            <div className="min-w-0">
              <p className="text-xs font-semibold uppercase tracking-wider text-soft">Plantilla disponible</p>
              <p className="truncate text-sm font-bold text-ink">JAGGUA · Hipoteca Banco de Bogotá</p>
              <p className="mt-1 text-xs text-muted">2 compradores · 8 actos · formulario validado</p>
            </div>
          </div>
          <button
            type="button"
            onClick={useStoredTemplate}
            disabled={loading}
            className="inline-flex h-11 items-center gap-2 rounded-xl bg-primary px-4 text-sm font-semibold text-white disabled:opacity-60"
          >
            {loading ? <Loader2 size={16} className="animate-spin" /> : loaded ? <CheckCircle2 size={16} /> : <FileText size={16} />}
            {loading ? "Cargando..." : loaded ? "Plantilla seleccionada" : "Usar esta plantilla"}
          </button>
        </div>
        <p className="mt-3 text-xs text-muted">También puedes usar la carga desde el PC que aparece en el flujo actual.</p>
        {error && <p className="mt-2 text-xs text-rose-700">{error}</p>}
      </div>
    </div>
  );
}
