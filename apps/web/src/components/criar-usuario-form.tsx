"use client";

import { useActionState, useMemo, useState } from "react";

import { createConvite, type ActionState } from "@/app/usuarios/actions";
import { Button, Card, Field, Input, SectionHeading, Select } from "@/components/ui";
import type { RoleInfo } from "@/lib/auth";

const initialState: ActionState = {};

export function CriarUsuarioForm({ roles }: { roles: RoleInfo[] }) {
  const defaultRole = roles[1]?.id ?? "editor";
  const [formKey, setFormKey] = useState(0);
  const [role, setRole] = useState(defaultRole);
  const [handledOk, setHandledOk] = useState(false);
  const [state, formAction, pending] = useActionState(createConvite, initialState);
  const selected = useMemo(() => roles.find((item) => item.id === role), [role, roles]);

  if (state.ok && !handledOk) {
    setHandledOk(true);
    setFormKey((key) => key + 1);
    setRole(defaultRole);
  } else if (!state.ok && handledOk) {
    setHandledOk(false);
  }

  return (
    <form key={formKey} action={formAction} className="flex flex-col gap-4">
      <SectionHeading description="A pessoa recebe um link para definir a própria senha. Não é preciso enviar senha pelo WhatsApp.">
        Convidar por e-mail
      </SectionHeading>

      <Field label="Nome">
        <Input name="nome" required />
      </Field>

      <Field label="E-mail">
        <Input name="email" type="email" required />
      </Field>

      <Field label="Perfil (role)">
        <Select
          name="role"
          required
          value={role}
          onChange={(event) => setRole(event.target.value as RoleInfo["id"])}
        >
          {roles.map((item) => (
            <option key={item.id} value={item.id}>
              {item.label}
            </option>
          ))}
        </Select>
      </Field>

      {selected ? (
        <Card className="bg-background p-3 text-sm">
          <p className="text-muted">{selected.description}</p>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-foreground">
            {selected.permission_labels.map((label) => (
              <li key={label}>{label}</li>
            ))}
          </ul>
        </Card>
      ) : null}

      <label className="flex items-start gap-2 text-sm">
        <input name="receber_alertas" type="checkbox" className="mt-0.5" />
        <span>
          Receber alertas de prazos por e-mail
          <span className="mt-0.5 block text-xs text-muted">
            Só dos prazos em que a pessoa for a responsável. O e-mail não inclui nome do
            cliente nem número do processo.
          </span>
        </span>
      </label>

      {state.error ? <p className="text-sm text-atrasado">{state.error}</p> : null}
      {state.ok ? (
        <p className="text-sm text-no-prazo">Convite enviado. Confira o e-mail no Mailpit.</p>
      ) : null}

      <Button type="submit" size="lg" disabled={pending}>
        {pending ? "Enviando…" : "Enviar convite"}
      </Button>
    </form>
  );
}
