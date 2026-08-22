"use client";

import { useActionState, useMemo, useState } from "react";

import { updateUsuario, type ActionState } from "@/app/usuarios/actions";
import { Button, Field, Input, Select } from "@/components/ui";
import type { RoleInfo, User } from "@/lib/auth";
import { OAB_UFS } from "@/lib/oab";

const initialState: ActionState = {};

type EditarUsuarioFormProps = {
  user: User;
  roles: RoleInfo[];
  isSelf: boolean;
  onCancel: () => void;
};

export function EditarUsuarioForm({ user, roles, isSelf, onCancel }: EditarUsuarioFormProps) {
  const boundUpdate = updateUsuario.bind(null, user.id);
  const [state, formAction, pending] = useActionState(boundUpdate, initialState);
  const [role, setRole] = useState(user.role);
  const [ehAdvogado, setEhAdvogado] = useState(Boolean(user.eh_advogado));
  const selected = useMemo(() => roles.find((item) => item.id === role), [role, roles]);

  return (
    <form action={formAction} className="flex flex-col gap-3 border-t border-border px-3 py-3">
      <Field label="Nome">
        <Input name="nome" required defaultValue={user.nome} className="h-10" />
      </Field>

      <Field label="E-mail">
        <Input name="email" type="email" required defaultValue={user.email} className="h-10" />
      </Field>

      <Field label="Redefinir senha (opcional)" hint="Deixe em branco para manter a senha atual">
        <Input
          name="password"
          type="password"
          minLength={6}
          placeholder="Nova senha"
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
          <Field label="Perfil">
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
            Conta ativa
          </label>
        </>
      )}

      <label className="flex items-start gap-2 text-sm">
        <input
          name="eh_advogado"
          type="checkbox"
          className="mt-0.5"
          checked={ehAdvogado}
          onChange={(event) => setEhAdvogado(event.target.checked)}
        />
        <span>Advogado (monitorar no Diário)</span>
      </label>

      {ehAdvogado ? (
        <div className="grid gap-3 sm:grid-cols-[1fr_7rem]">
          <Field label="Número OAB">
            <Input
              name="oab_numero"
              required
              inputMode="numeric"
              defaultValue={user.oab_numero ?? ""}
              className="h-10"
            />
          </Field>
          <Field label="UF">
            <Select name="oab_uf" required defaultValue={user.oab_uf ?? "BA"} className="h-10">
              {OAB_UFS.map((uf) => (
                <option key={uf} value={uf}>
                  {uf}
                </option>
              ))}
            </Select>
          </Field>
        </div>
      ) : null}

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

      <div className="flex flex-col gap-2 sm:flex-row">
        <Button type="submit" disabled={pending} className="sm:flex-1">
          {pending ? "Salvando…" : "Salvar"}
        </Button>
        <Button type="button" variant="secondary" disabled={pending} className="sm:flex-1" onClick={onCancel}>
          Cancelar
        </Button>
      </div>
    </form>
  );
}
