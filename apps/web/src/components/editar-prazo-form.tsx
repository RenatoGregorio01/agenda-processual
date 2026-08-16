"use client";

import { useActionState, useState } from "react";

import { updatePrazo, type ActionState } from "@/app/prazos/actions";
import { Button, ButtonLink } from "@/components/ui";
import { AlertasDraftField } from "@/components/alertas-draft-field";
import { CalculoDiasUteis } from "@/components/calculo-dias-uteis";
import { ChecklistDraftField } from "@/components/checklist-draft-field";
import { NumeroProcessoField } from "@/components/numero-processo-field";
import type { UserOption } from "@/lib/auth";
import type { Prazo } from "@/lib/prazos";

const initialState: ActionState = {};

type EditarPrazoFormProps = {
  prazo: Prazo;
  usuarios: UserOption[];
  checklistItems?: string[];
};

export function EditarPrazoForm({
  prazo,
  usuarios,
  checklistItems = [],
}: EditarPrazoFormProps) {
  const boundUpdate = updatePrazo.bind(null, prazo.id);
  const [state, formAction, pending] = useActionState(boundUpdate, initialState);
  const defaultResponsavel = prazo.responsavel_id ?? usuarios[0]?.id ?? "";
  const [numeroProcesso, setNumeroProcesso] = useState(prazo.numero_processo);
  const [numeroInvalido, setNumeroInvalido] = useState(false);
  const [dataDisponibilizacao, setDataDisponibilizacao] = useState(
    prazo.data_disponibilizacao ?? "",
  );
  const [dataVencimento, setDataVencimento] = useState(prazo.data_vencimento);
  const initialChecklist =
    checklistItems.length > 0
      ? checklistItems
      : prazo.acao.trim()
        ? [prazo.acao]
        : [""];

  return (
    <form action={formAction} className="flex flex-col gap-5">
      <NumeroProcessoField
        mode="edit"
        value={numeroProcesso}
        onChange={setNumeroProcesso}
        onInvalidChange={setNumeroInvalido}
      />

      <label className="flex flex-col gap-1.5 text-sm">
        <span className="font-medium">Cliente</span>
        <input
          name="cliente"
          required
          defaultValue={prazo.cliente}
          className="h-11 border border-border bg-background px-3 outline-none ring-primary focus:ring-2"
        />
      </label>

      <ChecklistDraftField initialItems={initialChecklist} />

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
              {user.nome}
            </option>
          ))}
        </select>
      </label>

      <AlertasDraftField
        initialDays={(prazo.alertas ?? []).map((item) => item.dias_antes)}
      />

      {state.error ? <p className="text-sm text-atrasado">{state.error}</p> : null}

      <div className="flex flex-col gap-3 sm:flex-row">
        <Button
          type="submit"
          size="lg"
          disabled={pending || usuarios.length === 0 || numeroInvalido}
        >
          {pending ? "Salvando…" : "Salvar alterações"}
        </Button>
        <ButtonLink href={`/prazos/${prazo.id}`} variant="secondary" size="lg">
          Cancelar
        </ButtonLink>
      </div>
    </form>
  );
}
