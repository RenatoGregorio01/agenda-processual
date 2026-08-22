import { AppShell, PageContent, PageHeader } from "@/components/app-shell";
import { DjenPublicacoesList } from "@/components/djen-publicacoes";
import { DjenSyncButton } from "@/components/djen-sync-button";
import { EmptyState } from "@/components/ui";
import { apiFetch } from "@/lib/api-server";
import { hasPermission, type User } from "@/lib/auth";
import type { DjenPublicacao } from "@/lib/djen";

async function getCurrentUser(): Promise<User | null> {
  const response = await apiFetch("/api/v1/auth/me");
  if (!response.ok) return null;
  return (await response.json()) as User;
}

async function listPublicacoes(status: string): Promise<DjenPublicacao[]> {
  const response = await apiFetch(`/api/v1/djen?status=${encodeURIComponent(status)}`);
  if (!response.ok) return [];
  return (await response.json()) as DjenPublicacao[];
}

export default async function DjenPage() {
  const [user, novas] = await Promise.all([getCurrentUser(), listPublicacoes("nova")]);

  return (
    <AppShell user={user}>
      <PageHeader
        title="Publicações no DJEN"
        description="Intimações do diário dos processos já cadastrados."
        actions={hasPermission(user, "prazos_criar") ? <DjenSyncButton /> : undefined}
      />
      <PageContent wide>
        {novas.length === 0 ? (
          <EmptyState>Nenhuma publicação nova. O job diário consulta o DJEN às 7h.</EmptyState>
        ) : (
          <DjenPublicacoesList items={novas} user={user} />
        )}
      </PageContent>
    </AppShell>
  );
}
