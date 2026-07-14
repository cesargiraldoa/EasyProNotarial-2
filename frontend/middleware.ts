import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { isRouteAllowedForRoles } from "@/lib/authorization";
import { readRolesFromJwt } from "@/lib/jwt-roles";

const PROTECTED_PREFIXES = ["/dashboard"];

export function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname;
  const isProtected = PROTECTED_PREFIXES.some((prefix) =>
    pathname.startsWith(prefix)
  );

  if (!isProtected) {
    return NextResponse.next();
  }

  const sessionToken = request.cookies.get("easypro2_session")?.value;

  if (!sessionToken) {
    const loginUrl = new URL("/login", request.nextUrl.origin);
    loginUrl.searchParams.set("next", pathname);
    return NextResponse.redirect(loginUrl);
  }

  const roles = readRolesFromJwt(sessionToken);

  if (!isRouteAllowedForRoles(pathname, roles)) {
    return NextResponse.redirect(new URL("/dashboard", request.nextUrl.origin));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*"],
};
