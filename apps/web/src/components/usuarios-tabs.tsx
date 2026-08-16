"use client";

import { useRouter, useSearchParams } from "next/navigation";
import type { ReactNode } from "react";

export type UsuariosAba = "convidar" | "enviados" | "contas";

type UsuariosTabsProps = {
  convitesCount: number;
  contasCount: number;
  convidar: ReactNode;
  enviados: ReactNode;
  contas: ReactNode;
};

function resolveAba(value: string | null): UsuariosAba {
  if (value === "enviados" || value === "convites") return "enviados";
  if (value === "contas") return "contas";
  return "convidar";
}

function tabClass(active: boolean) {
  return active
    ? "-mb-px border-b-2 border-primary px-4 py-2.5 text-sm font-semibold text-foreground"
    : "px-4 py-2.5 text-sm text-muted transition hover:text-foreground";
}

export function UsuariosTabs({
  convitesCount,
  contasCount,
  convidar,
  enviados,
  contas,
}: UsuariosTabsProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const aba = resolveAba(searchParams.get("aba"));

  function selectAba(next: UsuariosAba) {
    const params = new URLSearchParams(searchParams.toString());
    if (next === "convidar") {
      params.delete("aba");
    } else {
      params.set("aba", next);
    }
    const query = params.toString();
    router.replace(query ? `/usuarios?${query}` : "/usuarios", { scroll: false });
  }

  const panel = aba === "convidar" ? convidar : aba === "enviados" ? enviados : contas;

  return (
    <div>
      <div
        className="scroll-x-touch flex gap-1 overflow-x-auto border-b border-border bg-surface/40 px-1"
        role="tablist"
        aria-label="Seções de usuários"
      >
        <button
          type="button"
          role="tab"
          aria-selected={aba === "convidar"}
          onClick={() => selectAba("convidar")}
          className={`whitespace-nowrap ${tabClass(aba === "convidar")}`}
        >
          Convidar
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={aba === "enviados"}
          onClick={() => selectAba("enviados")}
          className={`whitespace-nowrap ${tabClass(aba === "enviados")}`}
        >
          <span className="sm:hidden">Enviados</span>
          <span className="hidden sm:inline">Convites enviados</span>
          <span className="ml-2 text-xs font-medium text-muted">{convitesCount}</span>
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={aba === "contas"}
          onClick={() => selectAba("contas")}
          className={`whitespace-nowrap ${tabClass(aba === "contas")}`}
        >
          <span className="sm:hidden">Contas</span>
          <span className="hidden sm:inline">Contas cadastradas</span>
          <span className="ml-2 text-xs font-medium text-muted">{contasCount}</span>
        </button>
      </div>

      <div role="tabpanel" className="mt-6">
        {panel}
      </div>
    </div>
  );
}
