import Link from "next/link";

import { CadastroForm } from "@/components/cadastro-form";
import { Card } from "@/components/ui";

export default function CadastroPage() {
  return (
    <div className="flex flex-1 flex-col bg-background">
      <main className="mx-auto flex w-full max-w-md flex-1 flex-col justify-start px-4 py-6 sm:px-6 sm:py-12 sm:justify-center">
        <Card className="px-4 py-6 sm:px-10 sm:py-12">
          <header className="text-center">
            <h1 className="font-[family-name:var(--font-display)] text-3xl font-semibold tracking-tight text-primary sm:text-4xl">
              Configurar escritório
            </h1>
            <p className="mx-auto mt-3 max-w-xs text-sm leading-relaxed text-muted sm:max-w-none sm:text-base">
              Cadastre o escritório e sua conta de administrador
            </p>
          </header>

          <div className="mt-6 sm:mt-10">
            <CadastroForm />
          </div>

          <p className="mt-6 text-center text-xs leading-relaxed text-muted">
            Já tem conta?{" "}
            <Link href="/login" className="text-primary underline-offset-4 hover:underline">
              Entrar
            </Link>
          </p>
        </Card>
      </main>
    </div>
  );
}
