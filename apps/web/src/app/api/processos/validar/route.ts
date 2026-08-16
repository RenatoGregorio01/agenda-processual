import { cookies } from "next/headers";
import { NextResponse, type NextRequest } from "next/server";

import { getServerApiBaseUrl } from "@/lib/api";
import { AUTH_COOKIE } from "@/lib/auth";

export async function GET(request: NextRequest) {
  const cookieStore = await cookies();
  const token = cookieStore.get(AUTH_COOKIE)?.value;
  if (!token) {
    return NextResponse.json({ detail: "Não autenticado" }, { status: 401 });
  }

  const numero = request.nextUrl.searchParams.get("numero")?.trim();
  if (!numero) {
    return NextResponse.json({ detail: "Informe o número do processo" }, { status: 400 });
  }

  const response = await fetch(
    `${getServerApiBaseUrl()}/api/v1/processos/validar?numero=${encodeURIComponent(numero)}`,
    {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
    },
  );

  const text = await response.text();
  return new NextResponse(text, {
    status: response.status,
    headers: { "Content-Type": "application/json" },
  });
}
