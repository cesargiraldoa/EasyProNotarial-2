# Plan de migracion funcional

## Principio rector
- No copiar ciegamente el codigo de EasyPro_1.
- Reutilizar la idea funcional que ya comprobo salida documental correcta.
- Mantener en EasyProNotarial-2 el modelo de caso, versionado, trazabilidad y reutilizacion de entidades.
- Convertir EasyPro_1 en referencia de comportamiento, no en plantilla de arquitectura.

## Objetivo de migracion
- Primer hito: una escritura de compraventa generada de principio a fin.
- El resultado debe incluir:
  - seleccion de plantilla,
  - registro de participantes,
  - registro de datos del acto,
  - generacion de borrador DOCX,
  - descarga/versionado,
  - exportacion,
  - aprobacion,
  - carga del documento final firmado.

## Fase 0. Base funcional comun
### Meta
- Asegurar que la compraventa tenga una variante unica y verificable de extremo a extremo.

### Acciones
- Definir una sola ruta principal de compraventa.
- Congelar un conjunto minimo de campos obligatorios.
- Alinear roles requeridos con participantes reutilizables y entidades juridicas.
- Establecer una nomenclatura unica para estados y versiones.

### Entregable
- Un caso de compraventa que pueda completar todo el flujo sin bifurcaciones manuales.

## Fase 1. Normalizacion de datos
### Meta
- Conectar plantillas, personas, bancos, apoderados y inmueble al caso.

### Acciones
- Reforzar el uso de `template_fields` como contrato del formulario.
- Normalizar `persons` y `legal_entities` como catalogos de reutilizacion.
- Usar `case_participants` como unico punto de comparecencia.
- Amarrar `case_act_data` al set de campos requeridos por plantilla.

### Entregable
- El flujo de compraventa toma datos estructurados y no solo JSON libre.

## Fase 2. Generacion documental estable
### Meta
- Convertir el documento base en borrador DOCX validado.

### Acciones
- Mantener el DOCX base real en `backend/storage/templates`.
- Validar campos requeridos antes de generar.
- Generar version `draft` como primera evidencia documental.
- Guardar snapshot de placeholders y datos de origen.

### Entregable
- Borrador DOCX versionado y descargable.

## Fase 3. Aprobacion y cierre operativo
### Meta
- Llegar a documento aprobado por notario y listo para cierre.

### Acciones
- Consolidar aprobacion por roles.
- Asignar numero oficial de escritura al aprobar.
- Mantener historial de workflow y timeline.
- Habilitar carga del PDF firmado final.

### Entregable
- Escritura con trazabilidad completa y evidencia final cargada.

## Fase 4. Redaccion inteligente asistida
### Meta
- Usar Gari como copiloto, no como unica base.

### Acciones
- Usar Gari para proponer texto, no para definir la estructura principal.
- Alimentar a Gari con plantilla, participantes, actos y campos estructurados.
- Registrar el texto generado como version documental adicional.
- Controlar las variaciones entre borradores.

### Entregable
- Redaccion asistida sobre una base estructurada y auditable.

## Priorizacion tecnica
### Alta prioridad
- Compraventa.
- Reutilizacion de participantes.
- Integracion de entidades juridicas.
- Versionado documental.
- Aprobacion y descarga de versiones.

### Prioridad media
- Preview embebido.
- Export PDF fiel.
- Analitica y dashboard.

### Prioridad baja
- Automatizaciones adicionales de lotes.
- IA para otros tipos documentales.

## Que conviene reutilizar de EasyPro_1
- El concepto de plantilla DOCX real.
- La deteccion de etiquetas y su mapeo a campos.
- La conversion a PDF via motor local estable.

## Que conviene tomar solo como referencia
- La logica simple de bloqueo tras aprobacion.
- La validacion manual de campos obligatorios.
- El rol del usuario como aprobador del estado documental.

## Que conviene descartar
- El modelo centrado en documento aislado.
- El mantenimiento manual de cada campo desde cero para cada documento.
- La dependencia total de una sola plantilla monolitica.

## Que conviene rehacer mejor
- El flujo de compraventa como proceso completo.
- La semantica de roles y comparecientes.
- El uso de bancos, fiducias, poderes e inmuebles como entidades de dominio.
- El control de estados por caso, no por formulario suelto.

## Siguiente entregable recomendado
- Sprint enfocado solo en una escritura de compraventa completa.
- Criterio de aceptacion:
  - se crea el caso,
  - se asigna plantilla,
  - se registran participantes,
  - se guardan datos del acto,
  - se genera borrador,
  - se descarga la version,
  - se aprueba,
  - se exporta,
  - se carga el firmado final,
  - el historial queda completo.
