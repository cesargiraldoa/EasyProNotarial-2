import { describe, expect, it } from "vitest";

import { defaults, diaTexto, enLetras, fechaText, genEnding, generar, money, type CompraventaState } from "../index";

describe("motor-escritura utilidades", () => {
  it("convierte numeros a letras", () => {
    expect(enLetras(0)).toBe("CERO");
    expect(enLetras(1)).toBe("UNO");
    expect(enLetras(21)).toBe("VEINTIUNO");
    expect(enLetras(1_000_000)).toBe("UN MILLÓN");
    expect(enLetras(69_714_000)).toBe("SESENTA Y NUEVE MILLONES SETECIENTOS CATORCE MIL");
  });

  it("formatea dinero con pesos colombianos", () => {
    expect(money(69_714_000)).toContain("SESENTA Y NUEVE MILLONES SETECIENTOS CATORCE MIL PESOS MONEDA LEGAL COLOMBIANA ($69.714.000)");
  });

  it("resuelve terminaciones de genero", () => {
    expect(genEnding("M")).toBe("o");
    expect(genEnding("F")).toBe("a");
    expect(genEnding("NB")).toBe("e");
    expect(genEnding("T")).toBe("e");
  });

  it("formatea fechas textuales", () => {
    expect(fechaText("2026-03-06")).toBe("seis (6) días del mes de marzo del año dos mil veintiséis (2026)");
  });

  it("formatea dias para lectura notarial", () => {
    expect(diaTexto(21)).toBe("veintiún");
    expect(diaTexto(1)).toBe("un");
  });

  it("usa tarifas del corpus cuando se inyectan", () => {
    const state = { ...(defaults.compraventa as CompraventaState), total: 1_000_000, vis: "no" } satisfies CompraventaState;
    const base = generar("compraventa", state).liquidacionHtml;
    const desdeCorpus = generar("compraventa", state, {
      tarifas: [
        { anio: 2026, concepto: "derechos_notariales_umbral_minimo", valor: 0 },
        { anio: 2026, concepto: "derechos_notariales_minimo_acto_con_cuantia", valor: 1000 },
        { anio: 2026, concepto: "derechos_notariales_por_mil", valor: 0.001 },
        { anio: 2026, concepto: "iva_sobre_derechos_notariales", valor: 0.2 },
      ],
    }).liquidacionHtml;

    expect(desdeCorpus).not.toBe(base);
    expect(desdeCorpus).toContain("$2.000");
    expect(desdeCorpus).toContain("$400");
  });
});
