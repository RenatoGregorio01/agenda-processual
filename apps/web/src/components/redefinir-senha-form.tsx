"use client";

import { useState, useTransition, type FormEvent } from "react";
import { useRouter } from "next/navigation";

import { Button, Field, Input } from "@/components/ui";

export function RedefinirSenhaForm({ token }: { token: string }) {
  const router = useRouter(); const [error, setError] = useState<string | null>(null); const [pending, startTransition] = useTransition();
  function onSubmit(event: FormEvent<HTMLFormElement>) { event.preventDefault(); setError(null); const data = new FormData(event.currentTarget); const password = String(data.get("password") || ""); if (password !== String(data.get("confirm") || "")) { setError("As senhas não coincidem."); return; } startTransition(async () => { const response = await fetch(`/api/auth/redefinir-senha/${encodeURIComponent(token)}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ password }) }); const body = await response.json().catch(() => ({})); if (!response.ok) { setError(typeof body.detail === "string" ? body.detail : "Não foi possível redefinir a senha."); return; } router.replace("/login"); router.refresh(); }); }
  return <form onSubmit={onSubmit} className="flex flex-col gap-5"><Field label="Nova senha"><Input name="password" type="password" minLength={6} required autoComplete="new-password" className="h-12" /></Field><Field label="Confirmar nova senha"><Input name="confirm" type="password" minLength={6} required autoComplete="new-password" className="h-12" /></Field>{error ? <p className="text-sm text-atrasado">{error}</p> : null}<Button type="submit" size="lg" fullWidth disabled={pending}>{pending ? "Salvando…" : "Redefinir senha"}</Button></form>;
}
