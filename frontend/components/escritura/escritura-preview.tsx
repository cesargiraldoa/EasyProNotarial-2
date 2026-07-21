import styles from "./escritura-preview.module.css";

export function EscrituraPreview({ html }: { html: string }) {
  return (
    <section className={styles.previewShell} aria-label="Vista previa de la escritura">
      <div className={styles.sheet} dangerouslySetInnerHTML={{ __html: html }} />
    </section>
  );
}
