# Integración Gari Billing en EasyPro

EasyPro consume Gari Billing únicamente a través de la API interna de Helexium-2.
No existe conexión directa entre EasyPro y MATIAS.

## Variables de entorno

Configurar en el backend de EasyPro:

```env
GARI_BILLING_BASE_URL=
GARI_BILLING_INTERNAL_KEY=
GARI_BILLING_TIMEOUT_SECONDS=30
```

No guardar estos valores en el repositorio ni en `.env`.

## Endpoint usado

Gari Billing expone el endpoint interno:

```http
POST /api/integrations/billing/invoices
```

Header requerido:

```http
X-Billing-Internal-Key: <valor interno>
```

## Flujo

1. El usuario autenticado crea una factura desde un caso/minuta en EasyPro.
2. EasyPro carga el caso completo y construye el payload de facturación.
3. El backend envía el payload a Gari Billing con `emit_mode=draft` por defecto.
4. Gari Billing responde con el resultado de la factura y EasyPro lo devuelve al frontend.

## Payload base

```json
{
  "source_system": "easypro",
  "external_reference": "case_<case_id>",
  "idempotency_key": "easypro-case_<case_id>",
  "emit_mode": "draft",
  "customer": {
    "customer_kind": "natural|juridica",
    "document_type": "CC|NIT",
    "document_number": "...",
    "legal_name": "...",
    "trade_name": "...",
    "email": "...",
    "phone": "...",
    "address": "..."
  },
  "lines": [
    {
      "code": "SERV-NOTARIAL-001",
      "description": "Servicio notarial",
      "quantity": 1,
      "unit_price": 100000,
      "discount_amount": 0,
      "tax_rate": 19,
      "unit_measure": "NIU"
    }
  ],
  "metadata": {
    "case_id": "...",
    "document_type": "minuta",
    "source_system": "easypro"
  }
}
```

## Endpoint en EasyPro

```http
POST /api/v1/billing/gari/invoices/from-case/{case_id}?emit_mode=draft
```

Valores admitidos para `emit_mode`:

```text
draft
ready
stub
matias_sandbox
```

## Seguridad

- El endpoint de EasyPro requiere usuario autenticado.
- El acceso está restringido a roles administrativos.
- `GARI_BILLING_INTERNAL_KEY` nunca se expone al frontend.
- Los secretos no se registran en logs.

## Decisión funcional

EasyPro no habla con MATIAS de forma directa. Toda la integración de facturación pasa por Gari Billing.
