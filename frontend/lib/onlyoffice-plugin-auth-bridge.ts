"use client";

import { useEffect } from "react";
import { getToken } from "@/lib/auth";
import {
  installOnlyOfficePluginAuthBridge,
  resolveAllowedOnlyOfficeOrigins,
  type OnlyOfficeDocumentContext,
} from "@/lib/onlyoffice-plugin-auth-bridge-core";

export function useOnlyOfficePluginAuthBridge(documentContext: OnlyOfficeDocumentContext | null) {
  useEffect(() => {
    const allowedOrigins = resolveAllowedOnlyOfficeOrigins({
      docsUrl: process.env.NEXT_PUBLIC_ONLYOFFICE_DOCS_URL,
      extraOrigins: process.env.NEXT_PUBLIC_ONLYOFFICE_ALLOWED_ORIGINS,
    });
    return installOnlyOfficePluginAuthBridge({
      target: window,
      allowedOrigins,
      getSessionToken: getToken,
      getDocumentContext: () => documentContext,
    });
  }, [documentContext]);
}
