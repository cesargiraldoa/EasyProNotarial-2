"use client";

import { Fragment, useEffect, useMemo, useState } from "react";
import { Plus, Trash2, X } from "lucide-react";
import {
  createRole,
  deleteRole,
  getCurrentUser,
  getRoleCatalog,
  getRolePermissions,
  getUsers,
  updateRole,
  updateRolePermissions,
  type CurrentUser,
  type RoleCatalogItem,
  type RolePermissionItem,
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

const MODULE_ORDER = [
  "resumen",
  "comercial",
  "notarias",
  "usuarios",
  "roles",
  "minutas",
  "crear_minuta",
  "actos_plantillas",
  "lotes",
  "system_status",
  "configuracion"
] as const;

type ModuleCode = (typeof MODULE_ORDER)[number];

const MODULE_LABELS: Record<ModuleCode, string> = {
  resumen: "Resumen",
  comercial: "Comercial",
  notarias: "Notarías",
  usuarios: "Usuarios",
  roles: "Roles",
  minutas: "Minutas",
  crear_minuta: "Crear Minuta",
  actos_plantillas: "Actos / Plantillas",
  lotes: "Lotes",
  system_status: "System Status",
  configuracion: "Configuración"
};

const EMPTY_NEW_ROLE: NewRolePayload = {
  name: "",
  code: "",
  scope: "notary",
  description: ""
};

function isRoleScope(value: string): value is RoleScope {
  return value === "global" || value === "notary";
}

function normalizePermissions(items: RolePermissionItem[]): RolePermissionItem[] {
  const byModule = new Map<string, boolean>();
  items.forEach((item) => {
    byModule.set(item.module_code, item.can_access === true);
  });

  return MODULE_ORDER.map((moduleCode) => ({
    module_code: moduleCode,
    can_access: byModule.get(moduleCode) ?? false
  }));
}

function getInitialPermissions(): RolePermissionItem[] {
  return MODULE_ORDER.map((moduleCode) => ({
    module_code: moduleCode,
    can_access: moduleCode === "resumen" || moduleCode === "minutas"
  }));
}

function ToggleSwitch({ checked, disabled, onToggle }: { checked: boolean; disabled: boolean; onToggle: () => void }) {
  const isChecked = checked === true;
  return (
    <div
      role="switch"
      aria-checked={isChecked}
      aria-disabled={disabled}
      onClick={() => {
        if (!disabled) {
          onToggle();
        }
      }}
      className={`relative h-7 w-14 rounded-full border transition ${
        disabled
          ? "cursor-not-allowed border-line bg-[var(--panel-soft)] opacity-60"
          : isChecked
            ? "cursor-pointer border-primary bg-primary"
            : "cursor-pointer border-line bg-[var(--panel-soft)]"
      }`}
    >
      <div
        className={`absolute top-0.5 h-5.5 w-5.5 rounded-full bg-white shadow transition-all ${
          isChecked ? "left-8" : "left-0.5"
        }`}
      />
    </div>
  );
}

export function RolesWorkspace() {
  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null);
  const [roles, setRoles] = useState<RoleCatalogItem[]>([]);
  const [users, setUsers] = useState<UserRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [globalError, setGlobalError] = useState<string | null>(null);

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newRole, setNewRole] = useState<NewRolePayload>(EMPTY_NEW_ROLE);
  const [isCreatingRole, setIsCreatingRole] = useState(false);
  const [createRoleError, setCreateRoleError] = useState<string | null>(null);

  const [selectedRoleId, setSelectedRoleId] = useState<number | null>(null);
  const [roleEditor, setRoleEditor] = useState<RoleEditorState>({ name: "", description: "" });
  const [isSavingRole, setIsSavingRole] = useState(false);
  const [roleEditorError, setRoleEditorError] = useState<string | null>(null);
  const [isDeletingRole, setIsDeletingRole] = useState(false);

  const [permissions, setPermissions] = useState<RolePermissionItem[]>([]);
  const [initialPermissions, setInitialPermissions] = useState<RolePermissionItem[]>([]);
  const [isLoadingPermissions, setIsLoadingPermissions] = useState(false);
  const [isSavingPermissions, setIsSavingPermissions] = useState(false);
  const [permissionsFeedback, setPermissionsFeedback] = useState<string | null>(null);
  const [permissionsError, setPermissionsError] = useState<string | null>(null);

  const roleCodes = useMemo(
    () => (currentUser?.role_codes ?? []).map((item) => item.toLowerCase()),
    [currentUser?.role_codes]
  );

  const isSuperAdmin = roleCodes.includes("super_admin");
  const isAdminNotary = roleCodes.includes("admin_notary");
  const canManageRoles = isSuperAdmin || isAdminNotary;

  const selectedRole = useMemo(
    () => roles.find((role) => role.id === selectedRoleId) ?? null,
    [roles, selectedRoleId]
  );

  const hasPermissionChanges = useMemo(() => {
    if (permissions.length !== initialPermissions.length) {
      return true;
    }
    return permissions.some((item, index) => {
      const source = initialPermissions[index];
      return item.module_code !== source?.module_code || item.can_access !== source?.can_access;
    });
  }, [initialPermissions, permissions]);

  useEffect(() => {
    void loadWorkspace();
  }, []);

  useEffect(() => {
    if (!selectedRole) {
      setPermissions([]);
      setInitialPermissions([]);
      return;
    }
    const selectedRoleIdForPermissions = selectedRole.id;

    let isCancelled = false;

    async function loadSelectedRolePermissions() {
      setIsLoadingPermissions(true);
      setPermissionsError(null);
      setPermissionsFeedback(null);
      try {
        const response = await getRolePermissions(selectedRoleIdForPermissions);
        if (isCancelled) {
          return;
        }
        const normalized = normalizePermissions(response);
        setPermissions(normalized);
        setInitialPermissions(
          normalized.map((item) => ({
            ...item
          }))
        );
      } catch (error) {
        if (!isCancelled) {
          setPermissions([]);
          setInitialPermissions([]);
          setPermissionsError(error instanceof Error ? error.message : "No fue posible cargar los permisos.");
        }
      } finally {
        if (!isCancelled) {
          setIsLoadingPermissions(false);
        }
      }
    }

    void loadSelectedRolePermissions();

    return () => {
      isCancelled = true;
    };
  }, [selectedRole]);

  async function loadWorkspace(selectRoleId?: number | null) {
    setIsLoading(true);
    setGlobalError(null);
    try {
      const [nextCurrentUser, nextRoles, nextUsers] = await Promise.all([getCurrentUser(), getRoleCatalog(), getUsers()]);
      setCurrentUser(nextCurrentUser);
      setRoles(nextRoles);
      setUsers(nextUsers);

      if (typeof selectRoleId === "number") {
        const exists = nextRoles.some((role) => role.id === selectRoleId);
        setSelectedRoleId(exists ? selectRoleId : null);
      } else {
        setSelectedRoleId((currentSelectedRoleId) => {
          if (currentSelectedRoleId === null) {
            return null;
          }
          const exists = nextRoles.some((role) => role.id === currentSelectedRoleId);
          return exists ? currentSelectedRoleId : null;
        });
      }
    } catch (error) {
      setGlobalError(error instanceof Error ? error.message : "No fue posible cargar los roles.");
    } finally {
      setIsLoading(false);
    }
  }

  function countRoleAssignments(role: RoleCatalogItem): number {
    return users.reduce((count, user) => {
      const found = user.assignments.some((assignment) => assignment.role_code === role.code);
      return count + (found ? 1 : 0);
    }, 0);
  }

  function selectRole(role: RoleCatalogItem) {
    const nextSelectedRoleId = selectedRoleId === role.id ? null : role.id;
    setSelectedRoleId(nextSelectedRoleId);
    if (nextSelectedRoleId === null) {
      setRoleEditor({ name: "", description: "" });
      setPermissionsFeedback(null);
      setPermissionsError(null);
      return;
    }
    setRoleEditor({
      name: role.name,
      description: role.description ?? ""
    });
    setRoleEditorError(null);
    setPermissionsFeedback(null);
    setPermissionsError(null);
  }

  async function handleSaveRole() {
    if (!selectedRole) {
      return;
    }

    setIsSavingRole(true);
    setRoleEditorError(null);
    try {
      await updateRole(selectedRole.id, {
        name: roleEditor.name.trim(),
        description: roleEditor.description.trim()
      });
      await loadWorkspace(selectedRole.id);
    } catch (error) {
      setRoleEditorError(error instanceof Error ? error.message : "No fue posible actualizar el rol.");
    } finally {
      setIsSavingRole(false);
    }
  }

  async function handleDeleteRole(role: RoleCatalogItem) {
    if (!isSuperAdmin) {
      return;
    }

    setIsDeletingRole(true);
    setRoleEditorError(null);
    try {
      await deleteRole(role.id);
      await loadWorkspace(selectedRole?.id === role.id ? null : selectedRole?.id ?? null);
    } catch (error) {
      setRoleEditorError(error instanceof Error ? error.message : "No fue posible eliminar el rol.");
    } finally {
      setIsDeletingRole(false);
    }
  }

  function togglePermission(moduleCode: string) {
    setPermissions((current) =>
      current.map((item) =>
        item.module_code === moduleCode
          ? {
              ...item,
              can_access: !item.can_access
            }
          : item
      )
    );
    setPermissionsFeedback(null);
    setPermissionsError(null);
  }

  async function handleSavePermissions() {
    if (!selectedRole) {
      return;
    }

    setIsSavingPermissions(true);
    setPermissionsFeedback(null);
    setPermissionsError(null);
    try {
      const normalized = normalizePermissions(
        await updateRolePermissions(selectedRole.id, normalizePermissions(permissions))
      );
      setPermissions(normalized);
      setInitialPermissions(normalized);
      setPermissionsFeedback("Permisos guardados ✓");
    } catch (error) {
      setPermissionsError(error instanceof Error ? error.message : "No fue posible guardar los permisos.");
    } finally {
      setIsSavingPermissions(false);
    }
  }

  async function handleCreateRole() {
    setCreateRoleError(null);

    const code = newRole.code.trim().toLowerCase();
    if (isAdminNotary && code === "super_admin") {
      setCreateRoleError("Admin Notaría no puede crear el código super_admin.");
      return;
    }

    setIsCreatingRole(true);
    try {
      const createdRole = await createRole({
        name: newRole.name.trim(),
        code,
        scope: newRole.scope,
        description: newRole.description.trim()
      });

      await updateRolePermissions(createdRole.id, getInitialPermissions());
      setShowCreateModal(false);
      setNewRole(EMPTY_NEW_ROLE);
      await loadWorkspace(createdRole.id);

      const selected = {
        id: createdRole.id,
        name: createdRole.name,
        description: createdRole.description,
        code: createdRole.code,
        scope: createdRole.scope
      };
      selectRole(selected);
    } catch (error) {
      setCreateRoleError(error instanceof Error ? error.message : "No fue posible crear el rol.");
    } finally {
      setIsCreatingRole(false);
    }
  }

  if (isLoading) {
    return <div className="ep-card rounded-[2rem] p-6 text-secondary">Cargando catálogo de roles...</div>;
  }

  return (
    <div className="space-y-6">
      <section className="ep-card rounded-[2rem] p-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div>
            <h1 className="text-3xl font-semibold tracking-[-0.03em] text-primary">Roles y permisos</h1>
            <p className="mt-2 text-sm text-secondary">Catálogo de roles y configuración de permisos por módulo.</p>
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

        {globalError ? <div className="mt-4 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{globalError}</div> : null}

        <div className="mt-6 overflow-x-auto">
          <table className="min-w-full border-separate border-spacing-0">
            <thead>
              <tr>
                <th className="border-b border-line px-4 py-3 text-left text-xs uppercase tracking-[0.18em] text-secondary">Nombre</th>
                <th className="border-b border-line px-4 py-3 text-left text-xs uppercase tracking-[0.18em] text-secondary">Código</th>
                <th className="border-b border-line px-4 py-3 text-left text-xs uppercase tracking-[0.18em] text-secondary">Ámbito</th>
                <th className="border-b border-line px-4 py-3 text-left text-xs uppercase tracking-[0.18em] text-secondary">Descripción</th>
                <th className="border-b border-line px-4 py-3 text-left text-xs uppercase tracking-[0.18em] text-secondary">Usuarios asignados</th>
                <th className="border-b border-line px-4 py-3 text-left text-xs uppercase tracking-[0.18em] text-secondary">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {roles.map((role) => {
                const isSuperAdminRole = role.code.toLowerCase() === "super_admin";
                const roleBlockedForAdminNotary = isAdminNotary && isSuperAdminRole;
                const roleAssignedCount = countRoleAssignments(role);
                const isExpanded = selectedRoleId === role.id;
                const canEditRole = !(isAdminNotary && role.code.toLowerCase() === "super_admin");

                return (
                  <Fragment key={role.id}>
                    <tr>
                      <td className="border-b border-line px-4 py-4 text-sm font-semibold text-primary">{role.name}</td>
                      <td className="border-b border-line px-4 py-4 text-sm text-secondary">{role.code}</td>
                      <td className="border-b border-line px-4 py-4 text-sm text-secondary">{role.scope}</td>
                      <td className="border-b border-line px-4 py-4 text-sm text-secondary">{role.description || "—"}</td>
                      <td className="border-b border-line px-4 py-4 text-sm text-secondary">{roleAssignedCount}</td>
                      <td className="border-b border-line px-4 py-4">
                        <div className="flex flex-wrap gap-2">
                          <button
                            type="button"
                            onClick={() => selectRole(role)}
                            className="rounded-xl border border-line px-3 py-2 text-xs font-semibold text-primary hover:bg-[var(--panel-soft)]"
                          >
                            {isExpanded ? "Cerrar" : "Editar permisos"}
                          </button>
                          {isSuperAdmin ? (
                            <button
                              type="button"
                              onClick={() => void handleDeleteRole(role)}
                              disabled={isDeletingRole || roleAssignedCount > 0}
                              className="inline-flex items-center gap-1 rounded-xl border border-rose-300/70 bg-rose-50 px-3 py-2 text-xs font-semibold text-rose-700 disabled:cursor-not-allowed disabled:opacity-60"
                            >
                              <Trash2 className="h-3.5 w-3.5" />
                              Eliminar
                            </button>
                          ) : null}
                        </div>
                        {roleBlockedForAdminNotary ? (
                          <p className="mt-2 text-xs text-amber-600">Edición restringida para admin_notary.</p>
                        ) : null}
                        {isSuperAdmin && roleAssignedCount > 0 ? (
                          <p className="mt-2 text-xs text-secondary">No se puede eliminar: tiene usuarios asignados.</p>
                        ) : null}
                      </td>
                    </tr>
                    <tr>
                      <td colSpan={6} className="border-b border-line p-0">
                        <div
                          className={`transition-all duration-300 ease-out ${
                            isExpanded ? "max-h-[1200px] opacity-100" : "max-h-0 opacity-0"
                          } overflow-hidden`}
                        >
                          <div className="ep-card-muted p-6">
                            <div className="grid gap-6 lg:grid-cols-2">
                              <div className="space-y-4">
                                <h3 className="text-lg font-semibold text-primary">Datos del rol</h3>
                                <div>
                                  <label className="mb-2 block text-sm font-medium text-primary">Nombre</label>
                                  <input
                                    value={isExpanded ? roleEditor.name : role.name}
                                    disabled={!canEditRole || isSavingRole}
                                    onChange={(event) => setRoleEditor((current) => ({ ...current, name: event.target.value }))}
                                    className="ep-input h-12 w-full rounded-2xl px-4 disabled:cursor-not-allowed disabled:opacity-60"
                                  />
                                </div>
                                <div>
                                  <label className="mb-2 block text-sm font-medium text-primary">Descripción</label>
                                  <textarea
                                    value={isExpanded ? roleEditor.description : role.description ?? ""}
                                    disabled={!canEditRole || isSavingRole}
                                    onChange={(event) => setRoleEditor((current) => ({ ...current, description: event.target.value }))}
                                    className="ep-input min-h-[120px] w-full rounded-2xl px-4 py-3 disabled:cursor-not-allowed disabled:opacity-60"
                                  />
                                </div>
                                <div className="grid gap-4 md:grid-cols-2">
                                  <div>
                                    <label className="mb-2 block text-sm font-medium text-primary">Código</label>
                                    <div className="ep-card-soft rounded-2xl px-4 py-3 text-sm text-secondary">{role.code}</div>
                                  </div>
                                  <div>
                                    <label className="mb-2 block text-sm font-medium text-primary">Ámbito</label>
                                    <div className="ep-card-soft rounded-2xl px-4 py-3 text-sm text-secondary">{role.scope}</div>
                                  </div>
                                </div>
                                {!canEditRole ? (
                                  <p className="text-sm text-amber-700">admin_notary no puede editar el rol super_admin.</p>
                                ) : null}
                                {roleEditorError ? (
                                  <div className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{roleEditorError}</div>
                                ) : null}
                                <div>
                                  <button
                                    type="button"
                                    onClick={() => void handleSaveRole()}
                                    disabled={!canEditRole || isSavingRole}
                                    className="rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
                                  >
                                    {isSavingRole ? "Guardando..." : "Guardar cambios"}
                                  </button>
                                </div>
                              </div>

                              <div className="space-y-4">
                                <h3 className="text-lg font-semibold text-primary">Permisos por módulo</h3>
                                {isLoadingPermissions ? <p className="text-sm text-secondary">Cargando permisos del rol...</p> : null}
                                {!isLoadingPermissions ? (
                                  <div className="overflow-x-auto">
                                    <table className="min-w-full border-separate border-spacing-0">
                                      <thead>
                                        <tr>
                                          <th className="border-b border-line px-3 py-2 text-left text-xs uppercase tracking-[0.18em] text-secondary">Módulo</th>
                                          <th className="border-b border-line px-3 py-2 text-left text-xs uppercase tracking-[0.18em] text-secondary">Acceso</th>
                                        </tr>
                                      </thead>
                                      <tbody>
                                        {permissions.map((item) => {
                                          const moduleCode = item.module_code as ModuleCode;
                                          return (
                                            <tr key={item.module_code}>
                                              <td className="border-b border-line px-3 py-3 text-sm text-primary">
                                                {MODULE_LABELS[moduleCode] ?? item.module_code}
                                              </td>
                                              <td className="border-b border-line px-3 py-3">
                                                <ToggleSwitch
                                                  checked={item.can_access === true}
                                                  disabled={!canEditRole || isSavingPermissions}
                                                  onToggle={() => togglePermission(item.module_code)}
                                                />
                                              </td>
                                            </tr>
                                          );
                                        })}
                                      </tbody>
                                    </table>
                                  </div>
                                ) : null}
                                {!canEditRole ? (
                                  <p className="text-sm text-amber-700">admin_notary no puede editar permisos del rol super_admin.</p>
                                ) : null}
                                {permissionsFeedback ? <p className="text-sm text-emerald-700">{permissionsFeedback}</p> : null}
                                {permissionsError ? <p className="text-sm text-rose-700">{permissionsError}</p> : null}
                                {!isLoadingPermissions && hasPermissionChanges ? (
                                  <div>
                                    <button
                                      type="button"
                                      onClick={() => void handleSavePermissions()}
                                      disabled={!canEditRole || isSavingPermissions}
                                      className="rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
                                    >
                                      {isSavingPermissions ? "Guardando..." : "Guardar permisos"}
                                    </button>
                                  </div>
                                ) : null}
                              </div>
                            </div>
                          </div>
                        </div>
                      </td>
                    </tr>
                  </Fragment>
                );
              })}
            </tbody>
          </table>
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
                Permisos iniciales: Resumen y Minutas activos. Los demás módulos se crean sin acceso.
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
