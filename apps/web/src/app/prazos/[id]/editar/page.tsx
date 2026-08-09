import Link from "next/link";
import { notFound, redirect } from "next/navigation";

import { EditarPrazoForm } from "@/components/editar-prazo-form";
import { apiFetch } from "@/lib/api-server";
import { hasPermission, type User } from "@/lib/auth";
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

export default async function EditarPrazoPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const [user, prazo] = await Promise.all([getCurrentUser(), getPrazo(id)]);
  if (!hasPermission(user, "prazos_alterar")) redirect("/prazos");
  if (!prazo) notFound();
  if (prazo.excluido_em) {
    redirect(`/prazos/${id}`);
  }

  return (
    <main className="mx-auto flex w-full max-w-xl flex-1 flex-col px-6 py-10 sm:px-10">
      <Link
        href={`/prazos/${prazo.id}`}
        className="text-sm text-muted underline-offset-4 hover:underline"
      >
        ← Voltar ao detalhe
      </Link>
      <h1 className="mt-6 text-3xl font-semibold tracking-tight text-foreground">Editar prazo</h1>
      <p className="mt-2 text-muted">Ajuste os dados sem perder o histórico do cadastro.</p>
      <div className="mt-8 border border-border bg-surface p-5 sm:p-7">
        <EditarPrazoForm prazo={prazo} />
      </div>
    </main>
  );
}
