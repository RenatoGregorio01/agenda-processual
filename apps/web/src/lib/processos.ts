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

export type DatajudAndamento = {
  data_hora: string | null;
  codigo: number | null;
  nome: string;
  complemento: string | null;
  orgao: string | null;
};

export type DatajudSync = {
  status:
    | "nunca_consultado"
    | "ok"
    | "indisponivel"
    | "tribunal_nao_suportado"
    | "erro"
    | "nao_configurado"
    | "limite";
  sincronizado_em: string | null;
  tribunal: string | null;
  grau: string | null;
  classe: string | null;
  orgao: string | null;
  mensagem: string | null;
  cache: boolean;
  andamentos: DatajudAndamento[];
};

export type ProcessoValidar = {
  incompleto: boolean;
  valido: boolean | null;
  mensagem: string | null;
  mascarado: string | null;
  cadastrado: boolean;
  processo_id: string | null;
  cliente: string | null;
  prazos_count: number | null;
  datajud: "encontrado" | "nao_encontrado" | "limite" | "erro" | null;
  datajud_mensagem: string | null;
};

export type ProcessoDetail = {
  processo: Processo;
  prazos: Prazo[];
  historico: AuditLog[];
  datajud: DatajudSync;
};
