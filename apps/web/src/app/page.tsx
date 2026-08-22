import Link from "next/link";

import { ApiStatus } from "@/components/api-status";

export default function Home() {
  return (
    <div className="relative flex flex-1 flex-col overflow-hidden">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(15,61,46,0.12),transparent_45%),radial-gradient(circle_at_80%_0%,rgba(15,61,46,0.08),transparent_40%),linear-gradient(180deg,#f7f6f3_0%,#efece4_100%)]"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 opacity-[0.35] [background-image:linear-gradient(rgba(26,26,26,0.04)_1px,transparent_1px),linear-gradient(90deg,rgba(26,26,26,0.04)_1px,transparent_1px)] [background-size:48px_48px]"
      />

      <main className="relative z-10 mx-auto flex w-full max-w-3xl flex-1 flex-col justify-center px-6 py-16 sm:px-10">
        <p className="font-[family-name:var(--font-display)] text-4xl font-semibold tracking-tight text-primary sm:text-5xl">
          Agenda Processual
        </p>
        <h1 className="mt-6 max-w-xl text-2xl font-medium leading-snug text-foreground sm:text-3xl">
          Prazos processuais sob controle
        </h1>
        <p className="mt-4 max-w-lg text-lg leading-relaxed text-muted">
          Cadastre o vencimento, acompanhe o que vence primeiro e saia do
          memoriômetro.
        </p>

        <div className="mt-10 flex flex-col gap-3 sm:flex-row sm:items-center">
          <Link
            href="/login"
            className="inline-flex h-12 items-center justify-center bg-primary px-6 text-base font-semibold text-primary-foreground transition hover:brightness-110"
          >
            Entrar
          </Link>
          <Link
            href="/cadastro"
            className="inline-flex h-12 items-center justify-center border border-border bg-surface px-6 text-base font-medium text-foreground transition hover:bg-background"
          >
            Cadastre-se
          </Link>
        </div>

        <div className="mt-12 border-t border-border pt-6">
          <ApiStatus />
        </div>
      </main>
    </div>
  );
}
