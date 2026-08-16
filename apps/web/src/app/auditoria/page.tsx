import { AppShell, PageContent, PageHeader } from "@/components/app-shell";
import { ButtonLink, Card, EmptyState } from "@/components/ui";
import { apiFetch } from "@/lib/api-server";
import { formatAuditDate, labelAcao, type AuditLog } from "@/lib/auditoria";
import { hasPermission, type User } from "@/lib/auth";

async function getCurrentUser(): Promise<User | null> {
  const response = await apiFetch("/api/v1/auth/me");
  if (!response.ok) return null;
  return (await response.json()) as User;
}

async function listAuditoria(): Promise<AuditLog[]> {
  const response = await apiFetch("/api/v1/auditoria?limit=200");
  if (!response.ok) return [];
  return (await response.json()) as AuditLog[];
}

export default async function AuditoriaPage() {
  const [user, logs] = await Promise.all([getCurrentUser(), listAuditoria()]);

  return (
    <AppShell user={user}>
      <PageHeader
        title="Auditoria"
        description={
          hasPermission(user, "auditoria_ver_tudo")
            ? "Visão completa: ações de todos os usuários."
            : "Você vê apenas as ações que você incluiu ou alterou."
        }
      />

      <PageContent>
        {logs.length === 0 ? (
          <EmptyState>
            Nenhuma ação registrada ainda. Login, criação e alterações de prazos aparecem aqui.
          </EmptyState>
        ) : (
          <ul className="space-y-3">
            {logs.map((log) => (
              <li key={log.id}>
                <Card className="border-l-[3px] border-l-primary px-4 py-4">
                  <div className="flex flex-wrap items-baseline justify-between gap-2">
                    <p className="text-sm font-semibold text-primary">{labelAcao(log.acao)}</p>
                    <p className="text-xs text-muted">{formatAuditDate(log.criado_em)}</p>
                  </div>
                  <p className="mt-2 text-foreground">{log.resumo}</p>
                  <p className="mt-1 text-sm text-muted">
                    {log.usuario_nome} · {log.usuario_email}
                  </p>
                  {log.entidade === "prazo" && log.entidade_id ? (
                    <ButtonLink
                      href={`/prazos/${log.entidade_id}`}
                      variant="link"
                      size="sm"
                      className="mt-2"
                    >
                      Ver prazo
                    </ButtonLink>
                  ) : null}
                </Card>
              </li>
            ))}
          </ul>
        )}
      </PageContent>
    </AppShell>
  );
}
