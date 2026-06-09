const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000";
const DEV_API_LOG_FLAG = "__easyproApiBaseUrlLogged";

export function getApiBaseUrl() {
  const configuredBaseUrl = process.env.NEXT_PUBLIC_API_URL?.trim();
  const baseUrl = configuredBaseUrl || DEFAULT_API_BASE_URL;

  if (process.env.NODE_ENV !== "production" && typeof window !== "undefined") {
    const globalWindow = window as Window & { [DEV_API_LOG_FLAG]?: boolean };
    if (!globalWindow[DEV_API_LOG_FLAG]) {
      globalWindow[DEV_API_LOG_FLAG] = true;
      console.info(`[EasyPro API] baseUrl = ${baseUrl}`);
    }
  }

  return baseUrl;
}

export function buildApiUrl(path: string) {
  return `${getApiBaseUrl()}${path}`;
}
