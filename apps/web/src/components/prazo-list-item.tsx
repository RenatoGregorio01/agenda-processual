import Link from "next/link";

import { PrazoBadge } from "@/components/prazo-badge";
import { Card } from "@/components/ui";
import { formatVencimentoParts, getUrgencyBadge, type Prazo } from "@/lib/prazos";

const cardTone = {
  atrasado: "atrasado",
  urgente: "urgente",
  "no-prazo": "no-prazo",
  cumprido: "cumprido",
  neutro: "default",
} as const;

export function PrazoListItem({ prazo }: { prazo: Prazo }) {
  const badge = getUrgencyBadge(prazo);
  const parts = formatVencimentoParts(prazo.data_vencimento);

  return (
    <li>
      <Link href={`/prazos/${prazo.id}`} className="block">
        <Card tone={cardTone[badge.tone]} className="transition hover:bg-[#fbfaf7]">
          <div className="flex items-center justify-between gap-3 px-3 py-2.5">
            <div className="flex min-w-0 items-baseline gap-2">
              <p className="font-[family-name:var(--font-display)] text-2xl font-semibold leading-none tracking-tight text-foreground">
                {parts.day}
              </p>
              <p className="text-[10px] font-medium uppercase tracking-wide text-muted">
                {parts.monthYear}
              </p>
            </div>
            <PrazoBadge badge={badge} />
          </div>
          <div className="border-t border-border px-3 py-2">
            <p className="truncate text-sm font-semibold text-foreground">{prazo.acao}</p>
            <p className="mt-0.5 truncate text-xs text-muted">
              Proc. {prazo.numero_processo} · {prazo.cliente} · {prazo.responsavel}
            </p>
          </div>
        </Card>
      </Link>
    </li>
  );
}
