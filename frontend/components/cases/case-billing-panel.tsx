"use client";

import { useEffect, useMemo, useState } from "react";
import { Plus, ReceiptText, Trash2, X } from "lucide-react";
import {
  createGariInvoiceFromCase,
  type BillingCustomerInput,
  type BillingLineInput,
  type CreateGariBillingInvoicePayload,
  type GariBillingInvoiceResult,
} from "@/lib/document-flow";

type BillingDocumentType = "minuta" | "escritura" | "otro";

type CustomerFormState = {
  customer_kind: "natural" | "juridica";
  document_type: BillingCustomerInput["document_type"];
  document_number: string;
  legal_name: string;
  trade_name: string;
  email: string;
  phone: string;
  address: string;
  payment_percentage: string;
  payment_amount: string;
};

type ServiceFormState = {
  code: string;
  description: string;
  quantity: string;
  unit_price: string;
  discount_amount: string;
  tax_rate: string;
  unit_measure: string;
  editable: boolean;
  calculation_mode: BillingLineInput["calculation_mode"];
};

const DOCUMENT_TYPE_OPTIONS: Array<{ label: string; value: BillingDocumentType }> = [
  { label: "Minuta", value: "minuta" },
  { label: "Escritura", value: "escritura" },
  { label: "Otro", value: "otro" },
];

const CUSTOMER_KIND_OPTIONS: Array<{ label: string; value: CustomerFormState["customer_kind"] }> = [
  { label: "Natural", value: "natural" },
  { label: "Jurídica", value: "juridica" },
];

const DOCUMENT_KIND_OPTIONS: Array<{ label: string; value: BillingCustomerInput["document_type"] }> = [
  { label: "CC", value: "CC" },
  { label: "NIT", value: "NIT" },
  { label: "CE", value: "CE" },
  { label: "Pasaporte", value: "PASAPORTE" },
  { label: "Otro", value: "OTRO" },
];

const SERVICE_PRESETS = [
  { label: "Servicio notarial", code: "SERV-NOTARIAL-001", description: "Servicio notarial", unit_price: "100000", tax_rate: "19", unit_measure: "NIU", calculation_mode: "fixed" as const },
  { label: "Escritura pública", code: "SERV-ESCRITURA-001", description: "Escritura pública", unit_price: "100000", tax_rate: "19", unit_measure: "NIU", calculation_mode: "fixed" as const },
  { label: "Copias", code: "SERV-COPIAS-001", description: "Copias", unit_price: "5000", tax_rate: "19", unit_measure: "NIU", calculation_mode: "manual" as const },
  { label: "Otro servicio", code: "SERV-OTRO-001", description: "Otro servicio", unit_price: "0", tax_rate: "19", unit_measure: "NIU", calculation_mode: "manual" as const },
] as const;

function createEmptyCustomer(defaultDocumentType: BillingDocumentType): CustomerFormState {
  return {
    customer_kind: "natural",
    document_type: defaultDocumentType === "escritura" ? "NIT" : "CC",
    document_number: "",
    legal_name: "",
    trade_name: "",
    email: "",
    phone: "",
    address: "",
    payment_percentage: "",
    payment_amount: "",
  };
}

function createDefaultService(): ServiceFormState {
  const preset = SERVICE_PRESETS[0];
  return {
    code: preset.code,
    description: preset.description,
    quantity: "1",
    unit_price: preset.unit_price,
    discount_amount: "0",
    tax_rate: preset.tax_rate,
    unit_measure: preset.unit_measure,
    editable: true,
    calculation_mode: preset.calculation_mode,
  };
}

function parseMoney(value: string) {
  const normalized = value.trim();
  if (!normalized) return 0;
  const parsed = Number(normalized.replace(/,/g, "."));
  return Number.isFinite(parsed) ? parsed : NaN;
}

function isEmailValid(value: string) {
  if (!value.trim()) return true;
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim());
}

function isDocumentNumberValid(value: string) {
  return /^[A-Za-z0-9 ._\-]{3,40}$/.test(value.trim());
}

function formatAmount(value: number) {
  return new Intl.NumberFormat("es-CO", { maximumFractionDigits: 2 }).format(value);
}

export function CaseBillingPanel({
  open,
  onClose,
  caseId,
  caseLabel,
  documentType,
  documentId,
  versionId,
}: {
  open: boolean;
  onClose: () => void;
  caseId: number;
  caseLabel?: string;
  documentType: BillingDocumentType;
  documentId?: number | null;
  versionId?: number | null;
}) {
  const [customer, setCustomer] = useState<CustomerFormState>(() => createEmptyCustomer(documentType));
  const [services, setServices] = useState<ServiceFormState[]>(() => [createDefaultService()]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<GariBillingInvoiceResult | null>(null);

  useEffect(() => {
    if (!open) return;
    setCustomer(createEmptyCustomer(documentType));
    setServices([createDefaultService()]);
    setIsSubmitting(false);
    setError(null);
    setResult(null);
  }, [open, documentType]);

  const totals = useMemo(() => {
    return services.reduce(
      (accumulator, item) => {
        const quantity = Number.isFinite(parseMoney(item.quantity)) ? parseMoney(item.quantity) : 0;
        const unitPrice = Number.isFinite(parseMoney(item.unit_price)) ? parseMoney(item.unit_price) : 0;
        const discountAmount = Number.isFinite(parseMoney(item.discount_amount)) ? parseMoney(item.discount_amount) : 0;
        const taxRate = Number.isFinite(parseMoney(item.tax_rate)) ? parseMoney(item.tax_rate) : 0;
        const lineBase = Math.max(quantity * unitPrice - discountAmount, 0);
        const lineTax = Math.max((lineBase * taxRate) / 100, 0);
        accumulator.subtotal += lineBase;
        accumulator.tax += lineTax;
        accumulator.total += lineBase + lineTax;
        return accumulator;
      },
      { subtotal: 0, tax: 0, total: 0 },
    );
  }, [services]);

  if (!open) {
    return null;
  }

  function updateCustomer<K extends keyof CustomerFormState>(key: K, value: CustomerFormState[K]) {
    setCustomer((current) => ({ ...current, [key]: value }));
  }

  function updateService(index: number, key: keyof ServiceFormState, value: string | boolean) {
    setServices((current) => current.map((item, itemIndex) => (itemIndex === index ? { ...item, [key]: value } : item)));
  }

  function applyPreset(index: number, presetCode: string) {
    const preset = SERVICE_PRESETS.find((item) => item.code === presetCode) ?? SERVICE_PRESETS[0];
    setServices((current) =>
      current.map((item, itemIndex) =>
        itemIndex === index
          ? {
              ...item,
              code: preset.code,
              description: preset.description,
              unit_price: preset.unit_price,
              tax_rate: preset.tax_rate,
              unit_measure: preset.unit_measure,
              calculation_mode: preset.calculation_mode,
            }
          : item,
      ),
    );
  }

  function addService() {
    setServices((current) => [...current, createDefaultService()]);
  }

  function removeService(index: number) {
    setServices((current) => (current.length <= 1 ? current : current.filter((_, itemIndex) => itemIndex !== index)));
  }

  function validateAndBuildPayload(): CreateGariBillingInvoicePayload | null {
    const documentNumber = customer.document_number.trim();
    const legalName = customer.legal_name.trim();
    if (!documentNumber) {
      setError("Debes diligenciar el documento del pagador.");
      return null;
    }
    if (!isDocumentNumberValid(documentNumber)) {
      setError("El número de documento del pagador no es válido.");
      return null;
    }
    if (!legalName) {
      setError("Debes diligenciar el nombre o razón social del pagador.");
      return null;
    }
    if (customer.email.trim() && !isEmailValid(customer.email)) {
      setError("El correo del pagador no es válido.");
      return null;
    }
    if (customer.payment_percentage.trim() && !Number.isFinite(Number(customer.payment_percentage))) {
      setError("El porcentaje de pago del pagador no es válido.");
      return null;
    }
    if (customer.payment_amount.trim() && !Number.isFinite(Number(customer.payment_amount))) {
      setError("El monto de pago del pagador no es válido.");
      return null;
    }
    if (services.length === 0) {
      setError("Debes agregar al menos un servicio facturable.");
      return null;
    }

    const billingLines: BillingLineInput[] = [];
    for (const item of services) {
      const code = item.code.trim();
      const description = item.description.trim();
      const quantity = parseMoney(item.quantity);
      const unitPrice = parseMoney(item.unit_price);
      const discountAmount = parseMoney(item.discount_amount);
      const taxRate = parseMoney(item.tax_rate);
      const unitMeasure = item.unit_measure.trim() || "NIU";

      if (!code) {
        setError("Cada servicio debe tener un código.");
        return null;
      }
      if (!description) {
        setError("Cada servicio debe tener una descripción.");
        return null;
      }
      if (!Number.isFinite(quantity) || quantity <= 0) {
        setError(`El servicio ${code} debe tener cantidad mayor que cero.`);
        return null;
      }
      if (!Number.isFinite(unitPrice) || unitPrice < 0) {
        setError(`El servicio ${code} debe tener un valor unitario válido.`);
        return null;
      }
      if (!Number.isFinite(discountAmount) || discountAmount < 0) {
        setError(`El servicio ${code} debe tener un descuento válido.`);
        return null;
      }
      if (!Number.isFinite(taxRate) || taxRate < 0) {
        setError(`El servicio ${code} debe tener un IVA válido.`);
        return null;
      }

      billingLines.push({
        code,
        description,
        quantity,
        unit_price: unitPrice,
        discount_amount: discountAmount,
        tax_rate: taxRate,
        unit_measure: unitMeasure,
        editable: item.editable,
        calculation_mode: item.calculation_mode,
      });
    }

    const billingCustomer: BillingCustomerInput = {
      customer_kind: customer.customer_kind,
      document_type: customer.document_type,
      document_number: documentNumber,
      legal_name: legalName,
      trade_name: customer.trade_name.trim() || null,
      email: customer.email.trim() || null,
      phone: customer.phone.trim() || null,
      address: customer.address.trim() || null,
      payment_percentage: customer.payment_percentage.trim() ? Number(customer.payment_percentage) : null,
      payment_amount: customer.payment_amount.trim() ? Number(customer.payment_amount) : null,
    };

    return {
      emit_mode: "draft",
      billing_customer: billingCustomer,
      billing_lines: billingLines,
      document_id: documentId ?? null,
      version_id: versionId ?? null,
      document_type: documentType,
    };
  }

  async function handleSubmit() {
    setError(null);
    setResult(null);
    const payload = validateAndBuildPayload();
    if (!payload) return;

    setIsSubmitting(true);
    try {
      const response = await createGariInvoiceFromCase(caseId, payload);
      setResult(response);
    } catch (issue) {
      setError(issue instanceof Error ? issue.message : "No fue posible crear la factura en Gari Billing.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/45 px-4 py-6 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-label="Facturación del caso"
      onClick={(event) => {
        if (event.currentTarget === event.target) {
          onClose();
        }
      }}
    >
      <div className="w-full max-w-5xl rounded-[2rem] border border-[var(--line)] bg-[var(--panel)] shadow-2xl">
        <div className="flex items-start justify-between gap-4 border-b border-[var(--line)] px-6 py-5">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-secondary">Facturación del caso</p>
            <h2 className="mt-1 text-2xl font-semibold tracking-[-0.04em] text-primary">{caseLabel || `Caso ${caseId}`}</h2>
            <p className="mt-1 text-sm text-secondary">Configura el pagador y los servicios antes de enviar el borrador a Gari Billing.</p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-[var(--line)] text-secondary"
            aria-label="Cerrar"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="grid gap-6 px-6 py-6 xl:grid-cols-[1.05fr_0.95fr]">
          <div className="space-y-6">
            <section className="rounded-[1.5rem] border border-[var(--line)] bg-[var(--panel-soft)] p-5">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-sm font-semibold text-primary">Pagador</p>
                  <p className="text-xs text-secondary">Debes registrar al menos un pagador. La versión actual trabaja con uno solo.</p>
                </div>
                <span className="rounded-full border border-[var(--line)] px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] text-secondary">Draft</span>
              </div>
              <div className="mt-4 grid gap-4 md:grid-cols-2">
                <label className="space-y-1 text-sm">
                  <span className="text-xs font-semibold uppercase tracking-[0.16em] text-secondary">Tipo de cliente</span>
                  <select className="ep-select w-full rounded-2xl px-4 py-3" value={customer.customer_kind} onChange={(event) => updateCustomer("customer_kind", event.target.value as CustomerFormState["customer_kind"])}>
                    {CUSTOMER_KIND_OPTIONS.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </label>
                <label className="space-y-1 text-sm">
                  <span className="text-xs font-semibold uppercase tracking-[0.16em] text-secondary">Tipo de documento</span>
                  <select className="ep-select w-full rounded-2xl px-4 py-3" value={customer.document_type} onChange={(event) => updateCustomer("document_type", event.target.value as BillingCustomerInput["document_type"])}>
                    {DOCUMENT_KIND_OPTIONS.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </label>
                <label className="space-y-1 text-sm">
                  <span className="text-xs font-semibold uppercase tracking-[0.16em] text-secondary">Número de documento</span>
                  <input className="ep-input w-full rounded-2xl px-4 py-3" value={customer.document_number} onChange={(event) => updateCustomer("document_number", event.target.value)} placeholder="123456789" />
                </label>
                <label className="space-y-1 text-sm">
                  <span className="text-xs font-semibold uppercase tracking-[0.16em] text-secondary">Nombre o razón social</span>
                  <input className="ep-input w-full rounded-2xl px-4 py-3" value={customer.legal_name} onChange={(event) => updateCustomer("legal_name", event.target.value)} placeholder="Nombre del pagador" />
                </label>
                <label className="space-y-1 text-sm">
                  <span className="text-xs font-semibold uppercase tracking-[0.16em] text-secondary">Nombre comercial</span>
                  <input className="ep-input w-full rounded-2xl px-4 py-3" value={customer.trade_name} onChange={(event) => updateCustomer("trade_name", event.target.value)} placeholder="Opcional" />
                </label>
                <label className="space-y-1 text-sm">
                  <span className="text-xs font-semibold uppercase tracking-[0.16em] text-secondary">Correo</span>
                  <input className="ep-input w-full rounded-2xl px-4 py-3" value={customer.email} onChange={(event) => updateCustomer("email", event.target.value)} placeholder="correo@dominio.com" />
                </label>
                <label className="space-y-1 text-sm">
                  <span className="text-xs font-semibold uppercase tracking-[0.16em] text-secondary">Teléfono</span>
                  <input className="ep-input w-full rounded-2xl px-4 py-3" value={customer.phone} onChange={(event) => updateCustomer("phone", event.target.value)} placeholder="3001234567" />
                </label>
                <label className="space-y-1 text-sm md:col-span-2">
                  <span className="text-xs font-semibold uppercase tracking-[0.16em] text-secondary">Dirección</span>
                  <input className="ep-input w-full rounded-2xl px-4 py-3" value={customer.address} onChange={(event) => updateCustomer("address", event.target.value)} placeholder="Dirección de facturación" />
                </label>
                <label className="space-y-1 text-sm">
                  <span className="text-xs font-semibold uppercase tracking-[0.16em] text-secondary">Pago %</span>
                  <input className="ep-input w-full rounded-2xl px-4 py-3" value={customer.payment_percentage} onChange={(event) => updateCustomer("payment_percentage", event.target.value)} placeholder="Opcional" inputMode="decimal" />
                </label>
                <label className="space-y-1 text-sm">
                  <span className="text-xs font-semibold uppercase tracking-[0.16em] text-secondary">Pago monto</span>
                  <input className="ep-input w-full rounded-2xl px-4 py-3" value={customer.payment_amount} onChange={(event) => updateCustomer("payment_amount", event.target.value)} placeholder="Opcional" inputMode="decimal" />
                </label>
              </div>
            </section>

            <section className="rounded-[1.5rem] border border-[var(--line)] bg-[var(--panel-soft)] p-5">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-sm font-semibold text-primary">Servicios facturables</p>
                  <p className="text-xs text-secondary">Agrega al menos un servicio. Los campos son editables en esta versión.</p>
                </div>
                <button
                  type="button"
                  onClick={addService}
                  className="inline-flex items-center gap-2 rounded-2xl border border-[var(--line)] px-4 py-2 text-sm font-semibold text-primary"
                >
                  <Plus className="h-4 w-4" />
                  Agregar servicio
                </button>
              </div>

              <div className="mt-4 space-y-4">
                {services.map((service, index) => (
                  <div key={`${service.code}-${index}`} className="rounded-[1.25rem] border border-[var(--line)] bg-[var(--panel)] p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div className="grid flex-1 gap-3 md:grid-cols-2">
                        <label className="space-y-1 text-sm md:col-span-2">
                          <span className="text-xs font-semibold uppercase tracking-[0.16em] text-secondary">Servicio sugerido</span>
                          <select
                            className="ep-select w-full rounded-2xl px-4 py-3"
                            value={service.code}
                            onChange={(event) => applyPreset(index, event.target.value)}
                          >
                            {SERVICE_PRESETS.map((preset) => (
                              <option key={preset.code} value={preset.code}>
                                {preset.label}
                              </option>
                            ))}
                          </select>
                        </label>
                        <label className="space-y-1 text-sm md:col-span-2">
                          <span className="text-xs font-semibold uppercase tracking-[0.16em] text-secondary">Código</span>
                          <input className="ep-input w-full rounded-2xl px-4 py-3" value={service.code} onChange={(event) => updateService(index, "code", event.target.value)} />
                        </label>
                        <label className="space-y-1 text-sm md:col-span-2">
                          <span className="text-xs font-semibold uppercase tracking-[0.16em] text-secondary">Descripción</span>
                          <input className="ep-input w-full rounded-2xl px-4 py-3" value={service.description} onChange={(event) => updateService(index, "description", event.target.value)} />
                        </label>
                        <label className="space-y-1 text-sm">
                          <span className="text-xs font-semibold uppercase tracking-[0.16em] text-secondary">Cantidad</span>
                          <input className="ep-input w-full rounded-2xl px-4 py-3" value={service.quantity} onChange={(event) => updateService(index, "quantity", event.target.value)} inputMode="decimal" />
                        </label>
                        <label className="space-y-1 text-sm">
                          <span className="text-xs font-semibold uppercase tracking-[0.16em] text-secondary">Valor unitario</span>
                          <input className="ep-input w-full rounded-2xl px-4 py-3" value={service.unit_price} onChange={(event) => updateService(index, "unit_price", event.target.value)} inputMode="decimal" />
                        </label>
                        <label className="space-y-1 text-sm">
                          <span className="text-xs font-semibold uppercase tracking-[0.16em] text-secondary">Descuento</span>
                          <input className="ep-input w-full rounded-2xl px-4 py-3" value={service.discount_amount} onChange={(event) => updateService(index, "discount_amount", event.target.value)} inputMode="decimal" />
                        </label>
                        <label className="space-y-1 text-sm">
                          <span className="text-xs font-semibold uppercase tracking-[0.16em] text-secondary">IVA %</span>
                          <input className="ep-input w-full rounded-2xl px-4 py-3" value={service.tax_rate} onChange={(event) => updateService(index, "tax_rate", event.target.value)} inputMode="decimal" />
                        </label>
                        <label className="space-y-1 text-sm">
                          <span className="text-xs font-semibold uppercase tracking-[0.16em] text-secondary">Unidad</span>
                          <input className="ep-input w-full rounded-2xl px-4 py-3" value={service.unit_measure} onChange={(event) => updateService(index, "unit_measure", event.target.value)} />
                        </label>
                        <label className="flex items-center gap-2 text-sm md:col-span-2">
                          <input type="checkbox" checked={service.editable} onChange={(event) => updateService(index, "editable", event.target.checked)} />
                          <span>Editable</span>
                        </label>
                        <label className="space-y-1 text-sm md:col-span-2">
                          <span className="text-xs font-semibold uppercase tracking-[0.16em] text-secondary">Modo de cálculo</span>
                          <select className="ep-select w-full rounded-2xl px-4 py-3" value={service.calculation_mode} onChange={(event) => updateService(index, "calculation_mode", event.target.value)}>
                            <option value="fixed">Fijo</option>
                            <option value="manual">Manual</option>
                            <option value="by_document_amount">Por monto del documento</option>
                          </select>
                        </label>
                      </div>
                      <button
                        type="button"
                        onClick={() => removeService(index)}
                        disabled={services.length <= 1}
                        className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-[var(--line)] text-secondary disabled:opacity-40"
                        aria-label="Eliminar servicio"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          </div>

          <div className="space-y-6">
            <section className="rounded-[1.5rem] border border-[var(--line)] bg-[var(--panel-soft)] p-5">
              <p className="text-sm font-semibold text-primary">Contexto del documento</p>
              <div className="mt-4 space-y-3 text-sm text-secondary">
                <div className="flex items-center justify-between gap-4">
                  <span>case_id</span>
                  <span className="font-semibold text-primary">{caseId}</span>
                </div>
                <div className="flex items-center justify-between gap-4">
                  <span>document_id</span>
                  <span className="font-semibold text-primary">{documentId ?? "Sin documento"}</span>
                </div>
                <div className="flex items-center justify-between gap-4">
                  <span>version_id</span>
                  <span className="font-semibold text-primary">{versionId ?? "Sin versión"}</span>
                </div>
                <div className="flex items-center justify-between gap-4">
                  <span>document_type</span>
                  <span className="rounded-full border border-[var(--line)] px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] text-secondary">{documentType}</span>
                </div>
                <div className="flex items-center justify-between gap-4">
                  <span>emit_mode</span>
                  <span className="rounded-full border border-[var(--line)] px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] text-secondary">draft</span>
                </div>
              </div>
            </section>

            <section className="rounded-[1.5rem] border border-[var(--line)] bg-[var(--panel-soft)] p-5">
              <p className="text-sm font-semibold text-primary">Previsualización</p>
              <div className="mt-4 grid gap-3 sm:grid-cols-3">
                <div className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-4">
                  <p className="text-[11px] uppercase tracking-[0.16em] text-secondary">Subtotal</p>
                  <p className="mt-2 text-lg font-semibold text-primary">${formatAmount(totals.subtotal)}</p>
                </div>
                <div className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-4">
                  <p className="text-[11px] uppercase tracking-[0.16em] text-secondary">IVA</p>
                  <p className="mt-2 text-lg font-semibold text-primary">${formatAmount(totals.tax)}</p>
                </div>
                <div className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-4">
                  <p className="text-[11px] uppercase tracking-[0.16em] text-secondary">Total</p>
                  <p className="mt-2 text-lg font-semibold text-primary">${formatAmount(totals.total)}</p>
                </div>
              </div>
            </section>

            <div className="flex flex-col gap-3">
              {error ? <p className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</p> : null}
              {result ? (
                <section className="rounded-[1.5rem] border border-[var(--line)] bg-[var(--panel-soft)] p-5">
                  <p className="text-sm font-semibold text-primary">Resultado de Gari Billing</p>
                  <div className="mt-4 grid gap-3 sm:grid-cols-2">
                    <div className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-4">
                      <p className="text-[11px] uppercase tracking-[0.16em] text-secondary">invoice_id</p>
                      <p className="mt-2 font-semibold text-primary">{result.invoice_id ?? "Sin dato"}</p>
                    </div>
                    <div className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-4">
                      <p className="text-[11px] uppercase tracking-[0.16em] text-secondary">status</p>
                      <p className="mt-2 font-semibold text-primary">{result.status ?? "Sin estado"}</p>
                    </div>
                    <div className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-4">
                      <p className="text-[11px] uppercase tracking-[0.16em] text-secondary">full_number</p>
                      <p className="mt-2 font-semibold text-primary">{result.full_number ?? "Sin número"}</p>
                    </div>
                    <div className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-4">
                      <p className="text-[11px] uppercase tracking-[0.16em] text-secondary">total</p>
                      <p className="mt-2 font-semibold text-primary">{result.total ?? "Sin total"}</p>
                    </div>
                  </div>
                  {result.error_message ? <p className="mt-4 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{result.error_message}</p> : null}
                </section>
              ) : null}
              <button
                type="button"
                onClick={() => void handleSubmit()}
                disabled={isSubmitting}
                className="inline-flex items-center justify-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white disabled:opacity-60"
              >
                <ReceiptText className="h-4 w-4" />
                {isSubmitting ? "Creando borrador..." : "Crear borrador en Gari Billing"}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
