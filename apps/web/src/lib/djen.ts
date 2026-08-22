export type DjenStatus = "nova" | "prazo_criado" | "ignorada";

export type DjenPublicacao = {
  id: string;
  processo_id: string | null;
  prazo_id: string | null;
  numero_processo: string;
  cliente: string | null;
  tribunal: string | null;
  tipo_comunicacao: string;
  tipo_documento: string | null;
  orgao: string | null;
  data_disponibilizacao: string | null;
  vencimento_sugerido: string | null;
  status: DjenStatus;
  motivo_cancelamento: string | null;
  sincronizado_em: string;
  criado_em: string;
};

export type DjenResumo = {
  novas: number;
};

export function formatDjenDate(iso: string | null): string {
  if (!iso) return "Sem data";
  const [year, month, day] = iso.split("-");
  if (!year || !month || !day) return iso;
  return `${day}/${month}/${year}`;
}

export function labelDjenStatus(status: DjenStatus, cancelada: boolean): string {
  if (cancelada) return "Cancelada";
  if (status === "prazo_criado") return "Prazo criado";
  if (status === "ignorada") return "Ignorada";
  return "Nova";
}
