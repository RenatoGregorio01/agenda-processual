"use client";

import Link from "next/link";
import { useActionState } from "react";

import { updatePrazo, type ActionState } from "@/app/prazos/actions";
import type { UserOption } from "@/lib/auth";
import type { Prazo } from "@/lib/prazos";

const initialState: ActionState = {};

type EditarPrazoFormProps = {
  prazo: Prazo;
  usuarios: UserOption[];
};

export function EditarPrazoForm({ prazo, usuarios }: EditarPrazoFormProps) {
  const boundUpdate = updatePrazo.bind(null, prazo.id);
  const [state, formAction, pending] = useActionState(boundUpdate, initialState);
  const defaultResponsavel = prazo.responsavel_id ?? usuarios[0]?.id ?? "";

  return (
    <form action={formAction} className="flex flex-col gap-5">
      <label className="flex flex-col gap-1.5 text-sm">
        <span className="font-medium">Número do processo</span>
        <input
          name="numero_processo"
          required
          defaultValue={prazo.numero_processo}
          className="h-11 border border-border bg-background px-3 outline-none ring-primary focus:ring-2"
        />
      </label>

      <label className="flex flex-col gap-1.5 text-sm">
        <span className="font-medium">Cliente</span>
        <input
          name="cliente"
          required
          defaultValue={prazo.cliente}
          className="h-11 border border-border bg-background px-3 outline-none ring-primary focus:ring-2"
        />
      </label>

      <label className="flex flex-col gap-1.5 text-sm">
        <span className="font-medium">O que precisa ser feito</span>
        <input
          name="acao"
          required
          defaultValue={prazo.acao}
          className="h-11 border border-border bg-background px-3 outline-none ring-primary focus:ring-2"
        />
      </label>

      <label className="flex flex-col gap-1.5 text-sm">
        <span className="font-medium">Data de disponibilização no diário</span>
        <input
          name="data_disponibilizacao"
          type="date"
          defaultValue={prazo.data_disponibilizacao ?? ""}
          className="h-11 border border-border bg-background px-3 outline-none ring-primary focus:ring-2"
        />
      </label>

      <label className="flex flex-col gap-1.5 text-sm">
        <span className="font-medium text-primary">Data de vencimento</span>
        <input
          name="data_vencimento"
          type="date"
          required
          defaultValue={prazo.data_vencimento}
          className="h-12 border-2 border-primary bg-background px-3 text-base font-semibold outline-none ring-primary focus:ring-2"
        />
        <span className="text-xs text-muted">
          Esta data deve aparecer em destaque na lista e nos alertas.
        </span>
      </label>

      <label className="flex flex-col gap-1.5 text-sm">
        <span className="font-medium">Responsável</span>
        <select
          name="responsavel_id"
          required
          defaultValue={defaultResponsavel}
          className="h-11 border border-border bg-background px-3 outline-none ring-primary focus:ring-2"
        >
          {usuarios.map((user) => (
            <option key={user.id} value={user.id}>
              {user.nome} ({user.email})
            </option>
          ))}
        </select>
      </label>

      <fieldset className="flex flex-col gap-2 border border-border p-4">
        <legend className="px-1 text-sm font-medium">Alertas por e-mail</legend>
        <label className="flex items-center gap-2 text-sm">
          <input name="alerta_3_dias" type="checkbox" defaultChecked={prazo.alerta_3_dias} />
          Alertar 3 dias antes
        </label>
        <label className="flex items-center gap-2 text-sm">
          <input name="alerta_2_dias" type="checkbox" defaultChecked={prazo.alerta_2_dias} />
          Alertar 2 dias antes
        </label>
        <label className="flex items-center gap-2 text-sm">
          <input name="alerta_1_dia" type="checkbox" defaultChecked={prazo.alerta_1_dia} />
          Alertar 1 dia antes
        </label>
      </fieldset>

      {state.error ? <p className="text-sm text-atrasado">{state.error}</p> : null}

      <div className="flex flex-col gap-3 sm:flex-row">
        <button
          type="submit"
          disabled={pending || usuarios.length === 0}
          className="inline-flex h-12 items-center justify-center bg-primary px-6 text-base font-semibold text-primary-foreground transition hover:brightness-110 disabled:opacity-60"
        >
          {pending ? "Salvando…" : "Salvar alterações"}
        </button>
        <Link
          href={`/prazos/${prazo.id}`}
          className="inline-flex h-12 items-center justify-center border border-border bg-surface px-6 text-base font-medium"
        >
          Cancelar
        </Link>
      </div>
    </form>
  );
}
