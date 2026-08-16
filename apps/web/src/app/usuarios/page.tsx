import { Suspense } from "react";
import { redirect } from "next/navigation";

import { AppShell, PageContent, PageHeader } from "@/components/app-shell";
import { CriarUsuarioForm } from "@/components/criar-usuario-form";
import { EditarUsuarioForm } from "@/components/editar-usuario-form";
import { ListaConvites } from "@/components/lista-convites";
import { UsuariosTabs } from "@/components/usuarios-tabs";
import { Card, EmptyState } from "@/components/ui";
import { apiFetch } from "@/lib/api-server";
import { hasPermission, type RoleInfo, type User } from "@/lib/auth";
import type { Convite } from "@/lib/convites";

async function getCurrentUser(): Promise<User | null> {
  const response = await apiFetch("/api/v1/auth/me");
  if (!response.ok) return null;
  return (await response.json()) as User;
}

async function listUsuarios(): Promise<User[]> {
  const response = await apiFetch("/api/v1/usuarios");
  if (!response.ok) return [];
  return (await response.json()) as User[];
}

async function listRoles(): Promise<RoleInfo[]> {
  const response = await apiFetch("/api/v1/roles");
  if (!response.ok) return [];
  return (await response.json()) as RoleInfo[];
}

async function listConvites(): Promise<Convite[]> {
  const response = await apiFetch("/api/v1/convites");
  if (!response.ok) return [];
  return (await response.json()) as Convite[];
}

export default async function UsuariosPage() {
  const currentUser = await getCurrentUser();
  if (!currentUser) redirect("/login");
  if (!hasPermission(currentUser, "usuarios_gerenciar")) redirect("/dashboard");

  const [usuarios, roles, convites] = await Promise.all([
    listUsuarios(),
    listRoles(),
    listConvites(),
  ]);

  return (
    <AppShell user={currentUser}>
      <PageHeader
        title="Usuários"
        description="Convide pessoas por e-mail e defina o perfil de permissões (admin, editor ou visualizador)."
      />

      <PageContent>
        <Suspense fallback={null}>
          <UsuariosTabs
            convitesCount={convites.length}
            contasCount={usuarios.length}
            convidar={
              <Card className="p-5 sm:p-7">
                <CriarUsuarioForm roles={roles} />
              </Card>
            }
            enviados={<ListaConvites convites={convites} />}
            contas={
              <div className="grid gap-4">
                {usuarios.length === 0 ? (
                  <EmptyState>Nenhuma conta cadastrada ainda.</EmptyState>
                ) : (
                  usuarios.map((user) => (
                    <EditarUsuarioForm
                      key={user.id}
                      user={user}
                      roles={roles}
                      isSelf={user.id === currentUser.id}
                    />
                  ))
                )}
              </div>
            }
          />
        </Suspense>
      </PageContent>
    </AppShell>
  );
}
