import Link from "next/link";

import { LogoutButton } from "@/components/logout-button";
import { PrazoFilters } from "@/components/prazo-filters";
import { PrazoListItem } from "@/components/prazo-list-item";
import { PrazoSearch } from "@/components/prazo-search";
import { ResponsavelFilter } from "@/components/responsavel-filter";
import { apiFetch } from "@/lib/api-server";
import { hasPermission, type User, type UserOption } from "@/lib/auth";
import { FILTROS, type FiltroPrazo, type Prazo } from "@/lib/prazos";
import { buildQuery } from "@/lib/query";

async function getCurrentUser(): Promise<User | null> {
  const response = await apiFetch("/api/v1/auth/me");
  if (!response.ok) return null;
  return (await response.json()) as User;
}

async function listUsuariosOpcoes(): Promise<UserOption[]> {
  const response = await apiFetch("/api/v1/usuarios/opcoes");
  if (!response.ok) return [];
  return (await response.json()) as UserOption[];
}

async function listPrazos(
  filtro: FiltroPrazo,
  responsavelId?: string,
  q?: string,
): Promise<Prazo[]> {
  const query = buildQuery({
    filtro: filtro === "todos" ? undefined : filtro,
    responsavel_id: responsavelId,
    q,
  });
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
  searchParams: Promise<{ filtro?: string; responsavel_id?: string; q?: string }>;
}) {
  const params = await searchParams;
  const filtro = resolveFiltro(params.filtro);
  const responsavelId = params.responsavel_id || undefined;
  const q = params.q?.trim() || undefined;
  const [user, usuarios, prazos] = await Promise.all([
    getCurrentUser(),
    listUsuariosOpcoes(),
    listPrazos(filtro, responsavelId, q),
  ]);

  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col px-6 py-10 sm:px-10">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="font-[family-name:var(--font-display)] text-2xl font-semibold text-primary">
            Agenda Processual
          </p>
          <h1 className="mt-5 text-3xl font-semibold tracking-tight text-foreground">Prazos</h1>
          <p className="mt-2 text-muted">
            {q
              ? `Resultados para “${q}” · ${prazos.length} encontrado${prazos.length === 1 ? "" : "s"}`
              : "Ordenados por vencimento"}
          </p>
        </div>
        <div className="flex flex-col items-end gap-3">
          <LogoutButton />
          <div className="flex flex-wrap justify-end gap-2">
            <Link
              href={`/dashboard${buildQuery({ responsavel_id: responsavelId })}`}
              className="inline-flex h-11 items-center justify-center border border-border bg-surface px-4 text-sm font-medium"
            >
              Hoje
            </Link>
            {hasPermission(user, "usuarios_gerenciar") ? (
              <Link
                href="/usuarios"
                className="inline-flex h-11 items-center justify-center border border-border bg-surface px-4 text-sm font-medium"
              >
                Usuários
              </Link>
            ) : null}
            <Link
              href="/auditoria"
              className="inline-flex h-11 items-center justify-center border border-border bg-surface px-4 text-sm font-medium"
            >
              Auditoria
            </Link>
            {hasPermission(user, "prazos_criar") ? (
              <Link
                href="/prazos/novo"
                className="inline-flex h-11 items-center justify-center bg-primary px-4 text-sm font-semibold text-primary-foreground transition hover:brightness-110"
              >
                Novo prazo
              </Link>
            ) : null}
          </div>
        </div>
      </div>

      <div className="mt-8 space-y-4">
        <PrazoSearch q={q} filtro={filtro} responsavelId={responsavelId} />
        <PrazoFilters current={filtro} responsavelId={responsavelId} q={q} />
        <ResponsavelFilter
          basePath="/prazos"
          usuarios={usuarios}
          currentUserId={user?.id}
          currentResponsavelId={responsavelId}
          extraParams={{
            filtro: filtro === "todos" ? undefined : filtro,
            q,
          }}
        />
      </div>

      {prazos.length === 0 ? (
        <p className="mt-12 max-w-md text-muted">
          {q
            ? "Nenhum prazo encontrado para essa busca."
            : filtro === "excluidos"
              ? "Nenhum prazo excluído. Itens removidos ficam aqui para restauração."
              : responsavelId
                ? "Nenhum prazo para este responsável com o filtro atual."
                : "Nenhum prazo por enquanto. Cadastre o primeiro para sair do memoriômetro."}
        </p>
      ) : (
        <ul className="mt-8 divide-y divide-border border-y border-border">
          {prazos.map((prazo) => (
            <PrazoListItem key={prazo.id} prazo={prazo} />
          ))}
        </ul>
      )}
    </main>
  );
}
