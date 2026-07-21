# ADR — Escritura asistida (port del HTML al software)

> Architecture Decision Record. Registra las decisiones de arquitectura del flujo "Escritura asistida" antes de codear. Estado: **aceptado** (2026-07-21).

## Contexto
El prototipo `prototipos/escritura-asistida.html` (spec congelada) implementa, funcionando y verificado, un motor determinista de redacción de escrituras (compraventa, compraventa+hipoteca, cancelación de hipoteca) con captura, edición, cumplimiento y liquidación. Se porta al software (Next.js + FastAPI + Postgres) reutilizando lo existente, sin reprocesar. Codea Codex; los prompts se co-crean; el asistente revisa en GitHub.

## Decisiones

1. **Editor propio, no OnlyOffice, para este flujo.** El editor (contenteditable con vincular/comentarios/resaltado/control de cambios) se porta del HTML a React. OnlyOffice sigue para otros flujos, pero la escritura asistida usa editor propio (es el diferenciador y ya está resuelto en el HTML).

2. **Motor determinista en TypeScript compartido** (`frontend/lib/motor-escritura/`), portado ~1:1 del JS del HTML. Corre en el cliente para el preview en vivo y en el editor. La **generación final de DOCX** la hace el backend a partir del HTML que emite el motor (`python-docx`). Un solo motor; no se reescribe en Python.

3. **Reutilizar la capa de caso existente.** El estado del formulario → `case_act_data.data_json`; las partes → `case_participants`; el acto y su encadenamiento → `act_catalog` + `case_acts`; la biblioteca → servicio `biblioteca_motor`; el documento → `case_document` + `case_document_version`; el borrador de Gari → `case_act_data.gari_draft_text`. **No se crean modelos nuevos de persistencia del caso.**

4. **La normatividad es dato versionado, no código ni pesos del LLM.** Fuente de verdad en Git (`corpus-juridico/*.json`) → cargada a Postgres (tablas `legal_*`) + índice `pgvector`. Vigencia temporal, artículo por artículo, doble estado (`vigencia_formal` / `aplicabilidad_operativa`). Nunca se borra: se versiona.

5. **La IA asiste, el motor manda, el notario decide.** Gari (openai + langgraph) hace extracción, prosa libre, clasificación y QA; nunca decide procedencia ni toca esqueleto/liquidación/citas. El RAG filtra por vigencia y cita al registro estructurado.

6. **Un acto de punta a punta primero** (compraventa), luego hipoteca y cancelación (casi gratis, ya soportados por motor y corpus).

## Estructura de carpetas
```
corpus-juridico/                      # fuente de verdad del corpus (JSON versionado)
  normas.json  reglas.json  clausulas.json  tarifas.json  jurisprudencia.json
frontend/lib/motor-escritura/         # motor determinista (TS, port del HTML)
frontend/components/escritura/        # UI del flujo (form, captura, editor)
frontend/app/(app)/dashboard/casos/[id]/escritura/   # ruta del flujo
backend/app/models/legal_*.py         # tablas del corpus
backend/app/modules/escritura/        # API del flujo (router + servicios)
backend/app/seeds/seed_corpus.py      # siembra corpus-juridico/ → BD
docs/ecosistema-notarial/prompts/     # prompts de Codex por WP (trazabilidad)
```

## Consecuencias
- Máxima reutilización: la lógica difícil (motor) y la persistencia (caso) no se reescriben.
- El corpus queda desacoplado de la app: se actualiza editando datos + PR, sin tocar código.
- El motor tiene una red de pruebas desde el día 1 (golden tests contra el HTML).
