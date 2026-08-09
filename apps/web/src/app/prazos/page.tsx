import Link from "next/link";

export default function PrazosPage() {
  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col px-6 py-16 sm:px-10">
      <p className="font-[family-name:var(--font-display)] text-3xl font-semibold text-primary">
        Agenda Processual
      </p>
      <h1 className="mt-6 text-2xl font-medium text-foreground">Prazos</h1>
      <p className="mt-3 max-w-lg text-muted">
        Placeholder da lista. A feature de prazos entra em seguida (ordenada por
        vencimento, com badges de urgência).
      </p>
      <Link href="/" className="mt-8 text-primary underline-offset-4 hover:underline">
        Voltar
      </Link>
    </main>
  );
}
