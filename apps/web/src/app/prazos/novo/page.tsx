import Link from "next/link";
import { redirect } from "next/navigation";

import { NovoPrazoForm } from "@/components/novo-prazo-form";
import { apiFetch } from "@/lib/api-server";
import { hasPermission, type User, type UserOption } from "@/lib/auth";

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

export default async function NovoPrazoPage({
  searchParams,
}: {
  searchParams: Promise<{ processo?: string; cliente?: string }>;
}) {
  const user = await getCurrentUser();
  if (!hasPermission(user, "prazos_criar")) redirect("/prazos");

  const [usuarios, params] = await Promise.all([listUsuariosOpcoes(), searchParams]);

  return (
    <main className="mx-auto flex w-full max-w-xl flex-1 flex-col px-6 py-10 sm:px-10">
      <Link href="/prazos" className="text-sm text-muted underline-offset-4 hover:underline">
        ← Voltar para prazos
      </Link>
      <h1 className="mt-6 text-3xl font-semibold tracking-tight text-foreground">Novo prazo</h1>
      <p className="mt-2 text-muted">
        Cadastre a obrigação. Se o número do processo já existir, o prazo entra na mesma ficha.
      </p>
      <div className="mt-8 border border-border bg-surface p-5 sm:p-7">
        <NovoPrazoForm
          usuarios={usuarios}
          initialNumero={params.processo ?? ""}
          initialCliente={params.cliente ?? ""}
        />
      </div>
    </main>
  );
}
