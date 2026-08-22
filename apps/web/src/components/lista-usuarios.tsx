"use client";

import { useState, useTransition } from "react";

import { desativarUsuario } from "@/app/usuarios/actions";
import { EditarUsuarioForm } from "@/components/editar-usuario-form";
import { Badge, Card, EmptyState } from "@/components/ui";
import type { RoleInfo, User } from "@/lib/auth";
import { formatOab } from "@/lib/oab";

function IconLapiz({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M4 20h4l10.5-10.5a2.1 2.1 0 00-3-3L5 17v3z"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
      <path d="M13.5 6.5l3 3" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  );
}

function IconLixeira({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path d="M5 7h14" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      <path d="M10 7V5h4v2" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      <path
        d="M7 7l1 12h8l1-12"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
    </svg>
  );
}

type ListaUsuariosProps = {
  usuarios: User[];
  roles: RoleInfo[];
  currentUserId: string;
};

export function ListaUsuarios({ usuarios, roles, currentUserId }: ListaUsuariosProps) {
  const [editingId, setEditingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pending, startTransition] = useTransition();

  if (usuarios.length === 0) {
    return <EmptyState>Nenhuma conta cadastrada ainda.</EmptyState>;
  }

  return (
    <div className="grid gap-2">
      {error ? <p className="text-sm text-atrasado">{error}</p> : null}
      {usuarios.map((user) => {
        const isSelf = user.id === currentUserId;
        const editing = editingId === user.id;
        return (
          <Card key={user.id} className="overflow-hidden">
            <div className="flex items-center gap-3 px-3 py-2.5">
              <div className="min-w-0 flex-1">
                <div className="flex min-w-0 items-center gap-2">
                  <p className="truncate font-medium text-foreground">{user.nome}</p>
                  {!user.ativo ? <Badge tone="atrasado">INATIVO</Badge> : null}
                  {isSelf ? <Badge tone="neutro">VOCÊ</Badge> : null}
                </div>
                <p className="mt-0.5 truncate text-sm text-muted">
                  {user.email}
                  {user.eh_advogado
                    ? ` · ${formatOab(user.oab_numero, user.oab_uf) ?? "OAB pendente"}`
                    : ""}
                </p>
              </div>
              <div className="flex shrink-0 items-center gap-1">
                <button
                  type="button"
                  className="inline-flex h-9 w-9 items-center justify-center rounded-md text-muted transition hover:bg-background hover:text-foreground"
                  aria-label={editing ? `Fechar edição de ${user.nome}` : `Editar ${user.nome}`}
                  aria-expanded={editing}
                  onClick={() => {
                    setError(null);
                    setEditingId((current) => (current === user.id ? null : user.id));
                  }}
                >
                  <IconLapiz className="h-4 w-4" />
                </button>
                {isSelf || !user.ativo ? null : (
                  <button
                    type="button"
                    className="inline-flex h-9 w-9 items-center justify-center rounded-md text-muted transition hover:bg-[#fdecea] hover:text-atrasado disabled:opacity-50"
                    aria-label={`Desativar ${user.nome}`}
                    disabled={pending}
                    onClick={() => {
                      if (
                        !window.confirm(
                          `Desativar a conta de ${user.nome}? A pessoa deixa de acessar o sistema.`,
                        )
                      ) {
                        return;
                      }
                      setError(null);
                      startTransition(async () => {
                        const result = await desativarUsuario(user.id);
                        if (result.error) setError(result.error);
                        else setEditingId((current) => (current === user.id ? null : current));
                      });
                    }}
                  >
                    <IconLixeira className="h-4 w-4" />
                  </button>
                )}
              </div>
            </div>
            {editing ? (
              <EditarUsuarioForm
                user={user}
                roles={roles}
                isSelf={isSelf}
                onCancel={() => setEditingId(null)}
              />
            ) : null}
          </Card>
        );
      })}
    </div>
  );
}
