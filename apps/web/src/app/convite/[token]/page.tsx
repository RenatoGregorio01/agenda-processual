import Link from "next/link";

import { AceitarConviteForm } from "@/components/aceitar-convite-form";
import { getServerApiBaseUrl } from "@/lib/api";
import type { ConvitePublic } from "@/lib/convites";

type PageProps = {
  params: Promise<{ token: string }>;
};

async function getConvite(token: string): Promise<ConvitePublic | null> {
  const response = await fetch(
    `${getServerApiBaseUrl()}/api/v1/convites/aceitar/${encodeURIComponent(token)}`,
    { cache: "no-store" },
  );
  if (!response.ok) return null;
  return (await response.json()) as ConvitePublic;
}

export default async function ConvitePage({ params }: PageProps) {
  const { token } = await params;
  const convite = await getConvite(token);

  return (
    <main className="mx-auto flex w-full max-w-md flex-1 flex-col justify-center px-6 py-16">
      <p className="font-[family-name:var(--font-display)] text-2xl font-semibold text-primary">
        Agenda Processual
      </p>
      <h1 className="mt-5 text-3xl font-semibold tracking-tight text-foreground">
        Ativar acesso
      </h1>
      <p className="mt-2 text-muted">Defina sua senha para começar a usar o sistema.</p>

      <section className="mt-8 border border-border bg-surface p-5 sm:p-7">
        {convite ? (
          <AceitarConviteForm token={token} convite={convite} />
        ) : (
          <div className="space-y-4 text-sm">
            <p className="text-atrasado">
              Este convite é inválido, expirou ou já foi utilizado.
            </p>
            <Link href="/login" className="inline-flex text-primary underline-offset-4 hover:underline">
              Ir para o login
            </Link>
          </div>
        )}
      </section>
    </main>
  );
}
