import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { isRouteAllowedForRoles } from "@/lib/authorization";
import { readRolesFromJwt } from "@/lib/jwt-roles";

const SESSION_COOKIE_NAME = "easypro2_session";

export async function requireRouteAccess(pathname: string) {
  const cookieStore = await cookies();
  const token = cookieStore.get(SESSION_COOKIE_NAME)?.value;
  const roles = readRolesFromJwt(token);

  if (!isRouteAllowedForRoles(pathname, roles)) {
    redirect("/dashboard");
  }
}
