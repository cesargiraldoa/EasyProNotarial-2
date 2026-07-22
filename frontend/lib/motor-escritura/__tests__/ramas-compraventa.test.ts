import { describe, expect, it } from "vitest";

import { defaults, generar, type CompraventaState } from "../index";

function state(overrides: Partial<CompraventaState>): CompraventaState {
  return JSON.parse(JSON.stringify({ ...(defaults.compraventa as CompraventaState), ...overrides })) as CompraventaState;
}

describe("motor-escritura ramas comunes de compraventa", () => {
  it("enumera varios inmuebles y exige matrícula/linderos por inmueble", () => {
    const s = state({
      inmuebles: [
        {
          descripcion: "APARTAMENTO 101 TORRE A",
          matricula: "001-111111",
          linderos: "Norte con zona comun.",
          catastral: "050010001",
          nupre: "NUPRE-001",
          avaluoCatastral: 100_000_000,
        },
        {
          descripcion: "PARQUEADERO 12 SOTANO",
          matricula: "",
          linderos: "",
          catastral: "050010002",
          nupre: "NUPRE-002",
          avaluoCatastral: 20_000_000,
        },
      ],
    });

    const resultado = generar("compraventa", s);

    expect(resultado.html).toContain("DESCRIPCIÓN DE LOS BIENES INMUEBLES");
    expect(resultado.html).toContain("APARTAMENTO 101 TORRE A");
    expect(resultado.html).toContain("PARQUEADERO 12 SOTANO");
    expect(resultado.html).toContain("NUPRE-002");
    expect(resultado.cumplimiento.items.map((item) => item.titulo)).toContain("Inmueble 2 no plenamente identificado");
    expect(resultado.cumplimiento.items.map((item) => item.titulo)).toContain("Faltan los linderos del inmueble 2");
    expect(resultado.cumplimiento.tiles.bloqueante).toBeGreaterThanOrEqual(2);
  });

  it("agrega párrafo y advertencia para folio segregado", () => {
    const resultado = generar("compraventa", state({ folioEstado: "segregado" }));

    expect(resultado.html).toContain("Estado del folio: Segregado");
    expect(resultado.html).toContain("Ley 1579/2012");
    expect(resultado.cumplimiento.items.map((item) => item.titulo)).toContain("Estado del folio: Segregado");
    expect(resultado.cumplimiento.tiles.advertencia).toBeGreaterThan(0);
  });

  it("cita Ley 1561/2012 para falsa tradición", () => {
    const resultado = generar("compraventa", state({ folioEstado: "falsa_tradicion" }));

    expect(resultado.html).toContain("Estado del folio: Falsa tradición");
    expect(resultado.html).toContain("Ley 1561/2012");
    expect(resultado.cumplimiento.items.find((item) => item.titulo === "Estado del folio: Falsa tradición")?.norma).toBe("Ley 1561/2012");
  });

  it("apila encadenamientos en el orden canónico", () => {
    const resultado = generar(
      "compraventa",
      state({
        gravamen: "hipoteca_previa",
        encadenamientos: {
          cancelacionHipotecaPrevia: true,
          cancelacionPatrimonioFamilia: true,
          afectacionViviendaFamiliar: true,
          hipotecaPrevia: {
            acreedor: "BANCO TEST S.A.",
            nit: "900.111.222-3",
            escritura: "1234",
            fecha: "2020-01-20",
            notaria: "Notaría 1 de Medellín",
            registroFecha: "2020-02-03",
            orip: "Medellín Zona Sur",
          },
          patrimonioFamilia: {
            escritura: "5678",
            fecha: "2018-05-10",
            notaria: "Notaría 2 de Medellín",
            beneficiarios: "los compradores",
          },
          afectacion: {
            beneficiarios: "LAURA XIMENA ORTIZ VÉLEZ",
          },
        },
      }),
    );

    const hipoteca = resultado.html.indexOf("ACTO PREVIO: CANCELACIÓN DE HIPOTECA");
    const patrimonio = resultado.html.indexOf("ACTO PREVIO: CANCELACIÓN DE PATRIMONIO DE FAMILIA");
    const afectacion = resultado.html.indexOf("ACTO POSTERIOR: AFECTACIÓN A VIVIENDA FAMILIAR");

    expect(hipoteca).toBeGreaterThan(-1);
    expect(patrimonio).toBeGreaterThan(hipoteca);
    expect(afectacion).toBeGreaterThan(patrimonio);
    expect(resultado.html).toContain("BANCO TEST S.A.");
    expect(resultado.cumplimiento.items.map((item) => item.titulo)).toContain("Cancelación de hipoteca previa encadenada");
  });

  it("activa cláusula de divisas para extranjero no residente", () => {
    const base = state({
      divisas: {
        parteExtranjeraNoResidente: true,
        pagoDivisas: true,
        moneda: "USD",
        valorDivisas: 100000,
        paisOrigenFondos: "Estados Unidos",
        declaracionCambio: "Formulario No. 4",
        canalizacionMercadoCambiario: false,
        registroInversionExtranjera: false,
      },
    });
    base.C = [{ ...base.C[0], tipoDoc: "PA", nombre: "MARIA FOREIGN TEST" }];

    const resultado = generar("compraventa", base);

    expect(resultado.html).toContain("Extranjería, no residencia y régimen cambiario");
    expect(resultado.html).toContain("Banco de la República");
    expect(resultado.html).toContain("Circular DCIN Banrep");
    expect(resultado.html).toContain("Formulario No. 4");
    expect(resultado.cumplimiento.items.map((item) => item.titulo)).toContain("Canalización por mercado cambiario pendiente");
    expect(resultado.cumplimiento.items.map((item) => item.titulo)).toContain("Registro de inversión extranjera pendiente");
  });

  it("bloquea predio rural que supera UAF sin autorización", () => {
    const resultado = generar(
      "compraventa",
      state({
        ph: false,
        rural: {
          predioRural: true,
          baldioAdjudicado: true,
          restriccionTemporal: true,
          superaUaf: true,
          autorizacionAnt: false,
          derechoPreferencia: true,
          municipioRegionUaf: "Urabá antioqueño",
          areaHectareas: 80,
          uafHectareas: 40,
        },
      }),
    );

    expect(resultado.html).toContain("Predio rural, UAF y baldíos");
    expect(resultado.html).toContain("arts. 39 y 72 · Ley 160/1994");
    expect(resultado.cumplimiento.items).toContainEqual(expect.objectContaining({ tipo: "crit", titulo: "UAF excedida sin autorización" }));
    expect(resultado.cumplimiento.tiles.bloqueante).toBeGreaterThan(0);
  });

  it("redacta venta de bien de menor con autorización por validar", () => {
    const resultado = generar(
      "compraventa",
      state({
        capacidad: {
          menorVendedor: true,
          ventaBienMenor: true,
          autorizacionVentaMenor: false,
          autorizacionDetalle: "auto judicial del Juzgado Primero de Familia",
          discapacidadConApoyos: true,
          apoyoAcreditado: true,
          apoyoNombre: "ANA APOYO TEST",
          apoyoDocumento: "C.C. 1.000.000",
          apoyoTipo: "acuerdo",
        },
      }),
    );

    expect(resultado.html).toContain("Capacidad, representación y apoyos");
    expect(resultado.html).toContain("capacidad legal plena");
    expect(resultado.html).toContain("auto judicial del Juzgado Primero de Familia");
    expect(resultado.html.toLowerCase()).not.toContain("incapaz");
    expect(resultado.cumplimiento.items.map((item) => item.titulo)).toContain("Venta de bien de menor sin autorización");
  });
});
