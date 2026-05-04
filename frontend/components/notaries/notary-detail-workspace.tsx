"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { ArrowLeft } from "lucide-react";
import { getNotary, getUserOptions, updateNotary, type NotaryDetail, type NotaryPayload, type UserOption } from "@/lib/api";
import { formatNotaryOptionLabel } from "@/lib/notaries";

type NotaryDetailTab = "informacion" | "branding" | "usuarios";

type SaveState = {
  info: boolean;
  branding: boolean;
};

type UserOptionWithRoles = UserOption & {
  roles?: string[];
  role_codes?: string[];
};

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
    last_management_at: notary.last_management_at ?? "",
    next_management_at: notary.next_management_at ?? "",
    commercial_notes: notary.commercial_notes ?? "",
    priority: notary.priority,
    lead_source: notary.lead_source ?? "",
    potential: notary.potential ?? "",
    internal_observations: notary.internal_observations ?? "",
    is_active: notary.is_active
  };
}

export function NotaryDetailWorkspace({ notaryId }: { notaryId: number }) {
  const [activeTab, setActiveTab] = useState<NotaryDetailTab>("informacion");
  const [notary, setNotary] = useState<NotaryDetail | null>(null);
  const [formState, setFormState] = useState<NotaryPayload | null>(null);
  const [users, setUsers] = useState<UserOptionWithRoles[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [saveState, setSaveState] = useState<SaveState>({ info: false, branding: false });
  const [feedback, setFeedback] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void loadWorkspace();
  }, [notaryId]);

  async function loadWorkspace() {
    setIsLoading(true);
    setError(null);
    try {
      const [notaryData, usersData] = await Promise.all([getNotary(notaryId), getUserOptions(false)]);
      setNotary(notaryData);
      setFormState(mapNotaryToPayload(notaryData));
      const filteredUsers = (usersData as UserOptionWithRoles[]).filter((user) => user.default_notary_id === notaryId);
      setUsers(filteredUsers);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "No fue posible cargar el detalle operativo.");
    } finally {
      setIsLoading(false);
    }
  }

  function updateField<K extends keyof NotaryPayload>(field: K, value: NotaryPayload[K]) {
    setFormState((current) => (current ? { ...current, [field]: value } : current));
  }

  async function saveNotary(section: keyof SaveState) {
    if (!formState) return;

    setSaveState((current) => ({ ...current, [section]: true }));
    setFeedback(null);
    setError(null);

    try {
      await updateNotary(notaryId, formState);
      await loadWorkspace();
      setFeedback(section === "info" ? "Información operativa guardada correctamente." : "Branding guardado correctamente.");
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "No fue posible guardar los cambios.");
    } finally {
      setSaveState((current) => ({ ...current, [section]: false }));
    }
  }

  const title = useMemo(() => {
    if (!notary) return "Detalle de notaría";
    return formatNotaryOptionLabel(notary);
  }, [notary]);

  if (isLoading || !formState || !notary) {
    return <div className="ep-card rounded-[2rem] p-6 text-secondary">Cargando detalle operativo de la notaría...</div>;
  }

  return (
    <div className="space-y-6">
      <section className="ep-card rounded-[2rem] p-6">
        <Link href="/dashboard/notarias" className="inline-flex items-center gap-2 text-sm font-semibold text-primary">
          <ArrowLeft className="h-4 w-4" />
          ← Volver a Notarías
        </Link>
        <h1 className="mt-4 text-3xl font-semibold tracking-[-0.03em] text-primary sm:text-4xl">{title}</h1>
        <p className="mt-2 text-base text-secondary">Detalle operativo de la notaría</p>
      </section>

      <section className="ep-card rounded-[2rem] p-4 sm:p-6">
        <div className="flex flex-wrap gap-2 rounded-2xl ep-card-muted p-2">
          {([
            { id: "informacion", label: "Información" },
            { id: "branding", label: "Branding" },
            { id: "usuarios", label: "Usuarios" }
          ] as const).map((tab) => (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveTab(tab.id)}
              className={`rounded-xl px-4 py-2 text-sm font-semibold transition ${activeTab === tab.id ? "bg-primary text-white shadow-panel" : "text-secondary hover:bg-white"}`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="mt-6">
          {activeTab === "informacion" ? (
            <div className="space-y-6">
              <div className="grid gap-4 lg:grid-cols-2">
                <label className="grid gap-2 text-sm font-medium text-primary">Departamento<input value={formState.department} onChange={(event) => updateField("department", event.target.value)} className="ep-input h-12 rounded-2xl px-4" /></label>
                <label className="grid gap-2 text-sm font-medium text-primary">Municipio<input value={formState.municipality} onChange={(event) => updateField("municipality", event.target.value)} className="ep-input h-12 rounded-2xl px-4" /></label>
                <label className="grid gap-2 text-sm font-medium text-primary">Etiqueta notaría<input value={formState.notary_label} onChange={(event) => updateField("notary_label", event.target.value)} className="ep-input h-12 rounded-2xl px-4" /></label>
                <label className="grid gap-2 text-sm font-medium text-primary">Notario/a actual<input value={formState.current_notary_name} onChange={(event) => updateField("current_notary_name", event.target.value)} className="ep-input h-12 rounded-2xl px-4" /></label>
                <label className="grid gap-2 text-sm font-medium text-primary">Dirección<input value={formState.address} onChange={(event) => updateField("address", event.target.value)} className="ep-input h-12 rounded-2xl px-4" /></label>
                <label className="grid gap-2 text-sm font-medium text-primary">Teléfono<input value={formState.phone} onChange={(event) => updateField("phone", event.target.value)} className="ep-input h-12 rounded-2xl px-4" /></label>
                <label className="grid gap-2 text-sm font-medium text-primary">Correo fuente<input type="email" value={formState.email} onChange={(event) => updateField("email", event.target.value)} className="ep-input h-12 rounded-2xl px-4" /></label>
                <label className="grid gap-2 text-sm font-medium text-primary">Estado activo<select value={String(formState.is_active)} onChange={(event) => updateField("is_active", event.target.value === "true")} className="ep-select h-12 rounded-2xl px-4"><option value="true">Activa</option><option value="false">Inactiva</option></select></label>
              </div>

              <label className="grid gap-2 text-sm font-medium text-primary">Horario<textarea value={formState.business_hours} onChange={(event) => updateField("business_hours", event.target.value)} rows={4} className="ep-input rounded-2xl px-4 py-3" /></label>

              <div>
                <button
                  type="button"
                  onClick={() => void saveNotary("info")}
                  disabled={saveState.info}
                  className="rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white shadow-panel disabled:cursor-not-allowed disabled:opacity-70"
                >
                  {saveState.info ? "Guardando..." : "Guardar cambios"}
                </button>
              </div>
            </div>
          ) : null}

          {activeTab === "branding" ? (
            <div className="space-y-6">
              <div className="grid gap-4 lg:grid-cols-2">
                <label className="grid gap-2 text-sm font-medium text-primary">Logo URL<input value={formState.logo_url} onChange={(event) => updateField("logo_url", event.target.value)} className="ep-input h-12 rounded-2xl px-4" /></label>
                <label className="grid gap-2 text-sm font-medium text-primary">Color base<input value={formState.base_color} onChange={(event) => updateField("base_color", event.target.value)} className="ep-input h-12 rounded-2xl px-4" /></label>
                <label className="grid gap-2 text-sm font-medium text-primary">Color primario<input value={formState.primary_color} onChange={(event) => updateField("primary_color", event.target.value)} className="ep-input h-12 rounded-2xl px-4" /></label>
                <label className="grid gap-2 text-sm font-medium text-primary">Color secundario<input value={formState.secondary_color} onChange={(event) => updateField("secondary_color", event.target.value)} className="ep-input h-12 rounded-2xl px-4" /></label>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div className="ep-card-soft rounded-2xl p-4">
                  <p className="text-xs uppercase tracking-[0.2em] text-secondary">Vista previa primario</p>
                  <div className="mt-3 h-12 rounded-xl border border-black/10" style={{ backgroundColor: formState.primary_color }} />
                </div>
                <div className="ep-card-soft rounded-2xl p-4">
                  <p className="text-xs uppercase tracking-[0.2em] text-secondary">Vista previa secundario</p>
                  <div className="mt-3 h-12 rounded-xl border border-black/10" style={{ backgroundColor: formState.secondary_color }} />
                </div>
              </div>

              <label className="grid gap-2 text-sm font-medium text-primary">Datos institucionales<textarea value={formState.institutional_data} onChange={(event) => updateField("institutional_data", event.target.value)} rows={5} className="ep-input rounded-2xl px-4 py-3" /></label>

              <div>
                <button
                  type="button"
                  onClick={() => void saveNotary("branding")}
                  disabled={saveState.branding}
                  className="rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white shadow-panel disabled:cursor-not-allowed disabled:opacity-70"
                >
                  {saveState.branding ? "Guardando..." : "Guardar branding"}
                </button>
              </div>
            </div>
          ) : null}

          {activeTab === "usuarios" ? (
            <div className="space-y-3">
              {users.length === 0 ? <div className="ep-card-muted rounded-2xl px-4 py-4 text-sm text-secondary">No hay usuarios asignados a esta notaría</div> : null}
              {users.map((user) => (
                <div key={user.id} className="ep-card-soft rounded-2xl p-4">
                  <p className="text-base font-semibold text-primary">{user.full_name}</p>
                  <p className="mt-1 text-sm text-secondary">{user.email}</p>
                  <p className="mt-2 text-sm text-secondary">Rol: {(user.roles ?? user.role_codes ?? []).join(", ") || "Sin rol"}</p>
                  <p className="mt-1 text-sm text-secondary">Estado: {user.is_active ? "Activo" : "Inactivo"}</p>
                </div>
              ))}
            </div>
          ) : null}
        </div>

        {feedback ? <div className="mt-5 rounded-2xl bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{feedback}</div> : null}
        {error ? <div className="mt-5 rounded-2xl bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</div> : null}
      </section>
    </div>
  );
}
