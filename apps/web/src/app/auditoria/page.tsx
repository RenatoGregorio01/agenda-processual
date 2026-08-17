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
          <ul className="space-y-2">
            {logs.map((log) => (
              <li key={log.id}>
                <Card className="border-l-[3px] border-l-primary px-3 py-2.5">
                  <div className="flex items-baseline justify-between gap-3">
                    <p className="min-w-0 text-xs font-semibold uppercase tracking-wide text-primary">
                      {labelAcao(log.acao)}
                    </p>
                    <p className="shrink-0 text-[11px] text-muted">
                      {formatAuditDate(log.criado_em)}
                    </p>
                  </div>
                  <p className="mt-1 text-sm leading-snug text-foreground">{log.resumo}</p>
                  <div className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-muted">
                    <span className="min-w-0 truncate">
                      {log.usuario_nome} · {log.usuario_email}
                    </span>
                    {log.entidade === "prazo" && log.entidade_id ? (
                      <ButtonLink
                        href={`/prazos/${log.entidade_id}`}
                        variant="link"
                        size="sm"
                        className="h-auto p-0 text-xs font-medium"
                      >
                        Ver prazo
                      </ButtonLink>
                    ) : null}
                  </div>
                </Card>
              </li>
            ))}
          </ul>
        )}
      </PageContent>
    </AppShell>
  );
}
