import assert from "node:assert/strict";
import test from "node:test";

import {
  EASYPRO_ONLYOFFICE_AUTH_REQUEST_TYPE,
  EASYPRO_ONLYOFFICE_AUTH_RESPONSE_TYPE,
  EASYPRO_ONLYOFFICE_HOST_SOURCE,
  EASYPRO_ONLYOFFICE_PLUGIN_SOURCE,
  createOnlyOfficePluginAuthBridgeHandler,
  installOnlyOfficePluginAuthBridge,
  resolveAllowedOnlyOfficeOrigins,
} from "../lib/onlyoffice-plugin-auth-bridge-core.ts";

const onlyOfficeOrigin = "https://onlyoffice.easypronotarial.com";

function sourceSpy() {
  const calls = [];
  return {
    calls,
    postMessage(message, targetOrigin) {
      calls.push({ message, targetOrigin });
    },
  };
}

test("bridge ignores unauthorized origins", () => {
  const source = sourceSpy();
  const handler = createOnlyOfficePluginAuthBridgeHandler({
    allowedOrigins: resolveAllowedOnlyOfficeOrigins(),
    getSessionToken: () => "jwt",
  });

  handler({
    origin: "https://attacker.example",
    source,
    data: {
      type: EASYPRO_ONLYOFFICE_AUTH_REQUEST_TYPE,
      source: EASYPRO_ONLYOFFICE_PLUGIN_SOURCE,
    },
  });

  assert.equal(source.calls.length, 0);
});

test("bridge ignores wrong message type", () => {
  const source = sourceSpy();
  const handler = createOnlyOfficePluginAuthBridgeHandler({
    allowedOrigins: resolveAllowedOnlyOfficeOrigins(),
    getSessionToken: () => "jwt",
  });

  handler({
    origin: onlyOfficeOrigin,
    source,
    data: {
      type: "WRONG",
      source: EASYPRO_ONLYOFFICE_PLUGIN_SOURCE,
    },
  });

  assert.equal(source.calls.length, 0);
});

test("bridge responds to authorized origin and only to event.source", () => {
  const source = sourceSpy();
  const otherSource = sourceSpy();
  const handler = createOnlyOfficePluginAuthBridgeHandler({
    allowedOrigins: resolveAllowedOnlyOfficeOrigins(),
    getSessionToken: () => "jwt-real",
  });

  handler({
    origin: onlyOfficeOrigin,
    source,
    data: {
      type: EASYPRO_ONLYOFFICE_AUTH_REQUEST_TYPE,
      source: EASYPRO_ONLYOFFICE_PLUGIN_SOURCE,
    },
  });

  assert.equal(source.calls.length, 1);
  assert.equal(otherSource.calls.length, 0);
  assert.equal(source.calls[0].targetOrigin, onlyOfficeOrigin);
  assert.deepEqual(source.calls[0].message, {
    type: EASYPRO_ONLYOFFICE_AUTH_RESPONSE_TYPE,
    source: EASYPRO_ONLYOFFICE_HOST_SOURCE,
    token: "jwt-real",
  });
});

test("bridge responds with typed error and no token when session is missing", () => {
  const source = sourceSpy();
  const handler = createOnlyOfficePluginAuthBridgeHandler({
    allowedOrigins: resolveAllowedOnlyOfficeOrigins(),
    getSessionToken: () => null,
  });

  handler({
    origin: onlyOfficeOrigin,
    source,
    data: {
      type: EASYPRO_ONLYOFFICE_AUTH_REQUEST_TYPE,
      source: EASYPRO_ONLYOFFICE_PLUGIN_SOURCE,
    },
  });

  assert.equal(source.calls.length, 1);
  assert.deepEqual(source.calls[0].message, {
    type: EASYPRO_ONLYOFFICE_AUTH_RESPONSE_TYPE,
    source: EASYPRO_ONLYOFFICE_HOST_SOURCE,
    error: "NO_SESSION",
  });
});

test("bridge cleanup removes the exact listener", () => {
  const calls = [];
  let installedHandler = null;
  const target = {
    addEventListener(type, handler) {
      calls.push(["add", type, handler]);
      installedHandler = handler;
    },
    removeEventListener(type, handler) {
      calls.push(["remove", type, handler]);
    },
  };

  const cleanup = installOnlyOfficePluginAuthBridge({
    target,
    allowedOrigins: resolveAllowedOnlyOfficeOrigins(),
    getSessionToken: () => "jwt",
  });
  cleanup();

  assert.equal(calls.length, 2);
  assert.equal(calls[0][0], "add");
  assert.equal(calls[1][0], "remove");
  assert.equal(calls[1][2], installedHandler);
});
