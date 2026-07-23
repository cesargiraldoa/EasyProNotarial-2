// @vitest-environment happy-dom
// Correctitud: al editar un campo cuyo valor SÍ va en el cuerpo, el elemento
// resaltado (.hl) debe CONTENER el texto tecleado — no una sección cualquiera.
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

// Campos cuyo valor DEBE aparecer resaltado en el cuerpo del documento.
const VALUE_FIELDS = [
  "banco", "apoderadoBanco", "apodNombre", "tituloNum", "tituloNotaria",
  "V-0-nombre", "C-0-nombre", "V-0-id",
  "inmueble-0-matricula", "inmueble-0-descripcion", "inmueble-0-linderos", "inmueble-0-nupre",
  "enc-hip-acreedor", "enc-pat-escritura", "enc-afectacion-beneficiarios",
  "divisas-declaracion", "divisas-origen", "rural-region",
  "capacidad-autorizacion", "apoyoNombre",
  // firmas: el valor aparece en el cuerpo sin data-f → resaltado por coincidencia de texto
  "testigo-0-nombre", "ruego-nombre",
];

describe("resaltado por valor: el .hl contiene el texto tecleado", () => {
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

  it("Compraventa + Hipoteca: cada campo con valor en el cuerpo se resalta", async () => {
    await act(async () => {
      buttonByText(container, "Compraventa + Hipoteca").dispatchEvent(new MouseEvent("click", { bubbles: true }));
    });
    await act(async () => {});
    for (const cb of Array.from(container.querySelectorAll<HTMLInputElement>('input[type="checkbox"][id]'))) {
      if (!cb.checked) await act(async () => cb.click());
    }
    const wrong: string[] = [];
    for (const id of VALUE_FIELDS) {
      const el = container.ownerDocument.getElementById(id) as HTMLInputElement | HTMLTextAreaElement | null;
      if (!el) { wrong.push(`${id}(no-render)`); continue; }
      const uniq = `ZQX${id.replace(/[^a-zA-Z0-9]/g, "")}`;
      await act(async () => setValue(el, uniq));
      const hl = container.querySelector<HTMLElement>(".hl");
      if (!hl || !hl.textContent?.includes(uniq)) wrong.push(id);
    }
    expect(wrong, `campos que no resaltaron su valor: ${wrong.join(", ")}`).toEqual([]);
  }, 60000);
});
