# SESSION.md — EasyProNotarial-2

## Estado de sesión

Este archivo consolida contexto operativo, decisiones y próximos hitos de EasyProNotarial-2 para continuar el trabajo con claridad en futuras sesiones con IA, Codex, Claude, Kimi o desarrollo manual.

---

# HITO: Facturación Electrónica y Nómina Electrónica EasyPro

## 1. Decisión estratégica

EasyPro NO se integrará directamente con la DIAN en la primera versión.

La ruta definida es usar un proveedor/intermediario tecnológico autorizado o proveedor API para:

- Facturación electrónica.
- Notas crédito.
- Notas débito.
- Documento soporte, si aplica.
- Nómina electrónica, si el proveedor lo soporta.
- Consulta de estados.
- Descarga/almacenamiento de XML, PDF, CUFE/CUNE y respuestas.

La razón de esta decisión:

- Reducir complejidad técnica.
- Evitar construir firma XML UBL 2.1 directa desde cero.
- Evitar asumir directamente validaciones técnicas DIAN.
- Acelerar MVP comercial.
- Permitir cambio de proveedor mediante arquitectura de adaptadores.

---

## 2. Proveedores a evaluar

### 2.1 Proveedor principal a evaluar: Plemsi

Plemsi queda como proveedor/intermediario principal a cotizar y evaluar.

Validar con Plemsi:

- API REST disponible.
- Ambiente sandbox/pruebas.
- Documentación técnica.
- Soporte multiempresa/multicliente.
- Facturación electrónica.
- Nómina electrónica.
- Notas crédito y débito.
- Documento soporte.
- Consulta de estados DIAN.
- Retorno de XML.
- Retorno de PDF.
- Retorno de CUFE/CUNE.
- Envío automático al adquirente/empleado.
- Manejo de resolución y numeración.
- Manejo de certificados digitales.
- Costos por documento.
- Costos mensuales.
- Costo de implementación.
- SLA y soporte.
- Límites de volumen.
- Tiempo de habilitación.

### 2.2 Proveedor alterno a evaluar

El segundo proveedor queda pendiente de nombre definitivo. Debe cotizarse como alternativa real frente a Plemsi.

Opciones posibles para revisar:

- Siigo API.
- Alegra API.
- Facturatech.
- The Factory HKA.
- Carvajal Tecnología y Servicios.
- Loggro.
- Otro proveedor recomendado por socios o notaría piloto.

Criterio: no elegir proveedor por marca sino por API, soporte técnico, costos, documentación y capacidad multiempresa.

---

## 3. Principio de arquitectura

EasyPro debe ser dueño del proceso de negocio.

El proveedor/intermediario solo debe emitir, validar y retornar documentos electrónicos.

Arquitectura objetivo:

```text
EasyPro
  ↓
Billing / Payroll Core interno
  ↓
Provider Adapter
  ↓
Plemsi u otro proveedor
  ↓
DIAN
  ↓
Respuesta proveedor
  ↓
EasyPro guarda estado, XML, PDF, CUFE/CUNE, logs y eventos
```

Regla clave:

```text
Nunca amarrar el dominio de EasyPro directamente a un proveedor.
Todo debe pasar por una interfaz/adaptador.
```

---

## 4. Módulo de Facturación Electrónica

### 4.1 Objetivo

Crear un módulo que permita generar, controlar y emitir facturas electrónicas asociadas a la operación de EasyPro.

Facturación podrá aplicar para:

- Plan SaaS mensual.
- Plan SaaS anual.
- Licencias por usuario.
- Licencias por notaría.
- Servicios de implementación.
- Capacitación.
- Soporte.
- Desarrollos adicionales.
- Casos notariales, si el modelo comercial lo requiere.
- Documentos generados, si se cobra por volumen.
- Integraciones o módulos adicionales.

### 4.2 Alcance funcional mínimo

El módulo debe permitir:

1. Configurar empresa emisora.
2. Configurar resolución, prefijo y numeración.
3. Crear clientes facturables.
4. Crear productos/servicios facturables.
5. Crear factura en borrador.
6. Calcular subtotal, impuestos, descuentos y total.
7. Emitir factura vía proveedor.
8. Consultar estado de emisión.
9. Guardar XML, PDF y respuesta técnica.
10. Guardar CUFE.
11. Crear nota crédito.
12. Crear nota débito.
13. Registrar eventos.
14. Descargar PDF/XML.
15. Auditar quién creó, emitió, anuló o descargó.

### 4.3 Estados de factura

```text
draft
ready_to_emit
submitted
accepted
rejected
cancelled
credit_note_created
debit_note_created
```

### 4.4 Tablas sugeridas

```text
billing_settings
billing_customers
billing_products
invoices
invoice_items
invoice_taxes
invoice_events
invoice_documents
provider_credentials
provider_requests
provider_responses
```

### 4.5 Campos clave de factura

Cabecera:

- id.
- tenant_id / organization_id / notary_id.
- customer_id.
- prefix.
- number.
- issue_date.
- due_date.
- currency.
- subtotal.
- discount_total.
- tax_total.
- total.
- status.
- provider_name.
- provider_document_id.
- cufe.
- xml_url.
- pdf_url.
- dian_status.
- created_by.
- emitted_by.
- emitted_at.

Detalle:

- invoice_id.
- product_id.
- description.
- quantity.
- unit_price.
- discount.
- tax_rate.
- tax_amount.
- line_total.

### 4.6 API sugerida

```text
GET    /api/billing/settings
PUT    /api/billing/settings
GET    /api/billing/customers
POST   /api/billing/customers
GET    /api/billing/products
POST   /api/billing/products
GET    /api/billing/invoices
POST   /api/billing/invoices
GET    /api/billing/invoices/{id}
POST   /api/billing/invoices/{id}/emit
POST   /api/billing/invoices/{id}/sync-status
POST   /api/billing/invoices/{id}/credit-note
POST   /api/billing/invoices/{id}/debit-note
GET    /api/billing/invoices/{id}/pdf
GET    /api/billing/invoices/{id}/xml
GET    /api/billing/provider/logs
```

### 4.7 Frontend sugerido

Ruta administrativa:

```text
/admin/facturacion
```

Pantallas:

- Configuración de facturación.
- Clientes.
- Productos/servicios.
- Listado de facturas.
- Crear factura.
- Detalle de factura.
- Eventos y respuesta proveedor.
- Descarga PDF/XML.

---

## 5. Módulo de Nómina Electrónica

### 5.1 Objetivo

Crear capacidad para generar y transmitir documentos soporte de nómina electrónica mediante proveedor tecnológico.

No construir cálculo completo de nómina en la primera fase.

La primera versión debe enfocarse en:

- Registrar empleados.
- Registrar devengados.
- Registrar deducciones.
- Generar documento soporte de nómina electrónica.
- Enviar al proveedor.
- Guardar CUNE, XML, PDF y estado.

### 5.2 Alcance funcional mínimo

1. Configurar empresa/emisor.
2. Configurar proveedor de nómina electrónica.
3. Crear empleados.
4. Cargar periodo de nómina.
5. Registrar devengados.
6. Registrar deducciones.
7. Calcular total devengado, total deducido y neto.
8. Generar documento electrónico.
9. Enviar al proveedor.
10. Consultar estado.
11. Guardar CUNE.
12. Guardar XML/PDF.
13. Generar ajustes o notas, si aplica.
14. Auditar eventos.

### 5.3 Estados de nómina electrónica

```text
draft
ready_to_submit
submitted
accepted
rejected
adjustment_required
cancelled
```

### 5.4 Tablas sugeridas

```text
payroll_settings
payroll_employees
payroll_periods
payroll_documents
payroll_earnings
payroll_deductions
payroll_events
payroll_documents_files
provider_requests
provider_responses
```

### 5.5 Campos clave empleado

- id.
- tenant_id / organization_id.
- document_type.
- document_number.
- first_name.
- last_name.
- email.
- address.
- city.
- department.
- contract_type.
- salary_type.
- base_salary.
- payment_method.
- bank_account, si aplica.
- active.

### 5.6 Campos clave documento nómina

- id.
- employee_id.
- payroll_period_id.
- issue_date.
- payment_date.
- accrued_total.
- deductions_total.
- net_total.
- status.
- provider_name.
- provider_document_id.
- cune.
- xml_url.
- pdf_url.
- created_by.
- submitted_by.
- submitted_at.

### 5.7 API sugerida

```text
GET    /api/payroll/settings
PUT    /api/payroll/settings
GET    /api/payroll/employees
POST   /api/payroll/employees
GET    /api/payroll/periods
POST   /api/payroll/periods
GET    /api/payroll/documents
POST   /api/payroll/documents
GET    /api/payroll/documents/{id}
POST   /api/payroll/documents/{id}/submit
POST   /api/payroll/documents/{id}/sync-status
GET    /api/payroll/documents/{id}/pdf
GET    /api/payroll/documents/{id}/xml
GET    /api/payroll/provider/logs
```

### 5.8 Frontend sugerido

Ruta administrativa:

```text
/admin/nomina-electronica
```

Pantallas:

- Configuración de nómina electrónica.
- Empleados.
- Periodos.
- Documentos de nómina.
- Crear documento.
- Detalle de documento.
- Respuesta proveedor.
- Descarga PDF/XML.

---

## 6. Capa común: Provider Adapter

Crear una interfaz común para que EasyPro pueda cambiar de proveedor sin reescribir todo.

### 6.1 Interfaz sugerida

```python
class ElectronicDocumentProvider:
    def emit_invoice(self, payload):
        pass

    def emit_credit_note(self, payload):
        pass

    def emit_debit_note(self, payload):
        pass

    def submit_payroll_document(self, payload):
        pass

    def get_document_status(self, provider_document_id):
        pass

    def get_pdf(self, provider_document_id):
        pass

    def get_xml(self, provider_document_id):
        pass
```

### 6.2 Adaptadores

```text
providers/
  base.py
  plemsi.py
  mock.py
  alternate.py
```

Fases:

1. MockProvider para desarrollo.
2. PlemsiProvider para integración real.
3. AlternateProvider cuando se elija segundo proveedor.

---

## 7. Seguridad

### 7.1 Secretos

No guardar credenciales del proveedor en texto plano.

Usar:

- Variables de entorno.
- Secret manager si está disponible.
- Cifrado si deben guardarse por tenant.
- Rotación de llaves.
- No exponer tokens en logs.

### 7.2 Auditoría

Auditar:

- Creación de factura.
- Emisión.
- Rechazo.
- Descarga PDF/XML.
- Cambio de configuración.
- Cambio de proveedor.
- Creación de nómina.
- Envío de nómina.
- Reintentos.

### 7.3 Multiempresa

Todo debe filtrar por organización/notaría/tenant.

Regla:

```text
Ninguna factura, nómina, PDF, XML o log puede consultarse sin validar tenant y permisos.
```

---

## 8. Fases de implementación

## Fase 0 — Cotización y decisión proveedor

Objetivo: elegir proveedor principal y alterno.

Tareas:

1. Solicitar documentación técnica a Plemsi.
2. Solicitar documentación técnica al proveedor alterno.
3. Confirmar si ambos soportan facturación y nómina electrónica.
4. Confirmar ambiente sandbox.
5. Confirmar costos.
6. Confirmar límites de documentos.
7. Confirmar tiempos de implementación.
8. Confirmar soporte multiempresa.
9. Confirmar método de autenticación API.
10. Confirmar responsabilidades legales.

Entregable:

```text
Matriz comparativa proveedor facturación/nómina electrónica.
```

## Fase 1 — Core interno sin proveedor real

Objetivo: construir base propia en EasyPro.

Incluye:

- Modelos.
- Migraciones.
- CRUD clientes.
- CRUD productos.
- CRUD facturas.
- CRUD empleados.
- CRUD periodos nómina.
- Cálculos básicos.
- Estados.
- Eventos.
- MockProvider.

Resultado:

```text
EasyPro genera facturas y documentos de nómina en estado interno, sin transmisión real.
```

## Fase 2 — PDF, XML placeholder y auditoría

Objetivo: tener demo funcional.

Incluye:

- PDF de factura.
- PDF de nómina.
- XML placeholder o estructura interna.
- Eventos.
- Descargas controladas.
- Logs.
- Validación de permisos.

Resultado:

```text
MVP demostrable sin conexión real al proveedor.
```

## Fase 3 — Integración Plemsi sandbox

Objetivo: conectar Plemsi en ambiente de pruebas.

Incluye:

- Credenciales sandbox.
- Mapear payload factura.
- Mapear payload nómina.
- Emitir factura de prueba.
- Emitir nómina de prueba.
- Consultar estado.
- Guardar PDF/XML/CUFE/CUNE.
- Manejar rechazos.
- Registrar request/response.

Resultado:

```text
EasyPro conectado a Plemsi en pruebas.
```

## Fase 4 — Proveedor alterno

Objetivo: validar portabilidad.

Incluye:

- Implementar AlternateProvider.
- Probar al menos flujo de factura.
- Confirmar que el dominio EasyPro no depende de Plemsi.

Resultado:

```text
Arquitectura desacoplada y no dependiente de un solo proveedor.
```

## Fase 5 — Producción controlada

Objetivo: habilitar emisión real.

Incluye:

- Certificados/resoluciones reales.
- Numeración real.
- Pruebas con cliente piloto.
- Firma de contrato y autorización.
- Monitoreo.
- Soporte.
- Plan de contingencia.

Resultado:

```text
Facturación electrónica y nómina electrónica operativas con proveedor.
```

---

## 9. Matriz de decisión proveedor

Evaluar cada proveedor con esta tabla:

| Criterio | Plemsi | Proveedor alterno |
|---|---|---|
| Facturación electrónica | Pendiente validar | Pendiente validar |
| Nómina electrónica | Pendiente validar | Pendiente validar |
| API REST | Pendiente validar | Pendiente validar |
| Sandbox | Pendiente validar | Pendiente validar |
| PDF/XML | Pendiente validar | Pendiente validar |
| CUFE/CUNE | Pendiente validar | Pendiente validar |
| Notas crédito/débito | Pendiente validar | Pendiente validar |
| Documento soporte | Pendiente validar | Pendiente validar |
| Multiempresa | Pendiente validar | Pendiente validar |
| Costo mensual | Pendiente cotizar | Pendiente cotizar |
| Costo por documento | Pendiente cotizar | Pendiente cotizar |
| Soporte técnico | Pendiente validar | Pendiente validar |
| Documentación clara | Pendiente validar | Pendiente validar |
| Facilidad integración | Pendiente validar | Pendiente validar |
| Riesgo lock-in | Medio | Pendiente |

---

## 10. Riesgos

| Riesgo | Mitigación |
|---|---|
| Dependencia total de Plemsi | Usar Provider Adapter |
| Cambios API proveedor | Encapsular lógica en adaptador |
| Errores en datos enviados | Validaciones previas |
| Facturas rechazadas | Guardar detalle de rechazo |
| Nómina rechazada | Validar campos obligatorios antes de enviar |
| Secretos expuestos | Variables de entorno/cifrado |
| Duplicidad de consecutivos | Índices únicos y transacciones |
| Acceso cruzado entre clientes | Tenant isolation estricto |
| Pérdida de XML/PDF | Storage y backups |
| Costos altos por proveedor | Comparar mínimo 2 opciones |

---

## 11. Índices y restricciones recomendadas

Facturas:

```text
unique(tenant_id, prefix, number)
index(tenant_id, status)
index(customer_id)
index(provider_document_id)
```

Nómina:

```text
unique(tenant_id, employee_id, payroll_period_id)
index(tenant_id, status)
index(provider_document_id)
index(cune)
```

---

## 12. Prompt Codex recomendado

```text
Trabaja en EasyProNotarial-2.

Objetivo:
Crear el módulo base para facturación electrónica y nómina electrónica usando arquitectura desacoplada por proveedor/intermediario, sin integrar todavía proveedor real.

Reglas:
- Crear o usar rama feature/electronic-documents-core desde main o develop según exista.
- No romper flujos actuales de casos/documentos.
- No tocar producción.
- No guardar secretos.
- Crear arquitectura de Provider Adapter.
- Crear MockProvider.
- Crear modelos, migraciones, servicios y endpoints mínimos.
- Todo debe ser multiempresa/multinotaría.
- Toda consulta debe validar tenant/organization/notary.
- Crear endpoints base para billing y payroll.
- Crear eventos y logs técnicos.
- Crear frontend administrativo mínimo si la estructura del frontend lo permite.
- Si falta contexto de estructura, primero inspeccionar repo y proponer rutas exactas.

Entregables:
1. Migraciones.
2. Modelos.
3. Servicios.
4. Routers/endpoints.
5. MockProvider.
6. Validaciones mínimas.
7. Resumen de archivos modificados.
8. Comandos para probar localmente.
```

---

## 13. Decisión final registrada

EasyPro implementará facturación electrónica y nómina electrónica mediante proveedor/intermediario.

Proveedor principal a evaluar: Plemsi.

Proveedor alterno: pendiente definir/cotizar.

La arquitectura debe quedar desacoplada por adaptadores para permitir cambiar de proveedor sin rediseñar el dominio de EasyPro.
