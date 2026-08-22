import Link from "next/link";
import { notFound } from "next/navigation";

import { cumprirPrazo } from "@/app/prazos/actions";
import { AppShell, PageContent, PageHeader } from "@/components/app-shell";
import { ExcluirPrazoButton } from "@/components/excluir-prazo-button";
import { PrazoAlertasEditor } from "@/components/prazo-alertas-editor";
import { PrazoBadge } from "@/components/prazo-badge";
import { PrazoChecklist } from "@/components/prazo-checklist";
import { AndamentosEmpty, ProcessoAndamentos } from "@/components/processo-andamentos";
import { RestaurarPrazoButton } from "@/components/restaurar-prazo-button";
import { Button, ButtonLink, Card } from "@/components/ui";
import { apiFetch } from "@/lib/api-server";
import { hasPermission, type User } from "@/lib/auth";
import { tituloFromChecklist, type ChecklistItem } from "@/lib/checklist";
import {
  formatVencimentoLongo,
  getUrgencyBadge,
  type Prazo,
} from "@/lib/prazos";
import type { DatajudSync } from "@/lib/processos";

async function getCurrentUser(): Promise<User | null> {
  const response = await apiFetch("/api/v1/auth/me");
  if (!response.ok) return null;
  return (await response.json()) as User;
}

async function getPrazo(id: string): Promise<Prazo | null> {
  const response = await apiFetch(`/api/v1/prazos/${id}`);
  if (response.status === 404) return null;
  if (!response.ok) return null;
  return (await response.json()) as Prazo;
}

async function listChecklist(prazoId: string): Promise<ChecklistItem[]> {
  const response = await apiFetch(`/api/v1/prazos/${prazoId}/checklist`);
  if (!response.ok) return [];
  return (await response.json()) as ChecklistItem[];
}

async function getAndamentosSalvos(processoId: string): Promise<DatajudSync | null> {
  const response = await apiFetch(`/api/v1/processos/${processoId}`);
  if (!response.ok) return null;
  const body = (await response.json()) as { datajud?: DatajudSync };
  return body.datajud ?? null;
}

async function syncAndamentos(processoId: string): Promise<DatajudSync | null> {
  const response = await apiFetch(
    `/api/v1/processos/${processoId}/datajud/sync?force=true`,
    {
      method: "POST",
    },
  );
  if (response.ok) {
    return (await response.json()) as DatajudSync;
  }
  // Se a sync falhar, ainda exibe andamentos já gravados na ficha.
  return getAndamentosSalvos(processoId);
}

export default async function PrazoDetalhePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const [user, prazo] = await Promise.all([getCurrentUser(), getPrazo(id)]);
  if (!prazo) notFound();

  const [checklist, datajud] = await Promise.all([
    listChecklist(prazo.id),
    prazo.processo_id ? syncAndamentos(prazo.processo_id) : Promise.resolve(null),
  ]);
  const titulo = tituloFromChecklist(checklist) ?? prazo.acao;
  const badge = getUrgencyBadge(prazo);
  const isExcluded = Boolean(prazo.excluido_em);
  const cumprir = cumprirPrazo.bind(null, prazo.id);
  const canEditChecklist = !isExcluded && hasPermission(user, "prazos_alterar");

  return (
    <AppShell user={user}>
      <PageHeader
        title="Detalhes do Prazo"
        actions={
          <ButtonLink href="/dashboard" variant="link" size="sm">
            ← Voltar ao dashboard
          </ButtonLink>
        }
      />

      <PageContent>
        <Card className="px-4 py-3">
          <div className="flex items-center justify-between gap-3">
            <h2 className="min-w-0 text-base font-semibold tracking-tight text-foreground sm:text-lg">
              <span className="font-medium uppercase tracking-wide text-muted">Vence em </span>
              <span className="font-[family-name:var(--font-display)]">
                {formatVencimentoLongo(prazo.data_vencimento)}
              </span>
            </h2>
            <div className="shrink-0">
              <PrazoBadge badge={badge} />
            </div>
          </div>
        </Card>

        <section className="mt-5">
          <h3 className="text-lg font-semibold text-foreground">{titulo}</h3>
          <p className="mt-1 text-sm text-muted">
            {isExcluded
              ? "Este prazo foi excluído e pode ser restaurado."
              : badge.label === "ATRASADO"
                ? "Prazo vencido. Protocolar o quanto antes."
                : badge.label === "AMANHÃ" || badge.label === "HOJE"
                  ? `${badge.label === "HOJE" ? "Hoje" : "Amanhã"} vence. Protocolar no prazo.`
                  : "Acompanhe o vencimento e a ação necessária."}
          </p>
        </section>

        <Card className="mt-5 p-4 text-sm">
          <dl className="grid grid-cols-[minmax(7rem,auto)_1fr] items-baseline gap-x-4 gap-y-2">
            <dt className="text-muted">Processo</dt>
            <dd className="min-w-0 font-medium">
              {prazo.processo_id ? (
                <Link
                  href={`/processos/${prazo.processo_id}`}
                  className="text-primary underline-offset-4 hover:underline"
                >
                  {prazo.numero_processo}
                </Link>
              ) : (
                prazo.numero_processo
              )}
            </dd>
            <dt className="text-muted">Cliente</dt>
            <dd className="min-w-0 font-medium">{prazo.cliente}</dd>
            <dt className="text-muted">Responsável</dt>
            <dd className="min-w-0 font-medium">{prazo.responsavel}</dd>
            {prazo.data_disponibilizacao ? (
              <>
                <dt className="text-muted">Disponibilização</dt>
                <dd className="min-w-0 font-medium">
                  {new Date(prazo.data_disponibilizacao + "T12:00:00").toLocaleDateString("pt-BR")}
                </dd>
              </>
            ) : null}
          </dl>
        </Card>

        <div className="mt-5">
          <PrazoChecklist
            prazoId={prazo.id}
            initialItems={checklist}
            canEdit={canEditChecklist}
          />
        </div>

        {datajud ? (
          <ProcessoAndamentos data={datajud} />
        ) : (
          <AndamentosEmpty
            message={
              prazo.processo_id
                ? "Não encontramos a ficha deste processo. Os andamentos do tribunal ficam indisponíveis por enquanto."
                : "Este prazo ainda não está vinculado a uma ficha de processo, então não dá para buscar andamentos no tribunal."
            }
          />
        )}

        <div className="mt-5">
          <PrazoAlertasEditor
            prazo={prazo}
            canEdit={!isExcluded && hasPermission(user, "prazos_alterar")}
          />
        </div>

        <div className="mt-6 flex flex-col gap-2">
          {isExcluded ? (
            hasPermission(user, "prazos_restaurar") ? (
              <RestaurarPrazoButton prazoId={prazo.id} />
            ) : (
              <p className="text-sm text-muted">Você não tem permissão para restaurar prazos.</p>
            )
          ) : (
            <>
              {prazo.status !== "cumprido" ? (
                hasPermission(user, "prazos_cumprir") ? (
                  <form action={cumprir}>
                    <Button type="submit" fullWidth>
                      Marcar como cumprido
                    </Button>
                  </form>
                ) : null
              ) : (
                <p className="text-sm font-medium text-no-prazo">Este prazo já foi cumprido.</p>
              )}
              {hasPermission(user, "prazos_alterar") ? (
                <ButtonLink href={`/prazos/${prazo.id}/editar`} variant="secondary" fullWidth>
                  Editar
                </ButtonLink>
              ) : null}
              {hasPermission(user, "prazos_excluir") ? (
                <ExcluirPrazoButton prazoId={prazo.id} acao={prazo.acao} />
              ) : null}
            </>
          )}
        </div>
      </PageContent>
    </AppShell>
  );
}
