import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";
import vm from "node:vm";

const source = fs.readFileSync(new URL("../onlyoffice-plugin/biblioteca/template-editor.js", import.meta.url), "utf8");
const html = fs.readFileSync(new URL("../onlyoffice-plugin/biblioteca/index.html", import.meta.url), "utf8");
const config = JSON.parse(fs.readFileSync(new URL("../onlyoffice-plugin/biblioteca/config.json", import.meta.url), "utf8"));

function makeElement(id = "") {
  return {
    id,
    value: "",
    style: {},
    className: "",
    textContent: "",
    innerHTML: "",
    disabled: false,
    children: [],
    listeners: {},
    parentNode: null,
    appendChild(child) {
      child.parentNode = this;
      this.children.push(child);
    },
    insertBefore(child) {
      child.parentNode = this;
      this.children.push(child);
    },
    addEventListener(type, handler) {
      this.listeners[type] = handler;
    },
    querySelector() {
      return null;
    },
    querySelectorAll() {
      return [];
    },
  };
}

function loadTemplateEditorRuntime() {
  const elements = new Map();
  const section = makeElement("section");
  const listaCampos = makeElement("listaCampos");
  listaCampos.parentNode = section;
  elements.set("listaCampos", listaCampos);
  elements.set("estado", makeElement("estado"));
  let documentContext = null;
  let refreshCount = 0;
  const executeCommandCalls = [];
  const fetchCalls = [];
  const returnMessages = [];
  const target = {
    postMessage(message, targetOrigin) {
      returnMessages.push({ message, targetOrigin });
    },
  };
  const document = {
    readyState: "complete",
    body: makeElement("body"),
    getElementById(id) {
      if (!elements.has(id)) elements.set(id, makeElement(id));
      return elements.get(id);
    },
    createElement() {
      return makeElement();
    },
    querySelector() {
      return null;
    },
    querySelectorAll() {
      return [];
    },
    addEventListener() {},
  };
  const window = {
    EASYPRO_ONLYOFFICE_PLUGIN_CONFIG: {
      apiBaseUrl: "https://api.example.test",
      hostOrigins: ["https://app.easypronotarial.com"],
    },
    parent: target,
    top: target,
    setTimeout,
    clearTimeout,
    fetch: async (url, init) => {
      fetchCalls.push({ url, init });
      if (String(url).includes("/api/v1/minuta/onlyoffice/forcesave")) {
        return {
          ok: true,
          async json() {
            return { ok: true, status: "requested", onlyoffice_error: 0 };
          },
        };
      }
      return {
        ok: true,
        async json() {
          return { saved: true, markers: ["NUMERO_PARQUEADERO"] };
        },
      };
    },
    Asc: {
      plugin: {
        executeCommand(name, value) {
          executeCommandCalls.push({ name, value });
        },
        executeMethod(_name, _args, callback) {
          callback(true);
        },
      },
    },
    __EasyProBibliotecaPlugin: {
      test: {
        obtenerApiBaseUrl() {
          return "https://api.example.test";
        },
        solicitarToken() {
          return Promise.resolve("cached-token");
        },
        refrescarAuthContexto() {
          refreshCount += 1;
          documentContext = { kind: "minuta", editor_token: "editor-token-123" };
          return Promise.resolve("fresh-token");
        },
        getDocumentContext() {
          return documentContext;
        },
      },
    },
  };
  window.window = window;
  const context = vm.createContext({
    window,
    document,
    URL,
    Promise,
    Error,
    String,
    JSON,
    setTimeout,
    clearTimeout,
  });
  vm.runInContext(source, context);
  return {
    button: elements.get("btnGuardarPlantillaVolver"),
    estado: elements.get("estado"),
    fetchCalls,
    executeCommandCalls,
    returnMessages,
    getRefreshCount: () => refreshCount,
  };
}

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
  assert.match(html, /template-editor\.js\?v=2\.3\.3/);
  assert.equal(config.version, "2.3.3");
  assert.doesNotMatch(source, /MutationObserver/);
  assert.doesNotMatch(source, /executeCommand\("save"/);
  assert.doesNotMatch(source, /executeMethod\("Save"/);
});

test("template save refreshes minuta context and continues", async () => {
  const runtime = loadTemplateEditorRuntime();

  await runtime.button.listeners.click();

  assert.equal(runtime.getRefreshCount(), 1);
  assert.equal(runtime.fetchCalls.length, 2);
  assert.match(runtime.fetchCalls[0].url, /\/api\/v1\/minuta\/onlyoffice\/forcesave\?token=editor-token-123$/);
  assert.equal(runtime.fetchCalls[0].init.method, "POST");
  assert.equal(runtime.fetchCalls[0].init.headers.Authorization, "Bearer fresh-token");
  assert.match(runtime.fetchCalls[1].url, /marked-template\/editor-state\?token=editor-token-123$/);
  assert.equal(runtime.fetchCalls[1].init.headers.Authorization, "Bearer fresh-token");
  assert.equal(runtime.executeCommandCalls.length, 0);
  assert.equal(runtime.returnMessages.length > 0, true);
  assert.equal(runtime.returnMessages[0].message.type, "EASYPRO_MINUTA_TEMPLATE_RETURN_REQUEST");
  assert.equal(runtime.estado.className, "ok");
});
