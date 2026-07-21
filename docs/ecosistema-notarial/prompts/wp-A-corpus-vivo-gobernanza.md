# Prompt Codex — Bloque A: Corpus vivo + RAG + gobernanza (agrupa WP-7a + WP-8 + biblioteca)

> Pegar en Codex. Contexto: `docs/ecosistema-notarial/plan-port-software.md`, `adr-escritura-asistida.md`. Al terminar, **un PR** contra `claude/notaria16-escritura-asistida-fsro6n`. Es un PR grande; sepáralo en commits por parte (A/B/C/D).

---

## ⚠ Antes de empezar
1. `git fetch origin` y **basa el trabajo en `claude/notaria16-escritura-asistida-fsro6n`** (trae WP-1..WP-5 mergeados). Backend en `backend/`, frontend en `frontend/` (NO `easypro2/`).
2. **No modifiques** el HTML congelado `docs/ecosistema-notarial/prototipos/escritura-asistida.html`.
3. **Regla dura de no-regresión:** los **golden tests del motor** (`frontend/lib/motor-escritura/__tests__/golden.test.ts`) deben seguir en verde. Todo cambio al motor debe ser **retrocompatible** (nuevos parámetros opcionales con default = comportamiento actual).

## Objetivo
Hacer que **el corpus jurídico (BD) sea la fuente de verdad viva** del cumplimiento y las tarifas, añadir **búsqueda semántica (RAG) con filtro por vigencia**, dejar el **proceso de actualización normativa** con pruebas por fecha, y cablear la **biblioteca del editor** al backend. Reutiliza lo existente (`backend/app/services/legal_corpus.py`, `modules/escritura/`, `biblioteca_motor`, el motor TS).

---

## Parte A — Validación server-side de reglas + tarifas desde el corpus
Hoy el motor TS lleva `TARIFAS` y las reglas como constantes, y la guarda de bloqueantes del `POST documento` confía en el conteo del cliente. Cámbialo así:

1. **Evaluador de reglas server-side** — `backend/app/services/escritura_reglas.py`: función `evaluar_reglas(session, acto_code, fecha, state: dict) -> list[Hallazgo]` que carga `reglas_vigentes(session, acto_code, fecha)` y evalúa cada `condicion_json` contra el `state` (data_json del caso), devolviendo hallazgos con `severidad` (BLOCK/REVIEW/WARN), mensaje y norma. Define un mini-evaluador de condiciones simple y documentado (operadores: igualdad, presencia, comparación numérica sobre campos del state).
2. **Guarda real en `POST /escritura/cases/{id}/documento`**: en vez de confiar en `cumplimiento_bloqueantes` del cliente, **recalcula** con `evaluar_reglas`; si hay algún `BLOCK`, responde **409** con la lista de bloqueantes. (Mantén compatibilidad: el body puede seguir enviando el conteo, pero **manda el server**.)
3. **Tarifas desde el corpus**: expón las tarifas vigentes (ya está `tarifas_vigentes`) y añade al motor TS un parámetro **opcional** `corpus?: { tarifas }` en `generar(acto, state, corpus?)`; si se provee, usa esas tarifas; si no, usa las constantes actuales (**golden tests intactos**). El frontend (workspace) pasa las tarifas que trae `getCorpus`.

**Aceptación A:** un caso con un dato que dispara una regla BLOCK → `POST documento` responde 409 aunque el cliente mande `cumplimiento_bloqueantes=0`. `generar` sin `corpus` produce idéntico output (golden verde).

## Parte B — RAG (búsqueda semántica con vigencia)
1. **Tabla de embeddings** — modelo `backend/app/models/legal_embedding.py` (`legal_embeddings`): `id`, `source_type` (norma|clausula), `source_id`, `chunk_text` (Text), `embedding` (`pgvector` `Vector`), `vigencia_desde`/`vigencia_hasta` (Date, copiadas de la fuente), `acto_code` (nullable). Migración Alembic (activa la extensión `vector`).
2. **Indexador** — `backend/app/services/legal_rag.py`: genera embeddings con `sentence-transformers` (modelo multilingüe ligero, p. ej. `paraphrase-multilingual-MiniLM-L12-v2`) del `texto` de las normas y del `texto` de las cláusulas; carga idempotente. CLI `python -m app.seeds.seed_embeddings`.
3. **Endpoint** `GET /escritura/corpus/buscar?q=&acto=&fecha=` → similitud vectorial **filtrada por vigencia a la fecha** (`vigencia_desde<=fecha<=vigencia_hasta|null`); devuelve los top-k con su fuente (slug/cita) y score. **Nunca** devuelve normas no vigentes a esa fecha.

**Aceptación B:** buscar "afectación a vivienda familiar" con fecha 2026 devuelve la Ley 258; una consulta con una fecha anterior a la vigencia de una norma **no** la devuelve; los embeddings se regeneran sin duplicar.

## Parte C — Gobernanza normativa + pruebas por fecha
1. **Servicio de cambio normativo** — `backend/app/services/legal_gobernanza.py`: `registrar_cambio(session, ...)` que, al modificar/derogar una norma, **no borra**: cierra `vigencia_hasta` de la versión anterior, inserta la nueva versión (o marca estado), crea la `legal_norma_relacion` correspondiente y **re-indexa** los embeddings afectados. Documenta el flujo detectar→registrar→impacto→re-indexar.
2. **Análisis de impacto**: función `impacto_de_norma(session, norma_id)` que lista cláusulas y reglas que la referencian (para saber qué revisar).
3. **Pruebas por fecha** — `backend/app/tests/test_gobernanza.py`: una norma con `vigencia_hasta` pasada NO aplica a una escritura con fecha posterior; una regla nueva (vigencia_desde) NO aplica a una escritura con fecha anterior; tras `registrar_cambio`, las escrituras con fecha vieja siguen usando la regla vieja y las nuevas la nueva.

**Aceptación C:** las pruebas por fecha pasan; `registrar_cambio` versiona sin romper consultas históricas.

## Parte D — Biblioteca del editor desde el backend
1. **Endpoint** `GET /escritura/biblioteca?acto=&fecha=` → cláusulas insertables del acto (desde `legal_clausulas` vigentes o `biblioteca_motor`), con `titulo`, `texto` (con slots) y `capa`.
2. **Frontend**: la biblioteca del editor (`escritura-redaccion-biblioteca.ts` / editor de WP-5) consume ese endpoint en vez de la lista hardcodeada (deja la lista portada como fallback si la API falla).

**Aceptación D:** el editor lista las cláusulas del acto activo desde la API; insertar una funciona igual que antes.

---

## Restricciones globales
- **Golden tests del motor: verdes** (cambios al motor retrocompatibles).
- Reutiliza `legal_corpus`, `modules/escritura`, `biblioteca_motor`, `document_persistence`; no dupliques.
- No toques el HTML congelado. Sin `easypro2/`. Base correcta.
- **Pruebas** por cada parte (A/B/C/D). Descripción del PR con: qué hace cada parte, cómo correr seeds/tests, y resultados en verde.
- Si algo excede lo razonable para un PR, díselo en la descripción y deja un TODO claro, pero no rompas nada existente.
