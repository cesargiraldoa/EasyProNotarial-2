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
  type LucideIcon,
} from "lucide-react";

export type NavigationItem = {
  label: string;
  href: string;
  icon: LucideIcon;
  disabled?: boolean;
};

export const appNavigation: NavigationItem[] = [
  { label: "Resumen", href: "/dashboard", icon: LayoutDashboard },
  { label: "Comercial", href: "/dashboard/comercial", icon: ShieldCheck },
  { label: "Notarías", href: "/dashboard/notarias", icon: Building2 },
  { label: "Usuarios", href: "/dashboard/usuarios", icon: Users2 },
  { label: "Roles", href: "/dashboard/roles", icon: ShieldCheck },
  { label: "Minutas", href: "/dashboard/casos", icon: FolderKanban },
  { label: "Crear Minuta", href: "/dashboard/casos/crear", icon: PenTool },
  { label: "Actos / Plantillas", href: "/dashboard/actos-plantillas", icon: Layers3 },
  { label: "Lotes (Next)", href: "/dashboard/lotes", icon: FileArchive, disabled: true },
  { label: "System Status", href: "/dashboard/system-status", icon: Activity },
  { label: "Configuración", href: "/dashboard/configuracion", icon: Settings },
  { label: "Mi Perfil", href: "/dashboard/perfil", icon: UserCircle },
  { label: "Ayuda", href: "/dashboard/ayuda", icon: HelpCircle },
];

