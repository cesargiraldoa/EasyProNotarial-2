# Plan de port al software — Escritura asistida (Fase 1)

> **Objetivo.** Adoptar y adaptar el prototipo `prototipos/escritura-asistida.html` (spec congelada) al software real —frontend Next.js + backend FastAPI + BD Postgres— **reutilizando** lo que ya existe, sin reprocesar. Luego sembrar el corpus real con lo que ya tenemos en el HTML.
>
> **Modelo de trabajo.** Codea **Codex**. Los **prompts se co-crean** (usuario + asistente). El asistente **revisa en GitHub** (PR por paquete de trabajo). Cada paquete de trabajo (WP) de este plan es la base de un prompt de Codex y de la lista de revisión del PR.
>
> _Creado: 2026-07-21. Rama de trabajo: `claude/notaria16-escritura-asistida-fsro6n`._

---

## 1. Decisiones fijadas

1. **Editor propio**, portado del HTML (contenteditable + vincular + comentarios + resaltado + control de cambios). **No OnlyOffice** para este flujo.
2. **Motor determinista en TypeScript compartido** (`frontend/lib/motor-escritura/`), portado casi 1:1 del JS del HTML. Corre en el cliente para el preview en vivo y en el editor. La generación final de DOCX la hace el backend a partir del HTML que produce el motor.
3. **Reutilizar la capa de caso existente** (`Case`, `CaseAct`, `CaseActData`, `CaseParticipant`, `ActCatalog`, servicio `biblioteca_motor`, `document_generation`, `gari_document_service`). NO crear modelos nuevos para persistir el caso.
4. **Lo nuevo** es solo: el **corpus jurídico** (normograma/reglas/tarifas/jurisprudencia con vigencia), el **motor-escritura** (TS) y el **editor propio** (React). Más el workspace de UI.
5. **La normatividad es dato versionado** (fuente de verdad en Git → BD), no código ni pesos del LLM. La IA (Gari) asiste; el motor determinista manda; el notario decide.

## 2. Stack real (confirmado)

- **Frontend:** Next.js 15 (App Router), React 19, TailwindCSS, lucide-react. (Sin dependencia de OnlyOffice para este flujo.)
- **Backend:** FastAPI 0.115, SQLAlchemy 2.0, Alembic, Postgres (psycopg2), JWT (python-jose). Ya presentes: `python-docx` (DOCX), `num2words`, `openai`, `langgraph`, `pgvector`, `sentence-transformers`, `celery`+`redis`, `unstructured[docx]`, `supabase`.
- **BD:** Postgres + `pgvector` (RAG). Migraciones con Alembic.

## 3. Mapa de reutilización (HTML → software)

| Pieza del HTML | Qué es | Dónde vive | Reutiliza |
|---|---|---|---|
| `NORMAS`, `TARIFAS`, `BIBLIO`, `normograma` verificado | Datos | Corpus (Git JSON → tablas nuevas) | — (nuevo, pero sembrado del HTML) |
| `renderEscritura`, `renderCancelacion`, `evaluar`, `liquidar`, `enLetras`, `money`, `genEnding`, `fillLeaders` | Motor determinista (funciones puras) | `frontend/lib/motor-escritura/` (TS) | **Port 1:1 del JS** |
| `G()`, `Gc()` | Estado del caso | `case_act_data.data_json` | **Modelo existente** |
| Vendedores/compradores/apoderado | Partes | `case_participants` | **Modelo existente** |
| Acto + encadenamiento | Tipo de acto | `act_catalog` + `case_acts` | **Modelo existente** |
| Biblioteca de cláusulas | Cláusulas insertables | servicio `biblioteca_motor` | **Servicio existente** |
| Editor (vincular/comentarios/resaltado/control de cambios) | Editor | `frontend/components/escritura/editor/` (React) | **Port del HTML** |
| Salida HTML de la escritura | Documento | `case_document` + `case_document_version`; DOCX vía `python-docx` | **Modelo/servicio existentes** |
| Borrador de estilo (futuro) | Gari | `case_act_data.gari_draft_text` + `gari_document_service` | **Campo/servicio existentes** |

## 4. Modelo de datos

### 4.1 Se REUSA (no se toca su esencia)
- **`Case`** — el caso (act_type, consecutive/year, official_deed_number, current_state, metadata_json).
- **`CaseAct`** — actos del caso (act_code, act_label, act_order) → soporta encadenamiento.
- **`CaseActData`** — `data_json` (estado del formulario = `G()`/`Gc()`), `gari_draft_text`.
- **`CaseParticipant`** — person/legal_entity + role_code + snapshot_json (las partes).
- **`ActCatalog`** — catálogo de actos (code, label, roles_json).

### 4.2 Se CREA — corpus jurídico (tablas nuevas, con vigencia temporal)
- **`legal_norma`** — tipo, número, año, **artículo**, autoridad, `estado` (vigente/modificada/derogada_parcial/derogada_total/inexequible/suspendida), `vigencia_formal`, `aplicabilidad_operativa`, `vigencia_desde`, `vigencia_hasta`, `url_oficial`, `confianza`, `fecha_verificacion`.
- **`legal_norma_relacion`** — `norma_origen_id` → `norma_destino_id`, `tipo` (modifica/deroga/compila/desarrolla), `articulo_afectado`, `fecha_efecto`.
- **`legal_clausula`** — texto/plantilla con slots, `capa` (por_ley/estilo), `norma_id`, actos, `notaria_id` (para la capa por notaría), vigencia.
- **`legal_regla`** — condición (JSON) → efecto, `severidad` (BLOCK/REVIEW/WARN), `norma_id`, vigencia.
- **`legal_tarifa`** — año, concepto, valor/fórmula, norma (Resolución SNR), vigencia.
- **`legal_jurisprudencia`** — providencia, regla operacional, `norma_relacionada_id`, url, fecha.
- Índice **`pgvector`** derivado del corpus para el RAG (con metadata de vigencia para filtrar por fecha).

> Regla dura: **nunca se borra, se versiona**; vigencia **artículo por artículo**; toda consulta del motor filtra por **fecha de otorgamiento** del acto.

## 5. Paquetes de trabajo (WP) — cada uno = un prompt para Codex + un PR a revisar

> Convención: cada WP produce **un PR** contra `claude/notaria16-escritura-asistida-fsro6n` (o rama hija), con **pruebas** y sin romper lo existente. El asistente revisa el PR antes de merge.

### WP-0 — ADR + esqueleto (lo hace el asistente, no Codex) — ✅ HECHO
- **Objetivo:** decisión de arquitectura registrada (ADR) + esqueleto de carpetas (`frontend/lib/motor-escritura/`, `corpus-juridico/`, módulo backend `escritura`).
- **Entregable:** `docs/ecosistema-notarial/adr-escritura-asistida.md` + carpetas vacías con README.
- **Aceptación:** ADR aprobado por el usuario.

### WP-1 — Corpus: esquema + siembra desde el HTML — ✅ HECHO (PR #133, merge `59fd981`)
- Tablas `legal_*` con vigencia temporal + doble estado, migración Alembic, corpus JSON en `corpus-juridico/`, seed idempotente, helper `normas_vigentes(acto, fecha)`. Revisado (C1–C5 correctas, tarifas 2026 exactas, jurisprudencia, 67 normas). Follow-up menor: sumar C-192/1998, C-107/2017, C-022/2021 y cerrar los 7 NO CONFIRMADO.
- **Objetivo:** tablas del corpus (§4.2) + seed inicial extraído del HTML (`NORMAS`, `TARIFAS`, `BIBLIO`) y del `normograma`/`verificacion-fuentes` verificados.
- **Archivos:** migración Alembic `backend/alembic/versions/xxx_corpus_juridico.py`; modelos `backend/app/models/legal_*.py`; datos `corpus-juridico/*.json`; seed `backend/app/seeds/seed_corpus.py`.
- **Aceptación:** `alembic upgrade head` ok; seed carga; consulta "normas/tarifas vigentes a fecha X para acto=compraventa" devuelve lo esperado; las 5 correcciones de `verificacion-fuentes` (C1–C5) quedan reflejadas en el dato.
- **Pruebas:** test de consulta por fecha (vigencia) + test de una regla bloqueante.

### WP-2 — Motor-escritura (TS) + golden tests — ✅ HECHO (PR #134, merge `9e52677`)
- Motor puro TS en `frontend/lib/motor-escritura/index.ts` (port 1:1 del HTML), golden tests en igualdad exacta contra los fixtures + unit tests (8/8 verde, verificado ejecutando). `TARIFAS`/citas como constantes portadas (cableado al corpus = follow-up).
- **Objetivo:** portar las funciones puras del HTML a `frontend/lib/motor-escritura/` (TypeScript, tipado), recibiendo el **corpus como input** (no hardcode).
- **Archivos:** `motor-escritura/{numeros,genero,render,evaluar,liquidar,leaders,index}.ts` + tipos.
- **Aceptación:** **golden tests** — para compraventa, compraventa+hipoteca y cancelación, dado el mismo caso, la salida coincide con la del HTML congelado (fixtures capturados del HTML).
- **Pruebas:** snapshots de los 3 actos + tests unitarios de `enLetras`/`money`/`genEnding`.

### WP-3 — Backend: API de escritura
- **Objetivo:** endpoints que unen corpus + caso + generación, sobre los modelos existentes.
- **Endpoints:** `GET /escritura/corpus?acto=&fecha=`; `GET/PUT /cases/{id}/escritura` (lee/escribe `case_act_data.data_json` + `case_participants`); `POST /cases/{id}/escritura/documento` (HTML→DOCX con `python-docx`).
- **Aceptación:** OpenAPI + tests; guarda y recupera el estado; genera DOCX de compraventa.
- **Pruebas:** round-trip de `data_json`; snapshot del DOCX.

### WP-4 — Frontend: formulario + Captura (preview en vivo)
- **Objetivo:** portar el formulario dinámico (fieldsets, cascada, miles/centavos, género) a React/Tailwind; modo **Captura** con preview en vivo usando `motor-escritura`; paneles de **cumplimiento** y **liquidación**.
- **Archivos:** `frontend/components/escritura/` + ruta `app/(app)/dashboard/casos/[id]/escritura/`.
- **Aceptación:** compraventa capturable; el documento y la liquidación coinciden con el HTML; sin bloqueantes = listo.
- **Pruebas:** e2e básico (Playwright) del preview.

### WP-5 — Frontend: editor propio (el diferenciador)
- **Objetivo:** portar el editor del HTML: contenteditable, **vincular/desvincular** (cascada posicional), **comentarios estilo Word** (anclados + resolver), **resaltado multicolor**, **control de cambios** (verde/rojo + aceptar/rechazar), **biblioteca insertable** (desde `biblioteca_motor`), **guiones de relleno**, **exportar PDF/Word**.
- **Archivos:** `frontend/components/escritura/editor/`.
- **Aceptación:** paridad de comportamiento con el editor del HTML (checklist por función).
- **Pruebas:** e2e de vincular + comentar + control de cambios.

### WP-6 — Actos 2 y 3 (hipoteca, cancelación)
- **Objetivo:** activar compraventa+hipoteca y cancelación de hipoteca (el motor y el corpus ya los soportan) → tarjetas en el lanzador + seed de su corpus.
- **Aceptación:** los 3 actos generan escritura correcta end-to-end.

### WP-7 — Gari + RAG
- **Objetivo:** RAG (`pgvector` + `sentence-transformers`) sobre el corpus con **filtrado por vigencia**; Gari (openai + langgraph) en extracción (prellenar campos), prosa libre, clasificación de acto y revisor QA — con validación humana y cita al corpus.
- **Aceptación:** Gari sugiere, nunca decide; toda sugerencia trazable y validable; el motor sigue mandando en esqueleto/liquidación/citas.

### WP-8 — Gobernanza + pruebas por fecha
- **Objetivo:** proceso de actualización normativa (detectar → PR → análisis de impacto norma→cláusula→regla → re-indexar RAG → versionar regla) + suite de pruebas de procedencia/no-procedencia **por fecha de otorgamiento**.
- **Aceptación:** cambiar una norma de prueba versiona sin romper escrituras anteriores; el RAG no recupera derogadas para una fecha dada.

## 6. El editor propio — funciones a portar del HTML (checklist WP-5)

- [ ] Contenteditable con dos modos: **Captura** (genera en vivo) ↔ **Redacción** (edita a mano).
- [ ] **Vincular/desvincular** selección como campo; edición cascadea a todas las apariciones (sync posicional).
- [ ] **Comentarios** anclados a la selección (panel lateral, resolver/eliminar).
- [ ] **Resaltado multicolor** (5 colores + quitar).
- [ ] **Control de cambios** (inserción verde / borrado rojo, aceptar/rechazar todo).
- [ ] **Biblioteca** insertable en el cursor (por acto, desde `biblioteca_motor`).
- [ ] **Guiones de relleno** (line-leaders) que se colapsan en edición y se materializan en PDF.
- [ ] **Exportar PDF** (print A4) y **Word** (.docx vía backend).
- [ ] Preservar la selección en la toolbar (mousedown→preventDefault).

## 7. Flujo Codex ↔ revisión

1. Usuario + asistente **co-crean el prompt** del WP (a partir de su ficha de arriba).
2. Codex abre **un PR** por WP contra la rama de trabajo.
3. El asistente **revisa el PR en GitHub**: criterios de aceptación, pruebas, no-regresión, y coherencia con la spec (el HTML) y el corpus.
4. Correcciones → nuevo prompt/commit. **Merge** cuando pasa la compuerta.
5. Se actualiza este plan (marca el WP como hecho) y `estado-y-proximos-pasos.md`.

## 8. Secuencia sugerida (sprints)

- **Sprint 1:** WP-0 + WP-1 + WP-2 → corpus sembrado + motor TS con golden tests (base reutilizable y probada, sin UI).
- **Sprint 2:** WP-3 + WP-4 → compraventa punta a punta por el software (API + Captura).
- **Sprint 3:** WP-5 → editor propio.
- **Sprint 4:** WP-6 → hipoteca y cancelación (casi gratis).
- **Sprint 5:** WP-7 → Gari + RAG.
- **Sprint 6:** WP-8 → gobernanza + pruebas por fecha.

## 9. Estado

- ✅ **WP-0** — ADR (`adr-escritura-asistida.md`).
- ✅ **WP-1** — Corpus jurídico (PR #133, `59fd981`).
- ✅ **WP-2** — Motor-escritura TS + golden tests (PR #134, `9e52677`; 8/8 verde).
- ✅ **WP-3** — API backend de escritura (PR #135, `2bdf55c`; 6 tests verde).
- ✅ **WP-4** — UI de Captura (PR #136, `bd8bf38`).
- ✅ **WP-5** — Editor propio / Redacción (PR #137, `1c573d2`; 12 tests verde). Escritura asistida completa (captura+redacción) para los 3 actos.

### Trabajo restante — agrupado en bloques
- ⏳ **Bloque A** — Corpus vivo + RAG + gobernanza + biblioteca API (agrupa WP-7a + WP-8 + biblioteca). Prompt: `prompts/wp-A-corpus-vivo-gobernanza.md`. Listo para Codex.
- ⏳ **Bloque B** — Gari (capa IA: extracción, prosa libre, clasificación, QA). Prompt pendiente.
- ⏳ **Bloque C/D** — Compraventa de TODO TIPO por lotes (varios inmuebles+folio+encadenamientos; extranjero/divisas+rural+capacidad). Prompts pendientes.
- Follow-up de datos: aplicar el JSON de GPT (enlaces/confianza) al corpus.

Siguiente: pegar `prompts/wp-A-corpus-vivo-gobernanza.md` en Codex → PR → revisión.
