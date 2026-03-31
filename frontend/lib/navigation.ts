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
} from "lucide-react";

export const appNavigation = [
  { label: "Resumen", href: "/dashboard", icon: LayoutDashboard },
  { label: "Comercial", href: "/dashboard/comercial", icon: ShieldCheck },
  { label: "Notarías", href: "/dashboard/notarias", icon: Building2 },
  { label: "Usuarios", href: "/dashboard/usuarios", icon: Users2 },
  { label: "Casos", href: "/dashboard/casos", icon: FolderKanban },
  { label: "Crear Caso", href: "/dashboard/casos/crear", icon: PenTool },
  { label: "Actos / Plantillas", href: "/dashboard/actos-plantillas", icon: Layers3 },
  { label: "Lotes", href: "/dashboard/lotes", icon: FileArchive },
  { label: "System Status", href: "/dashboard/system-status", icon: Activity },
  { label: "Configuración", href: "/dashboard/configuracion", icon: Settings },
  { label: "Ayuda", href: "/dashboard/ayuda", icon: HelpCircle },
];

