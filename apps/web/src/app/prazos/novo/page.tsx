import Link from "next/link";
import { redirect } from "next/navigation";

import { AppShell, PageContent, PageHeader } from "@/components/app-shell";
import { NovoPrazoForm } from "@/components/novo-prazo-form";
import { apiFetch } from "@/lib/api-server";
import { hasPermission, type User, type UserOption } from "@/lib/auth";
import type { DjenPublicacao } from "@/lib/djen";

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

async function getPublicacao(id: string): Promise<DjenPublicacao | null> {
  const response = await apiFetch(`/api/v1/djen/${id}`);
  if (!response.ok) return null;
  return (await response.json()) as DjenPublicacao;
}

export default async function NovoPrazoPage({
  searchParams,
}: {
  searchParams: Promise<{ processo?: string; cliente?: string; djen?: string }>;
}) {
  const user = await getCurrentUser();
  if (!hasPermission(user, "prazos_criar")) redirect("/dashboard");

  const [usuarios, params] = await Promise.all([listUsuariosOpcoes(), searchParams]);
  const publicacao = params.djen ? await getPublicacao(params.djen) : null;

  return (
    <AppShell user={user}>
      <PageHeader
        title="Novo prazo"
        description={
          publicacao
            ? `A partir da publicação DJEN (${publicacao.tipo_comunicacao}). Confira o vencimento antes de salvar.`
            : "Cadastre a obrigação. Se o número do processo já existir, o prazo entra na mesma ficha."
        }
        actions={
          <Link
            href={publicacao ? "/djen" : "/dashboard"}
            className="text-sm text-muted underline-offset-4 hover:underline"
          >
            Cancelar
          </Link>
        }
      />
      <PageContent>
        <div className="border border-border bg-surface p-5 sm:p-7">
          <NovoPrazoForm
            usuarios={usuarios}
            initialNumero={publicacao?.numero_processo || params.processo || ""}
            initialCliente={publicacao?.cliente || params.cliente || ""}
            initialDisponibilizacao={publicacao?.data_disponibilizacao ?? ""}
            initialVencimento={publicacao?.vencimento_sugerido ?? ""}
            initialAcao={
              publicacao
                ? [publicacao.tipo_comunicacao, publicacao.tipo_documento]
                    .filter(Boolean)
                    .join(" — ")
                : ""
            }
            djenPublicacaoId={publicacao?.id}
          />
        </div>
      </PageContent>
    </AppShell>
  );
}
