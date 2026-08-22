import Link from "next/link";

import { Card, SectionHeading } from "@/components/ui";

export default function PrivacidadePage() {
  return (
    <div className="flex flex-1 flex-col bg-background">
      <main className="mx-auto w-full max-w-2xl flex-1 px-6 py-12">
        <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted">
          Agenda Processual
        </p>
        <h1 className="mt-2 font-[family-name:var(--font-display)] text-3xl font-semibold tracking-tight text-foreground">
          Privacidade
        </h1>
        <p className="mt-3 text-sm leading-relaxed text-muted">
          Como este sistema trata dados pessoais no escritório que o utiliza.
        </p>

        <Card className="mt-8 space-y-8 p-5 sm:p-7">
          <section>
            <SectionHeading>Quais dados</SectionHeading>
            <ul className="list-disc space-y-1 pl-5 text-sm text-foreground">
              <li>Colaboradores: nome, e-mail, senha (somente o hash) e perfil de acesso.</li>
              <li>Clientes e casos: nome da parte, número do processo, prazos e andamentos.</li>
              <li>Registros de uso: login e alterações (auditoria), envio de alertas.
                A auditoria é apagada automaticamente após 365 dias.</li>
            </ul>
          </section>

          <section>
            <SectionHeading>Para quê</SectionHeading>
            <p className="text-sm leading-relaxed text-foreground">
              Gestão de prazos processuais, cálculo de vencimento, alerta ao responsável e
              histórico de quem alterou o quê. A consulta à Datajud (CNJ) envia só o número
              do processo, que é dado público.
            </p>
          </section>

          <section>
            <SectionHeading>Quem acessa</SectionHeading>
            <p className="text-sm leading-relaxed text-foreground">
              Os dados ficam no escritório da sua conta. Admin, editor e visualizador veem
              os prazos desse escritório, conforme o perfil. Alertas de e-mail vão só para
              o responsável do prazo, se a pessoa tiver optado por recebê-los. O corpo do
              e-mail não traz nome do cliente nem número do processo.
            </p>
          </section>

          <section>
            <SectionHeading>Seus direitos</SectionHeading>
            <p className="text-sm leading-relaxed text-foreground">
              Para corrigir ou pedir a exclusão dos seus dados, fale com o administrador do
              escritório que te convidou.
            </p>
          </section>
        </Card>

        <p className="mt-8 text-sm">
          <Link href="/login" className="text-primary underline-offset-4 hover:underline">
            Voltar ao login
          </Link>
        </p>
      </main>
    </div>
  );
}
