"use client";

import { useRouter, useSearchParams } from "next/navigation";
import type { ReactNode } from "react";

export type DashboardAba = "futuros" | "hoje" | "atrasados" | "todos" | "concluidos";

type TabTone = "atrasado" | "urgente" | "neutro";

type DashboardTabsProps = {
  futuros: ReactNode;
  hoje: ReactNode;
  atrasados: ReactNode;
  todos: ReactNode;
  concluidos: ReactNode;
  counts: Record<DashboardAba, number>;
};

const TABS: { id: DashboardAba; label: string; labelShort: string; tone: TabTone }[] = [
  { id: "futuros", label: "Vencimentos Futuros", labelShort: "Futuros", tone: "neutro" },
  { id: "hoje", label: "Vence Hoje", labelShort: "Hoje", tone: "urgente" },
  { id: "atrasados", label: "Atrasados", labelShort: "Atrasados", tone: "atrasado" },
  { id: "todos", label: "Todos", labelShort: "Todos", tone: "neutro" },
  { id: "concluidos", label: "Concluídos", labelShort: "Feitos", tone: "neutro" },
];

function resolveAba(value: string | null): DashboardAba {
  if (value === "amanha" || value === "futuros") return "futuros";
  if (
    value === "atrasados" ||
    value === "hoje" ||
    value === "todos" ||
    value === "concluidos"
  ) {
    return value;
  }
  return "hoje";
}

function tabClass(active: boolean, tone: TabTone) {
  if (!active) {
    return "whitespace-nowrap px-4 py-2.5 text-sm text-muted transition hover:text-foreground";
  }
  const color =
    tone === "atrasado"
      ? "border-atrasado text-atrasado"
      : tone === "urgente"
        ? "border-urgente text-urgente"
        : "border-primary text-foreground";
  return `-mb-px whitespace-nowrap border-b-2 px-4 py-2.5 text-sm font-semibold ${color}`;
}

function countClass(active: boolean, tone: TabTone) {
  if (!active) return "ml-2 text-xs font-medium text-muted";
  if (tone === "atrasado") return "ml-2 text-xs font-medium text-atrasado";
  if (tone === "urgente") return "ml-2 text-xs font-medium text-urgente";
  return "ml-2 text-xs font-medium text-muted";
}

export function DashboardTabs({
  futuros,
  hoje,
  atrasados,
  todos,
  concluidos,
  counts,
}: DashboardTabsProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const aba = resolveAba(searchParams.get("aba"));

  function selectAba(next: DashboardAba) {
    const params = new URLSearchParams(searchParams.toString());
    if (next === "hoje") {
      params.delete("aba");
    } else {
      params.set("aba", next);
    }
    const query = params.toString();
    router.replace(query ? `/dashboard?${query}` : "/dashboard", { scroll: false });
  }

  const panel =
    aba === "futuros"
      ? futuros
      : aba === "hoje"
        ? hoje
        : aba === "atrasados"
          ? atrasados
          : aba === "concluidos"
            ? concluidos
            : todos;

  return (
    <div>
      <div
        className="scroll-x-touch flex gap-1 overflow-x-auto border-b border-border bg-surface/40 px-1"
        role="tablist"
        aria-label="Vencimentos do dashboard"
      >
        {TABS.map((tab) => {
          const active = aba === tab.id;
          return (
            <button
              key={tab.id}
              type="button"
              role="tab"
              aria-selected={active}
              onClick={() => selectAba(tab.id)}
              className={tabClass(active, tab.tone)}
            >
              <span className="sm:hidden">{tab.labelShort}</span>
              <span className="hidden sm:inline">{tab.label}</span>
              <span className={countClass(active, tab.tone)}>{counts[tab.id]}</span>
            </button>
          );
        })}
      </div>
      <div role="tabpanel" className="mt-6">
        {panel}
      </div>
    </div>
  );
}
