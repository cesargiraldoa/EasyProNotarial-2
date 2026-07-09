# Notarial Template Lab

Sandbox general para explorar construcción inversa de plantillas notariales desde un DOCX diligenciado.

Este laboratorio no es flujo productivo. No toca endpoints, base de datos, OnlyOffice ni generación actual de minutas. Su objetivo es producir artefactos auditables para revisar cómo un documento real podría convertirse en una plantilla marcada experimental.

## Flujo

```text
DOCX diligenciado cualquiera
  -> DocumentMap estructural auditable
  -> ocurrencias tecnicas generales
  -> propuestas de campos accionables
  -> reporte HTML de revision
  -> DOCX etiquetado experimental
  -> validacion con marked_template_detector
```

## Uso

Desde la raíz del repo:

```powershell
python tools/notarial_template_lab/run_lab.py --input "C:\ruta\documento.docx"
```

El comando imprime:

- ruta de artefactos
- total de bloques
- total de runs
- total de propuestas
- total de reemplazos
- PASS/FAIL de validación
- campos detectados por `marked_template_detector`

## Artefactos

Se generan en:

```text
artifacts/notarial_template_lab/<safe_document_name>/
```

Archivos principales:

- `01_document_map.json`
- `03_field_proposals.json`
- `04_draft_replacements.json`
- `05_review_report.html`
- `06_template_draft.docx`
- `07_validation_report.json`

## Principios

- No usa LLM.
- No contiene reglas específicas de un documento, proyecto, banco, matrícula, NIT, comprador o valor concreto.
- Las propuestas se basan en patrones técnicos y rótulos notariales comunes.
- Si el contexto no es claro, la propuesta queda como `review_required`.
- El borrador solo reemplaza propuestas de alta confianza.
- El documento original no se modifica.

## Limitaciones

- El reemplazo preserva formato solo cuando el valor completo está dentro de un mismo run.
- Si una ocurrencia cruza varios runs, queda registrada como salto para revisión.
- Las frases largas en mayúscula y bloques que parecen títulos jurídicos no se reemplazan automáticamente.
- El laboratorio propone campos; no confirma semántica final ni genera una plantilla productiva.
