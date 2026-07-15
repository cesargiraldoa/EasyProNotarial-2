# Motor de Biblioteca issue 121 - diagnostico y ADR

Fecha: 2026-07-15
Rama: `biblioteca-motor-issue-121`
Issue fuente: https://github.com/cesargiraldoa/EasyProNotarial-2/issues/121

## Diagnostico

### Pipeline actual

1. Extraccion: `analysis.extract_docx_blocks` lee parrafos y celdas con `python-docx`.
2. Candidatos: `analysis.extract_candidates` aplica patrones por tipo, calcula offsets, `location_key` y `block_hash`.
3. Clasificacion: `_deterministic_field_code` asigna algunos `field_code`; `OpenAIBibliotecaClassifier` puede clasificar candidatos elegibles contra catalogo.
4. Catalogo: `_field_catalog_for_user` lee `notarial_field_catalog`; si no hay match se genera `PENDING_FIELD_*`.
5. Grupos: `review_document.build_review_groups` agrupa por `field_code + valor + categoria`.
6. Content Controls: `prepare_review_document` envuelve rangos OOXML con `w:sdt`, `w:tag` y highlight.
7. Plugin: `GetAllContentControls` reconstruye sugerencias desde tags, navega por `InternalId`, y hoy acepta/rechaza localmente en OnlyOffice.

### Medicion base

Documento sintetico usado: compradores multiples, comprador repetido, vendedores, otorgante, banco, NIT, persona juridica, tabla, runs divididos.

Resultado antes de cambios:

- candidatos detectados: 15
- candidatos clasificados/catalogados: 10
- candidatos provisionales: 5
- grupos: 13
- ocurrencias: 15
- controles envueltos: 15
- skipped por causa: `{}`

Distribucion por campo:

- `NIT`: 2 ocurrencias, mezcla entidades distintas.
- `BANCO`: 2 ocurrencias, mezcla entidad financiera repetida sin instancia juridica.
- `COMPRADOR_1`: 2 ocurrencias, comprador repetido correctamente solo por coincidencia de campo.
- `CEDULA_COMPRADOR_1`: 1 ocurrencia.
- `PENDING_FIELD_DOCUMENT_NUMBER_*`: 3 ocurrencias, documentos de comprador 2 y vendedores no asignados.
- `PENDING_FIELD_PERSON_NAME_*`: 2 ocurrencias, vendedores/persona juridica no asignados.

Fallas confirmadas:

- `field_code` funciona como identidad juridica en grupos, tags, plugin y cascada.
- Dos personas con el mismo rol no quedan aisladas por entidad.
- Una persona juridica con razon social + NIT no queda agrupada como entidad.
- Candidatos provisionales pueden llegar hasta acciones de aceptacion si el plugin no los bloquea.
- Rechazos no dejan auditoria persistida fuera de memoria/plugin.
- El panel lateral contiene el flujo principal de decision; el documento solo aporta highlight y navegacion.

### Dependencias actuales de `field_code` como identidad

- `backend/app/services/biblioteca_motor/analysis.py`
  - `_deterministic_field_code`
  - `_build_operational_suggestions`
  - `suggestion_id = hash(candidate_id + field_code)`
  - `PENDING_FIELD_*` se expone en `field_code`
- `backend/app/services/biblioteca_motor/review_document.py`
  - `build_review_groups`: `field_instance_id = field_code`
  - `group_id = hash(field_code + value + category)`
  - tag v1 incluye `field_code`
  - `cascade_field_controls_in_docx` actualiza por `FIELD_TAG_PREFIX + field_code`
- `frontend/onlyoffice-plugin/biblioteca/plugin.js`
  - `parseSuggestionTag`: `field_instance_id = parts[6]`
  - `aceptarOcurrencia`: acepta `occurrence.field_instance_id || occurrence.field_code`
  - `aplicarCascada`: agrupa por `field_instance_id` que hoy es `field_code`
  - insercion manual usa `fieldTag(codigoCampo, occurrenceId)`

### APIs OnlyOffice verificadas

Fuente oficial: https://api.onlyoffice.com/docs/plugin-and-macros/interacting-with-editors/document-api/Methods/

Capacidades soportadas relevantes:

- `AddContentControl(type, commonPr)`: crea controles block/inline/row/cell.
- `GetAllContentControls()`: lista controles con `InternalId`, `Tag`, `Alias`, texto.
- `InsertAndReplaceContentControls(arrDocuments)`: reemplaza contenido/propiedades de controles por `InternalId`.
- `RemoveContentControls([{InternalId}])`: retira controles por identificador.
- `MoveCursorToContentControl(id, isBegin)` y `SelectContentControl(id)`: navegacion/centrado por `InternalId`.
- `Asc.ButtonContentControl`: desde OnlyOffice 9.0 permite botones custom sobre Content Controls. Esta es la capacidad soportada para acciones inline `Si`, `No`, `Cambiar`.
- `Input helper`: ventana contextual ligada al cursor, util como fallback documentado para escoger otro campo, no como flujo principal.

Spike existente:

- `frontend/onlyoffice-plugin/biblioteca-spike`
- Tests automatizados: `frontend/tests/biblioteca-spike.test.mjs`
- Cubre busqueda de rango, seleccion, highlight, Content Controls, actualizacion y persistencia post-reapertura.

Linea base de pruebas:

- Backend focal con `unittest`: 32/32 OK.
- Plugin/spike con `node --test`: 26/26 OK.
- `pytest` no esta instalado en la venv local; se usa `unittest` para la suite focal actual.

## ADR

### Decision

El Motor de Biblioteca usara un modelo canonico con identidad juridica separada de `field_code`.

El backend y OOXML son la fuente de verdad:

- El backend detecta candidatos, crea entidades juridicas, asigna roles y genera `FieldInstance`.
- El DOCX de revision contiene Content Controls temporales con tags v2 que referencian `field_instance_id` y `occurrence_id`.
- Al aceptar se convierte el control temporal en control definitivo `easypro:field:v2:*`.
- Al rechazar se conserva el texto, se quita la estructura temporal y se registra la decision en snapshot/auditoria de version.
- La cascada opera exclusivamente por `field_instance_id`.

OnlyOffice sera el espacio principal de revision:

- El texto detectado se resalta en su ubicacion real.
- Los controles temporales exponen botones inline soportados por `Asc.ButtonContentControl`: `Si`, `No`, `Cambiar`.
- El panel lateral queda para estado, navegacion, busqueda, insercion manual, creacion de campos y soporte de cambio.

### Contratos canonicos

- `DetectedCandidate`: dato detectado con tipo, texto, contexto y ubicacion verificable.
- `LegalEntity`: persona natural, persona juridica o entidad financiera con nombre/documento/NIT normalizados.
- `LegalRoleAssignment`: relacion entidad-rol con cardinalidad (`COMPRADOR_1`, `COMPRADOR_2`, etc.).
- `FieldDefinition`: campo base de catalogo, no identidad de instancia.
- `FieldInstance`: instancia juridica estable; separa `base_field_code`, `visible_code`, entidad, rol y estado.
- `FieldOccurrence`: ocurrencia exacta en DOCX con hash, offset y tag.
- `ReviewSuggestion`: sugerencia revisable; puede ser definitiva o provisional.
- `ReviewDecision`: accion del protocolista con revalidacion y auditoria.

### Consecuencias

- Se elimina la arquitectura paralela donde el plugin decide con `field_code` y el backend solo prepara.
- `PENDING_FIELD_*` se mantiene como estado provisional, pero no puede aceptarse directamente.
- El catalogo puede sugerir codigos visibles, pero la cascada y persistencia no dependen de ellos.
- No hay reemplazos globales por texto; toda mutacion ocurre sobre rangos/controles OOXML identificados.

## Estado implementado

### Modelo canonico

Se agregaron contratos tipados en `backend/app/services/biblioteca_motor/contracts.py`:

- `DetectedCandidate`
- `LegalEntity`
- `LegalRoleAssignment`
- `FieldDefinition`
- `FieldInstance`
- `FieldOccurrence`
- `ReviewSuggestion`
- `ReviewDecision`

La identidad queda separada asi:

- `base_field_code`: dato juridico base, por ejemplo `NOMBRE`, `NUMERO_DOCUMENTO`, `NIT`.
- `field_instance_id`: identidad estable para cascada y persistencia.
- `visible_code`: codigo mostrado al usuario, por ejemplo `COMPRADOR_1`.
- `field_code`: campo de catalogo autorizado.
- `occurrence_id`: aparicion exacta del rango en OOXML.
- `entity_id` y `role`: entidad juridica y asignacion de rol.
- `catalog_status` y `review_status`: estado de catalogo y revision.

### Identidad juridica

`identity.py` agrupa candidatos por entidad y rol:

- nombres, cedulas, razon social, NIT y bancos se asocian por bloque/contexto y cercania;
- compradores y vendedores multiples reciben cardinalidad `COMPRADOR_1`, `COMPRADOR_2`, `VENDEDOR_1`, `VENDEDOR_2`;
- la misma entidad repetida conserva el mismo `field_instance_id`;
- personas distintas con el mismo rol quedan aisladas por `entity_id`;
- una entidad puede aparecer con varios roles sin perder su identidad de dato;
- persona juridica y NIT comparten entidad cuando aparecen vinculados;
- banco y NIT financiero se agrupan como entidad financiera.

### Tags OOXML v2

Sugerencia temporal:

```text
easypro:suggestion:v2:<analysis_id>:<suggestion_id>:<candidate_id>:<field_instance_id>:<field_code>:<visible_code>:<group_id>:<occurrence_id>:<catalog_status>
```

Campo definitivo:

```text
easypro:field:v2:<field_instance_id>:<occurrence_id>:<visible_code>:<field_code>
```

Los tags v1 ya no son el camino principal del flujo nuevo.

### Decisiones

Nuevo endpoint:

```text
POST /api/v1/biblioteca/decidir
```

Acciones:

- `accept`: revalida texto, ubicacion y hash; convierte el Content Control temporal en campo definitivo.
- `reject`: conserva texto original, quita estructura temporal y registra auditoria.
- `change`: asigna otro campo existente o crea uno nuevo, y solo despues convierte la ocurrencia.

Reglas:

- `PENDING_FIELD_*` no puede aceptarse directamente.
- si el catalogo no contiene el campo asignado, la decision falla.
- la creacion de campo dentro de `change` queda en la misma transaccion que la decision OOXML.
- si el documento cambio despues del analisis, la decision falla por revalidacion.

### Cascada

`POST /api/v1/biblioteca/actualizar-campo` aplica cambios por `field_instance_id` usando Content Controls definitivos `easypro:field:v2:*`. El plugin ya no realiza una mutacion local paralela antes del backend.

### UX OnlyOffice

- El backend envuelve el texto exacto detectado con highlight en su ubicacion real.
- El plugin registra botones inline con `Asc.ButtonContentControl`: `Si`, `No`, `Cambiar`.
- Las acciones inline reconstruyen el estado desde `GetAllContentControls`, ubican la ocurrencia por `InternalId` y delegan la decision al backend.
- El panel lateral queda como auxiliar para estado, navegacion, busqueda, insercion manual, cascada y soporte de cambio.

### Medicion posterior

Documento sintetico ampliado: compradores multiples, comprador repetido, dos vendedores, otorgantes, banco repetido, NIT financiero, persona juridica con NIT, tabla, valor y cedula catastral.

Resultado despues de implementar identidad juridica:

- candidatos detectados: 19
- candidatos clasificados/catalogados: 19
- candidatos provisionales: 0
- grupos: 15
- ocurrencias: 19
- controles envueltos: 19
- skipped por causa: `[]`

Casos cubiertos por pruebas:

- multiples compradores;
- mismo comprador repetido;
- dos personas diferentes con el mismo rol;
- persona juridica con razon social + NIT;
- banco + NIT;
- misma entidad con varios roles;
- campo fuera del catalogo;
- tablas;
- runs divididos;
- multiples controles en el mismo parrafo sin solapamiento;
- aceptacion;
- rechazo;
- cambiar campo;
- cascada por `field_instance_id`;
- documento editado despues del analisis;
- preservacion de texto/formato;
- cero reemplazos globales.

### Cobertura antes/despues

- Antes de cambios: backend focal `unittest` 32/32 OK; plugin + spike `node --test` 26/26 OK.
- Despues de cambios: backend focal 42/42 OK; backend completo 265 OK, 1 skipped; plugin 16/16 OK; spike 16/16 OK; puente auth OnlyOffice 8/8 OK.

### Validacion no ejecutada

No se valido manualmente un documento real limpio dentro de una sesion viva de OnlyOffice en este entorno: `docker compose ps` no pudo conectar con Docker Desktop porque el daemon no esta activo. La cobertura disponible queda en:

- DOCX sintetico real generado con `python-docx`, analizado y envuelto con OOXML;
- spike automatizado de capacidades OnlyOffice;
- pruebas del plugin contra `GetAllContentControls`, `MoveCursorToContentControl`, `InsertAndReplaceContentControls`, `AddContentControl` y `Asc.ButtonContentControl`;
- build frontend completo.
