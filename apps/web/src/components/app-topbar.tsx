"use client";

import { usePathname } from "next/navigation";

import { ButtonLink, SearchField } from "@/components/ui";
import { hasPermission, type User } from "@/lib/auth";

type AppTopbarProps = {
  user: User | null;
};

/** Páginas que já trazem o CTA “+ Novo prazo” no próprio header. */
function hideNovoPrazoCta(pathname: string): boolean {
  if (pathname === "/prazos" || pathname.startsWith("/prazos/novo")) return true;
  if (pathname.startsWith("/processos/")) return true;
  return false;
}

export function AppTopbar({ user }: AppTopbarProps) {
  const pathname = usePathname();
  const showNovoPrazo =
    hasPermission(user, "prazos_criar") && !hideNovoPrazoCta(pathname);

  return (
    <div className="sticky top-0 z-10 flex items-center gap-2 border-b border-border bg-surface/95 px-4 py-2.5 backdrop-blur-sm pt-[max(0.625rem,env(safe-area-inset-top))] sm:gap-3 sm:px-8 sm:py-3">
      <form action="/prazos" method="get" className="min-w-0 flex-1 sm:max-w-md">
        <SearchField
          name="q"
          placeholder="Buscar prazos…"
          aria-label="Buscar prazos"
          className="h-10 text-base sm:h-11 sm:text-sm"
        />
      </form>
      {showNovoPrazo ? (
        <ButtonLink href="/prazos/novo" size="sm" className="shrink-0 px-3 sm:h-11 sm:px-4 sm:text-sm">
          <span className="sm:hidden">+ Novo</span>
          <span className="hidden sm:inline">+ Novo prazo</span>
        </ButtonLink>
      ) : null}
    </div>
  );
}
