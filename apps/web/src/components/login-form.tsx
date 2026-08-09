"use client";

import { useState, useTransition, type FormEvent } from "react";
import { useRouter } from "next/navigation";

type LoginFormProps = {
  nextPath: string;
};

export function LoginForm({ nextPath }: LoginFormProps) {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [pending, startTransition] = useTransition();

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    const formData = new FormData(event.currentTarget);
    const email = String(formData.get("email") || "");
    const password = String(formData.get("password") || "");

    startTransition(async () => {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        setError(
          typeof data.detail === "string" ? data.detail : "Não foi possível entrar",
        );
        return;
      }

      router.replace(nextPath.startsWith("/") ? nextPath : "/prazos");
      router.refresh();
    });
  }

  return (
    <form onSubmit={onSubmit} className="flex flex-col gap-4">
      <label className="flex flex-col gap-1.5 text-sm">
        <span className="font-medium text-foreground">E-mail</span>
        <input
          name="email"
          type="email"
          required
          autoComplete="email"
          className="h-11 border border-border bg-background px-3 outline-none ring-primary focus:ring-2"
          placeholder="veronica@escritorio.com"
        />
      </label>

      <label className="flex flex-col gap-1.5 text-sm">
        <span className="font-medium text-foreground">Senha</span>
        <input
          name="password"
          type="password"
          required
          minLength={6}
          autoComplete="current-password"
          className="h-11 border border-border bg-background px-3 outline-none ring-primary focus:ring-2"
        />
      </label>

      {error ? <p className="text-sm text-atrasado">{error}</p> : null}

      <button
        type="submit"
        disabled={pending}
        className="mt-2 inline-flex h-12 items-center justify-center bg-primary px-6 text-base font-semibold text-primary-foreground transition hover:brightness-110 disabled:opacity-60"
      >
        {pending ? "Entrando…" : "Entrar"}
      </button>

      <button
        type="button"
        className="text-left text-sm text-muted underline-offset-4 hover:underline"
        onClick={() => setError("Recuperação de senha ainda não está disponível no MVP.")}
      >
        Esqueci a senha
      </button>
    </form>
  );
}
