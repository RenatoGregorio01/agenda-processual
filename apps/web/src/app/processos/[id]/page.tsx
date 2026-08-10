import Link from "next/link";
import { notFound } from "next/navigation";

import { PrazoBadge } from "@/components/prazo-badge";
import { apiFetch } from "@/lib/api-server";
import { formatAuditDate, labelAcao, type AuditLog } from "@/lib/auditoria";
import { hasPermission, type User } from "@/lib/auth";
import {
  formatVencimento,
  getUrgencyBadge,
  type Prazo,
} from "@/lib/prazos";
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

  const { processo, prazos, historico } = detail;
  const ativos = prazos.filter((item) => !item.excluido_em);
  const excluidos = prazos.filter((item) => item.excluido_em);

  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col px-6 py-10 sm:px-10">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <Link
            href="/prazos"
            className="text-sm text-muted underline-offset-4 hover:underline"
          >
            ← Voltar para prazos
          </Link>
          <p className="mt-5 font-[family-name:var(--font-display)] text-2xl font-semibold text-primary">
            Agenda Processual
          </p>
          <h1 className="mt-3 text-3xl font-semibold tracking-tight text-foreground">
            {processo.numero_processo}
          </h1>
          <p className="mt-2 text-muted">{processo.cliente}</p>
          <p className="mt-1 text-sm text-muted">
            {ativos.length} prazo{ativos.length === 1 ? "" : "s"} ativo
            {ativos.length === 1 ? "" : "s"}
            {excluidos.length > 0 ? ` · ${excluidos.length} excluído(s)` : ""}
          </p>
        </div>
        {hasPermission(user, "prazos_criar") ? (
          <Link
            href={`/prazos/novo?processo=${encodeURIComponent(processo.numero_processo)}&cliente=${encodeURIComponent(processo.cliente)}`}
            className="inline-flex h-11 items-center justify-center bg-primary px-4 text-sm font-semibold text-primary-foreground transition hover:brightness-110"
          >
            Novo prazo neste processo
          </Link>
        ) : null}
      </div>

      <section className="mt-10">
        <h2 className="text-lg font-semibold text-foreground">Prazos</h2>
        {ativos.length === 0 ? (
          <p className="mt-4 text-sm text-muted">Nenhum prazo ativo neste processo.</p>
        ) : (
          <ul className="mt-4 divide-y divide-border border-y border-border">
            {ativos.map((prazo) => (
              <PrazoLinha key={prazo.id} prazo={prazo} />
            ))}
          </ul>
        )}
        {excluidos.length > 0 ? (
          <div className="mt-8">
            <h3 className="text-sm font-medium text-muted">Excluídos</h3>
            <ul className="mt-3 divide-y divide-border border-y border-border opacity-70">
              {excluidos.map((prazo) => (
                <PrazoLinha key={prazo.id} prazo={prazo} />
              ))}
            </ul>
          </div>
        ) : null}
      </section>

      <section className="mt-12">
        <h2 className="text-lg font-semibold text-foreground">Histórico</h2>
        {historico.length === 0 ? (
          <p className="mt-4 text-sm text-muted">Ainda não há eventos registrados.</p>
        ) : (
          <ol className="mt-4 space-y-4">
            {historico.map((log) => (
              <HistoricoItem key={log.id} log={log} />
            ))}
          </ol>
        )}
      </section>
    </main>
  );
}

function PrazoLinha({ prazo }: { prazo: Prazo }) {
  const badge = getUrgencyBadge(prazo);
  return (
    <li>
      <Link href={`/prazos/${prazo.id}`} className="block py-4 transition hover:bg-surface/80">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <p className="text-xl font-bold tracking-tight text-foreground">
            {formatVencimento(prazo.data_vencimento)}
          </p>
          <PrazoBadge badge={badge} />
        </div>
        <p className="mt-2 font-medium text-foreground">{prazo.acao}</p>
        <p className="mt-1 text-sm text-muted">{prazo.responsavel}</p>
      </Link>
    </li>
  );
}

function HistoricoItem({ log }: { log: AuditLog }) {
  return (
    <li className="border-l-2 border-border pl-4">
      <p className="text-sm font-semibold text-primary">{labelAcao(log.acao)}</p>
      <p className="mt-1 text-sm text-foreground">{log.resumo}</p>
      <p className="mt-1 text-xs text-muted">
        {log.usuario_nome} · {formatAuditDate(log.criado_em)}
      </p>
    </li>
  );
}
