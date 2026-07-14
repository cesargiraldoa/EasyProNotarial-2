export const VALID_ROLE_CODES = [
  "super_admin",
  "admin_notary",
  "notary",
  "approver",
  "protocolist",
  "client",
] as const;

export type RoleCode = (typeof VALID_ROLE_CODES)[number];

export const ALL_ROLE_CODES: RoleCode[] = [...VALID_ROLE_CODES];

export const NOTARIAL_WORKSPACE_ROLES: RoleCode[] = [
  "super_admin",
  "admin_notary",
  "notary",
  "protocolist",
  "approver",
];

export const ROLE_PROTECTED_ROUTES: Record<string, RoleCode[]> = {
  "/dashboard/comercial": ["super_admin"],
  "/dashboard/notarias": ["super_admin"],
  "/dashboard/usuarios": ["super_admin", "admin_notary"],
  "/dashboard/roles": ["super_admin", "admin_notary"],
  "/dashboard/casos": NOTARIAL_WORKSPACE_ROLES,
  "/dashboard/minutas": NOTARIAL_WORKSPACE_ROLES,
  "/dashboard/actos-plantillas": NOTARIAL_WORKSPACE_ROLES,
  "/dashboard/inteligencia-documental": NOTARIAL_WORKSPACE_ROLES,
  "/dashboard/lotes": NOTARIAL_WORKSPACE_ROLES,
  "/dashboard/onlyoffice-editor": NOTARIAL_WORKSPACE_ROLES,
  "/dashboard/system-status": ["super_admin"],
  "/dashboard/configuracion": ["super_admin", "admin_notary"],
  "/dashboard/perfil": ALL_ROLE_CODES,
  "/dashboard/ayuda": ALL_ROLE_CODES,
};

type NavigationAccessItem = {
  roles: readonly string[];
};

export function normalizeUserRoles(roles: unknown): string[] {
  if (!Array.isArray(roles)) {
    return [];
  }

  return Array.from(
    new Set(
      roles
        .filter((role): role is string => typeof role === "string")
        .map((role) => role.trim().toLowerCase())
        .filter(Boolean),
    ),
  );
}

export function isRouteAllowedForRoles(pathname: string, roles: readonly string[]): boolean {
  const normalizedRoles = normalizeUserRoles([...roles]);
  const route = Object.keys(ROLE_PROTECTED_ROUTES)
    .filter((protectedRoute) => pathname === protectedRoute || pathname.startsWith(`${protectedRoute}/`))
    .sort((a, b) => b.length - a.length)[0];

  if (!route) {
    return true;
  }

  const allowedRoles = ROLE_PROTECTED_ROUTES[route];
  return normalizedRoles.some((role) => allowedRoles.includes(role as RoleCode));
}

export function isNavigationItemAllowed(item: NavigationAccessItem, roles: readonly string[]): boolean {
  const normalizedRoles = normalizeUserRoles([...roles]);
  return normalizedRoles.some((role) => item.roles.includes(role));
}
