// Comportamiento de cliente del preview de la escritura, portado del prototipo
// congelado `escritura-asistida.html`:
//  - applyHighlight: resaltado amarillo del último campo/sección editada (.hl / .hl-sec).
//  - useNormaTooltip: popup flotante con el detalle de la norma al pasar el mouse
//    sobre un badge de cita (.cite).

import { useEffect, type RefObject } from "react";
import { lookupNorma } from "@/lib/escritura-normas";

// FIELD_SEC / FALLBACK / secForId — portados 1:1 del HTML (bloque "resaltado y navegación").
const FIELD_SEC: Record<string, string> = {
  derecho: "objeto",
  credito: "hipoteca",
  banco: "hipoteca",
  bancoNit: "hipoteca",
  plazoAnios: "hipoteca",
  numCuotas: "hipoteca",
  apoderadoBanco: "acreedor",
  poderBancoEP: "acreedor",
  poderBancoNot: "acreedor",
  avaluoCatastral: "notas",
  nupre: "notas",
  apoderado: "comparecencia",
  apodNombre: "comparecencia",
  apodPoder: "comparecencia",
  afectada: "ley258",
  inmdesc: "objeto",
  linderos: "objeto",
  matricula: "objeto",
  catastral: "objeto",
  ph: "ph",
  phReg: "ph",
  vis: "vis",
  tituloNum: "titulo",
  tituloFecha: "titulo",
  tituloNotaria: "titulo",
  gravamen: "saneamiento",
  total: "precio",
  inicial: "precio",
  saldo: "precio",
  ax_tradicion: "compliance",
  ax_predial: "compliance",
  ax_admin: "compliance",
  ax_cedulas: "compliance",
  tipoNegocio: "objeto",
  tituloTipo: "titulo",
  subsidio: "precio",
  subsidioEnt: "precio",
  posesion2: "compliance",
  firmaRuego: "firmas",
  interprete: "firmas",
  pep: "compliance",
  cuentaTercero: "compliance",
  numEscritura: "otorgamiento",
  fechaOtorg: "comparecencia",
  huella: "firmas",
  testigos: "firmas",
  hojaInicial: "firmas",
};

const FALLBACK: Record<string, string> = { hipoteca: "precio", ph: "objeto", vis: "precio", ley258: "saneamiento" };

function secForId(id: string | null): string | null {
  if (!id) return null;
  if (id === "firmas") return "firmas";
  if (FIELD_SEC[id]) return FIELD_SEC[id];
  if (/^[vc]\d+(direccion|telefono|correo|ocupacion|pep|notiElec)$/.test(id)) return "firmas";
  if (/^v\d/.test(id)) return "comparecencia";
  if (/^c\d/.test(id)) return "aceptacion";
  return null;
}

// Los inputs React usan ids con guiones (`v-0-nombre`, `inmueble-0-matricula`, `divisas-moneda`)
// mientras el motor emite `data-f` sin guiones (`v0nombre`) o con puntos (`divisas.moneda`).
// Devuelve los posibles valores de `data-f` a buscar, del más específico al más laxo.
function dataFCandidates(id: string): string[] {
  const out = [id];
  const party = id.match(/^([vc])-(\d+)-(.+)$/);
  if (party) out.push(`${party[1]}${party[2]}${party[3]}`);
  const inmueble = id.match(/^inmueble-(\d+)-(.+)$/);
  if (inmueble) {
    const key = inmueble[2] === "avaluo" ? "avaluoCatastral" : inmueble[2];
    out.push(key);
    out.push(`inmueble.${inmueble[1]}.${key}`);
  }
  if (id.includes("-")) out.push(id.replace(/-/g, "."));
  return out;
}

// Clave normalizada para secForId (fallback por sección).
function sectionKeyFor(id: string): string {
  const party = id.match(/^([vc])-(\d+)-(.+)$/);
  if (party) return `${party[1]}${party[2]}${party[3]}`;
  if (/^inmueble-\d+-/.test(id)) return "matricula"; // cualquier campo de inmueble → sección objeto
  return id;
}

/**
 * Aplica el resaltado del último campo editado sobre el preview ya renderizado.
 * Limpia el resaltado anterior y devuelve el elemento resaltado (para scroll/flash).
 */
export function applyHighlight(root: HTMLElement, lastId: string | null): HTMLElement | null {
  root.querySelectorAll<HTMLElement>(".hl").forEach((el) => el.classList.remove("hl"));
  root.querySelectorAll<HTMLElement>(".hl-sec").forEach((el) => el.classList.remove("hl-sec"));
  if (!lastId) return null;

  for (const candidate of dataFCandidates(lastId)) {
    const spans = root.querySelectorAll<HTMLElement>(`[data-f="${candidate}"]`);
    if (spans.length) {
      spans.forEach((span) => span.classList.add("hl"));
      return spans[0];
    }
  }

  const key = secForId(sectionKeyFor(lastId));
  if (key && key !== "compliance") {
    const sec =
      root.querySelector<HTMLElement>(`[data-sec="${key}"]`) ||
      (FALLBACK[key] ? root.querySelector<HTMLElement>(`[data-sec="${FALLBACK[key]}"]`) : null);
    if (sec) {
      sec.classList.add("hl-sec");
      return sec;
    }
  }
  return null;
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
