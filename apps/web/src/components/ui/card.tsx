import type { ReactNode } from "react";

import { cn } from "@/lib/cn";

type CardTone = "default" | "atrasado" | "urgente" | "no-prazo" | "cumprido";

const toneBar: Record<CardTone, string> = {
  default: "",
  atrasado: "border-l-[3px] border-l-atrasado",
  urgente: "border-l-[3px] border-l-urgente",
  "no-prazo": "border-l-[3px] border-l-urgente",
  cumprido: "border-l-[3px] border-l-no-prazo",
};

type CardProps = {
  children: ReactNode;
  tone?: CardTone;
  className?: string;
};

export function Card({ children, tone = "default", className }: CardProps) {
  return (
    <div
      className={cn(
        "rounded-md border border-border bg-surface shadow-[0_1px_2px_rgba(26,26,26,0.04)]",
        toneBar[tone],
        className,
      )}
    >
      {children}
    </div>
  );
}
