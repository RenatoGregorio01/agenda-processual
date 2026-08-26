"use client";

import { useState, useTransition, type FormEvent } from "react";

import { Button, Field, Input } from "@/components/ui";

export function RecuperarSenhaForm() {
  const [sent, setSent] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pending, startTransition] = useTransition();
  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(null);
    const email = String(new FormData(event.currentTarget).get("email") || "");
    startTransition(async () => {
      const response = await fetch("/api/auth/recuperar-senha", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email }) });
      if (!response.ok) { setError("Não foi possível processar a solicitação. Tente novamente."); return; }
      setSent(true);
    });
  }
  if (sent) return <p className="rounded-md border border-border bg-background p-4 text-sm text-foreground">Se houver uma conta com este e-mail, enviaremos um link para redefinir sua senha.</p>;
  return <form onSubmit={onSubmit} className="flex flex-col gap-5"><Field label="E-mail"><Input name="email" type="email" required autoComplete="email" className="h-12" /></Field>{error ? <p className="text-sm text-atrasado">{error}</p> : null}<Button type="submit" size="lg" fullWidth disabled={pending}>{pending ? "Enviando…" : "Enviar link de recuperação"}</Button></form>;
}
