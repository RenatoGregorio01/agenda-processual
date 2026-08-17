"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

import { hasPermission, type User } from "@/lib/auth";

type AppSidebarProps = {
  user: User | null;
  open?: boolean;
  onToggle?: () => void;
};

function IconHoje({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <rect x="3" y="5" width="18" height="16" rx="2" stroke="currentColor" strokeWidth="1.6" />
      <path d="M3 10h18" stroke="currentColor" strokeWidth="1.6" />
      <path d="M8 3v4M16 3v4" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  );
}

function IconPrazos({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path d="M8 6h13M8 12h13M8 18h13" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      <path d="M4 6h.01M4 12h.01M4 18h.01" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" />
    </svg>
  );
}

function IconUsuarios({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <circle cx="9" cy="8" r="3" stroke="currentColor" strokeWidth="1.6" />
      <path
        d="M3.5 18.5c1.2-2.4 3.2-3.5 5.5-3.5s4.3 1.1 5.5 3.5"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
      />
      <circle cx="17" cy="9" r="2.5" stroke="currentColor" strokeWidth="1.6" />
      <path d="M14.5 18.5c.7-1.4 1.8-2.2 3.2-2.5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  );
}

function IconFeriados({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <rect x="3.5" y="5" width="17" height="15" rx="2" stroke="currentColor" strokeWidth="1.6" />
      <path d="M3.5 10h17" stroke="currentColor" strokeWidth="1.6" />
      <path d="M8 3.5v3M16 3.5v3" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      <path d="M9 14.5l2 2 4-4" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function IconAuditoria({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path d="M5 5h14v14H5z" stroke="currentColor" strokeWidth="1.6" />
      <path d="M8 9h8M8 12h8M8 15h5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  );
}

function IconSair({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path d="M10 5H6a1 1 0 00-1 1v12a1 1 0 001 1h4" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      <path d="M14 16l4-4-4-4M18 12H10" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function IconMais({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <circle cx="6" cy="12" r="1.4" fill="currentColor" />
      <circle cx="12" cy="12" r="1.4" fill="currentColor" />
      <circle cx="18" cy="12" r="1.4" fill="currentColor" />
    </svg>
  );
}

function IconUser({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <circle cx="12" cy="8" r="3.5" stroke="currentColor" strokeWidth="1.6" />
      <path
        d="M5.5 19c1.5-3 4-4.5 6.5-4.5S17 16 18.5 19"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
      />
    </svg>
  );
}

function BrandMark({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path d="M7 5l3 14M12 5l3 14M17 5l3 14" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

function navClass(active: boolean) {
  return active
    ? "flex min-h-11 items-center gap-3 rounded-md bg-primary/10 px-3 py-2.5 text-sm font-semibold text-primary"
    : "flex min-h-11 items-center gap-3 rounded-md px-3 py-2.5 text-sm text-muted transition hover:bg-[#f1efe9] hover:text-foreground";
}

function mobileTabClass(active: boolean) {
  return `flex min-h-12 flex-1 flex-col items-center justify-center gap-0.5 px-1 py-2 text-[11px] font-medium ${
    active ? "text-primary" : "text-muted"
  }`;
}

export function AppSidebar({ user, open = true, onToggle }: AppSidebarProps) {
  const pathname = usePathname();
  const [maisOpen, setMaisOpen] = useState(false);
  const [pathWhenMaisOpen, setPathWhenMaisOpen] = useState(pathname);
  const isAdmin = hasPermission(user, "usuarios_gerenciar");

  if (maisOpen && pathWhenMaisOpen !== pathname) {
    setMaisOpen(false);
    setPathWhenMaisOpen(pathname);
  }

  const activeHoje = pathname === "/dashboard";
  const activePrazos = pathname.startsWith("/prazos") || pathname.startsWith("/processos/");
  const activeUsuarios = pathname.startsWith("/usuarios");
  const activeFeriados = pathname.startsWith("/feriados");
  const activeAuditoria = pathname.startsWith("/auditoria");
  const activeMais = activeUsuarios || activeFeriados || activeAuditoria;

  useEffect(() => {
    if (!maisOpen) return;
    function onKey(event: KeyboardEvent) {
      if (event.key === "Escape") setMaisOpen(false);
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [maisOpen]);

  async function logout() {
    setMaisOpen(false);
    try {
      await fetch("/api/auth/logout", { method: "POST", credentials: "same-origin" });
    } finally {
      // Hard redirect: soft navigation no mobile mantém a UI autenticada em cache.
      window.location.assign(new URL("/login", window.location.origin).toString());
    }
  }

  const secondaryNav = (
    <>
      {isAdmin ? (
        <>
          <Link
            href="/usuarios"
            className={navClass(activeUsuarios)}
            onClick={() => {
              setMaisOpen(false);
              setPathWhenMaisOpen(pathname);
            }}
          >
            <IconUsuarios className="h-5 w-5 shrink-0" />
            Usuários
          </Link>
          <Link
            href="/feriados"
            className={navClass(activeFeriados)}
            onClick={() => setMaisOpen(false)}
          >
            <IconFeriados className="h-5 w-5 shrink-0" />
            Feriados
          </Link>
        </>
      ) : null}
      <Link
        href="/auditoria"
        className={navClass(activeAuditoria)}
        onClick={() => setMaisOpen(false)}
      >
        <IconAuditoria className="h-5 w-5 shrink-0" />
        Auditoria
      </Link>
      <button type="button" onClick={logout} className={`${navClass(false)} w-full text-left`}>
        <IconSair className="h-5 w-5 shrink-0" />
        Sair
      </button>
    </>
  );

  return (
    <>
      {open ? (
        <aside className="hidden w-60 shrink-0 flex-col border-r border-border bg-surface lg:flex">
          <div className="flex items-start gap-2 px-4 pb-5 pt-5">
            <div className="flex min-w-0 flex-1 items-center gap-2.5">
              <span className="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-primary text-primary-foreground">
                <BrandMark className="h-4 w-4" />
              </span>
              <p className="font-[family-name:var(--font-display)] text-[15px] font-semibold leading-tight text-foreground">
                Agenda Processual
              </p>
            </div>
            {onToggle ? (
              <button
                type="button"
                onClick={onToggle}
                className="mt-0.5 inline-flex h-6 w-6 shrink-0 items-center justify-center text-xs font-medium leading-none text-muted transition hover:text-foreground"
                aria-label="Esconder menu lateral"
                title="Esconder menu"
              >
                «
              </button>
            ) : null}
          </div>

          <nav className="flex flex-1 flex-col gap-1 px-3">
            <Link href="/dashboard" className={navClass(activeHoje)}>
              <IconHoje className="h-5 w-5 shrink-0" />
              Dashboard
            </Link>
            <Link href="/prazos" className={navClass(activePrazos)}>
              <IconPrazos className="h-5 w-5 shrink-0" />
              Prazos
            </Link>
            {secondaryNav}
          </nav>

          <div className="mt-auto flex items-center gap-2.5 border-t border-border px-4 py-4">
            <span className="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-[#eceae4] text-muted">
              <IconUser className="h-4 w-4" />
            </span>
            <div className="min-w-0">
              <p className="truncate text-sm font-medium text-foreground">{user?.nome ?? "Usuário"}</p>
              <p className="truncate text-[11px] text-muted">
                {user?.escritorio_nome || "Escritório"}
                {user?.role ? ` · ${user.role}` : ""}
              </p>
            </div>
          </div>
        </aside>
      ) : (
        <aside className="hidden w-10 shrink-0 flex-col items-center border-r border-border bg-surface pt-5 lg:flex">
          {onToggle ? (
            <button
              type="button"
              onClick={onToggle}
              className="inline-flex h-6 w-6 items-center justify-center text-xs font-medium leading-none text-muted transition hover:text-foreground"
              aria-label="Exibir menu lateral"
              title="Exibir menu"
            >
              »
            </button>
          ) : null}
        </aside>
      )}

      {maisOpen ? (
        <button
          type="button"
          aria-label="Fechar menu"
          className="fixed inset-0 z-30 bg-foreground/25 lg:hidden"
          onClick={() => setMaisOpen(false)}
        />
      ) : null}

      {maisOpen ? (
        <div className="fixed inset-x-0 bottom-[calc(3.5rem+env(safe-area-inset-bottom))] z-40 mx-3 mb-2 rounded-lg border border-border bg-surface p-3 shadow-[0_-4px_24px_rgba(26,26,26,0.08)] lg:hidden">
          <div className="mb-2 border-b border-border pb-2">
            <p className="truncate text-sm font-medium text-foreground">{user?.nome ?? "Usuário"}</p>
            <p className="truncate text-[11px] text-muted">
              {user?.escritorio_nome || "Escritório"}
              {user?.role ? ` · ${user.role}` : ""}
            </p>
          </div>
          <nav className="flex flex-col gap-1">{secondaryNav}</nav>
        </div>
      ) : null}

      <nav
        className="fixed inset-x-0 bottom-0 z-40 flex border-t border-border bg-surface pb-[env(safe-area-inset-bottom)] lg:hidden"
        aria-label="Navegação principal"
      >
        <Link href="/dashboard" className={mobileTabClass(activeHoje)}>
          <IconHoje className="h-5 w-5" />
          Pauta
        </Link>
        <Link href="/prazos" className={mobileTabClass(activePrazos && !activeHoje)}>
          <IconPrazos className="h-5 w-5" />
          Prazos
        </Link>
        <button
          type="button"
          onClick={() => {
            setPathWhenMaisOpen(pathname);
            setMaisOpen((value) => !value);
          }}
          className={mobileTabClass(maisOpen || activeMais)}
          aria-expanded={maisOpen}
        >
          <IconMais className="h-5 w-5" />
          Mais
        </button>
      </nav>
    </>
  );
}
