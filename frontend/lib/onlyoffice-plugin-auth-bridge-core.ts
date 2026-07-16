export const EASYPRO_ONLYOFFICE_AUTH_REQUEST_TYPE = "EASYPRO_ONLYOFFICE_AUTH_REQUEST";
export const EASYPRO_ONLYOFFICE_AUTH_RESPONSE_TYPE = "EASYPRO_ONLYOFFICE_AUTH_RESPONSE";
export const EASYPRO_ONLYOFFICE_RELOAD_REQUEST_TYPE = "EASYPRO_ONLYOFFICE_RELOAD_REQUEST";
export const EASYPRO_MINUTA_TEMPLATE_RETURN_REQUEST_TYPE = "EASYPRO_MINUTA_TEMPLATE_RETURN_REQUEST";
export const EASYPRO_ONLYOFFICE_PLUGIN_SOURCE = "motor-biblioteca";
export const EASYPRO_ONLYOFFICE_HOST_SOURCE = "easypro-host";
export const PRODUCTION_ONLYOFFICE_ORIGIN = "https://onlyoffice.easypronotarial.com";

export type OnlyOfficeAuthRequestPayload = {
  type: typeof EASYPRO_ONLYOFFICE_AUTH_REQUEST_TYPE;
  source: typeof EASYPRO_ONLYOFFICE_PLUGIN_SOURCE;
};

export type OnlyOfficeDocumentContext =
  | {
      kind: "case_document";
      case_id: number;
      document_id: number;
      version_id: number;
    }
  | {
      kind: "minuta";
      editor_token: string;
    };

export type OnlyOfficeAuthResponsePayload =
  | {
      type: typeof EASYPRO_ONLYOFFICE_AUTH_RESPONSE_TYPE;
      source: typeof EASYPRO_ONLYOFFICE_HOST_SOURCE;
      token: string;
      document_context?: OnlyOfficeDocumentContext;
    }
  | {
      type: typeof EASYPRO_ONLYOFFICE_AUTH_RESPONSE_TYPE;
      source: typeof EASYPRO_ONLYOFFICE_HOST_SOURCE;
      error: "NO_SESSION";
    };

export type OnlyOfficeReloadRequestPayload = {
  type: typeof EASYPRO_ONLYOFFICE_RELOAD_REQUEST_TYPE;
  source: typeof EASYPRO_ONLYOFFICE_PLUGIN_SOURCE;
  analysis_id?: string;
  review_document: Extract<OnlyOfficeDocumentContext, { kind: "case_document" }>;
};

export type MinutaTemplateReturnPayload = {
  caseId: number;
  documentId: number;
  versionId: number;
  documentName: string;
  sourceDocumentTitle: string;
  fields: unknown[];
  values: Record<string, string>;
  saved?: boolean;
};

export type MinutaTemplateReturnRequestPayload = {
  type: typeof EASYPRO_MINUTA_TEMPLATE_RETURN_REQUEST_TYPE;
  source: typeof EASYPRO_ONLYOFFICE_PLUGIN_SOURCE;
  payload: MinutaTemplateReturnPayload;
};

type PostMessageTarget = {
  postMessage: (message: OnlyOfficeAuthResponsePayload, targetOrigin: string) => void;
};

export type BridgeMessageEvent = {
  data: unknown;
  origin: string;
  source: PostMessageTarget | null;
};

export type BridgeEventTarget = {
  addEventListener: (type: "message", handler: (event: BridgeMessageEvent) => void) => void;
  removeEventListener: (type: "message", handler: (event: BridgeMessageEvent) => void) => void;
};

function normalizeOrigin(value: string | null | undefined): string | null {
  if (!value?.trim()) return null;
  try {
    return new URL(value.trim()).origin;
  } catch {
    return null;
  }
}

function addOriginsFromCsv(target: Set<string>, value: string | null | undefined) {
  if (!value) return;
  value.split(",").forEach((item) => {
    const origin = normalizeOrigin(item);
    if (origin) target.add(origin);
  });
}

export function resolveAllowedOnlyOfficeOrigins(options: {
  docsUrl?: string | null;
  extraOrigins?: string | null;
} = {}): Set<string> {
  const origins = new Set<string>([PRODUCTION_ONLYOFFICE_ORIGIN]);
  const configuredDocsOrigin = normalizeOrigin(options.docsUrl);
  if (configuredDocsOrigin) origins.add(configuredDocsOrigin);
  addOriginsFromCsv(origins, options.extraOrigins);
  origins.add("http://localhost:8082");
  origins.add("http://127.0.0.1:8082");
  return origins;
}

export function isOnlyOfficeAuthRequest(
  event: BridgeMessageEvent,
  allowedOrigins: Set<string>,
): event is BridgeMessageEvent & { data: OnlyOfficeAuthRequestPayload; source: PostMessageTarget } {
  if (!allowedOrigins.has(event.origin)) return false;
  if (!event.source) return false;
  if (!event.data || typeof event.data !== "object") return false;
  const data = event.data as Partial<OnlyOfficeAuthRequestPayload>;
  return data.type === EASYPRO_ONLYOFFICE_AUTH_REQUEST_TYPE
    && data.source === EASYPRO_ONLYOFFICE_PLUGIN_SOURCE;
}

export function isOnlyOfficeReloadRequest(
  event: BridgeMessageEvent,
  allowedOrigins: Set<string>,
): event is BridgeMessageEvent & { data: OnlyOfficeReloadRequestPayload } {
  if (!allowedOrigins.has(event.origin)) return false;
  if (!event.data || typeof event.data !== "object") return false;
  const data = event.data as Partial<OnlyOfficeReloadRequestPayload>;
  const review = data.review_document as Partial<OnlyOfficeDocumentContext> | undefined;
  return data.type === EASYPRO_ONLYOFFICE_RELOAD_REQUEST_TYPE
    && data.source === EASYPRO_ONLYOFFICE_PLUGIN_SOURCE
    && review?.kind === "case_document"
    && Number.isFinite(Number(review.case_id))
    && Number.isFinite(Number(review.document_id))
    && Number.isFinite(Number(review.version_id));
}

export function isMinutaTemplateReturnRequest(
  event: BridgeMessageEvent,
  allowedOrigins: Set<string>,
): event is BridgeMessageEvent & { data: MinutaTemplateReturnRequestPayload } {
  if (!allowedOrigins.has(event.origin)) return false;
  if (!event.data || typeof event.data !== "object") return false;
  const data = event.data as Partial<MinutaTemplateReturnRequestPayload>;
  const payload = data.payload as Partial<MinutaTemplateReturnPayload> | undefined;
  return data.type === EASYPRO_MINUTA_TEMPLATE_RETURN_REQUEST_TYPE
    && data.source === EASYPRO_ONLYOFFICE_PLUGIN_SOURCE
    && Number.isFinite(Number(payload?.caseId))
    && Number.isFinite(Number(payload?.documentId))
    && Number.isFinite(Number(payload?.versionId))
    && typeof payload?.documentName === "string"
    && typeof payload?.sourceDocumentTitle === "string"
    && Array.isArray(payload?.fields)
    && Boolean(payload?.values)
    && typeof payload?.values === "object"
    && !Array.isArray(payload?.values);
}

export function buildOnlyOfficeAuthResponse(
  token: string | null | undefined,
  documentContext?: OnlyOfficeDocumentContext | null,
): OnlyOfficeAuthResponsePayload {
  if (typeof token === "string" && token.trim()) {
    return {
      type: EASYPRO_ONLYOFFICE_AUTH_RESPONSE_TYPE,
      source: EASYPRO_ONLYOFFICE_HOST_SOURCE,
      token: token.trim(),
      ...(documentContext ? { document_context: documentContext } : {}),
    };
  }

  return {
    type: EASYPRO_ONLYOFFICE_AUTH_RESPONSE_TYPE,
    source: EASYPRO_ONLYOFFICE_HOST_SOURCE,
    error: "NO_SESSION",
  };
}

export function createOnlyOfficePluginAuthBridgeHandler(options: {
  allowedOrigins: Set<string>;
  getSessionToken: () => string | null;
  getDocumentContext?: () => OnlyOfficeDocumentContext | null;
  reloadCaseDocument?: (context: Extract<OnlyOfficeDocumentContext, { kind: "case_document" }>, analysisId?: string) => void;
  returnMinutaTemplateToForm?: (payload: MinutaTemplateReturnPayload) => void;
}) {
  return function handleOnlyOfficePluginAuth(event: BridgeMessageEvent) {
    if (isOnlyOfficeAuthRequest(event, options.allowedOrigins)) {
      event.source.postMessage(
        buildOnlyOfficeAuthResponse(options.getSessionToken(), options.getDocumentContext?.() ?? null),
        event.origin,
      );
      return;
    }
    if (options.reloadCaseDocument && isOnlyOfficeReloadRequest(event, options.allowedOrigins)) {
      if (!options.getSessionToken()) return;
      options.reloadCaseDocument(
        {
          kind: "case_document",
          case_id: Number(event.data.review_document.case_id),
          document_id: Number(event.data.review_document.document_id),
          version_id: Number(event.data.review_document.version_id),
        },
        event.data.analysis_id,
      );
      return;
    }
    if (options.returnMinutaTemplateToForm && isMinutaTemplateReturnRequest(event, options.allowedOrigins)) {
      if (!options.getSessionToken()) return;
      options.returnMinutaTemplateToForm({
        caseId: Number(event.data.payload.caseId),
        documentId: Number(event.data.payload.documentId),
        versionId: Number(event.data.payload.versionId),
        documentName: event.data.payload.documentName,
        sourceDocumentTitle: event.data.payload.sourceDocumentTitle,
        fields: event.data.payload.fields,
        values: Object.fromEntries(
          Object.entries(event.data.payload.values).map(([key, value]) => [key, value == null ? "" : String(value)]),
        ),
        saved: Boolean(event.data.payload.saved),
      });
    }
  };
}

export function installOnlyOfficePluginAuthBridge(options: {
  target: BridgeEventTarget;
  allowedOrigins: Set<string>;
  getSessionToken: () => string | null;
  getDocumentContext?: () => OnlyOfficeDocumentContext | null;
  reloadCaseDocument?: (context: Extract<OnlyOfficeDocumentContext, { kind: "case_document" }>, analysisId?: string) => void;
  returnMinutaTemplateToForm?: (payload: MinutaTemplateReturnPayload) => void;
}) {
  const handler = createOnlyOfficePluginAuthBridgeHandler({
    allowedOrigins: options.allowedOrigins,
    getSessionToken: options.getSessionToken,
    getDocumentContext: options.getDocumentContext,
    reloadCaseDocument: options.reloadCaseDocument,
    returnMinutaTemplateToForm: options.returnMinutaTemplateToForm,
  });
  options.target.addEventListener("message", handler);
  return () => options.target.removeEventListener("message", handler);
}
