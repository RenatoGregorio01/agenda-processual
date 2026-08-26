import { NextResponse } from "next/server";

import { getServerApiBaseUrl } from "@/lib/api";

export async function POST(request: Request) {
  let payload: Record<string, unknown>;
  try {
    payload = (await request.json()) as Record<string, unknown>;
  } catch {
    return NextResponse.json({ detail: "JSON inválido" }, { status: 400 });
  }

  let apiResponse: Response;
  try {
    apiResponse = await fetch(`${getServerApiBaseUrl()}/api/v1/cadastro/enviar-codigo`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } catch {
    return NextResponse.json(
      { detail: "Não foi possível conectar à API. Verifique se ela está no ar." },
      { status: 502 },
    );
  }

  const data = await apiResponse.json().catch(() => ({}));
  if (!apiResponse.ok) {
    return NextResponse.json(
      { detail: data.detail ?? "Não foi possível enviar o código" },
      { status: apiResponse.status },
    );
  }

  return NextResponse.json(data);
}
