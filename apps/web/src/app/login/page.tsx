import Link from "next/link";

import { LoginForm } from "@/components/login-form";
import { Card } from "@/components/ui";

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ next?: string }>;
}) {
  const params = await searchParams;

  return (
    <div className="flex flex-1 flex-col bg-background">
      <main className="mx-auto flex w-full max-w-md flex-1 flex-col justify-center px-6 py-12">
        <Card className="px-6 py-10 sm:px-10 sm:py-12">
          <header className="text-center">
            <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted">
              Escritório
            </p>
            <h1 className="mt-2 font-[family-name:var(--font-display)] text-3xl font-semibold tracking-tight text-primary sm:text-4xl">
              Agenda Processual
            </h1>
            <p className="mt-3 text-sm leading-relaxed text-muted sm:text-base">
              Acesse para ver a pauta e os vencimentos
            </p>
          </header>

          <div className="mt-10">
            <LoginForm nextPath={params.next || "/dashboard"} />
          </div>
          <p className="mt-6 text-center text-xs text-muted">
            Ao entrar, você usa o sistema do seu escritório.{" "}
            <Link href="/privacidade" className="text-primary underline-offset-4 hover:underline">
              Privacidade
            </Link>
          </p>
        </Card>
      </main>
    </div>
  );
}
