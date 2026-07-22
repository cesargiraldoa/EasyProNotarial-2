import { describe, it, expect } from "vitest";
import { sectionForId } from "../escritura-preview-fx";

// data-sec que REALMENTE emite el motor (lib/motor-escritura/index.ts).
const REAL_SECS = new Set([
  "aceptacion", "acreedor", "capacidad-apoyos", "comparecencia", "divisas",
  "enc-afectacion-vivienda", "enc-cancelacion-hipoteca", "enc-cancelacion-patrimonio",
  "estado-folio", "firmas", "fiscal", "hipoteca", "ley258", "liquidacion", "notas",
  "objeto", "otorgamiento", "ph", "precio", "primero", "protocolizacion", "rural-uaf",
  "saneamiento", "segundo", "sincuantia", "tercero", "titulo", "vis",
]);

// Los ids reales del form usan el lado en MAYÚSCULA: V-0-…, C-0-…
const partyIds = (side: "V" | "C") =>
  ["tipo", "nombre", "id", "cuota", "ciudad", "repr", "tipoDoc", "genero", "estado", "direccion", "telefono", "ocupacion", "correo", "notiElec", "pep"].map(
    (k) => `${side}-0-${k}`,
  );

const COMPRAVENTA_IDS = [
  "derecho", "tipoNegocio", "folioEstado", "total", "inicial", "saldo", "subsidio", "subsidioEnt",
  "banco", "bancoNit", "plazoAnios", "numCuotas", "apoderadoBanco", "poderBancoEP", "poderBancoNot",
  "apoderado", "apodNombre", "apodPoder", "fechaOtorg", "pep", "ph", "phReg", "vis", "afectada",
  "tituloNum", "tituloFecha", "tituloNotaria", "tituloTipo", "posesion2", "numEscritura",
  "firmaRuego", "interprete",
  "menorVendedor", "ventaBienMenor", "discapacidadConApoyos", "autorizacionVentaMenor",
  "capacidad-autorizacion", "apoyoAcreditado", "apoyoNombre", "apoyoDocumento", "apoyoActo",
  "enc-hip-acreedor", "enc-hip-nit", "enc-hip-escritura", "enc-hip-fecha", "enc-hip-notaria", "enc-hip-registro", "enc-hip-orip",
  "enc-pat-escritura", "enc-pat-fecha", "enc-pat-notaria", "enc-pat-beneficiarios", "enc-afectacion-beneficiarios",
  "divisas-moneda", "divisas-valor", "divisas-declaracion", "divisas-origen", "divisas-canalizacion", "divisas-registro", "divisas-apostilla",
  "rural-area", "rural-uaf", "rural-region", "rural-baldio", "rural-restriccion", "rural-supera-uaf", "rural-autorizacion-ant", "rural-preferencia",
  "inmueble-0-descripcion", "inmueble-0-linderos", "inmueble-0-matricula", "inmueble-0-catastral", "inmueble-0-avaluo", "inmueble-0-nupre",
  ...partyIds("V"), ...partyIds("C"),
  "testigo-0-nombre", "testigo-0-tipoDoc", "testigo-0-id", "testigo-0-ciudad", "ruego-nombre", "ruego-id",
];

const CANCELACION_IDS = [
  "cBanco", "cBancoNit", "cBancoDom", "cRepTipo", "cRepCargo", "cPoderEP", "cPoderFecha", "cPoderNotaria",
  "cApoNombre", "cApoCC", "cApoGenero", "cDeudor", "cHipEP", "cHipFecha", "cHipNotaria", "cHipRegFecha",
  "cHipMonto", "cOrip", "cInmdesc", "cMatricula", "cCatastral", "cNupre", "cNum", "cFechaOtorg",
  "cNotario", "cNotarioGenero", "cCalidad", "cActoAdmin", "cHojas", "cRecaudo", "cCorreoNotif",
  "cSinCuantia", "cNoPazSalvo", "cSarlaft", "cNotiElec",
];

describe("cobertura de resaltado: todo campo resuelve a una sección real", () => {
  for (const id of [...COMPRAVENTA_IDS, ...CANCELACION_IDS]) {
    it(`${id} → sección conocida`, () => {
      const sec = sectionForId(id);
      expect(sec, `sin sección para "${id}"`).not.toBeNull();
      expect(REAL_SECS.has(sec as string), `sección inválida "${sec}" para "${id}"`).toBe(true);
    });
  }
});
