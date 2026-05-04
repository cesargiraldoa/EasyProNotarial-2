# Inventario funcional de EasyPro_1

## Alcance revisado
- Repo analizado: `C:\EasyPro_1\proyecto notarios\proyecto-notarios_07012026`
- Se toma como referencia funcional, documental y operativa.
- No se modifico ningun archivo de ese repo.

## Estructura del proyecto
- `app/core`: configuracion Django, URLs globales, WSGI/ASGI y settings.
- `app/web`: app principal con modelos, forms, views, templates, urls, utils y templatetags.
- `app/static` y `app/web/static`: assets de AdminLTE, Bootstrap, jQuery y librerias front.
- `app/web/templates`: vistas HTML para login, home, plantillas, documentos, seguimiento, tablas y protocolos.
- `Documentos/`: carpeta con el documento base real encontrado en el repo.
- `nginx/`: configuracion de despliegue.
- `backup.sql`: respaldo de base de datos del sistema funcional.

## Tecnologia usada
- Backend: Django 4.2.16.
- Frontend server-side: templates Django.
- Base de datos: MySQL segun `settings.py`.
- Generacion documental:
  - `python-docx` para editar DOCX.
  - `libreoffice --headless` para convertir a PDF.
  - `PyPDF2` y `reportlab` para utilidades de PDF.
- Autenticacion/autorizacion: `django.contrib.auth` con permisos por modulo.
- Observabilidad: `django-prometheus`.

## Modulos principales
- `Document` y `DocumentDetails`: gestion de documentos ingresados.
- `Template` y `TemplateDetails`: plantillas y etiquetas detectadas.
- `TableMaster`: catalogos de valores para combos/listas.
- `Tracking`: seguimiento y aprobacion/rechazo.
- `Protocolo`: registro y consulta de escrituras en PDF.

## Tipos documentales que genera
### Confirmados por codigo
- Documentos genericos basados en una plantilla DOCX.
- PDF generado desde el DOCX completado.
- DOCX completado sin convertir a PDF.
- Protocolos PDF cargados manualmente en `Protocolo`.

### Pendiente de verificacion
- No se encontro un catalogo formal de tipos documentales en codigo; el tipo documental depende de la plantilla cargada.
- El repositorio contiene una plantilla base especifica: `SALIDA_DEL_PAIS NOT_TITULAR.docx`.

## Plantillas o documentos base usados
- Documento base encontrado:
  - `Documentos/SALIDA_DEL_PAIS NOT_TITULAR.docx`
- La logica permite cargar otras plantillas `.doc` o `.docx`, pero en el arbol visible solo aparece ese archivo base.

## Campos usados por tipo documental
### Modelo `Template`
- `name`
- `description`
- `status`
- `file_name`

### Modelo `TemplateDetails`
- `table_master`
- `label`
- `title`
- `class_css`
- `checked`
- `control_type`
- `num_order`

### Modelo `Document`
- `client_name`
- `title`
- `template`
- `status`
- `comments`

### Modelo `DocumentDetails`
- `table_master`
- `label`
- `title`
- `value_field`
- `class_css`
- `checked`
- `control_type`
- `num_order`

### Modelo `Protocolo`
- `escritura`
- `ano`
- `archivo_pdf`

## Flujo de usuario
### Plantillas
1. Crear plantilla con nombre, descripcion, estado y archivo DOCX.
2. El sistema extrae automaticamente las etiquetas `{{...}}` del Word.
3. Se crean o sincronizan registros en `TemplateDetails`.
4. El usuario ajusta manualmente cada etiqueta, su titulo, tipo de control y orden.

### Documentos
1. Crear documento con cliente, titulo y plantilla.
2. El sistema copia todos los `TemplateDetails` a `DocumentDetails`.
3. El usuario diligencia los campos en la pantalla de edicion.
4. El usuario guarda cambios y el documento queda en estado `registered`.
5. El usuario puede aprobar o rechazar desde seguimiento.
6. Si se aprueba, se bloquea la edicion.
7. Desde la accion de generacion se obtiene Word o PDF.

### Seguimiento
1. Ver lista filtrable de documentos.
2. Abrir verificacion de un documento.
3. Marcar aprobado o rechazado.
4. Registrar comentarios.
5. Validar campos obligatorios marcados como `checked`.

### Protocolos
1. Registrar numero de escritura, ano y PDF adjunto.
2. Consultar y descargar el PDF.

## Logica de generacion documental
### Extraccion de etiquetas
- `get_specific_words()` lee el DOCX y extrae etiquetas con regex `{{[a-zA-Z0-9_]+}}`.
- `insert_labels()` crea o actualiza `TemplateDetails` a partir de esas etiquetas.

### Reemplazo de valores
- `GeneratePdfView.reemplazar_etiquetas()` abre el DOCX con `python-docx`.
- Recorre runs y reemplaza la etiqueta completa por el valor capturado en `DocumentDetails.value_field`.
- Si el valor es fecha, intenta formatearlo en texto largo.
- Si un run contiene `[[--]]`, lo reemplaza por tabulacion.

### Exportacion a PDF
- `convertir_a_pdf()` usa LibreOffice en modo headless.
- El DOCX completado se guarda en `MEDIA_ROOT` y luego se convierte a PDF.

## Archivos clave
- `app/web/views/generatepdf.py`
- `app/web/views/document.py`
- `app/web/views/template.py`
- `app/web/views/tracking.py`
- `app/web/views/common.py`
- `app/web/models.py`
- `app/web/forms/document.py`
- `app/web/forms/template.py`
- `app/web/forms/protocolo.py`
- `app/core/settings.py`
- `app/web/urls.py`
- `Documentos/SALIDA_DEL_PAIS NOT_TITULAR.docx`

## Manualidades o pasos no automatizados
- La plantilla DOCX debe contener etiquetas exactas y completas.
- El usuario debe clasificar cada etiqueta en `TemplateDetails`.
- El usuario debe diligenciar cada `DocumentDetails` manualmente.
- La aprobacion depende de validar visualmente los campos marcados.
- El PDF depende de tener LibreOffice disponible en el entorno.
- El flujo no tiene una entidad de caso o expediente; el documento es la unidad principal.

## Reglas notariales implicitas
- El documento base debe respetar estructura formal notarial.
- Las fechas deben aparecer en texto largo cuando el valor es fecha.
- Los campos marcados como obligatorios no pueden quedar vacios al aprobar.
- El documento aprobado no se puede volver a editar.
- Los protocolos se manejan como registro separado por escritura y ano.

## Como logra generar documentos correctamente
- Usa una plantilla DOCX real como base.
- Extrae las etiquetas visibles de esa plantilla y las convierte en campos editables.
- Guarda los valores por etiqueta en la base de datos.
- Reemplaza exactamente las etiquetas `{{...}}` al generar el documento.
- Convierte el DOCX terminado a PDF con una herramienta de escritorio madura.
- Mantiene un flujo simple: plantilla -> documento -> verificacion -> salida.

## Resumen de valor funcional
- EasyPro_1 funciona porque combina una plantilla Word real, campos editables por etiqueta, aprobacion humana y conversion directa a PDF.
- Su fortaleza no esta en la arquitectura, sino en que el flujo de produccion documental es corto, visible y reproducible.
