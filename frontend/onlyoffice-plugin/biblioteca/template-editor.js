(function () {
  "use strict";

  var API_DEFAULT = "https://easypronotarial-2-production.up.railway.app";
  var PLUGIN_SOURCE = "motor-biblioteca";
  var RETURN_REQUEST_TYPE = "EASYPRO_MINUTA_TEMPLATE_RETURN_REQUEST";
  var TEMPLATE_STATE_PATH = "/api/v1/minutas/marked-template/editor-state";
  var DEFAULT_HOST_ORIGINS = [
    "https://easypronotarial.com",
    "http://localhost:5179",
    "http://127.0.0.1:5179"
  ];
  var HIGHLIGHT = { r: 255, g: 242, b: 102 };
  var selectedCode = "";
  var selectedLabel = "";
  var templateMode = false;

  function pluginApi() {
    return window.__EasyProBibliotecaPlugin || null;
  }

  function apiBase() {
    var api = pluginApi();
    if (api && api.test && typeof api.test.obtenerApiBaseUrl === "function") {
      return api.test.obtenerApiBaseUrl();
    }
    var config = window.EASYPRO_ONLYOFFICE_PLUGIN_CONFIG || {};
    return String(config.apiBaseUrl || API_DEFAULT).replace(/\/$/, "");
  }

  function normalizeOrigin(value) {
    if (typeof value !== "string" || !value.trim()) return null;
    try {
      return new URL(value.trim()).origin;
    } catch (_error) {
      return null;
    }
  }

  function hostOrigins() {
    var config = window.EASYPRO_ONLYOFFICE_PLUGIN_CONFIG || {};
    var origins = DEFAULT_HOST_ORIGINS.slice();
    if (Array.isArray(config.hostOrigins)) {
      config.hostOrigins.forEach(function (origin) { origins.push(origin); });
    }
    return origins.map(normalizeOrigin).filter(function (origin, index, all) {
      return origin && all.indexOf(origin) === index;
    });
  }

  function postTargets() {
    var targets = [];
    function add(target) {
      if (target && targets.indexOf(target) === -1) targets.push(target);
    }
    add(window.parent);
    add(window.top);
    try {
      var current = window;
      for (var index = 0; index < 5; index += 1) {
        if (!current.parent || current.parent === current) break;
        current = current.parent;
        add(current);
      }
    } catch (_error) {
      // Best effort only.
    }
    return targets;
  }

  function state(message, kind) {
    var element = document.getElementById("estado");
    if (!element) return;
    element.textContent = message;
    element.className = kind === "error" ? "error" : kind === "ok" ? "ok" : "";
    element.style.display = "block";
  }

  function execute(name, args) {
    return new Promise(function (resolve) {
      try {
        window.Asc.plugin.executeMethod(name, args || [], function (result) {
          resolve({ ok: result !== false && !(result && result.error), value: result });
        });
      } catch (error) {
        resolve({ ok: false, error: "execute_failed" });
      }
    });
  }

  function executeCommand(name, value) {
    return new Promise(function (resolve) {
      try {
        if (!window.Asc || !window.Asc.plugin || typeof window.Asc.plugin.executeCommand !== "function") {
          resolve({ ok: false, error: "executeCommand_unavailable" });
          return;
        }
        window.Asc.plugin.executeCommand(name, value || "");
        resolve({ ok: true });
      } catch (_error) {
        resolve({ ok: false, error: "executeCommand_failed" });
      }
    });
  }

  function command(scopeKey, payload, callback) {
    return new Promise(function (resolve) {
      window.Asc.scope = window.Asc.scope || {};
      window.Asc.scope[scopeKey] = JSON.stringify(payload || {});
      try {
        window.Asc.plugin.callCommand(callback, false, true, function (value) {
          try { resolve(typeof value === "string" ? JSON.parse(value) : value); }
          catch (_error) { resolve({ ok: false }); }
        });
      } catch (_error) {
        resolve({ ok: false });
      }
    });
  }

  function insertMarkerTextCommand() {
    try {
      var payload = JSON.parse(Asc.scope.easyproTemplateMarkerPayload || "{}");
      var marker = String(payload.marker || "");
      if (!marker) return JSON.stringify({ ok: false });
      var document = Api.GetDocument();
      // Automated tests can assert that we avoid paragraph insertion; final cursor fidelity still requires manual verification in real OnlyOffice.
      var range = document && typeof document.GetRangeBySelect === "function"
        ? document.GetRangeBySelect()
        : null;
      if (range && typeof range.SetText === "function") {
        range.SetText(marker);
        return JSON.stringify({ ok: true, mode: "range.SetText" });
      }
      if (range && typeof range.AddText === "function") {
        range.AddText(marker);
        return JSON.stringify({ ok: true, mode: "range.AddText" });
      }
      if (typeof Api.CreateRun === "function" && document && typeof document.InsertContent === "function") {
        var run = Api.CreateRun();
        if (run && typeof run.AddText === "function") {
          run.AddText(marker);
          document.InsertContent([run], true);
          return JSON.stringify({ ok: true, mode: "InsertContent.run" });
        }
      }
      return JSON.stringify({ ok: false, reason: "inline_api_unavailable" });
    } catch (_error) {
      return JSON.stringify({ ok: false });
    }
  }

  function highlightMarkersCommand() {
    try {
      var payload = JSON.parse(Asc.scope.easyproTemplateMarkerPayload || "{}");
      var document = Api.GetDocument();
      var ranges = document && typeof document.Search === "function"
        ? document.Search(payload.marker, false) || []
        : [];
      var count = 0;
      for (var index = 0; index < ranges.length; index += 1) {
        if (ranges[index] && typeof ranges[index].SetHighlight === "function") {
          ranges[index].SetHighlight(payload.r, payload.g, payload.b);
          count += 1;
        }
      }
      return JSON.stringify({ ok: count > 0, count: count });
    } catch (_error) {
      return JSON.stringify({ ok: false, count: 0 });
    }
  }

  function choose(code, label, item) {
    selectedCode = String(code || "").trim().toUpperCase();
    selectedLabel = String(label || selectedCode).trim();
    document.querySelectorAll(".campo-item.selected").forEach(function (node) {
      node.classList.remove("selected");
    });
    if (item) item.classList.add("selected");
    var selected = document.getElementById("campoSeleccionado");
    if (selected) selected.textContent = selectedCode
      ? "Etiqueta seleccionada: " + selectedCode
      : "Selecciona una etiqueta del listado";
    var button = document.getElementById("btnInsertarMarcador");
    if (button) button.disabled = !selectedCode;
  }

  async function insertSelected() {
    if (!selectedCode) {
      state("Selecciona primero una etiqueta.", "error");
      return;
    }
    var marker = "{{" + selectedCode + "}}";
    var payload = {
      marker: marker,
      r: HIGHLIGHT.r,
      g: HIGHLIGHT.g,
      b: HIGHLIGHT.b
    };
    var pasted = await execute("PasteText", [marker]);
    var inserted = pasted && pasted.ok ? { ok: true, mode: "PasteText" } : await command("easyproTemplateMarkerPayload", payload, insertMarkerTextCommand);
    if (!inserted || inserted.ok !== true) {
      state("No fue posible insertar la etiqueta en la posicion del cursor.", "error");
      return;
    }
    await command("easyproTemplateMarkerPayload", payload, highlightMarkersCommand);
    state("Etiqueta " + marker + " insertada. Puedes insertar mas etiquetas antes de guardar.", "ok");
  }

  function catalogHasCode(code) {
    var normalized = String(code || "").trim().toUpperCase();
    var found = false;
    document.querySelectorAll("#listaCampos .campo-code").forEach(function (node) {
      if (String(node.textContent || "").trim().toUpperCase() === normalized) found = true;
    });
    return found;
  }

  async function createAndInsert() {
    var codeInput = document.getElementById("manualFieldCode");
    var labelInput = document.getElementById("manualFieldLabel");
    var categoryInput = document.getElementById("manualFieldCategory");
    var scopeInput = document.getElementById("manualFieldScope");
    var code = String(codeInput && codeInput.value || "")
      .trim().toUpperCase().replace(/[^A-Z0-9]+/g, "_").replace(/^_+|_+$/g, "");
    var label = String(labelInput && labelInput.value || "").trim();
    var category = String(categoryInput && categoryInput.value || "otro").trim() || "otro";
    var scope = String(scopeInput && scopeInput.value || "notary").trim() || "notary";
    if (code.length < 2 || label.length < 2) {
      state("Escribe el codigo y el nombre de la nueva etiqueta.", "error");
      return;
    }
    if (catalogHasCode(code)) {
      choose(code, label, null);
      await insertSelected();
      state("La etiqueta ya existia en la biblioteca; se inserto sin duplicarla.", "ok");
      return;
    }
    try {
      var api = pluginApi();
      var token = await api.test.solicitarToken();
      var response = await window.fetch(apiBase() + "/api/v1/biblioteca/campos", {
        method: "POST",
        headers: {
          Authorization: "Bearer " + token,
          Accept: "application/json",
          "Content-Type": "application/json"
        },
        credentials: "omit",
        body: JSON.stringify({ code: code, label: label, category: category, field_type: "text", scope: scope })
      });
      if (!response.ok) throw new Error("create_failed");
      choose(code, label, null);
      if (typeof window.cargarCatalogo === "function") await window.cargarCatalogo();
      await insertSelected();
      var panel = document.getElementById("crearEtiquetaPanel");
      if (panel) panel.style.display = "none";
    } catch (_error) {
      state("No fue posible crear la etiqueta en la biblioteca.", "error");
    }
  }

  function currentContext() {
    var api = pluginApi();
    if (!api || !api.test || typeof api.test.getDocumentContext !== "function") return null;
    return api.test.getDocumentContext();
  }

  async function requestSave() {
    await executeCommand("save", "");
    var methodResult = await execute("Save", []);
    return methodResult.ok;
  }

  async function fetchEditorState(token, editorToken) {
    var response = await window.fetch(
      apiBase() + TEMPLATE_STATE_PATH + "?token=" + encodeURIComponent(editorToken),
      {
        method: "GET",
        headers: { Authorization: "Bearer " + token, Accept: "application/json" },
        credentials: "omit",
        cache: "no-store"
      }
    );
    if (!response.ok) throw new Error("state_failed");
    return response.json();
  }

  function delay(ms) {
    return new Promise(function (resolve) { window.setTimeout(resolve, ms); });
  }

  async function waitForSavedState(token, editorToken, onTick) {
    var latest = null;
    for (var attempt = 0; attempt < 60; attempt += 1) {
      if (typeof onTick === "function") onTick(attempt);
      latest = await fetchEditorState(token, editorToken);
      if (latest && latest.saved) return latest;
      await delay(1000);
    }
    return latest;
  }

  function postReturnToForm(payload) {
    var message = {
      type: RETURN_REQUEST_TYPE,
      source: PLUGIN_SOURCE,
      payload: payload
    };
    postTargets().forEach(function (target) {
      hostOrigins().forEach(function (origin) {
        try {
          target.postMessage(message, origin);
        } catch (_error) {
          // Ignore frames that cannot receive the message.
        }
      });
    });
  }

  async function saveTemplateAndReturn() {
    try {
      var api = pluginApi();
      if (!api || !api.test) throw new Error("plugin_unavailable");
      var token = await api.test.solicitarToken();
      var context = currentContext();
      if (!context || context.kind !== "minuta" || !context.editor_token) {
        if (typeof api.test.refrescarAuthContexto === "function") {
          try {
            token = await api.test.refrescarAuthContexto();
          } catch (_error) {
            // The explicit availability error below is clearer for this flow.
          }
          context = currentContext();
        }
        if (!context || context.kind !== "minuta" || !context.editor_token) {
          state("Esta accion solo esta disponible al editar una plantilla de minuta.", "error");
          return;
        }
      }
      state("Guardando plantilla en OnlyOffice...", "");
      await requestSave();
      state("Esperando confirmacion de guardado... 0s", "");
      var payload = await waitForSavedState(token, context.editor_token, function (attempt) {
        state("Esperando confirmacion de guardado... " + String(attempt) + "s", "");
      });
      if (!payload || !payload.saved) {
        state("OnlyOffice aun no confirmo el guardado. Guarda el documento y vuelve a intentar.", "error");
        return;
      }
      state("Plantilla guardada. Volviendo al formulario...", "ok");
      postReturnToForm(payload);
    } catch (_error) {
      state("No fue posible guardar la plantilla y volver al formulario.", "error");
    }
  }

  function hideLegacyTemplateControls() {
    if (!templateMode) return;
    var analyzeSection = document.getElementById("btnAnalizar");
    if (analyzeSection && analyzeSection.parentElement) {
      analyzeSection.parentElement.style.display = "none";
    }
    var suggestions = document.getElementById("sugerencias");
    if (suggestions) suggestions.style.display = "none";
    var changePanel = document.getElementById("panelCambio");
    if (changePanel) changePanel.style.display = "none";
    document.querySelectorAll(".sugerencia-card").forEach(function (card) {
      card.style.display = "none";
    });
    var subtitle = document.querySelector(".subtitle");
    if (subtitle) subtitle.textContent = "Edicion de etiquetas de plantilla";
  }

  async function detectTemplateMode() {
    try {
      var api = pluginApi();
      if (!api || !api.test) return;
      await api.test.solicitarToken();
      var context = currentContext();
      templateMode = Boolean(context && context.kind === "minuta");
      hideLegacyTemplateControls();
    } catch (_error) {
      templateMode = false;
    }
  }

  function install() {
    var list = document.getElementById("listaCampos");
    if (!list) return;

    list.addEventListener("click", function (event) {
      var item = event.target && event.target.closest ? event.target.closest(".campo-item") : null;
      if (!item || !list.contains(item)) return;
      event.preventDefault();
      event.stopPropagation();
      if (event.stopImmediatePropagation) event.stopImmediatePropagation();
      var codeNode = item.querySelector(".campo-code");
      var labelNode = item.querySelector(".campo-label");
      choose(codeNode && codeNode.textContent, labelNode && labelNode.textContent, item);
    }, true);

    var section = list.parentNode;
    var controls = document.createElement("div");
    controls.className = "template-editor-controls";
    controls.innerHTML = [
      '<div id="campoSeleccionado" class="selected-field">Selecciona una etiqueta del listado</div>',
      '<button id="btnInsertarMarcador" class="btn btn-primary" type="button" disabled>Insertar en el cursor</button>',
      '<button id="btnMostrarCrearEtiqueta" class="btn btn-secondary" type="button">Crear nueva etiqueta</button>',
      '<div id="crearEtiquetaPanel" class="new-field-panel" style="display:none">',
      '<input id="manualFieldLabel" class="search" placeholder="Nombre visible, ej. Numero de parqueadero"/>',
      '<input id="manualFieldCode" class="search" placeholder="CODIGO_CANONICO, ej. NUMERO_PARQUEADERO"/>',
      '<input id="manualFieldCategory" class="search" placeholder="Categoria, ej. inmueble"/>',
      '<select id="manualFieldScope" class="search"><option value="notary">Alcance: notaria</option><option value="global">Alcance: global</option></select>',
      '<button id="btnCrearEInsertar" class="btn btn-primary" type="button">Crear e insertar</button>',
      '</div>',
      '<button id="btnGuardarPlantillaVolver" class="btn btn-primary" type="button">Guardar plantilla y volver al formulario</button>'
    ].join("");
    section.insertBefore(controls, list);

    document.getElementById("btnInsertarMarcador").addEventListener("click", insertSelected);
    document.getElementById("btnMostrarCrearEtiqueta").addEventListener("click", function () {
      var panel = document.getElementById("crearEtiquetaPanel");
      panel.style.display = panel.style.display === "none" ? "block" : "none";
    });
    document.getElementById("btnCrearEInsertar").addEventListener("click", createAndInsert);
    document.getElementById("btnGuardarPlantillaVolver").addEventListener("click", saveTemplateAndReturn);

    detectTemplateMode();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", install);
  } else {
    install();
  }
}());
