(function () {
  "use strict";

  var AUTH_RESPONSE_TYPE = "EASYPRO_ONLYOFFICE_AUTH_RESPONSE";
  var HOST_SOURCE = "easypro-host";
  var START_PATH = "/api/v1/biblioteca/analisis/iniciar-seguro";
  var STATUS_PATH = "/api/v1/biblioteca/analisis/";
  var STATUS_SUFFIX = "/estado-seguro";
  var POLL_MS = 4000;
  var MAX_WAIT_MS = 45 * 60 * 1000;
  var documentContext = null;
  var running = false;

  function apiBaseUrl() {
    var config = window.EASYPRO_ONLYOFFICE_PLUGIN_CONFIG || {};
    return String(config.apiBaseUrl || "https://easypronotarial-2-production.up.railway.app").replace(/\/$/, "");
  }

  function showStatus(message, type) {
    var element = document.getElementById("estado");
    if (!element) return;
    element.textContent = message;
    element.className = type === "error" ? "error" : type === "ok" ? "ok" : "";
    element.style.display = "block";
  }

  function setButtonBusy(value) {
    running = value;
    var button = document.getElementById("btnAnalizar");
    if (!button) return;
    button.disabled = value;
    button.textContent = value ? "Analizando en segundo plano..." : "Analizar documento";
  }

  function sleep(milliseconds) {
    return new Promise(function (resolve) {
      window.setTimeout(resolve, milliseconds);
    });
  }

  async function readJson(response) {
    try {
      return await response.json();
    } catch (_error) {
      return {};
    }
  }

  async function authorizedFetch(token, path, options) {
    var requestOptions = Object.assign({}, options || {});
    requestOptions.headers = Object.assign({}, requestOptions.headers || {}, {
      Authorization: "Bearer " + token,
      Accept: "application/json",
      "Content-Type": "application/json"
    });
    requestOptions.credentials = "omit";
    requestOptions.cache = "no-store";
    return window.fetch(apiBaseUrl() + path, requestOptions);
  }

  async function startJob(userToken, context) {
    var response = await authorizedFetch(userToken, START_PATH, {
      method: "POST",
      body: JSON.stringify(context)
    });
    var payload = await readJson(response);
    if (!response.ok || !payload.run_id || !payload.poll_token) {
      var detail = payload.detail || payload.error_code || "No fue posible iniciar el análisis.";
      throw new Error(String(detail));
    }
    return payload;
  }

  async function getJobStatus(pollToken, runId) {
    var response = await authorizedFetch(
      pollToken,
      STATUS_PATH + String(runId) + STATUS_SUFFIX,
      { method: "GET" }
    );
    var payload = await readJson(response);
    if (!response.ok) {
      throw new Error(String(payload.detail || "No fue posible consultar el análisis."));
    }
    return payload;
  }

  function elapsedText(startedAt) {
    var seconds = Math.max(0, Math.floor((Date.now() - startedAt) / 1000));
    var minutes = Math.floor(seconds / 60);
    var remaining = seconds % 60;
    return minutes ? minutes + " min " + remaining + " s" : remaining + " s";
  }

  async function analyzeAsync() {
    if (running) return;
    setButtonBusy(true);
    var startedAt = Date.now();
    try {
      var plugin = window.__EasyProBibliotecaPlugin;
      if (!plugin || !plugin.test) throw new Error("Plugin no inicializado.");
      var userToken = await plugin.test.solicitarToken();
      if (!documentContext) throw new Error("No fue posible identificar el documento abierto.");

      var start = await startJob(userToken, documentContext);
      var runId = start.run_id;
      var pollToken = start.poll_token;
      showStatus(
        start.reused
          ? "Retomando análisis en curso..."
          : "Análisis iniciado. Puede tardar varios minutos; no cierre el editor.",
        ""
      );

      while (Date.now() - startedAt < MAX_WAIT_MS) {
        await sleep(POLL_MS);
        var state;
        try {
          state = await getJobStatus(pollToken, runId);
        } catch (_transientError) {
          showStatus("El análisis continúa. Reintentando consulta... " + elapsedText(startedAt), "");
          continue;
        }

        if (state.status === "completed" && state.review_document) {
          showStatus("Versión de revisión preparada. Recargando editor...", "ok");
          plugin.test.solicitarRecarga(state.review_document, null);
          return;
        }
        if (state.status === "failed") {
          throw new Error(state.error_code || state.error_message || "El análisis falló en el backend.");
        }
        showStatus("Analizando documento completo... " + elapsedText(startedAt), "");
      }
      throw new Error("El análisis excedió 45 minutos.");
    } catch (error) {
      showStatus(String(error && error.message ? error.message : error), "error");
    } finally {
      setButtonBusy(false);
    }
  }

  window.addEventListener("message", function (event) {
    var data = event.data || {};
    if (data.type === AUTH_RESPONSE_TYPE && data.source === HOST_SOURCE && data.document_context) {
      documentContext = data.document_context;
    }
  });

  function replaceAnalyzeHandler() {
    var button = document.getElementById("btnAnalizar");
    if (!button || !button.parentNode) return;
    var replacement = button.cloneNode(true);
    button.parentNode.replaceChild(replacement, button);
    replacement.addEventListener("click", analyzeAsync);
  }

  var originalInit = window.Asc && window.Asc.plugin && window.Asc.plugin.init;
  if (typeof originalInit === "function") {
    window.Asc.plugin.init = function () {
      originalInit.apply(this, arguments);
      window.setTimeout(replaceAnalyzeHandler, 0);
    };
  }

  window.__EasyProBibliotecaAsync = {
    analyzeAsync: analyzeAsync,
    startJob: startJob,
    getJobStatus: getJobStatus,
    getDocumentContext: function () { return documentContext; }
  };
}());
