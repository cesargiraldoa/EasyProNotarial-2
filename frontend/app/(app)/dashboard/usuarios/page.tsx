import { UsersAdminWorkspace } from "@/components/users/users-admin-workspace";
import { requireRouteAccess } from "@/lib/server-auth";

export default async function UsersPage() {
  await requireRouteAccess("/dashboard/usuarios");

  return <UsersAdminWorkspace />;
}
