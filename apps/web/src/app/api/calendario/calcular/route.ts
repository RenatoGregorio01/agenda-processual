import { cookies } from "next/headers";
import { NextResponse, type NextRequest } from "next/server";

import { getServerApiBaseUrl } from "@/lib/api";
import { AUTH_COOKIE } from "@/lib/auth";

export async function POST(request: NextRequest) {
  const cookieStore = await cookies();
  const token = cookieStore.get(AUTH_COOKIE)?.value;
  if (!token) {
    return NextResponse.json({ detail: "Não autenticado" }, { status: 401 });
  }

  const body = await request.text();
  const response = await fetch(
    `${getServerApiBaseUrl()}/api/v1/calendario/calcular-vencimento`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body,
      cache: "no-store",
    },
  );

  const text = await response.text();
  return new NextResponse(text, {
    status: response.status,
    headers: { "Content-Type": "application/json" },
  });
}
