"use client";

import { Fragment, useEffect, useMemo, useState } from "react";
import { Copy, Eye, EyeOff, Plus, RefreshCw } from "lucide-react";
import {
  createUser,
  getCurrentUser,
  getNotaries,
  getRoleCatalog,
  getUsers,
  updateUser,
  type CurrentUser,
  type NotaryRecord,
  type RoleCatalogItem,
  type UserAssignmentPayload,
  type UserPayload,
  type UserRecord
} from "@/lib/api";

type UserEditorState = {
  email: string;
  full_name: string;
  password: string;
  is_active: boolean;
  phone: string;
  job_title: string;
  default_notary_id: number | null;
  assignments: UserAssignmentPayload[];
};

type AssignmentDraft = {
  role_code: string;
  notary_id: number | null;
};

type EditorFeedback = {
  kind: "success" | "error";
  message: string;
};

const PAGE_SIZE = 20;

const EMPTY_EDITOR: UserEditorState = {
  email: "",
  full_name: "",
  password: "",
  is_active: true,
  phone: "",
  job_title: "",
  default_notary_id: null,
  assignments: []
};

function toEditorState(user: UserRecord): UserEditorState {
  return {
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
  };
}

function normalizePayload(state: UserEditorState): UserPayload {
  return {
    email: state.email.trim().toLowerCase(),
    full_name: state.full_name.trim(),
    password: state.password.trim() === "" ? null : state.password,
    is_active: state.is_active,
    phone: state.phone.trim(),
    job_title: state.job_title.trim(),
    default_notary_id: state.default_notary_id,
    assignments: state.assignments
      .filter((item) => item.role_code.trim() !== "")
      .map((item) => ({
        role_code: item.role_code,
        notary_id: item.notary_id
      }))
  };
}

export function UsersAdminWorkspace() {
  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null);
  const [users, setUsers] = useState<UserRecord[]>([]);
  const [roles, setRoles] = useState<RoleCatalogItem[]>([]);
  const [notaries, setNotaries] = useState<NotaryRecord[]>([]);

  const [isLoading, setIsLoading] = useState(true);
  const [globalError, setGlobalError] = useState<string | null>(null);

  const [search, setSearch] = useState("");
  const [notaryFilter, setNotaryFilter] = useState<string>("all");
  const [roleFilter, setRoleFilter] = useState<string>("all");
  const [statusFilter, setStatusFilter] = useState<"all" | "active" | "inactive">("all");
  const [page, setPage] = useState(1);

  const [openUserId, setOpenUserId] = useState<number | "new" | null>(null);
  const [editorState, setEditorState] = useState<UserEditorState>(EMPTY_EDITOR);
  const [roleDraft, setRoleDraft] = useState<AssignmentDraft>({ role_code: "", notary_id: null });
  const [showAddRole, setShowAddRole] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const [isSavingUser, setIsSavingUser] = useState(false);
  const [isSavingRoles, setIsSavingRoles] = useState(false);
  const [feedback, setFeedback] = useState<EditorFeedback | null>(null);

  const roleCodes = useMemo(
    () => (currentUser?.role_codes ?? []).map((item) => item.toLowerCase()),
    [currentUser?.role_codes]
  );

  const isSuperAdmin = roleCodes.includes("super_admin");

  const visibleRoles = useMemo(() => {
    if (isSuperAdmin) {
      return roles;
    }
    return roles.filter((role) => role.code.toLowerCase() !== "super_admin");
  }, [isSuperAdmin, roles]);

  useEffect(() => {
    void loadWorkspace();
  }, []);

  async function loadWorkspace() {
    setIsLoading(true);
    setGlobalError(null);
    try {
      const [nextCurrentUser, nextUsers, nextRoles, nextNotaries] = await Promise.all([
        getCurrentUser(),
        getUsers(),
        getRoleCatalog(),
        getNotaries()
      ]);
      setCurrentUser(nextCurrentUser);
      setUsers(nextUsers);
      setRoles(nextRoles);
      setNotaries(nextNotaries);
    } catch (error) {
      setGlobalError(error instanceof Error ? error.message : "No fue posible cargar usuarios.");
    } finally {
      setIsLoading(false);
    }
  }

  const filteredUsers = useMemo(() => {
    const normalized = search.trim().toLowerCase();
    return users.filter((user) => {
      const matchesSearch =
        normalized === ""
        || user.full_name.toLowerCase().includes(normalized)
        || user.email.toLowerCase().includes(normalized);
      const matchesNotary =
        !isSuperAdmin
        || notaryFilter === "all"
        || String(user.default_notary_id ?? "") === notaryFilter;
      const firstRole = user.assignments[0]?.role_code ?? user.roles[0] ?? "";
      const matchesRole = roleFilter === "all" || firstRole === roleFilter;
      const matchesStatus =
        statusFilter === "all"
        || (statusFilter === "active" && user.is_active)
        || (statusFilter === "inactive" && !user.is_active);

      return matchesSearch && matchesNotary && matchesRole && matchesStatus;
    });
  }, [isSuperAdmin, notaryFilter, roleFilter, search, statusFilter, users]);

  const totalPages = Math.max(1, Math.ceil(filteredUsers.length / PAGE_SIZE));

  const paginatedUsers = useMemo(() => {
    const safePage = Math.min(page, totalPages);
    const start = (safePage - 1) * PAGE_SIZE;
    return filteredUsers.slice(start, start + PAGE_SIZE);
  }, [filteredUsers, page, totalPages]);

  useEffect(() => {
    if (page > totalPages) {
      setPage(totalPages);
    }
  }, [page, totalPages]);

  function resetEditor(user: UserRecord | null) {
    setEditorState(user ? toEditorState(user) : EMPTY_EDITOR);
    setRoleDraft({ role_code: "", notary_id: null });
    setShowAddRole(false);
    setShowPassword(false);
    setFeedback(null);
  }

  function openNewAccordion() {
    setOpenUserId("new");
    resetEditor(null);
    setPage(1);
  }

  function toggleUserAccordion(user: UserRecord) {
    if (openUserId === user.id) {
      setOpenUserId(null);
      setFeedback(null);
      setShowAddRole(false);
      setShowPassword(false);
      return;
    }
    setOpenUserId(user.id);
    resetEditor(user);
  }

  function updateField<K extends keyof UserEditorState>(key: K, value: UserEditorState[K]) {
    setEditorState((current) => ({ ...current, [key]: value }));
  }

  async function copyPasswordToClipboard() {
    const password = editorState.password.trim();
    if (password === "") {
      setFeedback({ kind: "error", message: "No hay contraseña para copiar." });
      return;
    }

    try {
      await navigator.clipboard.writeText(editorState.password);
      setFeedback({ kind: "success", message: "Contraseña copiada al portapapeles." });
    } catch {
      setFeedback({ kind: "error", message: "No fue posible copiar la contraseña." });
    }
  }

  function generateTemporaryPassword() {
    const suffix = Math.floor(1000 + Math.random() * 9000);
    updateField("password", `EasyPro2026-${suffix}*`);
    setShowPassword(true);
    setFeedback({ kind: "success", message: "Contraseña temporal generada. Cópiala antes de guardar o compartir." });
  }

  function removeAssignment(index: number) {
    setEditorState((current) => ({
      ...current,
      assignments: current.assignments.filter((_, itemIndex) => itemIndex !== index)
    }));
    setFeedback(null);
  }

  function addAssignmentDraft() {
    if (!roleDraft.role_code) {
      return;
    }
    setEditorState((current) => ({
      ...current,
      assignments: [
        ...current.assignments,
        {
          role_code: roleDraft.role_code,
          notary_id: roleDraft.notary_id
        }
      ]
    }));
    setRoleDraft({ role_code: "", notary_id: null });
    setShowAddRole(false);
    setFeedback(null);
  }

  async function handleCreateUser() {
    setIsSavingUser(true);
    setFeedback(null);
    try {
      await createUser(normalizePayload(editorState));
      await loadWorkspace();
      setOpenUserId(null);
      setFeedback({ kind: "success", message: "Usuario creado correctamente." });
    } catch (error) {
      setFeedback({
        kind: "error",
        message: error instanceof Error ? error.message : "No fue posible crear el usuario."
      });
    } finally {
      setIsSavingUser(false);
    }
  }

  async function handleSaveUser(userId: number) {
    setIsSavingUser(true);
    setFeedback(null);
    try {
      await updateUser(userId, normalizePayload(editorState));
      await loadWorkspace();
      const refreshedUser = users.find((item) => item.id === userId) ?? null;
      if (refreshedUser) {
        setEditorState(toEditorState(refreshedUser));
      }
      setFeedback({ kind: "success", message: "Usuario actualizado correctamente." });
    } catch (error) {
      setFeedback({
        kind: "error",
        message: error instanceof Error ? error.message : "No fue posible guardar cambios."
      });
    } finally {
      setIsSavingUser(false);
    }
  }

  async function handleSaveRoles(userId: number) {
    setIsSavingRoles(true);
    setFeedback(null);
    try {
      const source = users.find((item) => item.id === userId);
      if (!source) {
        throw new Error("No se encontró el usuario seleccionado.");
      }
      await updateUser(userId, {
        email: source.email,
        full_name: source.full_name,
        password: null,
        is_active: source.is_active,
        phone: source.phone ?? "",
        job_title: source.job_title ?? "",
        default_notary_id: source.default_notary_id ?? null,
        assignments: editorState.assignments
      });
      await loadWorkspace();
      setFeedback({ kind: "success", message: "Asignaciones de roles actualizadas." });
    } catch (error) {
      setFeedback({
        kind: "error",
        message: error instanceof Error ? error.message : "No fue posible actualizar roles."
      });
    } finally {
      setIsSavingRoles(false);
    }
  }

  function clearFilters() {
    setSearch("");
    setNotaryFilter("all");
    setRoleFilter("all");
    setStatusFilter("all");
    setPage(1);
  }

  function onSearchChange(value: string) {
    setSearch(value);
    setPage(1);
  }

  function onNotaryFilterChange(value: string) {
    setNotaryFilter(value);
    setPage(1);
  }

  function onRoleFilterChange(value: string) {
    setRoleFilter(value);
    setPage(1);
  }

  function onStatusFilterChange(value: "all" | "active" | "inactive") {
    setStatusFilter(value);
    setPage(1);
  }

  function roleNameFromCode(code: string): string {
    const found = roles.find((role) => role.code === code);
    return found?.name ?? code;
  }

  function notaryLabelFromId(id: number | null): string {
    if (id === null) {
      return "Global";
    }
    return notaries.find((notary) => notary.id === id)?.notary_label ?? "Sin notaría";
  }

  function renderAccordion(userId: number | "new") {
    const isNew = userId === "new";
    const roleOptions = visibleRoles;
    const canSetNotary = isSuperAdmin;
    const draftRole = roles.find((role) => role.code === roleDraft.role_code);
    const draftIsGlobal = draftRole?.scope === "global";

    return (
      <div className="ep-card-muted p-6">
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-primary">Datos personales</h3>
            <div>
              <label className="mb-2 block text-sm font-medium text-primary">Nombre completo</label>
              <input
                value={editorState.full_name}
                onChange={(event) => updateField("full_name", event.target.value)}
                className="ep-input h-12 w-full rounded-2xl px-4"
              />
            </div>
            <div>
              <label className="mb-2 block text-sm font-medium text-primary">Email</label>
              <input
                value={editorState.email}
                onChange={(event) => updateField("email", event.target.value)}
                className="ep-input h-12 w-full rounded-2xl px-4"
              />
            </div>
            <div>
              <label className="mb-2 block text-sm font-medium text-primary">Contraseña</label>
              <div className="space-y-3">
                <div className="flex flex-col gap-3 lg:flex-row">
                  <input
                    type={showPassword ? "text" : "password"}
                    value={editorState.password}
                    onChange={(event) => updateField("password", event.target.value)}
                    placeholder={isNew ? "Define o genera una contraseña" : "Dejar vacío para conservar"}
                    className="ep-input h-12 min-w-0 flex-1 rounded-2xl px-4"
                  />
                  <div className="grid grid-cols-1 gap-2 sm:grid-cols-3 lg:flex lg:gap-2">
                    <button
                      type="button"
                      onClick={() => setShowPassword((current) => !current)}
                      className="inline-flex h-12 items-center justify-center gap-2 rounded-2xl border border-line bg-[var(--panel)] px-4 text-sm font-semibold text-primary"
                    >
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      {showPassword ? "Ocultar" : "Ver"}
                    </button>
                    <button
                      type="button"
                      onClick={generateTemporaryPassword}
                      className="inline-flex h-12 items-center justify-center gap-2 rounded-2xl border border-line bg-[var(--panel)] px-4 text-sm font-semibold text-primary"
                    >
                      <RefreshCw className="h-4 w-4" />
                      Generar contraseña
                    </button>
                    <button
                      type="button"
                      onClick={() => void copyPasswordToClipboard()}
                      disabled={editorState.password.trim() === ""}
                      className="inline-flex h-12 items-center justify-center gap-2 rounded-2xl border border-line bg-[var(--panel)] px-4 text-sm font-semibold text-primary disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      <Copy className="h-4 w-4" />
                      Copiar
                    </button>
                  </div>
                </div>
                <p className="text-xs text-secondary">
                  {isNew
                    ? "Define o genera una contraseña temporal para entregar al usuario."
                    : "Déjala vacía si no deseas cambiar la contraseña."}
                </p>
              </div>
            </div>
            <div>
              <label className="mb-2 block text-sm font-medium text-primary">Teléfono</label>
              <input
                value={editorState.phone}
                onChange={(event) => updateField("phone", event.target.value)}
                className="ep-input h-12 w-full rounded-2xl px-4"
              />
            </div>
            <div>
              <label className="mb-2 block text-sm font-medium text-primary">Cargo</label>
              <input
                value={editorState.job_title}
                onChange={(event) => updateField("job_title", event.target.value)}
                className="ep-input h-12 w-full rounded-2xl px-4"
              />
            </div>
            <div>
              <label className="mb-2 block text-sm font-medium text-primary">Estado</label>
              <select
                value={editorState.is_active ? "active" : "inactive"}
                onChange={(event) => updateField("is_active", event.target.value === "active")}
                className="ep-select h-12 w-full rounded-2xl px-4"
              >
                <option value="active">Activo</option>
                <option value="inactive">Inactivo</option>
              </select>
            </div>
            {canSetNotary ? (
              <div>
                <label className="mb-2 block text-sm font-medium text-primary">Notaría por defecto</label>
                <select
                  value={editorState.default_notary_id?.toString() ?? ""}
                  onChange={(event) => updateField("default_notary_id", event.target.value ? Number(event.target.value) : null)}
                  className="ep-select h-12 w-full rounded-2xl px-4"
                >
                  <option value="">Sin notaría por defecto</option>
                  {notaries.map((notary) => (
                    <option key={notary.id} value={notary.id}>
                      {notary.notary_label}
                    </option>
                  ))}
                </select>
              </div>
            ) : null}
            <div>
              <button
                type="button"
                onClick={() => {
                  if (isNew) {
                    void handleCreateUser();
                  } else {
                    void handleSaveUser(userId);
                  }
                }}
                disabled={isSavingUser}
                className="rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
              >
                {isSavingUser ? "Guardando..." : isNew ? "Crear usuario" : "Guardar cambios"}
              </button>
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-primary">Asignaciones de roles</h3>
            <div className="space-y-2">
              {editorState.assignments.length === 0 ? (
                <div className="ep-card-soft rounded-2xl px-4 py-3 text-sm text-secondary">Sin asignaciones.</div>
              ) : null}
              {editorState.assignments.map((assignment, index) => (
                <div key={`${assignment.role_code}-${index}`} className="ep-card-soft flex items-center justify-between gap-3 rounded-2xl px-4 py-3">
                  <div className="flex flex-wrap items-center gap-2 text-sm">
                    <span className="rounded-full bg-primary/10 px-3 py-1 text-xs font-semibold text-primary">
                      {roleNameFromCode(assignment.role_code)}
                    </span>
                    <span className="text-secondary">{notaryLabelFromId(assignment.notary_id ?? null)}</span>
                  </div>
                  <button
                    type="button"
                    onClick={() => removeAssignment(index)}
                    className="rounded-xl border border-rose-300/70 bg-rose-50 px-3 py-2 text-xs font-semibold text-rose-700"
                  >
                    Quitar
                  </button>
                </div>
              ))}
            </div>

            {!showAddRole ? (
              <button
                type="button"
                onClick={() => {
                  setShowAddRole(true);
                  setFeedback(null);
                }}
                className="inline-flex items-center gap-2 rounded-2xl border border-line bg-[var(--panel)] px-4 py-2 text-sm font-semibold text-primary"
              >
                <Plus className="h-4 w-4" />
                Agregar rol
              </button>
            ) : (
              <div className="ep-card-soft space-y-3 rounded-2xl p-4">
                <div>
                  <label className="mb-2 block text-sm font-medium text-primary">Rol</label>
                  <select
                    value={roleDraft.role_code}
                    onChange={(event) => {
                      const nextCode = event.target.value;
                      const selectedRole = roles.find((role) => role.code === nextCode);
                      setRoleDraft({
                        role_code: nextCode,
                        notary_id: selectedRole?.scope === "global" ? null : roleDraft.notary_id
                      });
                    }}
                    className="ep-select h-11 w-full rounded-2xl px-4"
                  >
                    <option value="">Selecciona un rol</option>
                    {roleOptions.map((role) => (
                      <option key={role.code} value={role.code}>
                        {role.name}
                      </option>
                    ))}
                  </select>
                </div>
                {canSetNotary ? (
                  <div>
                    <label className="mb-2 block text-sm font-medium text-primary">Notaría</label>
                    <select
                      value={roleDraft.notary_id?.toString() ?? ""}
                      onChange={(event) =>
                        setRoleDraft((current) => ({
                          ...current,
                          notary_id: event.target.value ? Number(event.target.value) : null
                        }))
                      }
                      disabled={draftIsGlobal || !roleDraft.role_code}
                      className="ep-select h-11 w-full rounded-2xl px-4 disabled:opacity-60"
                    >
                      <option value="">{draftIsGlobal ? "Ámbito global" : "Selecciona una notaría"}</option>
                      {notaries.map((notary) => (
                        <option key={notary.id} value={notary.id}>
                          {notary.notary_label}
                        </option>
                      ))}
                    </select>
                  </div>
                ) : null}
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={addAssignmentDraft}
                    className="rounded-2xl bg-primary px-4 py-2 text-sm font-semibold text-white"
                  >
                    Agregar
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowAddRole(false);
                      setRoleDraft({ role_code: "", notary_id: null });
                    }}
                    className="rounded-2xl border border-line px-4 py-2 text-sm font-semibold text-primary"
                  >
                    Cancelar
                  </button>
                </div>
              </div>
            )}

            {!isNew ? (
              <div>
                <button
                  type="button"
                  onClick={() => void handleSaveRoles(userId)}
                  disabled={isSavingRoles}
                  className="rounded-2xl border border-line bg-[var(--panel)] px-5 py-3 text-sm font-semibold text-primary disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {isSavingRoles ? "Guardando roles..." : "Guardar roles"}
                </button>
              </div>
            ) : null}
          </div>
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
    );
  }

  if (isLoading) {
    return <div className="ep-card rounded-[2rem] p-6 text-secondary">Cargando usuarios, roles y notarías...</div>;
  }

  const isCreating = openUserId === "new";

  return (
    <div className="space-y-6">
      <section className="ep-card rounded-[2rem] p-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div>
            <h1 className="text-3xl font-semibold tracking-[-0.03em] text-primary">Usuarios y roles</h1>
          </div>
          <button
            type="button"
            onClick={openNewAccordion}
            className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white shadow-panel"
          >
            <Plus className="h-4 w-4" />
            Nuevo usuario
          </button>
        </div>

        {globalError ? <div className="mt-4 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{globalError}</div> : null}

        <div className="mt-6 grid gap-4 md:grid-cols-3">
          <div className="ep-card-muted rounded-[1.5rem] p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-secondary">Usuarios visibles</p>
            <p className="mt-3 text-3xl font-semibold text-primary">{filteredUsers.length}</p>
          </div>
          <div className="ep-card-muted rounded-[1.5rem] p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-secondary">Roles disponibles</p>
            <p className="mt-3 text-3xl font-semibold text-primary">{roles.length}</p>
          </div>
          <div className="ep-card-muted rounded-[1.5rem] p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-secondary">Notarías asignables</p>
            <p className="mt-3 text-3xl font-semibold text-primary">{notaries.length}</p>
          </div>
        </div>

        <div className="mt-4 grid gap-3 lg:grid-cols-[minmax(0,2fr)_minmax(0,1fr)_minmax(0,1fr)_minmax(0,1fr)_auto]">
          <input
            value={search}
            onChange={(event) => onSearchChange(event.target.value)}
            placeholder="Buscar por nombre o email"
            className="ep-input h-11 rounded-2xl px-4"
          />
          {isSuperAdmin ? (
            <select
              value={notaryFilter}
              onChange={(event) => onNotaryFilterChange(event.target.value)}
              className="ep-select h-11 rounded-2xl px-4"
            >
              <option value="all">Todas las notarías</option>
              {notaries.map((notary) => (
                <option key={notary.id} value={notary.id}>
                  {notary.notary_label}
                </option>
              ))}
            </select>
          ) : null}
          <select value={roleFilter} onChange={(event) => onRoleFilterChange(event.target.value)} className="ep-select h-11 rounded-2xl px-4">
            <option value="all">Todos los roles</option>
            {roles.map((role) => (
              <option key={role.code} value={role.code}>
                {role.name}
              </option>
            ))}
          </select>
          <select
            value={statusFilter}
            onChange={(event) => onStatusFilterChange(event.target.value as "all" | "active" | "inactive")}
            className="ep-select h-11 rounded-2xl px-4"
          >
            <option value="all">Todos</option>
            <option value="active">Activo</option>
            <option value="inactive">Inactivo</option>
          </select>
          <button
            type="button"
            onClick={clearFilters}
            className="rounded-2xl border border-line bg-[var(--panel)] px-4 py-2 text-sm font-semibold text-primary"
          >
            Limpiar filtros
          </button>
        </div>

        <div className="mt-6 overflow-x-auto">
          <table className="min-w-full border-separate border-spacing-0">
            <thead>
              <tr>
                <th className="border-b border-line px-4 py-3 text-left text-xs uppercase tracking-[0.18em] text-secondary">Nombre</th>
                <th className="border-b border-line px-4 py-3 text-left text-xs uppercase tracking-[0.18em] text-secondary">Email</th>
                {isSuperAdmin ? (
                  <th className="border-b border-line px-4 py-3 text-left text-xs uppercase tracking-[0.18em] text-secondary">Notaría</th>
                ) : null}
                <th className="border-b border-line px-4 py-3 text-left text-xs uppercase tracking-[0.18em] text-secondary">Rol</th>
                <th className="border-b border-line px-4 py-3 text-left text-xs uppercase tracking-[0.18em] text-secondary">Estado</th>
                <th className="border-b border-line px-4 py-3 text-left text-xs uppercase tracking-[0.18em] text-secondary">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {isCreating ? (
                <Fragment>
                  <tr>
                    <td className="border-b border-line px-4 py-4 text-sm font-semibold text-primary">Nuevo usuario</td>
                    <td className="border-b border-line px-4 py-4 text-sm text-secondary">—</td>
                    {isSuperAdmin ? <td className="border-b border-line px-4 py-4 text-sm text-secondary">—</td> : null}
                    <td className="border-b border-line px-4 py-4 text-sm text-secondary">—</td>
                    <td className="border-b border-line px-4 py-4 text-sm text-secondary">Activo</td>
                    <td className="border-b border-line px-4 py-4">
                      <button
                        type="button"
                        onClick={() => setOpenUserId(null)}
                        className="rounded-xl border border-line px-3 py-2 text-xs font-semibold text-primary"
                      >
                        Cerrar
                      </button>
                    </td>
                  </tr>
                  <tr>
                    <td colSpan={isSuperAdmin ? 6 : 5} className="border-b border-line p-0">
                      <div className="overflow-hidden transition-all duration-300 ease-out">
                        {renderAccordion("new")}
                      </div>
                    </td>
                  </tr>
                </Fragment>
              ) : null}

              {paginatedUsers.map((user) => {
                const isExpanded = openUserId === user.id;
                const firstRole = user.assignments[0]?.role_name ?? user.roles[0] ?? "Sin rol";
                return (
                  <Fragment key={user.id}>
                    <tr>
                      <td className="border-b border-line px-4 py-4 text-sm font-semibold text-primary">{user.full_name}</td>
                      <td className="border-b border-line px-4 py-4 text-sm text-secondary">{user.email}</td>
                      {isSuperAdmin ? (
                        <td className="border-b border-line px-4 py-4 text-sm text-secondary">{user.default_notary_label ?? "Sin notaría"}</td>
                      ) : null}
                      <td className="border-b border-line px-4 py-4 text-sm text-secondary">
                        <span className="rounded-full bg-primary/10 px-3 py-1 text-xs font-semibold text-primary">{firstRole}</span>
                      </td>
                      <td className="border-b border-line px-4 py-4 text-sm">
                        <span className={`rounded-full px-3 py-1 text-xs font-semibold ${user.is_active ? "ep-kpi-success" : "ep-badge"}`}>
                          {user.is_active ? "Activo" : "Inactivo"}
                        </span>
                      </td>
                      <td className="border-b border-line px-4 py-4">
                        <button
                          type="button"
                          onClick={() => toggleUserAccordion(user)}
                          className="rounded-xl border border-line px-3 py-2 text-xs font-semibold text-primary hover:bg-[var(--panel-soft)]"
                        >
                          {isExpanded ? "Cerrar" : "Editar"}
                        </button>
                      </td>
                    </tr>
                    <tr>
                      <td colSpan={isSuperAdmin ? 6 : 5} className="border-b border-line p-0">
                        <div
                          className={`overflow-hidden transition-all duration-300 ease-out ${
                            isExpanded ? "max-h-[1400px] opacity-100" : "max-h-0 opacity-0"
                          }`}
                        >
                          {isExpanded ? renderAccordion(user.id) : null}
                        </div>
                      </td>
                    </tr>
                  </Fragment>
                );
              })}
            </tbody>
          </table>
        </div>

        <div className="mt-4 flex items-center justify-end gap-2">
          <button
            type="button"
            onClick={() => setPage((current) => Math.max(1, current - 1))}
            disabled={page <= 1}
            className="rounded-xl border border-line px-3 py-2 text-xs font-semibold text-primary disabled:cursor-not-allowed disabled:opacity-60"
          >
            Anterior
          </button>
          <div className="text-xs text-secondary">
            Página {Math.min(page, totalPages)} de {totalPages}
          </div>
          <button
            type="button"
            onClick={() => setPage((current) => Math.min(totalPages, current + 1))}
            disabled={page >= totalPages}
            className="rounded-xl border border-line px-3 py-2 text-xs font-semibold text-primary disabled:cursor-not-allowed disabled:opacity-60"
          >
            Siguiente
          </button>
        </div>
      </section>
    </div>
  );
}
