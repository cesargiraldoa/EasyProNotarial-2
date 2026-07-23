// Impresión / exportación a PDF de la escritura.
// Abre una ventana con el HTML del motor y dispara window.print() (permite
// "Guardar como PDF"). Rellena los guiones de relleno (line-leaders) que impiden
// intercalar texto al final de cada renglón/párrafo, midiéndolos al ancho de la
// página — igual que hacía el prototipo `escritura-asistida.html`.
// Devuelve false si el navegador bloqueó la ventana emergente.

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
.fill{display:inline-block;overflow:hidden;white-space:nowrap;vertical-align:bottom;color:#8a8a8a;letter-spacing:.05em}
`;

// Script que corre DENTRO de la ventana de impresión: mide cada guion de relleno
// al ancho real de la página y luego imprime.
const FILL_AND_PRINT = `
window.onload=function(){
  var LEADER=Array(401).join('\\u2014');
  var fills=document.querySelectorAll('.fill');
  var i,f;
  for(i=0;i<fills.length;i++){f=fills[i];f.textContent=LEADER;f.style.width='0px';}
  for(i=0;i<fills.length;i++){
    f=fills[i];var host=f.parentElement;if(!host)continue;
    var cs=getComputedStyle(host);
    var right=host.getBoundingClientRect().right-parseFloat(cs.paddingRight||0);
    var left=f.getBoundingClientRect().left;
    var w=right-left-2;
    f.style.width=(w>4?w:0)+'px';
  }
  setTimeout(function(){window.focus();window.print();},80);
};
`;

// Garantiza un guion de relleno al final de cada cláusula y parágrafo.
function ensureFillLeaders(html: string): string {
  if (typeof document === "undefined") return html;
  const root = document.createElement("div");
  root.innerHTML = html;
  root.querySelectorAll<HTMLElement>("p.cl, p.para").forEach((block) => {
    const last = block.lastElementChild;
    if (!(last && last.classList.contains("fill"))) {
      const span = document.createElement("span");
      span.className = "fill";
      block.appendChild(span);
    }
  });
  return root.innerHTML;
}

export function printEscrituraHtml(html: string): boolean {
  // Nota: NO usar "noopener"/"noreferrer" aquí — con esas flags el navegador
  // devuelve null y solo queda una pestaña en blanco imposible de escribir.
  const printWindow = window.open("", "_blank");
  if (!printWindow) return false;
  printWindow.document.open();
  printWindow.document.write(
    `<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Escritura</title><style>${PRINT_CSS}</style></head>` +
      `<body><article class="sheet">${ensureFillLeaders(html)}</article>` +
      `<script>${FILL_AND_PRINT}<\/script>` +
      `</body></html>`,
  );
  printWindow.document.close();
  return true;
}
