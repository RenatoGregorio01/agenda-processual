export type AuditAction =
  | "login"
  | "prazo_criado"
  | "prazo_atualizado"
  | "prazo_cumprido"
  | "prazo_excluido"
  | "prazo_restaurado"
  | "usuario_criado"
  | "usuario_atualizado"
  | "feriado_criado"
  | "feriado_atualizado"
  | "feriado_excluido"
  | "convite_criado"
  | "convite_reenviado"
  | "convite_revogado"
  | "convite_aceito"
  | "processo_criado"
  | "processo_atualizado"
  | "djen_ignorada";

export type AuditLog = {
  id: string;
  usuario_id: string;
  usuario_nome: string;
  usuario_email: string;
  acao: AuditAction;
  entidade: string;
  entidade_id: string | null;
  resumo: string;
  criado_em: string;
};

const ACTION_LABELS: Record<AuditAction, string> = {
  login: "Login",
  prazo_criado: "Criação",
  prazo_atualizado: "Edição",
  prazo_cumprido: "Cumprido",
  prazo_excluido: "Exclusão",
  prazo_restaurado: "Restauração",
  usuario_criado: "Usuário criado",
  usuario_atualizado: "Usuário atualizado",
  feriado_criado: "Feriado criado",
  feriado_atualizado: "Feriado atualizado",
  feriado_excluido: "Feriado excluído",
  convite_criado: "Convite enviado",
  convite_reenviado: "Convite reenviado",
  convite_revogado: "Convite revogado",
  convite_aceito: "Convite aceito",
  processo_criado: "Processo criado",
  processo_atualizado: "Processo atualizado",
  djen_ignorada: "Publicação DJEN ignorada",
};

export function labelAcao(acao: AuditAction): string {
  return ACTION_LABELS[acao] ?? acao;
}

export function formatAuditDate(value: string): string {
  return new Date(value).toLocaleString("pt-BR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}
