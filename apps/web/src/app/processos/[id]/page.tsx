import { notFound } from "next/navigation";

import { AppShell, PageContent, PageHeader } from "@/components/app-shell";
import { PrazoListItem } from "@/components/prazo-list-item";
import { AndamentosEmpty, ProcessoAndamentos } from "@/components/processo-andamentos";
import { ButtonLink, EmptyState, SectionHeading } from "@/components/ui";
import { apiFetch } from "@/lib/api-server";
import { formatAuditDate, labelAcao, type AuditLog } from "@/lib/auditoria";
import { hasPermission, type User } from "@/lib/auth";
import type { ProcessoDetail } from "@/lib/processos";

async function getCurrentUser(): Promise<User | null> {
  const response = await apiFetch("/api/v1/auth/me");
  if (!response.ok) return null;
  return (await response.json()) as User;
}

async function getProcesso(id: string): Promise<ProcessoDetail | null> {
  const response = await apiFetch(`/api/v1/processos/${id}`);
  if (response.status === 404) return null;
  if (!response.ok) return null;
  return (await response.json()) as ProcessoDetail;
}

export default async function ProcessoPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const [user, detail] = await Promise.all([getCurrentUser(), getProcesso(id)]);
  if (!detail) notFound();

  const { processo, prazos, historico, datajud } = detail;
  const ativos = prazos.filter((item) => !item.excluido_em);
  const excluidos = prazos.filter((item) => item.excluido_em);

  return (
    <AppShell user={user}>
      <PageHeader
        title={processo.numero_processo}
        description={
          <>
            <p className="text-base text-foreground">{processo.cliente}</p>
            <p className="mt-1">
              {ativos.length} prazo{ativos.length === 1 ? "" : "s"} ativo
              {ativos.length === 1 ? "" : "s"}
              {excluidos.length > 0 ? ` · ${excluidos.length} excluído(s)` : ""}
            </p>
          </>
        }
        actions={
          <>
            <ButtonLink href="/dashboard" variant="link" size="sm">
              ← Dashboard
            </ButtonLink>
            {hasPermission(user, "prazos_criar") ? (
              <ButtonLink
                href={`/prazos/novo?processo=${encodeURIComponent(processo.numero_processo)}&cliente=${encodeURIComponent(processo.cliente)}`}
              >
                + Novo prazo
              </ButtonLink>
            ) : null}
          </>
        }
      />

      <PageContent wide>
        <div className="grid gap-10 lg:grid-cols-5">
          <div className="lg:col-span-3">
            <SectionHeading>Prazos</SectionHeading>
            {ativos.length === 0 ? (
              <EmptyState>Nenhum prazo ativo neste processo.</EmptyState>
            ) : (
              <ul className="space-y-2">
                {ativos.map((prazo) => (
                  <PrazoListItem key={prazo.id} prazo={prazo} />
                ))}
              </ul>
            )}
            {excluidos.length > 0 ? (
              <div className="mt-8">
                <h3 className="mb-3 text-sm font-medium text-muted">Excluídos</h3>
                <ul className="space-y-2 opacity-70">
                  {excluidos.map((prazo) => (
                    <PrazoListItem key={prazo.id} prazo={prazo} />
                  ))}
                </ul>
              </div>
            ) : null}
          </div>

          <div className="space-y-8 lg:col-span-2">
            {datajud ? (
              <ProcessoAndamentos data={datajud} />
            ) : (
              <AndamentosEmpty message="Andamentos do tribunal ainda não foram consultados." />
            )}

            <section>
              <SectionHeading>Histórico</SectionHeading>
              {historico.length === 0 ? (
                <EmptyState>Ainda não há eventos registrados.</EmptyState>
              ) : (
                <ol className="space-y-3">
                  {historico.map((log) => (
                    <HistoricoItem key={log.id} log={log} />
                  ))}
                </ol>
              )}
            </section>
          </div>
        </div>
      </PageContent>
    </AppShell>
  );
}

function HistoricoItem({ log }: { log: AuditLog }) {
  return (
    <li className="rounded-md border border-border border-l-[3px] border-l-primary bg-surface px-4 py-3">
      <p className="text-sm font-semibold text-primary">{labelAcao(log.acao)}</p>
      <p className="mt-1 text-sm text-foreground">{log.resumo}</p>
      <p className="mt-1 text-xs text-muted">
        {log.usuario_nome} · {formatAuditDate(log.criado_em)}
      </p>
    </li>
  );
}
