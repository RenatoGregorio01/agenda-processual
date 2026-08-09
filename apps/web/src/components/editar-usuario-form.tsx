"use client";

import { useActionState } from "react";

import { updateUsuario, type ActionState } from "@/app/usuarios/actions";
import type { User } from "@/lib/auth";

const initialState: ActionState = {};

type EditarUsuarioFormProps = {
  user: User;
  isSelf: boolean;
};

export function EditarUsuarioForm({ user, isSelf }: EditarUsuarioFormProps) {
  const boundUpdate = updateUsuario.bind(null, user.id);
  const [state, formAction, pending] = useActionState(boundUpdate, initialState);

  return (
    <form action={formAction} className="flex flex-col gap-3 border border-border bg-surface p-4">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <p className="font-medium text-foreground">{user.nome}</p>
        <p className="text-xs text-muted">{user.email}</p>
      </div>

      <label className="flex flex-col gap-1.5 text-sm">
        <span className="font-medium">Nome</span>
        <input
          name="nome"
          required
          defaultValue={user.nome}
          className="h-10 border border-border bg-background px-3 outline-none ring-primary focus:ring-2"
        />
      </label>

      <label className="flex flex-col gap-1.5 text-sm">
        <span className="font-medium">E-mail</span>
        <input
          name="email"
          type="email"
          required
          defaultValue={user.email}
          className="h-10 border border-border bg-background px-3 outline-none ring-primary focus:ring-2"
        />
      </label>

      <label className="flex flex-col gap-1.5 text-sm">
        <span className="font-medium">Nova senha (opcional)</span>
        <input
          name="password"
          type="password"
          minLength={6}
          placeholder="Deixe em branco para manter"
          className="h-10 border border-border bg-background px-3 outline-none ring-primary focus:ring-2"
        />
      </label>

      {isSelf ? (
        <>
          {user.is_admin ? <input type="hidden" name="is_admin" value="on" /> : null}
          {user.ativo ? <input type="hidden" name="ativo" value="on" /> : null}
          <p className="text-sm text-muted">
            Permissão: {user.is_admin ? "Administrador" : "Padrão"} · Status:{" "}
            {user.ativo ? "Ativo" : "Inativo"} (não alterável na própria conta)
          </p>
        </>
      ) : (
        <>
          <label className="flex items-center gap-2 text-sm">
            <input name="is_admin" type="checkbox" defaultChecked={user.is_admin} />
            Administrador
          </label>
          <label className="flex items-center gap-2 text-sm">
            <input name="ativo" type="checkbox" defaultChecked={user.ativo} />
            Ativo
          </label>
        </>
      )}

      {state.error ? <p className="text-sm text-atrasado">{state.error}</p> : null}
      {state.ok ? <p className="text-sm text-no-prazo">Alterações salvas.</p> : null}

      <button
        type="submit"
        disabled={pending}
        className="inline-flex h-11 items-center justify-center border border-primary bg-primary px-4 text-sm font-semibold text-primary-foreground disabled:opacity-60"
      >
        {pending ? "Salvando…" : "Salvar"}
      </button>
    </form>
  );
}
