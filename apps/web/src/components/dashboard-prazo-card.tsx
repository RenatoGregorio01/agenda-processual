import Link from "next/link";

import { Badge, Card } from "@/components/ui";
import { formatVencimentoParts, type Prazo } from "@/lib/prazos";

type ColumnTone = "atrasado" | "urgente" | "no-prazo" | "cumprido";

const toneLabel: Record<ColumnTone, string> = {
  atrasado: "ATRASADO",
  urgente: "URGENTE",
  "no-prazo": "NO PRAZO",
  cumprido: "CUMPRIDO",
};

export function DashboardPrazoCard({
  prazo,
  tone,
}: {
  prazo: Prazo;
  tone: ColumnTone;
}) {
  const parts = formatVencimentoParts(prazo.data_vencimento);

  return (
    <Link href={`/prazos/${prazo.id}`} className="block">
      <Card tone={tone} className="transition hover:bg-[#fbfaf7]">
        <div className="flex items-center justify-between gap-3 px-3 py-2.5">
          <div className="flex min-w-0 items-baseline gap-2">
            <p className="font-[family-name:var(--font-display)] text-xl font-semibold leading-none tracking-tight text-foreground sm:text-2xl">
              {parts.day}
            </p>
            <p className="text-[10px] font-medium uppercase tracking-wide text-muted">
              {parts.monthYear}
            </p>
          </div>
          <Badge tone={tone}>{toneLabel[tone]}</Badge>
        </div>
        <div className="border-t border-border px-3 py-2">
          <p className="text-sm font-semibold leading-snug text-foreground">{prazo.acao}</p>
          <p className="mt-1 break-all text-xs text-muted sm:truncate sm:break-normal">
            <span className="sm:hidden">
              {prazo.numero_processo}
              <br />
              {prazo.cliente} · {prazo.responsavel}
            </span>
            <span className="hidden sm:inline">
              Proc. {prazo.numero_processo} · {prazo.cliente} · {prazo.responsavel}
            </span>
          </p>
        </div>
      </Card>
    </Link>
  );
}
