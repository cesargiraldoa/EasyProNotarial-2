import { describe, expect, it } from "vitest";

import compraventa from "../__fixtures__/compraventa.json";
import hipoteca from "../__fixtures__/hipoteca.json";
import cancelacion from "../__fixtures__/cancelacion.json";
import { defaults, generar, type ActoCode } from "../index";

interface GoldenFixture {
  doc_text: string;
  liquidacion_text: string;
  cumplimiento_items: string[];
  cumplimiento_tiles: string[];
  estado: string;
}

function normalize(html: string): string {
  return html
    .replace(/<span class="fill"[^>]*>[\s\S]*?<\/span>/g, "")
    .replace(/<\/(p|div|tr|h4|h3|li)>/g, "\n")
    .replace(/<br\s*\/?>/g, "\n")
    .replace(/<[^>]+>/g, "")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#(\d+);/g, (_match, n: string) => String.fromCharCode(Number(n)))
    .replace(/&nbsp;/g, " ")
    .replace(/—{2,}/g, "")
    .split("\n")
    .map((line) => line.replace(/[ \t]+/g, " ").trim())
    .filter(Boolean)
    .join("\n");
}

function normalizeSpaces(text: string): string {
  return text.replace(/\s+/g, " ").trim();
}

const fixtures: Record<ActoCode, GoldenFixture> = {
  compraventa,
  hipoteca,
  cancelacion,
};

describe("motor-escritura golden fixtures", () => {
  (["compraventa", "hipoteca", "cancelacion"] as const).forEach((acto) => {
    it(`reproduce el fixture de ${acto}`, () => {
      const resultado = generar(acto, defaults[acto]);
      const fixture = fixtures[acto];

      expect(normalize(resultado.html)).toBe(fixture.doc_text);
      expect(normalize(resultado.liquidacionHtml)).toBe(fixture.liquidacion_text);
      expect(resultado.cumplimiento.items.map((item) => item.titulo)).toEqual(fixture.cumplimiento_items);
      expect([
        `${resultado.cumplimiento.tiles.cumple}:Cumple`,
        `${resultado.cumplimiento.tiles.advertencia}:Advertencia`,
        `${resultado.cumplimiento.tiles.bloqueante}:Bloqueante`,
      ]).toEqual(fixture.cumplimiento_tiles);
      expect(normalizeSpaces(resultado.estado.texto)).toBe(normalizeSpaces(fixture.estado));
    });
  });
});
