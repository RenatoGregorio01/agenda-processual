import { cn } from "@/lib/cn";

type EmptyStateProps = {
  children: string;
  className?: string;
};

export function EmptyState({ children, className }: EmptyStateProps) {
  return (
    <p
      className={cn(
        "w-full rounded-md border border-dashed border-border bg-surface/60 px-4 py-8 text-left text-sm text-muted",
        className,
      )}
    >
      {children}
    </p>
  );
}
