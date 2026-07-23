import { describe, expect, it } from "vitest";
import { applyConditionals, fillPlantilla, formatToken, resolvePath } from "../escritura-plantilla";

const state = {
  numEscritura: "3.943",
  fechaOtorg: "2026-06-11",
  total: 160000000,
  saldo: 115850000,
  inicial: 0,
  derecho: "dominio",
  ph: true,
  credito: true,
  vis: "no",
  subsidio: false,
  V: [{ nombre: "JHON BYRON TRUJILLO DURAN", id: "15.485.004", estado: "casado_sc" }],
  C: [{ nombre: "MAURICIO TRUJILLO ROLDAN", id: "1.128.391.299", estado: "soltero" }],
};

describe("resolvePath", () => {
  it("resuelve rutas anidadas con índices de array", () => {
    expect(resolvePath(state, "V.0.nombre")).toBe("JHON BYRON TRUJILLO DURAN");
    expect(resolvePath(state, "C.0.id")).toBe("1.128.391.299");
    expect(resolvePath(state, "no.existe")).toBeUndefined();
  });
});

describe("formatToken", () => {
  it("formatea moneda, fecha y enums", () => {
    expect(formatToken("total", 160000000)).toBe("$160.000.000");
    expect(formatToken("fechaOtorg", "2026-06-11")).toBe("11 de junio de 2026");
    expect(formatToken("derecho", "dominio")).toBe("el derecho de dominio");
    expect(formatToken("V.0.estado", "casado_sc")).toBe("casado(a) con sociedad conyugal vigente");
  });
  it("montos en cero quedan vacíos", () => {
    expect(formatToken("inicial", 0)).toBe("");
  });
});

describe("applyConditionals", () => {
  it("mantiene bloques verdaderos y elimina falsos", () => {
    const html = "[[if credito]]HIPOTECA[[/if]][[if vis]]VIS[[/if]]";
    expect(applyConditionals(html, state)).toBe("HIPOTECA");
  });
  it("evalúa membresía in", () => {
    const html = "[[if C.0.estado in casado_sc|union]]RATIF[[/if]]";
    expect(applyConditionals(html, state)).toBe("");
    expect(applyConditionals(html, { C: [{ estado: "union" }] })).toBe("RATIF");
  });
  it("soporta anidamiento", () => {
    const html = "[[if credito]]A[[if vis]]B[[/if]]C[[/if]]";
    expect(applyConditionals(html, state)).toBe("AC");
  });
});

describe("fillPlantilla", () => {
  it("rellena tokens y deja blancos para vacíos", () => {
    const out = fillPlantilla("Nro {{numEscritura}} — {{V.0.nombre}} — {{nupre}}", state);
    expect(out).toContain("Nro 3.943");
    expect(out).toContain("MAURICIO TRUJILLO ROLDAN".length ? "JHON BYRON TRUJILLO DURAN" : "");
    expect(out).toContain("__________");
  });
});
