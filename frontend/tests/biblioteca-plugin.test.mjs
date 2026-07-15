import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import test from "node:test";
import vm from "node:vm";

test("plugin html and config keep production OnlyOffice runtime cache busting", () => {
  const html = readFileSync(resolve("onlyoffice-plugin/biblioteca/index.html"), "utf8");
  const config = JSON.parse(readFileSync(resolve("onlyoffice-plugin/biblioteca/config.json"), "utf8"));
  const runtimeIndex = html.indexOf('<script type="text/javascript" src="../v1/plugins.js"></script>');
  const pluginIndex = html.indexOf('<script src="plugin.js?v=1.1.0"></script>');

  assert.notEqual(runtimeIndex, -1);
  assert.notEqual(pluginIndex, -1);
  assert.ok(runtimeIndex < pluginIndex);
  assert.equal(config.version, "1.1.0");
  assert.equal(config.variations[0].url, "index.html?v=1.1.0");
});

function loadPlugin(options = {}) {
  const posted = [];
  const target = {
    postMessage(message, targetOrigin) {
      posted.push({ message, targetOrigin });
    },
  };
  const listeners = new Map();
  const elements = new Map();
  const commandCalls = [];
  const executeCalls = [];
  const window = {
    EASYPRO_ONLYOFFICE_PLUGIN_CONFIG: {
      authTimeoutMs: 10,
      analysisTimeoutMs: 10,
      diagnostics: Boolean(options.diagnostics),
      hostOrigins: ["https://app.easypronotarial.com"],
    },
    parent: target,
    top: target,
    setTimeout,
    clearTimeout,
    addEventListener(type, handler) {
      listeners.set(type, handler);
    },
    fetch: undefined,
    Asc: {
      scope: {},
      plugin: {
        executeMethod(name, args, callback) {
          executeCalls.push({ name, args });
          if (callback) callback();
        },
      },
    },
  };
  if (options.document) {
    window.Asc.plugin.callCommand = function (command, _close, _calc, callback) {
      commandCalls.push({ close: _close, calc: _calc });
      const result = command();
      if (callback) callback(result);
    };
  }
  window.window = window;

  function makeElement(id = "") {
    return {
      id,
      value: "",
      style: {},
      className: "",
      textContent: "",
      innerHTML: "",
      dataset: {},
      disabled: false,
      title: "",
      children: [],
      appendChild(child) {
        this.children.push(child);
      },
      addEventListener(type, handler) {
        this[`on${type}`] = handler;
      },
    };
  }

  const document = {
    getElementById(id) {
      if (!elements.has(id)) {
        elements.set(id, makeElement(id));
      }
      return elements.get(id);
    },
    createElement() {
      return makeElement();
    },
  };

  const context = vm.createContext({
    window,
    document,
    URL,
    Promise,
    Error,
    Number,
    String,
    Array,
    JSON,
    Math,
    Asc: window.Asc,
    Api: options.document ? { GetDocument: () => options.document } : undefined,
  });
  const script = readFileSync(resolve("onlyoffice-plugin/biblioteca/plugin.js"), "utf8");
  vm.runInContext(script, context);
  return { api: window.__EasyProBibliotecaPlugin.test, constants: window.__EasyProBibliotecaPlugin.constants, posted, window, elements, commandCalls, executeCalls };
}

function makeRange(text, meta = {}) {
  const range = {
    text,
    fontColor: meta.fontColor || "black",
    location_key: meta.location_key,
    block_hash: meta.block_hash,
    context_before: meta.context_before,
    context_after: meta.context_after,
    char_start: meta.char_start,
    char_end: meta.char_end,
    highlightCalls: [],
    colorCalls: [],
    selected: false,
    GetText() {
      return text;
    },
    Select() {
      this.selected = true;
    },
  };
  if (meta.highlight !== false) {
    range.SetHighlight = function (...args) {
      this.highlightCalls.push(args);
    };
  }
  if (meta.color !== false) {
    range.SetColor = function (...args) {
      this.colorCalls.push(args);
      this.fontColor = args[3] === true ? this.fontColor : "changed";
    };
  }
  return range;
}

function makeDocument(searchMap) {
  return {
    searches: [],
    Search(text) {
      this.searches.push(text);
      return searchMap[text] || [];
    },
  };
}

function suggestion(overrides = {}) {
  return {
    suggestion_id: "sug_1",
    candidate_id: "cand_1",
    original_text: "Daniela Campo",
    field_code: "COMPRADOR_1",
    field_label: "Comprador 1",
    category: "persona",
    confidence: 0.97,
    source: "hybrid",
    context_before: "LOS COMPRADORES:",
    context_after: "- cédula de ciudadanía número",
    location: {
      block_type: "paragraph",
      block_index: 1,
      paragraph_index: 1,
      table_index: null,
      row_index: null,
      cell_index: null,
      char_start: 17,
      char_end: 30,
      occurrence_index: 1,
      location_key: "paragraph:1:17:30:1",
      block_hash: "hash-1",
    },
    ...overrides,
  };
}

test("plugin receives token from authorized host origin", async () => {
  const { api, constants } = loadPlugin();
  const promise = api.solicitarToken();

  api.handleAuthMessage({
    origin: "https://easypronotarial.com",
    data: {
      type: constants.AUTH_RESPONSE_TYPE,
      source: constants.HOST_SOURCE,
      token: "jwt-real",
      document_context: {
        kind: "case_document",
        case_id: 174,
        document_id: 114,
        version_id: 229,
      },
    },
  });

  assert.equal(await promise, "jwt-real");
});

test("plugin times out without auth response", async () => {
  const { api } = loadPlugin();

  await assert.rejects(api.solicitarToken(), (error) => error.kind === "auth_timeout");
});

test("plugin rejects unauthorized response origin", async () => {
  const { api, constants } = loadPlugin();
  const promise = api.solicitarToken();

  api.handleAuthMessage({
    origin: "https://attacker.example",
    data: {
      type: constants.AUTH_RESPONSE_TYPE,
      source: constants.HOST_SOURCE,
      token: "jwt-real",
    },
  });

  await assert.rejects(promise, (error) => error.kind === "auth_timeout");
});

test("plugin sends only one simultaneous auth request", () => {
  const { api, posted } = loadPlugin();
  const first = api.solicitarToken();
  const postedAfterFirst = posted.length;
  const second = api.solicitarToken();

  assert.equal(first, second);
  assert.equal(posted.length, postedAfterFirst);
  first.catch(() => {});
});

test("plugin loads catalog with bearer token on 200", async () => {
  const { api } = loadPlugin();
  const calls = [];
  const result = await api.cargarCatalogoConToken("jwt-real", async (url, init) => {
    calls.push({ url, init });
    return {
      ok: true,
      status: 200,
      async json() {
        return [{ code: "COMPRADOR_1", label: "Comprador 1", category: "persona" }];
      },
    };
  });

  assert.equal(result[0].code, "COMPRADOR_1");
  assert.equal(calls[0].init.headers.Authorization, "Bearer jwt-real");
  assert.equal(calls[0].init.headers.Accept, "application/json");
  assert.match(calls[0].url, /\/api\/v1\/biblioteca\/campos$/);
});

test("plugin maps backend 401", async () => {
  const { api } = loadPlugin();
  await assert.rejects(
    api.cargarCatalogoConToken("jwt", async () => ({ ok: false, status: 401 })),
    (error) => error.kind === "unauthorized",
  );
});

test("plugin maps backend 403", async () => {
  const { api } = loadPlugin();
  await assert.rejects(
    api.cargarCatalogoConToken("jwt", async () => ({ ok: false, status: 403 })),
    (error) => error.kind === "forbidden",
  );
});

test("plugin maps network errors", async () => {
  const { api } = loadPlugin();
  await assert.rejects(
    api.cargarCatalogoConToken("jwt", async () => {
      throw new Error("Failed to fetch");
    }),
    (error) => error.kind === "network_error",
  );
});

test("plugin accepts empty catalog as an empty array", async () => {
  const { api } = loadPlugin();
  const result = await api.cargarCatalogoConToken("jwt", async () => ({
    ok: true,
    status: 200,
    async json() {
      return [];
    },
  }));

  assert.deepEqual(result, []);
});

test("plugin validates case and minuta document context", () => {
  const { api } = loadPlugin();
  const caseContext = api.validarDocumentContext({
    kind: "case_document",
    case_id: "174",
    document_id: "114",
    version_id: "229",
  });
  const minutaContext = api.validarDocumentContext({
    kind: "minuta",
    editor_token: " signed-token ",
  });

  assert.equal(caseContext.kind, "case_document");
  assert.equal(caseContext.case_id, 174);
  assert.equal(caseContext.document_id, 114);
  assert.equal(caseContext.version_id, 229);
  assert.equal(minutaContext.kind, "minuta");
  assert.equal(minutaContext.editor_token, "signed-token");
  assert.equal(api.validarDocumentContext({ kind: "case_document", case_id: "x" }), null);
});

test("plugin does not analyze without document context", async () => {
  const { api } = loadPlugin();

  await assert.rejects(
    api.analizarActualConToken("jwt-real", null, async () => {
      throw new Error("should not fetch");
    }),
    (error) => error.kind === "missing_document_context",
  );
});

test("plugin calls analyze-current and renders suggestions", async () => {
  const { api, elements } = loadPlugin();
  const calls = [];
  const context = {
    kind: "case_document",
    case_id: 174,
    document_id: 114,
    version_id: 229,
  };
  const suggestions = await api.analizarActualConToken("jwt-real", context, async (url, init) => {
    calls.push({ url, init });
    return {
      ok: true,
      status: 200,
      async json() {
        return {
          suggestions: [{
            candidate_id: "cand_1",
            original_text: "Daniela Campo",
            field_code: "COMPRADOR_1",
            field_label: "Comprador 1",
            category: "persona",
            confidence: 0.97,
            source: "hybrid",
          }],
        };
      },
    };
  });

  assert.equal(suggestions.length, 1);
  assert.match(calls[0].url, /\/api\/v1\/biblioteca\/analizar-actual$/);
  assert.equal(calls[0].init.headers.Authorization, "Bearer jwt-real");
  assert.equal(calls[0].init.headers["Content-Type"], "application/json");
  assert.deepEqual(JSON.parse(calls[0].init.body), context);

  api.renderSugerencias(suggestions);
  const list = elements.get("listaSugerencias");
  assert.equal(list.children.length, 1);
  assert.equal(list.children[0].dataset.candidateId, "cand_1");
  const buttons = list.children[0].children.at(-1).children;
  assert.equal(buttons[0].disabled, true);
  assert.equal(buttons[1].disabled, true);
});

test("plugin maps analyze-current 401 404 500 and timeout", async () => {
  const { api } = loadPlugin();
  const context = { kind: "minuta", editor_token: "signed-token" };

  await assert.rejects(
    api.analizarActualConToken("jwt", context, async () => ({ ok: false, status: 401 })),
    (error) => error.kind === "unauthorized",
  );
  await assert.rejects(
    api.analizarActualConToken("jwt", context, async () => ({ ok: false, status: 404 })),
    (error) => error.kind === "document_not_found",
  );
  await assert.rejects(
    api.analizarActualConToken("jwt", context, async () => ({ ok: false, status: 500 })),
    (error) => error.kind === "backend_unavailable",
  );
  await assert.rejects(
    api.analizarActualConToken("jwt", context, async () => new Promise(() => {})),
    (error) => error.kind === "analysis_timeout",
  );
});

test("plugin blocks duplicate analyze button requests", async () => {
  const { api, constants } = loadPlugin();
  let fetchCalls = 0;
  const pending = new Promise((resolve) => {
    setTimeout(() => resolve({
      ok: true,
      status: 200,
      async json() {
        return { suggestions: [] };
      },
    }), 5);
  });
  const originalFetch = globalThis.fetch;
  try {
    globalThis.fetch = undefined;
    const { window } = loadPlugin();
    window.fetch = async () => {
      fetchCalls += 1;
      return pending;
    };
    const pluginApi = window.__EasyProBibliotecaPlugin.test;
    const first = pluginApi.solicitarToken();
    pluginApi.handleAuthMessage({
      origin: "https://easypronotarial.com",
      data: {
        type: constants.AUTH_RESPONSE_TYPE,
        source: constants.HOST_SOURCE,
        token: "jwt-real",
        document_context: { kind: "minuta", editor_token: "signed-token" },
      },
    });
    await first;
    const a = pluginApi.analizarDocumento();
    const b = pluginApi.analizarDocumento();
    await Promise.all([a, b]);
    assert.equal(fetchCalls, 1);
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test("plugin marks a valid suggestion in yellow and records marker state", async () => {
  const range = makeRange("Daniela Campo", {
    location_key: "paragraph:1:17:30:1",
    block_hash: "hash-1",
    context_before: "LOS COMPRADORES:",
    context_after: "- cédula de ciudadanía número",
    char_start: 17,
    char_end: 30,
  });
  const document = makeDocument({ "Daniela Campo": [range] });
  const { api } = loadPlugin({ document });
  const items = api.prepararSugerencias([suggestion()]);

  await api.marcarSugerenciasEnDocumento(items);

  assert.deepEqual(range.highlightCalls[0], [255, 242, 102]);
  assert.equal(range.colorCalls.length, 0);
  assert.equal(api.getDiagnostics().capabilities.highlight_supported, true);
  assert.equal(api.getMarkerRegistry().sug_1.status, "marked");
  assert.equal(api.getMarkerRegistry().sug_1.field_code, "COMPRADOR_1");
});

test("plugin distinguishes repeated occurrences by location metadata", async () => {
  const first = makeRange("Daniela Campo", {
    location_key: "paragraph:1:17:30:1",
    block_hash: "hash-1",
    char_start: 17,
    char_end: 30,
  });
  const second = makeRange("Daniela Campo", {
    location_key: "paragraph:1:48:61:2",
    block_hash: "hash-1",
    char_start: 48,
    char_end: 61,
  });
  const document = makeDocument({ "Daniela Campo": [first, second] });
  const { api } = loadPlugin({ document });
  const item = suggestion({
    suggestion_id: "sug_2",
    location: {
      ...suggestion().location,
      char_start: 48,
      char_end: 61,
      occurrence_index: 2,
      location_key: "paragraph:1:48:61:2",
    },
  });

  await api.marcarSugerenciasEnDocumento(api.prepararSugerencias([item]));

  assert.equal(first.highlightCalls.length, 0);
  assert.equal(second.highlightCalls.length, 1);
  assert.equal(api.getMarkerRegistry().sug_2.status, "marked");
});

test("plugin respects occurrence_index when verified ranges share the same metadata shape", async () => {
  const first = makeRange("Daniela Campo", { char_start: 10, char_end: 23 });
  const second = makeRange("Daniela Campo", { char_start: 40, char_end: 53 });
  const document = makeDocument({ "Daniela Campo": [first, second] });
  const { api } = loadPlugin({ document });
  const item = suggestion({
    suggestion_id: "sug_occ_2",
    location: {
      ...suggestion().location,
      char_start: 40,
      char_end: 53,
      occurrence_index: 2,
      location_key: "",
      block_hash: "",
    },
  });

  await api.marcarSugerenciasEnDocumento(api.prepararSugerencias([item]));

  assert.equal(first.highlightCalls.length, 0);
  assert.equal(second.highlightCalls.length, 1);
});

test("plugin uses context_before and context_after to avoid wrong repeated text", async () => {
  const seller = makeRange("Daniela Campo", {
    context_before: "LOS VENDEDORES:",
    context_after: "- cédula",
  });
  const buyer = makeRange("Daniela Campo", {
    context_before: "LOS COMPRADORES:",
    context_after: "- cédula de ciudadanía número",
  });
  const document = makeDocument({ "Daniela Campo": [seller, buyer] });
  const { api } = loadPlugin({ document });

  await api.marcarSugerenciasEnDocumento(api.prepararSugerencias([suggestion()]));

  assert.equal(seller.highlightCalls.length, 0);
  assert.equal(buyer.highlightCalls.length, 1);
});

test("plugin marks stale when location no longer matches", async () => {
  const range = makeRange("Daniela Campo", { location_key: "paragraph:9:1:14:1", block_hash: "changed" });
  const document = makeDocument({ "Daniela Campo": [range] });
  const { api } = loadPlugin({ document });

  await api.marcarSugerenciasEnDocumento(api.prepararSugerencias([suggestion()]));

  assert.equal(range.highlightCalls.length, 0);
  assert.equal(api.getMarkerRegistry().sug_1.status, "stale");
});

test("plugin does not mark ambiguous repeated matches without verifying context or location", async () => {
  const first = makeRange("Daniela Campo");
  const second = makeRange("Daniela Campo");
  const document = makeDocument({ "Daniela Campo": [first, second] });
  const { api } = loadPlugin({ document });
  const item = suggestion({
    location: {
      ...suggestion().location,
      location_key: "",
      block_hash: "",
      char_start: 0,
      char_end: 0,
      occurrence_index: 2,
    },
    context_before: "",
    context_after: "",
  });

  await api.marcarSugerenciasEnDocumento(api.prepararSugerencias([item]));

  assert.equal(first.highlightCalls.length, 0);
  assert.equal(second.highlightCalls.length, 0);
  assert.equal(api.getMarkerRegistry().sug_1.status, "stale");
});

test("plugin does not alter preexisting red or black font colors", async () => {
  const red = makeRange("Daniela Campo", {
    location_key: "paragraph:1:17:30:1",
    block_hash: "hash-1",
    fontColor: "red",
  });
  const black = makeRange("Carlos Pérez", {
    location_key: "paragraph:2:10:22:1",
    block_hash: "hash-2",
    fontColor: "black",
  });
  const document = makeDocument({ "Daniela Campo": [red], "Carlos Pérez": [black] });
  const { api } = loadPlugin({ document });
  const secondSuggestion = suggestion({
    suggestion_id: "sug_black",
    candidate_id: "cand_black",
    original_text: "Carlos Pérez",
    context_before: "LOS COMPRADORES:",
    context_after: "- cédula",
    location: {
      ...suggestion().location,
      char_start: 10,
      char_end: 22,
      location_key: "paragraph:2:10:22:1",
      block_hash: "hash-2",
    },
  });

  await api.marcarSugerenciasEnDocumento(api.prepararSugerencias([suggestion(), secondSuggestion]));

  assert.equal(red.colorCalls.length, 0);
  assert.equal(black.colorCalls.length, 0);
  assert.equal(red.fontColor, "red");
  assert.equal(black.fontColor, "black");
});

test("plugin records mark_failed and never uses SetColor when OnlyOffice cannot highlight", async () => {
  const range = makeRange("Daniela Campo", {
    location_key: "paragraph:1:17:30:1",
    block_hash: "hash-1",
    highlight: false,
    fontColor: "red",
  });
  const document = makeDocument({ "Daniela Campo": [range] });
  const { api } = loadPlugin({ document });

  await api.marcarSugerenciasEnDocumento(api.prepararSugerencias([suggestion()]));

  assert.equal(api.getMarkerRegistry().sug_1.status, "mark_failed");
  assert.equal(api.getMarkerRegistry().sug_1.reason, "safe_highlight_unavailable");
  assert.equal(api.getMarkerRegistry().sug_1.can_navigate, true);
  assert.equal(range.colorCalls.length, 0);
  assert.equal(range.fontColor, "red");
  assert.equal(api.getDiagnostics().capabilities.highlight_supported, false);
});

test("plugin card click navigates to the correct marker", async () => {
  const range = makeRange("Daniela Campo", {
    location_key: "paragraph:1:17:30:1",
    block_hash: "hash-1",
  });
  const document = makeDocument({ "Daniela Campo": [range] });
  const { api, elements } = loadPlugin({ document });
  const items = api.prepararSugerencias([suggestion()]);

  await api.marcarSugerenciasEnDocumento(items);
  api.renderSugerencias(items);
  elements.get("listaSugerencias").children[0].onclick();

  await new Promise((resolve) => setTimeout(resolve, 0));
  assert.equal(range.selected, true);
});

test("plugin can navigate to a verified range even when safe highlight is unavailable", async () => {
  const range = makeRange("Daniela Campo", {
    location_key: "paragraph:1:17:30:1",
    block_hash: "hash-1",
    highlight: false,
  });
  const document = makeDocument({ "Daniela Campo": [range] });
  const { api } = loadPlugin({ document });
  const items = api.prepararSugerencias([suggestion()]);

  await api.marcarSugerenciasEnDocumento(items);
  await api.navegarAMarca("sug_1");

  assert.equal(api.getMarkerRegistry().sug_1.status, "mark_failed");
  assert.equal(range.selected, true);
  assert.equal(range.colorCalls.length, 0);
});

test("plugin reanalysis clears previous marks and avoids duplicates", async () => {
  const range = makeRange("Daniela Campo", {
    location_key: "paragraph:1:17:30:1",
    block_hash: "hash-1",
  });
  const document = makeDocument({ "Daniela Campo": [range] });
  const { api } = loadPlugin({ document });
  const items = api.prepararSugerencias([suggestion()]);

  await api.marcarSugerenciasEnDocumento(items);
  await api.limpiarMarcasTemporales();
  await api.marcarSugerenciasEnDocumento(items);

  assert.equal(range.highlightCalls.length, 3);
  assert.equal(range.colorCalls.length, 0);
  assert.equal(range.fontColor, "black");
  assert.equal(api.getMarkerRegistry().sug_1.status, "marked");
});

test("plugin keeps Yes and No disabled after rendering marked suggestions", async () => {
  const range = makeRange("Daniela Campo", {
    location_key: "paragraph:1:17:30:1",
    block_hash: "hash-1",
  });
  const document = makeDocument({ "Daniela Campo": [range] });
  const { api, elements } = loadPlugin({ document });
  const items = api.prepararSugerencias([suggestion()]);

  await api.marcarSugerenciasEnDocumento(items);
  api.renderSugerencias(items);
  const buttons = elements.get("listaSugerencias").children[0].children.at(-1).children;

  assert.equal(buttons[1].disabled, true);
  assert.equal(buttons[2].disabled, true);
});

test("plugin never calls ReplaceAllText or mutates original_text while marking", async () => {
  const range = makeRange("Daniela Campo", {
    location_key: "paragraph:1:17:30:1",
    block_hash: "hash-1",
  });
  const document = makeDocument({ "Daniela Campo": [range] });
  const { api, executeCalls } = loadPlugin({ document });
  const items = api.prepararSugerencias([suggestion()]);

  await api.marcarSugerenciasEnDocumento(items);

  assert.equal(items[0].original_text, "Daniela Campo");
  assert.equal(executeCalls.some((call) => call.name === "ReplaceAllText"), false);
  assert.equal(range.colorCalls.length, 0);
});

test("plugin handles OnlyOffice API errors as mark_failed", async () => {
  const document = {
    Search() {
      throw new Error("OnlyOffice failed");
    },
  };
  const { api } = loadPlugin({ document });
  const items = api.prepararSugerencias([suggestion()]);

  await api.marcarSugerenciasEnDocumento(items);

  assert.equal(api.getMarkerRegistry().sug_1.status, "mark_failed");
});

test("plugin creates no marks when there are no suggestions", async () => {
  const document = makeDocument({});
  const { api, commandCalls } = loadPlugin({ document });

  await api.marcarSugerenciasEnDocumento([]);

  assert.equal(commandCalls.length, 0);
  assert.equal(Object.keys(api.getMarkerRegistry()).length, 0);
});
