"use client";

import { useSyncExternalStore, Suspense, type ReactNode } from "react";

import { AppSidebar } from "@/components/app-sidebar";
import { AppTopbar } from "@/components/app-topbar";
import type { User } from "@/lib/auth";

const SIDEBAR_STORAGE_KEY = "agenda.sidebar.open";

const sidebarListeners = new Set<() => void>();

function subscribeSidebar(onStoreChange: () => void) {
  sidebarListeners.add(onStoreChange);
  return () => {
    sidebarListeners.delete(onStoreChange);
  };
}

function getSidebarOpen(): boolean {
  return window.localStorage.getItem(SIDEBAR_STORAGE_KEY) !== "0";
}

function getSidebarServerSnapshot(): boolean {
  return true;
}

function setSidebarOpenPersisted(next: boolean) {
  window.localStorage.setItem(SIDEBAR_STORAGE_KEY, next ? "1" : "0");
  sidebarListeners.forEach((listener) => listener());
}

type AppShellProps = {
  user: User | null;
  children: ReactNode;
};

export function AppShell({ user, children }: AppShellProps) {
  const sidebarOpen = useSyncExternalStore(
    subscribeSidebar,
    getSidebarOpen,
    getSidebarServerSnapshot,
  );

  function toggleSidebar() {
    setSidebarOpenPersisted(!sidebarOpen);
  }

  return (
    <div className="flex min-h-full min-h-dvh flex-1 overflow-x-hidden bg-background">
      <AppSidebar user={user} open={sidebarOpen} onToggle={toggleSidebar} />
      <div className="flex min-w-0 flex-1 flex-col pb-[calc(4.5rem+env(safe-area-inset-bottom))] lg:pb-0">
        <Suspense fallback={null}>
          <AppTopbar user={user} />
        </Suspense>
        {children}
      </div>
    </div>
  );
}

type PageHeaderProps = {
  title: string;
  description?: ReactNode;
  actions?: ReactNode;
};

export function PageHeader({ title, description, actions }: PageHeaderProps) {
  return (
    <header className="flex flex-row items-start justify-between gap-3 px-4 pb-1 pt-5 sm:px-8 sm:pt-6">
      <div className="min-w-0 flex-1">
        <h1 className="break-words font-[family-name:var(--font-display)] text-xl font-semibold tracking-tight text-foreground sm:text-3xl">
          {title}
        </h1>
        {description ? <div className="mt-1.5 text-sm text-muted">{description}</div> : null}
      </div>
      {actions ? (
        <div className="flex shrink-0 flex-wrap items-center justify-end gap-2 sm:gap-3">
          {actions}
        </div>
      ) : null}
    </header>
  );
}

type PageContentProps = {
  children: ReactNode;
  narrow?: boolean;
  wide?: boolean;
};

export function PageContent({ children, narrow, wide }: PageContentProps) {
  const widthClass = wide
    ? "w-full"
    : narrow
      ? "w-full max-w-xl"
      : "w-full max-w-3xl";

  return (
    <main className="flex-1 px-4 py-5 sm:px-8 sm:py-6">
      <div className={widthClass}>{children}</div>
    </main>
  );
}
