import { NextResponse } from "next/server";

import { getServerApiBaseUrl } from "@/lib/api";
import { AUTH_COOKIE } from "@/lib/auth";
import { authCookieSecure } from "@/lib/cookie";

export async function POST(request: Request) {
  let payload: { token?: string; password?: string };
  try {
    payload = (await request.json()) as { token?: string; password?: string };
  } catch {
    return NextResponse.json({ detail: "JSON inválido" }, { status: 400 });
  }

  if (!payload.token || !payload.password) {
    return NextResponse.json(
      { detail: "Token e senha são obrigatórios" },
      { status: 400 },
    );
  }

  let apiResponse: Response;
  try {
    apiResponse = await fetch(
      `${getServerApiBaseUrl()}/api/v1/convites/aceitar/${encodeURIComponent(payload.token)}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password: payload.password }),
      },
    );
  } catch {
    return NextResponse.json(
      { detail: "Não foi possível conectar à API. Verifique se ela está no ar." },
      { status: 502 },
    );
  }

  const data = await apiResponse.json().catch(() => ({}));
  if (!apiResponse.ok) {
    return NextResponse.json(
      { detail: data.detail ?? "Falha ao aceitar convite" },
      { status: apiResponse.status },
    );
  }

  const response = NextResponse.json({ ok: true });
  response.cookies.set({
    name: AUTH_COOKIE,
    value: data.access_token,
    httpOnly: true,
    sameSite: "lax",
    secure: authCookieSecure(),
    path: "/",
    maxAge: 60 * 60 * 12,
  });
  return response;
}
