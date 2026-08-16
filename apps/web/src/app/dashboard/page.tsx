import { Suspense } from "react";

import { AppShell, PageContent, PageHeader } from "@/components/app-shell";
import { DashboardPrazoList } from "@/components/dashboard-prazo-list";
import { DashboardTabs } from "@/components/dashboard-tabs";
import { ExportPautaButtons } from "@/components/export-pauta-buttons";
import { Stat } from "@/components/ui";
import { apiFetch } from "@/lib/api-server";
import type { User, UserOption } from "@/lib/auth";
import type { Prazo } from "@/lib/prazos";

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
  filtro: "atrasados" | "hoje" | "futuros" | "cumpridos",
): Promise<Prazo[]> {
  const response = await apiFetch(`/api/v1/prazos?filtro=${filtro}`);
  if (!response.ok) return [];
  return (await response.json()) as Prazo[];
}

export default async function DashboardPage() {
  const [user, atrasados, hoje, futuros, concluidos, usuarios] = await Promise.all([
    getCurrentUser(),
    listPrazos("atrasados"),
    listPrazos("hoje"),
    listPrazos("futuros"),
    listPrazos("cumpridos"),
    listUsuariosOpcoes(),
  ]);

  const todos = [...atrasados, ...hoje, ...futuros].sort((a, b) =>
    a.data_vencimento.localeCompare(b.data_vencimento),
  );
  const concluidosOrdenados = [...concluidos].sort((a, b) =>
    b.atualizado_em.localeCompare(a.atualizado_em),
  );

  return (
    <AppShell user={user}>
      <PageHeader
        title="Pauta"
        description="Vencimentos do escritório. A data é o que manda."
        actions={
          <ExportPautaButtons
            variant="menu"
            isAdmin={Boolean(user?.is_admin)}
            usuarios={usuarios}
          />
        }
      />

      <PageContent wide>
        <div className="mb-6 grid grid-cols-2 gap-2 lg:grid-cols-4">
          <Stat label="Atrasados" value={atrasados.length} tone="atrasado" />
          <Stat label="Vence hoje" value={hoje.length} tone="urgente" />
          <Stat label="Futuros" value={futuros.length} tone="muted" />
          <Stat label="Concluídos" value={concluidosOrdenados.length} tone="ok" />
        </div>

        <Suspense fallback={null}>
          <DashboardTabs
            counts={{
              futuros: futuros.length,
              hoje: hoje.length,
              atrasados: atrasados.length,
              todos: todos.length,
              concluidos: concluidosOrdenados.length,
            }}
            futuros={
              <DashboardPrazoList
                prazos={futuros}
                tone="no-prazo"
                emptyMessage="Nenhum vencimento futuro."
              />
            }
            hoje={
              <DashboardPrazoList
                prazos={hoje}
                tone="urgente"
                emptyMessage="Nada vence hoje."
              />
            }
            atrasados={
              <DashboardPrazoList
                prazos={atrasados}
                tone="atrasado"
                emptyMessage="Nenhum prazo atrasado."
              />
            }
            todos={
              <DashboardPrazoList
                prazos={todos}
                emptyMessage="Nenhum prazo pendente."
              />
            }
            concluidos={
              <DashboardPrazoList
                prazos={concluidosOrdenados}
                tone="cumprido"
                emptyMessage="Nenhum prazo concluído."
              />
            }
          />
        </Suspense>
      </PageContent>
    </AppShell>
  );
}
