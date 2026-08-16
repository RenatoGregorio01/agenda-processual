"use client";

import { useState } from "react";

import {
  ALERTA_DIAS_MAX,
  ALERTA_DIAS_MIN,
  DEFAULT_ALERTA_DIAS,
  labelAlertaDias,
} from "@/lib/prazos";

type AlertasDraftFieldProps = {
  name?: string;
  initialDays?: number[];
};

export function AlertasDraftField({
  name = "alerta_dias",
  initialDays = DEFAULT_ALERTA_DIAS,
}: AlertasDraftFieldProps) {
  const [days, setDays] = useState(() =>
    [...new Set(initialDays.filter((value) => value >= ALERTA_DIAS_MIN))].sort(
      (a, b) => b - a,
    ),
  );
  const [draft, setDraft] = useState("");
  const [error, setError] = useState<string | null>(null);

  function addDay() {
    const value = Number(draft);
    if (!Number.isInteger(value) || value < ALERTA_DIAS_MIN || value > ALERTA_DIAS_MAX) {
      setError(`Informe um número entre ${ALERTA_DIAS_MIN} e ${ALERTA_DIAS_MAX}.`);
      return;
    }
    if (days.includes(value)) {
      setError("Esse alerta já foi adicionado.");
      return;
    }
    setDays((current) => [...current, value].sort((a, b) => b - a));
    setDraft("");
    setError(null);
  }

  function removeDay(value: number) {
    setDays((current) => current.filter((item) => item !== value));
    setError(null);
  }

  return (
    <fieldset className="flex flex-col gap-2 border border-border p-4">
      <legend className="px-1 text-sm font-medium">Alertas por e-mail</legend>
      <p className="text-xs text-muted">
        Escolha com quantos dias de antecedência avisar. O padrão é 3 e 1 dia antes.
      </p>

      {days.map((value) => (
        <input key={value} type="hidden" name={name} value={value} />
      ))}

      {days.length === 0 ? (
        <p className="border border-dashed border-border px-3 py-3 text-sm text-muted">
          Nenhum alerta configurado.
        </p>
      ) : (
        <ul className="space-y-1.5">
          {days.map((value) => (
            <li
              key={value}
              className="flex items-center justify-between gap-2 border border-border bg-background px-3 py-1.5"
            >
              <span className="text-sm text-foreground">{labelAlertaDias(value)}</span>
              <button
                type="button"
                onClick={() => removeDay(value)}
                aria-label={`Remover alerta de ${labelAlertaDias(value)}`}
                className="inline-flex h-8 w-8 shrink-0 items-center justify-center text-muted transition hover:bg-surface hover:text-atrasado"
              >
                <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" aria-hidden>
                  <path
                    d="M6 6l12 12M18 6L6 18"
                    stroke="currentColor"
                    strokeWidth="1.8"
                    strokeLinecap="round"
                  />
                </svg>
              </button>
            </li>
          ))}
        </ul>
      )}

      <div className="flex flex-col gap-2 sm:flex-row sm:items-end">
        <label className="flex min-w-0 flex-1 flex-col gap-1 text-sm">
          <span className="text-muted">Dias de antecedência</span>
          <input
            type="number"
            min={ALERTA_DIAS_MIN}
            max={ALERTA_DIAS_MAX}
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            placeholder="Ex.: 7"
            className="h-10 border border-border bg-background px-3 outline-none ring-primary focus:ring-2"
          />
        </label>
        <button
          type="button"
          onClick={addDay}
          className="inline-flex h-10 items-center justify-center border border-border bg-surface px-4 text-sm font-medium text-foreground sm:mb-0"
        >
          Adicionar
        </button>
      </div>
      {error ? <p className="text-sm text-atrasado">{error}</p> : null}
    </fieldset>
  );
}
