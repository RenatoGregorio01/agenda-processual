"use client";

import { useState, useTransition, type FormEvent } from "react";
import { useRouter } from "next/navigation";

import { Button, Field, Input } from "@/components/ui";

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

      router.replace(nextPath.startsWith("/") ? nextPath : "/dashboard");
      router.refresh();
    });
  }

  return (
    <form method="post" onSubmit={onSubmit} className="flex flex-col gap-5">
      <Field label="E-mail">
        <Input
          name="email"
          type="email"
          required
          autoComplete="email"
          className="h-12"
        />
      </Field>

      <div className="flex flex-col gap-1.5">
        <Field label="Senha">
          <Input
            name="password"
            type="password"
            required
            minLength={6}
            autoComplete="current-password"
            className="h-12"
          />
        </Field>
        <div className="flex justify-end">
          <Button
            type="button"
            variant="link"
            size="sm"
            onClick={() =>
              setError("Recuperação de senha ainda não está disponível no MVP.")
            }
          >
            Esqueci a senha
          </Button>
        </div>
      </div>

      {error ? <p className="text-sm text-atrasado">{error}</p> : null}

      <Button type="submit" size="lg" fullWidth disabled={pending}>
        {pending ? "Entrando…" : "Entrar"}
      </Button>
    </form>
  );
}
