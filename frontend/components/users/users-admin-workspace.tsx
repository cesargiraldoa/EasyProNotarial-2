"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { Plus, Save, Shield, UserCog, Users2 } from "lucide-react";
import {
  createUser,
  getNotaries,
  getRoleCatalog,
  getUsers,
  updateUser,
  type NotaryRecord,
  type RoleCatalogItem,
  type UserPayload,
  type UserRecord
} from "@/lib/api";

const emptyPayload: UserPayload = {
  email: "",
  full_name: "",
  password: "",
  is_active: true,
  phone: "",
  job_title: "",
  default_notary_id: null,
  assignments: []
};

export function UsersAdminWorkspace() {
  const [users, setUsers] = useState<UserRecord[]>([]);
  const [roles, setRoles] = useState<RoleCatalogItem[]>([]);
  const [notaries, setNotaries] = useState<NotaryRecord[]>([]);
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null);
  const [formState, setFormState] = useState<UserPayload>(emptyPayload);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");

  useEffect(() => {
    void loadWorkspace();
  }, []);

  async function loadWorkspace() {
    setIsLoading(true);
    setError(null);
    try {
      const [usersData, rolesData, notariesData] = await Promise.all([
        getUsers(),
        getRoleCatalog(),
        getNotaries()
      ]);
      setUsers(usersData);
      setRoles(rolesData);
      setNotaries(notariesData);
      if (!selectedUserId && usersData.length > 0) {
        selectUser(usersData[0]);
      }
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "No fue posible cargar usuarios y roles.");
    } finally {
      setIsLoading(false);
    }
  }

  function selectUser(user: UserRecord) {
    setSelectedUserId(user.id);
    setFormState({
      email: user.email,
      full_name: user.full_name,
      password: "",
      is_active: user.is_active,
      phone: user.phone ?? "",
      job_title: user.job_title ?? "",
      default_notary_id: user.default_notary_id ?? null,
      assignments: user.assignments.map((assignment) => ({
        role_code: assignment.role_code,
        notary_id: assignment.notary_id ?? null
      }))
    });
    setFeedback(null);
    setError(null);
  }

  function handleNewUser() {
    setSelectedUserId(null);
    setFormState({ ...emptyPayload, assignments: [] });
    setFeedback(null);
    setError(null);
  }

  function updateField<K extends keyof UserPayload>(field: K, value: UserPayload[K]) {
    setFormState((current) => ({ ...current, [field]: value }));
  }

  function updateAssignment(index: number, field: "role_code" | "notary_id", value: string) {
    setFormState((current) => ({
      ...current,
      assignments: current.assignments.map((assignment, itemIndex) => {
        if (itemIndex !== index) return assignment;
        if (field === "role_code") {
          const role = roles.find((item) => item.code === value);
          return {
            role_code: value,
            notary_id: role?.scope === "global" ? null : assignment.notary_id
          };
        }
        return {
          ...assignment,
          notary_id: value ? Number(value) : null
        };
      })
    }));
  }

  function addAssignment() {
    setFormState((current) => ({
      ...current,
      assignments: [...current.assignments, { role_code: "", notary_id: null }]
    }));
  }

  function removeAssignment(index: number) {
    setFormState((current) => ({
      ...current,
      assignments: current.assignments.filter((_, itemIndex) => itemIndex !== index)
    }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSaving(true);
    setFeedback(null);
    setError(null);
    try {
      if (selectedUserId) {
        await updateUser(selectedUserId, formState);
        setFeedback("Usuario actualizado correctamente.");
      } else {
        const created = await createUser(formState);
        setFeedback("Usuario creado correctamente.");
        setSelectedUserId(created.id);
      }
      const usersData = await getUsers();
      setUsers(usersData);
      if (selectedUserId) {
        const current = usersData.find((user) => user.id === selectedUserId);
        if (current) selectUser(current);
      } else {
        const newest = usersData.find((user) => user.email === formState.email.toLowerCase());
        if (newest) selectUser(newest);
      }
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "No fue posible guardar el usuario.");
    } finally {
      setIsSaving(false);
    }
  }

  const filteredUsers = useMemo(() => {
    const normalizedSearch = search.trim().toLowerCase();
    if (!normalizedSearch) return users;
    return users.filter((user) =>
      user.full_name.toLowerCase().includes(normalizedSearch)
      || user.email.toLowerCase().includes(normalizedSearch)
      || user.roles.join(" ").toLowerCase().includes(normalizedSearch)
    );
  }, [search, users]);

  if (isLoading) {
    return <div className="ep-card rounded-[2rem] p-6 text-secondary">Cargando usuarios, roles y asignaciones...</div>;
  }

  return (
    <div className="space-y-6">
      <section className="ep-card rounded-[2rem] p-6">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
          <div className="max-w-3xl">
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-accent">Usuarios y roles</p>
            <h1 className="mt-3 text-3xl font-semibold tracking-[-0.05em] text-primary sm:text-4xl">Usuarios reales del sistema para operación, notaría y CRM</h1>
            <p className="mt-3 text-base leading-7 text-secondary">Aquí se administra el CRUD base de usuarios, los roles por notaría y la base de responsables comerciales reales que usa el CRM sobre Notary.</p>
          </div>
          <button onClick={handleNewUser} className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white shadow-panel transition hover:-translate-y-0.5">
            <Plus className="h-4 w-4" />
            Nuevo usuario
          </button>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-3">
          <div className="ep-card-muted rounded-[1.5rem] p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-secondary">Usuarios visibles</p>
            <p className="mt-3 text-3xl font-semibold text-primary">{users.length}</p>
            <p className="mt-2 text-sm text-secondary">Base activa de acceso, operación y CRM.</p>
          </div>
          <div className="ep-card-muted rounded-[1.5rem] p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-secondary">Roles disponibles</p>
            <p className="mt-3 text-3xl font-semibold text-primary">{roles.length}</p>
            <p className="mt-2 text-sm text-secondary">SuperAdmin, Admin Notaría y perfiles operativos base.</p>
          </div>
          <div className="rounded-[1.5rem] bg-primary p-4 text-white shadow-panel">
            <p className="text-xs uppercase tracking-[0.2em] text-white/72">Notarías asignables</p>
            <p className="mt-3 text-3xl font-semibold">{notaries.length}</p>
            <p className="mt-2 text-sm text-white/82">Roles por notaría y responsables sobre la misma entidad.</p>
          </div>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[minmax(320px,0.9fr)_minmax(0,1.1fr)]">
        <aside className="ep-card rounded-[2rem] p-6">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-primary/10 text-primary">
              <Users2 className="h-5 w-5" />
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-secondary">Listado</p>
              <h2 className="text-2xl font-semibold text-primary">Usuarios</h2>
            </div>
          </div>
          <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Buscar por nombre, correo o rol..." className="ep-input mt-5 h-12 w-full rounded-2xl px-4" />
          <div className="mt-5 space-y-3">
            {filteredUsers.map((user) => (
              <button key={user.id} onClick={() => selectUser(user)} className={`w-full rounded-[1.4rem] border px-4 py-4 text-left transition ${selectedUserId === user.id ? "border-primary/30 bg-[var(--panel-highlight)] shadow-soft" : "border-line bg-[var(--panel)] hover:bg-[var(--panel-soft)]"}`}>
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="font-semibold text-primary">{user.full_name}</p>
                    <p className="mt-1 text-sm text-secondary">{user.email}</p>
                  </div>
                  <span className={`rounded-full px-3 py-1 text-xs font-semibold ${user.is_active ? "ep-kpi-success" : "ep-badge"}`}>{user.is_active ? "Activo" : "Inactivo"}</span>
                </div>
                <p className="mt-3 text-sm text-secondary">{user.default_notary_label || "Sin notaría por defecto"}</p>
                <p className="mt-2 text-sm text-secondary">{user.roles.join(" · ") || "Sin roles asignados"}</p>
              </button>
            ))}
          </div>
        </aside>

        <form onSubmit={handleSubmit} className="space-y-6 ep-card rounded-[2rem] p-6">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-secondary">Editor administrativo</p>
              <h2 className="mt-2 text-2xl font-semibold text-primary">{selectedUserId ? "Editar usuario" : "Crear usuario"}</h2>
            </div>
            <button type="submit" disabled={isSaving} className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white shadow-panel disabled:cursor-not-allowed disabled:opacity-70">
              <Save className="h-4 w-4" />
              {isSaving ? "Guardando..." : "Guardar usuario"}
            </button>
          </div>

          <div className="grid gap-4 lg:grid-cols-2">
            <label className="grid gap-2 text-sm font-medium text-primary">Nombre completo<input value={formState.full_name} onChange={(event) => updateField("full_name", event.target.value)} className="ep-input h-12 rounded-2xl px-4" /></label>
            <label className="grid gap-2 text-sm font-medium text-primary">Correo<input type="email" value={formState.email} onChange={(event) => updateField("email", event.target.value)} className="ep-input h-12 rounded-2xl px-4" /></label>
            <label className="grid gap-2 text-sm font-medium text-primary">Contraseña<input type="password" value={formState.password ?? ""} onChange={(event) => updateField("password", event.target.value)} placeholder={selectedUserId ? "Dejar vacío para conservar" : "Mínimo 8 caracteres"} className="ep-input h-12 rounded-2xl px-4" /></label>
            <label className="grid gap-2 text-sm font-medium text-primary">Cargo<input value={formState.job_title} onChange={(event) => updateField("job_title", event.target.value)} className="ep-input h-12 rounded-2xl px-4" /></label>
            <label className="grid gap-2 text-sm font-medium text-primary">Teléfono<input value={formState.phone} onChange={(event) => updateField("phone", event.target.value)} className="ep-input h-12 rounded-2xl px-4" /></label>
            <label className="grid gap-2 text-sm font-medium text-primary">Estado<select value={String(formState.is_active)} onChange={(event) => updateField("is_active", event.target.value === "true")} className="ep-select h-12 rounded-2xl px-4"><option value="true">Activo</option><option value="false">Inactivo</option></select></label>
            <label className="grid gap-2 text-sm font-medium text-primary lg:col-span-2">Notaría por defecto<select value={formState.default_notary_id?.toString() ?? ""} onChange={(event) => updateField("default_notary_id", event.target.value ? Number(event.target.value) : null)} className="ep-select h-12 rounded-2xl px-4"><option value="">Sin notaría por defecto</option>{notaries.map((notary) => <option key={notary.id} value={notary.id}>{notary.notary_label} · {notary.municipality}</option>)}</select></label>
          </div>

          <div className="ep-filter-panel rounded-[1.5rem] p-5">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-secondary">Asignaciones</p>
                <h3 className="mt-2 text-xl font-semibold text-primary">Roles por usuario y notaría</h3>
              </div>
              <button type="button" onClick={addAssignment} className="inline-flex items-center gap-2 rounded-2xl border border-line bg-[var(--panel)] px-4 py-2 text-sm font-semibold text-primary transition hover:bg-[var(--panel-soft)]">
                <Plus className="h-4 w-4" />
                Agregar rol
              </button>
            </div>

            <div className="mt-5 space-y-4">
              {formState.assignments.length === 0 ? <div className="ep-card rounded-2xl px-4 py-4 text-sm text-secondary">Aún no hay roles asignados para este usuario.</div> : null}
              {formState.assignments.map((assignment, index) => {
                const selectedRole = roles.find((role) => role.code === assignment.role_code);
                const isGlobal = selectedRole?.scope === "global";
                return (
                  <div key={`${assignment.role_code}-${index}`} className="grid gap-3 ep-card rounded-2xl p-4 lg:grid-cols-[minmax(0,0.8fr)_minmax(0,1fr)_auto]">
                    <label className="grid gap-2 text-sm font-medium text-primary">Rol<select value={assignment.role_code} onChange={(event) => updateAssignment(index, "role_code", event.target.value)} className="ep-select h-11 rounded-2xl px-4"><option value="">Selecciona un rol</option>{roles.map((role) => <option key={role.code} value={role.code}>{role.name}</option>)}</select></label>
                    <label className="grid gap-2 text-sm font-medium text-primary">Notaría<select value={assignment.notary_id?.toString() ?? ""} onChange={(event) => updateAssignment(index, "notary_id", event.target.value)} disabled={isGlobal || !assignment.role_code} className="ep-select h-11 rounded-2xl px-4 disabled:opacity-60"><option value="">{isGlobal ? "Ámbito global" : "Selecciona una notaría"}</option>{notaries.map((notary) => <option key={notary.id} value={notary.id}>{notary.notary_label} · {notary.municipality}</option>)}</select></label>
                    <button type="button" onClick={() => removeAssignment(index)} className="mt-auto rounded-2xl border border-rose-300/60 bg-rose-500/10 px-4 py-3 text-sm font-semibold text-rose-700 transition hover:bg-rose-500/15 dark:text-rose-200">Quitar</button>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="grid gap-4 lg:grid-cols-3">
            <div className="ep-card-muted rounded-[1.5rem] p-4">
              <div className="flex items-center gap-3"><Shield className="h-5 w-5 text-primary" /><p className="text-sm font-semibold text-primary">Permisos base</p></div>
              <p className="mt-3 text-sm leading-6 text-secondary">SuperAdmin gestiona plataforma completa. Admin Notaría gestiona usuarios y CRM dentro de su alcance.</p>
            </div>
            <div className="ep-card-muted rounded-[1.5rem] p-4">
              <div className="flex items-center gap-3"><UserCog className="h-5 w-5 text-primary" /><p className="text-sm font-semibold text-primary">Responsables reales</p></div>
              <p className="mt-3 text-sm leading-6 text-secondary">Cualquier usuario activo puede ser responsable comercial y aparecer en filtros y detalle CRM.</p>
            </div>
            <div className="ep-card-muted rounded-[1.5rem] p-4">
              <div className="flex items-center gap-3"><Users2 className="h-5 w-5 text-primary" /><p className="text-sm font-semibold text-primary">Compatibilidad</p></div>
              <p className="mt-3 text-sm leading-6 text-secondary">Los responsables textuales heredados se conservan mientras se migra la asignación a usuarios reales.</p>
            </div>
          </div>

          {feedback ? <div className="ep-kpi-success rounded-2xl px-4 py-3 text-sm">{feedback}</div> : null}
          {error ? <div className="ep-kpi-critical rounded-2xl px-4 py-3 text-sm">{error}</div> : null}
        </form>
      </section>
    </div>
  );
}
