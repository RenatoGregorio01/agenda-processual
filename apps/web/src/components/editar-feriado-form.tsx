"use client";

import { useActionState, useState, useTransition } from "react";

import { deleteFeriado, updateFeriado, type ActionState } from "@/app/feriados/actions";
import { Button, Card, Field, Input } from "@/components/ui";
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
    <Card className="p-4">
      <form action={formAction} className="flex flex-col gap-3">
        <div className="grid gap-3 sm:grid-cols-2">
          <Field label="Data">
            <Input name="data" type="date" required defaultValue={feriado.data} />
          </Field>
          <Field label="Nome">
            <Input name="nome" required defaultValue={feriado.nome} />
          </Field>
        </div>
        {state.error ? <p className="text-sm text-atrasado">{state.error}</p> : null}
        {deleteError ? <p className="text-sm text-atrasado">{deleteError}</p> : null}
        <div className="flex flex-wrap gap-2">
          <Button type="submit" variant="secondary" size="sm" disabled={pending}>
            {pending ? "Salvando…" : "Salvar"}
          </Button>
          <Button
            type="button"
            variant="danger"
            size="sm"
            onClick={onDelete}
            disabled={deletePending}
          >
            {deletePending ? "Excluindo…" : "Excluir"}
          </Button>
        </div>
      </form>
    </Card>
  );
}
