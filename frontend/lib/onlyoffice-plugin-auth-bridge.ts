"use client";

import { useEffect } from "react";
import { getToken } from "@/lib/auth";
import {
  installOnlyOfficePluginAuthBridge,
  resolveAllowedOnlyOfficeOrigins,
  type MinutaTemplateReturnPayload,
  type OnlyOfficeDocumentContext,
} from "@/lib/onlyoffice-plugin-auth-bridge-core";

const MARKED_TEMPLATE_EDIT_KEY_PREFIX = "easypro:marked-template-edit:";

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
      reloadCaseDocument: (context) => {
        const currentPath = window.location.pathname;
        const targetPath = currentPath.includes("/dashboard/onlyoffice-editor/")
          ? `/dashboard/onlyoffice-editor/${context.case_id}/${context.document_id}/${context.version_id}`
          : `/dashboard/casos/${context.case_id}/editor/${context.document_id}/${context.version_id}`;
        window.location.assign(targetPath);
      },
      returnMinutaTemplateToForm: (payload: MinutaTemplateReturnPayload) => {
        window.sessionStorage.setItem(
          `${MARKED_TEMPLATE_EDIT_KEY_PREFIX}${payload.caseId}`,
          JSON.stringify({
            caseId: payload.caseId,
            documentId: payload.documentId,
            versionId: payload.versionId,
            documentName: payload.documentName,
            sourceDocumentTitle: payload.sourceDocumentTitle,
            fields: payload.fields,
            values: payload.values,
          }),
        );
        window.location.assign(`/dashboard/minutas/nueva?caseId=${payload.caseId}&mode=edit-form`);
      },
    });
  }, [documentContext]);
}
