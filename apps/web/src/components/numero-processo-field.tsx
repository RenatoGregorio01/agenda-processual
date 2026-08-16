"use client";

import Link from "next/link";
import { useEffect, useRef, useState, useTransition } from "react";

import { dvCnjValido, mascararCnj, soDigitos } from "@/lib/cnj";
import type { ProcessoValidar } from "@/lib/processos";

type NumeroProcessoFieldProps = {
  value: string;
  onChange: (value: string) => void;
  onClienteHint?: (cliente: string) => void;
  onInvalidChange?: (invalid: boolean) => void;
  onCadastradoChange?: (cadastrado: boolean) => void;
  mode?: "create" | "edit";
};

export function NumeroProcessoField({
  value,
  onChange,
  onClienteHint,
  onInvalidChange,
  onCadastradoChange,
  mode = "create",
}: NumeroProcessoFieldProps) {
  const [pending, startLookup] = useTransition();
  const [result, setResult] = useState<ProcessoValidar | null>(null);
  const [resultFor, setResultFor] = useState("");
  const onClienteHintRef = useRef(onClienteHint);
  const onInvalidChangeRef = useRef(onInvalidChange);
  const onCadastradoChangeRef = useRef(onCadastradoChange);
  onClienteHintRef.current = onClienteHint;
  onInvalidChangeRef.current = onInvalidChange;
  onCadastradoChangeRef.current = onCadastradoChange;

  const digits = soDigitos(value);
  const dvInvalido = digits.length === 20 && !dvCnjValido(value);
  const atual = resultFor === digits ? result : null;
  const invalido = dvInvalido || atual?.valido === false;

  useEffect(() => {
    onInvalidChangeRef.current?.(invalido);
  }, [invalido]);

  useEffect(() => {
    const numero = value.trim();
    if (soDigitos(numero).length < 5) {
      setResult(null);
      setResultFor("");
      onCadastradoChangeRef.current?.(false);
      return;
    }

    const handle = window.setTimeout(() => {
      startLookup(async () => {
        const response = await fetch(
          `/api/processos/validar?numero=${encodeURIComponent(numero)}`,
        );
        if (!response.ok) {
          return;
        }
        const next = (await response.json()) as ProcessoValidar;
        setResult(next);
        setResultFor(soDigitos(numero));
        onCadastradoChangeRef.current?.(Boolean(next.cadastrado));
        if (next.cadastrado && next.cliente) {
          onClienteHintRef.current?.(next.cliente);
        }
      });
    }, 400);

    return () => window.clearTimeout(handle);
  }, [value]);

  function handleBlur() {
    const masked = mascararCnj(value);
    if (masked && masked !== value) {
      onChange(masked);
    }
  }

  const mensagemErro =
    atual?.valido === false
      ? atual.mensagem
      : dvInvalido
        ? "Dígito verificador do número CNJ inválido."
        : null;

  return (
    <label className="flex flex-col gap-1.5 text-sm sm:col-span-2">
      <span className="font-medium">Número do processo</span>
      <input
        name="numero_processo"
        required
        value={value}
        onChange={(event) => onChange(event.target.value)}
        onBlur={handleBlur}
        aria-invalid={invalido}
        className="h-11 w-full border border-border bg-background px-3 outline-none ring-primary focus:ring-2"
        placeholder="0001234-12.2024.4.01.0000"
      />
      {pending ? (
        <span className="text-xs text-muted">Verificando processo…</span>
      ) : null}
      {mensagemErro ? (
        <span className="text-xs text-atrasado">{mensagemErro}</span>
      ) : null}
      {!mensagemErro && atual?.datajud_mensagem ? (
        <span
          className={
            atual.datajud === "nao_encontrado"
              ? "text-xs text-muted"
              : "text-xs text-foreground"
          }
        >
          {atual.datajud_mensagem}
        </span>
      ) : null}
      {mode === "create" && atual?.cadastrado && atual.processo_id ? (
        <span className="text-xs text-foreground">
          Processo já cadastrado com {atual.prazos_count ?? 0} prazo
          {(atual.prazos_count ?? 0) === 1 ? "" : "s"}.{" "}
          <Link
            href={`/processos/${atual.processo_id}`}
            className="text-primary underline-offset-4 hover:underline"
          >
            Abrir ficha
          </Link>
          . Este formulário adiciona um novo prazo ao mesmo processo.
        </span>
      ) : mode === "create" && !mensagemErro ? (
        <span className="text-xs text-muted">
          Se o número já existir, o novo prazo entra na ficha do processo.
        </span>
      ) : null}
    </label>
  );
}
