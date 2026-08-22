"use client";

import { useTransition } from "react";
import { useRouter } from "next/navigation";

import { ignorarPublicacaoDjen } from "@/app/djen/actions";
import { Button, ButtonLink } from "@/components/ui";
import { hasPermission, type User } from "@/lib/auth";
import { formatDjenDate, labelDjenStatus, type DjenPublicacao } from "@/lib/djen";

type DjenPublicacoesListProps = {
  items: DjenPublicacao[];
  user: User | null;
  emptyMessage?: string;
  compact?: boolean;
};

export function DjenPublicacoesList({
  items,
  user,
  emptyMessage = "Nenhuma publicação no DJEN.",
  compact = false,
}: DjenPublicacoesListProps) {
  const canCreate = hasPermission(user, "prazos_criar");

  if (items.length === 0) {
    return <p className="text-sm text-muted">{emptyMessage}</p>;
  }

  return (
    <ul className="space-y-2">
      {items.map((item) => (
        <DjenPublicacaoRow
          key={item.id}
          item={item}
          canCreate={canCreate}
          compact={compact}
        />
      ))}
    </ul>
  );
}

function DjenPublicacaoRow({
  item,
  canCreate,
  compact,
}: {
  item: DjenPublicacao;
  canCreate: boolean;
  compact: boolean;
}) {
  const router = useRouter();
  const [pending, startTransition] = useTransition();
  const cancelada = Boolean(item.motivo_cancelamento);
  const nova = item.status === "nova" && !cancelada;

  function ignorar() {
    startTransition(async () => {
      await ignorarPublicacaoDjen(item.id);
      router.refresh();
    });
  }

  const criarHref = `/prazos/novo?djen=${encodeURIComponent(item.id)}`;

  return (
    <li className="rounded-md border border-border bg-surface px-4 py-3">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-sm font-medium text-foreground">{item.tipo_comunicacao}</p>
          <p className="mt-0.5 text-xs text-muted">
            {[item.tribunal, item.tipo_documento, item.orgao].filter(Boolean).join(" · ")}
          </p>
        </div>
        <p className="shrink-0 text-xs font-medium text-primary">
          {labelDjenStatus(item.status, cancelada)}
        </p>
      </div>
      <p className="mt-2 text-sm text-foreground">
        {compact ? null : (
          <>
            {item.numero_processo}
            {item.cliente ? ` · ${item.cliente}` : ""}
            <br />
          </>
        )}
        Disponibilização: {formatDjenDate(item.data_disponibilizacao)}
        {item.vencimento_sugerido ? (
          <>
            {" "}
            · Vencimento sugerido: {formatDjenDate(item.vencimento_sugerido)}
          </>
        ) : null}
      </p>
      {canCreate && nova ? (
        <div className="mt-3 flex flex-col gap-2 sm:flex-row">
          <ButtonLink href={criarHref} size="sm" className="w-full sm:w-auto">
            Criar prazo
          </ButtonLink>
          <Button
            type="button"
            variant="secondary"
            size="sm"
            className="w-full sm:w-auto"
            disabled={pending}
            onClick={ignorar}
          >
            {pending ? "Ignorando…" : "Ignorar"}
          </Button>
        </div>
      ) : null}
      {item.processo_id && !compact ? (
        <p className="mt-2">
          <ButtonLink href={`/processos/${item.processo_id}`} variant="link" size="sm">
            Abrir ficha
          </ButtonLink>
        </p>
      ) : null}
    </li>
  );
}
