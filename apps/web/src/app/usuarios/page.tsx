import Link from "next/link";
import { redirect } from "next/navigation";

import { CriarUsuarioForm } from "@/components/criar-usuario-form";
import { EditarUsuarioForm } from "@/components/editar-usuario-form";
import { LogoutButton } from "@/components/logout-button";
import { apiFetch } from "@/lib/api-server";
import { hasPermission, type RoleInfo, type User } from "@/lib/auth";

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

export default async function UsuariosPage() {
  const currentUser = await getCurrentUser();
  if (!currentUser) redirect("/login");
  if (!hasPermission(currentUser, "usuarios_gerenciar")) redirect("/prazos");

  const [usuarios, roles] = await Promise.all([listUsuarios(), listRoles()]);

  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col px-6 py-10 sm:px-10">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="font-[family-name:var(--font-display)] text-2xl font-semibold text-primary">
            Agenda Processual
          </p>
          <h1 className="mt-5 text-3xl font-semibold tracking-tight text-foreground">
            Usuários
          </h1>
          <p className="mt-2 text-muted">
            Defina quem acessa a base e o perfil de permissões (admin, editor ou visualizador).
          </p>
        </div>
        <div className="flex flex-col items-end gap-3">
          <LogoutButton />
          <Link
            href="/prazos"
            className="inline-flex h-11 items-center justify-center border border-border bg-surface px-4 text-sm font-medium"
          >
            Voltar aos prazos
          </Link>
        </div>
      </div>

      <section className="mt-8 border border-border bg-background p-4 text-sm">
        <p className="font-medium text-foreground">Perfis disponíveis</p>
        <ul className="mt-3 space-y-2 text-muted">
          {roles.map((role) => (
            <li key={role.id}>
              <span className="font-medium text-foreground">{role.label}:</span> {role.description}
            </li>
          ))}
        </ul>
      </section>

      <section className="mt-10 border border-border bg-surface p-5 sm:p-7">
        <CriarUsuarioForm roles={roles} />
      </section>

      <section className="mt-10">
        <h2 className="text-lg font-semibold text-foreground">Contas cadastradas</h2>
        <div className="mt-4 grid gap-4">
          {usuarios.map((user) => (
            <EditarUsuarioForm
              key={user.id}
              user={user}
              roles={roles}
              isSelf={user.id === currentUser.id}
            />
          ))}
        </div>
      </section>
    </main>
  );
}
