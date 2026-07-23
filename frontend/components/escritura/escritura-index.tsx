"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { ArrowRight, Loader2, PenTool, RefreshCw } from "lucide-react";
import { getCases, type CaseRecord } from "@/lib/api";
import { crearCasoEscritura } from "@/lib/api-escritura";

export function EscrituraIndex() {
  const router = useRouter();
  const [cases, setCases] = useState<CaseRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);

  async function load() {
    setIsLoading(true);
    setError(null);
    try {
      setCases(await getCases({}));
    } catch (err) {
      setError(err instanceof Error ? err.message : "No fue posible cargar los casos.");
    } finally {
      setIsLoading(false);
    }
  }

  async function nuevaEscritura() {
    setIsCreating(true);
    setError(null);
    try {
      const creado = await crearCasoEscritura();
      router.push(`/dashboard/casos/${creado.case_id}/escritura`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "No fue posible iniciar la escritura.");
      setIsCreating(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="space-y-6">
      <section className="ep-card rounded-[2rem] px-6 py-5">
        <p className="text-sm font-semibold uppercase tracking-[0.22em] text-accent">Minutas Asistidas</p>
        <h1 className="mt-2 text-3xl font-semibold tracking-[-0.05em] text-primary">Inicia una escritura o retoma un caso</h1>
        <p className="mt-2 text-sm text-secondary">
          Empieza eligiendo el acto (compraventa, compraventa + hipoteca, cancelación de hipoteca); luego la fuente (banco, particular o proyecto) y la captura asistida. No necesitas subir ningún documento.
        </p>
        <div className="mt-4 flex flex-wrap gap-3">
          <button
            type="button"
            onClick={nuevaEscritura}
            disabled={isCreating}
            className="inline-flex items-center gap-2 rounded-full bg-primary px-4 py-2 text-sm font-semibold text-white transition hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isCreating ? <Loader2 className="h-4 w-4 animate-spin" /> : <PenTool className="h-4 w-4" />} Nueva escritura
          </button>
          <button
            type="button"
            onClick={load}
            className="inline-flex items-center gap-2 rounded-full border border-[var(--line)] bg-white px-4 py-2 text-sm font-semibold text-secondary transition hover:border-primary/25"
          >
            <RefreshCw className="h-4 w-4" /> Actualizar
          </button>
        </div>
      </section>

      <section className="ep-card rounded-[2rem] p-6">
        {isLoading ? (
          <p className="text-sm text-secondary">Cargando casos...</p>
        ) : error ? (
          <p className="text-sm font-semibold text-[var(--ins,#b23a2e)]">{error}</p>
        ) : cases.length === 0 ? (
          <p className="text-sm text-secondary">No hay casos todavía. Crea uno para empezar la escritura.</p>
        ) : (
          <div className="grid gap-3">
            {cases.map((item) => (
              <Link
                key={item.id}
                href={`/dashboard/casos/${item.id}/escritura`}
                className="flex items-center justify-between gap-4 ep-card-soft rounded-[1.6rem] p-5 transition hover:-translate-y-0.5 hover:border-primary/25 hover:shadow-soft"
              >
                <div>
                  <p className="text-sm font-semibold text-primary">{item.display_name || `Caso ${item.id}`}</p>
                  <p className="mt-1 text-xs text-secondary">
                    {item.act_type || "Sin acto"} · {item.current_state} · {item.notary_label}
                  </p>
                </div>
                <span className="inline-flex shrink-0 items-center gap-1 text-sm font-semibold text-primary">
                  Minutas Asistidas <ArrowRight className="h-4 w-4" />
                </span>
              </Link>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
