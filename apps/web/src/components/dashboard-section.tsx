import { PrazoListItem } from "@/components/prazo-list-item";
import type { Prazo } from "@/lib/prazos";

type DashboardSectionProps = {
  title: string;
  description: string;
  emptyMessage: string;
  prazos: Prazo[];
  accent?: "atrasado" | "urgente" | "default";
};

export function DashboardSection({
  title,
  description,
  emptyMessage,
  prazos,
  accent = "default",
}: DashboardSectionProps) {
  const titleClass =
    accent === "atrasado"
      ? "text-atrasado"
      : accent === "urgente"
        ? "text-urgente"
        : "text-foreground";

  return (
    <section className="mt-10">
      <div className="flex items-baseline justify-between gap-3">
        <div>
          <h2 className={`text-xl font-semibold tracking-tight ${titleClass}`}>
            {title}
            <span className="ml-2 text-base font-medium text-muted">({prazos.length})</span>
          </h2>
          <p className="mt-1 text-sm text-muted">{description}</p>
        </div>
      </div>

      {prazos.length === 0 ? (
        <p className="mt-4 text-sm text-muted">{emptyMessage}</p>
      ) : (
        <ul className="mt-4 divide-y divide-border border-y border-border">
          {prazos.map((prazo) => (
            <PrazoListItem key={prazo.id} prazo={prazo} />
          ))}
        </ul>
      )}
    </section>
  );
}
