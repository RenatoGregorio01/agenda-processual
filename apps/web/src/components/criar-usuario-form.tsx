"use client";

import { useActionState, useEffect, useMemo, useRef, useState } from "react";

import { createUsuario, type ActionState } from "@/app/usuarios/actions";
import type { RoleInfo } from "@/lib/auth";

const initialState: ActionState = {};

export function CriarUsuarioForm({ roles }: { roles: RoleInfo[] }) {
  const formRef = useRef<HTMLFormElement>(null);
  const [role, setRole] = useState(roles[1]?.id ?? "editor");
  const [state, formAction, pending] = useActionState(createUsuario, initialState);
  const selected = useMemo(() => roles.find((item) => item.id === role), [role, roles]);

  useEffect(() => {
    if (state.ok) {
      formRef.current?.reset();
      setRole(roles[1]?.id ?? "editor");
    }
  }, [state.ok, roles]);

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

      <label className="flex flex-col gap-1.5 text-sm">
        <span className="font-medium">Perfil (role)</span>
        <select
          name="role"
          required
          value={role}
          onChange={(event) => setRole(event.target.value as RoleInfo["id"])}
          className="h-11 border border-border bg-background px-3 outline-none ring-primary focus:ring-2"
        >
          {roles.map((item) => (
            <option key={item.id} value={item.id}>
              {item.label}
            </option>
          ))}
        </select>
      </label>

      {selected ? (
        <div className="border border-border bg-background p-3 text-sm">
          <p className="text-muted">{selected.description}</p>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-foreground">
            {selected.permission_labels.map((label) => (
              <li key={label}>{label}</li>
            ))}
          </ul>
        </div>
      ) : null}

      <label className="flex items-center gap-2 text-sm">
        <input name="ativo" type="checkbox" defaultChecked />
        Ativo (pode entrar no sistema)
      </label>

      <label className="flex items-start gap-2 text-sm">
        <input name="receber_alertas" type="checkbox" defaultChecked className="mt-0.5" />
        <span>
          Receber alertas de prazos por e-mail
          <span className="mt-0.5 block text-xs text-muted">
            Além do responsável do prazo, quem estiver marcado recebe os avisos 3/2/1 dia.
          </span>
        </span>
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
