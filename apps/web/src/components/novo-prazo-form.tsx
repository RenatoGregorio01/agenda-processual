"use client";

import Link from "next/link";
import { useActionState, useState } from "react";

import { createPrazo, type ActionState } from "@/app/prazos/actions";
import { CalculoDiasUteis } from "@/components/calculo-dias-uteis";
import type { UserOption } from "@/lib/auth";

const initialState: ActionState = {};

export function NovoPrazoForm({ usuarios }: { usuarios: UserOption[] }) {
  const [state, formAction, pending] = useActionState(createPrazo, initialState);
  const defaultResponsavel = usuarios[0]?.id ?? "";
  const [dataDisponibilizacao, setDataDisponibilizacao] = useState("");
  const [dataVencimento, setDataVencimento] = useState("");

  return (
    <form action={formAction} className="flex flex-col gap-5">
      <label className="flex flex-col gap-1.5 text-sm">
        <span className="font-medium">Número do processo</span>
        <input
          name="numero_processo"
          required
          className="h-11 border border-border bg-background px-3 outline-none ring-primary focus:ring-2"
          placeholder="0001234-56.2024.4.01.0000"
        />
      </label>

      <label className="flex flex-col gap-1.5 text-sm">
        <span className="font-medium">Cliente</span>
        <input
          name="cliente"
          required
          className="h-11 border border-border bg-background px-3 outline-none ring-primary focus:ring-2"
        />
      </label>

      <label className="flex flex-col gap-1.5 text-sm">
        <span className="font-medium">O que precisa ser feito</span>
        <input
          name="acao"
          required
          className="h-11 border border-border bg-background px-3 outline-none ring-primary focus:ring-2"
          placeholder="Protocolar contestação"
        />
      </label>

      <label className="flex flex-col gap-1.5 text-sm">
        <span className="font-medium">Data de disponibilização no diário</span>
        <input
          name="data_disponibilizacao"
          type="date"
          value={dataDisponibilizacao}
          onChange={(event) => setDataDisponibilizacao(event.target.value)}
          className="h-11 border border-border bg-background px-3 outline-none ring-primary focus:ring-2"
        />
      </label>

      <CalculoDiasUteis
        defaultDataBase={dataDisponibilizacao}
        onVencimento={setDataVencimento}
      />

      <label className="flex flex-col gap-1.5 text-sm">
        <span className="font-medium text-primary">Data de vencimento</span>
        <input
          name="data_vencimento"
          type="date"
          required
          value={dataVencimento}
          onChange={(event) => setDataVencimento(event.target.value)}
          className="h-12 border-2 border-primary bg-background px-3 text-base font-semibold outline-none ring-primary focus:ring-2"
        />
        <span className="text-xs text-muted">
          Preencha manualmente ou use o cálculo em dias úteis acima.
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
        <span className="text-xs text-muted">
          O responsável recebe o alerta por e-mail; demais usuários dependem da opção em Usuários.
        </span>
      </label>

      <fieldset className="flex flex-col gap-2 border border-border p-4">
        <legend className="px-1 text-sm font-medium">Alertas por e-mail</legend>
        <label className="flex items-center gap-2 text-sm">
          <input name="alerta_3_dias" type="checkbox" defaultChecked />
          Alertar 3 dias antes
        </label>
        <label className="flex items-center gap-2 text-sm">
          <input name="alerta_2_dias" type="checkbox" defaultChecked />
          Alertar 2 dias antes
        </label>
        <label className="flex items-center gap-2 text-sm">
          <input name="alerta_1_dia" type="checkbox" defaultChecked />
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
          {pending ? "Salvando…" : "Salvar prazo"}
        </button>
        <Link
          href="/prazos"
          className="inline-flex h-12 items-center justify-center border border-border bg-surface px-6 text-base font-medium"
        >
          Cancelar
        </Link>
      </div>
    </form>
  );
}
