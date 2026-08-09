import Link from "next/link";

import { LogoutButton } from "@/components/logout-button";
import { PrazoBadge } from "@/components/prazo-badge";
import { PrazoFilters } from "@/components/prazo-filters";
import { apiFetch } from "@/lib/api-server";
import {
  FILTROS,
  formatVencimento,
  getUrgencyBadge,
  type FiltroPrazo,
  type Prazo,
} from "@/lib/prazos";

async function listPrazos(filtro: FiltroPrazo): Promise<Prazo[]> {
  const query = filtro === "todos" ? "" : `?filtro=${filtro}`;
  const response = await apiFetch(`/api/v1/prazos${query}`);
  if (!response.ok) {
    return [];
  }
  return (await response.json()) as Prazo[];
}

function resolveFiltro(value?: string): FiltroPrazo {
  const found = FILTROS.find((item) => item.id === value);
  return found?.id ?? "todos";
}

export default async function PrazosPage({
  searchParams,
}: {
  searchParams: Promise<{ filtro?: string }>;
}) {
  const params = await searchParams;
  const filtro = resolveFiltro(params.filtro);
  const prazos = await listPrazos(filtro);

  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col px-6 py-10 sm:px-10">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="font-[family-name:var(--font-display)] text-2xl font-semibold text-primary">
            Agenda Processual
          </p>
          <h1 className="mt-5 text-3xl font-semibold tracking-tight text-foreground">Prazos</h1>
          <p className="mt-2 text-muted">Ordenados por vencimento</p>
        </div>
        <div className="flex flex-col items-end gap-3">
          <LogoutButton />
          <div className="flex flex-wrap justify-end gap-2">
            <Link
              href="/auditoria"
              className="inline-flex h-11 items-center justify-center border border-border bg-surface px-4 text-sm font-medium"
            >
              Auditoria
            </Link>
            <Link
              href="/prazos/novo"
              className="inline-flex h-11 items-center justify-center bg-primary px-4 text-sm font-semibold text-primary-foreground transition hover:brightness-110"
            >
              Novo prazo
            </Link>
          </div>
        </div>
      </div>

      <div className="mt-8">
        <PrazoFilters current={filtro} />
      </div>

      {prazos.length === 0 ? (
        <p className="mt-12 max-w-md text-muted">
          {filtro === "excluidos"
            ? "Nenhum prazo excluído. Itens removidos ficam aqui para restauração."
            : "Nenhum prazo por enquanto. Cadastre o primeiro para sair do memoriômetro."}
        </p>
      ) : (
        <ul className="mt-8 divide-y divide-border border-y border-border">
          {prazos.map((prazo) => {
            const badge = getUrgencyBadge(prazo);
            return (
              <li key={prazo.id}>
                <Link
                  href={`/prazos/${prazo.id}`}
                  className="block py-5 transition hover:bg-surface/80"
                >
                  <p className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
                    {formatVencimento(prazo.data_vencimento)}
                  </p>
                  <div className="mt-2">
                    <PrazoBadge badge={badge} />
                  </div>
                  <p className="mt-3 text-lg font-medium text-foreground">{prazo.acao}</p>
                  <p className="mt-1 text-sm text-muted">
                    {prazo.numero_processo} · {prazo.cliente} · {prazo.responsavel}
                  </p>
                </Link>
              </li>
            );
          })}
        </ul>
      )}
    </main>
  );
}
