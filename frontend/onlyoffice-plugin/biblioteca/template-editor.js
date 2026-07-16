(function () {
  "use strict";

  var API_DEFAULT = "https://easypronotarial-2-production.up.railway.app";
  var selectedCode = "";
  var selectedLabel = "";
  var HIGHLIGHT = { r: 255, g: 242, b: 102 };

  function apiBase() {
    var config = window.EASYPRO_ONLYOFFICE_PLUGIN_CONFIG || {};
    return String(config.apiBaseUrl || API_DEFAULT).replace(/\/$/, "");
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
    var occurrence = "manual_" + Date.now();
    var tag = "easypro:template:v1:" + selectedCode + ":" + occurrence;
    var added = await execute("AddContentControl", [1, {
      Tag: tag,
      Alias: "EasyPro etiqueta - " + selectedCode
    }]);
    if (!added.ok) {
      state("No fue posible insertar la etiqueta en la posición del cursor.", "error");
      return;
    }
    var value = added.value || {};
    var internalId = value.InternalId || value.InternalID || value.Id || value.id;
    if (internalId) {
      await execute("InsertAndReplaceContentControls", [[{
        InternalId: internalId,
        Tag: tag,
        Alias: "EasyPro etiqueta - " + selectedCode,
        Text: marker
      }]]);
    }
    await command("easyproTemplateMarkerPayload", {
      marker: marker,
      r: HIGHLIGHT.r,
      g: HIGHLIGHT.g,
      b: HIGHLIGHT.b
    }, highlightMarkersCommand);
    state("✓ " + marker + " insertado. Continúa editando y guarda el documento una sola vez.", "ok");
  }

  async function createAndInsert() {
    var codeInput = document.getElementById("manualFieldCode");
    var labelInput = document.getElementById("manualFieldLabel");
    var categoryInput = document.getElementById("manualFieldCategory");
    var code = String(codeInput && codeInput.value || "")
      .trim().toUpperCase().replace(/[^A-Z0-9]+/g, "_").replace(/^_+|_+$/g, "");
    var label = String(labelInput && labelInput.value || "").trim();
    var category = String(categoryInput && categoryInput.value || "otro").trim() || "otro";
    if (code.length < 2 || label.length < 2) {
      state("Escribe el código y el nombre de la nueva etiqueta.", "error");
      return;
    }
    try {
      var api = window.__EasyProBibliotecaPlugin;
      var token = await api.test.solicitarToken();
      var response = await window.fetch(apiBase() + "/api/v1/biblioteca/campos", {
        method: "POST",
        headers: {
          Authorization: "Bearer " + token,
          Accept: "application/json",
          "Content-Type": "application/json"
        },
        credentials: "omit",
        body: JSON.stringify({ code: code, label: label, category: category, field_type: "text" })
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

  function hideLegacyValueEditors() {
    document.querySelectorAll(".sugerencia-card").forEach(function (card) {
      if (card.textContent && card.textContent.indexOf("Aplicar en cascada") !== -1) {
        card.style.display = "none";
      }
    });
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
      '<button id="btnMostrarCrearEtiqueta" class="btn btn-secondary" type="button">+ Crear nueva etiqueta</button>',
      '<div id="crearEtiquetaPanel" class="new-field-panel" style="display:none">',
      '<input id="manualFieldLabel" class="search" placeholder="Nombre visible, ej. Número de parqueadero"/>',
      '<input id="manualFieldCode" class="search" placeholder="CÓDIGO, ej. NUMERO_PARQUEADERO"/>',
      '<input id="manualFieldCategory" class="search" placeholder="Categoría, ej. inmueble"/>',
      '<button id="btnCrearEInsertar" class="btn btn-primary" type="button">Crear e insertar</button>',
      '</div>'
    ].join("");
    section.insertBefore(controls, list);

    document.getElementById("btnInsertarMarcador").addEventListener("click", insertSelected);
    document.getElementById("btnMostrarCrearEtiqueta").addEventListener("click", function () {
      var panel = document.getElementById("crearEtiquetaPanel");
      panel.style.display = panel.style.display === "none" ? "block" : "none";
    });
    document.getElementById("btnCrearEInsertar").addEventListener("click", createAndInsert);

    var observer = new MutationObserver(hideLegacyValueEditors);
    observer.observe(document.body, { childList: true, subtree: true });
    hideLegacyValueEditors();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", install);
  } else {
    install();
  }
}());
