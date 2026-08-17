import { NextResponse, type NextRequest } from "next/server";

import { AUTH_COOKIE } from "@/lib/auth";

const protectedPrefixes = [
  "/dashboard",
  "/prazos",
  "/processos",
  "/auditoria",
  "/usuarios",
  "/feriados",
];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get(AUTH_COOKIE)?.value;
  const isProtected = protectedPrefixes.some(
    (prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`),
  );

  if (isProtected && !token) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("next", pathname);
    return NextResponse.redirect(loginUrl);
  }

  // Login com sessão: manda pro app. Convite deve abrir mesmo logado
  // (ex.: admin testando o link, ou outro usuário no mesmo browser).
  if (pathname === "/login" && token) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/dashboard",
    "/prazos/:path*",
    "/processos/:path*",
    "/auditoria",
    "/usuarios",
    "/feriados",
    "/convite/:path*",
    "/login",
  ],
};
