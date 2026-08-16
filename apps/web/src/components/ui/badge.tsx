import { cn } from "@/lib/cn";

export type BadgeTone = "atrasado" | "urgente" | "no-prazo" | "cumprido" | "neutro";

const toneClass: Record<BadgeTone, string> = {
  atrasado: "bg-atrasado text-white",
  urgente: "bg-urgente text-white",
  "no-prazo": "border border-urgente/40 bg-[#fef6ee] text-urgente",
  cumprido: "border border-no-prazo/40 bg-[#e8f5ef] text-no-prazo",
  neutro: "border border-border bg-[#eceae4] text-muted",
};

type BadgeProps = {
  tone?: BadgeTone;
  children: string;
  className?: string;
};

export function Badge({ tone = "neutro", children, className }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex shrink-0 px-1.5 py-0.5 text-[10px] font-semibold tracking-wide",
        toneClass[tone],
        className,
      )}
    >
      {children}
    </span>
  );
}
