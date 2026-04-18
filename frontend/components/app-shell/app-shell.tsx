"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { Bell, ChevronDown, HelpCircle, LogOut, Menu, MoonStar, Search, SunMedium, UserRound } from "lucide-react";
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
  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null);
  const menuRef = useRef<HTMLDivElement | null>(null);

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
        <aside className="ep-sidebar ep-shell-divider-y hidden w-[292px] shrink-0 flex-col px-6 py-6 lg:flex">
          <div className="flex items-center gap-4">
            <LogoBadge initials={defaultBranding.logoInitials} compact />
            <div className="min-w-0">
              <p className="text-sm font-semibold uppercase tracking-[0.24em] text-primary/80">EasyPro 2</p>
              <p className="mt-1 text-xs text-secondary">{defaultBranding.officeLabel}</p>
            </div>
          </div>

          <nav className="mt-10 space-y-2">
            {visibleNavigation.map(({ label, href, icon: Icon }) => {
              const isActive = pathname === href || pathname.startsWith(`${href}/`);
              return (
                <Link
                  key={label}
                  href={href}
                  className={cn(
                    "ep-nav-item flex min-h-12 items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium leading-5 transition",
                    isActive && "ep-nav-item-active",
                  )}
                >
                  <Icon className="h-4 w-4 shrink-0" />
                  <span className="min-w-0">{label === "Casos" ? "Minutas" : label === "Crear Caso" ? "Crear Minuta" : label}</span>
                </Link>
              );
            })}
          </nav>

          <div className="mt-auto space-y-2 pt-8">
            <Link href="/dashboard/ayuda" className="ep-nav-item flex min-h-12 w-full items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition">
              <HelpCircle className="h-4 w-4 shrink-0" />
              <span>Ayuda</span>
            </Link>
            <button onClick={onLogout} className="ep-nav-item flex min-h-12 w-full items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition">
              <LogOut className="h-4 w-4 shrink-0" />
              <span>Cerrar sesión</span>
            </button>
          </div>
        </aside>

        <div className="flex min-h-screen flex-1 flex-col">
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
