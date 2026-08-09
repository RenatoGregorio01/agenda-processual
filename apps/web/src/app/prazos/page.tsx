import Link from "next/link";

import { LogoutButton } from "@/components/logout-button";
import { apiFetch } from "@/lib/api-server";
import type { User } from "@/lib/auth";

async function getCurrentUser(): Promise<User | null> {
  const response = await apiFetch("/api/v1/auth/me");
  if (!response.ok) {
    return null;
  }
  return (await response.json()) as User;
}

export default async function PrazosPage() {
  const user = await getCurrentUser();

  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col px-6 py-16 sm:px-10">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="font-[family-name:var(--font-display)] text-3xl font-semibold text-primary">
            Agenda Processual
          </p>
          <h1 className="mt-6 text-2xl font-medium text-foreground">Prazos</h1>
          <p className="mt-3 max-w-lg text-muted">
            Placeholder da lista. A feature de prazos entra em seguida (ordenada por
            vencimento, com badges de urgência).
          </p>
          {user ? (
            <p className="mt-4 text-sm text-muted">
              Logada como <span className="font-medium text-foreground">{user.nome}</span> (
              {user.email})
            </p>
          ) : null}
        </div>
        <LogoutButton />
      </div>

      <Link href="/" className="mt-8 text-primary underline-offset-4 hover:underline">
        Voltar
      </Link>
    </main>
  );
}
