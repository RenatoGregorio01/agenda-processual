"use client";

import { useRouter } from "next/navigation";

import type { UserOption } from "@/lib/auth";
import { buildQuery } from "@/lib/query";

type ResponsavelFilterProps = {
  basePath: string;
  usuarios: UserOption[];
  currentUserId?: string;
  currentResponsavelId?: string;
  extraParams?: Record<string, string | undefined>;
};

export function ResponsavelFilter({
  basePath,
  usuarios,
  currentUserId,
  currentResponsavelId,
  extraParams = {},
}: ResponsavelFilterProps) {
  const router = useRouter();

  function navigate(responsavelId: string) {
    const query = buildQuery({
      ...extraParams,
      responsavel_id: responsavelId || undefined,
    });
    router.push(`${basePath}${query}`);
  }

  return (
    <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:gap-3">
      <label className="flex min-w-0 flex-1 flex-col gap-1.5 text-sm sm:max-w-xs">
        <span className="font-medium text-foreground">Responsável</span>
        <select
          value={currentResponsavelId ?? ""}
          onChange={(event) => navigate(event.target.value)}
          className="h-10 border border-border bg-background px-3 outline-none ring-primary focus:ring-2"
        >
          <option value="">Todos</option>
          {usuarios.map((user) => (
            <option key={user.id} value={user.id}>
              {user.nome}
            </option>
          ))}
        </select>
      </label>
      {currentUserId ? (
        <button
          type="button"
          onClick={() => navigate(currentUserId)}
          className={
            currentResponsavelId === currentUserId
              ? "mt-0 h-10 border border-primary bg-primary px-3 text-sm font-medium text-primary-foreground sm:mt-6"
              : "mt-0 h-10 border border-border bg-surface px-3 text-sm text-muted transition hover:border-primary/40 hover:text-foreground sm:mt-6"
          }
        >
          Meus prazos
        </button>
      ) : null}
    </div>
  );
}
