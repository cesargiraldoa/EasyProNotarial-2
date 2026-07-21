import { AlertTriangle, CheckCircle2, CircleAlert, ShieldCheck } from "lucide-react";
import type { Resultado } from "@/lib/motor-escritura";

type Cumplimiento = Resultado["cumplimiento"];
type Item = Cumplimiento["items"][number];

const tipoLabel: Record<Item["tipo"], string> = {
  ok: "Cumple",
  obl: "Obligatorio",
  warn: "Advertencia",
  crit: "Bloqueante",
};

const tipoClasses: Record<Item["tipo"], string> = {
  ok: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  obl: "bg-rose-50 text-rose-700 ring-rose-200",
  warn: "bg-amber-50 text-amber-700 ring-amber-200",
  crit: "bg-red-50 text-red-700 ring-red-200",
};

function TipoIcon({ tipo }: { tipo: Item["tipo"] }) {
  if (tipo === "crit") return <CircleAlert className="h-4 w-4" aria-hidden="true" />;
  if (tipo === "warn") return <AlertTriangle className="h-4 w-4" aria-hidden="true" />;
  if (tipo === "obl") return <ShieldCheck className="h-4 w-4" aria-hidden="true" />;
  return <CheckCircle2 className="h-4 w-4" aria-hidden="true" />;
}

export function CumplimientoPanel({ cumplimiento }: { cumplimiento: Cumplimiento }) {
  return (
    <section className="ep-card rounded-[1.25rem] p-5" aria-label="Cumplimiento">
      <div className="mb-4 flex items-center justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.08em] text-secondary">Cumplimiento</p>
          <h2 className="font-serif text-xl font-semibold text-primary">Validaciones del acto</h2>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-2">
        <div className="rounded-lg border border-emerald-100 bg-emerald-50 p-3 text-center">
          <div className="font-serif text-2xl font-semibold text-emerald-700">{cumplimiento.tiles.cumple}</div>
          <div className="text-[11px] font-medium text-emerald-800">Cumple</div>
        </div>
        <div className="rounded-lg border border-amber-100 bg-amber-50 p-3 text-center">
          <div className="font-serif text-2xl font-semibold text-amber-700">{cumplimiento.tiles.advertencia}</div>
          <div className="text-[11px] font-medium text-amber-800">Advertencia</div>
        </div>
        <div className="rounded-lg border border-red-100 bg-red-50 p-3 text-center">
          <div className="font-serif text-2xl font-semibold text-red-700">{cumplimiento.tiles.bloqueante}</div>
          <div className="text-[11px] font-medium text-red-800">Bloqueante</div>
        </div>
      </div>

      <div className="mt-4 divide-y divide-slate-100">
        {cumplimiento.items.map((item, index) => (
          <article key={`${item.titulo}-${index}`} className="grid grid-cols-[auto_1fr] gap-x-3 py-3">
            <span className={`inline-flex h-fit items-center gap-1 rounded-md px-2 py-1 text-[10px] font-bold uppercase tracking-[0.04em] ring-1 ${tipoClasses[item.tipo]}`}>
              <TipoIcon tipo={item.tipo} />
              {tipoLabel[item.tipo]}
            </span>
            <div>
              <h3 className="text-sm font-semibold text-primary">{item.titulo}</h3>
              <p className="mt-1 text-xs leading-5 text-secondary">{item.detalle}</p>
              <p className="mt-1 font-mono text-[10px] text-secondary/80">{item.norma}</p>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
