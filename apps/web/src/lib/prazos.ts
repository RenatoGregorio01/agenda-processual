export type StatusPrazo = "pendente" | "cumprido";

export type PrazoAlerta = {
  dias_antes: number;
  enviado: boolean;
};

export type Prazo = {
  id: string;
  processo_id?: string | null;
  numero_processo: string;
  cliente: string;
  acao: string;
  data_disponibilizacao: string | null;
  data_vencimento: string;
  responsavel: string;
  responsavel_id: string | null;
  status: StatusPrazo;
  alertas: PrazoAlerta[];
  excluido_em: string | null;
  criado_em: string;
  atualizado_em: string;
};

export const DEFAULT_ALERTA_DIAS = [3, 1];
export const ALERTA_DIAS_MIN = 1;
export const ALERTA_DIAS_MAX = 365;

export function labelAlertaDias(dias: number): string {
  return dias === 1 ? "1 dia antes" : `${dias} dias antes`;
}

export type FiltroPrazo =
  | "todos"
  | "atrasados"
  | "hoje"
  | "cumpridos"
  | "excluidos";

export type UrgencyBadge = {
  label: string;
  tone: "atrasado" | "urgente" | "no-prazo" | "cumprido" | "neutro";
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

const MONTHS_LONG_PT = [
  "janeiro",
  "fevereiro",
  "março",
  "abril",
  "maio",
  "junho",
  "julho",
  "agosto",
  "setembro",
  "outubro",
  "novembro",
  "dezembro",
] as const;

export function formatVencimentoParts(value: string): { day: string; monthYear: string } {
  const date = parseDateOnly(value);
  return {
    day: String(date.getDate()),
    monthYear: `${MONTHS_LONG_PT[date.getMonth()]}, ${date.getFullYear()}`,
  };
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
    return { label: "CUMPRIDO", tone: "cumprido" };
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
  { id: "hoje", label: "Hoje" },
  { id: "cumpridos", label: "Cumpridos" },
  { id: "excluidos", label: "Excluídos" },
];

