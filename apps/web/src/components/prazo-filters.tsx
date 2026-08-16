import Link from "next/link";

import { FILTROS, type FiltroPrazo } from "@/lib/prazos";
import { buildQuery } from "@/lib/query";

function tabClass(active: boolean) {
  return active
    ? "-mb-px whitespace-nowrap border-b-2 border-primary px-4 py-2.5 text-sm font-semibold text-foreground"
    : "whitespace-nowrap px-4 py-2.5 text-sm text-muted transition hover:text-foreground";
}

export function PrazoFilters({
  current,
  responsavelId,
  q,
  dataInicio,
  dataFim,
  periodoOpen = false,
}: {
  current: FiltroPrazo;
  responsavelId?: string;
  q?: string;
  dataInicio?: string;
  dataFim?: string;
  periodoOpen?: boolean;
}) {
  const rangeActive = periodoOpen || Boolean(dataInicio || dataFim);

  return (
    <div
      className="scroll-x-touch flex gap-1 overflow-x-auto border-b border-border bg-surface/40 px-1"
      role="tablist"
      aria-label="Filtros de prazos"
    >
      {FILTROS.map((filtro) => {
        const active = !rangeActive && filtro.id === current;
        const href = `/prazos${buildQuery({
          filtro: filtro.id === "todos" ? undefined : filtro.id,
          responsavel_id: responsavelId,
          q,
        })}`;
        return (
          <Link
            key={filtro.id}
            href={href}
            role="tab"
            aria-selected={active}
            className={tabClass(active)}
          >
            {filtro.label}
          </Link>
        );
      })}
      <Link
        href={`/prazos${buildQuery({
          responsavel_id: responsavelId,
          q,
          data_inicio: dataInicio,
          data_fim: dataFim,
          periodo: "1",
        })}`}
        role="tab"
        aria-selected={rangeActive}
        className={tabClass(rangeActive)}
      >
        Período
      </Link>
    </div>
  );
}
