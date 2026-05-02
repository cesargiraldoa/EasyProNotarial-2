# Diagnostico flujo EasyPro 2 vs EasyPro 1

## 1. Resumen ejecutivo

EasyPro 2 ya resolvio la parte mas delicada del producto: el motor de generacion DOCX funciona, la plantilla puede cambiar y el formulario de diligenciamiento se adapta a las etiquetas detectadas. Eso significa que el sistema ya no depende de un formulario fijo.

El problema actual no es el motor, sino la experiencia operativa. Hoy el flujo esta repartido entre varias vistas, varios modos de generar el mismo documento y varios catálogos que existen solo de forma parcial o dispersa. Frente a EasyPro 1, EasyPro 2 tiene mejor arquitectura, pero aun no ofrece una experiencia simple y corta para protocolista ni una bandeja clara para revision/aprobacion.

La conclusion tecnica-funcional es esta:
- El motor dinamico debe quedar intacto.
- La UX debe simplificarse alrededor de un flujo unico por rol.
- Los catálogos deben pasar de listas sueltas o hardcoded a selecciones consistentes.
- La aprobacion/rechazo necesita una superficie visible, no solo endpoints backend.

## 2. Regla critica

Mantener intacto el motor dinamico de generacion de EasyPro 2.

No tocar:
- reemplazo de etiquetas en DOCX
- logica de tab stop y leader de guiones notariales
- descarga del Word generado
- generacion DOCX desde plantilla
- regeneracion Gari del borrador
- versionado documental existente

Referencias de motor revisadas:
- [frontend/lib/document-flow.ts](C:/EasyProNotarial-2/easypro2/frontend/lib/document-flow.ts)
- [backend/app/services/document_generation.py](C:/EasyProNotarial-2/easypro2/backend/app/services/document_generation.py)
- [backend/app/services/gari_document_service.py](C:/EasyProNotarial-2/easypro2/backend/app/services/gari_document_service.py)
- [backend/app/modules/document_flow/router.py](C:/EasyProNotarial-2/easypro2/backend/app/modules/document_flow/router.py)

## 3. Tabla comparativa

| EasyPro 1 vista | EasyPro 2 equivalente | Estado actual | Brecha | Recomendacion |
|---|---|---|---|---|
| Home | `frontend/app/(app)/dashboard/page.tsx` + `DashboardOverview` | Existe un dashboard ejecutivo, mas analitico que operativo | No es una portada de trabajo simple para protocolista | Crear una portada de tarea rapida por rol, sin quitar el dashboard ejecutivo |
| Plantillas | `frontend/components/templates/templates-workspace.tsx` | Existe CRUD de plantillas con carga de DOCX y campos extraidos | La vista sigue siendo mas tecnica que operativa | Mantenerla, pero reducir carga visual y separar edicion tecnica de uso diario |
| Documentos / Minutas | `frontend/components/cases/cases-workspace.tsx` | Existe lista de minutas con filtros | La lista esta bien, pero no orienta claramente a "hacer el documento" | Mantener la bandeja y enfatizar estado, proximo paso y responsable |
| Crear documento | `frontend/components/cases/create-case-wizard.tsx` | Existe wizard por pasos para crear minuta desde plantilla | Hay mas complejidad de la necesaria para una operacion diaria | Convertirlo en flujo guiado corto: plantilla -> datos -> revision -> crear |
| Diligenciar documento | `frontend/components/cases/create-case-wizard.tsx` + `frontend/lib/document-flow.ts` | El formulario se arma dinamicamente desde `template.fields` | La logica correcta existe, pero la UX expone demasiadas decisiones | Reducir ruido y agrupar campos por seccion, conservando el motor dinamico |
| Detalle del caso | `frontend/components/cases/case-detail-workspace.tsx` | Hay workspace con documento, datos y trazabilidad | Falta lectura operativa mas directa para revision | Separar modo lectura, modo edicion y acciones de aprobacion |
| Documento Gari | Backend en `generate-with-gari` y descarga Gari | Existe soporte backend y descarga del Gari DOCX | No hay superficie principal clara en frontend para este camino | Mantenerlo como apoyo, no como pantalla principal de operacion diaria |
| Seguimiento | `frontend/components/cases/cases-workspace.tsx` + trazabilidad en detalle | Existe lista y timeline/workflow | Falta una bandeja de seguimiento dedicada por rol | Crear una cola de seguimiento con filtros por estado, asignado y accion pendiente |
| Verificar / aprobar / rechazar | `backend/app/modules/document_flow/router.py` | Los endpoints existen, con estados y comentarios | La UI no presenta aprobacion/rechazo de forma evidente | Exponer aprobacion y rechazo en detalle de caso, en modo lectura controlada |
| Tablas maestras / catalogos | `notaries`, `users`, `roles`, `persons`, `legal_entities`, `act-catalog` | Existen varias entidades maestras y APIs | Estan dispersas y no todas alimentan el flujo operativo | Consolidar solo los catalogos necesarios para diligenciamiento y revision |
| Protocolos | No se ve una vista de protocolos dedicada | No existe equivalente visible en frontend | Falta una pantalla simple de protocolo / salida final | Si se requiere, crearla despues de estabilizar el flujo documental principal |

## 4. Flujo recomendado para protocolista

1. Escoger plantilla.
2. Crear minuta/caso.
3. Seleccionar o reutilizar personas y, cuando aplique, entidades juridicas.
4. Diligenciar el formulario dinamico generado por la plantilla.
5. Guardar borrador.
6. Generar Word.
7. Descargar Word.

Lectura funcional:
- El protocolista no deberia tener que pensar en estados internos complejos.
- El wizard debe sentirse como una unica tarea continua.
- La plantilla debe definir lo obligatorio, y el sistema debe mostrar solo lo necesario.

## 5. Flujo recomendado para revisor/aprobador

1. Abrir bandeja de seguimiento.
2. Filtrar por estado, notaria, responsable o texto.
3. Abrir el caso en modo lectura.
4. Revisar versiones del documento y trazabilidad.
5. Aprobar o rechazar.
6. Dejar comentario.
7. Descargar la version necesaria o cargar el final firmado si el proceso lo exige.

Lectura funcional:
- La revision debe ser una accion clara, no una busqueda dentro de tabs genericos.
- El detalle debe priorizar lectura y decision, no captura de datos.
- Los comentarios de rechazo o aprobacion deben quedar visibles en timeline/workflow.

## 6. Catalogos / selects detectados

Detectados en UI actual:
- tipo de documento: `CC`, `CE`, `TI`, `PP`, `NIT`
- sexo: `F`, `M`, `No especifica`
- nacionalidad: lista fija en wizard y entrada libre en lookup de persona
- estado civil: lista fija en lookup de persona
- profesion / oficio: lista fija en lookup de persona
- notarias: selector en wizard y en plantillas
- usuarios / responsables: selector en wizard para responsable actual, protocolista, aprobador y notario titular
- notario suplente: selector opcional en wizard
- campos de plantilla con `field_type = select` y `options_json`
- catalogo de actos backend: `/api/v1/act-catalog`
- entidades juridicas: lookup y API separada

Detectados en backend o por modelo, pero no como flujo principal visible:
- estados de caso
- roles de aprobacion
- plantillas activas
- personas reutilizables
- documentos versionados

## 7. Catalogos / selects faltantes

Faltan como experiencia unificada en el flujo de minuta:
- tipo documental notarial con opciones mas amplias y controladas
- nacionalidad con catalogo real
- sexo con catalogo notarial y no solo tres valores
- profesion / oficio con catalogo reutilizable
- municipio con catalogo o autocompletado
- calidad en que actua
- tipo de acto como selector de trabajo, no solo como atributo derivado
- bancos
- forma de pago
- catalogos notariales adicionales por acto
- selector de interviniente/entidad juridica integrado al flujo de minuta
- bandeja de revision/aprobacion con acciones visibles

Observacion funcional:
- Hoy varias de estas cosas existen solo como texto libre, seeds, prompts o datos de contexto.
- Eso obliga al protocolista a escribir demasiado y aumenta variacion innecesaria.

## 8. Archivos revisados

- [frontend/components/cases/create-case-wizard.tsx](C:/EasyProNotarial-2/easypro2/frontend/components/cases/create-case-wizard.tsx)
- [frontend/components/cases/case-detail-workspace.tsx](C:/EasyProNotarial-2/easypro2/frontend/components/cases/case-detail-workspace.tsx)
- [frontend/components/cases/cases-workspace.tsx](C:/EasyProNotarial-2/easypro2/frontend/components/cases/cases-workspace.tsx)
- [frontend/components/templates/templates-workspace.tsx](C:/EasyProNotarial-2/easypro2/frontend/components/templates/templates-workspace.tsx)
- [frontend/components/app-shell/dashboard.tsx](C:/EasyProNotarial-2/easypro2/frontend/components/app-shell/dashboard.tsx)
- [frontend/components/persons/person-lookup.tsx](C:/EasyProNotarial-2/easypro2/frontend/components/persons/person-lookup.tsx)
- [frontend/components/ui/searchable-select.tsx](C:/EasyProNotarial-2/easypro2/frontend/components/ui/searchable-select.tsx)
- [frontend/lib/document-flow.ts](C:/EasyProNotarial-2/easypro2/frontend/lib/document-flow.ts)
- [frontend/lib/api.ts](C:/EasyProNotarial-2/easypro2/frontend/lib/api.ts)
- [frontend/app/(app)/dashboard/page.tsx](C:/EasyProNotarial-2/easypro2/frontend/app/(app)/dashboard/page.tsx)
- [frontend/app/(app)/dashboard/casos/page.tsx](C:/EasyProNotarial-2/easypro2/frontend/app/(app)/dashboard/casos/page.tsx)
- [frontend/app/(app)/dashboard/casos/crear/page.tsx](C:/EasyProNotarial-2/easypro2/frontend/app/(app)/dashboard/casos/crear/page.tsx)
- [frontend/app/(app)/dashboard/casos/[caseId]/page.tsx](C:/EasyProNotarial-2/easypro2/frontend/app/(app)/dashboard/casos/[caseId]/page.tsx)
- [frontend/app/(app)/dashboard/actos-plantillas/page.tsx](C:/EasyProNotarial-2/easypro2/frontend/app/(app)/dashboard/actos-plantillas/page.tsx)
- [backend/app/modules/document_flow/router.py](C:/EasyProNotarial-2/easypro2/backend/app/modules/document_flow/router.py)
- [backend/app/modules/templates/router.py](C:/EasyProNotarial-2/easypro2/backend/app/modules/templates/router.py)
- [backend/app/modules/cases/router.py](C:/EasyProNotarial-2/easypro2/backend/app/modules/cases/router.py)
- [backend/app/modules/dashboard/router.py](C:/EasyProNotarial-2/easypro2/backend/app/modules/dashboard/router.py)
- [backend/app/modules/act_catalog/router.py](C:/EasyProNotarial-2/easypro2/backend/app/modules/act_catalog/router.py)
- [backend/app/modules/persons/router.py](C:/EasyProNotarial-2/easypro2/backend/app/modules/persons/router.py)
- [backend/app/modules/notaries/router.py](C:/EasyProNotarial-2/easypro2/backend/app/modules/notaries/router.py)
- [backend/app/modules/legal_entities/router.py](C:/EasyProNotarial-2/easypro2/backend/app/modules/legal_entities/router.py)
- [backend/app/services/document_generation.py](C:/EasyProNotarial-2/easypro2/backend/app/services/document_generation.py)
- [backend/app/services/gari_document_service.py](C:/EasyProNotarial-2/easypro2/backend/app/services/gari_document_service.py)
- [backend/app/schemas/case.py](C:/EasyProNotarial-2/easypro2/backend/app/schemas/case.py)
- [backend/app/seeds/seed_document_templates.py](C:/EasyProNotarial-2/easypro2/backend/app/seeds/seed_document_templates.py)

## 9. Propuesta de sprint posterior

### Cambios seguros de UI/UX
- Reducir el wizard a una narrativa lineal de 3 o 4 pasos.
- Enfatizar accion principal y estado actual.
- Crear un modo lectura para detalle del caso.
- Separar visualmente generar, revisar, aprobar y descargar.
- Simplificar listados y tarjetas para que el protocolista no pierda contexto.

### Cambios de catalogos
- Convertir a select/autocomplete los campos que hoy son texto libre y se repiten.
- Reutilizar personas, entidades juridicas y representantes desde el flujo principal.
- Unificar catalogos de nacionalidad, sexo, estado civil, profesion, municipio, bancos y forma de pago.
- Exponer el catalogo de actos solo donde aporte valor operativo.

### Cambios de aprobacion / seguimiento
- Crear bandeja de seguimiento por rol.
- Hacer visibles aprobar, rechazar y comentar en la UI.
- Mostrar historial de decisiones y versiones en un solo lugar.
- Dejar claro quien tiene la siguiente accion.

### Cosas que NO deben tocarse
- motor de reemplazo de etiquetas
- logica de tab stop / leader de guiones
- descarga del Word
- generacion DOCX desde plantilla
- versionado documental
- flujo Gari backend
- contratos API existentes
- migraciones
- estructura de persistencia del documento ya funcional

## Cierre

Este diagnostico no propone cambios funcionales todavia. Solo deja identificado que EasyPro 2 ya tiene la base tecnica correcta y que el siguiente paso debe ser simplificar la experiencia operativa sin alterar el motor documental que ya funciona.
