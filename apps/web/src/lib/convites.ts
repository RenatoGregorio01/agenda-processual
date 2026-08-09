import type { Role } from "@/lib/auth";

export type Convite = {
  id: string;
  email: string;
  nome: string;
  role: Role;
  receber_alertas: boolean;
  expires_at: string;
  used_at: string | null;
  revoked_at: string | null;
  invited_by_id: string;
  criado_em: string;
  status: "pendente" | "aceito" | "expirado" | "revogado" | string;
};

export type ConvitePublic = {
  email: string;
  nome: string;
  role: Role;
  expires_at: string;
};

export function labelStatusConvite(status: string): string {
  switch (status) {
    case "pendente":
      return "Pendente";
    case "aceito":
      return "Aceito";
    case "expirado":
      return "Expirado";
    case "revogado":
      return "Revogado";
    default:
      return status;
  }
}
