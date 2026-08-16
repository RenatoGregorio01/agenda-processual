"use client";

import { useActionState, useMemo, useState } from "react";

import { updateUsuario, type ActionState } from "@/app/usuarios/actions";
import { Badge, Button, Card, Field, Input, Select } from "@/components/ui";
import type { RoleInfo, User } from "@/lib/auth";

const initialState: ActionState = {};

type EditarUsuarioFormProps = {
  user: User;
  roles: RoleInfo[];
  isSelf: boolean;
};

export function EditarUsuarioForm({ user, roles, isSelf }: EditarUsuarioFormProps) {
  const boundUpdate = updateUsuario.bind(null, user.id);
  const [state, formAction, pending] = useActionState(boundUpdate, initialState);
  const [role, setRole] = useState(user.role);
  const selected = useMemo(() => roles.find((item) => item.id === role), [role, roles]);

  return (
    <Card className="p-4">
      <form action={formAction} className="flex flex-col gap-3">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex flex-wrap items-center gap-2">
            <p className="font-medium text-foreground">{user.nome}</p>
            <Badge tone={user.ativo ? "cumprido" : "atrasado"}>
              {user.ativo ? "ATIVO" : "INATIVO"}
            </Badge>
          </div>
          <p className="text-xs text-muted">{user.email}</p>
        </div>

        <Field label="Nome">
          <Input name="nome" required defaultValue={user.nome} className="h-10" />
        </Field>

        <Field label="E-mail">
          <Input name="email" type="email" required defaultValue={user.email} className="h-10" />
        </Field>

        <Field label="Nova senha (opcional)" hint="Deixe em branco para manter">
          <Input
            name="password"
            type="password"
            minLength={6}
            placeholder="Deixe em branco para manter"
            className="h-10"
          />
        </Field>

        {isSelf ? (
          <>
            <input type="hidden" name="role" value={user.role} />
            {user.ativo ? <input type="hidden" name="ativo" value="on" /> : null}
            <p className="text-sm text-muted">
              Perfil: {roles.find((item) => item.id === user.role)?.label ?? user.role} · Status:{" "}
              {user.ativo ? "Ativo" : "Inativo"} (não alterável na própria conta)
            </p>
          </>
        ) : (
          <>
            <Field label="Perfil (role)">
              <Select
                name="role"
                required
                value={role}
                onChange={(event) => setRole(event.target.value as User["role"])}
                className="h-10"
              >
                {roles.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.label}
                  </option>
                ))}
              </Select>
            </Field>
            {selected ? <p className="text-xs text-muted">{selected.description}</p> : null}
            <label className="flex items-center gap-2 text-sm">
              <input name="ativo" type="checkbox" defaultChecked={user.ativo} />
              Ativo
            </label>
          </>
        )}

        <label className="flex items-start gap-2 text-sm">
          <input
            name="receber_alertas"
            type="checkbox"
            defaultChecked={user.receber_alertas}
            className="mt-0.5"
          />
          <span>
            Receber alertas de prazos por e-mail
            <span className="mt-0.5 block text-xs text-muted">
              Só dos prazos em que a pessoa for a responsável.
            </span>
          </span>
        </label>

        {state.error ? <p className="text-sm text-atrasado">{state.error}</p> : null}
        {state.ok ? <p className="text-sm text-no-prazo">Alterações salvas.</p> : null}

        <Button type="submit" disabled={pending}>
          {pending ? "Salvando…" : "Salvar"}
        </Button>
      </form>
    </Card>
  );
}
