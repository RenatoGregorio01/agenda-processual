import Link from "next/link";
import { notFound, redirect } from "next/navigation";

import { listChecklist } from "@/app/prazos/checklist-actions";
import { AppShell, PageContent, PageHeader } from "@/components/app-shell";
import { EditarPrazoForm } from "@/components/editar-prazo-form";
import { apiFetch } from "@/lib/api-server";
import { hasPermission, type User, type UserOption } from "@/lib/auth";
import type { Prazo } from "@/lib/prazos";

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

async function listUsuariosOpcoes(): Promise<UserOption[]> {
  const response = await apiFetch("/api/v1/usuarios/opcoes");
  if (!response.ok) return [];
  return (await response.json()) as UserOption[];
}

export default async function EditarPrazoPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const [user, prazo, usuarios, checklist] = await Promise.all([
    getCurrentUser(),
    getPrazo(id),
    listUsuariosOpcoes(),
    listChecklist(id),
  ]);
  if (!hasPermission(user, "prazos_alterar")) redirect("/dashboard");
  if (!prazo) notFound();
  if (prazo.excluido_em) {
    redirect(`/prazos/${id}`);
  }

  return (
    <AppShell user={user}>
      <PageHeader
        title="Editar prazo"
        description="Ajuste os dados sem perder o histórico do cadastro."
        actions={
          <Link
            href={`/prazos/${prazo.id}`}
            className="text-sm text-muted underline-offset-4 hover:underline"
          >
            Cancelar
          </Link>
        }
      />
      <PageContent>
        <div className="border border-border bg-surface p-5 sm:p-7">
          <EditarPrazoForm
            prazo={prazo}
            usuarios={usuarios}
            checklistItems={checklist.map((item) => item.texto)}
          />
        </div>
      </PageContent>
    </AppShell>
  );
}
