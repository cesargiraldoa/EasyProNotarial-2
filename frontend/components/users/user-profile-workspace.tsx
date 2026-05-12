"use client";

import { useEffect, useState } from "react";
import { BadgeCheck, Building2, Mail, ShieldCheck, UserRound } from "lucide-react";
import { getCurrentUser, updateCurrentUserProfile, type CurrentUser } from "@/lib/api";

type ProfileFormState = {
  full_name: string;
  phone: string;
  job_title: string;
  password: string;
  confirm_password: string;
};

type ProfileFeedback = {
  kind: "success" | "error";
  message: string;
};

const EMPTY_FORM: ProfileFormState = {
  full_name: "",
  phone: "",
  job_title: "",
  password: "",
  confirm_password: ""
};

export function UserProfileWorkspace() {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [formState, setFormState] = useState<ProfileFormState>(EMPTY_FORM);
  const [error, setError] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<ProfileFeedback | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    let cancelled = false;
    async function loadProfile() {
      setIsLoading(true);
      setError(null);
      try {
        const response = await getCurrentUser();
        if (!cancelled) {
          setUser(response);
          setFormState({
            full_name: response.full_name ?? "",
            phone: response.phone ?? "",
            job_title: response.job_title ?? "",
            password: "",
            confirm_password: ""
          });
        }
      } catch (loadError) {
        if (!cancelled) {
          setError(loadError instanceof Error ? loadError.message : "No fue posible cargar el perfil.");
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    void loadProfile();
    return () => {
      cancelled = true;
    };
  }, []);

  function updateField<K extends keyof ProfileFormState>(key: K, value: ProfileFormState[K]) {
    setFormState((current) => ({ ...current, [key]: value }));
    setFeedback(null);
    setError(null);
  }

  async function handleSave() {
    if (!user) {
      return;
    }
    const fullName = formState.full_name.trim();
    if (!fullName) {
      setFeedback({ kind: "error", message: "El nombre completo es obligatorio." });
      return;
    }
    const password = formState.password.trim();
    const confirmPassword = formState.confirm_password.trim();
    if (password !== confirmPassword) {
      setFeedback({ kind: "error", message: "La contraseña y su confirmación no coinciden." });
      return;
    }
    if (password.length > 0 && password.length < 8) {
      setFeedback({ kind: "error", message: "La nueva contraseña debe tener al menos 8 caracteres." });
      return;
    }

    setIsSaving(true);
    setFeedback(null);
    try {
      await updateCurrentUserProfile({
        full_name: formState.full_name,
        phone: formState.phone.trim() === "" ? null : formState.phone,
        job_title: formState.job_title.trim() === "" ? null : formState.job_title,
        password: password === "" ? null : password
      });
      const refreshedUser = await getCurrentUser();
      setUser(refreshedUser);
      setFormState({
        full_name: refreshedUser.full_name ?? "",
        phone: refreshedUser.phone ?? "",
        job_title: refreshedUser.job_title ?? "",
        password: "",
        confirm_password: ""
      });
      setFeedback({ kind: "success", message: "Perfil actualizado correctamente." });
    } catch (saveError) {
      setFeedback({
        kind: "error",
        message: saveError instanceof Error ? saveError.message : "No fue posible guardar el perfil."
      });
    } finally {
      setIsSaving(false);
    }
  }

  if (error) {
    return <div className="ep-kpi-critical rounded-[2rem] px-6 py-5 text-sm">{error}</div>;
  }

  if (isLoading || !user) {
    return <div className="ep-card rounded-[2rem] p-6 text-secondary">Cargando perfil...</div>;
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[minmax(0,1.05fr)_360px]">
      <section className="ep-card rounded-[2rem] p-6 sm:p-7">
        <p className="text-xs uppercase tracking-[0.2em] text-secondary">Perfil</p>
        <h1 className="mt-2 text-3xl font-semibold tracking-[-0.05em] text-primary">{user.full_name}</h1>
        <p className="mt-3 max-w-2xl text-base leading-7 text-secondary">Perfil base de operación para validar sesión, roles activos y contexto notarial dentro de EasyPro 2.</p>

        <div className="mt-6 grid gap-4 md:grid-cols-2">
          <div className="ep-card-muted rounded-[1.5rem] p-5">
            <div className="flex items-center gap-3">
              <div className="rounded-2xl bg-primary/10 p-3"><Mail className="h-5 w-5 text-primary" /></div>
              <div>
                <p className="text-xs uppercase tracking-[0.18em] text-secondary">Correo</p>
                <p className="mt-1 text-sm font-semibold text-primary">{user.email}</p>
              </div>
            </div>
          </div>
          <div className="ep-card-muted rounded-[1.5rem] p-5">
            <div className="flex items-center gap-3">
              <div className="rounded-2xl bg-primary/10 p-3"><BadgeCheck className="h-5 w-5 text-primary" /></div>
              <div>
                <p className="text-xs uppercase tracking-[0.18em] text-secondary">Estado</p>
                <p className="mt-1 text-sm font-semibold text-primary">{user.is_active ? "Activo" : "Inactivo"}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-6 rounded-[1.7rem] border border-line bg-[var(--panel)] p-5">
          <p className="text-sm font-semibold text-primary">Editar datos personales</p>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <div className="md:col-span-2">
              <label className="mb-2 block text-sm font-medium text-primary">Nombre completo</label>
              <input
                value={formState.full_name}
                onChange={(event) => updateField("full_name", event.target.value)}
                className="ep-input h-12 w-full rounded-2xl px-4"
              />
            </div>
            <div>
              <label className="mb-2 block text-sm font-medium text-primary">Teléfono</label>
              <input
                value={formState.phone}
                onChange={(event) => updateField("phone", event.target.value)}
                className="ep-input h-12 w-full rounded-2xl px-4"
              />
            </div>
            <div>
              <label className="mb-2 block text-sm font-medium text-primary">Cargo</label>
              <input
                value={formState.job_title}
                onChange={(event) => updateField("job_title", event.target.value)}
                className="ep-input h-12 w-full rounded-2xl px-4"
              />
            </div>
            <div className="md:col-span-2">
              <label className="mb-2 block text-sm font-medium text-primary">Nueva contraseña</label>
              <input
                type="password"
                value={formState.password}
                onChange={(event) => updateField("password", event.target.value)}
                placeholder="Deja vacío para conservar la contraseña actual"
                className="ep-input h-12 w-full rounded-2xl px-4"
              />
            </div>
            <div className="md:col-span-2">
              <label className="mb-2 block text-sm font-medium text-primary">Confirmar contraseña</label>
              <input
                type="password"
                value={formState.confirm_password}
                onChange={(event) => updateField("confirm_password", event.target.value)}
                placeholder="Repite la nueva contraseña"
                className="ep-input h-12 w-full rounded-2xl px-4"
              />
            </div>
          </div>
          <div className="mt-4 flex flex-wrap items-center gap-3">
            <button
              type="button"
              onClick={() => void handleSave()}
              disabled={isSaving}
              className="rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isSaving ? "Guardando..." : "Guardar cambios"}
            </button>
            <p className="text-xs text-secondary">No puedes cambiar correo, roles, notaría, estado ni asignaciones desde este perfil.</p>
          </div>
          {feedback ? (
            <div
              className={`mt-4 rounded-2xl px-4 py-3 text-sm ${
                feedback.kind === "success"
                  ? "border border-emerald-200 bg-emerald-50 text-emerald-700"
                  : "border border-rose-200 bg-rose-50 text-rose-700"
              }`}
            >
              {feedback.message}
            </div>
          ) : null}
        </div>

        <div className="ep-filter-panel mt-6 rounded-[1.7rem] p-5">
          <p className="text-sm font-semibold text-primary">Roles vigentes</p>
          <div className="mt-4 flex flex-wrap gap-2">
            {user.roles.map((role) => (
              <span key={role} className="ep-badge rounded-full px-3 py-2 text-xs font-semibold text-primary">{role}</span>
            ))}
          </div>
        </div>
      </section>

      <aside className="space-y-6">
        <section className="ep-card rounded-[2rem] p-6">
          <div className="flex items-center gap-3">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary text-lg font-semibold text-white">
              {user.full_name.split(" ").slice(0, 2).map((item) => item[0]).join("").toUpperCase()}
            </div>
            <div>
              <p className="text-lg font-semibold text-primary">{user.full_name}</p>
              <p className="text-sm text-secondary">Sesión autenticada</p>
            </div>
          </div>
          <div className="mt-5 space-y-3">
            <div className="ep-card-muted rounded-2xl px-4 py-3">
              <p className="text-xs uppercase tracking-[0.18em] text-secondary">Correo</p>
              <p className="mt-1 text-sm font-semibold text-primary">{user.email}</p>
            </div>
            <div className="ep-card-muted rounded-2xl px-4 py-3">
              <p className="text-xs uppercase tracking-[0.18em] text-secondary">Teléfono</p>
              <p className="mt-1 text-sm font-semibold text-primary">{user.phone || "No registrado"}</p>
            </div>
            <div className="ep-card-muted rounded-2xl px-4 py-3">
              <p className="text-xs uppercase tracking-[0.18em] text-secondary">Cargo</p>
              <p className="mt-1 text-sm font-semibold text-primary">{user.job_title || "No registrado"}</p>
            </div>
            {user.assignments.length === 0 ? (
              <div className="ep-card-muted rounded-2xl px-4 py-3 text-sm text-secondary">Sin asignaciones específicas registradas.</div>
            ) : (
              user.assignments.map((assignment) => (
                <div key={assignment.id} className="ep-card-muted rounded-2xl px-4 py-3">
                  <p className="text-sm font-semibold text-primary">{assignment.role_name}</p>
                  <p className="mt-1 text-sm text-secondary">{assignment.notary_label || "Ámbito global"}</p>
                </div>
              ))
            )}
          </div>
        </section>

        <section className="ep-card rounded-[2rem] p-6">
          <p className="text-xs uppercase tracking-[0.2em] text-secondary">Contexto operativo</p>
          <div className="mt-4 space-y-3">
            <div className="flex items-start gap-3 ep-card-muted rounded-2xl px-4 py-3 text-sm text-primary"><UserRound className="mt-0.5 h-4 w-4 text-primary" />Responsable actual del entorno autenticado.</div>
            <div className="flex items-start gap-3 ep-card-muted rounded-2xl px-4 py-3 text-sm text-primary"><Building2 className="mt-0.5 h-4 w-4 text-primary" />Notaría por defecto: {user.default_notary || "No asignada"}</div>
            <div className="flex items-start gap-3 ep-card-muted rounded-2xl px-4 py-3 text-sm text-primary"><ShieldCheck className="mt-0.5 h-4 w-4 text-primary" />Permisos funcionales cargados desde backend.</div>
          </div>
        </section>
      </aside>
    </div>
  );
}
