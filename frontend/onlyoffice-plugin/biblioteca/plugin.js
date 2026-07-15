(function () {
  "use strict";

  var AUTH_REQUEST_TYPE = "EASYPRO_ONLYOFFICE_AUTH_REQUEST";
  var AUTH_RESPONSE_TYPE = "EASYPRO_ONLYOFFICE_AUTH_RESPONSE";
  var RELOAD_REQUEST_TYPE = "EASYPRO_ONLYOFFICE_RELOAD_REQUEST";
  var PLUGIN_SOURCE = "motor-biblioteca";
  var HOST_SOURCE = "easypro-host";
  var AUTH_TIMEOUT_MS = 5000;
  var ANALYSIS_TIMEOUT_MS = 60000;
  var DEFAULT_API_BASE_URL = "https://easypronotarial-2-production.up.railway.app";
  var CATALOG_PATH = "/api/v1/biblioteca/campos";
  var ANALYZE_AND_PREPARE_PATH = "/api/v1/biblioteca/analizar-y-preparar";
  var DECISION_PATH = "/api/v1/biblioteca/decidir";
  var CASCADE_BACKEND_PATH = "/api/v1/biblioteca/actualizar-campo";
  var SUGGESTION_TAG_PREFIX = "easypro:suggestion:v2:";
  var FIELD_TAG_PREFIX = "easypro:field:v2:";
  var PROVISIONAL_FIELD_PREFIX = "PENDING_FIELD_";
  var DEFAULT_HOST_ORIGINS = [
    "https://easypronotarial.com",
    "http://localhost:5179",
    "http://127.0.0.1:5179"
  ];

  var camposCatalogo = [];
  var tokenEnMemoria = null;
  var documentContextEnMemoria = null;
  var suggestionControls = {};
  var fieldControls = {};
  var gruposActuales = [];
  var fieldsActuales = [];
  var activeControlId = null;
  var authPromise = null;
  var authTimer = null;
  var authResolve = null;
  var authReject = null;
  var listenersPreparados = false;
  var botonesInlinePreparados = false;
  var cambioOccurrence = null;
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
    var origins = DEFAULT_HOST_ORIGINS.slice();
    if (Array.isArray(config.hostOrigins)) {
      config.hostOrigins.forEach(function (origin) { origins.push(origin); });
    }
    return origins.map(normalizarOrigen).filter(function (origin, index, all) {
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
      return { kind: "minuta", editor_token: value.editor_token.trim() };
    }
    return null;
  }

  function resolverAuth(token, documentContext) {
    tokenEnMemoria = token;
    documentContextEnMemoria = documentContext || null;
    if (authTimer) window.clearTimeout(authTimer);
    authTimer = null;
    var resolve = authResolve;
    authPromise = null;
    authResolve = null;
    authReject = null;
    if (resolve) resolve(token);
  }

  function rechazarAuth(kind) {
    if (authTimer) window.clearTimeout(authTimer);
    authTimer = null;
    var reject = authReject;
    authPromise = null;
    authResolve = null;
    authReject = null;
    if (reject) reject(crearError(kind));
  }

  function handleAuthMessage(event) {
    var allowed = origenesHostPermitidos();
    if (allowed.indexOf(event.origin) === -1) return;
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
    if (target && targets.indexOf(target) === -1) targets.push(target);
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
      // Best effort only; no cross-origin properties are read beyond parent references.
    }
    return targets;
  }

  function enviarSolicitudAuth() {
    var message = { type: AUTH_REQUEST_TYPE, source: PLUGIN_SOURCE };
    var origins = origenesHostPermitidos();
    obtenerTargetsDeSolicitud().forEach(function (target) {
      origins.forEach(function (origin) {
        try {
          target.postMessage(message, origin);
        } catch (error) {
          // Ignore frames that cannot receive the request.
        }
      });
    });
  }

  function solicitarRecarga(reviewDocument, analysisId) {
    var context = validarDocumentContext(reviewDocument);
    if (!context || context.kind !== "case_document") return;
    var message = {
      type: RELOAD_REQUEST_TYPE,
      source: PLUGIN_SOURCE,
      analysis_id: analysisId || null,
      review_document: context
    };
    var origins = origenesHostPermitidos();
    obtenerTargetsDeSolicitud().forEach(function (target) {
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
    if (tokenEnMemoria) return Promise.resolve(tokenEnMemoria);
    if (authPromise) return authPromise;
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

  function decisionesInlineDisponibles() {
    if (botonesInlinePreparados) return true;
    mostrarEstado("OnlyOffice no expone botones inline de Content Controls. Abra el documento en una version compatible para revisar sugerencias.", "error");
    return false;
  }

  function setAnalisisEnCurso(value) {
    analisisEnCurso = value;
    var btn = document.getElementById("btnAnalizar");
    if (btn) {
      btn.disabled = value;
      btn.textContent = value ? "Preparando version de revision..." : "Analizar documento";
    }
  }

  function executeMethodAsync(name, args) {
    return new Promise(function (resolve) {
      if (!window.Asc || !window.Asc.plugin || typeof window.Asc.plugin.executeMethod !== "function") {
        resolve({ ok: false, error: "executeMethod_unavailable" });
        return;
      }
      try {
        window.Asc.plugin.executeMethod(name, args || [], function (result) {
          if (result === false || (result && typeof result === "object" && result.error)) {
            resolve({ ok: false, error: result && result.error ? String(result.error) : "method_failed", value: result });
            return;
          }
          resolve({ ok: true, value: result });
        });
      } catch (error) {
        resolve({ ok: false, error: "executeMethod_exception" });
      }
    });
  }

  function normalizeControls(value) {
    var controls = Array.isArray(value) ? value : [];
    return controls
      .map(function (control) {
        var tag = String(control.Tag || control.tag || "");
        var internalId = control.InternalId || control.InternalID || control.Id || control.id;
        if (!tag || !internalId) return null;
        return {
          internal_id: internalId,
          tag: tag,
          alias: control.Alias || control.alias || "",
          text: control.Text || control.text || ""
        };
      })
      .filter(Boolean);
  }

  function parseSuggestionTag(control) {
    if (!control.tag || control.tag.indexOf(SUGGESTION_TAG_PREFIX) !== 0) return null;
    var parts = control.tag.split(":");
    if (parts.length < 12) return null;
    return {
      type: "suggestion",
      internal_id: control.internal_id,
      tag: control.tag,
      alias: control.alias,
      text: control.text,
      analysis_id: parts[3],
      suggestion_id: parts[4],
      candidate_id: parts[5],
      field_instance_id: parts[6],
      field_code: parts[7],
      visible_code: parts[8],
      group_id: parts[9],
      occurrence_id: parts[10],
      catalog_status: parts[11] || "matched",
      requires_field_assignment: (parts[11] || "") !== "matched" || String(parts[7] || "").indexOf(PROVISIONAL_FIELD_PREFIX) === 0,
      status: "prepared"
    };
  }

  function parseFieldTag(control) {
    if (!control.tag || control.tag.indexOf(FIELD_TAG_PREFIX) !== 0) return null;
    var parts = control.tag.split(":");
    if (parts.length < 5) return null;
    return {
      type: "field",
      internal_id: control.internal_id,
      tag: control.tag,
      alias: control.alias,
      text: control.text,
      field_instance_id: parts[3],
      occurrence_id: parts[4],
      visible_code: parts[5] || parts[3],
      field_code: parts[6] || parts[5] || parts[3],
      status: "accepted"
    };
  }

  async function leerContentControls() {
    var response = await executeMethodAsync("GetAllContentControls", []);
    if (!response.ok) {
      suggestionControls = {};
      fieldControls = {};
      return { ok: false, error: response.error };
    }
    var controls = normalizeControls(response.value);
    suggestionControls = {};
    fieldControls = {};
    controls.forEach(function (control) {
      var suggestion = parseSuggestionTag(control);
      var field = parseFieldTag(control);
      if (suggestion) suggestionControls[suggestion.occurrence_id] = suggestion;
      if (field) {
        if (!fieldControls[field.field_instance_id]) fieldControls[field.field_instance_id] = [];
        fieldControls[field.field_instance_id].push(field);
      }
    });
    gruposActuales = agruparSugerencias(Object.keys(suggestionControls).map(function (key) { return suggestionControls[key]; }));
    fieldsActuales = agruparCampos(fieldControls);
    return { ok: true, controls: controls };
  }

  function agruparSugerencias(items) {
    var groups = {};
    items.forEach(function (item) {
      var groupId = item.group_id || item.field_instance_id;
      if (!groups[groupId]) {
        groups[groupId] = {
          group_id: groupId,
          field_instance_id: item.field_instance_id,
          field_code: item.field_code,
          visible_code: item.visible_code || item.field_code,
          catalog_status: item.catalog_status || "matched",
          requires_field_assignment: Boolean(item.requires_field_assignment),
          detected_value: item.text || "",
          occurrences: []
        };
      }
      groups[groupId].occurrences.push(item);
    });
    return Object.keys(groups).map(function (key) { return groups[key]; });
  }

  function agruparCampos(map) {
    return Object.keys(map).sort().map(function (fieldId) {
      return {
        field_instance_id: fieldId,
        controls: map[fieldId],
        value: map[fieldId][0] ? map[fieldId][0].text : ""
      };
    });
  }

  function renderCatalogo(campos) {
    var lista = document.getElementById("listaCampos");
    if (!lista) return;
    lista.innerHTML = "";
    if (!campos.length) {
      var empty = document.createElement("div");
      empty.className = "empty-state";
      empty.textContent = "No hay campos disponibles.";
      lista.appendChild(empty);
      return;
    }
    campos.forEach(function (campo) {
      var item = document.createElement("div");
      item.className = "campo-item";
      item.onclick = function () { insertarCampoEstructurado(campo.code); };
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
    renderCambioSelect(campos);
  }

  function renderCambioSelect(campos) {
    var select = document.getElementById("campoCambioSelect");
    if (!select) return;
    var filtro = document.getElementById("campoCambioBuscar");
    var q = filtro ? filtro.value.trim().toLowerCase() : "";
    select.innerHTML = "";
    (campos || []).filter(function (campo) {
      if (!q) return true;
      return String(campo.code || "").toLowerCase().indexOf(q) !== -1
        || String(campo.label || "").toLowerCase().indexOf(q) !== -1;
    }).forEach(function (campo) {
      var option = document.createElement("option");
      option.value = campo.code;
      option.textContent = campo.code + " - " + campo.label;
      select.appendChild(option);
    });
  }

  function filtrarCatalogo() {
    var buscar = document.getElementById("buscarCampo");
    var q = buscar ? buscar.value.trim().toLowerCase() : "";
    if (!q) {
      renderCatalogo(camposCatalogo);
      return;
    }
    var filtrados = camposCatalogo.filter(function (campo) {
      return String(campo.code || "").toLowerCase().indexOf(q) !== -1
        || String(campo.label || "").toLowerCase().indexOf(q) !== -1;
    });
    renderCatalogo(filtrados);
  }

  function normalizarCatalogo(payload) {
    if (!Array.isArray(payload)) throw crearError("invalid_json");
    return payload
      .filter(function (campo) { return campo && typeof campo.code === "string" && campo.code.trim(); })
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
        headers: { Authorization: "Bearer " + token, Accept: "application/json" },
        credentials: "omit",
        cache: "no-store"
      });
    } catch (error) {
      throw crearError("network_error");
    }
    if (response.status === 401) throw crearError("unauthorized");
    if (response.status === 403) throw crearError("forbidden");
    if (!response.ok) throw crearError("backend_unavailable");
    try {
      return normalizarCatalogo(await response.json());
    } catch (error) {
      if (error && error.kind) throw error;
      throw crearError("invalid_json");
    }
  }

  function normalizarPreparacion(payload) {
    if (!payload || typeof payload !== "object" || !payload.review_document) throw crearError("invalid_json");
    return {
      analysis_id: payload.analysis_id || "",
      review_document: payload.review_document,
      groups: Array.isArray(payload.groups) ? payload.groups : [],
      stats: payload.stats && typeof payload.stats === "object" ? payload.stats : {},
      diagnostics: payload.diagnostics && typeof payload.diagnostics === "object" ? payload.diagnostics : {},
      timing: payload.timing && typeof payload.timing === "object" ? payload.timing : {}
    };
  }

  async function analizarYPrepararConToken(token, documentContext, fetchImpl) {
    if (typeof token !== "string" || !token.trim()) throw crearError("no_session");
    var safeContext = validarDocumentContext(documentContext);
    if (!safeContext) throw crearError("missing_document_context");
    var fetcher = fetchImpl || window.fetch.bind(window);
    var timeoutId = null;
    var response;
    try {
      response = await Promise.race([
        fetcher(obtenerApiBaseUrl() + ANALYZE_AND_PREPARE_PATH, {
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
          timeoutId = window.setTimeout(function () { reject(crearError("analysis_timeout")); }, Number(getPluginConfig().analysisTimeoutMs || ANALYSIS_TIMEOUT_MS));
        })
      ]);
    } catch (error) {
      if (error && error.kind === "analysis_timeout") throw error;
      throw crearError("network_error");
    } finally {
      if (timeoutId) window.clearTimeout(timeoutId);
    }
    if (response.status === 401) throw crearError("unauthorized");
    if (response.status === 403) throw crearError("forbidden");
    if (response.status === 404) throw crearError("document_not_found");
    if (!response.ok) throw crearError("backend_unavailable");
    try {
      return normalizarPreparacion(await response.json());
    } catch (error) {
      if (error && error.kind) throw error;
      throw crearError("invalid_json");
    }
  }

  async function actualizarCampoBackend(token, documentContext, fieldInstanceId, value, fetchImpl) {
    var fetcher = fetchImpl || window.fetch.bind(window);
    var response = await fetcher(obtenerApiBaseUrl() + CASCADE_BACKEND_PATH, {
      method: "POST",
      headers: {
        Authorization: "Bearer " + token,
        Accept: "application/json",
        "Content-Type": "application/json"
      },
      credentials: "omit",
      cache: "no-store",
      body: JSON.stringify({
        document_context: validarDocumentContext(documentContext),
        field_instance_id: fieldInstanceId,
        value: value
      })
    });
    if (!response.ok) throw crearError("backend_unavailable");
    return response.json();
  }

  async function decidirSugerenciaBackend(token, documentContext, occurrence, action, overrides, fetchImpl) {
    var safeContext = validarDocumentContext(documentContext);
    if (!safeContext || safeContext.kind !== "case_document") throw crearError("missing_document_context");
    var fetcher = fetchImpl || window.fetch.bind(window);
    var payload = {
      document_context: safeContext,
      action: action,
      occurrence_id: occurrence.occurrence_id,
      suggestion_tag: occurrence.tag,
      field_instance_id: occurrence.field_instance_id,
      field_code: occurrence.field_code,
      visible_code: occurrence.visible_code || occurrence.field_code
    };
    if (overrides && typeof overrides === "object") {
      Object.keys(overrides).forEach(function (key) {
        payload[key] = overrides[key];
      });
    }
    var response = await fetcher(obtenerApiBaseUrl() + DECISION_PATH, {
      method: "POST",
      headers: {
        Authorization: "Bearer " + token,
        Accept: "application/json",
        "Content-Type": "application/json"
      },
      credentials: "omit",
      cache: "no-store",
      body: JSON.stringify(payload)
    });
    if (response.status === 409) throw crearError("stale_suggestion");
    if (response.status === 422) throw crearError("field_assignment_required");
    if (!response.ok) throw crearError("backend_unavailable");
    return response.json();
  }

  function esProvisional(occurrence) {
    if (!occurrence) return true;
    return Boolean(occurrence.requires_field_assignment)
      || String(occurrence.field_code || "").indexOf(PROVISIONAL_FIELD_PREFIX) === 0
      || String(occurrence.catalog_status || "matched") !== "matched";
  }

  function mensajeError(error) {
    var kind = error && error.kind;
    if (kind === "no_session") return "No hay una sesion activa. Cierre el editor y vuelva a abrirlo desde Ecosistema Notarial.";
    if (kind === "missing_document_context" || kind === "document_not_found") return "No fue posible identificar el documento abierto desde Ecosistema Notarial.";
    if (kind === "unauthorized") return "La sesion vencio. Vuelva a abrir el documento desde Ecosistema Notarial.";
    if (kind === "analysis_timeout") return "No fue posible obtener el analisis del documento.";
    return "No fue posible conectar el Motor de Biblioteca con Ecosistema Notarial.";
  }

  function categoriaClass(categoria) {
    return "cat-" + (categoria || "otro");
  }

  function renderSugerencias(groups) {
    var contenedor = document.getElementById("sugerencias");
    var lista = document.getElementById("listaSugerencias");
    var contador = document.getElementById("contador");
    if (!contenedor || !lista || !contador) return;
    var total = (groups || []).reduce(function (sum, group) { return sum + group.occurrences.length; }, 0);
    contenedor.style.display = "block";
    contador.textContent = String((groups || []).length);
    lista.innerHTML = "";
    if (!(groups || []).length && !fieldsActuales.length) {
      var empty = document.createElement("div");
      empty.className = "empty-state";
      empty.textContent = "No hay sugerencias ni campos estructurados en esta version.";
      lista.appendChild(empty);
      return;
    }
    (groups || []).forEach(function (group) {
      var card = document.createElement("div");
      card.className = "sugerencia-card";
      card.dataset.groupId = group.group_id;
      var title = document.createElement("div");
      title.className = "texto-original";
      title.textContent = group.detected_value || "Sugerencia";
      var field = document.createElement("div");
      field.className = "campo-sugerido";
      field.textContent = (group.visible_code || group.field_code || group.field_instance_id) + " · " + group.occurrences.length + " aparicion(es)";
      var badges = document.createElement("div");
      badges.className = "badges";
      var badge = document.createElement("span");
      badge.className = "badge " + categoriaClass(group.category);
      badge.textContent = group.requires_field_assignment ? "provisional" : "revision";
      badges.appendChild(badge);
      var actions = document.createElement("div");
      actions.className = "actions";
      var go = document.createElement("button");
      go.className = "btn";
      go.textContent = "Ir al texto";
      go.disabled = !group.occurrences.length;
      go.onclick = function (event) {
        event.stopPropagation();
        navegarAControl(group.occurrences[0]);
      };
      var yes = document.createElement("button");
      yes.className = "btn btn-yes";
      yes.textContent = "Si";
      yes.onclick = function (event) {
        event.stopPropagation();
        aceptarGrupo(group);
      };
      var no = document.createElement("button");
      no.className = "btn btn-no";
      no.textContent = "No";
      no.onclick = function (event) {
        event.stopPropagation();
        rechazarGrupo(group);
      };
      var change = document.createElement("button");
      change.className = "btn";
      change.textContent = "Cambiar";
      change.onclick = function (event) {
        event.stopPropagation();
        cambiarOcurrencia(group.occurrences[0]);
      };
      actions.appendChild(go);
      actions.appendChild(yes);
      actions.appendChild(no);
      actions.appendChild(change);
      card.appendChild(title);
      card.appendChild(field);
      card.appendChild(badges);
      card.appendChild(actions);
      lista.appendChild(card);
    });
    renderCamposEstructurados(lista);
    var diagnostico = document.getElementById("diagnosticoMotor");
    if (diagnostico) {
      diagnostico.style.display = "block";
      diagnostico.textContent = "Grupos: " + String((groups || []).length) + " · apariciones pendientes: " + String(total);
    }
  }

  function renderCamposEstructurados(lista) {
    if (!fieldsActuales.length) return;
    var section = document.createElement("div");
    section.className = "empty-state";
    section.textContent = "Campos estructurados";
    lista.appendChild(section);
    fieldsActuales.forEach(function (field) {
      var card = document.createElement("div");
      card.className = "sugerencia-card";
      var title = document.createElement("div");
      title.className = "texto-original";
      title.textContent = field.field_instance_id + " · " + field.controls.length + " aparicion(es)";
      var input = document.createElement("input");
      input.className = "search";
      input.value = field.value || "";
      var actions = document.createElement("div");
      actions.className = "actions";
      var apply = document.createElement("button");
      apply.className = "btn btn-primary";
      apply.textContent = "Aplicar en cascada";
      apply.onclick = function (event) {
        event.stopPropagation();
        aplicarCascada(field.field_instance_id, input.value);
      };
      actions.appendChild(apply);
      card.appendChild(title);
      card.appendChild(input);
      card.appendChild(actions);
      lista.appendChild(card);
    });
  }

  function fieldTag(fieldInstanceId, occurrenceId) {
    return FIELD_TAG_PREFIX + fieldInstanceId + ":" + occurrenceId + ":" + fieldInstanceId + ":" + fieldInstanceId;
  }

  async function reemplazarControl(internalId, tag, alias, text) {
    var response = await executeMethodAsync("InsertAndReplaceContentControls", [[{
      InternalId: internalId,
      Tag: tag,
      Alias: alias,
      Text: text
    }]]);
    return response.ok;
  }

  async function aceptarOcurrencia(occurrence) {
    if (!occurrence || !occurrence.internal_id) return false;
    if (!decisionesInlineDisponibles()) return false;
    if (esProvisional(occurrence)) {
      mostrarEstado("Asigne el dato a un campo existente o cree uno nuevo antes de aceptar.", "error");
      return false;
    }
    try {
      var token = await solicitarToken();
      var result = await decidirSugerenciaBackend(token, documentContextEnMemoria, occurrence, "accept");
      solicitarRecarga(result.review_document, occurrence.analysis_id);
      mostrarEstado("Decision guardada. Recargando version...", "ok");
      return true;
    } catch (error) {
      mostrarEstado(error && error.kind === "stale_suggestion" ? "El texto cambio despues del analisis. Ejecute el barrido nuevamente." : mensajeError(error), "error");
      return false;
    }
  }

  async function aceptarGrupo(group) {
    if (!group || !group.occurrences.length) return;
    await aceptarOcurrencia(group.occurrences[0]);
  }

  async function rechazarOcurrencia(occurrence) {
    if (!occurrence || !occurrence.internal_id) return false;
    if (!decisionesInlineDisponibles()) return false;
    try {
      var token = await solicitarToken();
      var result = await decidirSugerenciaBackend(token, documentContextEnMemoria, occurrence, "reject");
      solicitarRecarga(result.review_document, occurrence.analysis_id);
      mostrarEstado("Rechazo guardado. Recargando version...", "ok");
      return true;
    } catch (error) {
      mostrarEstado(error && error.kind === "stale_suggestion" ? "El texto cambio despues del analisis. Ejecute el barrido nuevamente." : mensajeError(error), "error");
      return false;
    }
  }

  async function rechazarGrupo(group) {
    if (!group || !group.occurrences.length) return;
    await rechazarOcurrencia(group.occurrences[0]);
  }

  async function cambiarOcurrencia(occurrence, explicitFieldCode, newFieldPayload) {
    if (!occurrence || !occurrence.internal_id) return false;
    if (!decisionesInlineDisponibles()) return false;
    if (!explicitFieldCode && !newFieldPayload) {
      abrirPanelCambio(occurrence);
      return false;
    }
    var fieldCode = explicitFieldCode;
    fieldCode = String(fieldCode || "").trim().toUpperCase();
    if (!fieldCode && !newFieldPayload) return false;
    try {
      var token = await solicitarToken();
      var overrides = newFieldPayload ? { new_field: newFieldPayload } : { field_code: fieldCode, visible_code: fieldCode };
      var result = await decidirSugerenciaBackend(token, documentContextEnMemoria, occurrence, "change", overrides);
      solicitarRecarga(result.review_document, occurrence.analysis_id);
      mostrarEstado("Cambio guardado. Recargando version...", "ok");
      return true;
    } catch (error) {
      mostrarEstado(error && error.kind === "field_assignment_required" ? "El campo seleccionado no esta disponible en el catalogo." : mensajeError(error), "error");
      return false;
    }
  }

  function abrirPanelCambio(occurrence) {
    cambioOccurrence = occurrence;
    var panel = document.getElementById("panelCambio");
    if (panel) panel.className = "change-panel visible";
    renderCambioSelect(camposCatalogo);
    mostrarEstado("Seleccione un campo o cree uno nuevo para la sugerencia marcada.", "");
  }

  function cerrarPanelCambio() {
    cambioOccurrence = null;
    var panel = document.getElementById("panelCambio");
    if (panel) panel.className = "change-panel";
  }

  async function asignarCampoSeleccionado() {
    if (!cambioOccurrence) return false;
    var select = document.getElementById("campoCambioSelect");
    var code = select ? select.value : "";
    if (!code) return false;
    var ok = await cambiarOcurrencia(cambioOccurrence, code);
    if (ok) cerrarPanelCambio();
    return ok;
  }

  async function crearYAsignarCampo() {
    if (!cambioOccurrence) return false;
    var code = document.getElementById("nuevoCampoCode");
    var label = document.getElementById("nuevoCampoLabel");
    var category = document.getElementById("nuevoCampoCategory");
    var fieldType = document.getElementById("nuevoCampoType");
    var payload = {
      code: code ? code.value.trim().toUpperCase() : "",
      label: label ? label.value.trim() : "",
      category: category && category.value.trim() ? category.value.trim() : "otro",
      field_type: fieldType && fieldType.value.trim() ? fieldType.value.trim() : "text"
    };
    if (!payload.code || !payload.label) {
      mostrarEstado("Codigo y nombre son obligatorios para crear el campo.", "error");
      return false;
    }
    var ok = await cambiarOcurrencia(cambioOccurrence, null, payload);
    if (ok) cerrarPanelCambio();
    return ok;
  }

  async function navegarAControl(control) {
    if (!control || !control.internal_id) return false;
    var moved = await executeMethodAsync("MoveCursorToContentControl", [control.internal_id]);
    if (!moved.ok) {
      moved = await executeMethodAsync("SelectContentControl", [control.internal_id]);
    }
    if (moved.ok) {
      activeControlId = control.internal_id;
      return true;
    }
    mostrarEstado("No fue posible navegar al campo en OnlyOffice.", "error");
    return false;
  }

  async function aplicarCascada(fieldInstanceId, value) {
    try {
      var token = await solicitarToken();
      var backend = await actualizarCampoBackend(token, documentContextEnMemoria, fieldInstanceId, value);
      solicitarRecarga(backend.review_document, null);
      mostrarEstado("Campo actualizado en backend. Recargando version...", "ok");
    } catch (error) {
      mostrarEstado("No fue posible aplicar la cascada.", "error");
    }
  }

  async function insertarCampoEstructurado(codigoCampo) {
    if (!codigoCampo) return;
    var occurrenceId = "manual_" + Date.now();
    var tag = fieldTag(codigoCampo, occurrenceId);
    var add = await executeMethodAsync("AddContentControl", [1, { Tag: tag, Alias: "EasyPro campo - " + codigoCampo }]);
    if (!add.ok) {
      mostrarEstado("OnlyOffice no permitio crear el campo estructurado en el cursor.", "error");
      return;
    }
    var internalId = add.value && (add.value.InternalId || add.value.InternalID || add.value.Id || add.value.id);
    if (internalId) {
      await reemplazarControl(internalId, tag, "EasyPro campo - " + codigoCampo, "{{" + codigoCampo + "}}");
    }
    await reconstruirDesdeControles();
    mostrarEstado("Campo estructurado insertado.", "ok");
  }

  async function reconstruirDesdeControles() {
    var result = await leerContentControls();
    if (result.ok) {
      renderSugerencias(gruposActuales);
    }
    return result;
  }

  function buscarSugerenciaPorControlId(contentControlId) {
    var id = String(contentControlId || "");
    var keys = Object.keys(suggestionControls);
    for (var index = 0; index < keys.length; index += 1) {
      var occurrence = suggestionControls[keys[index]];
      if (String(occurrence.internal_id) === id) return occurrence;
    }
    return null;
  }

  async function resolverAccionInline(contentControlId, action) {
    await reconstruirDesdeControles();
    var occurrence = buscarSugerenciaPorControlId(contentControlId);
    if (!occurrence) {
      mostrarEstado("No fue posible leer la sugerencia seleccionada.", "error");
      return;
    }
    if (action === "accept") {
      await aceptarOcurrencia(occurrence);
      return;
    }
    if (action === "reject") {
      await rechazarOcurrencia(occurrence);
      return;
    }
    await cambiarOcurrencia(occurrence);
  }

  function registrarBotonesContentControls() {
    if (botonesInlinePreparados) return false;
    if (!window.Asc || typeof window.Asc.ButtonContentControl !== "function") {
      botonesInlinePreparados = false;
      mostrarEstado("OnlyOffice incompatible: falta Asc.ButtonContentControl para decisiones inline.", "error");
      return false;
    }
    var acciones = [
      { action: "accept", icon: "resources/check.svg" },
      { action: "reject", icon: "resources/close.svg" },
      { action: "change", icon: "resources/edit.svg" }
    ];
    acciones.forEach(function (item) {
      var button = new window.Asc.ButtonContentControl();
      button.icons = item.icon;
      button.attachOnClick(function (contentControlId) {
        resolverAccionInline(contentControlId, item.action);
      });
    });
    botonesInlinePreparados = true;
    return true;
  }

  async function cargarCatalogo() {
    try {
      mostrarEstado("Conectando con Ecosistema Notarial...", "");
      var token = await solicitarToken();
      camposCatalogo = await cargarCatalogoConToken(token);
      renderCatalogo(camposCatalogo);
      await reconstruirDesdeControles();
      mostrarEstado(camposCatalogo.length ? "Catalogo cargado." : "El catalogo de campos esta vacio.", camposCatalogo.length ? "ok" : "");
    } catch (error) {
      renderCatalogo([]);
      mostrarEstado(mensajeError(error), "error");
    }
  }

  async function analizarDocumento() {
    if (analisisEnCurso) return;
    setAnalisisEnCurso(true);
    mostrarEstado("Analizando documento y preparando version de revision...", "");
    try {
      var token = await solicitarToken();
      var result = await analizarYPrepararConToken(token, documentContextEnMemoria);
      if (!result.review_document || !result.review_document.version_id) {
        mostrarEstado("El analisis fue recibido, pero no pudo preparar la version de revision.", "error");
        return;
      }
      solicitarRecarga(result.review_document, result.analysis_id);
      mostrarEstado("Version de revision preparada. Recargando editor...", "ok");
    } catch (error) {
      mostrarEstado(error && error.kind === "analysis_timeout" ? "No fue posible obtener el analisis del documento." : mensajeError(error), "error");
    } finally {
      setAnalisisEnCurso(false);
    }
  }

  function prepararDom() {
    var buscar = document.getElementById("buscarCampo");
    if (buscar) buscar.addEventListener("input", filtrarCatalogo);
    var cambioBuscar = document.getElementById("campoCambioBuscar");
    if (cambioBuscar) cambioBuscar.addEventListener("input", function () { renderCambioSelect(camposCatalogo); });
    var btnAsignarCampo = document.getElementById("btnAsignarCampo");
    if (btnAsignarCampo) btnAsignarCampo.addEventListener("click", asignarCampoSeleccionado);
    var btnCrearCampo = document.getElementById("btnCrearCampo");
    if (btnCrearCampo) btnCrearCampo.addEventListener("click", crearYAsignarCampo);
    var btnCancelarCambio = document.getElementById("btnCancelarCambio");
    if (btnCancelarCambio) btnCancelarCambio.addEventListener("click", cerrarPanelCambio);
    var btnAnalizar = document.getElementById("btnAnalizar");
    if (btnAnalizar) btnAnalizar.addEventListener("click", analizarDocumento);
  }

  window.Asc = window.Asc || {};
  window.Asc.plugin = window.Asc.plugin || {};

  window.Asc.plugin.init = function () {
    prepararListeners();
    registrarBotonesContentControls();
    prepararDom();
    cargarCatalogo();
  };

  window.Asc.plugin.button = function () {};
  window.Asc.plugin.onExternalMouseUp = function () {};

  window.cargarCatalogo = cargarCatalogo;
  window.renderSugerencias = renderSugerencias;
  window.insertarCampo = insertarCampoEstructurado;
  window.analizarDocumento = analizarDocumento;

  window.__EasyProBibliotecaPlugin = {
    constants: {
      AUTH_REQUEST_TYPE: AUTH_REQUEST_TYPE,
      AUTH_RESPONSE_TYPE: AUTH_RESPONSE_TYPE,
      RELOAD_REQUEST_TYPE: RELOAD_REQUEST_TYPE,
      PLUGIN_SOURCE: PLUGIN_SOURCE,
      HOST_SOURCE: HOST_SOURCE,
      CATALOG_PATH: CATALOG_PATH,
      ANALYZE_AND_PREPARE_PATH: ANALYZE_AND_PREPARE_PATH,
      DECISION_PATH: DECISION_PATH,
      CASCADE_BACKEND_PATH: CASCADE_BACKEND_PATH
    },
    test: {
      handleAuthMessage: handleAuthMessage,
      solicitarToken: solicitarToken,
      cargarCatalogoConToken: cargarCatalogoConToken,
      analizarYPrepararConToken: analizarYPrepararConToken,
      actualizarCampoBackend: actualizarCampoBackend,
      decidirSugerenciaBackend: decidirSugerenciaBackend,
      normalizarCatalogo: normalizarCatalogo,
      normalizarPreparacion: normalizarPreparacion,
      validarDocumentContext: validarDocumentContext,
      mensajeError: mensajeError,
      renderSugerencias: renderSugerencias,
      analizarDocumento: analizarDocumento,
      leerContentControls: leerContentControls,
      reconstruirDesdeControles: reconstruirDesdeControles,
      agruparSugerencias: agruparSugerencias,
      agruparCampos: agruparCampos,
      parseSuggestionTag: parseSuggestionTag,
      parseFieldTag: parseFieldTag,
      aceptarOcurrencia: aceptarOcurrencia,
      rechazarOcurrencia: rechazarOcurrencia,
      aceptarGrupo: aceptarGrupo,
      rechazarGrupo: rechazarGrupo,
      cambiarOcurrencia: cambiarOcurrencia,
      abrirPanelCambio: abrirPanelCambio,
      cerrarPanelCambio: cerrarPanelCambio,
      asignarCampoSeleccionado: asignarCampoSeleccionado,
      crearYAsignarCampo: crearYAsignarCampo,
      navegarAControl: navegarAControl,
      aplicarCascada: aplicarCascada,
      insertarCampoEstructurado: insertarCampoEstructurado,
      registrarBotonesContentControls: registrarBotonesContentControls,
      resolverAccionInline: resolverAccionInline,
      solicitarRecarga: solicitarRecarga,
      getSuggestionControls: function () { return suggestionControls; },
      getFieldControls: function () { return fieldControls; },
      getGroups: function () { return gruposActuales; },
      getFields: function () { return fieldsActuales; },
      getActiveControlId: function () { return activeControlId; },
      getCambioOccurrence: function () { return cambioOccurrence; },
      reset: function () {
        tokenEnMemoria = null;
        documentContextEnMemoria = null;
        suggestionControls = {};
        fieldControls = {};
        gruposActuales = [];
        fieldsActuales = [];
        activeControlId = null;
        cambioOccurrence = null;
        authPromise = null;
        authResolve = null;
        authReject = null;
        analisisEnCurso = false;
        if (authTimer) window.clearTimeout(authTimer);
        authTimer = null;
      }
    }
  };
}());
