"use client";

import { useTransition } from "react";

import { reenviarConvite, revogarConvite } from "@/app/usuarios/actions";
import { Badge, Button, Card, EmptyState, type BadgeTone } from "@/components/ui";
import { labelStatusConvite, type Convite } from "@/lib/convites";

function toneStatus(status: string): BadgeTone {
  if (status === "aceito") return "cumprido";
  if (status === "pendente") return "urgente";
  if (status === "revogado") return "atrasado";
  return "neutro";
}

export function ListaConvites({ convites }: { convites: Convite[] }) {
  const [pending, startTransition] = useTransition();

  if (convites.length === 0) {
    return <EmptyState>Nenhum convite enviado ainda.</EmptyState>;
  }

  return (
    <div className="grid gap-3">
      {convites.map((convite) => {
        const canManage = convite.status === "pendente" || convite.status === "expirado";
        return (
          <Card
            key={convite.id}
            className="flex flex-col gap-3 p-4 sm:flex-row sm:items-center sm:justify-between"
          >
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <p className="font-medium text-foreground">{convite.nome}</p>
                <Badge tone={toneStatus(convite.status)}>
                  {labelStatusConvite(convite.status).toUpperCase()}
                </Badge>
              </div>
              <p className="mt-1 text-sm text-muted">
                {convite.email} · perfil {convite.role} · expira{" "}
                {new Date(convite.expires_at).toLocaleString("pt-BR")}
              </p>
            </div>
            {canManage ? (
              <div className="flex flex-wrap gap-2">
                <Button
                  type="button"
                  variant="secondary"
                  size="sm"
                  disabled={pending}
                  onClick={() =>
                    startTransition(async () => {
                      await reenviarConvite(convite.id);
                    })
                  }
                >
                  Reenviar
                </Button>
                {convite.status === "pendente" ? (
                  <Button
                    type="button"
                    variant="danger"
                    size="sm"
                    disabled={pending}
                    onClick={() =>
                      startTransition(async () => {
                        if (window.confirm(`Revogar convite de ${convite.nome}?`)) {
                          await revogarConvite(convite.id);
                        }
                      })
                    }
                  >
                    Revogar
                  </Button>
                ) : null}
              </div>
            ) : null}
          </Card>
        );
      })}
    </div>
  );
}
