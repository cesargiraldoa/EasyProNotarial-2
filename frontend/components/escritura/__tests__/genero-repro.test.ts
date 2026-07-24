// @vitest-environment happy-dom
import { describe, it, expect, vi } from "vitest";
import * as React from "react";
import { act } from "react";
import { createRoot } from "react-dom/client";
import { EscrituraForm } from "../escritura-form";
import { emptyDefaults, type CaseState, type CompraventaState } from "@/lib/motor-escritura";

(globalThis as unknown as { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

describe("repro: cambio de genero en la parte", () => {
  it("al elegir Femenino, el estado y el select reflejan F", async () => {
    const container = document.createElement("div");
    document.body.appendChild(container);
    const root = createRoot(container);

    let current: CaseState = JSON.parse(JSON.stringify(emptyDefaults.compraventa));
    const onChange = vi.fn((next: CaseState) => {
      current = next;
      renderForm();
    });

    function renderForm() {
      act(() => {
        // Envolvemos en el mismo div con onChange/onInput que usa el workspace real.
        root.render(
          React.createElement(
            "div",
            { onChange: () => {}, onInput: () => {} },
            React.createElement(EscrituraForm, { acto: "compraventa", state: current, onChange }),
          ),
        );
      });
    }

    renderForm();

    const select = container.querySelector("#V-0-genero") as HTMLSelectElement | null;
    expect(select).toBeTruthy();
    expect(select!.value).toBe("M");

    const setter = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, "value")!.set!;
    act(() => {
      setter.call(select, "F");
      select!.dispatchEvent(new window.Event("change", { bubbles: true }));
    });

    // 1) el estado debe haberse actualizado
    expect((current as CompraventaState).V[0].genero).toBe("F");
    // 2) el select renderizado debe mostrar F (no revertir a M)
    const selectAfter = container.querySelector("#V-0-genero") as HTMLSelectElement | null;
    expect(selectAfter!.value).toBe("F");
  });
});
