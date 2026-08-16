import { Badge } from "@/components/ui";
import type { UrgencyBadge } from "@/lib/prazos";

export function PrazoBadge({ badge }: { badge: UrgencyBadge }) {
  return <Badge tone={badge.tone}>{badge.label}</Badge>;
}
