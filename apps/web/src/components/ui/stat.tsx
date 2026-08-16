import { cn } from "@/lib/cn";

type StatTone = "atrasado" | "urgente" | "muted" | "ok";

const toneClass: Record<StatTone, string> = {
  atrasado: "border-l-atrasado text-atrasado",
  urgente: "border-l-urgente text-urgente",
  muted: "border-l-border text-foreground",
  ok: "border-l-no-prazo text-no-prazo",
};

type StatProps = {
  label: string;
  value: number;
  tone?: StatTone;
};

export function Stat({ label, value, tone = "muted" }: StatProps) {
  return (
    <div
      className={cn(
        "rounded-md border border-border bg-surface border-l-[3px] px-3 py-2.5 sm:px-4 sm:py-3",
        toneClass[tone],
      )}
    >
      <p className="text-[10px] font-medium uppercase tracking-wide text-muted sm:text-[11px]">{label}</p>
      <p className="mt-1 font-[family-name:var(--font-display)] text-xl font-semibold leading-none sm:text-2xl">
        {value}
      </p>
    </div>
  );
}
