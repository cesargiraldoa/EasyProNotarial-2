"use client";

import Link from "next/link";
import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  ArrowLeft,
  Clock3,
  Save,
  ShieldCheck,
  UserRound
} from "lucide-react";
import {
  createCommercialActivity,
  getNotary,
  getUserOptions,
  updateNotary,
  type CommercialActivityPayload,
  type NotaryDetail,
  type NotaryPayload,
  type UserOption
} from "@/lib/api";
import { formatDateTime, getCurrentBogotaDateTimeLocalValue, toDateTimeLocalValue } from "@/lib/datetime";

const commercialStatuses = [
  "prospecto",
  "contactado",
  "en seguimiento",
  "reunión agendada",
  "propuesta enviada",
  "negociación",
  "cerrado ganado",
  "cerrado perdido",
  "no interesado"
];
const priorities = ["baja", "media", "alta", "crítica"];
const potentials = ["bajo", "medio", "alto", "estratégico"];


function mapNotaryToPayload(notary: NotaryDetail): NotaryPayload {
  return {
    legal_name: notary.legal_name,
    commercial_name: notary.commercial_name,
    city: notary.city,
    department: notary.department,
    municipality: notary.municipality,
    notary_label: notary.notary_label,
    address: notary.address ?? "",
    phone: notary.phone ?? "",
    email: notary.email ?? "",
    current_notary_name: notary.current_notary_name ?? "",
    business_hours: notary.business_hours ?? "",
    logo_url: notary.logo_url ?? "",
    primary_color: notary.primary_color,
    secondary_color: notary.secondary_color,
    base_color: notary.base_color ?? "#F4F7FB",
    institutional_data: notary.institutional_data,
    commercial_status: notary.commercial_status,
    commercial_owner: notary.commercial_owner ?? "",
    commercial_owner_user_id: notary.commercial_owner_user_id ?? null,
    main_contact_name: notary.main_contact_name ?? "",
    main_contact_title: notary.main_contact_title ?? "",
    commercial_phone: notary.commercial_phone ?? "",
    commercial_email: notary.commercial_email ?? "",
    last_management_at: toDateTimeLocalValue(notary.last_management_at, { strategy: "bogota" }),
    next_management_at: toDateTimeLocalValue(notary.next_management_at, { strategy: "bogota" }),
    commercial_notes: notary.commercial_notes ?? "",
    priority: notary.priority,
    lead_source: notary.lead_source ?? "",
    potential: notary.potential ?? "",
    internal_observations: notary.internal_observations ?? "",
    is_active: notary.is_active
  };
}

const emptyActivity: CommercialActivityPayload = {
  occurred_at: getCurrentBogotaDateTimeLocalValue(),
  management_type: "Llamada",
  comment: "",
  responsible: "",
  responsible_user_id: null,
  result: "",
  next_action: ""
};

function auditLabel(eventType: string, fieldName?: string | null) {
  if (eventType === "status_changed" && fieldName === "commercial_status") return "Cambio de estado comercial";
  if (eventType === "status_changed" && fieldName === "is_active") return "Cambio de estado activo";
  if (eventType === "owner_changed") return "Cambio de responsable";
  if (eventType === "activity_added") return "Gestión agregada";
  return eventType;
}

export function NotaryCrmWorkspace({ notaryId }: { notaryId: number }) {
  const [notary, setNotary] = useState<NotaryDetail | null>(null);
  const [formState, setFormState] = useState<NotaryPayload | null>(null);
  const [activityState, setActivityState] = useState<CommercialActivityPayload>(emptyActivity);
  const [userOptions, setUserOptions] = useState<UserOption[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isAddingActivity, setIsAddingActivity] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void loadWorkspace();
  }, [notaryId]);

  async function loadWorkspace() {
    setIsLoading(true);
    setError(null);
    try {
      const [notaryData, usersData] = await Promise.all([getNotary(notaryId), getUserOptions(true)]);
      setNotary(notaryData);
      setFormState(mapNotaryToPayload(notaryData));
      setUserOptions(usersData);
      setActivityState((current) => ({
        ...current,
        responsible_user_id: notaryData.commercial_owner_user_id ?? current.responsible_user_id,
        responsible: notaryData.commercial_owner_display ?? current.responsible
      }));
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "No fue posible cargar la notaría.");
    } finally {
      setIsLoading(false);
    }
  }

  function updateField<K extends keyof NotaryPayload>(field: K, value: NotaryPayload[K]) {
    setFormState((current) => (current ? { ...current, [field]: value } : current));
  }

  function updateActivityField<K extends keyof CommercialActivityPayload>(field: K, value: CommercialActivityPayload[K]) {
    setActivityState((current) => ({ ...current, [field]: value }));
  }

  function handleOwnerSelection(value: string) {
    const userId = value ? Number(value) : null;
    const selectedUser = userOptions.find((user) => user.id === userId);
    updateField("commercial_owner_user_id", userId);
    updateField("commercial_owner", selectedUser?.full_name ?? "");
  }

  function handleActivityResponsibleSelection(value: string) {
    const userId = value ? Number(value) : null;
    const selectedUser = userOptions.find((user) => user.id === userId);
    updateActivityField("responsible_user_id", userId);
    updateActivityField("responsible", selectedUser?.full_name ?? "");
  }

  async function handleSave(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!formState) return;
    setIsSaving(true);
    setFeedback(null);
    setError(null);
    try {
      await updateNotary(notaryId, formState);
      await loadWorkspace();
      setFeedback("Notaría y CRM actualizados correctamente.");
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "No fue posible guardar la notaría.");
    } finally {
      setIsSaving(false);
    }
  }

  async function handleAddActivity(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsAddingActivity(true);
    setFeedback(null);
    setError(null);
    try {
      await createCommercialActivity(notaryId, activityState);
      await loadWorkspace();
      setActivityState({
        ...emptyActivity,
        responsible_user_id: formState?.commercial_owner_user_id ?? null,
        responsible: formState?.commercial_owner ?? ""
      });
      setFeedback("Gestión comercial registrada correctamente.");
    } catch (activityError) {
      setError(activityError instanceof Error ? activityError.message : "No fue posible registrar la gestión.");
    } finally {
      setIsAddingActivity(false);
    }
  }

  const nextActionSummary = useMemo(
    () => notary?.commercial_activities.find((activity) => activity.next_action)?.next_action ?? "Sin próxima acción registrada.",
    [notary]
  );

  if (isLoading || !formState || !notary) {
    return <div className="ep-card rounded-[2rem] p-6 text-secondary">Cargando detalle de notaría...</div>;
  }

  return (
    <div className="space-y-6">
      <section className="ep-card rounded-[2rem] p-6">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
          <div className="max-w-3xl">
            <Link href="/dashboard/comercial" className="inline-flex items-center gap-2 text-sm font-semibold text-primary">
              <ArrowLeft className="h-4 w-4" />
              Volver a Comercial
            </Link>
            <p className="mt-4 text-sm font-semibold uppercase tracking-[0.22em] text-accent">Gestión comercial</p>
            <h1 className="mt-2 text-3xl font-semibold tracking-[-0.05em] text-primary sm:text-4xl">{notary.notary_label}</h1>
            <p className="mt-3 text-base leading-7 text-secondary">
              Registro comercial y seguimiento de gestiones.
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-2 lg:w-[420px]">
            <div className="ep-card-muted rounded-[1.5rem] p-4"><p className="text-xs uppercase tracking-[0.2em] text-secondary">Estado CRM</p><p className="mt-2 text-xl font-semibold text-primary">{notary.commercial_status}</p></div>
            <div className="ep-card-muted rounded-[1.5rem] p-4"><p className="text-xs uppercase tracking-[0.2em] text-secondary">Prioridad</p><p className="mt-2 text-xl font-semibold text-primary">{notary.priority}</p></div>
            <div className="ep-card-muted rounded-[1.5rem] p-4"><p className="text-xs uppercase tracking-[0.2em] text-secondary">Responsable</p><p className="mt-2 text-lg font-semibold text-primary">{notary.commercial_owner_display || "Sin asignar"}</p></div>
            <div className="rounded-[1.5rem] bg-primary p-4 text-white shadow-panel"><p className="text-xs uppercase tracking-[0.2em] text-white/70">Gestiones</p><p className="mt-2 text-xl font-semibold">{notary.activity_count}</p></div>
          </div>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[minmax(0,1.08fr)_minmax(380px,0.92fr)]">
        <form onSubmit={handleSave} className="space-y-6 ep-card rounded-[2rem] p-6">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-secondary">Editor integral</p>
              <h2 className="mt-2 text-2xl font-semibold text-primary">Gestión CRM comercial</h2>
            </div>
            <button type="submit" disabled={isSaving} className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white shadow-panel disabled:cursor-not-allowed disabled:opacity-70">
              <Save className="h-4 w-4" />
              {isSaving ? "Guardando..." : "Guardar cambios"}
            </button>
          </div>

          <div className="grid gap-6">
            <div className="grid gap-4 lg:grid-cols-2">
              <label className="grid gap-2 text-sm font-medium text-primary">Departamento<input value={formState.department} onChange={(event) => updateField("department", event.target.value)} className="ep-input h-12 rounded-2xl px-4" /></label>
              <label className="grid gap-2 text-sm font-medium text-primary">Municipio<input value={formState.municipality} onChange={(event) => updateField("municipality", event.target.value)} className="ep-input h-12 rounded-2xl px-4" /></label>
              <label className="grid gap-2 text-sm font-medium text-primary">Etiqueta de notaría<input value={formState.notary_label} onChange={(event) => updateField("notary_label", event.target.value)} className="ep-input h-12 rounded-2xl px-4" /></label>
              <label className="grid gap-2 text-sm font-medium text-primary">Notario/a actual<input value={formState.current_notary_name} onChange={(event) => updateField("current_notary_name", event.target.value)} className="ep-input h-12 rounded-2xl px-4" /></label>
              <label className="grid gap-2 text-sm font-medium text-primary">Dirección<input value={formState.address} onChange={(event) => updateField("address", event.target.value)} className="ep-input h-12 rounded-2xl px-4" /></label>
              <label className="grid gap-2 text-sm font-medium text-primary">Teléfono fuente<input value={formState.phone} onChange={(event) => updateField("phone", event.target.value)} className="ep-input h-12 rounded-2xl px-4" /></label>
              <label className="grid gap-2 text-sm font-medium text-primary">Correo fuente<input type="email" value={formState.email} onChange={(event) => updateField("email", event.target.value)} className="ep-input h-12 rounded-2xl px-4" /></label>
              <label className="grid gap-2 text-sm font-medium text-primary">Horario<textarea value={formState.business_hours} onChange={(event) => updateField("business_hours", event.target.value)} rows={3} className="ep-textarea rounded-2xl px-4 py-3" /></label>
            </div>

            <label className="grid gap-2 text-sm font-medium text-primary">Estado activo<select value={String(formState.is_active)} onChange={(event) => updateField("is_active", event.target.value === "true")} className="ep-select h-12 rounded-2xl px-4"><option value="true">Activa</option><option value="false">Inactiva</option></select></label>
          </div>

          <label className="grid gap-2 text-sm font-medium text-primary">Datos institucionales<textarea value={formState.institutional_data} onChange={(event) => updateField("institutional_data", event.target.value)} rows={4} className="ep-textarea rounded-2xl px-4 py-3" /></label>

          <div className="grid gap-4 lg:grid-cols-2">
            <label className="grid gap-2 text-sm font-medium text-primary">Estado comercial<select value={formState.commercial_status} onChange={(event) => updateField("commercial_status", event.target.value)} className="ep-select h-12 rounded-2xl px-4">{commercialStatuses.map((item) => <option key={item} value={item}>{item}</option>)}</select></label>
            <label className="grid gap-2 text-sm font-medium text-primary">Responsable comercial<select value={formState.commercial_owner_user_id?.toString() ?? ""} onChange={(event) => handleOwnerSelection(event.target.value)} className="ep-select h-12 rounded-2xl px-4"><option value="">Sin asignar por usuario</option>{userOptions.map((user) => <option key={user.id} value={user.id}>{user.full_name}</option>)}</select></label>
            <label className="grid gap-2 text-sm font-medium text-primary">Responsable heredado / respaldo<input value={formState.commercial_owner} onChange={(event) => updateField("commercial_owner", event.target.value)} className="ep-input h-12 rounded-2xl px-4" /></label>
            <label className="grid gap-2 text-sm font-medium text-primary">Contacto principal<input value={formState.main_contact_name} onChange={(event) => updateField("main_contact_name", event.target.value)} className="ep-input h-12 rounded-2xl px-4" /></label>
            <label className="grid gap-2 text-sm font-medium text-primary">Cargo del contacto<input value={formState.main_contact_title} onChange={(event) => updateField("main_contact_title", event.target.value)} className="ep-input h-12 rounded-2xl px-4" /></label>
            <label className="grid gap-2 text-sm font-medium text-primary">Celular comercial<input value={formState.commercial_phone} onChange={(event) => updateField("commercial_phone", event.target.value)} className="ep-input h-12 rounded-2xl px-4" /></label>
            <label className="grid gap-2 text-sm font-medium text-primary">Correo comercial<input type="email" value={formState.commercial_email} onChange={(event) => updateField("commercial_email", event.target.value)} className="ep-input h-12 rounded-2xl px-4" /></label>
            <label className="grid gap-2 text-sm font-medium text-primary">Última gestión<input type="datetime-local" value={formState.last_management_at} onChange={(event) => updateField("last_management_at", event.target.value)} className="ep-input h-12 rounded-2xl px-4" /></label>
            <label className="grid gap-2 text-sm font-medium text-primary">Próxima gestión<input type="datetime-local" value={formState.next_management_at} onChange={(event) => updateField("next_management_at", event.target.value)} className="ep-input h-12 rounded-2xl px-4" /></label>
            <label className="grid gap-2 text-sm font-medium text-primary">Prioridad<select value={formState.priority} onChange={(event) => updateField("priority", event.target.value)} className="ep-select h-12 rounded-2xl px-4">{priorities.map((item) => <option key={item} value={item}>{item}</option>)}</select></label>
            <label className="grid gap-2 text-sm font-medium text-primary">Origen del lead<input value={formState.lead_source} onChange={(event) => updateField("lead_source", event.target.value)} className="ep-input h-12 rounded-2xl px-4" /></label>
            <label className="grid gap-2 text-sm font-medium text-primary">Potencial<select value={formState.potential} onChange={(event) => updateField("potential", event.target.value)} className="ep-select h-12 rounded-2xl px-4"><option value="">Sin definir</option>{potentials.map((item) => <option key={item} value={item}>{item}</option>)}</select></label>
          </div>

          <label className="grid gap-2 text-sm font-medium text-primary">Notas comerciales<textarea value={formState.commercial_notes} onChange={(event) => updateField("commercial_notes", event.target.value)} rows={4} className="ep-textarea rounded-2xl px-4 py-3" /></label>
          <label className="grid gap-2 text-sm font-medium text-primary">Observaciones internas<textarea value={formState.internal_observations} onChange={(event) => updateField("internal_observations", event.target.value)} rows={4} className="ep-textarea rounded-2xl px-4 py-3" /></label>

          {feedback ? <div className="ep-kpi-success rounded-2xl px-4 py-3 text-sm">{feedback}</div> : null}
          {error ? <div className="ep-kpi-critical rounded-2xl px-4 py-3 text-sm">{error}</div> : null}
        </form>

        <aside className="space-y-6">
          <div className="ep-card rounded-[2rem] p-6">
            <div className="flex items-center gap-3"><UserRound className="h-5 w-5 text-primary" /><div><p className="text-xs uppercase tracking-[0.2em] text-secondary">Actividad comercial</p><h2 className="text-2xl font-semibold text-primary">Registrar gestión</h2></div></div>
            <form onSubmit={handleAddActivity} className="mt-5 space-y-4">
              <label className="grid gap-2 text-sm font-medium text-primary">Fecha<input type="datetime-local" value={activityState.occurred_at} onChange={(event) => updateActivityField("occurred_at", event.target.value)} className="ep-input h-12 rounded-2xl px-4" /></label>
              <label className="grid gap-2 text-sm font-medium text-primary">Tipo de gestión<input value={activityState.management_type} onChange={(event) => updateActivityField("management_type", event.target.value)} className="ep-input h-12 rounded-2xl px-4" /></label>
              <label className="grid gap-2 text-sm font-medium text-primary">Responsable<select value={activityState.responsible_user_id?.toString() ?? ""} onChange={(event) => handleActivityResponsibleSelection(event.target.value)} className="ep-select h-12 rounded-2xl px-4"><option value="">Sin usuario asignado</option>{userOptions.map((user) => <option key={user.id} value={user.id}>{user.full_name}</option>)}</select></label>
              <label className="grid gap-2 text-sm font-medium text-primary">Responsable textual<input value={activityState.responsible} onChange={(event) => updateActivityField("responsible", event.target.value)} className="ep-input h-12 rounded-2xl px-4" /></label>
              <label className="grid gap-2 text-sm font-medium text-primary">Comentario<textarea value={activityState.comment} onChange={(event) => updateActivityField("comment", event.target.value)} rows={4} className="ep-textarea rounded-2xl px-4 py-3" /></label>
              <label className="grid gap-2 text-sm font-medium text-primary">Resultado<input value={activityState.result} onChange={(event) => updateActivityField("result", event.target.value)} className="ep-input h-12 rounded-2xl px-4" /></label>
              <label className="grid gap-2 text-sm font-medium text-primary">Próxima acción<input value={activityState.next_action} onChange={(event) => updateActivityField("next_action", event.target.value)} className="ep-input h-12 rounded-2xl px-4" /></label>
              <button type="submit" disabled={isAddingActivity} className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white shadow-panel disabled:opacity-70"><Clock3 className="h-4 w-4" />{isAddingActivity ? "Registrando..." : "Agregar gestión"}</button>
            </form>
          </div>

          <div className="ep-card rounded-[2rem] p-6">
            <div className="flex items-center gap-3"><ShieldCheck className="h-5 w-5 text-primary" /><div><p className="text-xs uppercase tracking-[0.2em] text-secondary">Resumen operativo</p><h2 className="text-2xl font-semibold text-primary">Próxima acción</h2></div></div>
            <p className="mt-5 rounded-[1.4rem] bg-[var(--panel-soft)] px-4 py-4 text-sm leading-6 text-secondary">{nextActionSummary}</p>
          </div>
        </aside>
      </section>

      <section className="grid gap-6 xl:grid-cols-2">
        <div className="ep-card rounded-[2rem] p-6">
          <div className="flex items-center gap-3"><Clock3 className="h-5 w-5 text-primary" /><div><p className="text-xs uppercase tracking-[0.2em] text-secondary">Historial de gestiones</p><h2 className="text-2xl font-semibold text-primary">Seguimiento comercial</h2></div></div>
          <div className="mt-6 space-y-3">
            {notary.commercial_activities.length === 0 ? <div className="ep-card-muted rounded-[1.4rem] px-4 py-4 text-sm text-secondary">No hay gestiones registradas todavía.</div> : null}
            {notary.commercial_activities.map((activity) => (
              <div key={activity.id} className="ep-card-soft rounded-[1.5rem] p-4">
                <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                  <p className="text-sm font-semibold text-primary">{activity.management_type}</p>
                  <span className="text-xs text-secondary">{formatDateTime(activity.occurred_at, { strategy: "bogota" })}</span>
                </div>
                <p className="mt-2 text-sm text-secondary">Responsable: {activity.responsible_user_name || activity.responsible || "Sin definir"}</p>
                {activity.comment ? <p className="mt-2 text-sm leading-6 text-secondary">{activity.comment}</p> : null}
                {activity.result ? <p className="mt-2 text-sm text-secondary"><span className="font-semibold text-primary">Resultado:</span> {activity.result}</p> : null}
                {activity.next_action ? <p className="mt-2 text-sm text-secondary"><span className="font-semibold text-primary">Próxima acción:</span> {activity.next_action}</p> : null}
              </div>
            ))}
          </div>
        </div>

        <div className="ep-card rounded-[2rem] p-6">
          <div className="flex items-center gap-3"><ShieldCheck className="h-5 w-5 text-primary" /><div><p className="text-xs uppercase tracking-[0.2em] text-secondary">Auditoría básica</p><h2 className="text-2xl font-semibold text-primary">Cambios relevantes</h2></div></div>
          <div className="mt-6 space-y-3">
            {notary.crm_audit_logs.length === 0 ? <div className="ep-card-muted rounded-[1.4rem] px-4 py-4 text-sm text-secondary">No hay eventos de auditoría registrados todavía.</div> : null}
            {notary.crm_audit_logs.map((item) => (
              <div key={item.id} className="ep-card-soft rounded-[1.5rem] p-4">
                <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                  <p className="text-sm font-semibold text-primary">{auditLabel(item.event_type, item.field_name)}</p>
                  <span className="text-xs text-secondary">{formatDateTime(item.created_at)}</span>
                </div>
                <p className="mt-2 text-sm text-secondary">Actor: {item.actor_user_name || "Sistema"}</p>
                {(item.old_value || item.new_value) ? <p className="mt-2 text-sm text-secondary">{item.old_value || "-"} → {item.new_value || "-"}</p> : null}
                {item.comment ? <p className="mt-2 text-sm leading-6 text-secondary">{item.comment}</p> : null}
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
