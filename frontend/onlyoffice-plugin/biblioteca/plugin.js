(function () {
  "use strict";

  var AUTH_REQUEST_TYPE = "EASYPRO_ONLYOFFICE_AUTH_REQUEST";
  var AUTH_RESPONSE_TYPE = "EASYPRO_ONLYOFFICE_AUTH_RESPONSE";
  var PLUGIN_SOURCE = "motor-biblioteca";
  var HOST_SOURCE = "easypro-host";
  var AUTH_TIMEOUT_MS = 5000;
  var DEFAULT_API_BASE_URL = "https://easypronotarial-2-production.up.railway.app";
  var CATALOG_PATH = "/api/v1/biblioteca/campos";
  var DEFAULT_HOST_ORIGINS = [
    "https://easypronotarial.com",
    "http://localhost:5179",
    "http://127.0.0.1:5179"
  ];

  var camposCatalogo = [];
  var tokenEnMemoria = null;
  var authPromise = null;
  var authTimer = null;
  var authResolve = null;
  var authReject = null;
  var listenersPreparados = false;

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

  function resolverAuth(token) {
    tokenEnMemoria = token;
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
      resolverAuth(data.token.trim());
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

  function categoriaClass(categoria) {
    return "cat-" + (categoria || "otro");
  }

  function confianzaClass(confianza) {
    if (confianza > 0.95) return "conf-alta";
    if (confianza > 0.85) return "conf-media";
    return "conf-baja";
  }

  function renderSugerencias(data) {
    var sugerencias = Array.isArray(data) ? data : [];
    var wrapper = document.getElementById("sugerencias");
    var contador = document.getElementById("contador");
    var lista = document.getElementById("listaSugerencias");

    if (!wrapper || !contador || !lista) return;

    wrapper.style.display = "block";
    contador.textContent = String(sugerencias.length);
    lista.innerHTML = "";

    sugerencias.forEach(function (item) {
      var card = document.createElement("div");
      card.className = "sugerencia-card";
      card.dataset.texto = item.texto_original || "";
      card.dataset.campo = item.campo_sugerido || "";
      card.dataset.categoria = item.categoria || "";

      var texto = document.createElement("div");
      texto.className = "texto-original";
      texto.textContent = item.texto_original || "";

      var campo = document.createElement("div");
      campo.className = "campo-sugerido";
      campo.textContent = item.campo_sugerido || "";

      var badges = document.createElement("div");
      badges.className = "badges";

      var categoria = document.createElement("span");
      categoria.className = "badge " + categoriaClass(item.categoria);
      categoria.textContent = item.categoria || "otro";

      var confianza = document.createElement("span");
      confianza.className = "badge " + confianzaClass(Number(item.confianza || 0));
      confianza.textContent = Math.round(Number(item.confianza || 0) * 100) + "%";

      badges.appendChild(categoria);
      badges.appendChild(confianza);

      var actions = document.createElement("div");
      actions.className = "actions";

      var yes = document.createElement("button");
      yes.className = "btn btn-yes";
      yes.textContent = "Sí";
      yes.disabled = true;
      yes.title = "Análisis del documento disponible en el siguiente bloque.";

      var no = document.createElement("button");
      no.className = "btn btn-no";
      no.textContent = "No";
      no.disabled = true;
      no.title = "Análisis del documento disponible en el siguiente bloque.";

      actions.appendChild(yes);
      actions.appendChild(no);
      card.appendChild(texto);
      card.appendChild(campo);
      card.appendChild(badges);
      card.appendChild(actions);
      lista.appendChild(card);
    });
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

  function mensajeError(error) {
    var kind = error && error.kind;
    if (kind === "no_session") {
      return "No hay una sesión activa. Cierre el editor y vuelva a abrirlo desde Ecosistema Notarial.";
    }
    if (kind === "auth_timeout" || kind === "auth_failed" || kind === "network_error" || kind === "backend_unavailable" || kind === "invalid_json") {
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
    mostrarEstado("Análisis del documento disponible en el siguiente bloque.", "");
  }

  function analizarDocumento() {
    mostrarEstado("Análisis del documento disponible en el siguiente bloque.", "");
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
      CATALOG_PATH: CATALOG_PATH
    },
    test: {
      handleAuthMessage: handleAuthMessage,
      solicitarToken: solicitarToken,
      cargarCatalogoConToken: cargarCatalogoConToken,
      normalizarCatalogo: normalizarCatalogo,
      mensajeError: mensajeError,
      reset: function () {
        tokenEnMemoria = null;
        authPromise = null;
        authResolve = null;
        authReject = null;
        if (authTimer) {
          window.clearTimeout(authTimer);
        }
        authTimer = null;
      }
    }
  };
}());
