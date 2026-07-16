import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";

const source = fs.readFileSync(new URL("../onlyoffice-plugin/biblioteca/template-editor.js", import.meta.url), "utf8");
const html = fs.readFileSync(new URL("../onlyoffice-plugin/biblioteca/index.html", import.meta.url), "utf8");
const config = JSON.parse(fs.readFileSync(new URL("../onlyoffice-plugin/biblioteca/config.json", import.meta.url), "utf8"));

test("template editor inserts literal curly marker without backend cascade", () => {
  assert.match(source, /var marker = "\{\{" \+ selectedCode \+ "\}\}"/);
  assert.match(source, /InsertAndReplaceContentControls/);
  assert.match(source, /SetHighlight/);
  assert.doesNotMatch(source, /actualizar-campo/);
  assert.doesNotMatch(source, /solicitarRecarga/);
});

test("template editor supports creating a missing catalog field", () => {
  assert.match(source, /\/api\/v1\/biblioteca\/campos/);
  assert.match(source, /method: "POST"/);
  assert.match(source, /Crear e insertar/);
});

test("plugin exposes explicit select and insert controls", () => {
  assert.match(source, /Etiqueta seleccionada:/);
  assert.match(source, /Insertar en el cursor/);
  assert.match(html, /Biblioteca de etiquetas/);
  assert.match(html, /template-editor\.js\?v=2\.3\.0/);
  assert.equal(config.version, "2.3.0");
});
