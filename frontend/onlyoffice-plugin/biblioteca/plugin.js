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

// Aceptar sugerencia: convierte texto en Content Control
function aceptarSugerencia(textoOriginal, campoSugerido) {
    window.Asc.plugin.scope = { textoOriginal: textoOriginal, campoSugerido: campoSugerido };

    window.Asc.plugin.callCommand(function() {
        var oDoc = Api.GetDocument();
        var nCount = oDoc.GetElementsCount();
        var sTexto = window.Asc.plugin.scope.textoOriginal;
        var sCampo = window.Asc.plugin.scope.campoSugerido;

        // Buscar y reemplazar todas las ocurrencias con Content Control
        for (var i = 0; i < nCount; i++) {
            var oPar = oDoc.GetElement(i);
            if (!oPar || typeof oPar.GetText !== "function") continue;
            var sParText = oPar.GetText();
            if (sParText && sParText.indexOf(sTexto) !== -1) {
                // Crear Content Control inline
                var oRun = Api.CreateRun();
                oRun.AddText(sTexto);
                var oCC = Api.CreateInlineLvlSdt();
                oCC.SetAlias(sCampo);
                oCC.SetTag(sCampo);
                oCC.Push(oRun);
                // El reemplazo real se hace via search/replace
            }
        }

        // Usar Search and Replace nativo de OnlyOffice
        oDoc.ReplaceAllText(
            {searchText: sTexto, replaceText: "{{" + sCampo + "}}", matchCase: true},
        );
    }, false, false);
}

// Insertar campo en posición del cursor
function insertarCampo(codigoCampo, labelCampo) {
    window.Asc.plugin.scope = { codigo: codigoCampo, label: labelCampo };
    window.Asc.plugin.callCommand(function() {
        var sCodigo = window.Asc.plugin.scope.codigo;
        var oDoc = Api.GetDocument();
        var oCursor = oDoc.GetCurrentCursor();
        if (oCursor) {
            oCursor.AddText("{{" + sCodigo + "}}");
        }
    }, false, false);
}

// Función analizar: sube el documento al backend y obtiene sugerencias
async function analizarDocumento() {
    mostrarEstado("Analizando documento...", "cargando");

    // Obtener el documento como base64 via OnlyOffice
    window.Asc.plugin.callCommand(function() {
        // Solicitar descarga del documento actual
        window.Asc.plugin.executeMethod("GetImageDataFromSelection", [], function(data) {});
    }, false, false);

    // Alternativa: usar el endpoint con el storage_path del documento actual
    // Por ahora mostrar mensaje de que la función está en construcción
    mostrarEstado("Función de análisis disponible desde el panel principal", "ok");
}

// Event listener para mensajes del documento
window.Asc.plugin.onExternalMouseUp = function() {};
