import { DashboardPrazoCard } from "@/components/dashboard-prazo-card";
import { EmptyState } from "@/components/ui";
import { getUrgencyBadge, type Prazo } from "@/lib/prazos";

type ColumnTone = "atrasado" | "urgente" | "no-prazo" | "cumprido";

type DashboardPrazoListProps = {
  prazos: Prazo[];
  tone?: ColumnTone;
  emptyMessage: string;
};

function resolveTone(prazo: Prazo, fixed?: ColumnTone): ColumnTone {
  if (fixed) return fixed;
  if (prazo.status === "cumprido") return "cumprido";
  const badge = getUrgencyBadge(prazo);
  if (badge.tone === "atrasado" || badge.tone === "urgente" || badge.tone === "no-prazo" || badge.tone === "cumprido") {
    return badge.tone;
  }
  return "no-prazo";
}

export function DashboardPrazoList({ prazos, tone, emptyMessage }: DashboardPrazoListProps) {
  if (prazos.length === 0) {
    return <EmptyState>{emptyMessage}</EmptyState>;
  }

  return (
    <div className="grid w-full gap-2">
      {prazos.map((prazo) => (
        <DashboardPrazoCard
          key={prazo.id}
          prazo={prazo}
          tone={resolveTone(prazo, tone)}
        />
      ))}
    </div>
  );
}
