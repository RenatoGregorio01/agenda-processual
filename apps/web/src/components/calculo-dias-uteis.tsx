"use client";

import { useEffect, useState, useTransition } from "react";

type CalculoResult = {
  data_vencimento: string;
  feriados_no_intervalo: string[];
};

type CalculoDiasUteisProps = {
  onVencimento: (isoDate: string) => void;
  defaultDataBase?: string;
};

function formatDateBr(iso: string): string {
  const [y, m, d] = iso.split("-");
  if (!y || !m || !d) return iso;
  return `${d}/${m}/${y}`;
}

export function CalculoDiasUteis({
  onVencimento,
  defaultDataBase = "",
}: CalculoDiasUteisProps) {
  const [dataBase, setDataBase] = useState(defaultDataBase);
  const [dias, setDias] = useState("15");
  const [result, setResult] = useState<CalculoResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pending, startTransition] = useTransition();

  useEffect(() => {
    if (defaultDataBase) {
      setDataBase(defaultDataBase);
    }
  }, [defaultDataBase]);

  function calcular() {
    setError(null);
    const diasNum = Number(dias);
    if (!dataBase) {
      setError("Informe a data base.");
      return;
    }
    if (!Number.isInteger(diasNum) || diasNum < 1) {
      setError("Informe a quantidade de dias úteis (mínimo 1).");
      return;
    }

    startTransition(async () => {
      const response = await fetch("/api/calendario/calcular", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ data_base: dataBase, dias: diasNum }),
      });
      const payload = (await response.json().catch(() => null)) as
        | CalculoResult
        | { detail?: string }
        | null;

      if (!response.ok) {
        const detail =
          payload && "detail" in payload && typeof payload.detail === "string"
            ? payload.detail
            : "Não foi possível calcular o vencimento.";
        setError(detail);
        setResult(null);
        return;
      }

      const ok = payload as CalculoResult;
      setResult(ok);
      onVencimento(ok.data_vencimento);
    });
  }

  return (
    <fieldset className="flex flex-col gap-3 border border-border p-4">
      <legend className="px-1 text-sm font-medium">Calcular em dias úteis</legend>
      <p className="text-xs text-muted">
        Conta a partir do dia seguinte à data base, pulando sábados, domingos e
        feriados cadastrados. Você pode ajustar a data de vencimento depois.
      </p>

      <div className="grid gap-3 sm:grid-cols-2">
        <label className="flex flex-col gap-1.5 text-sm">
          <span className="font-medium">Data base</span>
          <input
            type="date"
            value={dataBase}
            onChange={(event) => setDataBase(event.target.value)}
            className="h-11 border border-border bg-background px-3 outline-none ring-primary focus:ring-2"
          />
        </label>
        <label className="flex flex-col gap-1.5 text-sm">
          <span className="font-medium">Quantidade de dias úteis</span>
          <input
            type="number"
            min={1}
            max={3650}
            value={dias}
            onChange={(event) => setDias(event.target.value)}
            className="h-11 border border-border bg-background px-3 outline-none ring-primary focus:ring-2"
          />
        </label>
      </div>

      <button
        type="button"
        onClick={calcular}
        disabled={pending}
        className="inline-flex h-11 w-fit items-center justify-center border border-border bg-surface px-4 text-sm font-medium transition hover:bg-background disabled:opacity-60"
      >
        {pending ? "Calculando…" : "Calcular vencimento"}
      </button>

      {error ? <p className="text-sm text-atrasado">{error}</p> : null}
      {result ? (
        <p className="text-sm text-foreground">
          Vencimento:{" "}
          <span className="font-semibold text-primary">
            {formatDateBr(result.data_vencimento)}
          </span>
          {result.feriados_no_intervalo.length > 0
            ? ` · ${result.feriados_no_intervalo.length} feriado(s) no intervalo`
            : null}
        </p>
      ) : null}
    </fieldset>
  );
}
