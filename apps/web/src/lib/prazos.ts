export type StatusPrazo = "pendente" | "cumprido";

export type Prazo = {
  id: string;
  numero_processo: string;
  cliente: string;
  acao: string;
  data_disponibilizacao: string | null;
  data_vencimento: string;
  responsavel: string;
  responsavel_id: string | null;
  status: StatusPrazo;
  alerta_3_dias: boolean;
  alerta_2_dias: boolean;
  alerta_1_dia: boolean;
  excluido_em: string | null;
  criado_em: string;
  atualizado_em: string;
};

export type FiltroPrazo = "todos" | "atrasados" | "7dias" | "cumpridos" | "excluidos";

export type UrgencyBadge = {
  label: string;
  tone: "atrasado" | "urgente" | "no-prazo" | "neutro";
};

const MONTHS_PT = [
  "jan",
  "fev",
  "mar",
  "abr",
  "mai",
  "jun",
  "jul",
  "ago",
  "set",
  "out",
  "nov",
  "dez",
] as const;

export function parseDateOnly(value: string): Date {
  const [year, month, day] = value.split("-").map(Number);
  return new Date(year, month - 1, day);
}

export function formatVencimento(value: string): string {
  const date = parseDateOnly(value);
  return `${date.getDate()} ${MONTHS_PT[date.getMonth()]} ${date.getFullYear()}`;
}

export function formatVencimentoLongo(value: string): string {
  const date = parseDateOnly(value);
  return date.toLocaleDateString("pt-BR", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

export function daysUntil(value: string, today = new Date()): number {
  const target = parseDateOnly(value);
  const start = new Date(today.getFullYear(), today.getMonth(), today.getDate());
  const diffMs = target.getTime() - start.getTime();
  return Math.round(diffMs / (1000 * 60 * 60 * 24));
}

export function getUrgencyBadge(prazo: Prazo, today = new Date()): UrgencyBadge {
  if (prazo.excluido_em) {
    return { label: "EXCLUÍDO", tone: "neutro" };
  }
  if (prazo.status === "cumprido") {
    return { label: "CUMPRIDO", tone: "neutro" };
  }

  const days = daysUntil(prazo.data_vencimento, today);
  if (days < 0) return { label: "ATRASADO", tone: "atrasado" };
  if (days === 0) return { label: "HOJE", tone: "urgente" };
  if (days === 1) return { label: "AMANHÃ", tone: "urgente" };
  if (days <= 3) return { label: `EM ${days} DIAS`, tone: "urgente" };
  return { label: `EM ${days} DIAS`, tone: "no-prazo" };
}

export const FILTROS: { id: FiltroPrazo; label: string }[] = [
  { id: "todos", label: "Todos" },
  { id: "atrasados", label: "Atrasados" },
  { id: "7dias", label: "7 dias" },
  { id: "cumpridos", label: "Cumpridos" },
  { id: "excluidos", label: "Excluídos" },
];
