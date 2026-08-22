"use client";

import { useState, useTransition, type FormEvent } from "react";
import { useRouter } from "next/navigation";

import { Button, Field, Input, Select } from "@/components/ui";
import type { LoginEscritorio, LoginResponse } from "@/lib/auth";

type LoginFormProps = {
  nextPath: string;
};

export function LoginForm({ nextPath }: LoginFormProps) {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [escritorios, setEscritorios] = useState<LoginEscritorio[]>([]);
  const [escritorioId, setEscritorioId] = useState("");
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
        body: JSON.stringify({ email, password, escritorio_id: escritorioId || undefined }),
      });

      const data = (await response.json().catch(() => ({}))) as LoginResponse & { detail?: string };
      if (!response.ok) {
        setError(
          typeof data.detail === "string" ? data.detail : "Não foi possível entrar",
        );
        return;
      }

      if (data.selecionar_escritorio) {
        setEscritorios(data.escritorios ?? []);
        setEscritorioId((data.escritorios ?? [])[0]?.id ?? "");
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

      {escritorios.length > 0 ? (
        <Field label="Escritório para acessar">
          <Select value={escritorioId} onChange={(event) => setEscritorioId(event.target.value)}>
            {escritorios.map((escritorio) => (
              <option key={escritorio.id} value={escritorio.id}>
                {escritorio.nome}
              </option>
            ))}
          </Select>
          <span className="text-xs text-muted">Escolha o escritório desta sessão.</span>
        </Field>
      ) : null}

      {error ? <p className="text-sm text-atrasado">{error}</p> : null}

      <Button type="submit" size="lg" fullWidth disabled={pending}>
        {pending ? "Entrando…" : escritorios.length > 0 ? "Acessar escritório" : "Entrar"}
      </Button>
    </form>
  );
}
