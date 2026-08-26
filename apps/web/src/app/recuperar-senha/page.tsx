import Link from "next/link";

import { RecuperarSenhaForm } from "@/components/recuperar-senha-form";
import { Card } from "@/components/ui";

export default function RecuperarSenhaPage() {
  return <div className="flex flex-1 flex-col bg-background"><main className="mx-auto flex w-full max-w-md flex-1 flex-col justify-center px-4 py-8 sm:px-6 sm:py-12"><Card className="px-5 py-8 sm:px-10 sm:py-12"><header className="text-center"><h1 className="font-[family-name:var(--font-display)] text-3xl font-semibold tracking-tight text-primary sm:text-4xl">Recuperar senha</h1><p className="mt-3 text-sm leading-relaxed text-muted sm:text-base">Enviaremos um link para você definir uma nova senha.</p></header><div className="mt-8 sm:mt-10"><RecuperarSenhaForm /></div><p className="mt-6 text-center text-sm text-muted"><Link href="/login" className="text-primary underline-offset-4 hover:underline">Voltar ao login</Link></p></Card></main></div>;
}
