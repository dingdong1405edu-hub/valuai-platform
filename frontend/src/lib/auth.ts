const COOKIE_NAME = "valuai_token";
const MAX_AGE = 60 * 60 * 24 * 7; // 7 days

export function getToken(): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie.match(new RegExp(`(?:^|; )${COOKIE_NAME}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}

export function setToken(token: string): void {
  document.cookie = `${COOKIE_NAME}=${encodeURIComponent(token)}; max-age=${MAX_AGE}; path=/; SameSite=Lax`;
}

export function clearToken(): void {
  document.cookie = `${COOKIE_NAME}=; max-age=0; path=/`;
}
