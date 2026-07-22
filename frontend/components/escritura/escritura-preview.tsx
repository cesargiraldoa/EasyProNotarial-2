"use client";

import { useEffect, useRef } from "react";
import styles from "./escritura-preview.module.css";
import { applyHighlight, fillLeaders, useNormaTooltip } from "./escritura-preview-fx";

type Props = {
  html: string;
  /** Id del último campo editado en el formulario (para resaltarlo en la escritura). */
  lastId?: string | null;
  /** Contador que cambia en cada edición para re-disparar el resaltado aunque el id se repita. */
  highlightTick?: number;
};

function inView(el: HTMLElement): boolean {
  const rect = el.getBoundingClientRect();
  const viewport = window.innerHeight || document.documentElement.clientHeight;
  return rect.top >= 48 && rect.bottom <= viewport - 8;
}

export function EscrituraPreview({ html, lastId = null, highlightTick = 0 }: Props) {
  const sheetRef = useRef<HTMLDivElement>(null);

  useNormaTooltip(sheetRef, html);

  // Guiones de relleno: rellenar/medir tras cada render y al redimensionar la ventana.
  useEffect(() => {
    const root = sheetRef.current;
    if (!root) return;
    fillLeaders(root);
    let raf = 0;
    function onResize() {
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => {
        if (sheetRef.current) fillLeaders(sheetRef.current);
      });
    }
    window.addEventListener("resize", onResize);
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", onResize);
    };
  }, [html]);

  useEffect(() => {
    const root = sheetRef.current;
    if (!root) return;
    const target = applyHighlight(root, lastId);
    if (!target) return;
    // flash breve para llamar la atención sobre el cambio
    target.classList.remove("flash");
    void target.offsetWidth;
    target.classList.add("flash");
    const timer = setTimeout(() => target.classList.remove("flash"), 1600);
    if (!inView(target)) {
      target.scrollIntoView({ behavior: "smooth", block: "center" });
    }
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [html, lastId, highlightTick]);

  return (
    <section className={styles.previewShell} aria-label="Vista previa de la escritura">
      <div ref={sheetRef} className={styles.sheet} dangerouslySetInnerHTML={{ __html: html }} />
    </section>
  );
}
