(function () {
  "use strict";

  var SPIKE_VERSION = "0.1.0";
  var TEST_TOKEN = "EASYPRO_SPIKE_RANGE_2026";
  var UPDATED_TOKEN = "EASYPRO_SPIKE_UPDATED_2026";
  var SPIKE_TAG = "easypro:spike:v1:EASYPRO_SPIKE_RANGE_2026";
  var HIGHLIGHT_RGB = { r: 255, g: 242, b: 102 };
  var METHOD_TIMEOUT_MS = 8000;

  var state = createInitialState();
  var statusItems = [];
  var pendingMethods = [];
  var originalOnMethodReturn = null;

  function createInitialState() {
    return {
      spike_version: SPIKE_VERSION,
      onlyoffice_version: "",
      test_token_matches: 0,
      capabilities: {
        document_supported: false,
        search_supported: false,
        range_text_supported: false,
        select_supported: false,
        highlight_supported: false,
        content_control_create_supported: false,
        content_control_tag_write_supported: false,
        content_control_tag_read_supported: false,
        content_control_update_supported: false,
        content_control_list_supported: false
      },
      range: {
        resolved: false,
        text_matches: false,
        select: "UNSUPPORTED",
        highlight_apply: "UNSUPPORTED",
        highlight_clear: "UNSUPPORTED"
      },
      content_control: {
        created: false,
        tag_written: false,
        tag_read: false,
        content_updated: false,
        content_restored: false,
        persisted_after_reopen: false
      },
      errors: []
    };
  }

  function readOnlyOfficeVersion() {
    var info = window.Asc && window.Asc.plugin ? window.Asc.plugin.info : null;
    if (!info || typeof info !== "object") return "";
    return String(info.editorVersion || info.version || info.buildVersion || info.editorId || "");
  }

  function safeError(error) {
    if (!error) return "unknown_error";
    if (typeof error === "string") return error.slice(0, 120);
    if (error.code) return String(error.code).slice(0, 120);
    if (error.message) return String(error.message).split("\n")[0].slice(0, 120);
    return "operation_failed";
  }

  function setStatus(name, status, reason) {
    statusItems.unshift({
      name: name,
      status: status,
      reason: reason || ""
    });
    if (status === "FAIL") {
      state.errors.push({ step: name, reason: reason || "failed" });
    }
    renderStatus();
    renderReport();
  }

  function renderStatus() {
    var list = document.getElementById("statusList");
    if (!list) return;
    list.innerHTML = "";
    statusItems.slice(0, 40).forEach(function (item) {
      var row = document.createElement("div");
      row.className = "status-item " + item.status;

      var name = document.createElement("div");
      name.className = "status-name";
      name.textContent = item.status + " - " + item.name;

      var reason = document.createElement("div");
      reason.className = "status-reason";
      reason.textContent = item.reason || "";

      row.appendChild(name);
      row.appendChild(reason);
      list.appendChild(row);
    });
  }

  function renderReport() {
    var report = document.getElementById("reportJson");
    if (!report) return;
    report.value = JSON.stringify(state, null, 2);
  }

  function parseCommandResult(value) {
    if (typeof value === "string" && value.trim()) {
      try {
        return JSON.parse(value);
      } catch (error) {
        return { ok: false, error: "invalid_command_json" };
      }
    }
    return value && typeof value === "object" ? value : { ok: false, error: "empty_command_result" };
  }

  function callOnlyOfficeCommand(scopeKey, payload, command) {
    return new Promise(function (resolve) {
      if (!window.Asc || !window.Asc.plugin || typeof window.Asc.plugin.callCommand !== "function") {
        resolve({ ok: false, error: "callCommand_unavailable" });
        return;
      }
      window.Asc.scope = window.Asc.scope || {};
      window.Asc.scope[scopeKey] = JSON.stringify(payload || {});
      try {
        window.Asc.plugin.callCommand(command, false, true, function (returnValue) {
          resolve(parseCommandResult(returnValue));
        });
      } catch (error) {
        resolve({ ok: false, error: "callCommand_exception" });
      }
    });
  }

  function settleMethod(item, returnValue) {
    if (!item || item.done) return;
    item.done = true;
    window.clearTimeout(item.timer);
    pendingMethods = pendingMethods.filter(function (candidate) {
      return candidate !== item;
    });
    item.resolve({ ok: true, method: item.name, returnValue: returnValue });
  }

  function executeMethodAsync(name, args) {
    return new Promise(function (resolve) {
      if (!window.Asc || !window.Asc.plugin || typeof window.Asc.plugin.executeMethod !== "function") {
        resolve({ ok: false, method: name, error: "executeMethod_unavailable" });
        return;
      }
      var item = {
        name: name,
        done: false,
        resolve: resolve,
        timer: window.setTimeout(function () {
          if (item.done) return;
          item.done = true;
          pendingMethods = pendingMethods.filter(function (candidate) {
            return candidate !== item;
          });
          resolve({ ok: false, method: name, error: "method_timeout" });
        }, METHOD_TIMEOUT_MS)
      };
      pendingMethods.push(item);
      try {
        window.Asc.plugin.executeMethod(name, args, function (returnValue) {
          settleMethod(item, returnValue);
        });
      } catch (error) {
        window.clearTimeout(item.timer);
        item.done = true;
        pendingMethods = pendingMethods.filter(function (candidate) {
          return candidate !== item;
        });
        resolve({ ok: false, method: name, error: "executeMethod_exception" });
      }
    });
  }

  function onMethodReturn(returnValue) {
    var methodName = window.Asc && window.Asc.plugin && window.Asc.plugin.info
      ? window.Asc.plugin.info.methodName
      : "";
    var item = pendingMethods.find(function (candidate) {
      return !methodName || candidate.name === methodName;
    });
    if (item) {
      settleMethod(item, returnValue);
      return;
    }
    if (typeof originalOnMethodReturn === "function") {
      originalOnMethodReturn(returnValue);
    }
  }

  function singleRange(ranges) {
    if (!Array.isArray(ranges)) {
      return { ok: false, count: 0, reason: "search_result_not_array" };
    }
    if (ranges.length !== 1) {
      return { ok: false, count: ranges.length, reason: ranges.length === 0 ? "token_not_found" : "token_not_unique" };
    }
    return { ok: true, count: 1, range: ranges.slice(0, 1).pop() };
  }

  function getRangeText(range) {
    if (range && typeof range.GetText === "function") return range.GetText();
    if (range && typeof range.text === "string") return range.text;
    return null;
  }

  function safeSearchCommand() {
    try {
      var doc = Api.GetDocument();
      var caps = {
        document_supported: Boolean(doc),
        search_supported: Boolean(doc && typeof doc.Search === "function"),
        range_text_supported: false,
        select_supported: false,
        highlight_supported: false
      };
      if (!caps.search_supported) {
        return JSON.stringify({ ok: false, capabilities: caps, count: 0, error: "search_unavailable" });
      }
      var ranges = doc.Search(TEST_TOKEN, false) || [];
      var selected = singleRange(ranges);
      if (!selected.ok) {
        return JSON.stringify({ ok: false, capabilities: caps, count: selected.count, error: selected.reason });
      }
      var range = selected.range;
      var text = getRangeText(range);
      caps.range_text_supported = text !== null;
      caps.select_supported = typeof range.Select === "function";
      caps.highlight_supported = typeof range.SetHighlight === "function";
      return JSON.stringify({
        ok: text === TEST_TOKEN,
        capabilities: caps,
        count: 1,
        text_matches: text === TEST_TOKEN,
        error: text === TEST_TOKEN ? null : "range_text_mismatch"
      });
    } catch (error) {
      return JSON.stringify({ ok: false, count: 0, error: "search_command_failed" });
    }
  }

  function selectRangeCommand() {
    try {
      var doc = Api.GetDocument();
      if (!doc || typeof doc.Search !== "function") {
        return JSON.stringify({ ok: false, count: 0, error: "search_unavailable" });
      }
      var selected = singleRange(doc.Search(TEST_TOKEN, false) || []);
      if (!selected.ok) return JSON.stringify({ ok: false, count: selected.count, error: selected.reason });
      var range = selected.range;
      if (getRangeText(range) !== TEST_TOKEN) {
        return JSON.stringify({ ok: false, count: 1, error: "range_text_mismatch" });
      }
      if (typeof range.Select !== "function") {
        return JSON.stringify({ ok: false, count: 1, error: "select_unavailable" });
      }
      range.Select();
      return JSON.stringify({ ok: true, count: 1 });
    } catch (error) {
      return JSON.stringify({ ok: false, count: 0, error: "select_command_failed" });
    }
  }

  function highlightCommand() {
    try {
      var payload = JSON.parse(Asc.scope.easyproSpikeHighlightPayload || "{}");
      var doc = Api.GetDocument();
      if (!doc || typeof doc.Search !== "function") {
        return JSON.stringify({ ok: false, count: 0, error: "search_unavailable" });
      }
      var selected = singleRange(doc.Search(TEST_TOKEN, false) || []);
      if (!selected.ok) return JSON.stringify({ ok: false, count: selected.count, error: selected.reason });
      var range = selected.range;
      if (getRangeText(range) !== TEST_TOKEN) {
        return JSON.stringify({ ok: false, count: 1, error: "range_text_mismatch" });
      }
      if (typeof range.SetHighlight !== "function") {
        return JSON.stringify({ ok: false, count: 1, error: "highlight_unavailable" });
      }
      if (payload.clear) {
        range.SetHighlight(null);
      } else {
        range.SetHighlight(HIGHLIGHT_RGB.r, HIGHLIGHT_RGB.g, HIGHLIGHT_RGB.b);
      }
      return JSON.stringify({ ok: true, count: 1 });
    } catch (error) {
      return JSON.stringify({ ok: false, count: 0, error: "highlight_command_failed" });
    }
  }

  function countTokenCommand() {
    try {
      var payload = JSON.parse(Asc.scope.easyproSpikeCountPayload || "{}");
      var token = payload.token === UPDATED_TOKEN ? UPDATED_TOKEN : TEST_TOKEN;
      var doc = Api.GetDocument();
      if (!doc || typeof doc.Search !== "function") {
        return JSON.stringify({ ok: false, count: 0, error: "search_unavailable" });
      }
      var ranges = doc.Search(token, false) || [];
      return JSON.stringify({ ok: true, count: Array.isArray(ranges) ? ranges.length : 0 });
    } catch (error) {
      return JSON.stringify({ ok: false, count: 0, error: "count_command_failed" });
    }
  }

  function updateCapabilities(result) {
    var caps = result && result.capabilities ? result.capabilities : {};
    Object.keys(caps).forEach(function (key) {
      state.capabilities[key] = Boolean(caps[key]);
    });
    if (typeof result.count === "number") {
      state.test_token_matches = result.count;
    }
  }

  async function detectCapabilities() {
    var result = await callOnlyOfficeCommand("easyproSpikeSearchPayload", {}, safeSearchCommand);
    updateCapabilities(result);
    if (result.ok) {
      state.range.resolved = true;
      state.range.text_matches = true;
      setStatus("Detectar capacidades de rango", "PASS", "Documento, busqueda y rango unico disponibles.");
    } else {
      state.range.resolved = false;
      state.range.text_matches = false;
      setStatus("Detectar capacidades de rango", result.error === "highlight_unavailable" ? "UNSUPPORTED" : "FAIL", result.error || "failed");
    }

    var controls = await readSpikeControls(false);
    if (controls.ok) {
      state.capabilities.content_control_list_supported = true;
      setStatus("Detectar lista de Content Controls", "PASS", "GetAllContentControls respondio.");
    } else {
      setStatus("Detectar lista de Content Controls", "UNSUPPORTED", controls.error || "content_control_list_unavailable");
    }
  }

  async function locateRange() {
    var result = await callOnlyOfficeCommand("easyproSpikeSearchPayload", {}, safeSearchCommand);
    updateCapabilities(result);
    state.range.resolved = Boolean(result.ok);
    state.range.text_matches = Boolean(result.text_matches);
    setStatus("Localizar rango", result.ok ? "PASS" : "FAIL", result.ok ? "Coincidencia unica verificada." : (result.error || "failed"));
    return result;
  }

  async function selectRange() {
    var result = await callOnlyOfficeCommand("easyproSpikeSelectPayload", {}, selectRangeCommand);
    state.range.select = result.ok ? "PASS" : (result.error === "select_unavailable" ? "UNSUPPORTED" : "FAIL");
    setStatus("Seleccionar rango", state.range.select, result.ok ? "Rango seleccionado." : (result.error || "failed"));
    return result;
  }

  async function applyHighlight(clear) {
    var result = await callOnlyOfficeCommand("easyproSpikeHighlightPayload", { clear: Boolean(clear) }, highlightCommand);
    var key = clear ? "highlight_clear" : "highlight_apply";
    state.range[key] = result.ok ? "PASS" : (result.error === "highlight_unavailable" ? "UNSUPPORTED" : "FAIL");
    setStatus(clear ? "Retirar highlight" : "Aplicar highlight", state.range[key], result.ok ? "SetHighlight ejecutado." : (result.error || "failed"));
    return result;
  }

  function controlTag(control) {
    if (!control || typeof control !== "object") return "";
    return String(control.Tag || control.tag || (control.Props && control.Props.Tag) || "");
  }

  function controlInternalId(control) {
    if (!control || typeof control !== "object") return "";
    return String(control.InternalId || control.internalId || (control.Props && control.Props.InternalId) || control.Id || "");
  }

  async function readSpikeControls(visible) {
    var result = await executeMethodAsync("GetAllContentControls", null);
    if (!result.ok || !Array.isArray(result.returnValue)) {
      if (visible) setStatus("Leer Content Controls", "UNSUPPORTED", result.error || "invalid_content_control_list");
      return { ok: false, error: result.error || "invalid_content_control_list", controls: [] };
    }
    var controls = result.returnValue.filter(function (control) {
      return controlTag(control) === SPIKE_TAG;
    });
    state.capabilities.content_control_list_supported = true;
    state.capabilities.content_control_tag_read_supported = controls.length > 0;
    state.content_control.tag_read = controls.length > 0;
    if (visible) {
      setStatus("Leer Content Controls", "PASS", "Controles spike encontrados: " + String(controls.length));
    }
    return { ok: true, controls: controls };
  }

  async function createContentControl() {
    var selected = await selectRange();
    if (!selected.ok) {
      setStatus("Crear Content Control", "FAIL", "No hay rango seleccionado y verificado.");
      return selected;
    }
    var props = {
      Tag: SPIKE_TAG,
      Alias: "EasyPro Spike",
      Lock: 0,
      Appearance: 1
    };
    var result = await executeMethodAsync("AddContentControl", [2, props]);
    if (!result.ok) {
      state.capabilities.content_control_create_supported = false;
      setStatus("Crear Content Control", "UNSUPPORTED", result.error || "add_content_control_failed");
      return result;
    }
    var controls = await readSpikeControls(false);
    if (controls.ok && controls.controls.length > 0) {
      state.capabilities.content_control_create_supported = true;
      state.capabilities.content_control_tag_write_supported = true;
      state.capabilities.content_control_tag_read_supported = true;
      state.content_control.created = true;
      state.content_control.tag_written = true;
      state.content_control.tag_read = true;
      setStatus("Crear Content Control", "PASS", "Tag EasyPro creado y leido.");
    } else {
      state.capabilities.content_control_create_supported = false;
      state.content_control.created = false;
      state.content_control.tag_written = false;
      setStatus("Crear Content Control", "UNSUPPORTED", "AddContentControl no produjo un control spike verificable.");
    }
    return result;
  }

  function contentControlPayload(internalId, value) {
    var safeValue = value === UPDATED_TOKEN ? UPDATED_TOKEN : TEST_TOKEN;
    var script = "var oDocument = Api.GetDocument();"
      + "var oParagraph = Api.CreateParagraph();"
      + "oParagraph.AddText('" + safeValue + "');"
      + "oDocument.InsertContent([oParagraph], true);";
    return [{
      Props: {
        InternalId: internalId,
        Tag: SPIKE_TAG,
        Alias: "EasyPro Spike",
        Lock: 0,
        Appearance: 1
      },
      Script: script
    }];
  }

  async function currentSpikeControl() {
    var controls = await readSpikeControls(false);
    if (!controls.ok) return { ok: false, error: controls.error };
    if (controls.controls.length !== 1) {
      return {
        ok: false,
        error: controls.controls.length === 0 ? "spike_control_not_found" : "multiple_spike_controls"
      };
    }
    var internalId = controlInternalId(controls.controls.slice(0, 1).pop());
    if (!internalId) return { ok: false, error: "missing_internal_id" };
    return { ok: true, internalId: internalId };
  }

  async function setContent(value) {
    var control = await currentSpikeControl();
    if (!control.ok) {
      setStatus(value === UPDATED_TOKEN ? "Actualizar contenido" : "Restaurar contenido", "FAIL", control.error);
      return control;
    }
    var result = await executeMethodAsync("InsertAndReplaceContentControls", [contentControlPayload(control.internalId, value)]);
    if (!result.ok) {
      setStatus(value === UPDATED_TOKEN ? "Actualizar contenido" : "Restaurar contenido", "UNSUPPORTED", result.error || "insert_replace_unavailable");
      return result;
    }
    var verification = await callOnlyOfficeCommand("easyproSpikeCountPayload", { token: value }, countTokenCommand);
    var verified = Boolean(verification.ok && verification.count === 1);
    state.capabilities.content_control_update_supported = verified;
    if (value === UPDATED_TOKEN) {
      state.content_control.content_updated = verified;
      setStatus("Actualizar contenido", verified ? "PASS" : "FAIL", verified ? "Contenido actualizado y verificado." : "La actualizacion no pudo verificarse en el documento.");
    } else {
      state.content_control.content_restored = verified;
      setStatus("Restaurar contenido", verified ? "PASS" : "FAIL", verified ? "Contenido restaurado y verificado." : "La restauracion no pudo verificarse en el documento.");
    }
    return result;
  }

  async function verifyPersistence() {
    var controls = await readSpikeControls(false);
    var count = await callOnlyOfficeCommand("easyproSpikeCountPayload", { token: TEST_TOKEN }, countTokenCommand);
    var ok = Boolean(controls.ok && controls.controls.length === 1 && count.ok && count.count === 1);
    state.content_control.persisted_after_reopen = ok;
    setStatus("Verificar persistencia despues de reapertura", ok ? "PASS" : "FAIL", ok ? "Tag y contenido restaurado encontrados." : "No se encontro exactamente un control spike persistente.");
    return { ok: ok };
  }

  async function cleanupSpike() {
    var controls = await readSpikeControls(false);
    if (!controls.ok) {
      setStatus("Limpiar spike", "UNSUPPORTED", controls.error || "content_control_list_unavailable");
      return controls;
    }
    if (!controls.controls.length) {
      setStatus("Limpiar spike", "PASS", "No hay controles spike.");
      return { ok: true };
    }
    var payload = controls.controls.map(function (control) {
      return { InternalId: controlInternalId(control) };
    }).filter(function (item) {
      return item.InternalId;
    });
    if (!payload.length) {
      setStatus("Limpiar spike", "FAIL", "No se pudo leer InternalId del control spike.");
      return { ok: false };
    }
    var result = await executeMethodAsync("RemoveContentControls", [payload]);
    setStatus("Limpiar spike", result.ok ? "PASS" : "UNSUPPORTED", result.ok ? "Controles spike removidos." : (result.error || "remove_unavailable"));
    return result;
  }

  async function copyReport() {
    renderReport();
    var report = document.getElementById("reportJson");
    if (!report) return;
    report.focus();
    report.select();
    try {
      if (navigator.clipboard && typeof navigator.clipboard.writeText === "function") {
        await navigator.clipboard.writeText(report.value);
        setStatus("Copiar informe tecnico", "PASS", "JSON copiado.");
        return;
      }
    } catch (error) {
      // Fall through to manual copy status.
    }
    setStatus("Copiar informe tecnico", "UNSUPPORTED", "Seleccione el JSON y copielo manualmente.");
  }

  function bind(id, handler) {
    var el = document.getElementById(id);
    if (!el) return;
    el.addEventListener("click", function () {
      Promise.resolve(handler()).catch(function (error) {
        setStatus(id, "FAIL", safeError(error));
      });
    });
  }

  function prepareDom() {
    state.onlyoffice_version = readOnlyOfficeVersion();
    bind("btnDetect", detectCapabilities);
    bind("btnLocate", locateRange);
    bind("btnSelect", selectRange);
    bind("btnHighlight", function () { return applyHighlight(false); });
    bind("btnClearHighlight", function () { return applyHighlight(true); });
    bind("btnCreateControl", createContentControl);
    bind("btnReadControls", function () { return readSpikeControls(true); });
    bind("btnUpdateContent", function () { return setContent(UPDATED_TOKEN); });
    bind("btnRestoreContent", function () { return setContent(TEST_TOKEN); });
    bind("btnVerifyPersistence", verifyPersistence);
    bind("btnCopyReport", copyReport);
    bind("btnCleanup", cleanupSpike);
    renderStatus();
    renderReport();
  }

  window.Asc = window.Asc || {};
  window.Asc.plugin = window.Asc.plugin || {};

  originalOnMethodReturn = window.Asc.plugin.onMethodReturn;
  window.Asc.plugin.onMethodReturn = onMethodReturn;
  window.Asc.plugin.init = function () {
    prepareDom();
  };
  window.Asc.plugin.button = function () {};

  window.__EasyProBibliotecaSpike = {
    constants: {
      SPIKE_VERSION: SPIKE_VERSION,
      TEST_TOKEN: TEST_TOKEN,
      UPDATED_TOKEN: UPDATED_TOKEN,
      SPIKE_TAG: SPIKE_TAG
    },
    test: {
      detectCapabilities: detectCapabilities,
      locateRange: locateRange,
      selectRange: selectRange,
      applyHighlight: applyHighlight,
      createContentControl: createContentControl,
      readSpikeControls: readSpikeControls,
      setContent: setContent,
      verifyPersistence: verifyPersistence,
      cleanupSpike: cleanupSpike,
      safeSearchCommand: safeSearchCommand,
      selectRangeCommand: selectRangeCommand,
      highlightCommand: highlightCommand,
      countTokenCommand: countTokenCommand,
      singleRange: singleRange,
      getReport: function () { return state; },
      getStatusItems: function () { return statusItems; }
    }
  };
}());
