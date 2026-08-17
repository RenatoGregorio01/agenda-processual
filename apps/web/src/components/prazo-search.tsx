import Link from "next/link";
import type { ReactNode } from "react";

import { buildQuery } from "@/lib/query";

type PrazoSearchProps = {
  q?: string;
  filtro?: string;
  responsavelId?: string;
  dataInicio?: string;
  dataFim?: string;
  /** Ação à direita da busca (ex.: Novo prazo). */
  trailing?: ReactNode;
};

export function PrazoSearch({
  q,
  filtro,
  responsavelId,
  dataInicio,
  dataFim,
  trailing,
}: PrazoSearchProps) {
  const clearHref = `/prazos${buildQuery({
    filtro: filtro && filtro !== "todos" ? filtro : undefined,
    responsavel_id: responsavelId,
    data_inicio: dataInicio,
    data_fim: dataFim,
  })}`;

  return (
    <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
      <form
        action="/prazos"
        method="get"
        className="flex min-w-0 flex-1 flex-col gap-2 sm:flex-row sm:items-center"
      >
        {filtro && filtro !== "todos" && !dataInicio && !dataFim ? (
          <input type="hidden" name="filtro" value={filtro} />
        ) : null}
        {responsavelId ? (
          <input type="hidden" name="responsavel_id" value={responsavelId} />
        ) : null}
        {dataInicio ? <input type="hidden" name="data_inicio" value={dataInicio} /> : null}
        {dataFim ? <input type="hidden" name="data_fim" value={dataFim} /> : null}
        <div className="relative min-w-0 flex-1">
          <span className="pointer-events-none absolute inset-y-0 left-3 flex items-center text-muted">
            <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" aria-hidden>
              <circle cx="11" cy="11" r="6.5" stroke="currentColor" strokeWidth="1.6" />
              <path d="M16 16l4 4" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
            </svg>
          </span>
          <input
            name="q"
            type="search"
            defaultValue={q ?? ""}
            placeholder="Buscar processo, cliente, ação..."
            className="h-11 w-full border border-border bg-surface pl-9 pr-3 text-sm outline-none ring-primary focus:ring-2"
          />
        </div>
        <div className="flex gap-2">
          <button
            type="submit"
            className="inline-flex h-11 flex-1 items-center justify-center bg-primary px-4 text-sm font-semibold text-primary-foreground sm:flex-none"
          >
            Buscar
          </button>
          {q ? (
            <Link
              href={clearHref}
              className="inline-flex h-11 items-center justify-center border border-border bg-surface px-4 text-sm text-muted"
            >
              Limpar
            </Link>
          ) : null}
        </div>
      </form>
      {trailing ? <div className="flex shrink-0 sm:items-center">{trailing}</div> : null}
    </div>
  );
}
