import { NextResponse } from "next/server";

import { getServerApiBaseUrl } from "@/lib/api";

export async function POST(request: Request, { params }: { params: Promise<{ token: string }> }) {
  const body = await request.json().catch(() => null);
  const { token } = await params;
  const response = await fetch(
    `${getServerApiBaseUrl()}/api/v1/auth/redefinir-senha/${encodeURIComponent(token)}`,
    { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) },
  );
  return NextResponse.json(await response.json().catch(() => ({})), { status: response.status });
}
