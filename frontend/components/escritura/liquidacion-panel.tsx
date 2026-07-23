"use client";

import { useRef } from "react";
import { ReceiptText } from "lucide-react";
import styles from "./escritura-preview.module.css";
import { useNormaTooltip } from "./escritura-preview-fx";

export function LiquidacionPanel({ html }: { html: string }) {
  const ref = useRef<HTMLDivElement>(null);
  useNormaTooltip(ref, html);
  return (
    <section className="ep-card rounded-[1.25rem] p-5" aria-label="Liquidacion">
      <div className="mb-4 flex items-center gap-3">
        <span className="inline-flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 text-primary">
          <ReceiptText className="h-5 w-5" aria-hidden="true" />
        </span>
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.08em] text-secondary">Liquidacion</p>
          <h2 className="font-serif text-xl font-semibold text-primary">Gastos y tributos</h2>
        </div>
      </div>
      <div ref={ref} className={styles.liquidacionHtml} dangerouslySetInnerHTML={{ __html: html }} />
    </section>
  );
}
