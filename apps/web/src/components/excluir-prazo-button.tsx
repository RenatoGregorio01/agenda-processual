"use client";

import { useState, useTransition } from "react";

import { excluirPrazo } from "@/app/prazos/actions";

type ExcluirPrazoButtonProps = {
  prazoId: string;
  acao: string;
};

export function ExcluirPrazoButton({ prazoId, acao }: ExcluirPrazoButtonProps) {
  const [confirming, setConfirming] = useState(false);
  const [pending, startTransition] = useTransition();

  if (!confirming) {
    return (
      <button
        type="button"
        className="inline-flex h-11 w-full items-center justify-center text-sm text-atrasado underline-offset-4 hover:underline"
        onClick={() => setConfirming(true)}
      >
        Excluir
      </button>
    );
  }

  return (
    <div className="border border-atrasado/30 bg-surface p-4">
      <p className="text-sm text-foreground">
        Excluir <span className="font-medium">“{acao}”</span>? O prazo sai da lista ativa, mas
        pode ser restaurado em <span className="font-medium">Excluídos</span>.
      </p>
      <div className="mt-4 flex flex-col gap-2 sm:flex-row">
        <button
          type="button"
          disabled={pending}
          className="inline-flex h-11 flex-1 items-center justify-center bg-atrasado px-4 text-sm font-semibold text-white disabled:opacity-60"
          onClick={() => {
            startTransition(async () => {
              await excluirPrazo(prazoId);
            });
          }}
        >
          {pending ? "Excluindo…" : "Sim, excluir"}
        </button>
        <button
          type="button"
          disabled={pending}
          className="inline-flex h-11 flex-1 items-center justify-center border border-border px-4 text-sm font-medium disabled:opacity-60"
          onClick={() => setConfirming(false)}
        >
          Cancelar
        </button>
      </div>
    </div>
  );
}
