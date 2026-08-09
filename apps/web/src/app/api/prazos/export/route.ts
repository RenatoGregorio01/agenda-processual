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

  const upstream = new URL(`${getServerApiBaseUrl()}/api/v1/prazos/export`);
  request.nextUrl.searchParams.forEach((value, key) => {
    upstream.searchParams.set(key, value);
  });
  if (!upstream.searchParams.has("formato")) {
    upstream.searchParams.set("formato", "csv");
  }

  const response = await fetch(upstream, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });

  if (!response.ok) {
    const detail = await response.text();
    return new NextResponse(detail || "Falha ao exportar", { status: response.status });
  }

  const headers = new Headers();
  const contentType = response.headers.get("Content-Type");
  const disposition = response.headers.get("Content-Disposition");
  if (contentType) headers.set("Content-Type", contentType);
  if (disposition) headers.set("Content-Disposition", disposition);

  const body = await response.arrayBuffer();
  return new NextResponse(body, { status: 200, headers });
}
