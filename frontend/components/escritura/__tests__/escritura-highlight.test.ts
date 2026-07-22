// @vitest-environment happy-dom
import { act, createElement, type ReactNode } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { ActoCode } from "@/lib/motor-escritura";
import { EscrituraWorkspace } from "../escritura-workspace";

(globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

const apiMocks = vi.hoisted(() => ({
  clasificarEscritura: vi.fn(),
  extraerEscritura: vi.fn(),
  getBibliotecaEscritura: vi.fn(),
  getCorpus: vi.fn(),
  getEscrituraState: vi.fn(),
  redactarProsaGari: vi.fn(),
  revisarEscritura: vi.fn(),
  saveEscrituraState: vi.fn(),
  generarDocumento: vi.fn(),
}));

vi.mock("next/link", async () => {
  const react = await vi.importActual<typeof import("react")>("react");
  return {
    default: ({ href, children, ...props }: { href: string; children?: ReactNode; className?: string }) =>
      react.createElement("a", { ...props, href }, children),
  };
});

vi.mock("@/lib/api-escritura", () => ({
  clasificarEscritura: apiMocks.clasificarEscritura,
  extraerEscritura: apiMocks.extraerEscritura,
  getBibliotecaEscritura: apiMocks.getBibliotecaEscritura,
  getCorpus: apiMocks.getCorpus,
  getEscrituraState: apiMocks.getEscrituraState,
  redactarProsaGari: apiMocks.redactarProsaGari,
  revisarEscritura: apiMocks.revisarEscritura,
  saveEscrituraState: apiMocks.saveEscrituraState,
  generarDocumento: apiMocks.generarDocumento,
  escrituraDownloadUrl: (u: string) => u,
}));

const caseMeta = {
  id: 123, notary_id: 1, case_type: "escritura", act_type: "compraventa", consecutive: 12, year: 2026,
  current_state: "borrador", internal_case_number: "EP-123", official_deed_number: null, official_deed_year: null,
  updated_at: "2026-07-21T00:00:00",
};

function wait(ms: number) { return new Promise((r) => window.setTimeout(r, ms)); }
async function waitFor(assertion: () => void) {
  const started = Date.now();
  let lastError: unknown;
  while (Date.now() - started < 1500) {
    try { assertion(); return; } catch (e) { lastError = e; await act(async () => { await wait(20); }); }
  }
  throw lastError;
}
function buttonByText(c: HTMLElement, t: string) {
  const b = Array.from(c.querySelectorAll("button")).find((i) => i.textContent?.includes(t));
  if (!b) throw new Error(`No button ${t}`); return b;
}
function inputByLabel(c: HTMLElement, t: string) {
  const l = Array.from(c.querySelectorAll("label")).find((i) => i.textContent?.trim() === t);
  if (!l?.htmlFor) throw new Error(`No label ${t}`);
  const i = c.ownerDocument.getElementById(l.htmlFor) as HTMLInputElement | null;
  if (!i) throw new Error(`No input ${t}`); return i;
}
function setInputValue(input: HTMLInputElement, value: string) {
  const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value")?.set;
  setter?.call(input, value);
  input.dispatchEvent(new Event("input", { bubbles: true }));
}

describe("DIAG integración resaltado", () => {
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
    await act(async () => { root.render(createElement(EscrituraWorkspace, { caseId: 123 })); });
  });
  afterEach(() => { act(() => root.unmount()); container.remove(); vi.clearAllMocks(); });

  it("editar Precio total resalta [data-f=total] en el preview", async () => {
    await act(async () => {
      buttonByText(container, "Compraventa").dispatchEvent(new MouseEvent("click", { bubbles: true }));
    });
    await waitFor(() => { expect(container.textContent).toContain("PRIMERO: OBJETO"); });

    const totalInput = inputByLabel(container, "Precio total");
    await act(async () => { setInputValue(totalInput, "500000000"); });

    await waitFor(() => {
      const hlTotal = container.querySelector<HTMLElement>('[data-f="total"].hl');
      expect(hlTotal).toBeTruthy();
      // amarillo aplicado inline (no depende del CSS)
      expect(hlTotal?.style.backgroundColor).not.toBe("");
    });
  });

  it("editar un campo sin data-f (direccion) resalta su valor por coincidencia de texto", async () => {
    await act(async () => {
      buttonByText(container, "Compraventa").dispatchEvent(new MouseEvent("click", { bubbles: true }));
    });
    await waitFor(() => { expect(container.textContent).toContain("PRIMERO: OBJETO"); });

    // "Direccion" del vendedor 1 (V-0-direccion): no tiene data-f, pero su valor
    // sí aparece en el cuerpo (bloque de notificaciones) → resaltado por texto.
    const dir = inputByLabel(container, "Direccion");
    await act(async () => { setInputValue(dir, "CALLE 30 SUR 27-45"); });

    await waitFor(() => {
      const hl = container.querySelector<HTMLElement>(".hl");
      expect(hl?.textContent).toContain("CALLE 30 SUR 27-45");
      expect(hl?.style.backgroundColor).not.toBe("");
    });
  });
});
