# Prompt Codex — Bloque B: Gari (capa IA) sobre la escritura asistida

> Pegar en Codex. Contexto: `docs/ecosistema-notarial/plan-port-software.md`, `adr-escritura-asistida.md`. Al terminar, **un PR** contra `claude/notaria16-escritura-asistida-fsro6n`.

---

## ⚠ Antes de empezar
1. `git fetch origin` y **basa el trabajo en `claude/notaria16-escritura-asistida-fsro6n`** (trae WP-1..WP-5 + Bloque A). Backend en `backend/`, frontend en `frontend/` (NO `easypro2/`).
2. **No modifiques** el HTML congelado ni `corpus-juridico/`. **Golden tests del motor: verdes.**
3. **Frontera dura (ADR decisión 5):** Gari **asiste, no decide.** Nunca genera cláusulas obligatorias, cifras ni citas por su cuenta; todo output de Gari es **una sugerencia que el humano valida**, y las citas salen **del corpus/RAG** (Bloque A), no inventadas.

## Objetivo
Añadir la capa de IA (Gari) al flujo de escritura, en 4 capacidades, reutilizando lo existente (`backend/app/services/gari_document_service.py` ya tiene cliente OpenAI y helpers; `legal_rag.buscar_corpus` de Bloque A para grounding).

## Reglas de implementación (guardrails)
- **Temperatura 0**; **loguea** el prompt + versión del modelo en cada llamada (trazabilidad).
- Todo resultado se devuelve marcado como **`sugerencia: true`** / "por validar"; nunca se aplica solo.
- En **tests, mockea el LLM** (no llames a OpenAI real): inyecta un cliente/función fake.
- Modelo por defecto: usa el ya configurado en `gari_document_service`; **pínchalo** (versión fija) en config.

## Capacidades / endpoints (módulo `backend/app/modules/escritura/`)
1. **Extracción / prellenado** — `POST /escritura/cases/{id}/extraer` (multipart: archivo). Extrae texto (usa `unstructured`/OCR ya disponible) de una escritura registrada / certificado de tradición / cédula, y con Gari **propone valores de campos** del `CaseState` (linderos, matrícula, nombres, cédulas…). Devuelve `{ sugerencias: { campo: {valor, confianza, fuente} }, por_validar: true }`. **No** sobrescribe el caso; el frontend muestra las sugerencias para que el protocolista acepte/edite.
2. **Prosa libre** — `POST /escritura/redaccion/prosa` (body: `{acto, contexto, instruccion}`). Gari redacta el **texto de una cláusula atípica** (p. ej. una forma de pago específica) en el estilo notarial. Devuelve `{ html_sugerido, sugerencia: true }`. El editor lo inserta como bloque editable.
3. **Clasificación de acto** — `POST /escritura/clasificar` (body: `{descripcion}`). Dada una descripción en lenguaje natural del caso, Gari **sugiere** el `acto` y qué ramas/subactos activar (mapea a las dimensiones de `docs/ecosistema-notarial/mapa-situaciones.md`). Devuelve `{ acto_sugerido, ramas: [...], sugerencia: true }`.
4. **Revisor QA** — `POST /escritura/cases/{id}/revisar` (body: `{acto, html?}`). Gari lee la escritura actual (o un `.doc` viejo pegado) y **señala** cláusulas faltantes / inconsistencias / datos que no cuadran, **citando el corpus** vía `buscar_corpus`. Devuelve `{ hallazgos: [{tipo, detalle, cita_slug}], sugerencia: true }`. **No** decide procedencia — eso lo hace el motor determinista + el notario.

## Frontend
- Panel/acciones en el workspace de escritura (WP-4/WP-5) para: subir documento → ver sugerencias de prellenado (aceptar por campo); botón "Redactar con Gari" en el editor; "Clasificar caso"; "Revisar con Gari" (lista de hallazgos con su cita). Todo marcado visualmente como **sugerencia de IA — validar**.
- Cliente en `frontend/lib/api-escritura.ts` (o `api-gari.ts`).

## Criterios de aceptación
1. Los 4 endpoints responden con auth/scoping (patrón `cases`), con el LLM **inyectable** (mock en tests).
2. **Nada de Gari se aplica automáticamente**: extracción devuelve sugerencias por validar; revisor devuelve hallazgos, no bloquea (el bloqueo sigue siendo del motor/reglas server-side de Bloque A).
3. Las citas del revisor provienen de `buscar_corpus` (corpus/RAG), no del modelo.
4. **Golden tests del motor verdes**; no se rompe Captura/Redacción.
5. Trazabilidad: se registra prompt + versión de modelo por llamada.

## Pruebas
- Backend (`test_gari.py`) con LLM mockeado: extracción mapea a campos con `por_validar`; clasificación devuelve acto+ramas; revisor devuelve hallazgos con `cita_slug` provenientes de un `buscar_corpus` mockeado/real-sobre-seed.
- Frontend: un test de que el panel de sugerencias muestra "validar" y que aceptar una sugerencia actualiza el estado (sin auto-aplicar).

## Restricciones
- Reutiliza `gari_document_service`, `legal_rag`, `modules/escritura`. No dupliques.
- Un solo PR, base correcta, sin `easypro2/`. Descripción con endpoints, cómo probar (con mock), y resultados verdes.
