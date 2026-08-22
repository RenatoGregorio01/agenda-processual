"use client";

import { useState } from "react";

import { Button, Card, SectionHeading } from "@/components/ui";
import type { DatajudAndamento, DatajudSync } from "@/lib/processos";

const PAGE_SIZE = 3;

function hasMeaningfulTime(value: string): boolean {
  const match = value.match(/T(\d{2}):(\d{2}):(\d{2})/);
  if (!match) return false;
  return !(match[1] === "00" && match[2] === "00" && match[3] === "00");
}

function formatAndamentoDate(value: string | null): string {
  if (!value) return "Sem data";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  // DataJud costuma mandar só a data (00:00). Não inventamos horário.
  if (!hasMeaningfulTime(value)) {
    const dateOnly = value.match(/^(\d{4})-(\d{2})-(\d{2})/);
    if (dateOnly) {
      const [, year, month, day] = dateOnly;
      return `${day}/${month}/${year}`;
    }
    return new Intl.DateTimeFormat("pt-BR", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      timeZone: "UTC",
    }).format(date);
  }
  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(date);
}

function formatSyncDate(value: string | null): string | null {
  if (!value) return null;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(date);
}

function statusMessage(data: DatajudSync): string {
  if (data.status === "ok" && data.andamentos.length === 0) {
    return "Consulta ok, mas o tribunal não enviou movimentações.";
  }
  if (data.status === "ok") {
    const when = formatSyncDate(data.sincronizado_em);
    return when ? `Atualizado em ${when}` : "Andamentos do tribunal";
  }
  if (data.status === "indisponivel") {
    return data.mensagem || "Não encontramos este processo na base pública do tribunal.";
  }
  if (data.status === "tribunal_nao_suportado") {
    return data.mensagem || "Tribunal não suportado para consulta automática.";
  }
  if (data.status === "nao_configurado") {
    return "Consulta ao tribunal não configurada.";
  }
  if (data.status === "limite") {
    return data.mensagem || "Muitas consultas ao tribunal. Tente de novo em instantes.";
  }
  return data.mensagem || "Não foi possível consultar os andamentos.";
}

function andamentoDetails(item: DatajudAndamento): string | null {
  const parts = [item.complemento, item.orgao].filter(Boolean);
  return parts.length > 0 ? parts.join(" · ") : null;
}

export function AndamentosEmpty({ message }: { message: string }) {
  return (
    <section className="mt-5">
      <SectionHeading>Andamentos do tribunal</SectionHeading>
      <Card className="px-4 py-4">
        <p className="text-sm text-muted">{message}</p>
      </Card>
    </section>
  );
}

export function ProcessoAndamentos({ data }: { data: DatajudSync }) {
  const [visibleCount, setVisibleCount] = useState(PAGE_SIZE);
  const notFound =
    data.status === "indisponivel" ||
    data.status === "tribunal_nao_suportado" ||
    data.status === "erro";
  const visible = data.andamentos.slice(0, visibleCount);
  const remaining = Math.max(0, data.andamentos.length - visible.length);

  return (
    <section className="mt-5">
      <SectionHeading description={statusMessage(data)}>Andamentos do tribunal</SectionHeading>
      {data.status === "ok" && (data.classe || data.orgao) ? (
        <p className="mt-1 text-xs text-muted">
          {[data.tribunal, data.grau, data.classe, data.orgao].filter(Boolean).join(" · ")}
        </p>
      ) : null}

      {data.andamentos.length === 0 ? (
        <Card className="px-4 py-4">
          <p className="text-sm text-foreground">
            {notFound
              ? "Não há andamentos públicos para este número. Pode ser processo sigiloso, atraso na indexação do tribunal ou numeração incompleta."
              : "Nenhum andamento público para exibir."}
          </p>
        </Card>
      ) : (
        <>
          <ol className="mt-4 space-y-3">
            {visible.map((item, index) => {
              const details = andamentoDetails(item);
              return (
                <li
                  key={`${item.codigo ?? "x"}-${item.data_hora ?? index}-${item.nome}-${item.complemento ?? ""}`}
                  className="rounded-md border border-border bg-surface px-4 py-3"
                >
                  <div className="flex items-start justify-between gap-3">
                    <p className="min-w-0 text-sm font-medium text-foreground">{item.nome}</p>
                    <p className="shrink-0 text-xs text-muted">
                      {formatAndamentoDate(item.data_hora)}
                    </p>
                  </div>
                  {details ? (
                    <p className="mt-1 text-xs leading-relaxed text-muted">{details}</p>
                  ) : null}
                </li>
              );
            })}
          </ol>
          {remaining > 0 ? (
            <Button
              type="button"
              variant="secondary"
              fullWidth
              className="mt-3"
              onClick={() => setVisibleCount((current) => current + PAGE_SIZE)}
            >
              Ver mais
            </Button>
          ) : null}
        </>
      )}
    </section>
  );
}
