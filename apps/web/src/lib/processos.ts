import type { AuditLog } from "@/lib/auditoria";
import type { Prazo } from "@/lib/prazos";

export type Processo = {
  id: string;
  numero_processo: string;
  cliente: string;
  criado_em: string;
  atualizado_em: string;
  prazos_count: number;
};

export type ProcessoDetail = {
  processo: Processo;
  prazos: Prazo[];
  historico: AuditLog[];
};
