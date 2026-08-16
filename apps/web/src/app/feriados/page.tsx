import { redirect } from "next/navigation";

import { AppShell, PageContent, PageHeader } from "@/components/app-shell";
import { CriarFeriadoForm } from "@/components/criar-feriado-form";
import { EditarFeriadoForm } from "@/components/editar-feriado-form";
import { Card, EmptyState, SectionHeading } from "@/components/ui";
import { apiFetch } from "@/lib/api-server";
import { hasPermission, type User } from "@/lib/auth";
import type { Feriado } from "@/lib/feriados";

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
  if (!hasPermission(currentUser, "usuarios_gerenciar")) redirect("/dashboard");

  const feriados = await listFeriados();

  return (
    <AppShell user={currentUser}>
      <PageHeader
        title="Feriados"
        description="Datas que não contam como dia útil no cálculo de vencimento (além de sábados e domingos)."
      />

      <PageContent>
        <Card className="p-5 sm:p-7">
          <CriarFeriadoForm />
        </Card>

        <section className="mt-10">
          <SectionHeading>Cadastrados ({feriados.length})</SectionHeading>
          {feriados.length === 0 ? (
            <EmptyState>Nenhum feriado cadastrado ainda.</EmptyState>
          ) : (
            <div className="grid gap-4">
              {feriados.map((feriado) => (
                <EditarFeriadoForm key={feriado.id} feriado={feriado} />
              ))}
            </div>
          )}
        </section>
      </PageContent>
    </AppShell>
  );
}
