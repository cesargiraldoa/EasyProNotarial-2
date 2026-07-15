export const EASYPRO_ONLYOFFICE_AUTH_REQUEST_TYPE = "EASYPRO_ONLYOFFICE_AUTH_REQUEST";
export const EASYPRO_ONLYOFFICE_AUTH_RESPONSE_TYPE = "EASYPRO_ONLYOFFICE_AUTH_RESPONSE";
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
}) {
  return function handleOnlyOfficePluginAuth(event: BridgeMessageEvent) {
    if (!isOnlyOfficeAuthRequest(event, options.allowedOrigins)) return;
    event.source.postMessage(
      buildOnlyOfficeAuthResponse(options.getSessionToken(), options.getDocumentContext?.() ?? null),
      event.origin,
    );
  };
}

export function installOnlyOfficePluginAuthBridge(options: {
  target: BridgeEventTarget;
  allowedOrigins: Set<string>;
  getSessionToken: () => string | null;
  getDocumentContext?: () => OnlyOfficeDocumentContext | null;
}) {
  const handler = createOnlyOfficePluginAuthBridgeHandler({
    allowedOrigins: options.allowedOrigins,
    getSessionToken: options.getSessionToken,
    getDocumentContext: options.getDocumentContext,
  });
  options.target.addEventListener("message", handler);
  return () => options.target.removeEventListener("message", handler);
}
