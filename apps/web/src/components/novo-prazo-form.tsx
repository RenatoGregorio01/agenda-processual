"use client";

import { useActionState, useState } from "react";

import { createPrazo, type ActionState } from "@/app/prazos/actions";
import { Button, ButtonLink } from "@/components/ui";
import { AlertasDraftField } from "@/components/alertas-draft-field";
import { CalculoDiasUteis } from "@/components/calculo-dias-uteis";
import { ChecklistDraftField } from "@/components/checklist-draft-field";
import { NumeroProcessoField } from "@/components/numero-processo-field";
import type { UserOption } from "@/lib/auth";

const initialState: ActionState = {};

type NovoPrazoFormProps = {
  usuarios: UserOption[];
  initialNumero?: string;
  initialCliente?: string;
  initialDisponibilizacao?: string;
  initialVencimento?: string;
  initialAcao?: string;
  djenPublicacaoId?: string;
};

export function NovoPrazoForm({
  usuarios,
  initialNumero = "",
  initialCliente = "",
  initialDisponibilizacao = "",
  initialVencimento = "",
  initialAcao = "",
  djenPublicacaoId,
}: NovoPrazoFormProps) {
  const [state, formAction, pending] = useActionState(createPrazo, initialState);
  const defaultResponsavel = usuarios[0]?.id ?? "";
  const [numeroProcesso, setNumeroProcesso] = useState(initialNumero);
  const [cliente, setCliente] = useState(initialCliente);
  const [dataDisponibilizacao, setDataDisponibilizacao] = useState(initialDisponibilizacao);
  const [dataVencimento, setDataVencimento] = useState(initialVencimento);
  const [numeroInvalido, setNumeroInvalido] = useState(false);
  const [processoCadastrado, setProcessoCadastrado] = useState(false);

  return (
    <form action={formAction} className="flex flex-col gap-5">
      {djenPublicacaoId ? (
        <input type="hidden" name="djen_publicacao_id" value={djenPublicacaoId} />
      ) : null}
      <div className="grid gap-5 sm:grid-cols-2">
        <NumeroProcessoField
          value={numeroProcesso}
          onChange={setNumeroProcesso}
          onInvalidChange={setNumeroInvalido}
          onCadastradoChange={setProcessoCadastrado}
          onClienteHint={(hint) =>
            setCliente((current) => current.trim() || hint)
          }
        />

        <label className="flex flex-col gap-1.5 text-sm sm:col-span-2">
          <span className="font-medium">Cliente</span>
          <input
            name="cliente"
            required
            value={cliente}
            onChange={(event) => setCliente(event.target.value)}
            className="h-11 w-full border border-border bg-background px-3 outline-none ring-primary focus:ring-2"
          />
        </label>
      </div>

      <ChecklistDraftField initialItems={initialAcao ? [initialAcao] : [""]} />

      <label className="flex flex-col gap-1.5 text-sm">
        <span className="font-medium">Data de disponibilização no diário</span>
        <input
          name="data_disponibilizacao"
          type="date"
          value={dataDisponibilizacao}
          onChange={(event) => setDataDisponibilizacao(event.target.value)}
          className="h-11 w-full max-w-xs border border-border bg-background px-3 outline-none ring-primary focus:ring-2"
        />
      </label>

      <CalculoDiasUteis
        defaultDataBase={dataDisponibilizacao}
        onVencimento={setDataVencimento}
      />

      <div className="grid gap-5 sm:grid-cols-2">
        <label className="flex flex-col gap-1.5 text-sm">
          <span className="font-medium text-primary">Data de vencimento</span>
          <input
            name="data_vencimento"
            type="date"
            required
            value={dataVencimento}
            onChange={(event) => setDataVencimento(event.target.value)}
            className="h-12 w-full border-2 border-primary bg-background px-3 text-base font-semibold outline-none ring-primary focus:ring-2"
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
            className="h-11 w-full border border-border bg-background px-3 outline-none ring-primary focus:ring-2 sm:h-12"
          >
            {usuarios.map((user) => (
              <option key={user.id} value={user.id}>
                {user.nome}
              </option>
            ))}
          </select>
          <span className="text-xs text-muted">
            O responsável recebe o alerta por e-mail se tiver a opção ativada em Usuários.
          </span>
        </label>
      </div>

      <AlertasDraftField />

      {state.error ? <p className="text-sm text-atrasado">{state.error}</p> : null}

      <div className="flex flex-col gap-3 sm:flex-row sm:justify-start">
        <Button
          type="submit"
          size="lg"
          disabled={pending || usuarios.length === 0 || numeroInvalido}
        >
          {pending
            ? "Salvando…"
            : processoCadastrado
              ? "Adicionar prazo ao processo"
              : "Salvar prazo"}
        </Button>
        <ButtonLink href="/dashboard" variant="secondary" size="lg">
          Cancelar
        </ButtonLink>
      </div>
    </form>
  );
}
