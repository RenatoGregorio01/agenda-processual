import Link from "next/link";

import { NovoPrazoForm } from "@/components/novo-prazo-form";

export default function NovoPrazoPage() {
  return (
    <main className="mx-auto flex w-full max-w-xl flex-1 flex-col px-6 py-10 sm:px-10">
      <Link href="/prazos" className="text-sm text-muted underline-offset-4 hover:underline">
        ← Voltar para prazos
      </Link>
      <h1 className="mt-6 text-3xl font-semibold tracking-tight text-foreground">Novo prazo</h1>
      <p className="mt-2 text-muted">Cadastre em menos de 1 minuto.</p>
      <div className="mt-8 border border-border bg-surface p-5 sm:p-7">
        <NovoPrazoForm />
      </div>
    </main>
  );
}
