import {
  Activity,
  Building2,
  GitCompareArrows,
  FolderKanban,
  HelpCircle,
  LayoutDashboard,
  Layers3,
  PenTool,
  Settings,
  ShieldCheck,
  Users2,
  UserCircle,
  type LucideIcon,
} from "lucide-react";
import { ALL_ROLE_CODES, NOTARIAL_WORKSPACE_ROLES } from "@/lib/authorization";

export type NavigationItem = {
  label: string;
  href: string;
  icon: LucideIcon;
  roles: string[];
  disabled?: boolean;
};

export const appNavigation: NavigationItem[] = [
  { label: "Resumen", href: "/dashboard", icon: LayoutDashboard, roles: [...ALL_ROLE_CODES] },
  { label: "Comercial", href: "/dashboard/comercial", icon: ShieldCheck, roles: ["super_admin"] },
  { label: "Notarías", href: "/dashboard/notarias", icon: Building2, roles: ["super_admin"] },
  { label: "Usuarios", href: "/dashboard/usuarios", icon: Users2, roles: ["super_admin", "admin_notary"] },
  { label: "Roles", href: "/dashboard/roles", icon: ShieldCheck, roles: ["super_admin", "admin_notary"] },
  { label: "Minutas", href: "/dashboard/casos", icon: FolderKanban, roles: [...NOTARIAL_WORKSPACE_ROLES] },
  { label: "Crear Minuta", href: "/dashboard/minutas/nueva", icon: PenTool, roles: [...NOTARIAL_WORKSPACE_ROLES] },
  { label: "Actos / Plantillas", href: "/dashboard/actos-plantillas", icon: Layers3, roles: [...NOTARIAL_WORKSPACE_ROLES] },
  { label: "Revisión Documental", href: "/dashboard/inteligencia-documental", icon: GitCompareArrows, roles: [...NOTARIAL_WORKSPACE_ROLES] },
  { label: "System Status", href: "/dashboard/system-status", icon: Activity, roles: ["super_admin"] },
  { label: "Configuración", href: "/dashboard/configuracion", icon: Settings, roles: ["super_admin", "admin_notary"] },
  { label: "Mi Perfil", href: "/dashboard/perfil", icon: UserCircle, roles: [...ALL_ROLE_CODES] },
  { label: "Ayuda", href: "/dashboard/ayuda", icon: HelpCircle, roles: [...ALL_ROLE_CODES] },
];
