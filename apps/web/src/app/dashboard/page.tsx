import Link from "next/link";

import { DashboardSection } from "@/components/dashboard-section";
import { LogoutButton } from "@/components/logout-button";
import { ResponsavelFilter } from "@/components/responsavel-filter";
import { apiFetch } from "@/lib/api-server";
import { hasPermission, type User, type UserOption } from "@/lib/auth";
import type { Prazo } from "@/lib/prazos";
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
  filtro: "atrasados" | "hoje" | "amanha",
  responsavelId?: string,
): Promise<Prazo[]> {
  const query = buildQuery({
    filtro,
    responsavel_id: responsavelId,
  });
  const response = await apiFetch(`/api/v1/prazos${query}`);
  if (!response.ok) return [];
  return (await response.json()) as Prazo[];
}

export default async function DashboardPage({
  searchParams,
}: {
  searchParams: Promise<{ responsavel_id?: string }>;
}) {
  const params = await searchParams;
  const responsavelId = params.responsavel_id || undefined;

  const [user, usuarios, atrasados, hoje, amanha] = await Promise.all([
    getCurrentUser(),
    listUsuariosOpcoes(),
    listPrazos("atrasados", responsavelId),
    listPrazos("hoje", responsavelId),
    listPrazos("amanha", responsavelId),
  ]);

  const totalUrgente = atrasados.length + hoje.length + amanha.length;
  const responsavelNome = usuarios.find((item) => item.id === responsavelId)?.nome;

  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col px-6 py-10 sm:px-10">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="font-[family-name:var(--font-display)] text-2xl font-semibold text-primary">
            Agenda Processual
          </p>
          <h1 className="mt-5 text-3xl font-semibold tracking-tight text-foreground">Hoje</h1>
          <p className="mt-2 text-muted">
            {totalUrgente === 0
              ? responsavelNome
                ? `Nenhum prazo urgente para ${responsavelNome}.`
                : "Nenhum prazo urgente no momento."
              : responsavelNome
                ? `${responsavelNome}: ${totalUrgente} prazo${totalUrgente === 1 ? "" : "s"} pedindo atenção.`
                : `${totalUrgente} prazo${totalUrgente === 1 ? "" : "s"} pedindo atenção.`}
          </p>
        </div>
        <div className="flex flex-col items-end gap-3">
          <LogoutButton />
          <div className="flex flex-wrap justify-end gap-2">
            <Link
              href={`/prazos${buildQuery({ responsavel_id: responsavelId })}`}
              className="inline-flex h-11 items-center justify-center border border-border bg-surface px-4 text-sm font-medium"
            >
              Todos os prazos
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

      <div className="mt-8">
        <ResponsavelFilter
          basePath="/dashboard"
          usuarios={usuarios}
          currentUserId={user?.id}
          currentResponsavelId={responsavelId}
        />
      </div>

      <DashboardSection
        title="Atrasados"
        description="Vencidos e ainda pendentes"
        emptyMessage="Nenhum prazo atrasado."
        prazos={atrasados}
        accent="atrasado"
      />

      <DashboardSection
        title="Vence hoje"
        description="Protocolar ainda hoje"
        emptyMessage="Nada vence hoje."
        prazos={hoje}
        accent="urgente"
      />

      <DashboardSection
        title="Vence amanhã"
        description="Preparar para o protocolo"
        emptyMessage="Nada vence amanhã."
        prazos={amanha}
        accent="urgente"
      />
    </main>
  );
}
