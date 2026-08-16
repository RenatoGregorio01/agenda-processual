import { NextResponse } from "next/server";

import { AUTH_COOKIE } from "@/lib/auth";
import { authCookieSecure } from "@/lib/cookie";

export async function POST() {
  const response = NextResponse.json({ ok: true });
  response.cookies.set({
    name: AUTH_COOKIE,
    value: "",
    httpOnly: true,
    sameSite: "lax",
    secure: authCookieSecure(),
    path: "/",
    maxAge: 0,
  });
  return response;
}
