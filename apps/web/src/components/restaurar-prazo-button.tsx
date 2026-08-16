"use client";

import { useTransition } from "react";

import { restaurarPrazo } from "@/app/prazos/actions";
import { Button } from "@/components/ui";

export function RestaurarPrazoButton({ prazoId }: { prazoId: string }) {
  const [pending, startTransition] = useTransition();

  return (
    <Button
      type="button"
      size="lg"
      fullWidth
      disabled={pending}
      onClick={() => {
        startTransition(async () => {
          await restaurarPrazo(prazoId);
        });
      }}
    >
      {pending ? "Restaurando…" : "Restaurar prazo"}
    </Button>
  );
}
