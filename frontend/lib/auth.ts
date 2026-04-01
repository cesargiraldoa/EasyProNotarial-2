const SESSION_KEY = "easypro2_session";

function getCookieToken() {
  if (typeof document === "undefined") return null;
  const match = document.cookie.match(new RegExp(`(?:^|; )${SESSION_KEY}=([^;]+)`));
  return match ? decodeURIComponent(match[1]) : null;
}

function getStoredToken() {
  if (typeof window === "undefined") return null;
  try {
    return window.localStorage.getItem(SESSION_KEY) || window.sessionStorage.getItem(SESSION_KEY) || null;
  } catch {
    return null;
  }
}

export function getToken() {
  return getCookieToken() || getStoredToken();
}
