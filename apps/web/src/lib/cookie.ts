/** Cookie de auth: secure em produção ou quando COOKIE_SECURE=true (homelab HTTPS). */
export function authCookieSecure(): boolean {
  return (
    process.env.NODE_ENV === "production" ||
    process.env.COOKIE_SECURE === "true" ||
    (process.env.APP_PUBLIC_URL ?? "").startsWith("https://")
  );
}
