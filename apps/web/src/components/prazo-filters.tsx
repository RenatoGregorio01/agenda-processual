import Link from "next/link";

import { FILTROS, type FiltroPrazo } from "@/lib/prazos";

export function PrazoFilters({ current }: { current: FiltroPrazo }) {
  return (
    <div className="flex gap-2 overflow-x-auto pb-1">
      {FILTROS.map((filtro) => {
        const active = filtro.id === current;
        return (
          <Link
            key={filtro.id}
            href={filtro.id === "todos" ? "/prazos" : `/prazos?filtro=${filtro.id}`}
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
    </div>
  );
}
