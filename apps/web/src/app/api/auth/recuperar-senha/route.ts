import { NextResponse } from "next/server";

import { getServerApiBaseUrl } from "@/lib/api";

export async function POST(request: Request) {
  const body = await request.json().catch(() => null);
  if (!body?.email) return NextResponse.json({ detail: "Informe seu e-mail." }, { status: 400 });
  const response = await fetch(`${getServerApiBaseUrl()}/api/v1/auth/recuperar-senha`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email: body.email }),
  });
  return NextResponse.json(await response.json().catch(() => ({})), { status: response.status });
}
