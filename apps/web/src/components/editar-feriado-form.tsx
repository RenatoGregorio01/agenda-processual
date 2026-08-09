"use client";

import { useActionState, useState, useTransition } from "react";

import { deleteFeriado, updateFeriado, type ActionState } from "@/app/feriados/actions";
import { formatFeriadoDate, type Feriado } from "@/lib/feriados";

const initialState: ActionState = {};

export function EditarFeriadoForm({ feriado }: { feriado: Feriado }) {
  const boundUpdate = updateFeriado.bind(null, feriado.id);
  const [state, formAction, pending] = useActionState(boundUpdate, initialState);
  const [deletePending, startDelete] = useTransition();
  const [deleteError, setDeleteError] = useState<string | null>(null);

  function onDelete() {
    if (!window.confirm(`Excluir feriado “${feriado.nome}” (${formatFeriadoDate(feriado.data)})?`)) {
      return;
    }
    startDelete(async () => {
      const result = await deleteFeriado(feriado.id);
      if (result.error) {
        setDeleteError(result.error);
      }
    });
  }

  return (
    <form action={formAction} className="flex flex-col gap-3 border border-border bg-background p-4">
      <div className="grid gap-3 sm:grid-cols-2">
        <label className="flex flex-col gap-1.5 text-sm">
          <span className="font-medium">Data</span>
          <input
            name="data"
            type="date"
            required
            defaultValue={feriado.data}
            className="h-11 border border-border bg-background px-3 outline-none ring-primary focus:ring-2"
          />
        </label>
        <label className="flex flex-col gap-1.5 text-sm">
          <span className="font-medium">Nome</span>
          <input
            name="nome"
            required
            defaultValue={feriado.nome}
            className="h-11 border border-border bg-background px-3 outline-none ring-primary focus:ring-2"
          />
        </label>
      </div>
      {state.error ? <p className="text-sm text-atrasado">{state.error}</p> : null}
      {deleteError ? <p className="text-sm text-atrasado">{deleteError}</p> : null}
      <div className="flex flex-wrap gap-2">
        <button
          type="submit"
          disabled={pending}
          className="inline-flex h-10 items-center justify-center border border-border bg-surface px-4 text-sm font-medium disabled:opacity-60"
        >
          {pending ? "Salvando…" : "Salvar"}
        </button>
        <button
          type="button"
          onClick={onDelete}
          disabled={deletePending}
          className="inline-flex h-10 items-center justify-center border border-border px-4 text-sm font-medium text-atrasado disabled:opacity-60"
        >
          {deletePending ? "Excluindo…" : "Excluir"}
        </button>
      </div>
    </form>
  );
}
