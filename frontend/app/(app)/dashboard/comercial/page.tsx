import { CommercialWorkspace } from "@/components/notaries/commercial-workspace";
import { requireRouteAccess } from "@/lib/server-auth";

export default async function CommercialPage() {
  await requireRouteAccess("/dashboard/comercial");

  return <CommercialWorkspace />;
}
