"use client";

import { useEffect, useMemo, useState } from "react";
import { Plus, Save, ShieldCheck, Trash2, Users2, X } from "lucide-react";
import {
  createRole,
  deleteRole,
  getCurrentUser,
  getRoleCatalog,
  getUsers,
  updateRole,
  type CurrentUser,
  type RoleCatalogItem,
  type UserRecord
} from "@/lib/api";

type NewRolePayload = {
  name: string;
  code: string;
  scope: "global" | "notary";
  description: string;
};

const emptyNewRole: NewRolePayload = {
  name: "",
  code: "",
  scope: "notary",
  description: ""
};

export function RolesWorkspace() {
  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null);
  const [roles, setRoles] = useState<RoleCatalogItem[]>([]);
  const [users, setUsers] = useState<UserRecord[]>([]);
  const [selectedRoleId, setSelectedRoleId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editName, setEditName] = useState("");
  const [editDescription, setEditDescription] = useState("");
  const [newRole, setNewRole] = useState<NewRolePayload>(emptyNewRole);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const normalizedRoleCodes = useMemo(
    () => (currentUser?.role_codes ?? []).map((role) => role.toLowerCase()),
    [currentUser?.role_codes]
  );
  const isSuperAdmin = normalizedRoleCodes.includes("super_admin");
  const isAdminNotary = normalizedRoleCodes.includes("admin_notary");
  const canManageRoles = isSuperAdmin || isAdminNotary;

  useEffect(() => {
    void loadWorkspace();
  }, []);

  async function loadWorkspace(preferredRoleId?: number) {
    setIsLoading(true);
    setError(null);
    try {
      const [user, rolesData, usersData] = await Promise.all([getCurrentUser(), getRoleCatalog(), getUsers()]);
      setCurrentUser(user);
      setRoles(rolesData);
      setUsers(usersData);

      const targetRoleId = preferredRoleId ?? selectedRoleId;
      if (targetRoleId && rolesData.some((role) => role.id === targetRoleId)) {
        setSelectedRoleId(targetRoleId);
      } else {
        setSelectedRoleId(rolesData[0]?.id ?? null);
      }
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "No fue posible cargar roles y usuarios.");
    } finally {
      setIsLoading(false);
    }
  }

  const roleUsage = useMemo(() => {
    return roles.reduce<Record<number, { count: number; assignedUsers: Array<{ id: number; full_name: string; notary_label: string | null }> }>>((acc, role) => {
      const assignedUsers = users
        .filter((user) => user.assignments.some((assignment) => assignment.role_id === role.id))
        .map((user) => {
          const assignment = user.assignments.find((item) => item.role_id === role.id);
          return {
            id: user.id,
            full_name: user.full_name,
            notary_label: assignment?.notary_label ?? user.default_notary_label ?? null
          };
        });

      acc[role.id] = {
        count: assignedUsers.length,
        assignedUsers
      };
      return acc;
    }, {});
  }, [roles, users]);

  const selectedRole = useMemo(
    () => roles.find((role) => role.id === selectedRoleId) ?? null,
    [roles, selectedRoleId]
  );

  const selectedRoleUsers = selectedRole ? roleUsage[selectedRole.id]?.assignedUsers ?? [] : [];
  const selectedRoleUsageCount = selectedRole ? roleUsage[selectedRole.id]?.count ?? 0 : 0;

  const canEditSelectedRole = useMemo(() => {
    if (!selectedRole || !canManageRoles) return false;
    if (isAdminNotary && selectedRole.code === "super_admin") return false;
    return true;
  }, [canManageRoles, isAdminNotary, selectedRole]);

  const disableDelete = !selectedRole || selectedRoleUsageCount > 0 || !isSuperAdmin;

  function openCreateModal() {
    setNewRole(emptyNewRole);
    setError(null);
    setFeedback(null);
    setShowCreateModal(true);
  }

  function closeCreateModal() {
    if (isCreating) return;
    setShowCreateModal(false);
  }

  function selectRole(role: RoleCatalogItem) {
    setSelectedRoleId(role.id);
    setIsEditing(false);
    setEditName(role.name);
    setEditDescription(role.description ?? "");
    setFeedback(null);
    setError(null);
  }

  function startEditing() {
    if (!selectedRole) return;
    setIsEditing(true);
    setEditName(selectedRole.name);
    setEditDescription(selectedRole.description ?? "");
    setFeedback(null);
    setError(null);
  }

  async function handleSaveRole() {
    if (!selectedRole) return;
    setIsSaving(true);
    setFeedback(null);
    setError(null);
    try {
      await updateRole(selectedRole.id, {
        name: editName.trim(),
        description: editDescription.trim()
      });
      setFeedback("Rol actualizado correctamente.");
      setIsEditing(false);
      await loadWorkspace(selectedRole.id);
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "No fue posible actualizar el rol.");
    } finally {
      setIsSaving(false);
    }
  }

  async function handleDeleteRole() {
    if (!selectedRole || disableDelete) return;
    setIsDeleting(true);
    setFeedback(null);
    setError(null);
    try {
      await deleteRole(selectedRole.id);
      setFeedback("Rol eliminado correctamente.");
      await loadWorkspace();
    } catch (deleteError) {
      setError(deleteError instanceof Error ? deleteError.message : "No fue posible eliminar el rol.");
    } finally {
      setIsDeleting(false);
    }
  }

  async function handleCreateRole() {
    setIsCreating(true);
    setFeedback(null);
    setError(null);
    try {
      if (isAdminNotary && newRole.code.trim().toLowerCase() === "super_admin") {
        throw new Error("Admin Notaría no puede crear el código super_admin.");
      }
      if (isAdminNotary && newRole.scope === "global") {
        throw new Error("Admin Notaría no puede crear roles de ámbito global.");
      }

      const created = await createRole({
        name: newRole.name.trim(),
        code: newRole.code.trim().toLowerCase(),
        scope: newRole.scope,
        description: newRole.description.trim()
      });
      setShowCreateModal(false);
      setFeedback("Rol creado correctamente.");
      await loadWorkspace(created.id);
    } catch (createError) {
      setError(createError instanceof Error ? createError.message : "No fue posible crear el rol.");
    } finally {
      setIsCreating(false);
    }
  }

  if (isLoading) {
    return <div className="ep-card rounded-[2rem] p-6 text-secondary">Cargando catálogo de roles...</div>;
  }

  return (
    <div className="space-y-6">
      <section className="ep-card rounded-[2rem] p-6">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
          <div className="max-w-3xl">
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-accent">Roles y permisos</p>
            <h1 className="mt-3 text-3xl font-semibold tracking-[-0.05em] text-primary sm:text-4xl">Catálogo de roles del sistema</h1>
            <p className="mt-3 text-base leading-7 text-secondary">Gestiona roles disponibles, su alcance y los usuarios que tienen cada asignación activa.</p>
          </div>
          {canManageRoles ? (
            <button onClick={openCreateModal} className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white shadow-panel transition hover:-translate-y-0.5">
              <Plus className="h-4 w-4" />
              Nuevo rol
            </button>
          ) : null}
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-3">
          <div className="ep-card-muted rounded-[1.5rem] p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-secondary">Roles visibles</p>
            <p className="mt-3 text-3xl font-semibold text-primary">{roles.length}</p>
            <p className="mt-2 text-sm text-secondary">Catálogo total disponible para tu perfil.</p>
          </div>
          <div className="ep-card-muted rounded-[1.5rem] p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-secondary">Roles en uso</p>
            <p className="mt-3 text-3xl font-semibold text-primary">{roles.filter((role) => (roleUsage[role.id]?.count ?? 0) > 0).length}</p>
            <p className="mt-2 text-sm text-secondary">Roles con al menos un usuario asignado.</p>
          </div>
          <div className="rounded-[1.5rem] bg-primary p-4 text-white shadow-panel">
            <p className="text-xs uppercase tracking-[0.2em] text-white/72">Asignaciones totales</p>
            <p className="mt-3 text-3xl font-semibold">{users.reduce((total, user) => total + user.assignments.length, 0)}</p>
            <p className="mt-2 text-sm text-white/82">Distribución vigente de perfiles y accesos.</p>
          </div>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[minmax(320px,0.9fr)_minmax(0,1.1fr)]">
        <aside className="ep-card rounded-[2rem] p-6">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-primary/10 text-primary">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-secondary">Listado</p>
              <h2 className="text-2xl font-semibold text-primary">Roles</h2>
            </div>
          </div>

          <div className="mt-5 space-y-3">
            {roles.map((role) => {
              const usage = roleUsage[role.id]?.count ?? 0;
              const isSelected = selectedRoleId === role.id;
              return (
                <button
                  key={role.id}
                  onClick={() => selectRole(role)}
                  className={`w-full rounded-[1.4rem] border px-4 py-4 text-left transition ${isSelected ? "border-primary/30 bg-[var(--panel-highlight)] shadow-soft" : "border-line bg-[var(--panel)] hover:bg-[var(--panel-soft)]"}`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="font-semibold text-primary">{role.name}</p>
                      <p className="mt-1 text-sm text-secondary">{role.code}</p>
                    </div>
                    <span className="ep-badge rounded-full px-3 py-1 text-xs font-semibold">{role.scope}</span>
                  </div>
                  <p className="mt-3 text-sm text-secondary">{role.description || "Sin descripción"}</p>
                  <p className="mt-2 text-sm text-secondary">Usuarios asignados: {usage}</p>
                </button>
              );
            })}
          </div>
        </aside>

        <div className="ep-card rounded-[2rem] p-6">
          {!selectedRole ? (
            <div className="ep-card-muted rounded-[1.5rem] px-4 py-6 text-sm text-secondary">Selecciona un rol para ver su detalle.</div>
          ) : (
            <div className="space-y-6">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p className="text-xs uppercase tracking-[0.2em] text-secondary">Detalle del rol</p>
                  <h2 className="mt-2 text-2xl font-semibold text-primary">{selectedRole.name}</h2>
                </div>
                <div className="flex flex-wrap gap-2">
                  {canEditSelectedRole ? (
                    isEditing ? (
                      <button
                        onClick={() => void handleSaveRole()}
                        disabled={isSaving}
                        className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white shadow-panel disabled:opacity-70"
                      >
                        <Save className="h-4 w-4" />
                        {isSaving ? "Guardando..." : "Guardar"}
                      </button>
                    ) : (
                      <button onClick={startEditing} className="inline-flex items-center gap-2 rounded-2xl border border-line bg-[var(--panel)] px-5 py-3 text-sm font-semibold text-primary transition hover:bg-[var(--panel-soft)]">
                        Editar
                      </button>
                    )
                  ) : (
                    <div className="ep-card-soft rounded-2xl px-4 py-3 text-xs text-secondary">No tienes permisos para editar este rol.</div>
                  )}

                  {isSuperAdmin ? (
                    <button
                      onClick={() => void handleDeleteRole()}
                      disabled={disableDelete || isDeleting}
                      className="inline-flex items-center gap-2 rounded-2xl border border-rose-300/60 bg-rose-500/10 px-5 py-3 text-sm font-semibold text-rose-700 transition hover:bg-rose-500/15 disabled:cursor-not-allowed disabled:opacity-60 dark:text-rose-200"
                    >
                      <Trash2 className="h-4 w-4" />
                      {isDeleting ? "Eliminando..." : "Eliminar rol"}
                    </button>
                  ) : null}
                </div>
              </div>

              <div className="grid gap-4 lg:grid-cols-2">
                <label className="grid gap-2 text-sm font-medium text-primary">
                  Nombre
                  <input
                    value={isEditing ? editName : selectedRole.name}
                    onChange={(event) => setEditName(event.target.value)}
                    readOnly={!isEditing}
                    className="ep-input h-12 rounded-2xl px-4 read-only:opacity-80"
                  />
                </label>
                <label className="grid gap-2 text-sm font-medium text-primary">
                  Código
                  <input value={selectedRole.code} readOnly className="ep-input h-12 rounded-2xl px-4 opacity-80" />
                </label>
                <label className="grid gap-2 text-sm font-medium text-primary">
                  Ámbito
                  <input value={selectedRole.scope} readOnly className="ep-input h-12 rounded-2xl px-4 opacity-80" />
                </label>
                <label className="grid gap-2 text-sm font-medium text-primary">
                  Usuarios asignados
                  <input value={String(selectedRoleUsageCount)} readOnly className="ep-input h-12 rounded-2xl px-4 opacity-80" />
                </label>
                <label className="grid gap-2 text-sm font-medium text-primary lg:col-span-2">
                  Descripción
                  <textarea
                    rows={4}
                    value={isEditing ? editDescription : selectedRole.description || ""}
                    onChange={(event) => setEditDescription(event.target.value)}
                    readOnly={!isEditing}
                    className="ep-input min-h-[120px] rounded-2xl px-4 py-3 read-only:opacity-80"
                  />
                </label>
              </div>

              <div className="ep-filter-panel rounded-[1.5rem] p-5">
                <div className="flex items-center gap-3">
                  <Users2 className="h-5 w-5 text-primary" />
                  <div>
                    <p className="text-xs uppercase tracking-[0.2em] text-secondary">Asignaciones</p>
                    <h3 className="mt-1 text-xl font-semibold text-primary">Usuarios con este rol</h3>
                  </div>
                </div>

                <div className="mt-4 space-y-3">
                  {selectedRoleUsers.length === 0 ? (
                    <div className="ep-card-muted rounded-2xl px-4 py-4 text-sm text-secondary">No hay usuarios asignados a este rol.</div>
                  ) : (
                    selectedRoleUsers.map((user) => (
                      <div key={user.id} className="ep-card-soft rounded-2xl px-4 py-4">
                        <p className="text-sm font-semibold text-primary">{user.full_name}</p>
                        <p className="mt-1 text-sm text-secondary">{user.notary_label || "Sin notaría asociada"}</p>
                      </div>
                    ))
                  )}
                </div>
              </div>

              {!isSuperAdmin && selectedRole?.code === "super_admin" && isAdminNotary ? (
                <div className="ep-badge rounded-2xl px-4 py-3 text-sm">Admin Notaría no puede editar el rol super_admin.</div>
              ) : null}
              {isSuperAdmin && selectedRoleUsageCount > 0 ? (
                <div className="ep-badge rounded-2xl px-4 py-3 text-sm">No puedes eliminar un rol con usuarios asignados.</div>
              ) : null}
            </div>
          )}
        </div>
      </section>

      {feedback ? <div className="ep-kpi-success rounded-2xl px-4 py-3 text-sm">{feedback}</div> : null}
      {error ? <div className="ep-kpi-critical rounded-2xl px-4 py-3 text-sm">{error}</div> : null}

      {showCreateModal ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/45 px-4 py-8">
          <div className="ep-card w-full max-w-2xl rounded-[2rem] p-6">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-secondary">Nuevo rol</p>
                <h3 className="mt-2 text-2xl font-semibold text-primary">Crear rol del sistema</h3>
              </div>
              <button onClick={closeCreateModal} className="ep-card-soft inline-flex h-10 w-10 items-center justify-center rounded-2xl" aria-label="Cerrar modal">
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="mt-5 grid gap-4 lg:grid-cols-2">
              <label className="grid gap-2 text-sm font-medium text-primary">
                Nombre
                <input value={newRole.name} onChange={(event) => setNewRole((current) => ({ ...current, name: event.target.value }))} className="ep-input h-12 rounded-2xl px-4" />
              </label>
              <label className="grid gap-2 text-sm font-medium text-primary">
                Código
                <input value={newRole.code} onChange={(event) => setNewRole((current) => ({ ...current, code: event.target.value }))} className="ep-input h-12 rounded-2xl px-4" />
              </label>
              <label className="grid gap-2 text-sm font-medium text-primary">
                Ámbito
                <select value={newRole.scope} onChange={(event) => setNewRole((current) => ({ ...current, scope: event.target.value as "global" | "notary" }))} className="ep-select h-12 rounded-2xl px-4">
                  {isAdminNotary ? null : <option value="global">global</option>}
                  <option value="notary">notary</option>
                </select>
              </label>
              <div className="ep-card-muted rounded-2xl px-4 py-4 text-sm text-secondary">
                Admin Notaría no puede crear el rol <span className="font-semibold">super_admin</span> ni roles de ámbito <span className="font-semibold">global</span>.
              </div>
              <label className="grid gap-2 text-sm font-medium text-primary lg:col-span-2">
                Descripción
                <textarea
                  rows={4}
                  value={newRole.description}
                  onChange={(event) => setNewRole((current) => ({ ...current, description: event.target.value }))}
                  className="ep-input min-h-[120px] rounded-2xl px-4 py-3"
                />
              </label>
            </div>

            <div className="mt-6 flex justify-end gap-3">
              <button onClick={closeCreateModal} className="rounded-2xl border border-line px-5 py-3 text-sm font-semibold text-primary transition hover:bg-[var(--panel-soft)]">
                Cancelar
              </button>
              <button
                onClick={() => void handleCreateRole()}
                disabled={isCreating}
                className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white shadow-panel disabled:opacity-70"
              >
                <Plus className="h-4 w-4" />
                {isCreating ? "Creando..." : "Crear"}
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
