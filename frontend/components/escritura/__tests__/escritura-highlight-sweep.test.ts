// @vitest-environment happy-dom
// Barrido: por cada acto, activa todos los bloques y edita TODOS los controles
// del formulario, verificando que cada uno resalta algo en el documento
// (.hl valor en el cuerpo, o .hl-sec la sección). Garantía de "todos sin excepción".
import { act, createElement, type ReactNode } from "react";
import { createRoot, type Root } from "react-dom/client";
import { beforeEach, afterEach, describe, expect, it, vi } from "vitest";
import type { ActoCode } from "@/lib/motor-escritura";
import { EscrituraWorkspace } from "../escritura-workspace";

(globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

const apiMocks = vi.hoisted(() => ({
  clasificarEscritura: vi.fn(), extraerEscritura: vi.fn(), getBibliotecaEscritura: vi.fn(),
  getCorpus: vi.fn(), getEscrituraState: vi.fn(), redactarProsaGari: vi.fn(),
  revisarEscritura: vi.fn(), saveEscrituraState: vi.fn(), generarDocumento: vi.fn(),
}));

vi.mock("next/link", async () => {
  const react = await vi.importActual<typeof import("react")>("react");
  return { default: ({ href, children, ...props }: { href: string; children?: ReactNode; className?: string }) =>
    react.createElement("a", { ...props, href }, children) };
});
vi.mock("@/lib/api-escritura", () => ({ ...apiMocks, escrituraDownloadUrl: (u: string) => u }));

const caseMeta = {
  id: 123, notary_id: 1, case_type: "escritura", act_type: "compraventa", consecutive: 12, year: 2026,
  current_state: "borrador", internal_case_number: "EP-123", official_deed_number: null, official_deed_year: null,
  updated_at: "2026-07-21T00:00:00",
};

function buttonByText(c: HTMLElement, t: string) {
  const b = Array.from(c.querySelectorAll("button")).find((i) => i.textContent?.includes(t));
  if (!b) throw new Error(`No button ${t}`); return b;
}
function setValue(el: HTMLInputElement | HTMLTextAreaElement, value: string) {
  const proto = el.tagName === "TEXTAREA" ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
  Object.getOwnPropertyDescriptor(proto, "value")?.set?.call(el, value);
  el.dispatchEvent(new Event("input", { bubbles: true }));
}

// Controles de diligencia de cumplimiento: no producen texto en el documento,
// solo activan/limpian un hallazgo en el informe normativo. Quedan fuera del
// invariante "cada control resalta algo en el cuerpo".
const DILIGENCIA_SOLO_CUMPLIMIENTO = new Set(["pep_indagado", "rupta_verificado"]);

async function sweepActo(container: HTMLElement, actoButton: string): Promise<string[]> {
  await act(async () => {
    buttonByText(container, actoButton).dispatchEvent(new MouseEvent("click", { bubbles: true }));
  });
  await act(async () => {});
  // activar todos los checkboxes → revela campos y renderiza secciones condicionales
  for (const cb of Array.from(container.querySelectorAll<HTMLInputElement>('input[type="checkbox"][id]'))) {
    if (!cb.checked) await act(async () => cb.click());
  }
  const ids = Array.from(container.querySelectorAll<HTMLElement>("input[id], select[id], textarea[id]"))
    .map((e) => e.id)
    .filter((id) => id && !DILIGENCIA_SOLO_CUMPLIMIENTO.has(id));
  const fails: string[] = [];
  for (const id of ids) {
    const el = container.ownerDocument.getElementById(id);
    if (!el) continue;
    if (el instanceof HTMLInputElement && el.type === "checkbox") {
      // Probar la acción significativa: MARCAR (revela/renderiza la sección).
      await act(async () => el.click());
      if (!el.checked) await act(async () => el.click());
    } else if (el instanceof HTMLSelectElement && el.options.length > 1) {
      await act(async () => {
        el.selectedIndex = el.selectedIndex === 0 ? 1 : 0;
        el.dispatchEvent(new Event("change", { bubbles: true }));
      });
    } else if (el instanceof HTMLInputElement || el instanceof HTMLTextAreaElement) {
      await act(async () => setValue(el, `X-${id}`));
    }
    if (container.querySelectorAll(".hl, .hl-sec").length === 0) fails.push(id);
  }
  return fails;
}

describe("resaltado: todos los campos sin excepción", () => {
  let container: HTMLDivElement;
  let root: Root;
  beforeEach(async () => {
    apiMocks.getEscrituraState.mockResolvedValue({ case_id: 123, acto: null, state: {}, case: caseMeta });
    apiMocks.getCorpus.mockImplementation(async (acto: ActoCode, fecha?: string) => ({
      acto, corpus_acto_code: acto, fecha: fecha ?? "2026-07-21", normas: [], clausulas: [], reglas: [], tarifas: [],
    }));
    apiMocks.getBibliotecaEscritura.mockResolvedValue([]);
    container = document.createElement("div");
    document.body.appendChild(container);
    root = createRoot(container);
    await act(async () => root.render(createElement(EscrituraWorkspace, { caseId: 123 })));
  });
  afterEach(() => { act(() => root.unmount()); container.remove(); vi.clearAllMocks(); });

  it("Compraventa + Hipoteca: cada control resalta algo", async () => {
    expect(await sweepActo(container, "Compraventa + Hipoteca")).toEqual([]);
  }, 60000);

  it("Cancelacion de hipoteca: cada control resalta algo", async () => {
    expect(await sweepActo(container, "Cancelacion de hipoteca")).toEqual([]);
  }, 60000);
});
