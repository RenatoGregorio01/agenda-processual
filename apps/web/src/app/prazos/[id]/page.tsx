import Link from "next/link";
import { notFound } from "next/navigation";

import { cumprirPrazo, excluirPrazo } from "@/app/prazos/actions";
import { PrazoBadge } from "@/components/prazo-badge";
import { apiFetch } from "@/lib/api-server";
import {
  formatVencimentoLongo,
  getUrgencyBadge,
  type Prazo,
} from "@/lib/prazos";

async function getPrazo(id: string): Promise<Prazo | null> {
  const response = await apiFetch(`/api/v1/prazos/${id}`);
  if (response.status === 404) return null;
  if (!response.ok) return null;
  return (await response.json()) as Prazo;
}

export default async function PrazoDetalhePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const prazo = await getPrazo(id);
  if (!prazo) notFound();

  const badge = getUrgencyBadge(prazo);
  const cumprir = cumprirPrazo.bind(null, prazo.id);
  const excluir = excluirPrazo.bind(null, prazo.id);

  return (
    <main className="mx-auto flex w-full max-w-2xl flex-1 flex-col px-6 py-10 sm:px-10">
      <Link href="/prazos" className="text-sm text-muted underline-offset-4 hover:underline">
        ← Voltar para prazos
      </Link>

      <section className="mt-8">
        <p className="text-sm uppercase tracking-wide text-muted">Vence em</p>
        <h1 className="mt-2 text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
          {formatVencimentoLongo(prazo.data_vencimento)}
        </h1>
        <div className="mt-3">
          <PrazoBadge badge={badge} />
        </div>
      </section>

      <section className="mt-10 border-t border-border pt-6">
        <h2 className="text-2xl font-semibold text-foreground">{prazo.acao}</h2>
        <p className="mt-2 text-muted">
          {badge.label === "ATRASADO"
            ? "Prazo vencido. Protocolar o quanto antes."
            : badge.label === "AMANHÃ" || badge.label === "HOJE"
              ? `${badge.label === "HOJE" ? "Hoje" : "Amanhã"} vence. Protocolar no prazo.`
              : "Acompanhe o vencimento e a ação necessária."}
        </p>
      </section>

      <section className="mt-8 space-y-2 text-sm">
        <p>
          <span className="text-muted">Processo:</span>{" "}
          <span className="font-medium">{prazo.numero_processo}</span>
        </p>
        <p>
          <span className="text-muted">Cliente:</span>{" "}
          <span className="font-medium">{prazo.cliente}</span>
        </p>
        <p>
          <span className="text-muted">Responsável:</span>{" "}
          <span className="font-medium">{prazo.responsavel}</span>
        </p>
        {prazo.data_disponibilizacao ? (
          <p>
            <span className="text-muted">Disponibilização no diário:</span>{" "}
            <span className="font-medium">
              {new Date(prazo.data_disponibilizacao + "T12:00:00").toLocaleDateString("pt-BR")}
            </span>
          </p>
        ) : null}
      </section>

      <section className="mt-8 border-t border-border pt-6">
        <h3 className="text-sm font-medium text-foreground">Alertas</h3>
        <ul className="mt-3 space-y-1 text-sm text-muted">
          <li>{prazo.alerta_3_dias ? "✓" : "–"} 3 dias antes</li>
          <li>{prazo.alerta_2_dias ? "✓" : "–"} 2 dias antes</li>
          <li>{prazo.alerta_1_dia ? "✓" : "–"} 1 dia antes (amanhã)</li>
        </ul>
      </section>

      <div className="mt-10 flex flex-col gap-3">
        {prazo.status !== "cumprido" ? (
          <form action={cumprir}>
            <button
              type="submit"
              className="inline-flex h-12 w-full items-center justify-center bg-primary px-6 text-base font-semibold text-primary-foreground transition hover:brightness-110"
            >
              Marcar como cumprido
            </button>
          </form>
        ) : (
          <p className="text-sm font-medium text-no-prazo">Este prazo já foi cumprido.</p>
        )}
        <form action={excluir}>
          <button
            type="submit"
            className="inline-flex h-11 w-full items-center justify-center text-sm text-atrasado underline-offset-4 hover:underline"
          >
            Excluir
          </button>
        </form>
      </div>
    </main>
  );
}
