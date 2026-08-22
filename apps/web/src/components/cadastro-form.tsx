"use client";

import { useState, useTransition, type FormEvent } from "react";
import { useRouter } from "next/navigation";

import { Button, Field, Input, Select } from "@/components/ui";
import { OAB_UFS } from "@/lib/oab";

function detailMessage(data: unknown, fallback: string): string {
  if (data && typeof data === "object" && "detail" in data) {
    const detail = (data as { detail: unknown }).detail;
    if (typeof detail === "string") return detail;
  }
  return fallback;
}

export function CadastroForm() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);
  const [ehAdvogado, setEhAdvogado] = useState(false);
  const [codigoEnviado, setCodigoEnviado] = useState(false);
  const [pending, startTransition] = useTransition();
  const [sendingCodigo, startSendingCodigo] = useTransition();

  function onEnviarCodigo() {
    setError(null);
    setInfo(null);
    const emailNorm = email.trim().toLowerCase();
    if (!emailNorm) {
      setError("Informe o e-mail para receber o código.");
      return;
    }

    startSendingCodigo(async () => {
      const response = await fetch("/api/cadastro/enviar-codigo", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: emailNorm }),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        setError(detailMessage(data, "Não foi possível enviar o código."));
        return;
      }
      setCodigoEnviado(true);
      setInfo("Enviamos um código de 6 dígitos para o seu e-mail.");
    });
  }

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setInfo(null);

    const formData = new FormData(event.currentTarget);
    const password = String(formData.get("password") || "");
    const confirm = String(formData.get("confirm") || "");
    const codigo = String(formData.get("codigo") || "").trim();

    if (password.length < 6) {
      setError("A senha precisa ter pelo menos 6 caracteres.");
      return;
    }
    if (password !== confirm) {
      setError("As senhas não coincidem.");
      return;
    }
    if (!/^\d{6}$/.test(codigo)) {
      setError("Informe o código de 6 dígitos enviado por e-mail.");
      return;
    }

    const payload = {
      escritorio_nome: String(formData.get("escritorio_nome") || "").trim(),
      nome: String(formData.get("nome") || "").trim(),
      email: email.trim().toLowerCase(),
      codigo,
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
        setError(detailMessage(data, "Não foi possível configurar o escritório."));
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
        <div className="flex flex-col gap-2 sm:flex-row sm:items-stretch">
          <Input
            name="email"
            type="email"
            required
            autoComplete="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className="h-12 flex-1"
          />
          <Button
            type="button"
            variant="secondary"
            className="h-12 shrink-0 sm:px-4"
            disabled={sendingCodigo || pending}
            onClick={onEnviarCodigo}
          >
            {sendingCodigo ? "Enviando…" : codigoEnviado ? "Reenviar código" : "Enviar código"}
          </Button>
        </div>
      </Field>

      <Field label="Código de confirmação">
        <Input
          name="codigo"
          inputMode="numeric"
          autoComplete="one-time-code"
          required
          minLength={6}
          maxLength={6}
          pattern="\d{6}"
          placeholder="000000"
          className="h-12 tracking-[0.2em]"
        />
        <p className="mt-1 text-xs text-muted">
          Digite o código de 6 dígitos enviado ao seu e-mail.
        </p>
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

      {info ? <p className="text-sm text-primary">{info}</p> : null}
      {error ? <p className="text-sm text-atrasado">{error}</p> : null}

      <Button type="submit" size="lg" fullWidth disabled={pending || sendingCodigo}>
        {pending ? "Configurando…" : "Configurar escritório"}
      </Button>
    </form>
  );
}
