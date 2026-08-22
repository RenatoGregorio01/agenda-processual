"use client";

import { useTransition } from "react";
import { useRouter } from "next/navigation";

import { sincronizarDjenEscritorio } from "@/app/djen/actions";
import { Button } from "@/components/ui";

export function DjenSyncButton() {
  const router = useRouter();
  const [pending, startTransition] = useTransition();

  function sync() {
    startTransition(async () => {
      await sincronizarDjenEscritorio();
      router.refresh();
    });
  }

  return (
    <Button type="button" variant="secondary" onClick={sync} disabled={pending}>
      {pending ? "Consultando DJEN…" : "Atualizar DJEN"}
    </Button>
  );
}
