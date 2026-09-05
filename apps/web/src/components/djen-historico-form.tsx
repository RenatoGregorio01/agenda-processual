"use client";

import { type FormEvent, useState, useTransition } from "react";
import { useRouter } from "next/navigation";

import { enfileirarHistoricoDjen } from "@/app/djen/actions";
import { Button } from "@/components/ui";

export function DjenHistoricoForm() {
  const router = useRouter();
  const [dataInicio, setDataInicio] = useState("");
  const [erro, setErro] = useState<string | null>(null);
  const [pending, startTransition] = useTransition();

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!dataInicio) return;
    startTransition(async () => {
      const mensagem = await enfileirarHistoricoDjen(dataInicio);
      setErro(mensagem);
      if (!mensagem) router.refresh();
    });
  }

  return (
    <form onSubmit={submit} className="rounded-md border border-border bg-surface p-4">
      <p className="text-sm font-semibold text-foreground">Importar histórico por OAB</p>
      <p className="mt-1 text-sm text-muted">
        Escolha a data inicial. A importação será dividida em lotes mensais e processada em fila.
      </p>
      <div className="mt-3 flex flex-wrap items-end gap-3">
        <label className="grid gap-1 text-sm text-foreground">
          A partir de
          <input
            type="date"
            required
            value={dataInicio}
            onChange={(event) => setDataInicio(event.target.value)}
            className="rounded-md border border-border bg-background px-3 py-2"
          />
        </label>
        <Button type="submit" variant="secondary" disabled={pending || !dataInicio}>
          {pending ? "Enfileirando…" : "Importar histórico"}
        </Button>
      </div>
      {erro ? <p className="mt-2 text-sm text-destructive">{erro}</p> : null}
    </form>
  );
}
