import { RolesWorkspace } from "@/components/roles/roles-workspace";
import { requireRouteAccess } from "@/lib/server-auth";

export default async function RolesPage() {
  await requireRouteAccess("/dashboard/roles");

  return <RolesWorkspace />;
}
