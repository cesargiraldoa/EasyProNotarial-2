(function () {
  "use strict";

  var AUTH_REQUEST_TYPE = "EASYPRO_ONLYOFFICE_AUTH_REQUEST";
  var AUTH_RESPONSE_TYPE = "EASYPRO_ONLYOFFICE_AUTH_RESPONSE";
  var PLUGIN_SOURCE = "motor-biblioteca";
  var HOST_SOURCE = "easypro-host";
  var AUTH_TIMEOUT_MS = 5000;
  var ANALYSIS_TIMEOUT_MS = 60000;
  var DEFAULT_API_BASE_URL = "https://easypronotarial-2-production.up.railway.app";
  var CATALOG_PATH = "/api/v1/biblioteca/campos";
  var ANALYZE_CURRENT_PATH = "/api/v1/biblioteca/analizar-actual";
  var DEFAULT_HOST_ORIGINS = [
    "https://easypronotarial.com",
    "http://localhost:5179",
    "http://127.0.0.1:5179"
  ];

  var camposCatalogo = [];
  var tokenEnMemoria = null;
  var documentContextEnMemoria = null;
  var sugerenciasActuales = [];
  var markerRegistry = {};
  var activeSuggestionId = null;
  var latestDiagnostics = {
    runtime: "plugin.js",
    suggestions: 0,
    marked: 0,
    stale: 0,
    failed: 0,
    capabilities: {
      search_supported: false,
      select_supported: false,
      highlight_supported: false,
      comment_supported: false
    }
  };
  var authPromise = null;
  var authTimer = null;
  var authResolve = null;
  var authReject = null;
  var listenersPreparados = false;
  var analisisEnCurso = false;

  function getPluginConfig() {
    var config = window.EASYPRO_ONLYOFFICE_PLUGIN_CONFIG;
    return config && typeof config === "object" ? config : {};
  }

  function normalizarOrigen(value) {
    if (typeof value !== "string" || !value.trim()) return null;
    try {
      return new URL(value.trim()).origin;
    } catch (error) {
      return null;
    }
  }

  function origenesHostPermitidos() {
    var config = getPluginConfig();
    var origenes = DEFAULT_HOST_ORIGINS.slice();
    if (Array.isArray(config.hostOrigins)) {
      config.hostOrigins.forEach(function (origin) {
        origenes.push(origin);
      });
    }
    return origenes
      .map(normalizarOrigen)
      .filter(function (origin, index, all) {
        return origin && all.indexOf(origin) === index;
      });
  }

  function obtenerApiBaseUrl() {
    var config = getPluginConfig();
    return (typeof config.apiBaseUrl === "string" && config.apiBaseUrl.trim()
      ? config.apiBaseUrl.trim()
      : DEFAULT_API_BASE_URL).replace(/\/$/, "");
  }

  function crearError(kind) {
    var error = new Error(kind);
    error.kind = kind;
    return error;
  }

  function validarDocumentContext(value) {
    if (!value || typeof value !== "object") return null;
    if (value.kind === "case_document") {
      var caseId = Number(value.case_id);
      var documentId = Number(value.document_id);
      var versionId = Number(value.version_id);
      if (Number.isFinite(caseId) && Number.isFinite(documentId) && Number.isFinite(versionId)) {
        return {
          kind: "case_document",
          case_id: caseId,
          document_id: documentId,
          version_id: versionId
        };
      }
    }
    if (value.kind === "minuta" && typeof value.editor_token === "string" && value.editor_token.trim()) {
      return {
        kind: "minuta",
        editor_token: value.editor_token.trim()
      };
    }
    return null;
  }

  function resolverAuth(token, documentContext) {
    tokenEnMemoria = token;
    documentContextEnMemoria = documentContext || null;
    if (authTimer) {
      window.clearTimeout(authTimer);
    }
    authTimer = null;
    var resolve = authResolve;
    authPromise = null;
    authResolve = null;
    authReject = null;
    if (resolve) {
      resolve(token);
    }
  }

  function rechazarAuth(kind) {
    if (authTimer) {
      window.clearTimeout(authTimer);
    }
    authTimer = null;
    var reject = authReject;
    authPromise = null;
    authResolve = null;
    authReject = null;
    if (reject) {
      reject(crearError(kind));
    }
  }

  function handleAuthMessage(event) {
    var allowedOrigins = origenesHostPermitidos();
    if (allowedOrigins.indexOf(event.origin) === -1) return;

    var data = event.data || {};
    if (data.type !== AUTH_RESPONSE_TYPE || data.source !== HOST_SOURCE) return;

    if (typeof data.token === "string" && data.token.trim()) {
      resolverAuth(data.token.trim(), validarDocumentContext(data.document_context));
      return;
    }

    if (data.error === "NO_SESSION") {
      rechazarAuth("no_session");
      return;
    }

    rechazarAuth("auth_failed");
  }

  function agregarTarget(targets, target) {
    if (!target) return;
    if (targets.indexOf(target) === -1) {
      targets.push(target);
    }
  }

  function obtenerTargetsDeSolicitud() {
    var targets = [];
    agregarTarget(targets, window.parent);
    agregarTarget(targets, window.top);
    try {
      var current = window;
      for (var index = 0; index < 5; index += 1) {
        if (!current.parent || current.parent === current) break;
        current = current.parent;
        agregarTarget(targets, current);
      }
    } catch (error) {
      // Cross-origin traversal is best-effort; direct parent/top remain enough for postMessage.
    }
    return targets;
  }

  function enviarSolicitudAuth() {
    var message = {
      type: AUTH_REQUEST_TYPE,
      source: PLUGIN_SOURCE
    };
    var origins = origenesHostPermitidos();
    var targets = obtenerTargetsDeSolicitud();

    targets.forEach(function (target) {
      origins.forEach(function (origin) {
        try {
          target.postMessage(message, origin);
        } catch (error) {
          // Ignore frames that cannot receive the request.
        }
      });
    });
  }

  function prepararListeners() {
    if (listenersPreparados) return;
    window.addEventListener("message", handleAuthMessage);
    listenersPreparados = true;
  }

  function solicitarToken() {
    prepararListeners();

    if (tokenEnMemoria) {
      return Promise.resolve(tokenEnMemoria);
    }

    if (authPromise) {
      return authPromise;
    }

    authPromise = new Promise(function (resolve, reject) {
      authResolve = resolve;
      authReject = reject;
      authTimer = window.setTimeout(function () {
        rechazarAuth("auth_timeout");
      }, Number(getPluginConfig().authTimeoutMs || AUTH_TIMEOUT_MS));
      enviarSolicitudAuth();
    });

    return authPromise;
  }

  function mostrarEstado(msg, tipo) {
    var estado = document.getElementById("estado");
    if (!estado) return;
    estado.textContent = msg;
    estado.className = tipo === "error" ? "error" : tipo === "ok" ? "ok" : "";
    estado.style.display = "block";
  }

  function setAnalisisEnCurso(value) {
    analisisEnCurso = value;
    var btn = document.getElementById("btnAnalizar");
    if (btn) {
      btn.disabled = value;
      btn.textContent = value ? "Analizando documento..." : "Analizar documento";
    }
  }

  function categoriaClass(categoria) {
    return "cat-" + (categoria || "otro");
  }

  function confianzaClass(confianza) {
    if (confianza > 0.95) return "conf-alta";
    if (confianza > 0.85) return "conf-media";
    return "conf-baja";
  }

  function safeSuggestionId(item, index) {
    if (item && typeof item.suggestion_id === "string" && item.suggestion_id.trim()) {
      return item.suggestion_id.trim();
    }
    if (item && typeof item.candidate_id === "string" && item.candidate_id.trim()) {
      return "sug_" + item.candidate_id.trim();
    }
    return "sug_" + index;
  }

  function normalizarSugerencia(item, index) {
    var location = item && item.location && typeof item.location === "object" ? item.location : {};
    return {
      suggestion_id: safeSuggestionId(item, index),
      candidate_id: item.candidate_id || "",
      original_text: item.original_text || item.texto_original || "",
      field_code: item.field_code || item.campo_sugerido || null,
      field_label: item.field_label || item.field_code || item.campo_sugerido || "Revisión humana",
      category: item.category || item.categoria || "otro",
      confidence: Number(item.confidence != null ? item.confidence : item.confianza || 0),
      source: item.source || item.metodo || "deterministic",
      context_before: item.context_before || "",
      context_after: item.context_after || "",
      location: {
        block_type: location.block_type || null,
        block_index: Number(location.block_index || 0),
        paragraph_index: location.paragraph_index == null ? null : Number(location.paragraph_index),
        table_index: location.table_index == null ? null : Number(location.table_index),
        row_index: location.row_index == null ? null : Number(location.row_index),
        cell_index: location.cell_index == null ? null : Number(location.cell_index),
        char_start: Number(location.char_start || 0),
        char_end: Number(location.char_end || 0),
        occurrence_index: Number(location.occurrence_index || item.occurrence_index || 1),
        location_key: location.location_key || "",
        block_hash: location.block_hash || ""
      }
    };
  }

  function prepararSugerencias(data) {
    return (Array.isArray(data) ? data : []).map(normalizarSugerencia);
  }

  function estadoMarca(suggestionId) {
    return markerRegistry[suggestionId] ? markerRegistry[suggestionId].status : "pending_mark";
  }

  function etiquetaEstadoMarca(status) {
    if (status === "marked") return "Marcado";
    if (status === "stale") return "Documento cambió";
    if (status === "mark_failed") return "No marcado";
    return "Pendiente";
  }

  function actualizarDiagnostico() {
    var total = sugerenciasActuales.length;
    var values = Object.keys(markerRegistry).map(function (key) { return markerRegistry[key]; });
    latestDiagnostics.suggestions = total;
    latestDiagnostics.marked = values.filter(function (item) { return item.status === "marked"; }).length;
    latestDiagnostics.stale = values.filter(function (item) { return item.status === "stale"; }).length;
    latestDiagnostics.failed = values.filter(function (item) { return item.status === "mark_failed"; }).length;

    var el = document.getElementById("diagnosticoMotor");
    if (!el) return;
    if (!getPluginConfig().diagnostics) {
      el.style.display = "none";
      return;
    }
    el.style.display = "block";
    el.textContent = "Runtime: " + latestDiagnostics.runtime
      + " · sugerencias: " + latestDiagnostics.suggestions
      + " · marcadas: " + latestDiagnostics.marked
      + " · stale: " + latestDiagnostics.stale
      + " · fallidas: " + latestDiagnostics.failed
      + " · search: " + String(latestDiagnostics.capabilities.search_supported)
      + " · select: " + String(latestDiagnostics.capabilities.select_supported)
      + " · highlight: " + String(latestDiagnostics.capabilities.highlight_supported)
      + " · comment: " + String(latestDiagnostics.capabilities.comment_supported);
  }

  function registrarEstadoMarca(suggestion, status, markerId, reason, canNavigate) {
    markerRegistry[suggestion.suggestion_id] = {
      suggestion_id: suggestion.suggestion_id,
      candidate_id: suggestion.candidate_id,
      field_code: suggestion.field_code,
      original_text: suggestion.original_text,
      location_key: suggestion.location.location_key,
      block_hash: suggestion.location.block_hash,
      marker_id: markerId || ("marker_" + suggestion.suggestion_id),
      status: status,
      reason: reason || "",
      can_navigate: Boolean(canNavigate) || status === "marked"
    };
  }

  function resaltarTarjetaActiva(suggestionId) {
    activeSuggestionId = suggestionId;
    renderSugerencias(sugerenciasActuales);
  }

  function renderSugerencias(data) {
    var sugerencias = prepararSugerencias(data);
    var wrapper = document.getElementById("sugerencias");
    var contador = document.getElementById("contador");
    var lista = document.getElementById("listaSugerencias");

    if (!wrapper || !contador || !lista) return;

    wrapper.style.display = "block";
    contador.textContent = String(sugerencias.length);
    lista.innerHTML = "";

    sugerencias.forEach(function (item) {
      var status = estadoMarca(item.suggestion_id);
      var card = document.createElement("div");
      card.className = "sugerencia-card" + (activeSuggestionId === item.suggestion_id ? " activa" : "");
      card.dataset.suggestionId = item.suggestion_id;
      card.dataset.texto = item.original_text;
      card.dataset.campo = item.field_code || "";
      card.dataset.categoria = item.category;
      card.dataset.candidateId = item.candidate_id || "";
      card.onclick = function () {
        navegarAMarca(item.suggestion_id);
      };

      var texto = document.createElement("div");
      texto.className = "texto-original";
      texto.textContent = item.original_text;

      var campo = document.createElement("div");
      campo.className = "campo-sugerido";
      campo.textContent = item.field_label;

      var badges = document.createElement("div");
      badges.className = "badges";

      var categoria = document.createElement("span");
      categoria.className = "badge " + categoriaClass(item.category);
      categoria.textContent = item.category;

      var confianza = document.createElement("span");
      confianza.className = "badge " + confianzaClass(item.confidence);
      confianza.textContent = Math.round(item.confidence * 100) + "%";

      var origen = document.createElement("span");
      origen.className = "badge";
      origen.textContent = item.source === "ai" ? "IA" : item.source === "hybrid" ? "Híbrido" : "Determinístico";

      var estado = document.createElement("span");
      estado.className = "badge estado-" + status;
      estado.textContent = etiquetaEstadoMarca(status);

      badges.appendChild(categoria);
      badges.appendChild(confianza);
      badges.appendChild(origen);
      badges.appendChild(estado);

      var notice = document.createElement("div");
      notice.className = "empty-state";
      notice.textContent = markerRegistry[item.suggestion_id] && markerRegistry[item.suggestion_id].reason === "safe_highlight_unavailable"
        ? "La versión actual de OnlyOffice no permite aplicar una marca temporal segura."
        : "Disponible en el siguiente bloque.";

      var actions = document.createElement("div");
      actions.className = "actions";

      var go = document.createElement("button");
      go.className = "btn";
      go.textContent = "Ir al texto";
      go.disabled = !markerRegistry[item.suggestion_id] || !markerRegistry[item.suggestion_id].can_navigate;
      go.onclick = function (event) {
        event.stopPropagation();
        navegarAMarca(item.suggestion_id);
      };

      var yes = document.createElement("button");
      yes.className = "btn btn-yes";
      yes.textContent = "Sí";
      yes.disabled = true;
      yes.title = "Disponible en el siguiente bloque.";

      var no = document.createElement("button");
      no.className = "btn btn-no";
      no.textContent = "No";
      no.disabled = true;
      no.title = "Disponible en el siguiente bloque.";

      actions.appendChild(go);
      actions.appendChild(yes);
      actions.appendChild(no);
      card.appendChild(texto);
      card.appendChild(campo);
      card.appendChild(badges);
      card.appendChild(notice);
      card.appendChild(actions);
      lista.appendChild(card);
    });
    actualizarDiagnostico();
  }

  function renderCatalogo(campos) {
    var lista = document.getElementById("listaCampos");
    if (!lista) return;
    lista.innerHTML = "";

    if (!campos.length) {
      var empty = document.createElement("div");
      empty.className = "empty-state";
      empty.textContent = "El catálogo de campos está vacío.";
      lista.appendChild(empty);
      return;
    }

    campos.forEach(function (campo) {
      var item = document.createElement("div");
      item.className = "campo-item";
      item.onclick = function () {
        insertarCampo(campo.code, campo.label);
      };

      var code = document.createElement("div");
      code.className = "campo-code";
      code.textContent = campo.code;

      var label = document.createElement("div");
      label.className = "campo-label";
      label.textContent = campo.label;

      item.appendChild(code);
      item.appendChild(label);
      lista.appendChild(item);
    });
  }

  function filtrarCatalogo() {
    var buscar = document.getElementById("buscarCampo");
    var q = buscar ? buscar.value.trim().toLowerCase() : "";
    if (!q) {
      renderCatalogo(camposCatalogo);
      return;
    }
    renderCatalogo(camposCatalogo.filter(function (campo) {
      return String(campo.code || "").toLowerCase().includes(q)
        || String(campo.label || "").toLowerCase().includes(q);
    }));
  }

  function normalizarCatalogo(payload) {
    if (!Array.isArray(payload)) {
      throw crearError("invalid_json");
    }
    return payload
      .filter(function (campo) {
        return campo && typeof campo.code === "string" && campo.code.trim();
      })
      .map(function (campo) {
        return {
          code: campo.code.trim(),
          label: typeof campo.label === "string" && campo.label.trim() ? campo.label.trim() : campo.code.trim(),
          category: campo.category || "otro"
        };
      });
  }

  async function cargarCatalogoConToken(token, fetchImpl) {
    var fetcher = fetchImpl || window.fetch.bind(window);
    var response;
    try {
      response = await fetcher(obtenerApiBaseUrl() + CATALOG_PATH, {
        method: "GET",
        headers: {
          Authorization: "Bearer " + token,
          Accept: "application/json"
        },
        credentials: "omit",
        cache: "no-store"
      });
    } catch (error) {
      throw crearError("network_error");
    }

    if (response.status === 401) {
      throw crearError("unauthorized");
    }

    if (response.status === 403) {
      throw crearError("forbidden");
    }

    if (!response.ok) {
      throw crearError("backend_unavailable");
    }

    try {
      return normalizarCatalogo(await response.json());
    } catch (error) {
      if (error && error.kind) throw error;
      throw crearError("invalid_json");
    }
  }

  function normalizarAnalisis(payload) {
    if (!payload || typeof payload !== "object" || !Array.isArray(payload.suggestions)) {
      throw crearError("invalid_json");
    }
    return payload.suggestions;
  }

  async function analizarActualConToken(token, documentContext, fetchImpl) {
    if (typeof token !== "string" || !token.trim()) {
      throw crearError("no_session");
    }
    var safeContext = validarDocumentContext(documentContext);
    if (!safeContext) {
      throw crearError("missing_document_context");
    }
    var fetcher = fetchImpl || window.fetch.bind(window);
    var timeoutId = null;
    var response;
    try {
      response = await Promise.race([
        fetcher(obtenerApiBaseUrl() + ANALYZE_CURRENT_PATH, {
          method: "POST",
          headers: {
            Authorization: "Bearer " + token.trim(),
            Accept: "application/json",
            "Content-Type": "application/json"
          },
          credentials: "omit",
          cache: "no-store",
          body: JSON.stringify(safeContext)
        }),
        new Promise(function (_resolve, reject) {
          timeoutId = window.setTimeout(function () {
            reject(crearError("analysis_timeout"));
          }, Number(getPluginConfig().analysisTimeoutMs || ANALYSIS_TIMEOUT_MS));
        })
      ]);
    } catch (error) {
      if (error && error.kind === "analysis_timeout") throw error;
      throw crearError("network_error");
    } finally {
      if (timeoutId) {
        window.clearTimeout(timeoutId);
      }
    }

    if (response.status === 401) {
      throw crearError("unauthorized");
    }
    if (response.status === 403) {
      throw crearError("forbidden");
    }
    if (response.status === 404) {
      throw crearError("document_not_found");
    }
    if (!response.ok) {
      throw crearError("backend_unavailable");
    }

    try {
      return normalizarAnalisis(await response.json());
    } catch (error) {
      if (error && error.kind) throw error;
      throw crearError("invalid_json");
    }
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
      window.Asc.scope[scopeKey] = JSON.stringify(payload);
      try {
        window.Asc.plugin.callCommand(command, false, true, function (returnValue) {
          resolve(parseCommandResult(returnValue));
        });
      } catch (error) {
        resolve({ ok: false, error: "callCommand_exception" });
      }
    });
  }

  function onlyOfficeMarkCommand() {
    function parsePayload() {
      try {
        return JSON.parse(Asc.scope.easyproMarkPayload || "[]");
      } catch (error) {
        return [];
      }
    }
    function normalize(value) {
      return String(value || "").replace(/\s+/g, " ").trim();
    }
    function getRangeText(range) {
      if (range && typeof range.GetText === "function") {
        return range.GetText();
      }
      if (range && typeof range.text === "string") {
        return range.text;
      }
      return null;
    }
    function rangeMatchesSuggestion(range, suggestion) {
      var text = getRangeText(range);
      if (text !== null && text !== suggestion.original_text) {
        return false;
      }
      if (range && range.location_key && suggestion.location && suggestion.location.location_key) {
        return range.location_key === suggestion.location.location_key;
      }
      if (range && range.block_hash && suggestion.location && suggestion.location.block_hash) {
        if (range.block_hash !== suggestion.location.block_hash) return false;
      }
      if (range && typeof range.context_before === "string" && suggestion.context_before) {
        if (normalize(range.context_before).slice(-40) !== normalize(suggestion.context_before).slice(-40)) return false;
      }
      if (range && typeof range.context_after === "string" && suggestion.context_after) {
        if (normalize(range.context_after).slice(0, 40) !== normalize(suggestion.context_after).slice(0, 40)) return false;
      }
      if (range && suggestion.location) {
        if (typeof range.char_start === "number" && range.char_start !== suggestion.location.char_start) return false;
        if (typeof range.char_end === "number" && range.char_end !== suggestion.location.char_end) return false;
      }
      return true;
    }
    function hasStrongEvidence(range, suggestion) {
      if (!range || !suggestion || !suggestion.location) return false;
      if (range.location_key && suggestion.location.location_key && range.location_key === suggestion.location.location_key) {
        return true;
      }
      if (range.block_hash && suggestion.location.block_hash && range.block_hash === suggestion.location.block_hash) {
        return true;
      }
      if (typeof range.char_start === "number" && typeof range.char_end === "number") {
        return range.char_start === suggestion.location.char_start && range.char_end === suggestion.location.char_end;
      }
      if (typeof range.context_before === "string" && typeof range.context_after === "string" && suggestion.context_before && suggestion.context_after) {
        return normalize(range.context_before).slice(-40) === normalize(suggestion.context_before).slice(-40)
          && normalize(range.context_after).slice(0, 40) === normalize(suggestion.context_after).slice(0, 40);
      }
      return false;
    }
    function chooseRange(ranges, suggestion) {
      var verified = [];
      for (var i = 0; i < ranges.length; i += 1) {
        if (rangeMatchesSuggestion(ranges[i], suggestion)) verified.push(ranges[i]);
      }
      if (verified.length === 1 && (ranges.length === 1 || hasStrongEvidence(verified[0], suggestion))) return verified[0];
      if (ranges.length === 1 && rangeMatchesSuggestion(ranges[0], suggestion)) return ranges[0];
      var occurrence = suggestion.location && suggestion.location.occurrence_index ? Number(suggestion.location.occurrence_index) : 1;
      if (verified.length >= occurrence && hasStrongEvidence(verified[occurrence - 1], suggestion)) return verified[occurrence - 1];
      return null;
    }
    function applyYellow(range) {
      if (range && typeof range.SetHighlight === "function") {
        range.SetHighlight(255, 242, 102);
        return "SetHighlight";
      }
      return null;
    }
    function capabilityProbe(doc, sampleRange) {
      return {
        search_supported: !!(doc && typeof doc.Search === "function"),
        select_supported: !!(sampleRange && typeof sampleRange.Select === "function"),
        highlight_supported: !!(sampleRange && typeof sampleRange.SetHighlight === "function"),
        comment_supported: !!(sampleRange && typeof sampleRange.AddComment === "function")
      };
    }
    var suggestions = parsePayload();
    var results = [];
    var runtime = "unknown";
    var capabilities = {
      search_supported: false,
      select_supported: false,
      highlight_supported: false,
      comment_supported: false
    };
    try {
      var doc = Api.GetDocument();
      runtime = "Api.GetDocument";
      for (var s = 0; s < suggestions.length; s += 1) {
        var suggestion = suggestions[s];
        var ranges = doc.Search(suggestion.original_text, false) || [];
        var target = chooseRange(ranges, suggestion);
        capabilities = capabilityProbe(doc, target || ranges[0]);
        if (!target) {
          results.push({ suggestion_id: suggestion.suggestion_id, status: "stale", reason: "location_not_verified" });
          continue;
        }
        var method = applyYellow(target);
        if (!method) {
          results.push({
            suggestion_id: suggestion.suggestion_id,
            status: "mark_failed",
            marker_id: "oo_" + suggestion.suggestion_id,
            reason: "safe_highlight_unavailable",
            can_navigate: typeof target.Select === "function"
          });
          continue;
        }
        results.push({
          suggestion_id: suggestion.suggestion_id,
          status: "marked",
          marker_id: "oo_" + suggestion.suggestion_id,
          method: method,
          can_navigate: typeof target.Select === "function"
        });
      }
      return JSON.stringify({ ok: true, runtime: runtime, capabilities: capabilities, results: results });
    } catch (error) {
      return JSON.stringify({ ok: false, runtime: runtime, capabilities: capabilities, error: "onlyoffice_command_failed", results: results });
    }
  }

  function onlyOfficeClearCommand() {
    function parsePayload() {
      try {
        return JSON.parse(Asc.scope.easyproClearPayload || "[]");
      } catch (error) {
        return [];
      }
    }
    function clearRange(range) {
      if (range && typeof range.SetHighlight === "function") {
        range.SetHighlight(null);
        return true;
      }
      return false;
    }
    var markers = parsePayload();
    try {
      var doc = Api.GetDocument();
      markers.forEach(function (marker) {
        var ranges = doc.Search(marker.original_text, false) || [];
        ranges.forEach(function (range) {
          if (range.location_key && marker.location_key && range.location_key !== marker.location_key) return;
          clearRange(range);
        });
      });
      return JSON.stringify({ ok: true });
    } catch (error) {
      return JSON.stringify({ ok: false, error: "clear_failed" });
    }
  }

  function onlyOfficeNavigateCommand() {
    function parsePayload() {
      try {
        return JSON.parse(Asc.scope.easyproNavigatePayload || "{}");
      } catch (error) {
        return {};
      }
    }
    var marker = parsePayload();
    try {
      var doc = Api.GetDocument();
      var ranges = doc.Search(marker.original_text, false) || [];
      var target = null;
      for (var i = 0; i < ranges.length; i += 1) {
        if (!ranges[i].location_key || !marker.location_key || ranges[i].location_key === marker.location_key) {
          target = ranges[i];
          break;
        }
      }
      if (!target) return JSON.stringify({ ok: false, error: "marker_not_found" });
      if (typeof target.Select === "function") {
        target.Select();
        return JSON.stringify({ ok: true, method: "Select" });
      }
      return JSON.stringify({ ok: false, error: "navigation_unavailable" });
    } catch (error) {
      return JSON.stringify({ ok: false, error: "navigation_failed" });
    }
  }

  async function limpiarMarcasTemporales() {
    var markers = Object.keys(markerRegistry).map(function (key) { return markerRegistry[key]; })
      .filter(function (marker) { return marker.status === "marked"; });
    if (markers.length) {
      await callOnlyOfficeCommand("easyproClearPayload", markers, onlyOfficeClearCommand);
    }
    markerRegistry = {};
    activeSuggestionId = null;
    actualizarDiagnostico();
  }

  async function marcarSugerenciasEnDocumento(sugerencias) {
    if (!sugerencias.length) {
      actualizarDiagnostico();
      return;
    }
    sugerencias.forEach(function (suggestion) {
      registrarEstadoMarca(suggestion, "pending_mark");
    });
    var result = await callOnlyOfficeCommand("easyproMarkPayload", sugerencias, onlyOfficeMarkCommand);
    if (result && result.runtime) {
      latestDiagnostics.runtime = result.runtime;
    }
    if (result && result.capabilities) {
      latestDiagnostics.capabilities = {
        search_supported: Boolean(result.capabilities.search_supported),
        select_supported: Boolean(result.capabilities.select_supported),
        highlight_supported: Boolean(result.capabilities.highlight_supported),
        comment_supported: Boolean(result.capabilities.comment_supported)
      };
    }
    var byId = {};
    (result && Array.isArray(result.results) ? result.results : []).forEach(function (item) {
      byId[item.suggestion_id] = item;
    });
    sugerencias.forEach(function (suggestion) {
      var item = byId[suggestion.suggestion_id];
      if (!result || result.ok === false) {
        registrarEstadoMarca(suggestion, "mark_failed", null, result && result.error);
      } else if (!item) {
        registrarEstadoMarca(suggestion, "mark_failed", null, "missing_result");
      } else {
        registrarEstadoMarca(suggestion, item.status, item.marker_id, item.reason, item.can_navigate);
      }
    });
    actualizarDiagnostico();
  }

  async function navegarAMarca(suggestionId) {
    var marker = markerRegistry[suggestionId];
    if (!marker || !marker.can_navigate) return;
    var result = await callOnlyOfficeCommand("easyproNavigatePayload", marker, onlyOfficeNavigateCommand);
    if (result && result.ok) {
      resaltarTarjetaActiva(suggestionId);
      return;
    }
    marker.status = "mark_failed";
    renderSugerencias(sugerenciasActuales);
  }

  function mensajeError(error) {
    var kind = error && error.kind;
    if (kind === "no_session") {
      return "No hay una sesión activa. Cierre el editor y vuelva a abrirlo desde Ecosistema Notarial.";
    }
    if (kind === "missing_document_context" || kind === "document_not_found") {
      return "No fue posible identificar el documento abierto desde Ecosistema Notarial.";
    }
    if (kind === "auth_timeout" || kind === "auth_failed" || kind === "analysis_timeout" || kind === "network_error" || kind === "backend_unavailable" || kind === "invalid_json") {
      return "No fue posible conectar el Motor de Biblioteca con Ecosistema Notarial.";
    }
    if (kind === "unauthorized") {
      return "La sesión venció. Vuelva a abrir el documento desde Ecosistema Notarial.";
    }
    if (kind === "forbidden") {
      return "No fue posible conectar el Motor de Biblioteca con Ecosistema Notarial.";
    }
    return "No fue posible conectar el Motor de Biblioteca con Ecosistema Notarial.";
  }

  async function cargarCatalogo() {
    try {
      mostrarEstado("Conectando con Ecosistema Notarial...", "");
      var token = await solicitarToken();
      camposCatalogo = await cargarCatalogoConToken(token);
      renderCatalogo(camposCatalogo);
      if (camposCatalogo.length) {
        mostrarEstado("Catálogo cargado.", "ok");
      } else {
        mostrarEstado("El catálogo de campos está vacío.", "");
      }
    } catch (error) {
      renderCatalogo([]);
      mostrarEstado(mensajeError(error), "error");
    }
  }

  function insertarCampo(codigoCampo) {
    if (!codigoCampo) return;
    window.Asc.plugin.executeMethod("PasteText", ["{{" + codigoCampo + "}}"], function () {});
  }

  function aceptarSugerencia() {
    mostrarEstado("Las acciones Sí/No se habilitarán en el siguiente bloque.", "");
  }

  async function analizarDocumento() {
    if (analisisEnCurso) return;
    setAnalisisEnCurso(true);
    await limpiarMarcasTemporales();
    sugerenciasActuales = [];
    renderSugerencias(sugerenciasActuales);
    mostrarEstado("Analizando documento...", "");
    try {
      var token = await solicitarToken();
      var sugerencias = await analizarActualConToken(token, documentContextEnMemoria);
      sugerenciasActuales = prepararSugerencias(sugerencias);
      renderSugerencias(sugerenciasActuales);
      await marcarSugerenciasEnDocumento(sugerenciasActuales);
      renderSugerencias(sugerenciasActuales);
      mostrarEstado(
        sugerenciasActuales.length ? "Sugerencias cargadas y marcadas en el documento." : "No se encontraron candidatos en el documento.",
        sugerenciasActuales.length ? "ok" : ""
      );
    } catch (error) {
      mostrarEstado(mensajeError(error), "error");
    } finally {
      setAnalisisEnCurso(false);
    }
  }

  function prepararDom() {
    var buscar = document.getElementById("buscarCampo");
    if (buscar) {
      buscar.addEventListener("input", filtrarCatalogo);
    }

    var btnAnalizar = document.getElementById("btnAnalizar");
    if (btnAnalizar) {
      btnAnalizar.addEventListener("click", analizarDocumento);
    }
  }

  window.Asc = window.Asc || {};
  window.Asc.plugin = window.Asc.plugin || {};

  window.Asc.plugin.init = function () {
    prepararListeners();
    prepararDom();
    cargarCatalogo();
  };

  window.Asc.plugin.button = function () {};
  window.Asc.plugin.onExternalMouseUp = function () {};

  window.cargarCatalogo = cargarCatalogo;
  window.renderSugerencias = renderSugerencias;
  window.aceptarSugerencia = aceptarSugerencia;
  window.insertarCampo = insertarCampo;
  window.analizarDocumento = analizarDocumento;

  window.__EasyProBibliotecaPlugin = {
    constants: {
      AUTH_REQUEST_TYPE: AUTH_REQUEST_TYPE,
      AUTH_RESPONSE_TYPE: AUTH_RESPONSE_TYPE,
      PLUGIN_SOURCE: PLUGIN_SOURCE,
      HOST_SOURCE: HOST_SOURCE,
      CATALOG_PATH: CATALOG_PATH,
      ANALYZE_CURRENT_PATH: ANALYZE_CURRENT_PATH
    },
    test: {
      handleAuthMessage: handleAuthMessage,
      solicitarToken: solicitarToken,
      cargarCatalogoConToken: cargarCatalogoConToken,
      analizarActualConToken: analizarActualConToken,
      normalizarCatalogo: normalizarCatalogo,
      normalizarAnalisis: normalizarAnalisis,
      validarDocumentContext: validarDocumentContext,
      mensajeError: mensajeError,
      renderSugerencias: renderSugerencias,
      analizarDocumento: analizarDocumento,
      prepararSugerencias: prepararSugerencias,
      marcarSugerenciasEnDocumento: marcarSugerenciasEnDocumento,
      limpiarMarcasTemporales: limpiarMarcasTemporales,
      navegarAMarca: navegarAMarca,
      getMarkerRegistry: function () {
        return markerRegistry;
      },
      getDiagnostics: function () {
        return latestDiagnostics;
      },
      reset: function () {
        tokenEnMemoria = null;
        documentContextEnMemoria = null;
        sugerenciasActuales = [];
        markerRegistry = {};
        activeSuggestionId = null;
        latestDiagnostics = {
          runtime: "plugin.js",
          suggestions: 0,
          marked: 0,
          stale: 0,
          failed: 0,
          capabilities: {
            search_supported: false,
            select_supported: false,
            highlight_supported: false,
            comment_supported: false
          }
        };
        authPromise = null;
        authResolve = null;
        authReject = null;
        analisisEnCurso = false;
        if (authTimer) {
          window.clearTimeout(authTimer);
        }
        authTimer = null;
      }
    }
  };
}());
