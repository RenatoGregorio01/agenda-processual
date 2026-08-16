import type { ReactNode } from "react";

import { cn } from "@/lib/cn";

type SectionHeadingProps = {
  children: ReactNode;
  description?: ReactNode;
  className?: string;
};

export function SectionHeading({ children, description, className }: SectionHeadingProps) {
  return (
    <div className={cn("mb-4", className)}>
      <h2 className="font-[family-name:var(--font-display)] text-xl font-semibold text-foreground">
        {children}
      </h2>
      {description ? <div className="mt-1 text-sm text-muted">{description}</div> : null}
    </div>
  );
}
