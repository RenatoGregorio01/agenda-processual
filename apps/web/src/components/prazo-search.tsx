import Link from "next/link";

import { buildQuery } from "@/lib/query";

type PrazoSearchProps = {
  q?: string;
  filtro?: string;
  responsavelId?: string;
};

export function PrazoSearch({ q, filtro, responsavelId }: PrazoSearchProps) {
  const clearHref = `/prazos${buildQuery({
    filtro: filtro && filtro !== "todos" ? filtro : undefined,
    responsavel_id: responsavelId,
  })}`;

  return (
    <form action="/prazos" method="get" className="flex flex-col gap-2 sm:flex-row sm:items-end">
      {filtro && filtro !== "todos" ? <input type="hidden" name="filtro" value={filtro} /> : null}
      {responsavelId ? (
        <input type="hidden" name="responsavel_id" value={responsavelId} />
      ) : null}
      <label className="flex min-w-0 flex-1 flex-col gap-1.5 text-sm">
        <span className="font-medium text-foreground">Buscar</span>
        <input
          name="q"
          type="search"
          defaultValue={q ?? ""}
          placeholder="Processo, cliente, ação ou responsável"
          className="h-10 border border-border bg-background px-3 outline-none ring-primary focus:ring-2"
        />
      </label>
      <div className="flex gap-2">
        <button
          type="submit"
          className="inline-flex h-10 items-center justify-center bg-primary px-4 text-sm font-semibold text-primary-foreground transition hover:brightness-110"
        >
          Buscar
        </button>
        {q ? (
          <Link
            href={clearHref}
            className="inline-flex h-10 items-center justify-center border border-border bg-surface px-4 text-sm text-muted"
          >
            Limpar
          </Link>
        ) : null}
      </div>
    </form>
  );
}
