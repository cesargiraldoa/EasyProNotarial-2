# AGENTS.md — EasyProNotarial-2
Actualizado: 2026-05-21

---

## Agentes de IA del sistema

---

### 1. Gari — Agente Documental Notarial

**Dominio:** Generación automática de escrituras públicas en formato .docx

**Estado:** Operativo

**Descripción:**
Gari recibe el contexto completo de un caso notarial (plantilla, intervinientes, datos del acto, datos de notaría y notario) y genera el texto completo de la escritura conforme a la ley colombiana (Decreto 960/1970). El resultado se convierte a .docx y se sube a Supabase Storage.

**Flujo:**
```
Caso completo (BD)
  → resolver_escritura_desde_template() — identifica variante_id = template.slug
  → build_gari_prompt() — construye prompt con:
       SYSTEM_PROMPT_GARI (reglas notariales colombianas)
       Datos notaría + notario
       Participantes con snapshot_json (personas + entidades representadas)
       ACTOS_POR_VARIANTE[slug] (lista de actos a incluir)
       Texto referencia .docx plantilla (hasta 14,000 chars)
  → GPT-4o generate (max_tokens=16000, temperature=0.2)
  → build_gari_docx_buffer() — convierte a .docx con guiones automáticos
  → Supabase Storage upload → cases/case-{id}/draft/
  → Registra CaseDocumentVersion en BD
```

**Archivos clave:**
- `backend/app/modules/document_flow/services/gari_service.py`
- `backend/app/modules/document_flow/router.py` → POST `/api/v1/document-flow/cases/{id}/generate-with-gari`

**Tools disponibles:**
- OpenAI GPT-4o API (via `openai>=1.0.0`)
- python-docx (generación .docx)
- Supabase Storage SDK (upload/download archivos)
- SQLAlchemy (lectura caso + participantes + plantilla)

**Tools pendientes:**
- Streaming de respuesta para casos con muchos actos (actualmente bloquea hasta que GPT termina)
- Regeneración parcial por acto individual
- Revisión semántica post-generación (agente verificador)
- Integración OnlyOffice para edición colaborativa post-generación

**Limitaciones conocidas:**
- ACTOS_POR_VARIANTE está hardcodeado en `build_gari_prompt()` — no es configurable desde UI
- Timeout en Railway con PDFs grandes en ingesta RAG
- Sin manejo de reintentos automáticos si GPT falla a mitad de generación

---

### 2. OCR + Verificación Facial — Agente de Identidad

**Dominio:** Verificación de documentos de identidad y coincidencia facial

**Estado:** Parcial (lógica de GPT-4o Vision presente, integración UI pendiente de confirmar)

**Descripción:**
Usa GPT-4o Vision para extraer datos de documentos de identidad (cédula, pasaporte) y verificar coincidencia facial entre foto del documento y foto en tiempo real.

**Archivos clave:**
- Ubicación exacta a confirmar en `backend/app/modules/` (no mapeado completamente)

**Tools disponibles:**
- OpenAI GPT-4o Vision (via `openai>=1.0.0`)

**Tools pendientes:**
- Endpoint público documentado
- Flujo frontend completo para captura y verificación
- Integración con módulo de personas (enriquecer datos desde OCR)

---

### 3. Facturación Electrónica — Agente Proveedor (PENDIENTE)

**Dominio:** Emisión de facturas electrónicas ante la DIAN vía proveedor intermediario

**Estado:** Pendiente — solo diseño, cero código

**Descripción:**
Agente adaptador que encapsula la comunicación con el proveedor de facturación electrónica (Plemsi evaluado como principal). Debe implementar la interfaz `ElectronicDocumentProvider`.

**Interfaz objetivo:**
```python
class ElectronicDocumentProvider:
    def emit_invoice(self, payload): ...
    def emit_credit_note(self, payload): ...
    def emit_debit_note(self, payload): ...
    def submit_payroll_document(self, payload): ...
    def get_document_status(self, provider_document_id): ...
    def get_pdf(self, provider_document_id): ...
    def get_xml(self, provider_document_id): ...
```

**Adaptadores planificados:**
- `providers/mock.py` — para desarrollo y demo sin proveedor real
- `providers/plemsi.py` — integración Plemsi (sandbox → producción)
- `providers/alternate.py` — segundo proveedor a definir

**Tools pendientes:**
- Todo: modelos, migraciones, servicios, routers, frontend, adaptadores

---

### 4. Nómina Electrónica — Agente Proveedor (PENDIENTE)

**Dominio:** Emisión de documentos soporte de nómina electrónica ante la DIAN

**Estado:** Pendiente — solo diseño, cero código

**Descripción:**
Extiende el Provider Adapter de facturación para cubrir documentos de nómina electrónica (CUNE, XML, PDF).

**Tools pendientes:**
- Todo: modelos, migraciones, servicios, routers, frontend, adaptadores
