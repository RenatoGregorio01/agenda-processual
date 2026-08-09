"use client";

import { useTransition } from "react";

import { reenviarConvite, revogarConvite } from "@/app/usuarios/actions";
import { labelStatusConvite, type Convite } from "@/lib/convites";

export function ListaConvites({ convites }: { convites: Convite[] }) {
  const [pending, startTransition] = useTransition();

  if (convites.length === 0) {
    return <p className="mt-4 text-sm text-muted">Nenhum convite enviado ainda.</p>;
  }

  return (
    <div className="mt-4 grid gap-3">
      {convites.map((convite) => {
        const canManage = convite.status === "pendente" || convite.status === "expirado";
        return (
          <div
            key={convite.id}
            className="flex flex-col gap-3 border border-border bg-background p-4 sm:flex-row sm:items-center sm:justify-between"
          >
            <div>
              <p className="font-medium text-foreground">
                {convite.nome}{" "}
                <span className="text-sm font-normal text-muted">({convite.email})</span>
              </p>
              <p className="mt-1 text-sm text-muted">
                {labelStatusConvite(convite.status)} · perfil {convite.role} · expira{" "}
                {new Date(convite.expires_at).toLocaleString("pt-BR")}
              </p>
            </div>
            {canManage ? (
              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  disabled={pending}
                  onClick={() =>
                    startTransition(async () => {
                      await reenviarConvite(convite.id);
                    })
                  }
                  className="inline-flex h-10 items-center justify-center border border-border bg-surface px-3 text-sm font-medium disabled:opacity-60"
                >
                  Reenviar
                </button>
                {convite.status === "pendente" ? (
                  <button
                    type="button"
                    disabled={pending}
                    onClick={() =>
                      startTransition(async () => {
                        if (window.confirm(`Revogar convite de ${convite.nome}?`)) {
                          await revogarConvite(convite.id);
                        }
                      })
                    }
                    className="inline-flex h-10 items-center justify-center border border-border px-3 text-sm font-medium text-atrasado disabled:opacity-60"
                  >
                    Revogar
                  </button>
                ) : null}
              </div>
            ) : null}
          </div>
        );
      })}
    </div>
  );
}
