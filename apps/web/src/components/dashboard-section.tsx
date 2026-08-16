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
    <section className="border border-border bg-surface">
      <div className="border-b border-border px-5 py-4">
        <div className="flex items-start justify-between gap-3">
          <div>
            <h2 className={`text-xl font-semibold tracking-tight ${titleClass}`}>{title}</h2>
            <p className="mt-1 text-sm text-muted">{description}</p>
          </div>
          <span className="pt-0.5 text-base font-medium text-foreground">{prazos.length}</span>
        </div>
      </div>

      {prazos.length === 0 ? (
        <p className="px-5 py-8 text-sm text-muted">{emptyMessage}</p>
      ) : (
        <ul className="divide-y divide-border px-5">
          {prazos.map((prazo) => (
            <PrazoListItem key={prazo.id} prazo={prazo} />
          ))}
        </ul>
      )}
    </section>
  );
}
