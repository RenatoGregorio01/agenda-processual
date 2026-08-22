"use client";

import { useState, useTransition, type FormEvent } from "react";
import { useRouter } from "next/navigation";

import { Button, Field, Input, Select } from "@/components/ui";
import type { ConvitePublic } from "@/lib/convites";
import { formatOab, OAB_UFS } from "@/lib/oab";

type AceitarConviteFormProps = {
  token: string;
  convite: ConvitePublic;
};

export function AceitarConviteForm({ token, convite }: AceitarConviteFormProps) {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [pending, startTransition] = useTransition();
  const needsOab = convite.eh_advogado && !(convite.oab_numero && convite.oab_uf);

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

    const body: Record<string, string | null> = { token, password };
    if (convite.eh_advogado) {
      body.oab_numero =
        String(formData.get("oab_numero") || convite.oab_numero || "").trim() || null;
      body.oab_uf =
        String(formData.get("oab_uf") || convite.oab_uf || "")
          .trim()
          .toUpperCase() || null;
    }

    startTransition(async () => {
      const response = await fetch("/api/convites/aceitar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
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

  const oabLabel = formatOab(convite.oab_numero, convite.oab_uf);

  return (
    <form onSubmit={onSubmit} className="flex flex-col gap-4">
      <div className="border border-border bg-background p-4 text-sm">
        <p className="font-medium text-foreground">{convite.nome}</p>
        <p className="mt-1 text-muted">{convite.email}</p>
        <p className="mt-2 text-muted">
          Perfil: <span className="text-foreground">{convite.role}</span>
          {convite.eh_advogado ? (
            <>
              {" "}
              · Advogado
              {oabLabel ? (
                <>
                  {" "}
                  (<span className="text-foreground">{oabLabel}</span>)
                </>
              ) : null}
            </>
          ) : null}
        </p>
      </div>

      {needsOab ? (
        <div className="grid gap-4 sm:grid-cols-[1fr_7rem]">
          <Field label="Número OAB">
            <Input name="oab_numero" required inputMode="numeric" />
          </Field>
          <Field label="UF">
            <Select name="oab_uf" required defaultValue="BA">
              {OAB_UFS.map((uf) => (
                <option key={uf} value={uf}>
                  {uf}
                </option>
              ))}
            </Select>
          </Field>
        </div>
      ) : null}

      <Field label="Senha">
        <Input
          name="password"
          type="password"
          required
          minLength={6}
          autoComplete="new-password"
        />
      </Field>

      <Field label="Confirmar senha">
        <Input
          name="confirm"
          type="password"
          required
          minLength={6}
          autoComplete="new-password"
        />
      </Field>

      {error ? <p className="text-sm text-atrasado">{error}</p> : null}

      <Button type="submit" size="lg" disabled={pending}>
        {pending ? "Ativando…" : "Definir senha e entrar"}
      </Button>
    </form>
  );
}
