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
    <div className="sticky top-0 z-10 flex items-center gap-3 border-b border-border bg-surface/95 px-5 py-3 backdrop-blur-sm sm:px-8">
      <form action="/prazos" method="get" className="min-w-0 flex-1 sm:max-w-md">
        <SearchField
          name="q"
          placeholder="Buscar processo, cliente ou responsável…"
          aria-label="Buscar prazos"
        />
      </form>
      {showNovoPrazo ? (
        <ButtonLink href="/prazos/novo" className="shrink-0">
          + Novo prazo
        </ButtonLink>
      ) : null}
    </div>
  );
}
