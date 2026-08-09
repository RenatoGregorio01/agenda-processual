import type { UrgencyBadge } from "@/lib/prazos";

const toneClass: Record<UrgencyBadge["tone"], string> = {
  atrasado: "text-atrasado",
  urgente: "text-urgente",
  "no-prazo": "text-no-prazo",
  neutro: "text-muted",
};

export function PrazoBadge({ badge }: { badge: UrgencyBadge }) {
  return (
    <span className={`text-xs font-semibold tracking-wide ${toneClass[badge.tone]}`}>
      {badge.label}
    </span>
  );
}
