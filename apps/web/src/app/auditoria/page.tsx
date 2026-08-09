import Link from "next/link";

import { LogoutButton } from "@/components/logout-button";
import { apiFetch } from "@/lib/api-server";
import { formatAuditDate, labelAcao, type AuditLog } from "@/lib/auditoria";
import type { User } from "@/lib/auth";

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
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col px-6 py-10 sm:px-10">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="font-[family-name:var(--font-display)] text-2xl font-semibold text-primary">
            Agenda Processual
          </p>
          <h1 className="mt-5 text-3xl font-semibold tracking-tight text-foreground">
            Auditoria
          </h1>
          <p className="mt-2 text-muted">
            {user?.is_admin
              ? "Visão administrativa: ações de todos os usuários."
              : "Você vê apenas as ações que você incluiu ou alterou."}
          </p>
        </div>
        <div className="flex flex-col items-end gap-3">
          <LogoutButton />
          <Link
            href="/prazos"
            className="inline-flex h-11 items-center justify-center border border-border bg-surface px-4 text-sm font-medium"
          >
            Voltar aos prazos
          </Link>
        </div>
      </div>

      {logs.length === 0 ? (
        <p className="mt-12 max-w-md text-muted">
          Nenhuma ação registrada ainda. Login, criação e alterações de prazos aparecem aqui.
        </p>
      ) : (
        <ul className="mt-8 divide-y divide-border border-y border-border">
          {logs.map((log) => (
            <li key={log.id} className="py-4">
              <div className="flex flex-wrap items-baseline justify-between gap-2">
                <p className="text-sm font-semibold text-primary">{labelAcao(log.acao)}</p>
                <p className="text-xs text-muted">{formatAuditDate(log.criado_em)}</p>
              </div>
              <p className="mt-2 text-foreground">{log.resumo}</p>
              <p className="mt-1 text-sm text-muted">
                {log.usuario_nome} · {log.usuario_email}
              </p>
              {log.entidade === "prazo" && log.entidade_id ? (
                <Link
                  href={`/prazos/${log.entidade_id}`}
                  className="mt-2 inline-block text-sm text-primary underline-offset-4 hover:underline"
                >
                  Ver prazo
                </Link>
              ) : null}
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
