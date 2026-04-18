"use client";

import { useEffect, useMemo, useState } from "react";
import { Plus, Trash2, X } from "lucide-react";
import {
  createRole,
  deleteRole,
  getCurrentUser,
  getRoleCatalog,
  getUsers,
  updateRole,
  updateUser,
  type CurrentUser,
  type RoleCatalogItem,
  type UserAssignmentPayload,
  type UserPayload,
  type UserRecord
} from "@/lib/api";

type RoleScope = "global" | "notary";

type NewRolePayload = {
  name: string;
  code: string;
  scope: RoleScope;
  description: string;
};

type RoleEditorState = {
  name: string;
  description: string;
};

type CurrentUserWithDefaultNotary = CurrentUser & {
  default_notary_id?: number | null;
};

const PAGE_SIZE = 20;
const EMPTY_NEW_ROLE: NewRolePayload = {
  name: "",
  code: "",
  scope: "notary",
  description: ""
};

function getCellKey(userId: number, roleCode: string): string {
  return `${userId}:${roleCode}`;
}

function isRoleScope(value: string): value is RoleScope {
  return value === "global" || value === "notary";
}

function createUserPayload(user: UserRecord, assignments: UserAssignmentPayload[]): UserPayload {
  return {
    email: user.email,
    full_name: user.full_name,
    password: null,
    is_active: user.is_active,
    phone: user.phone ?? "",
    job_title: user.job_title ?? "",
    default_notary_id: user.default_notary_id ?? null,
    assignments
  };
}

export function RolesWorkspace() {
  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null);
  const [roles, setRoles] = useState<RoleCatalogItem[]>([]);
  const [users, setUsers] = useState<UserRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newRole, setNewRole] = useState<NewRolePayload>(EMPTY_NEW_ROLE);
  const [isCreatingRole, setIsCreatingRole] = useState(false);
  const [createRoleError, setCreateRoleError] = useState<string | null>(null);

  const [activeRoleEditorId, setActiveRoleEditorId] = useState<number | null>(null);
  const [roleEditor, setRoleEditor] = useState<RoleEditorState>({ name: "", description: "" });
  const [roleEditorError, setRoleEditorError] = useState<string | null>(null);
  const [roleEditorLoading, setRoleEditorLoading] = useState(false);
  const [roleDeleting, setRoleDeleting] = useState(false);

  const [loadingCells, setLoadingCells] = useState<Record<string, boolean>>({});
  const [rowErrors, setRowErrors] = useState<Record<number, string | null>>({});
  const [globalError, setGlobalError] = useState<string | null>(null);

  const roleCodes = useMemo(
    () => (currentUser?.role_codes ?? []).map((item) => item.toLowerCase()),
    [currentUser?.role_codes]
  );

  const isSuperAdmin = roleCodes.includes("super_admin");
  const isAdminNotary = roleCodes.includes("admin_notary");
  const canManageRoles = isSuperAdmin || isAdminNotary;

  const currentDefaultNotaryId = useMemo(() => {
    const candidate = (currentUser as CurrentUserWithDefaultNotary | null)?.default_notary_id;
    return typeof candidate === "number" ? candidate : null;
  }, [currentUser]);

  useEffect(() => {
    void loadData();
  }, []);

  async function loadData() {
    setIsLoading(true);
    setGlobalError(null);
    try {
      const [nextCurrentUser, nextRoles, nextUsers] = await Promise.all([
        getCurrentUser(),
        getRoleCatalog(),
        getUsers()
      ]);
      setCurrentUser(nextCurrentUser);
      setRoles(nextRoles);
      setUsers(nextUsers);
    } catch (error) {
      setGlobalError(error instanceof Error ? error.message : "No fue posible cargar la matriz de roles.");
    } finally {
      setIsLoading(false);
    }
  }

  const visibleUsers = useMemo(() => {
    const scopedUsers = isAdminNotary && currentDefaultNotaryId !== null
      ? users.filter((user) => user.default_notary_id === currentDefaultNotaryId)
      : users;

    if (!search.trim()) {
      return scopedUsers;
    }

    const normalized = search.trim().toLowerCase();
    return scopedUsers.filter((user) => {
      return user.full_name.toLowerCase().includes(normalized) || user.email.toLowerCase().includes(normalized);
    });
  }, [currentDefaultNotaryId, isAdminNotary, search, users]);

  const totalPages = Math.max(1, Math.ceil(visibleUsers.length / PAGE_SIZE));

  useEffect(() => {
    if (page > totalPages) {
      setPage(totalPages);
    }
  }, [page, totalPages]);

  const pagedUsers = useMemo(() => {
    const start = (page - 1) * PAGE_SIZE;
    return visibleUsers.slice(start, start + PAGE_SIZE);
  }, [page, visibleUsers]);

  const totalAssignments = useMemo(
    () => visibleUsers.reduce((total, user) => total + user.assignments.length, 0),
    [visibleUsers]
  );

  function hasAssignment(user: UserRecord, role: RoleCatalogItem): boolean {
    const targetNotaryId = role.scope === "notary" ? user.default_notary_id ?? null : null;
    return user.assignments.some((assignment) => {
      const normalizedNotaryId = assignment.notary_id ?? null;
      return assignment.role_code === role.code && normalizedNotaryId === targetNotaryId;
    });
  }

  function roleAssignedCount(role: RoleCatalogItem): number {
    return visibleUsers.reduce((count, user) => count + (hasAssignment(user, role) ? 1 : 0), 0);
  }

  function openRoleEditor(role: RoleCatalogItem) {
    setActiveRoleEditorId(role.id);
    setRoleEditor({
      name: role.name,
      description: role.description ?? ""
    });
    setRoleEditorError(null);
  }

  async function handleSaveRole(roleId: number) {
    setRoleEditorLoading(true);
    setRoleEditorError(null);
    try {
      await updateRole(roleId, {
        name: roleEditor.name.trim(),
        description: roleEditor.description.trim()
      });
      await loadData();
      setActiveRoleEditorId(null);
    } catch (error) {
      setRoleEditorError(error instanceof Error ? error.message : "No fue posible actualizar el rol.");
    } finally {
      setRoleEditorLoading(false);
    }
  }

  async function handleDeleteRole(role: RoleCatalogItem) {
    if (!isSuperAdmin) {
      return;
    }
    if (roleAssignedCount(role) > 0) {
      return;
    }

    setRoleDeleting(true);
    setRoleEditorError(null);
    try {
      await deleteRole(role.id);
      await loadData();
      setActiveRoleEditorId(null);
    } catch (error) {
      setRoleEditorError(error instanceof Error ? error.message : "No fue posible eliminar el rol.");
    } finally {
      setRoleDeleting(false);
    }
  }

  async function handleToggleCell(user: UserRecord, role: RoleCatalogItem, checked: boolean) {
    const cellKey = getCellKey(user.id, role.code);
    const targetNotaryId = role.scope === "notary" ? user.default_notary_id ?? null : null;

    const previousUsers = users;

    const nextUsers = users.map((candidate) => {
      if (candidate.id !== user.id) {
        return candidate;
      }

      const existingAssignments = candidate.assignments.map((assignment) => ({
        role_code: assignment.role_code,
        notary_id: assignment.notary_id ?? null
      }));

      const updatedAssignments = checked
        ? existingAssignments.filter((assignment) => {
            return !(assignment.role_code === role.code && assignment.notary_id === targetNotaryId);
          })
        : [...existingAssignments, { role_code: role.code, notary_id: targetNotaryId }];

      return {
        ...candidate,
        assignments: updatedAssignments.map((assignment, index) => ({
          id: -(index + 1),
          role_id: 0,
          role_code: assignment.role_code,
          role_name: role.code,
          notary_id: assignment.notary_id,
          notary_label: assignment.notary_id === null ? null : candidate.default_notary_label ?? null
        }))
      };
    });

    setUsers(nextUsers);
    setLoadingCells((current) => ({ ...current, [cellKey]: true }));
    setRowErrors((current) => ({ ...current, [user.id]: null }));

    try {
      const sourceUser = previousUsers.find((candidate) => candidate.id === user.id);
      if (!sourceUser) {
        throw new Error("No fue posible identificar el usuario para actualizar.");
      }

      const currentPayloadAssignments: UserAssignmentPayload[] = sourceUser.assignments.map((assignment) => ({
        role_code: assignment.role_code,
        notary_id: assignment.notary_id ?? null
      }));

      const updatedPayloadAssignments = checked
        ? currentPayloadAssignments.filter((assignment) => {
            return !(assignment.role_code === role.code && assignment.notary_id === targetNotaryId);
          })
        : [...currentPayloadAssignments, { role_code: role.code, notary_id: targetNotaryId }];

      const payload = createUserPayload(sourceUser, updatedPayloadAssignments);
      const updatedUser = await updateUser(user.id, payload);

      setUsers((currentUsers) => currentUsers.map((candidate) => (candidate.id === updatedUser.id ? updatedUser : candidate)));
    } catch (error) {
      setUsers(previousUsers);
      setRowErrors((current) => ({
        ...current,
        [user.id]: error instanceof Error ? error.message : "No fue posible actualizar esta asignación."
      }));
    } finally {
      setLoadingCells((current) => {
        const clone = { ...current };
        delete clone[cellKey];
        return clone;
      });
    }
  }

  async function handleCreateRole() {
    setCreateRoleError(null);

    const code = newRole.code.trim().toLowerCase();
    const scope = newRole.scope;

    if (isAdminNotary && code === "super_admin") {
      setCreateRoleError("Admin Notaría no puede crear el código super_admin.");
      return;
    }

    setIsCreatingRole(true);
    try {
      await createRole({
        name: newRole.name.trim(),
        code,
        scope,
        description: newRole.description.trim()
      });
      setShowCreateModal(false);
      setNewRole(EMPTY_NEW_ROLE);
      await loadData();
    } catch (error) {
      setCreateRoleError(error instanceof Error ? error.message : "No fue posible crear el rol.");
    } finally {
      setIsCreatingRole(false);
    }
  }

  function onSearchChange(value: string) {
    setSearch(value);
    setPage(1);
  }

  if (isLoading) {
    return <div className="ep-card rounded-[2rem] p-6 text-secondary">Cargando roles y usuarios...</div>;
  }

  return (
    <div className="space-y-6">
      <section className="ep-card rounded-[2rem] p-6">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <h1 className="text-3xl font-semibold tracking-[-0.03em] text-primary">Roles y permisos</h1>
            <p className="mt-2 text-sm text-secondary">Matriz de usuarios y roles con asignación en tiempo real.</p>
          </div>

          {canManageRoles ? (
            <button
              type="button"
              onClick={() => {
                setShowCreateModal(true);
                setCreateRoleError(null);
              }}
              className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white shadow-panel"
            >
              <Plus className="h-4 w-4" />
              Nuevo rol
            </button>
          ) : null}
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-4">
          <div className="ep-card-muted rounded-2xl p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-secondary">Usuarios visibles</p>
            <p className="mt-2 text-3xl font-semibold text-primary">{visibleUsers.length}</p>
          </div>
          <div className="ep-card-muted rounded-2xl p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-secondary">Roles activos</p>
            <p className="mt-2 text-3xl font-semibold text-primary">{roles.length}</p>
          </div>
          <div className="ep-card-soft rounded-2xl p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-secondary">Asignaciones totales</p>
            <p className="mt-2 text-3xl font-semibold text-primary">{totalAssignments}</p>
          </div>
          <div>
            <label className="mb-2 block text-xs uppercase tracking-[0.2em] text-secondary">Buscar usuario</label>
            <input
              value={search}
              onChange={(event) => onSearchChange(event.target.value)}
              placeholder="Nombre o email"
              className="ep-input h-12 w-full rounded-2xl px-4"
            />
          </div>
        </div>

        {globalError ? <div className="mt-4 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{globalError}</div> : null}
      </section>

      <section className="ep-card rounded-[2rem] p-4 md:p-6">
        <div className="overflow-x-auto">
          <table className="min-w-full border-separate border-spacing-0">
            <thead>
              <tr>
                <th className="sticky left-0 z-20 min-w-[280px] border-b border-line bg-[var(--panel)] px-4 py-3 text-left text-xs uppercase tracking-[0.18em] text-secondary">
                  Usuario
                </th>
                {roles.map((role) => {
                  const roleIsBlocked = isAdminNotary && role.code.toLowerCase() === "super_admin";
                  return (
                    <th key={role.id} className="relative border-b border-line bg-[var(--panel)] px-4 py-3 text-left text-xs font-semibold text-primary">
                      <button
                        type="button"
                        onClick={() => openRoleEditor(role)}
                        className="rounded-lg px-1 py-1 text-left hover:bg-[var(--panel-soft)]"
                      >
                        <div className="text-sm font-semibold text-primary">{role.name}</div>
                        <div className="text-[11px] uppercase tracking-[0.14em] text-secondary">{role.scope}</div>
                      </button>

                      {activeRoleEditorId === role.id ? (
                        <div className="absolute right-2 top-14 z-30 w-72 rounded-2xl border border-line bg-[var(--panel)] p-4 shadow-panel">
                          <div className="mb-3 flex items-start justify-between gap-2">
                            <p className="text-sm font-semibold text-primary">Editar rol</p>
                            <button
                              type="button"
                              onClick={() => setActiveRoleEditorId(null)}
                              className="rounded-xl p-1 hover:bg-[var(--panel-soft)]"
                            >
                              <X className="h-4 w-4" />
                            </button>
                          </div>

                          <div className="space-y-3">
                            <div>
                              <label className="mb-1 block text-xs text-secondary">Nombre</label>
                              <input
                                value={roleEditor.name}
                                onChange={(event) => setRoleEditor((current) => ({ ...current, name: event.target.value }))}
                                className="ep-input h-10 w-full rounded-xl px-3"
                              />
                            </div>
                            <div>
                              <label className="mb-1 block text-xs text-secondary">Descripción</label>
                              <textarea
                                value={roleEditor.description}
                                onChange={(event) => setRoleEditor((current) => ({ ...current, description: event.target.value }))}
                                className="ep-input min-h-[84px] w-full rounded-xl px-3 py-2"
                              />
                            </div>

                            {roleEditorError ? <div className="rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-xs text-rose-700">{roleEditorError}</div> : null}

                            <div className="flex gap-2">
                              <button
                                type="button"
                                onClick={() => void handleSaveRole(role.id)}
                                disabled={roleEditorLoading}
                                className="rounded-xl bg-primary px-3 py-2 text-xs font-semibold text-white disabled:opacity-70"
                              >
                                {roleEditorLoading ? "Guardando..." : "Guardar"}
                              </button>
                              {isSuperAdmin ? (
                                <button
                                  type="button"
                                  onClick={() => void handleDeleteRole(role)}
                                  disabled={roleDeleting || roleAssignedCount(role) > 0}
                                  className="inline-flex items-center gap-1 rounded-xl border border-rose-300/70 bg-rose-50 px-3 py-2 text-xs font-semibold text-rose-700 disabled:opacity-60"
                                >
                                  <Trash2 className="h-3.5 w-3.5" />
                                  Eliminar
                                </button>
                              ) : null}
                            </div>

                            {isSuperAdmin && roleAssignedCount(role) > 0 ? (
                              <p className="text-[11px] text-secondary">No se puede eliminar: el rol tiene usuarios asignados.</p>
                            ) : null}
                          </div>
                        </div>
                      ) : null}

                      {roleIsBlocked ? <div className="mt-1 text-[10px] uppercase text-amber-600">Restringido para admin_notary</div> : null}
                    </th>
                  );
                })}
              </tr>
            </thead>
            <tbody>
              {pagedUsers.map((user) => (
                <tr key={user.id}>
                  <td className="sticky left-0 z-10 border-b border-line bg-[var(--panel)] px-4 py-3 align-top">
                    <div className="font-medium text-primary">{user.full_name}</div>
                    <div className="text-xs text-secondary">{user.email}</div>
                    <div className="text-xs text-secondary">{user.default_notary_label ?? "Sin notaría"}</div>
                    {rowErrors[user.id] ? <div className="mt-2 rounded-xl border border-rose-200 bg-rose-50 px-2 py-1 text-xs text-rose-700">{rowErrors[user.id]}</div> : null}
                  </td>

                  {roles.map((role) => {
                    const checked = hasAssignment(user, role);
                    const cellKey = getCellKey(user.id, role.code);
                    const isBusy = Boolean(loadingCells[cellKey]);
                    const isDisabledByRole = isAdminNotary && role.code.toLowerCase() === "super_admin";
                    return (
                      <td key={`${user.id}-${role.id}`} className="border-b border-line px-4 py-3 text-center">
                        <input
                          type="checkbox"
                          checked={checked}
                          disabled={isBusy || isDisabledByRole}
                          onChange={() => void handleToggleCell(user, role, checked)}
                          className="h-5 w-5 cursor-pointer rounded border-line text-primary disabled:cursor-not-allowed disabled:opacity-50"
                        />
                      </td>
                    );
                  })}
                </tr>
              ))}

              {pagedUsers.length === 0 ? (
                <tr>
                  <td colSpan={roles.length + 1} className="px-4 py-8 text-center text-sm text-secondary">
                    No hay usuarios para mostrar con los filtros actuales.
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>

        <div className="mt-4 flex items-center justify-between">
          <p className="text-sm text-secondary">Página {page} de {totalPages}</p>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => setPage((current) => Math.max(1, current - 1))}
              disabled={page <= 1}
              className="rounded-xl border border-line px-3 py-2 text-sm text-primary disabled:opacity-50"
            >
              Anterior
            </button>
            <button
              type="button"
              onClick={() => setPage((current) => Math.min(totalPages, current + 1))}
              disabled={page >= totalPages}
              className="rounded-xl border border-line px-3 py-2 text-sm text-primary disabled:opacity-50"
            >
              Siguiente
            </button>
          </div>
        </div>
      </section>

      {showCreateModal ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/45 px-4 py-8">
          <div className="ep-card w-full max-w-2xl rounded-[2rem] p-6">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-secondary">Nuevo rol</p>
                <h3 className="mt-2 text-2xl font-semibold text-primary">Crear rol del sistema</h3>
              </div>
              <button
                type="button"
                onClick={() => {
                  if (!isCreatingRole) {
                    setShowCreateModal(false);
                    setCreateRoleError(null);
                  }
                }}
                className="ep-card-soft inline-flex h-10 w-10 items-center justify-center rounded-2xl"
                aria-label="Cerrar"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="mt-5 grid gap-4 lg:grid-cols-2">
              <div>
                <label className="mb-2 block text-sm font-medium text-primary">Nombre</label>
                <input
                  value={newRole.name}
                  onChange={(event) => setNewRole((current) => ({ ...current, name: event.target.value }))}
                  className="ep-input h-12 w-full rounded-2xl px-4"
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-primary">Código</label>
                <input
                  value={newRole.code}
                  onChange={(event) => setNewRole((current) => ({ ...current, code: event.target.value }))}
                  className="ep-input h-12 w-full rounded-2xl px-4"
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-primary">Ámbito</label>
                <select
                  value={newRole.scope}
                  onChange={(event) => {
                    const nextValue = event.target.value;
                    if (isRoleScope(nextValue)) {
                      setNewRole((current) => ({ ...current, scope: nextValue }));
                    }
                  }}
                  className="ep-select h-12 w-full rounded-2xl px-4"
                >
                  {isAdminNotary ? null : <option value="global">global</option>}
                  <option value="notary">notary</option>
                </select>
              </div>

              <div className="ep-card-muted rounded-2xl p-4 text-xs text-secondary">
                {isAdminNotary
                  ? "Como admin_notary solo puedes crear roles de ámbito notary y no puedes usar super_admin."
                  : "Define el alcance del rol para aplicarlo globalmente o por notaría."}
              </div>

              <div className="lg:col-span-2">
                <label className="mb-2 block text-sm font-medium text-primary">Descripción</label>
                <textarea
                  value={newRole.description}
                  onChange={(event) => setNewRole((current) => ({ ...current, description: event.target.value }))}
                  className="ep-input min-h-[120px] w-full rounded-2xl px-4 py-3"
                />
              </div>
            </div>

            {createRoleError ? <div className="mt-4 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{createRoleError}</div> : null}

            <div className="mt-6 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => {
                  if (!isCreatingRole) {
                    setShowCreateModal(false);
                    setCreateRoleError(null);
                  }
                }}
                className="rounded-2xl border border-line px-5 py-3 text-sm font-semibold text-primary"
              >
                Cancelar
              </button>
              <button
                type="button"
                onClick={() => void handleCreateRole()}
                disabled={isCreatingRole}
                className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white disabled:opacity-70"
              >
                <Plus className="h-4 w-4" />
                {isCreatingRole ? "Creando..." : "Crear"}
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
