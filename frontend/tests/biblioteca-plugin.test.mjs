import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import test from "node:test";
import vm from "node:vm";

function loadPlugin() {
  const posted = [];
  const target = {
    postMessage(message, targetOrigin) {
      posted.push({ message, targetOrigin });
    },
  };
  const listeners = new Map();
  const elements = new Map();
  const window = {
    EASYPRO_ONLYOFFICE_PLUGIN_CONFIG: {
      authTimeoutMs: 10,
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
      plugin: {
        executeMethod() {},
      },
    },
  };
  window.window = window;

  const document = {
    getElementById(id) {
      if (!elements.has(id)) {
        elements.set(id, {
          id,
          value: "",
          style: {},
          className: "",
          textContent: "",
          innerHTML: "",
          appendChild() {},
          addEventListener() {},
        });
      }
      return elements.get(id);
    },
    createElement() {
      return {
        dataset: {},
        style: {},
        appendChild() {},
        addEventListener() {},
      };
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
    Math,
  });
  const script = readFileSync(resolve("onlyoffice-plugin/biblioteca/plugin.js"), "utf8");
  vm.runInContext(script, context);
  return { api: window.__EasyProBibliotecaPlugin.test, constants: window.__EasyProBibliotecaPlugin.constants, posted, window };
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
