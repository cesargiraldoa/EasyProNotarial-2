"use client";

import { Layers3 } from "lucide-react";

export function ProcessPlaceholder({
  section,
  title,
  copy,
}: {
  section: string;
  title: string;
  copy: string;
}) {
  return (
    <div className="space-y-6">
      <section className="rounded-[2rem] border border-white/90 bg-white p-6 shadow-panel">
        <div className="max-w-3xl">
          <p className="text-sm font-semibold uppercase tracking-[0.22em] text-accent">{section}</p>
          <h1 className="mt-3 text-3xl font-semibold tracking-[-0.05em] text-primary sm:text-4xl">{title}</h1>
          <p className="mt-4 text-base leading-7 text-secondary">{copy}</p>
        </div>
      </section>

      <section className="rounded-[2rem] border border-white/90 bg-white p-6 shadow-panel">
        <div className="flex items-start gap-4">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10 text-primary">
            <Layers3 className="h-6 w-6" />
          </div>
          <div>
            <h2 className="text-2xl font-semibold text-primary">Base preparada</h2>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-secondary">La navegación ya quedó ordenada alrededor del proceso documental. Este espacio está listo para conectar siguientes paquetes sin romper estructura ni UX.</p>
          </div>
        </div>
      </section>
    </div>
  );
}
