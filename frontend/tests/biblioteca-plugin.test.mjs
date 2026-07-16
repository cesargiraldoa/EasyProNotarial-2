import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import test from "node:test";
import vm from "node:vm";

test("plugin html and config use version 2.3.0 with official runtime first", () => {
  const html = readFileSync(resolve("onlyoffice-plugin/biblioteca/index.html"), "utf8");
  const config = JSON.parse(readFileSync(resolve("onlyoffice-plugin/biblioteca/config.json"), "utf8"));
  const runtimeIndex = html.indexOf('<script type="text/javascript" src="../v1/plugins.js"></script>');
  const pluginIndex = html.indexOf('<script src="plugin.js?v=2.3.0"></script>');

  assert.notEqual(runtimeIndex, -1);
  assert.notEqual(pluginIndex, -1);
  assert.ok(runtimeIndex < pluginIndex);
  assert.equal(config.version, "2.3.0");
  assert.equal(config.variations[0].url, "index.html?v=2.3.0");
});

function sourceSpy() {
  const calls = [];
  return {
    calls,
    postMessage(message, targetOrigin) {
      calls.push({ message, targetOrigin });
    },
  };
}

function loadPlugin(options = {}) {
  const postedTarget = sourceSpy();
  const listeners = new Map();
  const elements = new Map();
  const executeCalls = [];
  const buttonControls = [];
  const controls = options.controls || [];
  function FakeButtonContentControl() {
    this.icons = null;
    this.attachOnClick = (handler) => {
      this.handler = handler;
      buttonControls.push(this);
    };
  }
  const window = {
    EASYPRO_ONLYOFFICE_PLUGIN_CONFIG: {
      authTimeoutMs: 10,
      analysisTimeoutMs: 20,
      hostOrigins: ["https://app.easypronotarial.com"],
    },
    parent: postedTarget,
    top: postedTarget,
    setTimeout,
    clearTimeout,
    addEventListener(type, handler) {
      listeners.set(type, handler);
    },
    fetch: options.fetch,
    Asc: {
      ButtonContentControl: options.enableContentControlButtons === false ? undefined : FakeButtonContentControl,
      plugin: {
        executeMethod(name, args, callback) {
          executeCalls.push({ name, args });
          if (options.executeMethod) {
            callback(options.executeMethod(name, args, controls));
            return;
          }
          if (name === "GetAllContentControls") {
            callback(controls);
            return;
          }
          if (name === "InsertAndReplaceContentControls") {
            const payload = args[0] || [];
            payload.forEach((item) => {
              const target = controls.find((control) => String(control.InternalId) === String(item.InternalId));
              if (target) {
                target.Tag = item.Tag;
                target.Alias = item.Alias;
                target.Text = item.Text;
              }
            });
            callback(true);
            return;
          }
          if (name === "RemoveContentControls") {
            const ids = args[0] || [];
            ids.forEach((id) => {
              const index = controls.findIndex((control) => String(control.InternalId) === String(id));
              if (index >= 0) controls.splice(index, 1);
            });
            callback(true);
            return;
          }
          if (name === "MoveCursorToContentControl" || name === "SelectContentControl") {
            callback(true);
            return;
          }
          if (name === "AddContentControl") {
            const id = `manual-${controls.length + 1}`;
            controls.push({ InternalId: id, Tag: args[1].Tag, Alias: args[1].Alias, Text: "" });
            callback({ InternalId: id });
            return;
          }
          callback(true);
        },
      },
    },
  };
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
      if (!elements.has(id)) elements.set(id, makeElement(id));
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
    Date: class {
      static now() {
        return 2026001;
      }
    },
  });
  const script = readFileSync(resolve("onlyoffice-plugin/biblioteca/plugin.js"), "utf8");
  vm.runInContext(script, context);
  return { api: window.__EasyProBibliotecaPlugin.test, constants: window.__EasyProBibliotecaPlugin.constants, postedTarget, window, elements, getElement: (id) => document.getElementById(id), executeCalls, controls, buttonControls };
}

function auth(api, constants) {
  const promise = api.solicitarToken();
  api.handleAuthMessage({
    origin: "https://easypronotarial.com",
    data: {
      type: constants.AUTH_RESPONSE_TYPE,
      source: constants.HOST_SOURCE,
      token: "jwt-real",
      document_context: { kind: "case_document", case_id: 173, document_id: 113, version_id: 235 },
    },
  });
  return promise;
}

function suggestionControl(overrides = {}) {
  return {
    InternalId: "cc-1",
    Tag: "easypro:suggestion:v2:analysis_1:sug_1:cand_1:fi_comprador_1:COMPRADOR_1:COMPRADOR_1:grp_1:occ_001:matched",
    Alias: "EasyPro sugerencia - COMPRADOR_1",
    Text: "Daniela Campo",
    ...overrides,
  };
}

function fieldControl(overrides = {}) {
  return {
    InternalId: "field-1",
    Tag: "easypro:field:v2:fi_comprador_1:occ_001:COMPRADOR_1:COMPRADOR_1",
    Alias: "EasyPro campo - COMPRADOR_1",
    Text: "{{COMPRADOR_1}}",
    ...overrides,
  };
}

function decisionResponse(versionId = 236) {
  return {
    ok: true,
    status: 200,
    async json() {
      return {
        review_document: { kind: "case_document", case_id: 173, document_id: 113, version_id: versionId },
        audit: { status: "accepted" },
      };
    },
  };
}

test("plugin receives token from authorized host origin", async () => {
  const { api, constants } = loadPlugin();
  assert.equal(await auth(api, constants), "jwt-real");
});

test("plugin rejects unauthorized response origin", async () => {
  const { api, constants } = loadPlugin();
  const promise = api.solicitarToken();
  api.handleAuthMessage({
    origin: "https://attacker.example",
    data: { type: constants.AUTH_RESPONSE_TYPE, source: constants.HOST_SOURCE, token: "jwt-real" },
  });
  await assert.rejects(promise, (error) => error.kind === "auth_timeout");
});

test("plugin loads catalog with bearer token", async () => {
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
  assert.match(calls[0].url, /\/api\/v1\/biblioteca\/campos$/);
  assert.equal(calls[0].init.headers.Authorization, "Bearer jwt-real");
});

test("plugin calls analyze-and-prepare and requests host reload", async () => {
  const { api, constants, postedTarget, window } = loadPlugin();
  const calls = [];
  window.fetch = async (url, init) => {
    calls.push({ url, init });
    return {
      ok: true,
      status: 200,
      async json() {
        return {
          analysis_id: "analysis_1",
          review_document: { kind: "case_document", case_id: 173, document_id: 113, version_id: 236 },
          groups: [],
          stats: {},
        };
      },
    };
  };
  await auth(api, constants);

  await api.analizarDocumento();

  assert.match(calls[0].url, /\/api\/v1\/biblioteca\/analizar-y-preparar$/);
  assert.equal(calls[0].init.headers.Authorization, "Bearer jwt-real");
  const reload = postedTarget.calls.find((call) => call.message.type === constants.RELOAD_REQUEST_TYPE);
  assert.equal(reload.targetOrigin, "https://easypronotarial.com");
  assert.equal(JSON.stringify(reload.message.review_document), JSON.stringify({ kind: "case_document", case_id: 173, document_id: 113, version_id: 236 }));
});

test("plugin reads Content Controls and groups suggestions by backend tag", async () => {
  const { api } = loadPlugin({ controls: [suggestionControl(), suggestionControl({ InternalId: "cc-2", Tag: "easypro:suggestion:v2:analysis_1:sug_2:cand_2:fi_comprador_1:COMPRADOR_1:COMPRADOR_1:grp_1:occ_002:matched" })] });

  const result = await api.leerContentControls();

  assert.equal(result.ok, true);
  assert.equal(api.getGroups().length, 1);
  assert.equal(api.getGroups()[0].occurrences.length, 2);
  assert.equal(api.getGroups()[0].field_instance_id, "fi_comprador_1");
  assert.equal(api.getGroups()[0].visible_code, "COMPRADOR_1");
});

test("accept delegates the exact occurrence decision to backend and requests reload", async () => {
  const { api, constants, postedTarget, window } = loadPlugin({ controls: [suggestionControl()] });
  const calls = [];
  window.fetch = async (url, init) => {
    calls.push({ url, init, body: JSON.parse(init.body) });
    return decisionResponse(236);
  };
  await auth(api, constants);
  api.registrarBotonesContentControls();
  await api.leerContentControls();
  const occurrence = api.getGroups()[0].occurrences[0];

  const ok = await api.aceptarOcurrencia(occurrence);

  assert.equal(ok, true);
  assert.match(calls[0].url, /\/api\/v1\/biblioteca\/decidir$/);
  assert.equal(calls[0].init.headers.Authorization, "Bearer jwt-real");
  assert.equal(calls[0].body.action, "accept");
  assert.equal(calls[0].body.occurrence_id, "occ_001");
  assert.equal(calls[0].body.field_instance_id, "fi_comprador_1");
  const reload = postedTarget.calls.find((call) => call.message.type === constants.RELOAD_REQUEST_TYPE);
  assert.equal(JSON.stringify(reload.message.review_document), JSON.stringify({ kind: "case_document", case_id: 173, document_id: 113, version_id: 236 }));
});

test("accept blocks provisional fields until they are assigned", async () => {
  const calls = [];
  const { api, window } = loadPlugin({
    controls: [suggestionControl({
      Tag: "easypro:suggestion:v2:analysis_1:sug_1:cand_1:prov_x:PENDING_FIELD_PERSON_NAME_ABCD:PENDING_FIELD_PERSON_NAME_ABCD:grp_1:occ_001:unmapped",
    })],
  });
  window.fetch = async (url, init) => {
    calls.push({ url, init });
    return decisionResponse(236);
  };
  await api.leerContentControls();
  api.registrarBotonesContentControls();

  const ok = await api.aceptarOcurrencia(api.getGroups()[0].occurrences[0]);

  assert.equal(ok, false);
  assert.equal(calls.length, 0);
});

test("reject delegates the occurrence decision to backend", async () => {
  const { api, constants, window } = loadPlugin({ controls: [suggestionControl(), fieldControl()] });
  const calls = [];
  window.fetch = async (url, init) => {
    calls.push({ url, init, body: JSON.parse(init.body) });
    return decisionResponse(237);
  };
  await auth(api, constants);
  api.registrarBotonesContentControls();
  await api.leerContentControls();

  const ok = await api.rechazarOcurrencia(api.getGroups()[0].occurrences[0]);

  assert.equal(ok, true);
  assert.equal(calls[0].body.action, "reject");
  assert.equal(calls[0].body.occurrence_id, "occ_001");
});

test("change assigns another catalog field through backend", async () => {
  const { api, constants, window } = loadPlugin({ controls: [suggestionControl()] });
  const calls = [];
  window.fetch = async (url, init) => {
    calls.push({ url, init, body: JSON.parse(init.body) });
    return decisionResponse(238);
  };
  await auth(api, constants);
  api.registrarBotonesContentControls();
  await api.leerContentControls();

  const ok = await api.cambiarOcurrencia(api.getGroups()[0].occurrences[0], "VENDEDOR_1");

  assert.equal(ok, true);
  assert.equal(calls[0].body.action, "change");
  assert.equal(calls[0].body.field_code, "VENDEDOR_1");
  assert.equal(calls[0].body.visible_code, "VENDEDOR_1");
});

test("change without explicit field opens auxiliary selector without backend decision", async () => {
  const { api, elements } = loadPlugin({ controls: [suggestionControl()] });
  api.registrarBotonesContentControls();
  await api.leerContentControls();

  const ok = await api.cambiarOcurrencia(api.getGroups()[0].occurrences[0]);

  assert.equal(ok, false);
  assert.equal(api.getCambioOccurrence().occurrence_id, "occ_001");
  assert.equal(elements.get("panelCambio").className, "change-panel visible");
});

test("change can create and assign a new field transactionally", async () => {
  const { api, constants, window, getElement } = loadPlugin({ controls: [suggestionControl()] });
  const calls = [];
  window.fetch = async (url, init) => {
    calls.push({ url, init, body: JSON.parse(init.body) });
    if (/\/api\/v1\/biblioteca\/campos$/.test(url)) {
      return {
        ok: true,
        status: 200,
        async json() {
          return [{ code: "COMPRADOR_1", label: "Comprador 1", category: "persona" }];
        },
      };
    }
    return decisionResponse(241);
  };
  await auth(api, constants);
  api.registrarBotonesContentControls();
  await api.leerContentControls();
  await api.cambiarOcurrencia(api.getGroups()[0].occurrences[0]);
  getElement("nuevoCampoCode").value = "EMAIL_COMPRADOR_1";
  getElement("nuevoCampoLabel").value = "Email comprador 1";
  getElement("nuevoCampoCategory").value = "contacto";
  getElement("nuevoCampoType").value = "email";

  const ok = await api.crearYAsignarCampo();

  assert.equal(ok, true);
  assert.equal(calls.at(-1).body.action, "change");
  assert.deepEqual(calls.at(-1).body.new_field, {
    code: "EMAIL_COMPRADOR_1",
    label: "Email comprador 1",
    category: "contacto",
    field_type: "email",
  });
});

test("navigation uses Content Control id instead of text search", async () => {
  const { api, executeCalls } = loadPlugin({ controls: [suggestionControl()] });
  await api.leerContentControls();

  await api.navegarAControl(api.getGroups()[0].occurrences[0]);

  assert.equal(executeCalls.some((call) => call.name === "MoveCursorToContentControl"), true);
});

test("decision actions are blocked when OnlyOffice inline buttons are unsupported", async () => {
  const { api, constants, window } = loadPlugin({ controls: [suggestionControl()], enableContentControlButtons: false });
  const calls = [];
  window.fetch = async (url, init) => {
    calls.push({ url, init });
    return decisionResponse(236);
  };
  await auth(api, constants);
  await api.leerContentControls();

  const ok = await api.aceptarOcurrencia(api.getGroups()[0].occurrences[0]);

  assert.equal(ok, false);
  assert.equal(calls.length, 0);
});

test("cascade updates all controls with same field instance", async () => {
  const { api, constants, postedTarget, window, controls } = loadPlugin({
    controls: [
      fieldControl({ InternalId: "field-1", Tag: "easypro:field:v2:fi_comprador_1:occ_001:COMPRADOR_1:COMPRADOR_1" }),
      fieldControl({ InternalId: "field-2", Tag: "easypro:field:v2:fi_comprador_1:occ_002:COMPRADOR_1:COMPRADOR_1" }),
      fieldControl({ InternalId: "field-3", Tag: "easypro:field:v2:fi_vendedor_1:occ_003:VENDEDOR_1:VENDEDOR_1" }),
    ],
  });
  const calls = [];
  window.fetch = async (url, init) => {
    calls.push({ url, init, body: JSON.parse(init.body) });
    return {
      ok: true,
      status: 200,
      async json() {
        return {
          review_document: { kind: "case_document", case_id: 173, document_id: 113, version_id: 239 },
          updated_controls: 2,
        };
      },
    };
  };
  await auth(api, constants);
  api.registrarBotonesContentControls();
  await api.leerContentControls();

  await api.aplicarCascada("fi_comprador_1", "Maria Perez");

  assert.match(calls[0].url, /\/api\/v1\/biblioteca\/actualizar-campo$/);
  assert.equal(calls[0].body.field_instance_id, "fi_comprador_1");
  assert.equal(calls[0].body.value, "Maria Perez");
  assert.equal(controls[0].Text, "{{COMPRADOR_1}}");
  assert.equal(controls[1].Text, "{{COMPRADOR_1}}");
  assert.equal(controls[2].Text, "{{COMPRADOR_1}}");
  const reload = postedTarget.calls.find((call) => call.message.type === constants.RELOAD_REQUEST_TYPE);
  assert.equal(JSON.stringify(reload.message.review_document), JSON.stringify({ kind: "case_document", case_id: 173, document_id: 113, version_id: 239 }));
});

test("manual insertion creates a definitive Content Control", async () => {
  const { api, controls } = loadPlugin({ controls: [] });

  await api.insertarCampoEstructurado("COMPRADOR_1");

  assert.equal(controls.length, 1);
  assert.equal(controls[0].Tag, "easypro:field:v2:COMPRADOR_1:manual_2026001:COMPRADOR_1:COMPRADOR_1");
  assert.equal(controls[0].Text, "{{COMPRADOR_1}}");
});

test("OnlyOffice content control buttons are registered for inline review", () => {
  const { api, buttonControls } = loadPlugin({ enableContentControlButtons: true });

  assert.equal(api.registrarBotonesContentControls(), true);
  assert.equal(buttonControls.length, 3);
  assert.deepEqual(buttonControls.map((button) => button.icons), ["resources/check.svg", "resources/close.svg", "resources/edit.svg"]);
  assert.equal(api.registrarBotonesContentControls(), false);
});

test("inline resolver reads the selected Content Control and delegates decision", async () => {
  const { api, constants, window } = loadPlugin({ controls: [suggestionControl()] });
  const calls = [];
  window.fetch = async (url, init) => {
    calls.push({ url, init, body: JSON.parse(init.body) });
    return decisionResponse(240);
  };
  await auth(api, constants);
  api.registrarBotonesContentControls();

  await api.resolverAccionInline("cc-1", "accept");

  assert.equal(calls[0].body.action, "accept");
  assert.equal(calls[0].body.occurrence_id, "occ_001");
});

test("source has no prohibited destructive APIs or arbitrary ranges", () => {
  const source = readFileSync(resolve("onlyoffice-plugin/biblioteca/plugin.js"), "utf8");
  assert.doesNotMatch(source, /SetColor/);
  assert.doesNotMatch(source, /ReplaceAllText/);
  assert.doesNotMatch(source, /window\.prompt/);
  assert.doesNotMatch(source, /doc\.Search|\.Search\(/);
  assert.doesNotMatch(source, /ranges\[0\]/);
});
