"use client";

import { createContext, useContext, useMemo, type ReactNode } from "react";
import { readJwtPayload, readRolesFromJwt } from "@/lib/jwt-roles";

const SESSION_COOKIE_NAME = "easypro2_session";

export interface UserContext {
  id: string | null;
  email: string | null;
  nombre: string | null;
  roles: string[];
  notaria_id: string | null;
}

const UserContextValue = createContext<UserContext | null>(null);

function getCookieToken() {
  if (typeof document === "undefined") {
    return null;
  }

  const match = document.cookie.match(new RegExp(`(?:^|; )${SESSION_COOKIE_NAME}=([^;]+)`));
  return match ? decodeURIComponent(match[1]) : null;
}

function readStringClaim(payload: Record<string, unknown> | null, keys: string[]) {
  for (const key of keys) {
    const value = payload?.[key];
    if (typeof value === "string" && value.trim()) {
      return value;
    }
  }

  return null;
}

function readIdClaim(payload: Record<string, unknown> | null) {
  const value = payload?.id ?? payload?.user_id ?? payload?.sub;
  return typeof value === "string" || typeof value === "number" ? String(value) : null;
}

export function UserProvider({ children }: { children: ReactNode }) {
  const user = useMemo<UserContext | null>(() => {
    const token = getCookieToken();

    if (!token) {
      return null;
    }

    const payload = readJwtPayload(token);
    const notaryId = payload?.notaria_id ?? payload?.notary_id;

    return {
      id: readIdClaim(payload),
      email: readStringClaim(payload, ["email"]),
      nombre: readStringClaim(payload, ["nombre", "full_name", "name"]),
      roles: readRolesFromJwt(token),
      notaria_id: typeof notaryId === "string" || typeof notaryId === "number" ? String(notaryId) : null,
    };
  }, []);

  return <UserContextValue.Provider value={user}>{children}</UserContextValue.Provider>;
}

export function useUser() {
  return useContext(UserContextValue);
}
