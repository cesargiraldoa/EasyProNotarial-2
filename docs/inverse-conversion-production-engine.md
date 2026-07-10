# Motor de Conversion Inversa de Marcacion

## Arquitectura objetivo

El motor queda aislado en `backend/app/services/minuta/inverse_conversion_engine/`. Su responsabilidad es analizar marcadores, texto o documentos DOCX locales, recuperar evidencia del corpus ya cargado y producir candidatos auditables para revision humana.

No modifica el flujo tradicional de minutas, no genera documentos, no modifica `document_templates`, no toca OnlyOffice y no aprueba campos automaticamente.

## Por que LangGraph

LangGraph coordina pasos deterministas con estado explicito:

1. `initialize_run`
2. `extract_contexts`
3. `retrieve_lexical_evidence`
4. `retrieve_semantic_evidence`
5. `propose_candidates`
6. `validate_candidates`
7. `build_auditable_result`
8. `persist_audit`

Si LangGraph no esta instalado o la version local no soporta el esquema del estado, el modulo degrada a un runner secuencial con la misma interfaz `invoke`.

## Por que Pydantic AI

Pydantic AI queda encapsulado en `pydantic_ai_client.py` para que toda propuesta tenga contratos tipados. El modo por defecto esta deshabilitado y es deterministico. La ausencia de `OPENAI_API_KEY` no rompe el motor.

El LLM nunca aprueba campos. Solo puede proponer candidatos basados en evidencia recibida, y toda propuesta pasa por `conservative_validator.py`.

## Por que pgvector

pgvector prepara busqueda semantica futura dentro de PostgreSQL/Supabase, sin introducir Qdrant, Haystack, LlamaIndex ni servicios externos. La migracion intenta `CREATE EXTENSION IF NOT EXISTS vector` solo en PostgreSQL.

## Motor propio

La fachada publica es `InverseConversionEngineService`:

- `analyze_text(text, options)`
- `analyze_marker(raw_marker, context_before, context_after, options)`
- `analyze_document_path(path, options)`
- `get_run(run_id)`
- `list_run_steps(run_id)`

## Limites del LLM

El prompt base exige no inventar campos, usar solo evidencia, devolver JSON tipado, marcar revision humana si hay duda, no tocar texto juridico fijo y no aprobar cambios.

## RAG lexical

El motor reutiliza el modulo read-only `inverse_conversion_rag` sobre:

- `field_definitions`
- `field_aliases`
- `corpus_documents`
- `corpus_document_fields`
- `field_patterns`

## RAG semantico

`semantic_indexer.py` prepara registros desde patrones, definiciones, aliases y campos documentales. `semantic_repository.py` consulta `inverse_conversion_embeddings`.

Sin embeddings disponibles, la busqueda semantica degrada a busqueda lexical sobre contenido indexado. `semantic_enabled` debe activarse explicitamente.

## Tablas nuevas

- `inverse_conversion_embeddings`
- `inverse_conversion_runs`
- `inverse_conversion_run_steps`
- `inverse_conversion_candidates`

El indice semantico escribe solo en `inverse_conversion_embeddings`. La auditoria escribe solo en las tres tablas de runs.

## Endpoint interno

Endpoint aislado:

`POST /api/v1/inverse-conversion/analyze`

Entrada:

```json
{
  "text": "...",
  "marker": "...",
  "context_before": "...",
  "context_after": "...",
  "options": {
    "use_llm": false,
    "use_semantic": false
  }
}
```

No esta integrado al frontend.

## CLI

Ejecutar motor:

```powershell
python scripts/run_inverse_conversion_engine.py --marker "NUMERO_MATRICULA" --before "MATRICULA:" --after "[[--]]"
python scripts/run_inverse_conversion_engine.py --text "COMPRADOR: JUAN PEREZ - C.C. 123"
python scripts/run_inverse_conversion_engine.py --document-path "C:\ruta\documento.docx"
```

Preparar indice semantico:

```powershell
python scripts/index_inverse_conversion_embeddings.py --dry-run
python scripts/index_inverse_conversion_embeddings.py --commit
```

`--dry-run` es el modo recomendado. `--commit` escribe solo en `inverse_conversion_embeddings`.

## Como correr local

```powershell
cd C:\EasyProNotarial-2\easypro2\backend
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH=(Get-Location).Path
alembic upgrade head
python scripts/run_inverse_conversion_engine.py --marker "VALOR_VENTA" --before "VALOR DEL ACTO: $" --after "[[--]]"
```

## Despliegue produccion

1. Instalar dependencias backend.
2. Aplicar migracion Alembic.
3. Mantener `use_llm=false` por defecto.
4. Activar embeddings solo cuando exista proveedor y revision operacional.
5. Exponer el endpoint solo como API interna/controlada.

## Variables de entorno

- `OPENAI_API_KEY`: opcional; sin ella el cliente queda disabled/mock.
- `INVERSE_CONVERSION_LLM_ENABLED`: opt-in para intentar modo LLM.
- `DATABASE_URL`: base PostgreSQL/Supabase esperada para pgvector.

## Modo sin LLM

Es el modo predeterminado. Usa evidencia lexical y contratos tipados deterministas.

## Modo sin embeddings

El indice puede guardar hashes y contenido con `embedding = null`. Las consultas semanticas degradan a lexical.

## Reglas conservadoras

El validador bloquea o manda a revision:

- `TIPO_DOCUMENTO` contra `NUMERO_DOCUMENTO`.
- `MUNICIPIO_EXPEDICION_DOCUMENTO` contra `NUMERO_DOCUMENTO`.
- `DIA`, `MES`, `ANO` entre si.
- compradores ordinales 1/2/3 colapsados entre si o al campo base.
- `NUMERO_ESCRITURA_EN_LETRAS` contra `NUMERO_ESCRITURA_EN_NUMEROS`.
- campos `conflict` usados como definitivos.
- propuestas sin evidencia.
- score bajo.
- categoria semantica incompatible.
- texto juridico fijo detectado como variable.
- campo canonico inexistente.

## Que no toca

Este bloque no toca:

- carga de plantilla etiquetada;
- deteccion de campos existente;
- formulario dinamico;
- generacion documental actual;
- OnlyOffice;
- marked-template;
- `DocxRenderer`;
- `NotarialDocumentEngine`;
- reverse-builder;
- `document_templates`;
- documentos notariales reales.
