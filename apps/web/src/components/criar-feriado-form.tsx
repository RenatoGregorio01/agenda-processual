"use client";

import { useActionState, useEffect, useRef } from "react";

import { createFeriado, type ActionState } from "@/app/feriados/actions";

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
      <h2 className="text-lg font-semibold text-foreground">Novo feriado</h2>
      <div className="grid gap-4 sm:grid-cols-2">
        <label className="flex flex-col gap-1.5 text-sm">
          <span className="font-medium">Data</span>
          <input
            name="data"
            type="date"
            required
            className="h-11 border border-border bg-background px-3 outline-none ring-primary focus:ring-2"
          />
        </label>
        <label className="flex flex-col gap-1.5 text-sm">
          <span className="font-medium">Nome</span>
          <input
            name="nome"
            required
            placeholder="Independência do Brasil"
            className="h-11 border border-border bg-background px-3 outline-none ring-primary focus:ring-2"
          />
        </label>
      </div>
      {state.error ? <p className="text-sm text-atrasado">{state.error}</p> : null}
      {state.ok ? <p className="text-sm text-foreground">Feriado cadastrado.</p> : null}
      <button
        type="submit"
        disabled={pending}
        className="inline-flex h-11 w-fit items-center justify-center bg-primary px-5 text-sm font-semibold text-primary-foreground transition hover:brightness-110 disabled:opacity-60"
      >
        {pending ? "Salvando…" : "Cadastrar feriado"}
      </button>
    </form>
  );
}
