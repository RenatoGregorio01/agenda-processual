import Link from "next/link";

import { FILTROS, type FiltroPrazo } from "@/lib/prazos";
import { buildQuery } from "@/lib/query";

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
    <div className="flex justify-end gap-2 overflow-x-auto pb-1">
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
            className={
              active
                ? "whitespace-nowrap border border-primary bg-primary px-3 py-1.5 text-sm font-medium text-primary-foreground"
                : "whitespace-nowrap border border-border bg-surface px-3 py-1.5 text-sm text-muted transition hover:border-primary/40 hover:text-foreground"
            }
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
        className={
          rangeActive
            ? "whitespace-nowrap border border-primary bg-primary px-3 py-1.5 text-sm font-medium text-primary-foreground"
            : "whitespace-nowrap border border-border bg-surface px-3 py-1.5 text-sm text-muted transition hover:border-primary/40 hover:text-foreground"
        }
      >
        Período
      </Link>
    </div>
  );
}
