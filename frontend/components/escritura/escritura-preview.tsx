"use client";

import { useEffect, useRef } from "react";
import styles from "./escritura-preview.module.css";
import { applyHighlight, fillLeaders, useNormaTooltip } from "./escritura-preview-fx";

type Props = {
  html: string;
  /** Id del último campo editado en el formulario (para resaltarlo en la escritura). */
  lastId?: string | null;
  /** Valor tecleado del último campo editado (para resaltar por coincidencia de texto). */
  lastValue?: string | null;
  /** Contador que cambia en cada edición para re-disparar el resaltado aunque el id se repita. */
  highlightTick?: number;
};

export function EscrituraPreview({ html, lastId = null, lastValue = null, highlightTick = 0 }: Props) {
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
    const target = applyHighlight(root, lastId, lastValue);
    if (!target) return;
    // Centra el cambio en el preview (que tiene su propio scroll, no mueve el form).
    target.scrollIntoView({ behavior: "smooth", block: "center" });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [html, lastId, lastValue, highlightTick]);

  return (
    <section className={styles.previewShell} aria-label="Vista previa de la escritura">
      <div ref={sheetRef} className={styles.sheet} dangerouslySetInnerHTML={{ __html: html }} />
    </section>
  );
}
