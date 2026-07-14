// Inicialización
window.Asc.plugin.init = function() {
    // Cargar catálogo al iniciar
    if (typeof cargarCatalogo === "function") cargarCatalogo();
};

// Función principal: analizar documento
window.Asc.plugin.button = function(id) {};

// Obtener texto del documento para analizar
function obtenerTextoDocumento() {
    window.Asc.plugin.callCommand(function() {
        var oDoc = Api.GetDocument();
        var sText = "";
        var nCount = oDoc.GetElementsCount();
        for (var i = 0; i < nCount; i++) {
            var oElement = oDoc.GetElement(i);
            if (oElement) sText += oElement.GetText() + "\n";
        }
        return sText;
    }, false, false);
}

// Aceptar sugerencia: inserta el marcador del campo sugerido
function aceptarSugerencia(textoOriginal, campoSugerido) {
    window.Asc.plugin.executeMethod("PasteText", ["{{" + campoSugerido + "}}"], function() {
        mostrarEstado("Campo " + campoSugerido + " marcado.", "ok");
    });
    // Ocultar la card
    var cards = document.querySelectorAll(".sugerencia-card");
    cards.forEach(function(card) {
        if (card.getAttribute("data-texto") === textoOriginal) {
            card.style.display = "none";
        }
    });
}

// Insertar campo en posición del cursor
function insertarCampo(codigoCampo, labelCampo) {
    window.Asc.plugin.executeMethod("PasteText", ["{{" + codigoCampo + "}}"], function() {});
}

// Función analizar: notifica el flujo disponible para análisis
function analizarDocumento() {
    mostrarEstado("Analizando documento...", "cargando");
    
    var token = getToken();
    if (!token) {
        mostrarEstado("Error: no hay sesión activa. Recarga la página.", "error");
        return;
    }
    
    // En OnlyOffice v9 el plugin panel no puede acceder al documento directamente.
    // El análisis se hace desde el backend usando el storage_path del documento.
    // Por ahora notificamos al usuario que use el botón desde la Biblioteca.
    setTimeout(function() {
        mostrarEstado("Para analizar: usa el botón 'Subir documento' en la Biblioteca de Plantillas.", "ok");
    }, 500);
}

// Event listener para mensajes del documento
window.Asc.plugin.onExternalMouseUp = function() {};
