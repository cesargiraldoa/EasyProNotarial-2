# Prompt Codex — WP-3: API backend de Escritura asistida

> Pegar en Codex. Contexto: `docs/ecosistema-notarial/plan-port-software.md` y `adr-escritura-asistida.md`. Al terminar, **un PR** contra `claude/notaria16-escritura-asistida-fsro6n`.

---

## ⚠ Antes de empezar
1. `git fetch origin` y **basa el trabajo en `claude/notaria16-escritura-asistida-fsro6n`** (trae WP-1 corpus + WP-2 motor mergeados). Backend en **`backend/`** en la raíz (NO `easypro2/`).
2. **Reutiliza lo existente. NO reinventes** modelos ni servicios de documentos.

## Rol y objetivo
Eres ingeniero backend senior (FastAPI + SQLAlchemy 2.0). Crea el módulo `backend/app/modules/escritura/` que expone la API del flujo de escritura asistida, uniendo el **corpus** (WP-1), el **caso** (modelos existentes) y la **generación/persistencia de documentos** (servicios existentes). El render de la escritura lo produce el **motor TS del cliente** (WP-2); el backend NO re-implementa el render.

## Piezas existentes a REUTILIZAR (no crear equivalentes)
- **Corpus (WP-1):** `backend/app/services/legal_corpus.py` → `normas_vigentes(session, acto_code, fecha)` y equivalentes para cláusulas/reglas/tarifas.
- **Caso:** modelos `Case`, `CaseActData` (`data_json`, `gari_draft_text`), `CaseParticipant`, `CaseAct`, `ActCatalog`.
- **Documentos:** `backend/app/services/document_persistence.py` → `get_or_create_document(db, case, category, title)` y `persist_case_document_version(...)`. `backend/app/services/document_generation.py` → `generate_plain_pdf`, `convert_docx_to_pdf`, `recalculate_dash_fills`. `backend/app/services/gari_document_service.py` → `build_gari_docx_buffer(text)` (texto → DOCX).
- **Auth y acceso a caso:** replica las dependencias de `backend/app/modules/cases/router.py` (usuario actual, scoping por notaría, `HTTPException` 404/403). No inventes auth nueva.

## Endpoints (router con `prefix="/escritura"`, registrado en la app)
1. **`GET /escritura/corpus`** — query `acto` (compraventa|hipoteca|cancelacion) y `fecha` (ISO, opcional → hoy). Devuelve `{ normas, clausulas, reglas, tarifas }` **vigentes a esa fecha** para el acto, usando `legal_corpus`.
2. **`GET /escritura/cases/{case_id}`** — devuelve el estado del formulario: `CaseActData.data_json` parseado (el `CaseState` del motor) + metadatos del caso. 404 si no existe; 403 si el usuario no tiene acceso.
3. **`PUT /escritura/cases/{case_id}`** — body: `{ acto, state }` (el `CaseState`). Persiste `state` en `CaseActData.data_json` (crea la fila si no existe, upsert por `case_id`). Devuelve el estado guardado. _(La proyección a `CaseParticipant` queda como follow-up; por ahora el `data_json` es la fuente para el motor.)_
4. **`POST /escritura/cases/{case_id}/documento`** — body: `{ acto, html, filename?, cumplimiento_bloqueantes }`. `html` es la escritura que emite el motor TS del cliente.
   - **Guarda de cumplimiento:** si `cumplimiento_bloqueantes > 0`, responde `409` con mensaje "hay bloqueantes por resolver" y NO genera. _(La validación server-side completa contra `legal_reglas` BLOCK es follow-up de un WP posterior.)_
   - Convierte `html` → texto estructurado (quita tags/`.fill`/`.cite` como en el `normalize` del motor, respetando saltos por bloque) → DOCX con `build_gari_docx_buffer` (o `python-docx`), preservando negritas de los títulos `.clh` si es viable.
   - Persiste con `get_or_create_document(category="escritura", title=...)` + `persist_case_document_version(file_format="docx", ...)`. Opcional: generar PDF con `convert_docx_to_pdf`.
   - Devuelve `{ version_number, file_format, storage_path, download_url? }`.

## Schemas
`backend/app/schemas/escritura.py` con Pydantic v2: `CorpusResponse`, `EscrituraStateIn/Out`, `DocumentoIn`, `DocumentoOut`. `state` puede tiparse laxo (`dict`) porque el `CaseState` lo valida el motor; documenta la forma.

## Criterios de aceptación
1. Los 4 endpoints responden con auth y scoping por caso (mirando `cases/router.py`).
2. `GET /escritura/corpus?acto=compraventa&fecha=2026-08-14` devuelve el núcleo vigente (sin inexequibles/derogadas para esa fecha).
3. `PUT` luego `GET` de `/escritura/cases/{id}` hace round-trip del `data_json` sin pérdida.
4. `POST …/documento` con `cumplimiento_bloqueantes=0` crea una `CaseDocumentVersion` (docx) y devuelve su número de versión; con `>0` responde 409 sin crear versión.
5. No se modifican modelos existentes ni el motor TS ni el corpus.

## Pruebas — `backend/app/tests/test_escritura_api.py`
- Corpus por fecha (incluye exclusión de una norma inexequible).
- Round-trip de `PUT`/`GET` del estado.
- `POST documento`: caso feliz (crea versión) y caso 409 (bloqueantes).
- Auth: 404/403 en caso inexistente o sin acceso.

## Restricciones
- Reutiliza servicios/modelos existentes; no dupliques generación ni persistencia.
- Un solo PR, base correcta (`claude/notaria16-escritura-asistida-fsro6n`), rutas en `backend/`.
- Descripción del PR: endpoints, cómo probar, resultado de las pruebas (verde).
