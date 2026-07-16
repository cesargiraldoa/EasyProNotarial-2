import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";

const source = fs.readFileSync(new URL("../onlyoffice-plugin/biblioteca/template-editor.js", import.meta.url), "utf8");
const html = fs.readFileSync(new URL("../onlyoffice-plugin/biblioteca/index.html", import.meta.url), "utf8");
const config = JSON.parse(fs.readFileSync(new URL("../onlyoffice-plugin/biblioteca/config.json", import.meta.url), "utf8"));

test("template editor inserts literal curly marker without backend cascade", () => {
  assert.match(source, /var marker = "\{\{" \+ selectedCode \+ "\}\}"/);
  assert.match(source, /PasteText/);
  assert.match(source, /GetRangeBySelect/);
  assert.match(source, /InsertContent\(\[run\]/);
  assert.match(source, /SetHighlight/);
  assert.doesNotMatch(source, /CreateParagraph/);
  assert.doesNotMatch(source, /AddContentControl/);
  assert.doesNotMatch(source, /InsertAndReplaceContentControls/);
  assert.doesNotMatch(source, /actualizar-campo/);
  assert.doesNotMatch(source, /solicitarRecarga/);
  assert.doesNotMatch(source, /Aplicar en cascada/);
  assert.match(source, /manual verification in real OnlyOffice/);
});

test("template editor supports creating a missing catalog field", () => {
  assert.match(source, /\/api\/v1\/biblioteca\/campos/);
  assert.match(source, /method: "POST"/);
  assert.match(source, /Crear e insertar/);
  assert.match(source, /manualFieldScope/);
  assert.match(source, /catalogHasCode/);
});

test("plugin exposes explicit select and insert controls", () => {
  assert.match(source, /Etiqueta seleccionada:/);
  assert.match(source, /Insertar en el cursor/);
  assert.match(source, /Guardar plantilla y volver al formulario/);
  assert.match(source, /EASYPRO_MINUTA_TEMPLATE_RETURN_REQUEST/);
  assert.match(source, /marked-template\/editor-state/);
  assert.match(source, /attempt < 60/);
  assert.match(source, /Esperando confirmacion de guardado\.\.\. " \+ String\(attempt\) \+ "s"/);
  assert.match(html, /Biblioteca de etiquetas/);
  assert.match(html, /template-editor\.js\?v=2\.3\.0/);
  assert.equal(config.version, "2.3.0");
});
