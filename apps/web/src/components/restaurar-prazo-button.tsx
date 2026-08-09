"use client";

import { useTransition } from "react";

import { restaurarPrazo } from "@/app/prazos/actions";

export function RestaurarPrazoButton({ prazoId }: { prazoId: string }) {
  const [pending, startTransition] = useTransition();

  return (
    <button
      type="button"
      disabled={pending}
      className="inline-flex h-12 w-full items-center justify-center bg-primary px-6 text-base font-semibold text-primary-foreground transition hover:brightness-110 disabled:opacity-60"
      onClick={() => {
        startTransition(async () => {
          await restaurarPrazo(prazoId);
        });
      }}
    >
      {pending ? "Restaurando…" : "Restaurar prazo"}
    </button>
  );
}
