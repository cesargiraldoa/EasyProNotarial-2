import { BibliotecaWorkspace } from "@/components/biblioteca/biblioteca-workspace";
import { requireRouteAccess } from "@/lib/server-auth";

export default async function BibliotecaPage() {
  await requireRouteAccess("/dashboard/biblioteca");

  return <BibliotecaWorkspace />;
}
