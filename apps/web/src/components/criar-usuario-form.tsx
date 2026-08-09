"use client";

import { useActionState, useEffect, useRef } from "react";

import { createUsuario, type ActionState } from "@/app/usuarios/actions";

const initialState: ActionState = {};

export function CriarUsuarioForm() {
  const formRef = useRef<HTMLFormElement>(null);
  const [state, formAction, pending] = useActionState(createUsuario, initialState);

  useEffect(() => {
    if (state.ok) {
      formRef.current?.reset();
    }
  }, [state.ok]);

  return (
    <form ref={formRef} action={formAction} className="flex flex-col gap-4">
      <h2 className="text-lg font-semibold text-foreground">Novo usuário</h2>

      <label className="flex flex-col gap-1.5 text-sm">
        <span className="font-medium">Nome</span>
        <input
          name="nome"
          required
          className="h-11 border border-border bg-background px-3 outline-none ring-primary focus:ring-2"
        />
      </label>

      <label className="flex flex-col gap-1.5 text-sm">
        <span className="font-medium">E-mail</span>
        <input
          name="email"
          type="email"
          required
          className="h-11 border border-border bg-background px-3 outline-none ring-primary focus:ring-2"
        />
      </label>

      <label className="flex flex-col gap-1.5 text-sm">
        <span className="font-medium">Senha inicial</span>
        <input
          name="password"
          type="password"
          required
          minLength={6}
          className="h-11 border border-border bg-background px-3 outline-none ring-primary focus:ring-2"
        />
      </label>

      <label className="flex items-center gap-2 text-sm">
        <input name="is_admin" type="checkbox" />
        Administrador (pode gerenciar usuários e ver toda a auditoria)
      </label>

      <label className="flex items-center gap-2 text-sm">
        <input name="ativo" type="checkbox" defaultChecked />
        Ativo (pode entrar no sistema)
      </label>

      {state.error ? <p className="text-sm text-atrasado">{state.error}</p> : null}
      {state.ok ? <p className="text-sm text-no-prazo">Usuário criado com sucesso.</p> : null}

      <button
        type="submit"
        disabled={pending}
        className="inline-flex h-12 items-center justify-center bg-primary px-6 text-base font-semibold text-primary-foreground transition hover:brightness-110 disabled:opacity-60"
      >
        {pending ? "Salvando…" : "Criar usuário"}
      </button>
    </form>
  );
}
