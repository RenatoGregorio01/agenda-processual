"use client";

import { useState, useTransition, type FormEvent } from "react";
import { useRouter } from "next/navigation";

import { Button, Field, Input, Select } from "@/components/ui";
import { OAB_UFS } from "@/lib/oab";

export function CadastroForm() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [ehAdvogado, setEhAdvogado] = useState(false);
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

    const payload = {
      escritorio_nome: String(formData.get("escritorio_nome") || "").trim(),
      nome: String(formData.get("nome") || "").trim(),
      email: String(formData.get("email") || "").trim().toLowerCase(),
      password,
      eh_advogado: ehAdvogado,
      oab_numero: ehAdvogado ? String(formData.get("oab_numero") || "").trim() : null,
      oab_uf: ehAdvogado ? String(formData.get("oab_uf") || "").trim().toUpperCase() : null,
    };

    startTransition(async () => {
      const response = await fetch("/api/cadastro", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        setError(
          typeof data.detail === "string" ? data.detail : "Não foi possível criar o escritório.",
        );
        return;
      }
      router.replace("/dashboard");
      router.refresh();
    });
  }

  return (
    <form onSubmit={onSubmit} className="flex flex-col gap-4">
      <Field label="Nome do escritório">
        <Input name="escritorio_nome" required className="h-12" />
      </Field>

      <Field label="Seu nome">
        <Input name="nome" required className="h-12" />
      </Field>

      <Field label="E-mail">
        <Input name="email" type="email" required autoComplete="email" className="h-12" />
      </Field>

      <Field label="Senha">
        <Input
          name="password"
          type="password"
          required
          minLength={6}
          autoComplete="new-password"
          className="h-12"
        />
      </Field>

      <Field label="Confirmar senha">
        <Input
          name="confirm"
          type="password"
          required
          minLength={6}
          autoComplete="new-password"
          className="h-12"
        />
      </Field>

      <label className="flex items-start gap-2 text-sm">
        <input
          type="checkbox"
          className="mt-0.5"
          checked={ehAdvogado}
          onChange={(event) => setEhAdvogado(event.target.checked)}
        />
        <span>
          Sou advogado
          <span className="mt-0.5 block text-xs text-muted">
            Usamos OAB para buscar publicações no Diário (DJEN).
          </span>
        </span>
      </label>

      {ehAdvogado ? (
        <div className="grid gap-4 sm:grid-cols-[1fr_7rem]">
          <Field label="Número OAB">
            <Input name="oab_numero" required inputMode="numeric" className="h-12" />
          </Field>
          <Field label="UF">
            <Select name="oab_uf" required defaultValue="BA" className="h-12">
              {OAB_UFS.map((uf) => (
                <option key={uf} value={uf}>
                  {uf}
                </option>
              ))}
            </Select>
          </Field>
        </div>
      ) : null}

      {error ? <p className="text-sm text-atrasado">{error}</p> : null}

      <Button type="submit" size="lg" fullWidth disabled={pending}>
        {pending ? "Criando…" : "Criar escritório"}
      </Button>
    </form>
  );
}
