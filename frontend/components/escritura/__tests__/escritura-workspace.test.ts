// @vitest-environment happy-dom

import { act, createElement, type ReactNode } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { ActoCode } from "@/lib/motor-escritura";
import { EscrituraWorkspace } from "../escritura-workspace";

(globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

const apiMocks = vi.hoisted(() => ({
  getCorpus: vi.fn(),
  getEscrituraState: vi.fn(),
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
  getCorpus: apiMocks.getCorpus,
  getEscrituraState: apiMocks.getEscrituraState,
  saveEscrituraState: apiMocks.saveEscrituraState,
  generarDocumento: apiMocks.generarDocumento,
  escrituraDownloadUrl: (downloadUrl: string) => downloadUrl,
}));

const caseMeta = {
  id: 123,
  notary_id: 1,
  case_type: "escritura",
  act_type: "compraventa",
  consecutive: 12,
  year: 2026,
  current_state: "borrador",
  internal_case_number: "EP-123",
  official_deed_number: null,
  official_deed_year: null,
  updated_at: "2026-07-21T00:00:00",
};

function wait(ms: number) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

async function waitFor(assertion: () => void) {
  const started = Date.now();
  let lastError: unknown;
  while (Date.now() - started < 1500) {
    try {
      assertion();
      return;
    } catch (error) {
      lastError = error;
      await act(async () => {
        await wait(20);
      });
    }
  }
  throw lastError;
}

function buttonByText(container: HTMLElement, text: string) {
  const button = Array.from(container.querySelectorAll("button")).find((item) => item.textContent?.includes(text));
  if (!button) throw new Error(`No button found for ${text}`);
  return button;
}

function inputByLabel(container: HTMLElement, text: string) {
  const label = Array.from(container.querySelectorAll("label")).find((item) => item.textContent?.trim() === text);
  if (!label?.htmlFor) throw new Error(`No label found for ${text}`);
  const input = container.ownerDocument.getElementById(label.htmlFor) as HTMLInputElement | null;
  if (!input) throw new Error(`No input found for ${text}`);
  return input;
}

function setInputValue(input: HTMLInputElement, value: string) {
  const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value")?.set;
  setter?.call(input, value);
  input.dispatchEvent(new Event("input", { bubbles: true }));
}

function editorNode(container: HTMLElement) {
  const editor = container.querySelector<HTMLElement>('[aria-label="Editor de redaccion"]');
  if (!editor) throw new Error("No editor found");
  return editor;
}

function buttonByLabel(container: HTMLElement, label: string) {
  const button = Array.from(container.querySelectorAll("button")).find((item) => item.getAttribute("aria-label") === label);
  if (!button) throw new Error(`No button found for label ${label}`);
  return button;
}

function selectText(container: HTMLElement, text: string) {
  const stack: Node[] = Array.from(container.childNodes).reverse();
  while (stack.length) {
    const current = stack.pop();
    if (!current) continue;
    if (current.nodeType !== window.Node.TEXT_NODE) {
      stack.push(...Array.from(current.childNodes).reverse());
      continue;
    }
    const value = current.textContent ?? "";
    const index = value.indexOf(text);
    if (index >= 0) {
      const range = document.createRange();
      range.setStart(current, index);
      range.setEnd(current, index + text.length);
      const selection = window.getSelection();
      selection?.removeAllRanges();
      selection?.addRange(range);
      container.dispatchEvent(new MouseEvent("mouseup", { bubbles: true }));
      return;
    }
  }
  throw new Error(`Text not found: ${text}`);
}

async function openRedaccion(container: HTMLElement) {
  await act(async () => {
    buttonByText(container, "Redaccion").dispatchEvent(new MouseEvent("click", { bubbles: true }));
  });
  await waitFor(() => {
    expect(editorNode(container).textContent).toContain("PRIMERO: OBJETO DEL NEGOCIO");
  });
}

describe("EscrituraWorkspace", () => {
  let container: HTMLDivElement;
  let root: Root;

  beforeEach(async () => {
    apiMocks.getEscrituraState.mockResolvedValue({ case_id: 123, acto: null, state: {}, case: caseMeta });
    apiMocks.getCorpus.mockImplementation(async (acto: ActoCode, fecha?: string) => ({
      acto,
      corpus_acto_code: acto === "cancelacion" ? "cancelacion_hipoteca" : acto,
      fecha: fecha ?? "2026-07-21",
      normas: [],
      clausulas: [],
      reglas: [],
      tarifas: [],
    }));
    container = document.createElement("div");
    document.body.appendChild(container);
    root = createRoot(container);
    await act(async () => {
      root.render(createElement(EscrituraWorkspace, { caseId: 123 }));
    });
  });

  afterEach(() => {
    act(() => {
      root.unmount();
    });
    container.remove();
    vi.clearAllMocks();
  });

  it("elige un acto y actualiza el preview al editar un campo", async () => {
    await act(async () => {
      buttonByText(container, "Compraventa").dispatchEvent(new MouseEvent("click", { bubbles: true }));
    });

    await waitFor(() => {
      expect(container.textContent).toContain("PRIMERO: OBJETO DEL NEGOCIO");
    });

    const comprador = inputByLabel(container, "Nombre comprador 1");
    await act(async () => {
      setInputValue(comprador, "ANA MARIA TEST");
    });

    await waitFor(() => {
      expect(container.textContent).toContain("ANA MARIA TEST");
    });
  });

  it("en Redaccion edita un campo vinculado y propaga la cascada", async () => {
    await act(async () => {
      buttonByText(container, "Compraventa").dispatchEvent(new MouseEvent("click", { bubbles: true }));
    });
    await openRedaccion(container);

    const editor = editorNode(container);
    const firstBuyer = editor.querySelector<HTMLElement>('.campo[data-field="c0nombre"]');
    expect(firstBuyer).toBeTruthy();

    await act(async () => {
      firstBuyer!.textContent = "ANA REDACCION TEST";
      editor.dispatchEvent(new InputEvent("input", { bubbles: true, data: "T", inputType: "insertText" }));
    });

    await waitFor(() => {
      const copies = Array.from(editor.querySelectorAll<HTMLElement>('.campo[data-field="c0nombre"]'));
      expect(copies.length).toBeGreaterThan(1);
      expect(copies.every((item) => item.textContent === "ANA REDACCION TEST")).toBe(true);
    });
  });

  it("inserta una clausula de biblioteca en Redaccion", async () => {
    await act(async () => {
      buttonByText(container, "Compraventa").dispatchEvent(new MouseEvent("click", { bubbles: true }));
    });
    await openRedaccion(container);

    await act(async () => {
      buttonByText(container, "Nota REDAM").dispatchEvent(new MouseEvent("click", { bubbles: true }));
    });

    await waitFor(() => {
      expect(editorNode(container).textContent).toContain("Registro de Deudores Alimentarios");
    });
  });

  it("aplica resaltado y comentario sobre la seleccion", async () => {
    await act(async () => {
      buttonByText(container, "Compraventa").dispatchEvent(new MouseEvent("click", { bubbles: true }));
    });
    await openRedaccion(container);

    const editor = editorNode(container);
    selectText(editor, "PRIMERO");
    await act(async () => {
      buttonByLabel(container, "Resaltar Amarillo").dispatchEvent(new MouseEvent("click", { bubbles: true }));
    });
    expect(editor.querySelector(".mark.hl")).toBeTruthy();

    selectText(editor, "OBJETO");
    await act(async () => {
      buttonByLabel(container, "Comentar seleccion").dispatchEvent(new MouseEvent("click", { bubbles: true }));
    });

    expect(editor.querySelector(".cmt[data-cmt]")).toBeTruthy();
    expect(container.querySelector("#comentarios textarea")).toBeTruthy();
  });
});
