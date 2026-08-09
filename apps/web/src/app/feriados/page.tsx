import Link from "next/link";
import { redirect } from "next/navigation";

import { CriarFeriadoForm } from "@/components/criar-feriado-form";
import { EditarFeriadoForm } from "@/components/editar-feriado-form";
import { LogoutButton } from "@/components/logout-button";
import { apiFetch } from "@/lib/api-server";
import { hasPermission, type User } from "@/lib/auth";
import { formatFeriadoDate, type Feriado } from "@/lib/feriados";

async function getCurrentUser(): Promise<User | null> {
  const response = await apiFetch("/api/v1/auth/me");
  if (!response.ok) return null;
  return (await response.json()) as User;
}

async function listFeriados(): Promise<Feriado[]> {
  const response = await apiFetch("/api/v1/feriados");
  if (!response.ok) return [];
  return (await response.json()) as Feriado[];
}

export default async function FeriadosPage() {
  const currentUser = await getCurrentUser();
  if (!currentUser) redirect("/login");
  if (!hasPermission(currentUser, "usuarios_gerenciar")) redirect("/prazos");

  const feriados = await listFeriados();

  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col px-6 py-10 sm:px-10">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="font-[family-name:var(--font-display)] text-2xl font-semibold text-primary">
            Agenda Processual
          </p>
          <h1 className="mt-5 text-3xl font-semibold tracking-tight text-foreground">
            Feriados
          </h1>
          <p className="mt-2 text-muted">
            Datas que não contam como dia útil no cálculo de vencimento (além de sábados e
            domingos).
          </p>
        </div>
        <div className="flex flex-col items-end gap-3">
          <LogoutButton />
          <Link
            href="/dashboard"
            className="inline-flex h-11 items-center justify-center border border-border bg-surface px-4 text-sm font-medium"
          >
            Voltar ao painel
          </Link>
        </div>
      </div>

      <section className="mt-10 border border-border bg-surface p-5 sm:p-7">
        <CriarFeriadoForm />
      </section>

      <section className="mt-10">
        <h2 className="text-lg font-semibold text-foreground">
          Cadastrados ({feriados.length})
        </h2>
        {feriados.length === 0 ? (
          <p className="mt-4 text-sm text-muted">Nenhum feriado cadastrado ainda.</p>
        ) : (
          <div className="mt-4 grid gap-4">
            {feriados.map((feriado) => (
              <div key={feriado.id} className="space-y-2">
                <p className="text-xs text-muted">
                  {formatFeriadoDate(feriado.data)} · {feriado.nome}
                </p>
                <EditarFeriadoForm feriado={feriado} />
              </div>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
