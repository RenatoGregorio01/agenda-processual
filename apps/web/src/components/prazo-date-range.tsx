import Link from "next/link";

import { buildQuery } from "@/lib/query";

type PrazoDateRangeProps = {
  dataInicio?: string;
  dataFim?: string;
  responsavelId?: string;
  q?: string;
  open?: boolean;
};

export function PrazoDateRange({
  dataInicio,
  dataFim,
  responsavelId,
  q,
  open = false,
}: PrazoDateRangeProps) {
  if (!open && !dataInicio && !dataFim) {
    return null;
  }

  const clearHref = `/prazos${buildQuery({
    responsavel_id: responsavelId,
    q,
  })}`;

  return (
    <form
      action="/prazos"
      method="get"
      className="flex flex-col gap-3 border border-border bg-surface p-4 sm:flex-row sm:flex-wrap sm:items-end"
    >
      {responsavelId ? (
        <input type="hidden" name="responsavel_id" value={responsavelId} />
      ) : null}
      {q ? <input type="hidden" name="q" value={q} /> : null}
      <input type="hidden" name="periodo" value="1" />

      <label className="flex min-w-0 flex-1 flex-col gap-1.5 text-sm sm:max-w-[11rem]">
        <span className="font-medium text-foreground">De</span>
        <input
          type="date"
          name="data_inicio"
          defaultValue={dataInicio ?? ""}
          required
          className="h-11 border border-border bg-background px-3 outline-none ring-primary focus:ring-2"
        />
      </label>
      <label className="flex min-w-0 flex-1 flex-col gap-1.5 text-sm sm:max-w-[11rem]">
        <span className="font-medium text-foreground">Até</span>
        <input
          type="date"
          name="data_fim"
          defaultValue={dataFim ?? ""}
          required
          className="h-11 border border-border bg-background px-3 outline-none ring-primary focus:ring-2"
        />
      </label>
      <div className="flex gap-2">
        <button
          type="submit"
          className="inline-flex h-11 items-center justify-center bg-primary px-4 text-sm font-semibold text-primary-foreground"
        >
          Aplicar
        </button>
        {dataInicio || dataFim ? (
          <Link
            href={clearHref}
            className="inline-flex h-11 items-center justify-center border border-border bg-background px-4 text-sm text-muted"
          >
            Limpar
          </Link>
        ) : null}
      </div>
    </form>
  );
}
