# MVP documental: Poder General

## Qué se construyó
- Módulo de plantillas con soporte para `.docx` base, alcance, estado, roles requeridos, campos del acto y mapeo interno de variables.
- Flujo `Crear Caso` por wizard para `Poder General`.
- Catálogo reutilizable de personas e intervinientes por documento.
- Persistencia de participantes por rol dentro del caso.
- Captura de datos del acto en JSON estructurado.
- Generación de borrador Word versionado desde plantilla real.
- Exportación Word/PDF y carga de documento definitivo firmado.
- Flujo básico de aprobación con aprobador, notario titular o suplente.
- Secuencias separadas para consecutivo interno de caso y número oficial de escritura.

## Modelo de datos
- `document_templates`
- `template_required_roles`
- `template_fields`
- `persons`
- `cases` extendida con `template_id`, `internal_case_number`, `official_deed_number`, trazabilidad de aprobación y creador
- `case_participants`
- `case_act_data`
- `case_client_comments`
- `case_internal_notes`
- `case_documents`
- `case_document_versions`
- `case_workflow_events`
- `numbering_sequences`

## Endpoints principales
- `GET/POST/PUT /api/v1/templates`
- `GET /api/v1/templates/active`
- `GET/POST/PUT /api/v1/persons`
- `POST /api/v1/document-flow/cases/from-template`
- `GET /api/v1/document-flow/cases/{case_id}`
- `PUT /api/v1/document-flow/cases/{case_id}/participants`
- `PUT /api/v1/document-flow/cases/{case_id}/act-data`
- `POST /api/v1/document-flow/cases/{case_id}/generate-draft`
- `POST /api/v1/document-flow/cases/{case_id}/client-comments`
- `POST /api/v1/document-flow/cases/{case_id}/internal-notes`
- `POST /api/v1/document-flow/cases/{case_id}/approve`
- `POST /api/v1/document-flow/cases/{case_id}/export`
- `POST /api/v1/document-flow/cases/{case_id}/final-upload`
- `GET /api/v1/document-flow/cases/{case_id}/documents/{document_id}/versions/{version_id}/download`
- `GET /api/v1/document-flow/persons/lookup`

## Flujo funcional
1. Seleccionar plantilla activa.
2. Crear caso con notaría, responsables y consecutivo interno `CAS-YYYY-NNNN`.
3. Registrar intervinientes requeridos.
4. Registrar datos del acto.
5. Generar borrador Word `v1`, `v2`, etc.
6. Registrar comentarios del cliente y observaciones internas.
7. Aprobar por aprobador y luego por notario titular o suplente.
8. Asignar número oficial de escritura al aprobar notaría.
9. Exportar Word/PDF.
10. Cargar documento definitivo firmado.

## Decisiones técnicas
- La plantilla real se copia a `backend/storage/templates` para no depender de la ruta original en producción.
- El reemplazo documental usa placeholders internos, no visibles en la UX.
- La exportación PDF del MVP usa un generador PDF plano para asegurar salida local sin dependencias de Office.
- `phone` y `business_hours` siguen tratándose como texto en el resto del sistema.
- `Case` sigue siendo la entidad documental central; no se duplicó el flujo en otra entidad paralela.

## Pendientes siguientes
- Editor visual de plantillas.
- Conversión PDF fiel desde `.docx` con motor dedicado.
- Edición completa de participantes y datos del acto desde detalle.
- Reglas de transición por rol más estrictas.
- Intervinientes múltiples por rol y actos adicionales.
- Integración de generación documental enriquecida en headers/footers/tablas.
