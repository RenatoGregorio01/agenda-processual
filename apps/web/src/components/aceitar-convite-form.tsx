"use client";

import { useState, useTransition, type FormEvent } from "react";
import { useRouter } from "next/navigation";

import type { ConvitePublic } from "@/lib/convites";

type AceitarConviteFormProps = {
  token: string;
  convite: ConvitePublic;
};

export function AceitarConviteForm({ token, convite }: AceitarConviteFormProps) {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [pending, startTransition] = useTransition();

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    const formData = new FormData(event.currentTarget);
    const password = String(formData.get("password") || "");
    const confirm = String(formData.get("confirm") || "");

    if (password.length < 6) {
      setError("A senha precisa ter pelo menos 6 caracteres.");
      return;
    }
    if (password !== confirm) {
      setError("As senhas não coincidem.");
      return;
    }

    startTransition(async () => {
      const response = await fetch("/api/convites/aceitar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, password }),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        setError(
          typeof data.detail === "string"
            ? data.detail
            : "Não foi possível ativar o acesso.",
        );
        return;
      }
      router.replace("/dashboard");
      router.refresh();
    });
  }

  return (
    <form onSubmit={onSubmit} className="flex flex-col gap-4">
      <div className="border border-border bg-background p-4 text-sm">
        <p className="font-medium text-foreground">{convite.nome}</p>
        <p className="mt-1 text-muted">{convite.email}</p>
        <p className="mt-2 text-muted">
          Perfil: <span className="text-foreground">{convite.role}</span>
        </p>
      </div>

      <label className="flex flex-col gap-1.5 text-sm">
        <span className="font-medium">Senha</span>
        <input
          name="password"
          type="password"
          required
          minLength={6}
          autoComplete="new-password"
          className="h-11 border border-border bg-background px-3 outline-none ring-primary focus:ring-2"
        />
      </label>

      <label className="flex flex-col gap-1.5 text-sm">
        <span className="font-medium">Confirmar senha</span>
        <input
          name="confirm"
          type="password"
          required
          minLength={6}
          autoComplete="new-password"
          className="h-11 border border-border bg-background px-3 outline-none ring-primary focus:ring-2"
        />
      </label>

      {error ? <p className="text-sm text-atrasado">{error}</p> : null}

      <button
        type="submit"
        disabled={pending}
        className="inline-flex h-12 items-center justify-center bg-primary px-6 text-base font-semibold text-primary-foreground transition hover:brightness-110 disabled:opacity-60"
      >
        {pending ? "Ativando…" : "Definir senha e entrar"}
      </button>
    </form>
  );
}
