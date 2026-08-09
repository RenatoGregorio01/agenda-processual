import { LoginForm } from "@/components/login-form";

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ next?: string }>;
}) {
  const params = await searchParams;

  return (
    <div className="relative flex flex-1 flex-col overflow-hidden">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_15%_10%,rgba(15,61,46,0.14),transparent_40%),linear-gradient(180deg,#f7f6f3_0%,#efece4_100%)]"
      />

      <main className="relative z-10 mx-auto flex w-full max-w-md flex-1 flex-col justify-center px-6 py-16">
        <p className="font-[family-name:var(--font-display)] text-4xl font-semibold tracking-tight text-primary">
          Agenda Processual
        </p>
        <p className="mt-3 text-lg text-muted">Prazos processuais sob controle</p>

        <div className="mt-10 border border-border bg-surface p-6 sm:p-8">
          <h1 className="text-xl font-medium text-foreground">Entrar</h1>
          <p className="mt-2 text-sm text-muted">
            Use a conta criada pelo administrador do escritório.
          </p>
          <div className="mt-6">
            <LoginForm nextPath={params.next || "/prazos"} />
          </div>
        </div>
      </main>
    </div>
  );
}
