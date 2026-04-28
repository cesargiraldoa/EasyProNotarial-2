This file is a merged representation of a subset of the codebase, containing files not matching ignore patterns, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of a subset of the repository's contents that is considered the most important context.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Files matching these patterns are excluded: node_modules, .git, .next, dist, build, .vercel, coverage, *.log, *.tmp, .env, .env.*
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
.gitignore
app/(app)/dashboard/actos-plantillas/page.tsx
app/(app)/dashboard/ayuda/page.tsx
app/(app)/dashboard/casos/[caseId]/page.tsx
app/(app)/dashboard/casos/crear/page.tsx
app/(app)/dashboard/casos/page.tsx
app/(app)/dashboard/comercial/[notaryId]/page.tsx
app/(app)/dashboard/comercial/page.tsx
app/(app)/dashboard/configuracion/page.tsx
app/(app)/dashboard/lotes/page.tsx
app/(app)/dashboard/notarias/[notaryId]/page.tsx
app/(app)/dashboard/notarias/page.tsx
app/(app)/dashboard/page.tsx
app/(app)/dashboard/perfil/page.tsx
app/(app)/dashboard/roles/page.tsx
app/(app)/dashboard/system-status/page.tsx
app/(app)/dashboard/usuarios/page.tsx
app/(app)/layout.tsx
app/(marketing)/login/page.tsx
app/(marketing)/page.tsx
app/globals.css
app/layout.tsx
components/app-shell/app-shell.tsx
components/app-shell/dashboard.tsx
components/app-shell/notaries-settings.tsx
components/cases/case-detail-workspace.tsx
components/cases/cases-workspace.tsx
components/cases/create-case-wizard.tsx
components/marketing/landing-page.tsx
components/marketing/login-panel.tsx
components/notaries/commercial-workspace.tsx
components/notaries/notaries-catalog.tsx
components/notaries/notary-crm-workspace.tsx
components/notaries/notary-detail-workspace.tsx
components/persons/legal-entity-lookup.tsx
components/persons/person-lookup.tsx
components/process/process-placeholder.tsx
components/roles/roles-workspace.tsx
components/system/system-status-workspace.tsx
components/templates/templates-workspace.tsx
components/ui/brand-provider.tsx
components/ui/hybrid-autocomplete.tsx
components/ui/live-clock.tsx
components/ui/logo-badge.tsx
components/ui/searchable-select.tsx
components/ui/theme-provider.tsx
components/ui/utils.ts
components/ui/validated-input.tsx
components/users/user-profile-workspace.tsx
components/users/users-admin-workspace.tsx
lib/api.ts
lib/auth.ts
lib/branding.ts
lib/datetime.ts
lib/document-flow.ts
lib/legal-entities.ts
lib/navigation.ts
lib/text.ts
middleware.ts
next-env.d.ts
next.config.mjs
package.json
postcss.config.js
public/login-cafetero.png
public/notario-hero.png
scripts/e2e_document_flow_check.py
tailwind.config.ts
tsconfig.json
tsconfig.tsbuildinfo
```

# Files

## File: .gitignore
```
.vercel
```

## File: app/(app)/dashboard/actos-plantillas/page.tsx
```typescript
import { TemplatesWorkspace } from "@/components/templates/templates-workspace";

export default function ActsTemplatesPage() {
  return <TemplatesWorkspace />;
}
```

## File: app/(app)/dashboard/ayuda/page.tsx
```typescript
import { ProcessPlaceholder } from "@/components/process/process-placeholder";

export default function HelpPage() {
  return <ProcessPlaceholder section="Ayuda" title="Centro de apoyo operativo del proceso" copy="La interfaz ya reserva un espacio dedicado para ayuda, guías por rol y soporte contextual sobre comercial, minutas, revisiones y cierre documental." />;
}
```

## File: app/(app)/dashboard/casos/[caseId]/page.tsx
```typescript
import { CaseDetailWorkspace } from "@/components/cases/case-detail-workspace";

export default async function CaseDetailPage({
  params,
  searchParams,
}: {
  params: Promise<{ caseId: string }>;
  searchParams?: Promise<{ tab?: string | string[] }>;
}) {
  const { caseId } = await params;
  const resolvedSearchParams = searchParams ? await searchParams : undefined;
  const parsedCaseId = Number(caseId);
  const initialTab = Array.isArray(resolvedSearchParams?.tab) ? resolvedSearchParams?.tab[0] : resolvedSearchParams?.tab;

  if (!Number.isFinite(parsedCaseId) || parsedCaseId <= 0) {
    return <div className="ep-card rounded-[2rem] p-6 text-secondary">El identificador de la minuta no es v?lido.</div>;
  }

  return <CaseDetailWorkspace caseId={parsedCaseId} initialTab={initialTab} />;
}
```

## File: app/(app)/dashboard/casos/crear/page.tsx
```typescript
import { CreateCaseWizard } from "@/components/cases/create-case-wizard";

export default function CreateCasePage() {
  return <CreateCaseWizard />;
}
```

## File: app/(app)/dashboard/casos/page.tsx
```typescript
import { CasesWorkspace } from "@/components/cases/cases-workspace";

export default function CasesPage() {
  return <CasesWorkspace />;
}
```

## File: app/(app)/dashboard/comercial/[notaryId]/page.tsx
```typescript
import { NotaryCrmWorkspace } from "@/components/notaries/notary-crm-workspace";

export default async function CommercialNotaryDetailPage({ params }: { params: Promise<{ notaryId: string }> }) {
  const { notaryId } = await params;
  return <NotaryCrmWorkspace notaryId={Number(notaryId)} />;
}
```

## File: app/(app)/dashboard/comercial/page.tsx
```typescript
import { CommercialWorkspace } from "@/components/notaries/commercial-workspace";

export default function CommercialPage() {
  return <CommercialWorkspace />;
}
```

## File: app/(app)/dashboard/configuracion/page.tsx
```typescript
import { ProcessPlaceholder } from "@/components/process/process-placeholder";

export default function SettingsPage() {
  return <ProcessPlaceholder section="Configuración" title="Parámetros de operación y gobierno del producto" copy="Este espacio queda listo para gobernar branding, flujos, catálogos y reglas de proceso con una vista administrativa coherente con EasyPro 2." />;
}
```

## File: app/(app)/dashboard/lotes/page.tsx
```typescript
import { ProcessPlaceholder } from "@/components/process/process-placeholder";

export default function LotsPage() {
  return <ProcessPlaceholder section="Lotes" title="Operación masiva sobre el flujo documental" copy="La navegación y el shell quedaron alineados para que el siguiente paquete conecte lotes con creación masiva de minutas, control de errores y generación documental." />;
}
```

## File: app/(app)/dashboard/notarias/[notaryId]/page.tsx
```typescript
import { NotaryDetailWorkspace } from "@/components/notaries/notary-detail-workspace";

export default async function NotaryDetailPage({ params }: { params: Promise<{ notaryId: string }> }) {
  const { notaryId } = await params;
  return <NotaryDetailWorkspace notaryId={Number(notaryId)} />;
}
```

## File: app/(app)/dashboard/notarias/page.tsx
```typescript
import { NotariesCatalog } from "@/components/notaries/notaries-catalog";

export default function NotariesPage() {
  return <NotariesCatalog />;
}
```

## File: app/(app)/dashboard/page.tsx
```typescript
import { DashboardOverview } from "@/components/app-shell/dashboard";

export default function DashboardPage() {
  return <DashboardOverview />;
}
```

## File: app/(app)/dashboard/perfil/page.tsx
```typescript
import { UserProfileWorkspace } from "@/components/users/user-profile-workspace";

export default function ProfilePage() {
  return <UserProfileWorkspace />;
}
```

## File: app/(app)/dashboard/roles/page.tsx
```typescript
import { RolesWorkspace } from "@/components/roles/roles-workspace";

export default function RolesPage() {
  return <RolesWorkspace />;
}
```

## File: app/(app)/dashboard/system-status/page.tsx
```typescript
import { SystemStatusWorkspace } from "@/components/system/system-status-workspace";

export default function SystemStatusPage() {
  return <SystemStatusWorkspace />;
}
```

## File: app/(app)/dashboard/usuarios/page.tsx
```typescript
import { UsersAdminWorkspace } from "@/components/users/users-admin-workspace";

export default function UsersPage() {
  return <UsersAdminWorkspace />;
}
```

## File: app/(app)/layout.tsx
```typescript
import { AppShell } from "@/components/app-shell/app-shell";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return <AppShell>{children}</AppShell>;
}
```

## File: app/(marketing)/login/page.tsx
```typescript
import { LoginPanel } from "@/components/marketing/login-panel";

export default function LoginPage() {
  return <LoginPanel />;
}
```

## File: app/(marketing)/page.tsx
```typescript
import { LandingPage } from "@/components/marketing/landing-page";

export default function HomePage() {
  return <LandingPage />;
}
```

## File: app/globals.css
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --ink: 20 32 56;
  --text-muted: 82 96 130;
  --text-soft: 112 126 158;
  --surface: 245 248 252;
  --surface-alt: 236 242 249;
  --shell: 250 252 255;
  --panel: 255 255 255;
  --panel-strong: 247 250 253;
  --panel-soft: 241 246 251;
  --panel-highlight: 232 240 250;
  --overlay: 255 255 255 / 0.78;
  --primary: 13 46 93;
  --secondary: 82 96 130;
  --accent: 80 214 144;
  --line: 223 231 242;
  --line-strong: 206 217 232;
  --input: 255 255 255;
  --input-border: 214 224 238;
  --input-focus: 13 46 93;
  --success-bg: 235 250 241;
  --warning-bg: 255 246 221;
  --critical-bg: 255 236 240;
  --shadow-panel: 0 18px 45px rgba(11, 30, 58, 0.08);
  --shadow-soft: 0 10px 30px rgba(18, 38, 63, 0.08);
}

[data-theme="dark"] {
  --ink: 234 240 252;
  --text-muted: 171 184 212;
  --text-soft: 130 147 182;
  --surface: 8 14 24;
  --surface-alt: 12 20 34;
  --shell: 16 24 40;
  --panel: 19 29 47;
  --panel-strong: 24 36 58;
  --panel-soft: 28 42 68;
  --panel-highlight: 20 44 84;
  --overlay: 16 24 40 / 0.86;
  --primary: 139 180 255;
  --secondary: 171 184 212;
  --accent: 100 218 155;
  --line: 49 66 99;
  --line-strong: 63 83 121;
  --input: 23 35 57;
  --input-border: 66 86 122;
  --input-focus: 139 180 255;
  --success-bg: 20 63 45;
  --warning-bg: 74 56 17;
  --critical-bg: 78 30 42;
  --shadow-panel: 0 24px 60px rgba(2, 7, 18, 0.48);
  --shadow-soft: 0 16px 38px rgba(2, 7, 18, 0.36);
}

* {
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
}

body {
  margin: 0;
  min-height: 100vh;
  background: radial-gradient(circle at top, rgba(var(--panel-highlight), 0.18) 0%, transparent 26%), linear-gradient(180deg, rgb(var(--surface)) 0%, rgb(var(--surface-alt)) 100%);
  color: rgb(var(--ink));
  font-family: Aptos, "Segoe UI", "Helvetica Neue", sans-serif;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  transition: background-color 180ms ease, color 180ms ease;
}

a {
  color: inherit;
  text-decoration: none;
}

button,
input,
textarea,
select {
  font: inherit;
}

button,
input,
textarea,
select,
a,
svg,
article,
section,
div {
  transition: background-color 180ms ease, border-color 180ms ease, color 180ms ease, box-shadow 180ms ease, transform 180ms ease;
}

p,
h1,
h2,
h3,
h4,
span,
label,
button,
a {
  word-break: normal;
  overflow-wrap: break-word;
}

::selection {
  background: rgba(80, 214, 144, 0.28);
}

@layer components {
  .ep-shell {
    background: linear-gradient(180deg, rgba(var(--shell), 0.92) 0%, rgba(var(--surface), 0.9) 100%);
    border-color: rgba(var(--line), 0.9);
  }

  .ep-card {
    background: rgb(var(--panel));
    border: 1px solid rgba(var(--line), 0.88);
    box-shadow: var(--shadow-panel);
  }

  .ep-card-soft {
    background: rgb(var(--panel-strong));
    border: 1px solid rgba(var(--line), 0.78);
    box-shadow: var(--shadow-soft);
  }

  .ep-card-muted {
    background: rgb(var(--panel-soft));
    border: 1px solid rgba(var(--line), 0.76);
  }

  .ep-filter-panel {
    background: linear-gradient(180deg, rgba(var(--panel-strong), 0.96) 0%, rgba(var(--panel-soft), 0.98) 100%);
    border: 1px solid rgba(var(--line-strong), 0.8);
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06);
  }

  .ep-topbar,
  .ep-sidebar {
    background: rgba(var(--shell), 0.82);
    border-color: rgba(var(--line), 0.82);
    backdrop-filter: blur(18px);
  }

  .ep-dropdown {
    background: rgb(var(--panel));
    border: 1px solid rgba(var(--line-strong), 0.92);
    box-shadow: 0 22px 60px rgba(11, 30, 58, 0.18);
    backdrop-filter: none;
  }

  .ep-shell-divider-y {
    border-right: 1px solid rgba(var(--line), 0.38);
    box-shadow: inset -1px 0 0 rgba(255, 255, 255, 0.03);
  }

  .ep-shell-divider-x {
    border-bottom: 1px solid rgba(var(--line), 0.34);
    box-shadow: inset 0 -1px 0 rgba(255, 255, 255, 0.025);
  }

  .ep-input,
  .ep-select,
  .ep-textarea {
    background: rgb(var(--input));
    border: 1px solid rgb(var(--input-border));
    color: rgb(var(--ink));
  }

  .ep-input::placeholder,
  .ep-textarea::placeholder {
    color: rgb(var(--text-soft));
  }

  .ep-input:focus,
  .ep-select:focus,
  .ep-textarea:focus {
    border-color: rgba(var(--input-focus), 0.82);
    box-shadow: 0 0 0 3px rgba(var(--input-focus), 0.16);
    outline: none;
  }

  .ep-pill {
    background: rgb(var(--panel-strong));
    border: 1px solid rgba(var(--line), 0.82);
    color: rgb(var(--ink));
  }

  .ep-badge {
    background: rgb(var(--panel));
    border: 1px solid rgba(var(--line), 0.88);
    color: rgb(var(--ink));
    box-shadow: var(--shadow-soft);
  }

  .ep-kpi-critical {
    background: rgb(var(--critical-bg));
    border: 1px solid rgba(214, 75, 103, 0.26);
  }

  .ep-kpi-warning {
    background: rgb(var(--warning-bg));
    border: 1px solid rgba(201, 146, 30, 0.28);
  }

  .ep-kpi-success {
    background: rgb(var(--success-bg));
    border: 1px solid rgba(43, 152, 96, 0.24);
  }

  .ep-nav-item {
    color: rgb(var(--text-muted));
  }

  .ep-nav-item:hover,
  .ep-nav-item:focus-visible,
  .ep-nav-item-active {
    background: rgb(var(--panel-soft));
    color: rgb(var(--ink));
    box-shadow: var(--shadow-soft);
    outline: none;
  }

  .ep-login-shell {
    background: radial-gradient(circle at top left, rgba(var(--panel-highlight), 0.28) 0%, transparent 26%), linear-gradient(135deg, rgb(var(--surface)) 0%, rgb(var(--surface-alt)) 52%, rgba(var(--accent), 0.08) 100%);
  }
}

.text-primary,
.text-ink {
  color: rgb(var(--ink));
}

.text-secondary {
  color: rgb(var(--text-muted));
}

.border-line {
  border-color: rgb(var(--line));
}

.bg-white,
.bg-white\/90,
.bg-white\/85,
.bg-white\/80,
.bg-white\/75 {
  background-color: rgb(var(--panel));
}

.bg-slate-50 {
  background-color: rgb(var(--panel-soft));
}

.bg-slate-100 {
  background-color: rgb(var(--panel-highlight));
}

.shadow-panel {
  box-shadow: var(--shadow-panel);
}

.shadow-soft {
  box-shadow: var(--shadow-soft);
}

[data-theme="dark"] .text-white\/72,
[data-theme="dark"] .text-white\/80,
[data-theme="dark"] .text-white\/82,
[data-theme="dark"] .text-white\/70,
[data-theme="dark"] .text-white\/75 {
  color: rgba(234, 240, 252, 0.82) !important;
}

[data-theme="dark"] option {
  background: rgb(var(--input));
  color: rgb(var(--ink));
}
```

## File: app/layout.tsx
```typescript
import type { Metadata } from "next";
import "@/app/globals.css";
import { BrandProvider } from "@/components/ui/brand-provider";
import { ThemeProvider } from "@/components/ui/theme-provider";

export const metadata: Metadata = {
  title: "EasyPro 2",
  description: "Base multinotaría para operación notarial premium.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="es" suppressHydrationWarning>
      <body>
        <ThemeProvider>
          <BrandProvider>{children}</BrandProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
```

## File: components/app-shell/app-shell.tsx
```typescript
"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { Bell, ChevronDown, ChevronLeft, ChevronRight, HelpCircle, LogOut, Menu, MoonStar, Search, SunMedium, UserRound } from "lucide-react";
import { appNavigation } from "@/lib/navigation";
import { defaultBranding } from "@/lib/branding";
import { getCurrentUser, logout, type CurrentUser } from "@/lib/api";
import { LogoBadge } from "@/components/ui/logo-badge";
import { useTheme } from "@/components/ui/theme-provider";
import { cn } from "@/components/ui/utils";

type AppShellProps = {
  children: React.ReactNode;
};

function buildUserInitials(name?: string | null) {
  if (!name) return "EP";
  return (
    name
      .split(" ")
      .filter(Boolean)
      .slice(0, 2)
      .map((item) => item[0]?.toUpperCase())
      .join("") || "EP"
  );
}

export function AppShell({ children }: AppShellProps) {
  const pathname = usePathname();
  const router = useRouter();
  const { theme, toggleTheme } = useTheme();
  const [menuOpen, setMenuOpen] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null);
  const menuRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const storedSidebarState = window.localStorage.getItem("sidebar_collapsed");
    if (storedSidebarState !== null) {
      setIsSidebarCollapsed(storedSidebarState === "true");
    }
  }, []);

  useEffect(() => {
    window.localStorage.setItem("sidebar_collapsed", String(isSidebarCollapsed));
  }, [isSidebarCollapsed]);

  useEffect(() => {
    let cancelled = false;
    getCurrentUser()
      .then((user) => {
        if (!cancelled) {
          setCurrentUser(user);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setCurrentUser(null);
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    setMenuOpen(false);
  }, [pathname]);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setMenuOpen(false);
      }
    }

    function handleEscape(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setMenuOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("keydown", handleEscape);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleEscape);
    };
  }, []);

  function onLogout() {
    logout();
    setMenuOpen(false);
    router.push("/login");
    router.refresh();
  }

  const userName = currentUser?.full_name ?? "Operación EasyPro";
  const userSubtitle = currentUser?.roles?.[0] ?? "Sesión activa";
  const normalizedRoles = (currentUser?.role_codes ?? []).map((role) => role.toLowerCase());
  const recognizedRoles = new Set(["super_admin", "admin_notary", "notary", "approver", "protocolist", "client"]);
  const hasRecognizedRole = normalizedRoles.some((role) => recognizedRoles.has(role));

  const navVisibilityByLabel: Record<string, string[]> = {
    Resumen: ["super_admin", "admin_notary", "notary", "approver", "protocolist", "client"],
    Comercial: ["super_admin"],
    Notarías: ["super_admin"],
    Usuarios: ["super_admin", "admin_notary", "notary"],
    Roles: ["super_admin", "admin_notary"],
    Minutas: ["super_admin", "admin_notary", "notary", "approver", "protocolist", "client"],
    Casos: ["super_admin", "admin_notary", "notary", "approver", "protocolist", "client"],
    "Crear Minuta": ["super_admin", "admin_notary", "notary", "approver", "protocolist"],
    "Crear Caso": ["super_admin", "admin_notary", "notary", "approver", "protocolist"],
    "Actos / Plantillas": ["super_admin", "admin_notary", "notary", "approver", "protocolist"],
    Lotes: ["super_admin", "admin_notary", "notary", "approver", "protocolist"],
    "System Status": ["super_admin"],
    Configuración: ["super_admin", "admin_notary"],
    "Mi Perfil": ["super_admin", "admin_notary", "notary", "approver", "protocolist", "client"],
  };
  const navModuleCodesByLabel: Record<string, string[]> = {
    Resumen: ["resumen"],
    Comercial: ["comercial"],
    Notarías: ["notarias"],
    Usuarios: ["usuarios"],
    Roles: ["roles"],
    Minutas: ["minutas"],
    Casos: ["minutas"],
    "Crear Minuta": ["crear_minuta"],
    "Crear Caso": ["crear_minuta"],
    "Actos / Plantillas": ["actos_plantillas"],
    Lotes: ["lotes"],
    "System Status": ["system_status"],
    Configuración: ["configuracion"],
    "Mi Perfil": [],
  };
  const hasPermissions = Boolean(currentUser?.permissions?.length);
  const allowedModuleCodes = new Set(
    (currentUser?.permissions ?? [])
      .filter((permission) => permission.can_access)
      .map((permission) => permission.module_code.toLowerCase()),
  );

  const visibleNavigation = appNavigation.filter(({ label }) => {
    if (label === "Ayuda") {
      return false;
    }

    if (hasPermissions) {
      if (label === "Mi Perfil") {
        return true;
      }

      const allowedModuleCodesForLabel = navModuleCodesByLabel[label];
      if (!allowedModuleCodesForLabel) {
        return false;
      }

      return allowedModuleCodesForLabel.some((moduleCode) => allowedModuleCodes.has(moduleCode));
    }

    if (!hasRecognizedRole) {
      return label === "Resumen" || label === "Minutas" || label === "Casos";
    }

    const allowedRoles = navVisibilityByLabel[label];
    if (!allowedRoles) {
      return false;
    }

    return normalizedRoles.some((role) => allowedRoles.includes(role));
  });

  return (
    <div className="min-h-screen text-ink">
      <div className="mx-auto flex min-h-screen max-w-[1680px] flex-col lg:flex-row">
        <aside
          className={cn(
            "ep-sidebar ep-shell-divider-y hidden min-h-screen shrink-0 flex-col overflow-y-auto py-6 transition-all duration-300 ease-in-out lg:flex",
            isSidebarCollapsed ? "w-16 px-2" : "w-[292px] px-6",
          )}
        >
          <div className={cn("flex gap-4", isSidebarCollapsed ? "flex-col items-center" : "items-start justify-between")}>
            <div className={cn("flex items-center gap-4", isSidebarCollapsed && "justify-center")}>
              <LogoBadge initials={defaultBranding.logoInitials} compact />
              <div className={cn("min-w-0", isSidebarCollapsed && "hidden")}>
                <p className="text-sm font-semibold uppercase tracking-[0.24em] text-primary/80">EasyPro 2</p>
                <p className="mt-1 text-xs text-secondary">{defaultBranding.officeLabel}</p>
              </div>
            </div>
            <button
              type="button"
              onClick={() => setIsSidebarCollapsed((current) => !current)}
              aria-label={isSidebarCollapsed ? "Expandir menú lateral" : "Colapsar menú lateral"}
              title={isSidebarCollapsed ? "Expandir menú lateral" : "Colapsar menú lateral"}
              className="ep-nav-item inline-flex h-8 w-8 items-center justify-center rounded-xl transition"
            >
              {isSidebarCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
            </button>
          </div>

          <nav className="mt-10 space-y-2">
            {visibleNavigation.map(({ label, href, icon: Icon }) => {
              const isActive = pathname === href || pathname.startsWith(`${href}/`);
              const navLabel = label === "Casos" ? "Minutas" : label === "Crear Caso" ? "Crear Minuta" : label;
              return (
                <Link
                  key={label}
                  href={href}
                  title={isSidebarCollapsed ? navLabel : undefined}
                  className={cn(
                    "ep-nav-item flex min-h-12 items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium leading-5 transition",
                    isSidebarCollapsed && "justify-center gap-0 px-0",
                    isActive && "ep-nav-item-active",
                  )}
                >
                  <Icon className="h-4 w-4 shrink-0" />
                  {!isSidebarCollapsed ? <span className="min-w-0">{navLabel}</span> : null}
                </Link>
              );
            })}
          </nav>

          <div className="mt-auto space-y-2 pt-8">
            <Link
              href="/dashboard/ayuda"
              title={isSidebarCollapsed ? "Ayuda" : undefined}
              className={cn(
                "ep-nav-item flex min-h-12 w-full items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition",
                isSidebarCollapsed && "justify-center gap-0 px-0",
              )}
            >
              <HelpCircle className="h-4 w-4 shrink-0" />
              {!isSidebarCollapsed ? <span>Ayuda</span> : null}
            </Link>
            <button
              onClick={onLogout}
              title={isSidebarCollapsed ? "Cerrar sesión" : undefined}
              className={cn(
                "ep-nav-item flex min-h-12 w-full items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition",
                isSidebarCollapsed && "justify-center gap-0 px-0",
              )}
            >
              <LogOut className="h-4 w-4 shrink-0" />
              {!isSidebarCollapsed ? <span>Cerrar sesión</span> : null}
            </button>
          </div>
        </aside>

        <div className="flex min-h-screen flex-1 flex-col transition-all duration-300 ease-in-out">
          <header className="ep-topbar ep-shell-divider-x relative z-20 flex overflow-visible items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-10">
            <div className="flex min-w-0 items-center gap-3 lg:gap-5">
              <button className="ep-card-soft inline-flex h-11 w-11 items-center justify-center rounded-2xl lg:hidden">
                <Menu className="h-5 w-5" />
              </button>
              <div className="ep-card-soft hidden h-12 min-w-[320px] items-center gap-3 rounded-2xl px-4 lg:flex xl:min-w-[420px]">
                <Search className="h-4 w-4 shrink-0 text-secondary" />
                <span className="truncate text-sm text-secondary">Buscar minutas, actos, plantillas, notarías o usuarios...</span>
              </div>
            </div>

            <div className="relative z-30 flex shrink-0 items-center gap-3" ref={menuRef}>
              <button
                type="button"
                onClick={toggleTheme}
                aria-label="Cambiar tema"
                title="Cambiar tema"
                className="ep-card-soft inline-flex h-11 w-11 items-center justify-center rounded-2xl hover:border-primary/30"
              >
                {theme === "dark" ? <SunMedium className="h-4 w-4" /> : <MoonStar className="h-4 w-4" />}
              </button>

              <button type="button" className="ep-card-soft inline-flex h-11 w-11 items-center justify-center rounded-2xl" aria-label="Notificaciones" title="Notificaciones">
                <Bell className="h-4 w-4" />
              </button>

              <div className="relative">
                <button
                  type="button"
                  onClick={() => setMenuOpen((current) => !current)}
                  aria-expanded={menuOpen}
                  aria-haspopup="menu"
                  className="ep-card flex items-center gap-3 rounded-2xl px-3 py-2.5 hover:border-primary/30"
                >
                  <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-primary text-sm font-semibold text-white shadow-soft">
                    {buildUserInitials(currentUser?.full_name)}
                  </div>
                  <div className="hidden text-left md:block">
                    <p className="max-w-[180px] truncate text-sm font-semibold text-primary">{userName}</p>
                    <p className="max-w-[180px] truncate text-xs text-secondary">{userSubtitle}</p>
                  </div>
                  <ChevronDown className={`h-4 w-4 text-secondary transition-transform ${menuOpen ? "rotate-180" : ""}`} />
                </button>

                {menuOpen ? (
                  <div className="ep-dropdown absolute right-0 top-[calc(100%+14px)] z-50 w-[300px] rounded-[1.5rem] p-2 shadow-panel">
                    <div className="ep-card-muted rounded-[1.15rem] px-4 py-3">
                      <p className="text-sm font-semibold text-primary">{userName}</p>
                      <p className="mt-1 text-xs text-secondary">{currentUser?.email ?? "Sesión activa"}</p>
                    </div>
                    <div className="mt-2 space-y-1">
                      <Link href="/dashboard/perfil" onClick={() => setMenuOpen(false)} className="ep-nav-item flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition hover:bg-[var(--panel-soft)]">
                        <UserRound className="h-4 w-4" />
                        <span>Ver perfil</span>
                      </Link>
                      <button type="button" onClick={onLogout} className="ep-nav-item flex w-full items-center gap-3 rounded-2xl px-4 py-3 text-left text-sm font-medium transition hover:bg-[var(--panel-soft)]">
                        <LogOut className="h-4 w-4" />
                        <span>Cerrar sesión</span>
                      </button>
                    </div>
                  </div>
                ) : null}
              </div>
            </div>
          </header>

          <main className="flex-1 px-4 py-6 sm:px-6 lg:px-10 lg:py-8">{children}</main>
        </div>
      </div>
    </div>
  );
}
```

## File: components/app-shell/dashboard.tsx
```typescript
"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { BarChart3, Filter, LineChart, RefreshCw, ShieldAlert } from "lucide-react";
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";
import {
  getCurrentUser,
  getExecutiveDashboard,
  type DashboardChartDatum,
  type DashboardKpi,
  type DashboardTrendDatum,
  type ExecutiveDashboard,
  type ExecutiveDashboardFilters,
} from "@/lib/api";
import { LiveClock } from "@/components/ui/live-clock";
import { formatDateTime } from "@/lib/datetime";

const COLORS = ["#1e3a5f", "#2563eb", "#3b82f6", "#60a5fa", "#93c5fd", "#bfdbfe"];

function toneClasses(tone: string) {
  if (tone === "critical") return "ep-kpi-critical";
  if (tone === "warning") return "ep-kpi-warning";
  if (tone === "success") return "ep-kpi-success";
  return "ep-card";
}

function formatNumber(value: number) {
  return new Intl.NumberFormat("es-CO").format(value);
}

function findKpi(dashboard: ExecutiveDashboard, key: string) {
  return dashboard.kpis.find((item) => item.key === key)?.value ?? 0;
}

function ChartCard({ title, subtitle, data }: { title: string; subtitle: string; data: DashboardChartDatum[] }) {
  const maxValue = Math.max(...data.map((item) => item.value), 1);

  return (
    <article className="ep-card min-w-0 rounded-[1.9rem] p-6">
      <div className="flex min-w-0 items-start gap-3">
        <div className="rounded-2xl bg-primary/10 p-3">
          <BarChart3 className="h-5 w-5 text-primary" />
        </div>
        <div className="min-w-0">
          <p className="text-sm font-semibold text-primary">{title}</p>
          <p className="mt-1 text-sm leading-6 text-secondary">{subtitle}</p>
        </div>
      </div>
      <div className="mt-6 space-y-4">
        {data.length === 0 ? <div className="ep-card-muted rounded-2xl px-4 py-4 text-sm text-secondary">Sin datos para el filtro actual.</div> : null}
        {data.map((item) => (
          <div key={item.label} className="space-y-2.5">
            <div className="flex items-center justify-between gap-3 text-sm">
              <p className={`truncate font-medium ${item.highlight ? "text-primary" : "text-secondary"}`}>{item.label}</p>
              <span className="shrink-0 font-semibold text-primary">{formatNumber(item.value)}</span>
            </div>
            <div className="h-2.5 rounded-full bg-[var(--panel-soft)]">
              <div className={`h-2.5 rounded-full ${item.highlight ? "bg-primary" : "bg-[color:rgb(var(--secondary)/0.35)]"}`} style={{ width: `${Math.max((item.value / maxValue) * 100, 8)}%` }} />
            </div>
          </div>
        ))}
      </div>
    </article>
  );
}

function TrendCard({ data }: { data: DashboardTrendDatum[] }) {
  const maxValue = Math.max(...data.map((item) => item.value), 1);

  return (
    <article className="ep-card min-w-0 rounded-[1.9rem] p-6">
      <div className="flex min-w-0 items-start gap-3">
        <div className="rounded-2xl bg-primary/10 p-3">
          <LineChart className="h-5 w-5 text-primary" />
        </div>
        <div className="min-w-0">
          <p className="text-sm font-semibold text-primary">Tendencia temporal</p>
          <p className="mt-1 text-sm leading-6 text-secondary">Ritmo de actividad por fecha de actualización, útil para lectura de desktop y laptop.</p>
        </div>
      </div>
      <div className="mt-6 flex min-h-[240px] items-end gap-3 overflow-x-auto pb-2">
        {data.length === 0 ? <div className="ep-card-muted rounded-2xl px-4 py-4 text-sm text-secondary">Sin datos para la ventana seleccionada.</div> : null}
        {data.map((item) => (
          <div key={item.label} className="flex min-w-[78px] flex-col items-center gap-3">
            <div className="text-sm font-semibold text-primary">{item.value}</div>
            <div className="flex h-40 w-full items-end rounded-t-[1rem] bg-[var(--panel-soft)] px-2 pb-0">
              <div className="w-full rounded-t-[1rem] bg-primary" style={{ height: `${Math.max((item.value / maxValue) * 100, 10)}%` }} />
            </div>
            <div className="text-center text-xs font-medium text-secondary">{item.label}</div>
          </div>
        ))}
      </div>
    </article>
  );
}

function PieActCard({ data }: { data: DashboardChartDatum[] }) {
  return (
    <article className="ep-card rounded-[2rem] p-6">
      <p className="mb-4 text-sm font-semibold uppercase tracking-widest text-accent">Tipos de acto</p>
      <ResponsiveContainer width="100%" height={260}>
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            nameKey="label"
            cx="50%"
            cy="50%"
            outerRadius={90}
            label={({ name, percent }) => `${name} ${(((percent ?? 0) * 100)).toFixed(0)}%`}
          >
            {data.map((_, index) => (
              <Cell key={index} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </article>
  );
}

export function DashboardOverview() {
  const [filters, setFilters] = useState<ExecutiveDashboardFilters>({});
  const [draftFilters, setDraftFilters] = useState<ExecutiveDashboardFilters>({});
  const [dashboard, setDashboard] = useState<ExecutiveDashboard | null>(null);
  const [isSuperAdmin, setIsSuperAdmin] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void Promise.all([loadDashboard(filters), loadCurrentUser()]);
  }, [filters]);

  async function loadCurrentUser() {
    try {
      const user = await getCurrentUser();
      setIsSuperAdmin(user?.roles?.includes("super_admin") ?? false);
    } catch {
      setIsSuperAdmin(false);
    }
  }

  async function loadDashboard(nextFilters: ExecutiveDashboardFilters) {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getExecutiveDashboard(nextFilters);
      setDashboard(data);
      setDraftFilters({
        date_from: data.filters.date_from ?? "",
        date_to: data.filters.date_to ?? "",
        notary_id: data.filters.notary_id?.toString() ?? "",
        state: data.filters.state ?? "",
        act_type: data.filters.act_type ?? "",
        owner_user_id: data.filters.owner_user_id?.toString() ?? "",
      });
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "No fue posible cargar el dashboard ejecutivo.");
    } finally {
      setIsLoading(false);
    }
  }

  function updateDraft<K extends keyof ExecutiveDashboardFilters>(field: K, value: ExecutiveDashboardFilters[K]) {
    setDraftFilters((current) => ({ ...current, [field]: value }));
  }

  function applyFilters(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFilters({
      date_from: draftFilters.date_from?.trim() || undefined,
      date_to: draftFilters.date_to?.trim() || undefined,
      notary_id: draftFilters.notary_id?.trim() || undefined,
      state: draftFilters.state?.trim() || undefined,
      act_type: draftFilters.act_type?.trim() || undefined,
      owner_user_id: draftFilters.owner_user_id?.trim() || undefined,
    });
  }

  function resetFilters() {
    setDraftFilters({});
    setFilters({});
  }

  const leadKpis = useMemo(() => dashboard?.kpis.slice(0, 5) ?? [], [dashboard]);
  const docsByType = useMemo(() => dashboard?.documents_by_act_type ?? [], [dashboard]);
  const docsByState = useMemo(() => dashboard?.documents_by_state ?? [], [dashboard]);
  const pilot = dashboard?.pilot_reference;

  if (isLoading && !dashboard) {
    return <div className="ep-card rounded-[2rem] p-6 text-secondary">Cargando resumen ejecutivo...</div>;
  }

  if (error && !dashboard) {
    return <div className="ep-kpi-critical rounded-[2rem] px-6 py-5 text-sm">{error}</div>;
  }

  if (!dashboard) {
    return <div className="ep-card rounded-[2rem] p-6 text-secondary">No hay datos disponibles.</div>;
  }

  return (
    <div className="space-y-8 xl:space-y-9">
      <section className="ep-card rounded-[2rem] p-6 sm:p-7">
        <div className="flex flex-col gap-6 xl:flex-row xl:items-start xl:justify-between">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 rounded-full border border-primary/10 bg-primary/8 px-3 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-primary">
              <ShieldAlert className="h-3.5 w-3.5" />
              Resumen ejecutivo
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 xl:w-[520px]">
            <div className="ep-card-muted rounded-[1.5rem] p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-secondary">Hora actual</p>
              <p className="mt-2 text-base font-semibold text-primary"><LiveClock /></p>
            </div>
            <div className="ep-card-muted rounded-[1.5rem] p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-secondary">ÚLTIMA ACTUALIZACIÓN</p>
              <p className="mt-2 text-base font-semibold text-primary">{formatDateTime(dashboard.generated_at)}</p>
            </div>
            <div className="rounded-[1.5rem] bg-primary p-4 text-white shadow-panel sm:col-span-2">
              <p className="text-xs uppercase tracking-[0.18em] text-white/70">NOTARÍA PILOTO</p>
              <p className="mt-2 text-base font-semibold">{pilot ? `${pilot.municipality}, ${pilot.department}` : "Sin referencia"}</p>
            </div>
          </div>
        </div>

        <form onSubmit={applyFilters} className="ep-filter-panel mt-7 rounded-[1.8rem] p-4 sm:p-5">
          <div className="flex items-center gap-3">
            <Filter className="h-4 w-4 text-primary" />
            <p className="text-sm font-semibold text-primary">Filtros ejecutivos</p>
          </div>
          <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-12">
            <label className="grid gap-2 text-sm font-medium text-primary xl:col-span-2">Fecha desde<input type="date" value={draftFilters.date_from ?? ""} onChange={(event) => updateDraft("date_from", event.target.value)} className="ep-input h-12 rounded-2xl px-4" /></label>
            <label className="grid gap-2 text-sm font-medium text-primary xl:col-span-2">Fecha hasta<input type="date" value={draftFilters.date_to ?? ""} onChange={(event) => updateDraft("date_to", event.target.value)} className="ep-input h-12 rounded-2xl px-4" /></label>
            {isSuperAdmin ? (
              <div className="grid gap-2 text-sm font-medium text-primary xl:col-span-2">
                <label>Notaría</label>
                <select value={draftFilters.notary_id ?? ""} onChange={(event) => updateDraft("notary_id", event.target.value)} className="ep-select h-12 rounded-2xl px-4">{dashboard.filter_options.notaries.map((option) => <option key={`${option.id ?? "all"}-${option.label}`} value={option.id?.toString() ?? ""}>{option.label}</option>)}</select>
              </div>
            ) : null}
            <label className="grid gap-2 text-sm font-medium text-primary xl:col-span-2">Estado<select value={draftFilters.state ?? ""} onChange={(event) => updateDraft("state", event.target.value)} className="ep-select h-12 rounded-2xl px-4">{dashboard.filter_options.states.map((option) => <option key={option.label} value={option.label === "Todos los estados" ? "" : option.label}>{option.label}</option>)}</select></label>
            <label className="grid gap-2 text-sm font-medium text-primary xl:col-span-2">Tipo de acto<select value={draftFilters.act_type ?? ""} onChange={(event) => updateDraft("act_type", event.target.value)} className="ep-select h-12 rounded-2xl px-4">{dashboard.filter_options.act_types.map((option) => <option key={option.label} value={option.label === "Todos los actos" ? "" : option.label}>{option.label}</option>)}</select></label>
            <label className="grid gap-2 text-sm font-medium text-primary xl:col-span-2">Responsable<select value={draftFilters.owner_user_id ?? ""} onChange={(event) => updateDraft("owner_user_id", event.target.value)} className="ep-select h-12 rounded-2xl px-4">{dashboard.filter_options.owners.map((option) => <option key={`${option.id ?? "all"}-${option.label}`} value={option.id?.toString() ?? ""}>{option.label}</option>)}</select></label>
          </div>
          <div className="mt-5 flex flex-wrap gap-3">
            <button type="submit" disabled={isLoading} className="inline-flex items-center gap-2 rounded-full bg-primary px-5 py-3 text-sm font-semibold text-white shadow-panel disabled:opacity-70">
              <RefreshCw className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
              Aplicar filtros
            </button>
            <button type="button" onClick={resetFilters} className="ep-card-soft inline-flex items-center gap-2 rounded-full px-5 py-3 text-sm font-semibold text-primary">
              Limpiar
            </button>
          </div>
        </form>
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-12">
        {leadKpis.map((item: DashboardKpi, index) => {
          const span = index < 2 ? "xl:col-span-3" : "xl:col-span-2";
          return (
            <article key={item.key} className={`${toneClasses(item.tone)} ${span} rounded-[1.7rem] p-5 shadow-soft`}>
              <p className="text-xs uppercase tracking-[0.18em] text-secondary">{item.label}</p>
              <p className="mt-3 text-3xl font-semibold tracking-[-0.05em] text-primary">{formatNumber(item.value)}</p>
              <p className="mt-3 text-sm leading-6 text-secondary">{item.detail}</p>
            </article>
          );
        })}
      </section>

      <section className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
        <div className="min-w-0">
          <ChartCard title="Documentos por estado" subtitle="Dónde está detenido o avanzando el flujo documental." data={docsByState} />
        </div>
        <div className="min-w-0">
          <TrendCard data={dashboard.temporal_trend} />
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[minmax(0,1.15fr)_minmax(340px,0.85fr)]">
        <div className="min-w-0">
          <ChartCard title="Ranking de responsables" subtitle="Usuarios con mayor carga visible para balancear trabajo." data={dashboard.owner_ranking} />
        </div>
        <div className="min-w-0">
          <PieActCard data={docsByType} />
        </div>
      </section>

      {error ? <div className="ep-kpi-critical rounded-2xl px-4 py-3 text-sm">{error}</div> : null}
    </div>
  );
}
```

## File: components/app-shell/notaries-settings.tsx
```typescript
"use client";

import { NotariesCatalog } from "@/components/notaries/notaries-catalog";

export function NotariesSettings() {
  return <NotariesCatalog />;
}
```

## File: components/cases/case-detail-workspace.tsx
```typescript
"use client";

import Link from "next/link";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { ArrowLeft, Download, FileSignature, MessageSquareText, NotebookTabs, Sparkles, Upload } from "lucide-react";
import { addClientComment, addInternalNote, approveDocumentCase, exportDocumentCase, getDocumentCase, uploadFinalSigned, type DocumentFlowCase } from "@/lib/document-flow";
import { formatDateTime } from "@/lib/datetime";

const flowSteps = [
  "borrador",
  "en_diligenciamiento",
  "revision_cliente",
  "ajustes_solicitados",
  "revision_aprobador",
  "devuelto_aprobador",
  "revision_notario",
  "rechazado_notario",
  "aprobado_notario",
  "generado",
  "firmado_cargado",
  "cerrado",
];
const tabs = ["Resumen", "Intervinientes", "Datos del acto", "Comentarios del cliente", "Observaciones internas", "Documentos", "Trazabilidad", "Documento Gari"] as const;

function pretty(value: string) {
  return formatDateTime(value);
}

function parseActData(caseDetail: DocumentFlowCase | null) {
  const raw = caseDetail?.act_data?.data_json;
  if (!raw) return {} as Record<string, string>;
  try {
    const parsed = JSON.parse(raw) as Record<string, unknown>;
    return Object.fromEntries(Object.entries(parsed ?? {}).map(([key, value]) => [key, String(value ?? "")]));
  } catch {
    return {} as Record<string, string>;
  }
}

async function fetchGenerateWithGari(caseId: number, comment: string, correctionText: string | null) {
  const token = localStorage.getItem("easypro2_session");
  const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? "";
  const response = await fetch(`${baseUrl}/api/v1/document-flow/cases/${caseId}/generate-with-gari`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json",
      ...(token ? { "Authorization": `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ comment, correction_text: correctionText }),
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text);
  }
  return response.json() as Promise<DocumentFlowCase>;
}

export function CaseDetailWorkspace({ caseId, initialTab }: { caseId: number; initialTab?: string }) {
  const [caseDetail, setCaseDetail] = useState<DocumentFlowCase | null>(null);
  const [tab, setTab] = useState<(typeof tabs)[number]>(initialTab === "documento-gari" ? "Documento Gari" : "Resumen");
  const [clientComment, setClientComment] = useState("");
  const [internalNote, setInternalNote] = useState("");
  const [finalFile, setFinalFile] = useState<File | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [isGeneratingGari, setIsGeneratingGari] = useState(false);
  const [isApproving, setIsApproving] = useState(false);
  const [gariText, setGariText] = useState<string | null>(null);
  const [reviewerMode, setReviewerMode] = useState(false);
  const [correctionNote, setCorrectionNote] = useState("");
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!Number.isFinite(caseId) || caseId <= 0) {
      setError("El identificador de la minuta no es válido.");
      setIsLoading(false);
      return;
    }
    void load();
  }, [caseId]);

  useEffect(() => {
    if (initialTab === "documento-gari") {
      setTab("Documento Gari");
    }
  }, [initialTab]);

  async function load() {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getDocumentCase(caseId);
      setCaseDetail(data);
      const draftText = data?.act_data?.gari_draft_text ?? null;
      if (draftText && draftText.trim().length > 0) {
        setGariText(draftText);
      }
    } catch (issue) {
      setCaseDetail(null);
      setError(issue instanceof Error ? issue.message : "No fue posible cargar la minuta.");
    } finally {
      setIsLoading(false);
    }
  }

  const currentStep = useMemo(() => flowSteps.indexOf(caseDetail?.current_state || "borrador"), [caseDetail]);
  const actData = useMemo(() => parseActData(caseDetail), [caseDetail]);
  const documents = Array.isArray(caseDetail?.documents) ? caseDetail.documents : [];
  const participants = Array.isArray(caseDetail?.participants) ? caseDetail.participants : [];
  const clientComments = Array.isArray(caseDetail?.client_comments) ? caseDetail.client_comments : [];
  const internalNotes = Array.isArray(caseDetail?.internal_notes) ? caseDetail.internal_notes : [];
  const workflowEvents = Array.isArray(caseDetail?.workflow_events) ? caseDetail.workflow_events : [];
  const draftDocument = documents.find((item) => item.category === "draft") ?? null;
  const hasDraftVersion = Boolean(draftDocument && Array.isArray(draftDocument.versions) && draftDocument.versions.length > 0);
  const canShowApproveButton = caseDetail?.current_state !== "aprobado_notario" && caseDetail?.current_state !== "cerrado";

  useEffect(() => {
    const text = caseDetail?.act_data?.gari_draft_text ?? null;
    if (text && text.trim().length > 0) {
      setGariText(text);
    }
  }, [caseDetail?.act_data?.gari_draft_text]);

  async function fileToBase64(file: File) {
    return new Promise<string>((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(String(reader.result).split(",")[1] ?? "");
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }

  async function handleClientComment(event: FormEvent) {
    event.preventDefault();
    if (!clientComment.trim()) return;
    setError(null);
    setFeedback(null);
    try {
      setCaseDetail(await addClientComment(caseId, clientComment));
      setClientComment("");
      setFeedback("Comentario del cliente registrado.");
    } catch (issue) {
      setError(issue instanceof Error ? issue.message : "No fue posible registrar el comentario.");
    }
  }

  async function handleInternalNote(event: FormEvent) {
    event.preventDefault();
    if (!internalNote.trim()) return;
    setError(null);
    setFeedback(null);
    try {
      setCaseDetail(await addInternalNote(caseId, internalNote));
      setInternalNote("");
      setFeedback("Observación interna registrada.");
    } catch (issue) {
      setError(issue instanceof Error ? issue.message : "No fue posible registrar la observación interna.");
    }
  }

  async function handleExport(format: "docx" | "pdf") {
    setError(null);
    setFeedback(null);
    try {
      setCaseDetail(await exportDocumentCase(caseId, format));
      setFeedback(`Exportación ${format.toUpperCase()} lista.`);
    } catch (issue) {
      setError(issue instanceof Error ? issue.message : "No fue posible exportar el documento.");
    }
  }

  async function handleFinalUpload() {
    if (!finalFile) {
      setError("Selecciona un archivo antes de cargar el documento definitivo.");
      return;
    }
    setError(null);
    setFeedback(null);
    try {
      setCaseDetail(await uploadFinalSigned(caseId, finalFile.name, await fileToBase64(finalFile), "Documento definitivo cargado desde detalle."));
      setFeedback("Documento definitivo cargado.");
    } catch (issue) {
      setError(issue instanceof Error ? issue.message : "No fue posible cargar el documento definitivo.");
    }
  }

  async function handleGenerateGari() {
    setIsGeneratingGari(true);
    setError(null);
    setFeedback(null);
    try {
      const updated = await fetchGenerateWithGari(caseId, "Generado con Gari desde detalle del caso", null);
      setCaseDetail(updated);
      setGariText(updated?.act_data?.gari_draft_text ?? null);
      setTab("Documento Gari");
      setFeedback(null);
      setTimeout(() => setFeedback("Documento generado por Gari correctamente."), 100);
    } catch (issue) {
      setError(issue instanceof Error ? issue.message : "No fue posible generar el documento con Gari.");
    } finally {
      setIsGeneratingGari(false);
    }
  }

  async function handleApproveDocument() {
    setError(null);
    setFeedback(null);
    setIsApproving(true);
    try {
      await approveDocumentCase(caseId, "approver", "Documento aprobado");
      const updated = await getDocumentCase(caseId);
      setCaseDetail(updated);
      setGariText(updated?.act_data?.gari_draft_text ?? null);
      setFeedback("Documento revisado. Listo para firma del notario.");
    } catch (issue) {
      setError(issue instanceof Error ? issue.message : "Error al aprobar.");
    } finally {
      setIsApproving(false);
    }
  }

  if (isLoading) {
    return <div className="ep-card rounded-[2rem] p-6 text-secondary">Cargando minuta...</div>;
  }

  if (error && !caseDetail) {
    return <div className="ep-kpi-critical rounded-[2rem] px-6 py-5 text-sm">{error}</div>;
  }

  if (!caseDetail) {
    return <div className="ep-card rounded-[2rem] p-6 text-secondary">Sin datos de la minuta todavía.</div>;
  }

  async function handleDownload(downloadUrl: string, filename: string) {
    try {
      if (downloadUrl.startsWith("https://")) {
        const a = document.createElement("a");
        a.href = downloadUrl;
        a.download = filename;
        a.target = "_blank";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        return;
      }

      const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8001";
      const { getToken } = await import("@/lib/auth");
      const token = getToken();
      const res = await fetch(`${API_URL}${downloadUrl}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (!res.ok) throw new Error("No fue posible descargar el archivo.");
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (issue) {
      setError(issue instanceof Error ? issue.message : "Error al descargar.");
    }
  }

  return (
    <div className="space-y-6">
      <section className="ep-card rounded-[2rem] p-6">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <Link href="/dashboard/casos" className="inline-flex items-center gap-2 text-sm font-semibold text-primary"><ArrowLeft className="h-4 w-4" />Volver a minutas</Link>
            <p className="mt-4 text-sm font-semibold uppercase tracking-[0.22em] text-accent">Detalle de la minuta</p>
            <h1 className="mt-2 text-3xl font-semibold tracking-[-0.05em] text-primary">{caseDetail.act_type || "Minuta documental"}</h1>
            <p className="mt-3 text-base text-secondary">{caseDetail.internal_case_number || "Sin número interno"} · {caseDetail.notary_label || "Sin notaría"}</p>
          </div>
          <div className="grid gap-3 sm:grid-cols-2 lg:w-[430px]">
            <div className="ep-card-muted rounded-[1.5rem] p-4"><p className="text-xs uppercase tracking-[0.2em] text-secondary">Estado</p><p className="mt-2 text-lg font-semibold text-primary">{caseDetail.current_state || "Sin estado"}</p></div>
            <div className="ep-card-muted rounded-[1.5rem] p-4"><p className="text-xs uppercase tracking-[0.2em] text-secondary">Escritura oficial</p><p className="mt-2 text-lg font-semibold text-primary">{caseDetail.official_deed_number || "Pendiente"}</p></div>
            <div className="ep-card-muted rounded-[1.5rem] p-4"><p className="text-xs uppercase tracking-[0.2em] text-secondary">Responsable actual</p><p className="mt-2 text-lg font-semibold text-primary">{caseDetail.current_owner_user_name || "Sin asignar"}</p></div>
            <div className="ep-card-muted rounded-[1.5rem] p-4"><p className="text-xs uppercase tracking-[0.2em] text-secondary">Borrador actual</p><p className="mt-2 text-lg font-semibold text-primary">{draftDocument?.current_version_number ? `v${draftDocument.current_version_number}` : "Sin generar"}</p></div>
          </div>
        </div>
      </section>

      <section className="ep-card rounded-[2rem] p-6">
        <p className="text-xs uppercase tracking-[0.2em] text-secondary">Flujo documental</p>
        <div className="mt-4 grid gap-3 xl:grid-cols-6">
          {flowSteps.map((item, index) => <div key={item} className={`rounded-[1.35rem] border px-4 py-4 ${index === currentStep ? "border-primary/30 bg-primary text-white" : index < currentStep ? "border-emerald-500/20 bg-emerald-500/10" : "border-[var(--line)] bg-[var(--panel-soft)]"}`}><p className={`text-sm font-semibold ${index === currentStep ? "text-white" : "text-primary"}`}>{item}</p></div>)}
        </div>
      </section>

      <section className="ep-card rounded-[2rem] p-6">
        <div className="flex flex-wrap gap-2">{tabs.map((item) => <button key={item} type="button" onClick={() => setTab(item)} className={`rounded-full px-4 py-2 text-sm font-semibold ${tab === item ? "bg-primary text-white" : "ep-pill text-secondary"}`}>{item}</button>)}</div>
        <div className="mt-6">
          {tab === "Resumen" ? <div className="grid gap-4 lg:grid-cols-2"><div className="ep-card-soft rounded-[1.5rem] p-5"><p className="text-sm font-semibold text-primary">Plantilla</p><p className="mt-2 text-sm text-secondary">{caseDetail.template_name || "Sin plantilla"}</p><p className="mt-4 text-sm font-semibold text-primary">Creador</p><p className="mt-2 text-sm text-secondary">{caseDetail.created_by_user_name || "Sistema"}</p><p className="mt-4 text-sm font-semibold text-primary">Fecha de creación</p><p className="mt-2 text-sm text-secondary">{pretty(caseDetail.created_at)}</p></div><div className="ep-card-soft rounded-[1.5rem] p-5"><p className="text-sm font-semibold text-primary">Aprobación</p><p className="mt-2 text-sm text-secondary">{caseDetail.approved_by_user_name ? `${caseDetail.approved_by_user_name} · ${caseDetail.approved_by_role_code || "rol"}` : "Pendiente"}</p><p className="mt-4 text-sm font-semibold text-primary">Documento firmado final</p><p className="mt-2 text-sm text-secondary">{caseDetail.final_signed_uploaded ? "Cargado" : "Pendiente"}</p></div></div> : null}
          {tab === "Intervinientes" ? (
            participants.length > 0 ? <div className="grid gap-4 lg:grid-cols-2">{participants.map((item) => <div key={item.id} className="ep-card-soft rounded-[1.5rem] p-5"><div className="flex items-center justify-between"><p className="text-sm font-semibold text-primary">{item.role_label || "Interviniente"}</p><span className="ep-pill rounded-full px-3 py-1 text-xs text-secondary">{item.person.document_type || "DOC"} {item.person.document_number || "Sin número"}</span></div><p className="mt-3 text-lg font-semibold text-primary">{item.person.full_name || "Sin nombre"}</p><p className="mt-2 text-sm text-secondary">{item.person.nationality || "Sin nacionalidad"} · {item.person.marital_status || "Sin estado civil"}</p><p className="mt-2 text-sm text-secondary">{item.person.profession || "Sin profesión"} · {item.person.municipality || "Sin municipio"}</p><p className="mt-2 text-sm text-secondary">{item.person.address || "Sin dirección"} · {item.person.phone || "Sin teléfono"}</p></div>)}</div> : <div className="ep-card-muted rounded-[1.5rem] px-4 py-6 text-sm text-secondary">Sin intervinientes todavía.</div>
          ) : null}
          {tab === "Datos del acto" ? (
            Object.keys(actData).length > 0 ? <div className="grid gap-4 lg:grid-cols-2">{Object.entries(actData).map(([key, value]) => <div key={key} className="ep-card-soft rounded-[1.5rem] p-4"><p className="text-xs uppercase tracking-[0.18em] text-secondary">{key}</p><p className="mt-2 text-sm font-semibold text-primary">{String(value || "Sin dato")}</p></div>)}</div> : <div className="ep-card-muted rounded-[1.5rem] px-4 py-6 text-sm text-secondary">Sin datos del acto todavía.</div>
          ) : null}
          {tab === "Comentarios del cliente" ? <div className="space-y-4"><form onSubmit={handleClientComment} className="space-y-3"><textarea value={clientComment} onChange={(event) => setClientComment(event.target.value)} rows={4} className="ep-textarea w-full rounded-2xl px-4 py-3" placeholder="Registrar comentario del cliente..." /><button type="submit" className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white"><MessageSquareText className="h-4 w-4" />Agregar comentario</button></form><div className="space-y-3">{clientComments.length > 0 ? clientComments.map((item) => <div key={item.id} className="ep-card-soft rounded-[1.5rem] p-4"><p className="text-sm font-semibold text-primary">{item.created_by_user_name || "Usuario"}</p><p className="mt-2 text-sm text-secondary">{item.comment || "Sin comentario"}</p><p className="mt-2 text-xs text-secondary">{pretty(item.created_at)}</p></div>) : <div className="ep-card-muted rounded-[1.5rem] px-4 py-6 text-sm text-secondary">Sin comentarios del cliente todavía.</div>}</div></div> : null}
          {tab === "Observaciones internas" ? <div className="space-y-4"><form onSubmit={handleInternalNote} className="space-y-3"><textarea value={internalNote} onChange={(event) => setInternalNote(event.target.value)} rows={4} className="ep-textarea w-full rounded-2xl px-4 py-3" placeholder="Registrar observación interna..." /><button type="submit" className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white"><NotebookTabs className="h-4 w-4" />Agregar observación</button></form><div className="space-y-3">{internalNotes.length > 0 ? internalNotes.map((item) => <div key={item.id} className="ep-card-soft rounded-[1.5rem] p-4"><p className="text-sm font-semibold text-primary">{item.created_by_user_name || "Usuario"}</p><p className="mt-2 text-sm text-secondary">{item.note || "Sin nota"}</p><p className="mt-2 text-xs text-secondary">{pretty(item.created_at)}</p></div>) : <div className="ep-card-muted rounded-[1.5rem] px-4 py-6 text-sm text-secondary">Sin observaciones internas todavía.</div>}</div></div> : null}
          {tab === "Documentos" ? <div className="space-y-4"><div className="rounded-2xl border border-[#00E5A0]/30 bg-[#00E5A0]/5 p-5 space-y-3"><div className="flex items-center gap-3"><div className="w-8 h-8 rounded-full bg-[#00E5A0]/20 flex items-center justify-center"><Sparkles className="h-4 w-4 text-[#00E5A0]" /></div><div><p className="text-sm font-semibold text-primary">Gari ? Generaci?n documental</p><p className="text-xs text-secondary">Gari redacta el documento completo en lenguaje notarial colombiano</p></div></div><button type="button" onClick={() => void handleGenerateGari()} disabled={isGeneratingGari} className="inline-flex items-center gap-2 rounded-2xl px-5 py-3 text-sm font-semibold text-[#0D1B2A] bg-[#00E5A0] hover:bg-[#00C98A] transition disabled:opacity-60 disabled:cursor-not-allowed"><Sparkles className="h-4 w-4" />{isGeneratingGari ? "Gari est? redactando..." : "Generar con Gari"}</button>{gariText && (<p className="text-xs text-[#00E5A0]">Documento Gari disponible ? ver en tab "Documento Gari"</p>)}</div><div className="grid gap-4 lg:grid-cols-2"><button type="button" onClick={() => void handleExport("docx")} className="inline-flex items-center justify-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white"><Download className="h-4 w-4" />Exportar Word</button><button type="button" onClick={() => void handleExport("pdf")} className="inline-flex items-center justify-center gap-2 rounded-2xl border border-[var(--line)] px-5 py-3 text-sm font-semibold text-primary"><Download className="h-4 w-4" />Exportar PDF</button></div><label className="ep-card-muted flex items-center justify-between rounded-2xl px-4 py-4 text-sm text-secondary"><span className="inline-flex items-center gap-2"><Upload className="h-4 w-4 text-primary" />Documento definitivo</span><input type="file" accept=".pdf,.doc,.docx" onChange={(event) => setFinalFile(event.target.files?.[0] ?? null)} /></label><button type="button" onClick={() => void handleFinalUpload()} disabled={!finalFile} className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white disabled:opacity-60"><Upload className="h-4 w-4" />Cargar definitivo</button><div className="space-y-3">{documents.length > 0 ? documents.map((document) => <div key={document.id} className="ep-card-soft rounded-[1.5rem] p-4"><div className="flex items-center justify-between"><p className="text-sm font-semibold text-primary">{document.title || "Documento"}</p><span className="ep-pill rounded-full px-3 py-1 text-xs text-secondary">{document.category || "sin categoría"}</span></div><div className="mt-3 space-y-2">{Array.isArray(document.versions) && document.versions.length > 0 ? document.versions.map((version) => <button key={version.id} type="button" onClick={() => void handleDownload(version.download_url || "", `v${version.version_number}.${version.file_format || "docx"}`)} className="flex w-full items-center justify-between rounded-xl border border-[var(--line)] px-3 py-3 hover:bg-[var(--panel)] text-left"><span className="text-sm text-primary">v{version.version_number} ? {(version.file_format || "bin").toUpperCase()}</span><span className="text-xs text-secondary">{pretty(version.created_at)}</span></button>) : <div className="ep-card-muted rounded-xl px-3 py-3 text-sm text-secondary">Sin versiones todavía.</div>}</div></div>) : <div className="ep-card-muted rounded-[1.5rem] px-4 py-6 text-sm text-secondary">Sin documentos todavía.</div>}</div></div> : null}
          {tab === "Documento Gari" ? (
            <div className="space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => setReviewerMode(false)}
                    className={`rounded-full px-4 py-2 text-sm font-semibold transition ${!reviewerMode ? "bg-primary text-white" : "ep-pill text-secondary"}`}
                  >
                    Ver borrador
                  </button>
                  <button
                    type="button"
                    onClick={() => setReviewerMode(true)}
                    className={`rounded-full px-4 py-2 text-sm font-semibold transition ${reviewerMode ? "bg-primary text-white" : "ep-pill text-secondary"}`}
                  >
                    Modo revisor
                  </button>
                </div>
                <div className="flex items-center gap-2">
                  {draftDocument?.versions?.[0] && (
                    <button
                      type="button"
                      onClick={async () => {
  try {
    const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8001";
    const { getToken } = await import("@/lib/auth");
    const token = getToken();
    const res = await fetch(`${API_URL}/api/v1/document-flow/cases/${caseId}/gari-download`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    if (!res.ok) throw new Error("No fue posible descargar el archivo.");
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `caso_${caseId}_gari.docx`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  } catch (issue) {
    setError(issue instanceof Error ? issue.message : "Error al descargar.");
  }
}}
                      className="inline-flex items-center gap-2 rounded-full border border-[var(--line)] px-4 py-2 text-sm font-semibold text-primary"
                    >
                      <Download className="h-4 w-4" />
                      Descargar Word
                    </button>
                  )}
                  <button
                    type="button"
                    onClick={() => void handleGenerateGari()}
                    disabled={isGeneratingGari}
                    className="inline-flex items-center gap-2 rounded-full bg-[#00E5A0] px-4 py-2 text-sm font-semibold text-[#0D1B2A] hover:bg-[#00C98A] transition disabled:opacity-60"
                  >
                    <Sparkles className="h-4 w-4" />
                    {isGeneratingGari ? "Generando..." : "Regenerar con Gari"}
                  </button>
                </div>
              </div>

              {draftDocument && Array.isArray(draftDocument.versions) && draftDocument.versions.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {draftDocument.versions.map((v) => (
                    <span key={v.id} className="ep-pill rounded-full px-3 py-1 text-xs text-secondary">
                      v{v.version_number}  {v.file_format?.toUpperCase() ?? "DOCX"}  {formatDateTime(v.created_at)}
                    </span>
                  ))}
                </div>
              )}

              {gariText || (draftDocument && Array.isArray(draftDocument.versions) && draftDocument.versions.length > 0) ? (
                <div className="flex gap-4 items-start">
                  <div
                    className="flex-1 min-w-0 rounded-2xl border border-[var(--line)] bg-white text-[#1A1A1A] overflow-auto"
                    style={{ minHeight: "70vh" }}
                  >
                    <div
                      className="mx-auto px-16 py-14"
                      style={{
                        maxWidth: "780px",
                        fontFamily: "Georgia, 'Times New Roman', serif",
                        fontSize: "13px",
                        lineHeight: "1.85",
                        color: "#1A1A1A",
                      }}
                    >
                      {gariText ? (
                        gariText
                          .split(/\[\[--\]\]|\n/)
                          .map((line, i) => {
                            const trimmed = line.trim();
                            if (!trimmed) return <div key={i} style={{ height: "0.75em" }} />;
                            const isBold = trimmed.startsWith("**") && trimmed.endsWith("**");
                            const clean = isBold ? trimmed.slice(2, -2) : trimmed;
                            const isHeader = isBold || /^(PRIMERO|SEGUNDO|TERCERO|CUARTO|QUINTO|SEXTO|SÉPTIMO|OCTAVO|NOVENO|DÉCIMO|ESCRITURA PÚBLICA|ACTO:|FECHA:|DE:|A:|VALOR:|OTORGAMIENTO|ACEPTACION|DERECHOS NOTARIALES|SUPERFONDO|PARÁGRAFO|PARAGRAFO|CONSTANCIA|AUTORIZACIÓN|NOTA)/i.test(clean);
                            return (
                              <p
                                key={i}
                                style={{
                                  fontWeight: isHeader ? "700" : "400",
                                  textAlign: "justify",
                                  marginBottom: isHeader ? "0.8em" : "0.4em",
                                  marginTop: isHeader ? "1em" : "0",
                                }}
                              >
                                {clean}
                              </p>
                            );
                          })
                      ) : (
                        <div style={{ textAlign: "center", padding: "3rem 0", color: "#8892A4" }}>
                          <p style={{ fontSize: "14px" }}>El texto del documento está disponible en el archivo Word descargable.</p>
                          <p style={{ fontSize: "13px", marginTop: "0.5rem" }}>Usa el botón "Descargar Word" para ver el contenido completo.</p>
                        </div>
                      )}
                    </div>
                  </div>

                  {reviewerMode && (
                    <div className="w-80 shrink-0 space-y-4">
                      <div className="ep-card-soft rounded-2xl p-5 space-y-3">
                        <p className="text-sm font-semibold text-primary">Instrucciones de corrección</p>
                        <p className="text-xs text-secondary">Describe qué debe cambiar Gari en la próxima versión.</p>
                        <textarea
                          value={correctionNote}
                          onChange={(e) => setCorrectionNote(e.target.value)}
                          rows={6}
                          className="ep-textarea w-full rounded-xl px-3 py-2 text-sm"
                          placeholder="Ej: Corregir el estado civil del poderdante, agregar cláusula de..., cambiar el municipio de expedición..."
                        />
                        <button
                          type="button"
                          disabled={isRegenerating || !correctionNote.trim()}
                          onClick={async () => {
                            setIsRegenerating(true);
                            setError(null);
                            try {
                              const updated = await fetchGenerateWithGari(caseId, correctionNote, correctionNote);
                              setCaseDetail(updated);
                              setGariText(updated?.act_data?.gari_draft_text ?? null);
                              setCorrectionNote("");
                              setFeedback("Nueva versión generada con las correcciones.");
                            } catch (issue) {
                              setError(issue instanceof Error ? issue.message : "Error al regenerar.");
                            } finally {
                              setIsRegenerating(false);
                            }
                          }}
                          className="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-[#00E5A0] px-4 py-3 text-sm font-semibold text-[#0D1B2A] hover:bg-[#00C98A] transition disabled:opacity-60"
                        >
                          <Sparkles className="h-4 w-4" />
                          {isRegenerating ? "Regenerando..." : "Aplicar correcciones"}
                        </button>
                      </div>

                      {draftDocument && Array.isArray(draftDocument.versions) && draftDocument.versions.length > 0 && (
                        <div className="ep-card-soft rounded-2xl p-5 space-y-3">
                          <p className="text-sm font-semibold text-primary">Historial de versiones</p>
                          <div className="space-y-2">
                            {[...draftDocument.versions].reverse().map((v) => (
                              <div key={v.id} className="flex items-center justify-between rounded-xl border border-[var(--line)] px-3 py-2">
                                <div>
                                  <p className="text-sm font-semibold text-primary">v{v.version_number}</p>
                                  <p className="text-xs text-secondary">{formatDateTime(v.created_at)}</p>
                                </div>
                                <button
                                  type="button"
                                  onClick={() => void handleDownload(
                                    v.download_url ?? "",
                                    `gari_v${v.version_number}.docx`
                                  )}
                                  className="rounded-lg border border-[var(--line)] p-1.5 text-secondary hover:text-primary transition"
                                >
                                  <Download className="h-3.5 w-3.5" />
                                </button>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {canShowApproveButton && hasDraftVersion ? (
                        <button
                          type="button"
                          onClick={() => void handleApproveDocument()}
                          disabled={isApproving}
                          className="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-primary px-4 py-3 text-sm font-semibold text-white hover:opacity-90 transition disabled:cursor-not-allowed disabled:opacity-60"
                        >
                          <FileSignature className="h-4 w-4" />
                          {isApproving ? "Aprobando..." : "Aprobar documento"}
                        </button>
                      ) : null}
                      {canShowApproveButton && !hasDraftVersion ? (
                        <div className="ep-card-muted rounded-xl px-4 py-3 text-sm text-secondary">
                          Debes generar al menos un borrador antes de aprobar
                        </div>
                      ) : null}
                    </div>
                  )}
                </div>
              ) : (
                <div className="ep-card-muted rounded-2xl px-6 py-12 text-center space-y-4">
                  <Sparkles className="h-8 w-8 text-[#00E5A0] mx-auto" />
                  <p className="text-sm font-semibold text-primary">Aún no hay documento generado por Gari</p>
                  <p className="text-sm text-secondary">Ve al tab Documentos y presiona "Generar con Gari" para crear el borrador.</p>
                  <button
                    type="button"
                    onClick={() => setTab("Documentos")}
                    className="inline-flex items-center gap-2 rounded-full bg-[#00E5A0] px-5 py-2.5 text-sm font-semibold text-[#0D1B2A] hover:bg-[#00C98A] transition"
                  >
                    <Sparkles className="h-4 w-4" />
                    Ir a Documentos
                  </button>
                </div>
              )}
            </div>
          ) : null}
          {tab === "Trazabilidad" ? <div className="space-y-3">{workflowEvents.length > 0 ? workflowEvents.map((item) => <div key={item.id} className="ep-card-soft rounded-[1.5rem] p-4"><div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between"><p className="text-sm font-semibold text-primary">{item.event_type || "evento"}</p><span className="text-xs text-secondary">{pretty(item.created_at)}</span></div><p className="mt-2 text-sm text-secondary">Actor: {item.actor_user_name || "Sistema"}{item.actor_role_code ? ` · ${item.actor_role_code}` : ""}</p>{item.comment ? <p className="mt-2 text-sm text-secondary">{item.comment}</p> : null}{item.new_value ? <p className="mt-2 text-sm text-secondary">Nuevo valor: {item.new_value}</p> : null}</div>) : <div className="ep-card-muted rounded-[1.5rem] px-4 py-6 text-sm text-secondary">Sin trazabilidad todavía.</div>}</div> : null}
        </div>
        {feedback ? <div className="ep-kpi-success mt-6 rounded-2xl px-4 py-3 text-sm">{feedback}</div> : null}
        {error ? <div className="ep-kpi-critical mt-6 rounded-2xl px-4 py-3 text-sm">{error}</div> : null}
      </section>
    </div>
  );
}
```

## File: components/cases/cases-workspace.tsx
```typescript
"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { ArrowRight, Filter, RefreshCw } from "lucide-react";
import { getCaseFilters, getCases, getCurrentUser, type CaseFilterOptions, type CaseFilters, type CaseRecord } from "@/lib/api";

const emptyFilters: CaseFilters = {
  current_state: "",
  case_type: "",
  notary_id: "",
  current_owner_user_id: "",
  q: ""
};

function statusSummary(cases: CaseRecord[]) {
  const summary = new Map<string, number>();
  for (const item of cases) {
    summary.set(item.current_state, (summary.get(item.current_state) ?? 0) + 1);
  }
  return Array.from(summary.entries()).sort((a, b) => b[1] - a[1]);
}

export function CasesWorkspace() {
  const [cases, setCases] = useState<CaseRecord[]>([]);
  const [filters, setFilters] = useState<CaseFilters>(emptyFilters);
  const [filterOptions, setFilterOptions] = useState<CaseFilterOptions>({ case_types: [], act_types: [], states: [], owners: [], notaries: [] });
  const [isSuperAdmin, setIsSuperAdmin] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void Promise.all([loadCases(emptyFilters), loadFilters(), loadCurrentUser()]);
  }, []);

  async function loadCases(nextFilters: CaseFilters) {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getCases(nextFilters);
      setCases(data);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "No fue posible cargar las minutas.");
    } finally {
      setIsLoading(false);
    }
  }

  async function loadFilters() {
    try {
      setFilterOptions(await getCaseFilters());
    } catch {
      // Mantener vista usable sin filtros.
    }
  }

  async function loadCurrentUser() {
    try {
      const user = await getCurrentUser();
      setIsSuperAdmin(user?.roles?.includes("super_admin") ?? false);
    } catch {
      setIsSuperAdmin(false);
    }
  }

  function updateFilter<K extends keyof CaseFilters>(field: K, value: string) {
    const nextFilters = { ...filters, [field]: value };
    setFilters(nextFilters);
    void loadCases(nextFilters);
  }

  const stateStats = useMemo(() => statusSummary(cases), [cases]);
  const clientReviewCount = useMemo(() => cases.filter((item) => item.requires_client_review).length, [cases]);
  const finalSignedCount = useMemo(() => cases.filter((item) => item.final_signed_uploaded).length, [cases]);

  const ownerOptions = useMemo(() => {
    const seen = new Map<string, string>();
    cases.forEach((item) => {
      if (item.current_owner_user_id && item.current_owner_user_name) {
        seen.set(String(item.current_owner_user_id), item.current_owner_user_name);
      }
    });
    return Array.from(seen.entries());
  }, [cases]);

  const notaryOptions = useMemo(() => {
    const seen = new Map<string, string>();
    cases.forEach((item) => {
      seen.set(String(item.notary_id), item.notary_label);
    });
    return Array.from(seen.entries());
  }, [cases]);

  return (
    <div className="space-y-6">
      <section className="ep-card rounded-[2rem] p-6">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <h1 className="text-3xl font-semibold text-primary">Minutas</h1>
          </div>
          <div className="flex flex-wrap gap-3">
            <Link href="/dashboard/casos/crear" className="inline-flex items-center gap-2 rounded-2xl border border-[var(--line)] px-5 py-3 text-sm font-semibold text-primary">
              Crear minuta
            </Link>
            <button onClick={() => void loadCases(filters)} className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white shadow-panel">
              <RefreshCw className="h-4 w-4" />
              Refrescar minutas
            </button>
          </div>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-4">
          <div className="ep-card-muted rounded-[1.5rem] p-4"><p className="text-xs uppercase tracking-[0.2em] text-secondary">Minutas visibles</p><p className="mt-3 text-3xl font-semibold text-primary">{cases.length}</p></div>
          <div className="ep-card-muted rounded-[1.5rem] p-4"><p className="text-xs uppercase tracking-[0.2em] text-secondary">Con revisión cliente</p><p className="mt-3 text-3xl font-semibold text-primary">{clientReviewCount}</p></div>
          <div className="ep-card-muted rounded-[1.5rem] p-4"><p className="text-xs uppercase tracking-[0.2em] text-secondary">Firmado cargado</p><p className="mt-3 text-3xl font-semibold text-primary">{finalSignedCount}</p></div>
          <div className="rounded-[1.5rem] bg-primary p-4 text-white shadow-panel"><p className="text-xs uppercase tracking-[0.2em] text-white/72">Estados activos</p><p className="mt-3 text-3xl font-semibold">{stateStats.length}</p></div>
        </div>
      </section>

      <section className="ep-card rounded-[2rem] p-6">
        <div className="flex flex-col gap-5 xl:flex-row xl:items-end xl:justify-between">
          <div />
        </div>

        <div className={`ep-filter-panel mt-6 grid grid-cols-2 gap-3 rounded-[1.75rem] p-4 ${isSuperAdmin ? "lg:grid-cols-5" : "lg:grid-cols-4"}`}>
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-secondary">Estado</label>
            <select value={filters.current_state ?? ""} onChange={(event) => updateFilter("current_state", event.target.value)} className="ep-select h-10 rounded-2xl px-3 text-sm"><option value="">Todos</option>{filterOptions.states.map((item) => <option key={item} value={item}>{item}</option>)}</select>
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-secondary">Tipo de minuta</label>
            <select value={filters.case_type ?? ""} onChange={(event) => updateFilter("case_type", event.target.value)} className="ep-select h-10 rounded-2xl px-3 text-sm"><option value="">Todos</option>{filterOptions.case_types.map((item) => <option key={item} value={item}>{item}</option>)}</select>
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-secondary">Responsable</label>
            <select value={filters.current_owner_user_id ?? ""} onChange={(event) => updateFilter("current_owner_user_id", event.target.value)} className="ep-select h-10 rounded-2xl px-3 text-sm"><option value="">Todos</option>{ownerOptions.map(([id, name]) => <option key={id} value={id}>{name}</option>)}</select>
          </div>
          {isSuperAdmin ? (
            <div className="flex flex-col gap-1">
              <label className="text-xs font-medium text-secondary">Notaría</label>
              <select value={filters.notary_id ?? ""} onChange={(event) => updateFilter("notary_id", event.target.value)} className="ep-select h-10 rounded-2xl px-3 text-sm"><option value="">Todas</option>{notaryOptions.map(([id, label]) => <option key={id} value={id}>{label}</option>)}</select>
            </div>
          ) : null}
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-secondary">Buscar</label>
            <input value={filters.q ?? ""} onChange={(event) => updateFilter("q", event.target.value)} placeholder="Acto, minuta, notaría..." className="ep-input h-10 rounded-2xl px-3 text-sm" />
          </div>
        </div>

        {error ? <div className="ep-kpi-critical mt-5 rounded-2xl px-4 py-3 text-sm">{error}</div> : null}

        <div className="mt-6 grid gap-4">
          <div className="space-y-3">
            {isLoading ? <div className="ep-card-muted rounded-[1.5rem] px-4 py-6 text-sm text-secondary">Cargando minutas...</div> : null}
            {!isLoading && cases.length === 0 ? <div className="ep-card-muted rounded-[1.5rem] px-4 py-6 text-sm text-secondary">No hay minutas para los filtros seleccionados.</div> : null}
            {cases.map((item) => (
              <Link key={item.id} href={`/dashboard/casos/${item.id}`} className="block ep-card-soft rounded-[1.6rem] p-5 transition hover:-translate-y-0.5 hover:border-primary/25 hover:shadow-soft">
                <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                  <div className="min-w-0">
                    <div className="flex items-center gap-3">
                      <span className="rounded-full bg-primary/10 px-3 py-1 text-xs font-semibold text-primary">{item.case_type}</span>
                      <h3 className="truncate text-lg font-semibold text-primary">{item.act_type}</h3>
                    </div>
                    <p className="mt-2 text-sm text-secondary">Minuta {item.year}-{String(item.consecutive).padStart(4, "0")} · {item.notary_label}</p>
                    <p className="mt-2 text-sm leading-6 text-secondary">Responsable actual: {item.current_owner_user_name || "Sin asignar"}</p>
                  </div>
                  <div className="grid gap-2 text-sm text-secondary lg:min-w-[230px]">
                    <span className="ep-badge rounded-full px-3 py-1 font-semibold text-primary">{item.current_state}</span>
                    <span>Cliente: {item.client_user_name || "No aplica"}</span>
                    <span>Revisión cliente: {item.requires_client_review ? "Sí" : "No"}</span>
                    <span>Firmado final: {item.final_signed_uploaded ? "Cargado" : "Pendiente"}</span>
                  </div>
                </div>
                <div className="mt-4 flex items-center justify-between text-sm text-primary">
                  <span>{item.protocolist_user_name || "Sin protocolista"}</span>
                  <span className="inline-flex items-center gap-2 font-semibold">Ver detalle <ArrowRight className="h-4 w-4" /></span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
```

## File: components/cases/create-case-wizard.tsx
```typescript
"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { ArrowRight, CheckCircle2, FileSignature } from "lucide-react";
import { PersonLookup } from "@/components/persons/person-lookup";
import { LegalEntityLookup, type LegalEntityPayload, type LegalEntityRecord } from "@/components/persons/legal-entity-lookup";
import { SearchableSelect } from "@/components/ui/searchable-select";
import { ValidatedInput } from "@/components/ui/validated-input";
import {
  createDocumentCase,
  generateCaseDraft,
  getActCatalog,
  getActiveTemplates,
  saveCaseActData,
  saveCaseActs,
  saveCaseParticipants,
  type ActCatalogItem,
  type CaseActItem,
  type PersonRecord,
  type DocumentFlowCase,
  type PersonPayload,
  type TemplateRecord,
} from "@/lib/document-flow";
import { getCurrentUser, getNotaries, getUserOptions, type UserOption } from "@/lib/api";

const steps = [
  "Tipo y actos",
  "Datos generales",
  "Intervinientes",
  "Datos del acto",
  "Revisión",
];
const documentTypes = ["CC", "CE", "TI", "PP", "NIT"];
const sexOptions = ["F", "M", "No especifica"];
const nationalityOptions = ["Colombiana", "Extranjera", "Venezolana", "Española"];
const maritalStatusOptions = ["Soltero(a)", "Casado(a)", "Unión marital", "Divorciado(a)", "Viudo(a)"];
const professionSuggestions = ["Abogado", "Comerciante", "Administrador", "Ingeniero", "Contador", "Docente"];

type SelectOption = { value: string; label: string };

type ParticipantItem = {
  uid: string;
  kind: "person" | "entity";
  roleCode: string;
  roleLabel: string;
  personId: number | null;
  person: PersonPayload | null;
  legalEntityId: number | null;
  legalEntity: LegalEntityPayload | null;
  representative: PersonRecord | PersonPayload | null;
  representativeId: number | null;
  isComplete: boolean;
};

const entityRoleOptions: SelectOption[] = [
  { value: "apoderado_banco_libera", label: "Banco que libera hipoteca" },
  { value: "apoderado_fideicomiso", label: "Fideicomiso / vendedor" },
  { value: "apoderado_fideicomitente", label: "Fideicomitente / constructora" },
  { value: "apoderado_banco_hipoteca", label: "Banco hipotecante" },
  { value: "apoderado_otro", label: "Otra entidad" },
];

const entityRoleLabelMap: Record<string, string> = {
  apoderado_banco_libera: "Banco que libera hipoteca",
  apoderado_fideicomiso: "Fideicomiso / vendedor",
  apoderado_fideicomitente: "Fideicomitente / constructora",
  apoderado_banco_hipoteca: "Banco hipotecante",
  apoderado_otro: "Otra entidad",
};

const ESCRITURA_TYPES = [
  {
    code: "compraventa_vis_contado",
    label: "Compraventa VIS  Contado",
    description: "Sin crédito hipotecario nuevo",
    defaultActs: ["liberacion_hipoteca", "protocolizacion_cto", "compraventa_vis", "renuncia_resolutoria", "cancelacion_comodato", "patrimonio_familia", "poder_especial"],
    templateSlug: "aragua-parq-1c",
  },
  {
    code: "compraventa_vis_hipoteca",
    label: "Compraventa VIS  Con crédito hipotecario",
    description: "Con constitución de hipoteca nueva",
    defaultActs: ["liberacion_hipoteca", "protocolizacion_cto", "compraventa_vis", "renuncia_resolutoria", "cancelacion_comodato", "constitucion_hipoteca", "patrimonio_familia", "poder_especial"],
    templateSlug: "jaggua-bogota-1c",
  },
  {
    code: "correccion_rc",
    label: "Corrección de Registro Civil",
    description: "Corrección de acta de nacimiento",
    defaultActs: ["correccion_rc"],
    templateSlug: "correccion-registro-civil",
  },
  {
    code: "salida_pais",
    label: "Permiso de salida del país",
    description: "Autorización para menor de edad",
    defaultActs: ["salida_pais"],
    templateSlug: "salida-del-pais",
  },
  {
    code: "poder_general",
    label: "Poder general",
    description: "Otorgamiento de poder",
    defaultActs: ["poder_general"],
    templateSlug: "poder-general",
  },
];

const ROLE_PARTICIPANT_MAP: Record<string, { kind: "person" | "entity"; roleCode: string; roleLabel: string }> = {
  compradores: { kind: "person", roleCode: "comprador_1", roleLabel: "Comprador(a)" },
  fideicomiso: { kind: "entity", roleCode: "apoderado_fideicomiso", roleLabel: "Fideicomiso / Vendedor" },
  banco_libera: { kind: "entity", roleCode: "apoderado_banco_libera", roleLabel: "Banco que libera hipoteca" },
  constructora: { kind: "entity", roleCode: "apoderado_fideicomitente", roleLabel: "Constructora" },
  banco_hipoteca: { kind: "entity", roleCode: "apoderado_banco_hipoteca", roleLabel: "Banco hipotecante" },
  inscrito: { kind: "person", roleCode: "inscrito", roleLabel: "Inscrito(a) / Compareciente" },
  padre_otorgante: { kind: "person", roleCode: "padre_otorgante", roleLabel: "Padre otorgante" },
  madre_aceptante: { kind: "person", roleCode: "madre_aceptante", roleLabel: "Madre aceptante" },
  menor: { kind: "person", roleCode: "menor", roleLabel: "Menor de edad" },
  poderdante: { kind: "person", roleCode: "poderdante", roleLabel: "Poderdante" },
  apoderado: { kind: "person", roleCode: "apoderado", roleLabel: "Apoderado(a)" },
};

interface ActWizardItem {
  uid: string;
  code: string;
  label: string;
  roles: string[];
}

function safeString(value: unknown) {
  return typeof value === "string" ? value : "";
}

function normalizeUserOptions(users: UserOption[]): SelectOption[] {
  return (Array.isArray(users) ? users : []).map((item) => ({
    value: String(item.id ?? ""),
    label: [safeString(item.full_name), safeString(item.email)].filter(Boolean).join(" · ") || "Usuario sin nombre",
  })).filter((item) => item.value);
}

function sortByStepOrder<T extends { step_order?: number | null }>(items: T[]) {
  return [...items].sort((a, b) => Number(a.step_order ?? 0) - Number(b.step_order ?? 0));
}

function hasEntitySelection(item: ParticipantItem) {
  return item.legalEntityId !== null || item.legalEntity !== null;
}

function hasRepresentativeSelection(item: ParticipantItem) {
  return item.representativeId !== null || item.representative !== null;
}

function computeEntityComplete(item: ParticipantItem) {
  return hasEntitySelection(item) && hasRepresentativeSelection(item);
}

function buildActDataFromTemplate(template: TemplateRecord | null) {
  const fields = sortByStepOrder(Array.isArray(template?.fields) ? template.fields : []);
  const initialData: Record<string, string> = {};
  const today = new Date();
  const commonValues = {
    dia_elaboracion: String(today.getDate()),
    mes_elaboracion: today.toLocaleDateString("es-CO", { month: "long" }),
    ano_elaboracion: String(today.getFullYear()),
  };

  for (const field of fields) {
    initialData[field.field_code] = "";
  }

  for (const [key, value] of Object.entries(commonValues)) {
    if (key in initialData) {
      initialData[key] = value;
    }
  }

  return initialData;
}

function parseTemplateFieldOptions(optionsJson: string | null | undefined): SelectOption[] {
  if (!optionsJson) {
    return [];
  }

  try {
    const parsed = JSON.parse(optionsJson);
    if (!Array.isArray(parsed)) {
      return [];
    }

    return parsed
      .map((item, index) => {
        if (typeof item === "string") {
          return { value: item, label: item };
        }
        if (item && typeof item === "object") {
          const rawValue = safeString((item as { value?: unknown; label?: unknown }).value);
          const rawLabel = safeString((item as { value?: unknown; label?: unknown }).label);
          const value = rawValue || rawLabel;
          const label = rawLabel || rawValue || `Opción ${index + 1}`;
          if (value || label) {
            return { value, label };
          }
        }
        return null;
      })
      .filter((item): item is SelectOption => Boolean(item?.value));
  } catch {
    return [];
  }
}

export function CreateCaseWizard() {
  const [step, setStep] = useState(0);
  const [templates, setTemplates] = useState<TemplateRecord[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<TemplateRecord | null>(null);
  const [escrituraType, setEscrituraType] = useState<string | null>(null);
  const [actWizardItems, setActWizardItems] = useState<ActWizardItem[]>([]);
  const [actCatalog, setActCatalog] = useState<ActCatalogItem[]>([]);
  const [dragIndex, setDragIndex] = useState<number | null>(null);
  const [notaries, setNotaries] = useState<SelectOption[]>([]);
  const [users, setUsers] = useState<UserOption[]>([]);
  const [caseDetail, setCaseDetail] = useState<DocumentFlowCase | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [canSelectNotary, setCanSelectNotary] = useState(true);
  const [showSubstituteNotary, setShowSubstituteNotary] = useState(false);
  const [expandedGeneralField, setExpandedGeneralField] = useState<string | null>(null);
  const [expandedParticipantItems, setExpandedParticipantItems] = useState<Record<string, boolean>>({});
  const [generalForm, setGeneralForm] = useState({
    notary_id: "",
    client_user_id: "",
    current_owner_user_id: "",
    protocolist_user_id: "",
    approver_user_id: "",
    titular_notary_user_id: "",
    substitute_notary_user_id: "",
    requires_client_review: true,
    metadata_json: JSON.stringify({ clase: "Poder General" }, null, 2),
  });
  const [participantItems, setParticipantItems] = useState<ParticipantItem[]>([]);
  const [actData, setActData] = useState<Record<string, string>>({});

  useEffect(() => {
    void load();
  }, []);

  useEffect(() => {
    setParticipantItems([]);
  }, [selectedTemplate]);

  useEffect(() => {
    setActData(buildActDataFromTemplate(selectedTemplate));
  }, [selectedTemplate]);

  function deriveParticipantsFromActs(acts: ActWizardItem[]): ParticipantItem[] {
    const seenRoles = new Set<string>();
    const derived: ParticipantItem[] = [];

    for (const act of acts) {
      for (const role of act.roles) {
        if (role === "compradores") continue;
        if (seenRoles.has(role)) continue;
        seenRoles.add(role);
        const mapping = ROLE_PARTICIPANT_MAP[role];
        if (!mapping) continue;
        derived.push({
          uid: crypto.randomUUID(),
          kind: mapping.kind,
          roleCode: mapping.roleCode,
          roleLabel: mapping.roleLabel,
          personId: null,
          person: null,
          legalEntityId: null,
          legalEntity: null,
          representative: null,
          representativeId: null,
          isComplete: false,
        });
      }
    }

    return derived;
  }

  async function load() {
    setIsLoading(true);
    setError(null);
    try {
      const [templateData, notaryData, userData, currentUser, catalogData] = await Promise.all([
        getActiveTemplates(),
        getNotaries(),
        getUserOptions(true),
        getCurrentUser(),
        getActCatalog(),
      ]);
      const safeTemplates = Array.isArray(templateData) ? templateData : [];
      const safeNotaries = Array.isArray(notaryData) ? notaryData : [];
      const safeUsers = Array.isArray(userData) ? userData : [];
      const notaryOptions = safeNotaries
        .map((item) => ({
          value: String(item.id ?? ""),
          label: [safeString(item.notary_label), safeString(item.municipality)].filter(Boolean).join(" · ") || "Notaría sin nombre",
        }))
        .filter((item) => item.value);
      const isSuperAdmin = Array.isArray(currentUser?.role_codes) && currentUser.role_codes.includes("super_admin");
      const defaultNotaryRaw = currentUser?.default_notary_id;
      const defaultNotaryId = String(defaultNotaryRaw ?? "");
      console.log("notary_id seteado:", String(defaultNotaryRaw ?? ""));

      setTemplates(safeTemplates);
      setSelectedTemplate(
        safeTemplates.find((item) => item.slug === "poder-general") ?? safeTemplates[0] ?? null,
      );
      setNotaries(notaryOptions);
      setActCatalog(Array.isArray(catalogData) ? catalogData : []);
      setCanSelectNotary(isSuperAdmin);
      setGeneralForm((current) => ({
        ...current,
        notary_id: !isSuperAdmin ? defaultNotaryId : current.notary_id,
        client_user_id: current.client_user_id,
        current_owner_user_id: "",
        protocolist_user_id: "",
        approver_user_id: "",
        titular_notary_user_id: "",
        substitute_notary_user_id: "",
      }));
      setUsers(safeUsers);
    } catch (loadError) {
      setTemplates([]);
      setSelectedTemplate(null);
      setNotaries([]);
      setUsers([]);
      setError(loadError instanceof Error ? loadError.message : "No fue posible cargar la base del wizard.");
    } finally {
      setIsLoading(false);
    }
  }

  const userOptions = useMemo(() => normalizeUserOptions(users), [users]);
  const templateRoles = useMemo(() => sortByStepOrder(Array.isArray(selectedTemplate?.required_roles) ? selectedTemplate.required_roles : []), [selectedTemplate]);
  const templateFields = useMemo(() => sortByStepOrder(Array.isArray(selectedTemplate?.fields) ? selectedTemplate.fields : []), [selectedTemplate]);
  const buyerParticipantItems = useMemo(() => participantItems.filter((item) => item.kind === "person"), [participantItems]);
  const entityParticipantItems = useMemo(() => participantItems.filter((item) => item.kind === "entity"), [participantItems]);
  const showAside = step >= 3;
  const generalManagerFields = useMemo<Array<{ key: "current_owner_user_id" | "protocolist_user_id" | "approver_user_id" | "titular_notary_user_id"; label: string; value: string }>>(() => [
    { key: "current_owner_user_id", label: "Responsable actual", value: generalForm.current_owner_user_id },
    { key: "protocolist_user_id", label: "Protocolista", value: generalForm.protocolist_user_id },
    { key: "approver_user_id", label: "Aprobador", value: generalForm.approver_user_id },
    { key: "titular_notary_user_id", label: "Notario titular", value: generalForm.titular_notary_user_id },
  ], [generalForm.current_owner_user_id, generalForm.protocolist_user_id, generalForm.approver_user_id, generalForm.titular_notary_user_id]);

  function updateGeneralManager(field: "current_owner_user_id" | "protocolist_user_id" | "approver_user_id" | "titular_notary_user_id", value: string) {
    setGeneralForm((current) => ({ ...current, [field]: value }));
    setExpandedGeneralField(null);
  }

  function toPersonPayload(person: PersonRecord | PersonPayload): PersonPayload {
    return {
      document_type: person.document_type || "CC",
      document_number: person.document_number || "",
      full_name: person.full_name || "",
      sex: person.sex || "",
      nationality: person.nationality || "",
      marital_status: person.marital_status || "",
      profession: person.profession || "",
      municipality: person.municipality || "",
      is_transient: Boolean(person.is_transient),
      phone: person.phone || "",
      address: person.address || "",
      email: person.email || "",
      metadata_json: person.metadata_json || "{}",
    };
  }

  function normalizeParticipantItems(items: ParticipantItem[]) {
    const buyers = items.filter((item) => item.kind === "person");
    const entities = items.filter((item) => item.kind === "entity");
    const renumberedBuyers = buyers.map((item, index) => ({
      ...item,
      roleCode: `comprador_${index + 1}`,
      roleLabel: `Comprador(a) ${index + 1}`,
      isComplete: Boolean(item.personId || item.person),
    }));
    return [...renumberedBuyers, ...entities.map((item) => ({
      ...item,
      isComplete: Boolean(item.legalEntityId && item.representativeId && item.legalEntity && item.representative),
    }))];
  }

  function makeBuyerItem(index: number): ParticipantItem {
    return {
      uid: crypto.randomUUID(),
      kind: "person",
      roleCode: `comprador_${index}`,
      roleLabel: `Comprador(a) ${index}`,
      personId: null,
      person: null,
      legalEntityId: null,
      legalEntity: null,
      representative: null,
      representativeId: null,
      isComplete: false,
    };
  }

  function makeEntityItem(): ParticipantItem {
    return {
      uid: crypto.randomUUID(),
      kind: "entity",
      roleCode: "apoderado_otro",
      roleLabel: entityRoleLabelMap.apoderado_otro,
      personId: null,
      person: null,
      legalEntityId: null,
      legalEntity: null,
      representative: null,
      representativeId: null,
      isComplete: false,
    };
  }

  function updateParticipantItem(uid: string, updater: (current: ParticipantItem) => ParticipantItem) {
    setParticipantItems((current) => normalizeParticipantItems(current.map((item) => (item.uid === uid ? updater(item) : item))));
  }

  function updateBuyerPerson(uid: string, person: PersonRecord | PersonPayload, personId: number | null) {
    updateParticipantItem(uid, (current) => {
      const nextPerson = toPersonPayload(person);
      return {
        ...current,
        personId,
        person: nextPerson,
        isComplete: true,
      };
    });
  }

  function updateBuyerNewPerson(uid: string, person: PersonPayload) {
    updateParticipantItem(uid, (current) => ({
      ...current,
      personId: null,
      person: toPersonPayload(person),
      isComplete: true,
    }));
  }

  function clearBuyer(uid: string) {
    updateParticipantItem(uid, (current) => ({
      ...current,
      personId: null,
      person: null,
      isComplete: false,
    }));
  }

  function updateEntityRole(uid: string, roleCode: string) {
    updateParticipantItem(uid, (current) => ({
      ...current,
      roleCode,
      roleLabel: entityRoleLabelMap[roleCode] || "Otra entidad",
    }));
  }

  function updateEntityLegal(uid: string, entity: LegalEntityRecord | LegalEntityPayload, entityId: number | null) {
    updateParticipantItem(uid, (current) => ({
      ...current,
      legalEntityId: entityId,
      legalEntity: {
        nit: entity.nit || "",
        name: entity.name || "",
        legal_representative: entity.legal_representative || "",
        municipality: entity.municipality || "",
        address: entity.address || "",
        phone: entity.phone || "",
        email: entity.email || "",
      },
      isComplete: computeEntityComplete({
        ...current,
        legalEntityId: entityId,
        legalEntity: {
          nit: entity.nit || "",
          name: entity.name || "",
          legal_representative: entity.legal_representative || "",
          municipality: entity.municipality || "",
          address: entity.address || "",
          phone: entity.phone || "",
          email: entity.email || "",
        },
      }),
    }));
  }

  function updateEntityRepresentative(uid: string, person: PersonRecord | PersonPayload, personId: number | null) {
    updateParticipantItem(uid, (current) => ({
      ...current,
      representativeId: personId,
      representative: person,
      isComplete: computeEntityComplete({
        ...current,
        representativeId: personId,
        representative: person,
      }),
    }));
  }

  function clearEntityLegal(uid: string) {
    updateParticipantItem(uid, (current) => ({
      ...current,
      legalEntityId: null,
      legalEntity: null,
      isComplete: false,
    }));
  }

  function clearEntityRepresentative(uid: string) {
    updateParticipantItem(uid, (current) => ({
      ...current,
      representativeId: null,
      representative: null,
      isComplete: false,
    }));
  }

  function addBuyer() {
    const nextItem = makeBuyerItem(participantItems.filter((item) => item.kind === "person").length + 1);
    setParticipantItems((current) => normalizeParticipantItems([...current, nextItem]));
    setExpandedParticipantItems((current) => ({ ...current, [nextItem.uid]: true }));
  }

  function addEntity() {
    const nextItem = makeEntityItem();
    setParticipantItems((current) => normalizeParticipantItems([...current, nextItem]));
    setExpandedParticipantItems((current) => ({ ...current, [nextItem.uid]: true }));
  }

  function removeParticipant(uid: string) {
    setParticipantItems((current) => normalizeParticipantItems(current.filter((item) => item.uid !== uid)));
    setExpandedParticipantItems((current) => {
      const next = { ...current };
      delete next[uid];
      return next;
    });
  }

  function validateParticipants() {
    const buyers = participantItems.filter((item) => item.kind === "person");
    const entities = participantItems.filter((item) => item.kind === "entity");
    if (!buyers.some((item) => item.isComplete && (item.personId !== null || item.person !== null))) {
      return "Debes agregar al menos 1 comprador completo.";
    }
    for (const entity of entities) {
      const entityReady = hasEntitySelection(entity) && hasRepresentativeSelection(entity);
      if (!entityReady) {
        return "Cada entidad agregada debe tener entidad y apoderado completos.";
      }
    }
    return null;
  }

  async function handleCreateCase() {
    if (!selectedTemplate || !generalForm.notary_id) {
      throw new Error("Debes seleccionar la notaría y la plantilla para crear la minuta.");
    }
    const created = await createDocumentCase({
      template_id: selectedTemplate.id,
      notary_id: Number(generalForm.notary_id),
      client_user_id: generalForm.client_user_id ? Number(generalForm.client_user_id) : null,
      current_owner_user_id: generalForm.current_owner_user_id ? Number(generalForm.current_owner_user_id) : null,
      protocolist_user_id: generalForm.protocolist_user_id ? Number(generalForm.protocolist_user_id) : null,
      approver_user_id: generalForm.approver_user_id ? Number(generalForm.approver_user_id) : null,
      titular_notary_user_id: generalForm.titular_notary_user_id ? Number(generalForm.titular_notary_user_id) : null,
      substitute_notary_user_id: generalForm.substitute_notary_user_id ? Number(generalForm.substitute_notary_user_id) : null,
      requires_client_review: generalForm.requires_client_review,
      metadata_json: generalForm.metadata_json,
    });
    setCaseDetail(created);
    return created;
  }

  async function continueStep() {
    setError(null);
    setFeedback(null);
    setIsSaving(true);
    try {
      let activeCase = caseDetail;
      if (step === 0) {
        if (!escrituraType || actWizardItems.length === 0) {
          throw new Error("Selecciona el tipo de escritura y confirma los actos antes de continuar.");
        }
        if (!selectedTemplate) {
          throw new Error("No hay plantilla base disponible. Contacta al administrador.");
        }
        const derived = deriveParticipantsFromActs(actWizardItems);
        setParticipantItems(derived);
      }
      if (step === 1 && !activeCase) {
        activeCase = await handleCreateCase();
      }
      if (step === 1 && activeCase) {
  const actsPayload = actWizardItems.map((a, idx) => ({
    code: a.code,
    label: a.label,
    act_order: idx + 1,
    roles_json: Array.isArray(a.roles) ? JSON.stringify(a.roles) : (a.roles ?? "[]"),
  }));
        await saveCaseActs(activeCase.id, actsPayload);
      }
      if (step === 2 && activeCase) {
        const participantError = validateParticipants();
        if (participantError) {
          throw new Error(participantError);
        }
        const payload = participantItems.map((item) =>
          item.kind === "person"
            ? {
                role_code: item.roleCode,
                role_label: item.roleLabel,
                person_id: item.personId,
                person: item.person,
              }
            : {
                role_code: item.roleCode,
                role_label: item.roleLabel,
                person_id: item.representativeId,
                person: item.representative,
                legal_entity_id: item.legalEntityId,
                legal_entity: item.legalEntity,
              },
        );
        const updated = await saveCaseParticipants(
          activeCase.id,
          payload as any,
        );
        setCaseDetail(updated);
      }
      if (step === 3 && activeCase) {
        const missingRequiredField = templateFields.find((field) => field.is_required && !(actData[field.field_code] ?? "").trim());
        if (missingRequiredField) {
          throw new Error(`Completa el campo obligatorio ${missingRequiredField.label || missingRequiredField.field_code}.`);
        }
        const updated = await saveCaseActData(activeCase.id, { data_json: JSON.stringify(actData) });
        setCaseDetail(updated);
      }
      if (step === 4 && caseDetail) {
        const updated = await generateCaseDraft(caseDetail.id, "Generado con Gari desde el wizard.");
        setCaseDetail(updated);
        window.location.href = `/dashboard/casos/${caseDetail.id}?tab=documento-gari`;
        return;
      }
      setStep((current) => Math.min(current + 1, steps.length - 1));
    } catch (stepError) {
      setError(stepError instanceof Error ? stepError.message : "No fue posible avanzar en el wizard.");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <div className="space-y-6">
      <section className="ep-card z-0 rounded-[2rem] p-6">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.22em] text-accent">
              {caseDetail?.internal_case_number ? `Crear Minuta · ${caseDetail.internal_case_number}` : "Crear Minuta"}
            </p>
          </div>
          {caseDetail ? (
            <Link href={`/dashboard/casos/${caseDetail.id}`} className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white">
              Abrir detalle de la minuta <ArrowRight className="h-4 w-4" />
            </Link>
          ) : null}
        </div>
      </section>

      <section className="ep-card z-0 rounded-[2rem] p-6">
        <div className="grid gap-3 xl:grid-cols-5">
          {steps.map((item, index) => (
            <div key={item} className={`rounded-[1.35rem] border px-4 py-4 ${index === step ? "border-primary/30 bg-primary text-white" : index < step ? "border-emerald-500/20 bg-emerald-500/10" : "border-[var(--line)] bg-[var(--panel-soft)]"}`}>
              <div className="flex items-center gap-3">
                <div className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-semibold ${index === step ? "bg-white/15 text-white" : index < step ? "bg-emerald-500/20 text-primary" : "bg-[var(--panel)] text-primary"}`}>
                  {index < step ? <CheckCircle2 className="h-4 w-4" /> : index + 1}
                </div>
                <p className={`text-sm font-semibold ${index === step ? "text-white" : "text-primary"}`}>{item}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className={`grid gap-6 ${showAside ? "xl:grid-cols-[minmax(0,1.2fr)_360px]" : "xl:grid-cols-1"}`}>
        <div className="ep-card z-0 rounded-[2rem] p-6 space-y-6">
          {isLoading ? <div className="ep-card-muted z-0 rounded-[1.5rem] px-4 py-6 text-sm text-secondary">Cargando plantillas, notarías y usuarios...</div> : null}
          {!isLoading && error && templates.length === 0 ? <div className="ep-kpi-critical z-0 rounded-2xl px-4 py-3 text-sm">{error}</div> : null}
          {!isLoading && !error && templates.length === 0 ? <div className="ep-card-muted z-0 rounded-[1.5rem] px-4 py-6 text-sm text-secondary">No hay plantillas activas todavía.</div> : null}

          {!isLoading && templates.length > 0 ? (
            <>
              {step === 0 ? (
                <div className="space-y-6">
                  {!escrituraType ? (
                    <div className="space-y-5">
                      <div>
                        <h2 className="text-2xl font-semibold text-primary">1. Tipo de escritura</h2>
                        <p className="mt-1 text-sm text-secondary">Selecciona la operación que vas a escriturar.</p>
                      </div>
                      <div className="grid gap-4 lg:grid-cols-2">
                        {ESCRITURA_TYPES.map((tipo) => (
                          <button
                            key={tipo.code}
                            type="button"
                            onClick={() => {
                              setEscrituraType(tipo.code);
                              const matched = tipo.defaultActs.map((actCode) => {
                                const found = actCatalog.find((a) => a.code === actCode);
                                if (!found) return null;
                                return {
                                  uid: crypto.randomUUID(),
                                  code: found.code,
                                  label: found.label,
                                  roles: JSON.parse(found.roles_json || "[]"),
                                } as ActWizardItem;
                              }).filter(Boolean) as ActWizardItem[];
                              setActWizardItems(matched);
                              const tmpl = templates.find((t) => t.slug === tipo.templateSlug) ?? templates[0] ?? null;
                              setSelectedTemplate(tmpl);
                            }}
                            className="rounded-[1.5rem] border p-5 text-left hover:border-primary/30 hover:bg-primary/5 transition-colors border-[var(--line)]"
                          >
                            <p className="text-lg font-semibold text-primary">{tipo.label}</p>
                            <p className="mt-2 text-sm text-secondary">{tipo.description}</p>
                            <p className="mt-3 text-xs text-secondary">{tipo.defaultActs.length} acto{tipo.defaultActs.length !== 1 ? "s" : ""} sugeridos</p>
                          </button>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-5">
                      <div className="flex items-center justify-between gap-3">
                        <div>
                          <h2 className="text-2xl font-semibold text-primary">1. Actos de la escritura</h2>
                          <p className="mt-1 text-sm text-secondary">
                            {ESCRITURA_TYPES.find((t) => t.code === escrituraType)?.label} · Reordena arrastrando, quita o agrega actos según el caso.
                          </p>
                        </div>
                        <button
                          type="button"
                          onClick={() => { setEscrituraType(null); setActWizardItems([]); }}
                          className="text-sm font-semibold text-primary underline"
                        >
                          Cambiar tipo
                        </button>
                      </div>

                      <div className="space-y-2">
                        {actWizardItems.map((act, index) => (
                          <div
                            key={act.uid}
                            draggable
                            onDragStart={() => setDragIndex(index)}
                            onDragOver={(e) => e.preventDefault()}
                            onDrop={() => {
                              if (dragIndex === null || dragIndex === index) return;
                              const reordered = [...actWizardItems];
                              const [moved] = reordered.splice(dragIndex, 1);
                              reordered.splice(index, 0, moved);
                              setActWizardItems(reordered);
                              setDragIndex(null);
                            }}
                            onDragEnd={() => setDragIndex(null)}
                            className={`flex items-center gap-3 rounded-[1.4rem] border bg-[var(--panel)] px-4 py-3 cursor-grab active:cursor-grabbing transition-opacity ${dragIndex === index ? "opacity-40" : "opacity-100"} border-[var(--line)]`}
                          >
                            <span className="text-secondary select-none text-lg leading-none"></span>
                            <span className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-primary/10 text-xs font-bold text-primary">
                              {index + 1}
                            </span>
                            <span className="flex-1 text-sm font-medium text-primary">{act.label}</span>
                            <button
                              type="button"
                              onClick={() => setActWizardItems((prev) => prev.filter((a) => a.uid !== act.uid))}
                              className="text-rose-500 text-xs font-semibold px-3 py-1 rounded-xl hover:bg-rose-50 transition-colors"
                            >
                              Quitar
                            </button>
                          </div>
                        ))}
                      </div>

                      {actCatalog.filter((a) => !actWizardItems.some((item) => item.code === a.code)).length > 0 ? (
                        <div className="space-y-3">
                          <p className="text-sm font-semibold text-primary">+ Agregar acto</p>
                          <div className="grid gap-2 lg:grid-cols-2">
                            {actCatalog
                              .filter((a) => !actWizardItems.some((item) => item.code === a.code))
                              .map((a) => (
                                <button
                                  key={a.code}
                                  type="button"
                                  onClick={() =>
                                    setActWizardItems((prev) => [
                                      ...prev,
                                      {
                                        uid: crypto.randomUUID(),
                                        code: a.code,
                                        label: a.label,
                                        roles: JSON.parse(a.roles_json || "[]"),
                                      },
                                    ])
                                  }
                                  className="rounded-[1.2rem] border border-dashed border-[var(--line)] px-4 py-2 text-left text-sm text-secondary hover:border-primary/30 hover:text-primary transition-colors"
                                >
                                  + {a.label}
                                </button>
                              ))}
                          </div>
                        </div>
                      ) : null}

                      {actWizardItems.length === 0 ? (
                        <div className="ep-card-muted rounded-[1.5rem] px-4 py-5 text-sm text-secondary">
                          Agrega al menos un acto para continuar.
                        </div>
                      ) : null}
                    </div>
                  )}
                </div>
              ) : null}

              {step === 1 ? (
                <div className="space-y-5">
                  <h2 className="text-2xl font-semibold text-primary">2. Datos generales de la minuta</h2>
                  <div className="grid gap-4">
                    {canSelectNotary ? (
                      <SearchableSelect label="Notaría" value={generalForm.notary_id} options={notaries} onChange={(value) => setGeneralForm((current) => ({ ...current, notary_id: value }))} />
                    ) : null}
                    {generalManagerFields.map((field) => {
                      const isExpanded = expandedGeneralField === field.key;
                      const selectedLabel = userOptions.find((item) => item.value === field.value)?.label || "Sin asignar";
                      return (
                        <div key={field.key} className="ep-card-soft z-0 rounded-[1.6rem] p-4 space-y-3" style={{ position: "relative", zIndex: "auto" }}>
                          <button
                            type="button"
                            onClick={() => setExpandedGeneralField((current) => (current === field.key ? null : field.key))}
                            className="flex w-full items-center justify-between gap-3 rounded-[1.1rem] px-4 py-3 text-left"
                          >
                            <span className="text-sm font-medium text-primary">{field.label}</span>
                            <span className="text-sm font-medium text-secondary">{selectedLabel}</span>
                          </button>
                          {isExpanded ? (
                            <SearchableSelect
                              label={field.label}
                              value={field.value}
                              options={userOptions}
                              onChange={(value) => updateGeneralManager(field.key, value)}
                            />
                          ) : null}
                        </div>
                      );
                    })}
                    {showSubstituteNotary ? (
                      <div className="space-y-3">
                        <SearchableSelect label="Notario suplente" value={generalForm.substitute_notary_user_id} options={userOptions} onChange={(value) => setGeneralForm((current) => ({ ...current, substitute_notary_user_id: value }))} />
                        <button
                          type="button"
                          onClick={() => setShowSubstituteNotary(false)}
                          className="inline-flex items-center gap-2 text-sm font-semibold text-primary"
                        >
                          - Ocultar notario suplente
                        </button>
                      </div>
                    ) : (
                      <button
                        type="button"
                        onClick={() => setShowSubstituteNotary(true)}
                        className="inline-flex items-center gap-2 text-sm font-semibold text-primary"
                      >
                        + Agregar notario suplente
                      </button>
                    )}
                  </div>
                  <label className="ep-card-muted flex items-center gap-3 rounded-2xl px-4 py-3 text-sm text-secondary">
                    <input type="checkbox" checked={generalForm.requires_client_review} onChange={(event) => setGeneralForm((current) => ({ ...current, requires_client_review: event.target.checked }))} />
                    Requiere revisión cliente
                  </label>
                </div>
              ) : null}

              {step === 2 ? (
                <div className="space-y-6">
                  <h2 className="text-2xl font-semibold text-primary">3. Intervinientes</h2>
                  <p className="mt-1 text-sm text-secondary">
                    El sistema identificó los intervinientes requeridos según los actos seleccionados. Completa cada uno y agrega los compradores.
                  </p>

                  <section className="space-y-4">
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <h3 className="text-xl font-semibold text-primary">Compradores</h3>
                        <p className="text-sm text-secondary">Agrega una o varias personas naturales compradoras.</p>
                      </div>
                      <button
                        type="button"
                        onClick={addBuyer}
                        className="inline-flex items-center gap-2 rounded-2xl bg-primary px-4 py-2 text-sm font-semibold text-white"
                      >
                        + Agregar comprador
                      </button>
                    </div>

                    <div className="space-y-4">
                      {buyerParticipantItems.length > 0 ? buyerParticipantItems.map((item) => {
                        const isExpanded = Boolean(expandedParticipantItems[item.uid]);
                        const displayPerson = item.personId !== null || item.person ? item.person : null;
                        return (
                          <div key={item.uid} className="ep-card-soft rounded-[1.8rem] p-5 space-y-4">
                            <button
                              type="button"
                              onClick={() => setExpandedParticipantItems((current) => ({ ...current, [item.uid]: !current[item.uid] }))}
                              className="flex w-full min-h-12 items-center justify-between gap-3 rounded-[1.25rem] px-4 py-3 text-left"
                            >
                              <div className="space-y-1">
                                <p className="text-sm font-medium text-primary">{item.roleLabel}</p>
                                <h3 className="text-sm font-medium text-secondary">Comprador natural</h3>
                              </div>
                              <span className={`ep-pill rounded-full px-3 py-1 text-xs font-semibold ${item.isComplete ? "bg-emerald-500/10 text-emerald-700" : "text-secondary"}`}>
                                {item.isComplete ? "Completo" : "Incompleto"}
                              </span>
                            </button>
                            {isExpanded ? (
                              <div className="space-y-4">
                                {item.isComplete && displayPerson ? (
                                  <div className="rounded-[1.35rem] border border-emerald-500/20 bg-emerald-500/10 p-4">
                                    <div className="flex items-start justify-between gap-3">
                                      <div>
                                        <p className="text-sm font-semibold text-primary">{displayPerson.full_name || "Comprador asignado"}</p>
                                        <p className="mt-1 text-sm text-secondary">
                                          {displayPerson.document_type || "DOC"} {displayPerson.document_number || "Sin número"} · {displayPerson.municipality || "Sin municipio"}
                                        </p>
                                      </div>
                                      <CheckCircle2 className="mt-0.5 h-5 w-5 text-emerald-600" />
                                    </div>
                                    <div className="mt-4 flex flex-wrap items-center gap-3">
                                      <button
                                        type="button"
                                        onClick={() => clearBuyer(item.uid)}
                                        className="inline-flex items-center gap-2 text-sm font-semibold text-primary"
                                      >
                                        Cambiar
                                      </button>
                                      <button
                                        type="button"
                                        onClick={() => removeParticipant(item.uid)}
                                        className="inline-flex items-center gap-2 text-sm font-semibold text-rose-600"
                                      >
                                        Eliminar
                                      </button>
                                    </div>
                                  </div>
                                ) : (
                                  <PersonLookup
                                    onPick={(selected) => updateBuyerPerson(item.uid, selected, selected.id)}
                                    onNotFound={(person) => updateBuyerNewPerson(item.uid, person)}
                                  />
                                )}
                              </div>
                            ) : null}
                          </div>
                        );
                      }) : (
                        <div className="ep-card-muted rounded-[1.5rem] px-4 py-5 text-sm text-secondary">
                          Todavía no hay compradores agregados.
                        </div>
                      )}
                    </div>
                  </section>

                  <section className="space-y-4">
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <h3 className="text-xl font-semibold text-primary">Entidades y apoderados</h3>
                        <p className="text-sm text-secondary">Agrega bancos, fiducias o constructoras con su apoderado.</p>
                      </div>
                      <button
                        type="button"
                        onClick={addEntity}
                        className="inline-flex items-center gap-2 rounded-2xl bg-primary px-4 py-2 text-sm font-semibold text-white"
                      >
                        + Agregar entidad
                      </button>
                    </div>

                    <div className="space-y-4">
                      {entityParticipantItems.length > 0 ? entityParticipantItems.map((item) => {
                        const isExpanded = Boolean(expandedParticipantItems[item.uid]);
                        const entitySummary = item.legalEntity;
                        const representativeSummary = item.representative;
                        return (
                          <div key={item.uid} className="ep-card-soft rounded-[1.8rem] p-5 space-y-4">
                            <button
                              type="button"
                              onClick={() => setExpandedParticipantItems((current) => ({ ...current, [item.uid]: !current[item.uid] }))}
                              className="flex w-full min-h-12 items-center justify-between gap-3 rounded-[1.25rem] px-4 py-3 text-left"
                            >
                              <div className="space-y-1">
                                <p className="text-sm font-medium text-primary">{item.roleLabel}</p>
                                <h3 className="text-sm font-medium text-secondary">Entidad y apoderado</h3>
                              </div>
                              <span className={`ep-pill rounded-full px-3 py-1 text-xs font-semibold ${item.isComplete ? "bg-emerald-500/10 text-emerald-700" : "text-secondary"}`}>
                                {item.isComplete ? "Completo" : "Incompleto"}
                              </span>
                            </button>

                            {isExpanded ? (
                              <div className="space-y-4">
                                <div className="space-y-3 rounded-[1.4rem] border border-[var(--line)] bg-[var(--panel-soft)] p-4">
                                  <div className="flex items-center justify-between gap-3">
                                    <p className="text-sm font-semibold text-primary">Rol de la entidad</p>
                                  </div>
                                  <label className="grid gap-2 text-sm font-medium text-primary">
                                    <span>Rol</span>
                                    <select
                                      value={item.roleCode}
                                      onChange={(event) => updateEntityRole(item.uid, event.target.value)}
                                      className="ep-select h-11 rounded-2xl px-4"
                                    >
                                      {entityRoleOptions.map((option) => (
                                        <option key={option.value} value={option.value}>
                                          {option.label}
                                        </option>
                                      ))}
                                    </select>
                                  </label>
                                </div>

                                <div className="space-y-3 rounded-[1.4rem] border border-[var(--line)] bg-[var(--panel-soft)] p-4">
                                  <div className="flex items-center justify-between gap-3">
                                    <p className="text-sm font-semibold text-primary">Entidad</p>
                                    {item.legalEntity && item.legalEntityId ? (
                                      <span className="ep-pill rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-700">Completo</span>
                                    ) : null}
                                  </div>
                                {hasEntitySelection(item) ? (
                                  <div className="rounded-[1.35rem] border border-emerald-500/20 bg-emerald-500/10 p-4">
                                    <div className="flex items-start justify-between gap-3">
                                      <div>
                                        <p className="text-sm font-semibold text-primary">{entitySummary?.name || "Entidad asignada"}</p>
                                          <p className="mt-1 text-sm text-secondary">
                                            {entitySummary?.nit || "Sin NIT"}{entitySummary?.municipality ? ` · ${entitySummary.municipality}` : ""}
                                          </p>
                                        </div>
                                        <CheckCircle2 className="mt-0.5 h-5 w-5 text-emerald-600" />
                                      </div>
                                      <button
                                        type="button"
                                        onClick={() => clearEntityLegal(item.uid)}
                                        className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-primary"
                                      >
                                        Cambiar
                                      </button>
                                    </div>
                                  ) : (
                                    <LegalEntityLookup
                                      onPick={(entity) => updateEntityLegal(item.uid, entity, entity.id)}
                                      onNotFound={(entity) => updateEntityLegal(item.uid, entity, null)}
                                    />
                                  )}
                                </div>

                                {hasEntitySelection(item) ? (
                                  <div className="space-y-3 rounded-[1.4rem] border border-[var(--line)] bg-[var(--panel-soft)] p-4">
                                    <div className="flex items-center justify-between gap-3">
                                      <p className="text-sm font-semibold text-primary">Apoderado</p>
                                      {hasRepresentativeSelection(item) ? (
                                        <span className="ep-pill rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-700">Completo</span>
                                      ) : null}
                                    </div>
                                    {hasRepresentativeSelection(item) ? (
                                      <div className="rounded-[1.35rem] border border-emerald-500/20 bg-emerald-500/10 p-4">
                                        <div className="flex items-start justify-between gap-3">
                                          <div>
                                            <p className="text-sm font-semibold text-primary">{representativeSummary?.full_name || "Apoderado asignado"}</p>
                                            <p className="mt-1 text-sm text-secondary">
                                              {representativeSummary?.document_type || "DOC"} {representativeSummary?.document_number || "Sin número"} · {representativeSummary?.municipality || "Sin municipio"}
                                            </p>
                                          </div>
                                          <CheckCircle2 className="mt-0.5 h-5 w-5 text-emerald-600" />
                                        </div>
                                        <button
                                          type="button"
                                          onClick={() => clearEntityRepresentative(item.uid)}
                                          className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-primary"
                                        >
                                          Cambiar
                                        </button>
                                      </div>
                                    ) : (
                                      <PersonLookup
                                        onPick={(selected) => updateEntityRepresentative(item.uid, selected, selected.id)}
                                        onNotFound={(person) => updateEntityRepresentative(item.uid, person, null)}
                                      />
                                    )}
                                  </div>
                                ) : null}

                                <button
                                  type="button"
                                  onClick={() => removeParticipant(item.uid)}
                                  className="inline-flex items-center gap-2 text-sm font-semibold text-rose-600"
                                >
                                  Eliminar
                                </button>
                              </div>
                            ) : null}
                          </div>
                        );
                      }) : (
                        <div className="ep-card-muted rounded-[1.5rem] px-4 py-5 text-sm text-secondary">
                          Todavía no hay entidades agregadas.
                        </div>
                      )}
                    </div>
                  </section>
                </div>
              ) : null}

              {step === 3 ? (
                <div className="space-y-5">
                  <h2 className="text-2xl font-semibold text-primary">4. Datos del acto</h2>
                  {templateFields.length > 0 ? (
                    <div className="grid grid-cols-1 gap-4">
                      {templateFields.map((field) => {
                        const label = `${field.label || field.field_code}${field.is_required ? " *" : ""}`;
                        const value = actData[field.field_code] ?? "";

                        if (field.field_type === "select") {
                          return (
                            <div key={field.field_code} className="w-full">
                              <SearchableSelect
                                label={label}
                                value={value}
                                options={parseTemplateFieldOptions(field.options_json)}
                                onChange={(nextValue) => setActData((current) => ({ ...current, [field.field_code]: nextValue }))}
                              />
                            </div>
                          );
                        }

                        if (field.field_type === "textarea") {
                          return (
                            <label key={field.field_code} className="grid gap-2 text-sm font-medium text-primary">
                              <span>{label}</span>
                              <textarea
                                value={value}
                                onChange={(event) => setActData((current) => ({ ...current, [field.field_code]: event.target.value }))}
                                placeholder={field.placeholder_key || ""}
                                className="ep-input rounded-2xl px-4 py-3 w-full"
                              />
                            </label>
                          );
                        }

                        if (field.field_type === "date") {
                          return (
                            <label key={field.field_code} className="grid gap-2 text-sm font-medium text-primary">
                              <span>{label}</span>
                              <input
                                type="date"
                                value={value}
                                onChange={(event) => setActData((current) => ({ ...current, [field.field_code]: event.target.value }))}
                                className="ep-input h-12 rounded-2xl px-4"
                              />
                            </label>
                          );
                        }

                        if (field.field_type === "currency") {
                          return (
                            <label key={field.field_code} className="grid gap-2 text-sm font-medium text-primary">
                              <span>{label}</span>
                              <div className="relative">
                                <span className="pointer-events-none absolute inset-y-0 left-4 flex items-center text-sm text-secondary">$</span>
                                <input
                                  type="number"
                                  value={value}
                                  onChange={(event) => setActData((current) => ({ ...current, [field.field_code]: event.target.value }))}
                                  placeholder={field.placeholder_key || ""}
                                  className="ep-input h-12 rounded-2xl px-4 pl-8"
                                />
                              </div>
                            </label>
                          );
                        }

                        if (field.field_type === "number") {
                          return (
                            <ValidatedInput
                              key={field.field_code}
                              label={label}
                              type="number"
                              value={value}
                              placeholder={field.placeholder_key || ""}
                              onChange={(nextValue) => setActData((current) => ({ ...current, [field.field_code]: nextValue }))}
                            />
                          );
                        }

                        return (
                          <ValidatedInput
                            key={field.field_code}
                            label={label}
                            value={value}
                            placeholder={field.placeholder_key || ""}
                            onChange={(nextValue) => setActData((current) => ({ ...current, [field.field_code]: nextValue }))}
                          />
                        );
                      })}
                    </div>
                  ) : (
                    <div className="ep-card-muted z-0 rounded-[1.5rem] px-4 py-6 text-sm text-secondary">La plantilla seleccionada no tiene campos configurados.</div>
                  )}
                </div>
              ) : null}

              {step === 4 ? (
                <div className="space-y-5">
                  <h2 className="text-2xl font-semibold text-primary">5. Revisión</h2>
                  <div className="ep-card-soft rounded-[1.5rem] p-5 space-y-3">
                    <p className="text-sm font-semibold text-primary">Tipo de escritura</p>
                    <p className="text-sm text-secondary">
                      {ESCRITURA_TYPES.find((t) => t.code === escrituraType)?.label ?? "Sin definir"}
                    </p>
                    <p className="mt-3 text-sm font-semibold text-primary">Actos confirmados</p>
                    <div className="space-y-1">
                      {actWizardItems.map((a, i) => (
                        <p key={a.uid} className="text-sm text-secondary">{i + 1}. {a.label}</p>
                      ))}
                    </div>
                    <p className="mt-3 text-sm font-semibold text-primary">Número interno</p>
                    <p className="text-sm text-secondary">{caseDetail?.internal_case_number ?? ""}</p>
                  </div>
                  <div className="ep-card-muted rounded-[1.5rem] px-4 py-4 text-sm text-secondary">
                    Todo listo. Al continuar, el sistema generará la escritura con Gari y podrás previsualizarla, descargarla o regenerarla.
                  </div>
                </div>
              ) : null}
            </>
          ) : null}

          {error && !(isLoading && templates.length === 0) ? <div className="ep-kpi-critical rounded-2xl px-4 py-3 text-sm">{error}</div> : null}
          {feedback ? <div className="ep-kpi-success rounded-2xl px-4 py-3 text-sm">{feedback}</div> : null}
          {!isLoading && templates.length > 0 && step < 4 ? (
            <button type="button" onClick={() => void continueStep()} disabled={isSaving} className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white disabled:opacity-60">
              Continuar <ArrowRight className="h-4 w-4" />
            </button>
          ) : null}
          {!isLoading && templates.length > 0 && step === 4 ? (
            <button type="button" onClick={() => void continueStep()} disabled={isSaving} className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white disabled:opacity-60">
              Generar con Gari <ArrowRight className="h-4 w-4" />
            </button>
          ) : null}
        </div>

        {showAside ? (
          <aside className="space-y-4">
            <div className="ep-card z-0 rounded-[1.8rem] p-5">
              <p className="text-xs uppercase tracking-[0.2em] text-secondary">Minuta activa</p>
              <p className="mt-2 text-lg font-semibold text-primary">{caseDetail?.internal_case_number || "Aún no creado"}</p>
              <p className="mt-3 text-sm text-secondary">Plantilla: {selectedTemplate?.name || "Sin selección"}</p>
              <p className="mt-2 text-sm text-secondary">Estado: {caseDetail?.current_state || "borrador"}</p>
              <p className="mt-2 text-sm text-secondary">Escritura oficial: {caseDetail?.official_deed_number || "Pendiente de aprobación"}</p>
            </div>
            <div className="ep-card z-0 rounded-[1.8rem] p-5">
              <p className="text-xs uppercase tracking-[0.2em] text-secondary">Reglas funcionales</p>
              <ul className="mt-3 space-y-2 text-sm leading-6 text-secondary">
                <li>La plantilla define el trámite.</li>
                <li>El número oficial no se asigna al crear.</li>
                <li>Poderdante y apoderado son obligatorios.</li>
                <li>Las personas se reutilizan por tipo y número.</li>
              </ul>
            </div>
          </aside>
        ) : null}
      </section>
    </div>
  );
}
```

## File: components/marketing/landing-page.tsx
```typescript
"use client";

import Link from "next/link";
import Image from "next/image";
import { useState } from "react";
import {
  ArrowRight,
  Building2,
  CheckCircle2,
  FileStack,
  Layers3,
  Mail,
  Play,
  Plus,
  Phone,
  ShieldCheck,
  Sparkles,
  Workflow,
  X,
  XCircle,
} from "lucide-react";
import { defaultBranding } from "@/lib/branding";
import { LogoBadge } from "@/components/ui/logo-badge";

const beforeItems = [
  "Plantillas Word con etiquetas manuales",
  "Errores de digitación sin validación",
  "Sin trazabilidad ni historial",
  "Proceso lento minuta a minuta",
  "Sin control de calidad interno",
];

const afterItems = [
  "Formulario guiado por tipo de acto",
  "Validación automática de campos",
  "Flujo protocolista - revisor - aprobador - notario",
  "Generación del documento en segundos",
  "Historial completo por minuta e interviniente",
];

const features = [
  {
    title: "Multinotaría nativa",
    description: "Cada notaría con su branding, usuarios y datos completamente separados.",
    icon: Layers3,
  },
  {
    title: "Flujo de aprobación",
    description: "Protocolista - Revisor - Aprobador - Firma del notario. Trazable en cada paso.",
    icon: Workflow,
  },
  {
    title: "Actos masivos en lote",
    description: "Procese cientos de escrituras similares en un solo flujo automatizado.",
    icon: FileStack,
  },
  {
    title: "Motor documental dinámico",
    description: "Sin etiquetas manuales. El sistema construye el documento con los datos ingresados.",
    icon: Sparkles,
  },
  {
    title: "Trazabilidad completa",
    description: "Historial por minuta, interviniente y acto. Auditable en cualquier momento.",
    icon: ShieldCheck,
  },
  {
    title: "Personalizado por notaría",
    description: "Colores, logo, imagen de acceso y nombre comercial propios por sede.",
    icon: Building2,
  },
];

const faqs = [
  {
    question: "¿Necesito modificar mis plantillas Word actuales?",
    answer:
      "No. EasyPro genera los documentos a partir de los datos que ingresa el protocolista. Sus plantillas Word son el punto de partida, no el centro del proceso.",
  },
  {
    question: "¿Cuánto tiempo toma implementar EasyPro en mi notaría?",
    answer:
      "La configuración inicial toma menos de un día. En 24 horas su equipo puede estar operando la primera minuta real.",
  },
  {
    question: "¿Funciona para múltiples notarías?",
    answer:
      "Sí. EasyPro está diseñado para operar varias notarías desde una sola plataforma, con datos completamente separados entre sí.",
  },
  {
    question: "¿Qué pasa con las minutas que ya tenemos en proceso?",
    answer:
      "Las minutas anteriores pueden migrarse o continuar en el sistema anterior. EasyPro inicia con minutas nuevas y crece con su operación.",
  },
  {
    question: "¿Es seguro?",
    answer:
      "Sí. HTTPS en todos los accesos, autenticación con JWT, datos separados por notaría y backups automáticos diarios en Supabase.",
  },
];

const identityChips = ["Colores propios", "URL propia", "Imagen propia"];

const successCases = [
  {
    initials: "NC",
    status: "Live desde Abr 2026",
    title: "Notaría Única del Círculo de Caldas",
    subtitle: "Caldas, Antioquia  Colombia",
    description:
      "La primera notaría en operar en vivo con EasyPro, consolidando el flujo completo de atención, validación y generación documental en producción.",
    tags: ["Poder General", "Venta sin RPH", "Salida del País"],
    href: "https://wa.me/573107932844",
    cta: "Contactar como referencia",
    videoUrl: "https://www.youtube.com/embed/TODO_CALDAS",
    live: true,
  },
  {
    initials: "NB",
    status: "Demo disponible",
    title: "Notaría Primera del Círculo de Bello",
    subtitle: "Bello, Antioquia  Colombia",
    description:
      "Notaría piloto de referencia con acceso a demo guiada para validar el flujo, resolver dudas y revisar minutas reales antes de salir a producción.",
    tags: ["Entorno de demo", "Minutas reales", "Acceso guiado"],
    href: "https://wa.me/573107932844",
    cta: "Solicitar demo",
    videoUrl: "https://www.youtube.com/embed/TODO_BELLO",
    live: false,
  },
];

export function LandingPage() {
  const [openFaq, setOpenFaq] = useState<number | null>(0);
  const [newsletterEmail, setNewsletterEmail] = useState("");
  const [newsletterAccepted, setNewsletterAccepted] = useState(false);
  const [videoModal, setVideoModal] = useState<{ open: boolean; url: string; title: string }>({
    open: false,
    url: "",
    title: "",
  });

  return (
    <main className="min-h-screen bg-[#0D1B2A] font-sans text-white">
      <header className="sticky top-0 z-50 border-b border-[#1A3350] bg-[#0D1B2A]">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex min-w-0 items-center gap-3 sm:gap-4">
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-[#00E5A0] text-sm font-black text-black shadow-sm">
              EP
            </div>
            <span className="sr-only">
              <LogoBadge initials={defaultBranding.logoInitials} compact />
            </span>
            <div className="min-w-0">
              <p className="truncate text-base font-black uppercase tracking-[0.24em] text-white">
                {defaultBranding.commercialName}
              </p>
              <p className="truncate text-xs font-medium uppercase tracking-[0.18em] text-[#8892A4]">{defaultBranding.legalName}</p>
            </div>
          </div>

          <Link
            href="/login"
            className="inline-flex items-center justify-center rounded-full border border-white px-5 py-2.5 text-sm font-semibold text-white transition-all duration-200 hover:bg-white hover:text-[#0D1B2A]"
          >
            Ingresar
          </Link>
        </div>
      </header>

      <section className="relative overflow-hidden bg-[#0D1B2A] bg-[radial-gradient(ellipse_at_20%_50%,#1A3350_0%,transparent_60%)]">
        <div className="relative flex min-h-screen items-center py-20 px-6 md:px-10 lg:px-16">
          <div className="mx-auto grid w-full max-w-7xl items-center gap-14 lg:grid-cols-[1.15fr_0.85fr]">
            <div className="max-w-3xl">
              <div className="inline-flex items-center gap-3 rounded-full border border-[#1A3350] bg-[#1A3350] px-4 py-2 text-sm font-medium text-[#00E5A0]">
                <span className="relative flex h-2.5 w-2.5">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[#00E5A0] opacity-40" />
                  <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-[#00E5A0]" />
                </span>
                Plataforma notarial nueva generación
              </div>

              <h1 className="mt-10 text-5xl font-black leading-none tracking-tight text-white md:text-7xl lg:text-8xl">
                La notaría del futuro,
                <br />
                operando <span className="text-[#00E5A0]">hoy.</span>
              </h1>

              <p className="mt-6 max-w-xl text-lg leading-relaxed text-[#8892A4]">
                EasyPro digitaliza y estandariza cada acto notarial: escrituras, poderes, declaraciones y actos masivos sin plantillas con etiquetas manuales.
              </p>

              <div className="mt-8 flex flex-col gap-4 sm:flex-row">
                <Link
                  href="/login"
                  className="inline-flex items-center justify-center gap-2 rounded-full bg-[#00E5A0] px-8 py-4 text-base font-bold text-[#0D1B2A] transition-all duration-200 hover:bg-[#00C98A]"
                >
                  Iniciar sesión
                  <ArrowRight className="h-4 w-4" />
                </Link>
                <a
                  href="#funcionamiento"
                  className="inline-flex items-center justify-center rounded-full border border-white/30 px-8 py-4 text-base font-semibold text-white transition-all duration-200 hover:bg-white/10"
                >
                  Ver cómo funciona
                </a>
              </div>

              <div className="mt-12 grid gap-6 sm:grid-cols-3 sm:divide-x sm:divide-white/10">
                <div className="space-y-2 sm:pr-6">
                  <p className="text-lg font-bold text-white">9 Abr 2026</p>
                  <p className="text-sm text-[#8892A4]">Go-live</p>
                </div>
                <div className="space-y-2 sm:pl-6 sm:pr-6">
                  <p className="text-lg font-bold text-white">100% digital</p>
                  <p className="text-sm text-[#8892A4]">Sin papel</p>
                </div>
                <div className="space-y-2 sm:pl-6">
                  <p className="text-lg font-bold text-white">Multinotaría</p>
                  <p className="text-sm text-[#8892A4]">Una plataforma</p>
                </div>
              </div>
            </div>

            <div className="hidden md:block">
              <div className="relative mx-auto w-full max-w-md">
                <div className="absolute -inset-4 rounded-[2rem] bg-[#00E5A0]/10 blur-3xl" />
                <Image
                  src="/notario-hero.png"
                  alt="Imagen notarial de referencia para EasyPro"
                  width={720}
                  height={900}
                  priority
                  className="relative z-10 w-full rounded-3xl object-cover drop-shadow-2xl"
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="funcionamiento" className="bg-white py-24 text-[#0D1B2A]">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <p className="text-sm font-bold uppercase tracking-[0.28em] text-[#00E5A0]">OPERACIÓN INTELIGENTE</p>
          <h2 className="mt-4 text-4xl font-bold tracking-tight md:text-5xl">
            De lo manual a la operación
            <br />
            <span className="text-[#00E5A0]">inteligente.</span>
          </h2>

          <div className="mt-12 grid gap-6 lg:grid-cols-2">
            <article className="rounded-3xl border border-[#E5E7EB] bg-[#F8F9FA] p-8">
              <div className="flex items-center gap-3">
                <XCircle className="h-6 w-6 text-[#EF4444]" />
                <h3 className="text-lg font-bold text-[#EF4444]">Antes</h3>
              </div>
              <ul className="mt-6 space-y-4">
                {beforeItems.map((item) => (
                  <li key={item} className="flex items-start gap-3 text-base leading-relaxed text-[#0D1B2A]">
                    <span className="mt-2 h-2.5 w-2.5 shrink-0 rounded-full bg-[#EF4444]" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </article>

            <article className="rounded-3xl bg-[#0D1B2A] p-8 text-white">
              <div className="flex items-center gap-3">
                <CheckCircle2 className="h-6 w-6 text-[#22C55E]" />
                <h3 className="text-lg font-bold text-[#22C55E]">Con EasyPro</h3>
              </div>
              <ul className="mt-6 space-y-4">
                {afterItems.map((item) => (
                  <li key={item} className="flex items-start gap-3 text-base leading-relaxed text-[#F0F4FF]">
                    <span className="mt-2 h-2.5 w-2.5 shrink-0 rounded-full bg-[#00E5A0]" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </article>
          </div>
        </div>
      </section>

      <section className="bg-[#112236] py-24">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <p className="text-sm font-bold uppercase tracking-[0.28em] text-[#00E5A0]">CAPACIDADES</p>
          <h2 className="mt-4 text-4xl font-bold tracking-tight text-white md:text-5xl">
            Todo lo que su notaría
            <br />
            <span className="text-[#00E5A0]">necesita.</span>
          </h2>

          <div className="mt-12 grid gap-6 md:grid-cols-2 xl:grid-cols-3">
            {features.map(({ title, description, icon: Icon }) => (
              <article
                key={title}
                className="rounded-2xl border border-[#1E3A5F] bg-[#1A3350] p-8 transition-all duration-200 hover:border-[#00E5A0]/60 hover:bg-[#223351]"
              >
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-[#00E5A0]/10 text-[#00E5A0]">
                  <Icon className="h-5 w-5" />
                </div>
                <h3 className="mt-4 text-xl font-semibold text-white">{title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-[#8892A4]">{description}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="bg-white py-24 text-[#0D1B2A]">
        <div className="mx-auto grid max-w-7xl gap-12 px-4 sm:px-6 lg:grid-cols-[1.05fr_0.95fr] lg:px-8">
          <div>
            <p className="text-sm font-bold uppercase tracking-[0.28em] text-[#00E5A0]">IDENTIDAD INSTITUCIONAL</p>
            <h2 className="mt-4 text-4xl font-bold tracking-tight md:text-5xl">
              Cada notaría,
              <br />
              <span className="text-[#00E5A0]">su propia identidad.</span>
            </h2>
            <p className="mt-6 max-w-2xl text-lg leading-relaxed text-[#8892A4]">
              EasyPro se adapta al branding de cada notaría. Colores institucionales, logo, imagen de acceso y nombre comercial configurado en minutos, sin código.
            </p>

            <ul className="mt-8 space-y-4">
              {["Colores y logo propios por sede", "URL personalizada por notaría", "Imagen de acceso institucional"].map((item) => (
                <li key={item} className="flex items-center gap-3 text-base text-[#0D1B2A]">
                  <CheckCircle2 className="h-5 w-5 text-[#00E5A0]" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="flex items-center">
            <div className="w-full rounded-3xl bg-[#0D1B2A] p-8 text-white">
              <div className="flex items-center gap-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-[#00E5A0] text-sm font-black text-black">EP</div>
                <div>
                  <p className="text-lg font-bold tracking-tight">NOTARÍA DE CALDAS</p>
                  <p className="text-sm text-[#8892A4]">Notaría Primera del Círculo</p>
                </div>
              </div>

              <div className="mt-8 flex flex-wrap gap-3">
                {identityChips.map((chip) => (
                  <span key={chip} className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-white">
                    {chip}
                  </span>
                ))}
              </div>

              <div className="my-8 h-px bg-[#1A3350]" />

              <p className="text-sm text-[#8892A4]">Configuración activa · Notaría de Caldas</p>
            </div>
          </div>
        </div>
      </section>

      <section id="casos-de-exito" className="bg-[#0D1B2A] py-24">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <p className="text-sm font-bold uppercase tracking-[0.28em] text-[#00E5A0]">CASOS DE ÉXITO</p>
          <h2 className="mt-4 text-4xl font-bold tracking-tight text-white md:text-5xl">
            Notarías que ya operan
            <br />
            <span className="text-[#00E5A0]">con EasyPro.</span>
          </h2>
          <p className="mt-6 max-w-3xl text-lg leading-relaxed text-[#8892A4]">
            Estas notarías ya trabajan con una operación más clara, trazable y ordenada. Una está en producción y la otra funciona como referencia guiada para evaluación y demo.
          </p>

          <div className="mt-12 grid gap-6 md:grid-cols-2">
            {successCases.map((caseItem) => (
              <article
                key={caseItem.title}
                className="rounded-3xl border border-[#1E3A5F] bg-[#112236] p-8 transition-all duration-200 hover:border-[#00E5A0]/60"
              >
                <div className="flex items-start justify-between gap-6">
                  <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-[#00E5A0] text-base font-black text-black">
                    {caseItem.initials}
                  </div>

                  <div
                    className={`inline-flex items-center gap-2 rounded-full border border-[#1E3A5F] px-4 py-2 text-sm font-medium ${caseItem.live ? "text-[#00E5A0]" : "text-[#8892A4]"}`}
                  >
                    {caseItem.live ? (
                      <span className="relative flex h-2.5 w-2.5">
                        <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[#00E5A0] opacity-40" />
                        <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-[#00E5A0]" />
                      </span>
                    ) : null}
                    <span>{caseItem.status}</span>
                  </div>
                </div>

                <h3 className="mt-6 text-2xl font-bold tracking-tight text-white">{caseItem.title}</h3>
                <p className="mt-2 text-sm font-medium text-[#8892A4]">{caseItem.subtitle}</p>
                <p className="mt-5 text-base leading-relaxed text-[#8892A4]">{caseItem.description}</p>

                <div className="mt-6 flex flex-wrap gap-3">
                  {caseItem.tags.map((tag) => (
                    <span
                      key={tag}
                      className="rounded-full border border-[#1E3A5F] bg-[#1A3350] px-4 py-2 text-sm text-[#E6EBF5]"
                    >
                      {tag}
                    </span>
                  ))}
                </div>

                <div className="mt-8 border-t border-[#1E3A5F] pt-6 flex items-center justify-between gap-4 flex-wrap">
                  <button
                    type="button"
                    onClick={() =>
                      setVideoModal({
                        open: true,
                        url: caseItem.videoUrl,
                        title: caseItem.title,
                      })
                    }
                    className="inline-flex items-center gap-2 rounded-full border border-[#00E5A0]/40 px-4 py-2 text-sm font-semibold text-[#00E5A0] transition-colors hover:bg-[#00E5A0]/10"
                  >
                    <Play className="h-4 w-4" />
                    Ver testimonio
                  </button>

                  <a
                    href={caseItem.href}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-2 text-sm font-semibold text-[#00E5A0] transition-colors hover:text-[#00C98A]"
                  >
                    {caseItem.cta}
                    <ArrowRight className="h-4 w-4" />
                  </a>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="bg-[#0D1B2A] py-24">
        <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
          <p className="text-sm font-bold uppercase tracking-[0.28em] text-[#00E5A0]">SOPORTE Y CLARIDAD</p>
          <h2 className="mt-4 text-4xl font-bold tracking-tight text-white md:text-5xl">
            Preguntas
            <br />
            <span className="text-[#00E5A0]">frecuentes.</span>
          </h2>

          <div className="mt-12 space-y-4">
            {faqs.map((faq, index) => {
              const isOpen = openFaq === index;

              return (
                <div
                  key={faq.question}
                  className={`rounded-2xl border bg-[#112236] transition-all duration-200 ${isOpen ? "border-[#00E5A0]" : "border-[#1A3350]"}`}
                >
                  <button
                    type="button"
                    onClick={() => setOpenFaq(isOpen ? null : index)}
                    className="flex w-full items-center justify-between gap-4 px-6 py-5 text-left"
                    aria-expanded={isOpen}
                  >
                    <span className="text-lg font-medium text-white">{faq.question}</span>
                    <span className="flex h-8 w-8 items-center justify-center rounded-full border border-[#1A3350] text-[#00E5A0]">
                      {isOpen ? <X className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
                    </span>
                  </button>
                  {isOpen ? (
                    <div className="px-6 pb-6 pt-0 text-base leading-relaxed text-[#8892A4]">
                      {faq.answer}
                    </div>
                  ) : null}
                </div>
              );
            })}
          </div>
        </div>
      </section>

      <section className="bg-gradient-to-b from-[#0D1B2A] to-[#112236] py-32">
        <div className="mx-auto max-w-5xl px-4 text-center sm:px-6 lg:px-8">
          <h2 className="text-5xl font-black leading-none tracking-tight text-white md:text-7xl">
            Su notaría lista
            <br />
            para el <span className="text-[#00E5A0]">siguiente nivel.</span>
          </h2>
          <p className="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-[#8892A4]">
            Únase a las notarías que ya operan con EasyPro Notarial.
          </p>

          <div className="mt-10">
            <Link
              href="/login"
              className="inline-flex items-center justify-center rounded-full bg-[#00E5A0] px-12 py-5 text-lg font-bold text-[#0D1B2A] transition-all duration-200 hover:bg-[#00C98A]"
            >
              Solicitar acceso
            </Link>
          </div>

          <p className="mt-14 text-sm text-[#8892A4]">© 2026 EasyPro Notarial · Todos los derechos reservados</p>
        </div>
      </section>
      {videoModal.open ? (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm"
          onClick={() => setVideoModal({ open: false, url: "", title: "" })}
        >
          <div
            className="relative mx-4 w-full max-w-3xl rounded-3xl border border-[#1E3A5F] bg-[#0D1B2A] p-6"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="flex items-center justify-between gap-4">
              <h3 className="text-lg font-bold text-white">{videoModal.title}</h3>
              <button
                type="button"
                onClick={() => setVideoModal({ open: false, url: "", title: "" })}
                className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-[#1E3A5F] text-[#8892A4] transition-colors hover:border-[#00E5A0]/60 hover:text-[#00E5A0]"
                aria-label="Cerrar modal"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <iframe
              className="mt-4 aspect-video w-full rounded-2xl"
              src={videoModal.url}
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
              title={videoModal.title}
            />

            <p className="mt-3 text-center text-xs text-[#8892A4]">Video testimonial  próximamente disponible</p>
          </div>
        </div>
      ) : null}
      <footer>
        <section className="bg-black py-12 px-6">
          <div className="mx-auto grid max-w-7xl gap-8 lg:grid-cols-[1fr_1.1fr] lg:items-center">
            <div className="flex items-start gap-4">
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full border border-[#1E3A5F] bg-[#0D1B2A] text-[#00E5A0]">
                <Mail className="h-5 w-5" />
              </div>
              <div>
                <h3 className="text-2xl font-bold text-white">Mantente al día con EasyPro</h3>
                <p className="mt-2 max-w-xl text-sm leading-relaxed text-[#8892A4]">
                  Recibe novedades sobre la plataforma y el sector notarial colombiano.
                </p>
              </div>
            </div>

            <div className="grid gap-4">
              <div className="flex flex-col gap-3 sm:flex-row">
                <input
                  type="email"
                  value={newsletterEmail}
                  onChange={(event) => setNewsletterEmail(event.target.value)}
                  placeholder="Correo electrónico"
                  className="h-12 min-w-0 flex-1 rounded-full border border-[#1E3A5F] bg-[#0D1B2A] px-5 text-sm text-white placeholder:text-[#8892A4] focus:border-[#00E5A0] focus:outline-none"
                />
                <button
                  type="button"
                  onClick={() => {
                    if (!newsletterAccepted || !newsletterEmail.trim()) return;
                  }}
                  className="inline-flex h-12 items-center justify-center rounded-full bg-[#00E5A0] px-7 text-sm font-bold text-black transition-colors hover:bg-[#00d895]"
                >
                  Suscribirse
                </button>
              </div>

              <label className="flex items-start gap-3 text-sm text-[#8892A4]">
                <input
                  type="checkbox"
                  checked={newsletterAccepted}
                  onChange={(event) => setNewsletterAccepted(event.target.checked)}
                  className="mt-1 h-4 w-4 rounded border-[#1E3A5F] bg-transparent text-[#00E5A0] focus:ring-[#00E5A0]"
                />
                <span>Acepto las políticas de tratamiento de datos personales</span>
              </label>
            </div>
          </div>
        </section>

        <section className="bg-[#0D1B2A] py-16 px-6">
          <div className="mx-auto grid max-w-7xl gap-10 md:grid-cols-2 lg:grid-cols-4">
            <div>
              <div className="flex items-center gap-3">
                <div className="flex h-11 w-11 items-center justify-center rounded-full bg-[#00E5A0] text-sm font-black text-black">
                  EP
                </div>
                <div>
                  <p className="text-sm font-black tracking-[0.24em] text-white">EASYPRO NOTARIAL</p>
                  <p className="text-sm text-[#8892A4]">Plataforma notarial digital</p>
                </div>
              </div>
            </div>

            <div>
              <h4 className="text-sm font-bold uppercase tracking-[0.2em] text-white">Producto</h4>
              <ul className="mt-5 space-y-3 text-sm">
                <li>
                  <a href="#funcionamiento" className="text-[#8892A4] transition-colors hover:text-[#00E5A0]">
                    Capacidades
                  </a>
                </li>
                <li>
                  <a href="#funcionamiento" className="text-[#8892A4] transition-colors hover:text-[#00E5A0]">
                    Cómo funciona
                  </a>
                </li>
                <li>
                  <a href="#funcionamiento" className="text-[#8892A4] transition-colors hover:text-[#00E5A0]">
                    Preguntas frecuentes
                  </a>
                </li>
                <li>
                  <Link href="/login" className="text-[#8892A4] transition-colors hover:text-[#00E5A0]">
                    Solicitar acceso
                  </Link>
                </li>
              </ul>
            </div>

            <div>
              <h4 className="text-sm font-bold uppercase tracking-[0.2em] text-white">Empresa</h4>
              <ul className="mt-5 space-y-3 text-sm">
                <li>
                  <a href="#funcionamiento" className="text-[#8892A4] transition-colors hover:text-[#00E5A0]">
                    Sobre EasyPro
                  </a>
                </li>
                <li>
                  <a href="#funcionamiento" className="text-[#8892A4] transition-colors hover:text-[#00E5A0]">
                    Contacto
                  </a>
                </li>
                <li>
                  <a href="#funcionamiento" className="text-[#8892A4] transition-colors hover:text-[#00E5A0]">
                    Términos de uso
                  </a>
                </li>
                <li>
                  <a href="#funcionamiento" className="text-[#8892A4] transition-colors hover:text-[#00E5A0]">
                    Política de privacidad
                  </a>
                </li>
              </ul>
            </div>

            <div>
              <h4 className="text-sm font-bold uppercase tracking-[0.2em] text-white">Medellín, Colombia</h4>
              <div className="mt-5 space-y-2 text-sm leading-relaxed text-[#8892A4]">
                <p>Carrera 43B #1A Sur - 70</p>
                <p>Piso 10, Edificio Buró 4.0</p>
                <p>Medellín, Antioquia</p>
              </div>
            </div>
          </div>
        </section>

        <section className="border-t border-[#1E3A5F] bg-black py-4 px-6">
          <p className="text-center text-sm text-[#8892A4]">
            © 2026 EasyPro Notarial · Todos los derechos reservados · Colombia
          </p>
        </section>
      </footer>
      <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-3">
        <a
          href="https://wa.me/573107932844"
          target="_blank"
          rel="noreferrer"
          className="flex h-14 w-14 items-center justify-center rounded-full bg-[#25D366] shadow-lg transition-transform hover:scale-110"
          aria-label="Contactar por WhatsApp"
        >
          <svg viewBox="0 0 24 24" fill="white" className="h-6 w-6" aria-hidden="true">
            <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z" />
          </svg>
        </a>

        <a
          href="tel:+573107932844"
          className="flex h-14 w-14 items-center justify-center rounded-full bg-[#00E5A0] shadow-lg transition-transform hover:scale-110"
          aria-label="Llamar por teléfono"
        >
          <Phone size={24} color="#0D1B2A" />
        </a>
      </div>
    </main>
  );
}
```

## File: components/marketing/login-panel.tsx
```typescript
"use client";

import Image from "next/image";
import { FormEvent, useState } from "react";
import { login, completeLogin } from "@/lib/api";

function resolveAppOrigin() {
  if (typeof window === "undefined") {
    return "http://127.0.0.1:5179";
  }

  return window.location.origin;
}

export function LoginPanel() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [rememberSession, setRememberSession] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [consentAccepted, setConsentAccepted] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!consentAccepted) {
      setError("Debes aceptar el tratamiento de datos para continuar.");
      return;
    }

    setIsSubmitting(true);
    setError(null);

    const formData = new FormData(event.currentTarget);
    const email = String(formData.get("email") ?? "");
    const password = String(formData.get("password") ?? "");
    const nextPath = typeof window !== "undefined" ? new URLSearchParams(window.location.search).get("next") : null;

    try {
      const payload = await login({ email, password });
      completeLogin(payload.access_token, rememberSession);
      window.location.assign(`${resolveAppOrigin()}${nextPath ?? "/dashboard"}`);
    } catch (submissionError) {
      setError(submissionError instanceof Error ? submissionError.message : "No fue posible iniciar sesión.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#0D1B2A] text-white">
      <div className="grid min-h-screen lg:grid-cols-[1.22fr_0.78fr]">
        <section className="relative hidden lg:flex flex-col items-center justify-center bg-[#0D1B2A] p-10">
          <div className="relative w-full max-w-sm overflow-hidden rounded-3xl shadow-2xl">
            <Image
              src="/notario-hero.png"
              alt="EasyPro Notarial"
              width={480}
              height={560}
              className="w-full rounded-3xl object-cover"
              priority
            />
            <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-[#0D1B2A] to-transparent p-6">
              <p className="text-xs font-semibold uppercase tracking-widest text-[#00E5A0]">Plataforma activa</p>
              <p className="mt-1 text-lg font-bold text-white">Notaría de Caldas</p>
              <p className="mt-1 text-xs text-[#8892A4]">Notaría Primera del Círculo · Go-live 9 Abr 2026</p>
            </div>
          </div>

          <p className="mt-8 max-w-xs text-center text-sm leading-relaxed text-[#8892A4]">"La plataforma que modernizó nuestra operación notarial desde el primer día."</p>
          <p className="mt-2 text-xs font-semibold text-[#00E5A0]">Notaría de Caldas</p>
        </section>

        <section className="flex items-center justify-center bg-[#0D1B2A] px-8 py-10">
          <div className="w-full max-w-sm rounded-[2rem] border border-[#1E3A5F] bg-[#112236] p-6 shadow-2xl sm:p-7">
            <div className="space-y-5">
              <div className="flex items-center gap-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#00E5A0] text-sm font-black text-[#0D1B2A]">
                  EP
                </div>
                <p className="text-xs font-bold uppercase tracking-[0.3em] text-[#00E5A0]">ACCESO</p>
              </div>

              <div>
                <h1 className="text-4xl font-black tracking-tight text-white">Inicia sesión</h1>
                <p className="mt-3 text-sm text-[#8892A4]">Ingresa con tus credenciales institucionales</p>
              </div>
            </div>

            <form onSubmit={onSubmit} className="mt-8 space-y-5">
              <div>
                <label htmlFor="email" className="mb-1 block text-sm text-[#8892A4]">
                  Usuario
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  defaultValue="superadmin@easypro.co"
                  className="w-full rounded-2xl border border-[#1E3A5F] bg-[#1A3350] px-4 py-3 text-white placeholder:text-[#8892A4] transition focus:border-[#00E5A0] focus:outline-none"
                />
              </div>

              <div>
                <label htmlFor="password" className="mb-1 block text-sm text-[#8892A4]">
                  Contraseña
                </label>
                <input
                  id="password"
                  name="password"
                  type="password"
                  defaultValue="ChangeMe123!"
                  className="w-full rounded-2xl border border-[#1E3A5F] bg-[#1A3350] px-4 py-3 text-white placeholder:text-[#8892A4] transition focus:border-[#00E5A0] focus:outline-none"
                />
              </div>

              <label className="mt-2 flex cursor-pointer items-start gap-3">
                <input
                  type="checkbox"
                  checked={consentAccepted}
                  onChange={(event) => setConsentAccepted(event.target.checked)}
                  style={{ accentColor: "#00E5A0" }}
                  className="mt-1 h-4 w-4 rounded border-[#1E3A5F] bg-transparent"
                />
                <span className="text-xs leading-5 text-[#8892A4]">
                  He leído y acepto la <span className="font-medium text-[#00E5A0]">política de tratamiento de datos</span> y autorizo el uso institucional de la plataforma.
                </span>
              </label>

              <label className="flex items-center gap-3 text-sm text-[#8892A4]">
                <input
                  type="checkbox"
                  checked={rememberSession}
                  onChange={(event) => setRememberSession(event.target.checked)}
                  style={{ accentColor: "#00E5A0" }}
                  className="h-4 w-4 rounded border-[#1E3A5F] bg-transparent"
                />
                <span>Recordar sesión</span>
              </label>

              {error ? (
                <div className="rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-400">
                  {error}
                </div>
              ) : null}

              <button
                type="submit"
                disabled={isSubmitting || !consentAccepted}
                className="w-full rounded-2xl bg-[#00E5A0] py-4 text-sm font-bold text-[#0D1B2A] transition hover:bg-[#00C98A] disabled:cursor-not-allowed disabled:opacity-50"
              >
                {isSubmitting ? "Ingresando..." : "Ingresar"}
              </button>
            </form>

            <p className="mt-6 text-center text-xs text-[#8892A4]">© 2026 EasyPro Notarial · Acceso institucional</p>
          </div>
        </section>
      </div>
    </main>
  );
}
```

## File: components/notaries/commercial-workspace.tsx
```typescript
"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { RefreshCw } from "lucide-react";
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer
} from "recharts";
import {
  getNotaries,
  getNotaryFilterOptions,
  importAntioquiaSource,
  type NotaryFilterOptions,
  type NotaryFilters,
  type NotaryRecord
} from "@/lib/api";

const PAGE_SIZE = 20;

type StatusConfig = {
  key: string;
  label: string;
  badgeClass: string;
  chartColor: string;
};

const STATUS_CONFIG: StatusConfig[] = [
  { key: "prospecto", label: "Prospecto", badgeClass: "bg-slate-200 text-slate-700", chartColor: "#94a3b8" },
  { key: "contactado", label: "Contactado", badgeClass: "bg-blue-100 text-blue-700", chartColor: "#3b82f6" },
  { key: "en seguimiento", label: "En seguimiento", badgeClass: "bg-cyan-100 text-cyan-700", chartColor: "#06b6d4" },
  {
    key: "reunión agendada",
    label: "Reunión agendada",
    badgeClass: "bg-orange-100 text-orange-700",
    chartColor: "#f97316"
  },
  {
    key: "propuesta enviada",
    label: "Propuesta enviada",
    badgeClass: "bg-violet-100 text-violet-700",
    chartColor: "#8b5cf6"
  },
  { key: "negociación", label: "Negociación", badgeClass: "bg-amber-100 text-amber-700", chartColor: "#f59e0b" },
  {
    key: "cerrado ganado",
    label: "Cerrado ganado",
    badgeClass: "bg-emerald-100 text-emerald-700",
    chartColor: "#10b981"
  },
  { key: "cerrado perdido", label: "Cerrado perdido", badgeClass: "bg-red-100 text-red-700", chartColor: "#ef4444" },
  {
    key: "no interesado",
    label: "No interesado",
    badgeClass: "bg-slate-700 text-slate-100",
    chartColor: "#334155"
  }
];

const statusByKey = new Map<string, StatusConfig>(STATUS_CONFIG.map((status) => [status.key, status]));

const emptyFilters: NotaryFilters = {
  commercial_status: "",
  municipality: "",
  commercial_owner: "",
  priority: "",
  q: ""
};

function normalizeStatus(status: string): string {
  return status.trim().toLowerCase();
}

function badgeTone(status: string): string {
  return statusByKey.get(normalizeStatus(status))?.badgeClass ?? "bg-slate-100 text-slate-700";
}

export function CommercialWorkspace() {
  const [notaries, setNotaries] = useState<NotaryRecord[]>([]);
  const [filters, setFilters] = useState<NotaryFilters>(emptyFilters);
  const [filterOptions, setFilterOptions] = useState<NotaryFilterOptions>({
    municipalities: [],
    commercial_owners: [],
    priorities: [],
    commercial_statuses: []
  });
  const [isLoading, setIsLoading] = useState(true);
  const [isImporting, setIsImporting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [activeTab, setActiveTab] = useState<"lista" | "graficos">("lista");

  useEffect(() => {
    void Promise.all([loadNotaries(emptyFilters), loadFilterOptions()]);
  }, []);

  async function loadNotaries(nextFilters: NotaryFilters) {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getNotaries(nextFilters);
      setNotaries(data);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "No fue posible cargar el workspace comercial.");
    } finally {
      setIsLoading(false);
    }
  }

  async function loadFilterOptions() {
    try {
      const data = await getNotaryFilterOptions();
      setFilterOptions(data);
    } catch {
      // Mantener vista operativa sin bloquear filtros pre-cargados.
    }
  }

  async function handleReimport() {
    setIsImporting(true);
    setError(null);
    try {
      await importAntioquiaSource(true);
      await Promise.all([loadNotaries(filters), loadFilterOptions()]);
    } catch (importError) {
      setError(importError instanceof Error ? importError.message : "No fue posible reimportar el catálogo.");
    } finally {
      setIsImporting(false);
    }
  }

  function updateFilter<K extends keyof NotaryFilters>(field: K, value: string) {
    const nextFilters = { ...filters, [field]: value };
    setFilters(nextFilters);
    setCurrentPage(1);
    void loadNotaries(nextFilters);
  }

  const totalNotaries = notaries.length;
  const highPriorityCount = useMemo(
    () => notaries.filter((notary) => ["alta", "crítica"].includes(notary.priority.toLowerCase())).length,
    [notaries]
  );

  const activeOwnersCount = useMemo(() => {
    const owners = new Set(
      notaries
        .map((notary) => notary.commercial_owner_display?.trim() || "")
        .filter((owner) => owner.length > 0)
    );
    return owners.size;
  }, [notaries]);

  const statusCounts = useMemo(() => {
    const counts = new Map<string, number>(STATUS_CONFIG.map((status) => [status.key, 0]));
    for (const notary of notaries) {
      const normalized = normalizeStatus(notary.commercial_status || "");
      if (counts.has(normalized)) {
        counts.set(normalized, (counts.get(normalized) ?? 0) + 1);
      }
    }

    return STATUS_CONFIG.map((status) => ({
      ...status,
      count: counts.get(status.key) ?? 0
    }));
  }, [notaries]);

  const pieData = useMemo(
    () =>
      statusCounts
        .filter((item) => item.count > 0)
        .map((item) => ({
          name: item.label,
          value: item.count,
          color: item.chartColor
        })),
    [statusCounts]
  );

  const topMunicipalitiesData = useMemo(() => {
    const totals = new Map<string, number>();
    for (const notary of notaries) {
      const municipality = notary.municipality?.trim() || "Sin municipio";
      totals.set(municipality, (totals.get(municipality) ?? 0) + notary.activity_count);
    }

    return Array.from(totals.entries())
      .map(([municipality, gestiones]) => ({ municipality, gestiones }))
      .sort((a, b) => b.gestiones - a.gestiones)
      .slice(0, 10)
      .reverse();
  }, [notaries]);

  const ownersActivityData = useMemo(() => {
    const totals = new Map<string, number>();
    for (const notary of notaries) {
      const owner = notary.commercial_owner_display?.trim() || "Sin asignar";
      totals.set(owner, (totals.get(owner) ?? 0) + notary.activity_count);
    }

    return Array.from(totals.entries())
      .map(([responsable, gestiones]) => ({ responsable, gestiones }))
      .filter((item) => item.gestiones > 0)
      .sort((a, b) => b.gestiones - a.gestiones);
  }, [notaries]);

  const commercialProgressRate = useMemo(() => {
    if (totalNotaries === 0) {
      return 0;
    }

    const prospectCount = statusCounts.find((status) => status.key === "prospecto")?.count ?? 0;
    return ((totalNotaries - prospectCount) / totalNotaries) * 100;
  }, [statusCounts, totalNotaries]);

  const totalPages = Math.max(1, Math.ceil(notaries.length / PAGE_SIZE));
  const pageStart = (currentPage - 1) * PAGE_SIZE;
  const currentRows = notaries.slice(pageStart, pageStart + PAGE_SIZE);

  function goToPage(page: number) {
    const boundedPage = Math.min(Math.max(page, 1), totalPages);
    setCurrentPage(boundedPage);
  }

  return (
    <div className="space-y-6">
      <section className="ep-card rounded-[2rem] p-6">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
          <div className="max-w-3xl">
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-accent">Comercial</p>
            <h1 className="mt-3 text-3xl font-semibold tracking-[-0.05em] text-primary sm:text-4xl">Comercial</h1>
            <p className="mt-3 text-base leading-7 text-secondary">Gestión comercial y prospección de notarías</p>
          </div>
          <button
            onClick={handleReimport}
            disabled={isImporting}
            className="inline-flex items-center justify-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white shadow-panel transition hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-70"
          >
            <RefreshCw className={`h-4 w-4 ${isImporting ? "animate-spin" : ""}`} />
            {isImporting ? "Reimportando..." : "Reimportar catálogo"}
          </button>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-3">
          <div className="ep-card-muted rounded-[1.5rem] p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-secondary">Total notarías</p>
            <p className="mt-3 text-3xl font-semibold text-primary">{totalNotaries}</p>
          </div>
          <div className="ep-card-muted rounded-[1.5rem] p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-secondary">Alta prioridad</p>
            <p className="mt-3 text-3xl font-semibold text-primary">{highPriorityCount}</p>
          </div>
          <div className="ep-card-muted rounded-[1.5rem] p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-secondary">Responsables activos</p>
            <p className="mt-3 text-3xl font-semibold text-primary">{activeOwnersCount}</p>
          </div>
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          {statusCounts.map((status) => (
            <span key={status.key} className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${status.badgeClass}`}>
              {status.label}: {status.count}
            </span>
          ))}
        </div>
      </section>

      <section className="ep-card rounded-[2rem] p-6">
        <div className="ep-filter-panel grid gap-4 rounded-[1.75rem] p-4 lg:grid-cols-5">
          <label className="grid gap-2 text-sm font-medium text-primary">
            Estado comercial
            <select
              value={filters.commercial_status ?? ""}
              onChange={(event) => updateFilter("commercial_status", event.target.value)}
              className="ep-select h-12 rounded-2xl px-4"
            >
              <option value="">Todos</option>
              {filterOptions.commercial_statuses.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>

          <label className="grid gap-2 text-sm font-medium text-primary">
            Municipio
            <select
              value={filters.municipality ?? ""}
              onChange={(event) => updateFilter("municipality", event.target.value)}
              className="ep-select h-12 rounded-2xl px-4"
            >
              <option value="">Todos</option>
              {filterOptions.municipalities.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>

          <label className="grid gap-2 text-sm font-medium text-primary">
            Responsable
            <select
              value={filters.commercial_owner ?? ""}
              onChange={(event) => updateFilter("commercial_owner", event.target.value)}
              className="ep-select h-12 rounded-2xl px-4"
            >
              <option value="">Todos</option>
              {filterOptions.commercial_owners.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>

          <label className="grid gap-2 text-sm font-medium text-primary">
            Prioridad
            <select
              value={filters.priority ?? ""}
              onChange={(event) => updateFilter("priority", event.target.value)}
              className="ep-select h-12 rounded-2xl px-4"
            >
              <option value="">Todas</option>
              {filterOptions.priorities.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>

          <label className="grid gap-2 text-sm font-medium text-primary">
            Buscar
            <input
              value={filters.q ?? ""}
              onChange={(event) => updateFilter("q", event.target.value)}
              placeholder="Municipio, notaría, correo..."
              className="ep-input h-12 rounded-2xl px-4"
            />
          </label>
        </div>

        {error ? <div className="ep-kpi-critical mt-5 rounded-2xl px-4 py-3 text-sm">{error}</div> : null}

        <div className="mt-6 flex gap-1 rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-1 w-fit">
          <button
            onClick={() => setActiveTab("lista")}
            className={
              activeTab === "lista"
                ? "rounded-xl bg-primary px-5 py-2 text-sm font-semibold text-white"
                : "rounded-xl px-5 py-2 text-sm font-medium text-secondary hover:bg-[var(--panel-soft)]"
            }
          >
            Lista
          </button>
          <button
            onClick={() => setActiveTab("graficos")}
            className={
              activeTab === "graficos"
                ? "rounded-xl bg-primary px-5 py-2 text-sm font-semibold text-white"
                : "rounded-xl px-5 py-2 text-sm font-medium text-secondary hover:bg-[var(--panel-soft)]"
            }
          >
            Gráficos
          </button>
        </div>

        {activeTab === "lista" && (
          <div className="mt-4 overflow-hidden rounded-[1.5rem] border border-slate-200/70 bg-white/80">
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead className="bg-slate-50/90 text-left text-xs uppercase tracking-[0.14em] text-secondary">
                  <tr>
                    <th className="px-4 py-3">Notaría</th>
                    <th className="px-4 py-3">Municipio</th>
                    <th className="px-4 py-3">Estado comercial</th>
                    <th className="px-4 py-3">Responsable</th>
                    <th className="px-4 py-3">Prioridad</th>
                    <th className="px-4 py-3">Gestiones</th>
                    <th className="px-4 py-3">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {isLoading ? (
                    <tr>
                      <td colSpan={7} className="px-4 py-6 text-secondary">
                        Cargando registros comerciales...
                      </td>
                    </tr>
                  ) : null}

                  {!isLoading && currentRows.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="px-4 py-6 text-secondary">
                        No hay notarías para los filtros seleccionados.
                      </td>
                    </tr>
                  ) : null}

                  {!isLoading
                    ? currentRows.map((notary) => (
                        <tr key={notary.id} className="border-t border-slate-200/70 text-primary">
                          <td className="px-4 py-3">
                            <p className="font-semibold">{notary.notary_label}</p>
                            <p className="text-xs text-secondary">{notary.department}</p>
                          </td>
                          <td className="px-4 py-3">{notary.municipality || "Sin municipio"}</td>
                          <td className="px-4 py-3">
                            <span
                              className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${badgeTone(notary.commercial_status)}`}
                            >
                              {notary.commercial_status || "sin estado"}
                            </span>
                          </td>
                          <td className="px-4 py-3">{notary.commercial_owner_display || "Sin asignar"}</td>
                          <td className="px-4 py-3">{notary.priority}</td>
                          <td className="px-4 py-3">{notary.activity_count}</td>
                          <td className="px-4 py-3">
                            <Link
                              href={`/dashboard/comercial/${notary.id}`}
                              className="inline-flex items-center rounded-xl bg-primary px-3 py-2 text-xs font-semibold text-white"
                            >
                              Ver CRM
                            </Link>
                          </td>
                        </tr>
                      ))
                    : null}
                </tbody>
              </table>
            </div>

            <div className="flex items-center justify-between border-t border-slate-200/70 px-4 py-3 text-sm text-secondary">
              <span>
                Página {currentPage} de {totalPages}
              </span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => goToPage(currentPage - 1)}
                  disabled={currentPage <= 1}
                  className="rounded-xl border border-slate-300 px-3 py-1.5 text-primary disabled:cursor-not-allowed disabled:opacity-40"
                >
                  Anterior
                </button>
                <button
                  onClick={() => goToPage(currentPage + 1)}
                  disabled={currentPage >= totalPages}
                  className="rounded-xl border border-slate-300 px-3 py-1.5 text-primary disabled:cursor-not-allowed disabled:opacity-40"
                >
                  Siguiente
                </button>
              </div>
            </div>
          </div>
        )}

        {activeTab === "graficos" && (
          <div className="mt-4 grid gap-4 xl:grid-cols-2">
            <div className="ep-card-soft rounded-[1.5rem] p-4">
              <p className="mb-3 text-sm font-semibold text-primary">Distribución por estado comercial</p>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie data={pieData} dataKey="value" nameKey="name" innerRadius={70} outerRadius={110} paddingAngle={2}>
                    {pieData.map((entry) => (
                      <Cell key={entry.name} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
              <div className="mt-3 flex flex-wrap gap-2 text-xs">
                {pieData.length > 0 ? (
                  pieData.map((item) => (
                    <span key={item.name} className="inline-flex items-center gap-2 rounded-full bg-slate-100 px-3 py-1 text-slate-700">
                      <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: item.color }} />
                      {item.name}: {item.value}
                    </span>
                  ))
                ) : (
                  <span className="text-secondary">Sin datos para el gráfico.</span>
                )}
              </div>
            </div>

            <div className="ep-card-soft rounded-[1.5rem] p-4">
              <p className="mb-3 text-sm font-semibold text-primary">Top 10 municipios por gestiones</p>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={topMunicipalitiesData} layout="vertical" margin={{ top: 8, right: 12, left: 12, bottom: 8 }}>
                  <XAxis type="number" />
                  <YAxis type="category" dataKey="municipality" width={120} />
                  <Tooltip />
                  <Bar dataKey="gestiones" fill="#2563eb" radius={[0, 6, 6, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="ep-card-soft rounded-[1.5rem] p-4">
              <p className="mb-3 text-sm font-semibold text-primary">Gestiones por responsable</p>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={ownersActivityData} margin={{ top: 8, right: 12, left: 0, bottom: 36 }}>
                  <XAxis dataKey="responsable" angle={-25} textAnchor="end" interval={0} height={70} />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="gestiones" fill="#0ea5e9" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="ep-card-soft rounded-[1.5rem] p-6">
              <p className="text-sm font-semibold text-primary">Tasa de avance comercial</p>
              <p className="mt-5 text-5xl font-semibold tracking-[-0.04em] text-primary">{commercialProgressRate.toFixed(1)}%</p>
              <p className="mt-3 text-sm leading-6 text-secondary">
                Porcentaje de notarías que avanzaron más allá de estado prospecto, calculado como (total - prospecto) /
                total * 100.
              </p>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
```

## File: components/notaries/notaries-catalog.tsx
```typescript
"use client";

import Link from "next/link";
import { Search } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { getNotaries, type NotaryRecord } from "@/lib/api";

const PAGE_SIZE = 20;

function normalizeText(value: string | null | undefined): string {
  return (value ?? "").trim().toLowerCase();
}

export function NotariesCatalog() {
  const [notaries, setNotaries] = useState<NotaryRecord[]>([]);
  const [query, setQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    async function loadNotaries() {
      setIsLoading(true);
      setError(null);
      try {
        const data = await getNotaries();
        if (!isMounted) {
          return;
        }
        setNotaries(data);
      } catch (loadError) {
        if (!isMounted) {
          return;
        }
        setError(loadError instanceof Error ? loadError.message : "No fue posible cargar el catálogo de notarías.");
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    void loadNotaries();

    return () => {
      isMounted = false;
    };
  }, []);

  const filteredNotaries = useMemo(() => {
    const search = normalizeText(query);
    if (!search) {
      return notaries;
    }

    return notaries.filter((notary) => {
      const label = normalizeText(notary.notary_label);
      const municipality = normalizeText(notary.municipality);
      const holder = normalizeText(notary.current_notary_name);
      return label.includes(search) || municipality.includes(search) || holder.includes(search);
    });
  }, [notaries, query]);

  const totalPages = Math.max(1, Math.ceil(filteredNotaries.length / PAGE_SIZE));

  useEffect(() => {
    if (currentPage > totalPages) {
      setCurrentPage(totalPages);
    }
  }, [currentPage, totalPages]);

  useEffect(() => {
    setCurrentPage(1);
  }, [query]);

  const paginatedNotaries = useMemo(() => {
    const start = (currentPage - 1) * PAGE_SIZE;
    return filteredNotaries.slice(start, start + PAGE_SIZE);
  }, [currentPage, filteredNotaries]);

  const departmentsCount = useMemo(() => new Set(notaries.map((item) => normalizeText(item.department)).filter(Boolean)).size, [notaries]);

  const withAssignedUsersCount = useMemo(
    () => notaries.filter((item) => item.commercial_owner_user_id !== null).length,
    [notaries]
  );

  return (
    <div className="space-y-6">
      <section className="ep-card rounded-[2rem] p-6">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-3xl">
            <h1 className="text-3xl font-semibold tracking-[-0.05em] text-primary sm:text-4xl">Notarías</h1>
            <p className="mt-3 text-base text-secondary">Catálogo operativo de notarías registradas en el sistema</p>
          </div>

          <div className="w-full max-w-xl">
            <label htmlFor="notaries-search" className="mb-2 block text-sm font-medium text-primary">
              Buscar por nombre, municipio o notario titular
            </label>
            <div className="ep-input flex h-12 items-center gap-3 rounded-2xl px-4">
              <Search className="h-4 w-4 text-secondary" />
              <input
                id="notaries-search"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Ej. Notaría 12, Medellín, Juan Pérez"
                className="h-full w-full bg-transparent text-sm text-primary placeholder:text-secondary/70 focus:outline-none"
              />
            </div>
          </div>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-3">
          <div className="ep-card-muted rounded-[1.5rem] p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-secondary">Total notarías</p>
            <p className="mt-3 text-3xl font-semibold text-primary">{notaries.length}</p>
          </div>
          <div className="ep-card-muted rounded-[1.5rem] p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-secondary">Departamentos</p>
            <p className="mt-3 text-3xl font-semibold text-primary">{departmentsCount}</p>
          </div>
          <div className="ep-card-muted rounded-[1.5rem] p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-secondary">Con usuarios asignados</p>
            <p className="mt-3 text-3xl font-semibold text-primary">{withAssignedUsersCount}</p>
          </div>
        </div>
      </section>

      <section className="ep-card rounded-[2rem] p-6">
        {error ? <div className="ep-kpi-critical rounded-2xl px-4 py-3 text-sm">{error}</div> : null}

        <div className="mt-2 overflow-x-auto">
          <table className="min-w-full border-separate border-spacing-0">
            <thead>
              <tr className="text-left text-xs uppercase tracking-[0.16em] text-secondary">
                <th className="border-b border-white/10 px-4 py-3 font-semibold">Notaría</th>
                <th className="border-b border-white/10 px-4 py-3 font-semibold">Municipio</th>
                <th className="border-b border-white/10 px-4 py-3 font-semibold">Departamento</th>
                <th className="border-b border-white/10 px-4 py-3 font-semibold">Notario titular</th>
                <th className="border-b border-white/10 px-4 py-3 font-semibold">Teléfono</th>
                <th className="border-b border-white/10 px-4 py-3 font-semibold">Email</th>
                <th className="border-b border-white/10 px-4 py-3 font-semibold">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan={7} className="px-4 py-6 text-sm text-secondary">
                    Cargando catálogo...
                  </td>
                </tr>
              ) : null}

              {!isLoading && paginatedNotaries.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-6 text-sm text-secondary">
                    No hay notarías para el criterio de búsqueda ingresado.
                  </td>
                </tr>
              ) : null}

              {!isLoading
                ? paginatedNotaries.map((notary) => (
                    <tr key={notary.id} className="text-sm text-primary">
                      <td className="border-b border-white/5 px-4 py-4 font-medium">{notary.notary_label || "—"}</td>
                      <td className="border-b border-white/5 px-4 py-4 text-secondary">{notary.municipality || "—"}</td>
                      <td className="border-b border-white/5 px-4 py-4 text-secondary">{notary.department || "—"}</td>
                      <td className="border-b border-white/5 px-4 py-4 text-secondary">{notary.current_notary_name || "—"}</td>
                      <td className="border-b border-white/5 px-4 py-4 text-secondary">{notary.phone || "—"}</td>
                      <td className="border-b border-white/5 px-4 py-4 text-secondary">{notary.email || "—"}</td>
                      <td className="border-b border-white/5 px-4 py-4">
                        <Link
                          href={`/dashboard/notarias/${notary.id}`}
                          className="inline-flex items-center rounded-xl border border-primary/20 px-3 py-2 text-xs font-semibold text-primary transition hover:border-primary/40 hover:bg-primary/5"
                        >
                          Ver detalle
                        </Link>
                      </td>
                    </tr>
                  ))
                : null}
            </tbody>
          </table>
        </div>

        <div className="mt-5 flex flex-col gap-3 border-t border-white/10 pt-4 text-sm text-secondary sm:flex-row sm:items-center sm:justify-between">
          <p>
            Mostrando {paginatedNotaries.length} de {filteredNotaries.length} resultados · Página {currentPage} de {totalPages}
          </p>
          <div className="flex items-center gap-2">
            <div
              onClick={() => setCurrentPage((page) => Math.max(1, page - 1))}
              className={`inline-flex select-none items-center rounded-xl px-3 py-2 font-semibold ${
                currentPage === 1
                  ? "cursor-not-allowed border border-white/10 text-secondary/50"
                  : "cursor-pointer border border-primary/20 text-primary hover:border-primary/40 hover:bg-primary/5"
              }`}
            >
              Anterior
            </div>
            <div
              onClick={() => setCurrentPage((page) => Math.min(totalPages, page + 1))}
              className={`inline-flex select-none items-center rounded-xl px-3 py-2 font-semibold ${
                currentPage >= totalPages
                  ? "cursor-not-allowed border border-white/10 text-secondary/50"
                  : "cursor-pointer border border-primary/20 text-primary hover:border-primary/40 hover:bg-primary/5"
              }`}
            >
              Siguiente
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
```

## File: components/notaries/notary-crm-workspace.tsx
```typescript
"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { ArrowLeft, Clock3, Save, ShieldCheck, UserRound } from "lucide-react";
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
] as const;

const priorities = ["baja", "media", "alta", "crítica"] as const;
const potentials = ["bajo", "medio", "alto", "estratégico"] as const;
const tabs = ["Gestión", "Nueva gestión", "Historial"] as const;
type WorkspaceTab = (typeof tabs)[number];

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
  const [activeTab, setActiveTab] = useState<WorkspaceTab>("Gestión");
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

  async function handleSave() {
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

  async function handleAddActivity() {
    setIsAddingActivity(true);
    setFeedback(null);
    setError(null);
    try {
      await createCommercialActivity(notaryId, activityState);
      await loadWorkspace();
      setActivityState({
        ...emptyActivity,
        occurred_at: getCurrentBogotaDateTimeLocalValue(),
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
        <div className="space-y-5">
          <Link href="/dashboard/comercial" className="inline-flex items-center gap-2 text-sm font-semibold text-primary">
            <ArrowLeft className="h-4 w-4" />
            Volver a Comercial
          </Link>

          <div>
            <h1 className="text-3xl font-semibold tracking-[-0.05em] text-primary sm:text-4xl">
              {notary.notary_label} · {notary.municipality}
            </h1>
          </div>

          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <div className="ep-card-muted rounded-[1.3rem] p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-secondary">Estado CRM</p>
              <p className="mt-2 text-lg font-semibold text-primary">{notary.commercial_status}</p>
            </div>
            <div className="ep-card-muted rounded-[1.3rem] p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-secondary">Prioridad</p>
              <p className="mt-2 text-lg font-semibold text-primary">{notary.priority}</p>
            </div>
            <div className="ep-card-muted rounded-[1.3rem] p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-secondary">Responsable</p>
              <p className="mt-2 text-lg font-semibold text-primary">{notary.commercial_owner_display || "Sin asignar"}</p>
            </div>
            <div className="rounded-[1.3rem] bg-primary p-4 text-white shadow-panel">
              <p className="text-xs uppercase tracking-[0.2em] text-white/70">Gestiones</p>
              <p className="mt-2 text-lg font-semibold">{notary.activity_count}</p>
            </div>
          </div>
        </div>
      </section>

      <section className="ep-card rounded-[2rem] p-4 sm:p-6">
        <div className="border-b border-[var(--border-soft)] pb-4">
          <div className="flex flex-wrap gap-2">
            {tabs.map((tab) => {
              const isActive = tab === activeTab;
              return (
                <button
                  key={tab}
                  type="button"
                  onClick={() => setActiveTab(tab)}
                  className={`rounded-xl px-4 py-2 text-sm font-semibold transition ${
                    isActive ? "bg-primary text-white shadow-panel" : "ep-card-muted text-secondary hover:text-primary"
                  }`}
                >
                  {tab}
                </button>
              );
            })}
          </div>
        </div>

        <div className="pt-6">
          {activeTab === "Gestión" ? (
            <div className="space-y-5">
              <div className="grid gap-4 lg:grid-cols-2">
                <label className="grid gap-2 text-sm font-medium text-primary">Estado comercial
                  <select
                    value={formState.commercial_status}
                    onChange={(event) => updateField("commercial_status", event.target.value)}
                    className="ep-select h-12 rounded-2xl px-4"
                  >
                    {commercialStatuses.map((item) => (
                      <option key={item} value={item}>{item}</option>
                    ))}
                  </select>
                </label>

                <label className="grid gap-2 text-sm font-medium text-primary">Responsable comercial
                  <select
                    value={formState.commercial_owner_user_id?.toString() ?? ""}
                    onChange={(event) => handleOwnerSelection(event.target.value)}
                    className="ep-select h-12 rounded-2xl px-4"
                  >
                    <option value="">Sin asignar por usuario</option>
                    {userOptions.map((user) => (
                      <option key={user.id} value={user.id}>{user.full_name}</option>
                    ))}
                  </select>
                </label>

                <label className="grid gap-2 text-sm font-medium text-primary">Responsable heredado / respaldo
                  <input
                    value={formState.commercial_owner}
                    onChange={(event) => updateField("commercial_owner", event.target.value)}
                    className="ep-input h-12 rounded-2xl px-4"
                  />
                </label>

                <label className="grid gap-2 text-sm font-medium text-primary">Contacto principal
                  <input
                    value={formState.main_contact_name}
                    onChange={(event) => updateField("main_contact_name", event.target.value)}
                    className="ep-input h-12 rounded-2xl px-4"
                  />
                </label>

                <label className="grid gap-2 text-sm font-medium text-primary">Cargo del contacto
                  <input
                    value={formState.main_contact_title}
                    onChange={(event) => updateField("main_contact_title", event.target.value)}
                    className="ep-input h-12 rounded-2xl px-4"
                  />
                </label>

                <label className="grid gap-2 text-sm font-medium text-primary">Celular comercial
                  <input
                    value={formState.commercial_phone}
                    onChange={(event) => updateField("commercial_phone", event.target.value)}
                    className="ep-input h-12 rounded-2xl px-4"
                  />
                </label>

                <label className="grid gap-2 text-sm font-medium text-primary">Correo comercial
                  <input
                    type="email"
                    value={formState.commercial_email}
                    onChange={(event) => updateField("commercial_email", event.target.value)}
                    className="ep-input h-12 rounded-2xl px-4"
                  />
                </label>

                <label className="grid gap-2 text-sm font-medium text-primary">Última gestión
                  <input
                    type="datetime-local"
                    value={formState.last_management_at}
                    onChange={(event) => updateField("last_management_at", event.target.value)}
                    className="ep-input h-12 rounded-2xl px-4"
                  />
                </label>

                <label className="grid gap-2 text-sm font-medium text-primary">Próxima gestión
                  <input
                    type="datetime-local"
                    value={formState.next_management_at}
                    onChange={(event) => updateField("next_management_at", event.target.value)}
                    className="ep-input h-12 rounded-2xl px-4"
                  />
                </label>

                <label className="grid gap-2 text-sm font-medium text-primary">Prioridad
                  <select
                    value={formState.priority}
                    onChange={(event) => updateField("priority", event.target.value)}
                    className="ep-select h-12 rounded-2xl px-4"
                  >
                    {priorities.map((item) => (
                      <option key={item} value={item}>{item}</option>
                    ))}
                  </select>
                </label>

                <label className="grid gap-2 text-sm font-medium text-primary">Potencial
                  <select
                    value={formState.potential}
                    onChange={(event) => updateField("potential", event.target.value)}
                    className="ep-select h-12 rounded-2xl px-4"
                  >
                    <option value="">Sin definir</option>
                    {potentials.map((item) => (
                      <option key={item} value={item}>{item}</option>
                    ))}
                  </select>
                </label>

                <label className="grid gap-2 text-sm font-medium text-primary">Origen del lead
                  <input
                    value={formState.lead_source}
                    onChange={(event) => updateField("lead_source", event.target.value)}
                    className="ep-input h-12 rounded-2xl px-4"
                  />
                </label>
              </div>

              <div className="grid gap-4">
                <label className="grid gap-2 text-sm font-medium text-primary">Notas comerciales
                  <textarea
                    value={formState.commercial_notes}
                    onChange={(event) => updateField("commercial_notes", event.target.value)}
                    rows={4}
                    className="ep-textarea rounded-2xl px-4 py-3"
                  />
                </label>

                <label className="grid gap-2 text-sm font-medium text-primary">Observaciones internas
                  <textarea
                    value={formState.internal_observations}
                    onChange={(event) => updateField("internal_observations", event.target.value)}
                    rows={4}
                    className="ep-textarea rounded-2xl px-4 py-3"
                  />
                </label>
              </div>

              <div className="flex flex-wrap items-center gap-3">
                <button
                  type="button"
                  disabled={isSaving}
                  onClick={() => {
                    void handleSave();
                  }}
                  className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white shadow-panel disabled:cursor-not-allowed disabled:opacity-70"
                >
                  <Save className="h-4 w-4" />
                  {isSaving ? "Guardando..." : "Guardar gestión"}
                </button>
                <p className="text-xs text-secondary">Próxima acción sugerida: {nextActionSummary}</p>
              </div>
            </div>
          ) : null}

          {activeTab === "Nueva gestión" ? (
            <div className="space-y-4">
              <div className="grid gap-4 lg:grid-cols-2">
                <label className="grid gap-2 text-sm font-medium text-primary">Fecha
                  <input
                    type="datetime-local"
                    value={activityState.occurred_at}
                    onChange={(event) => updateActivityField("occurred_at", event.target.value)}
                    className="ep-input h-12 rounded-2xl px-4"
                  />
                </label>

                <label className="grid gap-2 text-sm font-medium text-primary">Tipo de gestión
                  <input
                    value={activityState.management_type}
                    onChange={(event) => updateActivityField("management_type", event.target.value)}
                    className="ep-input h-12 rounded-2xl px-4"
                  />
                </label>

                <label className="grid gap-2 text-sm font-medium text-primary">Responsable
                  <select
                    value={activityState.responsible_user_id?.toString() ?? ""}
                    onChange={(event) => handleActivityResponsibleSelection(event.target.value)}
                    className="ep-select h-12 rounded-2xl px-4"
                  >
                    <option value="">Sin usuario asignado</option>
                    {userOptions.map((user) => (
                      <option key={user.id} value={user.id}>{user.full_name}</option>
                    ))}
                  </select>
                </label>

                <label className="grid gap-2 text-sm font-medium text-primary">Responsable textual
                  <input
                    value={activityState.responsible}
                    onChange={(event) => updateActivityField("responsible", event.target.value)}
                    className="ep-input h-12 rounded-2xl px-4"
                  />
                </label>

                <label className="grid gap-2 text-sm font-medium text-primary lg:col-span-2">Comentario
                  <textarea
                    value={activityState.comment}
                    onChange={(event) => updateActivityField("comment", event.target.value)}
                    rows={4}
                    className="ep-textarea rounded-2xl px-4 py-3"
                  />
                </label>

                <label className="grid gap-2 text-sm font-medium text-primary">Resultado
                  <input
                    value={activityState.result}
                    onChange={(event) => updateActivityField("result", event.target.value)}
                    className="ep-input h-12 rounded-2xl px-4"
                  />
                </label>

                <label className="grid gap-2 text-sm font-medium text-primary">Próxima acción
                  <input
                    value={activityState.next_action}
                    onChange={(event) => updateActivityField("next_action", event.target.value)}
                    className="ep-input h-12 rounded-2xl px-4"
                  />
                </label>
              </div>

              <button
                type="button"
                disabled={isAddingActivity}
                onClick={() => {
                  void handleAddActivity();
                }}
                className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white shadow-panel disabled:cursor-not-allowed disabled:opacity-70"
              >
                <UserRound className="h-4 w-4" />
                {isAddingActivity ? "Agregando..." : "Agregar gestión"}
              </button>
            </div>
          ) : null}

          {activeTab === "Historial" ? (
            <div className="space-y-6">
              <div>
                <div className="mb-4 flex items-center gap-2">
                  <Clock3 className="h-5 w-5 text-primary" />
                  <h2 className="text-xl font-semibold text-primary">Gestiones anteriores</h2>
                </div>
                <div className="space-y-3">
                  {notary.commercial_activities.length === 0 ? (
                    <div className="ep-card-muted rounded-[1.4rem] px-4 py-4 text-sm text-secondary">Sin gestiones registradas</div>
                  ) : null}
                  {notary.commercial_activities.map((activity) => (
                    <div key={activity.id} className="ep-card-soft rounded-[1.5rem] p-4">
                      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                        <p className="text-sm font-semibold text-primary">{activity.management_type}</p>
                        <span className="text-xs text-secondary">{formatDateTime(activity.occurred_at, { strategy: "bogota" })}</span>
                      </div>
                      <p className="mt-2 text-sm text-secondary">Responsable: {activity.responsible_user_name || activity.responsible || "Sin definir"}</p>
                      {activity.comment ? <p className="mt-2 text-sm text-secondary">Comentario: {activity.comment}</p> : null}
                      {activity.result ? <p className="mt-2 text-sm text-secondary">Resultado: {activity.result}</p> : null}
                      {activity.next_action ? <p className="mt-2 text-sm text-secondary">Próxima acción: {activity.next_action}</p> : null}
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <div className="mb-4 flex items-center gap-2">
                  <ShieldCheck className="h-5 w-5 text-primary" />
                  <h2 className="text-xl font-semibold text-primary">Cambios relevantes</h2>
                </div>
                <div className="space-y-3">
                  {notary.crm_audit_logs.length === 0 ? (
                    <div className="ep-card-muted rounded-[1.4rem] px-4 py-4 text-sm text-secondary">No hay eventos de auditoría registrados todavía.</div>
                  ) : null}
                  {notary.crm_audit_logs.map((item) => (
                    <div key={item.id} className="ep-card-soft rounded-[1.5rem] p-4">
                      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                        <p className="text-sm font-semibold text-primary">{auditLabel(item.event_type, item.field_name)}</p>
                        <span className="text-xs text-secondary">{formatDateTime(item.created_at, { strategy: "bogota" })}</span>
                      </div>
                      <p className="mt-2 text-sm text-secondary">Actor: {item.actor_user_name || "Sistema"}</p>
                      {item.old_value || item.new_value ? (
                        <p className="mt-2 text-sm text-secondary">{item.old_value || "-"} → {item.new_value || "-"}</p>
                      ) : null}
                      {item.comment ? <p className="mt-2 text-sm text-secondary">{item.comment}</p> : null}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : null}

          {feedback ? <div className="mt-5 ep-kpi-success rounded-2xl px-4 py-3 text-sm">{feedback}</div> : null}
          {error ? <div className="mt-5 ep-kpi-critical rounded-2xl px-4 py-3 text-sm">{error}</div> : null}
        </div>
      </section>
    </div>
  );
}
```

## File: components/notaries/notary-detail-workspace.tsx
```typescript
"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { ArrowLeft } from "lucide-react";
import { getNotary, getUserOptions, updateNotary, type NotaryDetail, type NotaryPayload, type UserOption } from "@/lib/api";

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
    return `${notary.notary_label} · ${notary.municipality}`;
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
```

## File: components/persons/legal-entity-lookup.tsx
```typescript
"use client";

import { useState } from "react";
import { Search } from "lucide-react";
import {
  searchLegalEntities,
  type LegalEntityPayload,
  type LegalEntityRecord,
} from "@/lib/legal-entities";

export type { LegalEntityPayload, LegalEntityRecord } from "@/lib/legal-entities";

type LegalEntityLookupProps = {
  onPick: (entity: LegalEntityRecord) => void;
  onNotFound: (entity: LegalEntityPayload) => void;
};

function blankEntityDraft(seed?: Partial<LegalEntityPayload>): LegalEntityPayload {
  return {
    nit: "",
    name: "",
    legal_representative: "",
    municipality: "",
    address: "",
    phone: "",
    email: "",
    ...seed,
  };
}

function EntityField({
  label,
  value,
  onChange,
  type = "text",
  required = false,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  type?: string;
  required?: boolean;
}) {
  return (
    <label className="flex flex-col gap-1">
      <span className="text-sm font-medium text-primary">
        {label}
        {required ? " *" : ""}
      </span>
      <input
        type={type}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="ep-input h-11 rounded-xl px-3"
      />
    </label>
  );
}

export function LegalEntityLookup({ onPick, onNotFound }: LegalEntityLookupProps) {
  const [searchText, setSearchText] = useState("");
  const [results, setResults] = useState<LegalEntityRecord[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [draftEntity, setDraftEntity] = useState<LegalEntityPayload>(() => blankEntityDraft());

  function openCreateForm() {
    setDraftEntity((current) =>
      blankEntityDraft({
        ...current,
        nit: current.nit || searchText,
        name: current.name || searchText,
      }),
    );
    setShowCreateForm(true);
    setError(null);
  }

  async function runLookup() {
    setIsLoading(true);
    setError(null);
    setShowCreateForm(false);
    try {
      const data = await searchLegalEntities(searchText);
      const safeResults = Array.isArray(data) ? data : [];
      setResults(safeResults);
      if (safeResults.length === 0) {
        setDraftEntity((current) =>
          blankEntityDraft({
            ...current,
            nit: current.nit || searchText,
            name: current.name || searchText,
          }),
        );
        setShowCreateForm(true);
      }
    } catch (issue) {
      setResults([]);
      setError(issue instanceof Error ? issue.message : "No fue posible buscar la entidad.");
    } finally {
      setIsLoading(false);
    }
  }

  function saveNewEntity() {
    const nextDraft = {
      ...draftEntity,
      nit: draftEntity.nit.trim(),
      name: draftEntity.name.trim(),
      legal_representative: draftEntity.legal_representative?.trim() || "",
      municipality: draftEntity.municipality?.trim() || "",
      address: draftEntity.address?.trim() || "",
      phone: draftEntity.phone?.trim() || "",
      email: draftEntity.email?.trim() || "",
    };

    if (!nextDraft.nit || !nextDraft.name) {
      setError("Completa el NIT y el nombre de la entidad.");
      return;
    }

    onNotFound(nextDraft);
  }

  return (
    <div className="ep-card-muted rounded-[1.5rem] p-4 space-y-4">
      <div className="grid gap-3 lg:grid-cols-[minmax(0,1fr)_auto]">
        <input
          value={searchText}
          onChange={(event) => setSearchText(event.target.value)}
          placeholder="Buscar por NIT o nombre"
          className="ep-input h-11 rounded-xl px-3"
        />
        <button
          type="button"
          onClick={() => void runLookup()}
          className="inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2 text-sm font-semibold text-white"
        >
          <Search className="h-4 w-4" />
          Buscar
        </button>
      </div>

      <div className="space-y-3">
        {isLoading ? <p className="text-sm text-secondary">Buscando entidad...</p> : null}
        {error ? <p className="text-sm text-rose-500">{error}</p> : null}

        {!isLoading && results.length > 0 ? (
          <div className="space-y-2">
            <p className="text-sm font-medium text-primary">Resultados encontrados</p>
            {results.map((entity) => (
              <button
                key={entity.id}
                type="button"
                onClick={() => onPick(entity)}
                className="flex w-full flex-col items-start justify-between rounded-xl border border-[var(--line)] px-3 py-3 text-left hover:bg-[var(--panel)]"
              >
                <p className="text-sm font-semibold text-primary">{entity.name || "Sin nombre"}</p>
                <p className="text-xs text-secondary">{entity.nit || "Sin NIT"}{entity.municipality ? ` · ${entity.municipality}` : ""}</p>
              </button>
            ))}
            <button
              type="button"
              onClick={openCreateForm}
              className="inline-flex items-center gap-2 text-sm font-semibold text-primary"
            >
              No encontré la entidad
            </button>
          </div>
        ) : null}

        {!isLoading && !error && results.length === 0 && !showCreateForm ? (
          <p className="text-sm text-secondary">Sin resultados todavía.</p>
        ) : null}

        {showCreateForm ? (
          <div className="space-y-4 rounded-[1.25rem] border border-[var(--line)] bg-[var(--panel)] p-4">
            <div>
              <p className="text-sm font-semibold text-primary">Crear nueva entidad jurídica</p>
              <p className="mt-1 text-sm text-secondary">Completa los datos para guardar y usar esta entidad.</p>
            </div>

            <div className="grid gap-3 lg:grid-cols-2">
              <EntityField
                label="NIT"
                value={draftEntity.nit}
                required
                onChange={(value) => setDraftEntity((current) => ({ ...current, nit: value }))}
              />
              <EntityField
                label="Nombre"
                value={draftEntity.name}
                required
                onChange={(value) => setDraftEntity((current) => ({ ...current, name: value }))}
              />
              <EntityField
                label="Representante legal"
                value={draftEntity.legal_representative || ""}
                onChange={(value) => setDraftEntity((current) => ({ ...current, legal_representative: value }))}
              />
              <EntityField
                label="Municipio"
                value={draftEntity.municipality || ""}
                onChange={(value) => setDraftEntity((current) => ({ ...current, municipality: value }))}
              />
              <EntityField
                label="Dirección"
                value={draftEntity.address || ""}
                onChange={(value) => setDraftEntity((current) => ({ ...current, address: value }))}
              />
              <EntityField
                label="Teléfono"
                value={draftEntity.phone || ""}
                onChange={(value) => setDraftEntity((current) => ({ ...current, phone: value }))}
              />
              <EntityField
                label="Email"
                type="email"
                value={draftEntity.email || ""}
                onChange={(value) => setDraftEntity((current) => ({ ...current, email: value }))}
              />
            </div>

            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => void saveNewEntity()}
                className="inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2 text-sm font-semibold text-white"
              >
                Guardar
              </button>
              <button
                type="button"
                onClick={() => setShowCreateForm(false)}
                className="inline-flex items-center gap-2 text-sm font-semibold text-primary"
              >
                Volver a buscar
              </button>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}
```

## File: components/persons/person-lookup.tsx
```typescript
"use client";

import { useState } from "react";
import { Search } from "lucide-react";
import { lookupPersons, type PersonPayload, type PersonRecord } from "@/lib/document-flow";

const maritalStatusOptions = [
  "Soltero(a)",
  "Casado(a)",
  "Unión marital de hecho",
  "Divorciado(a)",
  "Viudo(a)",
  "Otro",
];

const professionOptions = [
  "Abogado(a)",
  "Administrador(a)",
  "Comerciante",
  "Contador(a)",
  "Docente",
  "Economista",
  "Enfermero(a)",
  "Independiente",
  "Ingeniero(a)",
  "Médico(a)",
  "Pensionado(a)",
  "Servidor(a) público(a)",
  "Tecnólogo(a)",
  "Otro",
];

type PersonLookupProps = {
  onPick: (person: PersonRecord) => void;
  onNotFound: (person: PersonPayload) => void;
};

function blankPersonDraft(seed?: Partial<PersonPayload>): PersonPayload {
  return {
    document_type: "CC",
    document_number: "",
    full_name: "",
    sex: "",
    nationality: "Colombiana",
    marital_status: "",
    profession: "",
    municipality: "",
    is_transient: false,
    phone: "",
    address: "",
    email: "",
    metadata_json: "{}",
    ...seed,
  };
}

function PersonField({
  label,
  value,
  onChange,
  type = "text",
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  type?: string;
}) {
  return (
    <label className="flex flex-col gap-1">
      <span className="text-sm font-medium text-primary">{label}</span>
      <input
        type={type}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="ep-input h-11 rounded-xl px-3"
      />
    </label>
  );
}

function SelectField({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: string[];
}) {
  return (
    <label className="flex flex-col gap-1">
      <span className="text-sm font-medium text-primary">{label}</span>
      <select
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="ep-select h-11 rounded-xl px-3"
      >
        <option value="">Selecciona una opción</option>
        {options.map((item) => (
          <option key={item} value={item}>
            {item}
          </option>
        ))}
      </select>
    </label>
  );
}

export function PersonLookup({ onPick, onNotFound }: PersonLookupProps) {
  const [documentType, setDocumentType] = useState("CC");
  const [documentNumber, setDocumentNumber] = useState("");
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<PersonRecord[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [draftPerson, setDraftPerson] = useState<PersonPayload>(() => blankPersonDraft());
  const [maritalStatusChoice, setMaritalStatusChoice] = useState("");
  const [maritalStatusCustom, setMaritalStatusCustom] = useState("");
  const [professionChoice, setProfessionChoice] = useState("");
  const [professionCustom, setProfessionCustom] = useState("");

  function syncDerivedFields(nextDraft: PersonPayload) {
    const nextMaritalStatus = nextDraft.marital_status || "";
    const nextProfession = nextDraft.profession || "";
    const nextMaritalChoice = maritalStatusOptions.includes(nextMaritalStatus) && nextMaritalStatus !== "Otro"
      ? nextMaritalStatus
      : nextMaritalStatus
        ? "Otro"
        : "";
    const nextProfessionChoice = professionOptions.includes(nextProfession) && nextProfession !== "Otro"
      ? nextProfession
      : nextProfession
        ? "Otro"
        : "";

    setMaritalStatusChoice(nextMaritalChoice);
    setMaritalStatusCustom(nextMaritalChoice === "Otro" ? nextMaritalStatus : "");
    setProfessionChoice(nextProfessionChoice);
    setProfessionCustom(nextProfessionChoice === "Otro" ? nextProfession : "");
  }

  function openCreateForm() {
    setDraftPerson((current) => {
      const nextDraft = blankPersonDraft({
        ...current,
        document_type: documentType || current.document_type,
        document_number: documentNumber || current.document_number,
        full_name: query || current.full_name,
      });
      syncDerivedFields(nextDraft);
      return nextDraft;
    });
    setShowCreateForm(true);
    setError(null);
  }

  async function runLookup() {
    setIsLoading(true);
    setError(null);
    setShowCreateForm(false);
    try {
      const data = await lookupPersons({ document_type: documentType, document_number: documentNumber, q: query });
      const safeResults = Array.isArray(data) ? data : [];
      setResults(safeResults);
      if (safeResults.length === 0) {
        const nextDraft = blankPersonDraft({
          document_type: documentType,
          document_number: documentNumber,
          full_name: query,
        });
        setDraftPerson(nextDraft);
        syncDerivedFields(nextDraft);
        setShowCreateForm(true);
      }
    } catch (issue) {
      setResults([]);
      setError(issue instanceof Error ? issue.message : "No fue posible buscar la persona.");
    } finally {
      setIsLoading(false);
    }
  }

  function saveNewPerson() {
    const nextDraft = {
      ...draftPerson,
      document_type: draftPerson.document_type.trim(),
      document_number: draftPerson.document_number.trim(),
      full_name: draftPerson.full_name.trim(),
      marital_status: maritalStatusChoice === "Otro" ? maritalStatusCustom.trim() : maritalStatusChoice,
      profession: professionChoice === "Otro" ? professionCustom.trim() : professionChoice,
      metadata_json: draftPerson.metadata_json || "{}",
    };

    if (!nextDraft.document_type || !nextDraft.document_number || !nextDraft.full_name || !nextDraft.marital_status || !nextDraft.municipality) {
      setError("Completa el tipo, número, nombre, estado civil y municipio de la persona.");
      return;
    }

    onNotFound(nextDraft);
  }

  return (
    <div className="ep-card-muted rounded-[1.5rem] p-4 space-y-4">
      <div className="grid gap-3 lg:grid-cols-[110px_minmax(0,1fr)_minmax(0,1fr)_auto]">
        <select
          value={documentType}
          onChange={(event) => setDocumentType(event.target.value)}
          className="ep-select h-11 rounded-xl px-3"
        >
          {["CC", "CE", "TI", "PP", "NIT"].map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
        <input
          value={documentNumber}
          onChange={(event) => setDocumentNumber(event.target.value)}
          placeholder="Número de documento"
          className="ep-input h-11 rounded-xl px-3"
        />
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Buscar por nombre"
          className="ep-input h-11 rounded-xl px-3"
        />
        <button
          type="button"
          onClick={() => void runLookup()}
          className="inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2 text-sm font-semibold text-white"
        >
          <Search className="h-4 w-4" />
          Buscar
        </button>
      </div>

      <div className="space-y-3">
        {isLoading ? <p className="text-sm text-secondary">Buscando persona...</p> : null}
        {error ? <p className="text-sm text-rose-500">{error}</p> : null}

        {!isLoading && results.length > 0 ? (
          <div className="space-y-2">
            <p className="text-sm font-medium text-primary">Resultados encontrados</p>
            {results.map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => onPick(item)}
                className="flex w-full items-center justify-between rounded-xl border border-[var(--line)] px-3 py-3 text-left hover:bg-[var(--panel)]"
              >
                <div>
                  <p className="text-sm font-semibold text-primary">{item.full_name || "Sin nombre"}</p>
                  <p className="text-xs text-secondary">
                    {item.document_type || "DOC"} {item.document_number || "Sin número"} · {item.municipality || "Sin municipio"}
                  </p>
                </div>
                <span className="text-xs font-semibold text-primary">Usar este</span>
              </button>
            ))}
            <button
              type="button"
              onClick={openCreateForm}
              className="inline-flex items-center gap-2 text-sm font-semibold text-primary"
            >
              No encontré la persona
            </button>
          </div>
        ) : null}

        {!isLoading && !error && results.length === 0 && !showCreateForm ? (
          <p className="text-sm text-secondary">Sin resultados todavía.</p>
        ) : null}

        {showCreateForm ? (
          <div className="space-y-4 rounded-[1.25rem] border border-[var(--line)] bg-[var(--panel)] p-4">
            <div>
              <p className="text-sm font-semibold text-primary">Crear nueva persona</p>
              <p className="mt-1 text-sm text-secondary">Completa los datos para guardar y usar esta persona en el interviniente.</p>
            </div>

            <div className="grid gap-3 lg:grid-cols-2">
              <label className="flex flex-col gap-1">
                <span className="text-sm font-medium text-primary">Tipo de documento</span>
                <select
                  value={draftPerson.document_type}
                  onChange={(event) => setDraftPerson((current) => ({ ...current, document_type: event.target.value }))}
                  className="ep-select h-11 rounded-xl px-3"
                >
                  {["CC", "CE", "TI", "PP", "NIT"].map((item) => (
                    <option key={item} value={item}>
                      {item}
                    </option>
                  ))}
                </select>
              </label>
              <PersonField
                label="Número de documento"
                value={draftPerson.document_number}
                onChange={(value) => setDraftPerson((current) => ({ ...current, document_number: value }))}
              />
              <PersonField
                label="Nombre completo"
                value={draftPerson.full_name}
                onChange={(value) => setDraftPerson((current) => ({ ...current, full_name: value }))}
              />
              <label className="flex flex-col gap-1">
                <span className="text-sm font-medium text-primary">Sexo</span>
                <select
                  value={draftPerson.sex || ""}
                  onChange={(event) => setDraftPerson((current) => ({ ...current, sex: event.target.value }))}
                  className="ep-select h-11 rounded-xl px-3"
                >
                  <option value="">Sin definir</option>
                  {["F", "M", "No especifica"].map((item) => (
                    <option key={item} value={item}>
                      {item}
                    </option>
                  ))}
                </select>
              </label>
              <PersonField
                label="Nacionalidad"
                value={draftPerson.nationality || ""}
                onChange={(value) => setDraftPerson((current) => ({ ...current, nationality: value }))}
              />
              <div className="space-y-1">
                <SelectField
                  label="Estado civil"
                  value={maritalStatusChoice}
                  options={maritalStatusOptions}
                  onChange={(value) => {
                    setMaritalStatusChoice(value);
                    if (value !== "Otro") {
                      setMaritalStatusCustom("");
                    }
                    setDraftPerson((current) => ({
                      ...current,
                      marital_status: value === "Otro" ? maritalStatusCustom.trim() : value,
                    }));
                  }}
                />
                {maritalStatusChoice === "Otro" ? (
                  <input
                    value={maritalStatusCustom}
                    onChange={(event) => {
                      const value = event.target.value;
                      setMaritalStatusCustom(value);
                      setDraftPerson((current) => ({ ...current, marital_status: value }));
                    }}
                    placeholder="Especifica..."
                    className="ep-input h-11 rounded-xl px-3"
                  />
                ) : null}
              </div>
              <div className="space-y-1">
                <SelectField
                  label="Profesión u oficio"
                  value={professionChoice}
                  options={professionOptions}
                  onChange={(value) => {
                    setProfessionChoice(value);
                    if (value !== "Otro") {
                      setProfessionCustom("");
                    }
                    setDraftPerson((current) => ({
                      ...current,
                      profession: value === "Otro" ? professionCustom.trim() : value,
                    }));
                  }}
                />
                {professionChoice === "Otro" ? (
                  <input
                    value={professionCustom}
                    onChange={(event) => {
                      const value = event.target.value;
                      setProfessionCustom(value);
                      setDraftPerson((current) => ({ ...current, profession: value }));
                    }}
                    placeholder="Especifica..."
                    className="ep-input h-11 rounded-xl px-3"
                  />
                ) : null}
              </div>
              <PersonField
                label="Municipio de domicilio"
                value={draftPerson.municipality || ""}
                onChange={(value) => setDraftPerson((current) => ({ ...current, municipality: value }))}
              />
              <PersonField
                label="Teléfono"
                value={draftPerson.phone || ""}
                onChange={(value) => setDraftPerson((current) => ({ ...current, phone: value }))}
              />
              <PersonField
                label="Email"
                type="email"
                value={draftPerson.email || ""}
                onChange={(value) => setDraftPerson((current) => ({ ...current, email: value }))}
              />
            </div>

            <div className="flex flex-col gap-1">
              <span className="text-sm font-medium text-primary">Dirección</span>
              <textarea
                value={draftPerson.address || ""}
                onChange={(event) => setDraftPerson((current) => ({ ...current, address: event.target.value }))}
                className="ep-input min-h-[96px] rounded-2xl px-4 py-3"
              />
            </div>

            <label className="flex items-center gap-3 rounded-2xl bg-[var(--panel-soft)] px-4 py-3 text-sm text-secondary">
              <input
                type="checkbox"
                checked={Boolean(draftPerson.is_transient)}
                onChange={(event) => setDraftPerson((current) => ({ ...current, is_transient: event.target.checked }))}
              />
              ¿Está de tránsito?
            </label>

            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => void saveNewPerson()}
                className="inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2 text-sm font-semibold text-white"
              >
                Guardar y usar
              </button>
              <button
                type="button"
                onClick={() => setShowCreateForm(false)}
                className="inline-flex items-center gap-2 text-sm font-semibold text-primary"
              >
                Volver a buscar
              </button>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}
```

## File: components/process/process-placeholder.tsx
```typescript
"use client";

import { Layers3 } from "lucide-react";

export function ProcessPlaceholder({
  section,
  title,
  copy,
}: {
  section: string;
  title: string;
  copy: string;
}) {
  return (
    <div className="space-y-6">
      <section className="rounded-[2rem] border border-white/90 bg-white p-6 shadow-panel">
        <div className="max-w-3xl">
          <p className="text-sm font-semibold uppercase tracking-[0.22em] text-accent">{section}</p>
          <h1 className="mt-3 text-3xl font-semibold tracking-[-0.05em] text-primary sm:text-4xl">{title}</h1>
          <p className="mt-4 text-base leading-7 text-secondary">{copy}</p>
        </div>
      </section>

      <section className="rounded-[2rem] border border-white/90 bg-white p-6 shadow-panel">
        <div className="flex items-start gap-4">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10 text-primary">
            <Layers3 className="h-6 w-6" />
          </div>
          <div>
            <h2 className="text-2xl font-semibold text-primary">Base preparada</h2>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-secondary">La navegación ya quedó ordenada alrededor del proceso documental. Este espacio está listo para conectar siguientes paquetes sin romper estructura ni UX.</p>
          </div>
        </div>
      </section>
    </div>
  );
}
```

## File: components/roles/roles-workspace.tsx
```typescript
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

function Toggle({ value, onChange, disabled = false }: { value: boolean; onChange: (v: boolean) => void; disabled?: boolean }) {
  const isChecked = value === true;
  return (
    <div
      role="switch"
      aria-checked={isChecked}
      aria-disabled={disabled}
      onClick={() => {
        if (!disabled) {
          onChange(!isChecked);
        }
      }}
      className={`relative h-6 w-11 rounded-full transition-[background-color] duration-200 ${
        disabled ? "cursor-not-allowed opacity-60" : "cursor-pointer"
      } ${isChecked ? "bg-[#10B981]" : "bg-[#CBD5E1]"}`}
    >
      <div
        className={`absolute top-[3px] h-[18px] w-[18px] rounded-full bg-white shadow-[0_1px_3px_rgba(0,0,0,0.2)] transition-transform duration-200 ease-in-out ${
          isChecked ? "translate-x-[22px]" : "translate-x-[2px]"
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
                                                <Toggle
                                                  value={item.can_access === true}
                                                  disabled={!canEditRole || isSavingPermissions}
                                                  onChange={() => togglePermission(item.module_code)}
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
```

## File: components/system/system-status-workspace.tsx
```typescript
"use client";

import { type ReactNode, useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Database,
  Globe,
  LockKeyhole,
  RefreshCw,
  ServerCog,
  ShieldAlert,
  Zap,
} from "lucide-react";
import { getExecutiveDashboard, type DashboardAlert, type DashboardSystemStatusItem, type ExecutiveDashboard } from "@/lib/api";
import { LiveClock } from "@/components/ui/live-clock";
import { formatDateTime } from "@/lib/datetime";

type ServiceTone = "online" | "warning" | "degraded" | "offline";

function normalizeServiceStatus(status: string): ServiceTone {
  const normalized = status.trim().toLowerCase();
  if (["ok", "online", "healthy", "success"].includes(normalized)) return "online";
  if (["warning"].includes(normalized)) return "warning";
  if (["critical", "offline", "down"].includes(normalized)) return "offline";
  return "degraded";
}

function serviceStatusLabel(status: ServiceTone) {
  if (status === "online") return "Online";
  if (status === "warning") return "Warning";
  if (status === "offline") return "Offline";
  return "Degraded";
}

function serviceBadgeClasses(status: ServiceTone) {
  if (status === "online") return "bg-emerald-500/12 text-emerald-700 ring-1 ring-emerald-500/25 dark:text-emerald-300";
  if (status === "warning") return "bg-amber-500/12 text-amber-700 ring-1 ring-amber-500/25 dark:text-amber-300";
  if (status === "offline") return "bg-rose-500/14 text-rose-700 ring-1 ring-rose-500/25 dark:text-rose-300";
  return "bg-sky-500/12 text-sky-700 ring-1 ring-sky-500/25 dark:text-sky-300";
}

function serviceDotClasses(status: ServiceTone) {
  if (status === "online") return "bg-emerald-500";
  if (status === "warning") return "bg-amber-500";
  if (status === "offline") return "bg-rose-500";
  return "bg-sky-500";
}

function alertClasses(level: string) {
  const normalized = level.trim().toLowerCase();
  if (normalized === "critical") return "ep-kpi-critical";
  if (normalized === "warning") return "ep-kpi-warning";
  return "ep-kpi-success";
}

function resolveIcon(key: string) {
  switch (key) {
    case "backend":
      return ServerCog;
    case "frontend":
      return Globe;
    case "database":
      return Database;
    case "auth":
      return LockKeyhole;
    default:
      return Activity;
  }
}

function ServiceCard({ item }: { item: DashboardSystemStatusItem }) {
  const Icon = resolveIcon(item.key);
  const tone = normalizeServiceStatus(item.status);

  return (
    <article className="ep-card-soft rounded-[1.5rem] p-5">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <div className="rounded-2xl bg-primary/10 p-3">
            <Icon className="h-5 w-5 text-primary" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className={`h-2.5 w-2.5 rounded-full ${serviceDotClasses(tone)}`} />
              <p className="text-sm font-semibold text-primary">{item.label}</p>
            </div>
            <p className="mt-2 text-sm leading-6 text-secondary">{item.detail}</p>
          </div>
        </div>
        <span className={`rounded-full px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] ${serviceBadgeClasses(tone)}`}>
          {serviceStatusLabel(tone)}
        </span>
      </div>
    </article>
  );
}

function SummaryMetric({ label, value, tone }: { label: string; value: ReactNode; tone?: ServiceTone }) {
  return (
    <div className="ep-card-muted rounded-[1.25rem] px-4 py-4">
      <p className="text-[11px] uppercase tracking-[0.18em] text-secondary">{label}</p>
      <div className="mt-2 flex items-center gap-2">
        {tone ? <span className={`h-2.5 w-2.5 rounded-full ${serviceDotClasses(tone)}`} /> : null}
        <p className="text-sm font-semibold text-primary">{value}</p>
      </div>
    </div>
  );
}

export function SystemStatusWorkspace() {
  const [dashboard, setDashboard] = useState<ExecutiveDashboard | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setIsLoading(true);
      setError(null);
      try {
        const data = await getExecutiveDashboard();
        if (!cancelled) {
          setDashboard(data);
        }
      } catch (loadError) {
        if (!cancelled) {
          setError(loadError instanceof Error ? loadError.message : "No fue posible cargar el System Status.");
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, []);

  const serviceItems = useMemo(() => {
    if (!dashboard) return [];
    const ordered = ["backend", "frontend", "database", "auth"];
    return ordered
      .map((key) => dashboard.system_status.find((item) => item.key === key))
      .filter((item): item is DashboardSystemStatusItem => Boolean(item));
  }, [dashboard]);

  const globalTone = useMemo<ServiceTone>(() => {
    if (!dashboard) return "degraded";
    const tones = serviceItems.map((item) => normalizeServiceStatus(item.status));
    if (tones.includes("offline")) return "offline";
    if (tones.includes("warning")) return "warning";
    if (tones.includes("degraded")) return "degraded";
    return "online";
  }, [dashboard, serviceItems]);

  const globalStatusText = useMemo(() => {
    if (globalTone === "online") return "Sistema estable";
    if (globalTone === "warning") return "Sistema con advertencias";
    if (globalTone === "offline") return "Sistema con fallas críticas";
    return "Sistema degradado";
  }, [globalTone]);

  const alertCount = dashboard?.critical_alerts.length ?? 0;
  const leadingAlert = dashboard?.critical_alerts[0];

  if (isLoading && !dashboard) {
    return <div className="ep-card rounded-[2rem] p-6 text-secondary">Cargando estado del sistema...</div>;
  }

  if (error && !dashboard) {
    return <div className="ep-kpi-critical rounded-[2rem] px-6 py-5 text-sm">{error}</div>;
  }

  if (!dashboard) {
    return <div className="ep-card rounded-[2rem] p-6 text-secondary">No hay información disponible.</div>;
  }

  return (
    <div className="space-y-6">
      <section className="ep-card rounded-[2rem] p-6 sm:p-7">
        <div className="grid gap-5 xl:grid-cols-[minmax(0,1.2fr)_minmax(320px,0.8fr)]">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-primary/10 bg-primary/5 px-3 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-primary">
              <ShieldAlert className="h-3.5 w-3.5" />
              System Status
            </div>
            <div className="mt-5 flex flex-wrap items-center gap-3">
              <span className={`rounded-full px-3 py-1.5 text-[11px] font-semibold uppercase tracking-[0.16em] ${serviceBadgeClasses(globalTone)}`}>
                {globalStatusText}
              </span>
              <span className="text-sm text-secondary">{formatDateTime(dashboard.generated_at)}</span>
            </div>
            <h1 className="mt-4 text-3xl font-semibold tracking-[-0.05em] text-primary sm:text-[2.2rem]">Estado general del entorno y servicios clave.</h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-secondary">
              Lectura rápida para backend, frontend, base de datos y autenticación.
            </p>
          </div>

          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
            <SummaryMetric label="Entorno" value={globalStatusText} tone={globalTone} />
            <SummaryMetric label="Hora actual" value={<LiveClock />} />
            <SummaryMetric label="Último corte" value={formatDateTime(dashboard.generated_at)} />
            <SummaryMetric label="Alertas críticas" value={String(alertCount)} tone={alertCount > 0 ? "warning" : "online"} />
            <SummaryMetric label="Severidad principal" value={leadingAlert?.title ?? "Sin alertas activas"} tone={leadingAlert ? normalizeServiceStatus(leadingAlert.level === "critical" ? "offline" : "warning") : "online"} />
          </div>
        </div>

        <div className="mt-5 rounded-[1.4rem] border border-line bg-[color:rgb(var(--panel-strong))] px-4 py-4">
          <div className="flex items-start gap-3">
            <div className="rounded-2xl bg-primary/10 p-2.5">
              <Zap className="h-4 w-4 text-primary" />
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.18em] text-secondary">Resumen crítico</p>
              <p className="mt-1 text-sm font-semibold text-primary">{leadingAlert?.title ?? "Sin hallazgos críticos en este corte."}</p>
              <p className="mt-2 text-sm leading-6 text-secondary">{leadingAlert?.detail ?? "Todos los servicios monitoreados responden dentro del estado esperado para esta vista."}</p>
            </div>
          </div>
        </div>
      </section>

      <section className="space-y-4">
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-secondary">Servicios</p>
            <h2 className="mt-1 text-2xl font-semibold text-primary">Estado operativo por componente</h2>
          </div>
          <div className="ep-pill rounded-full px-4 py-2 text-sm text-secondary">Backend · Frontend · Base de datos · Auth</div>
        </div>
        <div className="grid gap-4 xl:grid-cols-2">
          {serviceItems.map((item) => (
            <ServiceCard key={item.key} item={item} />
          ))}
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[minmax(0,0.95fr)_minmax(0,1.05fr)]">
        <article className="ep-card rounded-[1.8rem] p-5 sm:p-6">
          <div className="flex items-center gap-3">
            <div className="rounded-2xl bg-primary/10 p-3">
              <RefreshCw className="h-5 w-5 text-primary" />
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.18em] text-secondary">Sincronización</p>
              <h3 className="mt-1 text-xl font-semibold text-primary">Importación y referencias</h3>
            </div>
          </div>

          <div className="mt-5 grid gap-3">
            <div className="ep-card-muted rounded-[1.35rem] px-4 py-4">
              <p className="text-[11px] uppercase tracking-[0.16em] text-secondary">Última importación relevante</p>
              <p className="mt-2 text-sm font-semibold text-primary">{dashboard.latest_import_reference ?? "Sin referencia disponible"}</p>
            </div>
            <div className="ep-card-muted rounded-[1.35rem] px-4 py-4">
              <p className="text-[11px] uppercase tracking-[0.16em] text-secondary">Piloto visible</p>
              <p className="mt-2 text-sm font-semibold text-primary">{dashboard.pilot_reference ? `${dashboard.pilot_reference.municipality}, ${dashboard.pilot_reference.department}` : "Sin piloto definido"}</p>
            </div>
            <div className="ep-card-muted rounded-[1.35rem] px-4 py-4">
              <p className="text-[11px] uppercase tracking-[0.16em] text-secondary">Observación</p>
              <p className="mt-2 text-sm text-secondary">Esta sección concentra referencias operativas sin competir con el bloque principal de estado.</p>
            </div>
          </div>
        </article>

        <article className="ep-card rounded-[1.8rem] p-5 sm:p-6">
          <div className="flex items-center gap-3">
            <div className="rounded-2xl bg-amber-500/14 p-3">
              <AlertTriangle className="h-5 w-5 text-amber-600 dark:text-amber-300" />
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.18em] text-secondary">Alertas</p>
              <h3 className="mt-1 text-xl font-semibold text-primary">Detalle priorizado</h3>
            </div>
          </div>

          <div className="mt-5 space-y-3">
            {dashboard.critical_alerts.length === 0 ? (
              <div className="ep-card-muted rounded-[1.35rem] px-4 py-4 text-sm text-secondary">Sin alertas activas para el corte actual.</div>
            ) : null}
            {dashboard.critical_alerts.map((alert: DashboardAlert) => (
              <div key={`${alert.level}-${alert.title}`} className={`${alertClasses(alert.level)} rounded-[1.35rem] px-4 py-4`}>
                <div className="flex items-center gap-2">
                  <span className={`h-2.5 w-2.5 rounded-full ${serviceDotClasses(alert.level === "critical" ? "offline" : alert.level === "warning" ? "warning" : "online")}`} />
                  <p className="text-sm font-semibold text-primary">{alert.title}</p>
                </div>
                <p className="mt-2 text-sm leading-6 text-secondary">{alert.detail}</p>
              </div>
            ))}
          </div>
        </article>
      </section>
    </div>
  );
}
```

## File: components/templates/templates-workspace.tsx
```typescript
"use client";

import { FormEvent, useEffect, useState } from "react";
import { FileUp, Save } from "lucide-react";
import { createTemplate, getTemplates, updateTemplate, type TemplateRecord } from "@/lib/document-flow";
import { getNotaries } from "@/lib/api";

async function fileToBase64(file: File) {
  return new Promise<string>((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result).split(",")[1] ?? "");
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

const defaultVariableMap = JSON.stringify(
  {
    NOMBRE_PODERDANTE: "participants.poderdante.full_name",
    NOMBRE_APODERADO: "participants.apoderado.full_name",
    DIA_ELABORACION_ESCRITURA: "act.dia_elaboracion",
    NUMERO_ESCRITURA: "case.official_deed_number",
  },
  null,
  2,
);

const emptyForm = {
  name: "Poder General",
  case_type: "escritura",
  document_type: "Poder General",
  description: "Plantilla piloto de escritura pública tipo Poder General.",
  scope_type: "global",
  notary_id: "",
  is_active: true,
  internal_variable_map_json: defaultVariableMap,
};

export function TemplatesWorkspace() {
  const [templates, setTemplates] = useState<TemplateRecord[]>([]);
  const [notaries, setNotaries] = useState<Array<{ id: number; notary_label: string; municipality: string }>>([]);
  const [selected, setSelected] = useState<TemplateRecord | null>(null);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [form, setForm] = useState(emptyForm);

  useEffect(() => {
    void load();
  }, []);

  async function load() {
    setIsLoading(true);
    setError(null);
    try {
      const [templateData, notaryData] = await Promise.all([getTemplates(), getNotaries()]);
      const safeTemplates = Array.isArray(templateData) ? templateData : [];
      setTemplates(safeTemplates);
      setNotaries(Array.isArray(notaryData) ? notaryData.map((item) => ({ id: item.id, notary_label: item.notary_label || "Sin nombre", municipality: item.municipality || "Sin municipio" })) : []);
      if (safeTemplates.length > 0) {
        selectTemplate(safeTemplates[0]);
      } else {
        setSelected(null);
        setForm(emptyForm);
      }
    } catch (loadError) {
      setTemplates([]);
      setNotaries([]);
      setSelected(null);
      setError(loadError instanceof Error ? loadError.message : "No fue posible cargar las plantillas.");
    } finally {
      setIsLoading(false);
    }
  }

  function selectTemplate(item: TemplateRecord) {
    setSelected(item);
    setForm({
      name: item.name || emptyForm.name,
      case_type: item.case_type || emptyForm.case_type,
      document_type: item.document_type || emptyForm.document_type,
      description: item.description || "",
      scope_type: item.scope_type || emptyForm.scope_type,
      notary_id: item.notary_id ? String(item.notary_id) : "",
      is_active: item.is_active,
      internal_variable_map_json: item.internal_variable_map_json || defaultVariableMap,
    });
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setFeedback(null);
    setError(null);
    setIsSaving(true);
    try {
      const upload = uploadFile ? { filename: uploadFile.name, content_base64: await fileToBase64(uploadFile) } : null;
      const payload = {
        ...form,
        notary_id: form.notary_id ? Number(form.notary_id) : null,
        required_roles: [
          { role_code: "poderdante", label: "Poderdante", is_required: true, step_order: 1 },
          { role_code: "apoderado", label: "Apoderado(a)", is_required: true, step_order: 2 },
        ],
        fields: [
          { field_code: "dia_elaboracion", label: "Día elaboración", field_type: "number", section: "acto", is_required: true, options_json: null, placeholder_key: "DIA_ELABORACION_ESCRITURA", help_text: null, step_order: 1 },
          { field_code: "mes_elaboracion", label: "Mes elaboración", field_type: "text", section: "acto", is_required: true, options_json: null, placeholder_key: "MES_ELABORACION_ESCRITURA", help_text: null, step_order: 2 },
          { field_code: "ano_elaboracion", label: "Año elaboración", field_type: "number", section: "acto", is_required: true, options_json: null, placeholder_key: "ANO_ELABORACION_ESCRITURA", help_text: null, step_order: 3 },
          { field_code: "derechos_notariales", label: "Derechos notariales", field_type: "currency", section: "acto", is_required: true, options_json: null, placeholder_key: "DERECHOS_NOTARIALES", help_text: null, step_order: 4 },
          { field_code: "iva", label: "IVA", field_type: "currency", section: "acto", is_required: true, options_json: null, placeholder_key: "IVA", help_text: null, step_order: 5 },
          { field_code: "aporte_superintendencia", label: "Aporte superintendencia", field_type: "currency", section: "acto", is_required: true, options_json: null, placeholder_key: "APORTE_SUPERINTENDENCIA", help_text: null, step_order: 6 },
          { field_code: "fondo_notariado", label: "Fondo notariado", field_type: "currency", section: "acto", is_required: true, options_json: null, placeholder_key: "FONDO_NOTARIADO", help_text: null, step_order: 7 },
          { field_code: "consecutivos_hojas_papel_notarial", label: "Consecutivos hojas papel notarial", field_type: "text", section: "acto", is_required: true, options_json: null, placeholder_key: "CONSECUTIVOS_HOJAS_PAPEL_NOTARIAL", help_text: null, step_order: 8 },
          { field_code: "extension", label: "Extensión", field_type: "text", section: "acto", is_required: true, options_json: null, placeholder_key: "EXTENSION", help_text: null, step_order: 9 },
        ],
        upload,
      };
      const saved = selected ? await updateTemplate(selected.id, payload) : await createTemplate(payload);
      setSelected(saved);
      setUploadFile(null);
      await load();
      setFeedback("Plantilla guardada correctamente.");
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "No fue posible guardar la plantilla.");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <div className="space-y-6">
      <section className="ep-card rounded-[2rem] p-6">
        <p className="text-sm font-semibold uppercase tracking-[0.22em] text-accent">Plantillas</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-[-0.05em] text-primary">Plantillas documentales reutilizables</h1>
        <p className="mt-3 max-w-3xl text-base leading-7 text-secondary">La plantilla define intervinientes requeridos, campos del acto y variables internas del documento. En este MVP queda lista la base real de Poder General.</p>
      </section>
      <section className="grid gap-6 xl:grid-cols-[360px_minmax(0,1fr)]">
        <aside className="ep-card rounded-[2rem] p-5">
          <div className="flex items-center justify-between gap-3">
            <h2 className="text-xl font-semibold text-primary">Plantillas registradas</h2>
            <button type="button" onClick={() => { setSelected(null); setUploadFile(null); setForm(emptyForm); }} className="text-sm font-semibold text-primary">Nueva</button>
          </div>
          <div className="mt-4 space-y-3">
            {isLoading ? <div className="ep-card-muted rounded-[1.3rem] px-4 py-4 text-sm text-secondary">Cargando plantillas...</div> : null}
            {!isLoading && !error && templates.length === 0 ? <div className="ep-card-muted rounded-[1.3rem] px-4 py-4 text-sm text-secondary">Sin plantillas todavía.</div> : null}
            {templates.map((item) => (
              <button key={item.id} type="button" onClick={() => selectTemplate(item)} className={`block w-full rounded-[1.3rem] border px-4 py-4 text-left ${selected?.id === item.id ? "border-primary/30 bg-primary/8" : "border-[var(--line)]"}`}>
                <p className="text-sm font-semibold text-primary">{item.name || "Plantilla sin nombre"}</p>
                <p className="mt-1 text-xs text-secondary">{item.document_type || "Sin tipo documental"} · {item.is_active ? "Activa" : "Inactiva"}</p>
              </button>
            ))}
          </div>
        </aside>
        <form onSubmit={handleSubmit} className="ep-card rounded-[2rem] p-6 space-y-5">
          <div className="grid gap-4 lg:grid-cols-2">
            <label className="grid gap-2 text-sm font-medium text-primary">Nombre<input value={form.name} onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))} className="ep-input h-12 rounded-2xl px-4" /></label>
            <label className="grid gap-2 text-sm font-medium text-primary">Tipo documental<input value={form.document_type} onChange={(event) => setForm((current) => ({ ...current, document_type: event.target.value }))} className="ep-input h-12 rounded-2xl px-4" /></label>
            <label className="grid gap-2 text-sm font-medium text-primary">Tipo de minuta<input value={form.case_type} onChange={(event) => setForm((current) => ({ ...current, case_type: event.target.value }))} className="ep-input h-12 rounded-2xl px-4" /></label>
            <label className="grid gap-2 text-sm font-medium text-primary">Alcance<select value={form.scope_type} onChange={(event) => setForm((current) => ({ ...current, scope_type: event.target.value }))} className="ep-select h-12 rounded-2xl px-4"><option value="global">Global</option><option value="notary">Por notaría</option></select></label>
            <label className="grid gap-2 text-sm font-medium text-primary">Notaría<select value={form.notary_id} onChange={(event) => setForm((current) => ({ ...current, notary_id: event.target.value }))} className="ep-select h-12 rounded-2xl px-4"><option value="">Todas</option>{notaries.map((item) => <option key={item.id} value={item.id}>{item.notary_label} · {item.municipality}</option>)}</select></label>
            <label className="grid gap-2 text-sm font-medium text-primary">Estado<select value={form.is_active ? "active" : "inactive"} onChange={(event) => setForm((current) => ({ ...current, is_active: event.target.value === "active" }))} className="ep-select h-12 rounded-2xl px-4"><option value="active">Activa</option><option value="inactive">Inactiva</option></select></label>
          </div>
          <label className="grid gap-2 text-sm font-medium text-primary">Descripción<textarea value={form.description} onChange={(event) => setForm((current) => ({ ...current, description: event.target.value }))} rows={3} className="ep-textarea rounded-2xl px-4 py-3" /></label>
          <label className="grid gap-2 text-sm font-medium text-primary">Variables internas<textarea value={form.internal_variable_map_json} onChange={(event) => setForm((current) => ({ ...current, internal_variable_map_json: event.target.value }))} rows={10} className="ep-textarea rounded-2xl px-4 py-3 font-mono text-xs" /></label>
          <label className="ep-card-muted flex items-center justify-between rounded-[1.5rem] px-4 py-4 text-sm text-secondary"><span className="inline-flex items-center gap-2"><FileUp className="h-4 w-4 text-primary" />Archivo .docx base</span><input type="file" accept=".docx" onChange={(event) => setUploadFile(event.target.files?.[0] ?? null)} /></label>
          <div className="grid gap-4 lg:grid-cols-2">
            <div className="ep-card-soft rounded-[1.5rem] p-4"><p className="text-sm font-semibold text-primary">Intervinientes requeridos</p><ul className="mt-3 space-y-2 text-sm text-secondary"><li>Poderdante</li><li>Apoderado(a)</li></ul></div>
            <div className="ep-card-soft rounded-[1.5rem] p-4"><p className="text-sm font-semibold text-primary">Campos del acto</p><p className="mt-3 text-sm leading-6 text-secondary">Día, mes, año, derechos notariales, IVA, aporte superintendencia, fondo notariado, consecutivos de hojas y extensión.</p></div>
          </div>
          {feedback ? <div className="ep-kpi-success rounded-2xl px-4 py-3 text-sm">{feedback}</div> : null}
          {error ? <div className="ep-kpi-critical rounded-2xl px-4 py-3 text-sm">{error}</div> : null}
          <button type="submit" disabled={isSaving} className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white disabled:opacity-60"><Save className="h-4 w-4" />{isSaving ? "Guardando..." : "Guardar plantilla"}</button>
        </form>
      </section>
    </div>
  );
}
```

## File: components/ui/brand-provider.tsx
```typescript
"use client";

import type { CSSProperties, PropsWithChildren } from "react";
import { resolveBranding } from "@/lib/branding";

export function BrandProvider({ children }: PropsWithChildren) {
  const branding = resolveBranding();

  return (
    <div
      style={
        {
          "--primary": branding.primaryColor,
          "--secondary": branding.secondaryColor,
          "--accent": branding.accentColor
        } as CSSProperties
      }
    >
      {children}
    </div>
  );
}
```

## File: components/ui/hybrid-autocomplete.tsx
```typescript
"use client";

import { useMemo } from "react";

export function HybridAutocomplete({ label, value, options = [], onChange, placeholder = "" }: { label: string; value: string; options?: string[]; onChange: (value: string) => void; placeholder?: string }) {
  const safeValue = typeof value === "string" ? value : "";
  const safeOptions = Array.isArray(options) ? options : [];
  const suggestions = useMemo(() => safeOptions.filter((item) => item.toLowerCase().includes(safeValue.toLowerCase())).slice(0, 6), [safeOptions, safeValue]);
  const listId = `${label}-options`.replace(/\s+/g, "-").toLowerCase();

  return (
    <label className="grid gap-2 text-sm font-medium text-primary">
      <span>{label}</span>
      <input value={safeValue} onChange={(event) => onChange(event.target.value)} list={listId} placeholder={placeholder} className="ep-input h-12 rounded-2xl px-4" />
      <datalist id={listId}>
        {suggestions.map((item) => <option key={item} value={item} />)}
      </datalist>
    </label>
  );
}
```

## File: components/ui/live-clock.tsx
```typescript
"use client";

import { useEffect, useState } from "react";
import { formatDateTime } from "@/lib/datetime";

type LiveClockProps = {
  className?: string;
};

export function LiveClock({ className }: LiveClockProps) {
  const [now, setNow] = useState<Date | null>(null);

  useEffect(() => {
    const updateClock = () => setNow(new Date());
    updateClock();
    const timer = window.setInterval(updateClock, 1000);
    return () => window.clearInterval(timer);
  }, []);

  return (
    <span className={className} suppressHydrationWarning>
      {now ? formatDateTime(now) : "--/--/----, --:--:--"}
    </span>
  );
}
```

## File: components/ui/logo-badge.tsx
```typescript
import { cn } from "@/components/ui/utils";

type LogoBadgeProps = {
  initials: string;
  compact?: boolean;
};

export function LogoBadge({ initials, compact = false }: LogoBadgeProps) {
  return (
    <div
      className={cn(
        "flex items-center justify-center rounded-2xl bg-primary text-white shadow-soft",
        compact ? "h-10 w-10 text-sm" : "h-14 w-14 text-lg",
      )}
    >
      <span className="font-semibold tracking-[0.18em]">{initials}</span>
    </div>
  );
}
```

## File: components/ui/searchable-select.tsx
```typescript
"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { ChevronDown, Search, X } from "lucide-react";

type Option = { value: string; label: string };

type SearchableSelectProps = {
  label: string;
  value: string;
  options?: Option[];
  onChange: (value: string) => void;
  placeholder?: string;
};

export function SearchableSelect({
  label,
  value,
  options,
  onChange,
  placeholder = "Seleccionar...",
}: SearchableSelectProps) {
  const [query, setQuery] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const searchInputRef = useRef<HTMLInputElement | null>(null);

  const safeOptions = Array.isArray(options) ? options : [];
  const selected = safeOptions.find((option) => option.value === value) ?? null;
  const filtered = useMemo(() => {
    const term = query.trim().toLowerCase();
    if (!term) {
      return safeOptions;
    }
    return safeOptions.filter((option) => option.label.toLowerCase().includes(term));
  }, [safeOptions, query]);

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    setQuery("");
    const timer = window.setTimeout(() => {
      searchInputRef.current?.focus();
    }, 0);

    return () => window.clearTimeout(timer);
  }, [isOpen]);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    function handleOutsideClick(event: MouseEvent) {
      if (!containerRef.current?.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    document.addEventListener("mousedown", handleOutsideClick);
    return () => document.removeEventListener("mousedown", handleOutsideClick);
  }, []);

  function select(option: Option) {
    onChange(option.value);
    setIsOpen(false);
    setQuery("");
  }

  function clear(event: React.MouseEvent | React.KeyboardEvent) {
    event.stopPropagation();
    onChange("");
    setIsOpen(false);
    setQuery("");
  }

  return (
    <div className="flex flex-col gap-1.5">
      <span className="text-sm font-medium text-primary">{label}</span>
      <div ref={containerRef} className="z-0">
        <button
          type="button"
          onClick={() => setIsOpen((current) => !current)}
          className="flex w-full items-center gap-2 rounded-2xl border border-[var(--line)] bg-[var(--input)] px-3 py-2 text-left"
        >
          <span className="truncate text-sm text-primary">{selected?.label ?? placeholder}</span>
          <div className="ml-auto flex items-center gap-1">
            {selected ? (
              <span
                role="button"
                tabIndex={0}
                onClick={clear}
                onKeyDown={(event) => {
                  if (event.key === "Enter" || event.key === " ") {
                    clear(event);
                  }
                }}
                aria-label="Limpiar selección"
                className="rounded p-0.5 text-secondary hover:bg-[var(--panel)]"
              >
                <X className="h-4 w-4" />
              </span>
            ) : null}
            <ChevronDown className={`h-4 w-4 text-secondary transition-transform ${isOpen ? "rotate-180" : ""}`} />
          </div>
        </button>

        {isOpen ? (
          <div className="mt-2 rounded-2xl border border-[var(--line)] bg-[var(--panel)] shadow-xl">
            <div className="border-b border-[var(--line)] p-2">
              <div className="flex items-center gap-2 rounded-xl border border-[var(--line)] bg-[var(--input)] px-2 py-1.5">
                <Search className="h-4 w-4 text-secondary" />
                <input
                  ref={searchInputRef}
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  placeholder="Buscar..."
                  className="w-full bg-transparent text-sm text-primary outline-none placeholder:text-secondary"
                />
              </div>
            </div>
            <div className="max-h-[240px] overflow-y-auto p-1">
              {filtered.length === 0 ? (
                <div className="px-3 py-2 text-sm text-secondary">Sin opciones.</div>
              ) : (
                filtered.map((option) => (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => select(option)}
                    className={`w-full rounded-xl px-3 py-2 text-left text-sm ${
                      value === option.value ? "bg-primary text-white" : "text-primary hover:bg-[var(--input)]"
                    }`}
                  >
                    {option.label}
                  </button>
                ))
              )}
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}
```

## File: components/ui/theme-provider.tsx
```typescript
"use client";

import { createContext, useContext, useEffect, useMemo, useState, type PropsWithChildren } from "react";

type Theme = "light" | "dark";

type ThemeContextValue = {
  theme: Theme;
  toggleTheme: () => void;
};

const STORAGE_KEY = "easypro2_theme";
const ThemeContext = createContext<ThemeContextValue | null>(null);

function resolveInitialTheme(): Theme {
  if (typeof window === "undefined") {
    return "light";
  }
  const storedTheme = window.localStorage.getItem(STORAGE_KEY);
  if (storedTheme === "light" || storedTheme === "dark") {
    return storedTheme;
  }
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

export function ThemeProvider({ children }: PropsWithChildren) {
  const [theme, setTheme] = useState<Theme>("light");
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const nextTheme = resolveInitialTheme();
    setTheme(nextTheme);
    setIsReady(true);
  }, []);

  useEffect(() => {
    if (!isReady) {
      return;
    }
    document.documentElement.dataset.theme = theme;
    window.localStorage.setItem(STORAGE_KEY, theme);
  }, [isReady, theme]);

  const value = useMemo(
    () => ({
      theme,
      toggleTheme: () => setTheme((current) => (current === "light" ? "dark" : "light")),
    }),
    [theme],
  );

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme must be used within ThemeProvider");
  }
  return context;
}
```

## File: components/ui/utils.ts
```typescript
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

## File: components/ui/validated-input.tsx
```typescript
"use client";

export function ValidatedInput({ label, value, onChange, type = "text", placeholder = "", error }: { label: string; value: string; onChange: (value: string) => void; type?: string; placeholder?: string; error?: string | null }) {
  const safeValue = typeof value === "string" ? value : value == null ? "" : String(value);
  return (
    <label className="grid gap-2 text-sm font-medium text-primary">
      <span>{label}</span>
      <input value={safeValue} onChange={(event) => onChange(event.target.value)} type={type} placeholder={placeholder} className={`ep-input h-12 rounded-2xl px-4 ${error ? "border-rose-500/60" : ""}`} />
      {error ? <span className="text-xs text-rose-500">{error}</span> : null}
    </label>
  );
}
```

## File: components/users/user-profile-workspace.tsx
```typescript
"use client";

import { useEffect, useState } from "react";
import { BadgeCheck, Building2, Mail, ShieldCheck, UserRound } from "lucide-react";
import { getCurrentUser, type CurrentUser } from "@/lib/api";

export function UserProfileWorkspace() {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    getCurrentUser()
      .then((response) => {
        if (!cancelled) {
          setUser(response);
        }
      })
      .catch((loadError) => {
        if (!cancelled) {
          setError(loadError instanceof Error ? loadError.message : "No fue posible cargar el perfil.");
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (error) {
    return <div className="ep-kpi-critical rounded-[2rem] px-6 py-5 text-sm">{error}</div>;
  }

  if (!user) {
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
```

## File: components/users/users-admin-workspace.tsx
```typescript
"use client";

import { Fragment, useEffect, useMemo, useState } from "react";
import { Plus } from "lucide-react";
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
      return;
    }
    setOpenUserId(user.id);
    resetEditor(user);
  }

  function updateField<K extends keyof UserEditorState>(key: K, value: UserEditorState[K]) {
    setEditorState((current) => ({ ...current, [key]: value }));
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
              <input
                type="password"
                value={editorState.password}
                onChange={(event) => updateField("password", event.target.value)}
                placeholder="Dejar vacío para conservar"
                className="ep-input h-12 w-full rounded-2xl px-4"
              />
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
```

## File: lib/api.ts
```typescript
import { cleanNullableText, cleanText, repairText, sanitizeTextDeep } from "@/lib/text";
import { getToken } from "@/lib/auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8001";
const SESSION_KEY = "easypro2_session";

export type LoginPayload = {
  email: string;
  password: string;
};

export type CurrentUser = {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  roles: string[];
  role_codes: string[];
  permissions?: Array<{ module_code: string; can_access: boolean }>;
  default_notary?: string | null;
  default_notary_id?: number | null;
  assignments: Array<{
    id: number;
    role_id: number;
    role_code: string;
    role_name: string;
    notary_id?: number | null;
    notary_label?: string | null;
  }>;
};

export type NotaryPayload = {
  legal_name: string;
  commercial_name: string;
  city: string;
  department: string;
  municipality: string;
  notary_label: string;
  address: string;
  phone: string;
  email: string;
  current_notary_name: string;
  business_hours: string;
  logo_url: string;
  primary_color: string;
  secondary_color: string;
  base_color: string;
  institutional_data: string;
  commercial_status: string;
  commercial_owner: string;
  commercial_owner_user_id: number | null;
  main_contact_name: string;
  main_contact_title: string;
  commercial_phone: string;
  commercial_email: string;
  last_management_at: string;
  next_management_at: string;
  commercial_notes: string;
  priority: string;
  lead_source: string;
  potential: string;
  internal_observations: string;
  is_active: boolean;
};

export type CommercialActivityPayload = {
  occurred_at: string;
  management_type: string;
  comment: string;
  responsible: string;
  responsible_user_id: number | null;
  result: string;
  next_action: string;
};

export type CommercialActivityRecord = CommercialActivityPayload & {
  id: number;
  notary_id: number;
  responsible_user_name?: string | null;
};

export type NotaryAuditRecord = {
  id: number;
  event_type: string;
  field_name?: string | null;
  old_value?: string | null;
  new_value?: string | null;
  comment?: string | null;
  actor_user_id?: number | null;
  actor_user_name?: string | null;
  created_at: string;
};

export type NotaryRecord = NotaryPayload & {
  id: number;
  slug: string;
  accent_color: string;
  activity_count: number;
  commercial_owner_display?: string | null;
  commercial_owner_user_name?: string | null;
};

export type NotaryDetail = NotaryRecord & {
  commercial_activities: CommercialActivityRecord[];
  crm_audit_logs: NotaryAuditRecord[];
};

export type NotaryFilters = {
  commercial_status?: string;
  municipality?: string;
  commercial_owner?: string;
  priority?: string;
  q?: string;
};

export type NotaryFilterOptions = {
  municipalities: string[];
  commercial_owners: string[];
  priorities: string[];
  commercial_statuses: string[];
};

export type NotaryImportSummary = {
  source_path?: string | null;
  processed: number;
  created: number;
  updated: number;
  omitted: number;
  errors: Array<{ row_number: number; municipality?: string | null; notary_label?: string | null; error: string }>;
  results: Array<{ row_number: number; action: string; notary_id?: number | null; slug?: string | null; duplicate_key?: string | null }>;
};

export type RoleCatalogItem = {
  id: number;
  code: string;
  name: string;
  scope: string;
  description: string;
};

export type RolePermissionItem = {
  module_code: string;
  can_access: boolean;
};

export type UserAssignmentPayload = {
  role_code: string;
  notary_id: number | null;
};

export type UserPayload = {
  email: string;
  full_name: string;
  password: string | null;
  is_active: boolean;
  phone: string;
  job_title: string;
  default_notary_id: number | null;
  assignments: UserAssignmentPayload[];
};

export type UserRecord = {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  phone?: string | null;
  job_title?: string | null;
  default_notary_id?: number | null;
  default_notary_label?: string | null;
  roles: string[];
  assignments: Array<{ id: number; role_id: number; role_code: string; role_name: string; notary_id?: number | null; notary_label?: string | null }>;
};

export type UserOption = {
  id: number;
  full_name: string;
  email: string;
  is_active: boolean;
  default_notary_id?: number | null;
  default_notary_label?: string | null;
};

export type CasePayload = {
  notary_id: number;
  case_type: string;
  act_type: string;
  consecutive: number;
  year: number;
  current_state: string;
  current_owner_user_id: number | null;
  client_user_id: number | null;
  protocolist_user_id: number | null;
  approver_user_id: number | null;
  titular_notary_user_id: number | null;
  substitute_notary_user_id: number | null;
  requires_client_review: boolean;
  final_signed_uploaded: boolean;
  metadata_json: string;
};

export type CaseRecord = CasePayload & {
  id: number;
  notary_label: string;
  current_owner_user_name?: string | null;
  client_user_name?: string | null;
  protocolist_user_name?: string | null;
  approver_user_name?: string | null;
  titular_notary_user_name?: string | null;
  substitute_notary_user_name?: string | null;
  created_at: string;
  updated_at: string;
};

export type CaseStateDefinition = {
  id: number;
  case_type: string;
  code: string;
  label: string;
  step_order: number;
  is_initial: boolean;
  is_terminal: boolean;
  is_active: boolean;
};

export type CaseTimelineEvent = {
  id: number;
  event_type: string;
  from_state?: string | null;
  to_state?: string | null;
  comment?: string | null;
  metadata_json?: string | null;
  actor_user_id?: number | null;
  actor_user_name?: string | null;
  created_at: string;
};

export type CaseDetail = CaseRecord & {
  state_definitions: CaseStateDefinition[];
  timeline_events: CaseTimelineEvent[];
};

export type CaseFilters = {
  current_state?: string;
  case_type?: string;
  notary_id?: string;
  current_owner_user_id?: string;
  q?: string;
};

export type CaseFilterOptions = {
  case_types: string[];
  act_types: string[];
  states: string[];
  owners: string[];
  notaries: string[];
};

export type DashboardFilterOption = {
  id?: number | null;
  label: string;
};

export type DashboardKpi = {
  key: string;
  label: string;
  value: number;
  detail?: string | null;
  tone: string;
};

export type DashboardChartDatum = {
  label: string;
  value: number;
  highlight: boolean;
};

export type DashboardTrendDatum = {
  label: string;
  value: number;
};

export type DashboardAlert = {
  level: string;
  title: string;
  detail: string;
};

export type DashboardSystemStatusItem = {
  key: string;
  label: string;
  status: string;
  detail: string;
};

export type DashboardPilotReference = {
  notary_id?: number | null;
  notary_label: string;
  municipality: string;
  department: string;
  total_cases: number;
  active_cases: number;
  finalized_cases: number;
  notes?: string | null;
};

export type ExecutiveDashboardFilters = {
  date_from?: string;
  date_to?: string;
  notary_id?: string;
  state?: string;
  act_type?: string;
  owner_user_id?: string;
};

export type ExecutiveDashboard = {
  generated_at: string;
  filters: {
    date_from?: string | null;
    date_to?: string | null;
    notary_id?: number | null;
    state?: string | null;
    act_type?: string | null;
    owner_user_id?: number | null;
  };
  filter_options: {
    notaries: DashboardFilterOption[];
    states: DashboardFilterOption[];
    act_types: DashboardFilterOption[];
    owners: DashboardFilterOption[];
  };
  kpis: DashboardKpi[];
  documents_by_notary: DashboardChartDatum[];
  documents_by_state: DashboardChartDatum[];
  documents_by_act_type: DashboardChartDatum[];
  temporal_trend: DashboardTrendDatum[];
  owner_ranking: DashboardChartDatum[];
  operational_focus: DashboardChartDatum[];
  critical_alerts: DashboardAlert[];
  system_status: DashboardSystemStatusItem[];
  pilot_reference?: DashboardPilotReference | null;
  latest_import_reference?: string | null;
};
function getCookieToken() {
  if (typeof document === "undefined") {
    return null;
  }
  const match = document.cookie.match(new RegExp(`(?:^|; )${SESSION_KEY}=([^;]+)`));
  return match ? decodeURIComponent(match[1]) : null;
}

function getStoredToken() {
  if (typeof window === "undefined") {
    return null;
  }
  try {
    return window.localStorage.getItem(SESSION_KEY) || window.sessionStorage.getItem(SESSION_KEY) || null;
  } catch {
    return null;
  }
}

function getSessionToken() {
  return getCookieToken() || getStoredToken();
}

function persistSessionToken(token: string, rememberSession: boolean) {
  if (typeof document !== "undefined") {
    const cookie = rememberSession
      ? `${SESSION_KEY}=${encodeURIComponent(token)}; path=/; max-age=2592000; SameSite=None; Secure`
      : `${SESSION_KEY}=${encodeURIComponent(token)}; path=/; SameSite=None; Secure`;
    document.cookie = cookie;
  }
  if (typeof window !== "undefined") {
    try {
      window.localStorage.removeItem(SESSION_KEY);
      window.sessionStorage.removeItem(SESSION_KEY);
      if (rememberSession) {
        window.localStorage.setItem(SESSION_KEY, token);
      } else {
        window.sessionStorage.setItem(SESSION_KEY, token);
      }
    } catch {
      // ignore storage failures in local env
    }
  }
}

async function parseResponse<T>(response: Response): Promise<T> {
  const text = await response.text();
  if (!response.ok) {
    if (response.status === 401) {
      throw new Error("La sesión expiró o no es válida.");
    }
    if (response.status === 403) {
      throw new Error("No tienes permisos para ejecutar esta acción.");
    }
    throw new Error(repairText(text) || "No fue posible completar la solicitud.");
  }
  if (!text.trim()) {
    return null as T;
  }
  return sanitizeTextDeep(JSON.parse(text) as T);
}

function normalizeApiError(error: unknown, fallbackMessage = "No fue posible completar la solicitud.") {
  if (error instanceof Error) {
    const message = repairText(error.message).trim();
    const normalized = message.toLowerCase();

    if (!message || normalized === "failed to fetch" || normalized.includes("networkerror") || normalized.includes("load failed")) {
      return new Error("No fue posible conectarse con el servidor. Verifica que el backend de Easy Pro esté arriba.");
    }

    if (normalized.includes("unexpected end of json input") || normalized.includes("json")) {
      return new Error("El servidor respondió con un formato inesperado. Intenta recargar la vista.");
    }

    return new Error(message);
  }

  return new Error(fallbackMessage);
}

type JsonRequestInit = Omit<RequestInit, "body"> & { body?: unknown };

export async function apiFetch<T>(path: string, init: JsonRequestInit = {}): Promise<T> {
  const token = getSessionToken();
  const headers = new Headers(init.headers ?? {});
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  const body = init.body !== undefined ? JSON.stringify(init.body) : undefined;
  try {
    const response = await fetch(`${API_URL}${path}`, {
      ...init,
      headers,
      body: body as BodyInit | null | undefined,
      cache: init.cache ?? "no-store",
      credentials: "include"
    });
    return await parseResponse<T>(response);
  } catch (error) {
    throw normalizeApiError(error);
  }
}

function normalizeDateTime(value: string) { return value.trim() || null; }

function ensureArray<T>(value: T[] | null | undefined): T[] {
  return Array.isArray(value) ? value : [];
}

function ensureStringArray(value: unknown): string[] {
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === "string").map((item) => repairText(item)) : [];
}

function normalizeUserOptionsResponse(value: unknown): UserOption[] {
  return ensureArray(value as UserOption[]);
}

function normalizeNotaryResponse(value: unknown): NotaryRecord[] {
  return ensureArray(value as NotaryRecord[]);
}

function normalizeCaseResponse(value: unknown): CaseRecord[] {
  return ensureArray(value as CaseRecord[]);
}

function normalizeCaseFilterOptions(value: unknown): CaseFilterOptions {
  const payload = typeof value === "object" && value ? (value as Partial<CaseFilterOptions>) : {};
  return {
    case_types: ensureStringArray(payload.case_types),
    act_types: ensureStringArray(payload.act_types),
    states: ensureStringArray(payload.states),
    owners: ensureStringArray(payload.owners),
    notaries: ensureStringArray(payload.notaries),
  };
}

function buildQuery(params: Record<string, string | undefined> = {}) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => { if (value && value.trim()) query.set(key, value.trim()); });
  const suffix = query.toString();
  return suffix ? `?${suffix}` : "";
}

function normalizeNotaryPayload(payload: NotaryPayload) {
  return { ...payload, department: payload.department.trim() || "Antioquia", municipality: payload.municipality.trim(), notary_label: payload.notary_label.trim(), address: payload.address.trim() || null, phone: payload.phone.trim() || null, email: payload.email.trim() || null, current_notary_name: payload.current_notary_name.trim() || null, business_hours: payload.business_hours.trim() || null, logo_url: payload.logo_url.trim() || null, base_color: payload.base_color.trim() || "#F4F7FB", institutional_data: payload.institutional_data.trim(), commercial_status: payload.commercial_status, commercial_owner: payload.commercial_owner.trim() || null, commercial_owner_user_id: payload.commercial_owner_user_id, main_contact_name: payload.main_contact_name.trim() || null, main_contact_title: payload.main_contact_title.trim() || null, commercial_phone: payload.commercial_phone.trim() || null, commercial_email: payload.commercial_email.trim() || null, last_management_at: normalizeDateTime(payload.last_management_at), next_management_at: normalizeDateTime(payload.next_management_at), commercial_notes: payload.commercial_notes.trim() || null, priority: payload.priority, lead_source: payload.lead_source.trim() || null, potential: payload.potential.trim() || null, internal_observations: payload.internal_observations.trim() || null };
}
function normalizeUserPayload(payload: UserPayload) {
  return { ...payload, email: payload.email.trim().toLowerCase(), full_name: repairText(payload.full_name), password: payload.password?.trim() || null, phone: cleanNullableText(payload.phone), job_title: cleanNullableText(payload.job_title), assignments: payload.assignments.filter((assignment) => assignment.role_code) };
}
function normalizeCasePayload(payload: CasePayload) {
  return { ...payload, case_type: cleanText(payload.case_type), act_type: cleanText(payload.act_type), metadata_json: payload.metadata_json.trim() || "{}" };
}

export async function login(payload: LoginPayload) {
  try {
    const response = await fetch(`${API_URL}/api/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      credentials: "include"
    });
    return await parseResponse<{ access_token: string; token_type: string; user: CurrentUser }>(response);
  } catch (error) {
    throw normalizeApiError(error, "No fue posible iniciar sesión.");
  }
}

export function completeLogin(token: string, rememberSession: boolean) {
  persistSessionToken(token, rememberSession);
}

export function logout() {
  document.cookie = `${SESSION_KEY}=; path=/; max-age=0; SameSite=Lax`;
  if (typeof window !== "undefined") {
    try {
      window.localStorage.removeItem(SESSION_KEY);
      window.sessionStorage.removeItem(SESSION_KEY);
    } catch {
      // ignore storage failures
    }
  }
}

function decodeJwtPayload(token: string | null): Record<string, unknown> {
  if (!token) {
    return {};
  }
  const parts = token.split(".");
  if (parts.length < 2) {
    return {};
  }
  try {
    const payload = parts[1].replace(/-/g, "+").replace(/_/g, "/");
    const padded = payload + "=".repeat((4 - (payload.length % 4)) % 4);
    const raw = typeof atob === "function"
      ? atob(padded)
      : Buffer.from(padded, "base64").toString("binary");
    return JSON.parse(raw) as Record<string, unknown>;
  } catch {
    return {};
  }
}

export async function getCurrentUser(): Promise<CurrentUser> {
  const currentUser = await apiFetch<CurrentUser>("/api/v1/auth/me");
  const tokenPayload = decodeJwtPayload(getToken());
  const tokenNotaryId = typeof tokenPayload.notary_id === "number"
    ? tokenPayload.notary_id
    : typeof tokenPayload.notary_id === "string"
      ? Number(tokenPayload.notary_id)
      : null;
  return {
    ...currentUser,
    default_notary_id: currentUser.default_notary_id ?? (Number.isFinite(tokenNotaryId as number) ? (tokenNotaryId as number) : null),
  };
}
export async function getNotaries(filters: NotaryFilters = {}): Promise<NotaryRecord[]> { return normalizeNotaryResponse(await apiFetch<NotaryRecord[]>(`/api/v1/notaries${buildQuery(filters)}`)); }
export async function getNotaryFilterOptions(): Promise<NotaryFilterOptions> { return apiFetch<NotaryFilterOptions>("/api/v1/notaries/filters"); }
export async function getNotary(id: number): Promise<NotaryDetail> { return apiFetch<NotaryDetail>(`/api/v1/notaries/${id}`); }
export async function updateNotary(id: number, payload: NotaryPayload): Promise<NotaryRecord> { return apiFetch<NotaryRecord>(`/api/v1/notaries/${id}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: normalizeNotaryPayload(payload) }); }
export async function createCommercialActivity(id: number, payload: CommercialActivityPayload): Promise<CommercialActivityRecord> { return apiFetch<CommercialActivityRecord>(`/api/v1/notaries/${id}/commercial-activities`, { method: "POST", headers: { "Content-Type": "application/json" }, body: { ...payload, responsible: payload.responsible.trim() || null, result: payload.result.trim() || null, next_action: payload.next_action.trim() || null } }); }
export async function importAntioquiaSource(overwriteExisting = true): Promise<NotaryImportSummary> { return apiFetch<NotaryImportSummary>("/api/v1/notaries/imports/antioquia-source", { method: "POST", headers: { "Content-Type": "application/json" }, body: { overwrite_existing: overwriteExisting } }); }
export async function getRoleCatalog(): Promise<RoleCatalogItem[]> { return apiFetch<RoleCatalogItem[]>("/api/v1/users/roles"); }
export async function getUsers(): Promise<UserRecord[]> { return apiFetch<UserRecord[]>("/api/v1/users"); }
export async function getUserOptions(activeOnly = true): Promise<UserOption[]> { return normalizeUserOptionsResponse(await apiFetch<UserOption[]>(`/api/v1/users/options${activeOnly ? "?active_only=true" : "?active_only=false"}`)); }
export async function createUser(payload: UserPayload): Promise<UserRecord> { return apiFetch<UserRecord>("/api/v1/users", { method: "POST", headers: { "Content-Type": "application/json" }, body: normalizeUserPayload(payload) }); }
export async function updateUser(id: number, payload: UserPayload): Promise<UserRecord> { return apiFetch<UserRecord>(`/api/v1/users/${id}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: normalizeUserPayload(payload) }); }
export async function getCases(filters: CaseFilters = {}): Promise<CaseRecord[]> { return normalizeCaseResponse(await apiFetch<CaseRecord[]>(`/api/v1/cases${buildQuery(filters)}`)); }
export async function getCaseFilters(): Promise<CaseFilterOptions> { return normalizeCaseFilterOptions(await apiFetch<CaseFilterOptions>("/api/v1/cases/filters")); }
export async function getCase(id: number): Promise<CaseDetail> { return apiFetch<CaseDetail>(`/api/v1/cases/${id}`); }
export async function createCase(payload: Omit<CasePayload, "consecutive" | "year"> & { consecutive?: number; year?: number }): Promise<CaseDetail> { return apiFetch<CaseDetail>("/api/v1/cases", { method: "POST", headers: { "Content-Type": "application/json" }, body: normalizeCasePayload({ ...payload, consecutive: payload.consecutive ?? 0, year: payload.year ?? new Date().getFullYear() } as CasePayload) }); }
export async function updateCase(id: number, payload: CasePayload): Promise<CaseDetail> { return apiFetch<CaseDetail>(`/api/v1/cases/${id}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: normalizeCasePayload(payload) }); }
export async function updateCaseState(id: number, currentState: string, comment = ""): Promise<CaseDetail> { return apiFetch<CaseDetail>(`/api/v1/cases/${id}/state`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: { current_state: currentState, comment: comment.trim() || null } }); }
export async function updateCaseOwner(id: number, userId: number | null, comment = ""): Promise<CaseDetail> { return apiFetch<CaseDetail>(`/api/v1/cases/${id}/owner`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: { current_owner_user_id: userId, comment: comment.trim() || null } }); }
export async function addCaseComment(id: number, comment: string, metadataJson = ""): Promise<CaseDetail> { return apiFetch<CaseDetail>(`/api/v1/cases/${id}/timeline-events`, { method: "POST", headers: { "Content-Type": "application/json" }, body: { comment, metadata_json: metadataJson.trim() || null } }); }



export async function getExecutiveDashboard(filters: ExecutiveDashboardFilters = {}): Promise<ExecutiveDashboard> { return apiFetch<ExecutiveDashboard>(`/api/v1/dashboard/superadmin${buildQuery(filters)}`); }

export async function createRole(payload: {
  code: string; name: string; scope: string; description: string;
}): Promise<RoleCatalogItem> {
  return apiFetch<RoleCatalogItem>("/api/v1/users/roles", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: payload
  });
}

export async function updateRole(
  roleId: number,
  payload: { name: string; description: string }
): Promise<RoleCatalogItem> {
  return apiFetch<RoleCatalogItem>(`/api/v1/users/roles/${roleId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: payload
  });
}

export async function deleteRole(roleId: number): Promise<{ deleted: boolean }> {
  return apiFetch<{ deleted: boolean }>(`/api/v1/users/roles/${roleId}`, { method: "DELETE" });
}

export async function getRolePermissions(roleId: number): Promise<RolePermissionItem[]> {
  return apiFetch<RolePermissionItem[]>(`/api/v1/users/roles/${roleId}/permissions`);
}

export async function updateRolePermissions(roleId: number, permissions: RolePermissionItem[]): Promise<RolePermissionItem[]> {
  return apiFetch<RolePermissionItem[]>(`/api/v1/users/roles/${roleId}/permissions`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: permissions
  });
}
```

## File: lib/auth.ts
```typescript
const SESSION_KEY = "easypro2_session";

function getCookieToken() {
  if (typeof document === "undefined") return null;
  const match = document.cookie.match(new RegExp(`(?:^|; )${SESSION_KEY}=([^;]+)`));
  return match ? decodeURIComponent(match[1]) : null;
}

function getStoredToken() {
  if (typeof window === "undefined") return null;
  try {
    return window.localStorage.getItem(SESSION_KEY) || window.sessionStorage.getItem(SESSION_KEY) || null;
  } catch {
    return null;
  }
}

export function getToken() {
  return getCookieToken() || getStoredToken();
}
```

## File: lib/branding.ts
```typescript
export type NotaryBranding = {
  commercialName: string;
  legalName: string;
  primaryColor: string;
  secondaryColor: string;
  accentColor: string;
  logoInitials: string;
  officeLabel: string;
  city: string;
};

export const defaultBranding: NotaryBranding = {
  commercialName: "EasyPro Notarial",
  legalName: "Plataforma notarial digital",
  primaryColor: "13 46 93",
  secondaryColor: "77 91 124",
  accentColor: "80 214 144",
  logoInitials: "EP",
  officeLabel: "Sede principal",
  city: "Colombia",
};

export const resolveBranding = (): NotaryBranding => defaultBranding;
```

## File: lib/datetime.ts
```typescript
const EASYPRO_LOCALE = "es-CO";
const EASYPRO_TIME_ZONE = "America/Bogota";

type DateParseStrategy = "utc" | "bogota";

type FormatDateTimeOptions = {
  includeSeconds?: boolean;
  strategy?: DateParseStrategy;
};

type DateTimeLocalOptions = {
  strategy?: DateParseStrategy;
};

const ISO_WITH_ZONE = /(Z|[+-]\d{2}:?\d{2})$/i;
const ISO_DATE_ONLY = /^\d{4}-\d{2}-\d{2}$/;
const ISO_NAIVE = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2}(?:\.\d+)?)?$/;

function buildUtcDateFromNaive(value: string): Date | null {
  const match = value.match(
    /^(\d{4})-(\d{2})-(\d{2})(?:T(\d{2}):(\d{2})(?::(\d{2})(?:\.(\d{1,6}))?)?)?$/
  );
  if (!match) return null;

  const [, year, month, day, hour = "00", minute = "00", second = "00", fraction = "0"] = match;
  const milliseconds = Number(fraction.padEnd(3, "0").slice(0, 3));
  const date = new Date(Date.UTC(Number(year), Number(month) - 1, Number(day), Number(hour), Number(minute), Number(second), milliseconds));
  return Number.isNaN(date.getTime()) ? null : date;
}

function parseDateValue(value: string | number | Date | null | undefined, strategy: DateParseStrategy = "utc"): Date | null {
  if (value == null || value === "") return null;
  if (value instanceof Date) return Number.isNaN(value.getTime()) ? null : new Date(value.getTime());
  if (typeof value === "number") {
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? null : date;
  }

  const raw = String(value).trim();
  if (!raw) return null;

  if (ISO_WITH_ZONE.test(raw)) {
    const zonedDate = new Date(raw);
    return Number.isNaN(zonedDate.getTime()) ? null : zonedDate;
  }

  if (ISO_DATE_ONLY.test(raw) || ISO_NAIVE.test(raw)) {
    return buildUtcDateFromNaive(raw);
  }

  const fallback = new Date(raw);
  return Number.isNaN(fallback.getTime()) ? null : fallback;
}

function getFormatter(includeSeconds: boolean, timeZone: string) {
  return new Intl.DateTimeFormat(EASYPRO_LOCALE, {
    timeZone,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    ...(includeSeconds ? { second: "2-digit" } : {}),
  });
}

function getDateParts(date: Date, timeZone: string) {
  const formatter = new Intl.DateTimeFormat("en-CA", {
    timeZone,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });

  const partMap = Object.fromEntries(
    formatter
      .formatToParts(date)
      .filter((part) => part.type !== "literal")
      .map((part) => [part.type, part.value])
  ) as Record<string, string>;

  return {
    year: partMap.year,
    month: partMap.month,
    day: partMap.day,
    hour: partMap.hour,
    minute: partMap.minute,
  };
}

export function formatDateTime(value: string | number | Date | null | undefined, options: FormatDateTimeOptions = {}) {
  const { includeSeconds = true, strategy = "utc" } = options;
  const date = parseDateValue(value, strategy);
  if (!date) return value == null ? "" : String(value);
  const timeZone = strategy == "utc" ? EASYPRO_TIME_ZONE : "UTC";
  return getFormatter(includeSeconds, timeZone).format(date);
}

export function toDateTimeLocalValue(value: string | number | Date | null | undefined, options: DateTimeLocalOptions = {}) {
  const { strategy = "utc" } = options;
  const date = parseDateValue(value, strategy);
  if (!date) return "";
  const timeZone = strategy == "utc" ? EASYPRO_TIME_ZONE : "UTC";
  const parts = getDateParts(date, timeZone);
  return `${parts.year}-${parts.month}-${parts.day}T${parts.hour}:${parts.minute}`;
}

export function getCurrentBogotaDateTimeLocalValue() {
  return toDateTimeLocalValue(new Date(), { strategy: "utc" });
}

export { EASYPRO_LOCALE, EASYPRO_TIME_ZONE };
```

## File: lib/document-flow.ts
```typescript
import { cleanNullableText, cleanText } from "@/lib/text";

async function apiFetch<T = unknown>(path: string, options: { method?: string; body?: unknown; headers?: HeadersInit } = {}): Promise<T> {
  const token = typeof window !== "undefined" ? localStorage.getItem("easypro2_session") : null;
  const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? "";
  const url = `${baseUrl}${path}`;
  
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "Accept": "application/json",
  };
  if (options.headers) {
    Object.assign(headers, Object.fromEntries(new Headers(options.headers).entries()));
  }
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    method: options.method ?? "GET",
    headers,
    body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText);
  }

  const text = await response.text();
  if (!text) return null as T;
  return JSON.parse(text) as T;
}

const asString = (value: unknown, fallback = "") => cleanText(value, fallback);
const asNullableString = (value: unknown) => cleanNullableText(value);
const asNumber = (value: unknown, fallback = 0) => (typeof value === "number" && Number.isFinite(value) ? value : fallback);
const asNullableNumber = (value: unknown) => (typeof value === "number" && Number.isFinite(value) ? value : null);
const asBoolean = (value: unknown, fallback = false) => (typeof value === "boolean" ? value : fallback);
const asArray = <T>(value: unknown, mapper: (item: unknown) => T): T[] => Array.isArray(value) ? value.map(mapper) : [];

export type TemplateRequiredRole = { id: number; role_code: string; label: string; is_required: boolean; step_order: number };
export type TemplateField = { id: number; field_code: string; label: string; field_type: string; section: string; is_required: boolean; options_json?: string | null; placeholder_key?: string | null; help_text?: string | null; step_order: number };
export type TemplateRecord = { id: number; name: string; slug: string; case_type: string; document_type: string; description?: string | null; scope_type: string; notary_id?: number | null; notary_label?: string | null; is_active: boolean; source_filename?: string | null; storage_path?: string | null; internal_variable_map_json: string; required_roles: TemplateRequiredRole[]; fields: TemplateField[] };
export type PersonRecord = { id: number; document_type: string; document_number: string; full_name: string; sex?: string | null; nationality?: string | null; marital_status?: string | null; profession?: string | null; municipality?: string | null; is_transient: boolean; phone?: string | null; address?: string | null; email?: string | null; metadata_json?: string };
export type PersonPayload = Omit<PersonRecord, "id">;
export type DocumentFlowCasePayload = { template_id: number; notary_id: number; client_user_id: number | null; current_owner_user_id: number | null; protocolist_user_id: number | null; approver_user_id: number | null; titular_notary_user_id: number | null; substitute_notary_user_id: number | null; requires_client_review: boolean; metadata_json: string };
export type CaseParticipantPayload = { role_code: string; role_label: string; person_id?: number | null; person?: PersonPayload | null };
export type CaseActDataPayload = { data_json: string };
export type CaseComment = { id: number; created_by_user_id?: number | null; created_by_user_name?: string | null; comment?: string | null; note?: string | null; created_at: string };
export type CaseWorkflowEvent = { id: number; event_type: string; actor_user_id?: number | null; actor_user_name?: string | null; actor_role_code?: string | null; from_state?: string | null; to_state?: string | null; field_name?: string | null; old_value?: string | null; new_value?: string | null; comment?: string | null; approved_version_id?: number | null; metadata_json?: string | null; created_at: string };
export type CaseTimelineEvent = { id: number; event_type: string; from_state?: string | null; to_state?: string | null; comment?: string | null; metadata_json?: string | null; actor_user_id?: number | null; actor_user_name?: string | null; created_at: string };
export type CaseDocumentVersion = { id: number; version_number: number; file_format: string; storage_path: string; original_filename: string; generated_from_template_id?: number | null; created_by_user_id?: number | null; created_by_user_name?: string | null; placeholder_snapshot_json: string; created_at: string; download_url?: string | null };
export type CaseDocument = { id: number; category: string; title: string; current_version_number: number; versions: CaseDocumentVersion[] };
export type CaseParticipant = { id: number; role_code: string; role_label: string; person_id: number; person: PersonRecord; snapshot_json: string; created_at: string; updated_at: string };
export type CaseActData = { id: number; case_id: number; data_json?: string; gari_draft_text?: string | null; created_at: string; updated_at: string };
export type DocumentFlowCase = { id: number; notary_id: number; notary_label: string; template_id?: number | null; template_name?: string | null; template?: TemplateRecord | null; case_type: string; act_type: string; consecutive: number; year: number; internal_case_number?: string | null; official_deed_number?: string | null; official_deed_year?: number | null; current_state: string; current_owner_user_id?: number | null; current_owner_user_name?: string | null; created_by_user_id?: number | null; created_by_user_name?: string | null; client_user_id?: number | null; client_user_name?: string | null; protocolist_user_id?: number | null; protocolist_user_name?: string | null; approver_user_id?: number | null; approver_user_name?: string | null; titular_notary_user_id?: number | null; titular_notary_user_name?: string | null; substitute_notary_user_id?: number | null; substitute_notary_user_name?: string | null; requires_client_review: boolean; final_signed_uploaded: boolean; approved_at?: string | null; approved_by_user_id?: number | null; approved_by_user_name?: string | null; approved_by_role_code?: string | null; approved_document_version_id?: number | null; metadata_json: string; created_at: string; updated_at: string; timeline_events: CaseTimelineEvent[]; workflow_events: CaseWorkflowEvent[]; participants: CaseParticipant[]; act_data?: CaseActData | null; client_comments: CaseComment[]; internal_notes: CaseComment[]; documents: CaseDocument[] };

function normalizeTemplateRole(value: unknown): TemplateRequiredRole {
  const item = (value ?? {}) as Record<string, unknown>;
  return { id: asNumber(item.id), role_code: asString(item.role_code), label: asString(item.label), is_required: asBoolean(item.is_required, true), step_order: asNumber(item.step_order, 1) };
}
function normalizeTemplateField(value: unknown): TemplateField {
  const item = (value ?? {}) as Record<string, unknown>;
  return { id: asNumber(item.id), field_code: asString(item.field_code), label: asString(item.label), field_type: asString(item.field_type, "text"), section: asString(item.section, "acto"), is_required: asBoolean(item.is_required, true), options_json: asNullableString(item.options_json), placeholder_key: asNullableString(item.placeholder_key), help_text: asNullableString(item.help_text), step_order: asNumber(item.step_order, 1) };
}
function normalizeTemplate(value: unknown): TemplateRecord {
  const item = (value ?? {}) as Record<string, unknown>;
  return {
    id: asNumber(item.id),
    name: asString(item.name, "Plantilla sin nombre"),
    slug: asString(item.slug),
    case_type: asString(item.case_type, "escritura"),
    document_type: asString(item.document_type, "Documento"),
    description: asNullableString(item.description),
    scope_type: asString(item.scope_type, "global"),
    notary_id: asNullableNumber(item.notary_id),
    notary_label: asNullableString(item.notary_label),
    is_active: asBoolean(item.is_active, false),
    source_filename: asNullableString(item.source_filename),
    storage_path: asNullableString(item.storage_path),
    internal_variable_map_json: asString(item.internal_variable_map_json, "{}"),
    required_roles: asArray(item.required_roles, normalizeTemplateRole),
    fields: asArray(item.fields, normalizeTemplateField),
  };
}
function normalizePerson(value: unknown): PersonRecord {
  const item = (value ?? {}) as Record<string, unknown>;
  return {
    id: asNumber(item.id),
    document_type: asString(item.document_type, "CC"),
    document_number: asString(item.document_number),
    full_name: asString(item.full_name, "Persona sin nombre"),
    sex: asNullableString(item.sex),
    nationality: asNullableString(item.nationality),
    marital_status: asNullableString(item.marital_status),
    profession: asNullableString(item.profession),
    municipality: asNullableString(item.municipality),
    is_transient: asBoolean(item.is_transient, false),
    phone: asNullableString(item.phone),
    address: asNullableString(item.address),
    email: asNullableString(item.email),
    metadata_json: asString(item.metadata_json, "{}"),
  };
}
function normalizeComment(value: unknown): CaseComment {
  const item = (value ?? {}) as Record<string, unknown>;
  return { id: asNumber(item.id), created_by_user_id: asNullableNumber(item.created_by_user_id), created_by_user_name: asNullableString(item.created_by_user_name), comment: asNullableString(item.comment), note: asNullableString(item.note), created_at: asString(item.created_at) };
}
function normalizeWorkflowEvent(value: unknown): CaseWorkflowEvent {
  const item = (value ?? {}) as Record<string, unknown>;
  return { id: asNumber(item.id), event_type: asString(item.event_type), actor_user_id: asNullableNumber(item.actor_user_id), actor_user_name: asNullableString(item.actor_user_name), actor_role_code: asNullableString(item.actor_role_code), from_state: asNullableString(item.from_state), to_state: asNullableString(item.to_state), field_name: asNullableString(item.field_name), old_value: asNullableString(item.old_value), new_value: asNullableString(item.new_value), comment: asNullableString(item.comment), approved_version_id: asNullableNumber(item.approved_version_id), metadata_json: asNullableString(item.metadata_json), created_at: asString(item.created_at) };
}
function normalizeTimelineEvent(value: unknown): CaseTimelineEvent {
  const item = (value ?? {}) as Record<string, unknown>;
  return { id: asNumber(item.id), event_type: asString(item.event_type), from_state: asNullableString(item.from_state), to_state: asNullableString(item.to_state), comment: asNullableString(item.comment), metadata_json: asNullableString(item.metadata_json), actor_user_id: asNullableNumber(item.actor_user_id), actor_user_name: asNullableString(item.actor_user_name), created_at: asString(item.created_at) };
}
function normalizeDocumentVersion(value: unknown): CaseDocumentVersion {
  const item = (value ?? {}) as Record<string, unknown>;
  return { id: asNumber(item.id), version_number: asNumber(item.version_number), file_format: asString(item.file_format, "docx"), storage_path: asString(item.storage_path), original_filename: asString(item.original_filename, "archivo"), generated_from_template_id: asNullableNumber(item.generated_from_template_id), created_by_user_id: asNullableNumber(item.created_by_user_id), created_by_user_name: asNullableString(item.created_by_user_name), placeholder_snapshot_json: asString(item.placeholder_snapshot_json, "{}"), created_at: asString(item.created_at), download_url: asNullableString(item.download_url) };
}
function normalizeDocument(value: unknown): CaseDocument {
  const item = (value ?? {}) as Record<string, unknown>;
  return { id: asNumber(item.id), category: asString(item.category), title: asString(item.title, "Documento"), current_version_number: asNumber(item.current_version_number), versions: asArray(item.versions, normalizeDocumentVersion) };
}
function normalizeParticipant(value: unknown): CaseParticipant {
  const item = (value ?? {}) as Record<string, unknown>;
  return { id: asNumber(item.id), role_code: asString(item.role_code), role_label: asString(item.role_label), person_id: asNumber(item.person_id), person: normalizePerson(item.person), snapshot_json: asString(item.snapshot_json, "{}"), created_at: asString(item.created_at), updated_at: asString(item.updated_at) };
}
function normalizeActData(value: unknown): CaseActData | null {
  if (!value || typeof value !== "object") return null;
  const item = value as Record<string, unknown>;
  return { id: asNumber(item.id), case_id: asNumber(item.case_id), data_json: asString(item.data_json, "{}"), gari_draft_text: asNullableString(item.gari_draft_text), created_at: asString(item.created_at), updated_at: asString(item.updated_at) };
}
function normalizeCase(value: unknown): DocumentFlowCase {
  const item = (value ?? {}) as Record<string, unknown>;
  return {
    id: asNumber(item.id),
    notary_id: asNumber(item.notary_id),
    notary_label: asString(item.notary_label, "Sin notaría"),
    template_id: asNullableNumber(item.template_id),
    template_name: asNullableString(item.template_name),
    template: item.template ? normalizeTemplate(item.template) : null,
    case_type: asString(item.case_type, "escritura"),
    act_type: asString(item.act_type, "Documento"),
    consecutive: asNumber(item.consecutive),
    year: asNumber(item.year),
    internal_case_number: asNullableString(item.internal_case_number),
    official_deed_number: asNullableString(item.official_deed_number),
    official_deed_year: asNullableNumber(item.official_deed_year),
    current_state: asString(item.current_state, "borrador"),
    current_owner_user_id: asNullableNumber(item.current_owner_user_id),
    current_owner_user_name: asNullableString(item.current_owner_user_name),
    created_by_user_id: asNullableNumber(item.created_by_user_id),
    created_by_user_name: asNullableString(item.created_by_user_name),
    client_user_id: asNullableNumber(item.client_user_id),
    client_user_name: asNullableString(item.client_user_name),
    protocolist_user_id: asNullableNumber(item.protocolist_user_id),
    protocolist_user_name: asNullableString(item.protocolist_user_name),
    approver_user_id: asNullableNumber(item.approver_user_id),
    approver_user_name: asNullableString(item.approver_user_name),
    titular_notary_user_id: asNullableNumber(item.titular_notary_user_id),
    titular_notary_user_name: asNullableString(item.titular_notary_user_name),
    substitute_notary_user_id: asNullableNumber(item.substitute_notary_user_id),
    substitute_notary_user_name: asNullableString(item.substitute_notary_user_name),
    requires_client_review: asBoolean(item.requires_client_review, false),
    final_signed_uploaded: asBoolean(item.final_signed_uploaded, false),
    approved_at: asNullableString(item.approved_at),
    approved_by_user_id: asNullableNumber(item.approved_by_user_id),
    approved_by_user_name: asNullableString(item.approved_by_user_name),
    approved_by_role_code: asNullableString(item.approved_by_role_code),
    approved_document_version_id: asNullableNumber(item.approved_document_version_id),
    metadata_json: asString(item.metadata_json, "{}"),
    created_at: asString(item.created_at),
    updated_at: asString(item.updated_at),
    timeline_events: asArray(item.timeline_events, normalizeTimelineEvent),
    workflow_events: asArray(item.workflow_events, normalizeWorkflowEvent),
    participants: asArray(item.participants, normalizeParticipant),
    act_data: normalizeActData(item.act_data),
    client_comments: asArray(item.client_comments, normalizeComment),
    internal_notes: asArray(item.internal_notes, normalizeComment),
    documents: asArray(item.documents, normalizeDocument),
  };
}

export async function getActiveTemplates() { return asArray(await apiFetch<unknown>("/api/v1/templates/active"), normalizeTemplate); }
export async function getTemplates() { return asArray(await apiFetch<unknown>("/api/v1/templates"), normalizeTemplate); }
export async function createDocumentCase(payload: {
  template_id?: number | null;
  notary_id: number;
  client_user_id?: number | null;
  current_owner_user_id?: number | null;
  protocolist_user_id?: number | null;
  approver_user_id?: number | null;
  titular_notary_user_id?: number | null;
  substitute_notary_user_id?: number | null;
  requires_client_review?: boolean;
  metadata_json?: string;
}): Promise<DocumentFlowCase> {
  const token = localStorage.getItem("easypro2_session");
  const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? "";
  const url = `${baseUrl}/api/v1/document-flow/cases/from-template`;
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json",
      ...(token ? { "Authorization": `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text);
  }
  return response.json();
}
export async function getDocumentCase(caseId: number) { return normalizeCase(await apiFetch<unknown>(`/api/v1/document-flow/cases/${caseId}`)); }
export async function saveCaseParticipants(
  caseId: number,
  payload: any[]
): Promise<DocumentFlowCase> {
  const token = localStorage.getItem("easypro2_session");
  const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? "";
  const url = `${baseUrl}/api/v1/document-flow/cases/${caseId}/participants`;
  const response = await fetch(url, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json",
      ...(token ? { "Authorization": `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text);
  }
  return response.json();
}
export async function saveCaseActData(
  caseId: number,
  payload: { data_json: string }
): Promise<DocumentFlowCase> {
  const token = localStorage.getItem("easypro2_session");
  const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? "";
  const url = `${baseUrl}/api/v1/document-flow/cases/${caseId}/act-data`;
  const response = await fetch(url, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json",
      ...(token ? { "Authorization": `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text);
  }
  return response.json();
}
export async function addClientComment(caseId: number, comment: string) { return normalizeCase(await apiFetch<unknown>(`/api/v1/document-flow/cases/${caseId}/client-comments`, { method: "POST", headers: { "Content-Type": "application/json" }, body: { comment } })); }
export async function addInternalNote(caseId: number, note: string) { return normalizeCase(await apiFetch<unknown>(`/api/v1/document-flow/cases/${caseId}/internal-notes`, { method: "POST", headers: { "Content-Type": "application/json" }, body: { note } })); }
export async function generateCaseDraft(
  caseId: number,
  comment: string
): Promise<DocumentFlowCase> {
  const token = localStorage.getItem("easypro2_session");
  const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? "";
  const url = `${baseUrl}/api/v1/document-flow/cases/${caseId}/generate-with-gari`;
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json",
      ...(token ? { "Authorization": `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ comment }),
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text);
  }
  return response.json();
}
export async function generateWithGari(caseId: number, comment?: string, correctionText?: string): Promise<DocumentFlowCase> {
  const token = localStorage.getItem("easypro2_session");
  const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? "";
  const url = `${baseUrl}/api/v1/document-flow/cases/${caseId}/generate-with-gari`;
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json",
      ...(token ? { "Authorization": `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ comment: comment || null, correction_text: correctionText || null }),
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text);
  }
  return response.json();
}
export async function approveDocumentCase(caseId: number, role_code: string, comment = "") { return normalizeCase(await apiFetch<unknown>(`/api/v1/document-flow/cases/${caseId}/approve`, { method: "POST", headers: { "Content-Type": "application/json" }, body: { role_code, comment: comment || null } })); }
export async function exportDocumentCase(caseId: number, file_format: "docx" | "pdf") { return normalizeCase(await apiFetch<unknown>(`/api/v1/document-flow/cases/${caseId}/export`, { method: "POST", headers: { "Content-Type": "application/json" }, body: { file_format } })); }
export async function uploadFinalSigned(caseId: number, filename: string, content_base64: string, comment = "") { return normalizeCase(await apiFetch<unknown>(`/api/v1/document-flow/cases/${caseId}/final-upload`, { method: "POST", headers: { "Content-Type": "application/json" }, body: { filename, content_base64, comment: comment || null } })); }
export async function lookupPersons(params: { document_type?: string; document_number?: string; q?: string }) { const query = new URLSearchParams(); if (params.document_type) query.set("document_type", params.document_type); if (params.document_number) query.set("document_number", params.document_number); if (params.q) query.set("q", params.q); return asArray(await apiFetch<unknown>(`/api/v1/document-flow/persons/lookup?${query.toString()}`), normalizePerson); }
export async function createTemplate(payload: unknown) { return normalizeTemplate(await apiFetch<unknown>("/api/v1/templates", { method: "POST", headers: { "Content-Type": "application/json" }, body: payload })); }
export async function updateTemplate(id: number, payload: unknown) { return normalizeTemplate(await apiFetch<unknown>(`/api/v1/templates/${id}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: payload })); }

export type ActCatalogItem = {
  id: number;
  code: string;
  label: string;
  roles_json: string;
  is_active: boolean;
};

export type CaseActItem = {
  code: string;
  label: string;
  act_order: number;
  roles_json: string;
};

export async function getActCatalog(): Promise<ActCatalogItem[]> {
  const data = await apiFetch("/api/v1/act-catalog");
  return Array.isArray(data) ? data : [];
}

export async function saveCaseActs(caseId: number, acts: CaseActItem[]): Promise<void> {
  await apiFetch(`/api/v1/document-flow/cases/${caseId}/acts`, {
    method: "PUT",
    body: { acts },
  });
}
```

## File: lib/legal-entities.ts
```typescript
import { apiFetch } from "@/lib/api";

export type LegalEntityRecord = {
  id: number;
  nit: string;
  name: string;
  legal_representative?: string | null;
  municipality?: string | null;
  address?: string | null;
  phone?: string | null;
  email?: string | null;
};

export type LegalEntityPayload = Omit<LegalEntityRecord, "id">;

export type LegalEntityRepresentativeRecord = {
  id: number;
  legal_entity_id: number;
  person_id: number;
  person_name: string;
  person_document: string;
  power_type?: string | null;
  is_active: boolean;
};

export type LegalEntityRepresentativePayload = {
  person_id: number;
  power_type?: string | null;
};

function cleanOptionalText(value: string | null | undefined) {
  const next = value?.trim();
  return next ? next : null;
}

function buildQuery(q: string) {
  const query = q.trim();
  return query ? `?q=${encodeURIComponent(query)}` : "";
}

function normalizeEntity(payload: LegalEntityRecord): LegalEntityRecord {
  return {
    ...payload,
    nit: payload.nit.trim(),
    name: payload.name.trim(),
    legal_representative: cleanOptionalText(payload.legal_representative),
    municipality: cleanOptionalText(payload.municipality),
    address: cleanOptionalText(payload.address),
    phone: cleanOptionalText(payload.phone),
    email: cleanOptionalText(payload.email),
  };
}

function normalizeRepresentative(payload: LegalEntityRepresentativeRecord): LegalEntityRepresentativeRecord {
  return {
    ...payload,
    person_name: payload.person_name.trim(),
    person_document: payload.person_document.trim(),
    power_type: cleanOptionalText(payload.power_type),
  };
}

export async function searchLegalEntities(q: string): Promise<LegalEntityRecord[]> {
  const path = `/api/v1/legal-entities${buildQuery(q)}`;
  const data = await apiFetch<LegalEntityRecord[]>(path);
  return Array.isArray(data) ? data.map(normalizeEntity) : [];
}

export async function createLegalEntity(payload: LegalEntityPayload): Promise<LegalEntityRecord> {
  const data = await apiFetch<LegalEntityRecord>("/api/v1/legal-entities", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      ...payload,
      nit: payload.nit.trim(),
      name: payload.name.trim(),
      legal_representative: cleanOptionalText(payload.legal_representative),
      municipality: cleanOptionalText(payload.municipality),
      address: cleanOptionalText(payload.address),
      phone: cleanOptionalText(payload.phone),
      email: cleanOptionalText(payload.email),
    }),
  });
  return normalizeEntity(data);
}

export async function getLegalEntityRepresentatives(entityId: number): Promise<LegalEntityRepresentativeRecord[]> {
  const data = await apiFetch<LegalEntityRepresentativeRecord[]>(`/api/v1/legal-entities/${entityId}/representatives`);
  return Array.isArray(data) ? data.map(normalizeRepresentative) : [];
}

export async function createLegalEntityRepresentative(
  entityId: number,
  payload: LegalEntityRepresentativePayload,
): Promise<LegalEntityRepresentativeRecord> {
  const data = await apiFetch<LegalEntityRepresentativeRecord>(`/api/v1/legal-entities/${entityId}/representatives`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      person_id: payload.person_id,
      power_type: cleanOptionalText(payload.power_type),
    }),
  });
  return normalizeRepresentative(data);
}
```

## File: lib/navigation.ts
```typescript
import {
  Activity,
  Building2,
  FileArchive,
  FolderKanban,
  HelpCircle,
  LayoutDashboard,
  Layers3,
  PenTool,
  Settings,
  ShieldCheck,
  Users2,
  UserCircle,
} from "lucide-react";

export const appNavigation = [
  { label: "Resumen", href: "/dashboard", icon: LayoutDashboard },
  { label: "Comercial", href: "/dashboard/comercial", icon: ShieldCheck },
  { label: "Notarías", href: "/dashboard/notarias", icon: Building2 },
  { label: "Usuarios", href: "/dashboard/usuarios", icon: Users2 },
  { label: "Roles", href: "/dashboard/roles", icon: ShieldCheck },
  { label: "Casos", href: "/dashboard/casos", icon: FolderKanban },
  { label: "Crear Caso", href: "/dashboard/casos/crear", icon: PenTool },
  { label: "Actos / Plantillas", href: "/dashboard/actos-plantillas", icon: Layers3 },
  { label: "Lotes", href: "/dashboard/lotes", icon: FileArchive },
  { label: "System Status", href: "/dashboard/system-status", icon: Activity },
  { label: "Configuración", href: "/dashboard/configuracion", icon: Settings },
  { label: "Mi Perfil", href: "/dashboard/perfil", icon: UserCircle },
  { label: "Ayuda", href: "/dashboard/ayuda", icon: HelpCircle },
];
```

## File: lib/text.ts
```typescript
const BROKEN_TEXT_MARKERS = ["Ã", "Â", "â", "ƒ", "’", "‚", "\u00ad", "\ufffd"];

const COMMON_TEXT_REPAIRS: Array<[string, string]> = [
  ["Gesti?n", "Gestión"],
  ["Notar?a", "Notaría"],
  ["Revisi?n", "Revisión"],
  ["Validaci?n", "Validación"],
  ["Operaci?n", "Operación"],
  ["Sesi?n", "Sesión"],
  ["Configuraci?n", "Configuración"],
  ["Aprobaci?n", "Aprobación"],
  ["observaci?n", "observación"],
  ["Observaci?n", "Observación"],
  ["Exportaci?n", "Exportación"],
  ["creaci?n", "creación"],
  ["descripci?n", "descripción"],
  ["Descripci?n", "Descripción"],
  ["distribuci?n", "distribución"],
  ["Composici?n", "Composición"],
  ["atenci?n", "atención"],
  ["presi?n", "presión"],
  ["acci?n", "acción"],
  ["asignaci?n", "asignación"],
  ["m?s", "más"],
  ["M?s", "Más"],
  ["d?a", "día"],
  ["D?a", "Día"],
  ["a?o", "año"],
  ["A?o", "Año"],
  ["cuant?a", "cuantía"],
  ["Extensi?n", "Extensión"],
  ["Versi?n", "Versión"],
  ["versi?n", "versión"],
  ["todav?a", "todavía"],
  ["n?mero", "número"],
  ["N?mero", "Número"],
  ["v?lido", "válido"],
  ["profesi?n", "profesión"],
  ["direcci?n", "dirección"],
  ["notar?a", "notaría"],
  ["notarÃ­as", "notarías"],
  ["Bogot?", "Bogotá"],
  ["C?rculo", "Círculo"],
  ["cat?logo", "catálogo"],
  ["p?blica", "pública"],
  ["Mar?a", "María"],
  ["Mej?a", "Mejía"],
  ["Ben?tez", "Benítez"],
  ["G?mez", "Gómez"],
  ["Andr?s", "Andrés"],
  ["Medell?n", "Medellín"],
  ["Espa?ola", "Española"],
  ["Uni?n", "Unión"],
  ["?tiles", "útiles"],
];

function tryDecodeMojibake(value: string): string {
  try {
    const bytes = Uint8Array.from([...value].map((char) => char.charCodeAt(0) & 0xff));
    return new TextDecoder("utf-8", { fatal: false }).decode(bytes);
  } catch {
    return value;
  }
}

export function repairText(value: string | null | undefined): string {
  if (!value) return "";

  let result = value.trim();
  if (!result) return "";

  for (const [broken, fixed] of COMMON_TEXT_REPAIRS) {
    result = result.replaceAll(broken, fixed);
  }

  for (let attempt = 0; attempt < 4; attempt += 1) {
    if (!BROKEN_TEXT_MARKERS.some((marker) => result.includes(marker))) {
      break;
    }

    const repaired = tryDecodeMojibake(result);
    if (!repaired || repaired === result) {
      break;
    }
    result = repaired;
  }

  return result.replace(/\s{2,}/g, " ").trim();
}

export function cleanText(value: unknown, fallback = ""): string {
  if (typeof value !== "string") return fallback;
  const repaired = repairText(value);
  return repaired || fallback;
}

export function cleanNullableText(value: unknown): string | null {
  if (typeof value !== "string") return null;
  const repaired = repairText(value);
  return repaired || null;
}

export function sanitizeTextDeep<T>(value: T): T {
  if (typeof value === "string") {
    return repairText(value) as T;
  }
  if (Array.isArray(value)) {
    return value.map((item) => sanitizeTextDeep(item)) as T;
  }
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>).map(([key, item]) => [key, sanitizeTextDeep(item)]),
    ) as T;
  }
  return value;
}

export function joinReadable(parts: Array<string | null | undefined>, separator = " · "): string {
  return parts.map((part) => repairText(part)).filter(Boolean).join(separator);
}
```

## File: middleware.ts
```typescript
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const PROTECTED_PREFIXES = ["/dashboard"];

export function middleware(request: NextRequest) {
  const isProtected = PROTECTED_PREFIXES.some((prefix) =>
    request.nextUrl.pathname.startsWith(prefix)
  );

  if (!isProtected) {
    return NextResponse.next();
  }

  const sessionToken = request.cookies.get("easypro2_session")?.value;

  if (sessionToken) {
    return NextResponse.next();
  }

  const loginUrl = new URL("/login", request.nextUrl.origin);
  loginUrl.searchParams.set("next", request.nextUrl.pathname);
  return NextResponse.redirect(loginUrl);
}

export const config = {
  matcher: ["/dashboard/:path*"],
};
```

## File: next-env.d.ts
```typescript
/// <reference types="next" />
/// <reference types="next/image-types/global" />
/// <reference path="./.next/types/routes.d.ts" />

// NOTE: This file should not be edited
// see https://nextjs.org/docs/app/api-reference/config/typescript for more information.
```

## File: next.config.mjs
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {};

export default nextConfig;
```

## File: package.json
```json
{
  "name": "easypro2-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "set NEXT_PUBLIC_FRONTEND_URL=http://127.0.0.1:5179&& set NEXT_PUBLIC_API_URL=http://127.0.0.1:8001&& next dev --hostname 127.0.0.1 -p 5179",
    "build": "next build",
    "start": "set NEXT_PUBLIC_FRONTEND_URL=http://127.0.0.1:5179&& set NEXT_PUBLIC_API_URL=http://127.0.0.1:8001&& next start --hostname 127.0.0.1 -p 5179",
    "lint": "next lint"
  },
  "dependencies": {
    "clsx": "^2.1.1",
    "lucide-react": "^0.511.0",
    "next": "^15.3.1",
    "react": "^19.1.0",
    "react-dom": "^19.1.0",
    "recharts": "^3.8.1",
    "tailwind-merge": "^3.3.0"
  },
  "devDependencies": {
    "@types/node": "^22.15.3",
    "@types/react": "^19.1.2",
    "@types/react-dom": "^19.1.2",
    "autoprefixer": "^10.4.21",
    "postcss": "^8.5.3",
    "tailwindcss": "^3.4.17",
    "typescript": "^5.8.3"
  }
}
```

## File: postcss.config.js
```javascript
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {}
  }
};
```

## File: scripts/e2e_document_flow_check.py
```python
import asyncio
import base64
import json
import os
import shutil
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path

import websockets

ROOT = Path(r"C:\EasyProNotarial-2\easypro2")
FRONTEND_URL = "http://127.0.0.1:5179"
BACKEND_URL = "http://127.0.0.1:8000"
BACKEND_DIR = ROOT / "backend"
BACKEND_PYTHON = BACKEND_DIR / ".venv" / "Scripts" / "python.exe"
FRONTEND_DIR = ROOT / "frontend"
SCREENSHOT_DIR = ROOT / "artifacts" / "e2e"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
if not CHROME.exists():
    CHROME = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")


def http_json(url, method="GET", data=None, headers=None):
    body = None if data is None else json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, method=method, headers=headers or {})
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read().decode("utf-8")
        return resp.status, json.loads(raw) if raw else None


def wait_http(url, timeout=30):
    start = time.time()
    last = None
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url, timeout=3) as resp:
                return resp.status
        except Exception as exc:
            last = exc
            time.sleep(0.5)
    raise RuntimeError(f"timeout waiting for {url}: {last}")




class BrowserCDP:
    def __init__(self, ws_url: str):
        self.ws_url = ws_url
        self.ws = None
        self._id = 0
        self.pending = {}
        self._listener_task = None

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url, max_size=50_000_000)
        self._listener_task = asyncio.create_task(self._listener())

    async def close(self):
        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except BaseException:
                pass
        if self.ws:
            await self.ws.close()

    async def _listener(self):
        async for raw in self.ws:
            message = json.loads(raw)
            if "id" in message:
                fut = self.pending.pop(message["id"], None)
                if fut and not fut.done():
                    if "error" in message:
                        fut.set_exception(RuntimeError(str(message["error"])))
                    else:
                        fut.set_result(message.get("result", {}))

    async def send(self, method, params=None):
        self._id += 1
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        self.pending[self._id] = fut
        await self.ws.send(json.dumps({"id": self._id, "method": method, "params": params or {}}))
        return await fut

class CDP:
    def __init__(self, ws_url: str):
        self.ws_url = ws_url
        self.ws = None
        self._id = 0
        self.pending = {}
        self.console = []
        self.exceptions = []
        self.network_failures = []
        self.http_errors = []
        self.page_errors = []
        self._listener_task = None

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url, max_size=50_000_000)
        self._listener_task = asyncio.create_task(self._listener())
        await self.send("Page.enable")
        await self.send("Runtime.enable")
        await self.send("Network.enable")
        await self.send("Log.enable")

    async def close(self):
        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except BaseException:
                pass
        if self.ws:
            await self.ws.close()

    async def _listener(self):
        async for raw in self.ws:
            message = json.loads(raw)
            if "id" in message:
                fut = self.pending.pop(message["id"], None)
                if fut and not fut.done():
                    if "error" in message:
                        fut.set_exception(RuntimeError(str(message["error"])))
                    else:
                        fut.set_result(message.get("result", {}))
                continue
            method = message.get("method")
            params = message.get("params", {})
            if method == "Runtime.consoleAPICalled":
                args = []
                for arg in params.get("args", []):
                    args.append(arg.get("value") or arg.get("description") or "")
                self.console.append({"type": params.get("type"), "text": " ".join(map(str, args))})
            elif method == "Runtime.exceptionThrown":
                details = params.get("exceptionDetails", {})
                self.exceptions.append(details.get("text") or str(details))
            elif method == "Log.entryAdded":
                entry = params.get("entry", {})
                text = entry.get("text") or ""
                level = entry.get("level") or "info"
                self.console.append({"type": level, "text": text})
                if level == "error":
                    self.page_errors.append(text)
            elif method == "Network.loadingFailed":
                self.network_failures.append(params)
            elif method == "Network.responseReceived":
                response = params.get("response", {})
                status = int(response.get("status", 0))
                if status >= 400:
                    self.http_errors.append({"url": response.get("url"), "status": status})

    async def send(self, method, params=None):
        self._id += 1
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        self.pending[self._id] = fut
        await self.ws.send(json.dumps({"id": self._id, "method": method, "params": params or {}}))
        return await fut

    async def eval(self, expression, await_promise=True):
        result = await self.send("Runtime.evaluate", {
            "expression": expression,
            "returnByValue": True,
            "awaitPromise": await_promise,
        })
        if result.get("exceptionDetails"):
            raise RuntimeError(str(result["exceptionDetails"]))
        return result.get("result", {}).get("value")

    async def navigate(self, url):
        await self.send("Page.navigate", {"url": url})
        await self.wait_for_ready()

    async def wait_for_ready(self, timeout=30):
        start = time.time()
        while time.time() - start < timeout:
            state = await self.eval("document.readyState")
            if state == "complete":
                return
            await asyncio.sleep(0.25)
        raise RuntimeError("document did not reach readyState=complete")

    async def wait_for(self, js_condition, timeout=30):
        start = time.time()
        while time.time() - start < timeout:
            try:
                ok = await self.eval(f"Boolean({js_condition})")
            except Exception:
                ok = False
            if ok:
                return
            await asyncio.sleep(0.25)
        raise RuntimeError(f"condition timeout: {js_condition}")

    async def screenshot(self, filename):
        result = await self.send("Page.captureScreenshot", {"format": "png", "fromSurface": True})
        path = SCREENSHOT_DIR / filename
        path.write_bytes(base64.b64decode(result["data"]))
        return str(path)


async def main():
    if not CHROME.exists():
        raise RuntimeError("No browser executable found")

    backend = subprocess.Popen(
        [str(BACKEND_PYTHON), "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=str(BACKEND_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    frontend = subprocess.Popen(
        ["C:\Windows\System32\cmd.exe", "/c", "npm.cmd run start -- --hostname 127.0.0.1 --port 5179"],
        cwd=str(FRONTEND_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    user_data_dir = Path(tempfile.mkdtemp(prefix="easypro2-chrome-"))
    browser = subprocess.Popen([
        str(CHROME),
        "--headless=new",
        "--disable-gpu",
        "--remote-debugging-port=9222",
        f"--user-data-dir={user_data_dir}",
        "--window-size=1600,1200",
        "about:blank",
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    cdp = None
    browser_cdp = None
    try:
        wait_http(BACKEND_URL + "/health")
        wait_http(FRONTEND_URL + "/login")
        status, _ = http_json(BACKEND_URL + "/api/v1/auth/login", method="POST", data={"email": "superadmin@easypro.co", "password": "ChangeMe123!"}, headers={"Content-Type": "application/json"})
        if status != 200:
            raise RuntimeError("login api failed before browser test")

        # get browser ws endpoint
        version = None
        for _ in range(40):
            try:
                with urllib.request.urlopen("http://127.0.0.1:9222/json/version", timeout=2) as resp:
                    version = json.loads(resp.read().decode("utf-8"))
                    break
            except Exception:
                time.sleep(0.25)
        if not version:
            raise RuntimeError("chrome devtools endpoint not available")

        browser_cdp = BrowserCDP(version["webSocketDebuggerUrl"])
        await browser_cdp.connect()
        created_target = await browser_cdp.send("Target.createTarget", {"url": "about:blank"})
        target_id = created_target.get("targetId")
        target = None
        for _ in range(40):
            try:
                with urllib.request.urlopen("http://127.0.0.1:9222/json/list", timeout=5) as resp:
                    targets = json.loads(resp.read().decode("utf-8"))
                    target = next((item for item in targets if item.get("id") == target_id and item.get("webSocketDebuggerUrl")), None)
                    if target:
                        break
            except Exception:
                time.sleep(0.25)
        if not target:
            raise RuntimeError("could not find browser page target")

        cdp = CDP(target["webSocketDebuggerUrl"])
        await cdp.connect()

        evidence = {}

        await cdp.navigate(FRONTEND_URL + "/login")
        await cdp.wait_for("document.querySelector('input[name=email]') && document.querySelector('input[name=password]')")
        evidence["login_before"] = await cdp.screenshot("01-login.png")
        await cdp.eval("""
        (() => {
          const setValue = (selector, value) => {
            const input = document.querySelector(selector);
            if (!input) return false;
            const proto = Object.getPrototypeOf(input);
            const descriptor = Object.getOwnPropertyDescriptor(proto, 'value');
            if (descriptor && descriptor.set) descriptor.set.call(input, value);
            else input.value = value;
            input.dispatchEvent(new Event('input', { bubbles: true }));
            input.dispatchEvent(new Event('change', { bubbles: true }));
            return true;
          };
          const emailOk = setValue('input[name=email]', 'superadmin@easypro.co');
          const passwordOk = setValue('input[name=password]', 'ChangeMe123!');
          if (!emailOk || !passwordOk) return false;
          const button = Array.from(document.querySelectorAll('button')).find(btn => btn.textContent.includes('Ingresar'));
          if (!button) return false;
          button.click();
          return true;
        })()
        """)
        try:
            await cdp.wait_for("location.pathname === '/dashboard'", timeout=20)
        except Exception:
            print(json.dumps({
                'login_debug_url': await cdp.eval('location.href'),
                'login_debug_text': await cdp.eval('document.body.innerText.slice(0, 1500)'),
                'login_console': cdp.console[-20:],
                'login_http_errors': cdp.http_errors[-20:],
                'login_network_failures': cdp.network_failures[-20:],
                'login_exceptions': cdp.exceptions[-20:],
            }, ensure_ascii=False, indent=2))
            raise
        evidence["dashboard_after_login"] = await cdp.screenshot("02-dashboard-after-login.png")

        await cdp.navigate(FRONTEND_URL + "/dashboard/actos-plantillas")
        await cdp.wait_for("document.body.innerText.toLowerCase().includes('poder general')")
        evidence["templates"] = await cdp.screenshot("03-templates.png")

        await cdp.navigate(FRONTEND_URL + "/dashboard/casos")
        try:
            await cdp.wait_for("document.body.innerText.toLowerCase().includes('casos documentales')", timeout=20)
        except Exception:
            print(json.dumps({
                'cases_debug_url': await cdp.eval('location.href'),
                'cases_debug_text': await cdp.eval('document.body.innerText.slice(0, 2000)'),
                'cases_console': cdp.console[-30:],
                'cases_http_errors': cdp.http_errors[-30:],
                'cases_network_failures': cdp.network_failures[-30:],
                'cases_exceptions': cdp.exceptions[-30:],
            }, ensure_ascii=False, indent=2))
            raise
        evidence["cases"] = await cdp.screenshot("04-cases.png")

        await cdp.navigate(FRONTEND_URL + "/dashboard/casos/crear")
        await cdp.wait_for("document.body.innerText.toLowerCase().includes('wizard documental inicial para poder general')")
        evidence["wizard_step1"] = await cdp.screenshot("05-wizard-step1.png")

        await cdp.eval("Array.from(document.querySelectorAll('button')).find(btn => btn.textContent.includes('Poder General'))?.click(); true")
        await cdp.eval("Array.from(document.querySelectorAll('button')).find(btn => btn.textContent.includes('Continuar'))?.click(); true")
        await cdp.wait_for("document.body.innerText.toLowerCase().includes('datos generales del caso')")
        evidence["wizard_step2"] = await cdp.screenshot("06-wizard-step2.png")

        async def select_option(label, match):
            expr = f"""
            (() => {{
              const norm = (value) => (value || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
              const blocks = Array.from(document.querySelectorAll('div.grid.gap-2.text-sm.font-medium.text-primary'));
              const block = blocks.find(node => norm(node.innerText).includes(norm({json.dumps(label)})));
              if (!block) return false;
              const search = block.querySelector('input');
              if (!search) return false;
              search.value = {json.dumps(match)};
              search.dispatchEvent(new Event('input', {{ bubbles: true }}));
              const buttons = Array.from(block.querySelectorAll('button'));
              const target = buttons.find(btn => norm(btn.textContent).includes(norm({json.dumps(match)})));
              if (!target) return false;
              target.click();
              return true;
            }})()
            """
            return await cdp.eval(expr)

        async def set_text_input(js_expr, value):
            focused = await cdp.eval(f"""
            (() => {{
              const input = {js_expr};
              if (!input) return false;
              const descriptor = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value');
              if (descriptor && descriptor.set) descriptor.set.call(input, '');
              else input.value = '';
              input.dispatchEvent(new Event('input', {{ bubbles: true }}));
              input.focus();
              if (input.select) input.select();
              return true;
            }})()
            """)
            if not focused:
                raise RuntimeError(f'Input not found for expression: {js_expr}')
            await cdp.send('Input.insertText', {'text': value})
            await asyncio.sleep(0.1)

        async def click_button_in_block(js_expr, text):
            expr = f"""
            (() => {{
              const block = {js_expr};
              if (!block) return false;
              const target = Array.from(block.querySelectorAll('button')).find(btn => (btn.textContent || '').includes({json.dumps(text)}));
              if (!target) return false;
              target.click();
              return true;
            }})()
            """
            ok = await cdp.eval(expr)
            if not ok:
                raise RuntimeError(f'Button {text} not found in block {js_expr}')
            await asyncio.sleep(0.1)

        await select_option('Notaría', 'Caldas')
        await cdp.eval("Array.from(document.querySelectorAll('button')).find(btn => btn.textContent.includes('Continuar'))?.click(); true")
        await cdp.wait_for("document.body.innerText.toLowerCase().includes('intervinientes')")
        evidence["wizard_step3"] = await cdp.screenshot("07-wizard-step3.png")

        participant_values = [
            {"doc": "10010001", "name": "Carlos Poderdante UI", "profession": "Comerciante", "municipality": "Caldas", "phone": "3001000001", "email": "carlos.poderdante@easypro.co", "address": "Calle 10 # 20-30", "civil": "Soltero(a)"},
            {"doc": "10010002", "name": "Laura Apoderada UI", "profession": "Abogada", "municipality": "Medellin", "phone": "3001000002", "email": "laura.apoderada@easypro.co", "address": "Carrera 40 # 50-60", "civil": "Casado(a)"},
        ]
        for card_index, item in enumerate(participant_values):
            card_expr = f"Array.from(document.querySelectorAll('div.ep-card-soft')).filter(card => (card.innerText || '').toLowerCase().includes('bloque obligatorio'))[{card_index}]"
            await set_text_input(f"{card_expr}.querySelectorAll('label input')[0]", item['doc'])
            await set_text_input(f"{card_expr}.querySelectorAll('label input')[1]", item['name'])
            await set_text_input(f"{card_expr}.querySelector('input[list]')", item['profession'])
            await set_text_input(f"{card_expr}.querySelectorAll('label input')[3]", item['municipality'])
            await set_text_input(f"{card_expr}.querySelectorAll('label input')[4]", item['phone'])
            await set_text_input(f"{card_expr}.querySelectorAll('label input')[5]", item['email'])
            await set_text_input(f"{card_expr}.querySelectorAll('label input')[6]", item['address'])
            await click_button_in_block(f"{card_expr}.querySelectorAll('div.grid.gap-2.text-sm.font-medium.text-primary')[3]", item['civil'])
        await cdp.eval("Array.from(document.querySelectorAll('button')).find(btn => btn.textContent.includes('Continuar'))?.click(); true")
        await cdp.wait_for("document.body.innerText.toLowerCase().includes('datos del acto')")
        evidence["wizard_step4"] = await cdp.screenshot("08-wizard-step4.png")

        act_values = ['23', 'marzo', '2026', '185000', '35150', '6500', '5200', 'PG-UI-01', '4 hojas', 'Sin cuantía']
        for index, value in enumerate(act_values):
            await set_text_input(f"Array.from(document.querySelectorAll('label input'))[{index}]", value)
        await cdp.eval("Array.from(document.querySelectorAll('button')).find(btn => btn.textContent.includes('Continuar'))?.click(); true")
        await cdp.wait_for("document.body.innerText.toLowerCase().includes('generar borrador')")
        evidence["wizard_step5"] = await cdp.screenshot("09-wizard-step5.png")

        await cdp.eval("Array.from(document.querySelectorAll('button')).find(btn => btn.textContent.includes('Generar borrador Word v1'))?.click(); true")
        try:
            await cdp.wait_for("document.body.innerText.toLowerCase().includes('borrador word v1 generado correctamente')", timeout=25)
        except Exception:
            print(json.dumps({
                'draft_debug_url': await cdp.eval('location.href'),
                'draft_debug_text': await cdp.eval('document.body.innerText.slice(0, 2500)'),
                'draft_console': cdp.console[-40:],
                'draft_http_errors': cdp.http_errors[-40:],
                'draft_network_failures': cdp.network_failures[-40:],
                'draft_exceptions': cdp.exceptions[-40:],
            }, ensure_ascii=False, indent=2))
            raise
        evidence["wizard_done"] = await cdp.screenshot("10-wizard-done.png")

        case_href = await cdp.eval("(() => { const link = Array.from(document.querySelectorAll('a')).find(a => a.textContent.includes('Abrir detalle del caso')); return link ? link.href : ''; })()")
        if not case_href:
            raise RuntimeError('No detail link found after draft generation')
        await cdp.navigate(case_href)
        await cdp.wait_for("document.body.innerText.toLowerCase().includes('detalle del caso') && document.body.innerText.toLowerCase().includes('documentos')")
        evidence["case_detail"] = await cdp.screenshot("11-case-detail.png")
        await cdp.eval("Array.from(document.querySelectorAll('button')).find(btn => btn.textContent.includes('Documentos'))?.click(); true")
        await cdp.wait_for("document.body.innerText.toLowerCase().includes('exportar word') && document.body.innerText.toLowerCase().includes('documento definitivo')")
        evidence["case_documents"] = await cdp.screenshot("12-case-documents.png")

        body_text = await cdp.eval("document.body.innerText")
        current_url = await cdp.eval("location.href")
        meaningful_network_failures = [item for item in cdp.network_failures if not item.get('canceled')]
        has_draft = ('borrador documental' in body_text.lower()) or ('v1' in body_text.lower())
        has_documents_tab = 'Documentos' in body_text
        has_traceability = 'Trazabilidad' in body_text
        has_runtime_error = 'Application error: a client-side exception has occurred' in body_text

        result = {
            'current_url': current_url,
            'has_draft': has_draft,
            'has_documents_tab': has_documents_tab,
            'has_traceability': has_traceability,
            'has_runtime_error': has_runtime_error,
            'console': cdp.console[-20:],
            'exceptions': cdp.exceptions,
            'network_failures': cdp.network_failures,
            'meaningful_network_failures': meaningful_network_failures,
            'http_errors': cdp.http_errors,
            'page_errors': cdp.page_errors,
            'screenshots': evidence,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))

        if has_runtime_error or cdp.exceptions or meaningful_network_failures or any(item.get('status', 0) >= 500 for item in cdp.http_errors) or not has_draft:
            raise SystemExit(2)
    finally:
        try:
            await cdp.close()
        except Exception:
            pass
        try:
            await browser_cdp.close()
        except Exception:
            pass
        try:
            browser.terminate()
            browser.wait(timeout=5)
        except Exception:
            try:
                browser.kill()
            except BaseException:
                pass
        try:
            backend.terminate()
            backend.wait(timeout=5)
        except Exception:
            try:
                backend.kill()
            except BaseException:
                pass
        shutil.rmtree(user_data_dir, ignore_errors=True)

if __name__ == '__main__':
    asyncio.run(main())
```

## File: tailwind.config.ts
```typescript
import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        ink: "rgb(var(--ink) / <alpha-value>)",
        surface: "rgb(var(--surface) / <alpha-value>)",
        primary: "rgb(var(--primary) / <alpha-value>)",
        secondary: "rgb(var(--secondary) / <alpha-value>)",
        accent: "rgb(var(--accent) / <alpha-value>)",
        line: "rgb(var(--line) / <alpha-value>)"
      },
      boxShadow: {
        panel: "0 18px 45px rgba(11, 30, 58, 0.08)",
        soft: "0 10px 30px rgba(18, 38, 63, 0.08)"
      },
      borderRadius: {
        "4xl": "2rem"
      }
    }
  },
  plugins: []
};

export default config;
```

## File: tsconfig.json
```json
{
  "compilerOptions": {
    "target": "ES2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": false,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

## File: tsconfig.tsbuildinfo
```
{"fileNames":["./node_modules/typescript/lib/lib.es5.d.ts","./node_modules/typescript/lib/lib.es2015.d.ts","./node_modules/typescript/lib/lib.es2016.d.ts","./node_modules/typescript/lib/lib.es2017.d.ts","./node_modules/typescript/lib/lib.es2018.d.ts","./node_modules/typescript/lib/lib.es2019.d.ts","./node_modules/typescript/lib/lib.es2020.d.ts","./node_modules/typescript/lib/lib.es2021.d.ts","./node_modules/typescript/lib/lib.es2022.d.ts","./node_modules/typescript/lib/lib.es2023.d.ts","./node_modules/typescript/lib/lib.es2024.d.ts","./node_modules/typescript/lib/lib.esnext.d.ts","./node_modules/typescript/lib/lib.dom.d.ts","./node_modules/typescript/lib/lib.dom.iterable.d.ts","./node_modules/typescript/lib/lib.es2015.core.d.ts","./node_modules/typescript/lib/lib.es2015.collection.d.ts","./node_modules/typescript/lib/lib.es2015.generator.d.ts","./node_modules/typescript/lib/lib.es2015.iterable.d.ts","./node_modules/typescript/lib/lib.es2015.promise.d.ts","./node_modules/typescript/lib/lib.es2015.proxy.d.ts","./node_modules/typescript/lib/lib.es2015.reflect.d.ts","./node_modules/typescript/lib/lib.es2015.symbol.d.ts","./node_modules/typescript/lib/lib.es2015.symbol.wellknown.d.ts","./node_modules/typescript/lib/lib.es2016.array.include.d.ts","./node_modules/typescript/lib/lib.es2016.intl.d.ts","./node_modules/typescript/lib/lib.es2017.arraybuffer.d.ts","./node_modules/typescript/lib/lib.es2017.date.d.ts","./node_modules/typescript/lib/lib.es2017.object.d.ts","./node_modules/typescript/lib/lib.es2017.sharedmemory.d.ts","./node_modules/typescript/lib/lib.es2017.string.d.ts","./node_modules/typescript/lib/lib.es2017.intl.d.ts","./node_modules/typescript/lib/lib.es2017.typedarrays.d.ts","./node_modules/typescript/lib/lib.es2018.asyncgenerator.d.ts","./node_modules/typescript/lib/lib.es2018.asynciterable.d.ts","./node_modules/typescript/lib/lib.es2018.intl.d.ts","./node_modules/typescript/lib/lib.es2018.promise.d.ts","./node_modules/typescript/lib/lib.es2018.regexp.d.ts","./node_modules/typescript/lib/lib.es2019.array.d.ts","./node_modules/typescript/lib/lib.es2019.object.d.ts","./node_modules/typescript/lib/lib.es2019.string.d.ts","./node_modules/typescript/lib/lib.es2019.symbol.d.ts","./node_modules/typescript/lib/lib.es2019.intl.d.ts","./node_modules/typescript/lib/lib.es2020.bigint.d.ts","./node_modules/typescript/lib/lib.es2020.date.d.ts","./node_modules/typescript/lib/lib.es2020.promise.d.ts","./node_modules/typescript/lib/lib.es2020.sharedmemory.d.ts","./node_modules/typescript/lib/lib.es2020.string.d.ts","./node_modules/typescript/lib/lib.es2020.symbol.wellknown.d.ts","./node_modules/typescript/lib/lib.es2020.intl.d.ts","./node_modules/typescript/lib/lib.es2020.number.d.ts","./node_modules/typescript/lib/lib.es2021.promise.d.ts","./node_modules/typescript/lib/lib.es2021.string.d.ts","./node_modules/typescript/lib/lib.es2021.weakref.d.ts","./node_modules/typescript/lib/lib.es2021.intl.d.ts","./node_modules/typescript/lib/lib.es2022.array.d.ts","./node_modules/typescript/lib/lib.es2022.error.d.ts","./node_modules/typescript/lib/lib.es2022.intl.d.ts","./node_modules/typescript/lib/lib.es2022.object.d.ts","./node_modules/typescript/lib/lib.es2022.string.d.ts","./node_modules/typescript/lib/lib.es2022.regexp.d.ts","./node_modules/typescript/lib/lib.es2023.array.d.ts","./node_modules/typescript/lib/lib.es2023.collection.d.ts","./node_modules/typescript/lib/lib.es2023.intl.d.ts","./node_modules/typescript/lib/lib.es2024.arraybuffer.d.ts","./node_modules/typescript/lib/lib.es2024.collection.d.ts","./node_modules/typescript/lib/lib.es2024.object.d.ts","./node_modules/typescript/lib/lib.es2024.promise.d.ts","./node_modules/typescript/lib/lib.es2024.regexp.d.ts","./node_modules/typescript/lib/lib.es2024.sharedmemory.d.ts","./node_modules/typescript/lib/lib.es2024.string.d.ts","./node_modules/typescript/lib/lib.esnext.array.d.ts","./node_modules/typescript/lib/lib.esnext.collection.d.ts","./node_modules/typescript/lib/lib.esnext.intl.d.ts","./node_modules/typescript/lib/lib.esnext.disposable.d.ts","./node_modules/typescript/lib/lib.esnext.promise.d.ts","./node_modules/typescript/lib/lib.esnext.decorators.d.ts","./node_modules/typescript/lib/lib.esnext.iterator.d.ts","./node_modules/typescript/lib/lib.esnext.float16.d.ts","./node_modules/typescript/lib/lib.esnext.error.d.ts","./node_modules/typescript/lib/lib.esnext.sharedmemory.d.ts","./node_modules/typescript/lib/lib.decorators.d.ts","./node_modules/typescript/lib/lib.decorators.legacy.d.ts","./.next/types/routes.d.ts","./node_modules/@types/react/global.d.ts","./node_modules/csstype/index.d.ts","./node_modules/@types/react/index.d.ts","./node_modules/next/dist/styled-jsx/types/css.d.ts","./node_modules/next/dist/styled-jsx/types/macro.d.ts","./node_modules/next/dist/styled-jsx/types/style.d.ts","./node_modules/next/dist/styled-jsx/types/global.d.ts","./node_modules/next/dist/styled-jsx/types/index.d.ts","./node_modules/next/dist/shared/lib/amp.d.ts","./node_modules/next/amp.d.ts","./node_modules/next/dist/server/get-page-files.d.ts","./node_modules/@types/node/compatibility/disposable.d.ts","./node_modules/@types/node/compatibility/indexable.d.ts","./node_modules/@types/node/compatibility/iterators.d.ts","./node_modules/@types/node/compatibility/index.d.ts","./node_modules/@types/node/globals.typedarray.d.ts","./node_modules/@types/node/buffer.buffer.d.ts","./node_modules/@types/node/globals.d.ts","./node_modules/@types/node/web-globals/abortcontroller.d.ts","./node_modules/@types/node/web-globals/domexception.d.ts","./node_modules/@types/node/web-globals/events.d.ts","./node_modules/undici-types/header.d.ts","./node_modules/undici-types/readable.d.ts","./node_modules/undici-types/file.d.ts","./node_modules/undici-types/fetch.d.ts","./node_modules/undici-types/formdata.d.ts","./node_modules/undici-types/connector.d.ts","./node_modules/undici-types/client.d.ts","./node_modules/undici-types/errors.d.ts","./node_modules/undici-types/dispatcher.d.ts","./node_modules/undici-types/global-dispatcher.d.ts","./node_modules/undici-types/global-origin.d.ts","./node_modules/undici-types/pool-stats.d.ts","./node_modules/undici-types/pool.d.ts","./node_modules/undici-types/handlers.d.ts","./node_modules/undici-types/balanced-pool.d.ts","./node_modules/undici-types/agent.d.ts","./node_modules/undici-types/mock-interceptor.d.ts","./node_modules/undici-types/mock-agent.d.ts","./node_modules/undici-types/mock-client.d.ts","./node_modules/undici-types/mock-pool.d.ts","./node_modules/undici-types/mock-errors.d.ts","./node_modules/undici-types/proxy-agent.d.ts","./node_modules/undici-types/env-http-proxy-agent.d.ts","./node_modules/undici-types/retry-handler.d.ts","./node_modules/undici-types/retry-agent.d.ts","./node_modules/undici-types/api.d.ts","./node_modules/undici-types/interceptors.d.ts","./node_modules/undici-types/util.d.ts","./node_modules/undici-types/cookies.d.ts","./node_modules/undici-types/patch.d.ts","./node_modules/undici-types/websocket.d.ts","./node_modules/undici-types/eventsource.d.ts","./node_modules/undici-types/filereader.d.ts","./node_modules/undici-types/diagnostics-channel.d.ts","./node_modules/undici-types/content-type.d.ts","./node_modules/undici-types/cache.d.ts","./node_modules/undici-types/index.d.ts","./node_modules/@types/node/web-globals/fetch.d.ts","./node_modules/@types/node/web-globals/navigator.d.ts","./node_modules/@types/node/web-globals/storage.d.ts","./node_modules/@types/node/assert.d.ts","./node_modules/@types/node/assert/strict.d.ts","./node_modules/@types/node/async_hooks.d.ts","./node_modules/@types/node/buffer.d.ts","./node_modules/@types/node/child_process.d.ts","./node_modules/@types/node/cluster.d.ts","./node_modules/@types/node/console.d.ts","./node_modules/@types/node/constants.d.ts","./node_modules/@types/node/crypto.d.ts","./node_modules/@types/node/dgram.d.ts","./node_modules/@types/node/diagnostics_channel.d.ts","./node_modules/@types/node/dns.d.ts","./node_modules/@types/node/dns/promises.d.ts","./node_modules/@types/node/domain.d.ts","./node_modules/@types/node/events.d.ts","./node_modules/@types/node/fs.d.ts","./node_modules/@types/node/fs/promises.d.ts","./node_modules/@types/node/http.d.ts","./node_modules/@types/node/http2.d.ts","./node_modules/@types/node/https.d.ts","./node_modules/@types/node/inspector.d.ts","./node_modules/@types/node/inspector.generated.d.ts","./node_modules/@types/node/module.d.ts","./node_modules/@types/node/net.d.ts","./node_modules/@types/node/os.d.ts","./node_modules/@types/node/path.d.ts","./node_modules/@types/node/perf_hooks.d.ts","./node_modules/@types/node/process.d.ts","./node_modules/@types/node/punycode.d.ts","./node_modules/@types/node/querystring.d.ts","./node_modules/@types/node/readline.d.ts","./node_modules/@types/node/readline/promises.d.ts","./node_modules/@types/node/repl.d.ts","./node_modules/@types/node/sea.d.ts","./node_modules/@types/node/sqlite.d.ts","./node_modules/@types/node/stream.d.ts","./node_modules/@types/node/stream/promises.d.ts","./node_modules/@types/node/stream/consumers.d.ts","./node_modules/@types/node/stream/web.d.ts","./node_modules/@types/node/string_decoder.d.ts","./node_modules/@types/node/test.d.ts","./node_modules/@types/node/timers.d.ts","./node_modules/@types/node/timers/promises.d.ts","./node_modules/@types/node/tls.d.ts","./node_modules/@types/node/trace_events.d.ts","./node_modules/@types/node/tty.d.ts","./node_modules/@types/node/url.d.ts","./node_modules/@types/node/util.d.ts","./node_modules/@types/node/v8.d.ts","./node_modules/@types/node/vm.d.ts","./node_modules/@types/node/wasi.d.ts","./node_modules/@types/node/worker_threads.d.ts","./node_modules/@types/node/zlib.d.ts","./node_modules/@types/node/index.d.ts","./node_modules/@types/react/canary.d.ts","./node_modules/@types/react/experimental.d.ts","./node_modules/@types/react-dom/index.d.ts","./node_modules/@types/react-dom/canary.d.ts","./node_modules/@types/react-dom/experimental.d.ts","./node_modules/next/dist/lib/fallback.d.ts","./node_modules/next/dist/compiled/webpack/webpack.d.ts","./node_modules/next/dist/server/config.d.ts","./node_modules/next/dist/lib/load-custom-routes.d.ts","./node_modules/next/dist/shared/lib/image-config.d.ts","./node_modules/next/dist/build/webpack/plugins/subresource-integrity-plugin.d.ts","./node_modules/next/dist/server/body-streams.d.ts","./node_modules/next/dist/server/lib/cache-control.d.ts","./node_modules/next/dist/lib/setup-exception-listeners.d.ts","./node_modules/next/dist/lib/worker.d.ts","./node_modules/next/dist/lib/constants.d.ts","./node_modules/next/dist/client/components/app-router-headers.d.ts","./node_modules/next/dist/build/rendering-mode.d.ts","./node_modules/next/dist/server/lib/router-utils/build-prefetch-segment-data-route.d.ts","./node_modules/next/dist/server/require-hook.d.ts","./node_modules/next/dist/server/lib/experimental/ppr.d.ts","./node_modules/next/dist/build/webpack/plugins/app-build-manifest-plugin.d.ts","./node_modules/next/dist/lib/page-types.d.ts","./node_modules/next/dist/build/segment-config/app/app-segment-config.d.ts","./node_modules/next/dist/build/segment-config/pages/pages-segment-config.d.ts","./node_modules/next/dist/build/analysis/get-page-static-info.d.ts","./node_modules/next/dist/build/webpack/loaders/get-module-build-info.d.ts","./node_modules/next/dist/build/webpack/plugins/middleware-plugin.d.ts","./node_modules/next/dist/server/node-polyfill-crypto.d.ts","./node_modules/next/dist/server/node-environment-baseline.d.ts","./node_modules/next/dist/server/node-environment-extensions/error-inspect.d.ts","./node_modules/next/dist/server/node-environment-extensions/random.d.ts","./node_modules/next/dist/server/node-environment-extensions/date.d.ts","./node_modules/next/dist/server/node-environment-extensions/web-crypto.d.ts","./node_modules/next/dist/server/node-environment-extensions/node-crypto.d.ts","./node_modules/next/dist/server/node-environment.d.ts","./node_modules/next/dist/build/page-extensions-type.d.ts","./node_modules/next/dist/build/webpack/plugins/flight-manifest-plugin.d.ts","./node_modules/next/dist/server/instrumentation/types.d.ts","./node_modules/next/dist/lib/coalesced-function.d.ts","./node_modules/next/dist/shared/lib/router/utils/middleware-route-matcher.d.ts","./node_modules/next/dist/server/lib/router-utils/types.d.ts","./node_modules/next/dist/shared/lib/modern-browserslist-target.d.ts","./node_modules/next/dist/shared/lib/constants.d.ts","./node_modules/next/dist/trace/types.d.ts","./node_modules/next/dist/trace/trace.d.ts","./node_modules/next/dist/trace/shared.d.ts","./node_modules/next/dist/trace/index.d.ts","./node_modules/next/dist/build/load-jsconfig.d.ts","./node_modules/@next/env/dist/index.d.ts","./node_modules/next/dist/build/webpack/plugins/telemetry-plugin/use-cache-tracker-utils.d.ts","./node_modules/next/dist/build/webpack/plugins/telemetry-plugin/telemetry-plugin.d.ts","./node_modules/next/dist/telemetry/storage.d.ts","./node_modules/next/dist/build/build-context.d.ts","./node_modules/next/dist/shared/lib/bloom-filter.d.ts","./node_modules/next/dist/build/webpack-config.d.ts","./node_modules/next/dist/server/route-kind.d.ts","./node_modules/next/dist/server/route-definitions/route-definition.d.ts","./node_modules/next/dist/build/swc/generated-native.d.ts","./node_modules/next/dist/build/swc/types.d.ts","./node_modules/next/dist/server/dev/parse-version-info.d.ts","./node_modules/next/dist/next-devtools/shared/types.d.ts","./node_modules/next/dist/server/dev/dev-indicator-server-state.d.ts","./node_modules/next/dist/server/lib/parse-stack.d.ts","./node_modules/next/dist/next-devtools/server/shared.d.ts","./node_modules/next/dist/next-devtools/shared/stack-frame.d.ts","./node_modules/next/dist/next-devtools/dev-overlay/utils/get-error-by-type.d.ts","./node_modules/@types/react/jsx-runtime.d.ts","./node_modules/next/dist/next-devtools/dev-overlay/container/runtime-error/render-error.d.ts","./node_modules/next/dist/next-devtools/dev-overlay/shared.d.ts","./node_modules/next/dist/server/dev/hot-reloader-types.d.ts","./node_modules/next/dist/server/lib/cache-handlers/types.d.ts","./node_modules/next/dist/server/response-cache/types.d.ts","./node_modules/next/dist/server/resume-data-cache/cache-store.d.ts","./node_modules/next/dist/server/resume-data-cache/resume-data-cache.d.ts","./node_modules/next/dist/server/render-result.d.ts","./node_modules/next/dist/server/lib/i18n-provider.d.ts","./node_modules/next/dist/server/web/next-url.d.ts","./node_modules/next/dist/compiled/@edge-runtime/cookies/index.d.ts","./node_modules/next/dist/server/web/spec-extension/cookies.d.ts","./node_modules/next/dist/server/web/spec-extension/request.d.ts","./node_modules/next/dist/server/after/builtin-request-context.d.ts","./node_modules/next/dist/server/web/spec-extension/fetch-event.d.ts","./node_modules/next/dist/server/web/spec-extension/response.d.ts","./node_modules/next/dist/build/segment-config/middleware/middleware-config.d.ts","./node_modules/next/dist/server/web/types.d.ts","./node_modules/next/dist/build/webpack/plugins/pages-manifest-plugin.d.ts","./node_modules/next/dist/shared/lib/router/utils/parse-url.d.ts","./node_modules/next/dist/server/base-http/node.d.ts","./node_modules/next/dist/build/webpack/plugins/next-font-manifest-plugin.d.ts","./node_modules/next/dist/server/route-definitions/locale-route-definition.d.ts","./node_modules/next/dist/server/route-definitions/pages-route-definition.d.ts","./node_modules/next/dist/shared/lib/mitt.d.ts","./node_modules/next/dist/client/with-router.d.ts","./node_modules/next/dist/client/router.d.ts","./node_modules/next/dist/client/route-loader.d.ts","./node_modules/next/dist/client/page-loader.d.ts","./node_modules/next/dist/shared/lib/router/router.d.ts","./node_modules/next/dist/shared/lib/router-context.shared-runtime.d.ts","./node_modules/next/dist/shared/lib/loadable-context.shared-runtime.d.ts","./node_modules/next/dist/shared/lib/loadable.shared-runtime.d.ts","./node_modules/next/dist/shared/lib/image-config-context.shared-runtime.d.ts","./node_modules/next/dist/shared/lib/hooks-client-context.shared-runtime.d.ts","./node_modules/next/dist/shared/lib/head-manager-context.shared-runtime.d.ts","./node_modules/next/dist/server/route-definitions/app-page-route-definition.d.ts","./node_modules/next/dist/build/webpack/loaders/metadata/types.d.ts","./node_modules/next/dist/build/webpack/loaders/next-app-loader/index.d.ts","./node_modules/next/dist/server/lib/app-dir-module.d.ts","./node_modules/next/dist/server/web/spec-extension/adapters/request-cookies.d.ts","./node_modules/next/dist/server/async-storage/draft-mode-provider.d.ts","./node_modules/next/dist/server/web/spec-extension/adapters/headers.d.ts","./node_modules/next/dist/server/app-render/cache-signal.d.ts","./node_modules/next/dist/server/app-render/dynamic-rendering.d.ts","./node_modules/next/dist/server/request/fallback-params.d.ts","./node_modules/next/dist/server/app-render/work-unit-async-storage-instance.d.ts","./node_modules/next/dist/server/response-cache/index.d.ts","./node_modules/next/dist/server/lib/lazy-result.d.ts","./node_modules/next/dist/server/lib/implicit-tags.d.ts","./node_modules/next/dist/server/app-render/work-unit-async-storage.external.d.ts","./node_modules/next/dist/shared/lib/deep-readonly.d.ts","./node_modules/next/dist/shared/lib/router/utils/parse-relative-url.d.ts","./node_modules/next/dist/server/app-render/app-render.d.ts","./node_modules/next/dist/shared/lib/server-inserted-html.shared-runtime.d.ts","./node_modules/next/dist/shared/lib/amp-context.shared-runtime.d.ts","./node_modules/next/dist/server/route-modules/app-page/vendored/contexts/entrypoints.d.ts","./node_modules/next/dist/server/route-modules/app-page/module.compiled.d.ts","./node_modules/next/dist/client/components/error-boundary.d.ts","./node_modules/next/dist/client/components/layout-router.d.ts","./node_modules/next/dist/client/components/render-from-template-context.d.ts","./node_modules/next/dist/server/app-render/action-async-storage-instance.d.ts","./node_modules/next/dist/server/app-render/action-async-storage.external.d.ts","./node_modules/next/dist/client/components/client-page.d.ts","./node_modules/next/dist/client/components/client-segment.d.ts","./node_modules/next/dist/server/request/search-params.d.ts","./node_modules/next/dist/client/components/hooks-server-context.d.ts","./node_modules/next/dist/client/components/http-access-fallback/error-boundary.d.ts","./node_modules/next/dist/lib/metadata/types/alternative-urls-types.d.ts","./node_modules/next/dist/lib/metadata/types/extra-types.d.ts","./node_modules/next/dist/lib/metadata/types/metadata-types.d.ts","./node_modules/next/dist/lib/metadata/types/manifest-types.d.ts","./node_modules/next/dist/lib/metadata/types/opengraph-types.d.ts","./node_modules/next/dist/lib/metadata/types/twitter-types.d.ts","./node_modules/next/dist/lib/metadata/types/metadata-interface.d.ts","./node_modules/next/dist/lib/metadata/types/resolvers.d.ts","./node_modules/next/dist/lib/metadata/types/icons.d.ts","./node_modules/next/dist/lib/metadata/resolve-metadata.d.ts","./node_modules/next/dist/lib/metadata/metadata.d.ts","./node_modules/next/dist/lib/framework/boundary-components.d.ts","./node_modules/next/dist/server/app-render/rsc/preloads.d.ts","./node_modules/next/dist/server/app-render/rsc/postpone.d.ts","./node_modules/next/dist/server/app-render/rsc/taint.d.ts","./node_modules/next/dist/shared/lib/segment-cache/segment-value-encoding.d.ts","./node_modules/next/dist/server/app-render/collect-segment-data.d.ts","./node_modules/next/dist/next-devtools/userspace/app/segment-explorer-node.d.ts","./node_modules/next/dist/server/app-render/entry-base.d.ts","./node_modules/next/dist/build/templates/app-page.d.ts","./node_modules/@types/react/jsx-dev-runtime.d.ts","./node_modules/@types/react/compiler-runtime.d.ts","./node_modules/next/dist/server/route-modules/app-page/vendored/rsc/entrypoints.d.ts","./node_modules/@types/react-dom/client.d.ts","./node_modules/@types/react-dom/static.d.ts","./node_modules/@types/react-dom/server.d.ts","./node_modules/next/dist/server/route-modules/app-page/vendored/ssr/entrypoints.d.ts","./node_modules/next/dist/server/route-modules/app-page/module.d.ts","./node_modules/next/dist/server/web/adapter.d.ts","./node_modules/next/dist/server/use-cache/cache-life.d.ts","./node_modules/next/dist/server/app-render/types.d.ts","./node_modules/next/dist/client/components/router-reducer/router-reducer-types.d.ts","./node_modules/next/dist/client/flight-data-helpers.d.ts","./node_modules/next/dist/client/components/router-reducer/fetch-server-response.d.ts","./node_modules/next/dist/shared/lib/app-router-context.shared-runtime.d.ts","./node_modules/next/dist/server/route-modules/pages/vendored/contexts/entrypoints.d.ts","./node_modules/next/dist/server/route-modules/pages/module.compiled.d.ts","./node_modules/next/dist/build/templates/pages.d.ts","./node_modules/next/dist/server/route-modules/pages/module.d.ts","./node_modules/next/dist/next-devtools/userspace/pages/pages-dev-overlay-setup.d.ts","./node_modules/next/dist/server/render.d.ts","./node_modules/next/dist/server/route-definitions/pages-api-route-definition.d.ts","./node_modules/next/dist/server/route-matches/pages-api-route-match.d.ts","./node_modules/next/dist/server/route-matchers/route-matcher.d.ts","./node_modules/next/dist/server/route-matcher-providers/route-matcher-provider.d.ts","./node_modules/next/dist/server/route-matcher-managers/route-matcher-manager.d.ts","./node_modules/next/dist/server/normalizers/normalizer.d.ts","./node_modules/next/dist/server/normalizers/locale-route-normalizer.d.ts","./node_modules/next/dist/server/normalizers/request/pathname-normalizer.d.ts","./node_modules/next/dist/server/normalizers/request/suffix.d.ts","./node_modules/next/dist/server/normalizers/request/rsc.d.ts","./node_modules/next/dist/server/normalizers/request/prefetch-rsc.d.ts","./node_modules/next/dist/server/normalizers/request/next-data.d.ts","./node_modules/next/dist/server/normalizers/request/segment-prefix-rsc.d.ts","./node_modules/next/dist/build/static-paths/types.d.ts","./node_modules/next/dist/server/base-server.d.ts","./node_modules/next/dist/server/lib/async-callback-set.d.ts","./node_modules/next/dist/shared/lib/router/utils/route-regex.d.ts","./node_modules/next/dist/shared/lib/router/utils/route-matcher.d.ts","./node_modules/sharp/lib/index.d.ts","./node_modules/next/dist/server/image-optimizer.d.ts","./node_modules/next/dist/server/next-server.d.ts","./node_modules/next/dist/server/lib/types.d.ts","./node_modules/next/dist/server/lib/lru-cache.d.ts","./node_modules/next/dist/server/lib/dev-bundler-service.d.ts","./node_modules/next/dist/server/dev/static-paths-worker.d.ts","./node_modules/next/dist/server/dev/next-dev-server.d.ts","./node_modules/next/dist/server/next.d.ts","./node_modules/next/dist/server/lib/render-server.d.ts","./node_modules/next/dist/server/lib/router-server.d.ts","./node_modules/next/dist/shared/lib/router/utils/path-match.d.ts","./node_modules/next/dist/server/lib/router-utils/filesystem.d.ts","./node_modules/next/dist/server/lib/router-utils/setup-dev-bundler.d.ts","./node_modules/next/dist/server/lib/router-utils/router-server-context.d.ts","./node_modules/next/dist/server/route-modules/route-module.d.ts","./node_modules/next/dist/server/load-components.d.ts","./node_modules/next/dist/server/route-definitions/app-route-route-definition.d.ts","./node_modules/next/dist/server/async-storage/work-store.d.ts","./node_modules/next/dist/server/web/http.d.ts","./node_modules/next/dist/server/route-modules/app-route/shared-modules.d.ts","./node_modules/next/dist/client/components/redirect-status-code.d.ts","./node_modules/next/dist/client/components/redirect-error.d.ts","./node_modules/next/dist/build/templates/app-route.d.ts","./node_modules/next/dist/server/route-modules/app-route/module.d.ts","./node_modules/next/dist/server/route-modules/app-route/module.compiled.d.ts","./node_modules/next/dist/build/segment-config/app/app-segments.d.ts","./node_modules/next/dist/build/utils.d.ts","./node_modules/next/dist/build/turborepo-access-trace/types.d.ts","./node_modules/next/dist/build/turborepo-access-trace/result.d.ts","./node_modules/next/dist/build/turborepo-access-trace/helpers.d.ts","./node_modules/next/dist/build/turborepo-access-trace/index.d.ts","./node_modules/next/dist/export/routes/types.d.ts","./node_modules/next/dist/export/types.d.ts","./node_modules/next/dist/export/worker.d.ts","./node_modules/next/dist/build/worker.d.ts","./node_modules/next/dist/build/index.d.ts","./node_modules/next/dist/server/lib/incremental-cache/index.d.ts","./node_modules/next/dist/server/after/after.d.ts","./node_modules/next/dist/server/after/after-context.d.ts","./node_modules/next/dist/server/app-render/work-async-storage-instance.d.ts","./node_modules/next/dist/server/app-render/work-async-storage.external.d.ts","./node_modules/next/dist/server/request/params.d.ts","./node_modules/next/dist/server/route-matches/route-match.d.ts","./node_modules/next/dist/server/request-meta.d.ts","./node_modules/next/dist/cli/next-test.d.ts","./node_modules/next/dist/server/config-shared.d.ts","./node_modules/next/dist/server/base-http/index.d.ts","./node_modules/next/dist/server/api-utils/index.d.ts","./node_modules/next/dist/types.d.ts","./node_modules/next/dist/shared/lib/html-context.shared-runtime.d.ts","./node_modules/next/dist/shared/lib/utils.d.ts","./node_modules/next/dist/pages/_app.d.ts","./node_modules/next/app.d.ts","./node_modules/next/dist/server/web/spec-extension/unstable-cache.d.ts","./node_modules/next/dist/server/web/spec-extension/revalidate.d.ts","./node_modules/next/dist/server/web/spec-extension/unstable-no-store.d.ts","./node_modules/next/dist/server/use-cache/cache-tag.d.ts","./node_modules/next/cache.d.ts","./node_modules/next/dist/shared/lib/runtime-config.external.d.ts","./node_modules/next/config.d.ts","./node_modules/next/dist/pages/_document.d.ts","./node_modules/next/document.d.ts","./node_modules/next/dist/shared/lib/dynamic.d.ts","./node_modules/next/dynamic.d.ts","./node_modules/next/dist/pages/_error.d.ts","./node_modules/next/error.d.ts","./node_modules/next/dist/shared/lib/head.d.ts","./node_modules/next/head.d.ts","./node_modules/next/dist/server/request/cookies.d.ts","./node_modules/next/dist/server/request/headers.d.ts","./node_modules/next/dist/server/request/draft-mode.d.ts","./node_modules/next/headers.d.ts","./node_modules/next/dist/shared/lib/get-img-props.d.ts","./node_modules/next/dist/client/image-component.d.ts","./node_modules/next/dist/shared/lib/image-external.d.ts","./node_modules/next/image.d.ts","./node_modules/next/dist/client/link.d.ts","./node_modules/next/link.d.ts","./node_modules/next/dist/client/components/redirect.d.ts","./node_modules/next/dist/client/components/not-found.d.ts","./node_modules/next/dist/client/components/forbidden.d.ts","./node_modules/next/dist/client/components/unauthorized.d.ts","./node_modules/next/dist/client/components/unstable-rethrow.server.d.ts","./node_modules/next/dist/client/components/unstable-rethrow.d.ts","./node_modules/next/dist/client/components/navigation.react-server.d.ts","./node_modules/next/dist/client/components/unrecognized-action-error.d.ts","./node_modules/next/dist/client/components/navigation.d.ts","./node_modules/next/navigation.d.ts","./node_modules/next/router.d.ts","./node_modules/next/dist/client/script.d.ts","./node_modules/next/script.d.ts","./node_modules/next/dist/server/web/spec-extension/user-agent.d.ts","./node_modules/next/dist/compiled/@edge-runtime/primitives/url.d.ts","./node_modules/next/dist/server/web/spec-extension/image-response.d.ts","./node_modules/next/dist/compiled/@vercel/og/satori/index.d.ts","./node_modules/next/dist/compiled/@vercel/og/emoji/index.d.ts","./node_modules/next/dist/compiled/@vercel/og/types.d.ts","./node_modules/next/dist/server/after/index.d.ts","./node_modules/next/dist/server/request/root-params.d.ts","./node_modules/next/dist/server/request/connection.d.ts","./node_modules/next/server.d.ts","./node_modules/next/types/global.d.ts","./node_modules/next/types/compiled.d.ts","./node_modules/next/types.d.ts","./node_modules/next/index.d.ts","./node_modules/next/image-types/global.d.ts","./next-env.d.ts","./middleware.ts","./node_modules/source-map-js/source-map.d.ts","./node_modules/postcss/lib/previous-map.d.ts","./node_modules/postcss/lib/input.d.ts","./node_modules/postcss/lib/css-syntax-error.d.ts","./node_modules/postcss/lib/declaration.d.ts","./node_modules/postcss/lib/root.d.ts","./node_modules/postcss/lib/warning.d.ts","./node_modules/postcss/lib/lazy-result.d.ts","./node_modules/postcss/lib/no-work-result.d.ts","./node_modules/postcss/lib/processor.d.ts","./node_modules/postcss/lib/result.d.ts","./node_modules/postcss/lib/document.d.ts","./node_modules/postcss/lib/rule.d.ts","./node_modules/postcss/lib/node.d.ts","./node_modules/postcss/lib/comment.d.ts","./node_modules/postcss/lib/container.d.ts","./node_modules/postcss/lib/at-rule.d.ts","./node_modules/postcss/lib/list.d.ts","./node_modules/postcss/lib/postcss.d.ts","./node_modules/postcss/lib/postcss.d.mts","./node_modules/tailwindcss/types/generated/corepluginlist.d.ts","./node_modules/tailwindcss/types/generated/colors.d.ts","./node_modules/tailwindcss/types/config.d.ts","./node_modules/tailwindcss/types/index.d.ts","./tailwind.config.ts","./node_modules/clsx/clsx.d.mts","./node_modules/tailwind-merge/dist/types.d.ts","./components/ui/utils.ts","./lib/text.ts","./lib/auth.ts","./lib/api.ts","./lib/branding.ts","./lib/datetime.ts","./lib/document-flow.ts","./lib/legal-entities.ts","./node_modules/lucide-react/dist/lucide-react.d.ts","./lib/navigation.ts","./components/ui/brand-provider.tsx","./components/ui/theme-provider.tsx","./app/layout.tsx","./components/ui/logo-badge.tsx","./components/app-shell/app-shell.tsx","./app/(app)/layout.tsx","./node_modules/@types/d3-time/index.d.ts","./node_modules/@types/d3-scale/index.d.ts","./node_modules/victory-vendor/d3-scale.d.ts","./node_modules/recharts/types/shape/dot.d.ts","./node_modules/recharts/types/component/text.d.ts","./node_modules/recharts/types/zindex/zindexlayer.d.ts","./node_modules/recharts/types/cartesian/getcartesianposition.d.ts","./node_modules/recharts/types/component/label.d.ts","./node_modules/recharts/types/cartesian/cartesianaxis.d.ts","./node_modules/recharts/types/util/scale/customscaledefinition.d.ts","./node_modules/redux/dist/redux.d.ts","./node_modules/@reduxjs/toolkit/node_modules/immer/dist/immer.d.ts","./node_modules/reselect/dist/reselect.d.ts","./node_modules/redux-thunk/dist/redux-thunk.d.ts","./node_modules/@reduxjs/toolkit/dist/uncheckedindexed.ts","./node_modules/@reduxjs/toolkit/dist/index.d.mts","./node_modules/recharts/types/state/cartesianaxisslice.d.ts","./node_modules/recharts/types/synchronisation/types.d.ts","./node_modules/recharts/types/chart/types.d.ts","./node_modules/recharts/types/component/defaulttooltipcontent.d.ts","./node_modules/recharts/types/context/brushupdatecontext.d.ts","./node_modules/recharts/types/state/chartdataslice.d.ts","./node_modules/recharts/types/state/types/linesettings.d.ts","./node_modules/recharts/types/state/types/scattersettings.d.ts","./node_modules/@types/d3-path/index.d.ts","./node_modules/@types/d3-shape/index.d.ts","./node_modules/victory-vendor/d3-shape.d.ts","./node_modules/recharts/types/shape/curve.d.ts","./node_modules/recharts/types/component/labellist.d.ts","./node_modules/recharts/types/component/defaultlegendcontent.d.ts","./node_modules/recharts/types/util/payload/getuniqpayload.d.ts","./node_modules/recharts/types/util/useelementoffset.d.ts","./node_modules/recharts/types/component/legend.d.ts","./node_modules/recharts/types/state/legendslice.d.ts","./node_modules/recharts/types/state/types/stackedgraphicalitem.d.ts","./node_modules/recharts/types/util/stacks/stacktypes.d.ts","./node_modules/recharts/types/util/scale/rechartsscale.d.ts","./node_modules/recharts/types/util/chartutils.d.ts","./node_modules/recharts/types/state/selectors/areaselectors.d.ts","./node_modules/recharts/types/cartesian/area.d.ts","./node_modules/recharts/types/state/types/areasettings.d.ts","./node_modules/recharts/types/animation/easing.d.ts","./node_modules/recharts/types/shape/rectangle.d.ts","./node_modules/recharts/types/cartesian/bar.d.ts","./node_modules/recharts/types/util/barutils.d.ts","./node_modules/recharts/types/state/types/barsettings.d.ts","./node_modules/recharts/types/state/types/radialbarsettings.d.ts","./node_modules/recharts/types/util/svgpropertiesnoevents.d.ts","./node_modules/recharts/types/util/useuniqueid.d.ts","./node_modules/recharts/types/state/types/piesettings.d.ts","./node_modules/recharts/types/state/types/radarsettings.d.ts","./node_modules/recharts/types/state/graphicalitemsslice.d.ts","./node_modules/recharts/types/state/tooltipslice.d.ts","./node_modules/recharts/types/state/optionsslice.d.ts","./node_modules/recharts/types/state/layoutslice.d.ts","./node_modules/immer/dist/immer.d.ts","./node_modules/recharts/types/util/ifoverflow.d.ts","./node_modules/recharts/types/util/resolvedefaultprops.d.ts","./node_modules/recharts/types/cartesian/referenceline.d.ts","./node_modules/recharts/types/state/referenceelementsslice.d.ts","./node_modules/recharts/types/state/brushslice.d.ts","./node_modules/recharts/types/state/rootpropsslice.d.ts","./node_modules/recharts/types/state/polaraxisslice.d.ts","./node_modules/recharts/types/state/polaroptionsslice.d.ts","./node_modules/recharts/types/cartesian/line.d.ts","./node_modules/recharts/types/util/constants.d.ts","./node_modules/recharts/types/util/scatterutils.d.ts","./node_modules/recharts/types/shape/symbols.d.ts","./node_modules/recharts/types/cartesian/scatter.d.ts","./node_modules/recharts/types/cartesian/errorbar.d.ts","./node_modules/recharts/types/state/errorbarslice.d.ts","./node_modules/recharts/types/state/zindexslice.d.ts","./node_modules/recharts/types/state/eventsettingsslice.d.ts","./node_modules/recharts/types/state/renderedticksslice.d.ts","./node_modules/recharts/types/state/store.d.ts","./node_modules/recharts/types/cartesian/getticks.d.ts","./node_modules/recharts/types/cartesian/cartesiangrid.d.ts","./node_modules/recharts/types/state/selectors/combiners/combinedisplayedstackeddata.d.ts","./node_modules/recharts/types/state/selectors/selecttooltipaxistype.d.ts","./node_modules/recharts/types/types.d.ts","./node_modules/recharts/types/hooks.d.ts","./node_modules/recharts/types/state/selectors/axisselectors.d.ts","./node_modules/recharts/types/component/dots.d.ts","./node_modules/recharts/types/util/typeddatakey.d.ts","./node_modules/recharts/types/util/types.d.ts","./node_modules/recharts/types/container/surface.d.ts","./node_modules/recharts/types/container/layer.d.ts","./node_modules/recharts/types/component/cursor.d.ts","./node_modules/recharts/types/component/tooltip.d.ts","./node_modules/recharts/types/component/responsivecontainer.d.ts","./node_modules/recharts/types/component/cell.d.ts","./node_modules/recharts/types/component/customized.d.ts","./node_modules/recharts/types/shape/sector.d.ts","./node_modules/recharts/types/shape/polygon.d.ts","./node_modules/recharts/types/shape/cross.d.ts","./node_modules/recharts/types/polar/polargrid.d.ts","./node_modules/recharts/types/polar/defaultpolarradiusaxisprops.d.ts","./node_modules/recharts/types/polar/polarradiusaxis.d.ts","./node_modules/recharts/types/polar/defaultpolarangleaxisprops.d.ts","./node_modules/recharts/types/polar/polarangleaxis.d.ts","./node_modules/recharts/types/context/tooltipcontext.d.ts","./node_modules/recharts/types/polar/pie.d.ts","./node_modules/recharts/types/polar/radar.d.ts","./node_modules/recharts/types/util/radialbarutils.d.ts","./node_modules/recharts/types/polar/radialbar.d.ts","./node_modules/recharts/types/cartesian/brush.d.ts","./node_modules/recharts/types/cartesian/referencedot.d.ts","./node_modules/recharts/types/util/excludeeventprops.d.ts","./node_modules/recharts/types/util/svgpropertiesandevents.d.ts","./node_modules/recharts/types/cartesian/referencearea.d.ts","./node_modules/recharts/types/cartesian/barstack.d.ts","./node_modules/recharts/types/cartesian/xaxis.d.ts","./node_modules/recharts/types/cartesian/yaxis.d.ts","./node_modules/recharts/types/cartesian/zaxis.d.ts","./node_modules/recharts/types/chart/linechart.d.ts","./node_modules/recharts/types/chart/barchart.d.ts","./node_modules/recharts/types/chart/piechart.d.ts","./node_modules/recharts/types/chart/treemap.d.ts","./node_modules/recharts/types/chart/sankey.d.ts","./node_modules/recharts/types/chart/radarchart.d.ts","./node_modules/recharts/types/chart/scatterchart.d.ts","./node_modules/recharts/types/chart/areachart.d.ts","./node_modules/recharts/types/chart/radialbarchart.d.ts","./node_modules/recharts/types/chart/composedchart.d.ts","./node_modules/recharts/types/chart/sunburstchart.d.ts","./node_modules/recharts/types/shape/trapezoid.d.ts","./node_modules/recharts/types/cartesian/funnel.d.ts","./node_modules/recharts/types/chart/funnelchart.d.ts","./node_modules/recharts/types/util/global.d.ts","./node_modules/recharts/types/zindex/defaultzindexes.d.ts","./node_modules/decimal.js-light/decimal.d.ts","./node_modules/recharts/types/util/scale/getnicetickvalues.d.ts","./node_modules/recharts/types/context/chartlayoutcontext.d.ts","./node_modules/recharts/types/util/getrelativecoordinate.d.ts","./node_modules/recharts/types/util/createcartesiancharts.d.ts","./node_modules/recharts/types/util/createpolarcharts.d.ts","./node_modules/recharts/types/index.d.ts","./components/ui/live-clock.tsx","./components/app-shell/dashboard.tsx","./app/(app)/dashboard/page.tsx","./components/templates/templates-workspace.tsx","./app/(app)/dashboard/actos-plantillas/page.tsx","./components/process/process-placeholder.tsx","./app/(app)/dashboard/ayuda/page.tsx","./components/cases/cases-workspace.tsx","./app/(app)/dashboard/casos/page.tsx","./components/cases/case-detail-workspace.tsx","./app/(app)/dashboard/casos/[caseid]/page.tsx","./components/persons/person-lookup.tsx","./components/persons/legal-entity-lookup.tsx","./components/ui/searchable-select.tsx","./components/ui/validated-input.tsx","./components/cases/create-case-wizard.tsx","./app/(app)/dashboard/casos/crear/page.tsx","./components/notaries/commercial-workspace.tsx","./app/(app)/dashboard/comercial/page.tsx","./components/notaries/notary-crm-workspace.tsx","./app/(app)/dashboard/comercial/[notaryid]/page.tsx","./app/(app)/dashboard/configuracion/page.tsx","./app/(app)/dashboard/lotes/page.tsx","./components/notaries/notaries-catalog.tsx","./app/(app)/dashboard/notarias/page.tsx","./components/notaries/notary-detail-workspace.tsx","./app/(app)/dashboard/notarias/[notaryid]/page.tsx","./components/users/user-profile-workspace.tsx","./app/(app)/dashboard/perfil/page.tsx","./components/roles/roles-workspace.tsx","./app/(app)/dashboard/roles/page.tsx","./components/system/system-status-workspace.tsx","./app/(app)/dashboard/system-status/page.tsx","./components/users/users-admin-workspace.tsx","./app/(app)/dashboard/usuarios/page.tsx","./components/marketing/landing-page.tsx","./app/(marketing)/page.tsx","./components/marketing/login-panel.tsx","./app/(marketing)/login/page.tsx","./components/app-shell/notaries-settings.tsx","./components/ui/hybrid-autocomplete.tsx","./.next/types/cache-life.d.ts","./.next/types/validator.ts","./.next/types/app/layout.ts","./.next/types/app/(app)/layout.ts","./.next/types/app/(app)/dashboard/page.ts","./.next/types/app/(app)/dashboard/actos-plantillas/page.ts","./.next/types/app/(app)/dashboard/casos/page.ts","./.next/types/app/(app)/dashboard/casos/[caseid]/page.ts","./.next/types/app/(app)/dashboard/casos/crear/page.ts","./.next/types/app/(marketing)/page.ts","./.next/types/app/(marketing)/login/page.ts","./node_modules/@types/d3-array/index.d.ts","./node_modules/@types/d3-color/index.d.ts","./node_modules/@types/d3-ease/index.d.ts","./node_modules/@types/d3-interpolate/index.d.ts","./node_modules/@types/d3-timer/index.d.ts","./node_modules/@types/use-sync-external-store/index.d.ts"],"fileIdsList":[[100,148,165,166,341,687],[100,148,165,166,341,693],[100,148,165,166,341,699],[100,148,165,166,341,691],[100,148,165,166,341,685],[100,148,165,166,341,545],[100,148,165,166,341,721],[100,148,165,166,341,719],[100,148,165,166,341,542],[100,148,165,166,448,449,450,451],[100,148,165,166],[83,100,148,165,166,498,542,545,685,687,689,691,693,699,701,703,704,705,707,709,711,713,715,717,719,721],[100,148,165,166,686],[100,148,165,166,688],[100,148,165,166,692],[100,148,165,166,698],[100,148,165,166,690],[100,148,165,166,702],[100,148,165,166,700],[100,148,165,166,708],[100,148,165,166,706],[100,148,165,166,684],[100,148,165,166,710],[100,148,165,166,712],[100,148,165,166,714],[100,148,165,166,716],[100,148,165,166,544],[100,148,165,166,720],[100,148,165,166,718],[100,148,165,166,499,540,541],[86,100,148,165,166,472,482,530,533,534,538,539,541,543],[86,100,148,165,166,533,535,538,682,683],[86,100,148,165,166,472,532,535,536,538],[86,100,148,165,166,472,533,538],[86,100,148,165,166,472,533,536,538,694,695,696,697],[86,100,148,165,166,470,472,534,538,543],[86,100,148,165,166,470,533],[86,100,148,165,166,472,533,538,682],[86,100,148,165,166,472,533,535,538],[86,100,148,165,166,537,538],[86,100,148,165,166,536,538],[100,148,165,166,538],[86,100,148,165,166,533,538],[86,100,148,165,166,533,535,538,683],[86,100,148,165,166,533,536,538],[86,100,148,165,166,534],[86,100,148,165,166],[86,100,148,165,166,535],[100,148,165,166,530],[86,100,148,165,166,538],[100,148,165,166,528,529],[100,148,165,166,531,532],[100,148,165,166,531],[100,148,165,166,533],[100,148,165,166,495],[83,100,148,165,166,499,500],[100,148,165,166,556,557,558,559,560],[100,148,165,166,736],[100,148,165,166,546],[100,148,165,166,570],[100,145,146,148,165,166],[100,147,148,165,166],[148,165,166],[100,148,153,165,166,183],[100,148,149,154,159,165,166,168,180,191],[100,148,149,150,159,165,166,168],[95,96,97,100,148,165,166],[100,148,151,165,166,192],[100,148,152,153,160,165,166,169],[100,148,153,165,166,180,188],[100,148,154,156,159,165,166,168],[100,147,148,155,165,166],[100,148,156,157,165,166],[100,148,158,159,165,166],[100,147,148,159,165,166],[100,148,159,160,161,165,166,180,191],[100,148,159,160,161,165,166,175,180,183],[100,141,148,156,159,162,165,166,168,180,191],[100,148,159,160,162,163,165,166,168,180,188,191],[100,148,162,164,165,166,180,188,191],[98,99,100,101,102,103,104,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197],[100,148,159,165,166],[100,148,165,166,167,191],[100,148,156,159,165,166,168,180],[100,148,165,166,169],[100,148,165,166,170],[100,147,148,165,166,171],[100,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197],[100,148,165,166,173],[100,148,165,166,174],[100,148,159,165,166,175,176],[100,148,165,166,175,177,192,194],[100,148,160,165,166],[100,148,159,165,166,180,181,183],[100,148,165,166,182,183],[100,148,165,166,180,181],[100,148,165,166,183],[100,148,165,166,184],[100,145,148,165,166,180,185,191],[100,148,159,165,166,186,187],[100,148,165,166,186,187],[100,148,153,165,166,168,180,188],[100,148,165,166,189],[100,148,165,166,168,190],[100,148,162,165,166,174,191],[100,148,153,165,166,192],[100,148,165,166,180,193],[100,148,165,166,167,194],[100,148,165,166,195],[100,141,148,165,166],[100,141,148,159,161,165,166,171,180,183,191,193,194,196],[100,148,165,166,180,197],[86,90,100,148,165,166,199,200,201,203,443,491],[86,90,100,148,165,166,199,200,201,202,358,443,491],[86,90,100,148,165,166,199,200,202,203,443,491],[86,100,148,165,166,203,358,359],[86,100,148,165,166,203,358],[86,90,100,148,165,166,200,201,202,203,443,491],[86,90,100,148,165,166,199,201,202,203,443,491],[84,85,100,148,165,166],[92,100,148,165,166],[100,148,165,166,446],[100,148,165,166,453],[100,148,165,166,207,221,222,223,225,440],[100,148,165,166,207,246,248,250,251,254,440,442],[100,148,165,166,207,211,213,214,215,216,217,429,440,442],[100,148,165,166,440],[100,148,165,166,222,324,410,419,436],[100,148,165,166,207],[100,148,165,166,204,436],[100,148,165,166,258],[100,148,165,166,257,440,442],[100,148,162,165,166,306,324,353,497],[100,148,162,165,166,317,333,419,435],[100,148,162,165,166,371],[100,148,165,166,423],[100,148,165,166,422,423,424],[100,148,165,166,422],[94,100,148,162,165,166,204,207,211,214,218,219,220,222,226,234,235,364,389,420,440,443],[100,148,165,166,207,224,242,246,247,252,253,440,497],[100,148,165,166,224,497],[100,148,165,166,235,242,304,440,497],[100,148,165,166,497],[100,148,165,166,207,224,225,497],[100,148,165,166,249,497],[100,148,165,166,218,421,428],[100,148,165,166,174,266,436],[100,148,165,166,266,436],[86,100,148,165,166,266],[86,100,148,165,166,325],[100,148,165,166,321,369,436,479,480],[100,148,165,166,416,473,474,475,476,478],[100,148,165,166,415],[100,148,165,166,415,416],[100,148,165,166,215,365,366,367],[100,148,165,166,365,368,369],[100,148,165,166,477],[100,148,165,166,365,369],[86,100,148,165,166,208,467],[86,100,148,165,166,191],[86,100,148,165,166,224,294],[86,100,148,165,166,224],[100,148,165,166,292,296],[86,100,148,165,166,293,445],[86,90,100,148,162,165,166,198,199,200,201,202,203,443,489,490],[100,148,162,165,166],[100,148,162,165,166,211,273,365,375,390,410,425,426,440,441,497],[100,148,165,166,234,427],[100,148,165,166,443],[100,148,165,166,206],[86,100,148,165,166,306,320,332,342,344,435],[100,148,165,166,174,306,320,341,342,343,435,496],[100,148,165,166,335,336,337,338,339,340],[100,148,165,166,337],[100,148,165,166,341],[100,148,165,166,264,265,266,268],[86,100,148,165,166,259,260,261,267],[100,148,165,166,264,267],[100,148,165,166,262],[100,148,165,166,263],[86,100,148,165,166,266,293,445],[86,100,148,165,166,266,444,445],[86,100,148,165,166,266,445],[100,148,165,166,390,432],[100,148,165,166,432],[100,148,162,165,166,441,445],[100,148,165,166,329],[100,147,148,165,166,328],[100,148,165,166,236,274,312,314,316,317,318,319,362,365,435,438,441],[100,148,165,166,236,350,365,369],[100,148,165,166,317,435],[86,100,148,165,166,317,326,327,329,330,331,332,333,334,345,346,347,348,349,351,352,435,436,497],[100,148,165,166,311],[100,148,162,165,166,174,236,237,273,288,318,362,363,364,369,390,410,431,440,441,442,443,497],[100,148,165,166,435],[100,147,148,165,166,222,315,318,364,431,433,434,441],[100,148,165,166,317],[100,147,148,165,166,273,278,307,308,309,310,311,312,313,314,316,435,436],[100,148,162,165,166,278,279,307,441,442],[100,148,165,166,222,364,365,390,431,435,441],[100,148,162,165,166,440,442],[100,148,162,165,166,180,438,441,442],[100,148,162,165,166,174,191,204,211,224,236,237,239,274,275,280,285,288,314,318,365,375,377,380,382,385,386,387,388,389,410,430,431,436,438,440,441,442],[100,148,162,165,166,180],[100,148,165,166,207,208,209,211,216,219,224,242,430,438,439,443,445,497],[100,148,162,165,166,180,191,254,256,258,259,260,261,268,497],[100,148,165,166,174,191,204,246,256,284,285,286,287,314,365,380,389,390,396,399,400,410,431,436,438],[100,148,165,166,218,219,234,364,389,431,440],[100,148,162,165,166,191,208,211,314,394,438,440],[100,148,165,166,305],[100,148,162,165,166,397,398,407],[100,148,165,166,438,440],[100,148,165,166,312,315],[100,148,165,166,314,318,430,445],[100,148,162,165,166,174,240,246,287,380,390,396,399,402,438],[100,148,162,165,166,218,234,246,403],[100,148,165,166,207,239,405,430,440],[100,148,162,165,166,191,440],[100,148,162,165,166,224,238,239,240,251,269,404,406,430,440],[94,100,148,165,166,236,318,409,443,445],[100,148,162,165,166,174,191,211,218,226,234,237,274,280,284,285,286,287,288,314,365,377,390,391,393,395,410,430,431,436,437,438,445],[100,148,162,165,166,180,218,396,401,407,438],[100,148,165,166,229,230,231,232,233],[100,148,165,166,275,381],[100,148,165,166,383],[100,148,165,166,381],[100,148,165,166,383,384],[100,148,162,165,166,211,214,215,273,441],[100,148,162,165,166,174,206,208,236,274,288,318,373,374,410,438,442,443,445],[100,148,162,165,166,174,191,210,215,314,374,437,441],[100,148,165,166,307],[100,148,165,166,308],[100,148,165,166,309],[100,148,165,166,436],[100,148,165,166,255,271],[100,148,162,165,166,211,255,274],[100,148,165,166,270,271],[100,148,165,166,272],[100,148,165,166,255,256],[100,148,165,166,255,289],[100,148,165,166,255],[100,148,165,166,275,379,437],[100,148,165,166,378],[100,148,165,166,256,436,437],[100,148,165,166,376,437],[100,148,165,166,256,436],[100,148,165,166,362],[100,148,165,166,211,216,274,303,306,312,314,318,320,323,354,357,361,365,409,430,438,441],[100,148,165,166,297,300,301,302,321,322,369],[86,100,148,165,166,201,203,266,355,356],[86,100,148,165,166,201,203,266,355,356,360],[100,148,165,166,418],[100,148,165,166,222,279,317,318,329,333,365,409,411,412,413,414,416,417,420,430,435,440],[100,148,165,166,369],[100,148,165,166,373],[100,148,162,165,166,274,290,370,372,375,409,438,443,445],[100,148,165,166,297,298,299,300,301,302,321,322,369,444],[94,100,148,162,165,166,174,191,237,255,256,288,314,318,407,408,410,430,431,440,441,443],[100,148,165,166,279,281,284,431],[100,148,162,165,166,275,440],[100,148,165,166,278,317],[100,148,165,166,277],[100,148,165,166,279,280],[100,148,165,166,276,278,440],[100,148,162,165,166,210,279,281,282,283,440,441],[86,100,148,165,166,365,366,368],[100,148,165,166,241],[86,100,148,165,166,208],[86,100,148,165,166,436],[86,94,100,148,165,166,288,318,443,445],[100,148,165,166,208,467,468],[86,100,148,165,166,296],[86,100,148,165,166,174,191,206,253,291,293,295,445],[100,148,165,166,224,436,441],[100,148,165,166,392,436],[100,148,165,166,365],[86,100,148,160,162,165,166,174,206,242,248,296,443,444],[86,100,148,165,166,199,200,201,202,203,443,491],[86,87,88,89,90,100,148,165,166],[100,148,153,165,166],[100,148,165,166,243,244,245],[100,148,165,166,243],[86,90,100,148,162,164,165,166,174,198,199,200,201,202,203,204,206,237,341,402,440,442,445,491],[100,148,165,166,455],[100,148,165,166,457],[100,148,165,166,459],[100,148,165,166,461],[100,148,165,166,463,464,465],[100,148,165,166,469],[91,93,100,148,165,166,447,452,454,456,458,460,462,466,470,472,482,483,485,495,496,497,498],[100,148,165,166,471],[100,148,165,166,481],[100,148,165,166,293],[100,148,165,166,484],[100,147,148,165,166,279,281,282,284,332,436,486,487,488,491,492,493,494],[100,148,165,166,198],[100,148,165,166,518],[100,148,165,166,516,518],[100,148,165,166,507,515,516,517,519,521],[100,148,165,166,505],[100,148,165,166,508,513,518,521],[100,148,165,166,504,521],[100,148,165,166,508,509,512,513,514,521],[100,148,165,166,508,509,510,512,513,521],[100,148,165,166,505,506,507,508,509,513,514,515,517,518,519,521],[100,148,165,166,521],[100,148,165,166,503,505,506,507,508,509,510,512,513,514,515,516,517,518,519,520],[100,148,165,166,503,521],[100,148,165,166,508,510,511,513,514,521],[100,148,165,166,512,521],[100,148,165,166,513,514,518,521],[100,148,165,166,506,516],[86,100,148,165,166,551,562,567,573,574,581,583,584,586,627,630],[86,100,148,165,166,551,562,567,572,574,583,587,588,590,591,627,630],[86,100,148,165,166,583,588,632],[86,100,148,165,166,566,630],[86,100,148,165,166,550,551,553,562,630],[86,100,148,165,166,551,562,583,621,630],[86,100,148,165,166,551,589,610,614,630],[86,100,148,165,166,574,597,598,630,671],[100,148,165,166,550,630],[100,148,165,166,562,630],[86,100,148,165,166,551,562,567,573,574,627,630],[86,100,148,165,166,551,553,588,602,654],[86,100,148,165,166,549,551,553,602],[86,100,148,165,166,551,553,582,602,603,630],[86,100,148,165,166,551,562,565,569,573,574,598,612,613,627,630],[86,100,148,165,166,555,562,630],[86,100,148,165,166,555,562,627,630],[86,100,148,165,166,630],[86,100,148,165,166,588,598,630],[86,100,148,165,166,550,598,630],[86,100,148,165,166,598,630],[86,100,148,165,166,563],[86,100,148,165,166,551,598,630],[86,100,148,165,166,549,551,630],[86,100,148,165,166,550,551,552,630],[86,100,148,165,166,550,551,553,630,682],[86,100,148,165,166,575,576,577],[86,100,148,165,166,562,564,565,576,598,630,633],[100,148,165,166,620,630],[100,148,165,166,562,563,582,625,627,630],[100,148,165,166,549,550,551,553,554,555,562,563,565,573,574,575,578,582,585,588,589,598,602,604,610,612,613,614,615,622,625,626,627,630,631,632,634,635,636,637,638,639,640,641,643,645,647,648,649,650,651,652,655,656,657,658,659,660,661,662,663,664,665,666,667,668,669,670,671,672,673,674,675,677,678,679,680,681],[86,100,148,165,166,551,567,574,593,595,630,646],[86,100,148,165,166,551,555,562,603,630,644],[86,100,148,165,166,551,562],[86,100,148,165,166,551,555,562,603,630,642],[86,100,148,165,166,551,574,582,594,603,630],[86,100,148,165,166,551,562,567,572,574,583,627,630,638,646,649],[86,100,148,165,166,572,630],[86,100,148,165,166,587,630],[100,148,165,166,556,561,630],[100,148,165,166,554,555,556,561,627,630],[100,148,165,166,556,561,566],[100,148,165,166,556,561,597,615,630],[100,148,165,166,556,561,562,567,568,569,586,591,592,595,596,630],[100,148,165,166,556,561,575,578,630],[100,148,165,166,556,561,598,630],[100,148,165,166,556,561,562],[100,148,165,166,556,561],[100,148,165,166,556,561,562,601,602,604],[100,148,165,166,556,561,562,601,630],[100,148,165,166,556,561,563,585,630],[100,148,165,166,581,597,620,630],[100,148,165,166,562,567,580,581,582,597,605,608,616,620,622,623,624,626,630],[100,148,165,166,562,567,580,581],[100,148,165,166,620],[100,148,165,166,561,562,567,579,597,598,599,600,605,606,607,608,609,616,617,618,619],[100,148,165,166,556,561,562,564,565,597,630],[100,148,165,166,567,580,585,597,630],[100,148,165,166,580,590,597],[100,148,165,166,567,597,630],[86,100,148,165,166,565,593,594,597,630],[100,148,165,166,597],[100,148,165,166,580,597],[100,148,165,166,565,567,597,630],[100,148,165,166,583,597,630],[100,148,165,166,598,630],[86,100,148,165,166,588,589,630],[100,148,165,166,565,572,579,581,582,598,627,630],[86,100,148,165,166,585,589,610,614,630,657,658,659,672],[86,100,148,165,166,630,643,645,647,648,650],[100,148,165,166,630],[86,100,148,165,166,650],[100,148,165,166,562,630,676],[100,148,165,166,555,630],[86,100,148,165,166,597,611,614,630],[100,148,165,166,572,580,583,597],[86,100,148,165,166,593,653],[86,100,148,165,166,548,549,550,553,554,555,562,563,564,567,585,593,627,628,629,682],[100,148,165,166,556],[100,148,165,166,180,198],[100,148,165,166,523,524],[100,148,165,166,522,525],[100,113,117,148,165,166,191],[100,113,148,165,166,180,191],[100,108,148,165,166],[100,110,113,148,165,166,188,191],[100,148,165,166,168,188],[100,108,148,165,166,198],[100,110,113,148,165,166,168,191],[100,105,106,109,112,148,159,165,166,180,191],[100,113,120,148,165,166],[100,105,111,148,165,166],[100,113,134,135,148,165,166],[100,109,113,148,165,166,183,191,198],[100,134,148,165,166,198],[100,107,108,148,165,166,198],[100,113,148,165,166],[100,107,108,109,110,111,112,113,114,115,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,135,136,137,138,139,140,148,165,166],[100,113,128,148,165,166],[100,113,120,121,148,165,166],[100,111,113,121,122,148,165,166],[100,112,148,165,166],[100,105,108,113,148,165,166],[100,113,117,121,122,148,165,166],[100,117,148,165,166],[100,111,113,116,148,165,166,191],[100,105,110,113,120,148,165,166],[100,148,165,166,180],[100,108,113,134,148,165,166,196,198],[100,148,165,166,547],[100,148,165,166,571],[100,148,165,166,526]],"fileInfos":[{"version":"c430d44666289dae81f30fa7b2edebf186ecc91a2d4c71266ea6ae76388792e1","affectsGlobalScope":true,"impliedFormat":1},{"version":"45b7ab580deca34ae9729e97c13cfd999df04416a79116c3bfb483804f85ded4","impliedFormat":1},{"version":"3facaf05f0c5fc569c5649dd359892c98a85557e3e0c847964caeb67076f4d75","impliedFormat":1},{"version":"e44bb8bbac7f10ecc786703fe0a6a4b952189f908707980ba8f3c8975a760962","impliedFormat":1},{"version":"5e1c4c362065a6b95ff952c0eab010f04dcd2c3494e813b493ecfd4fcb9fc0d8","impliedFormat":1},{"version":"68d73b4a11549f9c0b7d352d10e91e5dca8faa3322bfb77b661839c42b1ddec7","impliedFormat":1},{"version":"5efce4fc3c29ea84e8928f97adec086e3dc876365e0982cc8479a07954a3efd4","impliedFormat":1},{"version":"feecb1be483ed332fad555aff858affd90a48ab19ba7272ee084704eb7167569","impliedFormat":1},{"version":"ee7bad0c15b58988daa84371e0b89d313b762ab83cb5b31b8a2d1162e8eb41c2","impliedFormat":1},{"version":"27bdc30a0e32783366a5abeda841bc22757c1797de8681bbe81fbc735eeb1c10","impliedFormat":1},{"version":"8fd575e12870e9944c7e1d62e1f5a73fcf23dd8d3a321f2a2c74c20d022283fe","impliedFormat":1},{"version":"2ab096661c711e4a81cc464fa1e6feb929a54f5340b46b0a07ac6bbf857471f0","impliedFormat":1},{"version":"080941d9f9ff9307f7e27a83bcd888b7c8270716c39af943532438932ec1d0b9","affectsGlobalScope":true,"impliedFormat":1},{"version":"2e80ee7a49e8ac312cc11b77f1475804bee36b3b2bc896bead8b6e1266befb43","affectsGlobalScope":true,"impliedFormat":1},{"version":"c57796738e7f83dbc4b8e65132f11a377649c00dd3eee333f672b8f0a6bea671","affectsGlobalScope":true,"impliedFormat":1},{"version":"dc2df20b1bcdc8c2d34af4926e2c3ab15ffe1160a63e58b7e09833f616efff44","affectsGlobalScope":true,"impliedFormat":1},{"version":"515d0b7b9bea2e31ea4ec968e9edd2c39d3eebf4a2d5cbd04e88639819ae3b71","affectsGlobalScope":true,"impliedFormat":1},{"version":"0559b1f683ac7505ae451f9a96ce4c3c92bdc71411651ca6ddb0e88baaaad6a3","affectsGlobalScope":true,"impliedFormat":1},{"version":"0dc1e7ceda9b8b9b455c3a2d67b0412feab00bd2f66656cd8850e8831b08b537","affectsGlobalScope":true,"impliedFormat":1},{"version":"ce691fb9e5c64efb9547083e4a34091bcbe5bdb41027e310ebba8f7d96a98671","affectsGlobalScope":true,"impliedFormat":1},{"version":"8d697a2a929a5fcb38b7a65594020fcef05ec1630804a33748829c5ff53640d0","affectsGlobalScope":true,"impliedFormat":1},{"version":"4ff2a353abf8a80ee399af572debb8faab2d33ad38c4b4474cff7f26e7653b8d","affectsGlobalScope":true,"impliedFormat":1},{"version":"fb0f136d372979348d59b3f5020b4cdb81b5504192b1cacff5d1fbba29378aa1","affectsGlobalScope":true,"impliedFormat":1},{"version":"d15bea3d62cbbdb9797079416b8ac375ae99162a7fba5de2c6c505446486ac0a","affectsGlobalScope":true,"impliedFormat":1},{"version":"68d18b664c9d32a7336a70235958b8997ebc1c3b8505f4f1ae2b7e7753b87618","affectsGlobalScope":true,"impliedFormat":1},{"version":"eb3d66c8327153d8fa7dd03f9c58d351107fe824c79e9b56b462935176cdf12a","affectsGlobalScope":true,"impliedFormat":1},{"version":"38f0219c9e23c915ef9790ab1d680440d95419ad264816fa15009a8851e79119","affectsGlobalScope":true,"impliedFormat":1},{"version":"69ab18c3b76cd9b1be3d188eaf8bba06112ebbe2f47f6c322b5105a6fbc45a2e","affectsGlobalScope":true,"impliedFormat":1},{"version":"a680117f487a4d2f30ea46f1b4b7f58bef1480456e18ba53ee85c2746eeca012","affectsGlobalScope":true,"impliedFormat":1},{"version":"2f11ff796926e0832f9ae148008138ad583bd181899ab7dd768a2666700b1893","affectsGlobalScope":true,"impliedFormat":1},{"version":"4de680d5bb41c17f7f68e0419412ca23c98d5749dcaaea1896172f06435891fc","affectsGlobalScope":true,"impliedFormat":1},{"version":"954296b30da6d508a104a3a0b5d96b76495c709785c1d11610908e63481ee667","affectsGlobalScope":true,"impliedFormat":1},{"version":"ac9538681b19688c8eae65811b329d3744af679e0bdfa5d842d0e32524c73e1c","affectsGlobalScope":true,"impliedFormat":1},{"version":"0a969edff4bd52585473d24995c5ef223f6652d6ef46193309b3921d65dd4376","affectsGlobalScope":true,"impliedFormat":1},{"version":"9e9fbd7030c440b33d021da145d3232984c8bb7916f277e8ffd3dc2e3eae2bdb","affectsGlobalScope":true,"impliedFormat":1},{"version":"811ec78f7fefcabbda4bfa93b3eb67d9ae166ef95f9bff989d964061cbf81a0c","affectsGlobalScope":true,"impliedFormat":1},{"version":"717937616a17072082152a2ef351cb51f98802fb4b2fdabd32399843875974ca","affectsGlobalScope":true,"impliedFormat":1},{"version":"d7e7d9b7b50e5f22c915b525acc5a49a7a6584cf8f62d0569e557c5cfc4b2ac2","affectsGlobalScope":true,"impliedFormat":1},{"version":"71c37f4c9543f31dfced6c7840e068c5a5aacb7b89111a4364b1d5276b852557","affectsGlobalScope":true,"impliedFormat":1},{"version":"576711e016cf4f1804676043e6a0a5414252560eb57de9faceee34d79798c850","affectsGlobalScope":true,"impliedFormat":1},{"version":"89c1b1281ba7b8a96efc676b11b264de7a8374c5ea1e6617f11880a13fc56dc6","affectsGlobalScope":true,"impliedFormat":1},{"version":"74f7fa2d027d5b33eb0471c8e82a6c87216223181ec31247c357a3e8e2fddc5b","affectsGlobalScope":true,"impliedFormat":1},{"version":"d6d7ae4d1f1f3772e2a3cde568ed08991a8ae34a080ff1151af28b7f798e22ca","affectsGlobalScope":true,"impliedFormat":1},{"version":"063600664504610fe3e99b717a1223f8b1900087fab0b4cad1496a114744f8df","affectsGlobalScope":true,"impliedFormat":1},{"version":"934019d7e3c81950f9a8426d093458b65d5aff2c7c1511233c0fd5b941e608ab","affectsGlobalScope":true,"impliedFormat":1},{"version":"52ada8e0b6e0482b728070b7639ee42e83a9b1c22d205992756fe020fd9f4a47","affectsGlobalScope":true,"impliedFormat":1},{"version":"3bdefe1bfd4d6dee0e26f928f93ccc128f1b64d5d501ff4a8cf3c6371200e5e6","affectsGlobalScope":true,"impliedFormat":1},{"version":"59fb2c069260b4ba00b5643b907ef5d5341b167e7d1dbf58dfd895658bda2867","affectsGlobalScope":true,"impliedFormat":1},{"version":"639e512c0dfc3fad96a84caad71b8834d66329a1f28dc95e3946c9b58176c73a","affectsGlobalScope":true,"impliedFormat":1},{"version":"368af93f74c9c932edd84c58883e736c9e3d53cec1fe24c0b0ff451f529ceab1","affectsGlobalScope":true,"impliedFormat":1},{"version":"af3dd424cf267428f30ccfc376f47a2c0114546b55c44d8c0f1d57d841e28d74","affectsGlobalScope":true,"impliedFormat":1},{"version":"995c005ab91a498455ea8dfb63aa9f83fa2ea793c3d8aa344be4a1678d06d399","affectsGlobalScope":true,"impliedFormat":1},{"version":"959d36cddf5e7d572a65045b876f2956c973a586da58e5d26cde519184fd9b8a","affectsGlobalScope":true,"impliedFormat":1},{"version":"965f36eae237dd74e6cca203a43e9ca801ce38824ead814728a2807b1910117d","affectsGlobalScope":true,"impliedFormat":1},{"version":"3925a6c820dcb1a06506c90b1577db1fdbf7705d65b62b99dce4be75c637e26b","affectsGlobalScope":true,"impliedFormat":1},{"version":"0a3d63ef2b853447ec4f749d3f368ce642264246e02911fcb1590d8c161b8005","affectsGlobalScope":true,"impliedFormat":1},{"version":"8cdf8847677ac7d20486e54dd3fcf09eda95812ac8ace44b4418da1bbbab6eb8","affectsGlobalScope":true,"impliedFormat":1},{"version":"8444af78980e3b20b49324f4a16ba35024fef3ee069a0eb67616ea6ca821c47a","affectsGlobalScope":true,"impliedFormat":1},{"version":"3287d9d085fbd618c3971944b65b4be57859f5415f495b33a6adc994edd2f004","affectsGlobalScope":true,"impliedFormat":1},{"version":"b4b67b1a91182421f5df999988c690f14d813b9850b40acd06ed44691f6727ad","affectsGlobalScope":true,"impliedFormat":1},{"version":"df83c2a6c73228b625b0beb6669c7ee2a09c914637e2d35170723ad49c0f5cd4","affectsGlobalScope":true,"impliedFormat":1},{"version":"436aaf437562f276ec2ddbee2f2cdedac7664c1e4c1d2c36839ddd582eeb3d0a","affectsGlobalScope":true,"impliedFormat":1},{"version":"8e3c06ea092138bf9fa5e874a1fdbc9d54805d074bee1de31b99a11e2fec239d","affectsGlobalScope":true,"impliedFormat":1},{"version":"87dc0f382502f5bbce5129bdc0aea21e19a3abbc19259e0b43ae038a9fc4e326","affectsGlobalScope":true,"impliedFormat":1},{"version":"b1cb28af0c891c8c96b2d6b7be76bd394fddcfdb4709a20ba05a7c1605eea0f9","affectsGlobalScope":true,"impliedFormat":1},{"version":"2fef54945a13095fdb9b84f705f2b5994597640c46afeb2ce78352fab4cb3279","affectsGlobalScope":true,"impliedFormat":1},{"version":"ac77cb3e8c6d3565793eb90a8373ee8033146315a3dbead3bde8db5eaf5e5ec6","affectsGlobalScope":true,"impliedFormat":1},{"version":"56e4ed5aab5f5920980066a9409bfaf53e6d21d3f8d020c17e4de584d29600ad","affectsGlobalScope":true,"impliedFormat":1},{"version":"4ece9f17b3866cc077099c73f4983bddbcb1dc7ddb943227f1ec070f529dedd1","affectsGlobalScope":true,"impliedFormat":1},{"version":"0a6282c8827e4b9a95f4bf4f5c205673ada31b982f50572d27103df8ceb8013c","affectsGlobalScope":true,"impliedFormat":1},{"version":"1c9319a09485199c1f7b0498f2988d6d2249793ef67edda49d1e584746be9032","affectsGlobalScope":true,"impliedFormat":1},{"version":"e3a2a0cee0f03ffdde24d89660eba2685bfbdeae955a6c67e8c4c9fd28928eeb","affectsGlobalScope":true,"impliedFormat":1},{"version":"811c71eee4aa0ac5f7adf713323a5c41b0cf6c4e17367a34fbce379e12bbf0a4","affectsGlobalScope":true,"impliedFormat":1},{"version":"51ad4c928303041605b4d7ae32e0c1ee387d43a24cd6f1ebf4a2699e1076d4fa","affectsGlobalScope":true,"impliedFormat":1},{"version":"60037901da1a425516449b9a20073aa03386cce92f7a1fd902d7602be3a7c2e9","affectsGlobalScope":true,"impliedFormat":1},{"version":"d4b1d2c51d058fc21ec2629fff7a76249dec2e36e12960ea056e3ef89174080f","affectsGlobalScope":true,"impliedFormat":1},{"version":"22adec94ef7047a6c9d1af3cb96be87a335908bf9ef386ae9fd50eeb37f44c47","affectsGlobalScope":true,"impliedFormat":1},{"version":"196cb558a13d4533a5163286f30b0509ce0210e4b316c56c38d4c0fd2fb38405","affectsGlobalScope":true,"impliedFormat":1},{"version":"73f78680d4c08509933daf80947902f6ff41b6230f94dd002ae372620adb0f60","affectsGlobalScope":true,"impliedFormat":1},{"version":"c5239f5c01bcfa9cd32f37c496cf19c61d69d37e48be9de612b541aac915805b","affectsGlobalScope":true,"impliedFormat":1},{"version":"8e7f8264d0fb4c5339605a15daadb037bf238c10b654bb3eee14208f860a32ea","affectsGlobalScope":true,"impliedFormat":1},{"version":"782dec38049b92d4e85c1585fbea5474a219c6984a35b004963b00beb1aab538","affectsGlobalScope":true,"impliedFormat":1},{"version":"80094d1103a44c7905600ace42a1b90508d3df67e0c0c3d35fd65df689b4688d","affectsGlobalScope":true},{"version":"7e29f41b158de217f94cb9676bf9cbd0cd9b5a46e1985141ed36e075c52bf6ad","affectsGlobalScope":true,"impliedFormat":1},{"version":"ac51dd7d31333793807a6abaa5ae168512b6131bd41d9c5b98477fc3b7800f9f","impliedFormat":1},{"version":"dc0a7f107690ee5cd8afc8dbf05c4df78085471ce16bdd9881642ec738bc81fe","impliedFormat":1},{"version":"acd8fd5090ac73902278889c38336ff3f48af6ba03aa665eb34a75e7ba1dccc4","impliedFormat":1},{"version":"d6258883868fb2680d2ca96bc8b1352cab69874581493e6d52680c5ffecdb6cc","impliedFormat":1},{"version":"1b61d259de5350f8b1e5db06290d31eaebebc6baafd5f79d314b5af9256d7153","impliedFormat":1},{"version":"f258e3960f324a956fc76a3d3d9e964fff2244ff5859dcc6ce5951e5413ca826","impliedFormat":1},{"version":"643f7232d07bf75e15bd8f658f664d6183a0efaca5eb84b48201c7671a266979","impliedFormat":1},{"version":"0f6666b58e9276ac3a38fdc80993d19208442d6027ab885580d93aec76b4ef00","impliedFormat":1},{"version":"05fd364b8ef02fb1e174fbac8b825bdb1e5a36a016997c8e421f5fab0a6da0a0","impliedFormat":1},{"version":"631eff75b0e35d1b1b31081d55209abc43e16b49426546ab5a9b40bdd40b1f60","impliedFormat":1},{"version":"6c7176368037af28cb72f2392010fa1cef295d6d6744bca8cfb54985f3a18c3e","affectsGlobalScope":true,"impliedFormat":1},{"version":"ab41ef1f2cdafb8df48be20cd969d875602483859dc194e9c97c8a576892c052","affectsGlobalScope":true,"impliedFormat":1},{"version":"437e20f2ba32abaeb7985e0afe0002de1917bc74e949ba585e49feba65da6ca1","affectsGlobalScope":true,"impliedFormat":1},{"version":"21d819c173c0cf7cc3ce57c3276e77fd9a8a01d35a06ad87158781515c9a438a","impliedFormat":1},{"version":"98cffbf06d6bab333473c70a893770dbe990783904002c4f1a960447b4b53dca","affectsGlobalScope":true,"impliedFormat":1},{"version":"3af97acf03cc97de58a3a4bc91f8f616408099bc4233f6d0852e72a8ffb91ac9","affectsGlobalScope":true,"impliedFormat":1},{"version":"808069bba06b6768b62fd22429b53362e7af342da4a236ed2d2e1c89fcca3b4a","affectsGlobalScope":true,"impliedFormat":1},{"version":"1db0b7dca579049ca4193d034d835f6bfe73096c73663e5ef9a0b5779939f3d0","affectsGlobalScope":true,"impliedFormat":1},{"version":"9798340ffb0d067d69b1ae5b32faa17ab31b82466a3fc00d8f2f2df0c8554aaa","affectsGlobalScope":true,"impliedFormat":1},{"version":"f26b11d8d8e4b8028f1c7d618b22274c892e4b0ef5b3678a8ccbad85419aef43","affectsGlobalScope":true,"impliedFormat":1},{"version":"5929864ce17fba74232584d90cb721a89b7ad277220627cc97054ba15a98ea8f","impliedFormat":1},{"version":"763fe0f42b3d79b440a9b6e51e9ba3f3f91352469c1e4b3b67bfa4ff6352f3f4","impliedFormat":1},{"version":"25c8056edf4314820382a5fdb4bb7816999acdcb929c8f75e3f39473b87e85bc","impliedFormat":1},{"version":"c464d66b20788266e5353b48dc4aa6bc0dc4a707276df1e7152ab0c9ae21fad8","impliedFormat":1},{"version":"78d0d27c130d35c60b5e5566c9f1e5be77caf39804636bc1a40133919a949f21","impliedFormat":1},{"version":"c6fd2c5a395f2432786c9cb8deb870b9b0e8ff7e22c029954fabdd692bff6195","impliedFormat":1},{"version":"1d6e127068ea8e104a912e42fc0a110e2aa5a66a356a917a163e8cf9a65e4a75","impliedFormat":1},{"version":"5ded6427296cdf3b9542de4471d2aa8d3983671d4cac0f4bf9c637208d1ced43","impliedFormat":1},{"version":"7f182617db458e98fc18dfb272d40aa2fff3a353c44a89b2c0ccb3937709bfb5","impliedFormat":1},{"version":"cadc8aced301244057c4e7e73fbcae534b0f5b12a37b150d80e5a45aa4bebcbd","impliedFormat":1},{"version":"385aab901643aa54e1c36f5ef3107913b10d1b5bb8cbcd933d4263b80a0d7f20","impliedFormat":1},{"version":"9670d44354bab9d9982eca21945686b5c24a3f893db73c0dae0fd74217a4c219","impliedFormat":1},{"version":"0b8a9268adaf4da35e7fa830c8981cfa22adbbe5b3f6f5ab91f6658899e657a7","impliedFormat":1},{"version":"11396ed8a44c02ab9798b7dca436009f866e8dae3c9c25e8c1fbc396880bf1bb","impliedFormat":1},{"version":"ba7bc87d01492633cb5a0e5da8a4a42a1c86270e7b3d2dea5d156828a84e4882","impliedFormat":1},{"version":"4893a895ea92c85345017a04ed427cbd6a1710453338df26881a6019432febdd","impliedFormat":1},{"version":"c21dc52e277bcfc75fac0436ccb75c204f9e1b3fa5e12729670910639f27343e","impliedFormat":1},{"version":"13f6f39e12b1518c6650bbb220c8985999020fe0f21d818e28f512b7771d00f9","impliedFormat":1},{"version":"9b5369969f6e7175740bf51223112ff209f94ba43ecd3bb09eefff9fd675624a","impliedFormat":1},{"version":"4fe9e626e7164748e8769bbf74b538e09607f07ed17c2f20af8d680ee49fc1da","impliedFormat":1},{"version":"24515859bc0b836719105bb6cc3d68255042a9f02a6022b3187948b204946bd2","impliedFormat":1},{"version":"ea0148f897b45a76544ae179784c95af1bd6721b8610af9ffa467a518a086a43","impliedFormat":1},{"version":"24c6a117721e606c9984335f71711877293a9651e44f59f3d21c1ea0856f9cc9","impliedFormat":1},{"version":"dd3273ead9fbde62a72949c97dbec2247ea08e0c6952e701a483d74ef92d6a17","impliedFormat":1},{"version":"405822be75ad3e4d162e07439bac80c6bcc6dbae1929e179cf467ec0b9ee4e2e","impliedFormat":1},{"version":"0db18c6e78ea846316c012478888f33c11ffadab9efd1cc8bcc12daded7a60b6","impliedFormat":1},{"version":"e61be3f894b41b7baa1fbd6a66893f2579bfad01d208b4ff61daef21493ef0a8","impliedFormat":1},{"version":"bd0532fd6556073727d28da0edfd1736417a3f9f394877b6d5ef6ad88fba1d1a","impliedFormat":1},{"version":"89167d696a849fce5ca508032aabfe901c0868f833a8625d5a9c6e861ef935d2","impliedFormat":1},{"version":"615ba88d0128ed16bf83ef8ccbb6aff05c3ee2db1cc0f89ab50a4939bfc1943f","impliedFormat":1},{"version":"a4d551dbf8746780194d550c88f26cf937caf8d56f102969a110cfaed4b06656","impliedFormat":1},{"version":"8bd86b8e8f6a6aa6c49b71e14c4ffe1211a0e97c80f08d2c8cc98838006e4b88","impliedFormat":1},{"version":"317e63deeb21ac07f3992f5b50cdca8338f10acd4fbb7257ebf56735bf52ab00","impliedFormat":1},{"version":"4732aec92b20fb28c5fe9ad99521fb59974289ed1e45aecb282616202184064f","impliedFormat":1},{"version":"2e85db9e6fd73cfa3d7f28e0ab6b55417ea18931423bd47b409a96e4a169e8e6","impliedFormat":1},{"version":"c46e079fe54c76f95c67fb89081b3e399da2c7d109e7dca8e4b58d83e332e605","impliedFormat":1},{"version":"bf67d53d168abc1298888693338cb82854bdb2e69ef83f8a0092093c2d562107","impliedFormat":1},{"version":"b52476feb4a0cbcb25e5931b930fc73cb6643fb1a5060bf8a3dda0eeae5b4b68","affectsGlobalScope":true,"impliedFormat":1},{"version":"f9501cc13ce624c72b61f12b3963e84fad210fbdf0ffbc4590e08460a3f04eba","affectsGlobalScope":true,"impliedFormat":1},{"version":"e7721c4f69f93c91360c26a0a84ee885997d748237ef78ef665b153e622b36c1","affectsGlobalScope":true,"impliedFormat":1},{"version":"0fa06ada475b910e2106c98c68b10483dc8811d0c14a8a8dd36efb2672485b29","impliedFormat":1},{"version":"33e5e9aba62c3193d10d1d33ae1fa75c46a1171cf76fef750777377d53b0303f","impliedFormat":1},{"version":"2b06b93fd01bcd49d1a6bd1f9b65ddcae6480b9a86e9061634d6f8e354c1468f","impliedFormat":1},{"version":"6a0cd27e5dc2cfbe039e731cf879d12b0e2dded06d1b1dedad07f7712de0d7f4","affectsGlobalScope":true,"impliedFormat":1},{"version":"13f5c844119c43e51ce777c509267f14d6aaf31eafb2c2b002ca35584cd13b29","impliedFormat":1},{"version":"e60477649d6ad21542bd2dc7e3d9ff6853d0797ba9f689ba2f6653818999c264","impliedFormat":1},{"version":"c2510f124c0293ab80b1777c44d80f812b75612f297b9857406468c0f4dafe29","affectsGlobalScope":true,"impliedFormat":1},{"version":"5524481e56c48ff486f42926778c0a3cce1cc85dc46683b92b1271865bcf015a","impliedFormat":1},{"version":"4c829ab315f57c5442c6667b53769975acbf92003a66aef19bce151987675bd1","affectsGlobalScope":true,"impliedFormat":1},{"version":"b2ade7657e2db96d18315694789eff2ddd3d8aea7215b181f8a0b303277cc579","impliedFormat":1},{"version":"9855e02d837744303391e5623a531734443a5f8e6e8755e018c41d63ad797db2","impliedFormat":1},{"version":"4d631b81fa2f07a0e63a9a143d6a82c25c5f051298651a9b69176ba28930756d","impliedFormat":1},{"version":"836a356aae992ff3c28a0212e3eabcb76dd4b0cc06bcb9607aeef560661b860d","impliedFormat":1},{"version":"1e0d1f8b0adfa0b0330e028c7941b5a98c08b600efe7f14d2d2a00854fb2f393","impliedFormat":1},{"version":"41670ee38943d9cbb4924e436f56fc19ee94232bc96108562de1a734af20dc2c","affectsGlobalScope":true,"impliedFormat":1},{"version":"c906fb15bd2aabc9ed1e3f44eb6a8661199d6c320b3aa196b826121552cb3695","impliedFormat":1},{"version":"22295e8103f1d6d8ea4b5d6211e43421fe4564e34d0dd8e09e520e452d89e659","impliedFormat":1},{"version":"58647d85d0f722a1ce9de50955df60a7489f0593bf1a7015521efe901c06d770","impliedFormat":1},{"version":"6b4e081d55ac24fc8a4631d5dd77fe249fa25900abd7d046abb87d90e3b45645","impliedFormat":1},{"version":"a10f0e1854f3316d7ee437b79649e5a6ae3ae14ffe6322b02d4987071a95362e","impliedFormat":1},{"version":"e208f73ef6a980104304b0d2ca5f6bf1b85de6009d2c7e404028b875020fa8f2","impliedFormat":1},{"version":"d163b6bc2372b4f07260747cbc6c0a6405ab3fbcea3852305e98ac43ca59f5bc","impliedFormat":1},{"version":"e6fa9ad47c5f71ff733744a029d1dc472c618de53804eae08ffc243b936f87ff","affectsGlobalScope":true,"impliedFormat":1},{"version":"83e63d6ccf8ec004a3bb6d58b9bb0104f60e002754b1e968024b320730cc5311","impliedFormat":1},{"version":"24826ed94a78d5c64bd857570fdbd96229ad41b5cb654c08d75a9845e3ab7dde","impliedFormat":1},{"version":"8b479a130ccb62e98f11f136d3ac80f2984fdc07616516d29881f3061f2dd472","impliedFormat":1},{"version":"928af3d90454bf656a52a48679f199f64c1435247d6189d1caf4c68f2eaf921f","affectsGlobalScope":true,"impliedFormat":1},{"version":"bceb58df66ab8fb00170df20cd813978c5ab84be1d285710c4eb005d8e9d8efb","affectsGlobalScope":true,"impliedFormat":1},{"version":"3f16a7e4deafa527ed9995a772bb380eb7d3c2c0fd4ae178c5263ed18394db2c","impliedFormat":1},{"version":"933921f0bb0ec12ef45d1062a1fc0f27635318f4d294e4d99de9a5493e618ca2","impliedFormat":1},{"version":"71a0f3ad612c123b57239a7749770017ecfe6b66411488000aba83e4546fde25","impliedFormat":1},{"version":"77fbe5eecb6fac4b6242bbf6eebfc43e98ce5ccba8fa44e0ef6a95c945ff4d98","impliedFormat":1},{"version":"4f9d8ca0c417b67b69eeb54c7ca1bedd7b56034bb9bfd27c5d4f3bc4692daca7","impliedFormat":1},{"version":"814118df420c4e38fe5ae1b9a3bafb6e9c2aa40838e528cde908381867be6466","impliedFormat":1},{"version":"a3fc63c0d7b031693f665f5494412ba4b551fe644ededccc0ab5922401079c95","impliedFormat":1},{"version":"f27524f4bef4b6519c604bdb23bf4465bddcccbf3f003abb901acbd0d7404d99","impliedFormat":1},{"version":"37ba7b45141a45ce6e80e66f2a96c8a5ab1bcef0fc2d0f56bb58df96ec67e972","impliedFormat":1},{"version":"45650f47bfb376c8a8ed39d4bcda5902ab899a3150029684ee4c10676d9fbaee","impliedFormat":1},{"version":"6b039f55681caaf111d5eb84d292b9bee9e0131d0db1ad0871eef0964f533c73","affectsGlobalScope":true,"impliedFormat":1},{"version":"18fd40412d102c5564136f29735e5d1c3b455b8a37f920da79561f1fde068208","impliedFormat":1},{"version":"c8d3e5a18ba35629954e48c4cc8f11dc88224650067a172685c736b27a34a4dc","impliedFormat":1},{"version":"f0be1b8078cd549d91f37c30c222c2a187ac1cf981d994fb476a1adc61387b14","affectsGlobalScope":true,"impliedFormat":1},{"version":"0aaed1d72199b01234152f7a60046bc947f1f37d78d182e9ae09c4289e06a592","impliedFormat":1},{"version":"2b55d426ff2b9087485e52ac4bc7cfafe1dc420fc76dad926cd46526567c501a","impliedFormat":1},{"version":"66ba1b2c3e3a3644a1011cd530fb444a96b1b2dfe2f5e837a002d41a1a799e60","impliedFormat":1},{"version":"7e514f5b852fdbc166b539fdd1f4e9114f29911592a5eb10a94bb3a13ccac3c4","impliedFormat":1},{"version":"5b7aa3c4c1a5d81b411e8cb302b45507fea9358d3569196b27eb1a27ae3a90ef","affectsGlobalScope":true,"impliedFormat":1},{"version":"5987a903da92c7462e0b35704ce7da94d7fdc4b89a984871c0e2b87a8aae9e69","affectsGlobalScope":true,"impliedFormat":1},{"version":"ea08a0345023ade2b47fbff5a76d0d0ed8bff10bc9d22b83f40858a8e941501c","impliedFormat":1},{"version":"47613031a5a31510831304405af561b0ffaedb734437c595256bb61a90f9311b","impliedFormat":1},{"version":"ae062ce7d9510060c5d7e7952ae379224fb3f8f2dd74e88959878af2057c143b","impliedFormat":1},{"version":"8a1a0d0a4a06a8d278947fcb66bf684f117bf147f89b06e50662d79a53be3e9f","affectsGlobalScope":true,"impliedFormat":1},{"version":"358765d5ea8afd285d4fd1532e78b88273f18cb3f87403a9b16fef61ac9fdcfe","impliedFormat":1},{"version":"9f55299850d4f0921e79b6bf344b47c420ce0f507b9dcf593e532b09ea7eeea1","impliedFormat":1},{"version":"2beff543f6e9a9701df88daeee3cdd70a34b4a1c11cb4c734472195a5cb2af54","impliedFormat":1},{"version":"2e07abf27aa06353d46f4448c0bbac73431f6065eef7113128a5cd804d0c384d","impliedFormat":1},{"version":"be1cc4d94ea60cbe567bc29ed479d42587bf1e6cba490f123d329976b0fe4ee5","impliedFormat":1},{"version":"42bc0e1a903408137c3df2b06dfd7e402cdab5bbfa5fcfb871b22ebfdb30bd0b","impliedFormat":1},{"version":"9894dafe342b976d251aac58e616ac6df8db91fb9d98934ff9dd103e9e82578f","impliedFormat":1},{"version":"413df52d4ea14472c2fa5bee62f7a40abd1eb49be0b9722ee01ee4e52e63beb2","impliedFormat":1},{"version":"db6d2d9daad8a6d83f281af12ce4355a20b9a3e71b82b9f57cddcca0a8964a96","impliedFormat":1},{"version":"829b9e6028b29e6a8b1c01ddb713efe59da04d857089298fa79acbdb3cfcfdef","impliedFormat":1},{"version":"24f8562308dd8ba6013120557fa7b44950b619610b2c6cb8784c79f11e3c4f90","impliedFormat":1},{"version":"5f90b8c733a1bda63e42160b15a2301051e83a6f9d5332a59d16eb12f463270d","impliedFormat":1},{"version":"a86f82d646a739041d6702101afa82dcb935c416dd93cbca7fd754fd0282ce1f","impliedFormat":1},{"version":"ad0d1d75d129b1c80f911be438d6b61bfa8703930a8ff2be2f0e1f8a91841c64","impliedFormat":1},{"version":"ce75b1aebb33d510ff28af960a9221410a3eaf7f18fc5f21f9404075fba77256","impliedFormat":1},{"version":"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855","impliedFormat":1},{"version":"496bbf339f3838c41f164238543e9fe5f1f10659cb30b68903851618464b98ba","impliedFormat":1},{"version":"5178eb4415a172c287c711dc60a619e110c3fd0b7de01ed0627e51a5336aa09c","impliedFormat":1},{"version":"ca6e5264278b53345bc1ce95f42fb0a8b733a09e3d6479c6ccfca55cdc45038c","impliedFormat":1},{"version":"9e2739b32f741859263fdba0244c194ca8e96da49b430377930b8f721d77c000","impliedFormat":1},{"version":"fb1d8e814a3eeb5101ca13515e0548e112bd1ff3fb358ece535b93e94adf5a3a","impliedFormat":1},{"version":"ffa495b17a5ef1d0399586b590bd281056cee6ce3583e34f39926f8dcc6ecdb5","impliedFormat":1},{"version":"98b18458acb46072947aabeeeab1e410f047e0cacc972943059ca5500b0a5e95","impliedFormat":1},{"version":"361e2b13c6765d7f85bb7600b48fde782b90c7c41105b7dab1f6e7871071ba20","impliedFormat":1},{"version":"c86fe861cf1b4c46a0fb7d74dffe596cf679a2e5e8b1456881313170f092e3fa","impliedFormat":1},{"version":"b6db56e4903e9c32e533b78ac85522de734b3d3a8541bf24d256058d464bf04b","impliedFormat":1},{"version":"24daa0366f837d22c94a5c0bad5bf1fd0f6b29e1fae92dc47c3072c3fdb2fbd5","impliedFormat":1},{"version":"570bb5a00836ffad3e4127f6adf581bfc4535737d8ff763a4d6f4cc877e60d98","impliedFormat":1},{"version":"889c00f3d32091841268f0b994beba4dceaa5df7573be12c2c829d7c5fbc232c","impliedFormat":1},{"version":"65f43099ded6073336e697512d9b80f2d4fec3182b7b2316abf712e84104db00","impliedFormat":1},{"version":"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855","impliedFormat":1},{"version":"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855","impliedFormat":1},{"version":"8e609bb71c20b858c77f0e9f90bb1319db8477b13f9f965f1a1e18524bf50881","impliedFormat":1},{"version":"acf5a2ac47b59ca07afa9abbd2b31d001bf7448b041927befae2ea5b1951d9f9","impliedFormat":1},{"version":"8e609bb71c20b858c77f0e9f90bb1319db8477b13f9f965f1a1e18524bf50881","impliedFormat":1},{"version":"d71291eff1e19d8762a908ba947e891af44749f3a2cbc5bd2ec4b72f72ea795f","impliedFormat":1},{"version":"c0480e03db4b816dff2682b347c95f2177699525c54e7e6f6aa8ded890b76be7","impliedFormat":1},{"version":"27ab780875bcbb65e09da7496f2ca36288b0c541abaa75c311450a077d54ec15","impliedFormat":1},{"version":"b620391fe8060cf9bedc176a4d01366e6574d7a71e0ac0ab344a4e76576fcbb8","impliedFormat":1},{"version":"380647d8f3b7f852cca6d154a376dbf8ac620a2f12b936594504a8a852e71d2f","impliedFormat":1},{"version":"208c9af9429dd3c76f5927b971263174aaa4bc7621ddec63f163640cbd3c473c","impliedFormat":1},{"version":"6459054aabb306821a043e02b89d54da508e3a6966601a41e71c166e4ea1474f","impliedFormat":1},{"version":"a23185bc5ef590c287c28a91baf280367b50ae4ea40327366ad01f6f4a8edbc5","impliedFormat":1},{"version":"bb37588926aba35c9283fe8d46ebf4e79ffe976343105f5c6d45f282793352b2","impliedFormat":1},{"version":"002eae065e6960458bda3cf695e578b0d1e2785523476f8a9170b103c709cd4f","impliedFormat":1},{"version":"c83bb0c9c5645a46c68356c2f73fdc9de339ce77f7f45a954f560c7e0b8d5ebb","impliedFormat":1},{"version":"05c97cddbaf99978f83d96de2d8af86aded9332592f08ce4a284d72d0952c391","impliedFormat":1},{"version":"72179f9dd22a86deaad4cc3490eb0fe69ee084d503b686985965654013f1391b","impliedFormat":1},{"version":"2e6114a7dd6feeef85b2c80120fdbfb59a5529c0dcc5bfa8447b6996c97a69f5","impliedFormat":1},{"version":"7b6ff760c8a240b40dab6e4419b989f06a5b782f4710d2967e67c695ef3e93c4","impliedFormat":1},{"version":"c8f004e6036aa1c764ad4ec543cf89a5c1893a9535c80ef3f2b653e370de45e6","impliedFormat":1},{"version":"dd80b1e600d00f5c6a6ba23f455b84a7db121219e68f89f10552c54ba46e4dc9","impliedFormat":1},{"version":"b064c36f35de7387d71c599bfcf28875849a1dbc733e82bd26cae3d1cd060521","impliedFormat":1},{"version":"6a148329edecbda07c21098639ef4254ef7869fb25a69f58e5d6a8b7b69d4236","impliedFormat":1},{"version":"8de9fe97fa9e00ec00666fa77ab6e91b35d25af8ca75dabcb01e14ad3299b150","impliedFormat":1},{"version":"f63ab283a1c8f5c79fabe7ca4ef85f9633339c4f0e822fce6a767f9d59282af2","impliedFormat":1},{"version":"dba114fb6a32b355a9cfc26ca2276834d72fe0e94cd2c3494005547025015369","impliedFormat":1},{"version":"a54c996c8870ef1728a2c1fa9b8eaec0bf4a8001cd2583c02dd5869289465b10","impliedFormat":1},{"version":"3e7efde639c6a6c3edb9847b3f61e308bf7a69685b92f665048c45132f51c218","impliedFormat":1},{"version":"df45ca1176e6ac211eae7ddf51336dc075c5314bc5c253651bae639defd5eec5","impliedFormat":1},{"version":"3754982006a3b32c502cff0867ca83584f7a43b1035989ca73603f400de13c96","impliedFormat":1},{"version":"a30ae9bb8a8fa7b90f24b8a0496702063ae4fe75deb27da731ed4a03b2eb6631","impliedFormat":1},{"version":"f974e4a06953682a2c15d5bd5114c0284d5abf8bc0fe4da25cb9159427b70072","impliedFormat":1},{"version":"50256e9c31318487f3752b7ac12ff365c8949953e04568009c8705db802776fb","impliedFormat":1},{"version":"7d73b24e7bf31dfb8a931ca6c4245f6bb0814dfae17e4b60c9e194a631fe5f7b","impliedFormat":1},{"version":"413586add0cfe7369b64979d4ec2ed56c3f771c0667fbde1bf1f10063ede0b08","impliedFormat":1},{"version":"06472528e998d152375ad3bd8ebcb69ff4694fd8d2effaf60a9d9f25a37a097a","impliedFormat":1},{"version":"50b5bc34ce6b12eccb76214b51aadfa56572aa6cc79c2b9455cdbb3d6c76af1d","impliedFormat":1},{"version":"b7e16ef7f646a50991119b205794ebfd3a4d8f8e0f314981ebbe991639023d0e","impliedFormat":1},{"version":"42c169fb8c2d42f4f668c624a9a11e719d5d07dacbebb63cbcf7ef365b0a75b3","impliedFormat":1},{"version":"a401617604fa1f6ce437b81689563dfdc377069e4c58465dbd8d16069aede0a5","impliedFormat":1},{"version":"e9dd71cf12123419c60dab867d44fbee5c358169f99529121eaef277f5c83531","impliedFormat":1},{"version":"5b6a189ba3a0befa1f5d9cb028eb9eec2af2089c32f04ff50e2411f63d70f25d","impliedFormat":1},{"version":"d6e73f8010935b7b4c7487b6fb13ea197cc610f0965b759bec03a561ccf8423a","impliedFormat":1},{"version":"174f3864e398f3f33f9a446a4f403d55a892aa55328cf6686135dfaf9e171657","impliedFormat":1},{"version":"824c76aec8d8c7e65769688cbee102238c0ef421ed6686f41b2a7d8e7e78a931","impliedFormat":1},{"version":"75b868be3463d5a8cfc0d9396f0a3d973b8c297401d00bfb008a42ab16643f13","impliedFormat":1},{"version":"15a234e5031b19c48a69ccc1607522d6e4b50f57d308ecb7fe863d44cd9f9eb3","impliedFormat":1},{"version":"d682336018141807fb602709e2d95a192828fcb8d5ba06dda3833a8ea98f69e3","impliedFormat":1},{"version":"6124e973eab8c52cabf3c07575204efc1784aca6b0a30c79eb85fe240a857efa","impliedFormat":1},{"version":"0d891735a21edc75df51f3eb995e18149e119d1ce22fd40db2b260c5960b914e","impliedFormat":1},{"version":"3b414b99a73171e1c4b7b7714e26b87d6c5cb03d200352da5342ab4088a54c85","impliedFormat":1},{"version":"4fbd3116e00ed3a6410499924b6403cc9367fdca303e34838129b328058ede40","impliedFormat":1},{"version":"b01bd582a6e41457bc56e6f0f9de4cb17f33f5f3843a7cf8210ac9c18472fb0f","impliedFormat":1},{"version":"0a437ae178f999b46b6153d79095b60c42c996bc0458c04955f1c996dc68b971","impliedFormat":1},{"version":"74b2a5e5197bd0f2e0077a1ea7c07455bbea67b87b0869d9786d55104006784f","impliedFormat":1},{"version":"4a7baeb6325920044f66c0f8e5e6f1f52e06e6d87588d837bdf44feb6f35c664","impliedFormat":1},{"version":"6dcf60530c25194a9ee0962230e874ff29d34c59605d8e069a49928759a17e0a","impliedFormat":1},{"version":"7274fbffbd7c9589d8d0ffba68157237afd5cecff1e99881ea3399127e60572f","impliedFormat":1},{"version":"1a42d2ec31a1fe62fdc51591768695ed4a2dc64c01be113e7ff22890bebb5e3f","impliedFormat":1},{"version":"1a82deef4c1d39f6882f28d275cad4c01f907b9b39be9cbc472fcf2cf051e05b","impliedFormat":1},{"version":"c5426dbfc1cf90532f66965a7aa8c1136a78d4d0f96d8180ecbfc11d7722f1a5","impliedFormat":1},{"version":"65a15fc47900787c0bd18b603afb98d33ede930bed1798fc984d5ebb78b26cf9","impliedFormat":1},{"version":"9d202701f6e0744adb6314d03d2eb8fc994798fc83d91b691b75b07626a69801","impliedFormat":1},{"version":"de9d2df7663e64e3a91bf495f315a7577e23ba088f2949d5ce9ec96f44fba37d","impliedFormat":1},{"version":"c7af78a2ea7cb1cd009cfb5bdb48cd0b03dad3b54f6da7aab615c2e9e9d570c5","impliedFormat":1},{"version":"1ee45496b5f8bdee6f7abc233355898e5bf9bd51255db65f5ff7ede617ca0027","impliedFormat":1},{"version":"0c7c947ff881c4274c0800deaa0086971e0bfe51f89a33bd3048eaa3792d4876","affectsGlobalScope":true,"impliedFormat":1},{"version":"db01d18853469bcb5601b9fc9826931cc84cc1a1944b33cad76fd6f1e3d8c544","affectsGlobalScope":true,"impliedFormat":1},{"version":"a8f8e6ab2fa07b45251f403548b78eaf2022f3c2254df3dc186cb2671fe4996d","affectsGlobalScope":true,"impliedFormat":1},{"version":"fa6c12a7c0f6b84d512f200690bfc74819e99efae69e4c95c4cd30f6884c526e","impliedFormat":1},{"version":"f1c32f9ce9c497da4dc215c3bc84b722ea02497d35f9134db3bb40a8d918b92b","impliedFormat":1},{"version":"b73c319af2cc3ef8f6421308a250f328836531ea3761823b4cabbd133047aefa","affectsGlobalScope":true,"impliedFormat":1},{"version":"e433b0337b8106909e7953015e8fa3f2d30797cea27141d1c5b135365bb975a6","impliedFormat":1},{"version":"15b36126e0089bfef173ab61329e8286ce74af5e809d8a72edcafd0cc049057f","impliedFormat":1},{"version":"ddff7fc6edbdc5163a09e22bf8df7bef75f75369ebd7ecea95ba55c4386e2441","impliedFormat":1},{"version":"106c6025f1d99fd468fd8bf6e5bda724e11e5905a4076c5d29790b6c3745e50c","impliedFormat":1},{"version":"a57b1802794433adec9ff3fed12aa79d671faed86c49b09e02e1ac41b4f1d33a","impliedFormat":1},{"version":"ad10d4f0517599cdeca7755b930f148804e3e0e5b5a3847adce0f1f71bbccd74","impliedFormat":1},{"version":"1042064ece5bb47d6aba91648fbe0635c17c600ebdf567588b4ca715602f0a9d","impliedFormat":1},{"version":"c49469a5349b3cc1965710b5b0f98ed6c028686aa8450bcb3796728873eb923e","impliedFormat":1},{"version":"4a889f2c763edb4d55cb624257272ac10d04a1cad2ed2948b10ed4a7fda2a428","impliedFormat":1},{"version":"7bb79aa2fead87d9d56294ef71e056487e848d7b550c9a367523ee5416c44cfa","impliedFormat":1},{"version":"72d63643a657c02d3e51cd99a08b47c9b020a565c55f246907050d3c8a5e77fb","impliedFormat":1},{"version":"1d415445ea58f8033ba199703e55ff7483c52ac6742075b803bd3e7bbe9f5d61","impliedFormat":1},{"version":"d6406c629bb3efc31aedb2de809bef471e475c86c7e67f3ef9b676b5d7e0d6b2","impliedFormat":1},{"version":"27ff4196654e6373c9af16b6165120e2dd2169f9ad6abb5c935af5abd8c7938c","impliedFormat":1},{"version":"71d8ba39a9e024d9e4bb922464d18542ed8d2c25ee78efa7890c27213cc6e5d3","impliedFormat":1},{"version":"8c030e515014c10a2b98f9f48408e3ba18023dfd3f56e3312c6c2f3ae1f55a16","impliedFormat":1},{"version":"dafc31e9e8751f437122eb8582b93d477e002839864410ff782504a12f2a550c","impliedFormat":1},{"version":"754498c5208ce3c5134f6eabd49b25cf5e1a042373515718953581636491f3c3","impliedFormat":1},{"version":"9c82171d836c47486074e4ca8e059735bf97b205e70b196535b5efd40cbe1bc5","impliedFormat":1},{"version":"f56bdc6884648806d34bc66d31cdb787c4718d04105ce2cd88535db214631f82","impliedFormat":1},{"version":"633d58a237f4bb25ec7d565e4ffa32cecdcee8660ac12189c4351c52557cee9e","impliedFormat":1},{"version":"2e4f37ffe8862b14d8e24ae8763daaa8340c0df0b859d9a9733def0eee7562d9","impliedFormat":1},{"version":"13283350547389802aa35d9f2188effaeac805499169a06ef5cd77ce2a0bd63f","impliedFormat":1},{"version":"ce791f6ea807560f08065d1af6014581eeb54a05abd73294777a281b6dfd73c2","impliedFormat":1},{"version":"6ac6715916fa75a1f7ebdfeacac09513b4d904b667d827b7535e84ff59679aff","impliedFormat":1},{"version":"49f95e989b4632c6c2a578cc0078ee19a5831832d79cc59abecf5160ea71abad","impliedFormat":1},{"version":"9666533332f26e8995e4d6fe472bdeec9f15d405693723e6497bf94120c566c8","impliedFormat":1},{"version":"ce0df82a9ae6f914ba08409d4d883983cc08e6d59eb2df02d8e4d68309e7848b","impliedFormat":1},{"version":"796273b2edc72e78a04e86d7c58ae94d370ab93a0ddf40b1aa85a37a1c29ecd7","impliedFormat":1},{"version":"5df15a69187d737d6d8d066e189ae4f97e41f4d53712a46b2710ff9f8563ec9f","impliedFormat":1},{"version":"e17cd049a1448de4944800399daa4a64c5db8657cc9be7ef46be66e2a2cd0e7c","impliedFormat":1},{"version":"43fa6ea8714e18adc312b30450b13562949ba2f205a1972a459180fa54471018","impliedFormat":1},{"version":"6e89c2c177347d90916bad67714d0fb473f7e37fb3ce912f4ed521fe2892cd0d","impliedFormat":1},{"version":"43ba4f2fa8c698f5c304d21a3ef596741e8e85a810b7c1f9b692653791d8d97a","impliedFormat":1},{"version":"4d4927cbee21750904af7acf940c5e3c491b4d5ebc676530211e389dd375607a","impliedFormat":1},{"version":"72105519d0390262cf0abe84cf41c926ade0ff475d35eb21307b2f94de985778","impliedFormat":1},{"version":"8a97e578a9bc40eb4f1b0ca78f476f2e9154ecbbfd5567ee72943bab37fc156a","impliedFormat":1},{"version":"c857e0aae3f5f444abd791ec81206020fbcc1223e187316677e026d1c1d6fe08","impliedFormat":1},{"version":"ccf6dd45b708fb74ba9ed0f2478d4eb9195c9dfef0ff83a6092fa3cf2ff53b4f","impliedFormat":1},{"version":"2d7db1d73456e8c5075387d4240c29a2a900847f9c1bff106a2e490da8fbd457","impliedFormat":1},{"version":"2b15c805f48e4e970f8ec0b1915f22d13ca6212375e8987663e2ef5f0205e832","impliedFormat":1},{"version":"f22d05663d873ee7a600faf78abb67f3f719d32266803440cf11d5db7ac0cab2","impliedFormat":1},{"version":"d93c544ad20197b3976b0716c6d5cd5994e71165985d31dcab6e1f77feb4b8f2","impliedFormat":1},{"version":"35069c2c417bd7443ae7c7cafd1de02f665bf015479fec998985ffbbf500628c","impliedFormat":1},{"version":"a8b1c79a833ee148251e88a2553d02ce1641d71d2921cce28e79678f3d8b96aa","impliedFormat":1},{"version":"126d4f950d2bba0bd45b3a86c76554d4126c16339e257e6d2fabf8b6bf1ce00c","impliedFormat":1},{"version":"7e0b7f91c5ab6e33f511efc640d36e6f933510b11be24f98836a20a2dc914c2d","impliedFormat":1},{"version":"045b752f44bf9bbdcaffd882424ab0e15cb8d11fa94e1448942e338c8ef19fba","impliedFormat":1},{"version":"2894c56cad581928bb37607810af011764a2f511f575d28c9f4af0f2ef02d1ab","impliedFormat":1},{"version":"0a72186f94215d020cb386f7dca81d7495ab6c17066eb07d0f44a5bf33c1b21a","impliedFormat":1},{"version":"2d3cc2211f352f46ea6b7cf2c751c141ffcdf514d6e7ae7ee20b7b6742da313f","impliedFormat":1},{"version":"c75445151ff8b77d9923191efed7203985b1a9e09eccf4b054e7be864e27923d","impliedFormat":1},{"version":"0aedb02516baf3e66b2c1db9fef50666d6ed257edac0f866ea32f1aa05aa474f","impliedFormat":1},{"version":"fa8a8fbf91ee2a4779496225f0312aac6635b0f21aa09cdafa4283fe32d519c5","affectsGlobalScope":true,"impliedFormat":1},{"version":"0e8aef93d79b000deb6ec336b5645c87de167168e184e84521886f9ecc69a4b5","impliedFormat":1},{"version":"56ccb49443bfb72e5952f7012f0de1a8679f9f75fc93a5c1ac0bafb28725fc5f","impliedFormat":1},{"version":"20fa37b636fdcc1746ea0738f733d0aed17890d1cd7cb1b2f37010222c23f13e","impliedFormat":1},{"version":"d90b9f1520366d713a73bd30c5a9eb0040d0fb6076aff370796bc776fd705943","impliedFormat":1},{"version":"bc03c3c352f689e38c0ddd50c39b1e65d59273991bfc8858a9e3c0ebb79c023b","impliedFormat":1},{"version":"19df3488557c2fc9b4d8f0bac0fd20fb59aa19dec67c81f93813951a81a867f8","affectsGlobalScope":true,"impliedFormat":1},{"version":"b25350193e103ae90423c5418ddb0ad1168dc9c393c9295ef34980b990030617","affectsGlobalScope":true,"impliedFormat":1},{"version":"bef86adb77316505c6b471da1d9b8c9e428867c2566270e8894d4d773a1c4dc2","impliedFormat":1},{"version":"de7052bfee2981443498239a90c04ea5cc07065d5b9bb61b12cb6c84313ad4ef","impliedFormat":1},{"version":"a3e7d932dc9c09daa99141a8e4800fc6c58c625af0d4bbb017773dc36da75426","impliedFormat":1},{"version":"43e96a3d5d1411ab40ba2f61d6a3192e58177bcf3b133a80ad2a16591611726d","impliedFormat":1},{"version":"4a2edd238d9104eac35b60d727f1123de5062f452b70ed8e0366cb36387dfdfd","impliedFormat":1},{"version":"ca921bf56756cb6fe957f6af693a35251b134fb932dc13f3dfff0bb7106f80b4","impliedFormat":1},{"version":"fee92c97f1aa59eb7098a0cc34ff4df7e6b11bae71526aca84359a2575f313d8","impliedFormat":1},{"version":"0bd0297484aacea217d0b76e55452862da3c5d9e33b24430e0719d1161657225","impliedFormat":1},{"version":"2ab6d334bcbf2aff3acfc4fd8c73ecd82b981d3c3aa47b3f3b89281772286904","impliedFormat":1},{"version":"d07cbc787a997d83f7bde3877fec5fb5b12ce8c1b7047eb792996ed9726b4dde","impliedFormat":1},{"version":"6ac6715916fa75a1f7ebdfeacac09513b4d904b667d827b7535e84ff59679aff","impliedFormat":1},{"version":"4805f6161c2c8cefb8d3b8bd96a080c0fe8dbc9315f6ad2e53238f9a79e528a6","impliedFormat":1},{"version":"b83cb14474fa60c5f3ec660146b97d122f0735627f80d82dd03e8caa39b4388c","impliedFormat":1},{"version":"f374cb24e93e7798c4d9e83ff872fa52d2cdb36306392b840a6ddf46cb925cb6","impliedFormat":1},{"version":"49179c6a23701c642bd99abe30d996919748014848b738d8e85181fc159685ff","impliedFormat":1},{"version":"b73cbf0a72c8800cf8f96a9acfe94f3ad32ca71342a8908b8ae484d61113f647","impliedFormat":1},{"version":"bae6dd176832f6423966647382c0d7ba9e63f8c167522f09a982f086cd4e8b23","impliedFormat":1},{"version":"20865ac316b8893c1a0cc383ccfc1801443fbcc2a7255be166cf90d03fac88c9","impliedFormat":1},{"version":"c9958eb32126a3843deedda8c22fb97024aa5d6dd588b90af2d7f2bfac540f23","impliedFormat":1},{"version":"461d0ad8ae5f2ff981778af912ba71b37a8426a33301daa00f21c6ccb27f8156","impliedFormat":1},{"version":"e927c2c13c4eaf0a7f17e6022eee8519eb29ef42c4c13a31e81a611ab8c95577","impliedFormat":1},{"version":"fcafff163ca5e66d3b87126e756e1b6dfa8c526aa9cd2a2b0a9da837d81bbd72","impliedFormat":1},{"version":"70246ad95ad8a22bdfe806cb5d383a26c0c6e58e7207ab9c431f1cb175aca657","impliedFormat":1},{"version":"f00f3aa5d64ff46e600648b55a79dcd1333458f7a10da2ed594d9f0a44b76d0b","impliedFormat":1},{"version":"772d8d5eb158b6c92412c03228bd9902ccb1457d7a705b8129814a5d1a6308fc","impliedFormat":1},{"version":"45490817629431853543adcb91c0673c25af52a456479588b6486daba34f68bb","impliedFormat":1},{"version":"802e797bcab5663b2c9f63f51bdf67eff7c41bc64c0fd65e6da3e7941359e2f7","impliedFormat":1},{"version":"8b4327413e5af38cd8cb97c59f48c3c866015d5d642f28518e3a891c469f240e","impliedFormat":1},{"version":"8514c62ce38e58457d967e9e73f128eedc1378115f712b9eef7127f7c88f82ae","impliedFormat":1},{"version":"f1289e05358c546a5b664fbb35a27738954ec2cc6eb4137350353099d154fc62","impliedFormat":1},{"version":"4b20fcf10a5413680e39f5666464859fc56b1003e7dfe2405ced82371ebd49b6","impliedFormat":1},{"version":"1d17ba45cfbe77a9c7e0df92f7d95f3eefd49ee23d1104d0548b215be56945ad","impliedFormat":1},{"version":"f7d628893c9fa52ba3ab01bcb5e79191636c4331ee5667ecc6373cbccff8ae12","impliedFormat":1},{"version":"1d879125d1ec570bf04bc1f362fdbe0cb538315c7ac4bcfcdf0c1e9670846aa6","impliedFormat":1},{"version":"a1ee88010a64e8647d07dba58ec43e6e05851b9ec7a62e4ca2b9c33be5abb2c8","impliedFormat":1},{"version":"46273e8c29816125d0d0b56ce9a849cc77f60f9a5ba627447501d214466f0ff3","impliedFormat":1},{"version":"d663134457d8d669ae0df34eabd57028bddc04fc444c4bc04bc5215afc91e1f4","impliedFormat":1},{"version":"e91f7b1344577a02f051b9b471f33044fef8334a76dc9e1de003d17595a5219b","impliedFormat":1},{"version":"3af3584f79c57853028ef9421ec172539e1fe01853296dc05a9d615ade4ffaf6","impliedFormat":1},{"version":"f82579d87701d639ff4e3930a9b24f4ee13ca74221a9a3a792feb47f01881a9c","impliedFormat":1},{"version":"d7e5d5245a8ba34a274717d085174b2c9827722778129b0081fefd341cca8f55","impliedFormat":1},{"version":"d9d32f94056181c31f553b32ce41d0ef75004912e27450738d57efcd2409c324","impliedFormat":1},{"version":"752513f35f6cff294ffe02d6027c41373adf7bfa35e593dbfd53d95c203635ee","impliedFormat":1},{"version":"6c800b281b9e89e69165fd11536195488de3ff53004e55905e6c0059a2d8591e","impliedFormat":1},{"version":"7d4254b4c6c67a29d5e7f65e67d72540480ac2cfb041ca484847f5ae70480b62","impliedFormat":1},{"version":"1a7e2ea171726446850ec72f4d1525d547ff7e86724cc9e7eec509725752a758","impliedFormat":1},{"version":"8c901126d73f09ecdea4785e9a187d1ac4e793e07da308009db04a7283ec2f37","impliedFormat":1},{"version":"db97922b767bd2675fdfa71e08b49c38b7d2c847a1cc4a7274cb77be23b026f1","impliedFormat":1},{"version":"aab290b8e4b7c399f2c09b957666fc95335eb4522b2dd9ead1bf0cb64da6d6ee","impliedFormat":1},{"version":"94fe3281392e1015b22f39535878610b4fa6f1388dc8d78746be3bc4e4bb8950","impliedFormat":1},{"version":"2652448ac55a2010a1f71dd141f828b682298d39728f9871e1cdf8696ef443fd","impliedFormat":1},{"version":"06c25ddfc2242bd06c19f66c9eae4c46d937349a267810f89783680a1d7b5259","impliedFormat":1},{"version":"120599fd965257b1f4d0ff794bc696162832d9d8467224f4665f713a3119078b","impliedFormat":1},{"version":"5433f33b0a20300cca35d2f229a7fc20b0e8477c44be2affeb21cb464af60c76","impliedFormat":1},{"version":"db036c56f79186da50af66511d37d9fe77fa6793381927292d17f81f787bb195","impliedFormat":1},{"version":"bd4131091b773973ca5d2326c60b789ab1f5e02d8843b3587effe6e1ea7c9d86","impliedFormat":1},{"version":"c7f6485931085bf010fbaf46880a9b9ec1a285ad9dc8c695a9e936f5a48f34b4","impliedFormat":1},{"version":"14f6b927888a1112d662877a5966b05ac1bf7ed25d6c84386db4c23c95a5363b","impliedFormat":1},{"version":"6ac6715916fa75a1f7ebdfeacac09513b4d904b667d827b7535e84ff59679aff","impliedFormat":1},{"version":"0427df5c06fafc5fe126d14b9becd24160a288deff40e838bfbd92a35f8d0d00","impliedFormat":1},{"version":"90c54a02432d04e4246c87736e53a6a83084357acfeeba7a489c5422b22f5c7a","impliedFormat":1},{"version":"49c346823ba6d4b12278c12c977fb3a31c06b9ca719015978cb145eb86da1c61","impliedFormat":1},{"version":"bfac6e50eaa7e73bb66b7e052c38fdc8ccfc8dbde2777648642af33cf349f7f1","impliedFormat":1},{"version":"92f7c1a4da7fbfd67a2228d1687d5c2e1faa0ba865a94d3550a3941d7527a45d","impliedFormat":1},{"version":"f53b120213a9289d9a26f5af90c4c686dd71d91487a0aa5451a38366c70dc64b","impliedFormat":1},{"version":"83fe880c090afe485a5c02262c0b7cdd76a299a50c48d9bde02be8e908fb4ae6","impliedFormat":1},{"version":"0a372c2d12a259da78e21b25974d2878502f14d89c6d16b97bd9c5017ab1bc12","impliedFormat":1},{"version":"57d67b72e06059adc5e9454de26bbfe567d412b962a501d263c75c2db430f40e","impliedFormat":1},{"version":"6511e4503cf74c469c60aafd6589e4d14d5eb0a25f9bf043dcbecdf65f261972","impliedFormat":1},{"version":"ec1ca97598eda26b7a5e6c8053623acbd88e43be7c4d29c77ccd57abc4c43999","impliedFormat":1},{"version":"6e2261cd9836b2c25eecb13940d92c024ebed7f8efe23c4b084145cd3a13b8a6","impliedFormat":1},{"version":"a67b87d0281c97dfc1197ef28dfe397fc2c865ccd41f7e32b53f647184cc7307","impliedFormat":1},{"version":"771ffb773f1ddd562492a6b9aaca648192ac3f056f0e1d997678ff97dbb6bf9b","impliedFormat":1},{"version":"232f70c0cf2b432f3a6e56a8dc3417103eb162292a9fd376d51a3a9ea5fbbf6f","impliedFormat":1},{"version":"a47e6d954d22dd9ebb802e7e431b560ed7c581e79fb885e44dc92ed4f60d4c07","impliedFormat":1},{"version":"f019e57d2491c159d47a107fd90219a1734bdd2e25cd8d1db3c8fae5c6b414c4","impliedFormat":1},{"version":"8a0e762ceb20c7e72504feef83d709468a70af4abccb304f32d6b9bac1129b2c","impliedFormat":1},{"version":"d1c9bf292a54312888a77bb19dba5e2503ad803f5393beafd45d78d2f4fe9b48","impliedFormat":1},{"version":"9252d498a77517aab5d8d4b5eb9d71e4b225bbc7123df9713e08181de63180f6","impliedFormat":1},{"version":"cb8d8ef7b9ce8ed3e6f1c814fcbf3f90dab0cb8863079236784fc350746e27c4","impliedFormat":1},{"version":"35e6379c3f7cb27b111ad4c1aa69538fd8e788ab737b8ff7596a1b40e96f4f90","impliedFormat":1},{"version":"1fffe726740f9787f15b532e1dc870af3cd964dbe29e191e76121aa3dd8693f2","impliedFormat":1},{"version":"3be035da7bee86b4c3abf392e0edaa44fc6e45092995eefe36b39118c8a84068","affectsGlobalScope":true,"impliedFormat":1},{"version":"8f828825d077c2fa0ea606649faeb122749273a353daab23924fe674e98ba44c","impliedFormat":1},{"version":"2896c2e673a5d3bd9b4246811f79486a073cbb03950c3d252fba10003c57411a","impliedFormat":1},{"version":"616775f16134fa9d01fc677ad3f76e68c051a056c22ab552c64cc281a9686790","impliedFormat":1},{"version":"65c24a8baa2cca1de069a0ba9fba82a173690f52d7e2d0f1f7542d59d5eb4db0","impliedFormat":1},{"version":"f9fe6af238339a0e5f7563acee3178f51db37f32a2e7c09f85273098cee7ec49","impliedFormat":1},{"version":"407a06ba04eede4074eec470ecba2784cbb3bf4e7de56833b097dd90a2aa0651","impliedFormat":1},{"version":"77e71242e71ebf8528c5802993697878f0533db8f2299b4d36aa015bae08a79c","impliedFormat":1},{"version":"98a787be42bd92f8c2a37d7df5f13e5992da0d967fab794adbb7ee18370f9849","impliedFormat":1},{"version":"5c96bad5f78466785cdad664c056e9e2802d5482ca5f862ed19ba34ffbb7b3a4","impliedFormat":1},{"version":"81d8603ac527e75cfec72bb9391228b58f161c2b33514a9d814c7f3ebd3ef466","impliedFormat":1},{"version":"5f3dc10ae646f375776b4e028d2bed039a93eebbba105694d8b910feebbe8b9c","impliedFormat":1},{"version":"bb0cd7862b72f5eba39909c9889d566e198fcaddf7207c16737d0c2246112678","impliedFormat":1},{"version":"4545c1a1ceca170d5d83452dd7c4994644c35cf676a671412601689d9a62da35","impliedFormat":1},{"version":"320f4091e33548b554d2214ce5fc31c96631b513dffa806e2e3a60766c8c49d9","impliedFormat":1},{"version":"a2d648d333cf67b9aeac5d81a1a379d563a8ffa91ddd61c6179f68de724260ff","impliedFormat":1},{"version":"d90d5f524de38889d1e1dbc2aeef00060d779f8688c02766ddb9ca195e4a713d","impliedFormat":1},{"version":"a3f41ed1b4f2fc3049394b945a68ae4fdefd49fa1739c32f149d32c0545d67f5","impliedFormat":1},{"version":"bad68fd0401eb90fe7da408565c8aee9c7a7021c2577aec92fa1382e8876071a","impliedFormat":1},{"version":"47699512e6d8bebf7be488182427189f999affe3addc1c87c882d36b7f2d0b0e","impliedFormat":1},{"version":"fec01479923e169fb52bd4f668dbeef1d7a7ea6e6d491e15617b46f2cacfa37d","impliedFormat":1},{"version":"8a8fb3097ba52f0ae6530ec6ab34e43e316506eb1d9aa29420a4b1e92a81442d","impliedFormat":1},{"version":"44e09c831fefb6fe59b8e65ad8f68a7ecc0e708d152cfcbe7ba6d6080c31c61e","impliedFormat":1},{"version":"1c0a98de1323051010ce5b958ad47bc1c007f7921973123c999300e2b7b0ecc0","impliedFormat":1},{"version":"4655709c9cb3fd6db2b866cab7c418c40ed9533ce8ea4b66b5f17ec2feea46a9","impliedFormat":1},{"version":"87affad8e2243635d3a191fa72ef896842748d812e973b7510a55c6200b3c2a4","impliedFormat":1},{"version":"ad036a85efcd9e5b4f7dd5c1a7362c8478f9a3b6c3554654ca24a29aa850a9c5","impliedFormat":1},{"version":"fedebeae32c5cdd1a85b4e0504a01996e4a8adf3dfa72876920d3dd6e42978e7","impliedFormat":1},{"version":"3eecb25bb467a948c04874d70452b14ae7edb707660aac17dc053e42f2088b00","impliedFormat":1},{"version":"cdf21eee8007e339b1b9945abf4a7b44930b1d695cc528459e68a3adc39a622e","impliedFormat":1},{"version":"330896c1a2b9693edd617be24fbf9e5895d6e18c7955d6c08f028f272b37314d","impliedFormat":1},{"version":"1d9c0a9a6df4e8f29dc84c25c5aa0bb1da5456ebede7a03e03df08bb8b27bae6","impliedFormat":1},{"version":"84380af21da938a567c65ef95aefb5354f676368ee1a1cbb4cae81604a4c7d17","impliedFormat":1},{"version":"1af3e1f2a5d1332e136f8b0b95c0e6c0a02aaabd5092b36b64f3042a03debf28","impliedFormat":1},{"version":"30d8da250766efa99490fc02801047c2c6d72dd0da1bba6581c7e80d1d8842a4","impliedFormat":1},{"version":"03566202f5553bd2d9de22dfab0c61aa163cabb64f0223c08431fb3fc8f70280","impliedFormat":1},{"version":"5f0292a40df210ab94b9fb44c8b775c51e96777e14e073900e392b295ca1061b","impliedFormat":1},{"version":"bc9ee0192f056b3d5527bcd78dc3f9e527a9ba2bdc0a2c296fbc9027147df4b2","impliedFormat":1},{"version":"8627ad129bcf56e82adff0ab5951627c993937aa99f5949c33240d690088b803","impliedFormat":1},{"version":"1de80059b8078ea5749941c9f863aa970b4735bdbb003be4925c853a8b6b4450","impliedFormat":1},{"version":"1d079c37fa53e3c21ed3fa214a27507bda9991f2a41458705b19ed8c2b61173d","impliedFormat":1},{"version":"5bf5c7a44e779790d1eb54c234b668b15e34affa95e78eada73e5757f61ed76a","impliedFormat":1},{"version":"5835a6e0d7cd2738e56b671af0e561e7c1b4fb77751383672f4b009f4e161d70","impliedFormat":1},{"version":"5c634644d45a1b6bc7b05e71e05e52ec04f3d73d9ac85d5927f647a5f965181a","impliedFormat":1},{"version":"4b7f74b772140395e7af67c4841be1ab867c11b3b82a51b1aeb692822b76c872","impliedFormat":1},{"version":"27be6622e2922a1b412eb057faa854831b95db9db5035c3f6d4b677b902ab3b7","impliedFormat":1},{"version":"a68d4b3182e8d776cdede7ac9630c209a7bfbb59191f99a52479151816ef9f9e","impliedFormat":99},{"version":"39644b343e4e3d748344af8182111e3bbc594930fff0170256567e13bbdbebb0","impliedFormat":99},{"version":"ed7fd5160b47b0de3b1571c5c5578e8e7e3314e33ae0b8ea85a895774ee64749","impliedFormat":99},{"version":"63a7595a5015e65262557f883463f934904959da563b4f788306f699411e9bac","impliedFormat":1},{"version":"ecbaf0da125974be39c0aac869e403f72f033a4e7fd0d8cd821a8349b4159628","impliedFormat":1},{"version":"4ba137d6553965703b6b55fd2000b4e07ba365f8caeb0359162ad7247f9707a6","impliedFormat":1},{"version":"ceec3c81b2d81f5e3b855d9367c1d4c664ab5046dff8fd56552df015b7ccbe8f","affectsGlobalScope":true,"impliedFormat":1},{"version":"8fac4a15690b27612d8474fb2fc7cc00388df52d169791b78d1a3645d60b4c8b","affectsGlobalScope":true,"impliedFormat":1},{"version":"064ac1c2ac4b2867c2ceaa74bbdce0cb6a4c16e7c31a6497097159c18f74aa7c","impliedFormat":1},{"version":"3dc14e1ab45e497e5d5e4295271d54ff689aeae00b4277979fdd10fa563540ae","impliedFormat":1},{"version":"1d63055b690a582006435ddd3aa9c03aac16a696fac77ce2ed808f3e5a06efab","impliedFormat":1},{"version":"b789bf89eb19c777ed1e956dbad0925ca795701552d22e68fd130a032008b9f9","impliedFormat":1},"f4e8976c19fc926644d72610bf1058bd6bf52add97e46a02bc0b912a751625c0","c8247281abf95cb10b9808667264eea4ac3bb170111e3d7fb77204c718f4d494",{"version":"402e5c534fb2b85fa771170595db3ac0dd532112c8fa44fc23f233bc6967488b","impliedFormat":1},{"version":"7965dc3c7648e2a7a586d11781cabb43d4859920716bc2fdc523da912b06570d","impliedFormat":1},{"version":"90c2bd9a3e72fe08b8fa5982e78cb8dc855a1157b26e11e37a793283c52bf64b","impliedFormat":1},{"version":"a8122fe390a2a987079e06c573b1471296114677923c1c094c24a53ddd7344a2","impliedFormat":1},{"version":"70c2cb19c0c42061a39351156653aa0cf5ba1ecdc8a07424dd38e3a1f1e3c7f4","impliedFormat":1},{"version":"a8fb10fd8c7bc7d9b8f546d4d186d1027f8a9002a639bec689b5000dab68e35c","impliedFormat":1},{"version":"c9b467ea59b86bd27714a879b9ad43c16f186012a26d0f7110b1322025ceaa83","impliedFormat":1},{"version":"57ea19c2e6ba094d8087c721bac30ff1c681081dbd8b167ac068590ef633e7a5","impliedFormat":1},{"version":"cba81ec9ae7bc31a4dc56f33c054131e037649d6b9a2cfa245124c67e23e4721","impliedFormat":1},{"version":"ad193f61ba708e01218496f093c23626aa3808c296844a99189be7108a9c8343","impliedFormat":1},{"version":"a0544b3c8b70b2f319a99ea380b55ab5394ede9188cdee452a5d0ce264f258b2","impliedFormat":1},{"version":"8c654c17c334c7c168c1c36e5336896dc2c892de940886c1639bebd9fc7b9be4","impliedFormat":1},{"version":"6a4da742485d5c2eb6bcb322ae96993999ffecbd5660b0219a5f5678d8225bb0","impliedFormat":1},{"version":"c65ca21d7002bdb431f9ab3c7a6e765a489aa5196e7e0ef00aed55b1294df599","impliedFormat":1},{"version":"c8fc655c2c4bafc155ceee01c84ab3d6c03192ced5d3f2de82e20f3d1bd7f9fa","impliedFormat":1},{"version":"be5a7ff3b47f7e553565e9483bdcadb0ca2040ac9e5ec7b81c7e115a81059882","impliedFormat":1},{"version":"1a93f36ecdb60a95e3a3621b561763e2952da81962fae217ab5441ac1d77ffc5","impliedFormat":1},{"version":"2a771d907aebf9391ac1f50e4ad37952943515eeea0dcc7e78aa08f508294668","impliedFormat":1},{"version":"0146fd6262c3fd3da51cb0254bb6b9a4e42931eb2f56329edd4c199cb9aaf804","impliedFormat":1},{"version":"183f480885db5caa5a8acb833c2be04f98056bdcc5fb29e969ff86e07efe57ab","impliedFormat":99},{"version":"b558c9a18ea4e6e4157124465c3ef1063e64640da139e67be5edb22f534f2f08","impliedFormat":1},{"version":"01374379f82be05d25c08d2f30779fa4a4c41895a18b93b33f14aeef51768692","impliedFormat":1},{"version":"b0dee183d4e65cf938242efaf3d833c6b645afb35039d058496965014f158141","impliedFormat":1},{"version":"c0bbbf84d3fbd85dd60d040c81e8964cc00e38124a52e9c5dcdedf45fea3f213","impliedFormat":1},"df9fc573f18c7bf4809e300a36999a2f830cb23023862485e7e4e21e3bf3e948",{"version":"c57b441e0c0a9cbdfa7d850dae1f8a387d6f81cbffbc3cd0465d530084c2417d","impliedFormat":99},{"version":"8658354b90861a76abc7b3c04ece2124295c7da0cc4c4d31c2c78d8607188d03","impliedFormat":1},"c0adf27efbfa148d5abcf99e860f8e3e6c8fc77a1f99e023c08ef4f12e6ece29","d1a2d7a2384590217fef6bcf9b4e22ba59f7610d77d11be94186885ccfb6a975","54dfac9ceefe7704a452a7c8026e8d4c3df17663ef9dc13313d44ccbc2d0b049",{"version":"48eccefed4751c0d9eb05b82096f88f0c9c8f2e0a7b6b442c2db9880af76efd1","signature":"dc1b40c7f17c490ad9df6eddfe24063ec47b995225de64c0cca16912c159de2b"},"20095967ea916de6271d1b3bebd6038892508d7a665e572113000e2eed24bbaf","02ce0bbc2e5623b71e647408b780a01d3fd6f2ecf3ba01bbbc2d78d848eb8825",{"version":"c89b9bee9a24be740ff2b72cd5c8dc53f30ce76ec2edea4405cb6cf89ce52f95","signature":"1e7adb72026d5762fceb218a2afaff87ac32344d824817daf050a8a50f4a2fde"},"2fcb06807ff4de389d4b03f7e9a14620472884334286567e09c6384d20c913b8",{"version":"acc9b958b822fe0a2da8d6377f7c25046f82a6bbcc2e948faaf727a7933bd58d","impliedFormat":1},"22a7ad418cfd6b97f1436acfdf38781d0fb4a4e55cf181c27c874c269dcb365e","4d588aa5261d914ec3ad43883dc2cdb9c88e05b04878975ceee5965fcad92f11","24486583c8bac0a06465afa20867d61f68f45bbfef77ed43f9c50f015d416510","64a86adb79e9ce90ae2f1449ce4eb0434e00c66b2c0d1480b548f7159d7e77cc","853bd87b3baba5da553f230dd7e7ad1dd0ffc2368cc2f052ce3e63d70010565f","7c2c31813262c91a14e2df4e6ab419488e1fdb10437c75c7bafa7e0b7403b53c","5be01310e4489bd90942d335e4984e8a23a253a7b7b09eeff01030463719e709",{"version":"56208c500dcb5f42be7e18e8cb578f257a1a89b94b3280c506818fed06391805","impliedFormat":1},{"version":"0c94c2e497e1b9bcfda66aea239d5d36cd980d12a6d9d59e66f4be1fa3da5d5a","impliedFormat":1},{"version":"eb9271b3c585ea9dc7b19b906a921bf93f30f22330408ffec6df6a22057f3296","impliedFormat":1},{"version":"aa4a927d0c7239dff845a64e676c71aeed2bbda89a7fb486baab22eb7688ba1d","impliedFormat":1},{"version":"340a990742a00862049b378aaa482b5bb8323d443c799dded51ce711f4f8eb51","impliedFormat":1},{"version":"89eeeebbc612a079c6e7ebe0bde08e06fbc46cfeaebf6157ea3051ed55967b10","impliedFormat":1},{"version":"4c72f66622e266b542fb097f4d1fe88eb858b88b98414a13ef3dd901109e03a1","impliedFormat":1},{"version":"23a933d83f3a8d595b35f3827c5e68239fb4f6eb44e96389269d183fe7ff09ba","impliedFormat":1},{"version":"2acad3ae616a9fb5a8c3d4d7bb5edb11d1d0102372ee939e7fc64359fec4046e","impliedFormat":1},{"version":"c812eabb7d2e13c8e72e216208448f92341a4094dd107cbb0bdb2cb23d1a83e7","impliedFormat":1},{"version":"f734b58ea162765ff4d4a36f671ee06da898921e985a2064510f4925ec1ed062","affectsGlobalScope":true,"impliedFormat":1},{"version":"55c0569d0b70dbc0bb9a811469a1e2a7b8e2bab2d70c013f2e40dfb2d2803d05","impliedFormat":1},{"version":"37f96daaddc2dd96712b2e86f3901f477ac01a5c2539b1bc07fd609d62039ee1","impliedFormat":1},{"version":"9c5c84c449a3d74e417343410ba9f1bd8bfeb32abd16945a1b3d0592ded31bc8","impliedFormat":1},{"version":"a7f09d2aaf994dbfd872eda4f2411d619217b04dbe0916202304e7a3d4b0f5f8","impliedFormat":1},{"version":"a66ebe9a1302d167b34d302dd6719a83697897f3104d255fe02ff65c47c5814e","impliedFormat":99},{"version":"a7f23fecdccf1504dae27c359db676d0a1fbaaeb400b55959078924e4c3a4992","impliedFormat":1},{"version":"bee66a62aa1da254412bb2c3c8c1a0dd12efea0722d35cc6ea7b5fdaa6778fd1","impliedFormat":1},{"version":"05d80364872e31465f8a1eaf2697e4fc418f78aa336f4cea68620a23f1379f6f","impliedFormat":1},{"version":"7345ba3b9eb2182d8cdc4c961b62847c3c9918985179ddefd5ca58a80d8b9e6a","impliedFormat":1},{"version":"81c4a0e6de3d5674ec3a721e04b3eb3244180bda86a22c4185ecac0e3f051cd8","impliedFormat":1},{"version":"39975a01d837394bcac2559639e88ecdc4cfd22433327b46ea6f78eb2c584813","impliedFormat":1},{"version":"7261cabedede09ebfd50e135af40be34f76fb9dbc617e129eaec21b00161ae86","impliedFormat":1},{"version":"ea554794a0d4136c5c6ea8f59ae894c3c0848b17848468a63ed5d3a307e148ae","impliedFormat":1},{"version":"2c378d9368abcd2eba8c29b294d40909845f68557bc0b38117e4f04fc56e5f9c","impliedFormat":1},{"version":"9b048390bcffe88c023a4cd742a720b41d4cd7df83bc9270e6f2339bf38de278","affectsGlobalScope":true,"impliedFormat":1},{"version":"c60b14c297cc569c648ddaea70bc1540903b7f4da416edd46687e88a543515a1","impliedFormat":1},{"version":"acfa00e5599216bcb8c9f3095e5fec4aeddfcc65aabe0eac7e8dbc51e33691c9","impliedFormat":1},{"version":"922d8f0f46dbe9fb80def96f7bcd9d5c1a6c0022d71023afa9eb7b45189d61f2","impliedFormat":1},{"version":"90588fb5ef85f4a8a4234e8062eb97bd3c8114dfb86a0c67f62685969222da8b","impliedFormat":1},{"version":"6ce50ada4bc9d2ad69927dce35cead36da337a618de0a2daaaeeafe38c692597","impliedFormat":1},{"version":"13b8d0a9b0493191f15d11a5452e7c523f811583a983852c1c8539ab2cfdae7c","impliedFormat":1},{"version":"8932771f941e3f8f153a950c65707d0611f30f577256aa59d4b92eda1c3d8f32","impliedFormat":1},{"version":"df6251bd4b5fad52759bfe96e8ab8f2ce625d0b6739b825209b263729a9c321e","impliedFormat":1},{"version":"846068dbe466864be6e2cae9993a4e3ac492a5cb05a36d5ce36e98690fde41f4","impliedFormat":1},{"version":"94c8c60f751015c8f38923e0d1ae32dd4780b572660123fa087b0cf9884a68a8","impliedFormat":1},{"version":"db8747c785df161ef65237bac36a7716168e5ebf18976ab16fd2fff69cf9c6ce","impliedFormat":1},{"version":"3085abdf921a6d225ad037c89eb2ba26a4c3b2c262f842dd3061949d1969b784","impliedFormat":1},{"version":"8e8f7b36675be31c4e9538529c30a552538c42ff866ba59fe70f23ba18479c5a","impliedFormat":1},{"version":"f4f7fbf0e5bf2097ddee2c998cca04b063f6f9cdcb255e728c0e85967119f9e5","impliedFormat":1},{"version":"c5b47653a15ec7c0bde956e77e5ca103ddc180d40eb4b311e4a024ef7c668fb0","impliedFormat":1},{"version":"223709d7c096b4e2bb00390775e43481426c370ac8e270de7e4c36d355fc8bc9","impliedFormat":1},{"version":"0528a80462b04f2f2ad8bee604fe9db235db6a359d1208f370a236e23fc0b1e0","impliedFormat":1},{"version":"17fb3716df78592be07500e9a90bd8c9424dd70c6201226886a8e71b9d2af396","impliedFormat":1},{"version":"82ef7d775e89b200380d8a14dc6af6d985a45868478773d98850ea2449f1be56","impliedFormat":1},{"version":"b86720947f763bbb869c2b183f8e58bca9fa089ed8f9c5a1574b2bea18cfbc02","impliedFormat":1},{"version":"fb7e20b94d23d989fa7c7d20fccebef31c1ef2d3d9ca179cadba6516e4e918ad","impliedFormat":1},{"version":"8326f735a1f0d2b4ad20539cda4e0d2e7c5fc0b534e3c0d503d5ed20a5711009","impliedFormat":1},{"version":"8d720cd4ee809af1d81f4ce88f02168568d5fded574d89875afd8fe7afd9549e","impliedFormat":1},{"version":"df87c2628c5567fd71dc0b765c845b0cbfef61e7c2e56961ac527bfb615ea639","impliedFormat":1},{"version":"659a83f1dd901de4198c9c2aa70e4a46a9bd0c41ce8a42ee26f2dbff5e86b1f3","impliedFormat":1},{"version":"1db5c2491eebd894eb9be03408601cddfe1b08357d021aeb86c3fb6c329a7843","impliedFormat":1},{"version":"224f85b48786de61fb0b018fbea89620ebec6289179daa78ed33c0f83014fc75","impliedFormat":1},{"version":"05fbfcb5c5c247a8b8a1d97dd8557c78ead2fff524f0b6380b4ac9d3e35249fb","impliedFormat":1},{"version":"322f70408b4e1f550ecc411869707764d8b28da3608e4422587630b366daf9de","impliedFormat":1},{"version":"acb93abc527fa52eb2adc5602a7c3c0949861f8e4317a187bb5c3372f872eff4","impliedFormat":1},{"version":"c4ef9e9e0fcb14b52c97ce847fb26a446b7d668d9db98a7de915a22c46f44c37","impliedFormat":1},{"version":"0e447b14e81b5b3e5d83cbea58b734850f78fb883f810e46d3dedba1a5124658","impliedFormat":1},{"version":"045f36d3a830b5ae1b7586492e1a2368d0e4b4209fa656f529fd6f6bb9ac7ced","impliedFormat":1},{"version":"929939785efdef0b6781b7d3a7098238ea3af41be010f18d6627fd061b6c9edf","impliedFormat":1},{"version":"fca68ac3b92725dbf3dac3f9fbc80775b66d2a9c642e75595a4a11a2095b3c9a","impliedFormat":1},{"version":"245d13141d7f9ec6edd36b14844b247e0680950c1c3289774d431cbbd47e714e","impliedFormat":1},{"version":"4326dc453ff5bf36ad778e93b7021cdd9abcfc4efe75a5c04032324f404af558","impliedFormat":1},{"version":"27b47fbd2f2d0d3cd44b8c7231c800f8528949cc56f421093e2b829d6976f173","impliedFormat":1},{"version":"0795a213434963328e8b60e65a9d03a88efc138ae171bbcca39d9000c040e7a4","impliedFormat":1},{"version":"fc745bebefc96e2a518a2d559af6850626cada22a75f794fd40a17aae11e2d54","impliedFormat":1},{"version":"2b0fe9ba00d0d593fb475d4204214a0f604ad8a56f22a5f05c378b52205ef36b","impliedFormat":1},{"version":"3d94a259051acf8acd2108cee57ad58fee7f7b278de76a7a5746f0656eecbff6","impliedFormat":1},{"version":"46097d076be332463ea64865c41d232865614cf358a11af75095dd9cef2871cc","impliedFormat":1},{"version":"6e18a70a7c64e6fe578a8f3ecc1dd562cd0bf6843bbf8e65fde37cf63b9a8ea8","impliedFormat":1},{"version":"3f3526aea8d29f0c53f8fb99201c770c87c357b5e87349aca8494bfd0c145c26","impliedFormat":1},{"version":"6ee92d844e5a1c0eb562d110676a3a17f00d2cd2ea2aaaff0a98d7881b9a4041","impliedFormat":1},{"version":"b9dc36d1f7c5c2350feafb55c090127104e59b7d2a20729b286dab00d70e283d","impliedFormat":1},{"version":"45d3f1d53fa99783a5e3c29debb065d6060d0db650a6a1055308a8619bd6b263","impliedFormat":1},{"version":"a14febaf38fd75a88620a0808732cf9841afc403da2dc3de7a6fc9a49d36bdbc","impliedFormat":1},{"version":"6052522a593f094cfee0e99c76312a229cf2d49ac2e75095af83813ec9f4b109","impliedFormat":1},{"version":"a0ceb6ce93981581494bae078b971b17e36b67502a36a056966940377517091d","impliedFormat":1},{"version":"a63ce903dd08c662702e33700a3d28ca66ed21ac0591e1dbf4a0b309ae80e690","impliedFormat":1},{"version":"2b63d2725550866e0f2b56b2394ce001ebf1145cb4b04dc9daa29d73867b878c","impliedFormat":1},{"version":"e885933b92f26fa3204403999eddc61651cd3109faf8bffa4f6b6e558b0ab2fa","impliedFormat":1},{"version":"bd834465d4395ac3d8d55e94bf2a39c1f5e9be719c99340957b3b6a3a85ec66a","impliedFormat":1},{"version":"fca1059bad0f439021325957b33c933bca31475e4a3a36dda02140f47ffaf8ed","impliedFormat":1},{"version":"6e2d2b63c278fd1c8dd54da2328622c964f50afa62978ed1a73ccd85e99a4fc7","impliedFormat":1},{"version":"e151e41c82004cf09b7ea863f591348c9035e0f7a69d4189cbac89cc9611b89d","impliedFormat":1},{"version":"0778cfe0d671f153a9d30655b81d5721dc7af6ebe4b654c57417b7cba3649b1c","impliedFormat":1},{"version":"b83ffe71adbac91c5596133251e5ec0c9e6664017ee5b776841effe93de8f466","impliedFormat":1},{"version":"61ecf051972c69e7c992bab9cf74c511ecba51b273c4e1590574d97a542bd4ea","impliedFormat":1},{"version":"068f5afbae92a20a5fcd9cfce76f7b90de2c59a952396b5da225b61f95a1d60a","impliedFormat":1},{"version":"bdf5e07a22e661de2c7115e8364b98ef399c24c9fe62035dc1ac945a9dd3372a","impliedFormat":1},{"version":"4e024e2530feda4719448af6bdd0c0c7cfa28d1a4887900f4886bec70cd48fea","impliedFormat":1},{"version":"99c88ea4f93e883d10c04961dbf37c403c4f3c8444948b86effec0bf52176d0e","impliedFormat":1},{"version":"e88f3729fcc3d38d2a1b3cdcbd773d13d72ea3bdf4d0c0c784818e3bfbe7998d","impliedFormat":1},{"version":"f25b1264b694a647593b0a9a044a267098aaf249d646981a7f0503b8bb185352","impliedFormat":1},{"version":"964d0862660f8e46675c83793f42ab2af336f3d6106dee966a4053d5dc433063","impliedFormat":1},{"version":"292ad4203c181f33beb9eb8fe7c6aaae29f62163793278a7ffc2fcc0d0dbed19","impliedFormat":1},{"version":"aa8e5ac3f73eede931d5da74ef1797c174b00854ac701ead5c4a7d6ce4a49029","impliedFormat":1},{"version":"f1a4ca3688d951daa2d7740da5a0827fa34d4a7709eed7b8225215986ee87108","impliedFormat":1},{"version":"08e159b5ef9d14bdd329457c5cbe181e84f13c4ff2546a24b9eb9129b0c71c46","impliedFormat":1},{"version":"f8453a3fe0fe49ab718357120bec2b8205e15eb91ff62eada60a4780458fa91e","impliedFormat":1},{"version":"06f186bb9a6408ef8563dbf17d53cbe23e68422518b49b96afac732844ddbaa1","impliedFormat":1},{"version":"525f9c06245b5b43b1237cfd757396fd7fd8090e5d6a4ded758c7ce17a04bf42","impliedFormat":1},{"version":"04bc74b8fa987f140989e9f4d6dc37f04a307417af3e0a3767baa1eef4964e10","impliedFormat":1},{"version":"6a9d3aa58228faa62ec3d9e305f472a24441f22a8d028234577beb592ec295b2","impliedFormat":1},{"version":"683e2d454f64394931d233740b762dabc379e3ce5c4c4ad4747cdbd6d5fd8e8d","impliedFormat":1},{"version":"18594ddc7900f3e477645819bce4d824989ad296e3d70bdcdce13cabc5d97335","impliedFormat":1},{"version":"9376cce4d849f1d6ad2cb0048807c77cfeb78cee6e29b61dcfe74c7ab2980e18","impliedFormat":1},{"version":"2698935791615907eb632186119dfc307363d6a163f26017084009e44ea261f2","impliedFormat":1},{"version":"4edfc4848068bf58016856dfeb27341c15679884575e1a501e2389a1fea5c579","impliedFormat":1},{"version":"0c3d7a094ef401b3c36c8e3d88382a7e7a8b1e4f702769eba861d03db559876b","impliedFormat":1},{"version":"d3c3280f081f28e846239d27c2f77a41417e6a19f39267d20a282fd07ef36b96","impliedFormat":1},{"version":"7e3a4800683a39375bc99f0d53b21328b0a0377ab7cbb732c564ca7ca04d9b37","impliedFormat":1},{"version":"c777b498a93261d6caa5dbd1187090b79f0263a03526c64ea4f844a679e8299e","impliedFormat":1},{"version":"b4677e9d8802a82455a0f03a211b85f5d4b04cfbc89fc9aa691695b8e70df326","impliedFormat":1},{"version":"7cb0d946957daea11f78a31b85de435e00bcd8964eba66d3e8056ba9d14b9c55","impliedFormat":1},{"version":"b3e441cdb9d9e55e6e120052fe8bf2a8b5e5a46287f21d5bc39561594574e1a9","impliedFormat":1},{"version":"0870e8eb0527c044e844a1d83127f020aa7f79048218a62b2875e818355f8cb2","impliedFormat":1},{"version":"6b7446f89f9e5d47835117416e6d7656bac2bf700513d330254ae979260ce99f","impliedFormat":1},{"version":"9750752db342b88df1b860958a20fac9fd6a507f67c5cfb6bd5cfa8759338b1e","impliedFormat":1},{"version":"946de511c5e04659d9dfaf5ef83770122846d26d3ffe30e636d3339482bbf35a","impliedFormat":1},{"version":"fbcc201a8fc377a92714567491e3f81e204750b612d51a1720af452f1a254760","impliedFormat":1},{"version":"6dd704b0ba0131eb9e707aeedc39be6a224b4669544e518217a75eb7f5dd65c2","impliedFormat":1},{"version":"6effa89f483e5c83c0e0063df5f1d8b006d9d0f1de7eed2233886642424dc8fb","impliedFormat":1},{"version":"84a8c844f9562da8994c07b44dd2777178a147e06020c62a7f6e349e695e7149","impliedFormat":1},{"version":"d43130c35762a80da2299f8b59a4321b6e64acfb0b11a36183379b4c7b83314b","impliedFormat":1},{"version":"6bf44b890824799af8e20c0387ffa987e890fac5c5954a3a7352351eefe55d5d","impliedFormat":1},{"version":"892b19153694b7a3c9a69bcedb54e1c8ad3b9fa370076db4d3522838afd2cd60","impliedFormat":1},{"version":"5461fca70947a4d8fa272d3dda4c729317cec825141313352adf33bc94de142a","impliedFormat":1},{"version":"f83afa274e0f11860c6609198ecca220f5df60690923b990ca06cae21771016e","impliedFormat":1},{"version":"af31f37264ea5d5349eec50786ceca75c572ed3be91bdd7cb428fdd8cd14b17c","impliedFormat":1},{"version":"85e4673ec8507aef18afd4a9acfae0294bdfaac29458ede0b8b56f5a63738486","impliedFormat":1},{"version":"40683566071340b03c74d0a4ffa84d49fedb181a691ce04c97e11b231a7deee4","impliedFormat":1},{"version":"81c8ab81daa2286241ad27468d6fc7ad3ecc62da04b18b77ce9b9b437f6b0863","impliedFormat":1},{"version":"f158721f7427976b5510660c8e53389d5033c915496c028558c66caaf3d1db1c","impliedFormat":1},{"version":"8e56db8febfe127a9142435940c9a5a1ad17ddb2b2a6d8e9e8984785a76db1fd","impliedFormat":1},{"version":"6113c2f172a875db117357f0aa35aa7c1b6316516e813977ef98dc3b4b8baf2a","impliedFormat":1},{"version":"f25c9802b1316afbf667dd8fa6db4ed23aa5e7acc076a1054ca45d7bc9c8e811","impliedFormat":1},{"version":"e99285f74c22ad823c0b9fac55316b84144e15eb91830034badd9eb0fafe71bf","impliedFormat":1},"198d6050e781188719391efefde77a4825f10742e0ca07ac253977b9ad7fcbd4",{"version":"903e81e74b733199790975eb327c42195c4f121a30369b77fe5f1d76251c7a37","signature":"85f279bae24715f398471327e303ba8c9706ed61698dee2aff253673a40bb9be"},"5e811ddc650849bfbb980e354945b020baabc7a9132ada55c72e2ae9a00006cb","ee6f74c01b4de1db2dce4d29a37b4d476a93c19f1925081c5188e8255ba4dafd","c80c5a14651fe24c65de4bf9fa023b62a3f7e4143cea704b8d8f43ce362d3fd1","908681722aef532db11df4213b895573b97211de1a8d2d429c120b3fca54cbf5","87bba61f684f88e9f9e660a09356ca83322d600abf4097fe6993992c8e7b36cb",{"version":"43f68f532b925cbd1c9b40c9f9b5695c34d08c51216f6f64b128c92cf6340225","signature":"28a5d382b226faa1c47137bf83672946cf6a27430efa112ea07c80459d0e0d6e"},"5c79831150a5dc4307a47120a2d181537c1301fc5b604e7d4c8ae8a73bf73012",{"version":"bb967849c113a975f530b3323f0966a15b3d6d91ce5ef1b3ac640720b57e6741","signature":"acc00e821bcecc2202cd34714a245f1c267bf52e86e2ab117810a50209e982c9"},{"version":"6e44264dbca30b076f88aaa3ac24b9d9153f60ffae4459a1091508ed0f94a9f4","signature":"bd374c7a21164bd4787ae8f42369cd7a90f04a815c567fbff7d786b7b5544cf3"},"a041ad7f493bd9b38bffb82ea107a6189e9359d9087ffb341990702ae0608511","1cc6c4d9dc6a292945117d9e11f2c3ab6db2cd5fef96a3bad3293d4d42dc20ff","e0761408acca413aad834710fd1e29d768a3ec1677e4f9158b27d8db5966e6aa","db0fffb6262e754b6b66fef6c0b0df0bca1e57e77c7d74f6d5b1250df2a94141",{"version":"a42ecff2971323a928ce323d937d14da6f3628e6d3ec5c5e56ab0199447b3487","signature":"68ee88bd74b0b2a157fdcb379116877e221b3bafd25f1a7c4269a12314dbd6f3"},"338cb5ccaa3bb4a334b93857710baf74dd6ff46271529964fcd2c66996138112","c65da47462d331ef4c619c8765fd36fe5cc48f5e315b33be654d28bf61b0dd1c","c20f4eb29af637c06e1415b3c34963be3bc68badf8cc70ed4f8e4f39f66e1496","17a0b047cb9917473f4e6e7ac061943ae3d5653cf2dd785590459ed764818068","a0a5346e426daeb26f0fc8d2e29726a85e830cedd6b6ed97842dbf99d3900b46","b89b8b0a66303921b96e6f7c7dde99aa8c32e0161496d042e6c64ff6f83f6ffe","c02323877e18bcd0b9330c4329b2b561624bf02a5644ffbf78c350f080a94344","f56f6cfe2bd9acf18401aef3cd7390b72f26e4c5180d321a87cc5dda7cc5b104","2cb6c60f59ea9ee88bd97b5a043c23100285afb48b597870f09476b330242319","dc3b6b3a1194973bd68076802c93a8147b5e8cabd23e2e264de5661bdd022f76","9c3092243cfef7ad7ec8277be6e1b05cb0f9cc64455af9cca0cfc458ac0ab674","a91cf633eb8bf7707679511ff1f4f9146fb8e08f8441b71797de68dade74eb36","fa93bb9831bbef4ef370e7f5248e7b82b68222efe4fae409e45787dcb953f265","be0dd2e6ba55888fc69bbce83f3998810dbc9a6135d4fda7750f72583e727892","eef99f19092cd2c01b9238ae8cf4d4fd4266d000ee207fdc344f18008c0bf375","23151a4103e96c885e59221993037fb1f71835821af416a944970e37573eebb0","d806d739f1fcf2913b041f403e858e195f1a969ed7a8b2602160ece3c27d70cb","6c2e38ed5be9cba2440aaf72d2efe02958cb3866264dbbe0714474676f46c6fd","5ecda65616c55d0a5053ff73200dd4fbfee728da9c46c9909e2ab4b36ef0f914","023b0feebf20f453ba2d55cd14ab110252985f1fdc5600d6801249394fadd4b4","590d171344a63c6193e7f829852e4dd4c769da23ac1e3589a52de1d3035a3b65","6b8b054ca91caad51a2bd2f38cfa77d83a688e778c8b0a0d99cd3d0ba143bda3","ac59c6e0e6a5224b0165a386ef749e2caea1ace310f11d872f50872d906788e1","ec8fb868d6ad781041d9d31f2df6e00428c3359ea1c806fe29a6a4567f0a3f80","8cbf265a19037216f601357512f9ac3b7d94ead0eab36f77d9c53c775a92052c","2552a31fad45a9ed1bde87e51b038dc0e786cd364b597162263abbf57018949b","740449c29c313c5e3f7a281ccfca1e1382532b4ae144d2e50ec225a49e09e869","0dcb2195e92b41e7558ee88cda7adc8d76728ecd2be00d9506562db838872f80","7edb7e9f94e5a64c0eae6ece11114d4b377e5ecbbc4d884655f26e98a7478ad1","1953b88989e87b5e039398645b227712b27a3ef2615112529059a091e3869d2b",{"version":"528105c7fed37fc8485fb0c6610e74aab7a82c01571dc3c7c5d6fb78302e69b5","signature":"89b0f68f8f0b901f9dfff2b9e7255520283a783d6af7f2bc2953d771232317a2"},"ed5ae9cb61b785028ede754193f6bd513d39abd324cd29aff571cbf6096c0e80","ca78d6c5d70a6971b12953049df748c69892c0fed6d6fd1f710b071545ddf0d5","cce229e046696dbe1b129953f6e2d02f5f42f8748cdeea719c0a9b74fd4368e2","577bac9b97b89e85178625b698bb59ad120df41498199ee356dffe513cf20c0e","e921c61eb6e1711f0c56046a94ea910a5e699191c249acec1b4746eb51ebb6e6",{"version":"b1538a92b9bae8d230267210c5db38c2eb6bdb352128a3ce3aa8c6acf9fc9622","impliedFormat":1},{"version":"6fc1a4f64372593767a9b7b774e9b3b92bf04e8785c3f9ea98973aa9f4bbe490","impliedFormat":1},{"version":"ff09b6fbdcf74d8af4e131b8866925c5e18d225540b9b19ce9485ca93e574d84","impliedFormat":1},{"version":"d5895252efa27a50f134a9b580aa61f7def5ab73d0a8071f9b5bf9a317c01c2d","impliedFormat":1},{"version":"1f366bde16e0513fa7b64f87f86689c4d36efd85afce7eb24753e9c99b91c319","impliedFormat":1},{"version":"7fa8d75d229eeaee235a801758d9c694e94405013fe77d5d1dd8e3201fc414f1","impliedFormat":1}],"root":[83,501,502,527,[530,537],[539,545],[683,734]],"options":{"allowJs":false,"esModuleInterop":true,"jsx":1,"module":99,"skipLibCheck":true,"strict":true,"target":4},"referencedMap":[[729,1],[731,2],[732,3],[730,4],[728,5],[727,6],[734,7],[733,8],[726,9],[724,10],[83,11],[725,12],[687,13],[689,14],[693,15],[699,16],[691,17],[703,18],[701,19],[704,14],[705,14],[709,20],[707,21],[685,22],[711,23],[713,24],[715,25],[717,26],[545,27],[721,28],[719,29],[542,30],[544,31],[684,32],[722,21],[692,33],[690,34],[698,35],[718,36],[720,37],[700,38],[706,34],[702,39],[708,34],[695,40],[694,41],[688,42],[712,43],[714,44],[686,45],[540,46],[723,47],[683,48],[543,49],[696,50],[541,47],[530,51],[697,11],[710,43],[716,43],[533,52],[532,11],[534,11],[535,11],[536,53],[537,54],[539,42],[531,11],[502,55],[501,56],[248,11],[561,57],[560,11],[557,11],[735,11],[736,11],[737,11],[738,58],[570,11],[547,59],[571,60],[546,11],[739,11],[145,61],[146,61],[147,62],[100,63],[148,64],[149,65],[150,66],[95,11],[98,67],[96,11],[97,11],[151,68],[152,69],[153,70],[154,71],[155,72],[156,73],[157,73],[158,74],[159,75],[160,76],[161,77],[101,11],[99,11],[162,78],[163,79],[164,80],[198,81],[165,82],[166,11],[167,83],[168,84],[169,85],[170,86],[171,87],[172,88],[173,89],[174,90],[175,91],[176,91],[177,92],[178,11],[179,93],[180,94],[182,95],[181,96],[183,97],[184,98],[185,99],[186,100],[187,101],[188,102],[189,103],[190,104],[191,105],[192,106],[193,107],[194,108],[195,109],[102,11],[103,11],[104,11],[142,110],[143,11],[144,11],[196,111],[197,112],[202,113],[358,47],[203,114],[201,115],[360,116],[359,117],[199,118],[356,11],[200,119],[84,11],[86,120],[355,47],[266,47],[740,11],[528,11],[85,11],[676,11],[601,11],[538,47],[93,121],[447,122],[452,10],[454,123],[224,124],[252,125],[430,126],[247,127],[235,11],[216,11],[222,11],[420,128],[283,129],[223,11],[389,130],[257,131],[258,132],[354,133],[417,134],[372,135],[424,136],[425,137],[423,138],[422,11],[421,139],[254,140],[225,141],[304,11],[305,142],[220,11],[236,143],[226,144],[288,143],[285,143],[209,143],[250,145],[249,11],[429,146],[439,11],[215,11],[330,147],[331,148],[325,47],[475,11],[333,11],[334,149],[326,150],[481,151],[479,152],[474,11],[416,153],[415,11],[473,154],[327,47],[368,155],[366,156],[476,11],[480,11],[478,157],[477,11],[367,158],[468,159],[471,160],[295,161],[294,162],[293,163],[484,47],[292,164],[277,11],[487,11],[490,11],[489,47],[491,165],[205,11],[426,166],[427,167],[428,168],[238,11],[214,169],[204,11],[346,47],[207,170],[345,171],[344,172],[335,11],[336,11],[343,11],[338,11],[341,173],[337,11],[339,174],[342,175],[340,174],[221,11],[212,11],[213,143],[267,176],[268,177],[265,178],[263,179],[264,180],[260,11],[352,149],[374,149],[446,181],[455,182],[459,183],[433,184],[432,11],[280,11],[492,185],[442,186],[328,187],[329,188],[320,189],[310,11],[351,190],[311,191],[353,192],[348,193],[347,11],[349,11],[365,194],[434,195],[435,196],[313,197],[317,198],[308,199],[412,200],[441,201],[287,202],[390,203],[210,204],[440,205],[206,127],[261,11],[269,206],[401,207],[259,11],[400,208],[94,11],[395,209],[237,11],[306,210],[391,11],[211,11],[270,11],[399,211],[219,11],[275,212],[316,213],[431,214],[315,11],[398,11],[262,11],[403,215],[404,216],[217,11],[406,217],[408,218],[407,219],[240,11],[397,204],[410,220],[396,221],[402,222],[228,11],[231,11],[229,11],[233,11],[230,11],[232,11],[234,223],[227,11],[382,224],[381,11],[387,225],[383,226],[386,227],[385,227],[388,225],[384,226],[274,228],[375,229],[438,230],[494,11],[463,231],[465,232],[312,11],[464,233],[436,195],[493,234],[332,195],[218,11],[314,235],[271,236],[272,237],[273,238],[303,239],[411,239],[289,239],[376,240],[290,240],[256,241],[255,11],[380,242],[379,243],[378,244],[377,245],[437,246],[324,247],[362,248],[323,249],[357,250],[361,251],[419,252],[418,253],[414,254],[371,255],[373,256],[370,257],[409,258],[364,11],[451,11],[363,259],[413,11],[276,260],[309,166],[307,261],[278,262],[281,263],[488,11],[279,264],[282,264],[449,11],[448,11],[450,11],[486,11],[284,265],[322,47],[92,11],[369,266],[253,11],[242,267],[318,11],[457,47],[467,268],[302,47],[461,149],[301,269],[444,270],[300,268],[208,11],[469,271],[298,47],[299,47],[291,11],[241,11],[297,272],[296,273],[239,274],[319,90],[286,90],[405,11],[393,275],[392,11],[453,11],[350,276],[321,47],[445,277],[87,47],[90,278],[91,279],[88,47],[89,11],[251,280],[246,281],[245,11],[244,282],[243,11],[443,283],[456,284],[458,285],[460,286],[462,287],[466,288],[500,289],[470,289],[499,290],[472,291],[482,292],[483,293],[485,294],[495,295],[498,169],[497,11],[496,296],[519,297],[517,298],[518,299],[506,300],[507,298],[514,301],[505,302],[510,303],[520,11],[511,304],[516,305],[522,306],[521,307],[504,308],[512,309],[513,310],[508,311],[515,297],[509,312],[587,11],[585,313],[589,314],[656,315],[651,316],[554,317],[622,318],[615,319],[672,320],[552,321],[621,322],[610,323],[655,324],[652,325],[604,326],[614,327],[657,328],[658,328],[659,329],[667,330],[661,330],[669,330],[673,330],[660,330],[662,330],[665,330],[668,330],[664,331],[666,330],[670,332],[663,333],[564,334],[636,47],[633,335],[637,47],[575,330],[565,330],[628,336],[553,337],[574,338],[578,339],[635,330],[550,47],[634,340],[632,47],[631,330],[566,47],[678,341],[646,333],[626,342],[682,343],[644,11],[642,11],[647,344],[645,345],[641,346],[643,347],[648,348],[650,349],[640,47],[573,350],[549,330],[639,330],[588,351],[638,47],[613,350],[671,330],[606,352],[562,353],[567,354],[616,355],[618,352],[597,356],[600,352],[579,357],[599,358],[608,359],[609,360],[605,361],[619,362],[607,363],[584,364],[627,365],[623,366],[624,367],[620,368],[598,369],[586,370],[591,371],[568,372],[595,373],[596,374],[592,375],[569,376],[580,377],[617,360],[563,378],[625,11],[590,379],[583,380],[611,11],[680,381],[681,382],[653,11],[679,383],[674,11],[602,11],[576,11],[649,384],[603,11],[555,383],[677,385],[582,386],[612,387],[581,388],[654,389],[593,11],[629,11],[630,390],[577,11],[594,11],[675,11],[551,47],[559,391],[556,11],[558,11],[394,392],[503,11],[529,11],[525,393],[524,11],[523,11],[526,394],[81,11],[82,11],[13,11],[14,11],[16,11],[15,11],[2,11],[17,11],[18,11],[19,11],[20,11],[21,11],[22,11],[23,11],[24,11],[3,11],[25,11],[26,11],[4,11],[27,11],[31,11],[28,11],[29,11],[30,11],[32,11],[33,11],[34,11],[5,11],[35,11],[36,11],[37,11],[38,11],[6,11],[42,11],[39,11],[40,11],[41,11],[43,11],[7,11],[44,11],[49,11],[50,11],[45,11],[46,11],[47,11],[48,11],[8,11],[54,11],[51,11],[52,11],[53,11],[55,11],[9,11],[56,11],[57,11],[58,11],[60,11],[59,11],[61,11],[62,11],[10,11],[63,11],[64,11],[65,11],[11,11],[66,11],[67,11],[68,11],[69,11],[70,11],[1,11],[71,11],[72,11],[12,11],[76,11],[74,11],[79,11],[78,11],[73,11],[77,11],[75,11],[80,11],[120,395],[130,396],[119,395],[140,397],[111,398],[110,399],[139,296],[133,400],[138,401],[113,402],[127,403],[112,404],[136,405],[108,406],[107,296],[137,407],[109,408],[114,409],[115,11],[118,409],[105,11],[141,410],[131,411],[122,412],[123,413],[125,414],[121,415],[124,416],[134,296],[116,417],[117,418],[126,419],[106,420],[129,411],[128,409],[132,11],[135,421],[548,422],[572,423],[527,424]],"affectedFilesPendingEmit":[729,731,732,730,728,727,734,733,726,725,687,689,693,699,691,703,701,704,705,709,707,685,711,713,715,717,545,721,719,542,544,684,722,692,690,698,718,720,700,706,702,708,695,694,688,712,714,686,540,723,683,543,696,541,530,697,710,716,533,532,534,535,536,537,539,531,502,527],"version":"5.9.3"}
```
