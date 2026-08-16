"use client";

import { useActionState, useEffect, useRef } from "react";

import { createFeriado, type ActionState } from "@/app/feriados/actions";
import { Button, Field, Input, SectionHeading } from "@/components/ui";

const initialState: ActionState = {};

export function CriarFeriadoForm() {
  const [state, formAction, pending] = useActionState(createFeriado, initialState);
  const formRef = useRef<HTMLFormElement>(null);

  useEffect(() => {
    if (state.ok) {
      formRef.current?.reset();
    }
  }, [state.ok]);

  return (
    <form ref={formRef} action={formAction} className="flex flex-col gap-4">
      <SectionHeading>Novo feriado</SectionHeading>
      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="Data">
          <Input name="data" type="date" required />
        </Field>
        <Field label="Nome">
          <Input name="nome" required placeholder="Independência do Brasil" />
        </Field>
      </div>
      {state.error ? <p className="text-sm text-atrasado">{state.error}</p> : null}
      {state.ok ? <p className="text-sm text-foreground">Feriado cadastrado.</p> : null}
      <Button type="submit" size="lg" disabled={pending}>
        {pending ? "Salvando…" : "Cadastrar feriado"}
      </Button>
    </form>
  );
}
