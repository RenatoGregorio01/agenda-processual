import Link from "next/link";

import { PrazoBadge } from "@/components/prazo-badge";
import { formatVencimento, getUrgencyBadge, type Prazo } from "@/lib/prazos";

export function PrazoListItem({ prazo }: { prazo: Prazo }) {
  const badge = getUrgencyBadge(prazo);

  return (
    <li>
      <Link href={`/prazos/${prazo.id}`} className="block py-5 transition hover:bg-surface/80">
        <p className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
          {formatVencimento(prazo.data_vencimento)}
        </p>
        <div className="mt-2">
          <PrazoBadge badge={badge} />
        </div>
        <p className="mt-3 text-lg font-medium text-foreground">{prazo.acao}</p>
        <p className="mt-1 text-sm text-muted">
          {prazo.processo_id ? (
            <>
              <span className="text-primary">{prazo.numero_processo}</span>
              {" · "}
            </>
          ) : (
            <>{prazo.numero_processo} · </>
          )}
          {prazo.cliente} · {prazo.responsavel}
        </p>
      </Link>
    </li>
  );
}
