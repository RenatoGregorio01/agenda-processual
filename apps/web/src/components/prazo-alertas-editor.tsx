"use client";

import { useRouter } from "next/navigation";
import { useState, useTransition } from "react";

import { updatePrazoAlertas } from "@/app/prazos/actions";
import {
  ALERTA_DIAS_MAX,
  ALERTA_DIAS_MIN,
  labelAlertaDias,
  type Prazo,
} from "@/lib/prazos";

export function PrazoAlertasEditor({
  prazo,
  canEdit,
}: {
  prazo: Prazo;
  canEdit: boolean;
}) {
  const router = useRouter();
  const [alertas, setAlertas] = useState(prazo.alertas ?? []);
  const [draft, setDraft] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, startTransition] = useTransition();

  function persist(nextDays: number[]) {
    setError(null);
    const previous = alertas;
    const next = nextDays
      .sort((a, b) => b - a)
      .map((dias) => ({
        dias_antes: dias,
        enviado: previous.find((item) => item.dias_antes === dias)?.enviado ?? false,
      }));
    setAlertas(next);
    startTransition(async () => {
      const result = await updatePrazoAlertas(prazo.id, nextDays);
      if (result.error) {
        setError(result.error);
        setAlertas(previous);
        return;
      }
      router.refresh();
    });
  }

  function removeAlert(dias: number) {
    persist(alertas.map((item) => item.dias_antes).filter((item) => item !== dias));
  }

  function addAlert() {
    const value = Number(draft);
    if (!Number.isInteger(value) || value < ALERTA_DIAS_MIN || value > ALERTA_DIAS_MAX) {
      setError(`Informe um número entre ${ALERTA_DIAS_MIN} e ${ALERTA_DIAS_MAX}.`);
      return;
    }
    if (alertas.some((item) => item.dias_antes === value)) {
      setError("Esse alerta já foi adicionado.");
      return;
    }
    setDraft("");
    persist([...alertas.map((item) => item.dias_antes), value]);
  }

  return (
    <section>
      <h3 className="text-sm font-medium text-foreground">Alertas por e-mail</h3>
      <p className="mt-1 text-xs text-muted">
        Escolha com quantos dias de antecedência o responsável deve ser avisado.
      </p>

      {alertas.length === 0 ? (
        <p className="mt-3 border border-dashed border-border px-3 py-3 text-sm text-muted">
          Nenhum alerta configurado.
        </p>
      ) : (
        <ul className="mt-3 space-y-1.5 text-sm">
          {alertas.map((item) => (
            <li
              key={item.dias_antes}
              className="flex items-center justify-between gap-2 border border-border bg-surface px-3 py-1.5"
            >
              <div className="min-w-0">
                <p className="text-foreground">{labelAlertaDias(item.dias_antes)}</p>
                <p className="text-xs text-muted">
                  {item.enviado ? (
                    <span className="font-medium text-no-prazo">Enviado ✓</span>
                  ) : (
                    "Aguardando envio"
                  )}
                </p>
              </div>
              {canEdit ? (
                <button
                  type="button"
                  onClick={() => removeAlert(item.dias_antes)}
                  disabled={pending}
                  aria-label={`Remover alerta de ${labelAlertaDias(item.dias_antes)}`}
                  className="inline-flex h-8 w-8 shrink-0 items-center justify-center text-muted transition hover:bg-background hover:text-atrasado disabled:opacity-50"
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
              ) : null}
            </li>
          ))}
        </ul>
      )}

      {canEdit ? (
        <div className="mt-3 flex flex-col gap-2 sm:flex-row sm:items-end">
          <label className="flex min-w-0 flex-1 flex-col gap-1 text-sm">
            <span className="text-muted">Adicionar alerta</span>
            <input
              type="number"
              min={ALERTA_DIAS_MIN}
              max={ALERTA_DIAS_MAX}
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              placeholder="Ex.: 7"
              disabled={pending}
              className="h-10 border border-border bg-surface px-3 outline-none ring-primary focus:ring-2 disabled:opacity-60"
            />
          </label>
          <button
            type="button"
            onClick={addAlert}
            disabled={pending || !draft}
            className="inline-flex h-10 items-center justify-center bg-primary px-4 text-sm font-semibold text-primary-foreground disabled:opacity-60"
          >
            {pending ? "Salvando…" : "Adicionar"}
          </button>
        </div>
      ) : null}

      {error ? <p className="mt-2 text-sm text-atrasado">{error}</p> : null}
    </section>
  );
}
