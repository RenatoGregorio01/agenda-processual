import { cookies } from "next/headers";

import { getApiBaseUrl } from "@/lib/api";
import { AUTH_COOKIE } from "@/lib/auth";

export async function apiFetch(path: string, init: RequestInit = {}): Promise<Response> {
  const cookieStore = await cookies();
  const token = cookieStore.get(AUTH_COOKIE)?.value;
  const headers = new Headers(init.headers);

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  return fetch(`${getApiBaseUrl()}${path}`, {
    ...init,
    headers,
    cache: "no-store",
  });
}
