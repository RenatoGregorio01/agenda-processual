"use client";

import { useState, useTransition } from "react";

import { excluirPrazo } from "@/app/prazos/actions";
import { Button, Card } from "@/components/ui";

type ExcluirPrazoButtonProps = {
  prazoId: string;
  acao: string;
};

export function ExcluirPrazoButton({ prazoId, acao }: ExcluirPrazoButtonProps) {
  const [confirming, setConfirming] = useState(false);
  const [pending, startTransition] = useTransition();

  if (!confirming) {
    return (
      <Button type="button" variant="link" fullWidth className="text-atrasado" onClick={() => setConfirming(true)}>
        Excluir
      </Button>
    );
  }

  return (
    <Card className="border-atrasado/30 p-4">
      <p className="text-sm text-foreground">
        Excluir <span className="font-medium">“{acao}”</span>? O prazo sai da lista ativa, mas
        pode ser restaurado em <span className="font-medium">Excluídos</span>.
      </p>
      <div className="mt-4 flex flex-col gap-2 sm:flex-row">
        <Button
          type="button"
          variant="danger"
          disabled={pending}
          className="flex-1"
          onClick={() => {
            startTransition(async () => {
              await excluirPrazo(prazoId);
            });
          }}
        >
          {pending ? "Excluindo…" : "Sim, excluir"}
        </Button>
        <Button
          type="button"
          variant="secondary"
          disabled={pending}
          className="flex-1"
          onClick={() => setConfirming(false)}
        >
          Cancelar
        </Button>
      </div>
    </Card>
  );
}
