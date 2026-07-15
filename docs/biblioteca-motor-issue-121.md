# Motor de Biblioteca issue 121 - diagnostico y ADR

Fecha: 2026-07-15
Rama: `biblioteca-motor-issue-121`
PR: https://github.com/cesargiraldoa/EasyProNotarial-2/pull/123
Issue fuente: https://github.com/cesargiraldoa/EasyProNotarial-2/issues/121

## Diagnostico

### Pipeline anterior

El flujo previo mezclaba dos responsabilidades incompatibles:

1. Lectura DOCX y ubicaciones aproximadas en `analysis.py`.
2. Deteccion semantica con patrones, reglas deterministicas y candidatos preseleccionados.
3. Clasificacion opcional contra catalogo despues de la deteccion.
4. Identidad basada en `field_code`, valor y cercania local.
5. Content Controls temporales en OOXML.
6. Plugin OnlyOffice con revision lateral y mutaciones locales parciales.

Problemas confirmados:

- `field_code` funcionaba como identidad juridica en agrupacion, tags, cascada y plugin.
- Personas diferentes con el mismo rol podian colisionar.
- Una misma entidad con varios roles no quedaba modelada explicitamente.
- Razon social, documento y NIT no quedaban agrupados por entidad juridica de forma confiable.
- Los `PENDING_FIELD_*` podian avanzar demasiado cerca de la aceptacion.
- Rechazos y cambios no generaban senales persistentes para aprendizaje.
- El panel lateral concentraba decisiones que deben ocurrir en el documento.
- El detector semantico era incremental: regex/cercania primero, LLM despues.

### Camino removido del flujo productivo

Se elimino del Motor de Biblioteca productivo:

- `PATTERNS` como detector principal.
- `extract_candidates` basado en regex.
- `_deterministic_field_code`.
- `OpenAIBibliotecaClassifier` con candidatos preseleccionados.
- `build_identity_model` por cercania.
- `_nearest_name`, `_nearest_document` y `_role_from_candidate`.
- El endpoint legacy `/biblioteca/analizar` quedo como `410 Gone`; no invoca detector ni transforma candidatos.

El modulo `backend/app/services/biblioteca_motor/identity.py` fue eliminado. El motor no conserva fallback silencioso: si no hay extractor LLM configurado, el analisis falla sin modificar el DOCX.

## ADR

### Decision

El Motor de Biblioteca queda como arquitectura LLM-first con backend y OOXML como fuente de verdad:

```text
DOCX versionado
-> DocumentMap
-> LLM Extractor
-> Anchor Resolver
-> Field Instance Resolver
-> Content Controls OOXML v2
-> OnlyOffice
-> decision humana
-> nueva version
-> field_signals
-> perfil de notaria
```

OnlyOffice sigue siendo el editor y la superficie principal de revision. El panel lateral es auxiliar para navegacion, progreso, seleccion de campo y creacion de campos.

### Responsabilidades

- `document_map.py`: construye un mapa ordenado de parrafos y parrafos dentro de celdas. No hace deteccion semantica.
- `llm_extractor.py`: llama al proveedor LLM con salida JSON estricta y valida modelos tipados.
- `anchor_resolver.py`: verifica `block_id`, texto exacto, ocurrencia, contexto, hashes, offsets y solapamientos.
- `field_instance_service.py`: genera identidad juridica estable desde entidades, roles y ocurrencias LLM.
- `field_signal_service.py`: registra senales anonimizadas por decision humana.
- `notary_prompt_service.py`: compila perfiles versionados por notaria y recupera ejemplos relevantes.
- `review_document.py`: modifica OOXML v2, valida texto actual, aplica decisiones y cascada por `field_instance_id`.

### Contratos

Contratos canonicos existentes en `contracts.py`:

- `DetectedCandidate`
- `LegalEntity`
- `LegalRoleAssignment`
- `FieldDefinition`
- `FieldInstance`
- `FieldOccurrence`
- `ReviewSuggestion`
- `ReviewDecision`

Contratos LLM estrictos en `llm_extractor.py`:

- `LLMEntity`
- `LLMRole`
- `LLMFieldInstance`
- `LLMOccurrence`
- `LLMUnmappedField`
- `LLMExtraction`
- `LLMExtractionAudit`
- `LLMExtractionResult`

La salida LLM debe contener `document_type`, `entities`, `roles`, `field_instances`, `occurrences`, `unmapped_fields`, `confidence`, `reason` y `diagnostics`.

Cada ocurrencia debe incluir `block_id`, `exact_text`, `occurrence_index`, `left_context` y `right_context`. El LLM no devuelve offsets confiables y nunca modifica documentos.

### Identidad

Se separan conceptos que antes estaban mezclados:

- `base_field_code`: dato juridico base, por ejemplo `NOMBRE`, `NIT`, `NUMERO_DOCUMENTO`.
- `field_code`: codigo de catalogo autorizado.
- `visible_code`: codigo visible para revision, por ejemplo `COMPRADOR_1`.
- `field_instance_id`: identidad juridica estable para cascada y persistencia.
- `occurrence_id`: aparicion exacta en el DOCX.
- `entity_id`: entidad juridica generada por backend.
- `role_assignment_id`: asignacion entidad-rol con ordinal por rol.
- `catalog_status` y `review_status`: estado de catalogo y revision.

`field_instance_id` nunca se deriva solamente de `field_code`; incluye entidad, rol, tipo de candidato, base y referencia LLM. Cambiar un campo resuelve una instancia destino existente o crea una nueva, sin reutilizar automaticamente la instancia anterior.

### Campos provisionales

Los datos utiles fuera del catalogo se conservan como sugerencias con `catalog_status = unmapped` y `PENDING_FIELD_*`.

Reglas:

- No se pueden aceptar directamente.
- Se pueden cambiar a campo existente.
- Se puede crear un nuevo campo con `code`, `label`, `category` y `field_type`.
- Solo despues de asignar o crear campo se convierte en `FieldInstance` definitiva.

### OnlyOffice

Se mantiene Content Controls OOXML v2.

Sugerencia temporal:

```text
easypro:suggestion:v2:<analysis_id>:<suggestion_id>:<candidate_id>:<field_instance_id>:<field_code>:<visible_code>:<group_id>:<occurrence_id>:<catalog_status>
```

Campo definitivo:

```text
easypro:field:v2:<field_instance_id>:<occurrence_id>:<visible_code>:<field_code>
```

El plugin valida `Asc.ButtonContentControl` como capability gate real. Si no esta disponible, bloquea decisiones y muestra incompatibilidad. No degrada silenciosamente al panel lateral.

Se elimino `window.prompt`. `Cambiar` abre un selector auxiliar de campo existente o formulario de creacion de campo; el backend recibe `new_field` y aplica la decision en una transaccion.

Para decisiones secuenciales en un mismo parrafo, el backend usa version actual, `suggestion_tag`, `occurrence_id` y texto actual del Content Control. Si los offsets/hash del bloque original ya no coinciden por una decision previa, se permite aplicar sobre el Content Control vigente solo si su texto coincide exactamente.

### Datos y migracion

Migracion Alembic:

```text
backend/alembic/versions/20260715_add_biblioteca_learning.py
```

Tablas:

- `biblioteca_analysis_runs`: notaria, caso/documento/versiones, hash documental, modelo, prompt/profile version, estado, tokens, latencia, costo, detectados, anclados, skipped, errores y diagnosticos.
- `field_signals`: notaria, analysis run, documento/versiones, tipo documental, seccion, entidad, rol, tipo de candidato, contexto anonimizado, hash de texto exacto, sugerencia LLM segura, decision humana, campo final, instancia final, usuario, modelo y versiones.
- `notary_prompt_profiles`: version por notaria, estado, reglas compiladas, alias, patrones positivos/negativos, preferencias de campos, conteo e ultimo id de senales fuente, fechas de generacion y activacion.

Las decisiones registradas son `accepted`, `rejected`, `changed` y `created_field`.

### Aprendizaje por notaria

Cada decision inserta `field_signal` en la misma transaccion que crea la nueva version documental. Si falla la persistencia, hay rollback completo.

El compilador:

- agrega patrones repetidos;
- prioriza frecuencia y recencia mediante senales recuperadas;
- ignora senales aisladas con umbral minimo;
- anonimiza contexto;
- genera reglas, alias, patrones positivos, patrones negativos y preferencias;
- versiona perfiles;
- mantiene un solo perfil activo por notaria.

Antes de analizar se carga el perfil activo y se recuperan ejemplos historicos relevantes. El retrieval esta acotado y ordena por misma notaria, tipo documental, seccion, rol, tipo de campo, frecuencia/score y recencia. No se envia toda la tabla `field_signals`.

### Privacidad y seguridad

- No se registran documentos completos en logs.
- `field_signals` no guarda nombres, cedulas o NIT en texto plano.
- El texto exacto se persiste solo como SHA-256.
- El contexto se anonimiza antes de persistir.
- La salida LLM se valida con modelos Pydantic `extra="forbid"`.
- Los codigos de catalogo se verifican.
- `PENDING_FIELD_*` no se acepta directamente.
- Las mutaciones OOXML son por Content Control/rango verificado, no por reemplazo global de texto.
- La cascada opera solo por `field_instance_id`.

### Costos

`biblioteca_analysis_runs` guarda tokens de entrada/salida, latencia y costo si el proveedor lo expone. El ADR no fija costo unitario porque depende del modelo configurado y de tarifas externas. El prompt actual usa version `biblioteca-llm-v1`.

### Metricas

DOCX sintetico:

- candidatos detectados: 6
- candidatos clasificados/catalogados: 5
- candidatos provisionales: 1
- grupos: 5
- ocurrencias: 6
- controles envueltos: 6
- skipped por causa: `{}`
- anchor success aplicado: 1.0

Corpus privado/anonimizado con fixtures LLM:

- casos: 3
- textos utiles esperados: 18
- textos encontrados: 18
- sugerencias inesperadas: 0
- sugerencias provisionales: 1
- skips: 0
- controles envueltos: 18
- recall: 1.0
- precision: 1.0
- anchor success aplicado: 1.0
- `PENDING_FIELD` aceptados: 0

El corpus cubre compraventa simple, compraventa con hipoteca, propiedad horizontal, personas naturales, personas juridicas, patrimonio autonomo, fiduciaria, bancos, apoderados, multiples compradores, multiples vendedores, misma entidad con varios roles, tablas, multiples campos en el mismo parrafo, campos fuera del catalogo y referencias legales que deben rechazarse.

### Validacion ejecutada

- Migraciones: `alembic upgrade head`, `alembic downgrade 20260714_add_notarial_field_catalog`, `alembic upgrade head`.
- `py_compile`: OK en modulos modificados.
- Backend focal: 23 tests OK.
- Backend completo: 246 tests OK, 1 skipped.
- Integracion LLM con fixtures/mocks: incluida en backend focal y completo.
- Plugin + spike OnlyOffice: 35 tests OK.
- Auth bridge OnlyOffice: 8 tests OK.
- Frontend build: `npm.cmd run build` OK.
- `git diff --check`: OK, con advertencias normales de CRLF.
- DOCX sintetico: OK, OOXML envuelto sin perdida de texto visible.
- Corpus anonimizado: recall 1.0, precision 1.0.
- Versionado y reapertura: cubierto por snapshot/backend y pruebas de persistencia OOXML automatizadas.

### Validacion no ejecutada

No se ejecuto una prueba manual en un OnlyOffice productivo vivo desde este entorno. `docker compose ps` no pudo conectar con Docker Desktop:

```text
failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine
```

La prueba manual debe ejecutarse en el entorno productivo/staging de OnlyOffice con Docker disponible.

### Rollback

1. Revertir el commit del PR antes de merge si la validacion manual falla.
2. Si la migracion fue aplicada en un entorno de prueba, ejecutar:

```text
alembic downgrade 20260714_add_notarial_field_catalog
```

3. No hay despliegue ni merge desde este PR. La ruta legacy `/biblioteca/analizar` permanece deshabilitada con `410 Gone`; el flujo soportado es `analizar-actual` y `analizar-y-preparar`.
