// Comportamiento de cliente del preview de la escritura, portado del prototipo
// congelado `escritura-asistida.html`:
//  - applyHighlight: resaltado amarillo del último campo/sección editada (.hl / .hl-sec).
//  - useNormaTooltip: popup flotante con el detalle de la norma al pasar el mouse
//    sobre un badge de cita (.cite).

import { useEffect, type RefObject } from "react";
import { lookupNorma } from "@/lib/escritura-normas";

// Sección (data-sec REAL que emite el motor) por campo del formulario. Garantiza
// que TODO campo resalte al menos su sección aunque su valor no aparezca como
// span en el cuerpo. Se cubre por id exacto y por prefijo/patrón.
const FIELD_SECTION: Record<string, string> = {
  // objeto / inmueble
  derecho: "objeto",
  tipoNegocio: "objeto",
  inmdesc: "objeto",
  linderos: "objeto",
  matricula: "objeto",
  catastral: "objeto",
  nupre: "notas",
  avaluoCatastral: "notas",
  folioEstado: "estado-folio",
  // precio
  total: "precio",
  inicial: "precio",
  saldo: "precio",
  subsidio: "precio",
  subsidioEnt: "precio",
  // hipoteca / acreedor
  credito: "hipoteca",
  banco: "hipoteca",
  bancoNit: "hipoteca",
  plazoAnios: "hipoteca",
  numCuotas: "hipoteca",
  apoderadoBanco: "acreedor",
  poderBancoEP: "acreedor",
  poderBancoNot: "acreedor",
  // comparecencia / apoderado
  apoderado: "comparecencia",
  apodNombre: "comparecencia",
  apodPoder: "comparecencia",
  fechaOtorg: "comparecencia",
  pep: "comparecencia",
  // ph / vis / ley258
  ph: "ph",
  phReg: "ph",
  vis: "vis",
  afectada: "ley258",
  // titulo
  tituloNum: "titulo",
  tituloFecha: "titulo",
  tituloNotaria: "titulo",
  tituloTipo: "titulo",
  gravamen: "saneamiento",
  // fiscal / otorgamiento / firmas
  posesion2: "fiscal",
  numEscritura: "otorgamiento",
  firmaRuego: "firmas",
  interprete: "firmas",
  testigos: "firmas",
  huella: "firmas",
  hojaInicial: "firmas",
  // capacidad / apoyos
  menorVendedor: "capacidad-apoyos",
  ventaBienMenor: "capacidad-apoyos",
  discapacidadConApoyos: "capacidad-apoyos",
  autorizacionVentaMenor: "capacidad-apoyos",
  apoyoAcreditado: "capacidad-apoyos",
  apoyoNombre: "capacidad-apoyos",
  apoyoDocumento: "capacidad-apoyos",
  apoyoActo: "capacidad-apoyos",
  // checkboxes que activan bloques (toggles)
  "enc-cancelacion-hipoteca": "enc-cancelacion-hipoteca",
  "enc-cancelacion-patrimonio": "enc-cancelacion-patrimonio",
  "enc-afectacion": "enc-afectacion-vivienda",
  parteExtranjeraNoResidente: "divisas",
  pagoDivisas: "divisas",
  predioRural: "rural-uaf",
  // cumplimiento / anexos (paz y salvo, debida diligencia) → notas notariales
  cuentaTercero: "notas",
  ax_tradicion: "notas",
  ax_predial: "notas",
  ax_admin: "notas",
  ax_cedulas: "notas",
};

// Alias de data-f anidado (con punto) para campos cuyo id usa guiones.
const NESTED_ENC: Record<string, string> = {
  "enc-hip-": "encadenamientos.hipotecaPrevia.",
  "enc-pat-": "encadenamientos.patrimonioFamilia.",
  "enc-afectacion-": "encadenamientos.afectacion.",
};

export function sectionForId(id: string): string | null {
  if (FIELD_SECTION[id]) return FIELD_SECTION[id];
  // prefijos de los bloques nuevos
  if (/^inmueble-/.test(id)) return "objeto";
  if (/^enc-hip-/.test(id)) return "enc-cancelacion-hipoteca";
  if (/^enc-pat-/.test(id)) return "enc-cancelacion-patrimonio";
  if (/^enc-afectacion-/.test(id)) return "enc-afectacion-vivienda";
  if (/^divisas-/.test(id)) return "divisas";
  if (/^rural-/.test(id)) return "rural-uaf";
  if (/^(capacidad-|apoyo)/.test(id)) return "capacidad-apoyos";
  // partes compraventa (ids con guiones y lado en MAYÚSCULA: V-0-…, C-0-…)
  if (/^[vV]-\d/.test(id)) return "comparecencia";
  if (/^[cC]-\d/.test(id)) return "aceptacion";
  // firmantes: testigo-N-… y ruego-…
  if (/^(testigo-|ruego-)/.test(id)) return "firmas";
  // cancelación de hipoteca (ids cXxx en camelCase, sin guiones)
  if (/^c[A-Z]/.test(id)) return sectionForCancelacion(id);
  // partes ya normalizadas (vNkey / cNkey)
  if (/^v\d/.test(id)) return "comparecencia";
  if (/^c\d/.test(id)) return "aceptacion";
  return null;
}

// Secciones reales del acto de cancelación: comparecencia, primero, segundo,
// tercero, sincuantia, firmas (no existe "otorgamiento" como en compraventa).
function sectionForCancelacion(id: string): string {
  if (/^(cBanco|cBancoNit|cBancoDom|cRep|cApo|cDeudor|cPoder|cSarlaft|cNoPazSalvo)/.test(id)) return "primero";
  if (/^(cHip|cOrip|cInmdesc|cMatricula|cCatastral|cNupre)/.test(id)) return "segundo";
  if (/^(cNum|cFechaOtorg|cNotario|cCalidad|cActoAdmin|cHojas)/.test(id)) return "tercero";
  if (/^(cCorreoNotif|cNotiElec)/.test(id)) return "firmas";
  return "sincuantia"; // cSinCuantia, cRecaudo y demás → sección sin cuantía (siempre presente)
}

// Los inputs React usan ids con guiones (`v-0-nombre`, `inmueble-0-matricula`,
// `divisas-moneda`, `enc-hip-acreedor`) mientras el motor emite `data-f` sin
// guiones (`v0nombre`), con puntos (`divisas.moneda`) o anidado
// (`encadenamientos.hipotecaPrevia.acreedor`). Devuelve los candidatos a buscar.
function dataFCandidates(id: string): string[] {
  const out = [id];
  // partes: lado en MAYÚSCULA en el form (V-0-nombre) → data-f del motor en minúscula (v0nombre)
  const party = id.match(/^([vcVC])-(\d+)-(.+)$/);
  if (party) out.push(`${party[1].toLowerCase()}${party[2]}${party[3]}`);
  const inmueble = id.match(/^inmueble-(\d+)-(.+)$/);
  if (inmueble) {
    const key = inmueble[2] === "avaluo" ? "avaluoCatastral" : inmueble[2];
    out.push(key, `inmueble.${inmueble[1]}.${key}`);
  }
  for (const [prefix, base] of Object.entries(NESTED_ENC)) {
    if (id.startsWith(prefix)) {
      const key = id.slice(prefix.length) === "registro" ? "registroFecha" : id.slice(prefix.length);
      out.push(base + key);
    }
  }
  if (id.startsWith("divisas-")) out.push(`divisas.${id.slice("divisas-".length)}`);
  if (id === "capacidad-autorizacion") out.push("capacidad.autorizacionDetalle");
  if (id === "apoyoNombre") out.push("capacidad.apoyoNombre");
  if (id === "apoyoDocumento") out.push("capacidad.apoyoDocumento");
  if (id.includes("-")) out.push(id.replace(/-/g, "."));
  return out;
}

const HL_BG = "#fce96a";
const HL_SEC_BG = "rgba(252, 233, 106, 0.45)";

// Estilos aplicados INLINE (no dependemos del CSS module para el amarillo).
function paintField(el: HTMLElement) {
  el.classList.add("hl");
  el.style.backgroundColor = HL_BG;
  el.style.color = "#1b1e23";
  el.style.borderRadius = "3px";
  el.style.boxShadow = `0 0 0 2px ${HL_BG}`;
}
function paintSection(el: HTMLElement) {
  el.classList.add("hl-sec");
  el.style.backgroundColor = HL_SEC_BG;
  el.style.borderRadius = "5px";
  el.style.boxShadow = `0 0 0 4px ${HL_SEC_BG}`;
}
function clearPaint(el: HTMLElement) {
  el.classList.remove("hl", "hl-sec");
  el.style.backgroundColor = "";
  el.style.color = "";
  el.style.borderRadius = "";
  el.style.boxShadow = "";
}

/**
 * Aplica el resaltado del último campo editado sobre el preview ya renderizado.
 * Limpia el resaltado anterior y devuelve el elemento resaltado (para scroll/flash).
 * Usa estilos inline para que el amarillo se vea sí o sí, sin depender del CSS.
 */
export function applyHighlight(root: HTMLElement, lastId: string | null): HTMLElement | null {
  root.querySelectorAll<HTMLElement>(".hl, .hl-sec").forEach(clearPaint);
  if (!lastId) return null;

  for (const candidate of dataFCandidates(lastId)) {
    const spans = root.querySelectorAll<HTMLElement>(`[data-f="${candidate}"]`);
    if (spans.length) {
      spans.forEach(paintField);
      return spans[0];
    }
  }

  const key = sectionForId(lastId);
  if (key) {
    const sec = root.querySelector<HTMLElement>(`[data-sec="${key}"]`);
    if (sec) {
      paintSection(sec);
      return sec;
    }
  }

  // Último recurso: si la sección mapeada no está renderizada (p. ej. un bloque
  // apagado), resalta la primera sección presente para que SIEMPRE haya feedback.
  const anySection = root.querySelector<HTMLElement>("[data-sec]");
  if (anySection) {
    paintSection(anySection);
    return anySection;
  }
  return null;
}

const LEADER = "—".repeat(400); // 400 rayas (—) para el guion de relleno

/**
 * Rellena los guiones de relleno (line-leaders) al final de cada cláusula y
 * parágrafo, midiéndolos para que cubran el resto del renglón hasta el margen
 * derecho — impide intercalar texto. Portado de fillLeaders() del prototipo.
 * Lee y escribe en fases separadas para forzar un solo reflujo.
 */
export function fillLeaders(root: HTMLElement): void {
  root.querySelectorAll<HTMLElement>("p.cl, p.para").forEach((block) => {
    const last = block.lastElementChild;
    if (!(last && last.classList.contains("fill"))) {
      const span = document.createElement("span");
      span.className = "fill";
      block.appendChild(span);
    }
  });

  const fills = Array.from(root.querySelectorAll<HTMLElement>(".fill"));
  // fase 1 (escritura): materializa y colapsa para medir el fin del texto
  fills.forEach((fill) => {
    fill.textContent = LEADER;
    fill.style.width = "0px";
  });
  // fase 2 (lectura): un solo reflujo para todas las mediciones
  const widths = fills.map((fill) => {
    const host = fill.parentElement;
    if (!host) return 0;
    const cs = window.getComputedStyle(host);
    const right = host.getBoundingClientRect().right - parseFloat(cs.paddingRight || "0");
    const left = fill.getBoundingClientRect().left;
    return right - left - 2;
  });
  // fase 3 (escritura): aplica el ancho restante en la última línea
  fills.forEach((fill, index) => {
    fill.style.width = `${widths[index] > 4 ? widths[index] : 0}px`;
  });
}

function esc(value: string): string {
  return value.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

/**
 * Marca los badges de cita que corresponden a una norma conocida y muestra un popup
 * flotante con su detalle al pasar el mouse / enfocar. Portado del bloque "popups" del HTML.
 */
export function useNormaTooltip(ref: RefObject<HTMLElement | null>, dep: unknown, selector = ".cite") {
  useEffect(() => {
    const root = ref.current;
    if (!root || typeof document === "undefined") return;

    root.querySelectorAll<HTMLElement>(selector).forEach((el) => {
      if (lookupNorma(el.textContent)) {
        el.classList.add("tip-norma");
        el.setAttribute("tabindex", "0");
      }
    });

    const tip = document.createElement("div");
    tip.setAttribute("role", "tooltip");
    Object.assign(tip.style, {
      position: "fixed",
      zIndex: "9999",
      maxWidth: "360px",
      background: "#fbfaf7",
      border: "1px solid #cfcbbe",
      borderRadius: "12px",
      boxShadow: "0 10px 34px rgba(0,0,0,.24)",
      padding: "14px 16px",
      fontFamily: 'system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif',
      opacity: "0",
      transform: "translateY(4px)",
      transition: "opacity .12s, transform .12s",
      pointerEvents: "none",
    });
    document.body.appendChild(tip);
    let hideTimer: ReturnType<typeof setTimeout> | null = null;

    function tippable(target: EventTarget | null): HTMLElement | null {
      if (!(target instanceof Element)) return null;
      return target.closest<HTMLElement>(`${selector}.tip-norma`);
    }

    function show(el: HTMLElement) {
      const data = lookupNorma(el.textContent);
      if (!data) return;
      tip.innerHTML =
        `<div style="font-size:11px;font-weight:700;letter-spacing:.04em;color:#31456e;display:flex;justify-content:space-between;gap:10px;align-items:center;">` +
        `<span>${esc(data.norma)}</span>` +
        (data.estado
          ? `<span style="font-size:9.5px;font-weight:700;padding:2px 7px;border-radius:5px;background:#e7f2ec;color:#2e7d53;white-space:nowrap;">${esc(data.estado)}</span>`
          : "") +
        `</div>` +
        `<h5 style="font-family:Georgia,'Times New Roman',serif;font-size:14.5px;margin:7px 0;font-weight:600;color:#1b1e23;">${esc(data.art)}</h5>` +
        `<div style="font-size:12.5px;line-height:1.55;color:#1b1e23;max-height:210px;overflow:auto;border-left:3px solid #31456e;padding:2px 0 2px 11px;white-space:pre-line;">${esc(data.texto)}</div>` +
        (data.fuente ? `<div style="font-size:10.5px;color:#7a828c;margin-top:9px;">Fuente: ${esc(data.fuente)}</div>` : "") +
        `<div style="font-size:10px;color:#b0781a;margin-top:8px;">Texto de referencia — validar contra fuente oficial.</div>`;
      tip.style.opacity = "1";
      tip.style.transform = "none";
      tip.style.pointerEvents = "auto";
      const rect = el.getBoundingClientRect();
      const tw = tip.offsetWidth;
      const th = tip.offsetHeight;
      const left = Math.min(Math.max(8, rect.left), window.innerWidth - tw - 8);
      let top = rect.top - th - 8;
      if (top < 8) top = rect.bottom + 8;
      tip.style.left = `${left}px`;
      tip.style.top = `${top}px`;
    }

    function hide() {
      tip.style.opacity = "0";
      tip.style.transform = "translateY(4px)";
      tip.style.pointerEvents = "none";
    }

    function onOver(event: Event) {
      const el = tippable(event.target);
      if (el) {
        if (hideTimer) clearTimeout(hideTimer);
        show(el);
      }
    }
    function onOut(event: Event) {
      if (tippable(event.target)) hideTimer = setTimeout(hide, 140);
    }
    function onFocusIn(event: Event) {
      const el = tippable(event.target);
      if (el) show(el);
    }
    function onFocusOut(event: Event) {
      if (tippable(event.target)) hide();
    }
    function onScroll() {
      hide();
    }
    function onTipOver() {
      if (hideTimer) clearTimeout(hideTimer);
    }
    function onTipOut() {
      hideTimer = setTimeout(hide, 140);
    }

    root.addEventListener("mouseover", onOver);
    root.addEventListener("mouseout", onOut);
    root.addEventListener("focusin", onFocusIn);
    root.addEventListener("focusout", onFocusOut);
    tip.addEventListener("mouseover", onTipOver);
    tip.addEventListener("mouseout", onTipOut);
    window.addEventListener("scroll", onScroll, true);

    return () => {
      if (hideTimer) clearTimeout(hideTimer);
      root.removeEventListener("mouseover", onOver);
      root.removeEventListener("mouseout", onOut);
      root.removeEventListener("focusin", onFocusIn);
      root.removeEventListener("focusout", onFocusOut);
      window.removeEventListener("scroll", onScroll, true);
      tip.remove();
    };
  }, [ref, dep, selector]);
}
