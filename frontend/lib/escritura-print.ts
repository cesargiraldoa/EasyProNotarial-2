// Impresión / exportación a PDF de la escritura desde el modo Captura.
// Abre una ventana con el HTML determinístico del motor y dispara window.print(),
// que permite "Guardar como PDF". Devuelve false si el navegador bloqueó la ventana.

const PRINT_CSS = `
@page{size:A4;margin:18mm}
*{box-sizing:border-box}
body{background:#fff;color:#1b1e23;font-family:Georgia,"Times New Roman",serif;font-size:12pt;line-height:1.72;margin:0}
.sheet{max-width:none;margin:0;padding:0;border:0;box-shadow:none}
.calif{border:1.5px solid #1b1e23;font-family:system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;font-size:10pt;line-height:1.5;padding:11px 13px;margin-bottom:18px}
.calif h4{font-size:9.5pt;margin:0 0 8px;text-align:center;text-transform:uppercase;letter-spacing:.05em}
.calif .r{display:grid;grid-template-columns:auto 1fr;gap:2px 12px}
.calif .k{color:#4a5058;font-size:8.5pt;text-transform:uppercase}
.calif table{width:100%;border-collapse:collapse;margin-top:6px;font-variant-numeric:tabular-nums}
.calif td{border-top:1px solid #cfcbbe;padding:3px 5px}
.calif td:last-child{text-align:right}
.cl{margin:0 0 12px;text-align:justify}
.clh{font-weight:700}
.para{margin:6px 0 0;padding-left:15px;text-align:justify}
.para .clh{font-weight:600;font-style:italic}
.ins{font-weight:600}
.sech{text-align:center}
.cite{display:none}
.fill{display:none}
`;

export function printEscrituraHtml(html: string): boolean {
  const printWindow = window.open("", "_blank", "noopener,noreferrer");
  if (!printWindow) return false;
  printWindow.document.write(
    `<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Escritura</title><style>${PRINT_CSS}</style></head>` +
      `<body><article class="sheet">${html}</article><script>window.print();</script></body></html>`,
  );
  printWindow.document.close();
  return true;
}
