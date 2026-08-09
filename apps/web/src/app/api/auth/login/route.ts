import { NextResponse } from "next/server";

import { getApiBaseUrl } from "@/lib/api";
import { AUTH_COOKIE, type LoginPayload } from "@/lib/auth";

export async function POST(request: Request) {
  let payload: LoginPayload;
  try {
    payload = (await request.json()) as LoginPayload;
  } catch {
    return NextResponse.json({ detail: "JSON inválido" }, { status: 400 });
  }

  if (!payload.email || !payload.password) {
    return NextResponse.json({ detail: "E-mail e senha são obrigatórios" }, { status: 400 });
  }

  const apiResponse = await fetch(`${getApiBaseUrl()}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: payload.email,
      password: payload.password,
    }),
  });

  const data = await apiResponse.json().catch(() => ({}));
  if (!apiResponse.ok) {
    return NextResponse.json(
      { detail: data.detail ?? "Falha no login" },
      { status: apiResponse.status },
    );
  }

  const response = NextResponse.json({ ok: true });
  response.cookies.set({
    name: AUTH_COOKIE,
    value: data.access_token,
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: 60 * 60 * 12,
  });
  return response;
}
